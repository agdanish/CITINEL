"""Analyst-supplied images: read by Gemini, corroborated by CITINEL itself.

A SOC runs on logs, but an analyst is handed pictures all day -- a forwarded
phishing email, a ransom note, an alert from a tool nobody integrated. Until
now every one of those had to be retyped by hand or lost. This is the seam
that reads them, and it is the only place in CITINEL where a model looks at
something that is not text.

The important half is not the reading. A model describing a picture is not a
detection: a screenshot has no provenance, no timestamp CITINEL can vouch
for, and nothing stops anyone pasting an image of anything at all. So the
reading is recorded as an OBSERVATION and is never allowed to support a claim.

What makes it worth having is the step after. Every indicator Gemini names is
checked against the incident's OWN findings, deterministically, in this file
-- string matching over raw log lines, no model involved. That produces two
genuinely different things:

    corroborated   the picture names something the record already contains.
                   This is a fact, not a reading: finding indices are cited,
                   and a human can go and look at them.
    unseen         the picture names something the record has never seen.
                   Also a fact, and often the more interesting one -- it is
                   how a screenshot tells a SOC about an asset or a sender
                   its own telemetry never covered.

An analyst pasting a phishing screenshot into an incident and being told
"this IP appears in 47 findings on this record" has learned something
CITINEL could not otherwise tell them, and every part of that sentence is
checkable.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from citinel.connectors.base import EnrichmentCache
from citinel.connectors.gemini import GeminiConnector

#: Indicators shorter than this match too much raw log text to be meaningful.
MIN_INDICATOR_LEN = 4
MAX_INDICATORS = 24
#: Findings scanned per indicator. The whole record, bounded for a huge one.
MAX_SCAN_FINDINGS = 4000


def visual_path(artifacts_dir: Path, incident_id: str) -> Path:
    return artifacts_dir / "visual" / f"{incident_id}.json"


def load_visuals(artifacts_dir: Path, incident_id: str) -> dict[str, Any] | None:
    p = visual_path(artifacts_dir, incident_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _values(node: Any, out: list[str]) -> None:
    """Every scalar VALUE reachable in a finding, ignoring the keys."""
    if isinstance(node, dict):
        for v in node.values():
            _values(v, out)
    elif isinstance(node, (list, tuple, set)):
        for v in node:
            _values(v, out)
    elif node is not None and not isinstance(node, bool):
        out.append(str(node))


def _haystack(incident) -> list[tuple[int, str]]:
    """One lowercased searchable string per finding, with its index.

    Walks the WHOLE finding rather than a hand-listed set of fields. The first
    version named `raw`, but the log line actually lives in `evidence_raw` --
    so an IP present in 43 findings was reported as "never seen in this
    record". A miss here is not a blank space, it is a false statement about
    the record, and naming fields by hand is how that happens.

    Values only, never keys. Fixing that miss by searching the finding's JSON
    text introduced the mirror-image lie: the serialisation contains its own
    field names, so an indicator reading "host" or "detail" matched every
    finding on the record and came back corroborated with a list of indices a
    reader could open and find nothing in. Corroboration is the half of this
    feature that is supposed to be checkable; a hit has to be a hit on content.
    """
    out: list[tuple[int, str]] = []
    for i, f in enumerate(incident.findings[:MAX_SCAN_FINDINGS]):
        vals: list[str] = []
        try:
            _values(f.as_dict() if hasattr(f, "as_dict") else vars(f), vals)
        except Exception:
            vals = [str(getattr(f, k, "")) for k in
                    ("title", "host", "evidence_raw", "detail", "techniques")]
        out.append((i, "\n".join(vals).lower()))
    return out


def corroborate(incident, indicators: list[dict[str, Any]]) -> dict[str, Any]:
    """Check each indicator against the record. No model runs here.

    This is the half a reader can verify: every hit names finding indices
    they can open, and every miss is a plain statement that the record does
    not contain that string.
    """
    hay = _haystack(incident)
    corroborated: list[dict[str, Any]] = []
    unseen: list[dict[str, Any]] = []
    for ind in indicators[:MAX_INDICATORS]:
        if not isinstance(ind, dict):
            continue
        value = str(ind.get("value") or "").strip()
        kind = str(ind.get("type") or "other")[:24]
        if len(value) < MIN_INDICATOR_LEN:
            continue
        needle = value.lower()
        hits = [i for i, text in hay if needle in text]
        row = {"value": value[:200], "type": kind, "finding_count": len(hits),
               "finding_indices": hits[:12]}
        (corroborated if hits else unseen).append(row)
    return {"corroborated": corroborated, "unseen": unseen}


def read_image(incident, image_b64: str, mime_type: str, note: str,
               cache_dir: Path, artifacts_dir: Path, ledger=None,
               connector: GeminiConnector | None = None) -> dict[str, Any]:
    """Read one analyst-supplied image and corroborate what it names."""
    gem = connector or GeminiConnector(EnrichmentCache(cache_dir))
    r = gem.read_evidence(image_b64, mime_type)
    reading = (r.detail or {}).get("reading") or {}

    entry: dict[str, Any] = {
        "status": r.status,
        "at": r.fetched_at,
        "model": (r.detail or {}).get("model", ""),
        "analyst_note": note[:300],
        "kind": "", "summary": "", "looks_malicious": None, "why": "",
        "corroborated": [], "unseen": [],
        "not_evidence": (
            "A model reading a picture is an observation, never evidence. The "
            "image has no provenance CITINEL can vouch for. What IS checkable "
            "is the corroboration below: those finding indices come from this "
            "record's own logs, matched in code with no model involved."
        ),
    }
    if r.status != "ok":
        entry["note"] = r.verdict
    else:
        entry["kind"] = str(reading.get("kind") or "")[:120]
        entry["summary"] = str(reading.get("summary") or "")[:800]
        entry["why"] = str(reading.get("why") or "")[:300]
        mal = reading.get("looks_malicious")
        entry["looks_malicious"] = bool(mal) if isinstance(mal, bool) else None
        found = reading.get("indicators")
        entry.update(corroborate(incident, found if isinstance(found, list) else []))

    stored = load_visuals(artifacts_dir, incident.incident_id) or {
        "incident_id": incident.incident_id, "provider": "gemini", "readings": []}
    stored["readings"] = ([entry] + stored.get("readings", []))[:12]
    out = visual_path(artifacts_dir, incident.incident_id)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(stored, indent=2))

    if ledger is not None and r.status != "not_configured":
        ledger.append(incident.incident_id, "gemini-vision", "tool_call", {
            "check": "analyst_image_read",
            "status": r.status,
            "kind": entry["kind"],
            "indicators_named": len(entry["corroborated"]) + len(entry["unseen"]),
            "corroborated_by_record": len(entry["corroborated"]),
            "unseen_in_record": len(entry["unseen"]),
            "reason": "an analyst-supplied image was read and every indicator it named "
                      "was checked against this record's own findings; the reading is an "
                      "observation, the corroboration is a fact, and neither is evidence",
        })
    return stored
