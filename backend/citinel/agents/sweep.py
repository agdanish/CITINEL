"""Persist one Gemini wide-lens sweep per incident, beside the swarm result.

Mirrors `agents/context.py`: the connector does the call, this module decides
what is worth keeping, clamps every field the console will render, writes it
to `<incidents_dir>/sweep/<id>.json`, and records that it happened on the
ledger. Re-reading a sweep costs nothing; running one costs one API call.

`not_evidence` is stamped into the payload for the same reason Tavily's
context carries it: a reader (or a judge) should be able to see from the data
itself that nothing here is allowed to support a claim.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from citinel.connectors.base import EnrichmentCache
from citinel.connectors.gemini import GeminiConnector

_RISKS = ("low", "medium", "high")
_WHERE = ("inside", "outside", "both")


def sweep_path(incidents_dir: Path, incident_id: str) -> Path:
    return incidents_dir / "sweep" / f"{incident_id}.json"


def load_sweep(incidents_dir: Path, incident_id: str) -> dict[str, Any] | None:
    p = sweep_path(incidents_dir, incident_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def run_sweep(incident, examined: int, cache_dir: Path, incidents_dir: Path,
              ledger=None, connector: GeminiConnector | None = None) -> dict[str, Any]:
    """Sweep every finding, keep the clamped result, record that it ran."""
    gem = connector or GeminiConnector(EnrichmentCache(cache_dir))
    r = gem.wide_sweep(incident, examined)
    d = r.detail or {}
    raw = d.get("sweep") or {}

    payload: dict[str, Any] = {
        "incident_id": incident.incident_id,
        "provider": "gemini",
        "model": d.get("model", ""),
        "status": r.status,
        "fetched_at": r.fetched_at,
        "findings_total": d.get("findings_total", len(incident.findings)),
        "findings_examined": d.get("findings_examined", examined),
        "findings_swept": d.get("findings_swept", 0),
        "truncated_sweep": bool(d.get("truncated_sweep")),
        "summary": "", "clusters": [], "only_outside_window": [],
        "blind_spot_risk": "", "blind_spot_reason": "",
        "not_evidence": (
            "A sweep is context, never evidence. Nothing here can support a "
            "claim, change the verdict, or reopen the triage lane: the "
            "citation contract still points only at the incident's own "
            "findings."
        ),
    }
    if r.status != "ok":
        payload["note"] = r.verdict
    else:
        payload["summary"] = str(raw.get("summary") or "")[:900]
        risk = str(raw.get("blind_spot_risk") or "").strip().lower()
        payload["blind_spot_risk"] = risk if risk in _RISKS else "unparsed"
        payload["blind_spot_reason"] = str(raw.get("blind_spot_reason") or "")[:300]
        for c in (raw.get("clusters") or [])[:12]:
            if not isinstance(c, dict):
                continue
            where = str(c.get("where") or "").strip().lower()
            payload["clusters"].append({
                "pattern": str(c.get("pattern") or "")[:160],
                "count": _int(c.get("count")),
                "hosts": [str(h)[:60] for h in (c.get("hosts") or [])[:8]],
                "where": where if where in _WHERE else "unparsed",
                "why": str(c.get("why") or "")[:240],
            })
        for o in (raw.get("only_outside_window") or [])[:12]:
            if not isinstance(o, dict):
                continue
            payload["only_outside_window"].append({
                "what": str(o.get("what") or "")[:160],
                "count": _int(o.get("count")),
                "why": str(o.get("why") or "")[:240],
            })

    out = sweep_path(incidents_dir, incident.incident_id)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))

    if ledger is not None and r.status not in ("not_configured",):
        ledger.append(incident.incident_id, "gemini-sweep", "tool_call", {
            "check": "wide_lens_sweep",
            "status": r.status,
            "model": payload["model"],
            "findings_total": payload["findings_total"],
            "findings_examined": payload["findings_examined"],
            "findings_swept": payload["findings_swept"],
            "blind_spot_risk": payload["blind_spot_risk"],
            "reason": "long-context read of every finding, including the region the "
                      "investigation's evidence window never reached -- context only, "
                      "never evidence, and it changes no verdict",
        })
    return payload


def _int(v: Any) -> int:
    try:
        return max(0, int(v))
    except (TypeError, ValueError):
        return 0
