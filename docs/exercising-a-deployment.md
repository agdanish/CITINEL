# Exercising a deployment

`scripts/exercise_production.py` makes the authenticated POSTs that fill the
console's partner panels, then re-reads the deployment to report what actually
landed. Standard library only; no install step.

## When to run it

- **After any deploy to a fresh service or a wiped disk.** Context, sweep,
  brief, handover, corpus advisory and Swytchcode receipts are all artifacts
  written by a POST. A deployment nobody has written to renders them as empty
  panels, which reads as "not built" rather than "not yet run".
- **Before showing the console to anyone** — a judge, a partner, a reviewer.
- **After rotating a partner key**, to confirm the seam still answers rather
  than degrading quietly to `not_configured`.
- **In CI**, on the deployed URL. It exits non-zero when a step fails, so a
  broken seam is a red build instead of a discovery made on stage.

## Running it

```bash
export CITINEL_WRITE_TOKEN=...        # never a CLI argument: arguments land in
                                      # shell history and in `ps` output
python3 scripts/exercise_production.py                       # production
python3 scripts/exercise_production.py --base-url http://localhost:8010
python3 scripts/exercise_production.py --dry-run             # prints, calls nothing
```

Useful flags: `--incident` (default: the record with the most findings),
`--target` (the host for the `isolate_host` proposal), `--brief-wait`,
`--timeout`.

Each step costs partner credits — Tavily queries, one Gemini call, several Lyzr
calls. It is not a health check; do not loop it.

## Reading the output

`PASS` means the seam ran and the panel now has content. `SKIPPED` means it did
not land and says why — usually a credential missing on the deployment, or a
seam answering `not_configured` behind an HTTP 200. `FAIL` means something is
broken and sets a non-zero exit.

Two auth failures are deliberately distinct: **503** with a `CITINEL_WRITE_TOKEN`
message means the deployment has no write token set at all (fix it in the
service's environment, then redeploy); **401** means it has one and yours does
not match it.

The closing SUMMARY ignores the step results and re-reads the deployment: which
partner actors now have frames on the incident's hash chain, which artifact
routes return 200, and whether the ledger still verifies. Trust that section
over the step lines — a POST returning 200 is a claim, a ledger frame is
evidence. Tavily is the one seam with no ledger frame by design; its evidence is
the context and brief artifacts, which the summary checks directly.
