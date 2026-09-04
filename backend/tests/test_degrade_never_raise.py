"""Four ways an external answer used to become a 500.

Every connector in this codebase documents the same contract: it degrades,
returning a status a caller can read, and it never raises into the incident
path. Each test below names a place where that contract was documented but not
actually held, and the route the exception surfaced on.

Two of them are the same defect twice, and that is the point: urlparse RAISES
on a malformed authority rather than returning an empty result, so a guard
written as `if not parsed.hostname` looks total and is not. n8n_api already
carried the fix; lyzr and the n8n webhook did not.
"""

from __future__ import annotations

import json
from types import SimpleNamespace as NS

import pytest

from citinel.config import settings
from citinel.connectors.base import EnrichmentCache
from citinel.connectors.enrichment import TavilyConnector
from citinel.connectors.lyzr import LyzrLedgerMirror, _lyzr_allow
from citinel.connectors.n8n import dispatch_signed


@pytest.fixture
def cache(tmp_path):
    return EnrichmentCache(tmp_path / "enrich")


def _tavily(cache, body, status=200):
    def send(method, url, headers, params, json_body):
        return status, body
    return TavilyConnector(cache, send)


def _witness(reply):
    return lambda url, headers, payload: (200, {"response": json.dumps(reply)})


LEDGER = NS(head="deadbeef", entries=lambda: iter([1, 2, 3]))


# -- 1. a model's count field, on GET /api/ledger/verify ----------------------

@pytest.mark.parametrize("count", ["unknown", "12.5", "1,024", ["3"], {"n": 3}, None])
def test_a_witness_count_that_is_not_a_number_does_not_500_ledger_verify(
        count, monkeypatch):
    """int() raised ValueError on the strings and TypeError on the containers.

    compare() is called from GET /api/ledger/verify, which has no handler, so a
    third-party model's malformed field took down the DETERMINISTIC chain
    verification computed one line earlier -- the audit surface failing because
    a witness stuttered.
    """
    monkeypatch.setattr(settings, "lyzr_api_key", "k")
    monkeypatch.setattr(settings, "lyzr_guard_url",
                        "https://agent-prod.studio.lyzr.ai/v3/inference/chat/")
    m = LyzrLedgerMirror(sender=_witness({"head": "deadbeef", "count": count}))
    r = m.compare(LEDGER)
    assert r.status == "agreed"          # the head matched; only count was junk
    assert r.remote_count == 0           # degraded to the same default a missing count gets


# -- 2. Tavily answering with a shape it really does produce ------------------

@pytest.mark.parametrize("body", [[], None, "a string", 3])
def test_a_non_object_tavily_body_does_not_escape_into_the_incident_path(
        body, cache, monkeypatch):
    """body.get("answer") on a list raised AttributeError.

    enricher._execute catches only (KeyError, TypeError) despite promising never
    to raise, so this escaped to POST /api/incidents/{id}/context as a 500 and
    abandoned every remaining query in the plan.
    """
    monkeypatch.setattr(settings, "tavily_api_key", "k")
    r = _tavily(cache, body).search("P01s0n1vy")
    assert r.status == "ok" and r.detail["results"] == []


def test_tavily_results_of_bare_strings_do_not_raise(cache, monkeypatch):
    """The more reachable half: Tavily's own /map endpoint returns bare URLs,
    so a scalar row is a shape this API genuinely produces. top.get() on a str
    raised the same AttributeError from the same line."""
    monkeypatch.setattr(settings, "tavily_api_key", "k")
    r = _tavily(cache, {"results": ["https://a", "https://b"]}).search("q")
    assert r.status == "ok"
    assert r.source_url == "https://tavily.com"     # no row was usable
    assert r.detail["results"] == []


# -- 3 and 4. urlparse raising rather than returning empty --------------------

def test_a_malformed_lyzr_guard_url_degrades_instead_of_raising(monkeypatch):
    """A typo in CITINEL_LYZR_GUARD_URL 500ed /api/ledger/verify and sign-off."""
    monkeypatch.setattr(settings, "lyzr_guard_url", "https://[abc")
    allow = _lyzr_allow()                    # used to raise ValueError here
    assert "[abc" not in " ".join(allow)     # the bad host is simply not allowed

    monkeypatch.setattr(settings, "lyzr_api_key", "k")
    r = LyzrLedgerMirror(sender=_witness({"head": "x", "count": 1})).compare(LEDGER)
    assert r.status == "unavailable"


def test_a_malformed_n8n_webhook_url_does_not_block_a_human_signoff(monkeypatch):
    """n8n improves the workflow and must never be able to stop a human from
    signing off on an incident. A mistyped URL made every sign-off a 500."""
    monkeypatch.setattr(settings, "n8n_webhook_url", "https://[abc")
    d = dispatch_signed(NS(incident_id="INC-1"), "ciso@bank")
    assert d.status == "error"
    assert "unparseable" in d.detail


# -- 5. Tavily extract(): the same scalar-row hazard, one method over ---------

def test_extract_with_a_dict_where_failed_results_should_be_a_list(cache, monkeypatch):
    """`(body.get("failed_results") or [{}])[0]` assumed a list. A dict there
    raises KeyError: 0; a string silently yields one character and then raises
    AttributeError on .get(). Both escaped a method whose only documented
    outcomes are ok and error."""
    monkeypatch.setattr(settings, "tavily_api_key", "k")
    r = _tavily(cache, {"results": [], "failed_results": {"error": "malformed"}}).extract("https://x")
    assert r.status == "error" and "unknown" in r.verdict


def test_extract_with_bare_string_rows_does_not_raise(cache, monkeypatch):
    monkeypatch.setattr(settings, "tavily_api_key", "k")
    r = _tavily(cache, {"results": ["https://a"]}).extract("https://x")
    assert r.status == "error"          # no usable row, reported rather than raised


# -- 6. the route whose job is to record that the automation broke ------------

def test_n8n_error_report_survives_a_payload_it_does_not_control(sandbox):
    """`or {}` is not a guard: a scalar is truthy, so a string under "execution"
    was assigned straight through and .get() on it raised AttributeError. A 500
    from the one route that exists to record an automation failure is the worst
    possible moment to fail."""
    from fastapi.testclient import TestClient
    import citinel.web.app as app_mod
    from tests.conftest import WRITE_HEADERS

    r = TestClient(app_mod.app).post(
        "/api/n8n/error",
        json={"execution": "not_a_dict", "workflow": ["also", "not"],
              "incident_id": ""},
        headers=WRITE_HEADERS)
    assert r.status_code == 200
    assert r.json()["frame"]["workflow"] == "unknown"


# -- 7. an instruction that miscounts the blocks in front of the model --------

INC = NS(incident_id="INC-T1", findings=[NS(title=f"f{i}") for i in range(12)])


def test_correlator_is_told_the_true_block_count_when_enrichment_is_appended():
    """The caller appends the Enrichment Squad's block AFTER the instruction is
    built, so the model saw n+1 blocks while being told n. verify_citations
    bounds finding_index against the incident's WHOLE findings list, so on a
    large incident a model citing the appended block lands in range and is
    checked against a finding it was never shown -- the claim is then dropped
    for a stated reason that is false."""
    from citinel.agents.pipeline import _correlator_instruction, _narrator_instruction

    plain = _correlator_instruction(INC, enriched=False)
    assert "Below are 12 fenced" in plain and "Enrichment Squad" not in plain

    enriched = _correlator_instruction(INC, enriched=True)
    assert "Below are 13 fenced" in enriched
    assert "Block 12 is not one of those" in enriched
    assert "cite only 0..11" in enriched


def test_narrator_is_told_the_true_block_count_when_a_correlation_exists():
    from citinel.agents.pipeline import _narrator_instruction

    none = _narrator_instruction(INC, None)
    assert "Below are 12 fenced" in none and "correlator-summary" not in none

    with_corr = _narrator_instruction(INC, NS(summary="a chain"))
    assert "Below are 13 fenced" in with_corr
    assert "never cite it" in with_corr
