"""Six more Lyzr Studio agents, each wired to one real seam in the pipeline.

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
  verdict audit           an independent second opinion on whether an already-
                          cited claim's quote actually supports it, beside
                          the pipeline's own `_assess_semantic_support`
                          estimate (A8 DEEP-F14/DEEP-F22). Disagreement is
                          persisted and ledgered, same reasoning as triage.
  response review         after the OPA policy gate has already decided: an
                          independent opinion on whether a proposed action's
                          scope looks proportionate to the evidence. Never
                          gates -- the gate has already run by the time this
                          is asked.
  corpus advisory         a standing, deployment-wide (not per-incident)
                          review of Sigma corpus coverage: which techniques
                          or rule directories look thin, from the same stats
                          `/api/corpus` already reports.
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
        for item in _as_list(r.get("thin"))[:24]:
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
        out["open_items"] = [str(x)[:200] for x in _as_list(r.get("open_items"))[:8]]
    else:
        out["detail"] = answer.get("detail", "")
    return out


#: The only values a verdict-audit reply's "support" is ever set to -- kept
#: local rather than imported from agents.pipeline so this connector has no
#: import-time dependency on the swarm package, same reasoning as the rest
#: of this module.
_SUPPORT_LEVELS = ("strong", "partial", "weak", "unclear")


# -- 4. verdict audit ------------------------------------------------------

def verdict_agent(sender=None) -> LyzrAgent:
    return LyzrAgent("verdict_audit", settings.lyzr_verdict_agent_id, "citinel-lyzr-verdict", sender)


def verdict_audit(incident_id: str, claims: list[dict[str, Any]], ledger, agent: LyzrAgent | None = None) -> dict[str, Any]:
    """Independent second opinion on whether each already-cited claim's quote
    actually supports what the claim says, beside the pipeline's own
    `_assess_semantic_support` estimate. Reads only claims that already
    survived citation_verification and carry a citation; never re-opens that
    keep/drop decision and never changes a claim. Capped to the first 20
    claims, same spirit as the pipeline's own MAX_SEMANTIC_SUPPORT_CLAIMS."""
    agent = agent or verdict_agent()
    items: list[dict[str, Any]] = []
    for i, c in enumerate(claims[:20]):
        cites = c.get("citations") or []
        cite = cites[0] if cites else {}
        items.append({
            "index": i, "statement": str(c.get("text") or "")[:400],
            "cited_quote": str((cite or {}).get("quoted_span") or "")[:400],
            "pipeline_support": c.get("semantic_support"),
        })
    answer = agent.ask({"incident_id": incident_id, "claims": items})
    out: dict[str, Any] = {"status": answer["status"], "agent_id": answer["agent_id"],
                           "asked_at": answer["asked_at"], "claims": [], "agree_count": 0, "disagree_count": 0}
    if answer["status"] == "ok":
        r = answer["reply"] or {}
        for item in _as_list(r.get("claims"))[:20]:
            if not isinstance(item, dict):
                continue
            idx, support = item.get("index"), str(item.get("support") or "").strip().lower()
            if not isinstance(idx, int) or not (0 <= idx < len(items)) or support not in _SUPPORT_LEVELS:
                continue
            base = items[idx]["pipeline_support"]
            agrees = (support == base) if base else None
            if agrees is True:
                out["agree_count"] += 1
            elif agrees is False:
                out["disagree_count"] += 1
            out["claims"].append({"index": idx, "support": support,
                                  "note": str(item.get("note") or "")[:300], "agrees_with_pipeline": agrees})
    else:
        out["detail"] = answer.get("detail", "")
    if ledger is not None and answer["status"] != "not_configured":
        ledger.append(incident_id, "lyzr-verdict", "decision", {
            "check": "verdict_audit", "status": answer["status"],
            "claims_reviewed": len(out["claims"]), "agree_count": out["agree_count"],
            "disagree_count": out["disagree_count"],
            "reason": "independent second opinion on citation support, beside the "
                      "pipeline's own semantic-support estimate -- advisory only, "
                      "never re-opens which claims kept their citations",
        })
    return out


# -- 5. response review -----------------------------------------------------

def response_agent(sender=None) -> LyzrAgent:
    return LyzrAgent("response_review", settings.lyzr_response_agent_id, "citinel-lyzr-response", sender)


def response_review(incident_id: str, action_class: str, target: str, assets_affected: int,
                    decision: dict[str, Any], ledger=None, agent: LyzrAgent | None = None) -> dict[str, Any]:
    """Independent opinion on whether a proposed action's scope looks
    proportionate to the evidence, asked after the OPA gate has already
    decided. Never gates: this changes nothing about whether the action
    executes, only adds a second, visible opinion beside the gate's own."""
    agent = agent or response_agent()
    answer = agent.ask({
        "incident_id": incident_id, "action_class": action_class, "target": target,
        "assets_affected": assets_affected,
        "policy_clause": decision.get("clause"), "policy_effect": decision.get("effect"),
        "autonomy": decision.get("autonomy"),
    })
    out: dict[str, Any] = {"status": answer["status"], "agent_id": answer["agent_id"],
                           "asked_at": answer["asked_at"], "assessment": None, "rationale": ""}
    if answer["status"] == "ok":
        r = answer["reply"] or {}
        assessment = str(r.get("assessment") or "").strip().lower()
        out["assessment"] = assessment if assessment in ("proportionate", "over_scoped", "under_scoped") else "unparsed"
        out["rationale"] = str(r.get("rationale") or "")[:300]
    else:
        out["detail"] = answer.get("detail", "")
    if ledger is not None and answer["status"] != "not_configured":
        ledger.append(incident_id, "lyzr-response", "decision", {
            "check": "response_review", "status": answer["status"], "action_class": action_class,
            "assessment": out["assessment"],
            "reason": "independent proportionality opinion on a proposed action, asked "
                      "after the OPA gate already decided -- advisory only, never gates",
        })
    return out


# -- 6. corpus advisory ------------------------------------------------------

def corpus_agent(sender=None) -> LyzrAgent:
    return LyzrAgent("corpus_advisory", settings.lyzr_corpus_agent_id, "citinel-lyzr-corpus", sender)


def corpus_advisory(stats: dict[str, Any], agent: LyzrAgent | None = None) -> dict[str, Any]:
    """A standing, deployment-wide review of Sigma corpus coverage -- which
    rule directories or techniques look thin -- from the same static and
    fired-rule stats `/api/corpus` already reports. Not per-incident."""
    agent = agent or corpus_agent()
    answer = agent.ask({
        "rules_total": stats.get("rules_total"), "by_dir": stats.get("by_dir"),
        "distinct_rules_fired": stats.get("distinct_rules_fired"),
        "detections_total": stats.get("detections_total"),
        "techniques_observed": (stats.get("techniques_observed") or [])[:60],
    })
    out: dict[str, Any] = {"status": answer["status"], "agent_id": answer["agent_id"],
                           "asked_at": answer["asked_at"], "gaps": [], "summary": ""}
    if answer["status"] == "ok":
        r = answer["reply"] or {}
        out["summary"] = str(r.get("summary") or "")[:800]
        out["gaps"] = [{"area": str(g.get("area") or "")[:120], "why": str(g.get("why") or "")[:300]}
                       for g in _as_list(r.get("gaps"))[:12] if isinstance(g, dict)]
    else:
        out["detail"] = answer.get("detail", "")
    return out



def _as_list(v: Any) -> list:
    """A model told to return a list can return a scalar or an object instead.
    Slicing that raises TypeError before any per-item isinstance check runs --
    on a live route, with the model spend already paid. Everything that slices
    a reply goes through here first."""
    return v if isinstance(v, list) else []


def _num(v: Any) -> float | None:
    try:
        x = float(v)
        return max(0.0, min(1.0, x))
    except (TypeError, ValueError):
        return None


def _clip(payload: Any, limit: int = 240) -> Any:
    s = json.dumps(payload, ensure_ascii=False) if not isinstance(payload, str) else payload
    return s if len(s) <= limit else s[:limit] + "…"
