"""n8n's other half: reading back what a playbook actually did, and resuming it.

The webhook and the REST API are two different planes, and n8n is explicit
that neither does the other's job -- the API manages and reads workflows and
executions but documents no endpoint that runs one, while a webhook triggers a
run and cannot be queried afterwards. CITINEL uses both, in the two directions
that matter:

  read    GET /api/v1/executions  turns an n8n run into something a reviewer
          can cite. An execution has an id, a status, a start and stop time and
          (with includeData) its own data. That is evidence, and evidence
          belongs on the Audit screen next to every other frame rather than in
          a separate tool a judge has to be told about.

  resume  POST to a Wait node's $execution.resumeUrl. This is the inversion
          worth having: instead of CITINEL asking a human and then telling n8n,
          the playbook itself pauses at a Wait node and hands CITINEL the URL
          that unpauses it. The approval then lives on CITINEL's own Approvals
          screen -- the analyst never leaves the console -- and the workflow
          branches on what they decided. n8n holds the state; CITINEL holds the
          human.

Both degrade to not_configured without their settings, for the same reason the
rest of this codebase does: n8n improves the workflow and is never load-bearing
for correctness.

Egress: the API base and the resume URL are operator-configured or handed back
by the operator's own n8n instance, never derived from parsed telemetry, so
there is nothing here a poisoned log could redirect. https is still required --
an execution payload carries incident data and must not travel in clear text.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from citinel.config import settings

#: n8n's own documented statuses.
EXECUTION_STATUSES = ("canceled", "crashed", "error", "new", "running",
                      "success", "unknown", "waiting")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _https_only(url: str, what: str) -> str | None:
    p = urlparse(url)
    if not p.hostname:
        return f"unparseable {what}: {url!r}"
    if p.scheme != "https":
        return (f"refusing non-https {what} (scheme {p.scheme!r}); "
                "incident data must not travel in clear text")
    return None


def list_executions(limit: int = 20, status: str | None = None,
                    sender=None) -> dict[str, Any]:
    """Recent n8n runs, as evidence. Never raises."""
    base, key = settings.n8n_api_url, settings.n8n_api_key
    if not (base and key):
        return {"status": "not_configured", "executions": [],
                "detail": "CITINEL_N8N_API_URL and CITINEL_N8N_API_KEY are both required"}
    base = base.rstrip("/")
    if (bad := _https_only(base, "n8n API URL")):
        return {"status": "error", "executions": [], "detail": bad}
    if status is not None and status not in EXECUTION_STATUSES:
        return {"status": "error", "executions": [],
                "detail": f"unknown execution status {status!r}; n8n documents {', '.join(EXECUTION_STATUSES)}"}

    url = f"{base}/api/v1/executions"
    params: dict[str, Any] = {"limit": max(1, min(int(limit), 250))}
    if status:
        params["status"] = status
    try:
        if sender is not None:
            code, body = sender("GET", url, {"X-N8N-API-KEY": key}, params, None)
        else:
            import httpx
            with httpx.Client(timeout=20) as c:
                r = c.get(url, headers={"X-N8N-API-KEY": key}, params=params)
                code, body = r.status_code, (r.json() if r.content else {})
    except Exception as e:
        return {"status": "error", "executions": [], "detail": f"n8n API call failed: {e}"}
    if code == 401:
        return {"status": "error", "executions": [],
                "detail": "n8n rejected the API key (401). Settings -> n8n API -> create a key."}
    if code // 100 != 2:
        return {"status": "error", "executions": [], "detail": f"n8n API HTTP {code}"}

    rows = (body or {}).get("data") if isinstance(body, dict) else None
    if not isinstance(rows, list):
        return {"status": "error", "executions": [],
                "detail": "n8n API answered without a data array; nothing can be claimed"}
    return {
        "status": "ok", "fetched_at": _now(), "detail": "",
        "executions": [{
            "id": str(e.get("id", "")),
            "workflow_id": str(e.get("workflowId", "")),
            "state": str(e.get("status", "")),
            "mode": str(e.get("mode", "")),
            "started_at": str(e.get("startedAt") or "")[:19],
            "stopped_at": str(e.get("stoppedAt") or "")[:19],
            "waiting_until": str(e.get("waitTill") or "")[:19],
            "finished": bool(e.get("finished")),
        } for e in rows[:limit] if isinstance(e, dict)],
    }


def resume(resume_url: str, decision: str, approver: str, note: str = "",
           sender=None) -> dict[str, Any]:
    """Unpause a workflow parked on a Wait node, carrying the human's answer.

    The URL is not constructed here on purpose. n8n exposes it at runtime as
    $execution.resumeUrl and its shape is not documented; a community example
    shows /webhook-waiting/<id>, but building that ourselves would be guessing
    at someone else's internals. The playbook hands us the URL, we call it back.
    """
    if not resume_url:
        return {"status": "error", "detail": "no resume URL was supplied"}
    if (bad := _https_only(resume_url, "n8n resume URL")):
        return {"status": "error", "detail": bad}

    payload = {"decision": decision, "approver": approver, "note": note[:500],
               "resumed_at": _now(), "source": "citinel-approvals"}
    try:
        if sender is not None:
            code, body = sender("POST", resume_url, {}, None, payload)
        else:
            import httpx
            with httpx.Client(timeout=20) as c:
                r = c.post(resume_url, json=payload)
                code, body = r.status_code, (r.json() if r.content else {})
    except Exception as e:
        return {"status": "error", "detail": f"n8n resume failed: {e}"}
    if code == 404:
        return {"status": "expired", "detail":
                "n8n does not recognise this resume URL. A Wait node with "
                "Limit Wait Time set will have already moved on."}
    if code // 100 != 2:
        return {"status": "error", "detail": f"n8n resume HTTP {code}"}
    return {"status": "resumed", "detail": f"workflow resumed with decision {decision!r}",
            "resumed_at": payload["resumed_at"],
            "response": body if isinstance(body, dict) else {}}
