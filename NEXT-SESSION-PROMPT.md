You're picking up CITINEL — Autonomous Cyber SOC, a Decode SIH 2026 hackathon
project (Team AeroFyta, Chennai Institute of Technology), finale 5 Sep 2026.
**Step 7 (the agent swarm) is done and confirmed live as of 1 Sep 2026** —
this is the biggest change since any earlier handoff. If you inherit a stale
memory saying Step 7 is "blocked" or "pending," it's wrong; verify against
`citinel status`, not memory.

Before doing anything else, read these files in `/Users/danish/CITINEL/` in
this order:
1. `HANDOFF-MEMORY.md` — read it in full. **§16 (Step 7) and §17 (current
   open items) matter most; §15 covers everything else the 31 Aug–1 Sep
   session touched.** §1's status line is current as of 1 Sep. Sections 1–14
   are historical record, still true, mostly superseded by §15–§17 where they
   overlap — the doc marks this explicitly, follow the "supersedes" notes
   rather than trusting section order.
2. `git log --oneline` in the repo, then `git log -1 <hash>` on the most
   recent 5-10 commits — the engineering detail (the exact bugs found, the
   exact fix, real live-tested numbers) lives in commit messages at the same
   density as the handoff doc. Don't re-derive facts already established.
3. `CITINEL-SDD.md` / `CITINEL-PROPOSAL.md` if you need the original spec —
   lower priority than the above for picking up current work.
4. `PARTNER-ONBOARDING.md` and `PARTNER-SESSION-NOTES.md` (new 1 Sep) for
   sponsor-track status; `STARTUPED-GTM-PLAYBOOK.md` for the GTM award.

## What NOT to do

- **Do not re-run the dashboard-wiring audit, the deep-research passes, or
  re-derive OCSF/Sigma/BOTS-extraction facts, or the adversarial partner-track
  audit.** All recorded once, expensively. HANDOFF-MEMORY §12–§13/§15 has the
  numbers.
- **Do not offer a "guaranteed win" on any judged prize.** Refused before,
  refused again if asked. Rubric-completeness honesty instead.
- **Do not re-litigate the "Best Use of Gemini"/"Best Use of CodeMate" tracks'
  existence**, or Danish's shortlist/eligibility status — all resolved,
  HANDOFF-MEMORY §9/§10.
- **Do not assume Step 7 is still blocked, and do not re-verify the Anthropic
  key from scratch** — it's confirmed working live (§16). Do check
  `citinel status` for current build-ladder state before making any claim
  about what's built, since that's the one thing genuinely worth re-checking
  every session (it reads real files on disk).
- **Do not blindly wire the dashboard to live data as a blanket pass.**
  HANDOFF-MEMORY §15 found that most pages are elaborately hand-crafted
  narrative prototypes, not thin templates — a naive data-swap breaks
  layout math and replaces a polished demo with a thinner real one. If this
  work resumes, scope it page-by-page, verify each one, don't rush all 18.
- **Do not raise Render/Anthropic spend without asking first**, even for a
  small amount — this project's whole session history treats every dollar
  and every model-tier choice as a real decision, not a rounding error.

## What to actually do

Run `cd /Users/danish/CITINEL/backend && ./.venv/bin/citinel status` first —
ground truth for build state, more current than this prompt will be. Then
read HANDOFF-MEMORY.md §17's numbered list in full — it's the current,
honest open-items list, in a rough priority order already reasoned through:

1. Confirm whether the last Step 7 prompt-fix verification run (in progress
   when the prior session ended) actually completed successfully — check the
   audit ledger's most recent `marshal` entry, or just run
   `citinel swarm run INC-0417` again live.
2. The dashboard-to-live-data wiring is the single highest-value piece of
   unfinished work — Step 7 now gives several previously-impossible pages
   (Replay, Confidence) something real to show. Scope carefully per the
   warning above.
3. Manual items only Danish can do: n8n webhook URL into `.env`, the Lyzr
   Studio agent (recipe is in `connectors/lyzr.py`'s docstring), the
   Swytchcode credit claim.
4. Step 14 (demo fallback capture) is the one remaining unbuilt ladder step.

Don't guess at anything time-sensitive (shortlist status, event dates,
credit-claim deadlines) — recompute or ask rather than trusting a number
that may have gone stale between sessions.
