"""CITINEL background worker: `python -m citinel.worker.run`.

This is the Render "worker" service (deploy/render.yaml) -- the Best-Use-of-
Render adversarial audit found this entry point did not exist, so the service
would crash-loop on deploy. Today, before Step 7's swarm exists, its
responsibility is bounded and honest: it re-runs the deterministic pipeline
(telemetry -> OCSF -> Sigma -> anomaly -> incidents) on a schedule and logs its
own liveness, so the worker is a real, observable process rather than a stub
that exits.

Once Step 7 lands, this is where the swarm's per-incident processing loop
attaches: pull CAUGHT incidents, run them through Sentinel -> ... -> Scribe,
write verdicts and drafts back to disk. The polling shape (not a queue
consumer) is deliberate for now -- Redis-backed queueing is a distinct,
larger change the coherence audit flagged, tracked separately rather than
half-built here.
"""

from __future__ import annotations

import logging
import shutil
import signal
import sys
import time
from pathlib import Path

from citinel.agents.pipeline import SwarmPipeline
from citinel.agents.store import save_result
from citinel.audit.ledger import AuditLedger
from citinel.config import settings
from citinel.connectors.lyzr import LyzrLedgerMirror
from citinel.incidents.builder import build_incidents, load_incidents
from citinel.incidents.model import State

# Paths from settings, not __file__: once pip-installed, this module lives in
# site-packages and a __file__-derived root points at the interpreter's own
# directory. The first real deployment hit exactly that.
DETECTIONS_PATH = settings.data_dir / "cache" / "detections.jsonl"
ANOMALIES_PATH = settings.data_dir / "cache" / "anomalies.jsonl"
INCIDENTS_DIR = settings.data_dir / "incidents"
#: Persists ACROSS incidents.jsonl rebuilds (a separate file), unlike incident
#: state itself -- see config.py's auto_swarm comment for why this exists.
#: Real, meaningful mitigation of the re-billing risk; not a full fix for
#: incident identity not surviving a rebuild, which is a separate, larger
#: change.
SWARM_PROCESSED_PATH = INCIDENTS_DIR / ".swarm_processed"

POLL_INTERVAL_S = 300  # re-check for new detections/escalations every 5 min

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s citinel-worker %(levelname)s %(message)s",
)
log = logging.getLogger("citinel.worker")

_running = True
_last_built_signature: tuple[float, float] | None = None


def _handle_shutdown(signum, frame) -> None:
    global _running
    log.info("received signal %s; shutting down after this cycle", signum)
    _running = False


def _already_processed() -> set[str]:
    if not SWARM_PROCESSED_PATH.exists():
        return set()
    return {line.strip() for line in SWARM_PROCESSED_PATH.read_text().splitlines() if line.strip()}


def _mark_processed(incident_id: str) -> None:
    SWARM_PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SWARM_PROCESSED_PATH.open("a", encoding="utf-8") as fh:
        fh.write(incident_id + "\n")


def _run_auto_swarm(pipeline: SwarmPipeline) -> None:
    """Run at most `settings.auto_swarm_max_per_cycle` not-yet-processed
    CAUGHT incidents through the swarm. Real API cost per incident -- the
    cap and the opt-in setting are the safety rails, not a suggestion; see
    config.py's auto_swarm comment for the re-billing risk this exists
    against.
    """
    if not settings.auto_swarm or not pipeline.available:
        return
    processed = _already_processed()
    incidents = load_incidents(INCIDENTS_DIR / "incidents.jsonl")
    candidates = [i for i in incidents
                  if i.state is State.CAUGHT and i.incident_id not in processed]
    if not candidates:
        return
    batch = candidates[:settings.auto_swarm_max_per_cycle]
    log.info("auto-swarm: %d candidate(s), running %d this cycle (cap %d)",
             len(candidates), len(batch), settings.auto_swarm_max_per_cycle)
    for inc in batch:
        try:
            result = pipeline.run(inc)
            save_result(result, INCIDENTS_DIR)
            log.info("auto-swarm: %s -> mode=%s", inc.incident_id, result.mode.value)
        except Exception:
            log.exception("auto-swarm: %s failed; will retry next cycle "
                          "(not marked processed)", inc.incident_id)
            continue
        # Marked processed regardless of mode (including NO_CREDENTIALS/
        # MODEL_REFUSED) -- a run that completed without raising is not a
        # transient failure worth burning tokens on again next cycle. Only an
        # exception (network error, etc.) skips the mark, so that case does
        # retry.
        _mark_processed(inc.incident_id)


def _input_signature() -> tuple[float, float]:
    """(mtime, mtime) of the two input files, 0.0 for a file that doesn't
    exist yet. Used to detect whether there is genuinely new work."""
    return (
        DETECTIONS_PATH.stat().st_mtime if DETECTIONS_PATH.exists() else 0.0,
        ANOMALIES_PATH.stat().st_mtime if ANOMALIES_PATH.exists() else 0.0,
    )


def run_once(pipeline: SwarmPipeline | None = None) -> None:
    """One pipeline cycle: rebuild incidents from whatever detections/
    escalations exist on disk, verify the audit ledger stayed intact, and
    (only if `pipeline` is passed and `settings.auto_swarm` is on) run a
    capped batch of not-yet-processed incidents through the swarm.

    build_incidents() unconditionally rewrites incidents.jsonl and APPENDS
    fresh ledger entries every call -- correct for a one-shot CLI rebuild, but
    not idempotent under polling: three identical cycles produced 9 duplicate
    ledger entries in testing, fabricating "new" detections that never
    happened. Guarded here by input mtimes so a cycle with unchanged inputs is
    a genuine no-op, not a silent audit-trail corruption.
    """
    global _last_built_signature

    if not DETECTIONS_PATH.exists() and not ANOMALIES_PATH.exists():
        log.info("no detections/anomalies cache yet; nothing to build")
        return

    signature = _input_signature()
    if signature == _last_built_signature:
        log.info("inputs unchanged since last cycle; skipping rebuild")
        return

    # AuditLedger.append() is inherently additive (SDD Section 16 finding 4:
    # each entry chains to the previous), so re-opening the same ledger path
    # across cycles preserves history rather than resetting it -- unlike the
    # CLI's `incidents build --fresh`, which is a one-shot rebuild command.
    # sink=LyzrLedgerMirror() is a no-op until CITINEL_LYZR_API_KEY/GUARD_URL are
    # set (record() early-returns unconfigured), so this is safe unconditionally.
    # Without it, the witness half of the ledger-integrity story is silently
    # dead: /api/ledger/verify's compare() would ask Lyzr "what's your head?"
    # and get nothing back, because nothing was ever recorded to it.
    ledger = AuditLedger(INCIDENTS_DIR / "ledger.jsonl", sink=LyzrLedgerMirror())
    report = build_incidents(
        DETECTIONS_PATH, ANOMALIES_PATH, INCIDENTS_DIR / "incidents.jsonl", ledger,
    )
    ok, message = ledger.verify_chain()
    log.info("cycle complete: %s | ledger: %s", report.summary(), message)
    if not ok:
        log.error("AUDIT LEDGER INTEGRITY FAILURE: %s", message)
    _last_built_signature = signature

    if pipeline is not None:
        _run_auto_swarm(pipeline)


def main() -> int:
    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)
    log.info("citinel worker starting (poll interval %ss)", POLL_INTERVAL_S)

    # Built once, outside the loop: constructing a SwarmPipeline verifies
    # both model ids live (L9, GET /v1/models) -- doing that every 5-minute
    # cycle would be a repeated, avoidable call. auto_swarm defaults to False
    # (config.py), so this is a no-op client-less pipeline unless explicitly
    # opted into.
    pipeline = None
    if settings.auto_swarm:
        from citinel.agents.build import build_pipeline
        try:
            pipeline = build_pipeline(AuditLedger(INCIDENTS_DIR / "ledger.jsonl",
                                                  sink=LyzrLedgerMirror()))
            log.info("auto-swarm enabled: up to %d incident(s)/cycle",
                     settings.auto_swarm_max_per_cycle)
        except Exception:
            log.exception("auto-swarm enabled but pipeline construction failed "
                          "(check CITINEL_TRIAGE_MODEL/REASONING_MODEL); "
                          "continuing without it")

    while _running:
        try:
            run_once(pipeline)
        except Exception:
            log.exception("worker cycle failed; will retry next interval")
        for _ in range(POLL_INTERVAL_S):
            if not _running:
                break
            time.sleep(1)

    log.info("citinel worker stopped cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
