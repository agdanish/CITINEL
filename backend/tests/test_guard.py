"""Tests for the governance PII guard and the Lyzr second-tier seam."""

from __future__ import annotations

import json

import pytest

from citinel.agents.guard import GuardResult, screen_draft, screen_text
from citinel.compliance.drafter import draft_dpdp
from citinel.connectors.lyzr import LyzrGuard, LyzrObserver, AgentEvent, NullObserver
from citinel.incidents.model import Finding, Incident, State


def test_high_confidence_types_are_caught_and_masked():
    text = ("contact ciso@waynecorp.com PAN ABCDE1234F "
            "SID S-1-5-21-11-22-33-1109 account bob.smith.WAYNECORPINC")
    found = {f.pii_type: f for f in screen_text(text)}
    assert set(found) == {"email", "pan", "windows_sid", "domain_account"}
    assert found["email"].masked == "c***@waynecorp.com"
    assert "1234F" not in found["pan"].masked          # masked, not echoed
    assert found["windows_sid"].masked.endswith("1109")


def test_sid_match_is_case_insensitive():
    # logs lowercase the SID; the guard must still catch it
    assert screen_text(r"key=hku\s-1-5-21-67332772-3493699611-3403467266-1109\run")


def test_numeric_types_require_a_corroborating_label():
    # bare digit runs (a PID, a byte count) must NOT be flagged
    assert screen_text("pid=384726154 bytes=9876543210 port=1122334455") == []
    # the same digits WITH a label are flagged
    assert any(f.pii_type == "aadhaar" for f in screen_text("Aadhaar: 1234 5678 9012"))
    assert any(f.pii_type == "indian_mobile" for f in screen_text("mobile 9876543210"))


def test_ioc_evidence_is_not_treated_as_pii():
    # IPs, hashes and ports are legitimate incident evidence, not PII
    ioc = "src 185.151.160.15:7787 sha256 a52ec0f10cbd9096cf886a13c1b67abf28756528"
    assert screen_text(ioc) == []


def _incident_with_pii_evidence() -> Incident:
    inc = Incident(incident_id="INC-0417", state=State.CITED, severity="high")
    inc.add_finding(Finding(
        source="anomaly", title="persistence: run key", level="score:0.8",
        timestamp="2016-08-24T16:48:41+00:00", host="we8105desk",
        evidence_raw=r'process_image="c:\Users\bob.smith.WAYNECORPINC\121214.tmp" '
                     r'key="HKU\s-1-5-21-67332772-3493699611-3403467266-1109\run"',
        detail={"kind": "persistence"}))
    return inc


def test_screen_draft_skips_placeholder_fields():
    # human-required fields are <placeholders>, not data -> no PII there
    draft = draft_dpdp(_incident_with_pii_evidence())
    result = screen_draft(draft)          # fields only, no extra evidence
    assert result.clean                   # placeholders carry no PII


def test_guard_flags_pii_in_evidence_the_signer_reads():
    inc = _incident_with_pii_evidence()
    draft = draft_dpdp(inc)
    evidence = "\n".join(f.evidence_raw for f in inc.findings)
    result = LyzrGuard().screen(draft, extra_evidence=evidence)
    types = {f.pii_type for f in result.findings}
    assert "windows_sid" in types and "domain_account" in types
    assert not result.clean
    assert "mitigates" in result.note.lower()          # honesty preserved


def test_lyzr_second_check_skipped_without_key(monkeypatch):
    from citinel.config import settings
    monkeypatch.setattr(settings, "lyzr_api_key", None)
    result = LyzrGuard().screen(draft_dpdp(_incident_with_pii_evidence()))
    assert result.checked_by == "citinel-local"        # local only, no crash


def test_lyzr_is_not_reachable_unless_explicitly_configured():
    # the base egress allow-list must NOT silently include any Lyzr host
    from citinel.agents.quarantine import EGRESS_ALLOW
    assert not any("lyzr" in h for h in EGRESS_ALLOW)


def test_lyzr_second_check_merges_findings_when_configured(monkeypatch):
    from citinel.config import settings
    monkeypatch.setattr(settings, "lyzr_api_key", "k")
    monkeypatch.setattr(settings, "lyzr_guard_url", "https://api.lyzr.ai/guard")
    monkeypatch.setattr(settings, "lyzr_agent_id", "a")
    called = []
    def sender(url, headers, payload):
        called.append(url)
        # the real Lyzr contract: chat-shaped in, {"response": "<json text>"} out
        assert set(payload) == {"user_id", "agent_id", "session_id", "message"}
        assert json.loads(payload["message"])["task"] == "pii_guard"
        reply = {"pii": [{"type": "name", "confidence": "medium", "masked": "J***"}]}
        return 200, {"response": json.dumps(reply)}
    result = LyzrGuard(sender=sender).screen(draft_dpdp(_incident_with_pii_evidence()))
    assert called == ["https://api.lyzr.ai/guard"]      # only the configured host
    assert result.checked_by == "citinel-local + lyzr"
    assert any(f.pii_type == "lyzr:name" for f in result.findings)


def test_lyzr_second_check_degrades_when_agent_replies_off_contract(monkeypatch):
    """The Studio agent not following its instructions (plain prose instead of
    JSON) must degrade to local-only, never raise or silently misread."""
    from citinel.config import settings
    monkeypatch.setattr(settings, "lyzr_api_key", "k")
    monkeypatch.setattr(settings, "lyzr_guard_url", "https://api.lyzr.ai/guard")
    monkeypatch.setattr(settings, "lyzr_agent_id", "a")
    sender = lambda url, h, p: (200, {"response": "Sure, here is the answer: no PII found."})
    result = LyzrGuard(sender=sender).screen(draft_dpdp(_incident_with_pii_evidence()))
    assert result.checked_by == "citinel-local"          # second check never merged in


def test_null_observer_never_touches_the_network():
    NullObserver().observe(AgentEvent("INC-0417", "sentinel", "start", {}))  # no-op, no raise


def test_lyzr_observer_degrades_without_config(monkeypatch):
    from citinel.config import settings
    monkeypatch.setattr(settings, "lyzr_api_key", None)
    obs = LyzrObserver(sender=lambda *a: (_ for _ in ()).throw(AssertionError("called")))
    obs.observe(AgentEvent("INC-0417", "sentinel", "start", {}))
    assert obs.forwarded == 0


# --- Lyzr attachment point 4: the audit-log external witness ------------------

def _configured_lyzr(monkeypatch):
    from citinel.config import settings
    monkeypatch.setattr(settings, "lyzr_api_key", "lyzr-test-key")
    monkeypatch.setattr(settings, "lyzr_guard_url", "https://agent.lyzr.ai/v1/guard")
    monkeypatch.setattr(settings, "lyzr_agent_id", "agent-123")


def test_a_failing_witness_never_blocks_an_append(tmp_path, monkeypatch):
    """The load-bearing guarantee: the local ledger is canonical. A bank's SOC
    must not stop recording because a third-party mirror is down."""
    from citinel.audit.ledger import AuditLedger
    from citinel.connectors.lyzr import LyzrLedgerMirror
    _configured_lyzr(monkeypatch)

    def exploding_sender(url, headers, payload):
        raise ConnectionError("witness is down")

    led = AuditLedger(tmp_path / "l.jsonl", sink=LyzrLedgerMirror(sender=exploding_sender))
    entry = led.append("INC-0417", "sentinel", "note", {"n": 1})

    assert entry.seq == 1, "the append must have succeeded"
    assert led.sink_failures == 1, "and the failure must be counted, not silent"
    ok, _ = led.verify_chain()
    assert ok, "the local chain is unaffected by the witness failing"


def test_entries_are_mirrored_when_the_witness_is_configured(tmp_path, monkeypatch):
    from citinel.audit.ledger import AuditLedger
    from citinel.connectors.lyzr import LyzrLedgerMirror
    _configured_lyzr(monkeypatch)
    seen = []

    def sender(url, headers, payload):
        assert set(payload) == {"user_id", "agent_id", "session_id", "message"}
        assert payload["session_id"] == LyzrLedgerMirror._SESSION_ID
        seen.append(json.loads(payload["message"]))
        return 200, {"response": json.dumps({"ok": True})}

    mirror = LyzrLedgerMirror(sender=sender)
    led = AuditLedger(tmp_path / "l.jsonl", sink=mirror)
    led.append("INC-0417", "sentinel", "note", {"n": 1})
    led.append("INC-0417", "router", "decision", {"lane": "escalate"})

    assert mirror.mirrored == 2
    assert [m["task"] for m in seen] == ["ledger_record", "ledger_record"]
    assert seen[1]["entry"]["entry_hash"] == led.head, "the witness sees the real chain head"


def test_witness_agreement_is_reported_when_heads_match(tmp_path, monkeypatch):
    from citinel.audit.ledger import AuditLedger
    from citinel.connectors.lyzr import LyzrLedgerMirror
    _configured_lyzr(monkeypatch)
    led = AuditLedger(tmp_path / "l.jsonl")
    led.append("INC-0417", "sentinel", "note", {"n": 1})

    mirror = LyzrLedgerMirror(sender=lambda u, h, p: (
        200, {"response": json.dumps({"head": led.head, "count": 1})}))
    c = mirror.compare(led)
    assert c.status == "agreed"
    assert c.tamper_suspected is False


def test_wholesale_local_replacement_is_caught_by_the_witness(tmp_path, monkeypatch):
    """The exact gap a self-contained hash chain cannot see: rewrite the whole
    file with recomputed hashes and verify_chain passes. The witness does not."""
    from citinel.audit.ledger import AuditLedger
    from citinel.connectors.lyzr import LyzrLedgerMirror
    _configured_lyzr(monkeypatch)

    path = tmp_path / "l.jsonl"
    real = AuditLedger(path)
    real.append("INC-0417", "sentinel", "note", {"decision": "escalated to human"})
    witnessed_head = real.head

    # Attacker rewrites the ledger from scratch, recomputing every hash.
    path.unlink()
    forged = AuditLedger(path)
    forged.append("INC-0417", "sentinel", "note", {"decision": "auto-closed, benign"})

    ok, msg = forged.verify_chain()
    assert ok, "the forged chain verifies against itself -- this is the blind spot"

    mirror = LyzrLedgerMirror(
        sender=lambda u, h, p: (200, {"response": json.dumps({"head": witnessed_head, "count": 1})}))
    c = mirror.compare(forged)
    assert c.status == "diverged"
    assert c.tamper_suspected is True
    assert "investigate" in c.detail


def test_unreachable_witness_is_never_reported_as_agreement(tmp_path, monkeypatch):
    """'I could not check' must not render as 'I checked and it is fine.'"""
    from citinel.audit.ledger import AuditLedger
    from citinel.connectors.lyzr import LyzrLedgerMirror
    _configured_lyzr(monkeypatch)
    led = AuditLedger(tmp_path / "l.jsonl")
    led.append("INC-0417", "sentinel", "note", {"n": 1})

    def dead(url, headers, payload):
        raise TimeoutError("no route to host")

    c = LyzrLedgerMirror(sender=dead).compare(led)
    assert c.status == "unavailable"
    assert c.tamper_suspected is False
    assert "unreachable" in c.detail


def test_unconfigured_witness_says_the_chain_stands_alone(tmp_path, monkeypatch):
    from citinel.audit.ledger import AuditLedger
    from citinel.connectors.lyzr import LyzrLedgerMirror
    from citinel.config import settings
    monkeypatch.setattr(settings, "lyzr_api_key", None)
    led = AuditLedger(tmp_path / "l.jsonl")
    led.append("INC-0417", "sentinel", "note", {"n": 1})

    c = LyzrLedgerMirror().compare(led)
    assert c.status == "not_configured"
    assert "stands alone" in c.detail
    assert c.tamper_suspected is False


def test_default_ledger_has_a_null_sink_and_is_unaffected(tmp_path):
    from citinel.audit.ledger import AuditLedger, NullSink
    led = AuditLedger(tmp_path / "l.jsonl")
    assert isinstance(led.sink, NullSink)
    led.append("INC-0417", "sentinel", "note", {"n": 1})
    assert led.sink_failures == 0
