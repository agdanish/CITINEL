"""Connector foundation: egress-guarded HTTP, cache-first, hash-dedup.

Every outbound call any connector makes passes through the Step 9 egress
allow-list (SAFE-F02): the allow-list is a live-enforced control here, not a
demo talking point. A connector cannot reach a host that is not on the list,
so a poisoned log that persuades an agent to "enrich" an attacker URL is
refused at the transport, deterministically.

Caching is cache-first with hash-dedup (PIPE-F04, AGT-F10): a repeated
indicator is answered from disk, never re-fetched. This is why VirusTotal's
4-requests/minute cap can never fire mid-demo -- the same hash asked twice
costs one call, not two.

The client accepts an injectable `sender`, so the whole layer is testable
with a fake transport and no network, and it degrades gracefully: a provider
with no API key returns a "not configured" result rather than raising, so the
pipeline runs fully offline.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from citinel.agents.quarantine import check_egress

# A sender turns a request into (status_code, json_body). The real one wraps
# httpx; tests inject a fake. This is the only seam that touches the network.
Sender = Callable[[str, str, dict, dict | None, dict | None], tuple[int, Any]]


class EgressRefused(Exception):
    pass


@dataclass
class EnrichmentResult:
    """One provider's answer about one indicator, in a normalized shape.

    source_url + fetched_at are what surface in the Tavily citation chip
    (SDD Section 15.3): an enrichment stops being an invisible backend call
    and becomes visible, judge-legible provenance in the glass-box replay.
    """

    provider: str
    indicator: str
    indicator_type: str          # ip | domain | hash | url | query
    status: str                  # ok | not_configured | error | egress_refused
    score: float | None = None   # provider-normalized 0..1 maliciousness, if any
    verdict: str = ""            # short human-readable summary
    source_url: str = ""         # citable source (the citation chip's target)
    fetched_at: str = ""
    cached: bool = False
    detail: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider, "indicator": self.indicator,
            "indicator_type": self.indicator_type, "status": self.status,
            "score": self.score, "verdict": self.verdict,
            "source_url": self.source_url, "fetched_at": self.fetched_at,
            "cached": self.cached, "detail": self.detail,
        }


class EnrichmentCache:
    """On-disk cache keyed by (provider, indicator) hash. Cache-first."""

    def __init__(self, cache_dir: Path) -> None:
        self.dir = cache_dir
        self.dir.mkdir(parents=True, exist_ok=True)
        self.hits = 0
        self.misses = 0

    def _path(self, provider: str, indicator: str) -> Path:
        h = hashlib.sha256(f"{provider}|{indicator}".encode()).hexdigest()[:32]
        return self.dir / f"{provider}-{h}.json"

    def get(self, provider: str, indicator: str) -> EnrichmentResult | None:
        p = self._path(provider, indicator)
        if not p.exists():
            self.misses += 1
            return None
        self.hits += 1
        d = json.loads(p.read_text())
        d["cached"] = True
        return EnrichmentResult(**d)

    def put(self, result: EnrichmentResult) -> None:
        p = self._path(result.provider, result.indicator)
        d = result.as_dict()
        d["cached"] = False
        p.write_text(json.dumps(d, ensure_ascii=False))


def _real_sender(timeout: float = 15.0) -> Sender:
    import httpx

    def send(method: str, url: str, headers: dict,
             params: dict | None, json_body: dict | None) -> tuple[int, Any]:
        with httpx.Client(timeout=timeout) as client:
            r = client.request(method, url, headers=headers, params=params, json=json_body)
            try:
                return r.status_code, r.json()
            except Exception:
                return r.status_code, {"_raw_text": r.text[:2000]}

    return send


class Connector:
    """Base for every outbound connector. Enforces egress, caches, rate-paces."""

    provider = "base"
    #: minimum seconds between live calls, to respect free-tier per-minute caps
    min_interval_s = 0.0

    def __init__(self, cache: EnrichmentCache, sender: Sender | None = None) -> None:
        self.cache = cache
        self._sender = sender or _real_sender()
        self._last_call = 0.0
        self.live_calls = 0

    def _guarded_request(
        self, method: str, url: str, *, headers: dict | None = None,
        params: dict | None = None, json_body: dict | None = None,
    ) -> tuple[int, Any]:
        decision = check_egress(url)
        if not decision.allowed:
            raise EgressRefused(decision.reason)
        if self.min_interval_s:
            wait = self.min_interval_s - (time.monotonic() - self._last_call)
            if wait > 0:
                time.sleep(wait)
        self.live_calls += 1
        self._last_call = time.monotonic()
        return self._sender(method, url, headers or {}, params, json_body)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
