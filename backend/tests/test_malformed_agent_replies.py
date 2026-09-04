"""A model told to answer with a list can answer with anything.

Every one of these shapes reached a live route and raised before the guards
went in -- the slice runs before the per-item isinstance check, so the
"degrade, never raise" contract these connectors document was not actually
held. Each test names the route the exception surfaced on.
"""

from __future__ import annotations

import json
from types import SimpleNamespace as NS

import pytest

from citinel.config import settings
from citinel.connectors import lyzr_agents as la
from citinel.connectors.lyzr import LyzrGuard


def _sender(reply):
    return lambda url, headers, body: (200, {"response": json.dumps(reply)})


@pytest.fixture
def lyzr_on(monkeypatch):
    monkeypatch.setattr(settings, "lyzr_api_key", "k")
    monkeypatch.setattr(settings, "lyzr_guard_url",
                        "https://agent-prod.studio.lyzr.ai/v3/inference/chat/")
    for f in ("lyzr_agent_id", "lyzr_handover_agent_id", "lyzr_corpus_agent_id",
              "lyzr_verdict_agent_id", "lyzr_review_agent_id"):
        monkeypatch.setattr(settings, f, "id")


DRAFT = NS(kind="certin", incident_id="T",
           fields=[NS(key="k", label="L", fill="auto", value="v")])


def test_pii_as_a_list_of_strings_does_not_500_the_draft_route(lyzr_on):
    """GET /api/incidents/{id}/draft -- AttributeError on item.get()."""
    r = LyzrGuard(sender=_sender({"pii": ["email", "phone"]})).screen(DRAFT)
    assert r.findings == [] and r.clean is True


def test_pii_as_a_bare_object_does_not_raise(lyzr_on):
    r = LyzrGuard(sender=_sender({"pii": {"type": "email"}})).screen(DRAFT)
    assert r.clean is True


def test_open_items_as_an_object_does_not_500_the_handover_route(lyzr_on):
    """POST /api/incidents/{id}/handover -- TypeError: unhashable type 'slice'."""
    out = la.handover_summary({"incident_id": "T"}, [], None,
                              agent=la.LyzrAgent("handover_summary", "id", "s",
                                                 _sender({"summary": "s", "open_items": {"a": 1}})))
    assert out["status"] == "ok" and out["open_items"] == []


def test_gaps_as_an_int_does_not_500_the_corpus_review_route(lyzr_on):
    """POST /api/corpus/review -- TypeError: 'int' object is not subscriptable."""
    out = la.corpus_advisory({"rules_total": 1},
                             agent=la.LyzrAgent("corpus_advisory", "id", "s",
                                                _sender({"summary": "s", "gaps": 7})))
    assert out["status"] == "ok" and out["gaps"] == []


def test_claims_as_an_int_does_not_fail_a_paid_swarm_run(lyzr_on):
    """The worst one: verdict_audit runs AFTER save_result, so the exception
    was swallowed into run['error'] and a complete, paid swarm run was
    reported to the console as a failure."""
    out = la.verdict_audit("T", [], None,
                           agent=la.LyzrAgent("verdict_audit", "id", "s",
                                              _sender({"claims": 3})))
    assert out["status"] == "ok" and out["claims"] == []


def test_thin_as_a_string_does_not_500_the_draft_route(lyzr_on):
    out = la.review_draft(DRAFT,
                          agent=la.LyzrAgent("field_review", "id", "s",
                                             _sender({"thin": "none", "summary": "ok"})))
    assert out["status"] == "ok" and out["thin"] == []


def test_gemini_sweep_survives_a_scalar_where_a_list_was_asked_for(sandbox, monkeypatch):
    """POST /api/incidents/{id}/sweep -- same class of defect in my own code."""
    from citinel.agents.sweep import run_sweep
    from citinel.connectors.base import EnrichmentCache
    from citinel.connectors.gemini import GeminiConnector
    from citinel.incidents.builder import load_incidents

    monkeypatch.setattr(settings, "gemini_api_key", "AIza-test")
    inc = load_incidents(sandbox / "incidents.jsonl")[0]

    def scalar(method, url, headers, params, json_body):
        return 200, {"candidates": [{"content": {"parts": [{"text": json.dumps(
            {"summary": "s", "clusters": 5, "only_outside_window": "none",
             "blind_spot_risk": "low"})}]}}]}

    out = run_sweep(inc, examined=1, cache_dir=sandbox / "cache", incidents_dir=sandbox,
                    connector=GeminiConnector(EnrichmentCache(sandbox / "cache"), sender=scalar))
    assert out["status"] == "ok"
    assert out["clusters"] == [] and out["only_outside_window"] == []
