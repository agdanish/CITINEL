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

Four of Tavily's primitives are used here, each where it earns its place,
and every one of them still lands on the not-evidence side of the line:

  search   every planned query (technique, rule, regulatory, campaign),
           with include_answer so Tavily's own synthesis comes back too.
  extract  the regulatory query's top source, pulled as full page text so a
           reader gets the actual CERT-In/DPDP wording inline rather than a
           link they may never open.
  map      the first technique's ATT&CK page, read as taxonomy: which
           sub-technique pages MITRE publishes under it right now, live,
           instead of a hardcoded list that goes stale.
  crawl    that same ATT&CK page plus the pages it links to, as full text --
           where extract reads one page, crawl reads a small neighbourhood.

Map and Crawl run for the FIRST technique query only, so the added cost is a
fixed +2 calls per gather no matter how many techniques a run found.
`primitives_used` in the persisted payload records which of the four a given
gather actually reached, from what happened rather than what is possible.
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
#: Two more query kinds, each capped to at most one call: a regulatory-
#: guidance lookup (always fireable -- every incident has a severity) and a
#: named threat-actor/campaign lookup (only when at least two distinct
#: techniques were actually found together, so the query is meaningfully
#: different from the per-technique searches above, not padding).
MAX_REGULATORY_QUERIES = 1
MAX_CAMPAIGN_QUERIES = 1
RESULTS_PER_QUERY = 3

#: ATT&CK enrichment (Map + Crawl) runs for the FIRST technique query only,
#: never once per technique: the added cost is then a fixed +2 calls per
#: gather however many techniques a run turned up, the same discipline the
#: regulatory Extract call follows. attack.mitre.org is the target on purpose
#: -- a stable, bot-friendly domain with a predictable URL scheme, unlike
#: guessing at a regulator portal's paths.
ATTACK_BASE = "https://attack.mitre.org/techniques"
MAX_MAP_URLS = 10
MAX_CRAWL_PAGES = 3


def attack_url(technique_id: str) -> str:
    """The ATT&CK page for a technique, root page even for a sub-technique
    (T1021.002 -> .../techniques/T1021/), because the root page is what
    actually links to the sub-technique and mitigation pages worth reading."""
    root = str(technique_id or "").strip().upper().split(".")[0]
    if not root.startswith("T") or not root[1:].isdigit():
        return ""
    return f"{ATTACK_BASE}/{root}/"


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
    tech_ids: list[str] = []
    stages = ((verdict or {}).get("correlation") or {}).get("stages") or []
    for st in stages:
        tid = str(st.get("technique_id") or "").strip()
        name = str(st.get("technique_name") or "").strip()
        if not tid or tid in seen:
            continue
        seen.add(tid)
        tech_ids.append(tid)
        plan.append({"for": tid, "kind": "technique",
                     "query": f"MITRE ATT&CK {tid} {name} detection and mitigation"})
        if len(plan) >= MAX_TECHNIQUE_QUERIES:
            break
    titles = Counter(f.title for f in incident.findings if f.source == "sigma")
    for title, _ in titles.most_common(MAX_RULE_QUERIES):
        plan.append({"for": title, "kind": "rule", "query": f'Sigma rule "{title}" detection'})

    if MAX_REGULATORY_QUERIES:
        plan.append({"for": incident.severity, "kind": "regulatory",
                     "query": f"CERT-In 6-hour cyber incident reporting and DPDP breach "
                              f"notification obligations for a {incident.severity} severity "
                              f"security incident in India"})
    if MAX_CAMPAIGN_QUERIES and len(tech_ids) >= 2:
        combo = " and ".join(tech_ids[:3])
        plan.append({"for": combo, "kind": "campaign",
                     "query": f"threat actor or campaign known for using MITRE ATT&CK "
                              f"techniques {combo} together"})
    return plan


def gather_context(incident, verdict: dict[str, Any] | None, cache_dir: Path,
                   incidents_dir: Path, connector: TavilyConnector | None = None) -> dict[str, Any]:
    tav = connector or TavilyConnector(EnrichmentCache(cache_dir))
    plan = plan_queries(incident, verdict)
    queries: list[dict[str, Any]] = []
    spent = 0
    attack_done = False
    for item in plan:
        r = tav.search(item["query"], max_results=RESULTS_PER_QUERY)
        entry: dict[str, Any] = dict(item)
        results = (r.detail or {}).get("results", []) if r.status == "ok" else []
        entry.update({"status": r.status, "fetched_at": r.fetched_at, "cached": r.cached,
                      "answer": (r.detail or {}).get("answer", "") if r.status == "ok" else "",
                      "results": results,
                      "note": r.verdict if r.status != "ok" else ""})
        if r.status == "ok" and not r.cached:
            spent += 1
        # The regulatory query gets one extra step: pull the FULL text of its
        # top source with Extract, not just the search snippet already in
        # "results" above -- real retrieval-augmentation (docs.tavily.com
        # Extract endpoint), so a reader gets the actual CERT-In/DPDP text
        # inline rather than a link they may never open. One extract call per
        # gather at most, only for this query kind, only when a result exists.
        # The first technique query gets the ATT&CK pair: Map reads the
        # taxonomy live (which sub-technique pages exist under this technique
        # right now), Crawl reads the technique page and the pages it links to
        # as full text. Search above still runs and still covers the whole web
        # -- this adds official-source depth beside it, it does not replace it.
        if item["kind"] == "technique" and not attack_done:
            base = attack_url(item["for"])
            if base:
                attack_done = True
                mr = tav.map_site(base, limit=MAX_MAP_URLS, select_paths=[r"/techniques/.*"])
                cr = tav.crawl(base, limit=MAX_CRAWL_PAGES,
                               select_paths=[r"/techniques/.*", r"/mitigations/.*"])
                for r_ in (mr, cr):
                    if r_.status == "ok" and not r_.cached:
                        spent += 1
                entry["attack_detail"] = {
                    "base_url": base,
                    "map_status": mr.status,
                    "mapped_urls": (mr.detail or {}).get("urls", []) if mr.status == "ok" else [],
                    "crawl_status": cr.status,
                    "crawled": (cr.detail or {}).get("pages", []) if cr.status == "ok" else [],
                    "fetched_at": cr.fetched_at or mr.fetched_at,
                    "note": "; ".join(x.verdict for x in (mr, cr) if x.status != "ok"),
                }
        if item["kind"] == "regulatory" and results:
            top_url = results[0].get("url") or ""
            if top_url:
                er = tav.extract(top_url)
                if er.status == "ok" and not er.cached:
                    spent += 1
                entry["extracted"] = {
                    "status": er.status, "source_url": er.source_url or top_url,
                    "fetched_at": er.fetched_at, "cached": er.cached,
                    "text": er.verdict if er.status == "ok" else "",
                    "truncated": bool((er.detail or {}).get("truncated")) if er.status == "ok" else False,
                    "note": "" if er.status == "ok" else er.verdict,
                }
        queries.append(entry)
    # Which Tavily primitives this gather actually reached for -- recorded
    # from what happened, not from what the code can in principle do, so an
    # unset key or a failed call never claims a primitive was used.
    primitives = ["search"]
    if any((q.get("extracted") or {}).get("status") == "ok" for q in queries):
        primitives.append("extract")
    if any((q.get("attack_detail") or {}).get("map_status") == "ok" for q in queries):
        primitives.append("map")
    if any((q.get("attack_detail") or {}).get("crawl_status") == "ok" for q in queries):
        primitives.append("crawl")

    out = {
        "incident_id": incident.incident_id,
        "gathered_at": datetime.now(timezone.utc).isoformat(),
        "provider": "tavily",
        "queries": queries,
        "credits_used": spent,
        "sources": sum(len(q["results"]) for q in queries),
        # Counted separately from "sources" on purpose: a search hit is a
        # ranked link, a retrieved page is full text this record actually
        # holds. Conflating them would overstate what was really fetched.
        "pages_retrieved": (
            sum(1 for q in queries if (q.get("extracted") or {}).get("status") == "ok")
            + sum(len((q.get("attack_detail") or {}).get("crawled", [])) for q in queries)
        ),
        "primitives_used": primitives,
        "not_evidence": "public context only; nothing here can support a claim -- "
                        "citations still point only at the record's own findings",
    }
    path = context_path(incident.incident_id, incidents_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)
    return out
