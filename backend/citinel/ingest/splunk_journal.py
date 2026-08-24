"""Extract raw events from Splunk journal.gz files without Splunk.

CITINEL's demo telemetry is Splunk BOTS v1 (CC0), which ships as Splunk index
buckets rather than portable logs (DEMO-F01). `rawdata/journal.gz` decompresses
with standard gzip, but the resulting stream interleaves raw event text with a
binary framing format that Splunk does not publicly specify.

Two design decisions follow from that, both chosen so extraction quality is
*measurable* rather than assumed:

1. Every payload is validated by parsing it. JSON is parsed with `raw_decode`,
   which reports where the object ends and therefore trims framing bytes that
   happen to fall in the printable range. Windows XML must close its own tag.
   Classic Windows and syslog records must carry their own structural markers.
   Anything that fails is counted and reported, never silently dropped.

2. Sourcetype is derived from event CONTENT, not from the framing. The framing
   declares sourcetypes in a dictionary table at slice boundaries, not per
   event, so position-based attribution is wrong -- an earlier version of this
   module attributed 228,844 events to `nessus:scan`, a sourcetype that the
   bucket's own SourceTypes.data records as holding 65. Content-derived labels
   can be checked against those recorded counts; positional ones cannot.

Recovery is verified against each bucket's SourceTypes.data, which is Splunk's
own per-sourcetype event count. See `verify.py`.
"""

from __future__ import annotations

import gzip
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

# Payload candidates. Newlines are INCLUDED: classic Windows events are
# multi-line, and excluding \n shatters one event into a dozen fragments.
_RUN = re.compile(rb"[\x20-\x7e\t\r\n]{40,}")

# Leading framing bytes that land in the printable range and precede a payload.
_LEAD = re.compile(r"^[^\{\<\*\dA-Za-z]+")

_IIS = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \S+ (GET|POST|HEAD|PUT|DELETE|OPTIONS|PROPFIND) "
)

_DECODER = json.JSONDecoder()


# Splunk Stream subtypes, keyed off markers the records actually carry rather
# than guessed from field presence alone. `protoid` marks a transport-level IP
# summary; `nt_status` is an SMB response code; `app` names the application
# protocol the sniffer identified.
_STREAM_APPS = {
    "http", "smb", "dns", "ldap", "mapi", "icmp", "snmp", "sip", "ssl", "ssh",
    "msrpc", "krb5", "netbios", "tcp", "udp",
}


def _stream_subtype(obj: dict) -> str:
    if "protoid" in obj:
        return "ip"
    if "nt_status" in obj or "smb_command" in obj:
        return "smb"
    if "http_method" in obj or "uri_path" in obj or "site" in obj:
        return "http"
    if "query" in obj or "answer" in obj or "query_type" in obj:
        return "dns"
    app = str(obj.get("app", "")).lower()
    if app in _STREAM_APPS:
        return app
    return "other"


@dataclass(slots=True)
class RawEvent:
    """One event as Splunk stored it, before any CITINEL normalization."""

    body: str
    event_class: str      # CITINEL-derived class, from content
    fmt: str              # json | winxml | winclassic | syslog | kv
    offset: int

    def as_dict(self) -> dict:
        return {
            "body": self.body,
            "event_class": self.event_class,
            "format": self.fmt,
            "offset": self.offset,
        }


@dataclass
class ExtractionReport:
    runs_scanned: int = 0
    extracted: int = 0
    rejected: int = 0
    by_class: dict[str, int] = field(default_factory=dict)
    reject_samples: list[str] = field(default_factory=list)

    def summary(self) -> str:
        pct = (self.rejected / self.runs_scanned * 100) if self.runs_scanned else 0.0
        return (
            f"{self.extracted:,} events extracted, "
            f"{self.rejected:,} runs rejected ({pct:.2f}% of {self.runs_scanned:,} scanned)"
        )


def _classify(raw: str) -> tuple[str, str, str] | None:
    """Return (event_class, format, cleaned_body), or None if it does not validate."""
    s = _LEAD.sub("", raw).strip()
    if len(s) < 40:
        return None

    # A leading '<' is only meaningful for Windows event XML. On anything else
    # it is a framing byte sitting in front of the real payload -- Splunk
    # Stream records arrive as `<{"endtime":...`. Strip it so they reach the
    # JSON branch below.
    if s.startswith("<") and not s.startswith("<Event"):
        s = s.lstrip("<").lstrip()
        if len(s) < 40:
            return None

    # --- JSON: suricata alerts and Splunk Stream network records -----------
    if s[0] == "{":
        try:
            obj, end = _DECODER.raw_decode(s)
        except ValueError:
            return None
        body = s[:end]
        if not isinstance(obj, dict):
            return None
        if "event_type" in obj:
            return f"suricata:{obj['event_type']}", "json", body
        if "endtime" in obj or "connection" in obj:
            return f"stream:{_stream_subtype(obj)}", "json", body
        return "json:other", "json", body

    # --- Windows event XML (Sysmon) ----------------------------------------
    if s.startswith("<Event"):
        close = s.rfind("</Event>")
        if close == -1:
            return None
        body = s[: close + len("</Event>")]
        if "Microsoft-Windows-Sysmon" in body:
            return "sysmon", "winxml", body
        if "Microsoft-Windows-Security-Auditing" in body:
            return "winevent:security", "winxml", body
        return "winevent:xml", "winxml", body

    # --- classic multi-line Windows event log --------------------------------
    if "LogName=" in s and "ComputerName=" in s:
        m = re.search(r"LogName=(\w+)", s)
        log = m.group(1).lower() if m else "unknown"
        return f"winevent:{log}", "winclassic", s

    # --- Windows registry ----------------------------------------------------
    if "key_path=" in s:
        return "winregistry", "kv", s

    # --- IIS W3C extended log format ---------------------------------------
    # `2016-08-10 20:00:00 192.168.250.70 GET /joomla/ ...` - space delimited,
    # date first, then an IP and an HTTP verb.
    if _IIS.match(s):
        return "iis", "w3c", s

    # --- Fortinet syslog -----------------------------------------------------
    if "devname=" in s and "logid=" in s:
        m = re.search(r"\btype=(\w+)", s)
        return f"fortinet:{m.group(1) if m else 'event'}", "syslog", s

    return None


def extract(
    path: Path, limit: int | None = None
) -> tuple[list[RawEvent], ExtractionReport]:
    """Extract validated events from one journal.gz."""
    with gzip.open(path, "rb") as fh:
        data = fh.read()

    report = ExtractionReport()
    events: list[RawEvent] = []

    for m in _RUN.finditer(data):
        report.runs_scanned += 1
        result = _classify(m.group().decode("utf-8", "replace"))
        if result is None:
            report.rejected += 1
            if len(report.reject_samples) < 8:
                sample = m.group()[:150].decode("utf-8", "replace")
                if len(sample) > 60:
                    report.reject_samples.append(sample)
            continue

        cls, fmt, body = result
        report.extracted += 1
        report.by_class[cls] = report.by_class.get(cls, 0) + 1
        if limit is None or len(events) < limit:
            events.append(RawEvent(body=body, event_class=cls, fmt=fmt, offset=m.start()))

    return events, report


def find_journals(root: Path) -> list[Path]:
    """Locate every rawdata/journal.gz beneath a BOTS dataset directory."""
    return sorted(root.rglob("rawdata/journal.gz"))


def declared_counts(bucket_dir: Path) -> dict[str, int]:
    """Splunk's own per-sourcetype event counts, from the bucket's metadata.

    This is the ground truth extraction is measured against.
    """
    f = bucket_dir / "SourceTypes.data"
    counts: dict[str, int] = {}
    if not f.exists():
        return counts
    for line in f.read_text(errors="replace").splitlines():
        parts = line.split("\t")
        if len(parts) < 3 or parts[0] == "0":
            continue
        name = parts[1].replace("sourcetype::", "").strip()
        try:
            counts[name] = int(parts[2].strip())
        except ValueError:
            continue
    return counts
