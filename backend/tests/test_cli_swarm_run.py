"""`citinel swarm run` raised NameError on every invocation.

The sink= argument was added to match the other three CLI write sites, each
of which imports LyzrLedgerMirror locally inside its own function. This one
did not, so the documented way to run the swarm from a shell died at the
ledger line -- after argument parsing, after the incident was found, before
any model was called. No test reached that line, which is why it survived a
full audit; found by actually running the command during an end-to-end check.
"""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from citinel.cli import app
from citinel.config import REPO_ROOT, settings


def test_swarm_run_reaches_the_pipeline_without_a_nameerror(tmp_path, monkeypatch):
    # One real incident is enough to get past the "no incident" guard, which
    # sits BEFORE the broken line; the failure only reproduces past it.
    src = REPO_ROOT / "data" / "incidents" / "incidents.jsonl"
    first = next(l for l in src.read_text().splitlines() if l.strip())
    inc_id = json.loads(first)["incident_id"]
    (tmp_path / "incidents.jsonl").write_text(first + "\n")

    # No credentials: build_pipeline returns an unavailable pipeline and the
    # command exits 1 with a plain message. That exit happens AFTER the ledger
    # line, so reaching it proves the import is there.
    monkeypatch.setattr(settings, "anthropic_api_key", None)
    monkeypatch.setattr(settings, "lyzr_api_key", None)

    r = CliRunner().invoke(app, ["swarm", "run", inc_id, "--incidents-dir", str(tmp_path)])
    assert "NameError" not in (r.output or ""), r.output
    assert r.exception is None or isinstance(r.exception, SystemExit), repr(r.exception)
    # This message is printed AFTER the ledger line, so seeing it proves the
    # import is present. (The ledger file itself is only created on first
    # append, so its existence is not the right thing to assert.)
    assert r.exit_code == 1 and "no Anthropic credentials" in r.output, r.output
