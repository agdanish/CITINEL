"""Tests for the enrichment connector layer, no network, no keys.

Pins the properties that make enrichment safe and demo-proof: egress is
enforced live, cache-first means a repeat costs zero calls, missing keys
degrade gracefully instead of crashing, and every result carries citable
provenance.
"""

from __future__ import annotations

import pytest

from citinel.connectors.base import EgressRefused, EnrichmentCache
from citinel.connectors.enrichment import (
    AbuseIPDBConnector,
    EnrichmentSquad,
    TavilyConnector,
    VirusTotalConnector,
)


@pytest.fixture()
def cache(tmp_path):
    return EnrichmentCache(tmp_path / "enrich")


def _fake_sender(status, body, calls):
    def send(method, url, headers, params, json_body):
        calls.append({"method": method, "url": url, "headers": headers,
                      "params": params, "json": json_body})
        return status, body
    return send


def test_missing_key_degrades_gracefully(cache, monkeypatch):
    # no key configured -> not_configured, no exception, no call attempted.
    # Pinned explicitly: a real key now lives in .env for the live deploy, so
    # this can no longer rely on the key being absent by environment accident.
    from citinel.config import settings
    monkeypatch.setattr(settings, "virustotal_api_key", None)
    calls = []
    vt = VirusTotalConnector(cache, _fake_sender(200, {}, calls))
    r = vt.check_ip("185.151.160.15")
    assert r.status == "not_configured"
    assert calls == []


def test_egress_is_enforced_on_live_calls(cache, monkeypatch):
    from citinel.config import settings
    monkeypatch.setattr(settings, "virustotal_api_key", "test-key")
    # Point the connector at a non-allowlisted host and confirm it is refused
    calls = []
    vt = VirusTotalConnector(cache, _fake_sender(200, {}, calls))
    with pytest.raises(EgressRefused):
        vt._guarded_request("GET", "https://evil.example.com/x")
    assert calls == []      # the sender was never reached


def test_cache_first_means_a_repeat_costs_zero_calls(cache, monkeypatch):
    from citinel.config import settings
    monkeypatch.setattr(settings, "abuseipdb_api_key", "test-key")
    body = {"data": {"abuseConfidenceScore": 100, "totalReports": 42,
                     "isp": "EvilCorp", "countryCode": "XX"}}
    calls = []
    ab = AbuseIPDBConnector(cache, _fake_sender(200, body, calls))
    first = ab.check_ip("185.151.160.15")
    second = ab.check_ip("185.151.160.15")
    assert first.status == "ok" and first.score == 1.0
    assert not first.cached and second.cached
    assert len(calls) == 1          # the second answer came from disk
    assert cache.hits == 1 and cache.misses == 1


def test_virustotal_normalizes_score_and_cites_source(cache, monkeypatch):
    from citinel.config import settings
    monkeypatch.setattr(settings, "virustotal_api_key", "k")
    body = {"data": {"attributes": {"last_analysis_stats":
            {"malicious": 12, "harmless": 60, "undetected": 8}}}}
    vt = VirusTotalConnector(cache, _fake_sender(200, body, []))
    r = vt.check_hash("abc123")
    assert 0 < r.score < 1
    assert "12/80" in r.verdict
    assert r.source_url.startswith("https://www.virustotal.com/gui/hash/")


def test_tavily_surfaces_provenance_for_the_citation_chip(cache, monkeypatch):
    from citinel.config import settings
    monkeypatch.setattr(settings, "tavily_api_key", "k")
    body = {"answer": "P01s0n1vy is a known APT group",
            "results": [{"title": "APT profile", "url": "https://example.org/apt",
                         "score": 0.9}]}
    tv = TavilyConnector(cache, _fake_sender(200, body, []))
    r = tv.search("P01s0n1vy threat actor")
    assert r.status == "ok"
    assert r.source_url == "https://example.org/apt"    # citation chip target
    assert r.fetched_at                                 # timestamp for the chip
    assert "P01s0n1vy" in r.verdict


def test_squad_fans_one_ip_to_two_providers(cache, monkeypatch):
    from citinel.config import settings
    monkeypatch.setattr(settings, "virustotal_api_key", "k")
    monkeypatch.setattr(settings, "abuseipdb_api_key", "k")
    def sender(method, url, headers, params, json_body):
        if "virustotal" in url:
            return 200, {"data": {"attributes": {"last_analysis_stats":
                        {"malicious": 5, "harmless": 70}}}}
        return 200, {"data": {"abuseConfidenceScore": 88, "totalReports": 9}}
    squad = EnrichmentSquad(cache, sender)
    results = squad.enrich_ip("185.151.160.15")
    providers = {r.provider for r in results}
    assert providers == {"virustotal", "abuseipdb"}
    assert all(r.status == "ok" for r in results)
