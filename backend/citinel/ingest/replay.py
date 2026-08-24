"""Chronological replay of extracted BOTS v1 telemetry.

STATE Section 4 makes pre-recorded replay the primary demo mode, guaranteed to
work offline, with live agent calls as garnish rather than the spine
(DEMO-F01). This module turns the raw journal into a time-ordered event stream
CITINEL can play back at a chosen speed.

Extraction is expensive (about 950,000 events across two 40MB journals), so the
result is cached to newline-delimited JSON under data/cache/. The cache is
gitignored: it is derived data, reproducible from the dataset at any time.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from citinel.ingest.splunk_journal import RawEvent, extract, find_journals

# --- timestamp extraction, per event format --------------------------------
_TS_JSON = re.compile(r'"timestamp"\s*:\s*"([^"]+)"')
_TS_WINXML = re.compile(r"SystemTime='([^']+)'")
# Windows classic logs lead with the event time. A stray printable framing
# byte can sit in front of it (observed: "108/10/2016 02:10:16 PM"), so this
# is searched within the head of the record rather than anchored to position 0.
_TS_WINCLASSIC = re.compile(r"(\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}:\d{2} [AP]M)")
# Windows registry records use 24-hour time with milliseconds and no meridiem.
_TS_WINREG = re.compile(r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})\.\d+")
_TS_FORTINET = re.compile(r"\bdate=(\d{4}-\d{2}-\d{2})\s+time=(\d{2}:\d{2}:\d{2})")
_TS_IIS = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")


def _parse_iso(value: str) -> datetime | None:
    v = value.strip().replace("Z", "+00:00")
    # Suricata writes -0600; fromisoformat wants -06:00 on Python < 3.11 rules.
    if re.search(r"[+-]\d{4}$", v):
        v = v[:-5] + v[-5:-2] + ":" + v[-2:]
    try:
        dt = datetime.fromisoformat(v)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def event_timestamp(ev: RawEvent) -> datetime | None:
    """Best-effort event time. Returns None rather than guessing."""
    body = ev.body
    if ev.fmt == "json":
        m = _TS_JSON.search(body)
        return _parse_iso(m.group(1)) if m else None
    if ev.fmt == "winxml":
        m = _TS_WINXML.search(body)
        return _parse_iso(m.group(1)) if m else None
    if ev.fmt == "winclassic":
        m = _TS_WINCLASSIC.search(body[:64])
        if not m:
            return None
        try:
            return datetime.strptime(m.group(1), "%m/%d/%Y %I:%M:%S %p").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            return None
    if ev.fmt == "syslog":
        m = _TS_FORTINET.search(body)
        if not m:
            return None
        return _parse_iso(f"{m.group(1)}T{m.group(2)}+00:00")
    if ev.fmt == "w3c":
        m = _TS_IIS.match(body.strip())
        return _parse_iso(m.group(1).replace(" ", "T") + "+00:00") if m else None
    if ev.fmt == "kv":
        m = _TS_WINREG.search(body[:64])
        if m:
            try:
                return datetime.strptime(m.group(1), "%m/%d/%Y %H:%M:%S").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                return None
        m = _TS_WINCLASSIC.search(body[:64])
        if m:
            try:
                return datetime.strptime(m.group(1), "%m/%d/%Y %I:%M:%S %p").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                return None
    return None


@dataclass
class ReplayStats:
    total: int = 0
    timestamped: int = 0
    undated: int = 0
    earliest: datetime | None = None
    latest: datetime | None = None

    def summary(self) -> str:
        pct = (self.timestamped / self.total * 100) if self.total else 0.0
        span = ""
        if self.earliest and self.latest:
            span = f", spanning {self.earliest.date()} to {self.latest.date()}"
        return (
            f"{self.total:,} events, {self.timestamped:,} timestamped "
            f"({pct:.1f}%), {self.undated:,} undated{span}"
        )


def build_cache(dataset_root: Path, cache_path: Path) -> ReplayStats:
    """Extract, timestamp, sort chronologically, and write a JSONL cache."""
    rows: list[tuple[float, dict]] = []
    stats = ReplayStats()

    for journal in find_journals(dataset_root):
        events, _report = extract(journal, limit=None)
        for ev in events:
            stats.total += 1
            ts = event_timestamp(ev)
            if ts is None:
                stats.undated += 1
                continue
            stats.timestamped += 1
            if stats.earliest is None or ts < stats.earliest:
                stats.earliest = ts
            if stats.latest is None or ts > stats.latest:
                stats.latest = ts
            row = ev.as_dict()
            row["timestamp"] = ts.isoformat()
            rows.append((ts.timestamp(), row))

    rows.sort(key=lambda r: r[0])
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", encoding="utf-8") as fh:
        for _epoch, row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return stats


def stream_cache(cache_path: Path, limit: int | None = None) -> Iterator[dict]:
    """Yield cached events in chronological order."""
    with cache_path.open("r", encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if limit is not None and i >= limit:
                return
            yield json.loads(line)
