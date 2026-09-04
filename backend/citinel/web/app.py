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
import secrets

import threading
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from citinel.agents.context import gather_context, load_context
from citinel.agents.pipeline import MAX_EVIDENCE_FINDINGS
from citinel.agents.brief import load_brief, poll_brief, start_brief
from citinel.agents.visual import load_visuals, read_image
from citinel.agents.sweep import load_sweep, run_sweep
from citinel.agents.store import annotate_result, load_result, load_runs, summaries, summary_of
from citinel.connectors.lyzr_agents import (
    corpus_advisory, handover_summary, response_review, review_draft,
    triage_second_opinion, verdict_audit,
)
from citinel.audit.ledger import AuditLedger
from citinel.compliance.drafter import draft_certin, draft_dpdp, render_text
from citinel.config import settings
from citinel.web.demo_capture import find_fixture, load_fixtures
from citinel.connectors.lyzr import LyzrGuard, LyzrLedgerMirror
from citinel.connectors.n8n import dispatch_signed
from citinel.connectors.startuped import SIGNALS, emit_quietly
from citinel.connectors.n8n_api import list_executions, resume as n8n_resume
from citinel.connectors.swytchcode import SwytchcodeExecutor
from citinel.incidents.builder import load_incidents
from citinel.incidents.state import derive_state
from citinel.policy.actions import ActionExecutor, ExecutionRefused, MockEndpoints
from citinel.policy.gate import PolicyGate
from citinel.policy.roles import Role, project_incident

LIVE_DIR = settings.data_dir / "incidents"
SEED_DIR = settings.data_dir / "seed"
#: Step 14 -- see demo_capture.py's module docstring for what this is and is
#: not. Ships inside data/seed/ so it is present in the Docker image without a
#: separate COPY line, the same reason eval-report.json and swarm/*.json live
#: there. Loaded once at import; a missing or malformed file means demo mode
#: reports as unavailable rather than failing the service.
DEMO_MANIFEST = load_fixtures(SEED_DIR / "demo-capture.json")
#: Structural, not incidental: even a hand-edited or corrupted manifest file
#: cannot make these servable from a fixture. capture_fixtures() never
#: requests them either, but a test that planted them anyway (adversarially,
#: on purpose) showed relying on that alone was not actually a second layer
#: of defense -- this denylist is the real one.
_NEVER_DEMO = frozenset({"/api/connectors", "/api/ledger/verify", "/api/source"})
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

#: The interactive API console is off unless a deployment asks for it. FastAPI
#: serves /docs, /redoc and /openapi.json to anyone by default, and this API's
#: write routes append to the audit ledger, execute policy-gated actions and
#: spend real model tokens -- so the default shipped a no-tooling, click-through
#: UI for forging ledger frames to every visitor (confirmed live, 200 on all
#: three, 2 Sep 2026). The schema is not a secret, but handing an anonymous
#: caller a Try-It-Out button for the write API is a different thing entirely.
#: CITINEL_API_DOCS=true restores them for local work.
_DOCS = settings.api_docs

app = FastAPI(
    title="CITINEL",
    description="Caught. Cited. Gated. Actioned. Closed.",
    version="0.2.0",
    docs_url="/docs" if _DOCS else None,
    redoc_url="/redoc" if _DOCS else None,
    openapi_url="/openapi.json" if _DOCS else None,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ledger_path() -> Path:
    """The one place the ledger's location is decided.

    Write path and read path must never diverge: a ledger appended in one file
    and verified from another would report a clean chain while the real frames
    went somewhere else. Everything below routes through here.
    """
    return settings.ledger_path or (INCIDENTS_DIR / "ledger.jsonl")


def _artifacts_dir() -> Path:
    """Where runtime artifacts live: swarm results, context, sweeps, handover
    notes, the corpus advisory.

    Separate from the corpus. incidents.jsonl ships baked into the image and
    is read-only; everything a run PRODUCES has to survive a redeploy, and on
    Render the container filesystem does not. Unset means the incidents
    directory, which is exactly today's behaviour everywhere else.
    """
    return settings.artifacts_dir or INCIDENTS_DIR


# Swarm artifacts the disk holds, over the ones baked in the image. The Render
# disk is seeded once, on the container's first boot; a demo incident whose
# verdict was added to data/seed AFTER that boot (INC-0419) therefore lives only
# in the image, and without this fallback its investigation would never appear on
# a redeployed service. The disk wins per incident, so a real run performed on the
# deployment still overrides the shipped one.
def _summaries() -> dict[str, Any]:
    merged = summaries(SEED_DIR)
    merged.update(summaries(_artifacts_dir()))
    return merged


def _load_result(incident_id: str) -> dict[str, Any] | None:
    return load_result(incident_id, _artifacts_dir()) or load_result(incident_id, SEED_DIR)


def _load_runs(incident_id: str) -> list[dict[str, Any]]:
    return load_runs(incident_id, _artifacts_dir()) or load_runs(incident_id, SEED_DIR)


def _ledger() -> AuditLedger:
    return AuditLedger(_ledger_path(), sink=LyzrLedgerMirror())


# Captured once, when the process starts. The demo-live incident's window is
# measured from here, so it is fresh on every deploy and restart (see
# settings.demo_live_incident). Nothing else reads it.
_BOOT_TS = datetime.now(timezone.utc).isoformat()


def _incidents() -> list:
    incs = load_incidents(INCIDENTS_DIR / "incidents.jsonl")
    live_id = (settings.demo_live_incident or "").strip()
    if live_id:
        # Reopen exactly one record for this live session: its six-hour clock
        # starts at boot, so a redeploy on demo morning makes it count down on
        # stage instead of showing a long-closed replay window. Honest, because
        # the served open time IS this session's start; off unless the env names
        # an id, so every other deployment keeps its real historical clock.
        for inc in incs:
            if inc.incident_id == live_id:
                inc.opened_ts = _BOOT_TS
    return incs


def _incident(incident_id: str):
    for inc in _incidents():
        if inc.incident_id == incident_id:
            return inc
    raise HTTPException(404, f"no incident {incident_id}")


def _chains() -> dict[str, list]:
    """Every case's ledger frames, from one pass over the file."""
    path = _ledger_path()
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


@app.middleware("http")
async def _serve_demo_capture(request, call_next):
    """?demo=1 on a GET request replays a captured fixture instead of
    computing live -- Step 14. Deliberately a middleware, not a per-route
    check: it runs before routing, so it can only ever answer a request that
    (a) is a GET, (b) explicitly asked for it, and (c) matches a path this
    deployment actually captured (never /api/connectors, /api/ledger/verify,
    or any write route -- capture_fixtures() only ever issues GETs against
    demo_capture.ROUTES, so no fixture for those can exist to be found here).
    A response served this way carries X-Citinel-Demo so the console can show
    it was a capture, not the live service, and never confuse the two.
    """
    if (request.method == "GET" and request.query_params.get("demo") == "1" and DEMO_MANIFEST
            and request.url.path not in _NEVER_DEMO):
        rest = "&".join(f"{k}={v}" for k, v in request.query_params.multi_items() if k != "demo")
        key = request.url.path + (f"?{rest}" if rest else "")
        fx = find_fixture(DEMO_MANIFEST, key)
        if fx is not None:
            from fastapi.responses import JSONResponse
            resp = JSONResponse(content=fx["body"], status_code=fx["status_code"])
            resp.headers["X-Citinel-Demo"] = "1"
            return resp
    return await call_next(request)


@app.middleware("http")
async def _guard_writes(request, call_next):
    """Every state-changing /api/ route requires a token. Confirmed live,
    2 Sep 2026: with no auth of any kind, an anonymous caller could POST a
    human_signoff naming a real person, and /api/ledger/verify would call
    the resulting hash-chained record "intact" -- an append-only ledger
    proves nothing about who really wrote to it without this.

    Deliberately a middleware, not per-route Depends(): it covers every
    current write route AND any future one without a second place to
    remember, and it runs before routing, so a malformed or unrouted
    request never reaches a handler either. Reads are never touched --
    GET/HEAD/OPTIONS pass straight through regardless of path, because a
    console nobody can browse without a login defeats the entire premise
    of a glass-box audit trail.

    Unset CITINEL_WRITE_TOKEN means writes are OFF, not open: a deployment
    that forgot to set it is a safe read-only demo, never an exposed one.
    That is deliberately a different status (503, "not configured") from a
    present-but-wrong token (401, "wrong credential") -- an operator
    debugging a stuck console needs to tell those apart at a glance.
    """
    if request.method not in ("GET", "HEAD", "OPTIONS") and request.url.path.startswith("/api/"):
        token = settings.write_token
        if not token:
            return JSONResponse(
                {"detail": "write operations are disabled on this deployment "
                            "(CITINEL_WRITE_TOKEN is not configured)"},
                status_code=503,
            )
        supplied = request.headers.get("X-Citinel-Write-Token", "")
        if not supplied or not secrets.compare_digest(supplied, token):
            return JSONResponse(
                {"detail": "write operations require a valid X-Citinel-Write-Token header"},
                status_code=401,
            )
    return await call_next(request)


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
    ledger_file = _ledger_path()
    return {
        "source": DATA_SOURCE,
        "description": {
            "live": "live pipeline output from data/incidents/",
            "seed": "committed demo corpus slice from data/seed/ (BOTS v1, CC0)",
        }[DATA_SOURCE],
        "incidents_file_present": incidents_file.exists(),
        "ledger_file_present": ledger_file.exists(),
        "incident_count": len(load_incidents(incidents_file)),
        "swarm_results": sorted(_summaries().keys()),
        "context_gathered": sorted(p.stem for p in (_artifacts_dir() / "context").glob("*.json")) if (_artifacts_dir() / "context").is_dir() else [],
        "swarm_credentials": settings.has_swarm_credentials,
        "ui_swarm_enabled": settings.ui_swarm_enabled,
        # The incident whose window is measured from this service's boot, if any.
        # The console reads it to default its links to the same record the Render
        # switch made live, so "the demo incident" means one thing across both.
        "demo_live_incident": (settings.demo_live_incident or "").strip() or None,
        "demo_capture": {
            "available": DEMO_MANIFEST is not None,
            "captured_at": DEMO_MANIFEST.get("captured_at") if DEMO_MANIFEST else None,
            "incident_ids": DEMO_MANIFEST.get("incident_ids", []) if DEMO_MANIFEST else [],
            "routes_captured": len(DEMO_MANIFEST.get("routes", {})) if DEMO_MANIFEST else 0,
        },
    }


# --- the read model ------------------------------------------------------------

@app.get("/api/incidents")
def list_incidents(summary: bool = False) -> list[dict]:
    """Every incident, with its state derived from the ledger and the swarm's
    summary attached. `summary=true` drops the findings (INC-0417 alone carries
    2,487 with their raw log lines, ~4 MB) for screens that only need the row."""
    chains, swarm = _chains(), _summaries()
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
    chains, swarm = _chains(), _summaries()
    d = _overlay(inc.as_dict(), chains.get(incident_id, []), swarm.get(incident_id))
    role = Role.parse(x_citinel_role)
    return project_incident(d, role, expand=expand).as_dict()


@app.get("/api/incidents/{incident_id}/audit")
def get_audit_chain(incident_id: str) -> list[dict]:
    """SDD Section 16 finding 4: full chain reconstruction from the case id."""
    chain = AuditLedger(_ledger_path()).entries_for(incident_id)
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
    d = _load_result(incident_id)
    if d is None:
        raise HTTPException(404, f"no persisted swarm result for {incident_id}; "
                                 f"POST /api/incidents/{incident_id}/swarm to run it")
    d["runs"] = _load_runs(incident_id)
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
    # the resolved kind, never the raw query string: `kind` is caller-supplied
    # and this note crosses the boundary to a go-to-market platform
    emit_quietly("citinel-reports-drafted", 1,
                 f"{'certin' if kind == 'certin' else 'dpdp'} artifact drafted for sign-off")
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
    ledger = AuditLedger(_ledger_path())
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
            # the deployment's own saved runs where it keeps them (the Render disk, or
            # data/incidents locally); the committed seed runs when it has none
            swarm_dir = _artifacts_dir() / "swarm"
            if not (swarm_dir.is_dir() and any(swarm_dir.glob("*.json"))):
                swarm_dir = SEED_DIR / "swarm"
            report = harness.build_report(swarm_dir=swarm_dir).as_dict()
            if report.get("measured"):
                report["served_from"] = "harness"
                return report
            # The harness ran and, finding no detection or anomaly output on this
            # host, honestly measured nothing. That is a fact about this host, not
            # about the product: the committed report below is a real run whose
            # input hashes it names. Serve that, labelled, instead of an empty
            # table under a heading that says "measured". (Confirmed on Render,
            # 4 Sep 2026: the image carries no data/cache, so Eval sat empty.)
            last_error = ("harness ran here and found no detection or anomaly output on "
                          "this host; serving the committed run instead")
        except Exception as e:  # inputs missing, most likely
            last_error = "harness could not run here: " + str(e)
    else:
        last_error = "eval harness not available in this deployment"
    cached = SEED_DIR / "eval-report.json"
    if cached.exists():
        import json as _json
        report = _json.loads(cached.read_text(encoding="utf-8"))
        report["served_from"] = "seed cache (" + last_error + ")"
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


def _corpus_advisory_path() -> Path:
    """Deployment-wide, not per-incident -- there is one corpus, not one per case."""
    return _artifacts_dir() / "corpus_advisory.json"


@app.get("/api/corpus/review")
def get_corpus_review() -> dict:
    """The standing Lyzr coverage advisory. 404 until generated -- a real call
    site, not a value that appears from nowhere the first time this is read."""
    p = _corpus_advisory_path()
    if not p.exists():
        raise HTTPException(404, "no corpus advisory has been generated yet")
    import json as _json
    return _json.loads(p.read_text(encoding="utf-8"))


@app.post("/api/corpus/review")
def write_corpus_review(body: dict | None = None) -> dict:
    """Ask the corpus advisor for which rule directories or techniques look
    thin, from the same stats /api/corpus already reports, and persist it.
    Each call is a real Lyzr call, so it is gated the same way handover is."""
    if not (body or {}).get("confirm"):
        raise HTTPException(400, 'each advisory is a Lyzr call; send {"confirm": true} to write one')
    advisory = corpus_advisory(get_corpus())
    advisory["written_at"] = _now()
    p = _corpus_advisory_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    import json as _json
    p.write_text(_json.dumps(advisory, ensure_ascii=False, indent=1), encoding="utf-8")
    return advisory


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
    "CITINEL_LYZR_VERDICT_AGENT_ID", "CITINEL_LYZR_RESPONSE_AGENT_ID", "CITINEL_LYZR_CORPUS_AGENT_ID",
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


def _swy_store_note() -> str:
    """Which of the three files the Swytchcode kernel needs for Slack are actually
    in the runtime's HOME, as presence and size only.

    An executed action on 4 Sep answered `not_configured: missing credentials for
    Slack` on Render while the ticketing leg beside it executed, which proved the
    CLI, the bundles and GitHub's per-call auth were all fine and left exactly one
    unknown: whether the three Secret Files reached `$HOME/.swytchcode` at boot.
    Nothing outside the container could see that, so the answer took a deploy to
    ask. Presence and byte count only -- never a path's contents, never a key.
    `credentials.db` is an encrypted SQLite file and `credkey` is its key material;
    both stay unread. The image decodes `/etc/secrets/swy-<name>.b64`, so a missing
    file here means the Secret File is absent, misnamed, or HOME differed at boot.
    """
    try:
        home = Path(os.path.expanduser("~"))
        store = home / ".swytchcode"
        parts = []
        for name in ("credentials.db", "credkey", "auth.json"):
            f = store / name
            parts.append(f"{name} {f.stat().st_size}B" if f.is_file() else f"{name} MISSING")
        return f" · slack store in {store}: " + ", ".join(parts)
    except Exception as e:                       # a diagnostic must never take the route down
        return f" · slack store unreadable: {type(e).__name__}"


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
            c("gemini", "wide-lens sweep over findings the evidence window never reached",
              bool(s.gemini_api_key), f"long-context read · {s.gemini_model}"),
            c("virustotal", "file and IP reputation for the Enrichment Squad", bool(s.virustotal_api_key), "reputation"),
            c("abuseipdb", "IP abuse reports for the Enrichment Squad", bool(s.abuseipdb_api_key), "reputation"),
            c("lyzr", "PII second opinion and ledger witness", lyzr_ok,
              "key + guard url + agent id all required" if not lyzr_ok else "all three set"),
            c("lyzr-triage", "independent triage lane beside the Router's, on the ledger", bool(lyzr_ok and s.lyzr_triage_agent_id), "CITINEL_LYZR_TRIAGE_AGENT_ID"),
            c("lyzr-review", "drafted-field review before sign-off", bool(lyzr_ok and s.lyzr_review_agent_id), "CITINEL_LYZR_REVIEW_AGENT_ID"),
            c("lyzr-handover", "shift-handover note from the ledger", bool(lyzr_ok and s.lyzr_handover_agent_id), "CITINEL_LYZR_HANDOVER_AGENT_ID"),
            c("lyzr-verdict", "independent second opinion on citation support, beside the Narrator's own estimate", bool(lyzr_ok and s.lyzr_verdict_agent_id), "CITINEL_LYZR_VERDICT_AGENT_ID"),
            c("lyzr-response", "independent proportionality review of a proposed action, beside the OPA gate", bool(lyzr_ok and s.lyzr_response_agent_id), "CITINEL_LYZR_RESPONSE_AGENT_ID"),
            c("lyzr-corpus", "independent coverage advisory on the Sigma corpus", bool(lyzr_ok and s.lyzr_corpus_agent_id), "CITINEL_LYZR_CORPUS_AGENT_ID"),
            c("n8n", "post-sign-off automation (notify, export, ticket)", bool(s.n8n_webhook_url),
              "webhook · starts a playbook and reads back which channels succeeded"),
            c("n8n-api", "reads playbook executions back as citable evidence, and answers one paused on a Wait node",
              bool(s.n8n_api_url and s.n8n_api_key), "CITINEL_N8N_API_URL + CITINEL_N8N_API_KEY"),
            c("startuped", "aggregate product-usage signals to the GTM platform",
              bool(s.startuped_api_key),
              "counts only -- no incident content ever; see GET /api/startuped/signals"),
            c("swytchcode", "ticketing + comms after an executed action", bool(s.swytchcode_api_key),
              "key set; the Python runtime is wired -- receipts say whether the CLI is scaffolded, a policy blocked the call, or it executed"
              + _swy_store_note()),
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
        save_result(result, _artifacts_dir())
        # an independent second opinion on the lane, from a separate Lyzr agent,
        # recorded beside the Router's decision (not_configured when no id is set)
        opinion = triage_second_opinion(inc, result.as_dict(), _ledger())
        annotate_result(incident_id, _artifacts_dir(), "lyzr_triage", opinion)
        # a second, independent opinion on citation support, beside the
        # pipeline's own semantic-support estimate (not_configured when unset)
        verdict_dict = result.as_dict().get("verdict") or {}
        audit = verdict_audit(incident_id, verdict_dict.get("claims") or [], _ledger())
        annotate_result(incident_id, _artifacts_dir(), "lyzr_verdict_audit", audit)
        # Product-usage signals only: a count that the loop ran, and a count
        # that a verdict survived citation. Nothing about the incident.
        emit_quietly("citinel-incidents-investigated", 1, "swarm run completed")
        if (result.as_dict().get("verdict") or {}).get("claims"):
            emit_quietly("citinel-verdicts-cited", 1, "verdict produced with cited claims")
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
    base["has_result"] = _load_result(incident_id) is not None
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
    d = load_context(incident_id, _artifacts_dir())
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
    verdict = _load_result(incident_id)
    return gather_context(inc, verdict, settings.data_dir / "cache" / "enrichment",
                          _artifacts_dir(), connector=_tavily())


@app.get("/api/incidents/{incident_id}/sweep")
def get_sweep(incident_id: str) -> dict:
    """The Gemini wide-lens sweep for this record: what the long-context read
    found in the findings the investigation's evidence window never reached.
    404 until swept. Context, never evidence."""
    _incident(incident_id)
    d = load_sweep(_artifacts_dir(), incident_id)
    if d is None:
        raise HTTPException(404, f"no wide-lens sweep has been run for {incident_id} yet")
    return d


@app.post("/api/incidents/{incident_id}/sweep")
def run_wide_sweep(incident_id: str, body: dict | None = None) -> dict:
    """Read EVERY finding on this record through Gemini's long context --
    including the region the swarm's own evidence window never reached -- and
    persist what it found. One API call; the body must confirm. Nothing swept
    becomes evidence: no verdict, lane or gate decision changes because of it.
    """
    inc = _incident(incident_id)
    if not settings.gemini_api_key:
        raise HTTPException(503, "no Gemini key configured on this deployment")
    if not (body or {}).get("confirm"):
        raise HTTPException(400, 'a sweep is one Gemini call; send {"confirm": true} to run it')
    result = _load_result(incident_id) or {}
    examined = int(result.get("findings_examined") or MAX_EVIDENCE_FINDINGS)
    return run_sweep(inc, examined, settings.data_dir / "cache" / "enrichment",
                     _artifacts_dir(), ledger=_ledger())


@app.get("/api/incidents/{incident_id}/brief")
def get_brief(incident_id: str) -> dict:
    """The Tavily Research brief for this record. Polls once when the run is
    still in flight, so the console advances it by asking. 404 until started.
    Context, never evidence."""
    _incident(incident_id)
    d = poll_brief(incident_id, settings.data_dir / "cache" / "enrichment", _artifacts_dir())
    if d is None:
        raise HTTPException(404, f"no threat brief has been requested for {incident_id} yet")
    return d


@app.post("/api/incidents/{incident_id}/brief")
def request_brief(incident_id: str, body: dict | None = None) -> dict:
    """Ask Tavily Research what this incident's technique combination usually
    means and what responders who have seen it recommend. Runs several
    searches of its own and answers with citations; the body must confirm.
    Advisory only -- it moves no verdict and reopens no lane."""
    inc = _incident(incident_id)
    if not settings.tavily_api_key:
        raise HTTPException(503, "no Tavily key configured on this deployment")
    if not (body or {}).get("confirm"):
        raise HTTPException(400, 'a brief is a multi-search Tavily run; send {"confirm": true} to start it')
    verdict = _load_result(incident_id)
    return start_brief(inc, verdict, settings.data_dir / "cache" / "enrichment",
                       _artifacts_dir())


@app.get("/api/n8n/executions")
def n8n_executions(limit: int = 20, status: str | None = None) -> dict:
    """What the automation layer actually did, read back from n8n itself.

    An automated action that can only be inspected inside another tool is not
    auditable. These runs carry an id, a state and a timestamp, so the console
    can show them beside the ledger frames rather than asking a reviewer to go
    and look somewhere else.
    """
    return list_executions(limit=limit, status=status)


@app.post("/api/incidents/{incident_id}/n8n/resume")
def n8n_resume_wait(incident_id: str, body: dict | None = None) -> dict:
    """Answer an n8n playbook that parked itself on a Wait node.

    The inversion this exists for: rather than CITINEL asking a human and then
    telling n8n, the playbook pauses and hands over its own resume URL. The
    analyst decides on CITINEL's Approvals screen without leaving the console,
    and the workflow branches on the answer. Recorded as a ledger frame,
    because a human decision that changes what a machine does next is exactly
    what the ledger is for.
    """
    _incident(incident_id)
    b = body or {}
    url, decision, approver = b.get("resume_url", ""), b.get("decision", ""), b.get("approver", "")
    if not url or decision not in ("approve", "reject") or not approver:
        raise HTTPException(400, 'resume_url, approver, and decision ("approve" or "reject") are all required')
    out = n8n_resume(url, decision, str(approver), str(b.get("note", "")))
    _ledger().append(incident_id, f"human:{approver}", "decision", {
        "check": "n8n_wait_resumed", "decision": decision,
        "status": out["status"], "note": str(b.get("note", ""))[:300],
        "reason": "a playbook paused on a Wait node and a named human answered it "
                  "from the console; n8n held the workflow state, CITINEL held the human",
    })
    return out


@app.post("/api/n8n/error")
def n8n_error_report(body: dict | None = None) -> dict:
    """n8n's Error Trigger reports a failed playbook here.

    A SOC that cannot see its own automation failing is missing the same class
    of blind spot it exists to find elsewhere. n8n's Error Trigger posts the
    execution id, the node that failed and the message; this records that as a
    ledger frame against the incident the playbook was working on, so a broken
    automation shows up on the audit trail instead of only in n8n's own logs.
    """
    # `or {}` looks like a guard and is not: a scalar is truthy, so a string
    # under "execution" was assigned straight through and .get() on it raised
    # AttributeError -- a 500 from the one route whose entire job is to record
    # that the automation layer failed. n8n's Error Trigger payload is not
    # CITINEL's to guarantee, and the worst moment to reject a malformed report
    # is the moment something is already broken.
    b = body if isinstance(body, dict) else {}
    execution = b.get("execution") if isinstance(b.get("execution"), dict) else {}
    workflow = b.get("workflow") if isinstance(b.get("workflow"), dict) else {}
    incident_id = str(b.get("incident_id") or "").strip()
    frame = {
        "check": "n8n_playbook_failed",
        "workflow": str(workflow.get("name") or workflow.get("id") or "unknown")[:120],
        "execution_id": str(execution.get("id") or ""),
        "execution_url": str(execution.get("url") or "")[:400],
        "last_node": str(execution.get("lastNodeExecuted") or "")[:120],
        "message": str((execution.get("error") if isinstance(execution.get("error"), dict)
                        else {}).get("message") or "")[:400],
        "reason": "the automation layer reported its own failure; recorded so a "
                  "broken playbook is visible on the audit trail, not only in n8n",
    }
    if not incident_id:
        return {"status": "recorded_without_incident", "detail":
                "no incident_id in the error payload; nothing was written to a chain",
                "frame": frame}
    _incident(incident_id)
    _ledger().append(incident_id, "n8n", "tool_call", frame)
    return {"status": "recorded", "incident_id": incident_id, "frame": frame}


@app.get("/api/incidents/{incident_id}/visual")
def get_visuals(incident_id: str) -> dict:
    """Images an analyst pasted onto this record, and what the record itself
    said about the indicators each one named. 404 until one is read."""
    _incident(incident_id)
    d = load_visuals(_artifacts_dir(), incident_id)
    if d is None:
        raise HTTPException(404, f"no image has been read for {incident_id} yet")
    return d


@app.post("/api/incidents/{incident_id}/visual")
def read_visual(incident_id: str, body: dict | None = None) -> dict:
    """Read an analyst-supplied screenshot and corroborate it against the record.

    The only place a model in CITINEL looks at something that is not text. A
    SOC runs on logs, but an analyst is handed pictures all day. The reading
    is an observation and can never support a claim; the corroboration that
    follows it -- every named indicator checked against this incident's own
    findings, in code, with no model involved -- is a fact with citable
    finding indices.
    """
    inc = _incident(incident_id)
    if not settings.gemini_api_key:
        raise HTTPException(503, "no Gemini key configured on this deployment")
    b = body or {}
    image = str(b.get("image_base64") or "")
    mime = str(b.get("mime_type") or "")
    if not image or not mime:
        raise HTTPException(400, "image_base64 and mime_type are both required")
    return read_image(inc, image, mime, str(b.get("note", "")),
                      settings.data_dir / "cache" / "enrichment",
                      _artifacts_dir(), ledger=_ledger())


@app.get("/api/startuped/signals")
def startuped_signals() -> dict:
    """Exactly what CITINEL reports to its go-to-market platform, and nothing else.

    Published as a route rather than buried in a connector on purpose. An
    integration that sends data somewhere should be able to show a reader what
    it sends -- and in this case the answer is five aggregate counters and no
    incident content of any kind, which is a claim worth being able to check.
    """
    return {
        "provider": "startuped",
        "configured": bool(settings.startuped_api_key),
        "signals": [{"signal_key": k, **v} for k, v in SIGNALS.items()],
        "what_is_never_sent": (
            "No incident id, host, IP, finding, evidence, target or account name "
            "ever leaves through this connector. Startuped is a go-to-market "
            "platform; CITINEL processes bank security telemetry. Only aggregate "
            "counts of product usage are reported, and the connector refuses -- "
            "rather than strips -- any payload field that could carry content."
        ),
    }


def _handover_path(incident_id: str) -> Path:
    return _artifacts_dir() / "handover" / f"{incident_id}.json"


@app.get("/api/incidents/{incident_id}/handover")
def get_handover(incident_id: str) -> dict:
    """The shift-handover note a Lyzr agent wrote from the ledger's own frames.
    404 until generated; the note names the frames it was written from."""
    _incident(incident_id)
    p = _handover_path(incident_id)
    if not p.exists():
        raise HTTPException(404, f"no handover note has been written for {incident_id} yet")
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
    d = _overlay(inc.as_dict(), chains.get(incident_id, []), _summaries().get(incident_id))
    note = handover_summary(d, chains.get(incident_id, []), d.get("swarm"))
    note.update({"incident_id": incident_id, "state": d["state"], "written_at": _now(),
                 "frames_used": min(15, len([e for e in chains.get(incident_id, []) if e.kind not in ("detection_added", "escalation_added")]))})
    p = _handover_path(incident_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    import json as _json
    p.write_text(_json.dumps(note, ensure_ascii=False, indent=1), encoding="utf-8")
    return note


#: Classes that touch no bank asset at all -- they read intel, run a scoped
#: query, or message a human. Their honest radius is 0, and the policy caps
#: them at 0 precisely so that a proposal CLAIMING one escalates.
_ASSET_FREE_CLASSES = frozenset({"enrich_ioc", "query_logs", "notify"})


def _enforced_blast_radius(action_class: str, claimed: int) -> int:
    """The radius the gate actually gates on -- floored here, never lowered.

    SAFE-F07 escalates an action whose blast radius exceeds its clause's
    automatic cap. Until now that radius arrived in the request body and was
    used as given, so the one number the safety rail turns on was chosen by the
    caller: an anonymous POST claiming assets_affected 0 for isolate_host
    walked past the cap. The console forwards the Marshal's own figure, so a
    hallucinated count had the same effect with no attacker present.

    The rule is a FLOOR and nothing else, in one direction only:

      - an asset-touching class is floored to 1, because an action executed
        against a named target touches at least that target
      - an asset-free class passes through untouched. Flooring those would be
        actively wrong: claiming 1 for query_logs is anomalous and the policy
        escalates it on purpose, and an earlier cut of this function pinned
        them to 0 in both directions -- which deleted that fail-safe. The
        existing suite caught it.

    Overstating is always allowed: it can only escalate, never authorise.

    What is NOT closed, stated plainly: a caller can still understate a
    genuinely bulk action as a small one -- 50 hosts declared as 3. Closing
    that needs the server to compute the real target set per action class,
    which is a larger change than this boundary fix.
    """
    if action_class in _ASSET_FREE_CLASSES:
        return claimed
    return max(1, claimed)


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
        claimed = 1 if raw_assets is None or raw_assets == "" else int(raw_assets)
    except (TypeError, ValueError):
        raise HTTPException(400, "assets_affected must be an integer")
    if claimed < 0:
        raise HTTPException(400, "assets_affected cannot be negative")
    assets = _enforced_blast_radius(action_class, claimed)
    approver = body.get("approver")

    decision = PolicyGate(POLICY_PATH).check(action_class, assets, target)
    ledger = _ledger()
    # an independent opinion on whether this scope looks proportionate, asked
    # after the gate above has already decided; it never gates -- not_configured
    # when no agent id is set, and nothing here changes what executes
    review = response_review(incident_id, action_class, target, assets, decision.as_dict(), ledger)
    executor = ActionExecutor(ENDPOINTS, ledger)
    try:
        receipt = executor.execute(incident_id, decision, target)
        if receipt.status == "awaiting_approval" and approver:
            receipt = executor.approve_and_execute(incident_id, decision, target, str(approver))
    except ExecutionRefused as e:
        raise HTTPException(403, {"refused": str(e), "decision": decision.as_dict()})

    emit_quietly("citinel-actions-gated", 1, f"gate verdict {decision.verdict.value}")
    swytch: list[dict[str, Any]] = []
    if receipt.status == "executed":
        for r in SwytchcodeExecutor().execute_for_decision(decision, target, incident_id):
            ledger.append(incident_id, "swytchcode", "tool_call", r.as_dict())
            swytch.append(r.as_dict())
    chain = ledger.entries_for(incident_id)
    return {"decision": decision.as_dict(), "receipt": receipt.as_dict(),
            "swytchcode": swytch, "simulated": True, "lyzr_response_review": review,
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
    # The end of the workflow: the moment the product delivered its value.
    # A count, not a name -- who signed is ledger business, not marketing.
    emit_quietly("citinel-signoffs", 1, "incident signed off by a named human")
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


# --- a wrong address gets the console's own 404 ------------------------------
@app.exception_handler(StarletteHTTPException)
async def _http_error(request: Request, exc: StarletteHTTPException):
    """The console's own 404 for a wrong address; the JSON contract for
    every machine path and every other status code.

    StaticFiles is mounted at "/" as a catch-all (below), and a file it
    cannot find raises a bare 404 that FastAPI answered with
    {"detail": "Not Found"} -- so a mistyped screen name, a stale bookmark
    or a QR code with a typo landed a judge on a raw JSON stub instead of
    the console. Any non-API 404 now returns dashboard/static/404.dc.html:
    read from STATIC_DIR at request time so it deploys like every other
    screen, and carrying the same Cache-Control the console files carry so
    a redeployed page is never served from a heuristic browser cache.

    /api/* and /healthz deliberately keep the JSON shape. The console's
    api.js, the demo-capture fixtures and the test suite all read
    r.json()["detail"] on a 404, and a machine caller must never be handed
    an HTML document where it expects a JSON error. Anything that is not a
    console 404 -- an API 404, a 400/401/403/409/503, a 204/304 with no
    body -- is delegated to FastAPI's own handler, so nothing else changes.
    """
    path = request.url.path
    machine = path.startswith("/api/") or path == "/healthz"
    if exc.status_code == 404 and not machine:
        page = STATIC_DIR / "404.dc.html"
        if page.is_file():
            return HTMLResponse(page.read_text(encoding="utf-8"), status_code=404,
                                headers={"Cache-Control": "no-cache"})
    return await http_exception_handler(request, exc)


# --- the glass-box UI ---------------------------------------------------------
# Mounted last, deliberately: StaticFiles at "/" is a catch-all, so every
# /api/* and /healthz route above must already be registered or the mount
# would shadow them. html=True serves the *.dc.html pages directly and
# is what makes the deployed Render service actually show the console rather
# than only answering JSON.
if STATIC_DIR.is_dir():
    # "/" must be an explicit route, registered BEFORE the mount below.
    # StaticFiles(html=True) serves index.html at a directory root, and this
    # console has no index.html -- its entry point is Overview.dc.html (the Entry
    # screen was removed 4 Sep 2026). Without
    # this redirect the root URL 404s, which is precisely the URL the deck's
    # QR code points at: a judge scanning it would get a blank error page.
    @app.get("/", include_in_schema=False)
    def _root() -> RedirectResponse:
        return RedirectResponse(url="/Overview.dc.html")

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="ui")
