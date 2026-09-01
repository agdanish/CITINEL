"""Tests for the worker's polling idempotency.

Pins the bug the audit's fix addresses: build_incidents() rewrites output and
APPENDS fresh ledger entries on every call, which is correct for a one-shot
rebuild but corrupts an unbounded audit trail under polling. The worker must
skip a cycle whose inputs have not changed.
"""

from __future__ import annotations

import json

import pytest

from citinel.worker import run as worker


@pytest.fixture(autouse=True)
def _no_lyzr_key(monkeypatch):
    # worker.run_once() now wires AuditLedger(sink=LyzrLedgerMirror()) for
    # real (the audit's dormant-code fix) -- a real key lives in .env for the
    # live deploy, so every test in this file would otherwise make a live
    # network call it isn't testing for. Autoused so no test here needs to
    # remember this individually.
    from citinel.config import settings
    monkeypatch.setattr(settings, "lyzr_api_key", None)


def _write_one_detection(path, title="rule"):
    path.write_text(json.dumps({
        "rule_id": "r", "rule_title": title, "level": "high", "techniques": [],
        "timestamp": "2016-08-24T10:00:00+00:00", "host": "h",
        "evidence": {"raw": "x", "native_fields": {}},
    }) + "\n")


def _count(path):
    from citinel.audit.ledger import AuditLedger
    return sum(1 for _ in AuditLedger(path).entries())


def test_repeated_cycles_with_unchanged_inputs_do_not_duplicate_ledger_entries(
    tmp_path, monkeypatch
):
    det = tmp_path / "det.jsonl"
    anom = tmp_path / "anom.jsonl"
    _write_one_detection(det)
    incidents_dir = tmp_path / "incidents"

    monkeypatch.setattr(worker, "DETECTIONS_PATH", det)
    monkeypatch.setattr(worker, "ANOMALIES_PATH", anom)
    monkeypatch.setattr(worker, "INCIDENTS_DIR", incidents_dir)
    monkeypatch.setattr(worker, "_last_built_signature", None)

    worker.run_once()
    first_count = _count(incidents_dir / "ledger.jsonl")
    assert first_count > 0

    worker.run_once()
    worker.run_once()
    second_count = _count(incidents_dir / "ledger.jsonl")
    assert second_count == first_count, "unchanged inputs must not grow the ledger"


def test_a_real_change_triggers_a_rebuild(tmp_path, monkeypatch):
    det = tmp_path / "det.jsonl"
    anom = tmp_path / "anom.jsonl"
    _write_one_detection(det)
    incidents_dir = tmp_path / "incidents"

    monkeypatch.setattr(worker, "DETECTIONS_PATH", det)
    monkeypatch.setattr(worker, "ANOMALIES_PATH", anom)
    monkeypatch.setattr(worker, "INCIDENTS_DIR", incidents_dir)
    monkeypatch.setattr(worker, "_last_built_signature", None)

    worker.run_once()
    first_count = _count(incidents_dir / "ledger.jsonl")

    import time
    time.sleep(0.05)
    _write_one_detection(det, title="a genuinely different rule")  # new mtime
    worker.run_once()
    second_count = _count(incidents_dir / "ledger.jsonl")
    assert second_count > first_count, "a real input change must trigger a rebuild"


def test_run_once_wires_the_ledger_to_a_real_lyzr_sink(tmp_path, monkeypatch):
    """Regression guard for the dormant-wiring fix: AuditLedger used to be
    constructed with no sink anywhere in production, so LyzrLedgerMirror.record
    never actually ran even once a key was configured -- only compare() worked,
    meaning the witness could ask "what's your head?" and get nothing back
    because it was never told anything. run_once() must pass a real sink."""
    det = tmp_path / "det.jsonl"
    anom = tmp_path / "anom.jsonl"
    _write_one_detection(det)
    incidents_dir = tmp_path / "incidents"

    monkeypatch.setattr(worker, "DETECTIONS_PATH", det)
    monkeypatch.setattr(worker, "ANOMALIES_PATH", anom)
    monkeypatch.setattr(worker, "INCIDENTS_DIR", incidents_dir)
    monkeypatch.setattr(worker, "_last_built_signature", None)

    recorded = []

    class _SpySink:
        def record(self, entry):
            recorded.append(entry.kind)

    monkeypatch.setattr(worker, "LyzrLedgerMirror", _SpySink)

    worker.run_once()

    assert recorded, "AuditLedger was constructed with no sink -- record() never ran"
    assert "incident_opened" in recorded or "detection_added" in recorded or len(recorded) > 0


def test_no_input_files_is_a_clean_noop(tmp_path, monkeypatch):
    monkeypatch.setattr(worker, "DETECTIONS_PATH", tmp_path / "missing_det.jsonl")
    monkeypatch.setattr(worker, "ANOMALIES_PATH", tmp_path / "missing_anom.jsonl")
    monkeypatch.setattr(worker, "INCIDENTS_DIR", tmp_path / "incidents")
    worker.run_once()  # must not raise
    assert not (tmp_path / "incidents").exists()
