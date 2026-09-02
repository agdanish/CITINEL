# Next session prompt (written 2 Sep 2026, end of the second wiring pass)

You're picking up CITINEL — Autonomous Cyber SOC (finale 5 Sep 2026). Read `HANDOFF-MEMORY.md` §19–§20 and `dashboard/static/HANDOFF.md` first; check `citinel status` and `curl https://citinel-web.onrender.com/api/source` for ground truth before believing any doc.

## Where things stand
- All 18 console pages read the live service; every operation the product claims has a route (swarm run, gate/execute, deny, rollback, sign-off, reopen, Tavily context, Lyzr handover). Suite: 231 tests. Deployed from `build/stage-1` (Render auto-deploys on push).
- Tavily is genuinely wired (public context per technique/rule, persisted with provenance, labelled not-evidence). Both incidents gathered.
- Lyzr: the base agent (guard + witness) works locally. Three more agent seams exist (`lyzr-triage`, `lyzr-review`, `lyzr-handover`) with Studio recipes in `LYZR-AGENT-CONFIG.md`. **Danish has to build them in Studio and set the ids**; until then those surfaces show "not configured".

## This session's task (ask Danish if he wants a different one)
1. Confirm which Render variables Danish has set (`/api/connectors` on the live site says which are present). If the Lyzr ids are in, exercise each seam once live and fix what breaks; record the frames.
2. If Danish has built the three Studio agents, run one swarm from the console (`RUN THE SWARM` on Replay, ~100K+ input tokens: ask first) so a verdict file carries a real `lyzr_triage`.
3. Then the finale story: which screens, in which order, with which incident (`?id=INC-0417` is the richer one: 2,487 findings, 3 proposals, 6 claims).

## Do not
- Do not fabricate a metric, a count, or a name. The false-positive rate is UNMEASURED; the sign-off is a draft ("we draft, we never file"); response actions hit simulated endpoints only.
- Do not raise Render or Anthropic spend without asking; a swarm run is real money.
- Do not sign off an incident on the live ledger for a test without reopening it after (`POST /api/incidents/{id}/reopen`), or the queue empties.
- Do not touch the pitch deck unless Danish asks. Do not promise a judged prize.
