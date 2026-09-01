"""Tests for the Enricher's tool-use loop, all offline.

Reuses test_agents_scaffold.py's fake-response-shape convention (content
blocks with .type, .stop_reason, .usage) so a tool_use block here matches the
same "shape the real SDK returns" discipline the other agents' tests hold to.
The connector side is the REAL EnrichmentSquad with an injected fake sender
(matching test_connectors.py's own pattern) -- only the model call is faked,
so tool execution is exercised for real, not assumed.
"""

from __future__ import annotations

from citinel.agents.enricher import MAX_TOOL_ITERATIONS, TOOLS, run_enricher
from citinel.agents.models import Role, VerifiedModel
from citinel.agents.transport import Transport
from citinel.connectors.base import EnrichmentCache
from citinel.connectors.enrichment import EnrichmentSquad


class _ToolUseBlock:
    type = "tool_use"
    def __init__(self, id, name, input): self.id, self.name, self.input = id, name, input


class _TextBlock:
    type = "text"
    def __init__(self, text): self.text = text


class _Usage:
    def __init__(self, input_tokens=100, output_tokens=50):
        self.input_tokens, self.output_tokens = input_tokens, output_tokens


class _Response:
    def __init__(self, content, stop_reason):
        self.content = content
        self.stop_reason = stop_reason
        self.usage = _Usage()


class _Messages:
    def __init__(self, script):
        self.script = list(script)
        self.seen: list[dict] = []

    def create(self, **kw):
        self.seen.append(kw)
        return self.script.pop(0)


class _FakeClient:
    def __init__(self, script):
        self.messages = _Messages(script)


def _transport(client) -> Transport:
    return Transport(client, VerifiedModel("fake-model", Role.REASONING, "Fake",
                                           200000, 64000, "2026-08-25", capabilities=()))


def _squad(tmp_path, sender=None) -> EnrichmentSquad:
    return EnrichmentSquad(EnrichmentCache(tmp_path / "cache"), sender)


def test_one_tool_call_then_a_final_stop(tmp_path, monkeypatch):
    from citinel.config import settings
    monkeypatch.setattr(settings, "virustotal_api_key", "k")
    monkeypatch.setattr(settings, "abuseipdb_api_key", "k")

    def sender(method, url, headers, params, json_body):
        if "virustotal" in url:
            return 200, {"data": {"attributes": {"last_analysis_stats": {"malicious": 0, "harmless": 60}}}}
        return 200, {"data": {"abuseConfidenceScore": 0, "totalReports": 0, "isp": "x", "countryCode": "US"}}

    client = _FakeClient([
        _Response([_ToolUseBlock("t1", "check_ip", {"ip": "185.151.160.15"})], "tool_use"),
        _Response([_TextBlock("no reputation concerns found")], "end_turn"),
    ])
    run = run_enricher(
        _transport(client), _squad(tmp_path, sender),
        system="test system", instruction="check the ip above",
        evidence=[], case_id="INC-TEST",
    )
    assert len(run.calls) == 2
    assert run.calls[0].stop_reason == "tool_use"
    assert run.calls[1].stop_reason == "end_turn"
    assert len(run.lookups) == 1
    assert run.lookups[0]["tool"] == "check_ip"
    assert run.lookups[0]["input"] == {"ip": "185.151.160.15"}
    assert {r["provider"] for r in run.lookups[0]["results"]} == {"virustotal", "abuseipdb"}
    assert run.evidence is not None
    assert "185.151.160.15" in run.evidence.content or "check_ip" in run.evidence.content
    assert run.stopped_reason == "stop_reason='end_turn', no further tool calls"

    # The assistant's tool_use turn was replayed verbatim before the result --
    # required by the API, and the actual behaviour under test.
    second_call_messages = client.messages.seen[1]["messages"]
    assert second_call_messages[1]["role"] == "assistant"
    assert second_call_messages[2]["role"] == "user"
    assert second_call_messages[2]["content"][0]["type"] == "tool_result"
    assert second_call_messages[2]["content"][0]["tool_use_id"] == "t1"


def test_no_indicators_worth_checking_stops_immediately(tmp_path):
    """The model deciding there's nothing to look up is a valid, common
    outcome -- not an error, and not forced to call a tool anyway."""
    client = _FakeClient([_Response([_TextBlock("nothing here worth enriching")], "end_turn")])
    run = run_enricher(
        _transport(client), _squad(tmp_path),
        system="s", instruction="i", evidence=[], case_id="INC-TEST",
    )
    assert len(run.calls) == 1
    assert run.lookups == []
    assert run.evidence is None, "no lookups means nothing to add as evidence"


def test_a_model_that_never_stops_hits_the_iteration_cap(tmp_path, monkeypatch):
    """The circuit breaker this loop exists to have -- a model that keeps
    requesting tools forever must not hang the pipeline.

    Pinned to no keys explicitly: a real VirusTotal/AbuseIPDB key now lives
    in .env, and without this pin these 6 unconfigured-sender calls silently
    became 6 REAL, rate-paced network calls (VirusTotal's own 15.5s
    min_interval_s) -- 77s for a test that should be instant, same class of
    leak already fixed twice elsewhere tonight."""
    from citinel.config import settings
    monkeypatch.setattr(settings, "virustotal_api_key", None)
    monkeypatch.setattr(settings, "abuseipdb_api_key", None)

    script = [_Response([_ToolUseBlock(f"t{i}", "check_ip", {"ip": "1.2.3.4"})], "tool_use")
              for i in range(MAX_TOOL_ITERATIONS)]
    client = _FakeClient(script)
    run = run_enricher(
        _transport(client), _squad(tmp_path),
        system="s", instruction="i", evidence=[], case_id="INC-TEST",
    )
    assert len(run.calls) == MAX_TOOL_ITERATIONS
    assert run.stopped_reason == f"hit the {MAX_TOOL_ITERATIONS}-iteration cap"
    # not_configured (no keys set) still counts as a real, recorded lookup
    assert len(run.lookups) == MAX_TOOL_ITERATIONS


def test_model_refusal_stops_the_loop_cleanly(tmp_path):
    client = _FakeClient([_Response([_TextBlock("I can't help analyse this.")], "refusal")])
    run = run_enricher(
        _transport(client), _squad(tmp_path),
        system="s", instruction="i", evidence=[], case_id="INC-TEST",
    )
    assert len(run.calls) == 1
    assert run.calls[0].refused is True
    assert run.stopped_reason == "model refused"
    assert run.lookups == []


def test_unknown_tool_name_does_not_crash_the_loop(tmp_path):
    """A tool call for something not in TOOLS is a routine, recordable
    outcome -- the loop degrades and continues, it does not raise."""
    client = _FakeClient([
        _Response([_ToolUseBlock("t1", "check_domain", {"domain": "evil.example"})], "tool_use"),
        _Response([_TextBlock("done")], "end_turn"),
    ])
    run = run_enricher(
        _transport(client), _squad(tmp_path),
        system="s", instruction="i", evidence=[], case_id="INC-TEST",
    )
    assert len(run.calls) == 2
    assert run.lookups[0]["results"] == []


def test_tools_only_offer_the_three_real_connectors():
    names = {t["name"] for t in TOOLS}
    assert names == {"check_ip", "check_hash", "search_context"}
    for t in TOOLS:
        assert "required" in t["input_schema"]
