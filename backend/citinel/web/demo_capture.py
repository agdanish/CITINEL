"""Step 14 of the build ladder: demo fallback capture.

Freezes real, credentialed API responses so a presenter can replay genuine
captured data on demand -- a safety net against a venue's flaky network or an
exhausted rate limit at the moment it matters most, never a silent substitute
for what the service would otherwise answer.

This is deliberately NOT the same mechanism as data/seed/ (see app.py's
_resolve_data_dir): seed is what a fresh deployment serves when the pipeline
has never run at all. A demo capture is made from a run that DID happen,
scoped to the routes most likely to stall or fail on stage -- and it only
ever answers a request that explicitly opts in (?demo=1); every other request
computes live exactly as before.

Routes never captured, by construction (capture_fixtures() only ever issues
GET requests against the list below):
  - /api/connectors and its "environment" block must always reflect this
    process's actual, current configuration -- freezing it would defeat the
    entire point of that diagnostic.
  - /api/ledger/verify is a live cryptographic check of the CURRENT ledger;
    replaying an old answer would misrepresent what was just verified.
  - Every write route (execute, deny, rollback, signoff, reopen, swarm,
    the context/handover POSTs): a write means something really happened,
    or it is honestly refused. None of that is safe to replay.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


class _HttpClient(Protocol):
    def get(self, url: str) -> Any: ...


#: (label, path template) -- "{id}" is filled in once per incident id passed
#: to capture_fixtures(). Order roughly matches a presenter's tour.
ROUTES: tuple[tuple[str, str], ...] = (
    # /api/source is deliberately absent: like /api/connectors and
    # /api/ledger/verify, its job is reporting THIS process's actual current
    # state (which corpus, whether a capture exists at all) -- freezing it
    # would be self-contradictory the moment a capture is replayed. app.py's
    # _NEVER_DEMO enforces this independently of this list.
    ("policy", "/api/policy"),
    ("corpus", "/api/corpus"),
    ("eval", "/api/eval"),
    ("incidents_summary", "/api/incidents?summary=true"),
    ("incident", "/api/incidents/{id}"),
    ("audit", "/api/incidents/{id}/audit"),
    ("verdict", "/api/incidents/{id}/verdict"),
    ("draft", "/api/incidents/{id}/draft"),
    ("context", "/api/incidents/{id}/context"),
    ("handover", "/api/incidents/{id}/handover"),
)

#: The subset of ROUTES that take an incident id -- captured once per id
#: rather than once overall.
_PER_INCIDENT = {label for label, path in ROUTES if "{id}" in path}


def capture_fixtures(client: _HttpClient, incident_ids: list[str]) -> dict[str, Any]:
    """Walk ROUTES once, plus once per incident id for the per-incident ones.

    Returns the manifest; writing it to disk is the caller's job (see
    scripts/record_demo.py), which is what keeps this trivially testable
    against a FastAPI TestClient with no real credentials or network.
    """
    routes: dict[str, dict[str, Any]] = {}
    for label, template in ROUTES:
        for incident_id in (incident_ids if label in _PER_INCIDENT else [None]):
            path = template.format(id=incident_id) if incident_id else template
            resp = client.get(path)
            routes[path] = {
                "status_code": resp.status_code,
                "body": resp.json() if resp.status_code != 204 else None,
            }
    return {
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "incident_ids": list(incident_ids),
        "routes": routes,
    }


def load_fixtures(path: Path) -> dict[str, Any] | None:
    """None on any problem (missing file, unreadable, malformed JSON) -- a
    broken demo capture must degrade to "no demo mode available", never to a
    startup failure."""
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def find_fixture(manifest: dict[str, Any] | None, path_and_query: str) -> dict[str, Any] | None:
    """`path_and_query` is the literal request target as captured -- e.g.
    "/api/incidents/INC-0417/verdict" or "/api/incidents?summary=true" --
    matched verbatim, never fuzzily, so a captured route can never
    accidentally answer a different one."""
    if not manifest:
        return None
    return manifest.get("routes", {}).get(path_and_query)
