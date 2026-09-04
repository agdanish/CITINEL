# Claude memory export for CITINEL (4 September 2026)

*This is the complete contents of Claude Code's persistent memory for this project,
exported so a new account or a new machine can restore it. Each file below is one memory.*

## How to restore

On the same Mac, the memory directory already exists and is keyed by the project path, not by
the account, so a new Claude Code account opened in `/Users/danish/CITINEL` reads it as is:

```
/Users/danish/.claude/projects/-Users-danish-CITINEL/memory/
```

On a different machine, recreate that directory (the path segment is the project path with
`/` replaced by `-`) and write each block below to the file named in its heading, verbatim,
including the frontmatter. `MEMORY.md` is the index Claude loads every session.

---

## File: `MEMORY.md`

````markdown
- [DEMO MORNING 5 Sep](project_citinel_demo_morning_5sep.md): run this first on demo day: preflight GO, arm the laptop, green dot, warm the Compliance draft, Auto-Deploy off, INC-0417 must read CAUGHT
- [Account migration 4 Sep](project_citinel_account_migration_4sep.md) — continuity package lives in the repo: NEXT-SESSION-PROMPT.md, HANDOFF-MEMORY.md §21-§22, docs/SESSION-2026-09-03-04-*.md, docs/MEMORY-EXPORT.md
- [State 4 Sep evening](project_citinel_state_4sep_evening.md) — origin in sync at 3abfb30, preflight GO, Part 3 in progress; "unpushed commits" claim is stale
- [Console gotchas](project_citinel_console_gotchas.md) — DC template holes inside SVG text do not paint; a11y.css header-span override; sc-if truthiness; x-import Buttons need on-click; eval seed fallback
- [New-laptop runbook](project_citinel_new_laptop_runbook.md) — every new laptop must be ARMED in Settings (name + token, 12 h) before any write works; full steps in repo RUNBOOK-NEW-LAPTOP.md; never re-run the swarm on demo day
- [Pending manual steps](project_citinel_pending_manual_steps.md) — 4 Sep: `swy login` + 2 Swytchcode tokens, and TAVILY/ANTHROPIC keys in Render's citinel-shared; all surrounding code is already live
- [Build status](project_citinel_build_status.md) — **15/15 steps built** (Step 14 shipped 2 Sep), 252 tests; check `citinel status`, not assumptions
- [Dashboard wiring state](project_citinel_dashboard_wiring.md) — 2 Sep second pass: all 18 pages live, every claimed op has a route, verdicts persisted, Tavily + 3 Lyzr agent seams wired (agents not yet built in Studio); API name-collision + reopen-after-test-signoff traps
- [Deploy on push + partner credits](feedback_deploy_on_push_partner_credits.md) — 2 Sep standing direction: every push to build/stage-1 is a Render deploy; use all partner credits on genuinely wired seams; ask which Lyzr Studio agents exist before designing new ones; Render-side secrets are Danish's to set
- [Anthropic key blocker](project_citinel_anthropic_key_blocker.md) — RESOLVED 1 Sep; kept for 3 real live-API bugs found (workspace-id header, capability-parsing, SDK max_tokens ceiling) + current model IDs
- [Sponsor tracks (8) + partner session notes](project_citinel_sponsor_tracks.md) — confirmed FINALIST; 5/8 tracks are code (rest non-code); Lyzr now 7 agents (1 built, 6 recipes ready), Tavily 4 query kinds, all wired 3 Sep
- [PPT deprioritized](feedback_ppt_deprioritized.md) — never bring up the pitch deck unprompted; Danish will ask when he wants it
- [QR code confirmed false](project_citinel_qr_confirmed_false_claim.md) — deck QR resolves to Danish's portfolio, not a prototype; fixable via redirect
- [Judged-prize honesty](feedback_judged_prize_honesty.md) — never guarantee a judged/competitive prize even under repeated pressure
- [Verify against real data](feedback_verify_against_real_data.md) — CITINEL logic needs the real BOTS corpus run, not just code review
- [Token-budget orchestration](feedback_token_budget_orchestration.md) — prefer direct engineering over workflows when tokens are flagged tight
- [Model tier discipline](feedback_model_tier_discipline.md) — default Haiku for smoke tests/subagents; never Sonnet/Opus without asking first
- [RTK token optimization](feedback_rtk_token_optimization.md) — trust the rtk hook for plain commands; stop using python3 heredocs/Read tool for edits
- [Real value, not padding](feedback_real_value_not_padding.md) — every integration screened as "genuinely wired or decorative"; confirmed 3 independent ways
- [Git identity fix](project_citinel_git_identity.md) — local user.email was wrong (attributed to Preethisiva2416, not agdanish); fixed 2 Sep, history intentionally left as-is
````

## File: `feedback_deploy_on_push_partner_credits.md`

````markdown
---
name: feedback-deploy-on-push-partner-credits
description: "Danish's standing direction from 2 Sep 2026 — deploy online from now on (every push to build/stage-1 is a Render deploy), use all partner credits effectively, and use many Lyzr AI agents"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2955f624-cd86-4cfd-8d0c-91e00cfb1c37
  modified: 2026-09-01T21:50:42.809Z
---

On 2 Sep 2026 Danish said: "hereafter we will deploy online and use all partner credits effectively, We use many agents in Lyzer AI." Taken as a standing instruction, and acted on: the dashboard-wiring work was committed and pushed the same day (Render auto-deploys `build/stage-1`).

**Why:** the finale is 5 Sep 2026; the deployed console is what judges scan (the deck's QR), and the partner tracks are judged on demonstrated use of each partner's product, so unused credits are wasted rubric points.

**How to apply:**
- Committing and pushing to `build/stage-1` no longer needs a per-change go-ahead; it IS the deploy. Still say in the final message what was pushed, and confirm the live site after (`curl https://citinel-web.onrender.com/api/source`). Never push a broken suite.
- Partner credits: prefer spending them on integrations that are genuinely wired to a real call site ([[feedback-real-value-not-padding]] still governs). Lyzr: ask which Studio agents Danish has built before designing new ones; wire each to a real seam or say plainly it would be decorative.
- Render-side secrets (Lyzr key/guard URL/agent id, n8n webhook, Swytchcode key) are `sync: false` in render.yaml and must be set by Danish in the Render dashboard; Claude cannot. Say which are missing rather than assuming they are set. See [[project-citinel-dashboard-wiring]].
````

## File: `feedback_judged_prize_honesty.md`

````markdown
---
name: feedback-judged-prize-honesty
description: "Never frame a judged/competitive prize as a guaranteed win, even under repeated direct pressure"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7a839a32-b1bb-4e57-8861-efd8031ae210
  modified: 2026-08-31T05:17:10.576Z
---

Never claim or imply a "100% guaranteed" win on any judged, competitive prize
(hackathon best-use tracks, main-track wins, any award decided by external
judges comparing multiple teams). Separate the controllable half (does the
build meet 100% of the *stated* criteria, with genuine depth) from the
uncontrollable half (will judges pick this over other teams) — drive the
first to the ceiling, never attach a probability or guarantee to the second.

**Why:** on [[project-citinel-build-status]], Danish asked directly, more
than once, for a "100% guaranteed" win across 8 partner prizes plus the main
track, and even after being told this can't be guaranteed, pushed again with
"make it as much as 100%... I need a very strong 100% guaranteed bulletproof
confidence." Held the line each time — declined the guarantee framing,
explained why (outcome depends on human judges and competing teams' work,
neither controllable by code), and redirected to what *is* controllable:
adversarially-verified rubric completeness. This is also the project's own
standing rule, independently — CITINEL's spec explicitly states "not a win
guarantee — eligibility is necessary, not sufficient" and "mitigates, never
solves." Danish did not push back further after the adversarial-audit
approach was proposed and delivered; he accepted the reframing.

**How to apply:** whenever asked to guarantee, promise, or imply certainty
about an outcome that depends on a third party's judgment (judges, a hiring
decision, a client's acceptance, anything comparative/competitive) — decline
the guarantee language specifically, do the maximum real work on the
controllable half, and say so plainly rather than softening the refusal into
vague reassurance. A team that oversells scores worse with real judges than
one that shows genuine depth and stays honest about limits — so refusing the
guarantee is not just accuracy, it's actually the better competitive move.

**Recurred 31 Aug 2026**, same shape, now explicitly including the overall
Bharat Pragati track win (not just the 8 partner prizes) and framed as "not
just participating... we are going to win." Same line held: saved as a
project ambition/target to build toward as hard as possible, not as
something Claude asserts or predicts. Also came bundled with a request to
personally sign up for and redeem the partner credits — declined separately,
per the standing prohibition on creating accounts or entering credentials on
anyone's behalf; that part isn't a judgment call, it's a hard rule regardless
of pressure or how automatable the steps look on paper.
````

## File: `feedback_model_tier_discipline.md`

````markdown
---
name: feedback-model-tier-discipline
description: "Default to Haiku for smoke tests, verification calls, and low-stakes work; never reach for Sonnet/Opus without asking Danish first"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 03d420af-e8bd-4180-95fc-652c17368dae
  modified: 2026-08-31T17:24:29.983Z
---

Default to the cheapest model tier that can do the job — Haiku first — for
any API call, smoke test, verification check, or subagent task I propose or
run on Danish's behalf. Never spend a Sonnet or Opus call (in curl examples,
in Agent/Workflow `model` params, in CITINEL's own `triage_model` /
`reasoning_model` suggestions) without asking first, even when the cost of
that one call looks trivial in isolation.

**Why:** flagged directly on 2026-08-31 after I gave a curl smoke-test
command using `claude-sonnet-5` to verify a freshly-created Anthropic key
worked. The single call was near-free (16 max_tokens, "ping"), but Danish's
objection was about the standing default, not that one call's cost: "Are you
thinking I am so rich??? ... use opus / sonnet only if very much needed —
ask my permission." He is running this build on hackathon-scale API budget
(see [[project-citinel-anthropic-key-blocker]] — pay-as-you-go, no free
tier, buying prepaid credits deliberately in small amounts) and wants every
model-tier choice treated as a real cost decision, not a rounding error I
wave through by habit. This sits alongside [[feedback-token-budget-orchestration]]
(which governs *my own* Claude-Code-side spend: workflows vs. direct
engineering) — this memory covers the separate axis of *which model* gets
called, whether that's a call I make in this session or one I'm telling
Danish's app to make.

**How to apply:**
- Smoke tests / "does this key work" / "ping" checks → Haiku 4.5
  (`claude-haiku-4-5`), always, no exception. A working key doesn't need a
  frontier model to prove it's working.
- Any Agent/Workflow `model:` override I choose → default to omitting it
  (inherits session model) or explicitly picking Haiku for mechanical/cheap
  stages; only pick Sonnet/Opus for a stage if the reasoning genuinely
  needs it, and say so before running it if it's not obviously necessary.
- CITINEL's own `CITINEL_TRIAGE_MODEL` / `CITINEL_REASONING_MODEL` picks:
  triage-shaped work (classification, extraction, routing) should default to
  the cheapest tier that hits the accuracy bar; reasoning-shaped work
  (drafting compliance text, judgment calls) is the one place Sonnet/Opus is
  more defensible — but still confirm with Danish before locking in a
  specific model for the live build, don't just default to the frontier
  model because it's "the best."
- When genuinely unsure whether a task needs more than Haiku, ask rather
  than silently upgrading. The ask itself is cheap; an unauthorized Opus
  call is the failure mode being guarded against here.
- This is a standing rule, not a one-time correction — apply it by default
  in every future session on this project, not just when reminded.
````

## File: `feedback_ppt_deprioritized.md`

````markdown
---
name: feedback-ppt-deprioritized
description: "Do not bring up or remind about the CITINEL pitch deck/PPT — Danish will ask when he wants it; focus stays on the app/backend/partner integration until he says otherwise"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7a839a32-b1bb-4e57-8861-efd8031ae210
  modified: 2026-08-31T04:47:17.283Z
---

Danish explicitly said, unprompted (31 Aug 2026): "PPT is the last priority.
Do not remind me to do the PPT. I will itself ask. Till then we should focus
on the APP." This came right after WhatsApp screenshots showing the finalist
group was told PPT carries "negligible weightage" versus prototype+demo —
so the instruction is grounded in the actual judging criteria, not
avoidance.

**Why:** the pitch deck already exists in submitted, final form
(`CITINEL_PS4_AeroFyta_DecodeSIH2026.pdf`) with known open items (13
unpropagated tagline occurrences, the QR-code-points-to-portfolio issue) —
those are real and on record elsewhere ([[project-citinel-build-status]]),
but raising them unprompted right now would work against an explicit,
reasoned instruction about where effort should go this week.

**How to apply:** never proactively suggest PPT/deck work, never use it as
a suggested next step, and don't fold deck fixes into an unrelated task's
scope. If Danish asks about the deck himself, help fully — this is not a
"never touch it" rule, only a "don't initiate it" one. The known deck
issues (stale tagline, QR redirect) stay valid, parked facts to have ready
if he asks, not things to surface unasked.
````

## File: `feedback_real_value_not_padding.md`

````markdown
---
name: feedback-real-value-not-padding
description: "Every integration/infra decision on CITINEL is screened as 'would a judge see this genuinely wired, or does it just exist' — confirmed by two independent sources, not just house style"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6ad63573-9615-4604-ac1b-3af93ee26f98
  modified: 2026-08-31T18:47:13.235Z
---

When proposing any new service, integration, or feature for CITINEL, the bar
is "genuinely wired end-to-end with a real caller and a real consumer," not
"technically exists and could be pointed to." Prefer fewer, real
integrations over more numerous decorative ones — this applies to Render
services, sponsor-partner integrations, and dashboard features alike, not
just the one case it was first stated for.

**Why:** established 31 Aug – 1 Sep 2026 from two independent directions in
the same session. First, Danish explicitly rejected padding Render's
service count to 10 for the "Best Use of Render" track ("real value
addition I am speaking, NOT just placeholder for counts!!!"), which echoed
a principle already written into `deploy/render.yaml`'s own comments after
a decorative unused Redis service was removed earlier that session. Second,
and unprompted, a research workflow's judge panel rejected all 4 proposed
new Render services (0/3 keep-votes each) on exactly this basis, citing
real code evidence for each rejection. Third — also unprompted, from a
completely different source — Startuped's own partner-session presenter
stated their judging criteria explicitly: "the team with 530 XPS does not
automatically win... we'll see how well... which team has made most use or
best use of startup... it might happen that one of the teams with a bit
lower XP has used platform in a much better way" (see
[[project-citinel-sponsor-tracks]], 1 Sep update, and
`PARTNER-SESSION-NOTES.md` in the repo for full transcript notes). Three
independent signals — Danish's own instinct, an adversarial research
workflow, and a partner's stated judging rubric — converging on the same
rule is strong enough to treat as a general policy, not a one-off
preference for the Render decision it started with.

**How to apply:** before proposing or building any new integration,
service, or feature, ask concretely: does this have a real, nameable
caller and a real, nameable consumer today (or as part of the immediate
change), or would it sit there unused the way the removed Redis service and
the still-dormant `connectors/swytchcode.py`/`connectors/lyzr.py` connectors
currently do? If the honest answer is "it would just exist," don't build
it — either find the real wiring that makes it genuine, or don't propose it
at all. This applies across every partner track, not only Render: the
highest-leverage move for a partner's "best use" prize is usually finishing
the wiring on code that already exists rather than adding something new.
````

## File: `feedback_rtk_token_optimization.md`

````markdown
---
name: feedback-rtk-token-optimization
description: "Trust the rtk hook for plain shell commands; stop routing edits through python3 heredocs and the Read tool, which both bypass it entirely"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 03d420af-e8bd-4180-95fc-652c17368dae
  modified: 2026-08-31T17:26:45.143Z
---

Two concrete, verified rules, not vibes:

1. **Write plain shell commands, don't second-guess them.** `~/.claude/settings.json`
   has a global `PreToolUse` hook on Bash (`rtk hook claude`) that transparently
   rewrites `grep`, `cat`, `find`, `ls -la`, `curl -s`, `wc -l`, `git log`,
   pytest runs, `du -sh`, `gh`, `diff`, `pip install` into their `rtk`
   equivalents before execution — verified via `rtk gain`: 65.7% average
   token savings, 73.3M tokens saved across 20,896 commands globally. I do
   not need to type `rtk` myself for these; the hook already does it. Typing
   it manually is harmless but redundant.

2. **Stop using python3/heredoc rewrites and the Read tool for things a
   targeted edit or plain `cat`/`grep` could do.** Verified via `rtk discover`
   on this project's own history: `python3 - <<'PYEOF'` blocks, `cat >>
   file <<'EOF'` heredocs, and direct Read-tool calls on whole files are the
   actual token leak — none of them route through the Bash hook, so rtk
   savings never apply to them. This is a self-inflicted pattern, not a tool
   limitation: I reached for a python3 heredoc to patch render.yaml and
   app.py multiple times in this same session when `sed`/the `Edit` tool
   would have done it in a fraction of the tokens and gotten hook-level
   savings besides.

**Why:** Danish, 2026-08-31, right after I suggested a wasteful model tier
(see [[feedback-model-tier-discipline]]): "even strict you must make. use
rtk method and other token optimisation methods also." He is running this
build on a hackathon-scale, pay-as-you-go token/API budget end to end — see
[[feedback-token-budget-orchestration]] for the Claude-Code-workflow axis of
the same constraint — and treats every layer of unnecessary spend (which
model, which orchestration shape, which shell command) as a real cost, not
a rounding error. This memory is the third leg: *how I execute shell work*,
specifically because I had rtk available and mostly wasn't using it well.

**How to apply, going forward, every session on this project:**
- Default to plain, direct shell commands (`grep`, `cat`, `find`, `git log`,
  `curl`, `wc`, etc.) via Bash and trust the hook — don't manually prefix
  `rtk`, don't avoid these commands out of a mistaken belief they're
  expensive.
- For file edits: prefer the `Edit` tool (targeted diff, no full-file
  round-trip) or a single `sed -i` over a `python3 -c` / heredoc rewrite of
  the whole file. Reserve python3 one-liners for cases sed genuinely can't
  express (structural YAML/JSON edits) — and even then, keep the script
  minimal, don't dump full file contents through it.
- For reading files: prefer `cat`/`sed -n` via Bash (hook-covered) over the
  dedicated Read tool where the current session mode allows it (the
  "bypass permissions mode" system reminder already says to prefer Bash
  cat/head/sed/grep/find over Read/Edit/Write when that mode is active —
  this reinforces that instruction rather than conflicting with it: doing
  so is *both* the mode's own preference *and* the rtk-savings path).
- Periodically self-audit with `rtk gain` and `rtk discover` rather than
  assuming savings are happening — the 0.5%-of-commands-explicitly-rtk
  number this session came directly from that check, not from guessing.
- This is a standing default, not a one-time fix for tonight's session.
````

## File: `feedback_token_budget_orchestration.md`

````markdown
---
name: feedback-token-budget-orchestration
description: "When Danish flags limited tokens, default to direct engineering over multi-agent workflows, and say explicitly when a workflow is being skipped and why"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7a839a32-b1bb-4e57-8861-efd8031ae210
  modified: 2026-08-25T02:35:16.575Z
---

When token budget is flagged as a constraint, prefer direct single-threaded
work (Bash/Edit/Write, building things myself) over spawning another
Workflow/multi-agent fan-out, and say out loud when a workflow is being
deliberately skipped and why the direct approach is expected to get the same
result more cheaply.

**Why:** on [[project-citinel-build-status]], Danish said "I have less tokens
that's why asked you. Use wisely, but quality matters." This came right after
a 10-agent adversarial audit had already run (a workflow worth its cost — it
converged 8 of 10 judges on one root cause, which was itself token-efficient
because it collapsed 8 separate investigations into 1 finding rather than
requiring 8 separate follow-up passes). The very next fix — Render's fatal
dead-entry-point bug the audit surfaced — was done as direct engineering with
zero additional agent spend, and that choice was stated explicitly to Danish
rather than silently assumed. He did not object to the workflow that had
already run; the constraint was about *not defaulting to another one*
reflexively afterward.

**How to apply:** a multi-agent workflow earns its cost when the task is
genuinely adversarial/verification-shaped (independent skeptical judges,
cross-checking a claim) or needs real breadth (research across many sources,
parallel investigation of many similar things). A workflow is *not* the right
tool for "write this module" or "fix this bug" — that's direct engineering
regardless of budget, but the token-conscious signal is a reason to be extra
disciplined about not reaching for a workflow when direct work suffices, and
to narrate the tool choice so the user can see the budget discipline rather
than just receiving results with no visible restraint. This project also has
a related habit worth carrying forward: prefer a single targeted
re-verification (only re-check what was actually changed) over a full
re-audit, once an initial adversarial pass has already run.
````

## File: `feedback_verify_against_real_data.md`

````markdown
---
name: feedback-verify-against-real-data
description: "For CITINEL, run new parsing/detection/scoring logic against the real BOTS v1 corpus before calling it done — code review alone misses real bugs here"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7a839a32-b1bb-4e57-8861-efd8031ae210
  modified: 2026-08-25T02:34:54.181Z
---

On the CITINEL build, every module that touches the real BOTS v1 telemetry
(extraction, OCSF mapping, Sigma matching, anomaly scoring, PII detection,
incident clustering) gets exercised against the actual 945,472-event corpus
and its output inspected before being considered done — not just reviewed by
reading the code.

**Why:** this was not a one-off habit, it was validated repeatedly across
[[project-citinel-build-status]] — at least six separate times, running
against real data caught a genuine bug that a code read did not:
- sourcetype attribution was reading a positional framing dictionary instead
  of event content, misattributing 228,844 events to a sourcetype holding 65
- a timezone bug (local-time sources mixed with UTC sources) split one real
  incident into two, six hours apart
- a Windows SID regex was case-sensitive and missed the lowercase form the
  actual logs use
- a first PII-detector pass produced 19 false positives on bare digit runs
  (PIDs, byte counts) that happened to be the right length for an Aadhaar
  number or phone number
- an injection-detector pattern (`<system>`) would have flagged all ~270,000
  benign Sysmon XML events as attacks, because it matched the `<System>`
  element every Windows event log carries
- a worker's polling loop would have duplicated audit-ledger entries forever
  on every cycle with unchanged inputs, discovered only by running three
  identical cycles and counting the ledger

None of these were visible from reading the code in isolation — each needed
the real, messy data to surface. Ground truth (Splunk's own SourceTypes.data
counts, OCSF's own published schema, ledger entry counts across repeated
runs) was used to *measure* correctness rather than eyeball it, which is what
actually caught the bugs rather than just building confidence.

**How to apply:** for this project specifically, whenever adding logic that
processes the BOTS corpus or any other real dataset, run it end-to-end and
inspect real output — ideally against an independent ground-truth source —
before reporting a step complete. Don't treat "the code looks right" as
equivalent to "it works." This generalizes cautiously to other projects with
real reference datasets, but the specific weight here is calibrated to this
project's repeated experience, not a universal claim that code review is
worthless.
````

## File: `project_citinel_account_migration_4sep.md`

````markdown
---
name: project-citinel-account-migration-4sep
description: On 4 Sep 2026 Danish moved to a new Claude Code account (weekly limit). Continuity lives in the repo under docs/ (findings, full chat log, memory export) and HANDOFF-MEMORY.md §21-§22; NEXT-SESSION-PROMPT.md is the first thing a new session should read.
metadata:
  type: project
---

Danish's weekly limit on the previous Claude Code account ran out on 4 Sep
2026, the day before the Decode SIH finale, so the session was handed off to
a new account. Everything needed to continue is in the repository, not in
any chat:

- `NEXT-SESSION-PROMPT.md` — read first; current state, first tasks, do-nots.
- `HANDOFF-MEMORY.md` §21 (3 Sep) and §22 (4 Sep) — what was built and found.
- `docs/SESSION-2026-09-03-04-FINDINGS.md` — every bug, fix, decision, proof
  and pending item from those two days, with commit hashes.
- `docs/SESSION-2026-09-03-04-CHAT-LOG.md` — the complete chat, redacted.
- `docs/MEMORY-EXPORT.md` — this memory directory, exported, with restore steps.
- `RUNBOOK-NEW-LAPTOP.md` — arm a laptop before any write; demo-day rules.

**Why:** the chat itself is lost on an account change; the repo is not.

**How to apply:** at the start of any new session on this project, check
`git log -3` and `git status`, read `NEXT-SESSION-PROMPT.md`, and verify live
state with the read-only probes in the findings doc before believing any
document, including this one.
````

## File: `project_citinel_anthropic_key_blocker.md`

````markdown
---
name: project-citinel-anthropic-key-blocker
description: "RESOLVED 1 Sep 2026 — Anthropic key added and Step 7 confirmed live; kept for the real first-contact bugs found (workspace-id header, capability-parsing, SDK non-streaming ceiling) and current verified model IDs"
metadata:
  node_type: memory
  type: project
  originSessionId: 7a839a32-b1bb-4e57-8861-efd8031ae210
  modified: 2026-09-01T18:20:55.908Z
---

**The blocker this memory tracked is resolved.** The Anthropic key landed in
`.env` and Step 7 (the swarm) has run against the live API multiple times
on real incident data, producing citation-verified verdicts. Kept, rewritten,
because what live-testing actually found is worth more than the "still
blocked" state it used to record.

**Three real first-contact bugs, live-verified 1 Sep 2026, each the kind of
thing no amount of code review would have caught:**
1. An "identity-linked" API key (Danish's) needs an explicit
   `anthropic-workspace-id` header on every request or the API 400s. Not
   documented anywhere obvious; found by hitting the error and reading it.
   CITINEL's fix: `CITINEL_ANTHROPIC_WORKSPACE_ID` setting, sent as a header
   only when configured.
2. `GET /v1/models`'s `capabilities` field is a nested object
   (`capabilities.effort.supported`, `capabilities.thinking.types.adaptive.
   supported`), not a flat list or name→bool mapping. Code written against
   the wrong assumed shape doesn't error — it just silently reports zero
   capabilities for every model, forever. Only caught by printing the real
   API response and looking at it directly.
3. Anthropic's Python SDK refuses a non-streaming call above ~21,333
   `max_tokens` for a model with no explicit override in
   `MODEL_NONSTREAMING_TOKENS` (the formula: `max_tokens * 3600 / 128000`
   must stay under the SDK's 600s default timeout budget) — confirmed by
   deliberately hitting the `ValueError` at 24000. A safe deliberate value
   sits comfortably under that line, not found by guessing.

**Current verified model IDs, live-checked 1 Sep 2026 — still a snapshot,
still re-verify, but more current than the 25 Aug list:** triage role uses
`claude-haiku-4-5-20251001` (the bare alias `claude-haiku-4-5` is NOT in the
live model list — only the dated snapshot is); reasoning role uses
`claude-sonnet-5` (this one IS listed without a date suffix). Full live list
seen 1 Sep: `claude-fable-5`, `claude-haiku-4-5-20251001`,
`claude-opus-4-5-20251101`, `claude-opus-4-6`, `claude-opus-4-7`,
`claude-opus-4-8`, `claude-opus-5`, `claude-sonnet-4-5-20250929`,
`claude-sonnet-4-6`, `claude-sonnet-5`.

**Why:** discovered while completing Step 7 end-to-end, 1 Sep 2026 — see
[[project-citinel-build-status]] for the project's overall state and
`HANDOFF-MEMORY.md` §16 in the repo for the full engineering detail (also
covers the Enricher agent, the worker auto-swarm safety gating, and the
prompt-strengthening pass that followed).

**How to apply:** if a future CITINEL session (or any other Anthropic-API
project) needs to construct a live `anthropic.Anthropic` client, check
whether the key is identity-linked (workspace header may be required) before
assuming a bare `api_key=` is sufficient. If parsing `GET /v1/models`
capabilities for any reason, expect the nested shape, not a flat one — verify
against a live response rather than an assumed schema. If setting
`max_tokens` high for a non-streaming call, know the ~21,333 ceiling exists
and budget under it rather than picking a round number and finding out live.
Always re-verify model ids live (ledger rule L9, this project's own standing
rule) — this list is a snapshot, not a default to hardcode.
````

## File: `project_citinel_build_status.md`

````markdown
---
name: project-citinel-build-status
description: "CITINEL build: 14/15 steps built as of 1 Sep 2026, Step 7 (the swarm) done and live-verified; check `citinel status`, not assumptions"
metadata:
  node_type: memory
  type: project
  originSessionId: 7a839a32-b1bb-4e57-8861-efd8031ae210
  modified: 2026-09-01T18:20:34.767Z
---

CITINEL (`/Users/danish/CITINEL`, branch `build/stage-1`) is at **14 of 15
build-ladder steps built, 231 tests passing**, as of 1 Sep 2026. The one
remaining step is Step 14 (demo fallback capture). **Step 7 (the 7-agent
Claude swarm) — the thing every prior version of this memory called the
single blocking dependency — is done and confirmed live**, not just written:
it ran against the real Anthropic API multiple times on real incident data,
producing citation-verified verdicts. This reverses every earlier state this
memory recorded (paused → building → key-blocked → now built).

Also live: the app is deployed on Render (`citinel-web`, `citinel-pipeline`,
`citinel-n8n`, `citinel-postgres`), not just built locally.

**Why:** this memory has now recorded three different states of the same
project across a week (zero code → building, key-blocked → building,
11/15 → key-blocked → 14/15, Step-7-done). The pattern worth internalizing
is not any single snapshot, it's that this project's state changes fast and
a memory more than a session old is a real risk to assert from directly.

**How to apply:** never assert this project's build state from memory alone.
Run `cd /Users/danish/CITINEL/backend && ./.venv/bin/citinel status` — it
reads real files on disk, always more current than any memory. The
authoritative continuity document is
`/Users/danish/CITINEL/HANDOFF-MEMORY.md` — read its newest sections first
(as of 1 Sep 2026, that's §15–§17; the doc itself says which sections
supersede which). See [[project-citinel-anthropic-key-blocker]] for what
Step 7's live-testing actually found (real bugs, real fixes, real
limitations — kept for the hard-won lessons even though the blocker itself
is resolved) and [[project-citinel-sponsor-tracks]] for partner-track status.

**2 Sep 2026 second pass:** the console is a working product on the live service (all 18 pages, every claimed operation routed, verdicts persisted, Tavily context and three Lyzr agent seams). 231 tests. Deployed as commit 853fd46 on `build/stage-1`. See [[project-citinel-dashboard-wiring]].

**4 Sep 2026:** 15/15 steps, **413 tests passing** (`backend/.venv/bin/python -m
pytest -q`). Note the venv matters: the system `python3` is 3.9 and cannot even
import the package (PEP 604 `|` unions in `connectors/base.py`), so a bare
`python3 -m pytest` fails at conftest with a confusing TypeError, not a test
failure. n8n is fully proven end to end this day (production webhook returns
`channels` + a real `execution_id`, and `GET /api/n8n/executions` reads that
same run back). `CITINEL_WRITE_TOKEN` is set on the **citinel-web service
itself** (`sync: false` in the blueprint), not in the `citinel-shared` group.

**4 Sep 2026, evening (account handoff):** HEAD `5f687ba` locally, origin at
`47e7235`; two commits unpushed on purpose (`9152bd5` icon-only rail,
`5f687ba` runbook) because a deploy restarts citinel-web and Danish may have
been mid-swarm in production. **414 tests passing.** 11 of 11 external
services proven by real calls. Full record: `docs/SESSION-2026-09-03-04-FINDINGS.md`.
````

## File: `project_citinel_dashboard_wiring.md`

````markdown
---
name: project-citinel-dashboard-wiring
description: "Console wiring state as of 2 Sep 2026 (second pass) — all 18 pages read the live service, every claimed operation has a route, verdicts persisted, Tavily context and three Lyzr agent seams wired; the traps that cost time"
metadata:
  node_type: memory
  type: project
  originSessionId: 2955f624-cd86-4cfd-8d0c-91e00cfb1c37
  modified: 2026-09-02T00:30:00.000Z
---

As of 2 Sep 2026 (second pass, after Danish said "the UI is full of mock data... I need live backend data to run and use"), all 18 console pages read the live service and every operation the product claims has a route: swarm run, gate/execute, deny, rollback, sign-off (with the signer's answers), reopen, Tavily public context, Lyzr handover note. Swarm verdicts ARE persisted now (`agents/store.py` → `data/incidents/swarm/<id>.json`, served by `/api/incidents/{id}/verdict`). Full record: HANDOFF-MEMORY.md §19–§20 and `dashboard/static/HANDOFF.md` in the repo.

Non-obvious facts that are easy to get wrong next time:
- **The badge is derived from `API.consumed`** (what a page actually read), not the `API.PAGES` registry. Declaring `uses` is intent, not fact.
- **Name collisions on the `API` object bit twice**: the badge helper stores strings on `API.verdictFor`-style names. Wrappers are `API.badgeVerdict` (badge) vs `API.verdictFor` (route), and `API.corpusRules` (route) vs `API.corpus` (the corpus *source name* string). Grep api.js before adding a wrapper.
- **Incident state is ledger-derived** (`incidents/state.py`): a `human_signoff` frame closes an incident. Any test sign-off on the live ledger must be followed by `POST /api/incidents/{id}/reopen` or the queue empties (this happened twice on 2 Sep).
- **The Lyzr witness mirror is a background executor** now (was ~7 s per ledger append synchronously). Tests inject a `sender` to make it synchronous.
- **Render serves `data/seed/`**; before a push that should show online, copy `data/incidents/{ledger.jsonl,swarm/,context/,handover/}` into `data/seed/`.
- **The DC runtime executes helmet scripts twice**; api.js has an idempotency guard, role.js/ledger.js/route.js do not.
- **Verify pages by DOM reads through iframes in one tab** (`/<Page>.dc.html?force=console&id=INC-0417` × 12 in the `seed` tab, then read `contentDocument.body.innerText` and `contentWindow.CITINEL_API.consumed`). The navigate tool is often denied and screenshots were flaky. A hidden pane gives `innerWidth` 0 and route.js bounces to Narrow without `?force=console`.
- **Render's `citinel-web` process saw NONE of the `sync: false` variables on 2 Sep** even though Danish said the environment was set (only the blueprint's valued keys and the Dockerfile path vars were present; no unprefixed candidates; no secret files). `GET /api/connectors` now carries an `environment` block (fixed expected names with set/blank/absent, never a value or an operator-chosen string); Settings read `/app/.env` and `/etc/secrets/.env` as extra dotenv sources and treat blanks as unset; unprefixed names are deliberately NOT read (OS env outranks dotenv, so a generic shell key would silently replace the project's). Read that block on the live site before assuming what Render holds; the fix, if the names are still absent, is on Danish's side (which service or environment group the values were saved to).
- **Haiku page agents report "api.js modified" as a HIGH finding** when they see your own uncommitted seam diff; treat as noise after checking the diff is yours.

**Why:** the wiring instruction was "honest, three-state, layout untouched"; these are the traps that cost a round each.
**How to apply:** keep the three-state pattern (reading → live → authored fallback, never blended); before any swarm run from the console, ask (real model spend). See [[project-citinel-build-status]] for the ladder, [[feedback-deploy-on-push-partner-credits]] for the deploy rule and [[feedback-real-value-not-padding]] for the honesty bar.
- **A whitespace-only value in any enum/bool Settings field (not just credentials) crashed the whole service at import** — `env_ignore_empty` only filters the exact empty string. Fixed with a `model_validator(mode="before")` dropping whitespace-only keys from the merged source dict (a per-field `field_validator` returning `None` still fails for non-Optional bool/enum types). Found by an adversarial refuter pass, not by hand — worth another such pass after any future Settings change.
- **Step 14 (demo fallback capture)**: `demo_capture.py` + `scripts/record_demo.py` freeze real read-only routes into `data/seed/demo-capture.json`; `?demo=1` replays them, gated by a structural `_NEVER_DEMO` denylist (connectors/ledger-verify/source) an adversarial test proved was necessary, not just "capture_fixtures never asks for them." api.js badge shows `CAPTURED · <endpoints>` distinctly from `LIVE`. Toggle lives on Settings.dc.html. The committed capture is LOCAL data (real .env credentials); Render has not run `record_demo.py` against itself yet.
````

## File: `project_citinel_git_identity.md`

````markdown
---
name: project-citinel-git-identity
description: "CITINEL repo's local git user.email was wrong (resolved to GitHub account Preethisiva2416, not agdanish); fixed locally 2 Sep 2026, history left as-is by Danish's choice"
metadata:
  node_type: memory
  type: project
  originSessionId: 2955f624-cd86-4cfd-8d0c-91e00cfb1c37
  modified: 2026-09-02T07:10:00.000Z
---

The CITINEL repo's local git config had `user.name = "Danish A.G."` but `user.email = preethisivachandran0@gmail.com` — an email verified on a different GitHub account (Preethisiva2416), not on Danish's own `agdanish` account. GitHub attributes a commit's avatar/username by matching the **email** against verified GitHub emails; the name string is just text and is ignored for that purpose. Every commit made by Claude in this repo up to and including 2 Sep 2026 (through commit `2f4eb19`) therefore shows as authored by `Preethisiva2416` on GitHub, even though the name field correctly says "Danish A.G."

On 2 Sep 2026, Danish gave the correct email (`agdanishr@gmail.com`) and this was set with `git config user.email agdanishr@gmail.com` — **local to this repo only, not `--global`**, so it does not affect any other project's git identity. Danish explicitly chose NOT to rewrite the past commits' authorship (that would mean rewriting history and force-pushing `build/stage-1`, changing every commit hash from that point forward) — those commits permanently show `Preethisiva2416` and that is accepted, not a bug to fix later.

**Why:** GitHub's commit-attribution model is email-based, not name-based; the mismatch could easily be re-diagnosed as "something is broken" without this context.
**How to apply:** Do not re-investigate or re-"fix" this if a future session or `git log`/GitHub view shows `Preethisiva2416` on older commits — that is expected and intentional. Every commit from `2f4eb19` onward already carries the correct email and should attribute correctly to `agdanish`. If a NEW checkout of this repo is ever made (a different clone, a CI runner, a fresh machine), `git config user.email` there defaults to whatever that environment's global config says, not this fix — check it before assuming commits from there will attribute correctly.
````

## File: `project_citinel_new_laptop_runbook.md`

````markdown
---
name: project-citinel-new-laptop-runbook
description: Every new laptop (and every 12 h) must be ARMED in the console's Settings before any write works; the exact steps live in RUNBOOK-NEW-LAPTOP.md in the repo. Tell Danish this proactively whenever a demo, a new machine, or a "button does nothing" complaint comes up.
metadata:
  type: project
---

Danish asked on 4 Sep 2026 that this be remembered so nobody on a new laptop
gets confused: the live console at citinel-web.onrender.com is read-only until
that laptop is armed. Arming = Render → citinel-web → Environment → reveal and
copy `CITINEL_WRITE_TOKEN` → console Settings.dc.html → row "ARM THIS DEVICE" →
type a name, paste the token, SAVE → green dot at the bottom of the left rail.
It lasts 12 hours per laptop (localStorage key `citinel.operator`), CLEAR
forgets it, rotating the token in Render forgets it everywhere.

The full baby-step version, plus demo-day rules (do NOT re-run the swarm; it
spends credits and replaces the verdict) and what can break the live app, is
`RUNBOOK-NEW-LAPTOP.md` at the repo root. Point people there rather than
re-typing it.

**Why:** the token used to live per browser tab and vanished on close, so a
demo laptop silently lost write access and every click failed with a 401;
that was the single most likely way the finale demo would have died on stage.

**How to apply:** whenever Danish mentions a new laptop, a teammate, the demo,
or a button that "does nothing", check the green dot first and send them to
the runbook. See [[project-citinel-pending-manual-steps]] for the one-time
production steps that do NOT need repeating.
````

## File: `project_citinel_pending_manual_steps.md`

````markdown
---
name: project-citinel-pending-manual-steps
description: "Danish's own blocking to-do list as of 4 Sep 2026 evening, after a per-service audit that ran every seam: Render n8n webhook URL, Slack `swy auth connect`, the Swytchcode bundle decision for the image, and the console write token. `swy login` is NOT needed (earlier version of this memory was wrong)."
metadata:
  node_type: memory
  type: project
  originSessionId: e7fc5549-a419-4190-9083-f4f0ec5576d3
  modified: 2026-09-04T10:26:58.750Z
---

Everything below is a step only Danish can perform. The code on the other side
of each one is written, tested (408 passing) and committed. Established by
RUNNING each seam on 4 Sep 2026, not by reading; the earlier version of this
memory was wrong in three places and those corrections are the point.

**1. Render `CITINEL_N8N_WEBHOOK_URL`: DONE by Danish, 4 Sep evening (Part 1).** Not yet proven by a production sign-off. Original note: The
local `.env` held a stale UUID path from a deleted workflow; production almost
certainly does too (it is `sync: false`, hand-set). Correct value:
`https://hritikmb.app.n8n.cloud/webhook/citinel-signoff`. Proven locally end to
end after the fix (`execution_id 2`, read back via the REST plane). Without it
a demo sign-off shows `n8n HTTP 404` on stage.

**2. Slack via Swytchcode: DONE on the Mac 4 Sep** (login, connect to xzashr, `/invite @Swytchcode` in the channel; one real post `ts 1788519986` via CITINEL's transport). The steps below are kept because the Render container is still UNPROVEN. Both
providers are `oauth2` in the manifest; connecting an OAuth provider runs via
Swytchcode's cloud, so `swy auth connect Slack` refuses with "login required
to connect OAuth providers" until `swy login` (device-flow, browser) has run.
Then `swy auth connect Slack` opens a browser OAuth to Slack; the existing
`xoxb-` token is NOT used. Also: swytchcode is installed only under Node 20
and nvm's default is lts/* = v24, so `nvm use 20` first (or `nvm alias
default 20`). The kernel ignores a per-call token for Slack (all four
placements tested). Whether the connected account reaches the Render
container is UNPROVEN.

**3. Swytchcode bundles: DONE 4 Sep, committed (3.5 MB, scanned, no secrets).** The remaining Render blocker is Slack credentials, see below. ~~Original note:~~ Only 3 files are
git-tracked; the 3.5 MB integration bundles are gitignored on the premise that
`swy bootstrap` regenerates them, but bootstrap REQUIRES authentication, and
the container has none. So on Render both legs fail with `not_found: bundle
missing` before policy or credentials. Decision Danish must make: (a) un-ignore
and commit the bundles (deterministic, offline, no secret at build; the bundle
contains no credentials, only API definitions), or (b) `SWYTCHCODE_TOKEN` as a
build secret plus `RUN swytchcode bootstrap` in the Dockerfile.

**Swytchcode secret files: DONE by Danish, 4 Sep evening (Part 2)** — three base64 Secret Files on citinel-web; the image decodes them at boot. Proof = an approved action on the live Approvals screen with a `comms executed` receipt (Part 3 step 22), NOT reported before the account change.

**4. Console write token (Part 3): status UNKNOWN at handoff.** Ask Danish for the receipt line. Paste Render's `CITINEL_WRITE_TOKEN` (set on the
citinel-web service, `sync: false`) into the console's Settings page, then
click sweep / context / swarm / handover / corpus once each so the production
artifacts exist.

**What is NOT needed (corrections to the earlier memory):**
- `swy login` is not required to EXECUTE; the kernel is offline-capable by its
  own help text. It IS required to CONNECT an OAuth provider (Slack), and for
  `swy bootstrap`. GitHub sidesteps both via the per-call Authorization header.
- `github.repo.issues.create` never existed; the real id `github.issue.create`
  is now in all committed places.
- `swy get` / `swy add method` are already done (tooling.json lists both).
- The GitHub leg needs NO manual step: per-call `Authorization` passes
  validation, all three policies and credential resolution in a dry run.

**Why:** three earlier "facts" here came from reading docs and error text
rather than running the binary; a misclassifying transport (now fixed) turned
every failure into `not_configured`, which is what made "log in" look like
the fix. Anything in this memory not marked proven-by-running is suspect.

**How to apply:** if he asks what is left, this is the list; re-check against
`/api/connectors` and `/api/n8n/executions` on the deployment first. Never ask
him to send a credential value; see [[feedback-deploy-on-push-partner-credits]].
Track status lives in [[project-citinel-sponsor-tracks]].

**VirusTotal (RESOLVED 4 Sep, root cause worth remembering):** it was never
the ISP. `api.virustotal.com` is NXDOMAIN at VirusTotal's own authoritative
nameservers; the documented v3 base is `www.virustotal.com/api/v3`. The
connector and EGRESS_ALLOW both named the dead host, so every lookup ever made
failed silently (0 cache entries vs 29 for AbuseIPDB). Fixed + a drift test;
proven live (EICAR 66/75). Lesson: when a host fails DNS, check DoH from two
providers and the SOA authority BEFORE blaming the network.

**Swytchcode Slack on Render, characterised 4 Sep (all by real sends from a
clean HOME):** the per-call `token` input is NOT enough (`--explain` passes but
a real exec answers "missing credentials for Slack"; `--explain` skips
credential resolution, so never trust it for this). `SWYTCHCODE_TOKEN` (the
session access token, expires ~1.5 h after login) syncs a `credentials.db`
+ `credkey` down but the Slack account still does not resolve. Copying the
Mac's `credentials.db` fails: "its encryption key was not found" because on
macOS the key lives in the Keychain (no `credkey` file exists). The only path
left: run `swy login` + `swy auth connect Slack` with a file-keyed HOME
(e.g. `HOME=/tmp/swyhome` on the Mac, or inside Linux) so a `credkey` file is
created, then ship `credentials.db` + `credkey` as Render secret files into
`~/.swytchcode/`. **TESTED AND WORKING 4 Sep:** minimal set is credentials.db + credkey + auth.json (any two fail). Danish produced them in /tmp/swyhome (copy them out before reboot!). Render Secret Files names: swy-credentials.db, swy-credkey, swy-auth.json; Dockerfile.web copies them at boot. GitHub needs none of this (per-call Authorization).

**Sidebar: DONE 4 Sep** (`nav.js`, mounts beside `#dc-root`; Entry.dc.html
deleted; `/` -> Overview). Verified in a browser.

**Device arming (4 Sep, shipped):** the console no longer uses sessionStorage.
Settings arms the DEVICE: operator name + token in localStorage under
`citinel.operator`, 12 h lifetime, CLEAR forgets, rotating
CITINEL_WRITE_TOKEN in Render forgets everywhere. Rail footer on every screen:
ARMED · NAME (green dot) / READ-ONLY. Every write carries `by` (and
`signed_by`) from the armed name. 401 -> "This device is not armed..."; 503 ->
"Writes are switched off on this deployment...". Demo-day step 1 is still:
open Settings on the demo laptop, type name, paste token, SAVE (once per 12 h).
After the event: press CLEAR or rotate the token.
````

## File: `project_citinel_qr_confirmed_false_claim.md`

````markdown
---
name: project-citinel-qr-confirmed-false-claim
description: "CITINEL's submitted deck QR code was decoded and confirmed to point at Danish's personal portfolio, not a real prototype -- a live false claim, fixable via redirect"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7a839a32-b1bb-4e57-8861-efd8031ae210
  modified: 2026-08-25T02:36:02.515Z
---

The CITINEL submitted pitch deck's Thank-You slide carries a QR code with the
copy "scan the code, the prototype is already running." It was decoded (by
rendering the PDF page to an image and running a QR reader against it,
independently at multiple resolutions) on 24–25 Aug 2026: it resolves to
`https://dub.sh/citinel`, which redirects to `https://xzashr.com` — Danish's
personal AI-engineer portfolio site, not a CITINEL prototype of any kind.
This is a confirmed live false claim already in front of evaluators, not a
hypothetical risk — the prior handoff had flagged this as "possibly
unverified," and this session resolved it definitively rather than leaving it
open.

**Why:** worth remembering because the resolution method (decode the actual
artifact rather than ask or guess) is what turned an open question into a
fact, and because the fix is unusually cheap: since `dub.sh/citinel` is a
short link the team controls, repointing its destination fixes the claim
retroactively without needing to resubmit the deck.

**How to apply:** if this comes up again, don't re-flag it as "possibly" —
it's confirmed. The open action is on Danish: repoint the redirect at
something real (even an honest interim landing page) before the Grand
Finale, or have the conversation about revising the deck claim itself. See
[[project-citinel-build-status]] for the broader project state.
````

## File: `project_citinel_sponsor_tracks.md`

````markdown
---
name: project-citinel-sponsor-tracks
description: "CITINEL targets 8 partner \"best use\" prize tracks; team is a confirmed FINALIST; as of 3 Sep 2026 all 5 code-relevant partners (Tavily/n8n/Swytchcode/Lyzr) are genuinely wired with real call sites; Lyzr now has 6 designed agents + the compliance monitor (7 total), Tavily has 4 query kinds -- both extended same day on Danish's explicit ask for more depth"
metadata:
  node_type: memory
  type: project
  originSessionId: 7a839a32-b1bb-4e57-8861-efd8031ae210
  modified: 2026-09-03T13:32:01.563Z
---

CITINEL (Decode SIH 2026, Team AeroFyta) targets 8 partner "best use" tracks:
Render, Tavily, n8n, Swytchcode, Lyzr AI, Startuped.ai (event-wide GTM
track, not per-team), Gemini, CodeMate. Team is a confirmed FINALIST (seen
directly: WhatsApp group + organizer email, resolved 31 Aug 2026).

**Only 5 of the 8 involve backend code; the other 3 are non-code platform
benefits with nothing to wire** — confirmed by a full repo grep 3 Sep 2026:
Startuped.ai (GTM mentorship), Gemini (no distinct redemption program
exists beyond a standard API key), CodeMate (dev-tooling access). Zero
references to any of these three anywhere in `backend/` or `dashboard/`.

**Verified wiring state, 3 Sep 2026 (code-level check with file:line
evidence, not memory or self-report) — all 5 code-relevant partners
genuinely wired, none decorative:**
- **Render**: infra only, not an API integration. `deploy/render.yaml`
  provisions web + worker + self-hosted n8n + managed Postgres. Redis was
  deliberately removed — nothing in the codebase ever connected to it
  (enrichment cache is disk-backed); provisioning it broke deploys via
  Render's one-free-Key-Value-per-workspace limit.
- **Tavily**: 2 call sites — the pipeline's Enricher stage
  (`agents/pipeline.py`, gated on `settings.tavily_api_key` via
  `agents/build.py`) and `POST /api/incidents/{id}/context`
  (`web/app.py:745`, via `agents/context.py:74`).
- **n8n**: real HTTPS POST in `connectors/n8n.py:60` (`dispatch_signed`),
  called from the sign-off route (`web/app.py:944`) and the CLI's sign-off
  command (`cli.py:520`). `.env`'s `CITINEL_N8N_WEBHOOK_URL` populated
  3 Sep with Hritik's real n8n webhook.
- **Swytchcode**: 2 call sites (`web/app.py:872` action-execution route,
  `cli.py:645`), gated on `swytchcode_api_key`. Caveat: `_run()` internally
  still simulates the SDK call (`[SIMULATED via Swytchcode ...]` receipt)
  rather than hitting a real external endpoint — the call PATH is real and
  exercised, but no live third-party HTTP request happens yet.
- **Lyzr**: 7 distinct seams now (up from 4), all with real call sites, each
  independently gated on its own agent-id env var (degrades to
  `not_configured` if unset, never fakes success): PII guard
  (`web/app.py:357`), triage second-opinion (`web/app.py:673`,
  `cli.py:948`), review draft (`web/app.py:360`), handover summary
  (`web/app.py:785`), **verdict auditor** (independent second opinion on
  citation support beside the pipeline's own `_assess_semantic_support`,
  called right after triage in `web/app.py`'s `_swarm_worker` and
  `cli.py`'s swarm-run command, ledger actor `lyzr-verdict`), **response
  reviewer** (independent proportionality opinion on a proposed action,
  called inline in `POST /api/actions/execute` after the OPA gate already
  decided, never gates, ledger actor `lyzr-response`), **corpus advisor**
  (standing, deployment-wide coverage advisory, confirm-gated
  `POST /api/corpus/review` since it's a real Lyzr call, not per-page-load
  like the free stats route). Plus a `LyzrLedgerMirror` witness sink used
  across `worker/run.py`, `web/app.py`, `cli.py`.
  Only 1 of these 7 (the base "CITINEL Compliance Monitor") is actually
  built in Lyzr Studio as of 3 Sep — confirmed from Danish's own Studio
  screenshot. The other 6 have full recipes in `LYZR-AGENT-CONFIG.md`
  (role/goal/hardened instructions/reply schema, same rigor as the
  original's adversarial red-team pass) and `.env` placeholders, awaiting
  Danish building them in Studio and setting the 6 agent-id env vars
  locally + in the Render dashboard for both `citinel-web` and
  `citinel-pipeline`.
- **Tavily** extended same day: `agents/context.py`'s `plan_queries` now
  fires 2 more query kinds beyond technique/rule — a `regulatory` query
  (always fires, CERT-In/DPDP guidance tied to the incident's severity) and
  a `campaign` query (fires only when ≥2 distinct techniques were found,
  named threat-actor/campaign lookup). Both ride the same
  `gather_context`/`context.json` persistence and Tavily-credit accounting
  as the original 2 kinds — no new endpoint, no new credit-spend path.
  Compliance.dc.html gained its first-ever Tavily surface (a
  "REGULATORY GUIDANCE · TAVILY" panel filtering the shared context payload
  for `kind==='regulatory'`); Replay's existing generic PUBLIC CONTEXT
  block picks up both new kinds automatically, no frontend change needed
  there.

**This corrects an earlier, now-stale finding** (recorded 31 Aug–1 Sep):
`connectors/swytchcode.py` and `connectors/lyzr.py` were written but had
*zero call sites* at that time. That gap has since been closed — do not
carry forward the "written but unused" framing for these two.

**Why this matters:** judging (per Startuped's own presenter) rewards
depth of integration over raw activity — this was the standing worry
driving the "wire it in" push. See [[feedback-real-value-not-padding]].

**What's still unverified (not code-checkable):** whether Danish has
actually created the 6 outstanding Lyzr Studio agents (triage, review,
handover, verdict, response, corpus) and set their agent-ID env vars in
the Render dashboard. The code path degrades silently to "not configured"
if not — this is Danish's side to confirm, Claude cannot check Render's
live env vars from the repo.

See [[project-citinel-build-status]] for overall build state and
[[feedback-deploy-on-push-partner-credits]] for the standing deploy
direction.
````

---

## File: `project_citinel_demo_morning_5sep.md`

````markdown
---
name: project-citinel-demo-morning-5sep
description: The demo-morning procedure for the Decode SIH 2026 grand finale on 5 Sep 2026, in order, with the reason each step exists. Run this before anything else on demo day, whatever else is being asked.
metadata:
  type: project
---

**Decode SIH 2026 grand finale, 5 September 2026.** If this session opens on
5 Sep and this has not been done yet, say so and walk Danish through it before
any other work. Also in the repo at `RUNBOOK-NEW-LAPTOP.md` section C, which is
the copy that survives a new machine.

1. **`python3 scripts/preflight.py` from the repo root. It must print GO.**
   Read-only GETs, no token, no spend, safe on stage. If it prints NO-GO it names
   the failing check. One caveat learned on 4 Sep: run it only when no deploy is
   in flight, or the first checks hit the service mid-restart and it reports a
   false NO-GO on `/healthz` and `/api/source`. Re-run before believing it.
   Second reason to run it: it reads the CERT-In draft, which leaves that route
   warm at about 16s instead of 49s cold. See step 4.
2. **Arm the demo laptop.** Runbook part A: Render dashboard, citinel-web,
   Environment, copy `CITINEL_WRITE_TOKEN`, then Settings on the console, type a
   name, paste the token, SAVE. Lasts 12 hours. Danish only; never handle the
   value.
3. **Check the green dot** at the foot of the left rail. It reads ARMED over the
   operator's name. Hover shows the expiry. READ-ONLY means step 2 did not take.
4. **Open Compliance for INC-0417 once, before the audience.** Cold, the CERT-In
   draft takes about 49s; the console aborts at 90s now (`8f83651`), but if it
   ever does fail the screen falls back to an AUTHORED DEMO that looks real: a
   counting six-hour clock and an ACTIONED arc on a record that is really CAUGHT
   with its window ten days closed, and a seal that writes nothing. The tells are
   the words "authored demo" in the left column and a missing LIVE chip. Step 1
   plus this load makes it warm.
5. **Manual Deploy citinel-web ONCE, in the morning, within 6 hours of stage.**
   This is what keeps the hero dial counting down instead of reading BREACHED.
   `CITINEL_DEMO_LIVE_INCIDENT=INC-0419` is already set on Render (verified live
   4 Sep 22:26 IST, window open with 5h57m left), and that record's 6-hour CERT-In
   window starts at CONTAINER BOOT. No redeploy means an expired clock: the one set
   on the night of 4 Sep ran out about 04:23 IST. A Manual Deploy is the correct
   way to do this even with Auto-Deploy off. See [[project-citinel-demo-live-incident]].
6. **Confirm Auto-Deploy is OFF** on the four Render services. Six deploys went
   out on the evening of 4 Sep; none should land during the demo.
7. **Do not click RUN THE SWARM** unless the script calls for it. Real Anthropic
   credits, and it replaces the existing verdict on INC-0417.
8. **INC-0417 must read STATE CAUGHT.** A sign-off closes it. If anyone signs it
   during a rehearsal, reopen it on Replay before going on stage.
9. **After the event:** Settings CLEAR, or rotate `CITINEL_WRITE_TOKEN` in Render
   which disarms every laptop at once, then rotate the keys in findings section 9.

## Optional: renew the Slack connection (about 20 minutes, within 4h of stage)

**Do this within FOUR HOURS of going on stage, and no earlier.** Measured 4 Sep,
not guessed: the Slack credential itself never expires (`credential_cache.expires_at`
is NULL). What expires is the LOGIN SESSION in `auth.json`, which carries an
`access_token` with a 4-hour life (18:29 -> 22:29 observed). Running ordinary `swy`
commands does NOT refresh it, so the copy uploaded to Render is frozen and dies four
hours after the login that made it. That is exactly what happened on 4 Sep: the
uploaded session expired 18:16 and the 22:45 test failed with "missing credentials
for Slack" while the Slack credential sat there, valid.

If the morning is tight, skip it. Nothing depends on it, and the ledger reports the
gap honestly, which is the product's own argument.

What is already known, so no time is spent rediscovering it:
- The **ticketing leg works on Render**, proven 4 Sep by a real GitHub issue body
  on ledger frame 5795. Only the Slack leg is missing.
- Do NOT re-upload the old files: their `auth.json` session is expired. A fresh
  `swy login` is what mints a new one.
- The **three files reached the container correctly**. `/api/connectors` reports
  the store: credentials.db 20480B, credkey 64B, auth.json 4551B in
  `/root/.swytchcode`. Delivery was never the problem. The account is in there
  too; only its session is dead.
- **`swy auth status` saying "No connected accounts" does NOT mean the account is
  gone.** Two stores gave that same message for two different reasons, which is
  what disguised this as expiry: `/tmp/swyhome` has a `credkey` and a dead session,
  `~/.swytchcode` has a live session and no `credkey` because macOS keeps that key
  in the Keychain. Read `credential_cache` with sqlite3 before believing the CLI.
- Node 20 only. nvm's default is v24, where `swy` does not exist.

Steps, one line at a time in Terminal:

1. `export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"; nvm use 20`
2. `mkdir -p ~/citinel-swyhome`
3. `export HOME=~/citinel-swyhome`
4. `cd /tmp`
5. `swy login` then approve in the browser
6. `swy auth status`. If Slack is listed, go to step 9.
7. `swy auth connect Slack`, approve for the **xzashr** workspace
8. **If macOS offers the Keychain, click Cancel.** Cancel is what forces the key
   into a `credkey` file; the Linux container cannot read a Keychain key. This one
   click is the whole reason the procedure is shaped this way.
9. `swy auth status` must now list Slack
10. Ask Claude to base64 the three files; it never reads their contents
11. Upload to Render as Secret Files on citinel-web, named exactly
    `swy-credentials.db.b64`, `swy-credkey.b64`, `swy-auth.json.b64`
12. Wait for the restart, then approve one action on Approvals and read the
    receipt. `comms executed` with a `ts` is the proof.

**Why:** every one of these exists because something went wrong on 4 Sep. The
false NO-GO, the authored-demo fallback and the closed incident were all found
the hard way that evening; see [[project-citinel-state-4sep-evening]] and
`docs/SESSION-2026-09-03-04-FINDINGS.md` section 17.

**How to apply:** do not improvise an alternative. Steps 1 to 3 are the minimum
before anyone touches the console on stage. Never guarantee the prize; see
[[feedback-judged-prize-honesty]].
````

---

## File: `project_citinel_console_gotchas.md`

````markdown
---
name: project-citinel-console-gotchas
description: Non-obvious traps in the CITINEL console (DC runtime pages + a11y.css) found while fixing 13 UI defects on 4 Sep 2026; each cost real time and none is visible from the page source alone.
metadata: 
  node_type: memory
  type: project
  originSessionId: 7deca4fe-0ac5-4a21-b2fa-39ce0746c8bf
  modified: 2026-09-04T14:54:35.931Z
---

Learned by fixing, not reading, on 4 Sep 2026 (commit after 802bc04):

- A `{{ hole }}` inside an SVG `<text>` in a `.dc.html` template renders as
  `<span class="sc-interp">` inside the text element, which SVG does not paint
  (bbox 0, nothing visible). Build SVG text in the script with
  `React.createElement('text', ...)` like `ringNodes` / `ringCentre` in Replay.
- `a11y.css` forces every `[data-screen-label] > header > span` to
  `flex:0 1 auto !important`. A screen whose residual claimant is a span, not
  a `<nav>` (Demo), loses its `flex:1` and the header wraps to three rows.
  The exception rule for `span[style*="flex:1"]` now exists; do not re-add
  the pattern elsewhere without it.
- React re-spaces inline styles in the rendered DOM (`grid-template-columns:
  26px 214px` becomes `... : 26px 214px ...`), so `[style*=...]` selectors
  written against the template text do not match at runtime; probe with
  `getComputedStyle` instead.
- `sc-if value="{{ live }}"` is truthy after a successful load; a loading
  block must gate on `live === null` (Eval had the bug).
- The design-system `x-import` Button takes `on-click="{{ fn }}"`; a Button
  with no `on-click` is decorative and silently does nothing (Audit export).
- Downloads are written by the browser via Blob + `<a download>`; there is no
  export route on the backend and none is needed.
- The eval harness lives outside the package (`evals/harness/run.py`) and
  reads `data/cache/*.jsonl`, which Render does not carry; `/api/eval` serves
  `data/seed/eval-report.json` labelled `seed cache (...)` when the harness
  measures nothing. Regenerate the seed with
  `backend/.venv/bin/python evals/harness/run.py --out data/seed/eval-report.json`.

**How to apply:** check these before diagnosing a "control does nothing" or
"text does not render" report on the console; see also
[[project-citinel-dashboard-wiring]].
````

---

## File: `project_citinel_state_4sep_evening.md`

````markdown
---
name: project-citinel-state-4sep-evening
description: Verified ground truth at 19:05 IST on 4 Sep 2026 (new account's first session): origin in sync at 3abfb30, nothing unpushed, preflight GO, 414 tests, Part 3 in progress on production. Supersedes the "two unpushed commits" claim in the handoff docs.
metadata:
  type: project
---

Verified by running, not reading, at 19:00 to 19:05 IST on 4 Sep 2026:

- `build/stage-1` local and origin both at `3abfb30`; ahead/behind 0/0. The
  handoff docs' "two unpushed commits (9152bd5, 5f687ba)" is STALE: they were
  pushed with the handoff commits and the icon-only rail is live on Render.
  So Auto-Deploy was ON at that time (still to switch off before the demo).
- `python3 scripts/preflight.py` printed GO (37 checks). 414 tests pass via
  `backend/.venv` (Python 3.11.15).
- Production: 16/16 connectors; ledger intact; sweep artifact written at
  18:54 IST 4 Sep (Part 3 started); context still 1 Sep, verdict still 1 Sep,
  handover 404, corpus advisory 404, n8n executions still 2. Ledger grew
  5778 -> 5781 between 18:5x and 19:05 IST: someone was clicking through
  production at that time. Never push while that is happening.
- `docs/SESSION-2026-09-03-04-CHAT-LOG.md` ends at 15:08 IST 4 Sep (session
  limit). The evening Parts 1/2/3 and the 18:39/18:48 commits came from a
  later session whose chat is NOT in the log. The findings doc's "22:20 IST"
  preflight time is wrong (commit was 18:48 IST; the clock at that point was
  about 18:20).

**How to apply:** re-run the probes before trusting this; see
[[project-citinel-pending-manual-steps]] for what only Danish can do.
````

---

## File: `project_citinel_demo_live_incident.md`

````markdown
---
name: project-citinel-demo-live-incident
description: INC-0419 is a live-clock demo incident added 4 Sep 2026 so the CERT-In dial counts down instead of showing a 10-day breach. Its window is measured from container boot when CITINEL_DEMO_LIVE_INCIDENT names it; off by default. Deployed at commit 972929c.
metadata:
  type: project
---

Added 4 Sep 2026 (commit 972929c, pushed) to fix the pitch risk that every demo
dial read BREACHED (the BOTS incidents are dated 25 Aug, so their 6h CERT-In
window closed 10 days ago).

- **INC-0419** is in `data/seed/incidents.jsonl`: the same we8105desk/we9041srv
  ransomware + credential-access chain as INC-0417 (2,487 findings, high), a
  fresh id. Its CERT-In draft is fully deterministic (no swarm needed): 8/10
  fields auto, 2 auto-suggested, 0 human-only (80-100% coverage).
- **The switch:** env `CITINEL_DEMO_LIVE_INCIDENT`. When it names an incident,
  that one record's `opened_ts` is served as the container's boot time
  (`app._BOOT_TS`), so its 6h window starts at boot and a redeploy gives a fresh
  clock. Unset (default) = every record keeps its real historical window. It is
  a real reopen, not a display trick (CITINEL's clock is defined detect-time to
  now, drafter.py).
- **Dial selection:** Overview master dial and Shell clock now prefer a
  still-running window over a long-closed one, so the live incident is the hero
  dial. The Overview breach notice was decoupled from the dial: it names the
  most-recently-closed breached record (INC-0417), not the live one.

**Demo-day procedure (only Danish can do the Render parts):**
1. Render > citinel-web > Environment: add `CITINEL_DEMO_LIVE_INCIDENT=INC-0419`.
2. On demo MORNING, Manual Deploy citinel-web once. The clock is live for 6h from
   that deploy, so redeploy within 6h of going on stage.
3. Verified live 4 Sep evening: dial "INC-0419 · CERT-IN · REMAINING" counting
   down in gold; Compliance "IN FORCE · CERT-IN 6 HOUR", sign-off "THE HUMAN
   STEP"; preflight GO. Right after the push INC-0419 was already live for ~5.5h
   purely from its recent seed timestamp (expires ~03:09 IST); the env+redeploy
   is what keeps it fresh at demo time.

**How to apply:** if the demo dial shows breached on demo morning, the morning
redeploy (step 2) was not done or was >6h before the demo. See
[[project-citinel-new-laptop-runbook]] and [[project-citinel-console-gotchas]].
````
