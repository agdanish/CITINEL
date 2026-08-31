"""Tests for the audit ledger and the five-state incident record."""

from __future__ import annotations

import json

import pytest

from citinel.audit.ledger import AuditLedger, LedgerError
from citinel.incidents.builder import _to_utc, build_incidents
from citinel.incidents.model import Incident, State, TransitionError


# --- ledger -----------------------------------------------------------------

def test_ledger_appends_and_verifies(tmp_path):
    led = AuditLedger(tmp_path / "l.jsonl")
    led.append("INC-0001", "sigma-layer", "detection_added", {"title": "x"})
    led.append("INC-0001", "incident-builder", "decision", {"decision": "sev"})
    ok, msg = led.verify_chain()
    assert ok and "2 entries" in msg


def test_ledger_rejects_unknown_kind(tmp_path):
    led = AuditLedger(tmp_path / "l.jsonl")
    with pytest.raises(LedgerError):
        led.append("INC-0001", "agent", "thinking_summary", {"text": "..."})


def test_ledger_requires_case_id(tmp_path):
    led = AuditLedger(tmp_path / "l.jsonl")
    with pytest.raises(LedgerError):
        led.append("", "agent", "note", {})


def test_ledger_detects_content_tampering(tmp_path):
    path = tmp_path / "l.jsonl"
    led = AuditLedger(path)
    led.append("INC-0001", "a", "note", {"v": 1})
    led.append("INC-0001", "a", "note", {"v": 2})
    lines = path.read_text().splitlines()
    e = json.loads(lines[0])
    e["payload"]["v"] = 999  # edit history in place
    lines[0] = json.dumps(e)
    path.write_text("\n".join(lines) + "\n")
    ok, msg = AuditLedger(path).verify_chain()
    assert not ok and "tampered" in msg


def test_ledger_detects_deletion(tmp_path):
    path = tmp_path / "l.jsonl"
    led = AuditLedger(path)
    for i in range(3):
        led.append("INC-0001", "a", "note", {"i": i})
    lines = path.read_text().splitlines()
    path.write_text("\n".join([lines[0], lines[2]]) + "\n")  # drop the middle
    ok, msg = AuditLedger(path).verify_chain()
    assert not ok


def test_case_id_reconstruction(tmp_path):
    """SDD Section 16 finding 4: the full chain from the case id alone."""
    led = AuditLedger(tmp_path / "l.jsonl")
    led.append("INC-0001", "a", "note", {})
    led.append("INC-0002", "a", "note", {})
    led.append("INC-0001", "b", "decision", {"d": 1})
    chain = led.entries_for("INC-0001")
    assert [e.actor for e in chain] == ["a", "b"]


def test_ledger_resumes_chain_across_reopen(tmp_path):
    path = tmp_path / "l.jsonl"
    AuditLedger(path).append("INC-0001", "a", "note", {})
    AuditLedger(path).append("INC-0001", "a", "note", {})  # reopened
    ok, msg = AuditLedger(path).verify_chain()
    assert ok and "2 entries" in msg


# --- state machine ----------------------------------------------------------

def test_happy_path_transitions():
    inc = Incident(incident_id="INC-0417")
    for s in (State.CITED, State.GATED, State.ACTIONED, State.CLOSED):
        inc.transition(s)
    assert inc.state is State.CLOSED


def test_cannot_skip_to_actioned():
    inc = Incident(incident_id="INC-0417")
    with pytest.raises(TransitionError):
        inc.transition(State.ACTIONED)


def test_closed_is_terminal():
    inc = Incident(incident_id="INC-0417", state=State.CLOSED)
    with pytest.raises(TransitionError):
        inc.transition(State.CITED)


def test_benign_close_allowed_before_action_only():
    inc = Incident(incident_id="INC-0001")
    inc.transition(State.CLOSED_BENIGN)  # from CAUGHT: fine
    inc2 = Incident(incident_id="INC-0002", state=State.ACTIONED)
    with pytest.raises(TransitionError):
        inc2.transition(State.CLOSED_BENIGN)  # after acting: must close properly


# --- builder ----------------------------------------------------------------

def _detection(ts, title="rule", host="h1"):
    return {"rule_id": "r", "rule_title": title, "level": "high",
            "techniques": ["T1490"], "timestamp": ts, "event_class": "sysmon",
            "host": host, "evidence": {"raw": "raw-line", "native_fields": {}}}


def test_gap_clustering_and_utc_normalization(tmp_path):
    det = tmp_path / "det.jsonl"
    rows = [
        _detection("2016-08-10T21:00:00+00:00"),
        # local-time source, same cluster: 15:10 -06:00 == 21:10 UTC
        _detection("2016-08-10T15:10:00-06:00"),
        # ten hours later: a new incident
        _detection("2016-08-11T07:00:00+00:00"),
    ]
    det.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    led = AuditLedger(tmp_path / "l.jsonl")
    rep = build_incidents(det, tmp_path / "none.jsonl", tmp_path / "inc.jsonl",
                          led, start=416)
    assert rep.incidents == 2
    first = rep.by_incident[0]
    assert first["id"] == "INC-0416"
    assert first["findings"] == 2          # the -06:00 event merged in
    assert rep.by_incident[1]["id"] == "INC-0417"
    ok, _ = led.verify_chain()
    assert ok


def test_low_score_anomaly_does_not_open_incident(tmp_path):
    anom = tmp_path / "anom.jsonl"
    anom.write_text(json.dumps({
        "kind": "process", "key": "c:\\windows\\system32\\igfxtray.exe",
        "score": 0.7, "count": 1, "reasons": [], "host": "h1",
        "first_ts": "2016-08-10T21:00:00+00:00", "last_ts": "",
        "exemplar_raw": "",
    }) + "\n")
    led = AuditLedger(tmp_path / "l.jsonl")
    rep = build_incidents(tmp_path / "no-det.jsonl", anom,
                          tmp_path / "inc.jsonl", led)
    assert rep.incidents == 0


def test_to_utc_normalizes_offsets():
    assert _to_utc("2016-08-24T10:48:41-06:00") == "2016-08-24T16:48:41+00:00"


def test_missing_ledger_is_not_reported_as_intact(tmp_path):
    """A ledger file that does not exist is absent, not verified.

    Regression guard for a real deploy bug: a fresh Render service with no
    data directory returned {"intact": true, "chain intact: 0 entries"} from
    /api/ledger/verify -- a green integrity claim on the one endpoint whose
    entire job is proving integrity, for a chain that did not exist.
    """
    from citinel.audit.ledger import AuditLedger
    led = AuditLedger(tmp_path / "subdir" / "absent.jsonl")
    (tmp_path / "subdir" / "absent.jsonl").unlink(missing_ok=True)
    ok, msg = led.verify_chain()
    assert ok is False
    assert "nothing to verify" in msg


def test_empty_but_present_ledger_is_genuinely_intact(tmp_path):
    """The other half of the distinction: an empty ledger that EXISTS has
    nothing written and nothing tampered, so it is trivially intact."""
    from citinel.audit.ledger import AuditLedger
    path = tmp_path / "empty.jsonl"
    AuditLedger(path)          # constructor creates the parent dir only
    path.touch()               # now the file genuinely exists, zero entries
    ok, msg = AuditLedger(path).verify_chain()
    assert ok is True
    assert "0 entries" in msg
