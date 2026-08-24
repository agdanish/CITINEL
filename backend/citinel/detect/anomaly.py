"""Statistical anomaly scoring: the second deterministic gate before the swarm.

SDD Section 14 item 2 (verified against a published agentic-SOC architecture,
arXiv:2603.23966) specifies an explicit statistical pre-filter ahead of the
agent layer: only events with a high priority score are forwarded, cutting
both cost and hallucination risk by restricting what ever reaches the LLM.

Design rules this module obeys:

  * Deterministic. Counting, set membership and fixed thresholds only. No
    model, no randomness. The same corpus always produces the same queue.
  * Explainable. Every score decomposes into named reasons carrying the
    actual numbers ("image seen 1x in 945,472 events"), because the scorer's
    reasons become evidence the glass-box UI must be able to show.
  * Aggregated. Escalations are grouped by (host, kind, key) so a process
    that launches 400 times yields one queue entry with count=400, not 400
    entries. The queue must stay reviewable by a human.

Honest limitation, stated rather than hidden: BOTS v1 is an attack-heavy
corpus with a thin "normal" baseline, so population rarity here is rarity
within an attack dataset, not rarity against months of clean bank traffic.
The mechanism is what matters; production baselines would be richer.
"""

from __future__ import annotations

import ipaddress
import json
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from citinel.detect.fields import native_fields

# --- thresholds (fixed, visible, deliberate) --------------------------------

ESCALATE_AT = 0.7          # total score at or above this enters the queue
RARE_ABS = 5               # population count at or below this is "rare"
SINGLETON = 1              # population count of exactly one is "unique"
BURST_WINDOW_S = 300       # failed-logon burst window
BURST_COUNT = 5            # failures within the window to call it a burst

#: Filesystem locations a bank workstation's processes should rarely launch
#: from. Deterministic substring checks, lowercase.
SUSPECT_PATHS = (
    "\\temp\\", "\\tmp\\", "\\appdata\\local\\temp", "\\downloads\\",
    "\\users\\public\\", "\\programdata\\", "\\recycler", "$recycle.bin",
)

#: Extensions that should never be the image of a launched process. A payload
#: masquerading as a temp or media file executing is unambiguous on its own.
NON_EXEC_EXTENSIONS = (
    ".tmp", ".dat", ".txt", ".log", ".jpg", ".jpeg", ".png", ".gif",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
)

#: Registry autorun locations: writes here are persistence attempts.
AUTORUN_KEYS = (
    "\\currentversion\\run", "\\currentversion\\runonce",
    "\\winlogon\\shell", "\\winlogon\\userinit",
)


def _is_external(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip).is_global
    except ValueError:
        return False


# --- pass 1: population frequencies ----------------------------------------

@dataclass
class Population:
    """Frequency baselines over the whole stream. Pass 1 output."""

    events: int = 0
    image: Counter = field(default_factory=Counter)          # process path
    pair: Counter = field(default_factory=Counter)           # (parent, image)
    host_dest: Counter = field(default_factory=Counter)      # (host, dest ip)
    dport: Counter = field(default_factory=Counter)          # destination port


def build_population(replay_cache: Path) -> Population:
    from citinel.ingest.replay import stream_cache

    pop = Population()
    for ev in stream_cache(replay_cache):
        pop.events += 1
        cls = ev["event_class"]
        if cls == "sysmon":
            f = native_fields(cls, ev["body"])
            eid = f.get("_EventID")
            if eid == "1":
                img = (f.get("Image") or "").lower()
                if img:
                    pop.image[img] += 1
                    parent = (f.get("ParentImage") or "").lower()
                    if parent:
                        pop.pair[(parent, img)] += 1
            elif eid == "3":
                host = (f.get("Computer") or "").lower()
                dip = f.get("DestinationIp") or ""
                if host and dip:
                    pop.host_dest[(host, dip)] += 1
                dport = f.get("DestinationPort") or ""
                if dport:
                    pop.dport[dport] += 1
        elif cls == "winevent:security":
            f = native_fields(cls, ev["body"])
            if f.get("EventCode") == "4688":
                img = (f.get("NewProcessName") or "").lower()
                if img:
                    pop.image[img] += 1
    return pop


# --- pass 2: chronological scoring ------------------------------------------

@dataclass
class Reason:
    feature: str
    detail: str
    contribution: float

    def as_dict(self) -> dict:
        return {"feature": self.feature, "detail": self.detail,
                "contribution": self.contribution}


def _rarity(count: int, total: int, feature: str, what: str) -> Reason | None:
    if count <= SINGLETON:
        return Reason(feature, f"{what} seen {count}x in {total:,} events", 0.7)
    if count <= RARE_ABS:
        return Reason(feature, f"{what} seen only {count}x in {total:,} events", 0.4)
    return None


def _net_rarity(count: int, total: int, feature: str, what: str) -> Reason | None:
    """Network rarity on a deliberately weaker scale than process rarity.

    A first run of this scorer used the process scale for network features and
    produced 10,141 network escalations -- re-flooding the queue the gate
    exists to protect. In a corpus with 16,552 distinct host->dest pairs over
    15 days, a singleton pair is normal, not suspicious. On this scale no
    single network signal can cross ESCALATE_AT alone; escalation requires
    corroboration (e.g. never-seen destination AND never-seen port).
    """
    if count <= SINGLETON:
        return Reason(feature, f"{what} seen {count}x in {total:,} events", 0.4)
    if count <= RARE_ABS:
        return Reason(feature, f"{what} seen only {count}x in {total:,} events", 0.25)
    return None


@dataclass
class Escalation:
    kind: str
    host: str
    key: str
    score: float
    reasons: list[Reason]
    count: int = 1
    first_ts: str = ""
    last_ts: str = ""
    exemplar_raw: str = ""

    def as_dict(self) -> dict:
        return {
            "kind": self.kind, "host": self.host, "key": self.key,
            "score": round(self.score, 3),
            "reasons": [r.as_dict() for r in self.reasons],
            "count": self.count, "first_ts": self.first_ts,
            "last_ts": self.last_ts, "exemplar_raw": self.exemplar_raw,
        }


@dataclass
class AnomalyReport:
    events: int = 0
    scored: int = 0
    escalations: int = 0
    by_kind: dict[str, int] = field(default_factory=dict)

    def summary(self) -> str:
        return (
            f"{self.events:,} events, {self.scored:,} scored, "
            f"{self.escalations:,} aggregated escalations "
            f"({', '.join(f'{k}={v}' for k, v in sorted(self.by_kind.items()))})"
        )


def score_stream(replay_cache: Path, pop: Population, out_path: Path) -> AnomalyReport:
    from citinel.ingest.replay import stream_cache

    report = AnomalyReport()
    queue: dict[tuple, Escalation] = {}
    seen_pairs: set[tuple] = set()          # first-seen (host, parent, image)
    seen_dests: set[tuple] = set()          # first-seen (host, dest)
    logon_fails: dict[tuple, deque] = defaultdict(deque)  # (host, account) -> times

    NOVELTY_FEATURES = {"proc_rarity", "pair_rarity", "first_seen_pair"}
    NOVELTY_CAP = 0.7

    def escalate(kind: str, host: str, key: str, ts: str, raw: str,
                 reasons: list[Reason]) -> None:
        # proc_rarity, pair_rarity and first_seen_pair all derive from the same
        # underlying fact ("never seen before"), so summing them double-counts
        # novelty: one boot's worth of ordinary startup processes outscored
        # malware in a suspect directory in the first run of this scorer.
        # Correlated novelty is capped; independent signals add on top.
        novelty = sum(r.contribution for r in reasons if r.feature in NOVELTY_FEATURES)
        other = sum(r.contribution for r in reasons if r.feature not in NOVELTY_FEATURES)
        total = min(novelty, NOVELTY_CAP) + other
        if total < ESCALATE_AT:
            return
        qk = (kind, host, key)
        if qk in queue:
            e = queue[qk]
            e.count += 1
            e.last_ts = ts
            e.score = max(e.score, total)
        else:
            queue[qk] = Escalation(kind=kind, host=host, key=key, score=total,
                                   reasons=reasons, first_ts=ts, last_ts=ts,
                                   exemplar_raw=raw)

    for ev in stream_cache(replay_cache):
        report.events += 1
        cls = ev["event_class"]
        ts = ev.get("timestamp", "")

        if cls == "sysmon":
            f = native_fields(cls, ev["body"])
            eid = f.get("_EventID")

            if eid == "1":
                report.scored += 1
                host = (f.get("Computer") or "").lower()
                img = (f.get("Image") or "").lower()
                parent = (f.get("ParentImage") or "").lower()
                reasons: list[Reason] = []
                r = _rarity(pop.image.get(img, 0), pop.events, "proc_rarity",
                            f"image {img!r}")
                if r: reasons.append(r)
                if parent:
                    r = _rarity(pop.pair.get((parent, img), 0), pop.events,
                                "pair_rarity", f"parent->child {parent!r} -> {img!r}")
                    if r: reasons.append(r)
                    pk = (host, parent, img)
                    if pk not in seen_pairs:
                        seen_pairs.add(pk)
                        # novelty alone is weak; it only tips borderline cases
                        reasons.append(Reason(
                            "first_seen_pair",
                            f"first time this parent->child pair on {host}", 0.2))
                if any(s in img for s in SUSPECT_PATHS):
                    reasons.append(Reason(
                        "suspect_path", f"image runs from a suspect location: {img}", 0.6))
                if img.endswith(NON_EXEC_EXTENSIONS):
                    reasons.append(Reason(
                        "exec_extension_mismatch",
                        f"process image has a non-executable extension: {img}", 0.6))
                escalate("process", host, img, ts, ev["body"], reasons)

            elif eid == "3":
                report.scored += 1
                host = (f.get("Computer") or "").lower()
                dip = f.get("DestinationIp") or ""
                dport = f.get("DestinationPort") or ""
                reasons = []
                r = _net_rarity(pop.host_dest.get((host, dip), 0), pop.events,
                                "dest_rarity", f"connection {host} -> {dip}")
                if r: reasons.append(r)
                r = _net_rarity(pop.dport.get(dport, 0), pop.events,
                                "port_rarity", f"destination port {dport}")
                if r: reasons.append(r)
                if _is_external(dip):
                    reasons.append(Reason("external_dest",
                                          f"destination {dip} is internet-routable", 0.2))
                dk = (host, dip)
                if dk not in seen_dests:
                    seen_dests.add(dk)
                escalate("network", host, f"{dip}:{dport}", ts, ev["body"], reasons)

        elif cls == "winevent:security":
            f = native_fields(cls, ev["body"])
            code = f.get("EventCode")

            if code == "4625":
                report.scored += 1
                host = (f.get("ComputerName") or "").lower()
                account = (f.get("AccountName") or f.get("SubjectUserName") or "?").lower()
                try:
                    t = datetime.fromisoformat(ts).timestamp()
                except ValueError:
                    continue
                dq = logon_fails[(host, account)]
                dq.append(t)
                while dq and t - dq[0] > BURST_WINDOW_S:
                    dq.popleft()
                if len(dq) >= BURST_COUNT:
                    escalate("auth_burst", host, account, ts, ev["body"], [Reason(
                        "failed_logon_burst",
                        f"{len(dq)} failed logons for {account!r} on {host} "
                        f"within {BURST_WINDOW_S}s", 0.8)])

            elif code == "4688":
                report.scored += 1
                host = (f.get("ComputerName") or "").lower()
                img = (f.get("NewProcessName") or "").lower()
                reasons = []
                r = _rarity(pop.image.get(img, 0), pop.events, "proc_rarity",
                            f"image {img!r}")
                if r: reasons.append(r)
                if any(s in img for s in SUSPECT_PATHS):
                    reasons.append(Reason(
                        "suspect_path", f"image runs from a suspect location: {img}", 0.6))
                if img.endswith(NON_EXEC_EXTENSIONS):
                    reasons.append(Reason(
                        "exec_extension_mismatch",
                        f"process image has a non-executable extension: {img}", 0.6))
                escalate("process", host, img, ts, ev["body"], reasons)

        elif cls == "winregistry":
            f = native_fields(cls, ev["body"])
            key_path = (f.get("key_path") or "").lower()
            if any(k in key_path for k in AUTORUN_KEYS):
                report.scored += 1
                host = ""
                proc = (f.get("process_image") or "").lower()
                escalate("persistence", host, key_path, ts, ev["body"], [Reason(
                    "autorun_write",
                    f"registry write to autorun location {key_path} by {proc or 'unknown'}",
                    0.8)])

    # persist, highest score first
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(queue.values(), key=lambda e: -e.score)
    with out_path.open("w", encoding="utf-8") as fh:
        for e in ordered:
            fh.write(json.dumps(e.as_dict(), ensure_ascii=False) + "\n")

    report.escalations = len(ordered)
    for e in ordered:
        report.by_kind[e.kind] = report.by_kind.get(e.kind, 0) + 1
    return report
