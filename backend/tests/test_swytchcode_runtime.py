"""The Swytchcode transport: two ecosystem APIs, and a guardrail under the gate.

The receipts here land on the permanent audit ledger, so what a receipt SAYS
matters as much as whether the call worked. "A policy stopped this" and
"nobody was logged in" are different facts about a deployment and must never
be confused -- which is exactly the bug the classification test below locks.
"""

from __future__ import annotations

import pytest

from citinel.config import settings
from citinel.connectors.swytchcode import SwytchcodeExecutor
from citinel.connectors.swytchcode_runtime_transport import build_args
from citinel.policy.gate import Decision, Verdict


def _decision(verdict=Verdict.ALLOW):
    return Decision(verdict=verdict, clause_ref="c-12", action_class="isolate_host",
                    reasons=["gate approved"], intent_preview="isolate WRK-2214",
                    engine="test")


@pytest.fixture
def keyed(monkeypatch):
    monkeypatch.setattr(settings, "swytchcode_api_key", "swy-test")


def test_two_distinct_ecosystem_apis_each_do_a_different_job(keyed):
    """The track wants >=2 external APIs. Two calls to one service would not
    be that; ticketing and comms are a real division of labour."""
    seen = []
    ex = SwytchcodeExecutor(sender=lambda api, action, p: (seen.append((api, action)), (200, {"ok": 1}))[1])
    receipts = ex.execute_for_decision(_decision(), "WRK-2214", "INC-0417")

    assert [a for a, _ in seen] == ["ticketing", "comms"]
    assert [r.ecosystem_api for r in receipts] == ["ticketing", "comms"]
    assert all(r.status == "executed" for r in receipts)


def test_the_arg_mapping_targets_real_canonical_ids_and_carries_the_incident(monkeypatch):
    monkeypatch.setenv("CITINEL_SWY_GITHUB_OWNER", "acme")
    monkeypatch.setenv("CITINEL_SWY_GITHUB_REPO", "soc")
    cid, args = build_args("ticketing", "create_incident_ticket",
                           {"incident_id": "INC-0417", "action": "isolate_host",
                            "target": "WRK-2214", "clause": "c-12"})
    assert cid == "github.issue.create"
    assert args["owner"] == "acme" and args["repo"] == "soc"
    assert "INC-0417" in args["body"]["body"]
    # the attribution the policy requires
    assert "CITINEL" in args["body"]["title"]

    cid2, args2 = build_args("comms", "notify_response_team", {"message": "isolated"})
    assert cid2 == "slack.chat.postmessage.create"
    assert args2["body"]["text"] == "isolated"


def test_credentials_travel_per_call_so_no_oauth_flow_is_needed(monkeypatch):
    monkeypatch.setenv("CITINEL_SWY_GITHUB_TOKEN", "ghp_x")
    _, args = build_args("ticketing", "create_incident_ticket", {})
    assert args["Authorization"] == "Bearer ghp_x"
    # and without one, no empty header is sent
    monkeypatch.delenv("CITINEL_SWY_GITHUB_TOKEN")
    _, args2 = build_args("ticketing", "create_incident_ticket", {})
    assert "Authorization" not in args2


def test_swytchcode_never_executes_what_the_gate_refused(keyed):
    """Swytchcode is the hand, never the head: OPA stays the only authority."""
    calls = []
    ex = SwytchcodeExecutor(sender=lambda a, ac, p: (calls.append(a), (200, {}))[1])
    receipts = ex.execute_for_decision(_decision(Verdict.DENY), "x", "INC-0417")

    assert calls == []                          # nothing left the process
    assert [r.status for r in receipts] == ["refused"]


def test_a_policy_block_is_recorded_as_the_guardrail_working(keyed):
    """Not an error. Swytchcode evaluates before the request leaves, so
    nothing happened -- and the ledger must say a policy stopped it."""
    ex = SwytchcodeExecutor(sender=lambda a, ac, p: (403, {
        "policy_blocked": True, "message": "names core banking infrastructure"}))
    r = ex.execute_for_decision(_decision(), "cbs-prod-01", "INC-0417")[0]

    assert r.status == "policy_blocked"
    assert "policy stopped" in r.detail and "core banking" in r.detail


def _cli_error(category: str, error: str, **extra):
    """A SwytchcodeError shaped exactly like the real binary raises it: the
    telemetry notice and a request log line on the same stream, then ONE JSON
    object carrying the classified error. Captured from swytchcode 2.20.15."""
    import json as _json
    payload = {"error": error, "category": category,
               "suggested_action": extra.get("suggested_action", ""),
               "docs_url": "https://docs.swytchcode.com/"}

    class FakeErr(Exception):
        message = ("Telemetry is disabled. Run `swytchcode login` or set "
                   "SWYTCHCODE_TOKEN to enable usage tracking.\n"
                   "2026/09/04 15:43:42 [swytchcode exec] request tool=x {}\n"
                   + _json.dumps(payload))
        details = None
    return FakeErr


def _raise_with(monkeypatch, err_cls):
    import swytchcode_runtime
    monkeypatch.setattr(swytchcode_runtime, "SwytchcodeError", err_cls, raising=False)
    monkeypatch.setattr(swytchcode_runtime, "exec",
                        lambda *a, **k: (_ for _ in ()).throw(err_cls()), raising=False)


def test_missing_provider_credentials_is_configuration_not_a_failed_action(keyed, monkeypatch):
    """The real not-authenticated shape is a JSON error with category "auth".
    It is a deployment fact and must surface as TransportUnavailable carrying
    the REAL condition, not the telemetry notice that precedes it."""
    from citinel.connectors import swytchcode_runtime_transport as t
    _raise_with(monkeypatch, _cli_error(
        "auth", "missing credentials for Slack - run `swytchcode auth connect Slack`"))
    with pytest.raises(t.TransportUnavailable) as ei:
        t.runtime_sender("comms", "notify_response_team", {"message": "x"})
    assert "missing credentials for Slack" in str(ei.value)
    assert "Telemetry" not in str(ei.value)


def test_the_telemetry_notice_alone_does_not_mean_not_configured(keyed, monkeypatch):
    """The bug this locks. The CLI prints "Run `swytchcode login`" on EVERY
    call, logged in or not, as a telemetry notice. The classifier used to
    substring-match the whole stream, so every failure of every kind became
    not_configured on the ledger: a broken policy definition and a missing
    Slack credential were both recorded as "the runtime is not scaffolded",
    which sent an operator to re-scaffold a runtime that was fine. Confirmed
    against the real binary, 4 Sep 2026."""
    from citinel.connectors import swytchcode_runtime_transport as t
    _raise_with(monkeypatch, _cli_error(
        "policy_error",
        'policy "citinel-no-core-banking-in-ticket": ambiguous field resolution: '
        '"body" has conflicting values in top-level and body'))
    code, body = t.runtime_sender("ticketing", "create_incident_ticket", {"incident_id": "I"})
    assert code == 502 and body["policy_blocked"] is False
    assert body["category"] == "policy_error"
    assert "ambiguous field resolution" in body["message"]


def test_a_policy_block_is_reported_under_the_cli_s_real_category(keyed, monkeypatch):
    """The binary reports a guard firing as category "policy_denied"."""
    from citinel.connectors import swytchcode_runtime_transport as t
    _raise_with(monkeypatch, _cli_error(
        "policy_denied", "CITINEL policy: a ticket naming core banking infrastructure is blocked"))
    code, body = t.runtime_sender("ticketing", "create_incident_ticket", {"incident_id": "I"})
    assert code == 403 and body["policy_blocked"] is True
    assert "core banking" in body["message"]


def test_no_key_means_nothing_is_attempted_or_claimed(monkeypatch):
    monkeypatch.setattr(settings, "swytchcode_api_key", None)
    calls = []
    ex = SwytchcodeExecutor(sender=lambda a, ac, p: (calls.append(a), (200, {}))[1])
    receipts = ex.execute_for_decision(_decision(), "WRK-2214", "INC-0417")
    assert calls == []
    assert all(r.status == "not_configured" for r in receipts)


def test_the_credential_goes_in_the_parameter_each_tool_actually_declares(monkeypatch):
    """Slack's postMessage declares `token`; Swytchcode's own GitHub example
    passes `Authorization`. Assuming one shape for both puts the credential in
    a field the tool never reads, and the call then fails for a reason that
    looks like anything except the real one."""
    from citinel.connectors.swytchcode_runtime_transport import _auth_param, build_args

    # read from the repo's real .swytchcode/tooling.json, which the CLI wrote
    assert _auth_param("slack.chat.postmessage.create") == "token"
    # a tool not registered yet falls back to the documented default
    assert _auth_param("something.not.registered") == "Authorization"

    monkeypatch.setenv("CITINEL_SWY_SLACK_TOKEN", "xoxb-1")
    _, args = build_args("comms", "notify_response_team", {"message": "x"})
    assert args["token"] == "xoxb-1"          # not wrapped in Bearer
    assert "Authorization" not in args


def test_a_missing_integration_bundle_is_a_deployment_fact(keyed, monkeypatch):
    """What the Render image produced: the bundles are gitignored and the
    Dockerfile copied only the tracked files, so the kernel could not find the
    integration at all. That is not a failed action and not a policy block."""
    from citinel.connectors import swytchcode_runtime_transport as t
    _raise_with(monkeypatch, _cli_error(
        "not_found", "integration GitHub.github@1.1.4 bundle missing.\nExpected: "
        "/app/.swytchcode/integrations/GitHub/github/1.1.4/wrekenfile.yaml\nRun: swytchcode bootstrap"))
    with pytest.raises(t.TransportUnavailable) as ei:
        t.runtime_sender("ticketing", "create_incident_ticket", {"incident_id": "I"})
    assert "bundle missing" in str(ei.value)


# -- the kernel succeeding is not the provider succeeding ----------------------

def _kernel_returns(monkeypatch, value):
    """swytchcode_runtime.exec returning a value, shaped as the real kernel wraps
    a provider body: {"data": <provider json>}. Captured from 2.20.15."""
    import swytchcode_runtime
    monkeypatch.setattr(swytchcode_runtime, "exec", lambda *a, **k: value, raising=False)
    monkeypatch.setenv("CITINEL_SWY_SLACK_CHANNEL", "C0TEST")
    monkeypatch.setenv("CITINEL_SWY_SLACK_TOKEN", "xoxb-test")
    monkeypatch.setenv("CITINEL_SWY_GITHUB_TOKEN", "ghp-test")


def test_a_slack_refusal_inside_an_http_200_is_a_failed_action(monkeypatch):
    """Found by sending a real message. Slack's Web API answers HTTP 200 to
    everything and signals failure only as {"ok": false, "error": ...} in the
    body. The kernel wrapped that in {"data": ...}, the transport's error check
    ran on the wrapper, and the unwrapped refusal went out as 200 -- so the
    ledger would have said "comms executed" for a message Slack never posted."""
    from citinel.connectors.swytchcode_runtime_transport import runtime_sender
    _kernel_returns(monkeypatch, {"data": {"ok": False, "error": "not_in_channel",
                                           "warning": "missing_charset"}})
    status, body = runtime_sender("comms", "notify_channel", {"incident_id": "INC-1", "title": "t", "summary": "s"})
    assert status == 502
    assert body["policy_blocked"] is False
    assert "not_in_channel" in body["message"] and body["provider_error"] == "not_in_channel"
    assert "invite" in body["suggested_action"]


def test_a_slack_success_is_still_a_success(monkeypatch):
    from citinel.connectors.swytchcode_runtime_transport import runtime_sender
    _kernel_returns(monkeypatch, {"data": {"ok": True, "ts": "1757000000.000100", "channel": "C0TEST"}})
    status, body = runtime_sender("comms", "notify_channel", {"incident_id": "INC-1", "title": "t", "summary": "s"})
    assert status == 200 and body["ok"] is True and body["ts"]


def test_a_github_success_without_an_ok_field_is_untouched(monkeypatch):
    """GitHub uses real HTTP status codes and has no `ok`; a created issue must
    not be mistaken for a refusal just because the body lacks the field."""
    from citinel.connectors.swytchcode_runtime_transport import runtime_sender
    _kernel_returns(monkeypatch, {"data": {"id": 1, "number": 7, "html_url": "https://github.com/o/r/issues/7"}})
    status, body = runtime_sender("ticketing", "create_incident_ticket", {"incident_id": "INC-1", "title": "t", "summary": "s"})
    assert status == 200 and body["number"] == 7


def test_a_provider_refusal_reaches_the_ledger_with_its_reason(keyed):
    """The receipt is what lands on the permanent ledger. "error: HTTP 502"
    told a reader nothing; the reason the transport already knew must travel."""
    ex = SwytchcodeExecutor(sender=lambda a, ac, p: (502, {
        "policy_blocked": False, "message": "provider refused: not_in_channel",
        "category": "provider_error", "provider_error": "not_in_channel",
        "suggested_action": "invite the Swytchcode app to the channel"}))
    receipts = ex.execute_for_decision(_decision(), "we8105desk", "INC-0417")
    comms = [r for r in receipts if r.ecosystem_api == "comms"][0]
    assert comms.status == "error"
    assert "not_in_channel" in comms.detail
    assert "HTTP 502" not in comms.detail


def test_a_comms_call_without_a_message_still_names_the_incident(monkeypatch):
    """Slack answers `no_text` to an empty body. Found by sending one for real
    with the wrong parameter name; the builder now composes the attribution
    line instead of shipping an empty string."""
    monkeypatch.setenv("CITINEL_SWY_SLACK_CHANNEL", "C0TEST")
    _, args = build_args("comms", "notify_response_team", {"incident_id": "INC-0417", "action": "isolate_host"})
    assert args["body"]["text"] and "INC-0417" in args["body"]["text"]
    _, args2 = build_args("comms", "notify_response_team", {"incident_id": "INC-1", "message": "  "})
    assert "INC-1" in args2["body"]["text"]          # whitespace-only counts as absent
