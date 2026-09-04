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

import json
import os
from pathlib import Path
from typing import Any

#: Canonical ids, overridable per deployment because Swytchcode's own sources
#: disagree about them. `swy list tooling --json` is the authority.
TICKETING_METHOD = os.environ.get("CITINEL_SWY_TICKET_METHOD", "github.issue.create")
COMMS_METHOD = os.environ.get("CITINEL_SWY_COMMS_METHOD", "slack.chat.postmessage.create")


class TransportUnavailable(RuntimeError):
    """The runtime is not installed or the project was never scaffolded."""


def _auth_param(canonical_id: str) -> str:
    """Which parameter this tool wants its credential in.

    Read from .swytchcode/tooling.json, which the CLI writes and which is the
    only authority: Slack's postMessage declares `token`, while Swytchcode's
    own GitHub example passes `Authorization`. Assuming one shape for both
    sends the credential in a field the tool does not read, and the call fails
    for a reason that looks like anything except the real one.
    """
    try:
        root = Path(__file__).resolve()
        for parent in root.parents:
            cfg = parent / ".swytchcode" / "tooling.json"
            if cfg.exists():
                tools = json.loads(cfg.read_text()).get("tools", {})
                for entry in tools.get(canonical_id, {}).get("inputs", []):
                    for name in entry:
                        if name.lower() in ("token", "authorization"):
                            return name
                break
    except Exception:
        pass
    return "Authorization"


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
        raw = os.environ.get("CITINEL_SWY_GITHUB_TOKEN")
        if raw:
            key = _auth_param(TICKETING_METHOD)
            args[key] = f"Bearer {raw}" if key.lower() == "authorization" else raw
        return TICKETING_METHOD, args

    if api == "comms":
        args = {
            "body": {
                "channel": os.environ.get("CITINEL_SWY_SLACK_CHANNEL", ""),
                "text": str(params.get("message", ""))[:2000],
            }
        }
        raw = os.environ.get("CITINEL_SWY_SLACK_TOKEN")
        if raw:
            key = _auth_param(COMMS_METHOD)
            args[key] = f"Bearer {raw}" if key.lower() == "authorization" else raw
        return COMMS_METHOD, args

    raise ValueError(f"unknown ecosystem api {api!r}")


def _error_json(stream: str) -> dict[str, Any]:
    """The one JSON object the CLI prints for an error, or {}.

    The CLI's stderr mixes a telemetry notice and a request log line with the
    error itself; only the JSON line is the error. Scanned last-to-first
    because the error is the final thing written.
    """
    for line in reversed(stream.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                obj = json.loads(line)
                if isinstance(obj, dict) and ("error" in obj or "category" in obj):
                    return obj
            except json.JSONDecodeError:
                continue
    return {}


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
        # Both of these are shapes an SDK we do not own controls, and this
        # handler is the only thing standing between them and a receipt on a
        # permanent ledger. `details` non-dict raised AttributeError and an
        # empty `message` raised IndexError out of splitlines()[0]; either one
        # was swallowed by the executor's broad except and written down as a
        # generic "error" -- so a real policy block would have been recorded as
        # something going wrong, which is the exact confusion the classification
        # below exists to prevent.
        raw_details = getattr(e, "details", None)
        details: dict[str, Any] = raw_details if isinstance(raw_details, dict) else {}
        message = getattr(e, "message", None) or str(e)
        if not isinstance(message, str):
            message = str(message)

        # The CLI writes THREE things onto the stream this message came from:
        # a telemetry notice ("Run `swytchcode login` or set SWYTCHCODE_TOKEN
        # to enable usage tracking"), a request log line, and ONE JSON object
        # carrying the actual error with a `category`. The classifier below
        # used to substring-match the whole stream, so the telemetry notice --
        # printed on every call, logged in or not -- satisfied "swytchcode
        # login" and every failure of every kind became TransportUnavailable,
        # written to the ledger as not_configured. A broken policy definition
        # and a missing Slack credential were both reported as "the runtime is
        # not scaffolded", which sent an operator to re-scaffold a runtime that
        # was fine. Confirmed empirically against the real binary, 4 Sep 2026.
        #
        # So: find the JSON line, classify on its `category`, and only fall
        # back to substring matching on the error TEXT of that line, never on
        # the surrounding chatter.
        err = _error_json(message)
        category = str(err.get("category") or details.get("category") or "").lower()
        text = str(err.get("error") or "").strip() or (message.splitlines() or [""])[0]
        first = text.splitlines()[0][:300] if text else "swytchcode call failed"
        suggested = str(err.get("suggested_action") or details.get("suggested_action") or "")
        low = f"{text} {category}".lower()

        # Deployment facts, not failed actions: nobody is authenticated for this
        # provider, or the tool was never added to tooling.json. The message
        # now names the real condition ("missing credentials for Slack") rather
        # than the telemetry notice.
        # `not_found` is the kernel's category for a tool that is not in
        # tooling.json OR an integration bundle that was never fetched. The
        # second is what a container gets when the bundles are gitignored and
        # the image only copies the tracked files -- found by simulating
        # exactly that directory: "integration GitHub.github@1.1.4 bundle
        # missing ... Run: swytchcode bootstrap".
        if category in ("auth", "not_found") or any(t in low for t in (
                "not authenticated", "authentication required", "missing credentials",
                "not found in tooling", "tool not found", "bundle missing")):
            raise TransportUnavailable(first) from e

        # A policy block is the guardrail working. The CLI reports it under the
        # documented action type.
        if category in ("policy_denied", "policy_blocked") or "policy_blocked" in low or "blocked by policy" in low:
            return 403, {"policy_blocked": True, "message": first,
                         "suggested_action": suggested}

        # Everything else -- a policy that could not be EVALUATED, input that
        # failed validation, a provider error -- is a failed action and must
        # be recorded as one, with its real reason.
        return 502, {"policy_blocked": False, "message": first,
                     "category": category or "unknown",
                     "suggested_action": suggested}
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
