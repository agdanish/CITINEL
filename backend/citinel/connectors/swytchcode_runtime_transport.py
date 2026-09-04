"""The real Swytchcode transport: CITINEL's side-effecting calls, via `swy exec`.

Swytchcode's own pitch is that API success is not the same as correct agent
behaviour -- the running example in their engineering session was an agent
that sent the same email thirty-five times, every call returning 200, the
outcome a disaster. Their answer is three mechanisms: a real API definition
so the model cannot invent endpoints, idempotency so a retry does not
multiply the side effect, and policy guardrails evaluated BEFORE a call
leaves.

That is the same shape CITINEL already has, which is why this fits without
bending anything: OPA decides, and only a gate-approved decision reaches this
module. Swytchcode is the second, independent guardrail underneath it -- the
hand, never the head. A policy block here is not a failure of CITINEL's
reasoning; it is a demonstration that an action can be stopped outside the
agent's own judgement, which is the whole argument.

Two ecosystem APIs, a real division of labour:
    ticketing  -> GitHub Issues    an incident ticket a human can pick up
    comms      -> Slack            the response team hears about it

Transport notes, learned the hard way from Swytchcode's own examples rather
than from their docs:
  * `swytchcode_runtime.exec` is a subprocess wrapper around the `swy` binary,
    not an HTTP client. Its README calls it "a pipe, not a brain". The binary
    must be on PATH (or at SWYTCHCODE_BIN) and the project must have been
    scaffolded with `swy init`.
  * Canonical ids differ between their docs and their own working examples.
    They are configured here, never hardcoded from documentation, and
    `swy list tooling --json` is the only authority for what a deployment
    actually has.
  * The success shape differs too: the docs show {"success", "result"} while
    their working Python example reads {"error", "data"}. Both are handled.
  * Credentials travel per call as `Authorization`, which is what their own
    multi-API example does. That keeps this headless: no OAuth browser flow,
    no managed credential store, nothing a demo machine has to have logged in.
"""

from __future__ import annotations

import os
from typing import Any

#: Canonical ids, overridable per deployment because Swytchcode's own sources
#: disagree about them. `swy list tooling --json` is the authority.
TICKETING_METHOD = os.environ.get("CITINEL_SWY_TICKET_METHOD", "github.repo.issues.create")
COMMS_METHOD = os.environ.get("CITINEL_SWY_COMMS_METHOD", "slack.chat.postmessage.create")


class TransportUnavailable(RuntimeError):
    """The runtime is not installed or the project was never scaffolded."""


def _bearer(var: str) -> str | None:
    v = os.environ.get(var)
    return f"Bearer {v}" if v else None


def build_args(api: str, action: str, params: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Map CITINEL's (api, action, params) onto a canonical id and exec args.

    Kept pure and separate from the call so the mapping is testable without a
    binary, a network, or a Swytchcode account.
    """
    if api == "ticketing":
        owner = os.environ.get("CITINEL_SWY_GITHUB_OWNER", "")
        repo = os.environ.get("CITINEL_SWY_GITHUB_REPO", "")
        title = f"[CITINEL] {params.get('action', action)} on {params.get('target', 'unspecified')}"
        body = (
            f"Opened by CITINEL for incident **{params.get('incident_id', '?')}**.\n\n"
            f"- action class: `{params.get('action', action)}`\n"
            f"- target: `{params.get('target', 'unspecified')}`\n"
            f"- governing clause: `{params.get('clause', 'n/a')}`\n\n"
            "The policy gate approved this action before it was executed. "
            "Endpoints are simulated; this ticket is the human-visible record."
        )
        args: dict[str, Any] = {
            "owner": owner, "repo": repo,
            "body": {"title": title, "body": body, "labels": ["citinel", "incident"]},
        }
        auth = _bearer("CITINEL_SWY_GITHUB_TOKEN")
        if auth:
            args["Authorization"] = auth
        return TICKETING_METHOD, args

    if api == "comms":
        args = {
            "body": {
                "channel": os.environ.get("CITINEL_SWY_SLACK_CHANNEL", ""),
                "text": str(params.get("message", ""))[:2000],
            }
        }
        auth = _bearer("CITINEL_SWY_SLACK_TOKEN")
        if auth:
            args["Authorization"] = auth
        return COMMS_METHOD, args

    raise ValueError(f"unknown ecosystem api {api!r}")


def runtime_sender(api: str, action: str, params: dict[str, Any]) -> tuple[int, Any]:
    """(status, body) in the shape SwytchcodeExecutor already expects.

    A policy block is NOT an error here: it is the guardrail doing its job, and
    it is reported as such so the receipt on the audit ledger says a policy
    stopped the action rather than that something went wrong.
    """
    try:
        from swytchcode_runtime import SwytchcodeError, exec as swy_exec
    except ImportError as e:  # the SDK is optional; the seam degrades without it
        raise TransportUnavailable(f"swytchcode-runtime is not installed: {e}") from e

    canonical_id, args = build_args(api, action, params)
    try:
        result = swy_exec(canonical_id, args)
    except SwytchcodeError as e:
        details = getattr(e, "details", None) or {}
        message = getattr(e, "message", str(e))
        low = f"{message} {details.get('category', '')}".lower()

        # Order matters, and so does precision. The CLI writes its progress and
        # notices onto the same stream as the error, so a naive substring match
        # is wrong: an unauthenticated call's text contains the word "policy"
        # incidentally and would be misread as a policy block -- which would
        # put "a policy stopped this" on the audit ledger when in truth nobody
        # was logged in. Confirmed empirically against the real binary.
        #
        # Configuration state first: not authenticated, or the tool was never
        # added to tooling.json. Both are deployment facts, not failed actions.
        if any(t in low for t in ("swytchcode login", "swytchcode_token",
                                  "not authenticated", "authentication required",
                                  "not found in tooling", "tool not found")):
            raise TransportUnavailable(message.splitlines()[0][:300]) from e

        # A policy block is the guardrail working. Matched on the documented
        # action type, not the bare word "policy".
        if "policy_blocked" in low or "blocked by policy" in low:
            return 403, {"policy_blocked": True, "message": message.splitlines()[0][:300],
                         "suggested_action": details.get("suggested_action", "")}

        return 502, {"policy_blocked": False, "message": message,
                     "suggested_action": details.get("suggested_action", "")}
    except FileNotFoundError as e:
        raise TransportUnavailable(f"the swytchcode binary is not on PATH: {e}") from e

    # Their docs say {"success", "result"}; their own working example reads
    # {"error", "data"}. Accept either rather than betting on one.
    if isinstance(result, dict):
        if result.get("error"):
            return 502, {"message": str(result["error"])[:400]}
        payload = result.get("data", result.get("result", result))
        return 200, payload
    return 200, result
