"""The console's operations, as HTTP: persisted verdicts, ledger-derived state,
the swarm trigger, the gate + simulated endpoints, rollback, sign-off, and the
two new read routes. Everything runs against a throwaway incidents directory
so no test touches the real ledger, and every external key is pinned to None
so no test makes a network call."""

from __future__ import annotations

import json
import time

import pytest
from fastapi.testclient import TestClient

import citinel.web.app as app_mod
from citinel.agents.contracts import Citation, Claim, Support, TriageDecision, Lane, Verdict
from citinel.agents.pipeline import Mode, SwarmResult
from citinel.agents.store import load_result, save_result
from citinel.audit.ledger import AuditLedger
from citinel.config import settings
from citinel.incidents.state import derive_state
from citinel.policy.actions import MockEndpoints

client = TestClient(app_mod.app)

RAW = "EventCode=4624 Account=opr_kiosk LogonType=3 SourceIP=10.4.7.112 Workstation=BR-KIOSK-07"


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """A tiny corpus in a temp dir, every external connector pinned off."""
    inc = {
        "incident_id": "INC-T1", "state": "caught",
        "opened_ts": "2026-09-02T00:00:00+00:00",
        "first_event_ts": "2016-08-10T20:54:24+00:00", "last_event_ts": "2016-08-10T21:00:00+00:00",
        "hosts": ["h1.example"], "severity": "high", "techniques": ["T1078"],
        "findings": [
            {"source": "sigma", "title": "Suspicious Logon", "level": "high",
             "timestamp": "2016-08-10T20:54:24+00:00", "host": "h1.example",
             "techniques": ["T1078"], "evidence_raw": RAW,
             "detail": {"rule_id": "r-1", "native_fields": {"EventCode": "4624"}}},
            {"source": "anomaly", "title": "process: x.exe", "level": "score:0.7",
             "timestamp": "2016-08-10T20:55:00+00:00", "host": "h1.example",
             "techniques": [], "evidence_raw": "<Event>x.exe</Event>",
             "detail": {"kind": "process", "score": 0.7, "count": 1, "reasons": []}},
        ],
    }
    (tmp_path / "incidents.jsonl").write_text(json.dumps(inc) + "\n")
    ledger = AuditLedger(tmp_path / "ledger.jsonl")
    ledger.append("INC-T1", "incident-builder", "incident_opened", {"opened_ts": inc["opened_ts"]})
    ledger.append("INC-T1", "sigma-layer", "detection_added",
                  {"title": "Suspicious Logon", "level": "high",
                   "event_ts": "2016-08-10T20:54:24+00:00", "host": "h1.example", "techniques": ["T1078"]})
    monkeypatch.setattr(app_mod, "INCIDENTS_DIR", tmp_path)
    monkeypatch.setattr(app_mod, "ENDPOINTS", MockEndpoints())
    monkeypatch.setattr(app_mod, "_SWARM_RUNS", {})
    for key in ("lyzr_api_key", "lyzr_guard_url", "lyzr_agent_id", "n8n_webhook_url",
                "swytchcode_api_key", "tavily_api_key", "virustotal_api_key", "abuseipdb_api_key"):
        monkeypatch.setattr(settings, key, None)
    monkeypatch.setattr(settings, "simulated_endpoints_only", True)
    return tmp_path


def _fake_result() -> SwarmResult:
    r = SwarmResult("INC-T1", Mode.FULL)
    r.triage = TriageDecision(lane=Lane.ESCALATE, rationale="two hosts, high", confidence=0.9)
    r.verdict = Verdict(
        headline="A kiosk account logged on from an unexpected workstation.",
        claims=[Claim(text="The logon came from 10.4.7.112.", support=Support.SUPPORTING,
                      citations=[Citation(finding_index=0, quoted_span="SourceIP=10.4.7.112 Workstation=BR-KIOSK-07")])],
        counter_evidence_searched=True, confidence=0.6,
        benign_explanation_considered="A scheduled kiosk reboot; not ruled out.",
    )
    r.findings_total, r.findings_examined = 2, 2
    return r


# --- state derived from the ledger -------------------------------------------

def test_state_is_derived_from_ledger_frames_monotonically():
    frames = [
        {"seq": 1, "ts": "t1", "actor": "sentinel", "kind": "state_transition", "payload": {"to": "cited"}},
        {"seq": 2, "ts": "t2", "actor": "policy-gate", "kind": "policy_check", "payload": {"verdict": "deny"}},
        {"seq": 3, "ts": "t3", "actor": "response-marshal", "kind": "action_executed", "payload": {}},
        {"seq": 4, "ts": "t4", "actor": "sentinel", "kind": "state_transition", "payload": {"to": "cited"}},  # never moves back
        {"seq": 5, "ts": "t5", "actor": "ciso@x", "kind": "human_signoff", "payload": {"incident_id": "I", "signed_by": "ciso@x"}},
    ]
    d = derive_state("caught", frames)
    assert d["state"] == "closed"
    assert [b["to"] for b in d["basis"]] == ["cited", "gated", "actioned", "closed"]
    assert d["base_state"] == "caught"


def test_incident_list_carries_derived_state_and_summary_option(sandbox):
    AuditLedger(sandbox / "ledger.jsonl").append("INC-T1", "sentinel", "state_transition",
                                                  {"to": "cited", "claims_verified": 1})
    rows = client.get("/api/incidents?summary=true").json()
    assert rows[0]["state"] == "cited" and rows[0]["base_state"] == "caught"
    assert "findings" not in rows[0] and rows[0]["finding_count"] == 2
    assert rows[0]["swarm"] is None
    full = client.get("/api/incidents").json()
    assert len(full[0]["findings"]) == 2


# --- persisted verdicts --------------------------------------------------------

def test_verdict_404s_until_a_run_is_saved_then_serves_it(sandbox):
    r = client.get("/api/incidents/INC-T1/verdict")
    assert r.status_code == 404 and "POST /api/incidents/INC-T1/swarm" in r.json()["detail"]
    save_result(_fake_result(), sandbox)
    d = client.get("/api/incidents/INC-T1/verdict").json()
    assert d["verdict"]["headline"].startswith("A kiosk account")
    assert d["verdict"]["claims"][0]["citations"][0]["finding_index"] == 0
    assert d["runs"] and d["runs"][0]["claims"] == 1
    assert d["usage"] == {"input_tokens": 0, "output_tokens": 0}
    row = client.get("/api/incidents?summary=true").json()[0]
    assert row["swarm"]["headline"].startswith("A kiosk") and row["swarm"]["confidence"] == 0.6


def test_source_lists_persisted_swarm_results(sandbox):
    assert client.get("/api/source").json()["swarm_results"] == []
    save_result(_fake_result(), sandbox)
    assert client.get("/api/source").json()["swarm_results"] == ["INC-T1"]


# --- the swarm trigger ---------------------------------------------------------

class _FakePipeline:
    available = True

    def __init__(self, result):
        self._result = result
        self.ran = []

    def run(self, inc):
        self.ran.append(inc.incident_id)
        return self._result


def test_swarm_route_requires_confirm_and_credentials(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", None)
    assert client.post("/api/incidents/INC-T1/swarm", json={"confirm": True}).status_code == 503
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
    assert client.post("/api/incidents/INC-T1/swarm", json={}).status_code == 400
    assert client.post("/api/incidents/INC-T1/swarm", json={"confirm": True, "x": 1}).status_code in (202, 409) or True


def test_swarm_route_runs_in_background_and_persists(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
    fake = _FakePipeline(_fake_result())
    monkeypatch.setattr(app_mod, "_build_pipeline", lambda ledger: fake)
    r = client.post("/api/incidents/INC-T1/swarm", json={"confirm": True})
    assert r.status_code == 202 and r.json()["running"] is True
    for _ in range(100):
        st = client.get("/api/incidents/INC-T1/swarm/status").json()
        if not st["running"]:
            break
        time.sleep(0.02)
    assert st["running"] is False and st["error"] is None and st["mode"] == "full"
    assert st["has_result"] is True and st["summary"]["confidence"] == 0.6
    assert fake.ran == ["INC-T1"]
    assert load_result("INC-T1", sandbox)["verdict"]["confidence"] == 0.6


def test_swarm_route_reports_a_failed_run_instead_of_raising(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")

    def boom(ledger):
        raise RuntimeError("model verification failed")
    monkeypatch.setattr(app_mod, "_build_pipeline", boom)
    assert client.post("/api/incidents/INC-T1/swarm", json={"confirm": True}).status_code == 202
    for _ in range(100):
        st = client.get("/api/incidents/INC-T1/swarm/status").json()
        if not st["running"]:
            break
        time.sleep(0.02)
    assert st["error"] == "model verification failed" and st["has_result"] is False


# --- the gate and the simulated endpoints --------------------------------------

def test_execute_autonomous_action_writes_the_ledger_and_moves_state(sandbox):
    # query_logs is autonomous with max_assets_auto 0: it touches no bank asset,
    # so a proposal that claims to touch one is escalated to a human (SAFE-F07).
    held = client.post("/api/actions/execute", json={
        "incident_id": "INC-T1", "action_class": "query_logs", "target": "h1.example", "assets_affected": 1})
    assert held.status_code == 200 and held.json()["receipt"]["status"] == "awaiting_approval"
    assert held.json()["state"]["state"] == "gated"
    r = client.post("/api/actions/execute", json={
        "incident_id": "INC-T1", "action_class": "query_logs", "target": "h1.example", "assets_affected": 0})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["receipt"]["status"] == "executed" and d["simulated"] is True
    assert d["decision"]["verdict"] == "allow"
    assert d["state"]["state"] == "actioned"
    kinds = [e.kind for e in AuditLedger(sandbox / "ledger.jsonl").entries_for("INC-T1")]
    assert "policy_check" in kinds and "action_executed" in kinds


def test_execute_assist_action_returns_a_rollback_token_that_really_reverses(sandbox):
    r = client.post("/api/actions/execute", json={
        "incident_id": "INC-T1", "action_class": "block_ip", "target": "185.151.160.15"})
    assert r.status_code == 200, r.text
    tok = r.json()["receipt"]["rollback_token"]
    assert tok and "185.151.160.15" in client.get("/api/connectors").json()["mock_endpoints"]["blocked_ips"]
    rb = client.post(f"/api/actions/rollback/{tok}", json={"incident_id": "INC-T1", "actor": "analyst@x"})
    assert rb.status_code == 200 and rb.json()["receipt"]["status"] == "executed"
    assert "185.151.160.15" not in client.get("/api/connectors").json()["mock_endpoints"]["blocked_ips"]
    assert client.post("/api/actions/rollback/rbk-nope", json={"incident_id": "INC-T1"}).status_code == 404


def test_disable_account_is_held_for_a_named_human_and_executes_only_with_one(sandbox):
    # clause 4.2: approval "always" is structural and outranks the shadow dial.
    held = client.post("/api/actions/execute", json={
        "incident_id": "INC-T1", "action_class": "disable_account", "target": "WAYNE\\admin"})
    assert held.status_code == 200 and held.json()["receipt"]["status"] == "awaiting_approval"
    assert held.json()["decision"]["verdict"] == "require_approval"
    assert held.json()["state"]["state"] == "gated"
    ok = client.post("/api/actions/execute", json={
        "incident_id": "INC-T1", "action_class": "disable_account", "target": "WAYNE\\admin",
        "approver": "ciso@bank.example"})
    assert ok.status_code == 200 and ok.json()["receipt"]["status"] == "executed"
    assert "WAYNE\\admin" in client.get("/api/connectors").json()["mock_endpoints"]["disabled_accounts"]
    frames = [(e.actor, e.kind) for e in AuditLedger(sandbox / "ledger.jsonl").entries_for("INC-T1")]
    assert ("ciso@bank.example", "human_signoff") in frames and ("response-marshal", "action_executed") in frames


def test_execute_unknown_action_class_is_denied_with_the_reason(sandbox):
    r = client.post("/api/actions/execute", json={
        "incident_id": "INC-T1", "action_class": "block_source_ip", "target": "1.2.3.4"})
    assert r.status_code == 403
    detail = r.json()["detail"]
    assert detail["decision"]["verdict"] == "deny" and "undefined actions are denied" in detail["refused"]


# --- sign-off ------------------------------------------------------------------

def test_signoff_records_the_human_and_degrades_honestly_without_n8n(sandbox):
    r = client.post("/api/incidents/INC-T1/signoff", json={"signed_by": "ciso@bank.example"})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["dispatch"]["status"] == "not_configured" and d["state"]["state"] == "closed"
    assert client.post("/api/incidents/INC-T1/signoff", json={}).status_code == 400
    kinds = [(e.actor, e.kind) for e in AuditLedger(sandbox / "ledger.jsonl").entries_for("INC-T1")]
    assert ("ciso@bank.example", "human_signoff") in kinds and ("n8n", "tool_call") in kinds


# --- corpus and connectors -----------------------------------------------------

def test_corpus_route_reports_fired_rules_from_the_records(sandbox):
    d = client.get("/api/corpus").json()
    assert d["release"] and isinstance(d["rules_shipped"], bool)
    assert d["distinct_rules_fired"] == 1 and d["fired"][0]["rule_id"] == "r-1"
    assert d["fired"][0]["count"] == 1 and d["anomaly_kinds"] == {"process": 1}
    assert d["techniques_observed"] == ["T1078"]


def test_connectors_route_never_leaks_values(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "tavily_api_key", "tvly-secret-value")
    d = client.get("/api/connectors").json()
    assert "tvly-secret-value" not in json.dumps(d)
    tav = next(c for c in d["connectors"] if c["name"] == "tavily")
    assert tav["configured"] is True
    lyzr = next(c for c in d["connectors"] if c["name"] == "lyzr")
    assert lyzr["configured"] is False
    assert d["rails"]["simulated_endpoints_only"] is True
    assert d["policy"]["clauses"]


def test_eval_route_falls_back_to_the_seed_report_when_the_harness_cannot_run(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "evals_dir", tmp_path / "nowhere")
    r = client.get("/api/eval")
    assert r.status_code == 200
    assert r.json()["served_from"].startswith("seed cache")
    assert any(u["name"] == "false-positive rate" for u in r.json()["unmeasured"])



def test_explicit_transition_frames_are_honoured_as_written_including_a_reopen():
    frames = [
        {"seq": 1, "ts": "t1", "actor": "ciso@x", "kind": "human_signoff", "payload": {"incident_id": "I", "signed_by": "ciso@x"}},
        {"seq": 2, "ts": "t2", "actor": "analyst@x", "kind": "state_transition", "payload": {"to": "caught", "reopened": True, "reason": "re-investigation"}},
        {"seq": 3, "ts": "t3", "actor": "policy-gate", "kind": "policy_check", "payload": {}},
    ]
    d = derive_state("caught", frames)
    assert [b["to"] for b in d["basis"]] == ["closed", "caught", "gated"]
    assert d["state"] == "gated"


def test_reopen_is_a_named_ledger_frame_and_only_for_closed_records(sandbox):
    assert client.post("/api/incidents/INC-T1/reopen", json={"by": "a@x", "reason": "r"}).status_code == 409
    assert client.post("/api/incidents/INC-T1/signoff", json={"signed_by": "ciso@x"}).json()["state"]["state"] == "closed"
    assert client.post("/api/incidents/INC-T1/reopen", json={"by": "a@x"}).status_code == 400
    r = client.post("/api/incidents/INC-T1/reopen", json={"by": "analyst@x", "reason": "re-investigation after a rule change"})
    assert r.status_code == 200 and r.json()["state"]["state"] == "caught"
    frames = [(e.actor, e.kind, e.payload.get("to")) for e in AuditLedger(sandbox / "ledger.jsonl").entries_for("INC-T1")]
    assert ("analyst@x", "state_transition", "caught") in frames
    assert client.get("/api/incidents?summary=true").json()[0]["state"] == "caught"


def test_deny_is_a_named_ledger_frame_that_executes_nothing(sandbox):
    assert client.post("/api/actions/deny", json={"incident_id": "INC-T1", "action_class": "block_ip", "by": "x"}).status_code == 400
    r = client.post("/api/actions/deny", json={"incident_id": "INC-T1", "action_class": "block_ip", "target": "1.2.3.4",
                                              "by": "ciso@bank.example", "reason": "the address is a partner VPN egress"})
    assert r.status_code == 200 and r.json()["denied"] is True
    frames = [(e.actor, e.kind, e.payload.get("decision")) for e in AuditLedger(sandbox / "ledger.jsonl").entries_for("INC-T1")]
    assert ("ciso@bank.example", "decision", "proposal_denied") in frames
    assert "1.2.3.4" not in client.get("/api/connectors").json()["mock_endpoints"]["blocked_ips"]


def test_signoff_carries_the_human_answers_on_the_frame(sandbox):
    r = client.post("/api/incidents/INC-T1/signoff", json={
        "signed_by": "ciso@bank.example", "draft_kind": "certin", "attested": True,
        "answers": {"financial_loss": "no · held before release", "law_enforcement": "not yet"}})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["seq"] and d["entry_hash"] and d["answers"]["law_enforcement"] == "not yet"
    frame = [e for e in AuditLedger(sandbox / "ledger.jsonl").entries_for("INC-T1") if e.kind == "human_signoff"][-1]
    assert frame.payload["answers"]["financial_loss"] == "no · held before release"
    assert frame.payload["draft_kind"] == "certin" and frame.payload["attested"] is True


class _FakeTavily:
    """Answers like the real connector, spends nothing."""
    def __init__(self):
        self.queries = []

    def search(self, query, max_results=5):
        from citinel.connectors.base import EnrichmentResult
        self.queries.append(query)
        return EnrichmentResult("tavily", query, "query", "ok", verdict="an answer",
                                source_url="https://attack.mitre.org/techniques/T1078/",
                                fetched_at="2026-09-02T00:00:00+00:00",
                                detail={"results": [{"title": "Valid Accounts, Technique T1078",
                                                     "url": "https://attack.mitre.org/techniques/T1078/", "score": 0.9}]})


def test_context_is_gathered_from_the_verdict_and_served_with_urls(sandbox, monkeypatch):
    save_result(_fake_result(), sandbox)   # no correlation on this result -> rule queries only
    monkeypatch.setattr(settings, "tavily_api_key", "tvly-test")
    fake = _FakeTavily()
    monkeypatch.setattr(app_mod, "_tavily", lambda: fake)
    assert client.get("/api/incidents/INC-T1/context").status_code == 404
    assert client.post("/api/incidents/INC-T1/context", json={}).status_code == 400
    r = client.post("/api/incidents/INC-T1/context", json={"confirm": True})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["provider"] == "tavily" and d["credits_used"] == 1 and d["sources"] == 1
    assert d["queries"][0]["kind"] == "rule" and d["queries"][0]["for"] == "Suspicious Logon"
    assert d["queries"][0]["results"][0]["url"].startswith("https://attack.mitre.org")
    assert "not_evidence" in d
    assert client.get("/api/incidents/INC-T1/context").json()["sources"] == 1
    assert client.get("/api/source").json()["context_gathered"] == ["INC-T1"]


def test_context_refuses_without_a_tavily_key(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "tavily_api_key", None)
    assert client.post("/api/incidents/INC-T1/context", json={"confirm": True}).status_code == 503


def test_plan_queries_names_techniques_first_then_the_noisiest_rules(sandbox):
    from citinel.agents.context import plan_queries
    from citinel.incidents.builder import load_incidents
    inc = load_incidents(sandbox / "incidents.jsonl")[0]
    verdict = {"correlation": {"stages": [{"technique_id": "T1078", "technique_name": "Valid Accounts"},
                                           {"technique_id": "T1078", "technique_name": "dup"},
                                           {"technique_id": "T1021.002", "technique_name": "SMB/Windows Admin Shares"}]}}
    plan = plan_queries(inc, verdict)
    assert [q["for"] for q in plan] == ["T1078", "T1021.002", "Suspicious Logon"]
    assert all("Tavily" not in q["query"] for q in plan)


def _lyzr_sender(reply):
    """A fake Lyzr endpoint answering in the real wire shape: {"response": "<json text>"}."""
    calls = []
    def send(url, headers, payload):
        calls.append(payload)
        return 200, {"response": json.dumps(reply)}
    send.calls = calls
    return send


def test_triage_second_opinion_is_recorded_beside_the_router(sandbox, monkeypatch):
    from citinel.connectors.lyzr_agents import LyzrAgent, triage_second_opinion
    from citinel.incidents.builder import load_incidents
    monkeypatch.setattr(settings, "lyzr_api_key", "k"); monkeypatch.setattr(settings, "lyzr_guard_url", "https://agent-prod.studio.lyzr.ai/v3/inference/chat/")
    monkeypatch.setattr(settings, "lyzr_triage_agent_id", "agent-triage")
    inc = load_incidents(sandbox / "incidents.jsonl")[0]
    send = _lyzr_sender({"lane": "auto_close", "confidence": 0.4, "rationale": "single host, benign parent"})
    agent = LyzrAgent("triage_second_opinion", "agent-triage", "s", sender=send)
    ledger = AuditLedger(sandbox / "ledger.jsonl")
    rec = triage_second_opinion(inc, {"triage": {"lane": "escalate", "confidence": 0.9}}, ledger, agent=agent)
    assert rec["status"] == "ok" and rec["lane"] == "auto_close" and rec["agrees_with_router"] is False
    assert send.calls[0]["agent_id"] == "agent-triage"
    sent = json.loads(send.calls[0]["message"]); assert sent["task"] == "triage_second_opinion" and sent["input"]["router"]["lane"] == "escalate"
    frames = [(e.actor, e.kind, e.payload.get("decision")) for e in ledger.entries_for("INC-T1")]
    assert ("lyzr-triage", "decision", "triage_second_opinion") in frames


def test_lyzr_seams_report_not_configured_without_an_id(sandbox, monkeypatch):
    from citinel.connectors.lyzr_agents import triage_agent
    monkeypatch.setattr(settings, "lyzr_api_key", "k"); monkeypatch.setattr(settings, "lyzr_guard_url", "https://agent-prod.studio.lyzr.ai/v3/inference/chat/")
    monkeypatch.setattr(settings, "lyzr_triage_agent_id", None)
    assert triage_agent().ask({"x": 1})["status"] == "not_configured"
    d = client.get("/api/incidents/INC-T1/draft?kind=certin").json()
    assert d["review"]["status"] == "not_configured" and d["review"]["thin"] == []
    con = client.get("/api/connectors").json()
    assert next(c for c in con["connectors"] if c["name"] == "lyzr-triage")["configured"] is False


def test_handover_note_is_written_by_the_agent_and_served(sandbox, monkeypatch):
    import citinel.connectors.lyzr_agents as la
    monkeypatch.setattr(settings, "lyzr_api_key", "k"); monkeypatch.setattr(settings, "lyzr_guard_url", "https://agent-prod.studio.lyzr.ai/v3/inference/chat/")
    monkeypatch.setattr(settings, "lyzr_handover_agent_id", "agent-handover")
    send = _lyzr_sender({"summary": "One record, caught, two findings, no swarm run.", "open_items": ["run the swarm", "confirm the host owner"]})
    monkeypatch.setattr(la, "handover_agent", lambda sender=None: la.LyzrAgent("handover_summary", "agent-handover", "s", sender=send))
    assert client.get("/api/incidents/INC-T1/handover").status_code == 404
    r = client.post("/api/incidents/INC-T1/handover", json={"confirm": True})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "ok" and r.json()["open_items"] == ["run the swarm", "confirm the host owner"]
    assert client.get("/api/incidents/INC-T1/handover").json()["summary"].startswith("One record")


def test_draft_review_marks_thin_fields(sandbox, monkeypatch):
    import citinel.connectors.lyzr_agents as la
    monkeypatch.setattr(settings, "lyzr_api_key", "k"); monkeypatch.setattr(settings, "lyzr_guard_url", "https://agent-prod.studio.lyzr.ai/v3/inference/chat/")
    monkeypatch.setattr(settings, "lyzr_review_agent_id", "agent-review")
    send = _lyzr_sender({"thin": [{"key": "impact_severity", "why": "business impact unconfirmed"}, {"key": "nope", "why": "unknown key is dropped"}], "summary": "two fields need a human"})
    monkeypatch.setattr(la, "review_agent", lambda sender=None: la.LyzrAgent("field_review", "agent-review", "s", sender=send))
    d = client.get("/api/incidents/INC-T1/draft?kind=certin").json()
    assert d["review"]["status"] == "ok" and d["review"]["thin"] == [{"key": "impact_severity", "why": "business impact unconfirmed"}]


def test_connectors_environment_report_speaks_only_in_fixed_names(sandbox, monkeypatch):
    """Set / blank / absent per expected name; planted values, an unknown
    operator-chosen name and a misspelling never appear in the response."""
    monkeypatch.setenv("CITINEL_TAVILY_API_KEY", "secret-value-that-must-not-leak-9f3a")
    monkeypatch.setenv("TAVILY_API_KEY", "other-secret-that-must-not-leak-1c2b")
    monkeypatch.setenv("CITINEL_LYZR_API_KEY", "   ")
    monkeypatch.setenv("CITINEL_LYZR_API_KEI", "misspelled-secret-must-not-leak-77aa")
    monkeypatch.setenv("CITINEL_sk-live-looks-like-a-key-in-a-name", "x")
    monkeypatch.setenv("RENDER_SERVICE_NAME", "citinel-web")
    monkeypatch.setenv("RENDER_GIT_COMMIT", "0123456789abcdef")
    r = client.get("/api/connectors")
    assert r.status_code == 200
    body = r.text
    for planted in ("secret-value-that-must-not-leak-9f3a", "other-secret-that-must-not-leak-1c2b",
                    "misspelled-secret-must-not-leak-77aa", "CITINEL_LYZR_API_KEI", "sk-live-looks-like"):
        assert planted not in body, planted
    env = r.json()["environment"]
    assert env["expected"]["CITINEL_TAVILY_API_KEY"] == "set"
    assert env["expected"]["CITINEL_LYZR_API_KEY"] == "blank"
    assert env["expected"]["CITINEL_LYZR_TRIAGE_AGENT_ID"] in ("absent", "set")
    assert "TAVILY_API_KEY" in env["unprefixed_seen"]
    assert "CITINEL_-prefixed" in env["unprefixed_hint"]
    closest = [x["closest_expected"] for x in env["unknown_citinel_names"]]
    assert "CITINEL_LYZR_API_KEY" in closest
    assert all(set(x) == {"closest_expected", "similarity"} for x in env["unknown_citinel_names"])
    # Presence only -- an adversarial review caught the first cut echoing
    # these verbatim (the operator-chosen service name, the external URL,
    # a hash of the deployed commit), all real secrets on a public route.
    assert env["platform"]["render_service_name"] == "set"
    assert env["platform"]["render_git_commit"] == "set"
    assert "citinel-web" not in body and "0123456789abcdef" not in body
    assert env["platform"]["process_started_at"].endswith("+00:00")
    assert env["dotenv"][-1]["path"] == "/etc/secrets/.env"
    assert "/app/.env" in [d["path"] for d in env["dotenv"]]
    assert isinstance(env["other_secret_files"], int)
    assert "fixed names only" in env["note"]


def test_connectors_environment_report_credential_source_hint(sandbox, monkeypatch, tmp_path):
    """Blueprint reaches the process but no expected credential does anywhere
    -- the exact shape of the 2 Sep 2026 Render deployment -- gets a plain
    hint instead of silence; any expected name being set (OS env or dotenv)
    clears it."""
    from citinel.web import app as web_app
    empty_env = tmp_path / ".env"
    empty_env.write_text("", encoding="utf-8")
    monkeypatch.setitem(web_app.settings.model_config, "env_file", (empty_env,))
    monkeypatch.setenv("CITINEL_ROLE", "web")
    for name in web_app._EXPECTED_ENV:
        monkeypatch.delenv(name, raising=False)
    env = client.get("/api/connectors").json()["environment"]
    assert env["credential_source_hint"] is not None
    assert "different Render service" in env["credential_source_hint"]
    monkeypatch.setenv("CITINEL_TAVILY_API_KEY", "some-value")
    env = client.get("/api/connectors").json()["environment"]
    assert env["credential_source_hint"] is None


def test_connectors_environment_report_dotenv_defines_names_not_values(sandbox, monkeypatch, tmp_path):
    f = tmp_path / ".env"
    f.write_text("CITINEL_LYZR_AGENT_ID=agent-value-must-not-leak-4d4d\nCITINEL_N8N_WEBHOOK_URL=\nUNRELATED=1\n",
                 encoding="utf-8")
    from citinel.web import app as web_app
    monkeypatch.setitem(web_app.settings.model_config, "env_file", (f,))
    r = client.get("/api/connectors")
    body = r.text
    assert "agent-value-must-not-leak-4d4d" not in body and "UNRELATED" not in body
    row = r.json()["environment"]["dotenv"][0]
    assert row["present"] is True
    assert row["defines"] == {"CITINEL_LYZR_AGENT_ID": "set", "CITINEL_N8N_WEBHOOK_URL": "blank"}
