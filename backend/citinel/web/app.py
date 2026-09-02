"""CITINEL web service: /healthz, the read model, and the operations the
console can actually perform.

This is the Render "web" service (deploy/render.yaml). It serves what the
pipeline has produced on disk -- incidents, the audit ledger, persisted swarm
results, the policy table, compliance drafts -- and it exposes, as HTTP, the
same operations the CLI performs: run the swarm on an incident, run a proposal
through the policy gate and (if it clears) the simulated endpoints, roll an
action back by its token, and record a human sign-off. Every operation writes
the same ledger frames the CLI writes, through the same code, so the console
and the terminal are two views of one system rather than two systems.

Paths come from settings, never from __file__: pip installs this package into
site-packages, and a path derived from there broke the first deployment.
"""

from __future__ import annotations

import os

import threading
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from citinel.agents.context import gather_context, load_context
from citinel.agents.store import annotate_result, load_result, load_runs, summaries, summary_of
from citinel.connectors.lyzr_agents import handover_summary, review_draft, triage_second_opinion
from citinel.audit.ledger import AuditLedger
from citinel.compliance.drafter import draft_certin, draft_dpdp, render_text
from citinel.config import settings
from citinel.connectors.lyzr import LyzrGuard, LyzrLedgerMirror
from citinel.connectors.n8n import dispatch_signed
from citinel.connectors.swytchcode import SwytchcodeExecutor
from citinel.incidents.builder import load_incidents
from citinel.incidents.state import derive_state
from citinel.policy.actions import ActionExecutor, ExecutionRefused, MockEndpoints
from citinel.policy.gate import PolicyGate
from citinel.policy.roles import Role, project_incident

LIVE_DIR = settings.data_dir / "incidents"
SEED_DIR = settings.data_dir / "seed"
POLICY_PATH = settings.policy_dir / "citinel-policy.yaml"
STATIC_DIR = settings.static_dir


def _resolve_data_dir() -> tuple[Path, str]:
    """Live pipeline output if present, else the committed demo seed.

    Returns the directory AND which one it is, because the difference is
    load-bearing and must never be invisible: `data/incidents/` is gitignored
    live output that a fresh deployment does not have, while `data/seed/` is
    the committed corpus slice that ships inside the image. `/api/source`
    exposes this, and every deployment can be asked which it is answering from.
    """
    if (LIVE_DIR / "incidents.jsonl").exists():
        return LIVE_DIR, "live"
    return SEED_DIR, "seed"


#: Module-level so tests can monkeypatch, matching the previous INCIDENTS_DIR.
INCIDENTS_DIR, DATA_SOURCE = _resolve_data_dir()

#: The simulated bank infrastructure this process acts on. One instance for the
#: life of the process so a rollback token issued by one request is honoured
#: by a later one; PIPE-F09 -- nothing here ever touches real infrastructure.
ENDPOINTS = MockEndpoints()

#: In-flight and finished swarm runs started from the console, by incident id.
_SWARM_RUNS: dict[str, dict[str, Any]] = {}
_SWARM_LOCK = threading.Lock()

app = FastAPI(
    title="CITINEL",
    description="Caught. Cited. Gated. Actioned. Closed.",
    version="0.2.0",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ledger() -> AuditLedger:
    return AuditLedger(INCIDENTS_DIR / "ledger.jsonl", sink=LyzrLedgerMirror())


def _incidents() -> list:
    return load_incidents(INCIDENTS_DIR / "incidents.jsonl")


def _incident(incident_id: str):
    for inc in _incidents():
        if inc.incident_id == incident_id:
            return inc
    raise HTTPException(404, f"no incident {incident_id}")


def _chains() -> dict[str, list]:
    """Every case's ledger frames, from one pass over the file."""
    path = INCIDENTS_DIR / "ledger.jsonl"
    out: dict[str, list] = {}
    if not path.exists():
        return out
    for e in AuditLedger(path).entries():
        out.setdefault(e.case_id, []).append(e)
    return out


def _overlay(inc_dict: dict[str, Any], chain: list, swarm: dict[str, Any] | None) -> dict[str, Any]:
    """The record as the ledger says it stands, plus the swarm's summary."""
    derived = derive_state(inc_dict["state"], chain)
    inc_dict["state"] = derived["state"]
    inc_dict["base_state"] = derived["base_state"]
    inc_dict["state_basis"] = derived["basis"]
    inc_dict["swarm"] = swarm
    return inc_dict


@app.middleware("http")
async def _never_serve_a_stale_console(request, call_next):
    """Revalidate every console file on every load.

    The dashboard is plain files served straight from disk, and StaticFiles
    sends no Cache-Control. A browser then applies heuristic freshness (about
    ten percent of the file's age since Last-Modified), so a judge who opened
    the console yesterday keeps yesterday's api.js and screens for hours after
    a deploy -- dashboard/static/DEPLOY.md names this exact defect, and the
    first live-wiring pass hit it locally within minutes. `no-cache` means
    "revalidate before use", not "never cache": StaticFiles' ETag and
    Last-Modified turn that into a 304 round trip, never a re-download. The
    JSON routes are left alone; they are fetched by the pages with their own
    timeouts and are not what goes stale.
    """
    response = await call_next(request)
    path = request.url.path
    if not path.startswith("/api/") and path != "/healthz":
        response.headers.setdefault("Cache-Control", "no-cache")
    return response


# --- liveness and provenance ---------------------------------------------------

@app.get("/healthz")
def healthz() -> dict:
    """Render's health check target. 200 with no dependency on the pipeline
    having run yet, so the service comes up clean even before anything exists."""
    return {"status": "ok", "service": "citinel-web"}


@app.get("/api/source")
def data_source() -> dict:
    """Which corpus this deployment is answering from, and whether it loaded.

    Exists because "no incidents" and "incidents not shipped" are different
    facts that both used to render as a 200 with an empty list. A deployment
    that silently serves nothing looks identical to a quiet night in the SOC;
    this endpoint makes the difference explicit and is what the UI's data-source
    badge reads rather than inferring liveness from an empty array.
    """
    incidents_file = INCIDENTS_DIR / "incidents.jsonl"
    ledger_file = INCIDENTS_DIR / "ledger.jsonl"
    return {
        "source": DATA_SOURCE,
        "description": {
            "live": "live pipeline output from data/incidents/",
            "seed": "committed demo corpus slice from data/seed/ (BOTS v1, CC0)",
        }[DATA_SOURCE],
        "incidents_file_present": incidents_file.exists(),
        "ledger_file_present": ledger_file.exists(),
        "incident_count": len(load_incidents(incidents_file)),
        "swarm_results": sorted(summaries(INCIDENTS_DIR).keys()),
        "context_gathered": sorted(p.stem for p in (INCIDENTS_DIR / "context").glob("*.json")) if (INCIDENTS_DIR / "context").is_dir() else [],
        "swarm_credentials": settings.has_swarm_credentials,
        "ui_swarm_enabled": settings.ui_swarm_enabled,
    }


# --- the read model ------------------------------------------------------------

@app.get("/api/incidents")
def list_incidents(summary: bool = False) -> list[dict]:
    """Every incident, with its state derived from the ledger and the swarm's
    summary attached. `summary=true` drops the findings (INC-0417 alone carries
    2,487 with their raw log lines, ~4 MB) for screens that only need the row."""
    chains, swarm = _chains(), summaries(INCIDENTS_DIR)
    out = []
    for inc in _incidents():
        d = _overlay(inc.as_dict(), chains.get(inc.incident_id, []), swarm.get(inc.incident_id))
        if summary:
            d.pop("findings", None)
        out.append(d)
    return out


@app.get("/api/incidents/{incident_id}")
def get_incident(
    incident_id: str,
    expand: bool = False,
    x_citinel_role: str | None = Header(default=None),
) -> dict:
    """One incident, projected at the caller's working depth.

    The role arrives in the X-Citinel-Role header and is SELF-ASSERTED --
    there is no authentication model yet (SDD Section 22 Q10, open). That is
    acceptable here and only here because this is depth adaptation, not
    access control: `expand=true` returns full depth to anyone, so nothing is
    being withheld from anyone. Do not extend this header to gate anything
    that actually needs protecting until Q10 is answered with a real auth
    model. See policy/roles.py for the full reasoning.
    """
    inc = _incident(incident_id)
    chains, swarm = _chains(), summaries(INCIDENTS_DIR)
    d = _overlay(inc.as_dict(), chains.get(incident_id, []), swarm.get(incident_id))
    role = Role.parse(x_citinel_role)
    return project_incident(d, role, expand=expand).as_dict()


@app.get("/api/incidents/{incident_id}/audit")
def get_audit_chain(incident_id: str) -> list[dict]:
    """SDD Section 16 finding 4: full chain reconstruction from the case id."""
    chain = AuditLedger(INCIDENTS_DIR / "ledger.jsonl").entries_for(incident_id)
    if not chain:
        raise HTTPException(404, f"no audit entries for {incident_id}")
    return [e.as_dict() for e in chain]


@app.get("/api/incidents/{incident_id}/verdict")
def get_verdict(incident_id: str) -> dict:
    """The swarm's persisted result: triage, correlation, the cited verdict,
    the proposals, what was dropped, and the run's own cost. 404 until a run
    has been saved -- the deterministic findings stand alone until then, and
    the console must say so rather than draw a verdict that does not exist."""
    _incident(incident_id)
    d = load_result(incident_id, INCIDENTS_DIR)
    if d is None:
        raise HTTPException(404, f"no persisted swarm result for {incident_id}; "
                                 f"POST /api/incidents/{incident_id}/swarm to run it")
    d["runs"] = load_runs(incident_id, INCIDENTS_DIR)
    return d


@app.get("/api/incidents/{incident_id}/draft")
def get_draft(incident_id: str, kind: str = "certin") -> dict:
    """A drafted report, plus the guard screen a human reviewer needs before
    signing it. CITINEL's own deterministic screen always runs; Lyzr adds an
    independent second opinion only when configured. We draft, we never file."""
    inc = _incident(incident_id)
    drafter = draft_certin if kind == "certin" else draft_dpdp
    draft = drafter(inc)
    evidence = "\n".join(f.evidence_raw for f in inc.findings if f.evidence_raw)
    guard = LyzrGuard().screen(draft, extra_evidence=evidence)
    # a second Lyzr agent reads the drafted fields and says which a human should
    # not sign as they stand; not_configured until its id is set
    review = review_draft(draft)
    return {"draft": draft.as_dict(), "rendered": render_text(draft),
            "guard": guard.as_dict(), "review": review}


@app.get("/api/policy")
def get_policy() -> dict:
    gate = PolicyGate(POLICY_PATH)
    return {"name": gate.name, "version": gate.version,
            "policy_sha256": gate.policy_sha256, "clauses": gate.table()}


@app.get("/api/ledger/verify")
def verify_ledger() -> dict:
    """Two independent integrity checks, reported separately on purpose.

    `chain` is the local hash chain: it proves no entry was edited in place.
    It cannot prove the file was not replaced wholesale, because a rewritten
    chain verifies perfectly against itself. `witness` is the external Lyzr
    mirror, which covers exactly that blind spot and nothing else. They are
    not merged into one boolean.
    """
    ledger = AuditLedger(INCIDENTS_DIR / "ledger.jsonl")
    ok, message = ledger.verify_chain()
    witness = LyzrLedgerMirror().compare(ledger)
    return {"intact": ok, "message": message, "witness": witness.as_dict()}


@app.get("/api/eval")
def get_eval() -> dict:
    """The credibility screen's data source (Eval.dc.html).

    Deliberately serves the harness's UNMEASURED entries alongside its
    measurements. A false-positive rate the system has not earned is exactly
    what this endpoint exists to refuse to supply. When the harness or its
    inputs are not shipped (the deployed image carries neither data/cache nor
    evals/), the committed report in data/seed/ is served and labelled as such.
    """
    import importlib.util
    import sys as _sys

    harness_path = settings.evals_dir / "harness" / "run.py"
    if harness_path.exists():
        try:
            spec = importlib.util.spec_from_file_location("citinel_eval_harness", harness_path)
            harness = importlib.util.module_from_spec(spec)
            _sys.modules[spec.name] = harness          # @dataclass needs this, see cli.py
            spec.loader.exec_module(harness)
            report = harness.build_report().as_dict()
            report["served_from"] = "harness"
            return report
        except Exception as e:  # inputs missing, most likely
            last_error = str(e)
    else:
        last_error = "eval harness not available in this deployment"
    cached = SEED_DIR / "eval-report.json"
    if cached.exists():
        import json as _json
        report = _json.loads(cached.read_text(encoding="utf-8"))
        report["served_from"] = "seed cache (harness could not run here: " + last_error + ")"
        return report
    raise HTTPException(503, last_error)


@lru_cache(maxsize=1)
def _corpus_static() -> dict[str, Any]:
    """The pinned Sigma corpus as shipped on this host; counted once."""
    from citinel.detect.sigma_engine import SIGMA_RELEASE
    root = settings.data_dir / "raw" / "sigma" / "rules"
    out: dict[str, Any] = {"release": SIGMA_RELEASE, "rules_shipped": root.is_dir(),
                           "rules_total": None, "by_dir": {}, "version": {}}
    if root.is_dir():
        by_dir = {d.name: sum(1 for _ in d.rglob("*.yml")) for d in root.iterdir() if d.is_dir()}
        out["by_dir"] = by_dir
        out["rules_total"] = sum(by_dir.values())
        v = root / "version.txt"
        if v.exists():
            for line in v.read_text(encoding="utf-8").splitlines():
                if ":" in line:
                    k, _, val = line.partition(":")
                    out["version"][k.strip().lower().replace(" ", "_")] = val.strip()
    return out


@app.get("/api/corpus")
def get_corpus() -> dict:
    """What the deterministic layer is running and what it actually fired.

    The corpus facts (release pin, rule count) come from the shipped rules
    directory when it is present and are reported as not shipped when it is
    not; the fired-rule table is computed from the incident records, so it is
    the same on every deployment. No accession bench: nothing drafts rules yet.
    """
    static = dict(_corpus_static())
    fired: dict[tuple[str, str], dict[str, Any]] = {}
    anomaly_kinds: Counter = Counter()
    techniques: set[str] = set()
    for inc in _incidents():
        for i, f in enumerate(inc.findings):
            techniques.update(f.techniques)
            if f.source != "sigma":
                anomaly_kinds[(f.detail or {}).get("kind", "unknown")] += 1
                continue
            key = ((f.detail or {}).get("rule_id", ""), f.title)
            row = fired.setdefault(key, {
                "rule_id": key[0], "title": f.title, "level": f.level, "count": 0,
                "techniques": set(), "hosts": set(), "incidents": set(),
                "first_seen": f.timestamp, "last_seen": f.timestamp,
                "example": {"incident_id": inc.incident_id, "finding_index": i},
            })
            row["count"] += 1
            row["techniques"].update(f.techniques)
            row["hosts"].add(f.host)
            row["incidents"].add(inc.incident_id)
            row["first_seen"] = min(row["first_seen"], f.timestamp)
            row["last_seen"] = max(row["last_seen"], f.timestamp)
    rows = sorted(fired.values(), key=lambda r: -r["count"])
    for r in rows:
        r["techniques"] = sorted(r["techniques"])
        r["hosts"] = sorted(r["hosts"])
        r["incidents"] = sorted(r["incidents"])
    static.update({
        "fired": rows,
        "distinct_rules_fired": len(rows),
        "detections_total": sum(r["count"] for r in rows),
        "anomaly_kinds": dict(anomaly_kinds),
        "techniques_observed": sorted(techniques),
    })
    return static


#: Recorded once at import: lets an operator tell "the process restarted after
#: I saved the variables" from "it never did" (both otherwise look identical).
_PROCESS_STARTED_AT = datetime.now(timezone.utc).isoformat(timespec="seconds")

#: The variables this service reads for credentials and model ids. Fixed by the
#: code, so echoing them back is not echoing anything an operator typed.
_EXPECTED_ENV = (
    "CITINEL_ANTHROPIC_API_KEY", "CITINEL_ANTHROPIC_WORKSPACE_ID", "CITINEL_TAVILY_API_KEY",
    "CITINEL_VIRUSTOTAL_API_KEY", "CITINEL_ABUSEIPDB_API_KEY", "CITINEL_TRIAGE_MODEL",
    "CITINEL_REASONING_MODEL", "CITINEL_N8N_WEBHOOK_URL", "CITINEL_SWYTCHCODE_API_KEY",
    "CITINEL_LYZR_API_KEY", "CITINEL_LYZR_GUARD_URL", "CITINEL_LYZR_AGENT_ID",
    "CITINEL_LYZR_TRIAGE_AGENT_ID", "CITINEL_LYZR_REVIEW_AGENT_ID", "CITINEL_LYZR_HANDOVER_AGENT_ID",
)
#: Set by the blueprint / Dockerfile with values; their presence proves the
#: platform's environment reaches the process at all.
_BLUEPRINT_ENV = (
    "CITINEL_ROLE", "CITINEL_SIMULATED_ENDPOINTS_ONLY", "CITINEL_DEFAULT_AUTONOMY",
    "CITINEL_AUTO_SWARM", "CITINEL_AUTO_SWARM_MAX_PER_CYCLE", "CITINEL_DATABASE_URL",
    "CITINEL_DATA_DIR", "CITINEL_POLICY_DIR", "CITINEL_STATIC_DIR", "CITINEL_EVALS_DIR",
)


def _presence(value: str | None) -> str:
    return "absent" if value is None else ("blank" if value.strip() == "" else "set")


def _environment_report() -> dict[str, Any]:
    """What the running process can see of its configuration, described ONLY
    in names the code itself defines: for each expected variable whether it is
    set, blank or absent; which conventional unprefixed spellings exist (so an
    operator who set ANTHROPIC_API_KEY is told the name this service reads);
    for an unknown CITINEL_* name only the closest expected name and a
    similarity, never the unknown name itself; and for each dotenv location
    whether it exists and which expected keys it defines. No value, length,
    hash or operator-chosen string ever leaves this function -- the route is
    public, and a diagnostic must not double as a secret oracle."""
    import difflib
    env = os.environ
    expected = {name: _presence(env.get(name)) for name in _EXPECTED_ENV}
    blueprint = {name: _presence(env.get(name)) for name in _BLUEPRINT_ENV}
    unprefixed_seen = sorted(
        name[len("CITINEL_"):] for name in _EXPECTED_ENV if env.get(name[len("CITINEL_"):]) is not None)
    known = set(_EXPECTED_ENV) | set(_BLUEPRINT_ENV)
    unknown: list[dict[str, Any]] = []
    for name in sorted(env):
        if not name.upper().startswith("CITINEL_") or name in known:
            continue
        match = difflib.get_close_matches(name.upper(), _EXPECTED_ENV, n=1, cutoff=0.0)
        ratio = difflib.SequenceMatcher(None, name.upper(), match[0]).ratio() if match else 0.0
        unknown.append({"closest_expected": match[0] if match else None, "similarity": round(ratio, 2)})

    env_file = settings.model_config.get("env_file")
    paths = [Path(str(p)) for p in (env_file if isinstance(env_file, (tuple, list)) else [env_file]) if p]
    dotenv: list[dict[str, Any]] = []
    for p in paths:
        row: dict[str, Any] = {"path": str(p), "present": p.is_file()}
        if row["present"]:
            try:
                from dotenv import dotenv_values
                values = dotenv_values(p)
                row["defines"] = {k: _presence(values.get(k)) for k in _EXPECTED_ENV if k in values}
            except Exception as exc:  # unreadable or unparsable: say so, show nothing
                row["defines"] = None
                row["error"] = type(exc).__name__
        dotenv.append(row)
    secrets_dir = Path("/etc/secrets")
    try:
        other_secret_files = sum(1 for p in secrets_dir.iterdir() if not p.name.startswith("..")) \
            if secrets_dir.is_dir() else 0
    except OSError:
        other_secret_files = 0
    return {
        "platform": {
            # Presence only, like everything else in this function: an
            # earlier cut returned these three verbatim (an adversarial
            # review caught it, 2 Sep 2026) -- RENDER_SERVICE_NAME and
            # RENDER_EXTERNAL_URL are operator-chosen strings (the latter can
            # reveal the true onrender.com origin behind a custom domain),
            # and RENDER_GIT_COMMIT is literally a hash fingerprinting the
            # exact deployed code. None of that belongs on a public route.
            "render_service_name": _presence(env.get("RENDER_SERVICE_NAME")),
            "render_git_commit": _presence(env.get("RENDER_GIT_COMMIT")),
            "render_external_url": _presence(env.get("RENDER_EXTERNAL_URL")),
            "process_started_at": _PROCESS_STARTED_AT,
        },
        "expected": expected,
        "blueprint": blueprint,
        "unprefixed_seen": unprefixed_seen,
        "unprefixed_hint": "this service reads only the CITINEL_-prefixed spelling" if unprefixed_seen else None,
        # Presence data alone cannot tell "never configured" apart from
        # "configured on a different Render service, or in an Environment
        # Group this service isn't linked to" -- both look identical from
        # inside this process. When the platform clearly reaches this service
        # (the blueprint's own vars are set) but not one expected credential
        # is visible anywhere this process looks, say so plainly rather than
        # let the report imply it is conclusive.
        "credential_source_hint": (
            "platform env reaches this service (blueprint vars are set) but none of the expected "
            "credential names are visible here or in a dotenv file -- this looks identical to "
            "'never configured' and to 'configured on a different Render service, or in an "
            "Environment Group not linked to this one'; check the Render dashboard's Environment "
            "tab for this exact service"
        ) if any(v == "set" for v in blueprint.values()) and not (
            any(v == "set" for v in expected.values())
            or any(row.get("defines") and any(v == "set" for v in row["defines"].values()) for row in dotenv)
        ) else None,
        "unknown_citinel_names": unknown,
        "dotenv": dotenv,
        "secret_env_file_present": (secrets_dir / ".env").is_file(),
        "other_secret_files": other_secret_files,
        "note": "fixed names only: no value, length, hash or operator-chosen string is ever exposed",
    }


@app.get("/api/connectors")
def get_connectors() -> dict:
    """Which external services this deployment is actually configured to
    reach (presence only, never a value), the safety rails in force, the
    simulated infrastructure's current state, and the policy in force."""
    s = settings
    lyzr_ok = bool(s.lyzr_api_key and s.lyzr_guard_url and s.lyzr_agent_id)

    def c(name: str, role: str, configured: bool, detail: str) -> dict[str, Any]:
        return {"name": name, "role": role, "configured": configured, "detail": detail}

    gate = PolicyGate(POLICY_PATH)
    return {
        "rails": {
            "simulated_endpoints_only": s.simulated_endpoints_only,
            "default_autonomy": s.default_autonomy.value,
            "auto_swarm": s.auto_swarm,
            "auto_swarm_max_per_cycle": s.auto_swarm_max_per_cycle,
            "ui_swarm_enabled": s.ui_swarm_enabled,
        },
        "connectors": [
            c("anthropic", "the swarm's models", s.has_swarm_credentials,
              f"triage {s.triage_model or 'unset'} · reasoning {s.reasoning_model or 'unset'}"),
            c("tavily", "OSINT lookups for the Enrichment Squad", bool(s.tavily_api_key), "web search"),
            c("virustotal", "file and IP reputation for the Enrichment Squad", bool(s.virustotal_api_key), "reputation"),
            c("abuseipdb", "IP abuse reports for the Enrichment Squad", bool(s.abuseipdb_api_key), "reputation"),
            c("lyzr", "PII second opinion, swarm observer, ledger witness", lyzr_ok,
              "key + guard url + agent id all required" if not lyzr_ok else "all three set"),
            c("lyzr-triage", "independent triage lane beside the Router's, on the ledger", bool(lyzr_ok and s.lyzr_triage_agent_id), "CITINEL_LYZR_TRIAGE_AGENT_ID"),
            c("lyzr-review", "drafted-field review before sign-off", bool(lyzr_ok and s.lyzr_review_agent_id), "CITINEL_LYZR_REVIEW_AGENT_ID"),
            c("lyzr-handover", "shift-handover note from the ledger", bool(lyzr_ok and s.lyzr_handover_agent_id), "CITINEL_LYZR_HANDOVER_AGENT_ID"),
            c("n8n", "post-sign-off automation (notify, export, ticket)", bool(s.n8n_webhook_url), "webhook"),
            c("swytchcode", "ticketing + comms after an executed action", bool(s.swytchcode_api_key), "ecosystem apis"),
        ],
        "mock_endpoints": {
            "isolated_hosts": sorted(ENDPOINTS.isolated_hosts),
            "blocked_ips": sorted(ENDPOINTS.blocked_ips),
            "quarantined": sorted(ENDPOINTS.quarantined),
            "disabled_accounts": sorted(ENDPOINTS.disabled_accounts),
            "revoked_sessions": sorted(ENDPOINTS.revoked_sessions),
            "notifications": list(ENDPOINTS.notifications[-20:]),
        },
        "policy": {"name": gate.name, "version": gate.version,
                   "policy_sha256": gate.policy_sha256, "clauses": gate.table()},
        "environment": _environment_report(),
    }


# --- operations: the same code paths the CLI runs -----------------------------

def _build_pipeline(ledger: AuditLedger):
    """Seam for tests; the real builder verifies the models live (L9)."""
    from citinel.agents.build import build_pipeline
    return build_pipeline(ledger)


def _swarm_worker(incident_id: str, inc) -> None:
    from citinel.agents.store import save_result
    run = _SWARM_RUNS[incident_id]
    try:
        pipeline = _build_pipeline(_ledger())
        if not pipeline.available:
            raise RuntimeError("no Anthropic credentials on this deployment; "
                               "the deterministic findings stand alone")
        result = pipeline.run(inc)
        save_result(result, INCIDENTS_DIR)
        # an independent second opinion on the lane, from a separate Lyzr agent,
        # recorded beside the Router's decision (not_configured when no id is set)
        opinion = triage_second_opinion(inc, result.as_dict(), _ledger())
        annotate_result(incident_id, INCIDENTS_DIR, "lyzr_triage", opinion)
        run.update(mode=result.mode.value, banner=result.banner(),
                   summary=summary_of(result.as_dict()))
    except Exception as e:  # recorded, never raised into a thread
        run["error"] = str(e)
    finally:
        run["running"] = False
        run["finished_at"] = _now()


def _swarm_status(incident_id: str) -> dict[str, Any]:
    base = {"incident_id": incident_id, "running": False, "started_at": None,
            "finished_at": None, "mode": None, "banner": None, "error": None, "summary": None}
    base.update(_SWARM_RUNS.get(incident_id, {}))
    base["has_result"] = load_result(incident_id, INCIDENTS_DIR) is not None
    return base


@app.post("/api/incidents/{incident_id}/swarm", status_code=202)
def run_swarm(incident_id: str, body: dict | None = None) -> dict:
    """Run the swarm on this incident, live, in the background.

    Real model spend every time, so the body must say {"confirm": true}; one
    run at a time per process; 503 when this deployment has no credentials
    rather than a fake result. Poll /swarm/status, then read /verdict.
    """
    if not settings.ui_swarm_enabled:
        raise HTTPException(403, "running the swarm from the console is disabled on this deployment")
    inc = _incident(incident_id)
    if not settings.has_swarm_credentials:
        raise HTTPException(503, "no Anthropic credentials configured on this deployment; "
                                 "the deterministic findings stand alone")
    if not (body or {}).get("confirm"):
        raise HTTPException(400, 'each run is real model spend; send {"confirm": true} to start it')
    with _SWARM_LOCK:
        if any(r.get("running") for r in _SWARM_RUNS.values()):
            raise HTTPException(409, "a swarm run is already in progress; one at a time")
        _SWARM_RUNS[incident_id] = {"incident_id": incident_id, "running": True,
                                    "started_at": _now(), "finished_at": None,
                                    "mode": None, "banner": None, "error": None, "summary": None}
    threading.Thread(target=_swarm_worker, args=(incident_id, inc), daemon=True).start()
    return _swarm_status(incident_id)


@app.get("/api/incidents/{incident_id}/swarm/status")
def swarm_status(incident_id: str) -> dict:
    _incident(incident_id)
    return _swarm_status(incident_id)


def _tavily():
    """Seam for tests; the real connector spends credits and caches by query."""
    from citinel.connectors.base import EnrichmentCache
    from citinel.connectors.enrichment import TavilyConnector
    return TavilyConnector(EnrichmentCache(settings.data_dir / "cache" / "enrichment"))


@app.get("/api/incidents/{incident_id}/context")
def get_context(incident_id: str) -> dict:
    """Public context gathered for this record's verdict: per technique and
    per rule, the query, the URLs, the fetch time. 404 until gathered."""
    _incident(incident_id)
    d = load_context(incident_id, INCIDENTS_DIR)
    if d is None:
        raise HTTPException(404, f"no public context gathered for {incident_id}; "
                                 f"POST /api/incidents/{incident_id}/context to gather it")
    return d


@app.post("/api/incidents/{incident_id}/context")
def gather_public_context(incident_id: str, body: dict | None = None) -> dict:
    """Search the open web (Tavily) for the techniques the correlator named and
    the rules that fired most, and persist the result. One credit per query
    that the enrichment cache does not already hold; the body must confirm.
    Nothing gathered becomes evidence: it is context, cited with URL and time."""
    inc = _incident(incident_id)
    if not settings.tavily_api_key:
        raise HTTPException(503, "no Tavily key configured on this deployment")
    if not (body or {}).get("confirm"):
        raise HTTPException(400, 'each query is a Tavily credit; send {"confirm": true} to gather')
    verdict = load_result(incident_id, INCIDENTS_DIR)
    return gather_context(inc, verdict, settings.data_dir / "cache" / "enrichment",
                          INCIDENTS_DIR, connector=_tavily())


def _handover_path(incident_id: str) -> Path:
    return INCIDENTS_DIR / "handover" / f"{incident_id}.json"


@app.get("/api/incidents/{incident_id}/handover")
def get_handover(incident_id: str) -> dict:
    """The shift-handover note a Lyzr agent wrote from the ledger's own frames.
    404 until generated; the note names the frames it was written from."""
    _incident(incident_id)
    p = _handover_path(incident_id)
    if not p.exists():
        raise HTTPException(404, f"no handover note for {incident_id}; POST /api/incidents/{incident_id}/handover to write one")
    import json as _json
    return _json.loads(p.read_text(encoding="utf-8"))


@app.post("/api/incidents/{incident_id}/handover")
def write_handover(incident_id: str, body: dict | None = None) -> dict:
    """Ask the handover agent for a plain summary of where this record stands,
    from its last frames, and persist it. Honest degradation: not_configured
    without an agent id, unavailable when the call fails; never a made-up note."""
    inc = _incident(incident_id)
    if not (body or {}).get("confirm"):
        raise HTTPException(400, 'each note is a Lyzr call; send {"confirm": true} to write one')
    chains = _chains()
    d = _overlay(inc.as_dict(), chains.get(incident_id, []), summaries(INCIDENTS_DIR).get(incident_id))
    note = handover_summary(d, chains.get(incident_id, []), d.get("swarm"))
    note.update({"incident_id": incident_id, "state": d["state"], "written_at": _now(),
                 "frames_used": min(15, len([e for e in chains.get(incident_id, []) if e.kind not in ("detection_added", "escalation_added")]))})
    p = _handover_path(incident_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    import json as _json
    p.write_text(_json.dumps(note, ensure_ascii=False, indent=1), encoding="utf-8")
    return note


@app.post("/api/actions/execute")
def execute_action(body: dict) -> dict:
    """Run one proposal through the gate and, if it clears, carry it out on the
    simulated endpoints -- the CLI's `policy execute`, as HTTP. The gate's
    decision is written to the ledger whatever it says; an executed action
    gets its receipt and rollback token; a denied one comes back 403 with the
    clause that denied it; an approval-held one executes only when the body
    names an approver, and that approval is a ledger frame too.
    """
    incident_id = body.get("incident_id")
    action_class = body.get("action_class")
    if not incident_id or not action_class:
        raise HTTPException(400, "incident_id and action_class are required")
    _incident(incident_id)
    target = str(body.get("target") or "unspecified")
    raw_assets = body.get("assets_affected")
    try:
        # 0 is a real value here: the policy's "touches no bank asset" classes cap at 0,
        # so a falsy-default would silently turn every such proposal into an escalation
        assets = 1 if raw_assets is None or raw_assets == "" else int(raw_assets)
    except (TypeError, ValueError):
        raise HTTPException(400, "assets_affected must be an integer")
    if assets < 0:
        raise HTTPException(400, "assets_affected cannot be negative")
    approver = body.get("approver")

    decision = PolicyGate(POLICY_PATH).check(action_class, assets, target)
    ledger = _ledger()
    executor = ActionExecutor(ENDPOINTS, ledger)
    try:
        receipt = executor.execute(incident_id, decision, target)
        if receipt.status == "awaiting_approval" and approver:
            receipt = executor.approve_and_execute(incident_id, decision, target, str(approver))
    except ExecutionRefused as e:
        raise HTTPException(403, {"refused": str(e), "decision": decision.as_dict()})

    swytch: list[dict[str, Any]] = []
    if receipt.status == "executed":
        for r in SwytchcodeExecutor().execute_for_decision(decision, target, incident_id):
            ledger.append(incident_id, "swytchcode", "tool_call", r.as_dict())
            swytch.append(r.as_dict())
    chain = ledger.entries_for(incident_id)
    return {"decision": decision.as_dict(), "receipt": receipt.as_dict(),
            "swytchcode": swytch, "simulated": True,
            "state": derive_state("caught", chain)}


@app.post("/api/actions/deny")
def deny_action(body: dict) -> dict:
    """A human refuses a proposal. Nothing executes; the refusal itself is a
    ledger frame carrying the name and the reason, because a dead end on the
    record is still a record and a later reader must see who decided it."""
    incident_id = body.get("incident_id")
    action_class = body.get("action_class")
    by = str(body.get("by") or "").strip()
    reason = str(body.get("reason") or "").strip()
    if not incident_id or not action_class or not by or not reason:
        raise HTTPException(400, "incident_id, action_class, by and reason are required")
    _incident(incident_id)
    ledger = _ledger()
    ledger.append(incident_id, by, "decision", {
        "decision": "proposal_denied", "action_class": action_class,
        "target": str(body.get("target") or ""), "reason": reason, "simulated": True,
    })
    return {"denied": True, "by": by, "reason": reason,
            "state": derive_state("caught", ledger.entries_for(incident_id))}


@app.post("/api/actions/rollback/{token}")
def rollback_action(token: str, body: dict | None = None) -> dict:
    """Reverse an executed action by its token. The simulated endpoints keep
    their state in this process, so a token is honoured for the life of the
    service and an unknown one is a 404, never a pretend success."""
    body = body or {}
    incident_id = body.get("incident_id")
    if not incident_id:
        raise HTTPException(400, "incident_id is required")
    _incident(incident_id)
    executor = ActionExecutor(ENDPOINTS, _ledger())
    try:
        receipt = executor.rollback(incident_id, token, str(body.get("actor") or "console"))
    except (KeyError, ExecutionRefused) as e:
        raise HTTPException(404, f"no rollback for token {token}: {e}")
    return {"receipt": receipt.as_dict(), "simulated": True}


@app.post("/api/incidents/{incident_id}/signoff")
def sign_off(incident_id: str, body: dict) -> dict:
    """The human sign-off moment, as HTTP: log it, then fire n8n's post-sign-off
    flow. n8n is glue, never the gate; without a webhook it reports
    not_configured and the sign-off still stands on the ledger."""
    signed_by = str(body.get("signed_by") or "").strip()
    if not signed_by:
        raise HTTPException(400, "signed_by is required")
    inc = _incident(incident_id)
    # The human's own answers to the fields the drafter refuses to guess (loss, law
    # enforcement, personal data, signatory) ride on the sign-off frame, so the
    # ledger holds what the signer asserted, not only that they signed. Capped and
    # stringified: this is a record of a decision, not a document store.
    answers_in = body.get("answers") or {}
    answers = {}
    if isinstance(answers_in, dict):
        for k, v in list(answers_in.items())[:24]:
            answers[str(k)[:64]] = str(v)[:500]
    payload = {"incident_id": incident_id, "signed_by": signed_by}
    if answers:
        payload["answers"] = answers
    kind = str(body.get("draft_kind") or "").strip()
    if kind:
        payload["draft_kind"] = kind[:16]
    if body.get("attested") is not None:
        payload["attested"] = bool(body.get("attested"))
    ledger = _ledger()
    ledger.append(incident_id, signed_by, "human_signoff", payload)
    result = dispatch_signed(inc, signed_by)
    ledger.append(incident_id, "n8n", "tool_call", result.as_dict())
    chain = ledger.entries_for(incident_id)
    signoff = [e for e in chain if e.kind == "human_signoff" and e.actor == signed_by][-1]
    return {"signed_by": signed_by, "dispatch": result.as_dict(), "seq": signoff.seq,
            "entry_hash": signoff.entry_hash, "ts": signoff.ts, "answers": answers,
            "state": derive_state("caught", chain)}


@app.post("/api/incidents/{incident_id}/reopen")
def reopen(incident_id: str, body: dict) -> dict:
    """Reopen a closed record for re-investigation, as a ledger frame.

    Nothing is edited: the closure stays on the reel and an explicit
    `state_transition` back to caught follows it, carrying who reopened it and
    why. The Queue puts the record back on the belt, the swarm can run again,
    and the whole history remains one contiguous chain.
    """
    by = str(body.get("by") or "").strip()
    reason = str(body.get("reason") or "").strip()
    if not by or not reason:
        raise HTTPException(400, "by and reason are required; a reopen is a named decision")
    _incident(incident_id)
    ledger = _ledger()
    chain = ledger.entries_for(incident_id)
    before = derive_state("caught", chain)["state"]
    if before not in ("closed", "closed_benign"):
        raise HTTPException(409, f"{incident_id} is {before}, not closed; nothing to reopen")
    ledger.append(incident_id, by, "state_transition",
                  {"to": "caught", "from": before, "reopened": True, "reason": reason})
    return {"incident_id": incident_id, "reopened_by": by, "reason": reason,
            "state": derive_state("caught", ledger.entries_for(incident_id))}


# --- the glass-box UI ---------------------------------------------------------
# Mounted last, deliberately: StaticFiles at "/" is a catch-all, so every
# /api/* and /healthz route above must already be registered or the mount
# would shadow them. html=True serves Entry.dc.html-style pages directly and
# is what makes the deployed Render service actually show the console rather
# than only answering JSON.
if STATIC_DIR.is_dir():
    # "/" must be an explicit route, registered BEFORE the mount below.
    # StaticFiles(html=True) serves index.html at a directory root, and this
    # console has no index.html -- its entry point is Entry.dc.html. Without
    # this redirect the root URL 404s, which is precisely the URL the deck's
    # QR code points at: a judge scanning it would get a blank error page.
    @app.get("/", include_in_schema=False)
    def _root() -> RedirectResponse:
        return RedirectResponse(url="/Entry.dc.html")

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="ui")
