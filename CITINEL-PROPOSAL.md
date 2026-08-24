# CITINEL — The Full Proposal

### An Autonomous, Glass-Box AI Cyber SOC for India's Cooperative Banks and Small NBFCs

*Team AeroFyta (Chennai Institute of Technology) · Decode SIH 2026 · Track "Bharat Pragati" · PS4: Autonomous Cyber SOC for AI-powered threat detection and automated incident response*

*Tagline: **Caught. Cited. Gated. Actioned. Closed.*** *(brand hook, updated 24 Aug 2026 — see `HANDOFF-MEMORY.md` §4a; not yet propagated to the submitted deck or the locked badge PNGs)*

---

> **Read this first:** every factual claim in this document either (a) traces to a finding ID in CITINEL's own research corpus (`docs/A1-market-impact.md` … `A6-compliance.md`), or (b) survived a 3-vote adversarial verification pass against a real, cited external source, as documented in `CITINEL-SDD.md`. Nothing here describes software that has been built — CITINEL is fully specified and zero lines of code exist yet, by design, not delay. This document does not make promises about timelines; per the project's own governing rule, **Danish owns all timelines**.

---

## 1. Executive Summary

India's cooperative banks and small NBFCs sit in an unusual bind: they carry **exactly the same RBI and CERT-In security obligations** as any scheduled national bank — six-hour breach reporting, DPDP compliance, the same sophisticated attackers — while operating with a fraction of a national bank's security budget, staff, and tooling. Meanwhile the global cybersecurity workforce is short by roughly **790,000 people** (ISC2, 2023), a gap that lands hardest on exactly the institutions least able to compete for scarce analysts.

The tools that exist today don't fit this segment. Rules-only detection tools miss anything genuinely novel. Raw large-language-model "copilots" hallucinate and can't be safely left to act alone on a bank's own infrastructure. Enterprise SOC platforms assume enterprise budgets and enterprise headcount.

**CITINEL is built for what's actually true about this segment**, not a scaled-down enterprise product. It runs every incident through two decisions in order: first, a deterministic question — *have we seen this exact pattern before?* — answered instantly and explainably by 3,000+ Sigma rules and statistical scorers, closing most alerts before any AI model is ever invoked. Only genuinely novel cases reach a seven-agent Claude swarm that investigates the way a human analyst would: gather evidence, build a timeline, and write a verdict that **cites the exact log line proving it** — never a black-box confidence score alone. And nothing the agents decide executes unsupervised if it's consequential: a readable, per-action-class policy gate (OPA) decides what's allowed to run automatically and what needs a human's one-click approval.

The result is a SOC that is **honest about what it is** — it drafts, it never files; it mitigates, it never claims to solve; every autonomous action is reversible and bounded — while still being fast, cheap, and explainable enough that a small IT team at a cooperative bank could actually run it.

---

## 2. The Problem, In Detail

**2.1 — A regulatory burden with no matching budget.** Cooperative banks and small NBFCs are directly subject to RBI's cybersecurity directions and CERT-In's mandatory six-hour breach-reporting window — the same clock that applies to any scheduled commercial bank. There is no regulatory discount for being small. What's missing is not the obligation, it's the capacity to meet it: a dedicated 24×7 SOC, a security engineering team, and the tooling budget that comes with either.

**2.2 — A structural workforce shortage.** The global cybersecurity talent gap of roughly 790,000 people (ISC2, 2023) does not distribute evenly — it concentrates against exactly the employers who can't out-bid a bank, an MNC, or a government contract for scarce analyst talent. For a small cooperative bank's IT team, "hire more security staff" is frequently not an available option at any price.

**2.3 — The tooling gap is real, not just a budget gap.** Two categories of existing tool both fail this segment for different reasons:
- **Rules-only SIEM/detection tools** are fast, explainable, and cheap — but structurally blind to anything that doesn't match a known signature. A genuinely novel attack chain simply doesn't trip them.
- **Raw LLM-based "AI SOC copilot" tools** can reason over novel situations, but carry real, documented risk: they hallucinate, they can be manipulated by content embedded in the very logs they're meant to analyze (prompt injection), and unsupervised autonomous response actions from a model that "struggles to reliably distinguish malicious behavior from legitimate but unusual activity" (a direct 2026 finding from CITINEL's own architecture-hardening research, §16) are not something any serious bank should hand real infrastructure to.

Neither category is safe to deploy unsupervised at a small institution. That gap — not "AI for security" in the abstract — is what CITINEL is built to close.

**2.4 — Timing: a live, government-scale digitization wave.** This is not a speculative future market. The Government of India approved a **₹2,516 crore, five-year Centrally Sponsored Project (2022–23 to 2026–27)**, delivered as a single common NABARD-built ERP, to computerize **63,000 Primary Agricultural Credit Societies** — with **50,455 PACS already onboarded as of 27 January 2025** (Ministry of Cooperation, primary source; corroborated by Lok Sabha/PIB replies through early 2026). CITINEL's target segment is being connected to digital infrastructure at national scale, right now, by a government program — which means it is also being newly exposed, right now.

---

## 3. The Solution — Architecture, End to End

CITINEL's pipeline runs as seven stages, each with a specific, deliberate job:

**Stage 1 — Ingest.** Logs arrive via syslog, webhook, and lightweight forwarding agents (Fluent Bit) and normalize into one schema, OCSF. A new log source becomes a mapping exercise, not a rebuild — and because OCSF requires every event producer to declare a `metadata.version` field, CITINEL's normalization layer can branch its parsing logic per-source as different bank systems adopt schema updates at different paces, rather than assuming one pinned version everywhere (a concrete hardening finding from this session's architecture research, §16 finding 7).

**Stage 2 — Detect.** 3,000+ community Sigma rules plus statistical anomaly scorers run deterministically and close known-pattern threats immediately — before any language model is invoked at all. This is a cost and safety decision as much as a technical one: it keeps the expensive, harder-to-fully-verify agent layer reserved for genuinely novel cases, and it means most incidents are closed via fast, fully-explainable, deterministic logic. CITINEL's own hardening research benchmarked its bundled Sigma corpus against SigmaHQ's actual quality bar — a minimum of two independent human reviewers who validate detection logic and replicate the referenced attack before any rule merges, layered under three tiers of automated schema/convention validation — and recommends pinning to a specific vetted release rather than trusting upstream state blindly.

**Stage 3 — Investigate.** What the deterministic layer can't explain reaches a **seven-agent Claude swarm**: a **Sentinel** orchestrator, a **Triage Router** (strict structured routing), an **Enrichment Squad** (parallel threat-intel lookups — VirusTotal, AbuseIPDB, GeoIP, live Tavily search), a **Correlator** (extended-thinking kill-chain reconstruction against MITRE ATT&CK), a **Verdict Narrator** (citations-grounded — deliberately a separate agent role, because Anthropic's Citations capability and strict structured-JSON output are not compatible in a single model call), a **Response Marshal** (proposes actions, consults the policy gate, executes only against approved targets), and a **Scribe** (drafts compliance artifacts and handover notes). Every claim in the final verdict is cited to the exact source log line — an analyst can click through the entire chain of evidence, not just read a confidence percentage.

**Stage 4 — Decide.** Every action the Response Marshal proposes passes a readable, per-action-class **Open Policy Agent (OPA)** gate — the rule the agents must obey, not a rule they write for themselves. A tunable **Shadow / Assist / Autonomous dial** governs each action *class* independently: low-risk, fully reversible actions (like enrichment queries) run automatically; moderately consequential ones (like host isolation) run automatically but carry a **rollback token**; anything with real blast radius (like disabling a production account) waits for one-click human approval. **Blast-radius rings** cap how much any single automatic action can touch at once — a deliberate design response to real-world incidents (like the 2024 CrowdStrike outage) where automation moved too wide, too fast.

**Stage 5 — Act.** Reversible, low-risk actions execute immediately with a rollback token attached. Everything else waits.

**Stage 6 — Report.** On a confirmed incident, the Scribe agent auto-drafts the CERT-In six-hour report (an estimated 70–80% of fields machine-draftable from the live incident record) and the relevant DPDP breach artifacts (roughly 50–60% machine-draftable) — legal characterization, consequence assessment, and the final decision to file remain entirely human. **CITINEL drafts. It never files.**

**Stage 7 — Record.** Every decision and every tool call — not a model's own summary of its reasoning, but the actual evidence trail — writes to an **append-only audit log**, forming a complete, reconstructable chain from detection through sign-off.

**The safety plane, woven through all seven stages.** Log content is always treated as untrusted *data*, never as *instructions* — a quarantine plane, an injection detector, and a deterministic egress allow-list exist specifically because a malicious actor can embed prompt-injection payloads inside the very logs the system is meant to analyze. This session's own architecture-hardening research confirms this defense narrows but does not eliminate the injection surface — a crafted value inside an extracted field can still reach the model — so CITINEL frames it honestly as a **residual-risk reducer**, not a closed control, exactly consistent with the product's own "mitigates, never solves" rule.

---

## 4. Trust and Explainability, By Design

CITINEL's central bet is that **a SOC an analyst can't verify is a SOC an analyst won't trust with real autonomy** — so every design choice pushes toward verifiability over raw automation:

- **Glass-box, not black-box.** Every verdict cites the exact log line that proves it. This directly mirrors how leading SOC products (Microsoft Sentinel, Elastic Security) already keep raw evidence in-context via progressive disclosure — flyouts and side-panels, not a page navigation away from the investigation — a pattern this session's UI/UX research confirmed and CITINEL's glass-box replay design already follows.
- **Calibrated confidence, not a raw score.** Disclosing an AI system's own *calibrated* self-assessment — not just a raw probability — produced measured trust gains of 34–52% in controlled research, while simultaneously cutting both under-reliance (unnecessary human takeovers) and over-reliance (unchecked machine errors) — a rare double win. CITINEL's confidence panel is designed to be measured for calibration by its own evaluation harness, not just displayed as a number.
- **A dial with anti-complacency safeguards, not a switch.** Autonomous-vehicle research that validates user-adjustable trust dials also carries a sharp warning: raising the dial measurably *increases* risk, and rising user confidence over time erodes the safety margin a conservative default provides. CITINEL's takeaway from this isn't "add more dial levels" — it's that the dial itself needs guardrails against complacency (default decay, periodic re-justification of higher autonomy), so turning autonomy up never quietly means turning safeguards down.
- **A confirmation-bias check on the human sign-off step itself.** Research on human-AI reliance shows that when an AI's verdict happens to agree with an analyst's own incorrect initial hypothesis, under-reliance on the correct alternative jumps to 64.5% (versus a ~3.9% baseline) — human sign-off is not automatically a safety guarantee if the human and the model share the same blind spot. CITINEL's roadmap includes a nudge that surfaces disagreeing evidence specifically when an analyst's hypothesis matches the AI verdict exactly.
- **External, deterministic checks — not agent self-verification.** Research on self-improving agentic systems is explicit that self-generated feedback for self-correction carries real risk (self-deception, reward tampering) and that self-consistency checks can fail precisely when a model is confidently wrong. CITINEL's OPA gate and mandatory human sign-off are external and deterministic by design — not something the agents check on themselves.

---

## 5. Why This Wins — The Full UVP Catalogue

CITINEL's differentiation was validated across two dedicated research passes (33 total unique value propositions, each independently checked against real external sources). The strongest, organized by theme:

**Trust and safety architecture**
- Glass-box citation trust — every verdict traces to its evidence, not a confidence score alone.
- A rules-first, AI-second pipeline that cuts both cost and hallucination risk by restricting what ever reaches the model layer.
- A tunable autonomy dial with rollback tokens and blast-radius containment on every automated action — not an all-or-nothing switch.
- Multi-layer injection defense (quarantine, detection, egress allow-listing, human gate) — research confirms no single defense strategy is robust across all axes, so CITINEL's layered shape is structurally correct, not a placeholder for a future single fix.
- Roughly two-thirds of documented attacks against LLM agents are inherited or amplified from the base model itself — direct support for why CITINEL's injection-hardening has to be a separate defense layer, not something assumed from the underlying model's own alignment.

**Regulatory and buyer-economics moat**
- A regulator-endorsed enrichment path: RBI's own 30 June 2025 advisory already directs all cooperative banks to integrate DoT's Financial Fraud Risk Indicator — CITINEL can ingest it with essentially no adoption friction.
- CERT-In/DPDP-aware compliance drafting, framed with total honesty about what a services-authorization credential ("CERT-In empanelled") actually means — a category CITINEL deliberately never claims for itself as a product.
- Buyer-economics fit for a segment every competitor's tooling assumes away: cooperative banks and NBFCs carry regulator obligations without enterprise-SOC budgets.

**Anti-lock-in**
- Every generated Sigma rule and response playbook exports as an open, portable artifact — nothing proprietary holds a bank's own detections hostage.

**India-context distribution moat**
- The live, government-funded PACS computerization program (§2.4 above) is a real, falsifiable, currently-running national digitization rail CITINEL can integrate against or distribute through via NABARD/StCB/DCCB channels — not a vague "vernacular-first" claim.

**Technical differentiators from cutting-edge 2025–2026 research**
- Naive majority voting among LLM agents is empirically unstable and vulnerable to "confabulation consensus" — agents sharing the same bias and converging on the same wrong answer. CITINEL's roadmap treats verdict-consensus as a defensible technical UVP: a task-aware, audited aggregation mechanism (reasoning-tree auditing beats plain majority voting by up to ~5–5.7 percentage points in independent research) added as a bolt-on module via the Anti-Corruption-Layer pattern — not a rewrite of the core swarm.
- CITINEL's correction-memory flywheel (few-shot, explicitly *not* fine-tuning) is exactly the "scaffolding improvement" pattern current self-improving-agent research identifies as the faster, more reversible path to durable improvement — a design choice the research confirms as correct, not merely adequate.

---

## 6. Beyond the Core — The Innovation Backlog

Twenty-nine candidate features sit in CITINEL's backlog (none committed — every item awaits a roadmap decision). Highlights, organized by what they'd add:

**Sharper investigation.** Re-runnable evidence queries alongside every cited verdict (so an analyst can independently re-execute evidence in their own SIEM); a generate-then-validate investigation stage that separates hypothesis generation from structural-feasibility checking before any response executes; typed-tool evidence grounding with a "propose follow-up investigation questions" output field (a published multi-agent architecture using this exact pattern measurably raised actionable-alert F1 from 0.66 to 0.78 and cut false positives from 24.9% to 14.2% — though at a real latency cost worth weighing, 3.4× slower than a single-agent baseline).

**Deeper human-AI collaboration.** A counterfactual "what would change this verdict" panel; a persistent, per-analyst-tier autonomy model (junior analysts get human-in-the-loop assistance, senior analysts get more delegated authority — reusing the existing dial, not replacing it); structured agree/disagree/modify logging on every verdict, not just approve/deny on actions; each verdict's evidence packaged as a persistent, auditable "rationale artifact" with analyst-triggerable operational actions that write back into the audit log.

**Adjacent-domain transplants.** A Near-Miss Ledger (aviation-safety-inspired — a log of auto-remediated attempts that never escalated, easier to analyze because a control already succeeded); an auto-drafted blameless postmortem in the SRE tradition, distinct from the regulator-facing CERT-In/DPDP drafts; behavioral/device-identity graphs transplanted from fraud detection for insider-threat and account-takeover detection — already established, deployed practice in commercial SOC/UEBA tooling.

**India-specific.** Deepened Indic-language incident narratives; WhatsApp/SMS-native alert delivery for rural branch IT staff; offline/low-bandwidth branch sync for unreliable-connectivity sites.

**Community and network effects (weakest-evidenced angle — flagged honestly).** A CITINEL-operated, strictly opt-in threat-sharing portal across subscribing cooperative banks, modeled on FINRA's own March 2026 Financial Intelligence Fusion Center precedent — a real regulator-brokered opt-in model, though this is new infrastructure that doesn't exist today and several adjacent federated-learning ideas did not survive verification.

**A genuine research gap, disclosed rather than hidden:** gamification and analyst skill-building features (attack simulation, tabletop-exercise generation, training loops) remain unresearched — the dedicated research pass on this angle returned zero confirmed claims.

---

## 7. The Demo — Designed on Real Evidence, Not Instinct

CITINEL's Grand Finale demo design draws on dedicated research into judge psychology, live-security-contest craft, and pitch-day technique:

- **Bounded novelty.** Judges implicitly favor innovative moments — but only up to a point; excessive novelty reads as aversive because it violates expectations. The live poisoned-log attack-then-defense set piece is framed as a recognizable SOC ritual with one genuinely novel element inside it, not a maximalist spectacle.
- **The peak-end rule.** A short judged demo (3–10 minutes) is remembered almost entirely by its single most intense moment and by how it ends — not its average quality. CITINEL's structure engineers exactly one unmistakable peak (the live attack-then-defense moment) and a deliberately composed, confident closing beat.
- **Live, legible decision-making.** DEF CON's own 2026 contest formats confirm three concrete mechanics that make live technical action gripping to spectators: a persistent visual "damage state" indicator, on-screen real-time projection of decision-making, and a visible adversary element. CITINEL's demo plan gives the audience a live dashboard tile that visibly flips red as an injection lands and green as the swarm remediates and the policy gate blocks the bad action.
- **A rehearsed fallback, because "demo gods" risk is real.** Even top-tier security conferences have had live demos fail on stage. CITINEL's plan includes a byte-for-byte identical pre-recorded fallback, cued and ready to cut to within seconds.
- **Front-loaded concreteness.** Research on countering initial skepticism toward ambitious claims recommends getting to a real, running artifact fast rather than narrating the architecture abstractly first — CITINEL's script gets to the actual dashboard, the actual policy denial, the actual compliance draft within the opening minute.

**An honest, disclosed gap:** research into what specifically impresses corporate-sponsor judges evaluating integration depth (for Render, n8n, Tavily, and the other named partner tools) returned zero surviving claims — this angle is genuinely unanswered and should be sourced separately from sponsor rubrics, not assumed from general demo-psychology findings.

---

## 8. The Partner Ecosystem — Genuine Integrations, Not Decorative Logos

Every partner tool does a real job inside the pipeline described in §3 — the OPA policy gate remains the one authority no integration bypasses:

- **Anthropic Claude** — the seven-agent investigation swarm and its citations-grounded verdicts.
- **Open Policy Agent** — the policy gate every autonomous action must clear.
- **Sigma / SigmaHQ** — the deterministic detection corpus and portable rule-export format.
- **OCSF** — the normalization schema every ingested log conforms to.
- **Render** — hosting (web service + background worker + managed Postgres/Redis).
- **n8n** — escalation, notification, and report-export workflow glue (explicitly never the policy authority itself).
- **Tavily** — the Enrichment Squad's live OSINT search arm.
- **Swytchcode** — agent-to-API execution for response actions and communications.
- **Codemate.ai** — a build-time AI development aid, explicitly not a runtime component.
- **Lyzr AI** *(proposed addition — pending confirmation)* — a governance/observability control plane sitting above the swarm: fleet observability, a second independent hallucination/PII guard on the Verdict Narrator's output, and RBAC formalizing the existing Analyst/CISO view split. Designed as a genuinely low-coupling addition via the Anti-Corruption-Layer pattern — it does not require redesigning the core swarm or the OPA gate.

---

## 9. Built to Scale Honestly — Enterprise and Government Readiness

CITINEL's MVP explicitly excludes multi-tenancy, full MITRE ATT&CK coverage, and model fine-tuning — but dedicated research turned vague roadmap lines into concrete, credible paths:

**A real, non-redesign path to multi-tenancy.** Two independently viable patterns exist: AWS Bedrock AgentCore's "Pool Model" (namespace-based partitioning of a tenant:user identifier) and Google Cloud's reference architecture (a dedicated project per tenant plus an org-level access-boundary policy, with agents needing no custom authorization code because the platform enforces the boundary). Both push isolation to the **platform/IAM layer** — meaning a future multi-tenant CITINEL would not require rewriting the swarm's own reasoning logic. A confirmed identity pattern completes the picture: an "on-behalf-of" model (RFC 8693) issuing task-scoped tokens rather than long-lived credentials, with tenant-resource authorization enforced independently at the gateway layer rather than trusted from the agent's own claims.

**Certification sequencing, said honestly.** For Indian enterprise and government buyers specifically, **ISO 27001 dominates procurement requirements over SOC 2** — the more realistic first certification target if CITINEL is ever pursued past the hackathon stage. And a hard, non-negotiable framing rule: **CERT-In empanelment is a services authorization for firms performing security audits — not a product credential.** CITINEL evaluated the actual empanelment bar (proven assessment experience, qualified staff, existing testing infrastructure, firm-level track record) and confirms honestly that a pre-revenue, hackathon-stage team could not currently meet it. CITINEL will never claim to be, or be pursuing, "CERT-In empanelled" as a product.

**Government e-Marketplace (GeM).** Seller registration is genuinely open to startups — a real, findable path — but GeM is "registration is possible," not yet a proven distribution channel; that stronger framing was specifically checked and did not hold up.

---

## 10. Intellectual Property — An Honest Landscape, Not a Claim

*(This section is evidence-based legal/technical landscape information only. It is not legal advice, not a patentability opinion on CITINEL, and not a claim that CITINEL has, will get, or is likely to get a patent. Any real filing decision belongs to Danish and a registered Indian patent agent.)*

India's Section 3(k) does not blanket-ban software patents — the 2019 *Ferid Allani* precedent, reinforced by India's 2025 Computer Related Inventions Guidelines, makes clear that a claim reciting a specific technical mechanism producing a measurable technical effect can be patentable, while a bare "use LLM agents for security" claim cannot. CITINEL's two flagship architectural bets are honestly not blank-slate territory: a pending (unexamined) 2025 US filing already claims a specific multi-agent communication protocol, and an August 2026 arXiv preprint (automotive-cybersecurity domain) already implements both a deterministic-filter-then-LLM pipeline and a mandatory pre-action policy gate — structurally close analogues to CITINEL's own design. Real patentability, if pursued, would have to rest on CITINEL's own specific implementation details — not the general architectural pattern, which is becoming an established genre in security-agent research. **Defensive publication** — deliberately forgoing exclusive rights in exchange for disclosure that blocks competitors from later patenting the same thing — is a credible, low-cost complementary strategy for whichever parts of the design the team wants to keep open rather than exclusively owned. This is a genuinely open decision for Danish, not a foregone conclusion either way.

---

## 11. What's Honestly Not Built, and Why That's the Right Call

CITINEL is fully specified and zero lines of code exist. That is a deliberate hackathon-stage choice: independent industry research (Gartner's 2025 Hype Cycle places autonomous AI-SOC agents at 1–5% production adoption — "pilot purgatory," with real deployments confined to low-risk tasks and humans retaining decision authority) confirms that CITINEL's conservative, human-gated default is the *correct* engineering posture right now, not a hackathon shortcut to be relaxed the moment it's convenient. Two research angles remain genuinely open rather than closed (gamification features; community/network-effect features), and CITINEL says so rather than papering over the gap. The accessibility question — whether the locked red-severity/gold-citation color pairing is colorblind-safe — is also flagged as unresearched, not assumed safe.

---

## 12. The Ask

CITINEL is ready for the next phase: engineering scaffolding (`backend/`, `dashboard/`, `policies/`, `connectors/`), version control initialization, and a build-phase go/no-go on the twenty-nine backlog features and the patentability question above. All of it is Danish's call. This document, and its companion technical spec (`CITINEL-SDD.md`), exist so that call can be made with full information — nothing more, nothing less.

---

*Prepared 21 August 2026, synthesized from eleven adversarially-verified deep-research passes and a full audit of the CITINEL repository. Full citations, confidence tags, and refuted-claim disclosures for every statement above live in `CITINEL-SDD.md`.*
