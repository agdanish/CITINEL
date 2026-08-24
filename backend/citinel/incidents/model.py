"""The incident record: one record, five states.

Deck slide 6's central entity, and the brand hook made literal: an incident
moves Caught -> Cited -> Gated -> Actioned -> Closed, and every transition is
enforced here and recorded in the audit ledger. The tagline is the state
machine (HANDOFF-MEMORY Section 4a; the five-word form).

State meanings:
  CAUGHT    detections/escalations exist under one incident id
  CITED     a verdict exists and every claim cites its evidence   (Step 7)
  GATED     proposed actions have passed the policy gate           (Step 8)
  ACTIONED  gated actions executed (with rollback where promised)  (Step 8)
  CLOSED    human sign-off recorded; drafts exported               (Step 10)

Skipping forward is prohibited except one honest shortcut: an incident that
turns out to be benign may close from any state -- CLOSED_BENIGN records that
the pipeline dismissed it, which is the normal fate of most escalations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class State(str, Enum):
    CAUGHT = "caught"
    CITED = "cited"
    GATED = "gated"
    ACTIONED = "actioned"
    CLOSED = "closed"
    CLOSED_BENIGN = "closed_benign"


#: Legal forward transitions. Anything else raises.
TRANSITIONS: dict[State, frozenset[State]] = {
    State.CAUGHT: frozenset({State.CITED, State.CLOSED_BENIGN}),
    State.CITED: frozenset({State.GATED, State.CLOSED_BENIGN}),
    State.GATED: frozenset({State.ACTIONED, State.CLOSED, State.CLOSED_BENIGN}),
    State.ACTIONED: frozenset({State.CLOSED}),
    State.CLOSED: frozenset(),
    State.CLOSED_BENIGN: frozenset(),
}


class TransitionError(Exception):
    pass


@dataclass
class Finding:
    """One detection or escalation attached to an incident."""

    source: str                 # "sigma" | "anomaly"
    title: str
    level: str                  # sigma level, or "score:<n>" for anomalies
    timestamp: str
    host: str
    techniques: list[str] = field(default_factory=list)
    evidence_raw: str = ""      # the exact log line; what a citation chip opens
    detail: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source, "title": self.title, "level": self.level,
            "timestamp": self.timestamp, "host": self.host,
            "techniques": self.techniques, "evidence_raw": self.evidence_raw,
            "detail": self.detail,
        }


@dataclass
class Incident:
    incident_id: str
    state: State = State.CAUGHT
    opened_ts: str = ""
    first_event_ts: str = ""
    last_event_ts: str = ""
    hosts: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    techniques: list[str] = field(default_factory=list)
    severity: str = "medium"

    def transition(self, to: State) -> State:
        allowed = TRANSITIONS[self.state]
        if to not in allowed:
            raise TransitionError(
                f"{self.incident_id}: illegal transition {self.state.value} -> {to.value} "
                f"(allowed: {sorted(s.value for s in allowed)})"
            )
        self.state = to
        return to

    def add_finding(self, f: Finding) -> None:
        self.findings.append(f)
        if f.host and f.host not in self.hosts:
            self.hosts.append(f.host)
        for t in f.techniques:
            if t not in self.techniques:
                self.techniques.append(t)
        if not self.first_event_ts or f.timestamp < self.first_event_ts:
            self.first_event_ts = f.timestamp
        if f.timestamp > self.last_event_ts:
            self.last_event_ts = f.timestamp

    def as_dict(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "state": self.state.value,
            "opened_ts": self.opened_ts,
            "first_event_ts": self.first_event_ts,
            "last_event_ts": self.last_event_ts,
            "hosts": self.hosts,
            "severity": self.severity,
            "techniques": self.techniques,
            "finding_count": len(self.findings),
            "findings": [f.as_dict() for f in self.findings],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Incident":
        inc = cls(
            incident_id=d["incident_id"],
            state=State(d["state"]),
            opened_ts=d.get("opened_ts", ""),
            first_event_ts=d.get("first_event_ts", ""),
            last_event_ts=d.get("last_event_ts", ""),
            hosts=list(d.get("hosts", [])),
            techniques=list(d.get("techniques", [])),
            severity=d.get("severity", "medium"),
        )
        inc.findings = [Finding(**f) for f in d.get("findings", [])]
        return inc
