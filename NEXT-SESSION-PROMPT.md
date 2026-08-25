You're picking up CITINEL — Autonomous Cyber SOC, a Decode SIH 2026 hackathon
project (Team AeroFyta, Chennai Institute of Technology). The application
build is now underway (started 24–25 Aug 2026) — this is different from
earlier handoffs that said "zero application code exists." Read
HANDOFF-MEMORY.md §1 and §12–§14 before assuming anything about build state.

Before doing anything else, read these files in `/Users/danish/CITINEL/` in
this order:
1. `HANDOFF-MEMORY.md` — read it in full, all 14 sections. §12–§14 (the newest)
   supersede §9 and §11's "paused" framing; §1's status line is now accurate,
   not the old "zero application code" claim. Sections 1–8 are historical
   record from before the build — still true, still useful, just not current
   state.
2. `CITINEL-SDD.md` — the 23-section spec-driven-development document.
3. `CITINEL-PROPOSAL.md` — the narrative pitch version.
4. `git log --oneline` in the repo, then read a few recent commit messages in
   full (`git log -1 <hash>`) — the engineering *why*, the bugs found and
   fixed, and the exact numbers (extraction recovery rates, test counts,
   adversarial-audit scores) live in commit messages, not duplicated in the
   handoff doc. Don't re-derive facts already established there.
5. `PARTNER-ONBOARDING.md` and `STARTUPED-GTM-PLAYBOOK.md` — the sponsor-track
   action documents already handed to Danish.

## What NOT to do

- **Do not re-run deep research, the adversarial partner-track audit, or
  re-derive the OCSF/Sigma/BOTS-extraction facts.** All verified once,
  expensively, and recorded. HANDOFF-MEMORY §12–§13 has the numbers and the
  audit journal path if raw detail is ever needed.
- **Do not offer a "guaranteed win" on any judged prize** (the Bharat Pragati
  main track or any of the 8 partner "best use" tracks) even if asked
  directly, even more than once. This was asked for explicitly in the prior
  session and refused on the project's own standing rule (STATE §1.4/§5.1:
  "not a win guarantee — eligibility is necessary, not sufficient"). Give
  rubric-completeness honesty instead: what's built, what's genuinely tested,
  what a skeptical judge would still deny and why.
- **Do not re-litigate whether the "Best Use of Gemini" / "Best Use of
  CodeMate" tracks exist.** Danish stated both are real, from private
  organizer channels this assistant cannot access. Two live fetches of the
  public event page don't show either — that's already been surfaced to him
  once (HANDOFF-MEMORY §13). Proceed on his word; don't ask again.
- **Do not start Step 7 (the agent swarm) without confirming a valid
  `CITINEL_ANTHROPIC_API_KEY` is actually in `.env` first** — check, don't
  assume. It is the single blocking dependency for the rest of the build and,
  per the adversarial audit, for most of the 8 partner-prize tracks too.

## What to actually do

Run `cd /Users/danish/CITINEL/backend && ./.venv/bin/citinel status` first —
it reads real files on disk, so it's the ground truth for build progress, more
current than this prompt will be by the time you read it. Check whether `.env`
now has a real Anthropic key (`grep ANTHROPIC_API_KEY .env` — never print the
value). If it does, Step 7 is very likely the highest-leverage next build
step — confirm with Danish, don't just start.

Then surface, early and plainly, whatever in HANDOFF-MEMORY §10's open-items
list is still genuinely unresolved and time-sensitive as of today's date —
particularly the shortlist outcome (item 1) and Preethi's enrollment status
(item 7), both still open as of the last update and both able to invalidate
the whole finale plan if wrong. Don't guess at their status; ask.
