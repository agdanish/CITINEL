"""Startuped.ai signals: how much of CITINEL is actually being used.

The hard rule, first, because it shapes everything else in this file:

    NOTHING ABOUT AN INCIDENT EVER LEAVES THROUGH HERE.

Startuped is a go-to-market platform. CITINEL processes cooperative-bank
security telemetry. Sending a host, an IP, a finding or even an incident id to
a marketing tool would be a real privacy failure wearing an integration's
clothes, and it would be worse for being deliberate. Every signal below
carries an aggregate count and nothing else -- there is a test that asserts
exactly that, and `_forbidden` exists so a future edit cannot quietly widen
the hole.

The shape of the API also pushes in this direction, which is convenient. A
Startuped "signal" is not a tracking event: there is no identity field, no
`track(event, properties)` call, and the docs say plainly that there is no
native lead or account association. It is a NAMED record with a time series
hanging off it. So CITINEL keeps five long-lived signals -- one per thing a
GTM reader would actually want to know -- and appends a value each time the
product does that thing:

    incidents investigated     the core loop is being used at all
    verdicts cited             the differentiating feature is landing
    actions gated              the policy engine is being exercised
    reports drafted            the compliance value is being delivered
    sign-offs completed        a human reached the end of the workflow

That is a genuine answer to the question a GTM platform exists to ask -- is
anyone using this, and which part -- without the product having to disclose a
single thing about the banks it protects.

Failure is always silent. A marketing signal must never be able to slow down,
break, or alter an incident investigation, so every call here is best-effort
and every exception is swallowed at the boundary.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from citinel.agents.quarantine import EGRESS_ALLOW, check_egress
from citinel.config import settings

BASE = "https://www.startuped.ai/api/v1/marketing/signals"

#: Keys the API forbids (org is derived from the API key) plus every field
#: that could carry incident content. Both are refused before a call is made.
_FORBIDDEN = frozenset({
    "organizationid", "organizationslug", "organizationdomain",
    "incident_id", "incidentid", "host", "hosts", "ip", "findings",
    "evidence", "raw", "evidence_raw", "target", "account", "user",
})

#: The five signals CITINEL maintains. signalKey is unique per organisation.
SIGNALS: dict[str, dict[str, str]] = {
    "citinel-incidents-investigated": {
        "name": "Incidents investigated",
        "description": "Security incidents put through CITINEL's agent swarm. "
                       "Counts only; no incident detail leaves the deployment.",
        "type": "behavioral",
    },
    "citinel-verdicts-cited": {
        "name": "Verdicts with cited evidence",
        "description": "Investigations that produced a verdict whose every claim "
                       "survived citation verification -- the product's core promise.",
        "type": "conversion",
    },
    "citinel-actions-gated": {
        "name": "Response actions gated by policy",
        "description": "Proposed containment actions evaluated against the policy "
                       "gate, whether allowed, held for a human, or denied.",
        "type": "behavioral",
    },
    "citinel-reports-drafted": {
        "name": "Compliance reports drafted",
        "description": "CERT-In and DPDP artifacts drafted for human sign-off. "
                       "CITINEL drafts; a human always signs and files.",
        "type": "conversion",
    },
    "citinel-signoffs": {
        "name": "Human sign-offs completed",
        "description": "Incidents a named human signed off -- the end of the "
                       "workflow, and the moment the product delivered its value.",
        "type": "retention",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.startuped_api_key}",
            "Content-Type": "application/json"}


def _clean(payload: dict[str, Any]) -> dict[str, Any] | str:
    """Refuse anything forbidden rather than stripping it.

    Stripping would let a caller believe it sent something it did not. A
    refusal is loud, and a marketing signal is never worth guessing about.
    """
    for k in payload:
        if k.lower() in _FORBIDDEN:
            return f"refusing to send field {k!r} to a go-to-market platform"
    return payload


def emit(signal_key: str, count: int, note: str = "", sender=None) -> dict[str, Any]:
    """Append one aggregate count to a named signal. Never raises.

    Creates the signal on first use (the API takes a POST) and appends a
    time-series value afterwards (a PUT addressed by signalKey). Both carry
    the same body, so a deployment that has never emitted before and one that
    has behave identically from the caller's side.
    """
    if signal_key not in SIGNALS:
        return {"status": "error", "detail": f"unknown signal {signal_key!r}"}
    if not settings.startuped_api_key:
        return {"status": "not_configured",
                "detail": "CITINEL_STARTUPED_API_KEY unset; no signal was sent"}
    if not check_egress(BASE, EGRESS_ALLOW).allowed:
        return {"status": "egress_refused", "detail": "startuped.ai is not on the egress allow-list"}

    meta = SIGNALS[signal_key]
    body: dict[str, Any] = {
        # name/description/type/status are all required by the OpenAPI spec
        # even though the docs page calls three of them optional. Sending all
        # four satisfies both readings.
        "name": meta["name"], "description": meta["description"],
        "type": meta["type"], "status": "active",
        "signalKey": signal_key,
        "value": "Medium",
        "signalValue": {"value": int(count), "timestamp": _now(),
                        "note": str(note)[:200]},
    }
    checked = _clean(body)
    if isinstance(checked, str):
        return {"status": "refused", "detail": checked}

    try:
        if sender is not None:
            code, resp = sender("POST", BASE, _headers(), body)
            if code == 409:                       # already exists: append instead
                code, resp = sender("PUT", f"{BASE}/{signal_key}", _headers(), body)
        else:
            import httpx
            with httpx.Client(timeout=10) as c:
                r = c.post(BASE, headers=_headers(), json=body)
                if r.status_code == 409:
                    r = c.put(f"{BASE}/{signal_key}", headers=_headers(), json=body)
                code, resp = r.status_code, (r.json() if r.content else {})
    except Exception as e:
        # Silent by design: a marketing signal must never be able to slow
        # down, break, or alter an incident investigation.
        return {"status": "error", "detail": f"startuped signal failed: {e}"}

    if code == 401:
        return {"status": "error", "detail":
                "Startuped rejected the API key (401). Keys expire after 30 days by default."}
    if code // 100 != 2:
        return {"status": "error", "detail": f"startuped HTTP {code}"}
    return {"status": "sent", "signal_key": signal_key, "count": int(count),
            "at": _now(), "detail": ""}


def emit_quietly(signal_key: str, count: int, note: str = "") -> None:
    """Fire-and-forget wrapper for call sites inside the incident path."""
    try:
        emit(signal_key, count, note)
    except Exception:
        pass
