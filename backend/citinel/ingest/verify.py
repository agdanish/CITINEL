"""Measure telemetry extraction against Splunk's own recorded event counts.

Every BOTS bucket ships a `SourceTypes.data` file holding Splunk's per-
sourcetype event totals. That is independent ground truth: it was written by
Splunk at index time, not by CITINEL. Comparing extraction against it turns
"the parser looks right" into a number that can be checked, which is what this
repository's evidence discipline requires of any claim.

Run via:  citinel telemetry verify
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from citinel.ingest.splunk_journal import declared_counts, extract, find_journals

# CITINEL derives its own event classes from content. This maps them back onto
# Splunk's sourcetype names purely so recovery can be scored per sourcetype.
_FOLD: dict[str, str] = {
    "sysmon": "XmlWinEventLog:Microsoft-Windows-Sysmon/Operational",
    "winevent:security": "WinEventLog:Security",
    "winevent:system": "WinEventLog:System",
    "winevent:application": "WinEventLog:Application",
    "winregistry": "WinRegistry",
    "fortinet:traffic": "fgt_traffic",
    "fortinet:utm": "fgt_utm",
    "iis": "iis",
}


def fold(event_class: str) -> str:
    if event_class in _FOLD:
        return _FOLD[event_class]
    if event_class.startswith("suricata:"):
        return "suricata"
    if event_class.startswith("fortinet:"):
        return "fgt_event"
    return event_class  # stream:* already matches Splunk's naming


@dataclass
class BucketResult:
    name: str
    extracted: int
    declared: int
    per_sourcetype: list[tuple[str, int, int]]  # (sourcetype, got, declared)

    @property
    def recovery(self) -> float:
        return (self.extracted / self.declared * 100) if self.declared else 0.0


def verify(dataset_root: Path) -> list[BucketResult]:
    results: list[BucketResult] = []
    for journal in find_journals(dataset_root):
        bucket = journal.parent.parent
        _events, report = extract(journal, limit=0)
        declared = declared_counts(bucket)

        folded: dict[str, int] = {}
        for cls, n in report.by_class.items():
            key = fold(cls)
            folded[key] = folded.get(key, 0) + n

        rows = [
            (st, folded.get(st, 0), want)
            for st, want in sorted(declared.items(), key=lambda kv: -kv[1])
        ]
        results.append(
            BucketResult(
                name=bucket.name,
                extracted=report.extracted,
                declared=sum(declared.values()),
                per_sourcetype=rows,
            )
        )
    return results
