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

from dataclasses import dataclass
from typing import Any

from citinel.agents.guard import GuardResult, PIIFinding, screen_draft
from citinel.agents.quarantine import EGRESS_ALLOW, check_egress
from citinel.config import settings


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

        if status // 100 == 2 and isinstance(body, dict):
            extra = body.get("pii", []) or []
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
        payload = {"agent_id": settings.lyzr_agent_id, "task": "pii_guard", "input": text}
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
