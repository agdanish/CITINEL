"""Lyzr connector: the governance / observability control plane (SDD 15.3).

Lyzr sits ABOVE the swarm as a provider-agnostic control plane (it works with
Claude, it does not replace it). CITINEL wires two genuine attachment points:

  1. LyzrGuard -- an independent second-opinion PII/hallucination check on top
     of CITINEL's own deterministic guard (agents/guard.py) and on top of
     citation-grounding. Screens compliance drafts before human sign-off.

  2. LyzrObserver -- fleet observability: forwards each agent's lifecycle
     events so a Lyzr dashboard can show live per-agent status. The swarm
     (Step 7) reports through this seam; a NullObserver is the default so the
     pipeline is unaffected when Lyzr is not configured.

Both degrade gracefully with no key, and every outbound call is egress-checked.
Because Lyzr's API host is set per deployment, it is read from config and added
to the egress allow-list only when explicitly configured -- never a wildcard.

Honest boundaries: Lyzr is a second check and an observer. It is NOT the policy
authority (OPA is) and NOT the system of record (CITINEL's own append-only
ledger is; Lyzr can mirror it, per 15.3's "fulfill, not duplicate", but the
ledger remains canonical).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from citinel.agents.guard import GuardResult, PIIFinding, screen_draft
from citinel.agents.quarantine import EGRESS_ALLOW, check_egress
from citinel.audit.ledger import LedgerSink
from citinel.config import settings

# Lyzr's real REST contract is chat-shaped: POST a body to a chat endpoint,
# get back {"response": "<text>"}. There is no generic task-dispatch API.
# The exact request shape (see _chat_payload below) was first taken from
# docs.lyzr.ai's quickstart page and was WRONG in two ways a docs page alone
# couldn't have caught -- confirmed only once a real agent was deployed and
# its own "Agent API" tab showed the actual generated integration snippet.
# _chat_payload's docstring has the specifics and the correction. The lesson
# generalizes: for this connector, the platform's own generated snippet for
# a live agent outranks its docs when the two disagree.
#
# So the three things CITINEL needs from one Lyzr agent (screen for PII,
# remember a ledger entry, report the last one) all ride inside `message` as
# JSON, and the agent must reply with pure JSON text in `response` -- which
# only works if the Studio agent is instructed to do exactly that.
#
# The exact Role/Goal/Instructions to paste into Studio -- including the
# injection-hardening this needed once we accounted for pii_guard's "input"
# being untrusted attacker telemetry, not trusted user text, plus which
# Studio toggles to set and a known open gap in the memory design -- live in
# LYZR-AGENT-CONFIG.md at the repo root. That is the single source of truth;
# duplicating a long, security-relevant prompt inline here would just create
# a second copy to drift out of sync with the first.
#
# ledger_record and ledger_head deliberately share one fixed session_id
# (see LyzrLedgerMirror below) so Lyzr's own session memory is what ties them
# together across calls -- pii_guard does not need that continuity, so it
# uses its own. LYZR-AGENT-CONFIG.md's "Known follow-up" section covers a
# real, still-open gap in that design: Lyzr's memory is not confirmed to
# guarantee exact-hash recall over the hours/days between calls.


def _parse_agent_reply(body: Any) -> dict[str, Any]:
    """Unwrap {"response": "<json text>"} and parse the inner JSON.

    The agent not replying in the instructed format must degrade, never
    raise or crash the caller -- it is a prompt-following failure, not a
    CITINEL bug, and the callers below treat an empty dict as "got nothing
    usable" rather than trusting absent keys.
    """
    if not isinstance(body, dict):
        return {}
    raw = body.get("response", "")
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _chat_payload(task_message: str, session_id: str) -> dict[str, Any]:
    """Build a request body against Lyzr's REAL wire format.

    Confirmed against the live "Agent API" tab for a deployed agent (the
    platform's own generated integration snippet, not a docs page) --
    verified 1 Sep 2026 after the docs-derived version below turned out to
    be wrong in two ways: the endpoint is a fixed
    https://agent-prod.studio.lyzr.ai/v3/inference/chat/, not
    /v3/agent/{agent_id}/chat, and agent_id travels in the JSON body
    (alongside a user_id) rather than being baked into the URL path. Lyzr's
    own docs are known to be inconsistent across doc trees (see
    LYZR-AGENT-CONFIG.md's research notes) -- this is the source that
    actually matters when the two disagree.

    `user_id` is set to a fixed, non-personal identifier rather than any
    real account's email -- observed examples used the account owner's own
    login email, but nothing suggests that specific value is required
    rather than just illustrative. If Lyzr rejects this, the fix is here.
    """
    return {
        "user_id": "citinel-backend",
        "agent_id": settings.lyzr_agent_id,
        "session_id": session_id,
        "message": task_message,
    }


def _lyzr_allow() -> frozenset[str]:
    """Egress allow-list extended with the operator-configured Lyzr host."""
    if settings.lyzr_guard_url:
        from urllib.parse import urlparse
        host = urlparse(settings.lyzr_guard_url).hostname
        if host:
            return EGRESS_ALLOW | {host}
    return EGRESS_ALLOW


class LyzrGuard:
    """CITINEL's local guard, plus Lyzr's independent second opinion."""

    def __init__(self, sender=None) -> None:
        self._sender = sender    # sender(url, headers, json) -> (status, body)

    def screen(self, draft, extra_evidence: str = "") -> GuardResult:
        # Tier 1: CITINEL's own deterministic screen -- always runs.
        result = screen_draft(draft, extra_evidence)

        # Tier 2: Lyzr's independent check -- only when configured.
        if not (settings.lyzr_api_key and settings.lyzr_guard_url):
            return result

        decision = check_egress(settings.lyzr_guard_url, _lyzr_allow())
        if not decision.allowed:
            result.note += f" (Lyzr second-check skipped: {decision.reason})"
            return result

        text = "\n".join(f.value for f in draft.fields
                         if f.fill != "human" and not f.value.strip().startswith("<"))
        try:
            status, body = self._call(text)
        except Exception as e:
            result.note += f" (Lyzr second-check unavailable: {e})"
            return result

        reply = _parse_agent_reply(body)
        if status // 100 == 2 and reply:
            extra = reply.get("pii", []) or []
            for item in extra:
                result.findings.append(PIIFinding(
                    pii_type=f"lyzr:{item.get('type', 'flagged')}",
                    confidence=item.get("confidence", "medium"),
                    masked=item.get("masked", "***"),
                    context_field="lyzr-second-check"))
            result.checked_by = "citinel-local + lyzr"
            result.clean = len(result.findings) == 0
        return result

    def _call(self, text: str) -> tuple[int, Any]:
        headers = {"x-api-key": settings.lyzr_api_key, "Content-Type": "application/json"}
        message = json.dumps({"task": "pii_guard", "input": text})
        payload = _chat_payload(message, "citinel-lyzr-guard")
        if self._sender is not None:
            return self._sender(settings.lyzr_guard_url, headers, payload)
        import httpx
        with httpx.Client(timeout=20) as c:
            r = c.post(settings.lyzr_guard_url, headers=headers, json=payload)
            return r.status_code, (r.json() if r.content else {})


@dataclass
class AgentEvent:
    case_id: str
    agent: str
    phase: str            # start | finish | tool_call
    detail: dict


class AgentObserver:
    """Fleet-observability seam. The swarm (Step 7) reports here."""

    def observe(self, event: AgentEvent) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class NullObserver(AgentObserver):
    """Default: records nothing external. The pipeline never depends on Lyzr."""

    def observe(self, event: AgentEvent) -> None:
        return None


class LyzrObserver(AgentObserver):
    """Forwards agent lifecycle events to a Lyzr observability dashboard."""

    def __init__(self, sender=None) -> None:
        self._sender = sender
        self.forwarded = 0

    def observe(self, event: AgentEvent) -> None:
        if not (settings.lyzr_api_key and settings.lyzr_guard_url):
            return
        if not check_egress(settings.lyzr_guard_url, _lyzr_allow()).allowed:
            return
        try:
            if self._sender is not None:
                self._sender(settings.lyzr_guard_url,
                             {"x-api-key": settings.lyzr_api_key},
                             {"type": "agent_event", **event.__dict__})
            self.forwarded += 1
        except Exception:
            return    # observability must never break the pipeline


# ---------------------------------------------------------------------------
# Attachment point 4 of 4 (SDD 15.3): the immutable audit log, as an external
# witness to CITINEL's own -- "fulfill, not duplicate".
# ---------------------------------------------------------------------------

@dataclass
class MirrorComparison:
    """The result of asking the witness whether it still agrees with us."""

    status: str          # agreed | diverged | unavailable | not_configured
    local_head: str
    remote_head: str = ""
    local_count: int = 0
    remote_count: int = 0
    detail: str = ""

    @property
    def tamper_suspected(self) -> bool:
        return self.status == "diverged"

    def as_dict(self) -> dict[str, Any]:
        return {"status": self.status, "local_head": self.local_head,
                "remote_head": self.remote_head, "local_count": self.local_count,
                "remote_count": self.remote_count,
                "tamper_suspected": self.tamper_suspected, "detail": self.detail}


class LyzrLedgerMirror(LedgerSink):
    """Mirrors each audit entry to Lyzr, and can ask it what it remembers.

    The mirroring half is the cheap half. `compare` is where the value is:
    a witness nobody ever queries proves nothing, so this class is only
    honestly "an immutable audit log" if something actually reconciles the
    two chains. `citinel ledger-witness` (CLI) and /api/ledger/verify's
    witness field are the callers that make it real.

    What a divergence does and does not mean, because the distinction matters
    to anyone reading the output under pressure:

      diverged     the two chains disagree at the head. Either the local file
                   was replaced wholesale (the attack a self-contained chain
                   cannot see), or entries were mirrored and then the local
                   ledger was rolled back, or the mirror is simply behind.
                   It is a signal to investigate, never a proof of tampering
                   on its own.
      unavailable  the witness could not be reached. This says nothing at all
                   about the local chain's integrity -- it is a statement
                   about network reachability, and is deliberately NOT
                   reported as agreement.

    Never the system of record: `LedgerSink`'s contract is that the local
    append already committed before this is called, and that anything raised
    here is swallowed.
    """

    #: record() and _head_request() share this fixed session id so Lyzr's own
    #: session memory is what ties "what was I told" to "what do I now report"
    #: across separate HTTP calls -- see the module-level docstring above.
    _SESSION_ID = "citinel-lyzr-ledger"

    def __init__(self, sender=None) -> None:
        self._sender = sender
        self.mirrored = 0

    # -- the witness side ---------------------------------------------------

    def record(self, entry) -> None:
        """Forward one committed entry. Called by AuditLedger.append."""
        if not (settings.lyzr_api_key and settings.lyzr_guard_url):
            return
        if not check_egress(settings.lyzr_guard_url, _lyzr_allow()).allowed:
            return
        message = json.dumps({"task": "ledger_record", "entry": entry.as_dict()})
        payload = _chat_payload(message, self._SESSION_ID)
        if self._sender is not None:
            self._sender(settings.lyzr_guard_url,
                         {"x-api-key": settings.lyzr_api_key}, payload)
        else:
            import httpx
            with httpx.Client(timeout=10) as c:
                c.post(settings.lyzr_guard_url,
                       headers={"x-api-key": settings.lyzr_api_key}, json=payload)
        self.mirrored += 1

    # -- the half that makes it worth having --------------------------------

    def compare(self, ledger) -> MirrorComparison:
        """Reconcile the local chain head against the witness's.

        Detects wholesale replacement of the local ledger, which
        `verify_chain` structurally cannot: a rewritten file with recomputed
        hashes verifies perfectly against itself.
        """
        local_head = ledger.head
        local_count = sum(1 for _ in ledger.entries())

        if not (settings.lyzr_api_key and settings.lyzr_guard_url):
            return MirrorComparison(
                "not_configured", local_head, local_count=local_count,
                detail="no Lyzr witness configured; the local chain stands alone "
                       "and wholesale replacement would not be detectable")

        decision = check_egress(settings.lyzr_guard_url, _lyzr_allow())
        if not decision.allowed:
            return MirrorComparison("unavailable", local_head,
                                    local_count=local_count, detail=decision.reason)
        try:
            status, body = self._head_request()
        except Exception as e:
            return MirrorComparison("unavailable", local_head,
                                    local_count=local_count,
                                    detail=f"witness unreachable: {e}")
        if status // 100 != 2 or not isinstance(body, dict):
            return MirrorComparison("unavailable", local_head,
                                    local_count=local_count,
                                    detail=f"witness returned HTTP {status}")

        reply = _parse_agent_reply(body)
        if not reply:
            # The agent answered (2xx) but not in the instructed JSON shape --
            # a misconfigured/mis-prompted agent, not a security signal. This
            # must not silently fall into "diverged" (a real investigate-this
            # claim) just because remote_head defaulted to "".
            return MirrorComparison(
                "unavailable", local_head, local_count=local_count,
                detail="witness replied but not in the expected JSON format "
                       "(check the Studio agent's instructions)")

        remote_head = str(reply.get("head", ""))
        remote_count = int(reply.get("count", 0) or 0)
        if remote_head and remote_head == local_head:
            return MirrorComparison(
                "agreed", local_head, remote_head, local_count, remote_count,
                detail=f"witness agrees at {local_count} entries")
        return MirrorComparison(
            "diverged", local_head, remote_head, local_count, remote_count,
            detail=("local and witness chain heads differ -- investigate: "
                    "wholesale local replacement, a rollback, or mirror lag. "
                    "Not proof of tampering on its own."))

    def _head_request(self) -> tuple[int, Any]:
        headers = {"x-api-key": settings.lyzr_api_key, "Content-Type": "application/json"}
        message = json.dumps({"task": "ledger_head"})
        payload = _chat_payload(message, self._SESSION_ID)
        if self._sender is not None:
            return self._sender(settings.lyzr_guard_url, headers, payload)
        import httpx
        with httpx.Client(timeout=15) as c:
            r = c.post(settings.lyzr_guard_url, headers=headers, json=payload)
            return r.status_code, (r.json() if r.content else {})
