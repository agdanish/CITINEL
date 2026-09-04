"""n8n in both directions: CITINEL starts a playbook, reads what it did, and
answers one that paused for a human.

The property under test throughout is that an automated action stays
auditable. A run CITINEL cannot cite, or a failure only n8n can see, is the
same blind spot this product exists to close elsewhere.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from citinel.config import settings
from citinel.connectors.n8n import dispatch_signed
from citinel.connectors.n8n_api import list_executions, resume
from citinel.web.app import app
from tests.conftest import WRITE_HEADERS

client = TestClient(app)

EXECS = {"data": [
    {"id": 231, "workflowId": "w1", "status": "success", "mode": "webhook",
     "startedAt": "2026-09-04T06:00:00.000Z", "stoppedAt": "2026-09-04T06:00:12.000Z",
     "finished": True},
    {"id": 232, "workflowId": "w1", "status": "waiting", "mode": "webhook",
     "startedAt": "2026-09-04T06:05:00.000Z", "waitTill": "2026-09-04T18:00:00.000Z",
     "finished": False},
]}


def _api_on(monkeypatch):
    monkeypatch.setattr(settings, "n8n_api_url", "https://x.app.n8n.cloud")
    monkeypatch.setattr(settings, "n8n_api_key", "n8n-key")


def test_a_playbook_run_becomes_something_a_reviewer_can_cite(monkeypatch):
    _api_on(monkeypatch)
    seen = {}

    def sender(method, url, headers, params, body):
        seen.update(method=method, url=url, headers=headers, params=params)
        return 200, EXECS

    out = list_executions(limit=5, sender=sender)
    assert out["status"] == "ok" and len(out["executions"]) == 2
    assert out["executions"][0]["id"] == "231" and out["executions"][0]["state"] == "success"
    # the paused one carries what it is waiting for
    assert out["executions"][1]["state"] == "waiting"
    assert out["executions"][1]["waiting_until"].startswith("2026-09-04T18")
    # n8n's documented auth header, not a bearer token
    assert seen["headers"]["X-N8N-API-KEY"] == "n8n-key"
    assert seen["url"].endswith("/api/v1/executions")


def test_the_read_path_degrades_without_settings(monkeypatch):
    monkeypatch.setattr(settings, "n8n_api_url", None)
    monkeypatch.setattr(settings, "n8n_api_key", None)
    out = list_executions()
    assert out["status"] == "not_configured" and out["executions"] == []


def test_a_rejected_key_says_so_rather_than_reporting_no_runs(monkeypatch):
    """401 must not look like "there were no executions" -- that would read as
    a quiet automation layer when it is really an unusable credential."""
    _api_on(monkeypatch)
    out = list_executions(sender=lambda *a: (401, {}))
    assert out["status"] == "error" and "401" in out["detail"]


def test_an_unknown_status_filter_is_refused_before_the_call(monkeypatch):
    _api_on(monkeypatch)
    calls = []
    out = list_executions(status="finished", sender=lambda *a: (calls.append(1), (200, EXECS))[1])
    assert out["status"] == "error" and calls == []


def test_resuming_a_paused_playbook_carries_the_humans_answer(monkeypatch):
    _api_on(monkeypatch)          # a resume URL is pinned to the configured instance
    body = {}

    def sender(method, url, headers, params, payload):
        body.update(payload)
        return 200, {"ok": True}

    out = resume("https://x.app.n8n.cloud/webhook-waiting/231", "approve", "ciso@bank", "looks contained", sender=sender)
    assert out["status"] == "resumed"
    assert body["decision"] == "approve" and body["approver"] == "ciso@bank"
    assert body["source"] == "citinel-approvals"


def test_a_resume_url_must_be_https(monkeypatch):
    out = resume("http://x.app.n8n.cloud/webhook-waiting/231", "approve", "a")
    assert out["status"] == "error" and "https" in out["detail"]


def test_an_expired_wait_is_reported_as_expired_not_as_an_error(monkeypatch):
    _api_on(monkeypatch)
    out = resume("https://x.app.n8n.cloud/w/1", "approve", "a", sender=lambda *a: (404, {}))
    assert out["status"] == "expired" and "moved on" in out["detail"]


def test_the_resume_route_records_the_decision_on_the_ledger(sandbox):
    r = client.post("/api/incidents/INC-T1/n8n/resume", headers=WRITE_HEADERS, json={
        "resume_url": "https://x.app.n8n.cloud/webhook-waiting/9",
        "decision": "approve", "approver": "ciso@bank", "note": "contained"})
    assert r.status_code == 200
    chain = client.get("/api/incidents/INC-T1/audit").json()
    frames = [e for e in chain if (e.get("payload") or {}).get("check") == "n8n_wait_resumed"]
    assert len(frames) == 1
    assert frames[0]["payload"]["decision"] == "approve"
    assert frames[0]["actor"] == "human:ciso@bank"


def test_the_resume_route_refuses_an_unnamed_or_undecided_approver(sandbox):
    for bad in ({"resume_url": "https://x/1", "decision": "approve"},
                {"resume_url": "https://x/1", "decision": "maybe", "approver": "a"},
                {"decision": "approve", "approver": "a"}):
        assert client.post("/api/incidents/INC-T1/n8n/resume", json=bad,
                           headers=WRITE_HEADERS).status_code == 400


def test_a_failed_playbook_lands_on_the_incidents_own_audit_trail(sandbox):
    """A SOC that cannot see its own automation failing has the blind spot it
    exists to find elsewhere."""
    r = client.post("/api/n8n/error", headers=WRITE_HEADERS, json={
        "incident_id": "INC-T1",
        "workflow": {"id": "1", "name": "Beat 5b"},
        "execution": {"id": "231", "url": "https://x/execution/231",
                      "lastNodeExecuted": "Open Ticket",
                      "error": {"message": "connection refused"}}})
    assert r.status_code == 200 and r.json()["status"] == "recorded"
    chain = client.get("/api/incidents/INC-T1/audit").json()
    f = [e for e in chain if (e.get("payload") or {}).get("check") == "n8n_playbook_failed"]
    assert len(f) == 1
    assert f[0]["payload"]["last_node"] == "Open Ticket"
    assert f[0]["payload"]["execution_id"] == "231"


def test_an_error_report_without_an_incident_writes_to_no_chain(sandbox):
    r = client.post("/api/n8n/error", headers=WRITE_HEADERS,
                    json={"workflow": {"name": "X"}, "execution": {"id": "9"}})
    assert r.json()["status"] == "recorded_without_incident"


def test_dispatch_captures_the_execution_id_that_makes_a_run_citable(monkeypatch):
    monkeypatch.setattr(settings, "n8n_webhook_url", "https://x.app.n8n.cloud/webhook/abc")

    class Inc:
        incident_id, severity, state = "INC-T1", "high", "cited"
        hosts, findings, techniques = ["h1"], [], []
        opened_ts = "2026-09-04T00:00:00Z"

    out = dispatch_signed(Inc(), "ciso@bank", sender=lambda url, body: (200, {
        "channels": ["ciso", "ticket"], "execution_id": "231"}))
    assert out.status == "dispatched" and out.execution_id == "231"
    assert out.as_dict()["execution_id"] == "231"
