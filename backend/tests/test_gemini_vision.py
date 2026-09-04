"""Gemini vision: the only place a model in CITINEL looks at something that
is not text, and the corroboration that keeps it honest.

The reading is an observation. The cross-reference is a fact. The tests that
matter here are the ones that stop the second from quietly becoming as soft
as the first.
"""

from __future__ import annotations

import json

from citinel.agents.visual import corroborate, load_visuals, read_image
from citinel.config import settings
from citinel.connectors.base import EnrichmentCache
from citinel.connectors.gemini import GeminiConnector

READING = {
    "kind": "phishing email",
    "summary": "A credential-harvesting email impersonating IT support.",
    "indicators": [
        {"value": "10.4.7.112", "type": "ip"},
        {"value": "evil-not-in-this-record.example", "type": "domain"},
    ],
    "looks_malicious": True,
    "why": "asks the recipient to verify an account via an unexpected link",
}


def _sender(reply):
    def send(method, url, headers, params, json_body):
        return 200, {"candidates": [{"content": {"parts": [{"text": json.dumps(reply)}]}}]}
    return send


def _inc(sandbox):
    from citinel.incidents.builder import load_incidents
    return load_incidents(sandbox / "incidents.jsonl")[0]


def test_corroboration_searches_the_whole_finding_not_a_guessed_field(sandbox):
    """The bug this locks: the first version searched a field called `raw`,
    but the log line lives in `evidence_raw`. An indicator present in dozens
    of findings was reported as "never seen in this record" -- not a blank
    space, a false statement about the record."""
    inc = _inc(sandbox)
    # this string is in the fixture's evidence_raw, nowhere else
    out = corroborate(inc, [{"value": "10.4.7.112", "type": "ip"}])
    assert out["corroborated"], "an indicator in evidence_raw must be found"
    assert out["corroborated"][0]["finding_count"] >= 1
    assert out["corroborated"][0]["finding_indices"]


def test_an_indicator_the_record_has_never_seen_is_reported_as_unseen(sandbox):
    out = corroborate(_inc(sandbox), [{"value": "nothing-like-this.example", "type": "domain"}])
    assert out["corroborated"] == []
    assert out["unseen"][0]["value"] == "nothing-like-this.example"


def test_indicators_too_short_to_mean_anything_are_dropped(sandbox):
    """A two-character "indicator" matches most raw log text and would
    manufacture corroboration out of noise."""
    out = corroborate(_inc(sandbox), [{"value": "ab", "type": "other"}])
    assert out["corroborated"] == [] and out["unseen"] == []


def test_a_reading_is_stored_with_its_corroboration_and_its_disclaimer(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "AIza-test")
    inc = _inc(sandbox)
    gem = GeminiConnector(EnrichmentCache(sandbox / "cache"), sender=_sender(READING))

    out = read_image(inc, "Zm9v", "image/png", "forwarded by ops",
                     sandbox / "cache", sandbox, connector=gem)
    e = out["readings"][0]
    assert e["status"] == "ok" and e["kind"] == "phishing email"
    assert e["looks_malicious"] is True
    assert e["analyst_note"] == "forwarded by ops"
    assert "never evidence" in e["not_evidence"]
    # both halves present: what the record knows, and what it does not
    assert any(c["value"] == "10.4.7.112" for c in e["corroborated"])
    assert any(u["value"].startswith("evil-not-in") for u in e["unseen"])
    assert load_visuals(sandbox, inc.incident_id)["readings"][0]["kind"] == "phishing email"


def test_readings_accumulate_newest_first(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "AIza-test")
    inc = _inc(sandbox)
    for kind in ("first", "second"):
        gem = GeminiConnector(EnrichmentCache(sandbox / "cache"),
                              sender=_sender(dict(READING, kind=kind)))
        out = read_image(inc, "Zm9v", "image/png", "", sandbox / "cache", sandbox, connector=gem)
    assert [r["kind"] for r in out["readings"]] == ["second", "first"]


def test_an_unsupported_image_type_is_refused_before_the_call(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "AIza-test")
    calls = []

    def spy(method, url, headers, params, json_body):
        calls.append(url)
        return 200, {}

    gem = GeminiConnector(EnrichmentCache(sandbox / "cache"), sender=spy)
    out = read_image(_inc(sandbox), "Zm9v", "application/pdf", "",
                     sandbox / "cache", sandbox, connector=gem)
    assert out["readings"][0]["status"] == "error"
    assert calls == []                      # nothing was sent, nothing was spent


def test_no_key_reads_nothing_and_corroborates_nothing(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", None)
    out = read_image(_inc(sandbox), "Zm9v", "image/png", "", sandbox / "cache", sandbox)
    e = out["readings"][0]
    assert e["status"] == "not_configured"
    assert e["corroborated"] == [] and e["unseen"] == []


def test_an_unparseable_reading_does_not_invent_corroboration(sandbox, monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "AIza-test")

    def prose(method, url, headers, params, json_body):
        return 200, {"candidates": [{"content": {"parts": [{"text": "Sure! Here's what I see:"}]}}]}

    gem = GeminiConnector(EnrichmentCache(sandbox / "cache"), sender=prose)
    out = read_image(_inc(sandbox), "Zm9v", "image/png", "", sandbox / "cache", sandbox, connector=gem)
    assert out["readings"][0]["status"] == "error"
    assert out["readings"][0]["corroborated"] == []
