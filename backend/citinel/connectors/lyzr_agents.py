"""Three more Lyzr Studio agents, each wired to one real seam in the pipeline.

The rule for adding an agent here is the project's own: it earns its place
only when a real call site sends it real work and does something with the
answer that a human can see. Each agent has its own Studio id
(`CITINEL_LYZR_*_AGENT_ID`), the same fixed chat endpoint and API key as the
compliance monitor, and a JSON task message in the shape LYZR-AGENT-CONFIG.md
documents. An unset id means the seam says `not_configured`; a failed call
says `unavailable`. Nothing here is ever a source of evidence: opinions are
recorded as opinions, reviews as reviews, summaries as summaries.

  triage second opinion   after a swarm run: an independent lane + confidence
                          beside the Router's, written to the ledger as a
                          `decision` by actor `lyzr-triage`, so disagreement
                          is a fact a human sees on the Replay and Confidence
                          screens, not a hidden vote.
  draft field review      on the compliance desk: which drafted fields are thin
                          or need a human before sign-off, per field.
  handover summary        for the shift handover: a plain summary of where a
                          record stands, from the ledger's own frames.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from citinel.config import settings
from citinel.connectors.lyzr import _chat_payload, _lyzr_allow, _parse_agent_reply
from citinel.agents.quarantine import EGRESS_ALLOW, check_egress


class LyzrAgent:
    """One Studio agent: a task name, an id, and the one call it answers."""

    def __init__(self, task: str, agent_id: str | None, session_id: str, sender=None) -> None:
        self.task = task
        self.agent_id = agent_id
        self.session_id = session_id
        self._sender = sender

    @property
    def configured(self) -> bool:
        return bool(settings.lyzr_api_key and settings.lyzr_guard_url and self.agent_id)

    def ask(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Returns {status, reply, agent_id, asked_at}; never raises."""
        asked = datetime.now(timezone.utc).isoformat()
        base = {"task": self.task, "agent_id": self.agent_id, "asked_at": asked}
        if not self.configured:
            return dict(base, status="not_configured", reply=None,
                        detail="CITINEL_LYZR_API_KEY, CITINEL_LYZR_GUARD_URL and the agent id must all be set")
        decision = check_egress(settings.lyzr_guard_url, _lyzr_allow())
        if not decision.allowed:
            return dict(base, status="egress_refused", reply=None, detail=decision.reason)
        message = json.dumps({"task": self.task, "input": payload}, ensure_ascii=False)
        body = _chat_payload(message, self.session_id, agent_id=self.agent_id)
        headers = {"x-api-key": settings.lyzr_api_key, "Content-Type": "application/json"}
        try:
            if self._sender is not None:
                status, resp = self._sender(settings.lyzr_guard_url, headers, body)
            else:
                import httpx
                with httpx.Client(timeout=25) as c:
                    r = c.post(settings.lyzr_guard_url, headers=headers, json=body)
                    status, resp = r.status_code, (r.json() if r.content else {})
        except Exception as e:  # network, timeout, bad JSON
            return dict(base, status="unavailable", reply=None, detail=f"Lyzr call failed: {e}")
        reply = _parse_agent_reply(resp) if status // 100 == 2 else None
        if not reply:
            return dict(base, status="unavailable", reply=None, detail=f"Lyzr HTTP {status} or unparseable reply")
        return dict(base, status="ok", reply=reply, detail="")


# -- 1. triage second opinion ---------------------------------------------------

def triage_agent(sender=None) -> LyzrAgent:
    return LyzrAgent("triage_second_opinion", settings.lyzr_triage_agent_id, "citinel-lyzr-triage", sender)


def triage_second_opinion(incident, result_dict: dict[str, Any], ledger, agent: LyzrAgent | None = None) -> dict[str, Any]:
    """Ask for an independent lane on the same evidence summary the Router saw
    and record the answer beside the Router's decision. Returns the record."""
    agent = agent or triage_agent()
    triage = result_dict.get("triage") or {}
    titles: dict[str, int] = {}
    for f in incident.findings[:40]:
        titles[f.title] = titles.get(f.title, 0) + 1
    top = sorted(titles.items(), key=lambda kv: -kv[1])[:6]
    answer = agent.ask({
        "incident_id": incident.incident_id, "finding_count": len(incident.findings),
        "hosts": incident.hosts[:8], "techniques": incident.techniques[:16], "severity": incident.severity,
        "top_findings": [{"title": t, "count": n} for t, n in top],
        "router": {"lane": triage.get("lane"), "confidence": triage.get("confidence"), "rationale": triage.get("rationale")},
    })
    record: dict[str, Any] = {"decision": "triage_second_opinion", "status": answer["status"],
                              "agent_id": answer["agent_id"], "asked_at": answer["asked_at"]}
    if answer["status"] == "ok":
        r = answer["reply"] or {}
        lane = str(r.get("lane") or "").strip().lower()
        record.update({
            "lane": lane if lane in ("escalate", "auto_close") else "unparsed",
            "confidence": _num(r.get("confidence")),
            "rationale": str(r.get("rationale") or "")[:400],
            "agrees_with_router": (lane == str(triage.get("lane") or "")) if lane in ("escalate", "auto_close") else None,
        })
    else:
        record["detail"] = answer.get("detail", "")
    if ledger is not None and answer["status"] != "not_configured":
        ledger.append(incident.incident_id, "lyzr-triage", "decision", record)
    return record


# -- 2. draft field review ------------------------------------------------------

def review_agent(sender=None) -> LyzrAgent:
    return LyzrAgent("field_review", settings.lyzr_review_agent_id, "citinel-lyzr-review", sender)


def review_draft(draft, agent: LyzrAgent | None = None) -> dict[str, Any]:
    """Which drafted fields a human should not sign as they stand. Per field."""
    agent = agent or review_agent()
    answer = agent.ask({
        "kind": draft.kind, "incident_id": draft.incident_id,
        "fields": [{"key": f.key, "label": f.label, "fill": f.fill, "value": str(f.value)[:600]} for f in draft.fields],
    })
    out: dict[str, Any] = {"status": answer["status"], "agent_id": answer["agent_id"], "asked_at": answer["asked_at"],
                           "thin": [], "summary": ""}
    if answer["status"] == "ok":
        r = answer["reply"] or {}
        keys = {f.key for f in draft.fields}
        for item in (r.get("thin") or [])[:24]:
            if isinstance(item, dict) and item.get("key") in keys:
                out["thin"].append({"key": item["key"], "why": str(item.get("why") or "")[:300]})
        out["summary"] = str(r.get("summary") or "")[:600]
    else:
        out["detail"] = answer.get("detail", "")
    return out


# -- 3. handover summary --------------------------------------------------------

def handover_agent(sender=None) -> LyzrAgent:
    return LyzrAgent("handover_summary", settings.lyzr_handover_agent_id, "citinel-lyzr-handover", sender)


def handover_summary(incident_dict: dict[str, Any], chain: list, verdict_summary: dict[str, Any] | None,
                     agent: LyzrAgent | None = None) -> dict[str, Any]:
    """A plain-language handover note from the ledger's own frames."""
    agent = agent or handover_agent()
    frames = [e for e in chain if getattr(e, "kind", None) not in ("detection_added", "escalation_added")][-15:]
    answer = agent.ask({
        "incident_id": incident_dict.get("incident_id"), "state": incident_dict.get("state"),
        "severity": incident_dict.get("severity"), "hosts": (incident_dict.get("hosts") or [])[:8],
        "finding_count": incident_dict.get("finding_count"),
        "verdict": verdict_summary or None,
        "recent_frames": [{"ts": e.ts, "actor": e.actor, "kind": e.kind, "payload": _clip(e.payload)} for e in frames],
    })
    out: dict[str, Any] = {"status": answer["status"], "agent_id": answer["agent_id"], "asked_at": answer["asked_at"],
                           "summary": "", "open_items": []}
    if answer["status"] == "ok":
        r = answer["reply"] or {}
        out["summary"] = str(r.get("summary") or "")[:1200]
        out["open_items"] = [str(x)[:200] for x in (r.get("open_items") or [])[:8]]
    else:
        out["detail"] = answer.get("detail", "")
    return out


def _num(v: Any) -> float | None:
    try:
        x = float(v)
        return max(0.0, min(1.0, x))
    except (TypeError, ValueError):
        return None


def _clip(payload: Any, limit: int = 240) -> Any:
    s = json.dumps(payload, ensure_ascii=False) if not isinstance(payload, str) else payload
    return s if len(s) <= limit else s[:limit] + "…"
