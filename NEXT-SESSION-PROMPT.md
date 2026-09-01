You're picking up CITINEL — Autonomous Cyber SOC, a Decode SIH 2026 hackathon
project (Team AeroFyta, Chennai Institute of Technology), finale 5 Sep 2026.
Step 7 (the agent swarm) is done and confirmed live (1 Sep). **As of 2 Sep the
dashboard has started reading the live service: Queue, Audit and Evidence are
wired and browser-verified; the other 15 pages are not.** If you inherit a memory saying
"the dashboard is not wired at all" or "Step 7 is blocked," both are stale;
verify against `citinel status` and `git status`, not memory.

Before doing anything else, read these files in `/Users/danish/CITINEL/` in
this order:
1. `HANDOFF-MEMORY.md` — read it in full. **§18 (the 2 Sep dashboard-wiring
   session), §16 (Step 7) and §17 (open items) matter most.** Sections 1–15
   are historical record, still true, superseded where §16–§18 say so —
   follow the "supersedes" notes rather than section order.
2. `dashboard/static/HANDOFF.md` — the wiring manifest for the console. Its
   §1 explains the seam (`api.js`) and why the badge is derived from what a
   page *actually read* (`API.consumed`), its §2 table says which pages are
   wired. Keep it in step with `API.PAGES` when you wire a page.
3. `git log --oneline` — the 2 Sep work is committed and pushed. Render
   auto-deploys `build/stage-1`, so **every push is a deploy**; that is
   Danish's standing instruction since 2 Sep ("hereafter we will deploy
   online"). After a push, confirm with
   `curl -s https://citinel-web.onrender.com/api/source`.
4. `CITINEL-SDD.md` / `CITINEL-PROPOSAL.md` only if you need the original spec.
5. `PARTNER-ONBOARDING.md`, `PARTNER-SESSION-NOTES.md`, `STARTUPED-GTM-PLAYBOOK.md`
   for sponsor-track and GTM-award status.

## What NOT to do

- **Do not re-run the dashboard-wiring audit, the deep-research passes, the
  adversarial partner-track audit, or the Queue-wiring review.** All recorded
  (HANDOFF-MEMORY §12–§13, §15, §18). The audit's per-page detail is in the
  workflow journal named in §15; §18 says which verdicts still stand.
- **Do not assume Replay/Confidence became wireable because Step 7 runs.**
  §18's first bullet: the swarm's verdict/claims/citations/proposals are
  printed and discarded; the ledger records facts only. Wiring those pages
  needs a persistence decision plus a paid re-run — Danish's call, ask first.
- **Do not raise Render/Anthropic spend without asking first**, even a small
  amount. Every swarm run is real money; every model-tier choice is a decision.
- **Do not offer a "guaranteed win" on any judged prize.** Rubric-completeness
  honesty instead.
- **Do not re-litigate** the Gemini/CodeMate tracks, shortlist status, or
  eligibility — all resolved (§9/§10).
- **Do not blanket-wire the remaining pages.** They are hand-crafted narrative
  prototypes (§15). One page at a time: read it in full, map every rendered
  value to a real field or cut it, keep the three states that never blend
  (reading → live → authored fallback), leave the badge to `api.js`, swap
  content not layout, honour `?id=`, verify in the browser preview. Queue,
  Audit and Evidence are the worked examples.
- **Do not trust a browser screenshot over a DOM read** for verification this
  console; the pane's screenshot tooling was flaky on 2 Sep. Read the badge,
  `window.CITINEL_API.consumed`, and the rendered text through
  `javascript_tool`. And bust the HTTP cache once for any URL the browser had
  loaded before the `Cache-Control: no-cache` middleware went in
  (`fetch(url, {cache:'reload'})`).

## This session's task: continue wiring, one page at a time

Run `cd /Users/danish/CITINEL/backend && ./.venv/bin/citinel status` first,
then start the preview server (`.claude/launch.json` → `citinel-dashboard`,
port 8000) and open a page with `?force=console` — the hidden browser pane
reports zero width and `route.js` would otherwise bounce you to Narrow.

Recommended order for the remaining PARTIAL pages, by value ÷ risk:
1. **Shell** (`uses: ['incidents']` → add `policy`, `ledgerVerify`) — state
   and severity tallies, clause count, ledger entry count are clean reads
   (the audit's diff is in §15's journal, entry 9); label the eps meter and
   statutory clocks as authored or cut them.
2. **Overview** — highest visibility, most elaborate; read §15's warning first.
3. **Compliance** (`draft`, `incident`) — the draft endpoint is real and now
   returns the guard screen too; "we draft, we never file" must survive.
4. Then Handover, Narrow, Settings, Entry. Eval already has a live route
   (`/api/eval`) that its page does not read yet.

Manual items only Danish can do, still open (§17): n8n webhook URL into
`.env`/Render, the Lyzr Studio agent (recipe in `connectors/lyzr.py`'s
docstring), the Swytchcode credit claim. After any swarm run that should show online,
copy `data/incidents/ledger.jsonl` over `data/seed/ledger.jsonl` and push
(§18 deploy caveat). Then
Step 14 (demo fallback capture), the one unbuilt ladder step.

Don't guess at anything time-sensitive (shortlist status, event dates,
credit-claim deadlines) — recompute or ask rather than trusting a number
that may have gone stale between sessions.
