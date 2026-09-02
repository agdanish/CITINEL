"""Persist what the swarm produced, so the console can show it.

Before this module, `citinel swarm run` printed a SwarmResult and dropped it:
the ledger records that the run happened (facts only, never narration), the
CLI showed the verdict once, and nothing kept it. That is exactly why the
Replay and Confidence screens had nothing real to read. This is the one place
a verdict is written to disk: `<incidents_dir>/swarm/<incident_id>.json` holds
the latest complete result, and `<incident_id>.runs.jsonl` appends one line
per run so re-runs are visible rather than silently overwritten.

Deliberately NOT the ledger. The ledger's standing rule is structured
decisions and tool calls only, never a model's narration; a verdict's claims
are the model's assertions. Keeping them beside the ledger, not in it, keeps
that rule intact and lets the UI say plainly which is which.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SWARM_SUBDIR = "swarm"


def swarm_dir(incidents_dir: Path) -> Path:
    return incidents_dir / SWARM_SUBDIR


def result_path(incident_id: str, incidents_dir: Path) -> Path:
    return swarm_dir(incidents_dir) / f"{incident_id}.json"


def save_result(result, incidents_dir: Path) -> Path:
    """Write the latest result atomically and append the run record."""
    d: dict[str, Any] = result.as_dict()
    d["saved_at"] = datetime.now(timezone.utc).isoformat()
    d["banner"] = result.banner()
    d["calls"] = [c.ledger_payload() for c in result.calls]
    d["usage"] = {
        "input_tokens": sum(c.input_tokens for c in result.calls),
        "output_tokens": sum(c.output_tokens for c in result.calls),
    }
    path = result_path(result.incident_id, incidents_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)
    verdict = d.get("verdict") or {}
    with (swarm_dir(incidents_dir) / f"{result.incident_id}.runs.jsonl").open(
        "a", encoding="utf-8"
    ) as fh:
        fh.write(json.dumps({
            "saved_at": d["saved_at"], "mode": d["mode"],
            "confidence": verdict.get("confidence"),
            "claims": len(verdict.get("claims", [])),
            "proposals": len(d.get("proposals", [])),
            "call_count": d.get("call_count", 0),
            **d["usage"],
        }) + "\n")
    return path


def load_result(incident_id: str, incidents_dir: Path) -> dict[str, Any] | None:
    p = result_path(incident_id, incidents_dir)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def load_runs(incident_id: str, incidents_dir: Path) -> list[dict[str, Any]]:
    p = swarm_dir(incidents_dir) / f"{incident_id}.runs.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def summary_of(d: dict[str, Any]) -> dict[str, Any]:
    """The few fields a list view needs, never the whole verdict."""
    verdict = d.get("verdict") or {}
    triage = d.get("triage") or {}
    return {
        "mode": d.get("mode"), "degraded": d.get("degraded"),
        "saved_at": d.get("saved_at"),
        "lane": triage.get("lane"),
        "headline": verdict.get("headline"),
        "confidence": verdict.get("confidence"),
        "claims": len(verdict.get("claims", [])),
        "proposals": len(d.get("proposals", [])),
        "findings_examined": d.get("findings_examined"),
        "findings_total": d.get("findings_total"),
    }


def summaries(incidents_dir: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    sd = swarm_dir(incidents_dir)
    if not sd.is_dir():
        return out
    for p in sorted(sd.glob("*.json")):
        if p.name.endswith(".tmp"):
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        out[d.get("incident_id", p.stem)] = summary_of(d)
    return out


def annotate_result(incident_id: str, incidents_dir: Path, key: str, value: Any) -> bool:
    """Attach one extra, clearly named block to a persisted result (for example
    an independent second opinion). Never touches the verdict itself."""
    p = result_path(incident_id, incidents_dir)
    if not p.exists():
        return False
    d = json.loads(p.read_text(encoding="utf-8"))
    d[key] = value
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)
    return True
