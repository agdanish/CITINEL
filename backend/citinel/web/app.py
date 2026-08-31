"""CITINEL web service: /healthz + read endpoints over the built pipeline.

This is the Render "web" service (deploy/render.yaml). Its job at this stage
of the build is to serve what already exists on disk -- incidents, the audit
ledger, the policy table, compliance drafts -- as real HTTP, so the Blueprint
has a genuine, non-crash-looping entry point. The Best-Use-of-Render
adversarial audit found `uvicorn citinel.web.app:app` pointed at a module that
did not exist; this file is that module.

Once Step 7 (the agent swarm) lands, this becomes the surface the glass-box
dashboard (Step 11) fetches from -- no reshaping needed, the read model is
already incident/finding/decision/draft shaped.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles

from citinel.audit.ledger import AuditLedger
from citinel.compliance.drafter import draft_certin, draft_dpdp, render_text
from citinel.connectors.lyzr import LyzrLedgerMirror
from citinel.incidents.builder import load_incidents
from citinel.policy.gate import PolicyGate
from citinel.policy.roles import Role, project_incident

REPO_ROOT = Path(__file__).resolve().parents[3]
LIVE_DIR = REPO_ROOT / "data" / "incidents"
SEED_DIR = REPO_ROOT / "data" / "seed"
POLICY_PATH = REPO_ROOT / "policies" / "citinel-policy.yaml"
STATIC_DIR = REPO_ROOT / "dashboard" / "static"


def _resolve_data_dir() -> tuple[Path, str]:
    """Live pipeline output if present, else the committed demo seed.

    Returns the directory AND which one it is, because the difference is
    load-bearing and must never be invisible: `data/incidents/` is gitignored
    live output that a fresh deployment does not have, while `data/seed/` is
    the committed corpus slice that ships inside the image. Serving seed data
    while implying it is live would be the same class of unearned claim as
    reporting a missing ledger "intact" -- so `/api/source` exposes this, and
    every deployment can be asked which it is answering from.
    """
    if (LIVE_DIR / "incidents.jsonl").exists():
        return LIVE_DIR, "live"
    return SEED_DIR, "seed"


#: Module-level so tests can monkeypatch, matching the previous INCIDENTS_DIR.
INCIDENTS_DIR, DATA_SOURCE = _resolve_data_dir()

app = FastAPI(
    title="CITINEL",
    description="Caught. Cited. Gated. Actioned. Closed.",
    version="0.1.0",
)


@app.get("/healthz")
def healthz() -> dict:
    """Render's health check target. 200 with no dependency on the pipeline
    having run yet, so the service comes up clean even before Step 7 exists."""
    return {"status": "ok", "service": "citinel-web"}


@app.get("/api/source")
def data_source() -> dict:
    """Which corpus this deployment is answering from, and whether it loaded.

    Exists because "no incidents" and "incidents not shipped" are different
    facts that both used to render as a 200 with an empty list. A deployment
    that silently serves nothing looks identical to a quiet night in the SOC;
    this endpoint makes the difference explicit and is what the UI's data-source
    badge should read rather than inferring liveness from an empty array.
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
    }


@app.get("/api/incidents")
def list_incidents() -> list[dict]:
    incs = load_incidents(INCIDENTS_DIR / "incidents.jsonl")
    return [i.as_dict() for i in incs]


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
    incs = {i.incident_id: i for i in load_incidents(INCIDENTS_DIR / "incidents.jsonl")}
    inc = incs.get(incident_id)
    if inc is None:
        raise HTTPException(404, f"no incident {incident_id}")
    role = Role.parse(x_citinel_role)
    return project_incident(inc.as_dict(), role, expand=expand).as_dict()


@app.get("/api/incidents/{incident_id}/audit")
def get_audit_chain(incident_id: str) -> list[dict]:
    """SDD Section 16 finding 4: full chain reconstruction from the case id."""
    ledger = AuditLedger(INCIDENTS_DIR / "ledger.jsonl")
    chain = ledger.entries_for(incident_id)
    if not chain:
        raise HTTPException(404, f"no audit entries for {incident_id}")
    return [e.as_dict() for e in chain]


@app.get("/api/incidents/{incident_id}/draft")
def get_draft(incident_id: str, kind: str = "certin") -> dict:
    incs = {i.incident_id: i for i in load_incidents(INCIDENTS_DIR / "incidents.jsonl")}
    inc = incs.get(incident_id)
    if inc is None:
        raise HTTPException(404, f"no incident {incident_id}")
    drafter = draft_certin if kind == "certin" else draft_dpdp
    draft = drafter(inc)
    return {"draft": draft.as_dict(), "rendered": render_text(draft)}


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
    chain verifies perfectly against itself.

    `witness` is the external Lyzr mirror (SDD 15.3 attachment point 4), which
    covers exactly that blind spot and nothing else. They are not merged into
    one boolean: "the chain is internally consistent" and "an independent
    party still recognises this chain" are different claims, and collapsing
    them would let an unreachable witness read as a clean bill of health.
    """
    ledger = AuditLedger(INCIDENTS_DIR / "ledger.jsonl")
    ok, message = ledger.verify_chain()
    witness = LyzrLedgerMirror().compare(ledger)
    return {
        "intact": ok,
        "message": message,
        "witness": witness.as_dict(),
    }



@app.get("/api/eval")
def get_eval() -> dict:
    """The credibility screen's data source (Eval.dc.html).

    Deliberately serves the harness's UNMEASURED entries alongside its
    measurements. The screen must render both: a false-positive rate the
    system has not earned is exactly what this endpoint exists to refuse to
    supply, and a UI that showed only the `measured` list would quietly
    recreate the fabricated metric by omission.
    """
    import importlib.util
    import sys as _sys

    harness_path = REPO_ROOT / "evals" / "harness" / "run.py"
    if not harness_path.exists():
        raise HTTPException(503, "eval harness not available in this deployment")
    spec = importlib.util.spec_from_file_location("citinel_eval_harness", harness_path)
    harness = importlib.util.module_from_spec(spec)
    _sys.modules[spec.name] = harness          # @dataclass needs this, see cli.py
    spec.loader.exec_module(harness)
    return harness.build_report().as_dict()

# --- the glass-box UI ---------------------------------------------------------
# Mounted last, deliberately: StaticFiles at "/" is a catch-all, so every
# /api/* and /healthz route above must already be registered or the mount
# would shadow them. html=True serves Entry.dc.html-style pages directly and
# is what makes the deployed Render service actually show the console rather
# than only answering JSON.
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="ui")
