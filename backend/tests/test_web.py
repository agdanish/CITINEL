"""Tests for the web service -- the Render entry point that was missing.

TestClient boots the real FastAPI app in-process; these are the smoke tests
the Best-Use-of-Render audit asked for: the module must actually import and
serve, not just exist as a Dockerfile CMD string.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from citinel.web.app import app

client = TestClient(app)


def test_healthz_returns_ok_with_no_pipeline_dependency():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "citinel-web"}


def test_policy_endpoint_serves_the_real_gate_table():
    r = client.get("/api/policy")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "CITINEL response policy"
    assert any(c["clause"] == "4.2" for c in body["clauses"])


def test_incidents_endpoint_serves_real_incidents():
    r = client.get("/api/incidents")
    assert r.status_code == 200
    ids = {i["incident_id"] for i in r.json()}
    assert "INC-0417" in ids


def test_single_incident_404s_when_unknown():
    r = client.get("/api/incidents/INC-9999")
    assert r.status_code == 404


def test_audit_endpoint_reconstructs_the_chain():
    r = client.get("/api/incidents/INC-0417/audit")
    assert r.status_code == 200
    entries = r.json()
    assert len(entries) > 0
    assert all(e["case_id"] == "INC-0417" for e in entries)


def test_draft_endpoint_renders_a_real_draft():
    r = client.get("/api/incidents/INC-0417/draft", params={"kind": "certin"})
    assert r.status_code == 200
    body = r.json()
    assert body["draft"]["incident_id"] == "INC-0417"
    assert "DRAFT" in body["rendered"]


def test_ledger_verify_endpoint():
    r = client.get("/api/ledger/verify")
    assert r.status_code == 200
    assert r.json()["intact"] is True
