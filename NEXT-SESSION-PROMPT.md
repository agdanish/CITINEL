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
- **Do not assume Step 7 is still blocked or unverified, and do not
  re-verify the Anthropic key from scratch** — it's confirmed working live
  end-to-end, including the final prompt-fix run (§16, §17 item 1). Do check
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

## This session's task: start wiring the dashboard to live data

Run `cd /Users/danish/CITINEL/backend && ./.venv/bin/citinel status` first —
ground truth for build state, more current than this prompt will be.

**This is the explicit task for this session, chosen by Danish 2 Sep 2026.**
Do not re-litigate whether it's the right next thing to do — it's already
decided. Read HANDOFF-MEMORY.md §15 (the audit's findings) and §17 item 2
before touching any page, then work it properly, not as a blanket pass:

- **The audit already ran** (`citinel-full-wiring-audit`, §15) — don't
  re-run it. Verdict: 11 of 18 pages are `PARTIAL` (real data exists but is
  entangled with fictional demo content that needs cutting cleanly, not
  crudely), 7 are `NOT_WIREABLE_TODAY` (Replay, Confidence, Approvals,
  Corpus, Executive, Demo, Policy). Some of the `NOT_WIREABLE_TODAY` pages —
  Replay, Confidence — may have moved to wireable now that Step 7 produces
  real verdicts/citations/proposals; check before assuming the audit's verdict
  on those two is still current, but trust it for the rest.
- **The seam already exists and is unused.** `api.js` has `live: true` flags
  on 7 real backend endpoints that no page's script actually calls yet.
  Wiring means calling what's already there, not inventing a new seam.
- **Most pages are hand-crafted narrative prototypes, not thin templates**
  (confirmed by reading Overview, Audit, Policy in full — §15). A naive
  data-swap breaks layout math and replaces a polished demo with a thinner
  real one. Pick one `PARTIAL` page, read it in full before editing, wire it,
  verify it renders correctly in the browser preview, then move to the next.
  Don't attempt all 11 in one pass.
- The pages are local, hand-editable files (`dashboard/static/*.dc.html` +
  `api.js`) — wiring is a code change, not a design change, so no Claude
  Design canvas round-trip is normally needed. Only if a page genuinely needs
  a layout/visual change beyond swapping in live data, say so and give Danish
  the exact prompt to paste into that canvas instead of guessing at layout
  changes yourself (§8 for how that canvas relates to this repo).

Once dashboard wiring is genuinely underway or a natural stopping point is
reached, the rest of §17's list is still open in this order: manual items
only Danish can do (n8n webhook URL into `.env`, the Lyzr Studio agent —
recipe in `connectors/lyzr.py`'s docstring, the Swytchcode credit claim), then
Step 14 (demo fallback capture), the one remaining unbuilt ladder step.

Don't guess at anything time-sensitive (shortlist status, event dates,
credit-claim deadlines) — recompute or ask rather than trusting a number
that may have gone stale between sessions.
