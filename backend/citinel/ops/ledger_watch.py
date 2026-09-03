"""Scheduled tamper check on the deployed audit ledger.

A hash-chained ledger only protects anything if somebody actually verifies it.
The console verifies on demand, which means the chain is checked exactly when a
human happens to look -- and an attacker who rewrites history is betting that
nobody looks between the edit and the demo. This runs the same check on a
schedule, from outside the web service, and escalates through n8n when the
chain does not hold.

It deliberately talks HTTP rather than reading the file: a cron job gets its
own container and its own filesystem, so it cannot see the web service's disk
at all. Asking the running service is also the more honest test -- it verifies
what the deployment actually serves, not what some other copy of the data says.

Exit codes: 0 intact, 1 broken or unreachable. Render surfaces a non-zero exit
as a failed run, so the dashboard itself becomes the alert of last resort.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone


def _get(url: str, timeout: int = 30) -> tuple[int, dict]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode() or "{}")


def _post(url: str, payload: dict, timeout: int = 20) -> int:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status


def main() -> int:
    base = (os.environ.get("CITINEL_WEB_URL") or "").rstrip("/")
    if not base:
        print("CITINEL_WEB_URL is not set; nothing to verify", file=sys.stderr)
        return 1
    hook = os.environ.get("CITINEL_N8N_WEBHOOK_URL") or ""
    checked_at = datetime.now(timezone.utc).isoformat()

    try:
        status, body = _get(f"{base}/api/ledger/verify")
    except Exception as e:
        alert = {"event": "ledger_unreachable", "detail": str(e),
                 "checked_at": checked_at, "target": base}
        print(json.dumps(alert))
        _notify(hook, alert)
        return 1

    intact = bool(body.get("intact")) and status == 200
    result = {
        "event": "ledger_verified" if intact else "ledger_tamper_suspected",
        "intact": intact, "http_status": status,
        "message": str(body.get("message") or "")[:400],
        "witness": body.get("witness"),
        "checked_at": checked_at, "target": base,
    }
    print(json.dumps(result))
    if not intact:
        # Only an actual failure escalates. A green check every six hours that
        # pages somebody is a check people learn to ignore.
        _notify(hook, result)
        return 1
    return 0


def _notify(hook: str, payload: dict) -> None:
    if not hook:
        print("no CITINEL_N8N_WEBHOOK_URL set; alert not dispatched", file=sys.stderr)
        return
    try:
        code = _post(hook, payload)
        print(f"alert dispatched to n8n, HTTP {code}", file=sys.stderr)
    except Exception as e:  # the check's own verdict still stands
        print(f"alert dispatch failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
