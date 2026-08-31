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

from citinel.audit.ledger import AuditLedger
from citinel.config import settings
from citinel.incidents.builder import build_incidents

# Paths from settings, not __file__: once pip-installed, this module lives in
# site-packages and a __file__-derived root points at the interpreter's own
# directory. The first real deployment hit exactly that.
DETECTIONS_PATH = settings.data_dir / "cache" / "detections.jsonl"
ANOMALIES_PATH = settings.data_dir / "cache" / "anomalies.jsonl"
INCIDENTS_DIR = settings.data_dir / "incidents"

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


def _input_signature() -> tuple[float, float]:
    """(mtime, mtime) of the two input files, 0.0 for a file that doesn't
    exist yet. Used to detect whether there is genuinely new work."""
    return (
        DETECTIONS_PATH.stat().st_mtime if DETECTIONS_PATH.exists() else 0.0,
        ANOMALIES_PATH.stat().st_mtime if ANOMALIES_PATH.exists() else 0.0,
    )


def run_once() -> None:
    """One pipeline cycle: rebuild incidents from whatever detections/
    escalations exist on disk, and verify the audit ledger stayed intact.

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
    ledger = AuditLedger(INCIDENTS_DIR / "ledger.jsonl")
    report = build_incidents(
        DETECTIONS_PATH, ANOMALIES_PATH, INCIDENTS_DIR / "incidents.jsonl", ledger,
    )
    ok, message = ledger.verify_chain()
    log.info("cycle complete: %s | ledger: %s", report.summary(), message)
    if not ok:
        log.error("AUDIT LEDGER INTEGRITY FAILURE: %s", message)
    _last_built_signature = signature


def main() -> int:
    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)
    log.info("citinel worker starting (poll interval %ss)", POLL_INTERVAL_S)

    while _running:
        try:
            run_once()
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
