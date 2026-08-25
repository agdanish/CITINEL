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

from fastapi import FastAPI, HTTPException

from citinel.audit.ledger import AuditLedger
from citinel.compliance.drafter import draft_certin, draft_dpdp, render_text
from citinel.incidents.builder import load_incidents
from citinel.policy.gate import PolicyGate

REPO_ROOT = Path(__file__).resolve().parents[3]
INCIDENTS_DIR = REPO_ROOT / "data" / "incidents"
POLICY_PATH = REPO_ROOT / "policies" / "citinel-policy.yaml"

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


@app.get("/api/incidents")
def list_incidents() -> list[dict]:
    incs = load_incidents(INCIDENTS_DIR / "incidents.jsonl")
    return [i.as_dict() for i in incs]


@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str) -> dict:
    incs = {i.incident_id: i for i in load_incidents(INCIDENTS_DIR / "incidents.jsonl")}
    inc = incs.get(incident_id)
    if inc is None:
        raise HTTPException(404, f"no incident {incident_id}")
    return inc.as_dict()


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
    ledger = AuditLedger(INCIDENTS_DIR / "ledger.jsonl")
    ok, message = ledger.verify_chain()
    return {"intact": ok, "message": message}
