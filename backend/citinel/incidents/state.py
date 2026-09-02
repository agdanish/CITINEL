"""Where an incident really is, read off the ledger.

`incidents.jsonl` is rebuilt from scratch by every `incidents build`, so the
state it carries is always CAUGHT: it has no memory of what the swarm, the
gate, the marshal or a human did afterwards. Those facts are on the
append-only ledger, one frame each. This derives the working state from those
frames, never from the model's prose, and names the frames it used so a
reader can check the derivation against the reel.

Implied states are monotonic on purpose: a gate ruling or an executed action
can move the record forward, never back. A `state_transition` frame that says
`reopened: true` is different -- it is a named human's recorded decision to
send the record back to caught for re-investigation, and it is honoured as
written. That is how a record is reopened without anyone editing history:
the closure stays on the reel, the reopen follows it. The sentinel's own
`cited` transitions stay monotonic: a re-run that produces a new verdict must
not undo a gate ruling or an executed action already on the chain.
"""

from __future__ import annotations

from typing import Any, Iterable

RANK = {"caught": 0, "cited": 1, "gated": 2, "actioned": 3, "closed": 4, "closed_benign": 4}


def _field(e: Any, name: str, default: Any = None) -> Any:
    if isinstance(e, dict):
        return e.get(name, default)
    return getattr(e, name, default)


def implied_state(kind: str, payload: dict[str, Any]) -> str | None:
    """Which state one ledger frame implies, if any."""
    if kind == "state_transition":
        to = payload.get("to")
        return to if to in RANK else None
    if kind == "policy_check":
        return "gated"            # the gate has ruled on a proposal, allow or deny
    if kind == "action_executed":
        return "actioned"
    if kind == "human_signoff":
        # approve_and_execute records the approval this way; the sign-off
        # command records {incident_id, signed_by} and closes the case.
        return "actioned" if "approved" in payload else "closed"
    return None


def derive_state(base: str, entries: Iterable[Any]) -> dict[str, Any]:
    state = base if base in RANK else "caught"
    basis: list[dict[str, Any]] = []
    for e in entries:
        kind = _field(e, "kind", "")
        payload = _field(e, "payload", {}) or {}
        to = implied_state(kind, payload)
        if to is None:
            continue
        reopened = kind == "state_transition" and bool(payload.get("reopened"))
        if reopened or to == "closed_benign" or RANK[to] > RANK[state]:
            state = to
            basis.append({"seq": _field(e, "seq"), "ts": _field(e, "ts"),
                          "kind": kind, "actor": _field(e, "actor"), "to": to})
    return {"state": state, "base_state": base, "basis": basis}
