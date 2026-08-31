# CITINEL — Handoff Memory

*Prepared 21 August 2026, end of a long research/documentation session; updated 24 August 2026 after a separate, long Claude Design UI/UX session (§8) and a hackathon-reality check (§9); updated again 25 August 2026 after Danish authorized the application build and a full build session ran (§12–§13 — read these last, they supersede §9's "paused" framing and §11's old next-step guidance). This is a map + must-know-facts document, not a duplicate of the full detail — the full detail lives in `CITINEL-SDD.md` (23 sections), `CITINEL-PROPOSAL.md`, and now the git log / commit messages in this repo itself (16 commits as of 25 Aug — read `git log` for the by-step engineering detail; this file has the *why*, not the diff). Read this first, then pull the specific section you need rather than re-reading everything.*

---

## 1. What CITINEL is

**CITINEL — Autonomous Cyber SOC.** An AI Security Operations Center for **Indian cooperative banks and small NBFCs** — a segment with the same RBI/CERT-In regulatory obligations as national banks but none of the security budget. Built by **Team AeroFyta** (Chennai Institute of Technology) for **Decode SIH 2026**, Track "Bharat Pragati," PS4: *"Autonomous Cyber SOC for AI-powered threat detection and automated incident response."*

Tagline (brand hook, updated 24 Aug 2026 — was "Caught. Cited. Closed."): **"Caught. Cited. Gated. Actioned. Closed."** Not yet propagated to the submitted deck PDF (13 occurrences, unrevised) or the two locked badge-tagline PNGs — see §4a.

**Status as of 25 Aug 2026 — THIS HAS CHANGED, read carefully.** Git is now initialized (branch `build/stage-1`, 16 commits) and the application build is underway: **11 of a 15-step build ladder are built**, 108 tests passing, `citinel status` in `backend/` shows live progress. Stage 1 (the fully-offline deterministic pipeline — telemetry replay, OCSF normalization, Sigma detection, anomaly scoring) is complete and verified against the real Splunk BOTS v1 corpus (945,472 events). The policy gate, injection quarantine plane, compliance drafter, and six sponsor connectors are also built. **The one thing NOT built is Step 7, the 7-agent Claude swarm — it is blocked on an Anthropic API key that has not yet been added to `.env`.** Full detail, the exact build order, and why it matters for the partner-prize plan: §12–§13. The separate 23-page UI/UX prototype (Claude Design canvas, §8) is unchanged since 24 Aug and still exists in parallel, outside this repo — don't conflate the two build threads.

## 2. The architecture, one paragraph

Logs normalize to **OCSF**. A deterministic **Sigma engine (3,000+ community rules) + statistical anomaly scorers** run first and close known threats *before any model is involved*. Only what rules can't explain reaches a **7-agent Claude swarm** (Sentinel orchestrator → Triage Router → Enrichment Squad → Correlator → Verdict Narrator [citations-grounded] → Response Marshal → Scribe), which investigates and produces a verdict that **cites the exact log line proving it**. Every proposed response action passes a readable **OPA policy gate** with a **Shadow/Assist/Autonomous dial per action class**, **rollback tokens**, and **blast-radius rings**. Log content is always treated as untrusted data (quarantine plane, injection detector, egress allow-list) — never as instructions. Confirmed incidents **auto-draft the CERT-In 6-hour report and DPDP breach artifacts**, but a human always signs — **"we draft, we never file."** Everything writes to an **append-only audit log**. Planned deployment: Render (web service + background worker + managed Postgres/Redis).

## 3. Where everything lives

| What | Where |
|---|---|
| Full audit + spec (23 sections, evidence-tagged) | [`/Users/danish/CITINEL/CITINEL-SDD.md`](CITINEL-SDD.md) |
| Narrative pitch/proposal (this handoff's sibling) | [`/Users/danish/CITINEL/CITINEL-PROPOSAL.md`](CITINEL-PROPOSAL.md) |
| Repo's own source of truth (highest precedence) | `docs/CITINEL-STATE.md` |
| Master knowledge base | `docs/CITINEL-MASTER-KB.md` |
| Six original research reports (A1–A6) | `docs/A1-market-impact.md` … `docs/A6-compliance.md` |
| Brand law (locked, do not regenerate assets) | `citinel-brand/README.md` |
| Submitted pitch deck (15 slides, final form) | `CITINEL_PS4_AeroFyta_DecodeSIH2026.pdf` |
| SDD as a live, published HTML artifact | https://claude.ai/code/artifact/3784b725-c161-4cb8-8680-9a30acdd0dab *(private — needs the user's own share-menu toggle to go link-public; I cannot make that toggle myself)* |
| Standalone pitch-page artifact ("the proposal") | https://claude.ai/code/artifact/77f08d59-d768-4ce9-97e0-f1c124c21761 *(same privacy caveat)* |
| The 23-page UI/UX prototype (real, active, not tracked here) | A separate **Claude Design** canvas session — exact URL not recorded anywhere in this repo; get it from Danish and add it here. Pages include Overview, Queue, Replay, Confidence, Evidence, Approvals, Corpus, Eval, Policy, Compliance, Audit, Handover, Settings, Demo, Narrow, Executive, Shell, Entry, plus a design-system reference. See §8. |
| That prototype's in-canvas QA tooling | `_audit/matrix.html` (responsive-sweep runner, persists partial results to `localStorage`) and `_audit/read.html` (results reader) — live inside the Claude Design canvas, not this repo's filesystem. |
| Badge-tagline asset regeneration (in progress, external) | A separate **ChatGPT** session ("CITINEL logo redesign" / "Logo Design Request" threads) — regenerating `citinel-badge-tagline-light.png`/`-dark.png` with the new five-word tagline. Not this repo, not Claude Design. See §8. |
| **Application build (new, 25 Aug)** | `backend/citinel/` — the real pipeline (ingest, ocsf, detect, incidents, audit, policy, agents, compliance, connectors, web, worker). Run `backend/.venv/bin/citinel status` for live build-ladder progress, `backend/.venv/bin/citinel --help` for every command. Tests: `backend/tests/` (108 passing). See §12. |
| Sponsor onboarding checklist (new, 25 Aug) | [`PARTNER-ONBOARDING.md`](PARTNER-ONBOARDING.md) — signup URLs, free-tier vs. shortlist-gated credits, `.env` mapping, per-partner steps for all 8 tracks. See §13. |
| Startuped GTM playbook (new, 25 Aug) | [`STARTUPED-GTM-PLAYBOOK.md`](STARTUPED-GTM-PLAYBOOK.md) — curated module inputs + click-by-click path for the "Best GTM/Launch Strategy" award. The platform run itself is still Danish's to do. |
| Deploy config (new, 25 Aug) | `deploy/render.yaml` (5-service Blueprint, not yet deployed live) + Dockerfiles. `connectors/n8n/citinel-beat5b.json` — importable n8n workflow. `policies/citinel-policy.yaml` + `.rego` twin — the readable response policy. |

## 4. Locked brand tokens — do not deviate

- Navy `#0B1F3A` · surface charcoal `#0E1116` · evidence gold `#E7B10A` (citation highlights + regulatory clock **only**) · red reserved for severity (no single hex locked in the repo)
- Display type: Michroma / Orbitron per the brand README
- Navy-on-light / white-on-dark placement only; exactly one falcon mark; never mix the legacy swirl and current faceted AeroFyta emblems

## 4a. Open: tagline change not yet fully propagated (24 Aug 2026)

The brand hook changed from "Caught. Cited. Closed." to "Caught. Cited.
Gated. Actioned. Closed." — decided after an accessibility audit found
the product's own UI already renders the full five-state arc as visible
text on five screens, while every screen's alt text (19 identical
occurrences, now fixed) still said only three, giving screen-reader
users a systematically weaker model of the product than sighted users.

Propagated: this file, `CITINEL-PROPOSAL.md`, `CITINEL-SDD.md` (three
locations), `citinel-brand/README.md`'s tagline-system definition, and
all 19 alt-text occurrences in the Claude Design UI prototype.

NOT propagated, and each needs its own explicit decision, not a
mechanical find-replace:
- **The submitted pitch deck** (`CITINEL_PS4_AeroFyta_DecodeSIH2026.pdf`,
  "final form" per §3) — the three-word form appears 13 times. This is
  already in judges' hands; revising it is a resubmission question, not
  a copy-edit.
- **Two locked badge assets** — `citinel-badge-tagline-dark.png` and
  `citinel-badge-tagline-light.png` had the three-word form baked into
  pixels. Danish has since taken this on personally, outside this repo
  and outside Claude Design, via a separate ChatGPT session (the "lock,
  do not regenerate" call is his to make, and he's made it). Status as
  of 24 Aug: a white-on-transparent variant with the correct five-word
  tagline was generated successfully. A solid-charcoal-background
  (`#0E1116`, opaque, not transparent) variant was just prompted for;
  generation result not yet confirmed. Once finished, the two PNG files
  in `citinel-brand/` need to actually be replaced on disk, and the
  `citinel-brand/README.md` line 29 description (currently accurately
  describing the *old* pixel content) needs updating to match — neither
  has happened yet as of this handoff.

## 5. The honesty discipline — never violate these

These are hard rules from the repo itself (`CITINEL-STATE.md` §5.1) and reinforced by this session's own research passes. Any new content (pitch copy, features, claims) must obey them:

- **"We draft, we never file."** CITINEL auto-drafts compliance artifacts; a human always signs and submits. Never imply the system files anything itself.
- **"Mitigates, never solves."** No security claim is ever framed as eliminating risk.
- **No timelines.** "Danish owns all timelines" — only official, already-public external deadlines (event dates) may be stated as fact. Never invent or imply a build/ship date.
- **No fabricated metrics.** Every number traces to a finding ID or an adversarially-verified external source. The FP rate (<10%) is a *target*, not an achieved result.
- **CERT-In empanelment ≠ a product credential.** It's a services authorization for firms performing audits — CITINEL must never claim to be, or be pursuing, "CERT-In empanelled" as a product. (Confirmed hard rule — SDD §20.)
- **§21 Patentability content is explicitly non-legal-advice.** Never state or imply CITINEL has, will get, or is likely to get a patent. Any real filing decision is Danish's alone, via a real Indian patent agent.
- Response actions in any demo run **only against simulated/mock endpoints** — never real infrastructure.

## 6. Research passes completed (13 total: 11 on 21 Aug, 2 more on 24 Aug)

The 2 additional passes (24 Aug, not reflected in the SDD's own section numbering below since they're implementation/CSS research, not product research) backed the Claude Design UI/UX pass in §8:
- **Responsive/accessibility CSS techniques** (111 agents) — grid/flex blowout, truncation-with-reveal vs. WCAG 1.4.4/1.4.10, unbreakable-token wrapping, container queries, `clamp()` zoom-safety (F94), dense-table reflow (G206/C33).
- **Gap-filling follow-up** (102 agents) — same topics the first pass left thin: grid/flex blowout mechanics (now fully verified), SVG axis-label collision (library survey: D3 core has none, D3FC/Vega-Lite/Observable Plot each hand-roll differently), wide-display-typeface accommodation (mostly unverified — only "font-stretch does nothing without a shipped condensed face" survived), and programmatic overflow detection — **this pass reversed something stated earlier in the same conversation**: `scrollWidth > clientWidth` reliably detects overflow regardless of the element's `overflow` CSS value; the common claim that it fails on `overflow:visible` is itself the wrong one. If a fresh session inherits any note claiming otherwise, trust this correction, not that note.



All used the `deep-research` Workflow skill: 5 parallel search angles → source fetch → 3-vote adversarial verification (2/3 refutes kills a claim) → synthesis. Only claims that survived verification are ever presented as fact.

| # | Topic | SDD section | Outcome |
|---|---|---|---|
| 1 | Validated UVPs & USPs | §13 | 20 items, clean synthesis |
| 2 | Innovation Backlog (original) | §14 items 1–21 | 15 confirmed claims, hand-synthesized (session-limit hit) |
| 3 | Architecture hardening | §16 | 9 findings, clean synthesis after one resume |
| 4 | Additional UVPs (unconventional) | §17 | 6 clustered findings, clean synthesis after one resume |
| 5 | Demo wow-moment design | §18 | 7 findings, clean synthesis after one resume |
| 6 | UI/UX design | §19 | 6 findings, clean synthesis first try — no resume ever needed |
| 7 | Enterprise & Government readiness | §20 | 16 confirmed claims — **synthesis step returned corrupted debug output on *two* separate runs**; section was hand-reconstructed directly from the verification vote log both times. If ever re-run, expect the same bug and plan to reconstruct by hand again. |
| 8 | Patentability assessment | §21 | 21 confirmed claims, clean synthesis first try |
| 9 | Innovation/Creativity features (final pass) | §14.F items 22–29 | 15 confirmed claims, clean synthesis after one resume (mid-run DNS outage) |

Two genuine research gaps, not silently closed: **gamification/skill-building features** (zero confirmed claims — unresearched) and **community/network-effect features** (weakly evidenced — only one surviving claim, the FINRA fusion-center precedent).

## 7. Hard-won operational lessons (avoid repeating these mistakes)

- **Resuming a `Workflow` needs `args` repeated, every time.** `Workflow({scriptPath, resumeFromRunId})` alone fails instantly with "No research question provided" — the exact original question text must be passed again as `args` for cached calls to hit and the retry to work at all.
- **A "Completed" workflow status does not mean the synthesis succeeded.** The Enterprise/Government pass completed 105/105 agents with 0 errors twice, and both times its synthesis step silently returned literal placeholder text (`"claim": "test claim"`) instead of real content. Always sanity-check a workflow's actual JSON output before trusting a "completed" label — read the raw `.output` file or the `journal.jsonl`, don't trust the summary alone.
- **`/private/tmp` scratch files (including `tasks/*.output`) do not survive a session/process restart.** The `journal.jsonl` files under `~/.claude/projects/.../subagents/workflows/<runId>/` **do** survive — that's the durable source of truth for a completed workflow's full agent-by-agent results if the scratch copy is gone. To recover a synthesis result from a journal: filter for the entry whose `result` dict has a `findings` key.
- **Artifact publishing needs a `WebFetch` on the artifact's own URL first** if the session hasn't "viewed" the latest version — otherwise `Artifact({action:"publish",...})` errors with a version-conflict message.
- **Published artifacts are private by default.** I cannot make one link-public — only the user can, via the artifact page's own share menu.
- **`getBoundingClientRect()` on multiline inline text overstates its footprint** — it unions every line box into one rectangle. Use `getClientRects()` (one DOMRect per line) for real overlap checks, and `Range.getBoundingClientRect()` for a specific text-fragment's actual bounds.
- **A "Completed" `Workflow` with 0 errors can still have a wrong premise, not just a corrupted synthesis.** Beyond the placeholder-text failure above: this session stated a specific CSS claim (`scrollWidth` failing on `overflow:visible`) confidently, without having verified it, and a later dedicated research pass reversed it. When a technical claim feels load-bearing for tooling (an audit harness's actual detection logic, not just a talking point), verify it before building on it, don't state it from memory and correct it later.
- **When auditing copy for a specific pattern (em dashes, rule-of-three, whatever), scan attribute values too, not just rendered text nodes.** `alt`, `aria-label`, `title`, `placeholder` are a real, separate blind spot — this session found 19 identical em-dash instances hiding in `alt` text that a text-node-only scan had structurally excluded "by rule" without anyone deciding to exclude them.
- **A classifier that buckets by "nearest preceding tag" is too weak for both prose-vs-caption and interactive-vs-not distinctions.** It produced a false "0 interactive" reading (should have been 6) and a genuine miscount between two copy buckets (358→310, still not fully reconciled as of this handoff — see §9). Scan back for the actual enclosing element, not the nearest one.
- **A screenshot is sometimes the only reliable evidence.** The nav-label collapse from a blanket `nowrap`+`ellipsis` rule, and the Overview overflow/scrollbar in the orphaned responsive zone, were both caught by looking at a rendered screenshot, not by reasoning about the CSS. When something claims to be fixed and a live render is available, look at it before trusting the claim.

## 8. This session's work — Claude Design UI/UX pass (24 Aug 2026)

All of this happened in the separate Claude Design canvas noted in §3, driven from a Claude Code conversation acting as creative director/reviewer over that canvas's own build agent. None of it is code in this repo.

**Copy-quality pass, essentially complete.** Target was zero em dashes/en dashes in prose without losing any claim precision (denominators, unmet-target qualifications, simulated-endpoint disclosures, inference labels, provenance values all had to survive). Result: 99 prose sentences restructured (not re-punctuated — each rewrite had to add a fact, not just swap punctuation), 165 short "label — descriptor" UI captions (badges, buttons, alt text) standardized to a `·` separator matching an existing in-product precedent, 3 of those captions split into genuinely separate interactive elements (a status chip plus its own link) after discovering the status text was previously glued into the link's tab stop, rule titles restructured from one dashed string into two real columns (name + behaviour, independently truncating, independently searchable). Final state: 0 spaced em dashes in prose, 24 unspaced em dashes kept (legitimate empty-cell placeholder glyph), 10 en-dash numeric ranges kept (legitimate range typography). One count reconciliation (231 originally-classified label-pair dashes vs. 310 later accounted for) traced to classifier miscategorization, not a missing bucket — see the lesson above.

**Tagline changed** from "Caught. Cited. Closed." to "Caught. Cited. Gated. Actioned. Closed." — full detail and propagation status in §4a.

**Accessibility/RWD engineering pass**, grounded in the two 24-Aug research passes (§6): a zero-specificity `:where()` rule resets `min-width`/`min-height:auto` to `0` across every container (root-cause fix, not per-component patching — any real floor set elsewhere still wins the cascade); a `[data-reveal]` system tags `tabindex="0"` only on elements actually measuring as clipped (`scrollWidth > clientWidth`, re-checked after `document.fonts.ready` and on resize/mutation), firing on focus rather than hover-only since hover-only reachability is a genuinely open W3C question, not a settled one; `overflow-wrap: anywhere` (never `break-all`, never the deprecated `break-word`) on 83 mono/hash/id elements; 20 rail `clamp()` values rebuilt with a `rem` term instead of bare `vw` (WCAG F94 — pure-`vw` sizing doesn't respond to browser zoom); container queries guarded with `contain-intrinsic-size` against the mandatory-containment zero-collapse; `max-width: 100vw` on the page box as a last-resort fallback (a miss becomes scrollable, not invisibly clipped). A blanket `nowrap`+`ellipsis` rule was tried, broke nav labels (`OVERVIEW` → `O…`) because `nowrap` on those elements meant "sized by content, don't shrink," and was reverted — a real example of a guardrail fighting authored intent, caught from a screenshot.

**Open, unresolved as of this handoff — the responsive "orphaned zone."** The dense console layout was designed for 1920px down to a documented 1366px floor; a separate "Narrow" view was designed for ≤720px; nothing was ever built for the gap between them. That gap is real and was hit live: measured at 875px (924px on a re-measure), `body.scrollWidth` was 1280px against an 875px container — a genuine 404px blowout, not a false alarm. Claude Design's response: route anything below **1280px** (the actual measured console floor, not the originally-guessed 1366px) at *page load* to a separate `Narrow.dc.html`, framed as the WCAG G206 "in-content non-scrolling-layout option" technique, with a `?force=console` override. The stated reason for routing instead of extending live reflow: a prior attempt to reflow down through that zone stripped the countdown dial of the rail height it was sizing itself from, so it grew uncontrolled from width instead — worse than the scrollbar it was meant to fix.

**This was left as an explicit, un-executed instruction, not a settled decision — a fresh session needs to actually do this, not just know about it:** the dial is separately being converted to `aspect-ratio`-based sizing (decoupling it from needing to measure a sibling's rendered height at all). Retest true single-page live reflow through the 720–1280 zone *now that that fix is in*, since the original blocker may no longer exist. If reflow now holds, collapse back to one page per screen with live reflow, no routing, applied identically across all 23 screens. If it still fails for a different, specifically-named reason, keep the routed split, but fix it so crossing 1280px live (not just at load) actually switches the view instead of showing a banner while the dense layout keeps panning. Either way, also audit for other instruments sized off a sibling's rendered dimension rather than their own intrinsic properties (the dial isn't necessarily the only one — blast-radius rings and other ring devices are candidates).

**The full responsive matrix has not had a clean, complete run.** `_audit/matrix.html`/`read.html` exist and persist partial progress via `localStorage`, but every attempted run so far has been blocked (renderer hangs), partial, or deliberately deferred rather than reported as complete-when-it-wasn't. It should run once, across all 23 screens, at a widened checkpoint set (add 1200, 1024, 900, 768, 721, 720, 600, 480, 375 to the original 1920/1440/1366) so a gap like the orphaned zone can't hide between checkpoints again — and it should run *after*, not before, the reflow-vs-routing decision above is settled, since that decision changes what "correct" looks like at every width in that range.

## 9. Hackathon reality-check (24 Aug 2026) — largely superseded, see the strikethrough-style notes

- **The Grand Finale is 5 September 2026** (SDD §15, sourced from a live fetch of the event page on 21 Aug). ~~As of this update (24 Aug) that is 12 days, not 20~~ — **confirmed correct on 25 Aug via a second independent live fetch of the event page** (§12). Recompute the day count from today's date against 5 Sep; do not reuse a hardcoded number from either handoff update, they go stale immediately.
- ~~A live, external, currently-unverified claim may exist~~ — **RESOLVED, and it is worse than "may."** The QR code was decoded on 24–25 Aug: it points to `https://dub.sh/citinel`, which redirects to `https://xzashr.com` — Danish's personal portfolio site, **not** a CITINEL prototype. This is a **confirmed live false claim** on the submitted deck's Thank-You slide, sitting in front of evaluators right now, not a hypothetical. Because it's a redirect, it's fixable by repointing the destination without resubmitting the deck. Full detail: §12.
- ~~Team eligibility hard-disqualifier risk~~ — **RESOLVED 25 Aug (Danish, directly): all 6 members are currently enrolled, Danish is team lead.** The event's 3–6 members / same institute / currently enrolled / at least one female member rule is satisfied. This is no longer a risk; do not re-raise it.
- ~~The application-build decision is explicitly paused~~ — **RESOLVED: Danish authorized the build on 25 Aug.** It is now underway; see §12. Do not re-ask whether to start it.
- **The partner-prize plan is now 8 tracks, not 7, and partially built, not entirely unbuilt.** Lyzr confirmed in-stack; two more tracks (Gemini, CodeMate) added via private organizer channels Danish has access to and this assistant does not. Genuine build progress exists (§12) but is capped by the swarm not existing yet, per an adversarial rubric audit (§13). Eligibility is still necessary, not sufficient — none of this is a guaranteed win, see §13's honesty framing.

## 10. Open items — Danish's calls, not decided by Claude

Full list with context: SDD §22 (23 items). Status as of 25 Aug, highest-priority first:
1. ~~Did CITINEL make the Top 60/80 shortlist?~~ — **RESOLVED 25 Aug (Danish, directly): AeroFyta IS shortlisted.** The finale on 5 Sep is real and is being built toward. This unlocks the P2 shortlist-gated sponsor credits in `PARTNER-ONBOARDING.md` (Render $50, Tavily 8,000 credits, n8n 1-month Cloud Pro, CodeMate 15-day Pro per member) — redemption links are sent privately to shortlisted teams, so check the team inbox / event group chat. The old 11 Aug/Top 60 vs. 13 Aug/Top 80 deadline discrepancy is now moot for planning purposes; the outcome is known regardless of which count was correct.
2. ~~Where does the deck's QR code point~~ — **RESOLVED 24–25 Aug: it points to Danish's personal portfolio, not a prototype.** See §9/§12. Open action: repoint the `dub.sh/citinel` redirect at something real before the finale.
3. ~~Initialize git~~ — **DONE 25 Aug.** Branch `build/stage-1`, 16 commits. Still open: the separate Claude Design UI prototype has no version control of its own.
4. Patentability strategy (§21) — still genuinely undecided.
5. Two research gaps (gamification, community/network-effect features) — still open, low priority.
6. ~~Lyzr AI integration confirmed?~~ — **RESOLVED 25 Aug: yes, confirmed in-stack** by Danish. Built (§12).
7. ~~Confirm Preethi's current enrollment status~~ — **RESOLVED 25 Aug (Danish, directly): all 6 members currently enrolled, Danish team lead.** Eligibility rule satisfied in full. Closed.
8. ~~Application build: start now or wait?~~ — **RESOLVED 25 Aug: started.** See §12.
9. The submitted deck's 13 tagline occurrences and the two badge PNGs (§4a) — still unresolved, unchanged since 24 Aug.
10. The responsive "orphaned zone" retest (§8) — still unresolved, unchanged since 24 Aug; this thread was not picked up this session (Danish chose the application build instead, §12).
11. **NEW (25 Aug): get the Anthropic API key into `.env`.** The single blocking dependency for the rest of the build — see §12/§13.
12. **NEW (25 Aug): the "Best Use of Gemini" and "Best Use of CodeMate" tracks.** Danish stated both exist per private organizer channels (a Google Meet and a separate private meet) this assistant cannot access or verify. CITINEL's own prior research and two live fetches of the public event page show neither track publicly. Proceeding as instructed, but get the organizers' written criteria if at all possible before the finale — building against a remembered verbal description is real risk if the wording differs from what's built. See §13.
13. **NEW (25 Aug): get the Swytchcode Decode-SIH referral link** from event channels (WhatsApp/Discord) — needed to claim the $100 participant credit and required for the CLI-scaffolding criterion.
14. **NEW (25 Aug): run the Startuped platform for real.** `STARTUPED-GTM-PLAYBOOK.md` has the curated inputs and click-by-click path; the actual tool usage (the thing the award judges) is still Danish's to do.

## 11. Suggested next step as of 24 Aug — SUPERSEDED, kept as history

*(This section's guidance is stale — Danish already chose the application-build thread on 25 Aug, and it is now well underway. Preserved for continuity, not as current instructions. Read §13 for the actual current next step.)*

There were two independently-paused threads: the application build, and the Claude Design UI/UX prototype's orphaned-zone retest (§8). Danish chose the application build. **The UI/UX prototype thread was not picked up this session and its state in §8 is unchanged and still accurate** — it remains available to resume whenever Danish wants it.

## 12. This session's work — the application build begins (24–25 Aug 2026)

Danish authorized the application build (previously paused on "Wait," §9/§10). Full engineering detail lives in the git log — read `git log --oneline` and individual commit messages for the by-step reasoning, bugs found, and fixes; this section is the map, not the diff.

**Repo state:** git initialized (`2351cd3` — closes open item 3), branch `build/stage-1`, **16 commits**, **11 of 15 build-ladder steps built**, **108 tests passing**. Run `cd backend && ./.venv/bin/citinel status` for live progress at any time — it reads real files on disk, so it cannot drift ahead of the code.

**Build ladder status:**
| Step | Component | State |
|---|---|---|
| 1–6 | Skeleton, telemetry replay, OCSF normalizer, Sigma engine, anomaly scorer, incident record + audit ledger | ✅ built |
| 7 | **Agent swarm (7-agent Claude pipeline)** | ❌ **blocked — needs `CITINEL_ANTHROPIC_API_KEY` in `.env`, not yet added** |
| 8–10 | OPA-equivalent policy gate, injection quarantine plane, compliance drafter | ✅ built (built out of order, key-free, while waiting for Step 7's key) |
| 11 | Glass-box dashboard | ❌ not started |
| 12 | Sponsor integrations | ⚠️ partial — connectors built and tested for Render/Tavily/VirusTotal/AbuseIPDB/n8n/Swytchcode/Lyzr, all stubbed pending keys; Render's fatal deploy bug (dead `web/app.py`/`worker/run.py` entry points, invalid `worker: plan: free`) found and fixed; **not yet deployed live** |
| 13 | Eval harness | ❌ not started |
| 14 | Demo fallback capture | ❌ not started |

**Stage 1 (the fully offline deterministic pipeline) is genuinely done and verified against real data**, not just written: Splunk BOTS v1 (CC0) was extracted without Splunk by validating each candidate payload rather than trusting a proprietary binary framing format — 945,472 of 955,807 declared events recovered (98.9%), and the two sourcetypes Sigma actually targets (Sysmon, WinEventLog:Security) recovered at **100.0%**. OCSF normalization is **100.00% schema-valid** against a pinned snapshot of the real OCSF 1.9.0 schema (fetched live, not recalled from memory — this caught three real errors: registry activity is class `201001`/`201002` in the `win` extension namespace not `1008`; two classes CITINEL would have used are deprecated as of 1.9.0). Sigma runs the real SigmaHQ `r2026-07-01` pinned release (3,302 rules, 0 parse errors). The demo's hero incident is real: **INC-0417 is the Cerber ransomware chain** (2,487 findings, matches the incident ID already printed on the submitted deck's slide 6), INC-0416 is the P01s0n1vy web-attack chain.

**A pattern held across essentially every step, worth repeating to a fresh session:** run new logic against the real BOTS corpus before calling it done, not just code review. This caught real bugs every single time — a timezone bug that split one incident into two six hours apart (local-time sources vs. UTC sources mixed), a case-sensitivity miss on a Windows SID regex, 19 false-positive PII flags on bare digit runs (fixed by requiring a corroborating label), an injection-detector pattern that would have flagged all ~270,000 benign Sysmon events as attacks, and a worker-polling bug that would have duplicated audit-ledger entries forever. None of these announce themselves in a code read.

**Two structural things worth knowing before touching this code:**
- **No OPA binary or Docker exists on this machine.** The policy gate runs the fallback ladder's own pre-committed rung 2 (signed YAML, in-process) — `policies/citinel-policy.yaml` is canonical, `policies/citinel.rego` is the twin for real OPA at deploy time, and every `Decision` records which engine produced it.
- **Model IDs are never hardcoded** (ledger rule L9). As of a live check on 25 Aug 2026, the current Claude family is `claude-fable-5`, `claude-opus-5` (docs-recommended default), `claude-sonnet-5`, `claude-haiku-4-5` — all pinned snapshots, not evergreen aliases. Verify against `GET /v1/models` at the point of use in Step 7, don't trust this list by the time you read it.

## 13. Partner-prize plan — now 8 tracks, adversarially audited, honestly scored

**The plan grew from 7 tracks to 8 partners during this session**, and two of the additions rest on information this assistant cannot independently verify: **Danish informed the assistant, via private organizer channels (a Google Meet and a separate private meet, not the public event page) that "Best Use of Gemini" and "Best Use of CodeMate" tracks exist and will be awarded.** Two live fetches of the public `oscode.co.in` event page, both before and after being told this, show neither track — CodeMate's own page wording says its Pro benefit is "contingent on the main track win," not a judged track, and Gemini/Google for Developers/MLH are listed as partners with no award specified. **This is not a contradiction to resolve by re-arguing it — it is accepted on Danish's authority and built for accordingly.** But it is real, load-bearing risk that should be named plainly to Danish again if a fresh session inherits this: get the organizers' criteria in writing before the finale if at all possible, since building against a remembered verbal description carries real risk if the actual wording differs.

**Danish also asked, explicitly and more than once, for a "100% guaranteed" win on all 8 partner prizes plus the Bharat Pragati main track.** The honest answer given, and the one any fresh session should hold to: **no judged, competitive prize can be guaranteed by engineering** — the outcome depends on human judges and on what other shortlisted teams build, neither of which code controls. This is not hedging; it is the project's own standing rule (STATE §1.4/§5.1, SDD §15.4: "not a win guarantee — eligibility is necessary, not sufficient"). What *is* controllable, and what this session drove hard on instead, is **rubric completeness**: does the build genuinely meet every stated criterion, with real depth, adversarially stress-tested. Never present rubric completeness as a win guarantee to Danish or in any artifact — the gap between "meets every criterion" and "wins the judged prize" is real and must stay visible.

**An adversarial audit (10 hostile "skeptical judge" agents, one per track + main track + cross-track coherence) was run on 25 Aug and found real, brutal, honest gaps — not inflated scores.** Full results are in that workflow's journal (`~/.claude/projects/-Users-danish-CITINEL/.../subagents/workflows/wf_dd8f5ec8-ce5/journal.jsonl` — may not survive indefinitely; re-run only if truly needed, it cost ~594K tokens). The scores (0–100, rubric completeness, as of 25 Aug before this session's fixes): Render 30, Tavily 24, n8n 55, Swytchcode 20, Lyzr 15, Gemini 6, CodeMate 5, Startuped 30, Bharat Pragati main track 46, cross-track coherence 57.

**The critical finding, independently reached by 8 of the 10 judges: almost every gap traces to ONE root cause, not eight separate ones.** Tavily has no agent to consume its results. Swytchcode has no gate-approved Decision to execute. Lyzr has no verdict to guard. Gemini has nothing to cross-check. n8n's sign-off trigger has no caller outside its own unit test. **Because Step 7 (the swarm) does not exist yet, nothing downstream has anything real to call.** The main-track judge said it in plain words; the coherence judge said "build Step 7 first, then re-sequence." This session fixed the one FATAL, key-independent bug it found (Render's dead entry points and invalid worker plan — §12) directly, without spending further audit budget, and then stopped rather than keep polishing individual connectors that the audit itself said wouldn't move the needle. **Do not re-run the audit or re-derive these scores from scratch** — read the journal if the detail is needed, and don't re-litigate the Gemini/CodeMate verification question with Danish, he has already stated his source.

**The concrete recommended architectural change for Gemini specifically (not yet built):** an independent cross-model verifier — Gemini audits the per-claim citations the Claude Verdict Narrator produces (does each cited log span actually support the claim?), not a second vote on the verdict. This is a genuine, non-decorative fit (it implements SDD §17 findings 4 and 7 on external/cross-model checks beating single-model self-consistency) rather than a forced bolt-on to a Claude-based product. Needs the Verdict Narrator (part of Step 7) to exist first.

**Sponsor-track deliverables already handed to Danish, both committed:** `PARTNER-ONBOARDING.md` (signup priority order, free-tier-vs-shortlist-gated status per partner, exact `.env` mapping) and `STARTUPED-GTM-PLAYBOOK.md` (curated GTM module inputs + the click-by-click path on the Startuped website — the actual platform run is still his to do, since the award is judged on demonstrated tool use).

## 13a. Lyzr attachment points — status (31 Aug 2026)

SDD 15.3 named four Lyzr attachment points. Three are now genuinely wired;
the fourth was deliberately built elsewhere, for a stated architectural
reason:

| # | Attachment point | Status |
|---|---|---|
| 1 | **PII/hallucination second opinion** (`LyzrGuard`) | **Wired** — CITINEL's own deterministic guard always runs (tier 1); Lyzr adds an independent second opinion (tier 2) when configured. Reachable via the compliance CLI. |
| 2 | **Fleet observability** (`LyzrObserver`) | **Wired 31 Aug.** Previously the class existed and was unit-tested, but *nothing in the pipeline ever called it* — a real gap, not a design choice. `SwarmPipeline` now takes an `observer` (defaulting to `NullObserver`) and emits sentinel start/finish plus a per-agent event on every model call. |
| 3 | **Audit mirroring** | **Wired 31 Aug.** All ledger writes in the pipeline now route through one `_ledger()` helper that appends *and* mirrors to the observer. The ledger stays canonical (SDD 15.3's "fulfill, not duplicate"); Lyzr can display the same trail. A structural test greps the source to fail if a future call site writes to the ledger directly and skips the mirror. |
| 4 | **RBAC** | **Deliberately NOT built on Lyzr** — built in CITINEL's own policy layer instead (`policy/roles.py`), and named honestly as *role-adaptive projection*, not RBAC. Two reasons, both load-bearing. (a) Routing authorization to an external control plane contradicts the architecture's own rule that the policy gate is the sole authority, and would make a third-party outage a correctness problem for a bank SOC. Lyzr's other three points fail safe — a second opinion and a dashboard can both be down without changing a verdict; an authorization engine cannot. (b) The spec asks for role-adaptive *depth* ("Tier-1 concise / Tier-3 deep", "two skins"), which is a UX affordance, not a confidentiality boundary. Calling it RBAC would overclaim a security property that isn't there. |

**On the role projection specifically, so nobody later mistakes it for auth:**
`GET /api/incidents/{id}` now projects at the caller's depth via an
`X-Citinel-Role` header, with `?expand=true` returning full depth to anyone.
The role is **self-asserted** — there is no authentication model (§22 Q10,
still open). That is acceptable *only* because nothing is withheld: the CISO
view folds the per-finding array into a count and explicitly discloses what
it folded (`_projection.omitted`), delivering the spec's "citations one click
deeper" rather than a thinner record that looks complete. **Do not extend
this header to gate anything that actually needs protecting until Q10 has a
real answer.**

## 14. Suggested immediate next step (25 Aug 2026, current)

**The single highest-leverage action is getting `CITINEL_ANTHROPIC_API_KEY` into `.env`.** Everything else — the swarm itself (Step 7), and per §13's audit, most of the 8 partner-prize tracks — is gated on it. Copy `.env.example` to `.env` and fill it in; nothing else in the build is currently blocking.

**Two former blockers closed 25 Aug, both by Danish directly:** AeroFyta **is shortlisted** (the finale is real), and **all 6 members are enrolled** with Danish as team lead (eligibility rule fully satisfied). Neither needs re-asking. The shortlist confirmation also makes the P2 sponsor credits in `PARTNER-ONBOARDING.md` claimable — redemption links go out privately to shortlisted teams, so the team inbox / event group chat is worth checking now.

While waiting on the API key, still open and independently actionable:
- **Claim the P2 shortlist-gated credits** (`PARTNER-ONBOARDING.md`) — now unlocked. Render $50 · Tavily 8,000 credits · n8n 1-month Cloud Pro · CodeMate 15-day Pro per member.
- **Get the Gemini/CodeMate track criteria in writing** (§10 item 12, §13) if at all possible.
- **Repoint the QR redirect** (§10 item 2) at something real, or plan the deck-revision conversation.
- **The separate UI/UX prototype thread (§8, §11)** remains available and untouched — Danish may still want it picked up in parallel or after.

Do not restart the adversarial audit, do not re-derive Splunk/OCSF/Sigma facts already verified in §12, and do not offer a win guarantee on any judged prize — hold the line §13 describes.
