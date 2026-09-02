"""Settings accept the conventional unprefixed variable names as fallbacks.

Confirmed need, 2 Sep 2026: a Render deployment whose operator had filled in
the environment still reported every connector "not configured". Names only
are tested here; no real key is ever read.
"""
import os

from citinel.config import Settings


def _clear(monkeypatch, suffix: str) -> None:
    for k in list(os.environ):
        if k.upper().endswith(suffix):
            monkeypatch.delenv(k, raising=False)


def test_unprefixed_name_is_accepted(monkeypatch):
    _clear(monkeypatch, "TAVILY_API_KEY")
    monkeypatch.setenv("TAVILY_API_KEY", "conventional")
    assert Settings(_env_file=None).tavily_api_key == "conventional"


def test_documented_prefixed_name_wins_when_both_are_set(monkeypatch):
    _clear(monkeypatch, "TAVILY_API_KEY")
    monkeypatch.setenv("TAVILY_API_KEY", "conventional")
    monkeypatch.setenv("CITINEL_TAVILY_API_KEY", "documented")
    assert Settings(_env_file=None).tavily_api_key == "documented"


def test_every_aliased_field_reads_both_spellings(monkeypatch):
    fields = ["anthropic_api_key", "anthropic_workspace_id", "tavily_api_key", "virustotal_api_key",
              "abuseipdb_api_key", "triage_model", "reasoning_model", "n8n_webhook_url",
              "swytchcode_api_key", "lyzr_api_key", "lyzr_guard_url", "lyzr_agent_id",
              "lyzr_triage_agent_id", "lyzr_review_agent_id", "lyzr_handover_agent_id"]
    for f in fields:
        _clear(monkeypatch, f.upper())
        monkeypatch.setenv(f.upper(), "v-" + f)
    s = Settings(_env_file=None)
    for f in fields:
        assert getattr(s, f) == "v-" + f, f
    for f in fields:
        monkeypatch.setenv("CITINEL_" + f.upper(), "p-" + f)
    s = Settings(_env_file=None)
    for f in fields:
        assert getattr(s, f) == "p-" + f, f


def test_field_name_still_works_from_code():
    assert Settings(_env_file=None, tavily_api_key="in-code").tavily_api_key == "in-code"
