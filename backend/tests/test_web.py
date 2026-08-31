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


# --- role-adaptive projection (two roles, one record) ------------------------

def test_incident_defaults_to_analyst_full_depth_with_no_role_header():
    r = client.get("/api/incidents/INC-0417")
    assert r.status_code == 200
    body = r.json()
    assert body["_projection"]["role"] == "analyst"
    assert body["_projection"]["depth"] == "full"
    assert "findings" in body


def test_ciso_gets_the_position_view_with_findings_folded_and_disclosed():
    r = client.get("/api/incidents/INC-0417", headers={"X-Citinel-Role": "ciso"})
    assert r.status_code == 200
    body = r.json()
    assert body["_projection"]["depth"] == "position"
    assert "findings" not in body
    # folded, and SAID to be folded -- never a thinner record that looks whole
    assert body["_projection"]["omitted"] == ["findings"]
    assert body["finding_count"] > 0


def test_ciso_expand_returns_full_depth_nothing_is_withheld():
    """The 'one click deeper' promise: this is depth adaptation, not access
    control, so expand must return everything to a CISO too."""
    r = client.get("/api/incidents/INC-0417?expand=true",
                   headers={"X-Citinel-Role": "ciso"})
    assert r.status_code == 200
    body = r.json()
    assert body["_projection"]["depth"] == "full"
    assert "findings" in body


def test_unknown_role_defaults_to_more_detail_not_less():
    r = client.get("/api/incidents/INC-0417", headers={"X-Citinel-Role": "wat"})
    assert r.json()["_projection"]["role"] == "analyst"
    assert "findings" in r.json()


# --- data-source honesty ------------------------------------------------------

def test_source_endpoint_reports_which_corpus_is_answering():
    """A seed-backed deployment must not pass as live. Regression guard for a
    deploy bug where a fresh Render service served an empty list with a 200,
    indistinguishable from a quiet night in the SOC."""
    r = client.get("/api/source")
    assert r.status_code == 200
    body = r.json()
    assert body["source"] in {"live", "seed"}
    assert body["description"]
    assert isinstance(body["incidents_file_present"], bool)


# --- eval harness: the credibility screen -------------------------------------

def test_eval_endpoint_serves_measurements_with_denominators():
    r = client.get("/api/eval")
    assert r.status_code == 200
    body = r.json()
    assert body["swarm_evaluated"] is False, "no swarm has run; must not claim otherwise"
    # every rate-style measurement carries the count it came from
    for m in body["measured"]:
        if "rate" in m:
            assert m.get("denominator"), f"{m['name']} published a rate with no denominator"


def test_eval_endpoint_refuses_to_publish_an_unmeasured_fp_rate():
    """The load-bearing one. CITINEL's <10% FP figure is a target that has
    never been measured; the endpoint must say UNMEASURED rather than supply
    a plausible number, and must say what is missing."""
    body = client.get("/api/eval").json()
    fp = [u for u in body["unmeasured"] if "false-positive" in u["name"]]
    assert fp, "the FP rate must be explicitly listed as unmeasured, not omitted"
    assert fp[0]["status"] == "UNMEASURED"
    assert fp[0]["required_to_measure"]

    # and it must not appear as a measurement anywhere
    names = " ".join(m["name"].lower() for m in body["measured"])
    assert "false-positive" not in names and "false positive" not in names
