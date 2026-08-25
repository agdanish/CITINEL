"""Tests for the worker's polling idempotency.

Pins the bug the audit's fix addresses: build_incidents() rewrites output and
APPENDS fresh ledger entries on every call, which is correct for a one-shot
rebuild but corrupts an unbounded audit trail under polling. The worker must
skip a cycle whose inputs have not changed.
"""

from __future__ import annotations

import json

from citinel.worker import run as worker


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


def test_no_input_files_is_a_clean_noop(tmp_path, monkeypatch):
    monkeypatch.setattr(worker, "DETECTIONS_PATH", tmp_path / "missing_det.jsonl")
    monkeypatch.setattr(worker, "ANOMALIES_PATH", tmp_path / "missing_anom.jsonl")
    monkeypatch.setattr(worker, "INCIDENTS_DIR", tmp_path / "incidents")
    worker.run_once()  # must not raise
    assert not (tmp_path / "incidents").exists()
