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

from citinel.config import settings
from citinel.connectors.base import Connector, EnrichmentResult


class TavilyConnector(Connector):
    """Real-time OSINT search (SDD Section 15.3 -- Best Use of Tavily)."""

    provider = "tavily"
    endpoint = "https://api.tavily.com/search"

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
                json_body={"api_key": settings.tavily_api_key, "query": query,
                           "max_results": max_results,
                           "search_depth": "basic"},
            )
        except Exception as e:
            return EnrichmentResult(self.provider, query, "query", "error",
                                    verdict=f"Tavily call failed: {e}")
        if status != 200:
            return EnrichmentResult(self.provider, query, "query", "error",
                                    verdict=f"Tavily HTTP {status}")
        results = body.get("results", []) if isinstance(body, dict) else []
        top = results[0] if results else {}
        result = EnrichmentResult(
            provider=self.provider, indicator=query, indicator_type="query",
            status="ok",
            verdict=(body.get("answer") or top.get("title", ""))[:300],
            source_url=top.get("url", "https://tavily.com"),
            fetched_at=self._now(),
            detail={"results": [{"title": r.get("title"), "url": r.get("url"),
                                 "score": r.get("score")} for r in results[:max_results]]},
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
