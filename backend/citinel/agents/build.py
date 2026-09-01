"""Construct a real SwarmPipeline: the one place credentials become a client.

Every other module in this package takes a `Transport`/`VerifiedModel` as a
parameter and never reaches for `settings.anthropic_api_key` itself -- that
discipline is what keeps `pipeline.py` testable with a fake client. This
module is where the wiring actually happens, once, for real callers (the CLI,
the worker). Two failure classes, deliberately different:

  ModelNotConfigured / ModelNotVerified   -- a config problem (L9). Raise with
                                             a message an operator can act on.
  no Anthropic key at all                 -- not a config *error*: the
                                             pipeline is designed to run
                                             without one (Mode.NO_CREDENTIALS).
                                             `build_pipeline()` returns a
                                             pipeline with no transports
                                             rather than raising, so a caller
                                             that just wants "run whatever is
                                             available" doesn't need a
                                             try/except around this call.
"""

from __future__ import annotations

from datetime import datetime, timezone

from citinel.agents.models import Role, verify
from citinel.agents.pipeline import SwarmPipeline
from citinel.agents.transport import Transport
from citinel.audit.ledger import AuditLedger
from citinel.config import settings
from citinel.connectors.base import EnrichmentCache
from citinel.connectors.enrichment import EnrichmentSquad
from citinel.connectors.lyzr import AgentObserver, LyzrObserver, NullObserver


def _observer() -> AgentObserver:
    if settings.lyzr_api_key and settings.lyzr_guard_url:
        return LyzrObserver()
    return NullObserver()


def _enrichment_squad() -> EnrichmentSquad | None:
    # Additive, not required -- see SwarmPipeline's own docstring. Skipped
    # entirely (None) only when NONE of the three providers are configured;
    # each connector still degrades to not_configured individually for a
    # single missing key, same as everywhere else those connectors are used.
    if not (settings.tavily_api_key or settings.virustotal_api_key or settings.abuseipdb_api_key):
        return None
    return EnrichmentSquad(EnrichmentCache(settings.data_dir / "cache" / "enrichment"))


def build_pipeline(ledger: AuditLedger) -> SwarmPipeline:
    """A real SwarmPipeline. No credentials -> a pipeline that reports
    NO_CREDENTIALS per-incident, matching pipeline.py's own designed
    degradation path -- this function does not special-case that itself.
    """
    if not settings.anthropic_api_key:
        return SwarmPipeline(ledger, observer=_observer())

    import anthropic
    headers = {}
    if settings.anthropic_workspace_id:
        headers["anthropic-workspace-id"] = settings.anthropic_workspace_id
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key, default_headers=headers)
    now = datetime.now(timezone.utc).isoformat()

    # L9: both roles verified live against GET /v1/models before either is
    # used. A retired/mistyped id fails here, at startup, not mid-investigation.
    triage_model = verify(client, Role.TRIAGE, now=now)
    reasoning_model = verify(client, Role.REASONING, now=now)

    triage = Transport(client, triage_model)
    reasoning = Transport(client, reasoning_model)
    return SwarmPipeline(ledger, triage=triage, reasoning=reasoning,
                         enrichment=_enrichment_squad(), observer=_observer())
