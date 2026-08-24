# CITINEL — Handoff Memory

*Prepared 21 August 2026, end of a long research/documentation session; updated 24 August 2026 after a separate, long Claude Design UI/UX session (§8) and a hackathon-reality check (§9), for continuity into a fresh Claude Code session — possibly on a different account than either of the above. This is a map + must-know-facts document, not a duplicate of the full detail — the full detail lives in `CITINEL-SDD.md` (23 sections) and `CITINEL-PROPOSAL.md`. Read this first, then pull the specific section you need from those two files rather than re-reading everything.*

---

## 1. What CITINEL is

**CITINEL — Autonomous Cyber SOC.** An AI Security Operations Center for **Indian cooperative banks and small NBFCs** — a segment with the same RBI/CERT-In regulatory obligations as national banks but none of the security budget. Built by **Team AeroFyta** (Chennai Institute of Technology) for **Decode SIH 2026**, Track "Bharat Pragati," PS4: *"Autonomous Cyber SOC for AI-powered threat detection and automated incident response."*

Tagline (brand hook, updated 24 Aug 2026 — was "Caught. Cited. Closed."): **"Caught. Cited. Gated. Actioned. Closed."** Not yet propagated to the submitted deck PDF (13 occurrences, unrevised) or the two locked badge-tagline PNGs — see §4a.

**Status: this repo is still fully specified, zero lines of application code, no git.** That remains true and is still a deliberate choice per §5. But it is no longer the whole picture: a screen-by-screen UI/UX prototype (23 pages) has been under real, active development in a **separate Claude Design canvas session**, outside this repo, since before this update — see §8. Don't conflate "this repo has no code" with "nothing has been built" when orienting a fresh session.

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

## 9. Hackathon reality-check (24 Aug 2026) — read before planning anything time-sensitive

- **The Grand Finale is 5 September 2026** (SDD §15, sourced from a live fetch of the event page on 21 Aug — treat as fact per §5's own rule on official public dates). As of this update (24 Aug) that is **12 days**, not 20 — a "20 days" figure surfaced once in the conversation that produced this update and did not reconcile with the sourced date. Confirm where that number came from before planning around it; this project has already logged one unresolved date/count discrepancy (SDD §15.4, §22 item 14) and this may be a second instance of the same failure mode.
- **A live, external, currently-unverified claim may exist.** The submitted, "final form" pitch deck's Thank-You slide has a real QR code with the copy "scan the code, the prototype is already running." No prototype URL is recorded anywhere in this repo (SDD §22 item 2, unresolved). If nothing real is behind that QR code yet, that is not a future risk — it is a false claim already sitting in front of evaluators.
- **Team eligibility has an unconfirmed hard-disqualifier risk.** The event's eligibility rule requires at least one female member on a 3–6 person team from the same institute (SDD §15.4). Preethi's current enrollment status needs confirming — if it's ever been in question, this gates the team's eligibility entirely, not just one prize track.
- **The application-build decision is explicitly paused, not decided.** Offered three options (start the build now / resolve open SDD §22 questions first / chase the QR-code exposure first) in the conversation that produced this update, Danish answered "Wait." Zero application code exists, no git repository exists, and nothing here authorizes starting either without him picking this back up explicitly.
- **The partner-prize plan (SDD §15) is fully designed but entirely unbuilt.** All 7 sponsor tracks are "closed by spec" — each mapped to its exact published rubric line — but eligibility is necessary, not sufficient (§15.4's own words): none of it exists as working code.

## 10. Open items — Danish's calls, not decided by Claude

Full list with context: SDD §22 (23 items). Highest-priority ones, folding in what §9 above surfaced:
1. Did CITINEL make the Top 60/80 shortlist? (Deadline/count discrepancy itself unresolved — 11 Aug/Top 60 vs. 13 Aug/Top 80 per different sources.)
2. Where does the deck's Thank-You-slide QR code actually point, and does anything real exist behind it yet? (§9 — may be actively misleading evaluators right now.)
3. Initialize git — the campaign's single biggest point of failure right now (no version control at all, for either this repo or the separate UI prototype).
4. Patentability strategy (§21): pursue a provisional filing, defensive publication, both, or neither — genuinely undecided, and the research found no cost/timeline data for India-specific student filings to plan against.
5. Two research gaps from the 21 Aug pass (gamification/skill-building features, community/network-effect features) — worth a dedicated follow-up or not?
6. Lyzr AI integration (added to the partner-prize plan, §15.3) — confirmed for the actual build or not?
7. Confirm Preethi's current enrollment status (§9 — team-eligibility hard disqualifier if wrong).
8. Application build: start now, or keep waiting? (§9 — currently paused on Danish's own "Wait.")
9. The submitted deck's 13 tagline occurrences, and the two badge PNGs (§4a) — revise the deck (a resubmission question), and finish + install the badge regeneration already underway in ChatGPT.
10. The responsive "orphaned zone" retest (§8) — genuinely blocking further UI/UX polish until it's resolved one way or the other, since it decides whether 23 screens get one architecture or two.

## 11. Suggested immediate next step

There are now two independently-paused threads, not one — ask Danish which he wants picked up, don't assume:
- **The application build** (backend/dashboard/policies/connectors per §2.2), paused mid-conversation on his own "Wait." Do not restart this without him saying so explicitly.
- **The Claude Design UI/UX prototype**, mid-way through the orphaned-zone retest in §8 — this one has a concrete, specific next technical action already queued (retest reflow now that the dial's `aspect-ratio` fix is in) rather than an open strategic question, so it's the more mechanically ready of the two if he wants something to resume immediately.

Either way, also flag §9's timeline correction and the QR-code question early in the conversation — both are time-sensitive enough that surfacing them late would be a real failure, not just a missed nicety.
