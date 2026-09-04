"""Shared fixtures for the web-API test suite."""

from __future__ import annotations

import json

import pytest

import citinel.web.app as app_mod
from citinel.audit.ledger import AuditLedger
from citinel.config import settings
from citinel.policy.actions import MockEndpoints

RAW = "EventCode=4624 Account=opr_kiosk LogonType=3 SourceIP=10.4.7.112 Workstation=BR-KIOSK-07"

#: The sandbox authenticates every write for the duration of the test that
#: asked for it (via client.headers, reverted after) -- tests exercise the
#: real authenticated path, not a bypass of the guard added for the
#: unauthenticated-ledger-forgery finding. A handful of dedicated tests in
#: test_write_guard.py use a bare TestClient with no header at all to prove
#: the guard itself: no token configured -> 503, wrong token -> 401.
TEST_WRITE_TOKEN = "test-write-token-not-a-real-secret"
WRITE_HEADERS = {"X-Citinel-Write-Token": TEST_WRITE_TOKEN}


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
    # "every external connector pinned off" was not true of all of them: the
    # n8n REST plane, Gemini and Startuped were still reading whatever the
    # developer's own .env held, so sandboxed route tests made live outbound
    # calls -- the resume-route test really did POST to the open internet, and
    # a background swarm run really did report to a marketing platform.
    for key in ("lyzr_api_key", "lyzr_guard_url", "lyzr_agent_id", "n8n_webhook_url",
                "n8n_api_url", "n8n_api_key", "gemini_api_key", "startuped_api_key",
                "swytchcode_api_key", "tavily_api_key", "virustotal_api_key", "abuseipdb_api_key"):
        monkeypatch.setattr(settings, key, None)
    monkeypatch.setattr(settings, "simulated_endpoints_only", True)
    monkeypatch.setattr(settings, "write_token", TEST_WRITE_TOKEN)
    return tmp_path
