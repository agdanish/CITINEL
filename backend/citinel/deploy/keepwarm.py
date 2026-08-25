"""Pre-warm the free-tier Render web service so the demo QR never cold-starts.

Render free web services spin down after 15 minutes of inactivity, with a
30-60s cold start on the next request. The Blueprint runs this every 10 minutes
as a cron so the service the QR code points at stays warm through judging.
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    host = os.environ.get("CITINEL_WEB_URL", "")
    if not host:
        print("CITINEL_WEB_URL not set; nothing to warm")
        return 0
    url = host if host.startswith("http") else f"https://{host}"
    url = url.rstrip("/") + "/healthz"
    try:
        import httpx

        r = httpx.get(url, timeout=30)
        print(f"warmed {url} -> HTTP {r.status_code}")
        return 0
    except Exception as e:  # a warm-up failure must never fail the cron
        print(f"warm-up call to {url} failed: {e}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
