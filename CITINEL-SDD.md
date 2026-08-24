# CITINEL — Spec-Driven Development (SDD) Document

*Produced from a full-repository audit of `/Users/danish/CITINEL` on 20–21 August 2026. Everything in this document is sourced directly from files in the repo. Anything not directly evidenced in the repo is explicitly labeled **Assumption** or **Inferred**. The draft was adversarially verified by four independent review passes (docs accuracy, deck/brand accuracy, completeness, assumption-labeling) before finalization.*

*Extended 21 August 2026 with eleven external deep-research passes total (§13–§21, plus a final addition folded into §14), each 95–112 agents, all fan-out search → source extraction → 3-vote adversarial claim verification. External claims are cited to their own sources and confidence-tagged the same way the repo's own research corpus is tagged; nothing from these passes is presented as already built. Ten of the eleven hit either the session-usage limit or a transient infrastructure failure at some point in their run; every one of those ten was resumed to completion via matching `scriptPath`/`resumeFromRunId`/`args`, so cached agent calls hit instantly and only the previously-failed steps re-ran. Four resumes (§16 Architecture, §17 Additional UVPs, §18 Demo Wow-Moment, and the final §14 addition) produced a full, clean, automated synthesis and now supersede any earlier hand-synthesized text for those sections. One resume (§20 Enterprise/Government) fully re-verified every claim on both its original and resumed run but its synthesis step returned corrupted debug/placeholder output both times — a distinct failure mode from the session-limit issue — so §20 was reconstructed by hand directly from that run's own verification journal; this is a more complete recovery than an ordinary hand-synthesis would be, since several previously-"errored/unchecked" claims are now properly confirmed. The §14 addition's resume needed one extra retry after a mid-run DNS/network outage failed 49 of 104 agent calls; the retry recovered via cache and finished the rest live. §19 (UI/UX) and §21 (Patentability) each completed with a full automated synthesis on their first run, no resume needed.*

---

## Repo Read Confirmation

**Total files on disk: 150** across 6 top-level folders (no `node_modules`, no `dist`, no build folders — and notably, **no `.git`**: this directory is not a git repository).

| Type | Count | Read status |
|---|---|---|
| Markdown (`.md`) | 17 | **All 17 read in full** (docs/ ×10, slide-deck-images/ ×6, citinel-brand/ ×1) |
| HTML (`.html`) | 1 | **Read in full** (`slide-deck-images/CITINEL_Placement_Map.html`) |
| PDF (`.pdf`) | 3 | **All 42 pages read** — final-form deck (15 pp), official template (9 pp), organizer webinar deck (18 pp) |
| PNG (`.png`) | 125 | Binary image assets — most catalogued via the two in-repo inventories (`citinel-brand/README.md` asset table, 15 files; `CITINEL_Canva_Layout_Blueprint.md` asset register, 84 files) and visually reviewed as composited in the 15-page deck PDF. **~20 PNGs appear in neither inventory** and were accounted for only by directory listing (detailed in §9.10–9.11). Not opened individually pixel-by-pixel — they are artwork, not source/config/docs |
| `.DS_Store` | 4 | macOS Finder metadata — not read (no informational content) |

**Files not fully read and why:** only the 125 PNGs (binary artwork, covered as above) and 4 `.DS_Store` files (OS metadata). Every file containing text — every markdown, HTML, and PDF page — was read completely. No source code, config, manifest, lock, or `.env` file exists anywhere in the repository, so there were none to read and **no secret values exist in the repo**.

---

## 1. Executive Summary

**This repository contains no application code.** It is the complete **pre-build campaign record, knowledge base, brand system, and final-form pitch deck** for **CITINEL — Autonomous Cyber SOC**, Team AeroFyta's (Chennai Institute of Technology) entry into **Decode SIH 2026** (OSCode/communityX's student-led SIH-preparation hackathon), Track 3 "Bharat Pragati," PS4: *"Autonomous Cyber SOC for AI-powered threat detection and automated incident response."*

What CITINEL **is** (as specified, not yet built): an AI Security Operations Center for Indian cooperative banks and small NBFCs, in which Sigma rules catch known threats deterministically, a swarm of seven Claude agents investigates the rest with **cited evidence** (every verdict points at the exact log line proving it), response actions pass a **readable per-action-class OPA policy** (enrich = automatic; isolate = automatic with rollback; disable a production account = one-click human approval), the pipeline treats all log content as untrusted data (prompt-injection hardening), and confirmed incidents **auto-draft the CERT-In 6-hour report and DPDP breach artifacts** for mandatory human sign-off.

What the repo actually holds today:

1. **`docs/`** — the single source of truth: a master knowledge base, a machine-oriented state file (`CITINEL-STATE.md`, the highest-precedence document), six deep-research reports (market, competition, technical, hackathon-winning patterns, analyst UX, compliance) carrying roughly 250 tagged finding IDs, and a 4-phase idea-tournament/red-team record that locked the concept at 81/90.
2. **`citinel-brand/`** — a frozen, rule-governed brand asset system: 15 inventoried PNGs plus an authoritative README (16 PNGs on disk — `1R.png` is an unlisted stray, see §9.10).
3. **`slide-deck-images/`** + root PDF — 103 PNGs (slide graphics, six team headshots, two logo lockups), six assembly/layout guides, one HTML placement map, and the **final-form 15-slide Round-1 deck** (`CITINEL_PS4_AeroFyta_DecodeSIH2026.pdf`). *(Inferred: submitted — the PDF is complete and the 11 Aug 2026 deadline has passed, but no artifact in the repo records the submission itself.)*
4. **`partners-logo/`, `ppt-template/`, `webinar/`** — sponsor logos and organizer reference material.

The build phase (3-stage MVP: pipeline → agent swarm + policy gate → compliance drafter + glass-box UI) is specified in detail but **has not started in this repository** — the planned `backend/`, `dashboard/`, `policies/`, `connectors/` folders referenced in `docs/README.md` do not exist.

This edition additionally externally validates the product's messaging (§13, 20 UVPs/USPs checked against 2025–2026 market and competitive evidence) and proposes a candidate feature roadmap (§14, 21 items — none committed, all flagged for Danish's approval).

*Further extended 21 August 2026 (§15) with a live fetch of the official event page (oscode.co.in/events/decode-sih-2026), closing every partner-prize eligibility gap it surfaced — including one partner (Lyzr AI) that was entirely absent from the prior architecture. This is now the target build plan, not a backlog proposal.*

---

## 2. Current Architecture

### 2.1 What exists on disk (the real, current architecture)

```
CITINEL/                                  ← NOT a git repository; 150 files, ~285 MB
├── CITINEL_PS4_AeroFyta_DecodeSIH2026.pdf  ← final-form 15-slide deck (4.9 MB)
├── citinel-brand/        ← 16 brand PNGs + README.md (authoritative brand law)
├── docs/                 ← knowledge base (10 .md, ~370 KB of text)
│   ├── CITINEL-STATE.md          ← SINGLE SOURCE OF TRUTH, highest precedence
│   ├── CITINEL-MASTER-KB.md      ← hackathon facts + locked idea spec
│   ├── orchestrator-phase0-4.md  ← historical idea-tournament & red-team record
│   ├── A1-market-impact.md … A6-compliance.md  ← six research reports
│   └── README.md                 ← public-facing project readme
├── slide-deck-images/    ← 103 PNGs + 6 assembly guides + placement-map HTML
├── partners-logo/        ← 6 sponsor logo PNGs (Codemate, Render, Startuped, SwytchCode, Tavily, n8n)
├── ppt-template/         ← official 9-page Decode SIH ideation template (PDF)
└── webinar/              ← organizer kickoff/orientation deck (18-page PDF)
```

**Documented precedence chain when sources disagree** (stated in `CITINEL-STATE.md`): `CITINEL-STATE.md` > Master KB Part 2 > orchestrator record > research reports. The orchestrator MD deliberately retains superseded phrasing as history. The brand README declares itself the authority on all brand questions.

- **Stack/frameworks/versions**: none — there is no code, no `package.json`/`requirements.txt`/lockfile, no CI, no `.env`.
- **Entry points**: for a human or AI agent, the entry point is `docs/README.md` → `docs/CITINEL-MASTER-KB.md` → `docs/CITINEL-STATE.md`.
- **"Request lifecycle" today**: documentation-only — research findings (tagged IDs like `A1-F26`, `COMP-F18`, `SAFE-F03`) flow into the locked spec, which flows into slide copy and the deck, with deck numbers traceable to finding IDs and a Contradiction Ledger (L1–L11) governing how claims may be phrased.

### 2.2 The planned product architecture (specified in docs + deck; NOT built)

Everything below is **specification**, evidenced in `CITINEL-STATE.md` §1.5/§1.7, KB §2.5, the deck's Tech Stack and Architecture Diagram slides (slides 8–9), and `orchestrator-phase0-4.md` Phase 4.

**Planned alert lifecycle ("one pipeline"):**

```
Bank endpoints / Identity+AD / Network+Firewall / (Core banking = roadmap)
  → syslog · webhooks · Fluent Bit                      [ingest]
  → OCSF normalizer                                     [one schema]
  → Sigma engine (3,000+ community rules) + statistical anomaly scorers
       └─ known threats close deterministically, before any model
  → 7-agent Claude swarm (only for what rules can't express):
       Sentinel (orchestrator) · Triage Router (Haiku-class, strict JSON)
       · Enrichment Squad (parallel VirusTotal/AbuseIPDB/GeoIP/Tavily)
       · Correlator (extended thinking → MITRE ATT&CK kill-chain)
       · Verdict Narrator (Citations-grounded; separate role because citations
         are incompatible with strict structured outputs in one call)
       · Response Marshal (proposes actions, consults OPA gate, executes
         per dial tier against SIMULATED endpoints only)
       · Scribe (CERT-In/DPDP drafts, Sigma+playbook drafts, handover cards)
  → OPA policy gate + autonomy dial (Shadow → Assist → Autonomous, per action class)
       enrich = auto · isolate = auto + rollback · account-disable = human approval
  → append-only audit log (structured decisions + tool calls; never thinking summaries)
  → compliance drafter (CERT-In 6-hour draft ~70–80% fields; DPDP artifacts ~50–60%)
  → human sign-off (mandatory by design; "we draft, we never file")
  → glass-box dashboard (investigation replay, approval cards, regulatory clock)
```

**Safety plane (specified):** quarantined untrusted-content plane (log content is data, never instructions) · instruction/data separation · injection detector layer · deterministic egress allow-list · provenance-flagged rendering of untrusted strings inside report drafts (red quarantine styling — the "anti-laundering" moment) · blast-radius rings + staged rollout (CrowdStrike 8.5M-device lesson) · claim discipline "mitigates, never solves."

**Planned deployment & runtime stack:** PostgreSQL + Redis (managed) on Render — web service (glass-box UI) + background worker (pipeline) + managed datastores = 3 service types, always-on demo URL (deck slide 8; STATE §1.10) · "Python services" appears in the slide-copy guides (`CITINEL_Slide_Text_Final.md`, slide-8 block) though not in STATE or visibly on the shipped slide · n8n for escalation/notification/report-export flows (OPA remains the sole policy authority) · Swytchcode for agent→API execution (ticketing + comms) · Tavily for live OSINT enrichment · Codemate.ai as build-time AI pair tool (explicitly not runtime) · Atomic Red Team attack replays only in an isolated VM.

**Model layer** (A3 research): Claude with tiered model use (Haiku-class routing, larger models for correlation), prompt caching, ~5¢/incident target economics (own instrumented figure, to be labeled [INFERENCE]). Air-gapped deployments via a pluggable local model are explicitly roadmap, not MVP.

**Fallback ladder (pre-committed):** (1) copilot shape if multi-agent correlation is unstable early — agents recommend, humans drive; (2) signed YAML config file enforcing identical per-action semantics if OPA integration slips; (3) pre-recorded BOTS v1 replay if venue hardware is risky.

**Declared out of scope for MVP (on the deck itself):** multi-tenancy · honeypots/deception · model fine-tuning (correction memory only) · machine filing to CERT-In (no API exists; channel is email/phone/fax + non-mandatory PDF form) · full ATT&CK coverage (curated set) · Indic UX beyond one sample narrative (roadmap).

---

## 3. Data Layer

**Implemented today: none.** No database, no schema files, no migrations, no ORM, no SQL/Prisma/GraphQL anywhere in the repo.

**Specified (planned) data layer**, from STATE/KB/deck:

| Planned store / structure | Purpose | Evidence |
|---|---|---|
| **OCSF-normalized event records** | Single schema for all ingested telemetry (syslog/webhook/agent → OCSF) | STATE §1.5, deck slides 8–9, PIPE-F01 |
| **Incident record ("one record, five states")** | The central entity; deck slide 6 shows its lifecycle: Raw Event → OCSF Record → Cited Verdict → Gated Action → Signed CERT-In Form, all under one incident ID (demo incident `INC-0417`). Brand hook doubles as the state machine: **Caught → Cited → Gated → Actioned → Closed** *(updated 24 Aug 2026, was Caught → Cited → Closed — see HANDOFF-MEMORY §4a)* | Deck slide 6 (unrevised, still three-word form); brand README tagline system |
| **PostgreSQL (managed, on Render)** | Primary persistence (*Inferred:* incident records, verdicts, policy decisions — the docs name the engine but no table design exists) | Deck slide 8; STATE §1.10 |
| **Redis (managed, on Render)** | *Inferred:* caching/queue — required by the hash-first dedup + enrichment-caching design (VirusTotal 4/min cap) | Deck slide 8; PIPE-F04; AGT-F10 |
| **Append-only audit log** | Structured decisions + tool calls with detect-time → sign-time proof; explicitly *never* model "thinking summaries" (AGT-F06 caveat: thinking output is a summary, not a forensic record) | STATE §1.5; SAFE-F06 |
| **Sigma rule corpus** | 3,000+ community rules in, plus machine-drafted rules out — every generated rule passes a human review gate before joining the corpus; rules export as portable open artifacts | PIPE-F07/F08/F10; deck slide 12 |
| **Correction memory / org-context few-shots** | Analyst corrections stored as few-shot context, explicitly *not* fine-tuning | STATE §1.5 knowledge flywheel; UX-F31 |
| **Eval harness dataset** | ~20 labeled incidents, LLM-as-judge scoring; the published FP rate comes from here (<10% target) | AGT-F12; deck slide 10 |
| **Demo telemetry** | Splunk BOTS v1 (CC0) replay; Atomic Red Team (MIT) in isolated VM; LANL labeled data for ground truth | DEMO-F01/F02/F05 |

**Relationships** (*Inferred* from the pipeline spec — no ER diagram exists): incident 1—N events, 1—N verdicts (each verdict N—N cited log lines), 1—N proposed actions (each action → one policy decision → optional rollback token), 1—1 CERT-In draft + 1—N DPDP artifacts, 1—N audit entries, 0—N generated Sigma rules.

---

## 4. Backend / API Surface

**Endpoints found in the repo: zero.** There is no backend, no route definitions, no OpenAPI spec, no auth code.

What the documentation commits the future backend to expose or consume (all planned, none built):

**Inbound (ingest):**
- Syslog listener, webhook receivers, Fluent Bit forwarding (PIPE-F03). The slide-copy guides phrase it: "Ingestion is syslog and webhooks — nothing at the branch changes" (`CITINEL_Slide_Text_Final.md`, slide-11 block); the shipped slide 11 itself reads "Syslog, webhooks, agent. A new source is a mapping, not a rebuild."

**Outbound (consumed third-party APIs):**
- VirusTotal (free tier: 4 req/min, 500/day — hard cap driving cache design), AbuseIPDB (1,000/day), MaxMind GeoLite2, Tavily search, Swytchcode (agent→API execution across ≥2 ecosystems, e.g., ticketing + comms), n8n workflows (export/notify), Anthropic Claude API.

**Response actions:** executed **only against simulated/mock endpoints** (mock host, mock directory, mock firewall — deck slide 11); real connectors are explicitly roadmap.

**Auth requirements:** nowhere specified. **Assumption:** the authentication/authorization model (analyst vs CISO roles, per the two-role views on the UX slide) is an open design decision — the docs distinguish Analyst view and CISO view but define no auth mechanism.

**Human-facing surface:** a Render-hosted web service serving the glass-box dashboard, plus a background worker running the pipeline (deck slide 8). No URL routes are specified anywhere; the Thank-You slide carries a real QR code and a reserved demo-URL slot (see Open Questions — the QR's destination is not recorded in the repo).

---

## 5. Business Logic & Domain Rules

### 5.1 Rules the repository actually enforces today (documentation-governance rules)

These are the "business rules" genuinely in force in this repo, and they bind any future work:

1. **Precedence:** `CITINEL-STATE.md` overrides everything; older codenames "PRAHARI"/"CERTIUS" must be silently normalized to CITINEL.
2. **Name freeze:** the product is styled **"CITINEL — Autonomous Cyber SOC"**; rename ticket may open only after 5 Sep 2026.
3. **Zero PS-drift:** every output must visibly serve all five load-bearing PS4 terms (AUTONOMOUS, CYBER SOC, AI-POWERED, THREAT DETECTION, AUTOMATED INCIDENT RESPONSE).
4. **Honest-claims ledger (L1–L11), binding all numbers:** L1 talent gap → cite 790K (ISC2 2023) only, hedge the rest · L2 every incident count labeled by denominator (CERT-In incidents ≠ NCRP complaints — never merged) · L3 FP rates only as ranges, <10% stated as *target* · L4 alerts/day → peer-reviewed 3,832 for enterprise claims · L5 autonomy marketing → cite convergent gating behavior, not vendor percentages · L6 market size only as ranges with scope ambiguity declared · L7 "6 hours under the Apr 2024 RBI Master Directions" phrasing · L8 CIMS → trust primary absence, draft-and-export design · L9 model names verified live before appearing on any asset · L10 a credible demo artifact is mandatory at idea stage · L11 the Decode template (H1-F02) governs, not the SIH 6-slide format.
5. **Standing hard rules** (STATE header, distinct from the ledger): honest claims only — DPDP framed as a *closing runway to ~May 2027*, never current enforcement · "we draft, we never file" · no timelines ever — "Danish owns all timelines" (official external deadlines may be stated as facts) · clean-room: public knowledge only; the lead's employer specifics never appear (public framing: "builds agentic systems professionally") · sponsor integrations genuine, never decorative ("OPA stays the authority — n8n is orchestration glue, never the gate").
6. **Trace-gap labeling duty (TG-1):** the ₹1–2 crore/yr Indian SOC payroll figure is a derived number and must always carry `[INFERENCE from A1-F29/F30/F31]`.
7. **Differentiation line discipline:** only the narrowed §1.4 line is permitted; the old "Copilot is not available in Indian government clouds" claim is **retired forever** (its source concerned US GCC licensing). *(The historical orchestrator record still contains the retired line in its Phase-4 section — preserved intentionally as history, superseded by STATE.)*
8. **Human sign-off is mandatory by design** — repeated across STATE, KB, deck, and the Q&A bank.
9. **Locked artifacts:** the 100–150-word Slide-6 solution box (130 words) is verbatim-locked; the one-breath pitch must be delivered verbatim.
10. **Brand hard rules** (citinel-brand/README.md): assets are frozen (no regeneration/restyle/upscale); exactly one falcon mark; exact spellings CITINEL/AEROFYTA; three locked tagline tiers; navy-on-light / white-on-dark placement only; gold accent restricted to citation highlights and the regulatory clock; red reserved for severity; never mix the legacy swirl and current faceted AeroFyta emblems on one surface.

### 5.2 Product domain rules (specified for the future system)

- **Rules before models:** Sigma runs first and closes known threats deterministically; Claude reasons only over correlation and novel chains; agents are used only where breadth/reasoning pays the ~15× token cost.
- **Per-action-class autonomy:** reversible actions run autonomously; isolation carries a rollback token; consequential actions (production account disable) cannot execute without one-click human approval; blast-radius rings cap exposure.
- **Citations mandatory:** every verdict must cite the exact log line (Citations API); cited-narrative and strict-JSON outputs are separated into different agent roles because they cannot coexist in one call.
- **Untrusted-content plane:** log content can never become instructions; injected strings render escaped, red-flagged, provenance-tagged inside drafts; egress is allow-listed; the defense is framed as "mitigates, never solves."
- **Compliance clock:** on confirmation, CERT-In 6-hour draft (~70–80% of form fields machine-draftable) + DPDP two-stage artifacts (~50–60% of content) are generated from the live incident record; legal characterization, data-principal consequence assessment, and sign-off remain human.
- **Flywheel with a gate:** every resolved incident emits a portable open Sigma rule + playbook draft that must pass human review before joining the corpus.
- **Measurement:** FP rate is published from the ~20-incident labeled harness, never claimed in advance.

---

## 6. Existing Frontend

**None.** No HTML/CSS/JS application code exists (the single HTML file is an internal Canva placement reference, not product UI). No routing, no components, no state management, no styling framework.

The repo does, however, contain a **detailed UX specification** for the future frontend (A5 research → STATE §1.5 → deck slide 7):

- **Three signature UX moments:** (A) glass-box investigation replay — a clickable timeline of the 7-agent pipeline (Ingest → Match → Enrich → Correlate → Narrate → Propose → Record) where every claim carries an evidence chip that opens the exact raw log row, with a replay scrubber; (B) policy-guarded approval card — action name, assets-affected count, policy clause reference (e.g., `policy_clause=4.2`), blast-radius rings, Approve/Deny; (C) regulatory-clock auto-report + shift-handover card (open incidents, awaiting approval, actions taken, watch list — generated at shift end).
- **Ten evidence-traced UX design principles** (A5 §5): evidence-first narrative before verdict; visible/replayable chain-of-reasoning; honest confidence with counter-evidence ("Supports and argues against" panel, "confidence, not certainty"); one-click gated actions; configurable autonomy tiers; role-adaptive explanation depth (Tier-1 concise / Tier-3 deep; Analyst view vs CISO view over the same record); immutable queryable audit trail; visible feedback loop; unified workspace (kill the 5-console "tab marathon"); auto-drafted compliant reporting on the clock.
- **Anti-patterns explicitly designed against:** explanation theater / fluent-explanation over-reliance (include counter-evidence and forcing functions); a lone clean accuracy percentage; black-box verdicts.
- **Assumption:** dark-first UI is implied by the brand surface map ("Dark dashboard header: citinel-wordmark-white.png"; app splash on dark) but has never been stated as a decision.

---

## 7. Integrations & Third-Party Services

No secrets exist anywhere in the repo (no `.env`, no keys, no tokens). All integrations are documented intentions with named wiring points:

| Service | Role | Where wired (per docs/deck) |
|---|---|---|
| **Anthropic Claude** | The agent layer: 7-agent swarm; Citations; structured outputs; extended thinking; prompt caching; tiered models | STATE §1.5; A3 AGT-F01..F12; deck slides 6/8/9 |
| **Swytchcode** (sponsor) | Agent→API execution path for Response Marshal & Scribe (≥2 ecosystem APIs: ticketing + comms) | STATE §1.10; deck slide 8 |
| **Render** (sponsor) | Hosting: web service (glass-box UI) + background worker (pipeline) + managed PostgreSQL + Redis; always-on demo URL | STATE §1.10; deck slide 8 |
| **n8n** (sponsor) | Escalation, notification, report-export workflows — now with an explicit visible demo beat (§15.3 Beat 5b); explicitly *never* the policy authority | STATE §1.10; deck slide 8 |
| **Tavily** (sponsor) | Enrichment Squad's live OSINT arm (IOC context, actor background, CVE chatter) feeding cited narratives, with source/timestamp now shown in the citation chip itself (§15.3) | STATE §1.10; deck slides 8–9 |
| **Startuped.ai** (sponsor) | GTM/business validation; deck slide 13 (Business Model Canvas) "is built from it" — to be run through the platform itself per the §15.3 checklist, not just Claude-derived research | Deck slide 8 |
| **Codemate.ai** (sponsor) | Build-time AI development agent — explicitly "not runtime" | Deck slide 8 |
| **Lyzr AI** (sponsor) | Governance/observability control plane over the 7-agent swarm — fleet observability, a second independent Hallucination & PII Guard on Verdict Narrator output, RBAC formalizing Analyst/CISO views, and fulfillment of the SAFE-F06 audit-log requirement. **Newly added §15.3 — pending Danish's confirmation (Open Question 15), not yet reflected in STATE or the deck** | §15.3 (this SDD only) |
| **VirusTotal / AbuseIPDB / MaxMind GeoLite2** | Threat-intel enrichment on free tiers (4/min·500/day; 1,000/day; free DB) with hash-first dedup + caching | PIPE-F04..F06; deck slide 11 |
| **OPA (Open Policy Agent)** | The per-action-class policy gate; readable/auditable policy artifact | SAFE-F03; deck slides 8–9 |
| **Sigma / SigmaHQ** | Deterministic detection corpus (3,000+ rules) + portable rule export format | PIPE-F07; deck slides 8/12 |
| **OCSF** | Normalization schema | PIPE-F01; deck slides 8–9 |
| **MITRE ATT&CK (+ TRAM precedent)** | Kill-chain narrative mapping (curated technique set, not all 600+) | PIPE-F08 |
| **Splunk BOTS v1 (CC0) / Atomic Red Team (MIT) / LANL dataset** | License-clean demo telemetry and ground truth; ART only in an isolated VM | DEMO-F01/F02/F05 |
| **Fluent Bit** | Log forwarding/ingest | PIPE-F03 |

Organizer/context integrations: OSCode/communityX event platform (registration, submission), Canva (deck assembly — the entire slide-deck-images toolchain targets Canva), WhatsApp/Discord community channels (KB Part 1).

---

## 8. Non-Functional Constraints (signals observed in the docs)

- **Cost ceiling:** ~5¢/incident target on tiered models + prompt caching (own instrumented figure, must be labeled [INFERENCE]); multi-agent ~15× token cost accepted only where breadth pays; free-tier API caps are hard design inputs (cache-first, hash-first dedup so VirusTotal's 4/min can never fire mid-demo).
- **Latency/throughput targets:** the deck's "2 AM test" walks alert-land (02:04) → CERT-In draft ready (02:09) → human sign-off (07:30) — minutes inside a six-hour clock; assisted-investigation benchmarks cited at 58 min vs 105 min manual (CSA, n=148). *(The deck states both "24 minutes inside the clock" and "34 minutes inside the clock" in different elements of slide 11 — an internal inconsistency to resolve.)*
- **Quality bar:** published (not claimed) FP rate on a ~20-incident labeled harness; <10% target vs a 46–80% industry survey range.
- **Security posture:** injection defense-in-depth (quarantine plane, instruction/data split, detector, egress allow-list, provenance-flagged rendering); response actions only against mocks; Atomic Red Team only in an isolated VM; append-only audit with detect-time/sign-time evidence; least-privilege framing throughout.
- **Compliance-by-design:** CERT-In 6-hour clock, DPDP 72-hour two-stage reporting, RBI/SEBI/IRDAI sector overlays; 180-day log retention and NTP sync obligations noted in research; human sign-off legally mandatory.
- **Scalability/availability:** 24×7 operation is the product premise; multi-tenancy explicitly deferred; B2B2X white-label ("sell once, protect many" — one MSSP integration reaches hundreds of banks).
- **Sustainability:** open standards (OCSF, Sigma), portable exports as an anti-lock-in strategy, open-core survival precedents (Wazuh, TheHive→StrangeBee), named non-dilutive runway (C3iHub ₹30L; Cyber Surakshit Bharat channel).
- **Demo resilience:** primary demo mode is pre-recorded BOTS replay (guaranteed offline), live agents as garnish; three-step fallback ladder pre-committed.

---

## 9. Known Gaps / TODOs / Tech Debt (explicitly flagged in the repo, plus audit findings)

### Flagged by the docs themselves
1. **Open items only Danish can close** (STATE §5, verbatim checklist): ① submission-portal mechanics *(now moot post-deadline — see Open Questions)*; ② instrument own cost-per-incident / cost-per-report baselines during build; ③ optional 2–3 real MSSP quotes (pricing anchors A1-F33/F34 are Med/1-source); ④ sponsor free-tier quota checks (Swytchcode $100 scope, Render $50, n8n, Tavily 8k, Startuped 1k; VT/AbuseIPDB re-confirm); ⑤ confirm the OSCode PS list carries no extra PS4 text; ⑥ live Anthropic model-name check whenever a deck/build asset names a model (standing L9 duty).
2. **Open risks** (STATE §1.9): moat (an incumbent could ship CERT-In drafting in a quarter); mock-eval calibration unknown until the first OSCode mock; verbatim-delivery execution risk; Med-confidence pricing anchors; free-tier caps in live settings.
3. **Novelty sensitivity:** the NOV-9 fresh-verification condition was **closed post-lock on 2 Aug 2026** ("novelty verified and narrowed" — STATE §1.1, §5), but A6 flags any *future* vendor shipment of CERT-In/DPDP form auto-population as a trigger that would erode the novelty claim — a standing sensitivity subsumed under the moat risk above.
4. **Brand debt** (brand README "Provenance and known limitations"): all assets are AI-generated raster PNGs; **no vector (SVG/AI) sources exist**; a manual vector rebuild is planned before any trademark filing/print/merch; the horizontal lockup aliases above ~60% of native width.
5. **Awaiting next phases** (STATE §7): H2 mock-evaluation calibration passes; "Phase B" work packages (sponsor-integration, deck-polish, demo-script) generate on request.

### Found by this audit (not previously flagged)
6. **No git repository.** The entire campaign record has no version control (`Is a git repository: false`). Highest-leverage single fix available.
7. **The build hasn't started here:** `docs/README.md`'s structure diagram promises `ppt/` and `(build)` folders (`backend/ · dashboard/ · policies/ · connectors/`) that don't exist; the deck PDF sits at the root, not in `ppt/`.
8. **Deck vs. guides vs. docs — evidence-chain drift.** The slide-copy guides' 20-item reference list was already updated to the 2026 sources (RBI Commercial Banks Directions 2026 paras 182/221–223 of 31 Jul 2026; IBM 2026 India + global cuts; SANS 2026 n=444; OpenSec arXiv:2601.21083; Gartner 2 Jun 2026; Five Eyes 1 May 2026), and the guides' slide-4 copy already states the 31 Jul 2026 RBI 24×7 mandate. The *actual* residual drift is: (a) the guides retain `[FILL]` placeholders (team names, demo URL, contact) and simpler copy than the shipped slides (e.g., the team slide's six one-line roles vs the deck's seat/backup/question-routing layout; slide-8/11 body text differs); (b) a handful of deck figures have **no counterpart anywhere in docs/ or the guides** — notably ₹255M / "Rs 25.5 crore, up 15.9%" (IBM 2026 India record, deck pp. 3/15) and several Evidence-slide chips (Vectra 2026 "63% unworked," SANS 2026 "36% governed," OpenSec "82.5% false," Gartner "half via injection," IBM 2026 "1 in 4 AI-enabled," "Rs 31.6 cr unautomated"); and (c) the docs/ **finding-ID chain stops at the 2025 editions** (A1-F10 = ₹220M IBM 2025; WIN-F31 = 790,000 ISC2 2023) — the 2026 numbers on the deck carry no finding IDs or archived URLs in the research corpus, which is against the corpus's own full-URL/traceability discipline.
9. **Internal deck inconsistencies:** slide 11 shows both "24 minutes inside the clock" and "34 minutes inside the clock"; the deck uses both "789,793" (Evidence-slide chip, attributed ISC2 2023 — a precision variant of WIN-F31's 790,000) and the rounded "790,000" (slides 4–5) for the same figure.
10. **Uninventoried assets (~20 PNGs appear in no in-repo inventory or guide):** `citinel-brand/1R.png` (violates the brand README's own rule 7 — its inventory lists 15 files, disk holds 16); and in `slide-deck-images/`: `14R.png`, `SP7.png`, `2.B1–2.B3.png`, `4.6.png`, `4.7.png`, `10.6.png`, `11.6.png`, `12.6.png`, `12.7.png` (the blueprint's register claims "78 deck images (1.1–15.5)" while 87 numbered PNGs exist on disk), plus the six team headshots (`danish/preethi/sanjay/ismail/hritik/elangovan.png` — visibly used on the shipped Team slide but referenced by no guide) and `logo_lockup_square.png`/`logo_lockup_wide.png`.
11. **Brand README "composites" rule is stale:** the README states composites (side-by-side lockup, footer strip, demo QR) "are not committed yet … say they are planned, not present" — yet two lockup composites (`logo_lockup_square/wide.png`) exist in `slide-deck-images/`.
12. **`.DS_Store` files** (4) committed alongside real assets — harmless noise, worth a `.gitignore` when git is initialized.
13. **External research pass integrity note (21 Aug 2026, updated):** across all eleven deep-research passes run for this document, ten hit either a session-usage limit or a transient infrastructure failure mid-run; every one was resumed to completion the same day. Nine of those ten (including §14's original pass, §16, §17, and §18) now have a full, clean, automated synthesis superseding any earlier hand-synthesis. The one exception is §20 (Enterprise/Government), whose synthesis step returned corrupted debug/placeholder output on both its original and resumed run despite clean verification each time — §20 was reconstructed by hand directly from that run's verification journal instead, and is flagged as such in its own section header. §19 and §21 needed no resume at all. Flagging this for transparency, consistent with this document's own evidence-labeling discipline.

---

## 10. User Personas & Core User Flows *(documented in research; "core flows" partially inferred)*

### Personas (documented, ranked in A1 §4)
1. **Primary buyer-user: IT head / CISO-equivalent of a cooperative bank or small NBFC** (ranked 19/20) — "one officer, a round-the-clock duty, alone"; bound by RBI's 24×7 C-SOC mandate + 6-hour reporting; budget ₹25k–₹1L/month vs $1M+/yr staffed-SOC cost.
2. **Channel operator: MSSP / SEBI-mandated Market-SOC operator (NSE/BSE)** — the B2B2X buyer who white-labels the engine; "they keep the customer, we keep the engine."
3. **SOC analyst (Tier-1/2/3)** — the daily operator; Tier-1 does cited-triage relief, Tier-3 gets deep rationale (role-adaptive depth); shift-handover pain is a first-class design target.
4. **CISO/DPO/sign-off authority** — reviews approval cards and signs regulator drafts (CISO view).
5. **Secondary skins (roadmap):** SEBI-regulated small entities (17/20), hospitals (17/20).
6. **Audience personas** (for the campaign itself): SIH-style judges (five red-team personas incl. "tired evaluator #147"), mentors, sponsors.

### Core user flows (from STATE §4 demo beats, deck slides 6–7, A5)
- **F1 — Autonomous cited triage (the 2 AM flow):** alert lands → OCSF normalize → Sigma/anomaly gate → swarm investigates → verdict with citation chips → reversible actions auto-run; analyst later replays the glass-box timeline and clicks any claim to the raw log row.
- **F2 — Policy-gated approval:** Response Marshal proposes account-disable → approval card with assets-affected, policy clause, blast radius → human Approve/Deny → action + decision sealed into the audit log (isolation variant carries a visible rollback token).
- **F3 — Compliance clock:** incident confirmed → Scribe drafts CERT-In 6-hour form (70–80% pre-filled) + DPDP artifacts → human edits/signs → export (email/PDF; never machine-filed) → audit ribbon proves detect-time → sign-time.
- **F4 — Shift handover:** at shift end, a handover card preserves open incidents, awaiting-approval queue, actions taken, watch list with time-sensitivity.
- **F5 — Attack-then-defense demo (the wow):** poisoned log ("ignore previous instructions…") hijacks a naive side-by-side agent, then dies in CITINEL's quarantine plane; its escaped, red-flagged remnant is visible inside the signed draft.
- **F6 — Flywheel review:** closed incident → drafted Sigma rule/playbook → human review gate → corpus grows; exports are portable ("take your detections and go").
- **F7 — Judge/demo flow (campaign):** QR on the Thank-You slide → three-minute walkthrough (live/brief/video) → replay incident INC-0417 end-to-end.

---

## 11. Screen / Page Inventory Needed (hand-off list for Claude Design)

Derived from the three signature UX moments, ten UX principles, demo beats, deck slides 6–9, and the planned Render web service. **Screens marked ★ are explicitly specified in the repo** (STATE §1.5 signature moments; deck slide 7's annotated UI mockups; deck slide 14 / STATE §4 demo). **Everything else is this audit's synthesis — screens inferred as necessary to complete the specified flows — and needs Danish's confirmation.**

**Shell & identity** *(inferred)*
1. Splash / login (dark surface, `citinel-badge-tagline-dark` or white wordmark; auth model TBD)
2. App shell: dark dashboard header (white wordmark — the one shell element the brand surface map does specify), global regulatory-clock element (evidence-gold accent), incident state legend (Caught → Cited → Gated → Actioned → Closed) — this matches what the Claude Design shell already renders; the spec line was stale even before the 24 Aug tagline update

**Core operational screens**
3. SOC overview dashboard — live alert/incident counts, autonomy-dial position, clock statuses, agent health *(inferred)*
4. Alert queue / triage list — Sigma-closed vs escalated-to-swarm lanes; severity routing *(inferred)*
5. ★ **Incident detail — Glass-box investigation replay** *(hero)* — 7-step agent timeline (Ingest → Match → Enrich → Correlate → Narrate → Propose → Record) with replay scrubber; per-claim citation chips opening the exact raw log row (unedited); agent status rail; MITRE ATT&CK kill-chain narrative
6. Evidence viewer — raw log line(s) with provenance metadata; quarantine styling for untrusted content (red, escaped, "untrusted content — from log") *(inferred as a distinct surface; the quarantine rendering itself is specified)*
7. ★ **Approval card / action center** *(hero)* — action, assets affected, policy clause, blast-radius rings, Approve/Deny, rollback-token status; plus a pending-approvals queue *(queue inferred)*
8. ★ **Confidence & counter-evidence panel** — "supports / argues against," confidence-not-certainty bar, retired-vs-kept evidence ("we deleted a good line — checked, then cut") — drawn on deck slide 7
9. ★ **Shift handover card** — open incidents / awaiting approval / actions taken / watch list; generated at shift end
10. ★ **Compliance clock module** *(hero)* — CERT-In 6-hour draft review with pre-filled-field map (70–80%), human-edit + sign-off flow, countdown; DPDP artifact set; export confirmation — "we draft, we never file" messaging

**Governance & system** *(all inferred as screens; the underlying mechanisms are specified)*
11. Readable policy screen — the per-action-class OPA policy rendered human-readable; autonomy dial (Shadow/Assist/Autonomous) per action class; policy-change history *(read-only vs editable is an open product decision — deck slide 4 says the IT head "can read and change" the rulebook)*
12. Append-only audit log viewer — decisions + tool calls, detect-time → sign-time ribbon, queryable
13. Sigma flywheel / rule-review queue — machine-drafted rules awaiting human review; corpus browser; portable export
14. Eval & measurement page — published FP rate vs <10% target on the 20-incident harness; cost-per-incident instrumentation
15. ★ **Analyst view vs CISO view** — role-adaptive depth over the same record ("two roles, one record," deck slide 7) — two skins of screens 5–12
16. ★ **Demo mode** — INC-0417 end-to-end replay; attack-then-defense side-by-side (naive agent vs CITINEL); three-minute walkthrough entry from QR (deck slide 14; STATE §4 beats)
17. Connector/status settings — ingest sources, enrichment quota/cache status, simulated-endpoint roster ("we hit mocks, we say so") *(inferred)*
18. System states — empty/first-run, degraded modes matching the fallback ladder (copilot-shape banner; config-file dial notice), error/offline *(inferred)*

**Out of scope for design now** (declared in the repo): multi-tenant operator console, honeypot views, Indic-language UI beyond one sample narrative, air-gapped variant.

---

## 12. Design System Inputs (found in the repo)

An explicit, locked brand foundation exists in `citinel-brand/README.md`:

**Color tokens**
| Token | Hex | Rule |
|---|---|---|
| Brand navy (ink) | `#0B1F3A` | Flat logos, headings, tagline on light |
| Surface charcoal | `#0E1116` | Dark UI background; app-icon square |
| Pure white | `#FFFFFF` | Logos/text on dark |
| Evidence gold (accent) | `#E7B10A` | **UI only:** citation highlights + the regulatory clock; never in logos; never a status chip |
| Alert red | reserved (no hex committed) | Product severity states only; never brand/decoration |
| Template cyan (external) | ~`#42BFEE` | OSCode deck accent — harmonize with, never adopt |

Rules: single-color logos (navy or white) except the two metallic-blue badges; max one accent per surface; no gradients/glows/shadows on flat assets.

**Typography:** the CITINEL letterforms are baked raster art (never retype the name — place the PNG). Supporting text near logos: **Michroma** or **Orbitron**, all caps, wide letterspacing (~300 Canva units), navy-on-light/white-on-dark. *(The deck also uses a squarish pixel-style display face for slide headers and lowercase pixel kickers — chosen in Canva; no font file or name is recorded in the repo — flagged as an open question.)* No type scale, spacing scale, grid, or component tokens exist for product UI — only the deck's Canva grid (1920×1080, 12-col, col 130 / gutter 24 / margins 48).

**Logo/asset system:** 15 inventoried brand PNGs (16 on disk — `1R.png` is an unlisted stray, §9.10) — CITINEL crystal-falcon badge/wordmark/falcon/app-icon families (light+dark) and the AeroFyta team system (current *faceted* generation vs legacy *swirl* carve-outs — never mixed). A surface map prescribes exactly which asset goes on deck covers, footers, team slides, app splash, dark header, favicon, README hero. Two lockup composites (`logo_lockup_square/wide.png`) exist in `slide-deck-images/` outside the brand inventory (§9.11).

**Taglines (locked, exact punctuation):** official — *"The SOC that shows its evidence, obeys your policy, and beats the clock."* · brand hook — `CAUGHT. CITED. GATED. ACTIONED. CLOSED.` (also the incident state machine; updated 24 Aug 2026 from the three-word `CAUGHT. CITED. CLOSED.` — the submitted deck's 13 occurrences and the two badge-tagline PNGs still carry the old form, see HANDOFF-MEMORY §4a) · category line — `AUTONOMOUS CYBER SOC` (badge-only).

**What does NOT exist yet** (explicit): vector sources; product-UI component library; dark/light theme spec beyond the two surface colors; iconography set; data-viz palette; accessibility targets.

---

## 13. Validated UVPs & USPs

*Sourced from a 106-agent adversarial deep-research pass (21 Aug 2026, Sonnet 5): 5 search angles → 24 sources fetched → 108 claims extracted → 25 adversarially verified (10 confirmed, 15 refuted). Each item below is tagged by evidence tier: **[Verified]** = survived independent 3-vote adversarial re-checking in this pass; **[Existing]** = already established in the repo's own research corpus (A1–A6, cited by finding ID); **[External, hedged]** = verified but resting on thin evidence (single source, single preprint) and must be presented with that caveat attached. Several claims that would have made strong UVP anchors — specific CERT-In penalty figures from new secondary sources, a "seven RBI Directions dated 31 Jul 2026" framing, DPDP's ₹200cr/₹250cr penalties as independently re-verified by this pass, and the C-Edge/RansomEXX "0.5% of transaction volume" detail — did **not** survive this fresh check and are excluded below; this does not overturn the repo's own primary-sourced versions of related facts (already correctly hedged in §5.1 rule 4 and the existing docs corpus), it only means this pass adds no new external corroboration on top of them. Full findings: `/private/tmp/claude-501/.../tasks/wmfnnhgni.output`.*

### A. Trust & explainability (glass-box vs. black-box)
1. **Every verdict cites the exact log line it's based on** — the pipeline treats explainability as a hard requirement, not a dashboard feature. *[Existing — AGT-F07]*
2. **Built on the foundation model shown most resistant to log-based prompt injection in independent 2026 benchmarking.** A single preprint (LogJack, arXiv:2604.15368, Apr 2026) tested 8 LLMs on injected cloud logs: Claude Sonnet 4.6 scored a 0.0% verbatim-hijack rate (vs. up to 86.2% for Llama 3.3 70B) and achieved zero remote-code-execution outcomes across 90 trials, where 6 of the other 7 models achieved at least one. *[External, hedged — single non-peer-reviewed preprint, brittle regex-based classifier, modest sample (30 trials/model/condition); illustrative, not certified]*
3. **Readable, auditable OPA policy-as-code replaces vendor confidence-score black-box gating** — the rulebook a bank's IT head can read and change, not a threshold hidden inside a vendor's model. *[Existing — SAFE-F03/F04]*
4. **Confidence ships with its own counter-evidence**, not as a lone clean percentage — "supports vs. argues against," explicitly framed as confidence, not certainty. *[Existing — UX-F30, deck slide 7]*
5. **The audit log is structurally separate from the AI's own "thinking" output** — a distinction most competitor architectures don't need to draw because they don't expose reasoning at all. *[Existing — AGT-F06/SAFE-F06]*

### B. Regulatory & compliance moat
6. **No named competitor in a 2026 12-platform agentic-SOC comparison mentions CERT-In, DPDP, RBI, or SEBI anywhere** — India regulator-form drafting is white space by omission across the comparison, not a claim resting on CITINEL alone. *[Verified, medium confidence — one comparison article + one refuted competitor claim, not an exhaustive per-vendor audit; open question below]*
7. **The closest known claimant to CITINEL's compliance-drafter feature doesn't hold up under scrutiny** — a specific competitor's public claim to already auto-generate the DPDP breach-notification PDF with a dual CERT-In/DPDP clock failed independent adversarial verification (0-3). *[Verified — reinforces rather than undermines the moat]*
8. **The compliance clock is built ahead of DPDP's own breach-notification duty coming into force**, not reacting to enforcement that's already live. DPDP Rules 2025 were gazetted 13 Nov 2025; Rule 7 (the breach-notification duty itself) is scheduled to activate ~18 months later. *[Verified, high confidence — corroborated against the primary Gazette text; matches STATE's existing "closing runway, never current enforcement" framing]*
9. **Known-threat coverage never depends on an LLM being available, correct, or even called** — Sigma's deterministic layer runs first, a resilience property most "AI-SOC" branding doesn't foreground. *[Existing — PIPE-F07]*

### C. Buyer economics / price-floor wedge
10. **The closest comparable incumbent has pulled all pricing behind a sales-quote wall.** Dropzone AI shows "Contact Us" on every tier (Standard, Enterprise, MSSP) as of 2026 — CITINEL's transparent ₹250–1,000/device/month band is a structural contrast with an industry trend toward opaque enterprise pricing. *[Verified, high confidence — checked directly against Dropzone's live pricing page]*
11. **A competitor's own pricing page benchmarks AI-analyst capacity against a human analyst's cost** — Dropzone's Standard tier caps at 4,000 investigations/year, explicitly labeled "the average output of a human tier-1 analyst." Independent, competitor-sourced validation that AI-SOC economics are meant to be measured against the human cost baseline CITINEL undercuts for the Indian budget band. *[Verified 3-0]*
12. **Even the incumbent's last disclosed price sits an order of magnitude above the Indian buyer band.** Dropzone's historical (2025) ~$36k/yr mark (~₹30L/yr) dwarfs the ₹25k–1L/month (₹3–12L/yr) co-op-bank/small-NBFC budget. *[Verified — must be presented as a historical, not current, comparator; Dropzone's 2026 price is no longer public]*
13. **The B2B2X channel rides a distribution structure a regulator already built.** SEBI's CSCRF directs NSE and BSE to operate Market-SOCs onboarding small/self-certification Regulated Entities — a channel no named AI-SOC competitor is documented as targeting. *[Existing — A1-F42, reinforced by a fresh source fetch in this pass]*

### D. Anti-lock-in / sustainability
14. **Every closed incident exports a portable, standard-format Sigma rule and playbook** — contrasted against TheHive, the closest open-source SOC case-management analogue, whose free Community tier now requires vendor registration and auto-degrades to read-only after a 14-day trial without a paid license. CITINEL's export is portable by design, not license-gated. *[Verified, high confidence — checked directly against StrangeBee's own documentation]*
15. **Wazuh proves genuinely open, no-lock-in SOC infrastructure has real commercial viability** — a fully free, unpaywalled GPLv2 core, no feature gate. CITINEL extends the same philosophy one layer up, into the agentic-investigation and compliance-drafting layer, where no comparable open precedent yet exists. *[Verified 3-0]*
16. **Machine-drafted Sigma rules pass a mandatory human review gate before joining the corpus** — sustaining trust in the flywheel's output as it compounds. *[Existing — PIPE-F08/AGT-F12]*
17. **A working precedent for monetizing community-contributed detection content already exists in the market** — SOC Prime's "Threat Bounty" program has paid independent detection engineers for contributed rules since 2019, validating that CITINEL's own portable-Sigma flywheel sits inside a proven commercial pattern. *[Verified 2-0 — one verifier call errored on a session-limit cutoff, not a refutation]*

### E. Architecture / safety-by-design
18. **The autonomy dial is set per action class, not per deployment** — reversible actions run autonomously while consequential ones stay gated, without reconfiguring the whole system. *[Existing — SAFE-F04]*
19. **Blast-radius rings and staged rollout are designed in from day one**, explicitly modeled on the CrowdStrike July 2024 8.5M-device lesson — not bolted on after a failure. *[Existing — SAFE-F07]*
20. **A poisoned log string that survives investigation still can't launder itself into the human-signed compliance report** — it renders escaped and visibly flagged inside the draft itself, a specific engineering answer to combining citations with compliance drafting that most competitor architectures don't attempt together. *[Existing — cycle-3 anti-laundering fix]*

**Open question this pass could not close:** none of the ten individually-named competitors from the original research brief (Microsoft Security Copilot, CrowdStrike Charlotte AI, Palo Alto XSIAM/Cortex AgentiX, Google SecOps, Prophet Security, Torq, Simbian, Exaforce, Radiant Security, StrikeReady) was individually and specifically audited for CERT-In/DPDP form-auto-drafting — item 6 above rests on one comparison article's silence plus one refuted competitor claim, not an exhaustive sweep. Carried into §15 Open Questions.

---

## 14. Innovation Backlog — Candidate Features (proposals, not committed scope)

*Sourced from a second 105-agent deep-research pass (21 Aug 2026, Sonnet 5) hunting creative, high-impact feature ideas from emerging agentic-SOC patterns, adjacent domains (SRE, fraud, aviation, healthcare safety culture), India-specific differentiators, trust/explainability research, and business-model innovation. This pass hit a session-usage limit during its automated synthesis step after verification completed (15 of 25 checked claims confirmed, 10 refuted); the items below are Claude's manual synthesis of those 15 surviving claims into concrete product proposals, plus a small number of reasoned extensions clearly marked as such. **Nothing here is committed.** Every item is a candidate for Danish's roadmap decision, consistent with the repo's own "Danish owns all timelines" rule (§5.1 rule 5) and the existing declared-out-of-scope list (§2.2). Evidence tiers: **[Verified]** = survived 3-vote adversarial checking against a real external source; **[Repo-adjacent]** = already named as future-work in the existing docs, reinforced or sharpened by this pass; **[Proposed]** = reasoned extension with no independent external verification — flag as lowest-confidence.*

### A. Emerging agentic-SOC patterns
1. **Re-runnable evidence queries.** Alongside each cited verdict, auto-generate a ready-to-run SIEM query (not just a narrative citation) so an analyst can independently re-execute and verify the evidence in their own SIEM before approving. *[Verified 3-0 — inspired by a published multi-agent SOC framework where a "Senior SOC Triage Analyst" agent generates Splunk SPL queries for a separate "Threat Intelligence Analyst" agent to cross-check against MITRE ATT&CK, arXiv:2603.23966]*
2. **A second, explicit statistical pre-filter ahead of the swarm.** Sharpen the existing anomaly scorer into a distinct gate that only forwards high-priority-score events to the agent swarm — a published architecture's explicit rationale for cutting both cost and hallucination risk by restricting what reaches the LLM layer. *[Verified 3-0, arXiv:2603.23966 — sharpens an existing spec element (PIPE-F07's anomaly scorer) rather than adding a new one]*
3. **Make the human/automated control boundary a visible UI element, not just an enforced policy.** Label, on the dial itself, which action classes are analyst-controlled vs. automated — mirroring a major cloud vendor's own description of its hybrid "agentic automation" pattern for keeping humans in control of high-impact actions. *[Verified 3-0, Google Cloud's agentic-SOC documentation — independently validates CITINEL's existing dial as an industry-recognized pattern; the proposal is exposing the boundary visually]*

### B. Adjacent-domain transplants (SRE / aviation / healthcare)
4. **A Near-Miss Ledger**, separate from full incident review: a lightweight log of blocked or auto-remediated attempts that never escalated to a full incident (Sigma-matched and closed with no human involvement) — inspired by aviation safety's "near-miss" reporting, argued to be easier to analyze than full incidents because at least one control succeeded. *[Verified 3-0, Belfer Center / Harvard Kennedy School research on adapting aviation safety models to cybersecurity]*
5. **An auto-drafted blameless postmortem**, distinct from the CERT-In/DPDP regulator drafts — structured like an SRE postmortem (incident, impact, mitigation, root cause, follow-ups), written for internal engineering/ops learning rather than regulatory filing, and explicitly assuming good intent from everyone involved. *[Verified 3-0, Google SRE Book's postmortem-culture chapter — a direct extension of the existing Scribe agent's drafting capability]*
6. **Structured agree/disagree/modify logging on every verdict**, not just Approve/Deny on actions — so the eval harness can measure human-AI collaboration uplift the way published research does: one study found phishing-detection precision and intrusion-detection recall each improved measurably under structured human-AI collaboration versus either working alone. *[Verified 2-1, arXiv:2505.03179 — extends the existing eval-harness/correction-memory design]*

### C. India-specific creative differentiators
7. **Ingest DoT's Financial Fraud Risk Indicator (FRI) as an enrichment source.** RBI's own 30 June 2025 advisory already directs all cooperative banks — CITINEL's core segment — to integrate FRI, a risk-scored mobile-number classification built from I4C's NCRP portal, DoT's Chakshu platform, and bank-shared intelligence. A regulator-endorsed, India-specific enrichment feed with no adoption friction to argue for. *[Verified 3-0/2-1, PIB press release — strongest-fit proposal in this list]*
8. **Deepen Indic-language incident narratives beyond the single sample already on the roadmap.** *[Repo-adjacent — already named as roadmap in STATE §1.7/deck slide 4; this proposes extending it]*
9. **WhatsApp/SMS-native alert delivery** for rural cooperative-bank IT staff — surface the approval-card summary over a channel branch-level staff already use daily. *[Proposed — plausible given this pass's rural-connectivity research angle, but not independently sourced]*
10. **A WhatsApp-shareable export of the shift-handover card**, extending the existing handover card (UX-F32/F33) with a one-tap export to the same channel. *[Proposed — extends an existing spec element, not independently sourced]*
11. **Offline/low-bandwidth branch sync** — a store-and-forward ingest mode for syslog/webhook sources at branches with unreliable connectivity, queuing events locally and reconciling once connectivity returns. *[Proposed — consistent with the existing "nothing at the branch changes" ingest philosophy, not independently sourced]*

### D. Trust, explainability & safety innovation
12. **A counterfactual "what would change this verdict" panel**, alongside the existing confidence-not-certainty bar — showing which specific piece of evidence, if different, would flip the verdict or its confidence score. Two concrete implementations exist in the literature: an example-based table (alternative instances and how they'd shift the score) and a visualization-based ICE-style plot (confidence as a function of one varied feature). Peer-reviewed research (AAAI) found this measurably improved both understanding and trust, replicated across two independent studies. *[Verified 3-0, AAAI-23 — directly implementable extension of the existing counter-evidence panel]*
13. **Pre-approval blast-radius simulation.** Show the *predicted* change in blast radius for each proposed action before the analyst approves it, and update the incident's "threat story" in real time as the simulated action would compress it — moving from static blast-radius rings to predictive simulation. *[Verified, single source (Cloud Security Alliance), moderate confidence]*

### E. Business-model & flywheel innovation
14. **An MSSP/analyst detection-bounty program** — pay or credit partner-MSSP analysts and cooperative-bank IT staff for Sigma rules that pass the human-review gate and get broadly adopted, following a proven commercial pattern (SOC Prime's "Threat Bounty," running since 2019). *[Verified 2-0 — one verification call errored on the session-limit cutoff, not a refutation; directly extends the existing Sigma-export flywheel]*
15. **A contributor leaderboard/reputation system** tied to the bounty program above — surface which MSSP partners or analysts contributed the most-adopted rules, turning the review-gated corpus into a visible reputation signal across the channel. *[Proposed — extends item 14, not independently sourced]*
16. **LLM-judge pre-scoring on draft Sigma rules** before they reach the human review queue — rank likely false-positive rate using the existing eval-harness methodology, so reviewers see a ranked queue rather than a flat one. *[Proposed — extends the existing eval harness (AGT-F12) and review gate (PIPE-F08)]*

### Already-specified roadmap items this research independently reinforces *(not new — listed for completeness)*
17. Deception/honeypot integration — already future-work (ARCH-F03), explicitly out of scope for MVP.
18. Multi-tenant Market-SOC deployment — already future-work (ARCH-F05), explicitly out of scope for MVP.
19. Pluggable local-model adapter for air-gapped government/CII deployments — already roadmap (A2 §5(j)).
20. Domain-agnostic engine reuse (AIOps, fraud-detection skins) — already the long-run business story (A2 §5(f)), staged after the SOC skin is deep.
21. Regulator-connector expansion (RBI/SEBI/IRDAI/CEA/NCIIPC packs re-skinning the same normalized incident record) — already the Stage-3 scale story (COMP-F30 §6).

**What was explicitly excluded:** claims that failed adversarial verification in this pass are not listed as proposals, including a claim that "even 2026 agentic-SOC architectures haven't reconciled human-in-the-loop governance with machine-speed response" (refuted 0-3) and Google's specific "Detection Engineering agent autonomously builds and validates new rules" / "Threat Hunting agent" claims (each split-refuted). Full findings: `/private/tmp/claude-501/.../tasks/wf3m3gyvx.output`.

### F. From a dedicated innovation/creativity research pass (21 Aug 2026)

*A 104-agent deep-research pass (25 claims verified: 15 confirmed, 2 refuted, 8 never independently re-checked due to a mid-run DNS/network outage that failed 49 of 104 agent calls) hunting explicitly for features not already covered by §13, §14's items 1–21, or §17's UVPs. Resumed once from cache after the outage; all previously-completed calls hit cache instantly, and the retry finished cleanly with a full automated synthesis. Coverage across its five requested angles was sharply uneven — flagged per-item below.*

22. **A generate-then-validate investigation stage ahead of the swarm's verdict.** A published agentic-SOC framework (AgentSOC) explicitly separates *hypothesis generation* (a component proposing candidate attack narratives) from *structural-feasibility validation* (a graph-traversal check against privilege/path/ATT&CK preconditions) before any response executes — a distinct pattern from flat alert-to-verdict scoring. A related graph-foundation-model technique (CyberGFM) applies BERT-style masked-token prediction over network-graph random walks for lateral-movement detection, reporting up to 2× average-precision improvement over prior graph-embedding baselines. *[Verified 3-0/2-1/2-1, arXiv:2601.05988 + arXiv:2604.20134]* **Coupling: medium** — requires standing up a network/identity graph store and a hypothesis-generation-plus-validation stage feeding evidence into the existing swarm, not a replacement for it; new infrastructure the current OCSF-ingest pipeline doesn't imply.
23. **Typed-tool evidence grounding, plus a "propose follow-up investigation questions" output field.** A published multi-agent SOC architecture (CORTEX) — an orchestrator, a behavior-analysis agent, workflow-specific evidence-acquisition agents each grounding claims via typed tool calls (`getUserRecord`, `searchBehaviorEvents`, `runStructuredQuery`), and a reasoning/coordination agent — measurably outperformed the best single-agent baseline: actionable-alert F1 rose from 0.66 to 0.78 and the false-positive rate fell from 24.9% to 14.2%. Its final-report step also extracts observables and proposes follow-up questions, worth adding as a distinct output field alongside CITINEL's cited verdicts. *[Verified 2-1/3-0, arXiv:2510.00311]* **Coupling: low** — an output-schema extension and tool-call audit layer, no change to the OPA gate or autonomy dial. **Honest tradeoff, same source:** the multi-agent design carries a real latency/cost cost — a median 152.4s per-alert resolution time (3.4× slower than a tool-using single-agent baseline) and 5.7× more tokens per ticket — worth weighing against CITINEL's own cost-conscious "rules first, AI second" design before adding more agent-to-agent steps. *[Verified 3-0, same source]*
24. **A CITINEL-authored MITRE ATT&CK extension taxonomy for AI-agentic attack behavior.** Anthropic's own disclosure of a disrupted, state-sponsored campaign using autonomous multi-step AI orchestration states plainly: "there is no ATT&CK ID for this type of agentic orchestration — yet these are precisely the behaviors we expect to see much more of." A genuine, citable taxonomy gap CITINEL could design a small set of custom technique tags against, layered on top of existing ATT&CK mapping in the swarm's citations. *[Verified 2-1, Anthropic's own Nov 2025 disclosure]* **Coupling: low** — additive schema/tagging work only.
25. **Per-analyst-tier autonomy, not just one org-wide dial position.** A published SOC-copilot framework (CyberAlly) differentiates AI oversight mode by analyst seniority — Tier-1 analysts get human-in-the-loop or human-on-the-loop AI assistance, while Tier-3 senior analysts get human-out-of-the-loop AI delegation for threat hunting — rather than one dial setting for the whole org. The same paper's "AI avatar" pattern (a persistent, personified assistant combining RAG-over-knowledge-graph enrichment with collaborative ticketing that still requires human validation) is a separate, purely additive front-end UX layer worth considering alongside it. *[Verified 2-1/2-1, arXiv:2505.23397]* **Coupling: low-to-medium** — reuses the existing Shadow/Assist/Autonomous OPA-gated dial mechanism, just settable per analyst role/tier rather than replacing it; the avatar UX is additive front-end work.
26. **A confirmation-bias check on the human-sign-off step.** Human-AI reliance splits into two distinct decision types — "delegation" (letting AI act without seeing its output first) and "adoption" (reviewing a suggestion before deciding how to use it) — and confirmation bias is a large, quantified risk: when an AI verdict agrees with an analyst's own incorrect initial hypothesis, under-reliance on the correct alternative jumps to 64.5%, versus a ~3.9% baseline missed-opportunity rate. *[Verified 3-0/3-0, arXiv:2605.28255 — competitive-QA domain, not SOC-specific, but the reliance-decision framework transfers directly]* **Coupling: low** — two additive UX/telemetry features on top of the existing mandatory sign-off step: separately track delegation-mode vs. adoption-mode interactions, and surface a disagreeing-evidence nudge when an analyst's own hypothesis matches the AI verdict exactly.
27. **Package each verdict's evidence as a persistent, auditable "rationale artifact"** with a defined set of analyst-triggerable operational actions (calibrate a scorer threshold, refine a triage rule) that write back into the audit log — an "Explainability-as-Intervention" pattern from peer-reviewed cybersecurity-training-lab research, directly extending CITINEL's existing citation-based explainability from a read-only trail into an operational feedback loop. *[Verified 3-0/3-0, Frontiers in Computer Science, Aug 2026 — general IDS/XAI research, not banking-specific]* **Coupling: low** — additive schema and UI work on the existing append-only audit log and cited-verdict output. The same rationale-artifact structure is flagged as a natural building block for a future training/practice mode (see the gamification gap below).
28. **An opt-in, regulator- or vendor-brokered threat-sharing precedent worth studying before designing CITINEL's own version.** FINRA launched an opt-in Financial Intelligence Fusion Center in March 2026 — a centralized portal letting member broker-dealers voluntarily exchange cyber/fraud threat intelligence, collected and disseminated by FINRA itself. A concrete precedent for a CITINEL-operated, opt-in (never mandatory) anonymized threat-sharing portal across subscribing cooperative banks — a genuine network-effect feature, distinct from anything in the original 21-item backlog. *[Verified 3-0, FINRA's own press release + independent trade-press corroboration]* **Coupling: medium** — a new shared data-exchange service with consent/anonymization controls, architecturally separate from the core swarm/OPA pipeline, but real new infrastructure that doesn't exist today.
29. **Behavioral/device-identity graphs, transplanted from fraud detection, for insider-threat and account-takeover detection.** Fraud-detection systems build graphs from logins, device IDs, OS/device types, and query patterns, connecting accounts whose behavioral or device similarity exceeds a threshold to uncover coordinated fraud rings — a pattern already established as real, deployed SOC/UEBA practice (Microsoft Sentinel UEBA, Palo Alto Networks, Exabeam, Group-IB) and independently corroborated in 2026 peer-reviewed insider-threat GNN research, making it a low-risk transfer rather than a speculative one. *[Verified 2-1, arXiv:2411.05815 — the SOC/insider-threat application is this research pass's own reasonable synthesis, not the paper's own claim]* **Coupling: medium** — a new behavioral/device-identity graph structure alongside OCSF-normalized ingest, feeding candidate findings into the existing swarm rather than changing it.

**Two angles this pass could not cover — flagged, not silently dropped:** community/network-effect features (angle 3) came back the weakest of the five — five separate claims about federated learning and a Sigma-rule marketplace precedent were all refuted (0-3 or 1-2), leaving only the FINRA precedent above. **Gamification and analyst skill-building features (angle 4) produced zero confirmed claims at all** — attack-simulation, tabletop-exercise generation, and analyst training-loop ideas remain genuinely unresearched; the closest adjacent material is item 27's rationale-artifact structure, which was extracted as an explainability finding, not a training-mode finding. Both gaps are carried to §22 Open Questions rather than papered over.

---

## 15. Partner Prize Eligibility — Bulletproof Plan

*Sourced from a live fetch of `oscode.co.in/events/decode-sih-2026` on 21 Aug 2026 — the current, authoritative eligibility rules, not the internal docs' Aug-2 snapshot. **[External, primary]** throughout unless noted. Total event prize pool: ₹50,00,000 across 3 flagship tracks; CITINEL competes in **Bharat Pragati** (AI for Cybersecurity, FinTech & Digital Governance). Every "Best Use of X" partner award is judged **at the Grand Finale (5 Sep), on the built/deployed product — not the Round-1 idea deck.** Multi-prize stacking is not addressed by the rules (not prohibited, not explicitly guaranteed) — standard hackathon practice allows it, but this is not certified by the source.*

### 15.1 Seven named partners, exact criteria

| # | Partner | Prize | Exact criteria (quoted) |
|---|---|---|---|
| 1 | **Swytchcode** | $1,000 credits/yr (winning team) · $100 credits (every participant) | "Build their solution using the Swytchcode CLI" · "Use the Python or TypeScript runtime" · "Integrate at least two external APIs from the Swytchcode ecosystem" · "Include an AI-powered workflow or AI agent" · "Demonstrate a functional end-to-end application" |
| 2 | **Render** | US$600/500/400 (1st/2nd/3rd, per venue) · US$50 (every shortlisted team) | "Deploy their project on Render" · "Use more than one Render service" |
| 3 | **n8n** | 1-yr Cloud Pro per winning-team member (~$600/member) · 1-mo Pro (every shortlisted team) | "Integrate n8n into their hackathon project" · "Demonstrate how workflow automation improves the project's functionality, efficiency, or user experience" |
| 4 | **Tavily** | 10,000/5,000/3,000 API credits (1st/2nd/3rd) · 8,000 credits (every shortlisted team) | "Integrate Tavily APIs into their project" · "Use real-time web search, AI retrieval, or knowledge augmentation" · "Demonstrate a creative and impactful implementation" |
| 5 | **Startuped.ai** | Up to ₹25,000 cash + 2 mo Pro + 2,000 credits + founder strategy session + podcast/website feature (**one overall winner across the entire event, not per-venue**) | "Demonstrate how Startuped.ai was used for: Idea validation, Market research, GTM planning, Product positioning, Launch strategy" |
| 6 | **Lyzr AI** | ₹10,000 Bengaluru + ₹10,000 Delhi (₹20,000 total) · $20/mo credits (every participant) | "Teams that build innovative solutions using the Lyzr AI platform" |
| 7 | **Codemate.ai** | 15 days Pro (every shortlisted/finalist member) · 3 months Pro + PPI (only for members of the team that **wins one of the 3 flagship tracks**) | No independent technical bar — contingent on the main track win |

*(Google for Developers and MLH are listed as general event partners with no specific prize criteria — not a track to target.)*

### 15.2 Gap analysis and closure

| Partner | Prior status | Now |
|---|---|---|
| Swytchcode | Already spec-complete — STATE §1.10 pre-mapped this exact rubric (CLI · Python/TS · ≥2 APIs · AI agent · end-to-end app) | **Closed by spec.** Build as specified: scaffold with the CLI, not just call the API at runtime. |
| Render | Already spec-complete — deck slide 8's stack (web service + background worker + managed Postgres/Redis) exceeds the ">1 service" bar | **Closed by spec.** Pure execution risk — get the deployment live. |
| n8n | Wired conceptually (STATE §1.10: "escalation, notification, and report-export workflows as visible n8n flows"), but no demo beat *showed* it | **Closed** — new demo micro-beat added, §15.3. |
| Tavily | Enrichment Squad already does real-time search/RAG (STATE §1.5) | **Closed** — citation-chip provenance sharpened, §15.3. |
| Startuped.ai | GTM research exists and is rigorous (A1–A6), but was produced via Claude research, not run *through* the Startuped.ai tool itself — the criterion requires demonstrated platform use | **Closed by process** — execution checklist, §15.3 (requires the team's own account; cannot be completed by this document alone). |
| Lyzr AI | **Absent entirely** — not in STATE, the deck, or any prior SDD section | **Closed by new integration**, §15.3 — promoted from "not present" to committed architecture. |
| Codemate.ai | Already used build-time (STATE §1.10) | **Closed** — no separate bar; reward flows from winning Bharat Pragati. |

### 15.3 Closure designs

**n8n — explicit demo beat.** Insert as **Beat 5b**, immediately after the human signs the CERT-In draft in STATE §4's existing Beat 5. The n8n canvas (screen-share or recording) is shown live: five nodes fire visibly in sequence — `Webhook: Incident Signed` → `Format Notification` → `Send Slack/email to CISO` → `Export Signed PDF to Compliance Drive` → `Create Follow-up Ticket`. The judged word is *demonstrate* — this makes the automation seen, not inferred. Division of labor stays exactly as STATE already frames it: n8n owns the *visible* escalation/export workflow; Swytchcode owns the *invisible* agent→API execution glue (Response Marshal/Scribe's ticketing+comms calls) — no overlap.

**Tavily — provenance in the citation chip.** Where the Enrichment Squad's OSINT lookups feed a cited narrative, the citation chip in the glass-box replay (screen 5, §11) renders the source explicitly: `source: Tavily search — [URL], fetched [timestamp]`, not just the underlying log line. Turns an invisible backend call into a visible, judge-legible "creative and impactful implementation."

**Startuped.ai — execution checklist (human steps outside this document's scope):**
1. Team lead creates a Startuped.ai account (1 month free + 1,000 credits already granted to every participant).
2. Run CITINEL's *already-locked* positioning through their five modules — primary persona (A1-F45), differentiation line (STATE §1.4), channel strategy (A1-F47/F42), competitive landscape (A2) — rather than inventing new GTM thinking.
3. Export/screenshot each module's output; these exports are the literal proof-of-use artifact the criterion requires.
4. Where the tool's own output sharpens deck slide 13, swap it in — makes "Slide 13 is built from it" (deck slide 8) literally true.
5. Keep the dashboard ready to show live at the Grand Finale.

**Lyzr AI — governance/observability layer over the existing swarm, not a replacement of it.** Lyzr is provider-agnostic (works with Claude, doesn't compete with it) and sits *above* agent frameworks as a control plane. Four concrete attachment points, each fulfilling an *already-locked* requirement rather than inventing a new one:
- **Fleet observability** — instrument all 7 agents (Sentinel → Scribe) with the Lyzr SDK so their dashboard shows live per-agent status; becomes a new glass-box screen (extends §11 item 3, the SOC overview dashboard, from *inferred* to *built-with-Lyzr*).
- **Hallucination & PII Guard** — a second, independent check on the Verdict Narrator's output, on top of (not instead of) citation-grounding (AGT-F07); specifically screens the CERT-In/DPDP drafts for inadvertent PII before human sign-off.
- **RBAC** — formalizes the already-specified Analyst-view/CISO-view split (deck slide 7) into an enforced permission system instead of a UI-only skin.
- **Immutable audit log** — can fulfill (not duplicate) the already-locked SAFE-F06 append-only audit requirement.

This is one genuine tech-stack addition, requiring an update to STATE §1.10 and deck slide 8's partner list when Danish signs off on the build. §7's Integrations table below reflects it as committed.

### 15.4 What this plan does not and cannot claim

- **Not a win guarantee.** Every criterion above is now closable by design; none of it exists as working code yet (§1, §2.1 — the repo has zero application code). Eligibility is necessary, not sufficient.
- **Team-eligibility rule, no exceptions, per the organizer page:** 3–6 members, same institute, currently enrolled, at least one female member. The current roster (Danish, Preethi, Sanjay, Ismail Ridwan, Hritik, Elangovan) satisfies this on its face — confirm Preethi's current enrollment status, since this is a hard disqualifier if wrong.
- **Date discrepancy, unresolved:** the live page states idea-submission deadline **13 Aug 2026** and **Top 80** teams advancing to the Grand Finale; the internal docs and webinar deck state **11 Aug** and **Top 60**. Not reconciled here — carried to §16 Open Questions.

---

## 16. Architecture Hardening Recommendations

*Sourced from a 112-agent deep-research pass, resumed to completion on 21 Aug 2026 (25 claims verified: 14 confirmed, 11 refuted, 0 unverified) with a full automated synthesis — this supersedes the section's original hand-synthesized text. **Correction from the original version:** the original hand-synthesis (recovered before this resume) listed two recommendations — short-lived scoped credentials per agent tool call, and a 3-tier OAuth On-Behalf-Of identity chain, both sourced to "HashiCorp Vault's AI-agent identity pattern" — as "Verified 3-0." On full re-verification this run, the Vault dynamic-secrets/short-lived-credentials claim was explicitly **refuted**. Both recommendations are retracted below; do not carry them forward.*

**Agentic reliability — failure isolation for the 7-agent swarm:**
1. **Decouple error detection from the critical execution path** — async self-monitoring, not an inline check that blocks each agent's turn — paired with **contextual rollback over naive retries**: when an agent fails or hallucinates, recover state from execution history rather than blindly re-running it. Extends the existing rollback-token concept (currently scoped only to response *actions*, per SAFE-F04) to agent-level failure recovery too. *[Confidence: medium — COCO, arXiv:2508.13815, Aug 2025]*
2. **Hallucinations propagate across agent-to-agent handoffs, not just within one agent's reasoning** — a named taxonomy category, "Communication Hallucinations," covers erroneous message propagation, uncoordinated protocols, and ineffective updates specifically in multi-agent systems. Citation-grounding should be enforced at every inter-agent handoff (Sentinel→Router→Enrichment→Correlator→Narrator→Marshal→Scribe), not just the final Narrator output — sharpening AGT-F07, which as currently specified only requires citations on the final verdict. *[Confidence: medium — arXiv:2509.18970]*

**Supply-chain security — the Sigma rule corpus:**
3. SigmaHQ's own quality bar for the 3,000+ community rules CITINEL bundles requires **at least 2 human reviewers who validate logic and replicate the referenced attack before merge**, plus three tiers of automated schema/convention validation (JSON-schema check, PySigma core validators, a custom SigmaHQ convention layer). CITINEL should audit its bundled corpus against this exact bar — pin to a specific vetted release/commit, re-run the same PySigma validator chain locally at ingestion rather than trusting upstream merge state blindly. *[Confidence: high — SigmaHQ's own Nov 2025 QA-pipeline blog post]*

**Data architecture & compliance:**
4. **A mandatory case-ID header propagated through every agent/tool call**, logged as the join key across orchestrator, tool-call, and decision logs — a documented pattern (retrofitted after a regulated-finance deployment discovered its MCP tool interfaces "were not designed for audit") that makes full audit-chain reconstruction possible from the case ID alone. Directly reusable for CITINEL's append-only audit log and CERT-In/DPDP artifact drafting. *[Confidence: medium — arXiv:2606.29142, a single n=1 practitioner case study — see caveats]*
5. **A redaction-proxy architecture** — raw source content never reaches the model, only extracted/tokenized fields cross the inference boundary — narrows but does **not eliminate** the prompt-injection attack surface: a crafted value inside an extracted field can still reach the model. Frame CITINEL's quarantine plane + injection detector as a residual-risk reducer, not a closed control. *[Confidence: medium — same source]*
6. **A policy/sign-off synchronization gap is a real, documented failure class**, not a hypothetical: in one deployment, a compliance-approved policy update wasn't yet gated into production ingestion, so the agent kept applying a stale policy — and the drift was caught only by internal audit, not by the agent system's own monitoring. No current agent framework natively synchronizes policy versions with a compliance document lifecycle. Directly relevant to CITINEL's OPA policy layer and Sigma corpus updates. *[Confidence: medium — same source]*
7. **OCSF requires every event producer to declare `metadata.version`**, so downstream consumers can determine which attributes/definitions are available. CITINEL's log-normalization layer should branch parsing/enrichment logic on the producer-declared version per event, not assume one pinned schema version across all bank source systems. *[Confidence: high — cross-checked against OCSF's own primary GitHub schema]*
8. **For MSSP-style multi-tenant Postgres growth, shard on `tenant_id`** (not each table's own primary key) — colocating a tenant's data on one shard sharply reduces the cost of distributed transactions, joins, and foreign-key enforcement, which dominate SOC query patterns ("show me this bank's incidents"). Apply from schema design onward, including the audit log and incident tables. *[Confidence: medium — Citus/Microsoft's SaaS design guide]*

**Evaluation, observability, and the honesty of the autonomy default:**
9. **Production autonomous-SOC adoption remains narrow (Gartner 2025 Hype Cycle: 1–5% of organizations)**; real deployments confine agents to low-risk tasks (alert enrichment, summarization) with humans retaining decision authority — "pilot purgatory" — and autonomous investigation plus high-risk response actions (account disablement, host isolation) remain unreliable at scale and at telling malicious from legitimate-but-unusual activity. This directly validates CITINEL's Shadow/Assist/Autonomous OPA dial as the correct conservative *default*, not a hackathon compromise to relax post-launch. *[Confidence: medium — Gartner 2025 Hype Cycle + March 2026 trade-press practitioner synthesis]*

**What was checked and did NOT survive — do not use:** short-lived scoped credentials / Vault dynamic secrets for agent tool calls and the 3-tier OAuth On-Behalf-Of identity chain (both refuted this run — see correction note above); the EU AI Act Article 26 framing as a legal precondition for agent least-privilege; OCSF's specific semantic-versioning scheme (the 1.8.0-dev claim); Citus's tenant-count-based database-per-tenant-vs-sharding threshold; the "MAST failure taxonomy: 41.77%/36.94%/21.30%" statistic; a specific "71% accuracy on 348 false positives" LLM-SOC benchmark; hash-chained tamper-evident audit logs and "90% storage reduction via Merkle-root anchoring"; database-per-tenant vs. sharded-schema as "the" multi-tenancy tradeoff (see §20 instead); COCO's "Bidirectional Reflection Protocol" and "Heterogeneous Cross-Validation" specifics.

**Evidentiary caveat:** findings 4–6 above all trace to a single non-peer-reviewed 2026 arXiv preprint describing one anonymized practitioner's deployment in KYC/credit decisioning, not cyber-SOC — read as illustrative failure classes to design against, not as benchmarked or independently replicated findings. Findings 7 and 3 are the most independently verifiable (checked directly against OCSF's and SigmaHQ's own primary sources). Finding 9 rests on trade journalism citing a paywalled Gartner report — directionally trustworthy, not a precise checkable statistic.

---

## 17. Additional UVPs & USPs — Unconventional & Cutting-Edge

*Sourced from a 106-agent deep-research pass, resumed to completion on 21 Aug 2026 (25 claims verified: 17 confirmed, 8 refuted, 0 unverified) with a full automated synthesis — this supersedes the section's original hand-synthesized text. The synthesis clustered the 17 confirmed claims into 6 findings (below, A–F); items G–K carry forward five additional, narrower confirmed claims from the same 25-claim verification pass that the auto-clusterer didn't surface as separate top-level findings but which remain valid (not contradicted by anything refuted this run). Same-session note: this pass again hunted specifically for angles beyond the 20-item UVP pass (§13).*

**A. Trust-dial nuance — from autonomous-vehicle and human-machine-teaming research**
1. AV research validates a **user-adjustable trust/autonomy dial** as a legitimate design pattern echoing Shadow/Assist/Autonomous — but the same study warns that raising the dial measurably **increases** risk (+19% collision-risk metric, +22% risk-duration exposure moving from lowest to highest trust setting) and that rising user confidence over time erodes the safety margin a conservative default provides. The actionable takeaway isn't "add more dial levels" — it's that **the dial itself needs anti-complacency safeguards** (default decay, periodic re-justification of higher autonomy), so autonomy going up never quietly means safeguards going down. *[Confidence: medium — Aston University 2025 "Variable Trust Control Setting" simulation study, PMC11906505]*
2. **Calibrated self-assessment, not raw confidence display, is what drives trust — and it's a rare double win.** Disclosing an AI's own calibrated confidence (vs. a raw softmax score), at identical underlying accuracy, produced trust gains of 34–52% while cutting *both* under-reliance (unnecessary human takeovers, 9.37→4.1) and over-reliance (unchecked machine errors, 4.75→2.37) simultaneously. Implementable as an additive field on the existing verdict output schema — CITINEL's confidence panel needs to be measured for calibration by the eval harness (AGT-F12), not just displayed. *[Confidence: high — HRL Laboratories 2025, Frontiers in Robotics and AI]*

**B. India-context moat**
3. **The PACS computerization program is a live, large-scale, government-funded national digital rail for exactly CITINEL's target segment:** 63,000 Primary Agricultural Credit Societies, ₹2,516 crore, a five-year Centrally Sponsored Project (2022–23 to 2026–27) approved 29 June 2022, delivered as a single common NABARD-built ERP customizable per state (not fragmented per-cooperative systems), with **50,455 PACS already onboarded as of 27 January 2025.** A go-to-market/distribution angle (a pre-existing national integration surface via NABARD/StCB/DCCB channels), not a core-architecture claim. *[Confidence: high — cooperation.gov.in (primary) + corroborating Lok Sabha/PIB replies]* *(A related claim asserting a rigid, formal three-tier PACS→DCCB/StCB→NABARD hierarchy was refuted — don't assert that structural detail. Also refuted this run: NUCFDC's "Bank in a Box" and a claimed existing shared SOC for Urban Cooperative Banks — whether a pooled cooperative-bank SOC already exists in India remains genuinely open, not confirmed either way.)*

**C. Multi-agent consensus — CITINEL's strongest new defensible technical UVP candidate**
4. **Naive majority voting among LLM agents is empirically unstable and vulnerable to "confabulation consensus"** (agents sharing biases and converging on the same wrong answer, making raw vote frequency an unreliable correctness signal). The optimal aggregation mechanism is task-dependent (voting beats alternatives by 13.2% on reasoning tasks, consensus by 2.8% on knowledge tasks); more agents help but more discussion rounds before voting hurts; and auditing full reasoning trees (verifying locally at points where reasoning diverges, not tallying global votes) beats plain majority voting by up to ~5–5.7 points absolute accuracy across five multi-agent architectures. *[Confidence: high — three independent Sep 2025–Feb 2026 arXiv papers converging on the same problem]* **Coupling/cohesion warning:** this is HIGH RISK if implemented by modifying the swarm's internal agent-to-agent debate logic directly — it touches core reasoning and likely forces a redesign. Treat as a candidate for a bolt-on verdict-audit module (see F below), not a change to Correlator/Narrator's internals. *(AgentAuditor's specific recovery percentages, 65.35%/81.82%, and a claimed "first consensus model for stochastic multi-agent LLMs" with formal stability guarantees were both refuted — the general finding survives, those specific numbers/claims do not.)*
5. **Confirms an existing design choice is right:** self-improving agentic systems can achieve durable improvement via "scaffolding" changes (prompts, memory, tools, control logic) without retraining the foundation model — faster and more reversible than parameter updates. CITINEL's correction-memory flywheel (few-shot, explicitly not fine-tuning — STATE §1.5) is exactly this safer scaffolding approach, and it's the model for how any verdict-consensus upgrade from finding 4 should be added too. *[Confidence: medium — single 2026 survey, Schmidhuber co-authored]*

**D. Architecture-quality vocabulary**
6. **The Anti-Corruption Layer (ACL) pattern** — an AWS-documented, DDD-derived mediation layer that isolates a core system's semantics from an external or differently-modeled system, decoupling callers from callees — is the standard, authoritative name for how a new differentiator module (a verdict-consensus upgrade, Lyzr's governance layer, future connectors) should interface with CITINEL's locked Claude swarm/OPA core without either side needing to change. This is the direct architectural answer to this pass's own coupling/cohesion requirement. *[Confidence: high — AWS Prescriptive Guidance, stated in four places on its own pattern page]* *(A related "Social Trust Calibration Framework" claim, and a claimed 2026 patent filing for this exact multi-agent verdict scenario, were refuted — treat this as the general, well-established pattern name, not a fully validated implementation recipe or evidence of prior art specific to CITINEL.)*

**E–F. Carried forward from the original 16-confirmed set (same 25-claim pass, not re-surfaced as separate top-level clusters this round, not contradicted by any refutation above):**
7. A caution against relying on agent self-verification: self-generated feedback for self-correction carries documented risks (self-deception, reward tampering), and self-consistency checks can fail specifically when a model is confidently wrong — a point *in favor* of CITINEL's existing design, since the OPA gate and mandatory human sign-off are external, deterministic checks, not agent self-checks.
8. A specific fast, low-latency consensus protocol (Aegean) achieves 1.2–20× lower latency and up to 11× lower P99 tail latency than baseline multi-agent consensus, within 2.5% accuracy — a concrete reference point if latency ever becomes a constraint on any future multi-agent verdict aggregation (finding 4).
9. Roughly two-thirds of attacks against LLM agents are inherited or amplified from the base LLM itself — base-model safety alignment doesn't reliably transfer once an LLM gets tools, memory, and autonomy. Direct support for why CITINEL's injection-hardening (quarantine plane, detector, egress allow-list — SAFE-F02) has to be a separate defense layer, not something assumed from Claude's own alignment.
10. No single defense strategy is robust across all axes (scalability, adversarial robustness, overhead, coverage) — the field is converging on hybrid, multi-layer defenses. Validates CITINEL's existing multi-layer shape (quarantine + detector + egress allow-list + human gate) as structurally correct, not a placeholder for a future single fix.
11. A specific claimed "67,930-PACS-sanctioned / ₹741.34 crore-released" pair of figures was checked and **refuted** this run — do not use those exact numbers even though the broader PACS onboarding trajectory (finding 3) is separately confirmed via other sources.

**Honest count:** this pass produced 6 clustered top-level findings plus 4 carried-forward supporting claims (10 distinct pieces of evidence total) — short of the "25+" originally asked for. Padding to a round number with restated or unverified claims would violate this document's own evidence discipline, so the honest count is reported instead.

---

## 18. Demo Wow-Moment Design

*Sourced from a 95-agent deep-research pass, resumed to completion on 21 Aug 2026 (25 claims verified: 14 confirmed, 11 refuted, 0 unverified) with a full automated synthesis — this supersedes the section's original hand-synthesized text. Deliberately about presentation craft and judge psychology, not messaging (already covered in §13).*

1. **Novelty must be moderate, not maximized.** Judges/audiences implicitly favor innovative (or historic) options over safe, status-quo ones — but only up to a point; excessive novelty is aversive because it violates expectations. CITINEL's injection-attack-defense set piece should be framed as a recognizable SOC/incident-response ritual (something judges already understand) into which one genuinely novel element is introduced — surprising-but-legible, not a maximalist spectacle. *[Confidence: high — N=272 mouse-tracking study, iScience 2025, PMC12124592]*
2. **The peak-end rule governs how the whole demo will be remembered — and it's well-established specifically for short, bounded experiences like a 3–10 minute pitch.** Engineer exactly one unmistakable peak (the live prompt-injection attack-then-defense moment) and don't let anything after it dilute it; instead compose a short, confident, visually clean closing beat, since judges weight both the peak *and* the ending, not the middle. *[Confidence: high — Redelmeier/Kahneman colonoscopy studies + Fredrickson-Kahneman "snapshot model"; a 2022 meta-analysis of 174 effect sizes found the effect large (r=.581) and duration effects near nil]*
3. **Retrospective judgment reliably over-weights recent information for most people (a smaller group over-weights the earliest information instead), replicated across behavior and neural measures** — reinforcing that the opening line and the closing beat both matter more than the middle. *[Confidence: medium — Yoo, Bahg, Turner & Krajbich 2025]* **Important correction from the original synthesis:** the original hand-synthesis reported this as a weak, unsettled 1-1 vote; on full re-verification it's a confirmed 3-0 finding for the general "both ends get disproportionate weight" claim. However, a related, more specific claim — that recency is unconditionally weighted *more* than primacy — was explicitly **refuted**. Don't overclaim a simple "recency beats primacy" rule.
4. **Live, visible decision-making projected on screen works, with more specificity than previously recorded:** DEF CON 34 contest formats use three concrete showmanship mechanics — a physical/visual "damage state" model marking breached components in real time (Adversary Wars CTF's plastic-brick city), on-screen bracket-structured real-time projection of incident-response decisions (Backdoor & Breaches), and a live human disruptor with visible, audience-legible penalties for failure (Crash and Compile). Give CITINEL's demo a persistent visual "damage state" tile that flips from green to red as the poisoned-log injection lands, and keep the OPA approval card and glass-box replay screen-shared live rather than narrated over slides. *[Confidence: high — DEF CON's own official 2026 contest descriptions]*
5. **"Demo gods" failure is a real, currently-documented risk even at top-tier security conferences.** XBOW's own blog documents that a DEF CON 33 (2025) talk by two of its researchers could not be delivered live due to technical issues and had to fall back to a recorded version afterward — a first-party admission, not marketing. Because CITINEL's marquee moment is a *live* attack-then-defense demo, treat live-fail risk as a certainty to plan for: pre-record a byte-for-byte identical fallback run of the same scenario. *[Confidence: medium — XBOW's own blog post, single source but first-party admission]*
6. **Two concrete, replicable YC Demo Day techniques:** a live, judge/investor-personalized opening (Weebly's founder rebuilt each investor's own website live in the first 5 minutes, rather than opening on slides or metrics) and rigorously pre-enumerating the toughest possible questions before pitching (LendUp founder Sasha Orloff's attested pre-mortem technique — and STATE §3's existing "15 hardest judge questions" bank is exactly this, already built; a confirmation, not a new task). Adapt the personalization technique honestly (no fabrication) — e.g. open by referencing a log or artifact type the specific judging panel or a named sponsor's stack would recognize (Render logs, n8n workflow traces, Tavily search results), not a generic title-slide preamble. *[Confidence: medium — first-person named-founder quotes reproduced in LTSE, secondary-blog sourcing]*
7. **Front-load concreteness over novelty-claims.** Innovation-bias research advises expecting initial skepticism of ambitious ideas and countering it by making the idea concrete as fast as possible, not by amplifying the novelty claim itself. Get to a real, running artifact (the actual triage dashboard, an actual OPA policy denial, an actual auto-drafted compliance PDF) within the first 60–90 seconds of the existing 5-beat script, rather than narrating the 7-agent architecture in the abstract first. *[Confidence: high — same iScience 2025 paper as finding 1, extrapolated from consumer-product experiments to pitch judges]*

**Unresolved gap, carried to §22 Open Questions:** the angle on what specifically impresses corporate sponsor/integration-depth judges (evaluating "best use of X" for Render, n8n, Tavily, Swytchcode, Startuped.ai, Lyzr AI, Codemate.ai specifically) produced **zero surviving claims** — genuinely unanswered by this pass, not covered by the general psychology/DEF CON findings above. Source sponsor-judging criteria separately (sponsor rubrics or prior SIH sponsor-track debriefs) rather than assume transfer.

**What was checked and refuted — do not claim:** that XBOW's Black Hat 2025 demo ran against real, live bug-bounty targets, or that "live and real" (vs. simulated) specifically drove audience reaction (both refuted) — stay consistent with CITINEL's own simulated-endpoints-only design; that people remember negative peaks more vividly than positive ones (a negativity-bias claim, refuted); Kevin Mitnick's "full screen transparency" technique as stated (refuted); the YC "exactly one minute, one slide" format claim (refuted); the "micro-demo" and "tell-show-tell" segmenting structure (both refuted) — no verified structural template for splitting the demo into micro-segments exists, so the existing 5-beat structure stands as designed. Note the DEF CON evidence (finding 4) describes contest/spectacle formats, not judged startup-pitch formats — the mapping to a hackathon judging panel is a reasonable analogy, not empirically proven for that exact context.

---

## 19. UI/UX Design Recommendations

*Sourced from a 105-agent pass (21 Aug 2026) — the only one of five parallel passes today that completed its full automated synthesis cleanly (105/105 agents, no session-limit failures). Confidence tags are the workflow's own.*

1. **Keep raw evidence in-context — never navigate the analyst away.** Both Microsoft Sentinel and Elastic Security keep raw logs, entity detail, and query results inside flyouts/side-panels/bottom-docked panels rather than forcing a page change, using progressive disclosure (collapsible panels, tabbed sub-views) instead of one flat dense screen. This directly validates the existing citation-chip-opens-raw-log-line design for the glass-box replay (§11 screen 5). *[High confidence — Sentinel + Elastic product docs]*
2. **Inline hover quick-actions and a bottom-docked, persistent investigation panel** (rather than a modal takeover) keep an analyst in flow during triage. *[Medium confidence, single source — Elastic]*
3. **Group the 7-step agent timeline hierarchically by agent, nested by operation type**, with a dedicated "show failures only" toggle separate from the full timeline — Honeycomb's Agent Timeline pattern maps directly onto CITINEL's glass-box replay and its counter-evidence panel. *[High confidence — Honeycomb docs]*
4. **Three distinct, independently viable visual formats exist for showing step-by-step agent reasoning** — a terminal-style log, a spatial vertical timeline with dotted nodes per tool call, and bordered step cards labeled thinking/tool/answer — worth prototyping more than one before locking the 7-step replay's visual treatment. *[Medium confidence, single source]*
5. **Motion should be sparing and calibrated to context — moving elements inherently compete for attention.** A direct caution for the blast-radius rings and the regulatory clock: don't let ambient animation compete with a high-stakes Approve/Deny decision. *[High confidence — Nielsen Norman Group]*
6. **For the approval card specifically, two patterns survived verification together:** an "Autonomy Dial" (a spectrum of agent independence set per action type, not a binary switch — already close to CITINEL's Shadow/Assist/Autonomous design) paired with an "Intent Preview" — a plain-language, sequential, pre-execution summary of exactly what's about to happen, shown *before* the blast-radius rings and Approve/Deny buttons. *[Medium confidence, single editorial source]* **Explicitly refuted, do not oversell:** the claim that an audit log plus a rollback/undo control is *the single most effective* trust mechanism (0-3) — rollback tokens are necessary but the research says Intent Preview and the Autonomy Dial are what's actually shown to build trust, not rollback alone.

**Open gap this pass could not close, carried to §22 Open Questions:** the accessibility/WCAG/colorblind-safe-severity angle produced **zero surviving claims** — meaning CITINEL's locked red-severity vs. gold-citation color pair (a commonly colorblind-confusable combination) remains genuinely unresearched, not confirmed-safe. This needs a dedicated follow-up pass before accessibility targets are set (§12's "What does NOT exist yet" list already flags this gap; this research pass didn't close it).

**Also flagged, not fully resolved:** dark-mode-first typography and information-density trends for data-dense screens (Angle 3) were only thinly covered by the general motion-restraint findings above — no confirmed claims speak to typography or layout-density specifically for CITINEL's screens.

---

## 20. Enterprise & Government Pitch-Readiness Features

*Sourced from a 105-agent deep-research pass, resumed on 21 Aug 2026. All 105 agents completed and the verify step fully re-checked all 25 claims (16 confirmed, 9 refuted, 0 unverified/errored) — a complete recovery from the original run's session-limit cutoff. However, the automated synthesis step itself returned corrupted debug/placeholder output ("test claim", "Test summary for schema validation debug") instead of real findings — a distinct failure mode from the session-limit issue that affected §16/17/18. Claude reconstructed this section by hand directly from the run's own verification journal, cross-referencing each of the 16 confirmed claims back to its source. This is a more complete recovery than the section's original hand-synthesis: several claims the original version had to list as "errored/unchecked, do not use" are now properly confirmed below.*

**A credible, non-redesign path to multi-tenancy exists — makes STATE's "explicitly out of scope" item concrete:**
1. Google Cloud's reference architecture for multi-tenant agentic AI enforces isolation at the **platform/IAM layer** — a dedicated Cloud project per tenant plus an org-level Principal Access Boundary Policy, with **agents needing no custom authorization code** since the platform automatically enforces the boundary; a shared MCP server can also serve multiple tenants if it does identity propagation. *[Verified 3-0, docs.cloud.google.com — primary]*
2. AWS Bedrock AgentCore's alternative "Pool Model" achieves the same goal differently: namespace-based partitioning of a tenant:user identifier (e.g. `tenant-a:user-123`) rather than separate deployments per tenant, with **per-session compute isolation via lightweight microVMs** (not a full VM per tenant) bounding cross-session exposure without per-tenant infrastructure cost. *[Verified 3-0, aws.amazon.com — primary]*

Together, these give CITINEL a real answer — for the roadmap, not the MVP — to "how would this actually scale to multiple banks without redesigning the swarm": IAM-layer isolation over a shared deployment, not a rewrite of Sentinel/Correlator/Narrator's own logic.

**Enterprise-grade agent identity — now confirmed (the original version had to list this as unverified):**
3. A concrete identity pattern for adding tenant-aware, least-privilege agent auth without touching the swarm's internals: an **"on behalf of" model based on RFC 8693's `act` claim**, where an agent is issued a platform credential carrying the tenant's identity as a claim rather than assuming it directly, enabling policy enforcement on both the agent and tenant dimensions simultaneously; **task-scoped tokens** issued at task start (encoding task ID, tenant, and a minimal permission set, with lifetime matched to expected task duration) replacing long-lived agent credentials; and **tenant-resource authorization enforced independently at the gateway/resource layer** ("does this tenant own this resource?"), verified server-side rather than trusting claims the agent itself provides. *[Verified 3-0 on all three, woxff.github.io]*
4. Framing: in multi-tenant B2B platforms, a single credential-handling mistake (e.g. missing tenant isolation) can expose one customer's data to another — tenant isolation is a security-critical requirement, not a nice-to-have, for any multi-tenant CITINEL deployment. *[Verified 3-0, scalekit.com]*

**Certification sequencing — what's honest to claim, and what isn't:**
5. For Indian enterprise/government buyers specifically, a startup should **start with ISO 27001 over SOC 2** because it dominates Indian procurement requirements — the more realistic first certification target if CITINEL is ever pursued past the hackathon. *[Verified 3-0, cybersek.in]*

**CERT-In empanelment — a hard rule, now confirmed more thoroughly than before:**
6. CERT-In empanelment is formal government authorization for a **firm** to perform security audits, vulnerability assessments, and penetration testing — not a general-purpose product-credibility badge a product company can claim by default. *[Verified 3-0, getastra.com + sisa.ai, independently]*
7. CERT-In evaluates applicant firms on **proven assessment experience, qualified staff, and existing security-testing infrastructure** — criteria a pre-revenue hackathon-stage startup like CITINEL could not honestly claim to meet. "CERT-In empanelled" is not a credibly claimable status pre-revenue. *[Verified 3-0, sisa.ai]*
8. **Now confirmed (previously listed as unverified):** CERT-In empanelment is legally/contractually required for a specific, enumerated set of entities — CII operators, RBI-regulated banks/NBFCs, SEBI intermediaries, IRDAI insurers, telecom operators, power-sector entities, and central/state government or PSU tenders — not a universal security-vendor credential. Government IT security tenders at central, state, and PSU level **routinely list CERT-In empanelment as a qualification/eligibility criterion** for bidders. Empanelment itself requires firm-level track record and certifications (past audit engagements, staff certifications, documented methodology, firm-level ISO 27001, financial thresholds, audited client references) that an early-stage/pre-revenue startup could not credibly claim to hold. *[Verified 3-0 on all three, cybersecify.com]*

**CITINEL must never claim "CERT-In empanelled" as a product credential — it would be both false and a different category of claim entirely.** This is a hard rule, on par with STATE's existing "we draft, we never file" discipline.

**GeM (Government e-Marketplace) eligibility:**
9. GeM registration is open to both buyer organizations (government departments, ministries, CPSEs, state entities, autonomous institutions) and sellers/service providers, meaning a startup *can in principle* register as a seller to sell into government buyers via GeM. *[Verified 3-0, gem.gov.in — primary]* The broader claim that GeM is *the* established channel through which government departments already buy was checked and refuted as overreach (the cited quote didn't support that specific framing) — treat GeM as "registration is possible," not as a proven distribution channel.

**What was checked and did NOT survive this run — avoid these claims entirely:** that tenant context passed via HTTP headers/JWT claims means the core agent's reasoning code needs no changes at all (refuted — some tenant-awareness still touches the agent layer); that Indian enterprises/government/SEBI/RBI-regulated entities require ISO 27001 while SOC 2 Type II is only a US-market expectation, as a blanket framing (refuted — the narrower "start with ISO 27001" claim above *is* confirmed, this broader version is not); that empanelled firms must hold individual professional certifications (OSCP/CEH/CISSP/CREST) (refuted); that CERT-In empanelment carries an ongoing annual-revalidation/5-day-reporting compliance burden (refuted); "trust centers" replacing vendor-mediated sales conversations as the primary buyer-trust mechanism (refuted); current compliance certifications plus transparent pricing and case studies as *the* core credibility elements B2B buyers look for (refuted); a formal Indian-government air-gapped-vs-private/on-prem-cloud tier distinction (refuted); the inbound/outbound agent-authentication-boundary split as a general framing (refuted — though the narrower RFC 8693 findings above *are* confirmed).

**Cross-reference:** this concretizes Innovation Backlog items 18 (multi-tenant Market-SOC) and 19 (air-gapped local-model adapter) — both were previously vague roadmap lines; findings 1–4 above give the multi-tenancy one a real technical shape, including identity architecture. Air-gapped/data-residency specifics did not survive verification this pass and remain vague — a gap for a dedicated follow-up.

---

## 21. Patentability Assessment (Non-Legal-Advice)

*Sourced from a 104-agent deep-research pass (21 Aug 2026; 25 claims verified: 21 confirmed, 4 refuted, 0 unverified), completed with a full automated synthesis on its first run. This section is a synthesis of public patent-law doctrine, published guidance documents, and analogous technical disclosures — it is evidence-based technical/legal-landscape information, **not a legal opinion, not a patentability assessment of CITINEL itself, and not confirmation that CITINEL has, will get, or is likely to get a patent.** Per CITINEL's own rules ("we draft, we never file"; "Danish owns all timelines" — §5.1), any actual filing, drafting, or legal-strategy decision must go through Danish and a real registered Indian patent agent/attorney. Nothing here should be represented to users, investors, judges, or in any external communication as legal advice or as an existing/pending CITINEL patent.*

**India's software/AI patentability framework:**
1. India's **Section 3(k) does not impose a blanket ban on software patents.** The statute excludes "a mathematical or business method or a computer programme *per se* or algorithms" — and the "per se" qualifier, per the landmark Delhi High Court ruling *Ferid Allani v. Union of India* (2019, still good law and still cited in 2023–2025 rulings), excludes only software claimed in isolation without technical effect. Software combined with other elements, or demonstrating "technical effect"/"technical contribution," can be patentable whether or not novel hardware is involved. *[Confidence: high — 6 independently corroborated claims across multiple Indian legal-analysis sources]*
2. India's **2025 Computer Related Inventions (CRI) Guidelines** (finalized 29 July 2025) refine this for AI specifically: mathematical/algorithmic constructs remain "inherently abstract and not patentable in themselves"; AI/ML/DL inventions may be patentable only when they produce a **tangible, real-world technical effect** (not a vague or speculative improvement) with measurable benefit and sufficient implementation detail; and **AI cannot be the sole inventor** — Indian law requires a human "person" as inventor (confirmed by India's 2026 DABUS refusal), while AI-assisted, human-directed inventions remain eligible on ordinary criteria. *[Confidence: high — EU IP Helpdesk's summary + corroborating Indian IP-law sources]* **Practical implication:** claims describing CITINEL only as "using LLM agents to triage alerts" would likely fail this standard; claims tied to specific measurable effects (e.g. false-positive reduction from the deterministic pre-filter, or blast-radius containment) would have a stronger footing — as a matter of doctrine, not as a claim CITINEL is making about itself.

**Comparative US doctrine (context only — India-first product, not the governing law here):**
3. US USPTO guidance (an Aug 2025 Deputy Commissioner memo plus July 2024 AI eligibility examples) draws an analogous abstract-idea-vs-technical-improvement line: a network-intrusion-detection claim was found eligible specifically because it improved the technical field via concrete remedial action (blocking/dropping malicious traffic — USPTO Example 47), while merely automating an existing process with ML was held ineligible (*Recentive Analytics v. Fox Corp.*, Fed. Cir. 2025). *[Confidence: high — verified directly against the primary USPTO memo text, corroborated by ~7 independent law-firm client alerts]*

**Prior-art risk — CITINEL's flagship patterns are not blank-slate territory:**
4. Concrete multi-agent orchestration *mechanisms* (not the abstract idea of "using agents") are already being actively filed: a pending, unexamined 2025 US application (US20250259042A1, Qomplx Inc., filed 18 Feb 2025) claims a specific token-based inter-agent communication protocol where agents exchange compressed embeddings rather than natural language. *[Confidence: medium — verified directly against Google Patents' USPTO mirror; single primary source, pending not granted]*
5. **CITINEL's two core architectural bets already have close structural analogues in published research.** An Aug 2026 arXiv preprint (CyberLLM, TU Munich et al., automotive/software-defined-vehicle cybersecurity) implements both (a) a deterministic pre-filter (regex rules, AST analyzers, topology graph checks) feeding an LLM refinement pass — directly paralleling CITINEL's Sigma-plus-statistical-scorer-before-agent-swarm pipeline — and (b) a mandatory policy/oracle validation gate every autonomous action must pass before execution, with refusal triggering escalation and re-planning — directly paralleling CITINEL's OPA-gated response dial. *[Confidence: high on the disclosure's existence and content; the practical implication is a caveat — unreviewed preprint, different domain — not a certainty]* **This means any real patentability for CITINEL would have to rest on its specific implementation details** (the Sigma+statistical-scorer combination, blast-radius rings, rollback tokens, CERT-In/DPDP-specific compliance logic), not the general "deterministic-filter-then-LLM" or "policy-gate-before-autonomous-action" pattern, which is becoming an established architectural genre in security-adjacent agentic AI.

**A credible, lower-cost alternative:**
6. **Defensive publication** is a recognized IP strategy for an early-stage team without patent budget: deliberately forgoing exclusive patent rights in exchange for public disclosure that becomes prior art, blocking competitors from later patenting the same invention — a "freedom to operate" strategy rather than an exclusivity strategy, and a credible complement or alternative for parts of CITINEL's design the team wants to keep open rather than exclusively owned. *[Confidence: medium — single directly-cited source, split 2-1 vote, but independently corroborated during verification by multiple IP-strategy firms]*

**What was checked and did NOT survive — do not use:** a fabricated "Deontic Subsystem" claimed inside the Qomplx patent filing; a fabricated new "Section 5" of the CRI Guidelines 2025; an overstated claim that India's framework is "closer to EPO than to the US Alice framework"; an overstated cybersecurity "worked example" attributed to the USPTO memo.

**Unresolved gap, carried to §22 Open Questions:** the angle on concrete provisional-filing costs, procedural timeline, startup/student fee concessions, and documented examples of student/hackathon teams or early-stage Indian startups patenting comparable AI/cybersecurity systems produced **no claims that survived adversarial verification** — this is a real gap in the research, not an implicit negative answer, and should be treated as unanswered.

---

## 22. Open Questions for Danish

1. **Shortlist outcome:** Top 60 were to be announced 12 Aug 2026 — did CITINEL advance? (Nothing in the repo records the result; it gates everything downstream: mentorship, sponsor credits, the 5 Sep finale build.)
2. **The QR / demo URL:** the Thank-You slide of the final-form deck contains a *real QR code* and the copy "scan the code. the prototype is already running," yet this repo contains no code and no recorded demo URL. Where does the QR point, does a prototype exist elsewhere (separate repo? Render account?), and should that work be brought under this repo's planned `backend/`/`dashboard/` structure? *(Related: was the deck in fact submitted on 11 Aug? The repo has no record of the submission event itself.)*
3. **Version control:** the folder is not a git repository. Initialize git (with `.gitignore` for `.DS_Store`) and push to a remote? This is the campaign's single point of failure right now.
4. **2026-edition evidence chain (§9.8):** the deck and slide guides cite 2026 sources (RBI Directions 2026, IBM 2026, SANS 2026, OpenSec, Gartner, Five Eyes), but the docs/ research corpus stops at 2025-era finding IDs, and several deck figures (₹255M/25.5cr IBM 2026 India; the Evidence-slide 2026 chips) have no finding ID or archived URL anywhere. Back-fill these into docs/ with IDs + full URLs per the corpus's own traceability rules?
5. **Slide-guide sync:** should the six assembly-guide MDs be updated to match the shipped deck (remaining gaps: `[FILL]` placeholders, team-slide layout, some body copy), or frozen as history with a pointer to the PDF as canonical?
6. **Slide-11 discrepancy:** "24 minutes inside the clock" vs "34 minutes inside the clock" — which figure is intended for future materials? (Also: standardize 789,793 vs 790,000.)
7. **Uninventoried assets (§9.10–9.11):** `1R.png`, `14R.png`, `SP7.png`, `2.B1–2.B3`, `4.6/4.7`, `10.6`, `11.6`, `12.6/12.7`, the six team headshots, and the two `logo_lockup_*` composites — add to the inventories (and update the brand README's stale "composites not committed" note), or delete the strays?
8. **Open checklist items** (STATE §5): cost-per-incident instrumentation plan, MSSP quotes, sponsor quota table — track as issues once git exists?
9. **Design authority for product UI:** is dark-first confirmed for the dashboard? Which display typeface is canonical for product UI (Michroma/Orbitron per brand README, vs the deck's pixel-style display face)? What are the accessibility targets (the approval card and quarantine-red/evidence-gold semantics need contrast-checked tokens)?
10. **Auth & roles:** Analyst vs CISO views are specified, but no authentication/authorization model exists anywhere. Single-tenant with two roles for MVP?
11. **SDD placement:** should this SDD live in `docs/` under the state file's precedence chain (and does it become the build-phase source of truth alongside CITINEL-STATE.md)?
12. **Competitor-by-competitor CERT-In/DPDP audit (§13 item 6):** the white-space claim currently rests on one 2026 comparison article's silence plus one refuted competitor claim. Worth commissioning an individual check of each of the ten named competitors (Microsoft Security Copilot, CrowdStrike Charlotte AI, Palo Alto XSIAM/Cortex AgentiX, Google SecOps, Prophet Security, Torq, Simbian, Exaforce, Radiant Security, StrikeReady) before repeating the claim in a judge-facing setting?
13. **Innovation Backlog triage (§14):** of the 16 new candidate features, which (if any) does Danish want scoped into an actual roadmap phase, and which should stay backlog-only? None are currently authorized to enter the build plan.
14. **Deadline/shortlist-size discrepancy (§15.4):** the live event page states idea-submission deadline 13 Aug 2026 and Top 80 teams advancing; internal docs and the webinar deck state 11 Aug and Top 60. Which is current? Directly affects whether item 1 above (shortlist outcome) has even been decided yet.
15. **Lyzr AI stack addition (§15.3):** the partner-prize plan adds Lyzr AI as a governance/observability layer over the swarm — a real change to STATE §1.10 and deck slide 8's partner list. Confirmed for the build, or does Danish want a different attachment point (or none)?
16. **Accessibility research gap (§19):** the UI/UX pass's accessibility angle produced zero surviving claims — CITINEL's locked red-severity/gold-citation color pair (a commonly colorblind-confusable combination) remains genuinely unresearched. Worth commissioning a dedicated follow-up before setting accessibility targets?
17. **CERT-In empanelment discipline (§20 items 6–8):** confirmed as a hard rule, now with fuller evidentiary backing than the original version — CITINEL must never claim "CERT-In empanelled" as a product credential, since it's a services authorization for firms performing audits, not something a product earns. Worth adding to STATE's own honest-claims rule set (§5.1 rule 4/5) so it isn't only recorded here?
18. **Research-integrity status, final:** all eleven deep-research passes run 21 Aug 2026 are now complete. Nine finished (or were resumed to finish) with a full, clean, automated synthesis (§13, §14 including its final addition, §16, §17, §18, §19, §21). §20 (Enterprise/Government) is the sole exception — fully re-verified on both its runs, but its synthesis step returned corrupted debug-placeholder output both times, so it was reconstructed by hand from the verification journal directly (see §9 item 13 and §20's own header). No further resumes are pending.
19. **Patentability strategy decision (§21):** the research found CITINEL's two flagship architectural patterns (deterministic-pre-filter-then-agent pipeline; policy-gated autonomous-response mechanism) already have close structural analogues in a pending US patent filing and an Aug 2026 arXiv preprint — meaning real patentability would rest on CITINEL's specific implementation details, not the general pattern. Does Danish want to pursue a provisional patent filing (via a real Indian patent agent — CITINEL's own research could not surface cost/timeline/student-fee-concession specifics, a genuine gap), pursue defensive publication instead for parts of the design, do both for different components, or table this until post-hackathon? This decision sits squarely under "Danish owns all timelines" (§5.1 rule 5) and must not be decided or implied by Claude.
20. **Gamification/skill-building research gap (§14.F):** the final research pass produced zero confirmed claims on attack-simulation, tabletop-exercise generation, or analyst training loops for under-resourced bank IT teams — genuinely unresearched, not a "no." Worth a dedicated follow-up pass, given item 27's rationale-artifact structure is flagged as a plausible building block?
21. **Community/network-effect feature strategy (§14.F item 28):** the FINRA Financial Intelligence Fusion Center precedent suggests a CITINEL-operated opt-in threat-sharing portal across subscribing cooperative banks is architecturally credible, but it's new infrastructure (a multi-tenant sharing backend with consent/anonymization controls) that doesn't exist today and wasn't otherwise strongly evidenced this pass (five adjacent federated-learning/marketplace claims were refuted). Backlog-only, or worth scoping further?
22. **MITRE ATT&CK extension taxonomy (§14.F item 24):** Anthropic's own disclosure confirms no existing ATT&CK technique ID covers AI-agentic multi-step orchestration behavior. Is a CITINEL-authored extension-taxonomy for this gap worth scoping into the roadmap, or backlog-only?
23. **CERT-In empanelment framing, sharpened (§20 items 6–8):** now confirmed (not just plausible) that empanelment is legally required for RBI-regulated banks/NBFCs among other named entity types, and that government tenders routinely list it as a bidder-eligibility gate — but CITINEL itself, as a pre-revenue product company, cannot currently meet empanelment's firm-level track-record criteria. Should the pitch instead describe a future partnership with an already-empanelled firm, rather than any framing that could read as CITINEL pursuing empanelment directly?

---

## 23. Approval Checklist

Tick each item to approve moving to the next phase (Claude Design hand-off):

- [ ] **Repo read confirmed** — 150 files; all 17 MD + 1 HTML + 3 PDFs (42 pages) read in full; 125 PNGs accounted for (most via in-repo inventories + composited deck review; ~20 outside any inventory, flagged in §9.10–9.11); no code/config/secret files exist to read.
- [ ] **Executive summary accepted** — "documentation-and-deck campaign repo; product specified, not built" is the correct characterization.
- [ ] **Planned architecture accepted as the build target** — pipeline, 7-agent swarm, OPA dial, compliance drafter, safety plane, fallback ladder (§2.2).
- [ ] **Assumption labels reviewed** — every item marked *Assumption/Inferred* (deck submission status, auth model, dark-first UI, DB schema, all non-★ screens in §11) is either confirmed or corrected.
- [ ] **Gap list acknowledged** (§9) — especially: no git, the guides/docs/deck evidence-chain drift (§9.8), uninventoried assets, slide-11 inconsistency, stale brand-README composites note.
- [ ] **UVPs/USPs reviewed** (§13, §17) — 20 messaging claims plus 6 clustered additional unconventional/cutting-edge findings (10 pieces of evidence total, now fully re-synthesized), each evidence-tagged.
- [ ] **Innovation Backlog reviewed** (§14) — 29 candidate features (21 original + 8 from a final, fully-synthesized innovation/creativity pass in §14.F), none committed; Danish selects which (if any) enter the actual roadmap. Note the two research gaps in §14.F (gamification/skill-building: zero confirmed claims; community/network-effect: weakly evidenced) are carried to Q20–21.
- [ ] **Partner Prize Plan reviewed** (§15) — all 7 partner tracks closed by design; Lyzr AI stack addition specifically confirmed; date/shortlist discrepancy resolved.
- [ ] **Architecture Hardening reviewed** (§16, fully re-synthesized) — 9 findings, each evidence-tagged; note the retraction of the original version's short-lived-credentials/OAuth-OBO recommendations (refuted on full re-verification); none yet applied since no code exists.
- [ ] **Demo Wow-Moment design reviewed** (§18, fully re-synthesized) — peak-end structure, "demo gods" fallback-recording recommendation (new), opening hook, and existing Q&A-bank confirmed as already-aligned practice; sponsor-judging-criteria gap (§18, angle 4) noted as unresolved.
- [ ] **UI/UX recommendations reviewed** (§19) — accessibility gap (Q16) specifically flagged for follow-up before component work starts.
- [ ] **Enterprise/Government readiness reviewed** (§20, hand-reconstructed from a corrupted-synthesis run) — CERT-In-as-product-credential prohibition (Q17) specifically acknowledged as a hard rule; the RFC 8693 agent-identity pattern is now confirmed evidence, not unverified.
- [ ] **Patentability assessment reviewed** (§21, new) — explicitly non-legal-advice; prior-art risk (Qomplx filing, CyberLLM preprint) acknowledged; filing/defensive-publication decision (Q19) is Danish's alone to make.
- [ ] **Open questions answered** (§22) — at minimum: shortlist outcome, QR/prototype location, git initialization, design authority (Q1–Q3, Q9), the newer §15/§19/§20/§21/§14.F-driven questions (Q14–23).
- [ ] **Screen inventory (§11) approved as the Claude Design input** — ★ explicit heroes confirmed; inferred screens, states, and the out-of-scope line accepted or amended.
- [ ] **Design system inputs (§12) approved** — brand tokens/rules carried into product UI; missing pieces (type scale, components, a11y) assigned to the design phase.
- [ ] **Explicit approval to proceed** to the Claude Design phase.

---

*End of SDD. Per instruction, this document stops here — no design prompts, no design-system generation, no code. Awaiting explicit approval.*
