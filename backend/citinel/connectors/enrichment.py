"""Enrichment Squad connectors: Tavily (sponsor), VirusTotal, AbuseIPDB.

Each provider degrades gracefully with no key (returns status="not_configured"),
answers from cache when the indicator was seen before, and reaches the network
only through the egress-guarded base. Every result is normalized to
EnrichmentResult so the Correlator and Verdict Narrator consume one shape
regardless of provider -- and every result carries a citable source_url +
fetched_at for the citation chip.

Tavily is a Decode SIH sponsor ("Best Use of Tavily"): its result surfaces the
search source and timestamp explicitly in the citation chip (SDD Section 15.3),
turning an invisible backend call into visible, judge-legible provenance.
"""

from __future__ import annotations

import json
from typing import Any

from citinel.config import settings
from citinel.connectors.base import Connector, EnrichmentResult


class TavilyConnector(Connector):
    """Real-time OSINT search (SDD Section 15.3 -- Best Use of Tavily)."""

    provider = "tavily"
    endpoint = "https://api.tavily.com/search"
    extract_endpoint = "https://api.tavily.com/extract"
    crawl_endpoint = "https://api.tavily.com/crawl"
    map_endpoint = "https://api.tavily.com/map"
    research_endpoint = "https://api.tavily.com/research"

    def search(self, query: str, max_results: int = 5) -> EnrichmentResult:
        cached = self.cache.get(self.provider, query)
        if cached:
            return cached
        if not settings.tavily_api_key:
            return EnrichmentResult(self.provider, query, "query", "not_configured",
                                    verdict="Tavily key not set; enrichment skipped")
        try:
            status, body = self._guarded_request(
                "POST", self.endpoint,
                headers={"Content-Type": "application/json"},
                # include_answer asks Tavily for its own LLM-synthesized answer,
                # not just ranked links -- without it "answer" is never in the
                # response at all, so reading body.get("answer") below was a
                # silent no-op until this was requested explicitly.
                json_body={"api_key": settings.tavily_api_key, "query": query,
                           "max_results": max_results,
                           "search_depth": "basic", "include_answer": "basic"},
            )
        except Exception as e:
            return EnrichmentResult(self.provider, query, "query", "error",
                                    verdict=f"Tavily call failed: {e}")
        if status != 200:
            return EnrichmentResult(self.provider, query, "query", "error",
                                    verdict=f"Tavily HTTP {status}")
        # Everything below is defensive because `body` is whatever the API
        # returned: the transport types it Any and hands back r.json()
        # unmodified, so a valid-JSON non-object (a list, a bare string) arrives
        # here intact. The isinstance guard on `results` was the only one, which
        # made it dead code in precisely the case it was written for -- reading
        # body.get("answer") two lines down raised AttributeError before
        # `results` was ever looked at. The items are guarded too: Tavily's own
        # /map endpoint returns bare URL strings, so a scalar row is a shape
        # this API genuinely produces, and .get() on a str raises the same way.
        # An AttributeError here does not stay here. enricher._execute catches
        # only (KeyError, TypeError) despite promising never to raise, so it
        # escapes into the incident path: POST /api/incidents/{id}/context
        # answers 500 and abandons every remaining query in the plan, and a
        # console swarm run is discarded wholesale by the worker's blanket
        # handler after the model spend has already been incurred.
        results = body.get("results", []) if isinstance(body, dict) else []
        rows = [r for r in results if isinstance(r, dict)] if isinstance(results, list) else []
        top = rows[0] if rows else {}
        answer = (body.get("answer") if isinstance(body, dict) else "") or ""
        result = EnrichmentResult(
            provider=self.provider, indicator=query, indicator_type="query",
            status="ok",
            verdict=(answer or str(top.get("title") or ""))[:300],
            source_url=str(top.get("url") or "https://tavily.com"),
            fetched_at=self._now(),
            detail={"results": [{"title": r.get("title"), "url": r.get("url"),
                                 "score": r.get("score")} for r in rows[:max_results]],
                    "answer": answer},
        )
        self.cache.put(result)
        return result

    def research_start(self, question: str) -> tuple[str, str]:
        """Kick off a Tavily Research run: their agentic endpoint, which runs
        several searches of its own, reasons across them and returns a cited
        report. Search answers "what pages mention this"; Research answers a
        question. Async by design -- returns (request_id, note).
        """
        if not settings.tavily_api_key:
            return "", "Tavily key not set; no research was started"
        try:
            status, body = self._guarded_request(
                "POST", self.research_endpoint,
                headers={"Content-Type": "application/json",
                         "Authorization": f"Bearer {settings.tavily_api_key}"},
                json_body={"input": question, "model": "auto",
                           "output_length": "short", "citation_format": "numbered"},
            )
        except Exception as e:
            return "", f"Tavily research call failed: {e}"
        if status // 100 != 2 or not isinstance(body, dict):
            return "", f"Tavily research HTTP {status}"
        rid = str(body.get("request_id") or "")
        return (rid, "") if rid else ("", "Tavily returned no request id")

    def research_poll(self, request_id: str) -> dict[str, Any]:
        """One poll. 202 = still working, 200 = completed or failed.

        Deliberately one poll per call rather than a blocking wait loop: a
        research run takes as long as it takes, and holding an HTTP worker
        open for it would put the console's own timeout in charge of whether
        the answer is allowed to exist.
        """
        if not settings.tavily_api_key:
            return {"status": "not_configured", "content": "", "sources": []}
        try:
            status, body = self._guarded_request(
                "GET", f"{self.research_endpoint}/{request_id}",
                headers={"Authorization": f"Bearer {settings.tavily_api_key}"},
            )
        except Exception as e:
            return {"status": "error", "content": "", "sources": [],
                    "detail": f"Tavily research poll failed: {e}"}
        if status == 202:
            return {"status": "pending", "content": "", "sources": []}
        if status != 200 or not isinstance(body, dict):
            return {"status": "error", "content": "", "sources": [],
                    "detail": f"Tavily research poll HTTP {status}"}
        state = str(body.get("status") or "")
        content = body.get("content")
        return {
            "status": "completed" if state == "completed" else (state or "error"),
            "content": content if isinstance(content, str) else json.dumps(content or "")[:6000],
            "sources": [{"title": str(x.get("title") or "")[:160],
                         "url": str(x.get("url") or "")[:400]}
                        for x in (body.get("sources") or [])[:12] if isinstance(x, dict)],
            "response_time": body.get("response_time"),
        }

    def extract(self, url: str, max_chars: int = 4000) -> EnrichmentResult:
        """Full page content, not a search snippet -- Tavily's own retrieval
        primitive for grounding an LLM in a real source rather than a link a
        human might never click (docs.tavily.com Extract endpoint). Cached
        under a distinct provider key so it never collides with a search()
        cache entry for the same URL string.
        """
        cache_key = f"extract:{url}"
        cached = self.cache.get(self.provider, cache_key)
        if cached:
            return cached
        if not settings.tavily_api_key:
            return EnrichmentResult(self.provider, url, "url", "not_configured",
                                    verdict="Tavily key not set; extraction skipped")
        try:
            status, body = self._guarded_request(
                "POST", self.extract_endpoint,
                headers={"Content-Type": "application/json"},
                json_body={"api_key": settings.tavily_api_key, "urls": [url],
                           "extract_depth": "basic", "format": "text"},
            )
        except Exception as e:
            return EnrichmentResult(self.provider, url, "url", "error",
                                    verdict=f"Tavily extract failed: {e}")
        if status != 200:
            return EnrichmentResult(self.provider, url, "url", "error",
                                    verdict=f"Tavily extract HTTP {status}")
        # Rows are filtered to dicts for the same reason search() filters them:
        # a subscript into failed_results assumed a list (a dict there raises
        # KeyError: 0, a string silently yields one character), and results[0]
        # assumed a mapping. Both are shapes this API produces -- /map answers
        # with bare URL strings -- and both raised out of a method whose only
        # documented outcomes are ok and error.
        raw_rows = body.get("results", []) if isinstance(body, dict) else []
        rows = [r for r in raw_rows if isinstance(r, dict)] if isinstance(raw_rows, list) else []
        if not rows:
            fails = body.get("failed_results") if isinstance(body, dict) else None
            first = next((f for f in fails if isinstance(f, dict)), {}) \
                if isinstance(fails, list) else {}
            return EnrichmentResult(self.provider, url, "url", "error",
                                    verdict=f"Tavily could not extract this URL: {first.get('error', 'unknown')}")
        raw = str(rows[0].get("raw_content") or "")
        result = EnrichmentResult(
            provider=self.provider, indicator=cache_key, indicator_type="url",
            status="ok", verdict=raw[:max_chars],
            source_url=str(rows[0].get("url") or url), fetched_at=self._now(),
            detail={"truncated": len(raw) > max_chars, "full_length": len(raw)},
        )
        self.cache.put(result)
        return result

    def map_site(self, url: str, limit: int = 10, select_paths: list[str] | None = None) -> EnrichmentResult:
        """URL discovery, not content: which pages actually exist under a
        section of a site right now (docs.tavily.com Map endpoint). Used to
        read a taxonomy live -- e.g. which sub-technique pages ATT&CK
        currently publishes under a technique -- instead of hardcoding a list
        that goes stale. Named map_site, not map, so it never shadows the
        builtin on this class.
        """
        cache_key = f"map:{url}:{limit}"
        cached = self.cache.get(self.provider, cache_key)
        if cached:
            return cached
        if not settings.tavily_api_key:
            return EnrichmentResult(self.provider, url, "url", "not_configured",
                                    verdict="Tavily key not set; mapping skipped")
        body_in: dict = {"api_key": settings.tavily_api_key, "url": url,
                         "max_depth": 1, "max_breadth": limit, "limit": limit,
                         "allow_external": False}
        if select_paths:
            body_in["select_paths"] = select_paths
        try:
            status, body = self._guarded_request(
                "POST", self.map_endpoint,
                headers={"Content-Type": "application/json"}, json_body=body_in)
        except Exception as e:
            return EnrichmentResult(self.provider, url, "url", "error",
                                    verdict=f"Tavily map failed: {e}")
        if status != 200:
            return EnrichmentResult(self.provider, url, "url", "error",
                                    verdict=f"Tavily map HTTP {status}")
        urls = [u for u in (body.get("results") or []) if isinstance(u, str)] if isinstance(body, dict) else []
        result = EnrichmentResult(
            provider=self.provider, indicator=cache_key, indicator_type="url",
            status="ok", verdict=f"{len(urls)} page(s) discovered under {url}",
            source_url=url, fetched_at=self._now(),
            detail={"urls": urls[:limit]},
        )
        self.cache.put(result)
        return result

    def crawl(self, url: str, limit: int = 3, select_paths: list[str] | None = None,
              max_chars: int = 2500) -> EnrichmentResult:
        """Full content from a page AND the pages it links to, in one call
        (docs.tavily.com Crawl endpoint) -- where extract() reads one page,
        this reads a small neighbourhood of them. Deliberately tight bounds:
        depth 1 and a low `limit`, because ATT&CK pages are densely
        cross-linked and an unbounded crawl is both slow and a real credit
        cost (1 credit per 10 pages, 2 with instructions).
        """
        cache_key = f"crawl:{url}:{limit}"
        cached = self.cache.get(self.provider, cache_key)
        if cached:
            return cached
        if not settings.tavily_api_key:
            return EnrichmentResult(self.provider, url, "url", "not_configured",
                                    verdict="Tavily key not set; crawl skipped")
        body_in: dict = {"api_key": settings.tavily_api_key, "url": url,
                         "max_depth": 1, "max_breadth": limit, "limit": limit,
                         "allow_external": False, "extract_depth": "basic",
                         "format": "text"}
        if select_paths:
            body_in["select_paths"] = select_paths
        try:
            status, body = self._guarded_request(
                "POST", self.crawl_endpoint,
                headers={"Content-Type": "application/json"}, json_body=body_in)
        except Exception as e:
            return EnrichmentResult(self.provider, url, "url", "error",
                                    verdict=f"Tavily crawl failed: {e}")
        if status != 200:
            return EnrichmentResult(self.provider, url, "url", "error",
                                    verdict=f"Tavily crawl HTTP {status}")
        pages = body.get("results", []) if isinstance(body, dict) else []
        kept = [{"url": p.get("url", ""), "text": str(p.get("raw_content") or "")[:max_chars]}
                for p in pages[:limit] if p.get("url")]
        if not kept:
            return EnrichmentResult(self.provider, url, "url", "error",
                                    verdict=f"Tavily crawl returned no pages for {url}")
        result = EnrichmentResult(
            provider=self.provider, indicator=cache_key, indicator_type="url",
            status="ok", verdict=f"{len(kept)} page(s) crawled from {url}",
            source_url=body.get("base_url", url) if isinstance(body, dict) else url,
            fetched_at=self._now(), detail={"pages": kept},
        )
        self.cache.put(result)
        return result


class VirusTotalConnector(Connector):
    """File/IP/domain reputation. Free public API: 4/min, 500/day (PIPE-F04)."""

    provider = "virustotal"
    min_interval_s = 15.5    # <= 4 requests per minute, with margin

    def _lookup(self, path: str, indicator: str, itype: str) -> EnrichmentResult:
        cached = self.cache.get(self.provider, indicator)
        if cached:
            return cached
        if not settings.virustotal_api_key:
            return EnrichmentResult(self.provider, indicator, itype, "not_configured",
                                    verdict="VirusTotal key not set; enrichment skipped")
        url = f"https://api.virustotal.com/api/v3/{path}"
        try:
            status, body = self._guarded_request(
                "GET", url, headers={"x-apikey": settings.virustotal_api_key})
        except Exception as e:
            return EnrichmentResult(self.provider, indicator, itype, "error",
                                    verdict=f"VirusTotal call failed: {e}")
        if status != 200:
            return EnrichmentResult(self.provider, indicator, itype, "error",
                                    verdict=f"VirusTotal HTTP {status}")
        stats = (body.get("data", {}).get("attributes", {})
                 .get("last_analysis_stats", {})) if isinstance(body, dict) else {}
        malicious = stats.get("malicious", 0)
        total = sum(stats.values()) or 1
        result = EnrichmentResult(
            provider=self.provider, indicator=indicator, indicator_type=itype,
            status="ok", score=round(malicious / total, 3),
            verdict=f"{malicious}/{total} engines flagged this {itype} as malicious",
            source_url=f"https://www.virustotal.com/gui/{itype}/{indicator}",
            fetched_at=self._now(), detail={"stats": stats})
        self.cache.put(result)
        return result

    def check_ip(self, ip: str) -> EnrichmentResult:
        return self._lookup(f"ip_addresses/{ip}", ip, "ip")

    def check_domain(self, domain: str) -> EnrichmentResult:
        return self._lookup(f"domains/{domain}", domain, "domain")

    def check_hash(self, file_hash: str) -> EnrichmentResult:
        return self._lookup(f"files/{file_hash}", file_hash, "hash")


class AbuseIPDBConnector(Connector):
    """IP abuse reputation. Free tier: 1,000 checks/day."""

    provider = "abuseipdb"
    endpoint = "https://api.abuseipdb.com/api/v2/check"

    def check_ip(self, ip: str, max_age_days: int = 90) -> EnrichmentResult:
        cached = self.cache.get(self.provider, ip)
        if cached:
            return cached
        if not settings.abuseipdb_api_key:
            return EnrichmentResult(self.provider, ip, "ip", "not_configured",
                                    verdict="AbuseIPDB key not set; enrichment skipped")
        try:
            status, body = self._guarded_request(
                "GET", self.endpoint,
                headers={"Key": settings.abuseipdb_api_key, "Accept": "application/json"},
                params={"ipAddress": ip, "maxAgeInDays": max_age_days})
        except Exception as e:
            return EnrichmentResult(self.provider, ip, "ip", "error",
                                    verdict=f"AbuseIPDB call failed: {e}")
        if status != 200:
            return EnrichmentResult(self.provider, ip, "ip", "error",
                                    verdict=f"AbuseIPDB HTTP {status}")
        data = body.get("data", {}) if isinstance(body, dict) else {}
        conf = data.get("abuseConfidenceScore", 0)
        result = EnrichmentResult(
            provider=self.provider, indicator=ip, indicator_type="ip",
            status="ok", score=round(conf / 100, 3),
            verdict=(f"abuse confidence {conf}% over {data.get('totalReports', 0)} "
                     f"reports; ISP {data.get('isp', '?')}, {data.get('countryCode', '?')}"),
            source_url=f"https://www.abuseipdb.com/check/{ip}",
            fetched_at=self._now(),
            detail={"confidence": conf, "total_reports": data.get("totalReports"),
                    "country": data.get("countryCode"), "isp": data.get("isp")})
        self.cache.put(result)
        return result


class EnrichmentSquad:
    """Fans one indicator out to the relevant providers, cache-first."""

    def __init__(self, cache, sender=None) -> None:
        self.tavily = TavilyConnector(cache, sender)
        self.virustotal = VirusTotalConnector(cache, sender)
        self.abuseipdb = AbuseIPDBConnector(cache, sender)

    def enrich_ip(self, ip: str) -> list[EnrichmentResult]:
        return [self.virustotal.check_ip(ip), self.abuseipdb.check_ip(ip)]

    def enrich_hash(self, file_hash: str) -> list[EnrichmentResult]:
        return [self.virustotal.check_hash(file_hash)]

    def enrich_context(self, query: str) -> list[EnrichmentResult]:
        return [self.tavily.search(query)]
