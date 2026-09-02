#!/usr/bin/env python3
"""Step 14 of the build ladder: demo fallback capture.

Runs against a live, running citinel-web (started separately, with real
credentials, against the corpus you want frozen) and saves its exact
responses as data/seed/demo-capture.json -- see
backend/citinel/web/demo_capture.py's module docstring for what this is and
is not, and which routes it deliberately never touches.

Usage:
    # in one terminal: a real server with real credentials
    cd backend && uvicorn citinel.web.app:app --port 8000

    # in another:
    python scripts/record_demo.py
    python scripts/record_demo.py --incident INC-0417 --incident INC-0416
    python scripts/record_demo.py --base-url http://localhost:8000 --out data/seed/demo-capture.json

Only GET requests are ever issued (see demo_capture.ROUTES) -- this script
cannot execute an action, spend a rollback token, or write a sign-off. The
network calls it triggers indirectly (a swarm's saved verdict is read, not
re-run; /draft, /context, /handover DO call Lyzr/Tavily live if those routes
haven't been asked before and aren't already cached) are the same ones the
console itself makes when a person clicks through it by hand.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

import httpx  # noqa: E402

from citinel.web.demo_capture import capture_fixtures  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--base-url", default="http://localhost:8000")
    p.add_argument("--incident", action="append", dest="incidents", default=None,
                   help="repeatable; defaults to every incident /api/incidents reports")
    p.add_argument("--out", default=str(REPO_ROOT / "data" / "seed" / "demo-capture.json"))
    args = p.parse_args()

    with httpx.Client(base_url=args.base_url, timeout=120.0) as client:
        incidents = args.incidents
        if not incidents:
            r = client.get("/api/incidents")
            r.raise_for_status()
            incidents = [i["incident_id"] for i in r.json()]
        if not incidents:
            print("no incidents reported by the server; nothing to capture", file=sys.stderr)
            return 1

        print(f"capturing against {args.base_url} for {', '.join(incidents)} ...")
        manifest = capture_fixtures(client, incidents)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    routes = manifest["routes"]
    ok = sum(1 for r in routes.values() if r["status_code"] == 200)
    print(f"wrote {out} -- {len(routes)} routes captured, {ok} returned 200, "
          f"captured_at={manifest['captured_at']}")
    for path, r in sorted(routes.items()):
        if r["status_code"] != 200:
            print(f"  non-200: {r['status_code']}  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
