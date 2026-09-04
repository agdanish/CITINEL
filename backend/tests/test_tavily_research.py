"""Tavily Research: the fifth primitive, and the only one that answers a question.

Async by design, so the properties worth locking are that a pending run does
not block, that a completed one persists, and that a brief can never become
evidence.
"""

from __future__ import annotations

from citinel.agents.brief import compose_question, load_brief, poll_brief, start_brief
from citinel.config import settings
from citinel.connectors.base import EnrichmentCache
from citinel.connectors.enrichment import TavilyConnector


def _tav(sandbox, sender):
    return TavilyConnector(EnrichmentCache(sandbox / "cache"), sender=sender)


def _inc(sandbox):
    from citinel.incidents.builder import load_incidents
    return load_incidents(sandbox / "incidents.jsonl")[0]


def test_the_question_is_built_from_what_the_investigation_found(sandbox):
    inc = _inc(sandbox)
    q = compose_question(inc, {"correlation": {"stages": [
        {"technique_id": "T1078"}, {"technique_id": "T1021.002"}]}})
    assert "T1078" in q and "T1021.002" in q
    assert "Cite your sources" in q
    # a brief about an incident id would be worthless
    assert inc.incident_id not in q


def test_a_started_brief_persists_pending_and_does_not_block(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "tavily_api_key", "tvly-test")
    calls = []

    def sender(method, url, headers, params, json_body):
        calls.append((method, url))
        return 201, {"request_id": "req-123", "status": "pending"}

    out = start_brief(_inc(sandbox), None, sandbox / "cache", sandbox,
                      connector=_tav(sandbox, sender))
    assert out["status"] == "pending" and out["request_id"] == "req-123"
    assert out["content"] == "" and "never evidence" in out["not_evidence"]
    assert len(calls) == 1                     # started, not waited on
    assert load_brief(sandbox, _inc(sandbox).incident_id)["request_id"] == "req-123"


def test_polling_a_pending_run_stays_pending_without_losing_the_request(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "tavily_api_key", "tvly-test")
    start_brief(_inc(sandbox), None, sandbox / "cache", sandbox,
                connector=_tav(sandbox, lambda *a: (201, {"request_id": "r1", "status": "pending"})))
    out = poll_brief(_inc(sandbox).incident_id, sandbox / "cache", sandbox,
                     connector=_tav(sandbox, lambda *a: (202, {})))
    assert out["status"] == "pending" and out["request_id"] == "r1"


def test_a_completed_run_persists_its_report_and_its_sources(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "tavily_api_key", "tvly-test")
    inc = _inc(sandbox)
    start_brief(inc, None, sandbox / "cache", sandbox,
                connector=_tav(sandbox, lambda *a: (201, {"request_id": "r1"})))

    def done(method, url, headers, params, json_body):
        return 200, {"status": "completed",
                     "content": "Ransomware pattern; isolate first. [1]",
                     "sources": [{"title": "CISA advisory", "url": "https://cisa.gov/x"}],
                     "response_time": 41.2}

    out = poll_brief(inc.incident_id, sandbox / "cache", sandbox, connector=_tav(sandbox, done))
    assert out["status"] == "completed"
    assert "isolate first" in out["content"]
    assert out["sources"][0]["url"] == "https://cisa.gov/x"
    # and it survives on disk for the console to read without re-spending
    assert load_brief(sandbox, inc.incident_id)["status"] == "completed"


def test_no_key_means_no_brief_and_nothing_invented(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "tavily_api_key", None)
    out = start_brief(_inc(sandbox), None, sandbox / "cache", sandbox)
    assert out["status"] == "error" and out["content"] == "" and out["sources"] == []


def test_polling_before_anything_was_started_returns_nothing(sandbox):
    assert poll_brief("INC-NOPE", sandbox / "cache", sandbox) is None
