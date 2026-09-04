"""Tavily Research: a cited threat brief on the TTP combination an incident showed.

The fifth and deepest Tavily primitive, and the only one that answers a
QUESTION rather than returning pages. Search finds documents about a
technique. Extract reads one of them. Crawl reads a neighbourhood. Map lists
what exists. Research runs several searches of its own, reasons across the
results and returns a report with numbered citations -- which is the right
shape for the one question a CISO actually asks about an incident: "what is
this pattern, and what do people who have seen it before say to do?"

Asynchronous by design. `start` kicks a run off and stores the request id;
`poll` advances it exactly one step per call. Nothing blocks an HTTP worker
waiting for a research run to finish, because that would put the console's
own timeout in charge of whether the answer is allowed to exist at all.

Same line every other external source here respects: a brief is context, not
evidence. It cannot support a claim, move a verdict, or reopen a lane. What
it can do is put the open web's answer, with its sources, next to the
incident -- so a reader can check it rather than take CITINEL's word.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from citinel.connectors.base import EnrichmentCache
from citinel.connectors.enrichment import TavilyConnector

MAX_TECHNIQUES = 6


def brief_path(artifacts_dir: Path, incident_id: str) -> Path:
    return artifacts_dir / "brief" / f"{incident_id}.json"


def load_brief(artifacts_dir: Path, incident_id: str) -> dict[str, Any] | None:
    p = brief_path(artifacts_dir, incident_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _save(artifacts_dir: Path, incident_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    p = brief_path(artifacts_dir, incident_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2))
    return payload


def compose_question(incident, verdict: dict[str, Any] | None) -> str:
    """The question is built from what the investigation actually found, not
    from the incident id -- a brief about "INC-0417" would be worthless."""
    techniques: list[str] = []
    for stage in ((verdict or {}).get("correlation") or {}).get("stages", []):
        t = stage.get("technique_id")
        if t and t not in techniques:
            techniques.append(t)
    for t in getattr(incident, "techniques", [])[:MAX_TECHNIQUES]:
        if t not in techniques:
            techniques.append(t)
    techniques = techniques[:MAX_TECHNIQUES]
    titles: list[str] = []
    for f in getattr(incident, "findings", [])[:60]:
        if f.title not in titles:
            titles.append(f.title)
        if len(titles) >= 4:
            break
    return (
        "A security operations centre at an Indian cooperative bank has an incident "
        f"showing these MITRE ATT&CK techniques together: {', '.join(techniques) or 'unclassified'}. "
        f"The detections that fired were: {'; '.join(titles) or 'anomaly-only'}. "
        "What attack pattern or campaign does this combination typically indicate, "
        "what do incident responders who have handled it recommend doing first, and "
        "what should this bank check for that it may not have looked at yet? "
        "Cite your sources."
    )


def start_brief(incident, verdict: dict[str, Any] | None, cache_dir: Path,
                artifacts_dir: Path, connector: TavilyConnector | None = None) -> dict[str, Any]:
    tav = connector or TavilyConnector(EnrichmentCache(cache_dir))
    question = compose_question(incident, verdict)
    request_id, note = tav.research_start(question)
    payload = {
        "incident_id": incident.incident_id,
        "provider": "tavily",
        "primitive": "research",
        "question": question,
        "request_id": request_id,
        "status": "pending" if request_id else "error",
        "content": "", "sources": [], "note": note,
        "not_evidence": (
            "A brief is context, never evidence. Nothing in it can support a "
            "claim, change the verdict, or reopen the triage lane: the citation "
            "contract still points only at the incident's own findings."
        ),
    }
    return _save(artifacts_dir, incident.incident_id, payload)


def poll_brief(incident_id: str, cache_dir: Path, artifacts_dir: Path,
               connector: TavilyConnector | None = None) -> dict[str, Any] | None:
    """Advance a pending brief by one step. Returns None if none was started."""
    stored = load_brief(artifacts_dir, incident_id)
    if stored is None:
        return None
    if stored.get("status") != "pending" or not stored.get("request_id"):
        return stored
    tav = connector or TavilyConnector(EnrichmentCache(cache_dir))
    r = tav.research_poll(str(stored["request_id"]))
    state = r.get("status")
    if state == "pending":
        return stored
    stored["status"] = state or "error"
    stored["content"] = str(r.get("content") or "")[:6000]
    stored["sources"] = r.get("sources") or []
    stored["response_time"] = r.get("response_time")
    if r.get("detail"):
        stored["note"] = r["detail"]
    return _save(artifacts_dir, incident_id, stored)
