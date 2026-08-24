"""Append-only audit ledger: every decision, every tool call, one join key.

Two spec obligations meet here:

* SAFE-F06 / AGT-F06: the audit log records *structured decisions and tool
  calls* -- never model "thinking summaries", which are a summary and not a
  forensic record. Nothing in this module accepts free-form reasoning text as
  an entry payload by design; callers log what was decided and what was done.

* SDD Section 16 finding 4: a mandatory case id propagated through every
  entry, logged as the join key, so the full audit chain for one incident can
  be reconstructed from the case id alone (`entries_for`).

Entries are append-only JSONL. Each entry carries the SHA-256 of the previous
entry, so any in-place edit or deletion breaks `verify_chain`. This is a
standard integrity technique offered as-is; no research claim is attached to
it (the specific tamper-evidence research surveyed in SDD Section 16 did not
survive verification and is deliberately not cited here).

Timestamps are wall-clock at append time: the replayed telemetry is from 2016,
but the *detection* of it happens now, and detect-time -> sign-time is the
interval the regulatory clock and the audit ribbon prove.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

GENESIS = "0" * 64

#: The vocabulary of things that may be recorded. A closed set, on purpose:
#: an entry kind outside it is refused, which keeps "never log thinking
#: summaries" enforceable rather than aspirational.
ENTRY_KINDS = frozenset({
    "incident_opened",
    "state_transition",
    "detection_added",
    "escalation_added",
    "tool_call",
    "decision",
    "policy_check",
    "action_executed",
    "action_rolled_back",
    "draft_generated",
    "human_signoff",
    "note",
})


class LedgerError(Exception):
    pass


def _canonical(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _entry_hash(seq: int, ts: str, case_id: str, actor: str, kind: str,
                payload: dict[str, Any], prev_hash: str) -> str:
    material = f"{seq}|{ts}|{case_id}|{actor}|{kind}|{_canonical(payload)}|{prev_hash}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


@dataclass(slots=True)
class Entry:
    seq: int
    ts: str
    case_id: str
    actor: str
    kind: str
    payload: dict[str, Any]
    prev_hash: str
    entry_hash: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "seq": self.seq, "ts": self.ts, "case_id": self.case_id,
            "actor": self.actor, "kind": self.kind, "payload": self.payload,
            "prev_hash": self.prev_hash, "entry_hash": self.entry_hash,
        }


class AuditLedger:
    """One append-only JSONL file. No update, no delete, no reorder."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._seq, self._tip = self._load_tip()

    def _load_tip(self) -> tuple[int, str]:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return 0, GENESIS
        last = None
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    last = line
        if last is None:
            return 0, GENESIS
        e = json.loads(last)
        return e["seq"], e["entry_hash"]

    def append(self, case_id: str, actor: str, kind: str,
               payload: dict[str, Any]) -> Entry:
        if kind not in ENTRY_KINDS:
            raise LedgerError(f"unknown entry kind: {kind!r}")
        if not case_id:
            raise LedgerError("case_id is mandatory on every entry")
        seq = self._seq + 1
        ts = datetime.now(timezone.utc).isoformat()
        h = _entry_hash(seq, ts, case_id, actor, kind, payload, self._tip)
        entry = Entry(seq=seq, ts=ts, case_id=case_id, actor=actor, kind=kind,
                      payload=payload, prev_hash=self._tip, entry_hash=h)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry.as_dict(), ensure_ascii=False) + "\n")
        self._seq, self._tip = seq, h
        return entry

    def entries(self) -> Iterator[Entry]:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    d = json.loads(line)
                    yield Entry(**d)

    def entries_for(self, case_id: str) -> list[Entry]:
        """Full audit-chain reconstruction from the case id alone (finding 4)."""
        return [e for e in self.entries() if e.case_id == case_id]

    def verify_chain(self) -> tuple[bool, str]:
        """Recompute every hash. Any edit, deletion or reorder breaks it."""
        prev = GENESIS
        expected_seq = 0
        for e in self.entries():
            expected_seq += 1
            if e.seq != expected_seq:
                return False, f"sequence break at entry {e.seq} (expected {expected_seq})"
            if e.prev_hash != prev:
                return False, f"chain break at seq {e.seq}: prev_hash mismatch"
            recomputed = _entry_hash(e.seq, e.ts, e.case_id, e.actor, e.kind,
                                     e.payload, e.prev_hash)
            if recomputed != e.entry_hash:
                return False, f"content tampered at seq {e.seq}: hash mismatch"
            prev = e.entry_hash
        return True, f"chain intact: {expected_seq} entries"
