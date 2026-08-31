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


class LedgerSink:
    """An optional external witness that receives every appended entry.

    Why this seam exists, stated precisely, because the security property is
    narrow and easy to overclaim:

    A self-contained hash chain detects *edits*. Change one entry and every
    subsequent hash stops matching, which `verify_chain` catches. What it
    cannot catch is *wholesale replacement*: an attacker who rewrites the
    entire file and recomputes every hash from GENESIS produces a chain that
    verifies perfectly. The chain proves internal consistency, not that it is
    the same chain that existed yesterday.

    An external witness closes exactly that gap and nothing else. A copy held
    somewhere the attacker does not control cannot be retroactively rewritten
    with the local file, so comparing the local chain head against the
    witness's head detects a replacement the local check is blind to.

    Non-negotiable: the local ledger stays canonical (SDD 15.3's "fulfill, not
    duplicate"). A sink is a witness, never the record. `append` therefore
    swallows every sink failure -- a bank's SOC must not stop recording
    because a third-party service is down, and a mirror that could block an
    append would be a liability rather than a safeguard.
    """

    def record(self, entry: "Entry") -> None:  # pragma: no cover - interface
        raise NotImplementedError


class NullSink(LedgerSink):
    """Default. No external witness; the local chain stands alone."""

    def record(self, entry: "Entry") -> None:
        return None


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

    def __init__(self, path: Path, sink: LedgerSink | None = None) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._seq, self._tip = self._load_tip()
        self.sink = sink or NullSink()
        #: Sink failures are counted, not raised -- so "the witness is down"
        #: is observable rather than silent, without ever blocking an append.
        self.sink_failures = 0

    @property
    def head(self) -> str:
        """The current chain head hash. What an external witness compares."""
        return self._tip

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
        # The local write is committed above and is canonical. Everything past
        # this point is best-effort: a witness that raises, hangs or is simply
        # absent must not turn a recorded decision into an unrecorded one.
        try:
            self.sink.record(entry)
        except Exception:
            self.sink_failures += 1
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
        """Recompute every hash. Any edit, deletion or reorder breaks it.

        A ledger file that does not exist is NOT "intact" -- it is absent, and
        those are different facts. Returning True here would be a fabricated
        verification: the caller asked whether the chain verifies, and the
        honest answer for a missing file is "there is no chain to verify," not
        a green checkmark. This matters because a missing data directory in a
        fresh deployment used to surface as `{"intact": true, "chain intact: 0
        entries"}` -- an integrity claim the system had not earned, on the one
        endpoint whose entire purpose is proving integrity.

        An empty-but-present ledger is genuinely, trivially intact and still
        returns True: nothing has been written, nothing has been tampered.
        """
        if not self.path.exists():
            return False, (f"no ledger at {self.path}: nothing to verify "
                           "(this is absence, not integrity)")
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
