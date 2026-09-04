"""The Gemini wide-lens sweep: the findings nobody read.

The property under test is the honest one. A sweep must never invent a
region it did not read, never become evidence, and never appear at all when
no key is configured -- the same contract Tavily's context and Lyzr's
opinions hold to.
"""

from __future__ import annotations

import json

from citinel.agents.sweep import load_sweep, run_sweep
from citinel.config import settings
from citinel.connectors.base import EnrichmentCache
from citinel.connectors.gemini import GeminiConnector
from tests.conftest import WRITE_HEADERS
from citinel.web.app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _gemini_sender(reply: dict, status: int = 200):
    """A fake Google endpoint answering in the real wire shape."""
    calls = []

    def send(method, url, headers, params, json_body):
        calls.append({"method": method, "url": url, "headers": headers, "body": json_body})
        return status, {"candidates": [{"content": {"parts": [{"text": json.dumps(reply)}]}}]}

    send.calls = calls
    return send


SWEEP = {
    "summary": "The unexamined region is dominated by one host absent from the window.",
    "clusters": [{"pattern": "repeated service logon", "count": 900,
                  "hosts": ["HOST-C"], "where": "outside", "why": "never seen inside"}],
    "only_outside_window": [{"what": "HOST-C", "count": 900, "why": "absent from findings 0-40"}],
    "blind_spot_risk": "high",
    "blind_spot_reason": "a whole host appears only past the window",
}


def test_sweep_reads_past_the_window_and_persists_what_it_found(sandbox, monkeypatch):
    from citinel.incidents.builder import load_incidents
    monkeypatch.setattr(settings, "gemini_api_key", "AIza-test")
    inc = load_incidents(sandbox / "incidents.jsonl")[0]
    sender = _gemini_sender(SWEEP)
    gem = GeminiConnector(EnrichmentCache(sandbox / "cache"), sender=sender)

    out = run_sweep(inc, examined=1, cache_dir=sandbox / "cache",
                    incidents_dir=sandbox, ledger=None, connector=gem)

    assert out["status"] == "ok"
    assert out["blind_spot_risk"] == "high"
    assert out["clusters"][0]["where"] == "outside"
    assert out["only_outside_window"][0]["what"] == "HOST-C"
    # the honesty stamp travels with the data, not just the docs
    assert "never evidence" in out["not_evidence"]
    # and it is on disk for the console to read without re-spending a call
    assert load_sweep(sandbox, inc.incident_id)["summary"] == out["summary"]


def test_the_key_goes_in_a_header_never_in_the_url(sandbox, monkeypatch):
    """An API key in a query string leaks into logs, proxies and referrers."""
    from citinel.incidents.builder import load_incidents
    monkeypatch.setattr(settings, "gemini_api_key", "AIza-secret")
    inc = load_incidents(sandbox / "incidents.jsonl")[0]
    sender = _gemini_sender(SWEEP)
    GeminiConnector(EnrichmentCache(sandbox / "cache"), sender=sender).wide_sweep(inc, examined=1)

    call = sender.calls[0]
    assert "AIza-secret" not in call["url"]
    assert call["headers"]["x-goog-api-key"] == "AIza-secret"


def test_no_key_means_no_sweep_and_nothing_invented(sandbox, monkeypatch):
    from citinel.incidents.builder import load_incidents
    monkeypatch.setattr(settings, "gemini_api_key", None)
    inc = load_incidents(sandbox / "incidents.jsonl")[0]
    out = run_sweep(inc, examined=1, cache_dir=sandbox / "cache", incidents_dir=sandbox)

    assert out["status"] == "not_configured"
    assert out["summary"] == "" and out["clusters"] == [] and out["only_outside_window"] == []


def test_an_unusable_reply_degrades_rather_than_being_guessed_at(sandbox, monkeypatch):
    from citinel.incidents.builder import load_incidents
    monkeypatch.setattr(settings, "gemini_api_key", "AIza-test")
    inc = load_incidents(sandbox / "incidents.jsonl")[0]

    def prose(method, url, headers, params, json_body):
        return 200, {"candidates": [{"content": {"parts": [{"text": "Sure! Here's a summary:"}]}}]}

    gem = GeminiConnector(EnrichmentCache(sandbox / "cache"), sender=prose)
    out = run_sweep(inc, examined=1, cache_dir=sandbox / "cache",
                    incidents_dir=sandbox, connector=gem)
    assert out["status"] == "error" and out["clusters"] == []


def test_sweeping_a_fully_examined_incident_is_refused_as_pointless(sandbox, monkeypatch):
    from citinel.incidents.builder import load_incidents
    monkeypatch.setattr(settings, "gemini_api_key", "AIza-test")
    inc = load_incidents(sandbox / "incidents.jsonl")[0]
    sender = _gemini_sender(SWEEP)
    gem = GeminiConnector(EnrichmentCache(sandbox / "cache"), sender=sender)

    out = run_sweep(inc, examined=len(inc.findings), cache_dir=sandbox / "cache",
                    incidents_dir=sandbox, connector=gem)
    assert out["status"] == "not_needed"
    assert sender.calls == []          # no call, no spend


def test_routes_gate_on_confirm_and_on_a_key(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", None)
    assert client.get("/api/incidents/INC-T1/sweep").status_code == 404
    r = client.post("/api/incidents/INC-T1/sweep", json={"confirm": True}, headers=WRITE_HEADERS)
    assert r.status_code == 503

    monkeypatch.setattr(settings, "gemini_api_key", "AIza-test")
    r = client.post("/api/incidents/INC-T1/sweep", json={}, headers=WRITE_HEADERS)
    assert r.status_code == 400 and "confirm" in r.text


def test_the_ledger_path_setting_moves_write_and_read_together(tmp_path, monkeypatch):
    """A ledger appended in one file and verified from another would report a
    clean chain while the real frames went elsewhere. One resolver, both ends."""
    from citinel.web import app as app_mod

    disk = tmp_path / "disk" / "ledger.jsonl"
    disk.parent.mkdir(parents=True)
    monkeypatch.setattr(settings, "ledger_path", disk)

    assert app_mod._ledger_path() == disk
    led = app_mod._ledger()
    led.append("INC-T1", "test", "note", {"detail": "written to the disk path"})

    # the frame is on the disk path, not beside the corpus
    assert disk.exists()
    assert not (app_mod.INCIDENTS_DIR / "ledger.jsonl").samefile(disk) if (app_mod.INCIDENTS_DIR / "ledger.jsonl").exists() else True
    # and the read side finds it through the same resolver
    from citinel.audit.ledger import AuditLedger
    assert len(AuditLedger(app_mod._ledger_path()).entries_for("INC-T1")) == 1


def test_unset_ledger_path_keeps_the_default_beside_the_corpus(monkeypatch):
    from citinel.web import app as app_mod
    monkeypatch.setattr(settings, "ledger_path", None)
    assert app_mod._ledger_path() == app_mod.INCIDENTS_DIR / "ledger.jsonl"


def test_a_sweep_records_a_frame_the_ledger_actually_accepts(sandbox, monkeypatch):
    """The kind must be a real ENTRY_KIND. 'observation' looked reasonable and
    would have raised LedgerError on the first live sweep."""
    from citinel.audit.ledger import AuditLedger
    from citinel.incidents.builder import load_incidents
    monkeypatch.setattr(settings, "gemini_api_key", "AIza-test")
    inc = load_incidents(sandbox / "incidents.jsonl")[0]
    ledger = AuditLedger(sandbox / "sweep-ledger.jsonl")
    gem = GeminiConnector(EnrichmentCache(sandbox / "cache"), sender=_gemini_sender(SWEEP))

    run_sweep(inc, examined=1, cache_dir=sandbox / "cache", incidents_dir=sandbox,
              ledger=ledger, connector=gem)

    frames = [e for e in ledger.entries_for(inc.incident_id) if e.actor == "gemini-sweep"]
    assert len(frames) == 1
    assert frames[0].kind == "tool_call"
    assert frames[0].payload["check"] == "wide_lens_sweep"
    assert "never evidence" in frames[0].payload["reason"]


def test_artifacts_dir_moves_what_a_run_produces_but_never_the_corpus(tmp_path, monkeypatch):
    """The container filesystem is ephemeral, so anything a run PRODUCES has to
    be redirectable to a disk. The corpus itself ships in the image and must
    not follow it -- pointing reads of incidents.jsonl at an empty disk would
    leave the service with no data at all."""
    from citinel.web import app as app_mod

    disk = tmp_path / "artifacts"
    monkeypatch.setattr(settings, "artifacts_dir", disk)

    assert app_mod._artifacts_dir() == disk
    # the corpus stays where the image put it
    assert app_mod.INCIDENTS_DIR != disk
    assert (app_mod.INCIDENTS_DIR / "incidents.jsonl").exists()

    # and a sweep written now lands on the disk, not beside the corpus
    from citinel.agents.sweep import sweep_path
    p = sweep_path(app_mod._artifacts_dir(), "INC-T1")
    assert disk in p.parents
    assert app_mod.INCIDENTS_DIR not in p.parents


def test_unset_artifacts_dir_keeps_everything_beside_the_corpus(monkeypatch):
    from citinel.web import app as app_mod
    monkeypatch.setattr(settings, "artifacts_dir", None)
    assert app_mod._artifacts_dir() == app_mod.INCIDENTS_DIR
