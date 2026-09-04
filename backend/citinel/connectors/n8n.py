"""n8n connector: CITINEL fires the post-signoff automation flow (Best Use of n8n).

The division of labour is exactly as STATE Section 1.10 frames it: n8n owns the
VISIBLE escalation/export workflow (notify CISO, export the signed draft, open a
follow-up ticket), while OPA remains the sole policy authority -- n8n is
orchestration glue, never the gate. This connector is the CITINEL side: on human
sign-off it POSTs the signed incident to the n8n webhook, and the flow
(connectors/n8n/citinel-beat5b.json) fans it out.

The webhook URL is the only integration point. It does NOT go through the
Step 9 static egress allow-list (EGRESS_ALLOW) the way enrichment lookups
do, and that is a deliberate difference, not an oversight: EGRESS_ALLOW is
an exact-host match with no wildcards, because enrichment indicators are
attacker-influenced (a poisoned log could try to steer where a "lookup"
goes) and a fixed list is the right defense for that threat. The n8n
webhook host is operator-configured in `.env`, never attacker-reachable --
there is nothing for a poisoned log to redirect, since the destination
never comes from parsed content. What this module DOES enforce: https-only,
so a misconfigured plain-http URL can't leak the signed incident payload in
clear text. If CITINEL_N8N_WEBHOOK_URL is unset the connector reports
not_configured and the pipeline is unaffected -- n8n improves the workflow,
it is never load-bearing for correctness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from citinel.config import settings


@dataclass
class N8nDispatch:
    status: str                  # dispatched | partially_dispatched | not_configured | error
    channels: list[str]
    detail: str
    failed_channels: list[str] = field(default_factory=list)
    #: n8n's own id for the run this dispatch started, when the playbook
    #: returns one. It is what makes an automated action citable afterwards:
    #: with it the run can be read back through the REST API, replayed, and
    #: shown on the Audit screen instead of living only inside n8n.
    execution_id: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"status": self.status, "channels": self.channels,
                "failed_channels": self.failed_channels, "detail": self.detail,
                "execution_id": self.execution_id}


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
    parsed = urlparse(url)
    if not parsed.hostname:
        return N8nDispatch("error", [], f"unparseable n8n webhook URL: {url!r}")
    if parsed.scheme != "https":
        return N8nDispatch("error", [],
                           f"refusing non-https n8n webhook URL (scheme {parsed.scheme!r}); "
                           "the signed incident payload must not travel in clear text")

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

    if not isinstance(resp, dict) or "channels" not in resp:
        # A response that doesn't say which channels actually succeeded is
        # not evidence of success -- reporting one anyway would be the exact
        # class of fabricated claim CITINEL exists to refuse (see
        # verify_chain's "absence, not integrity"). Prior versions of this
        # function defaulted to claiming all three channels dispatched here;
        # that was wrong, and the SHA-256-chained audit ledger recorded it.
        return N8nDispatch("error", [],
                           f"n8n response did not report which channels succeeded "
                           f"(got: {resp!r}); nothing can be honestly claimed as dispatched")

    channels = list(resp.get("channels", []))
    failed = list(resp.get("failed_channels", []))
    # A playbook that returns its own execution id turns a notification into a
    # record: `Respond to Webhook` can include {{ $execution.id }}, and once it
    # does the run is readable, replayable and citable through the n8n API.
    execution_id = str(resp.get("execution_id") or resp.get("executionId") or "")
    status_word = "partially_dispatched" if failed else "dispatched"
    detail = f"signed {incident.incident_id} escalated via n8n to {', '.join(channels) or 'no channels'}"
    if failed:
        detail += f"; FAILED: {', '.join(failed)}"
    return N8nDispatch(status_word, channels, detail, failed_channels=failed,
                       execution_id=execution_id)
