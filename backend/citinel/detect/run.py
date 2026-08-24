"""Run the deterministic detection layer over the replay corpus.

Produces the detections cache downstream stages consume: each hit carries the
rule's identity, level, ATT&CK techniques, and -- most importantly -- the exact
raw log line that fired it, with its native fields. That raw line is what the
glass-box UI's citation chips open (UX-F20): the evidence is captured at
detection time, not reconstructed later.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from citinel.detect.fields import native_fields
from citinel.detect.sigma_engine import SigmaEngine, event_logsources


@dataclass
class DetectReport:
    events: int = 0
    events_hit: int = 0
    detections: int = 0
    by_rule: dict[str, int] = field(default_factory=dict)
    by_level: dict[str, int] = field(default_factory=dict)

    def summary(self) -> str:
        pct = (self.events_hit / self.events * 100) if self.events else 0.0
        return (
            f"{self.events:,} events -> {self.events_hit:,} matched ({pct:.3f}%), "
            f"{self.detections:,} detections from {len(self.by_rule)} distinct rules"
        )


def run_detection(
    rules_root: Path,
    replay_cache: Path,
    out_path: Path,
    limit: int | None = None,
) -> DetectReport:
    from citinel.ingest.replay import stream_cache

    engine = SigmaEngine()
    engine.load(rules_root)

    # Candidate rule lists depend only on (event_class, dispatch key), so they
    # are computed once per key. This is what makes the run tractable.
    cand_cache: dict = {}

    def candidates(cls: str, fields: dict) -> list:
        if cls == "sysmon":
            key = (cls, fields.get("_EventID"))
        elif cls == "winevent:security":
            key = (cls, fields.get("EventCode"))
        else:
            key = (cls, None)
        if key not in cand_cache:
            cand_cache[key] = engine.rules_for(event_logsources(cls, fields))
        return cand_cache[key]

    report = DetectReport()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as out:
        for ev in stream_cache(replay_cache, limit=limit):
            report.events += 1
            cls = ev["event_class"]
            fields = native_fields(cls, ev["body"])
            if not fields:
                continue
            cands = candidates(cls, fields)
            if not cands:
                continue
            matched = engine.match(fields, ev["body"], cands)
            if not matched:
                continue
            report.events_hit += 1
            for cr in matched:
                report.detections += 1
                report.by_rule[cr.title] = report.by_rule.get(cr.title, 0) + 1
                report.by_level[cr.level] = report.by_level.get(cr.level, 0) + 1
                out.write(json.dumps({
                    "rule_id": cr.rule_id,
                    "rule_title": cr.title,
                    "level": cr.level,
                    "techniques": cr.techniques,
                    "timestamp": ev.get("timestamp"),
                    "event_class": cls,
                    "host": fields.get("Computer") or fields.get("ComputerName") or "",
                    "evidence": {
                        # The exact raw line, verbatim. This is the citation.
                        "raw": ev["body"],
                        "native_fields": {
                            k: v for k, v in fields.items()
                            if k in ("Image", "CommandLine", "ParentImage",
                                     "ParentCommandLine", "User", "EventCode",
                                     "_EventID", "TargetFilename", "TargetObject",
                                     "cs-uri-stem", "cs-uri-query", "c-ip")
                            and v
                        },
                    },
                }, ensure_ascii=False) + "\n")

    return report
