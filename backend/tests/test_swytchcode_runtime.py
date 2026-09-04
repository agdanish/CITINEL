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


def test_a_missing_login_is_configuration_not_a_failed_action(keyed, monkeypatch):
    """The bug this locks: the CLI prints progress on the same stream as the
    error, and an unauthenticated call's text contains the word "policy"
    incidentally. A loose match reported "a policy stopped this" on the audit
    ledger when in truth nobody was logged in."""
    from citinel.connectors import swytchcode_runtime_transport as t

    class FakeErr(Exception):
        message = ("Telemetry is disabled. Run `swytchcode login` or set "
                   "SWYTCHCODE_TOKEN to enable usage tracking.\n"
                   "fetching policy bundles...")
        details = {}

    import swytchcode_runtime
    monkeypatch.setattr(swytchcode_runtime, "SwytchcodeError", FakeErr, raising=False)

    def boom(*a, **k):
        raise FakeErr()
    monkeypatch.setattr(swytchcode_runtime, "exec", boom, raising=False)

    with pytest.raises(t.TransportUnavailable):
        t.runtime_sender("comms", "notify_response_team", {"message": "x"})


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
