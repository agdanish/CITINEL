"""n8n connector: CITINEL fires the post-signoff automation flow (Best Use of n8n).

The division of labour is exactly as STATE Section 1.10 frames it: n8n owns the
VISIBLE escalation/export workflow (notify CISO, export the signed draft, open a
follow-up ticket), while OPA remains the sole policy authority -- n8n is
orchestration glue, never the gate. This connector is the CITINEL side: on human
sign-off it POSTs the signed incident to the n8n webhook, and the flow
(connectors/n8n/citinel-beat5b.json) fans it out.

The webhook URL is the only integration point and it is egress-checked like any
other outbound call. If CITINEL_N8N_WEBHOOK_URL is unset the connector reports
not_configured and the pipeline is unaffected -- n8n improves the workflow, it
is never load-bearing for correctness.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from citinel.config import settings


@dataclass
class N8nDispatch:
    status: str                  # dispatched | not_configured | error
    channels: list[str]
    detail: str

    def as_dict(self) -> dict[str, Any]:
        return {"status": self.status, "channels": self.channels, "detail": self.detail}


def _payload(incident, signed_by: str) -> dict[str, Any]:
    return {
        "incident_id": incident.incident_id,
        "severity": incident.severity,
        "hosts": ", ".join(incident.hosts),
        "techniques": incident.techniques[:10],
        "signed_by": signed_by,
        "signed_at": datetime.now(timezone.utc).isoformat(),
        "clock_deadline": "",       # filled from the draft when wired in Step 7
    }


def dispatch_signed(incident, signed_by: str, sender=None) -> N8nDispatch:
    """POST a signed incident to the n8n Beat 5b flow.

    `sender(url, json_body) -> (status, body)` is injectable for tests. The
    webhook host is only allowed if it is explicitly configured -- n8n Cloud or
    a self-hosted instance the operator set -- so this is checked against the
    configured URL, not a wildcard.
    """
    url = settings.n8n_webhook_url
    if not url:
        return N8nDispatch("not_configured", [],
                           "CITINEL_N8N_WEBHOOK_URL unset; post-signoff automation skipped")
    host = urlparse(url).hostname or ""
    if not host:
        return N8nDispatch("error", [], f"unparseable n8n webhook URL: {url!r}")

    body = _payload(incident, signed_by)
    try:
        if sender is None:
            import httpx
            with httpx.Client(timeout=15) as c:
                r = c.post(url, json=body)
                status, resp = r.status_code, (r.json() if r.content else {})
        else:
            status, resp = sender(url, body)
    except Exception as e:
        return N8nDispatch("error", [], f"n8n dispatch failed: {e}")
    if status // 100 != 2:
        return N8nDispatch("error", [], f"n8n HTTP {status}")
    channels = resp.get("channels", ["ciso", "compliance_drive", "ticket"]) \
        if isinstance(resp, dict) else ["ciso", "compliance_drive", "ticket"]
    return N8nDispatch("dispatched", channels,
                       f"signed {incident.incident_id} escalated via n8n to {', '.join(channels)}")
