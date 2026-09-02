"""Public context for a verdict: what the open web says about the techniques
and rules an investigation turned up, fetched through Tavily and cited with
the URL and the fetch time.

This is the honest version of the "external citation" the console's design
always wanted to show. It is deliberately NOT evidence: the citation contract
(`Citation.finding_index` into the incident's own findings) is untouched, and
nothing gathered here can support a claim. It is context a reader can follow
-- an advisory, a technique write-up, a vendor note -- attached to the
technique or rule it was searched for, with the query that produced it, so a
judge can see exactly what was asked and when.

Persisted beside the swarm result (`<incidents_dir>/context/<id>.json`) so the
console serves it without re-spending credits; every query is one Tavily
credit unless the enrichment cache already holds it.
"""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from citinel.connectors.base import EnrichmentCache
from citinel.connectors.enrichment import TavilyConnector

CONTEXT_SUBDIR = "context"
MAX_TECHNIQUE_QUERIES = 4
MAX_RULE_QUERIES = 2
RESULTS_PER_QUERY = 3


def context_path(incident_id: str, incidents_dir: Path) -> Path:
    return incidents_dir / CONTEXT_SUBDIR / f"{incident_id}.json"


def load_context(incident_id: str, incidents_dir: Path) -> dict[str, Any] | None:
    p = context_path(incident_id, incidents_dir)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def plan_queries(incident, verdict: dict[str, Any] | None) -> list[dict[str, str]]:
    """Which searches to run, derived from what the run actually found.

    Techniques come from the correlator's stages (the verdict's own chain),
    rules from the sigma titles that fired most on the record. Each query
    names what it is FOR so the console can pin results to the right row.
    """
    plan: list[dict[str, str]] = []
    seen: set[str] = set()
    stages = ((verdict or {}).get("correlation") or {}).get("stages") or []
    for st in stages:
        tid = str(st.get("technique_id") or "").strip()
        name = str(st.get("technique_name") or "").strip()
        if not tid or tid in seen:
            continue
        seen.add(tid)
        plan.append({"for": tid, "kind": "technique",
                     "query": f"MITRE ATT&CK {tid} {name} detection and mitigation"})
        if len(plan) >= MAX_TECHNIQUE_QUERIES:
            break
    titles = Counter(f.title for f in incident.findings if f.source == "sigma")
    for title, _ in titles.most_common(MAX_RULE_QUERIES):
        plan.append({"for": title, "kind": "rule", "query": f'Sigma rule "{title}" detection'})
    return plan


def gather_context(incident, verdict: dict[str, Any] | None, cache_dir: Path,
                   incidents_dir: Path, connector: TavilyConnector | None = None) -> dict[str, Any]:
    tav = connector or TavilyConnector(EnrichmentCache(cache_dir))
    plan = plan_queries(incident, verdict)
    queries: list[dict[str, Any]] = []
    spent = 0
    for item in plan:
        r = tav.search(item["query"], max_results=RESULTS_PER_QUERY)
        entry: dict[str, Any] = dict(item)
        entry.update({"status": r.status, "fetched_at": r.fetched_at, "cached": r.cached,
                      "answer": r.verdict if r.status == "ok" else "",
                      "results": (r.detail or {}).get("results", []) if r.status == "ok" else [],
                      "note": r.verdict if r.status != "ok" else ""})
        if r.status == "ok" and not r.cached:
            spent += 1
        queries.append(entry)
    out = {
        "incident_id": incident.incident_id,
        "gathered_at": datetime.now(timezone.utc).isoformat(),
        "provider": "tavily",
        "queries": queries,
        "credits_used": spent,
        "sources": sum(len(q["results"]) for q in queries),
        "not_evidence": "public context only; nothing here can support a claim -- "
                        "citations still point only at the record's own findings",
    }
    path = context_path(incident.incident_id, incidents_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)
    return out
