# A7 — Post-Build Security Hardening & IP/Differentiation Analysis (Decode SIH 2026, Track 3 "Bharat Pragati" PS4)

*Prepared 2–3 Sep 2026, a post-build supplement to the Aug 2 idea-lock research pack (A1–A6) and `CITINEL-STATE.md`. A1–A6 researched the IDEA before any code existed; this report audits the ACTUAL DEPLOYED CODEBASE and adds two research angles the original pack never covered. Two instruments fed it: (1) an adversarial security audit of the real, running codebase across six attack surfaces, every finding independently re-verified before counting; (2) two cited, adversarially-verified web research passes (3-vote panels against primary sources) — one on security-hardening standards, one on patent/IP novelty. New finding-ID prefixes: **SEC-Fxx** (codebase audit), **EXT-Fxx** (external security research), **PAT-Fxx** (patent/IP research).*

*Angles already thoroughly covered by the Aug 2 pack are NOT re-researched here — see **A2-competition.md** for competitive landscape and **A6-compliance.md** for CERT-In/DPDP/RBI mechanics. Two of the five patent-research angles (Merkle/witness-cosigning audit architectures for AI decisions; Gartner/Forrester-sourced moat analysis) returned zero confirmed findings and remain genuinely unresearched — treat as open gaps, not negative results.*

**Standing hard rules from `CITINEL-STATE.md` apply unchanged and are not relitigated here: honest claims only · we draft, we never file · no timelines/schedules — Danish owns all timelines · the §1.4 differentiation line only · "mitigates, never solves" claim discipline for injection defense. Section 3 below adds newer (2025–2026) citations that independently reinforce that same discipline — it does not replace it.**

---

## Executive Summary

1. **The most serious issue found all session is now closed and deployed.** With no authentication of any kind, anyone reaching `citinel-web.onrender.com` could forge a `human_signoff` naming a real person and close an incident on their authority — and the ledger's own `/verify` route would call the result "chain intact." Fixed with a fail-closed `X-Citinel-Write-Token` guard on every write route (commit `c30f484`); reads stay fully public. [SEC-F01, SEC-F02]
2. **25 codebase findings confirmed by independent re-verification; 7 of the highest-severity ones are already closed** by tonight's write-guard and blast-radius fixes. 18 remain open, none breaking the live demo. [SEC-F01–F25]
3. **Two open findings directly undercut a core marketing claim and deserve priority**: citation-gating — CITINEL's headline "every claim cites the exact log line" feature — is only mechanically enforced on the Narrator's claims; the Correlator's kill-chain citations and the Marshal's proposal citations reach the console unverified. [SEC-F08] Separately, prompt injection can steer the Triage Router straight to `auto_close`, ending an investigation on attacker-authored content with a reassuring banner. [SEC-F06]
4. **The append-only ledger has no persistent disk on Render** — confirmed independently by this audit after being flagged earlier in the session. Every restart or deploy silently deletes all live-written frames; only the committed seed corpus survives. This is the single fact most at odds with "tamper-evident audit trail" as a headline claim, and it is a paid-tier decision, not a code fix. [SEC-F13, SEC-F19]
5. **External security research (5 findings, all high-confidence, primary-sourced) reinforces rather than replaces the existing "mitigates, never solves" claim discipline** from A3/SAFE-F02: detection-based defenses against prompt injection are heuristic by construction and are defeated at 97–100% rates by advanced attacks even when active — CITINEL must never claim "immune to injection." The credible alternative — deterministic, capability-based authorization at the tool-call boundary — is exactly what CITINEL's policy gate already does, and now has a named, non-bespoke academic vocabulary (Biba integrity, reference monitoring, least privilege). [EXT-F01, EXT-F02]
6. **OWASP's Agentic Security Initiative (Dec 2025) independently validates three CITINEL mechanisms in its own published taxonomy**, without CITINEL having invented the vocabulary: the hash-chained ledger with external witness maps to its T8 "Repudiation & Untraceability" mitigation; the tiered policy gate maps to its T10/ASI09 finding that a flat approve-everything gate is *itself* an attack surface; mock-only execution maps to its Playbook 3 sandboxing guidance. [EXT-F03]
7. **OWASP ASVS 5.0 gives a quantified, checkable hardening bar for the FastAPI/container layer (345 requirements, L1≈20%, L2≈70%) but explicitly covers zero LLM/agentic risk** — ASVS-L2 conformance and agent-pipeline safety are two separate, non-substitutable claims, and CITINEL's language must never conflate them. [EXT-F04]
8. **India offers a real, current legal pathway to patent an AI-security mechanism.** Section 3(k) bars only a "computer programme per se"; since *Ferid Allani* (Delhi HC, 2019, folded into the June 2025 CRI Guidelines v2.0), a software-based invention showing a "technical effect or technical contribution" is patentable. This is confirmed, current law — not a hopeful reading. [PAT-F01]
9. **No single CITINEL component is likely patentable alone — every piece has adjacent prior art.** Threshold-gated autonomous response with no human approval is already patented (Darktrace US12069073B2, SecureWorks US20250148052A1); ML-scored triage with a recommended action is already granted (Capital One US11165815B2); multi-agent LLM pipelines producing an "auditable" triage decision are already shipped (Microsoft Copilot for Security) and published academically (CORTEX, Sept 2025). [PAT-F02, PAT-F03]
10. **The likely patentable surface, if any exists, is the specific *combination*** — citation-gating bound to hash-chained/witnessed audit + blast-radius-tiered approval + injection quarantine + dissenting second-opinion + glass-box replay — not any one piece. The one mechanism that looked most distinctively unclaimed (binding a model's output content to the exact evidentiary source text, as opposed to binding output to model/execution identity, which is what the nearest prior art — CommitLLM — actually does) could **not** be checked against the academic literature most directly on point (ALCE, FullCite, an ACL 2026 survey of 134 grounding papers) due to research-tooling failures. This is the single most consequential open question before any filing decision, and it is unresolved, not favorable. [PAT-F04, open question below]

---

## SECTION 1 — Codebase Security: What Shipped and Verified Tonight (2 Sep 2026)

| Commit | What it closes | Verified |
|---|---|---|
| `cbd3d1f` | Public interactive API console (`/docs`, `/redoc`, `/openapi.json` all 200 to anyone) closed behind `CITINEL_API_DOCS` (default off) | 3 routes confirmed 404 by default, restorable for local dev |
| `cbd3d1f` | Policy gate trusted a caller-supplied `assets_affected` — an anonymous POST claiming `0` for `isolate_host` walked past the SAFE-F07 blast-radius cap | Server-side floor added; asset-free classes (`enrich_ioc`/`query_logs`/`notify`) deliberately pass through unfloored so the existing "claiming 1 for a zero-asset class escalates on purpose" fail-safe survives — this exact regression was caught by the pre-existing test suite mid-fix |
| `c30f484` | **The critical finding**: any unauthenticated caller could POST a `human_signoff` naming a real person, and `/api/ledger/verify` would certify the forged chain "intact" | Fail-closed `X-Citinel-Write-Token` guard, `secrets.compare_digest`, on every non-GET `/api/` route. Verified 3 ways: 263 backend tests including a dedicated `test_write_guard.py`; in-browser (token persists via `sessionStorage`, reaches every write); a real `uvicorn` process (not TestClient) hit directly with `curl` — no header 401, wrong header 401, correct header 200 with a real ledger write, every GET route untouched |

**Deployment consequence, stated plainly:** writes on the live console (execute, deny, sign off, reopen, run the swarm, gather context/handover) return 503 until `CITINEL_WRITE_TOKEN` is set in the Render dashboard and the same value is pasted into the console's own Settings screen. Reads are completely unaffected — the glass-box premise (public, no-login browsing) holds. This is Render-side secret configuration, Danish's to set.

---

## SECTION 2 — Full Codebase Audit Result: 25 Confirmed Findings

*Six attack surfaces (authorization/abuse, the LLM pipeline reading attacker-controlled input, secrets/deployment, classic appsec, ledger integrity, supply chain), each finding independently re-verified — a second, adversarial pass that could dismiss a finding on the merits, and did dismiss several early over-claims. `breaks_demo` marks whether closing it would stop an unauthenticated judge from browsing; none of the 25 do.*

| # | Severity | Surface | Status | Finding |
|---|---|---|---|---|
| SEC-F01 | Critical | integrity | **FIXED** | Any unauthenticated caller could forge hash-chained ledger frames, including a `human_signoff` closing an incident under a named human's authority |
| SEC-F02 | High | authz | **FIXED** | Every write route was unauthenticated |
| SEC-F03 | High | authz | **FIXED** | "Structural human approval" was satisfied by an attacker-supplied free-text string |
| SEC-F04 | High | authz | **FIXED** | Sign-off forgery under any name |
| SEC-F05 | High | authz | Open | Unauthenticated resource exhaustion — attacker-sized ledger frames, unbounded in-memory swarm-run state (now requires the write token, lowering severity in practice) |
| SEC-F06 | High | llm | **Open — priority** | An attacker-written log line can steer the Triage Router to `auto_close`, ending the investigation with a reassuring banner |
| SEC-F07 | High | llm | Open | The Marshal's trusted instruction interpolates the model-written verdict headline (and log-derived host names) unfenced |
| SEC-F08 | High | llm | **Open — priority** | Only the Narrator's claims are mechanically citation-verified; Correlator kill-chain citations and Marshal proposal citations reach the console unchecked |
| SEC-F09 | High | secrets | Partially closed | No deployment kill-switch for paid operations (`ui_swarm_enabled` defaults open); the swarm route itself is now behind the write-token, closing the unauthenticated denial-of-wallet vector specifically |
| SEC-F10 | High | appsec | Open | Unauthenticated 4.2 MB response amplification on `/api/incidents`, no cache/pagination/rate limit (must stay a public read; needs pagination, not auth) |
| SEC-F11 | High | integrity | Open | The hash chain covers only the ledger file — verdicts and raw evidence the console presents sit outside it |
| SEC-F12 | High | integrity | Open | Two concurrent writes can permanently break the chain (each request builds its own `AuditLedger` instance — a real concurrency bug independent of auth) |
| SEC-F13 | High | integrity | **Known, Danish's call** | No persistent disk on Render — every restart/deploy silently deletes all live-written ledger frames |
| SEC-F14 | High | supplychain | Open | No lockfile reaches the Render build; Python dependencies float on unbounded `>=` floors |
| SEC-F15 | High | supplychain | Open | The separate `citinel-n8n` service runs a mutable `:latest` tag with a persistent credential volume |
| SEC-F16 | Medium | authz | Reduced | Rollback tokens published on a public read route, not bound to an incident or actor (now requires the write token to redeem) |
| SEC-F17 | Medium | authz | **FIXED** | Denial-of-wallet via the unauthenticated swarm route |
| SEC-F18 | Medium | llm | Open | The citation gate verifies quotes against text the *attacker* wrote — real, but the console should be precise that this proves "verbatim in evidence," not "trustworthy" |
| SEC-F19 | Medium | secrets | **Known, Danish's call** | Same root cause as SEC-F13 |
| SEC-F20 | Medium | secrets | Open | Neither Docker image pins its base image or dependencies |
| SEC-F21 | Medium | appsec | **Checked tonight, currently inert** | `GET /api/incidents/{id}/draft` fires real paid Lyzr calls on every hit with no cache or confirm gate — but Lyzr credentials are `absent` on the live deployment right now, so this is a zero-cost landmine, not an active drain. **Must be fixed before Lyzr credentials are ever set on Render.** |
| SEC-F22 | Medium | integrity | Open | The external witness — the stated defense against wholesale ledger replacement — is not configured on the live deployment |
| SEC-F23 | Low | llm | Open | The Enricher's tool loop has no cap on tool calls per turn |
| SEC-F24 | Low | llm | **Superseded** | Blast radius trusted the model's own number — this is the same class of issue `cbd3d1f`'s server-side floor already fixes for the *execution* path; the swarm's *displayed/suggested* value is still whatever the model said, which is now cosmetic since the gate enforces the real floor |
| SEC-F25 | Low | supplychain | Open | No SBOM, no vulnerability scan, no `pip` in the deployed venv — nobody, including this audit, can enumerate known CVEs in current dependencies |

---

## SECTION 3 — External Security Research: Newer Citations Reinforcing the Existing Claim Discipline

*Five findings, all high-confidence, all verified against primary sources by independent 3-vote panels. This research post-dates A3/A6 (OWASP's Agentic taxonomy below was published 9 Dec 2025, after the Aug 2 idea-lock) and should be read as sharpening the citation base behind the already-locked "mitigates, never solves" line — not as new positioning.*

**[EXT-F01]** Prompt-injection detection filters and classifiers — including LLM-as-judge detectors — are heuristic by construction and cannot guarantee prevention. In controlled evaluation, advanced indirect-prompt-injection attacks defeated nearly every baseline filtering defense (Prompt Warning, Sandwich, Paraphrasing, Spotlighting, Keyword Filtering, LLM-as-Judge) across nine LLM backbones, with hijack rates of 97–100% even with defenses active.
Sources: arXiv:2506.08837 (14 authors, ETH Zurich/Google DeepMind/Microsoft/IBM/Invariant Labs, Jun 2025); arXiv:2604.03870 (ASU/Morgan Stanley/UC Davis/WashU/Rice/Oxford, Apr 2026). **Consequence: CITINEL must never claim "immune to prompt injection" on the strength of the quarantine layer — the correct claim remains "designed per published secure-agent patterns," matching SAFE-F02/LAND-F24's existing "mitigates, never solves" discipline exactly.**

**[EXT-F02]** The credible alternative to detection is a deterministic authorization gate at the tool-call boundary — attaching capability/provenance tags to data and checking policy at the moment a tool is invoked, rather than asking the model to behave. Published architectures (CaMeL, FIDES, Progent, RTBAS, FORGE) are explicitly organized in the literature as instances of three classical security constructs: Biba integrity protection, reference monitoring, and least privilege.
Sources: arXiv:2503.18813 (CaMeL); arXiv:2606.26479 (survey). **Consequence: this gives CITINEL's policy gate (tier classification + named human approval before execution) a named, non-bespoke design vocabulary — "built to a published secure-agent design pattern," a stronger and more precise claim than "we have a policy gate."**

**[EXT-F03]** OWASP's Agentic AI Threats & Mitigations taxonomy and its Top 10 for Agentic Applications (published 9 Dec 2025, ASI01–ASI10 identifiers) name exact threat/control pairs CITINEL's architecture already instantiates: (a) untraceable agent action is a first-class threat (T8, Repudiation & Untraceability) whose prescribed mitigation is cryptographically signed, immutable logs — directly the hash-chained, externally-witnessed ledger; (b) human-in-the-loop approval is itself a named attack surface, not an assumed-sound mitigation — attackers can induce decision fatigue for rushed approvals (T10) or exploit confident, polished agent explanations to mislead operators (ASI09) — OWASP's remedy is risk-tiered oversight with dynamic intervention thresholds, meaning a flat "approve everything" gate is itself theater and a genuinely tiered gate is the named defense; (c) tool execution should run sandboxed, non-production, with just-in-time access and mandatory approval for consequential actions (Playbook 3) — directly mock-only execution; (d) indirect prompt injection via ingested content is OWASP's #1-ranked agentic risk (ASI01), with the real-world EchoLeak zero-click exploit (CVE-2025-32711) against Microsoft 365 Copilot as the canonical example of exactly the threat class facing any pipeline, like CITINEL's, that parses attacker-controlled telemetry.
Sources: genai.owasp.org (Agentic AI Threats & Mitigations; Top 10 for Agentic Applications, 9 Dec 2025). **Consequence: three CITINEL mechanisms can be described as "OWASP-named controls," not bespoke design choices — a materially stronger claim in front of security-literate judges. EchoLeak is a strong, concrete real-world analogy for the demo's "poisoned log" beat.**

**[EXT-F04]** OWASP ASVS 5.0.0 (May 2025) gives a quantified, independently-checkable bar for the FastAPI/container web layer: 345 requirements across 17 chapters, L1 = 70 requirements (~20%), L2 = 253 cumulative (~70%). Every security-logging requirement (chapter V16) sits at L2 or above — the specific controls a tamper-evident ledger needs (unmodifiable logs, transmission to a logically separate system, synchronized timestamps) are all L2, meaning ASVS-L1 conformance would say nothing about CITINEL's ledger design. Critically, ASVS 5.0 contains **zero** references to LLM, AI, agentic, or prompt-injection risk anywhere in all 345 requirements — by explicit design, so as not to overlap OWASP's LLM/Agentic projects (which is why OWASP maintains a separate AISVS project).
Source: github.com/OWASP/ASVS (verified two independent ways: a full CSV parse reproducing the exact 345/70/253 split, and a git-clone grep confirming zero word-boundary matches for LLM/AI/agentic terms). **Consequence: ASVS-L2 conformance and agentic-pipeline safety are two separate, non-substitutable claims — CITINEL's language must state both, never let one stand in for the other.**

**[EXT-F05]** OWASP publishes an exact, checkable baseline HSTS configuration for a production HTTPS service: `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`.
Source: OWASP HTTP Headers Cheat Sheet. A literal, low-inference, standalone finding — useful as a concrete item on the ASVS-hardening checklist, nothing more.

---

## SECTION 4 — What NOT to Claim (Overreach Caught by Adversarial Verification)

*Each of these was proposed during research and explicitly refuted by independent 3-vote panels. Listed because they are genuinely tempting phrasing — a future draft of pitch material should not resurrect any of them.*

- "Architectural/out-of-band enforcement is the field's 2024–2026 research consensus" — too strong; the literature shows it as *a* credible direction, not settled consensus.
- "Some prompt-injection mitigations are actively counterproductive, hence security theater" — not supported; the correct claim is narrower: detection alone is *insufficient*, not that specific alternatives are harmful.
- "CaMeL's guarantee holds even when the underlying model remains individually susceptible to injection" — overreach; the mechanism is real, but this precise formulation of what it guarantees did not survive verification.
- "OWASP requires stripping platform/version-identifying headers (Server, X-Powered-By, etc.)" — this specific claim is not OWASP-sourced as worded, even though header-stripping may still be reasonable general practice.
- "The *Ferid Allani* judgment expressly names AI and blockchain as automatically-patentable fields" — refuted 0-3; the ruling sets a general technical-effect test, not a named AI carve-out. Do not cite it that way.
- "A SentinelOne patent covers fully autonomous, no-human-intervention malware remediation" as directly comparable prior art to CITINEL's human-approval gate — refuted; the actual patent scope is narrower (root-cause attribution) and this specific comparison over-extends it.
- "AuditableLLM's SHA-256 hash-chain already covers LLM audit logging generally" — refuted; that work targets a different audit surface (model lifecycle/parameter events), not inference-output auditing the way CITINEL's ledger does.
- "CommitLLM's exact protocol mechanics (commit-then-challenge, Freivalds' algorithm, Merkle proofs over embedding/KV state)" as characterized in one research pass — refuted; treat CommitLLM's high-level purpose (binding output to model/execution identity) as confirmed, but do not repeat these specific mechanism details without re-checking them directly.

---

## SECTION 5 — Patent / IP Novelty Analysis

*India's Patents Act §3(k) bars only a "computer programme per se" — software patentability is real but narrower than in the US, and requires demonstrating a technical effect. This section reports what a research pass found; it is not legal advice, and nothing here should be read as "this is patentable." A qualified patent attorney and a formal, professional prior-art search must precede any actual filing.*

**[PAT-F01] The operative Indian legal test.** *Ferid Allani v. Union of India* (Delhi HC, 12 Dec 2019) held that a software-based invention is patentable if it demonstrates a "technical effect or technical contribution" — Section 3(k) bars only the programme "per se," not every software-implemented invention. This is current, still-cited law, folded into the Indian Patent Office's June 2025 CRI Guidelines v2.0. Confirmed 3-0 against the primary judgment text, corroborated by multiple independent law-firm analyses.

**[PAT-F02] CITINEL's individual mechanisms each have adjacent prior art — none of them is novel in isolation.**
- Fully autonomous execution of a security response once a score crosses a threshold, with *no* human-approval step: already patented (Darktrace US12069073B2, granted Aug 2024; SecureWorks US20250148052A1, published May 2025, narrower scope — alert classification, not active remediation).
- ML-scored alert triage that also recommends a next action: already granted (Capital One US11165815B2).
- Both single-agent and multi-agent LLM pipelines that triage security telemetry into an "auditable" decision: already shipped in production (Microsoft Copilot for Security, deployed across Defender XDR customers) and already published academically (CORTEX, arXiv, Sept 2025) — CORTEX's own paper frames single-agent end-to-end LLM triage as the prior art it improves on.

None of this prior art combines an LLM with citation-to-evidence verification, a hash-chained/witnessed ledger, or blast-radius-tiered human approval — but each *piece* of CITINEL's architecture, taken alone, is anticipated by something already granted or shipped.

**[PAT-F03] The likely patentable surface, if one exists, is the specific integration** — citation-gating bound to a hash-chained/witnessed ledger, blast-radius-tiered approval, injection quarantine, dissenting second-opinion recording, and glass-box replay, combined in one system for security operations. This is consistent with India's technical-effect doctrine (a system/combination claim solving a stated technical problem — verifiable, auditable autonomous action — rather than a claim on any one generic step).

**[PAT-F04] The single most consequential open question is unresolved, not favorable.** CITINEL's most distinctive mechanism — mechanically verifying that a model's claim is backed by the *exact evidentiary source text* it cites, rather than merely asking the model to cite — is the piece with the thinnest confirmed prior-art picture. The nearest confirmed adjacent work (CommitLLM, a gateway-provenance paper) binds a cryptographic commitment to *model/execution identity* (which model, what input, what decode policy produced this output) — a different and narrower binding than CITINEL's claim-to-evidence-span verification. But the academic literature most directly on point for *that specific* mechanism — ALCE (EMNLP 2023, the first automated benchmark for LLM citation quality), FullCite (a framework linking each LLM claim to a supporting evidence span — a close conceptual parallel), and an ACL 2026 survey reviewing 134 prior grounding/attribution papers — **could not be checked** due to research-tooling failures during this pass. Treat CITINEL's citation-gating novelty as *unknown*, not confirmed-clear, until a follow-up research pass (or a professional prior-art search) actually reads that literature.

**Recommendation:** if a patent filing is genuinely under consideration, the two items to resolve first are (1) a proper read of ALCE/FullCite/the ACL 2026 survey against CITINEL's exact citation-verification mechanism, and (2) a conversation with a patent attorney about whether a system/combination provisional filing (covering the five-mechanism integration in PAT-F03) makes sense *before* any further public disclosure — a demo, a pitch deck, or open-sourcing any part of the pipeline can itself start a novelty clock running against a later filing.

---

## SECTION 6 — Recommended Differentiation Additions

*These extend, and must never contradict, the locked §1.4 differentiation line and the four headline features in `CITINEL-STATE.md` §1.4. None of the below is a replacement for that line — it is supporting evidence a judge who pushes back can be answered with.*

1. **"Built to named, published secure-agent design patterns, not ad hoc."** The policy gate is describable as implementing Biba integrity protection, reference monitoring, and least privilege — the same academic vocabulary as CaMeL and peer research (EXT-F02). This upgrades "we have a policy gate" to a citable claim.
2. **"Three of our mechanisms map directly onto OWASP's own Dec-2025 agentic-security taxonomy."** The ledger→T8, tiered approval→T10/ASI09, mock-only execution→Playbook 3 (EXT-F03). Naming EchoLeak (CVE-2025-32711) as the real-world precedent for the "poisoned log" demo beat is a strong, concrete, judge-recognizable anchor — stronger than the CrowdStrike outage analogy already used for blast-radius (SAFE-F07), and complementary to it, not a replacement.
3. **Honest patent framing, if IP is raised by a judge:** "No single piece of our pipeline is patentable alone — every component has prior art. What we believe is genuinely novel is the specific combination, and we're validating that with a proper prior-art search before considering a filing." This is a *stronger* answer than an overclaim, because it demonstrates the same evidence-discipline the product itself is built on.
4. **A precise line distinguishing citation-gating from "AI explainability":** most competitors' "explainability" is a confidence score or a natural-language rationale; CITINEL's citation gate is a *mechanical, non-prompted check* that the model's claim text appears verbatim in the evidence it cites — closer to a compiler check than to an LLM's own self-report. (Caveat: keep this claim scoped to what SEC-F08 confirms is actually enforced today — only Narrator claims, not yet Correlator/Marshal ones — until that gap is closed.)

---

## SECTION 7 — Implementation Roadmap, Ordered

*Ranked by (confirmed severity × live exploitability), not by ease. "Breaks demo" already ruled out for all of these — none of them changes what a judge sees browsing the console.*

1. **Set `CITINEL_WRITE_TOKEN` on Render** (Danish, Render dashboard) — restores write functionality on the live console; the single blocking item from tonight's work.
2. **Decide on a persistent Render disk for the ledger** (SEC-F13/F19) — paid tier, Danish's call; the biggest gap between the "tamper-evident audit trail" claim and current reality.
3. **Extend citation-gate enforcement to Correlator and Marshal claims** (SEC-F08) — closes the gap directly under CITINEL's headline feature; high value for the effort.
4. **Harden the Triage Router against an attacker-authored `auto_close`** (SEC-F06) and fence the Marshal's unfenced interpolation of model-written text (SEC-F07) — the two concrete injection findings that survived audit.
5. **Fix the concurrency race in the ledger** (SEC-F12) — a correctness bug independent of auth; two simultaneous writes can permanently break the hash chain.
6. **Add pagination/rate-limiting to `/api/incidents`** (SEC-F10) — must stay a public read, needs bounding, not gating.
7. **Fix `/draft`'s unauthenticated paid-call exposure before Lyzr credentials are ever set on Render** (SEC-F21) — currently inert only because Lyzr is unconfigured; this is a precondition to check *before* turning Lyzr on, not an emergency tonight.
8. **Supply-chain hygiene**: pin the Docker base image and Python dependencies to the existing (currently unused) `uv.lock` (SEC-F14/F20), pin `citinel-n8n`'s image tag off `:latest` (SEC-F15), add a minimal SBOM/vuln scan once `pip` is available in the venv (SEC-F25).
9. **Configure the external ledger witness on the live deployment** (SEC-F22) — the code path exists; it is simply not wired to real credentials in production yet.

---

## Contradictions & Disputes Found

- The audit's own severity label for SEC-F09 ("no deployment kill-switch, breaks_demo: false") slightly understates how much tonight's write-guard already narrows it: the *unauthenticated* denial-of-wallet path (SEC-F17) it partly describes is now closed; what remains open is only the "no kill-switch even for an authenticated/token-holding caller" residual, which is much lower severity in practice.
- One research pass's `refuted` list and its `caveats` text describe the same eight overreach claims in slightly different words but agree on substance in every case — no real contradiction, just two independent write-ups of the same verification round.

## What I Could NOT Verify (honest gaps)

- **Indian regulatory specifics for a vendor product** (CERT-In's vendor-vs-regulated-entity split, DPDP obligations specific to a SOC tool, RBI framework requirements) — not re-researched here because A6-compliance.md already covers this ground thoroughly from the Aug 2 pack; this report did not attempt to duplicate or update it.
- **AI-SOC competitive/analyst positioning** (Dropzone AI, Prophet Security, Radiant Security, Torq, Tines, Gartner/Forrester views on unmet needs) — same reasoning; A2-competition.md already covers this and was not re-researched.
- **Audit-log legal-admissibility standards in depth** (NIST SP 800-92, ISO 27001 Annex A.12.4, what specifically makes a hash-chained ledger legally defensible vs. merely tamper-evident) — the external research surfaced only OWASP's generic "signed, immutable logs for regulatory compliance" line; the deeper legal/technical comparison did not survive verification and remains open.
- **Certificate-transparency-style Merkle logs, third-party witness cosigning, threshold attestation, or RFC 3161 timestamping applied specifically to AI decision records** — zero confirmed findings; genuinely unresearched, not negative.
- **The single most consequential patent question** (does ALCE/FullCite/the ACL 2026 grounding survey already cover CITINEL's exact citation-verification mechanism as prior art) — could not be checked due to research-tooling failures; see PAT-F04.
- **A methodology note, for transparency:** the patent-research workflow's final automated synthesis step returned a broken placeholder ("Test call to verify schema") instead of real output on its last run, despite the underlying research completing correctly. The findings in Sections 5–6 above were recovered by hand from an earlier, genuine synthesis result still present in the workflow's raw execution log, cross-checked against the individually-verified claims in the same log. This is disclosed because a document claiming "adversarially verified" owes the same evidentiary honesty to its own production process that CITINEL's citation gate demands of the product.
