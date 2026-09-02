"""Shared fixtures for the web-API test suite."""

from __future__ import annotations

import json

import pytest

import citinel.web.app as app_mod
from citinel.audit.ledger import AuditLedger
from citinel.config import settings
from citinel.policy.actions import MockEndpoints

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
