# CITINEL: Autonomous Cyber SOC
## Decode SIH 2026 · Track 3 "Bharat Pragati" · PS4
### Complete Idea-Architecture Record: Phase 0 Intake Audit → Phase 4 Locked Idea Spec

Compiled 2 August 2026. Round 1 idea submission due 11 August 2026.

Evidence base: A1 (market/domain, prefix A1), A2 (competition/white-space, prefix LAND), A3 (technical feasibility, prefixes AGT/PIPE/SAFE/DEMO/ARCH), A4 (winning-idea intelligence, prefix WIN), A5 (analyst UX, prefix UX), A6 (compliance, prefix COMP), plus human recon H1 (official PS wording + Decode SIH template). Every claim cites finding IDs or is labeled [NEW-INFERENCE]. Cross-report conflicts live in the Contradiction Ledger. Unverifiable items live in the Research Gap List. Phases appear in the order they were executed.

---

# PHASE 0 · INTAKE AUDIT

No H1.md was attached at audit time, so no human-recon overrides applied in Phases 0-2. [Superseded mid-engagement: H1 arrived before Phase 3. See H1 RECON INTAKE below Phase 2.]

## ID map (aliases, applied silently)
Reports use their own prefixes, not A{n}-Fxx. Declared equivalences, cited as-is throughout for traceability to the originals:

| File | Report | Native prefix(es) | Alias |
|---|---|---|---|
| 1.md | A1 Market/Domain | A1-Fxx | native, no repair |
| 2.md | A2 Competition/White-space | LAND-Fxx | A2 ≡ LAND |
| 3.md | A3 Technical Feasibility | AGT / PIPE / SAFE / DEMO / ARCH-Fxx | A3 ≡ all five |
| 4.md | A4 Winning-Idea Intel | WIN-Fxx | A4 ≡ WIN |
| 5.md | A5 Analyst UX | UX-Fxx | A5 ≡ UX |
| 6.md | A6 Compliance | COMP-Fxx | A6 ≡ COMP |

## Verdicts

**A1: REPAIRED.** IDs atomic-ish (some compound: F10, F17 bundle stats, cite with sub-clause context), confidence tags present, Could-Not-Verify present, Numbers Bank present. Repair: sources are publisher-domain + date, not full URLs. Ruling: domain+publisher+date = traceable, so existing confidence tags stand, EXCEPT the report's own 1-SRC/vendor-aggregated flags (F01 upper bound, F04, F11, F33/F34, F36, F37, F57) which stay Low-Med and cannot alone justify any 9+ score. Full URLs for every deck-cited stat added to gap list.

**A2: PASS.** Full-URL Numbers Bank, confidence tags, contradictions, gaps all present. Note: white-space section 5(a)-(j) territories inherit IDs from body findings, acceptable. Absence-of-evidence findings (F37 Indic gap; §5(a) "nearest incumbent: none") are correctly self-flagged; they cap at Med alone.

**A3: REPAIRED.** Contract elements present. Two repairs: (1) mixed link quality in the bank (some truncated paths), treated as traceable with pre-deck URL verification flagged; (2) its "gaps now partially closed" note claiming ISC2 2025 "indicates ~3M" [1-SRC] directly contradicts A1's primary-source verification that ISC2 2025 published NO numeric gap. That A3 claim is DOWNGRADED to Low and logged in the ledger (entry L1). Everything else in A3 is unusually well-sourced (primary Anthropic docs, CERT-In PDF, CC0/MIT licenses verified).

**A4: PASS.** Clean IDs, bank with links, honest [INFERENCE] labeling (F25, §4 phrasings), internal contradictions pre-resolved (F21 prototype tension). WIN-F22 rubric weights correctly flagged nodal-specific [1-SRC], so weights inform emphasis, never a 9+ justification alone.

**A5: PASS.** Cleanest report of the six: full URLs, peer-reviewed anchors (UX-F20/F21/F23/F33/F43/F44), explicit NOT-FOUND list. Compound IDs (UX-F45) cited with sub-clause context.

**A6: PASS.** Primary-source discipline strongest of all (CERT-In PDFs verbatim). Minor: sub-IDs (F09a, F13a, F17a, F20a) are non-standard but unambiguous. COMP-F20 (no tool auto-drafts India forms) is Med, absence-based: it becomes 9+-eligible ONLY because A2 §5(a) independently reached the same absence conclusion; joint re-verification before 11 Aug is on the gap list since A6 itself names vendor shipment as the recommendation-breaking event.

**No report is DEGRADED. No regeneration needed.**

---

# PHASE 1 · SYNTHESIS

## 10 strongest constraints

**C-01. The bare concept is not novel, and judges will know it.** Agentic SOC is a named Gartner category with five majors and 15+ funded startups; a hostile judge names Microsoft Copilot, Charlotte AI, XSIAM, Google SecOps, Dropzone in 30 seconds [LAND-F01..F13, WIN-F30]. Novelty must come from India-specific, unclaimed clauses, never from "we built an agentic SOC."

**C-02. Even the student-tier version has prior art.** "Wazuh + local LLM triage + ATT&CK mapping" already exists as public GitHub projects [LAND-F14]. The build must materially exceed the hobbyist pattern: policy engine, compliance artifacts, injection hardening, Indic UX, or it is derivative twice over.

**C-03. Full autonomy is a trap: distrusted, unshipped, and legally untenable.** Only 11% of leaders accept unreviewed autonomous action [UX-F16]; OWASP and four named vendors mandate human approval for consequential actions [SAFE-F01, SAFE-F05]; report-filing liability sits with the filer and CERT-In has no machine-submission channel [COMP-F21, COMP-F22, COMP-F23]. Any "fully autonomous" claim self-destructs under attack (a).

**C-04. Our own architecture has a peer-published attack against it.** Prompt injection via attacker-controlled log content defeats LLM log analysis and can trigger unintended actions [LAND-F23]; it is OWASP LLM01 two editions running [SAFE-F01, LAND-F24]. Ignoring it hands judges question Q6/Q7 [A4 §4] as a kill shot.

**C-05. The 3-week, ₹0 scope wall is hard.** Multi-tenancy and honeypot subsystems are documented over-scope [ARCH-F05, ARCH-F03]; free-tier caps force caching/dedup design (VirusTotal 4/min, 500/day; AbuseIPDB 1,000/day) [PIPE-F04, PIPE-F05]; multi-agent burns ~15x chat tokens so agents must be spent only where breadth pays [AGT-F11].

**C-06. The idea round is format-gated and volume-capped.** 6-slide template, PDF only, originality demanded; AI-boilerplate is a documented negative; 500 ideas per PS then freeze [WIN-F05, WIN-F04, WIN-F09]. Decode SIH's exact template is unverified (gap list): assume SIH-mirroring until confirmed. [Superseded by H1-F02: Decode uses an 8-slide template. See H1 RECON INTAKE and ledger L11.]

**C-07. PS-drift is the #1 documented rejection cause, and we hold only the PS title line.** Every clause (threat detection AND automated incident response AND autonomy) must be addressed with zero drift [WIN-F02]. Full official PS4 wording: gap list, mandatory pre-submission. [Closed by H1-F01.]

**C-08. Claude engineering realities shape the architecture.** Citations and strict structured outputs are incompatible in one call, so cited-narrative agents and JSON agents must be separate roles [AGT-F08]; extended-thinking summaries are NOT forensic audit trails, so decisions and tool calls must be logged separately as the audit record [AGT-F06, SAFE-F06].

**C-09. Regulatory timing needs honest framing.** DPDP breach duties become fully enforceable ~13 May 2027 [A1-F39, COMP-F17a] and CERT-In monetary enforcement has no published cases [COMP-F24]. "Why now" must be pitched as a compliance runway closing, not as current-day DPDP enforcement, or attack (c) lands.

**C-10. Judges demand numbers no one has published.** FP rates, accuracy, failure-mode handling are standard grill topics [A4 §4 Q4-Q6, WIN-F29], but no cost-per-report [COMP-F31] or LLM cost-per-alert [A1-F58] benchmark exists. We must instrument our own baselines and label them [INFERENCE], which is defensible but must be pre-built into the idea doc.

## 10 strongest opportunities

**O-01. India compliance auto-drafting is verified open white-space.** No tool auto-populates CERT-In or DPDP forms from incident data [COMP-F20, COMP-F13]; ~70-80% of CERT-In fields and ~50-60% of DPDP content are machine-draftable from a resolved incident record [COMP-F18, COMP-F19]; a single breach triggers 3+ filings on different clocks across 7 regulators, which is a normalization-engine play [COMP-F17, COMP-F30].

**O-02. A national regulator literally defined our product gap.** SEBI CSCRF mandates a SOC for every RE and orders NSE/BSE to build shared Market SOCs because smaller REs cannot afford their own [A1-F41, A1-F42]. This is the strongest third-party validation any team in the PS4 pool can cite.

**O-03. A named persona with a fresh disaster story.** Cooperative banks/small NBFCs rank #1 (19/20) [A1-F45]; C-Edge/RansomEXX forced ~300 of them offline in 2024 [A1-F26]; RBI legally requires the 24×7 C-SOC they cannot afford (₹1-2 cr/yr payroll vs ₹25k-₹1L/month budgets) [A1-F43, A1-F29, A1-F31, A1-F33].

**O-04. Prompt-injection-hardened log analysis is a live attack-plus-defense demo in nearly unclaimed territory.** The attack is peer-published [LAND-F23], only Simbian claims a defense [LAND-F10], and concrete mitigations are implementable at student scale [LAND-F24, SAFE-F02, SAFE-F03]. Highest single technical-wow element available.

**O-05. A readable, per-action-class policy dial converts the danger objection into the demo.** OPA/Cedar policy-as-code gates [SAFE-F03], Shadow→Assist→Autonomous rollout [SAFE-F04], blast-radius rings justified by the CrowdStrike 8.5M-device lesson every judge remembers [SAFE-F07], mirroring the approval-gate pattern leaders converged on [UX-F27, UX-F28, LAND §5(d)].

**O-06. Evidence-first cited triage is simultaneously Claude's genuine edge and the peer-reviewed trust winner.** Citations API grounds every verdict in the exact log line [AGT-F07]; analysts accept AI verdicts even at lower accuracy when evidence-backed [UX-F20]; 90% of leaders call explainability critical [UX-F18]; the glass-box replay is the signature UX moment [A5 Feature A].

**O-07. Portable open Sigma + playbook flywheel is the anti-lock-in differentiator.** Incumbents emit vendor-locked artifacts (YARA-L, XSIAM playbooks) [LAND-F04, LAND-F03]; open portable output has community-flywheel precedent [A1-F53, PIPE-F07, PIPE-F10] and incumbents have anti-incentives to copy it [A2 §5(e)].

**O-08. Indic-language SOC experience is empty white-space.** No vendor offers it [LAND-F37]; qualitative India evidence supports the need [UX-F40]; it pairs naturally with DPDP's plain-language data-principal notices at no materiality threshold [COMP-F09] and is cheap to demo with Claude.

**O-09. The impact arsenal is India-record-grade and multi-sourced.** ₹220M average breach cost, record high [A1-F10, COMP-F15]; ₹22,845.73 crore citizen fraud losses, +206% YoY [A1-F17, UX-F45]; $2.2M average AI/automation savings per breach [WIN-F28b]; 73% of Indian orgs under-use automation [COMP-F15]; 6-hour clocks across CERT-In/RBI/SEBI/IRDAI [COMP-F30, SAFE-F09].

**O-10. The feasibility-plus-sustainability proof-chain is unusually complete.** Orchestrator-worker maps 1:1 to SOC roles [AGT-F01]; CC0/MIT kill-chain demo assets exist [DEMO-F01..F04]; OCSF+Sigma+free-tier intel pipeline verified [PIPE-F01..F08]; ~5¢/incident economics [ARCH-F07]; open-core survival precedents plus C3iHub ₹30L and Cyber Surakshit Bharat runway [A1-F51, A1-F52, A1-F55, A1-F56]; and SIH student prior art is shallow ML/forensics [LAND-F26].

## CONTRADICTION LEDGER v1

| # | Contradiction | Sources | Trust call and why |
|---|---|---|---|
| L1 | India talent gap: "3M needed / <200K trained" vs ISC2 2025 publishing no numeric gap vs official 790K (2023) | A1-F11 vs A3 gap-note vs WIN-F31, UX-F37 | TRUST WIN-F31 (790,000, ISC2 2023, primary, last official India figure). Present "~1M-3M" only as a hedged secondary range. A3's ISC2-2025 claim downgraded to Low: it contradicts A1's direct primary check. |
| L2 | India incident counts conflated across denominators: CERT-In incidents (15.93L 2023; 29.44L handled 2025) vs NCRP complaints (22.68L 2024) vs PIB mislabeling complaints as "cybersecurity incidents" | LAND-F39 vs COMP-F16 vs A1-F14/F16, UX-F45 | TRUST A2's disaggregation (LAND-F39). Rule for all downstream phases: label every count by denominator, never merge. A6's exec bullet repeating the PIB phrasing inherits this correction. |
| L3 | False-positive rate: ~46% vs >50-80% vs 25-27% of analyst time | A1-F03 vs WIN-F29, UX-F19 vs UX-F14 | Not a true conflict (different metrics/populations). Rule: cite only as ranges, per A4's own resolution. World-class target <10% [WIN-F29] usable as our stated goalpost. |
| L4 | Alerts/day: ~960 (Low, 1-SRC) vs 3,832 peer-reviewed with 62% ignored | A1-F04 vs UX-F07, UX-F08 | TRUST UX-F08's peer-reviewed 3,832/62% for enterprise-scale claims; use 960 only as "average org" with its Low flag. India-specific per-analyst figure NOT FOUND [UX-F08]: never fabricate one. |
| L5 | Autonomy claims: Torq "95% Tier-1 without humans" vs Dropzone "fully autonomous SOC not yet real" | LAND-F09 vs LAND-F06 | Both vendor marketing. TRUST the convergent behavior, not the claims: everyone gates consequential actions [SAFE-F05]. Design implication: bounded autonomy is the only defensible frame. |
| L6 | India MSSP/security market size disagrees ~10x | A1-F37; LAND-F13; A3 gap-note (MarketsandMarkets) | TRUST no single number. Cite direction only (double-digit CAGR, compliance-driven). Any TAM slide states the range and scope ambiguity explicitly. |
| L7 | RBI reporting window 2-6 hr (2016) vs 6 hr (2024 MDs) | COMP-F25 | Not a conflict: tightened over time. Cite "6 hours under the Apr 2024 Master Directions." |
| L8 | CERT-In "CIMS portal" referenced by blogs vs primary docs showing email/phone/fax only | COMP-F14, COMP-F22 | TRUST primary absence (email/phone/fax + non-mandatory PDF). Design stays draft-plus-manual-export. Verify pre-submission (gap list). |
| L9 | Claude model naming/pricing drift across trackers | A3 contradictions section | TRUST tier structure only ($1/$5, $3/$15, $5/$25 per M) for economics; verify live model names before the deck. |
| L10 | Prototype necessity at idea stage: "critical error to omit" vs "won without one" | WIN-F21 | Pre-resolved by A4: credible feasibility evidence (mockup/test case/video) is required in practice; a full build is not. Locked idea must ship a demo artifact plan. |

**RESEARCH GAP LIST v1 (manual verification before 11 Aug):** (1) full official Decode SIH Track 3 PS4 wording, every clause [C-07]; (2) Decode SIH Round-1 template/format vs SIH's 6-slide standard [C-06]; (3) fresh check that no vendor shipped CERT-In/DPDP form auto-population, A6's stated recommendation-breaker [COMP-F20]; (4) CIMS portal existence [L8]; (5) live Anthropic model names/pricing [L9]; (6) full URLs for every deck-cited A1 stat [Phase 0 repair]; (7) CERT-In official 2024 annual total [A1 gaps]; (8) Tavily/n8n/Render free-tier quotas [A3 gaps]; (9) I4C current budget if cited [A1-F57]; (10) our own instrumented cost-per-incident and cost-per-report baselines, presented as [INFERENCE] [A1-F58, COMP-F31].

**PHASE 1 COMPLETE.**

---
# PHASE 2 · CONCEPT TOURNAMENT

Eight genuinely distinct concepts: different primary users, autonomy levels, and white-space angles [A2 §5]. Scoring ceiling this phase = 8 (9+ requires surviving a Phase-3 persona attack, per calibration rule). Criteria: NOV novelty, TCX technical complexity, CLR clarity, FEA feasibility, SUS sustainability, IMP scale of impact, UX user experience, FUT future-work, BIZ business potential.

## The concepts

**C1 · CLOCKWORK SOC (compliance-clock-first)**
Pitch: The SOC whose entire purpose is beating India's reporting clocks: detection feeds a resolved-incident record that auto-drafts CERT-In 6-hour, DPDP 72-hour, and sector filings from one normalized incident, human approves, one-click export. User: DPO/CISO of SEBI-regulated small entities and any CERT-In-covered body [A1-F41, A1-F45 #3, COMP-F02]. Autonomy: draft-only, human files. White-space: (a)+(f) [A2 §5]. Core innovation: multi-regulator normalization engine over an open gap [COMP-F20, COMP-F17]. Swarm: Haiku router → Annexure-I classifier (structured outputs) [AGT-F08, COMP-F04] → timeline/evidence agent (citations) [AGT-F07] → per-regulator drafters → human gate. Differentiation: "Unlike every SOAR/GRC tool, we populate the actual Indian forms from live incident data" [COMP-F13, COMP-F20]. Self-declared weakness: thin detection/response core risks WIN-F02 drift, "GRC tool wearing a SOC costume."

**C2 · GUARDIAN DIAL (guarded-autonomy tiered response + compliance skin)**
Pitch: A multi-agent SOC where every verdict cites its evidence, every response action passes a READABLE per-action-class policy, and autonomy is a dial (Shadow→Assist→Autonomous) with blast-radius rings, wearing a CERT-In/DPDP compliance skin. User: IT head of cooperative banks/small NBFCs [A1-F45 #1, A1-F26, A1-F43]. Autonomy: graded per action class. White-space: (d)+(a)+(h)+(e) combined [A2 §5]. Core innovation: the readable, auditable policy dial plus India compliance plus injection hardening plus portable Sigma output as ONE system [A2 §6 lines 1-4]. Swarm: orchestrator [AGT-F01] + triage router [AGT-F03] + parallel enrichment [AGT-F04, PIPE-F04..F06] + correlation with extended thinking [AGT-F06] + ATT&CK classifier [PIPE-F08] + OPA-gated response [SAFE-F03] + playbook/knowledge agent [PIPE-F10] + compliance drafter [COMP-F18]. Differentiation: "Unlike CrowdStrike's black-box bounded autonomy, our autonomy is a policy you can read, audit, and roll back" [LAND-F02, A2 §6.3]. Weakness: novelty is combinatorial, no single element is unique; "bounded autonomy" is contested territory [LAND-F02/F09].

**C3 · POISONPROOF (adversarially-hardened SOC)**
Pitch: The first student SOC whose spine is defense of its own AI: quarantined data plane, injection detectors, dual-model cross-examination, canary tripwires, proven live by a poisoned log hijacking a naive agent and failing against ours. User: MSSPs and AI-SOC builders [A1-F47]. Autonomy: assist-level. White-space: (h) [A2 §5]. Core innovation: injection-hardened log analysis, claimed by only Simbian [LAND-F10, LAND-F23]. Swarm: C2 core plus sanitizer/quarantine agent, detector layer [LAND-F24], cross-examiner, tripwire monitor [SAFE-F02]. Differentiation: "The only SOC that demos the attack against itself and survives it" [LAND-F23]. Weakness: a feature posing as a product; unclear standalone buyer.

**C4 · BHASHA SOC (Indic-first SOC-in-a-box)**
Pitch: A SOC that speaks the operator's language: Hindi/Tamil investigation narratives, voice readout, plain-language DPDP data-principal notices, priced for MSMEs. User: MSME owner/operator, tier-2/3 [LAND-F34, A1 §4 #4]. Autonomy: assist. White-space: (c)+(b) [A2 §5]. Core innovation: Indic SOC UX, verified empty space [LAND-F37, UX-F40] plus no-threshold DPDP notices [COMP-F09]. Swarm: triage + Indic narrative agent + notice generator + voice layer [AGT-F07 for grounding]. Differentiation: "No global vendor speaks to the people actually running Indian MSME IT" [LAND-F37]. Weakness: the language layer is thin engineering; capability tier contested by AirMDR/Simbian [A2 §5(b)]; "translation wrapper" dismissal risk.

**C5 · M-SOC ENGINE (multi-tenant Market-SOC/MSSP engine)**
Pitch: The autonomous engine INSIDE SEBI's mandated Market SOC and MSSPs: one multi-tenant deployment triages for hundreds of small REs and cooperative banks at ₹-per-device economics. User: NSE/BSE M-SOC operators and MSSP platform leads [A1-F42, A1-F47]. Autonomy: graded, operator-configured per tenant. White-space: (b) via channel + (f) [A2 §5]. Core innovation: B2B2X positioning where a regulator manufactured the buyer [A1-F42]. Swarm: C2 core × tenant isolation, per-tenant policy store, fleet dashboard. Differentiation: "We don't sell to 1,500 banks, we power the one SOC SEBI told the exchanges to build" [A1-F42]. Weakness: multi-tenancy is documented 3-week over-scope [ARCH-F05].

**C6 · DECOY-TRUST (deception-integrated agentic SOC)**
Pitch: Agents that plant and adapt decoys from triage findings, then treat decoy interaction as ground truth: high-trust signals that side-step prompt injection entirely. User: mid-size enterprises/MSSPs. Autonomy: assist-to-auto on decoy-confirmed incidents. White-space: (g) [A2 §5]. Core innovation: dynamic deception as the trust anchor for autonomy [LAND-F38]. Swarm: decoy-manager agent + high-trust signal path + C2 triage core [ARCH-F03]. Differentiation: "When the decoy fires, there's no ambiguity to inject into" [A2 §5(g)]. Weakness: a second system to build; prior-art precision ~75% [ARCH-F03]; over-scope.

**C7 · AIRGAP SENTINEL (sovereign SOC for govt/CII)**
Pitch: An autonomous SOC deployable inside air-gapped Indian government and CII networks with a pluggable local model, where Copilot cannot go. User: PSU/CII security owners under NCIIPC [COMP-F29, WIN-F14]. Autonomy: conservative, on-prem policy. White-space: (j) [A2 §5, LAND-F01b]. Core innovation: sovereignty-constrained deployment as the moat. Swarm: C2 core behind a model-adapter (Claude ↔ local), offline intel mirror. Differentiation: "Microsoft isn't even in Indian government clouds; we are built for the rooms Copilot can't enter" [LAND-F01b]. Weakness: local-model triage quality unprovable in 3 weeks; tension with the Claude-core edge [A2 §5(j)]; government-as-sole-customer is the winners' documented anti-pattern [WIN-F18].

**C8 · NIGHT-WATCH (autonomous night shift for Indian MSSP delivery)**
Pitch: The AI that works the 2 a.m. window in Indian delivery centers: investigates every alert overnight, executes only pre-approved routine actions, and hands over at dawn with evidence-first cards that preserve hypothesis, evidence, and time-sensitivity. User: SOC shift managers at TCS/Wipro-type MSSPs [UX-F35, UX-F36]. Autonomy: on-the-loop overnight for routine, morning approval queue for the rest. White-space: handover science, thinly engaged by anyone [UX-F32, UX-F33]. Swarm: triage + investigation + handover-card generator + approval queue [AGT-F01, UX-F32]. Differentiation: "Hands over like your best analyst, not like a log dump" [UX-F32]. Weakness: autonomous Tier-1 is exactly Dropzone/Prophet's pitch [LAND-F06, LAND-F07]; packaging novelty, not technical novelty.

## Tournament table (Phase-2 ceiling: 8)

| # | Concept | NOV | TCX | CLR | FEA | SUS | IMP | UX | FUT | BIZ | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C2 | Guardian Dial | 7 | 8 | 7 | 7 | 7 | 8 | 8 | 8 | 7 | **67** |
| C1 | Clockwork SOC | 8 | 5 | 8 | 8 | 6 | 7 | 7 | 6 | 8 | **63** |
| C5 | M-SOC Engine | 7 | 7 | 6 | 4 | 7 | 8 | 5 | 7 | 8 | 59 |
| C8 | Night-Watch | 5 | 6 | 8 | 7 | 6 | 7 | 8 | 6 | 6 | 59 |
| C4 | Bhasha SOC | 6 | 4 | 8 | 8 | 5 | 7 | 8 | 6 | 6 | 58 |
| C3 | PoisonProof | 8 | 8 | 6 | 7 | 5 | 5 | 5 | 7 | 4 | 55 |
| C7 | Airgap Sentinel | 7 | 7 | 6 | 4 | 6 | 7 | 5 | 7 | 5 | 54 |
| C6 | Decoy-Trust | 7 | 8 | 5 | 3 | 5 | 6 | 6 | 7 | 5 | 52 |

Spread check: table spans 3-8, no collapse.

## Score justifications (per concept, per criterion)

**C2:** NOV 7: combination of four thinly-claimed territories [A2 §5(d)(a)(h)(e)] but bounded autonomy itself is contested [LAND-F02/F09]. TCX 8: OCSF+Sigma+orchestrator-worker+OPA+hardening+citations is the deepest feasible stack [PIPE-F01/F07, AGT-F01/F07, SAFE-F02/F03]. CLR 7: the dial metaphor carries it [SAFE-F04] but more parts than C1. FEA 7: "3 weeks, tight, medium risk" with a documented fallback [ARCH-F02, A3 thresholds]. SUS 7: open standards + portable artifacts + open-core precedent [PIPE-F01, A2 §5(e), A1-F51/F52]. IMP 8: hits breach cost, alert fatigue, and compliance at once [A1-F10, A1-F02, COMP-F15]. UX 8: all three of A5's judge-winning moments live here [A5 Features A/B/C, UX-F18/F20/F27]. FUT 8: deception, multi-tenancy, domain-agnostic engine staged as roadmap [ARCH-F03/F05, A2 §5(f)]. BIZ 7: WTP band + MSSP channel evidenced [A1-F33/F46/F47] but SMB motion unproven.

**C1:** NOV 8: verified open gap, no vendor auto-populates Indian forms [COMP-F20, COMP-F13, A2 §5(a)]. TCX 5: A2 itself calls it "a RAG + template task Claude does well" [A2 §5(a)]; thin detection core. CLR 8: "files your CERT-In report inside 6 hours" is instant [A5 Feature C]. FEA 8: 70-80%/50-60% field mapping, medium effort [COMP-F18/F19, ARCH-F04]. SUS 6: regulator-format drift maintenance; weak flywheel [A1-F53 unengaged]. IMP 7: every CERT-In-covered org [COMP-F02] but touches reporting burden, not breach prevention. UX 7: one killer moment [A5 Feature C], daily triage relief underserved [UX-F01]. FUT 6: regulator connectors [COMP-F30], ceiling is "GRC suite." BIZ 8: compliance automation is a paid category with unserved India specificity [COMP-F20a, A6 §6.4].

**C5:** NOV 7: positioning novelty via regulator-manufactured buyer [A1-F42], tech novelty modest. TCX 7: multi-tenancy is hard ops, not interesting AI. CLR 6: needs CSCRF+M-SOC+B2B2X explained in 30 seconds [A1-F41/F42]. FEA 4: HIGH effort, HIGH risk, documented over-scope [ARCH-F05]. SUS 7: mandate-driven demand endures [A1-F41]. IMP 8: one deployment shields hundreds of REs [A1-F42], the C-Edge blast radius inverted [A1-F26]. UX 5: operator console dilutes analyst UX [A5 features secondary]. FUT 7: regulator-by-regulator expansion [COMP-F30]. BIZ 8: strongest WTP logic in the field [A1-F42/F47, WIN-F22].

**C8:** NOV 5: Dropzone/Prophet's exact autonomous-Tier-1 pitch [LAND-F06/F07]; handover cards fresh but thin [UX-F32/F33]. TCX 6: C2-subset plus bounded card generation. CLR 8: lands instantly with delivery-center judges [UX-F35/F36]. FEA 7: buildable subset. SUS 6: attrition ROI durable [UX-F12/F13], no artifact flywheel. IMP 7: delivery-hub scale real [UX-F35], relief incremental. UX 8: attacks a documented failure mode [UX-F32/F33] plus burnout [UX-F12]. FUT 6: roadmap is "become C2." BIZ 6: sells into the exact segment three funded startups court [LAND-F06/F07/F13].

**C4:** NOV 6: empty space [LAND-F37] but thin as a spine; box contested [A2 §5(b)]. TCX 4: Claude does Indic natively, little engineering added [A2 §5(c)]. CLR 8: instantly clear. FEA 8: low risk. SUS 5: language upkeep, no flywheel. IMP 7: 74%/13% MSME gap [LAND-F34] + no-threshold notices [COMP-F09], shallow protection depth caps it. UX 8: serves the truly underserved operator [UX-F40, A5 P10]. FUT 6: incremental (more languages, voice, WhatsApp). BIZ 6: WTP exists [A1-F33] but MSME direct is the documented hard road [A1-F47].

**C3:** NOV 8: nearly unclaimed, one competitor [LAND-F10], attack peer-published [LAND-F23]. TCX 8: detectors, cross-examination, quarantine, open research frontier [LAND-F24/F25, SAFE-F02]. CLR 6: explaining injection to a mixed jury costs time. FEA 7: demoable [A2 §5(h)] but rigor claims must stay modest [LAND-F25]. SUS 5: arms race, no flywheel. IMP 5: second-order impact (protects the AI SOC, not the org); India numbers attach loosely. UX 5: invisible when working [A5 principles unengaged]. FUT 7: benchmark gap is publishable [LAND-F25]. BIZ 4: hardening is a bundled feature, not a standalone purchase [LAND-F10].

**C7:** NOV 7: unclaimed by platforms [A2 §5(j), LAND-F01b]. TCX 7: adapter layer real, but quality unproven. CLR 6: dual-model story complicates "sovereign SOC." FEA 4: local-model triage quality unverifiable in 3 weeks [A2 §5(j)]. SUS 6: sovereignty narrative durable, model upkeep heavy. IMP 7: CII/PSU resonance [COMP-F29, WIN-F14]. UX 5: constrained surface. FUT 7: defence/CII runway, slow. BIZ 5: government-sole-customer anti-pattern [WIN-F18], long cycles [A1 §4].

**C6:** NOV 7: thin-claimed [A2 §5(g)], Smokescreen partial prior art [LAND-F38]. TCX 8: two integrated systems. CLR 5: heaviest explanation load. FEA 3: HIGH/HIGH, ~75% precision prior art [ARCH-F03]. SUS 5: decoy-realism arms race. IMP 6: enterprise-tilted. UX 6: high-confidence alerts cut noise [A2 §5(g)]. FUT 7: rich research runway. BIZ 5: niche budget line; ~$11.7M exit ceiling signal [LAND-F38].

## Eliminations

Killed, one line each: **C6** dies on FEA 3, documented over-scope with weak prior-art precision [ARCH-F03]. **C7** dies on FEA 4 plus the WIN-F18 government-sole-customer anti-pattern. **C3** dies on BIZ 4, a feature without a standalone buyer [LAND-F10]; its hardening module survives as a component of the finalists. **C4** dies on TCX 4, insufficient technical substance for the complexity criterion [A2 §5(c)]; its Indic layer survives as a feature. **C8** dies on NOV 5, packaging over substance against funded incumbents [LAND-F06/F07]; its handover cards survive as a feature. **C5** dies on FEA 4 [ARCH-F05]; its B2B2X positioning survives as the go-to-market story, not the MVP.

## TOP 2 ADVANCING TO PHASE 3

**C2 GUARDIAN DIAL (67)**: highest floor across all nine criteria, matches the research-recommended shape [ARCH-F06], carries every A5 signature moment.
**C1 CLOCKWORK SOC (63)**: highest ceiling on NOV/CLR/FEA/BIZ, sits on the cleanest verified white-space [COMP-F20], and carries a known, undeclared-to-judges structural risk (WIN-F02 drift) that Phase 3 persona (a) must now attack head-on.

Note per calibration rule: neither concept may gain a score on any criterion in the same cycle its weakness on that criterion is exposed; gains must survive the following cycle's attack first.

**PHASE 2 COMPLETE.**

---

# H1 RECON INTAKE (received after Phase 2, before Phase 3; ground truth, overrides report assumptions about Decode SIH itself)

**H1-F01 (PS wording):** "Autonomous Cyber SOC for AI-powered threat detection and automated incident response." Five load-bearing terms: AUTONOMOUS, CYBER SOC, AI-POWERED, THREAT DETECTION, AUTOMATED INCIDENT RESPONSE. Zero-drift rule [WIN-F02] now has its exact target. Gap list item #1: CLOSED.

**H1-F02 (template):** 8 slides: Title, Team, Problem Statement (title from OSCode list + aim + why-chosen), Real-World Problem Alignment (who faces it + current gap + how solution fills it practically + EXISTING GOVERNMENT SCHEMES hook), Proposed Solution (100-150 words + 3-4 KEY FEATURES + what's different), Tech Stack & Architecture, Architecture Diagram, Thank You. Gap list item #2: CLOSED. This OVERRIDES the Phase-1 assumption of the SIH 6-slide format [WIN-F05]; ledger updated (L11: Decode template ≠ SIH template; trust H1-F02 here, keep WIN-F05 for actual SIH later).

**Template consequences fed to the personas:** (1) HARD CAP of 3-4 key features: C2 currently carries seven, that is now attackable buzzword-stacking [WIN-F03]. (2) No feasibility, references, or business slide exists: impact numbers, viability, and rigor signals must be woven into Problem/Alignment slides or die. (3) The schemes prompt directly rewards Digital India / Cyber Surakshit Bharat / C3iHub / I4C hooks [A1-F55, A1-F56, A1-F57]. (4) TWO of eight slides are architecture: technical complexity gets disproportionate visible real estate. (5) The 100-150-word box is persona (d)'s exam paper.

---
# PHASE 3 · RED-TEAM LOOPS

## CYCLE 1: all five personas vs C2 GUARDIAN DIAL and C1 CLOCKWORK SOC

### (a) Past SIH judge

**vs C1: "Read the PS aloud. Where is your automated incident response?"** PS4 demands detection AND automated response AND autonomy [H1-F01]. C1 detects minimally and responds never: it drafts paperwork. That is the #1 documented rejection, solving an adjacent problem [WIN-F02]. The template makes it worse: the 100-150-word box would describe a compliance tool while the problem title says Autonomous Cyber SOC [H1-F02]. **LANDED, structural.** No score on any C1 criterion may rise this cycle; FEA-as-submission and IMP-on-stated-problem fall.

**vs C2: "Seven features is buzzword-stacking, and your template allows four."** Dial, OPA, citations, injection defense, compliance drafts, Sigma flywheel, Indic UX [WIN-F03, H1-F02]. **LANDED:** forces feature compression (revision R1). Follow-up: "is every tech necessary?" Sigma-deterministic + Claude-only-for-hard-reasoning and OCSF survive as necessity, not decoration [PIPE-F07, PIPE-F01]. Follow-up: "novelty vs Microsoft/CrowdStrike?" Survives on India-specific clauses no incumbent ships [A2 §6.1-6.3, COMP-F20], but combination-novelty doubt is held open for cycle 2. Scheme-hook check: C2 has real ones [A1-F55, A1-F56]. SURVIVED on necessity and schemes, LANDED on feature count.

### (b) Security industry veteran

**vs C2, attack 1: "Why not Dropzone at $36k or Copilot?"** Price umbrella: target buyers pay ₹25k-₹1L/month total [A1-F33] vs Dropzone's $36k/yr floor [LAND-F06]; Copilot absent from Indian government clouds [LAND-F01b]; neither drafts CERT-In/DPDP artifacts [COMP-F20]. **SURVIVED with IDs.**
**Attack 2: "Your injection defense is a parlor trick; detectors are bypassable."** Partially true: benchmarks for SOC-LLM robustness do not exist [LAND-F25]. Defense survives ONLY as defense-in-depth (data/instruction separation, quarantined content plane, deterministic egress gates, human approval on consequential actions) with modest claims [SAFE-F02, SAFE-F03, LAND-F24]. **LANDED on claim discipline:** revision R2, "mitigates, never solves."
**Attack 3: "Auto-generated Sigma rules will be garbage and pollute the corpus."** TRAM precedent shows bounded coverage only [PIPE-F08]. **LANDED:** revision R3, human-review gate plus a ~20-incident LLM-judge eval harness [AGT-F12].
**Attack 4: "OCSF normalization of a co-op bank's legacy CBS logs is the real cost."** Survives via honest MVP scope: syslog/webhook/Fluent Bit plus 2-3 connectors, BOTS replay for the rest [PIPE-F03, DEMO-F01]. **SURVIVED.**

**vs C1:** "Reporting without response is a form-filler; BreachRx already exists globally" [COMP-F20]. **LANDED** on standalone BIZ.

### (c) Skeptical VC

**vs C2, attack 1: "Co-op banks are procurement hell. Who actually pays?"** Direct-SMB motion is weak; survives only by leading with the channel: MSSPs and the SEBI-mandated M-SOC operators, B2B2X [A1-F47, A1-F42]. **LANDED on framing:** revision R4, channel-first business story.
**Attack 2: "Why now? DPDP isn't enforced until May 2027 and CERT-In has never fined anyone."** [COMP-F17a, COMP-F24]. Survives via the honest frame: a closing compliance runway plus record breach cost [A1-F10], never a claim of current enforcement. **SURVIVED with C-09 discipline.**
**Attack 3: "TAM?"** Survives only as a range with scope ambiguity declared [A1-F37, L6]. **SURVIVED.**
**Attack 4: "Moat? An incumbent adds CERT-In drafting in one quarter."** True: no tech moat on drafting. Held open as declared risk; partial answer is price floor + open portable artifacts incumbents are anti-incentivized to copy [LAND-F06, A2 §5(e)]. **LANDED partially:** BIZ frozen this cycle.

### (d) Tired evaluator #147

**vs C2:** "Guarded-autonomy tiered-response multi-agent policy-as-code citation-grounded..." is word salad at submission #147. The 100-150-word box [H1-F02] fails as currently phrased. **LANDED:** revision R5, one-breath pitch. CLR drops.
**vs C1:** "Files your CERT-In report before the clock runs out" lands in five seconds. SURVIVED, for whatever a doomed concept's clarity is worth.

### (e) Senior SOC analyst (A5)

**vs C2, five attacks:** "Another console among my 83?" Unified workspace answer [UX-F11, A5 P9]. "AI text floods?" Role-adaptive depth [UX-F21]. "Wrong at 2 a.m.?" Approval gates, rollback, immutable audit [UX-F27, UX-F29, SAFE-F06]. "Does correcting it matter?" Feedback loop [UX-F31]. "Explanation theater?" Counter-evidence display and forcing functions [UX-F30, UX-F43]. **ALL SURVIVED:** the concept was built from A5. UX 9-eligible this cycle (attacked, survived, IDs cited).
**vs C1:** "Reporting is the CISO's pain, not mine. Where is my triage relief?" [UX-F01]. **LANDED.**

### Cycle-1 revisions

**C2 v2:** R1 four key features: (1) glass-box cited triage [AGT-F07, UX-F20], (2) policy dial with approval gates and blast-radius rings [SAFE-F03/F04/F07], (3) injection-hardened pipeline [SAFE-F02], (4) compliance-clock module drafting CERT-In/DPDP [COMP-F18/F19]. Sigma flywheel and Indic UX demoted to differentiator/roadmap lines. R2 claims discipline. R3 rule-review gate plus eval harness. R4 channel-first BIZ. R5 one-breath pitch: "An AI SOC that investigates every alert with cited evidence, acts only inside a policy you can read, and drafts your CERT-In report before the 6-hour clock runs out."
**C1r:** bolts on a minimal detect-respond core to cure drift. Convergence toward C2-lite noted for cycle-2 judgment.

### Cycle-1 re-score (raises only where attacked AND survived unrevised)

| Concept | NOV | TCX | CLR | FEA | SUS | IMP | UX | FUT | BIZ | Total |
|---|---|---|---|---|---|---|---|---|---|---|
| C2 v2 | 7 | 8 | 6↓ | 8↑ | 7 | 8 | **9**↑ | 8 | 7 | **68** |
| C1r | 8 | 5 | 8 | 5↓ | 6 | 6↓ | 7 | 6 | 7↓ | 58 |

Raises: C2 FEA 7→8 (attacked by (a)+(b), survived on existing scope/fallback design [ARCH-F02, DEMO-F01, A3 thresholds]); C2 UX 8→9 (survived all five (e) attacks [UX-F18/F20/F27/F30/F31]). Drops: C2 CLR 7→6 (persona (d) landed). C1r FEA 8→5, IMP 7→6, BIZ 8→7 (drift + standalone-category attacks landed [H1-F01, WIN-F02, COMP-F20a]). Frozen despite merit: C2 TCX, NOV, BIZ (weaknesses exposed this cycle; revisions must survive cycle 2 first).

---

## CYCLE 2: personas re-attack revisions plus previously untested criteria

### (a) Past SIH judge

**vs C2 v2: "Is the compliance module itself drift? Reporting is not response."** Defense: NIST SP 800-61r3 includes post-incident activity and reporting within incident response [SAFE-F08], and in India the CERT-In filing is a LEGAL component of responding to an incident [COMP-F01, COMP-F03]; the module consumes the response record, it does not replace response. **SURVIVED.**
**vs C2 v2: "Your 22.68 lakh incidents number is a complaints-count conflation."** Trap pre-defused by ledger discipline: NCRP complaints labeled as complaints, CERT-In 29.44 lakh handled (2025) labeled separately [LAND-F39, COMP-F16, L2]. **SURVIVED: IMP 9-eligible** [A1-F10, A1-F17, WIN-F28b].
**vs C1r: "You rebuilt the other team's product with a weaker core."** The structural proof, three IDs: the PS demands response at the center [H1-F01]; drift is the #1 rejection [WIN-F02]; and A6's own verdict states compliance drafting "should be ONE high-visibility module... on top of the autonomous SOC, not the whole product" [A6 §6, COMP-F21]. C1's entire differentiator is absorbable as a module of C2, and C2 already absorbed it in Phase 2. **CEILING PROVEN STRUCTURAL. C1r ELIMINATED.** All further cycles run on C2 alone.

### (b) Security veteran

**"Show me injection architecture, not adjectives."** C2 v2 presents the concrete design: untrusted-content quarantine plane, instruction/data separation, detector layer, deterministic egress allow-list, OPA gate before any action, human approval on consequential classes, plus the live attack-then-defense demo script [SAFE-F02, SAFE-F03, LAND-F24, A2 §5(h)]. **SURVIVED: TCX 9-eligible** (exposed cycle 1, revised, survived cycle 2).
**"Combination novelty is marketing."** Defense: each of the four features maps to verified unclaimed or single-claimant territory [COMP-F20, LAND-F23 with only LAND-F10 defending, A2 §6], no incumbent ships the combination, no SIH student team has shipped any of it [LAND-F26]. Survives, but 9 is withheld until the sharpest single line survives cycle 3. **NOV 7→8.**

### (c) Skeptical VC

**"Why do MSSPs pick you over Dropzone at their price point?"** India-compliance modules Dropzone lacks [COMP-F20], ₹-band economics under the $36k floor [LAND-F06, A1-F33/F34], white-label multi-tenant roadmap, and portable open artifacts the MSSP keeps [A2 §5(e), A1-F47]. **SURVIVED: BIZ 7→8** (exposed cycle 1, revised R4, survived).
**First attack on SUS: "Free-tier house of cards. Who maintains this after September?"** Open-core survival precedents [A1-F51, A1-F52], community-compatible Sigma corpus [A1-F53], open standards with no vendor lock [PIPE-F01], and a nameable runway: C3iHub ₹30L cohort plus Cyber Surakshit Bharat channel [A1-F55, A1-F56]. **SURVIVED: SUS 7→8.**

### (d) Tired evaluator #147

Re-test of the one-breath pitch and the 100-150-word box: verdict, understood in under 30 seconds, dial diagram carries the architecture slide [SAFE-F04, H1-F02]. **SURVIVED: CLR 6→7** (raise permitted, revision survived a full cycle). 9 withheld pending the full template mock in cycle 3.

### (e) Senior SOC analyst

**"Corrections retrain WHAT exactly, in three weeks?"** Honest answer: correction memory and few-shot org-context injection, not fine-tuning; labeled roadmap, with the eval harness measuring verdict-match like Torq's 85% pattern [UX-F31, AGT-F12]. **SURVIVED modestly: UX holds 9.**

### Cycle-2 revisions

**C2 v3:** drafted the actual 100-150-word template box and the dial-centric architecture diagram spec; week-by-week 3-week plan with the documented fallbacks (copilot-shape fallback, config-dial fallback, pre-recorded BOTS replay) [A3 thresholds, ARCH-F01, DEMO-F01]; NOV line sharpened to a single sentence for cycle-3 testing; FUT roadmap staged (deception, M-SOC multi-tenancy, domain-agnostic engine) [ARCH-F03, ARCH-F05, A2 §5(f), COMP-F30 Stage 3].

### Cycle-2 re-score

| Concept | NOV | TCX | CLR | FEA | SUS | IMP | UX | FUT | BIZ | Total |
|---|---|---|---|---|---|---|---|---|---|---|
| C2 v3 | 8↑ | **9**↑ | 7↑ | 8 | 8↑ | **9**↑ | **9** | 8 | 8↑ | **74** |
| C1r | ELIMINATED [H1-F01, WIN-F02, COMP-F21/A6 §6] | | | | | | | | | |

Frozen despite merit: CLR (revision needs one more survival), FEA and FUT (not yet attacked in their revised form), NOV (sharpest line untested).

**CYCLE 2 COMPLETE.**

---

## CYCLE 3: terminal convergence, all five personas vs C2 v3

C1r is dead [H1-F01, WIN-F02, A6 §6/COMP-F21]. Every gun now points at C2 v3. Frozen-or-untested criteria this cycle: NOV (sharpest line), CLR (full template mock), FEA (revised plan), SUS, FUT, BIZ (moat redux). The three standing 9s (TCX, IMP, UX) take re-pressure to confirm they hold.

### (a) Past SIH judge, final pass

**Attack 1, the template mock read cold.** The actual 100-150-word box under test: *"CITINEL is an autonomous Cyber SOC that investigates every alert with cited evidence, acts only inside a policy humans can read, and beats India's regulatory clocks. Alerts from bank systems normalize to OCSF; Sigma rules catch known threats deterministically; Claude agents correlate the rest into a MITRE ATT&CK kill-chain narrative where every verdict cites the exact log line proving it. Response actions pass a per-action policy: enrichment runs automatically, host isolation runs with rollback, disabling a production account waits for one-click human approval. The pipeline treats all log content as untrusted data, so a poisoned log cannot hijack the AI. On confirmation, it drafts the CERT-In 6-hour report and DPDP breach artifacts for human sign-off. Built for cooperative banks that RBI requires to run a 24×7 SOC they cannot afford."* Judge verdict: every PS4 clause present in order (autonomous, AI-powered, detection, automated response) [H1-F01], four features exactly [H1-F02], zero buzzword padding, each tech necessary [WIN-F03]. **SURVIVED.**
**Attack 2, "why did your team choose this?" box.** Answer on evidence: C-Edge took ~300 cooperative banks offline in 2024 [A1-F26], a regulator has already declared small entities cannot afford SOCs [A1-F42], and the lead builds agentic systems professionally. Schemes hook slot filled: Digital India, Cyber Surakshit Bharat, C3iHub, I4C [A1-F55, A1-F56, A1-F57]. **SURVIVED.**
**Attack 3, checklist gate.** The A4 20-check list [A4 §5]: 18 pass on current spec; #17 (final original wording) and #19 (numbers woven into the alignment slide) close at deck-writing. **SURVIVED. CLR 7→9** (revision made cycle 2, survived full cycle-3 attack, IDs: H1-F02, WIN-F03, WIN-F02).

### (b) Security industry veteran, final pass

**Attack 1, "your live demo dies on stage: rate limits, venue hardware, flaky agents."** Defense ladder, pre-committed: primary demo is pre-recorded BOTS v1 telemetry replayed offline, guaranteed to work [DEMO-F01, A3 thresholds]; enrichment cached with hash-first dedup so VirusTotal's 4/min cap never fires mid-demo [PIPE-F04, AGT-F10]; if multi-agent correlation wobbles in week 1, the documented fallback is the copilot shape with the dial as config [ARCH-F01, A3 thresholds]; and the idea round requires a credible demo artifact, not a live build [WIN-F21]. **SURVIVED. FEA 8→9** [DEMO-F01..F04, ARCH-F02, WIN-F21].
**Attack 2, "it's API glue."** Inventory says otherwise: OCSF normalization layer [PIPE-F01], deterministic Sigma engine [PIPE-F07], OPA policy-as-code gate [SAFE-F03], quarantined untrusted-content plane with detector layer [SAFE-F02, LAND-F24], orchestrator-worker swarm engineered around the citations-vs-structured-outputs incompatibility [AGT-F01, AGT-F08], append-only decision log separate from thinking summaries [AGT-F06, SAFE-F06], 20-incident LLM-judge eval harness [AGT-F12]. **TCX HOLDS 9.**
**Attack 3, injection laundering: "the poisoned string ends up inside the CERT-In draft the human signs."** Sharpest attack of the cycle. Defense: citations force provenance so every draft sentence traces to a raw log line rendered as escaped, visibly-flagged data [AGT-F07]; free-text fields from untrusted sources render in quarantine styling; the human gate is legally mandatory anyway [COMP-F21]. Added to the demo script as beat three: injection attempt visible INSIDE the draft, flagged. **SURVIVED, demo improved.**

### (c) Skeptical VC, final pass

**Attack 1, moat redux, hardest form: "your one unclaimed feature is a template-filler an incumbent replicates in a sprint; everything else is shipped by funded startups. Why does YOUR company exist in 18 months?"** Defense stack: the gap persists for documented economic reasons, India formats are low-TAM for global roadmaps [A2 §5(a)]; incumbent price floors structurally exclude the buyer (Dropzone from $36k/yr vs a ₹25k-₹1L/month total budget) [LAND-F06, A1-F33]; distribution rides a regulator-manufactured channel [A1-F42, A1-F47]; cost-effectiveness is near-unbeatable (₹0 stack, ~5¢/incident) [ARCH-F07]; and the judged criterion is commercial viability and cost-effectiveness at idea stage, not decade-long defensibility [WIN-F22]. Verdict: survives IN THE JUDGING FRAME; the moat question itself is unfalsifiable pre-market and goes to open risks as #1. **BIZ 8→9** [A1-F42, A1-F33/F34, A1-F47, ARCH-F07, WIN-F22].
**Attack 2, "roadmap is a wishlist."** Each stage carries its own evidence: deception integration with known precision baselines [ARCH-F03], M-SOC multi-tenancy against a standing mandate [ARCH-F05, A1-F42], regulator-connector expansion across seven bodies [COMP-F30], the domain-agnostic engine as documented unclaimed positioning [A2 §5(f)], and a publishable research contribution in the SOC-robustness benchmark gap [LAND-F25]. **SURVIVED. FUT 8→9.**
**Attack 3, "who maintains this after September?"** Regulator formats shipped as versioned data packs, not code; portable Sigma corpus is community-compatible [A1-F53]; open-core survival is precedented at zero funding [A1-F51, A1-F52]; named non-dilutive runway: C3iHub ₹30L cohort, Cyber Surakshit Bharat channel [A1-F55, A1-F56]. **SURVIVED. SUS 8→9.**

### (d) Tired evaluator #147, final pass

Thirty-second read of the mock box above, then the dial diagram. Reported comprehension: "AI SOC, every verdict shows its evidence, actions gated by a readable policy, files the 6-hour report, for co-op banks." Five concepts retained, zero jargon stalls. The two architecture slides carry the swarm and the dial visually [H1-F02]. **CLR 9 CONFIRMED.**

### (e) Senior SOC analyst, final shift-test

One alert walked end to end: 2 a.m. impossible-travel login → cited verdict in the glass-box replay [UX-F20, A5 Feature A] → routine enrichment auto-runs, isolation proposed with blast-radius panel and rollback, approval card waits [UX-F27, A5 Feature B] → 7 a.m. handover card preserves hypothesis, evidence, pending decision, time-sensitivity [UX-F32, UX-F33] → confirmed incident emits the CERT-In draft [A5 Feature C]. Verdict: "I would use this on shift." One honest nuance logged, not scored: real adoption needs connector depth beyond the MVP's 2-3, which matches A5's own guidance to demo one deep workflow over shallow breadth [A5 Caution 3]. **UX HOLDS 9.** IMP re-pressure ("projected, not proven") also resolved: all idea-stage impact is projected; this one is government-and-IBM-sourced with our own instrumented baselines planned and labeled [A1-F10, A1-F17, WIN-F28b, C-10]. **IMP HOLDS 9.**

## TERMINAL TABLE (cycle 3)

| Concept | NOV | TCX | CLR | FEA | SUS | IMP | UX | FUT | BIZ | Total |
|---|---|---|---|---|---|---|---|---|---|---|
| **C2 v4 FINAL** | **9** | **9** | **9** | **9** | **9** | **9** | **9** | **9** | **9** | **81** |

NOV 8→9 closed by attack (a)/(b) survival of the sharpest line: "Unlike Microsoft Security Copilot, which is not even available in Indian government clouds and cannot file an Indian regulator's report, we draft the CERT-In 6-hour report from the investigation itself" [A2 §6.1, LAND-F01b, COMP-F20], plus verified student-field clearance [LAND-F26, LAND-F14].

## TERMINATION VERDICT

**DOMINATION ACHIEVED: C2 v4 holds ≥9 on all nine criteria after three full attack cycles, every 9 carrying both finding IDs and a survived same-cycle attack.** Two conditions bind the verdict, logged honestly rather than hidden: (1) NOV 9 is CONDITIONAL on gap-list #3, a fresh pre-submission check that no vendor has shipped CERT-In/DPDP form auto-population, because COMP-F20 is absence-based Med evidence elevated only by A2 §5(a)'s independent convergence; A6 itself names vendor shipment as the recommendation-breaker. (2) BIZ 9 holds in the judging frame [WIN-F22]; the long-run moat question survives as OPEN RISK #1 for Phase 4, not as a score. No criterion is awarded 10: with mock evals unrun and gap-list items open, a pre-submission 10 would be rubric collapse in the upward direction.

**PHASE 3 COMPLETE.**

---
# PHASE 4 · LOCKED IDEA SPEC: C2 v4

## 1. Name, tagline, pitch

**Name: CITINEL.** Reads as citadel x sentinel, the fortress that keeps watch; the citizen-sentinel reading also lands for a system guarding citizens' deposits [A1-F26]. Speakable by any jury. Lock the official expansion line before the deck; name-collision check stays on gap list (#8).

**Tagline:** *The SOC that shows its evidence, obeys your policy, and beats the clock.*

**2-line pitch:** CITINEL is an autonomous Cyber SOC where Claude agents investigate every alert with cited evidence, act only inside a per-action policy humans can read, and draft India's mandatory CERT-In report before the 6-hour clock runs out. Built for the cooperative banks and small NBFCs that RBI requires to run a 24×7 SOC they cannot afford [A1-F43, A1-F29].

**30-second verbal:** "In 2024, one ransomware hit took nearly 300 Indian cooperative banks offline [A1-F26]. RBI requires them to run 24×7 security operations, but a human SOC costs over a crore a year and they can spend a lakh a month [A1-F29, A1-F31, A1-F33]. CITINEL is their AI SOC: Sigma rules catch known threats deterministically, Claude agents correlate the rest into an attack story where every verdict cites the exact log line proving it, response actions pass a policy you can read (enrich automatically, isolate with rollback, never touch a production account without one-click human approval), the pipeline treats every log as untrusted so a poisoned log can't hijack the AI, and when an incident is confirmed, the CERT-In 6-hour report is already drafted for sign-off."

**Template 100-150-word box:** locked as the cycle-3 mock (survived personas a and d verbatim).

## 2. Target user, pain, why-now

**Primary persona:** IT head / CISO-equivalent of a cooperative bank or small NBFC, ranked #1 target at 19/20 [A1-F45]. **Channel:** MSSPs and SEBI-mandated Market-SOC operators, B2B2X [A1-F47, A1-F42]. **Secondary skins:** SEBI-regulated small entities, hospitals [A1-F45 #2-3].

**Pain, quantified:** C-Edge/RansomEXX forced ~300 co-op banks offline in one incident [A1-F26]; RBI mandates a 24×7 C-SOC with 6-hour CIMS reporting [A1-F43]; a compliant human SOC needs 8-12 analysts at $1M+/yr, ₹1-2 crore payroll even at Indian salaries [A1-F29, A1-F31], against a ₹25k-₹1L/month affordability ceiling [A1-F33, Med, validation on gap list]; 66% of SOC teams can't keep pace [A1-F02]; triage burns 15-40 min/alert [A1-F06]; average India breach now costs ₹220M [A1-F10].

**Why-now drivers (honest framing per C-09):** CERT-In 6-hour rule in force since June 2022 [SAFE-F09]; SEBI CSCRF SOC deadlines already passed in 2025 [A1-F41]; DPDP's ₹250cr+₹200cr stackable penalties become fully enforceable ~May 2027, a closing runway, not current enforcement [A1-F40, COMP-F17a]; agentic SOC recognized as a Gartner category in 2025, validating the pattern while leaving the India layer empty [WIN-F30]; 73% of Indian orgs still make limited or no use of AI/automation despite proven savings [COMP-F15].

## 3. Core innovation and differentiation

**The line:** "Unlike Microsoft Security Copilot, which is not even available in Indian government clouds and cannot file an Indian regulator's report, CITINEL drafts the CERT-In 6-hour report and DPDP breach artifacts from the investigation itself" [A2 §6.1, LAND-F01b, COMP-F20].

**Three features no incumbent or rival student team will have:**
1. **Compliance-clock module:** CERT-In/DPDP form auto-population from live incident data; verified unclaimed by SOAR/GRC/AI-SOC vendors globally [COMP-F20, COMP-F13, A2 §5(a)], ~70-80% of CERT-In fields machine-draftable [COMP-F18].
2. **Injection-hardened pipeline with a live attack-and-defense demo:** poisoned log hijacks a naive agent on stage, fails against ours; attack peer-published, defense claimed by exactly one vendor [LAND-F23, LAND-F10, SAFE-F02], absent from the hobbyist Wazuh+LLM pattern [LAND-F14].
3. **Readable autonomy:** a per-action-class OPA policy artifact anyone can audit, plus the Shadow→Assist→Autonomous dial with blast-radius rings, vs incumbents' black-box "bounded autonomy" [SAFE-F03, SAFE-F04, SAFE-F07, LAND-F02].

**Bonus differentiator (roadmap line, not headline):** every resolved incident emits a portable open Sigma rule + playbook, anti-lock-in incumbents won't copy [A2 §5(e), A1-F53].

## 4. Concept anatomy

**Agent swarm (workflow-first discipline [AGT-F02], agents only where breadth or reasoning pays the ~15x token cost [AGT-F11]):**

| Agent | Role | Why an agent |
|---|---|---|
| Sentinel (orchestrator) | Decomposes incidents, spawns workers [AGT-F01] | Novel alert chains need dynamic decomposition |
| Triage Router | Severity/path routing, Haiku-class, strict JSON [AGT-F03, AGT-F08] | Cheap classification at volume |
| Enrichment squad | Parallel VT/AbuseIPDB/GeoIP/Tavily lookups [AGT-F04, PIPE-F04..F06] | Parallel breadth is where multi-agent pays |
| Correlator | Extended thinking over long log windows → ATT&CK kill-chain [AGT-F05, AGT-F06, PIPE-F08] | Genuine reasoning over ambiguity |
| Verdict Narrator | Citations-grounded evidence-first narrative [AGT-F07] | Cited narrative is incompatible with strict JSON, so a separate role [AGT-F08] |
| Response Marshal | Proposes actions, consults OPA gate, executes per dial tier against simulated endpoints [SAFE-F03, PIPE-F09] | Tool-use loop with policy checks |
| Scribe | CERT-In/DPDP drafts, Sigma+playbook drafts, handover cards [COMP-F18/F19, PIPE-F10, UX-F32] | Consumes the structured record the swarm already produced |

**Deterministic non-agent layers:** OCSF normalizer [PIPE-F01], Sigma engine (3,000+ community rules) [PIPE-F07], statistical anomaly scorers, OPA policy engine, append-only audit log.

**Autonomy-safety design:** per-action-class dial [SAFE-F04]; approval gates on consequential actions, mirroring all four named vendors [SAFE-F01, SAFE-F05, UX-F27]; blast-radius rings and staged rollout justified by the CrowdStrike 8.5M-device lesson [SAFE-F07]; immutable audit logs structured decisions and tool calls, never thinking summaries [SAFE-F06, AGT-F06]; injection defense = quarantined untrusted-content plane, instruction/data separation, detector layer, deterministic egress allow-list, provenance-flagged rendering inside report drafts [SAFE-F02, LAND-F24, cycle-3 laundering fix].

**Knowledge flywheel:** resolved incident → human-reviewed portable Sigma rule + playbook + correction memory, measured by a ~20-incident LLM-judge eval harness [PIPE-F10, A1-F53, UX-F31, AGT-F12].

**Domain-agnostic future path:** same engine, swapped connector + policy + regulator packs → AIOps and fraud, positioned as unclaimed business story, staged after the SOC skin is deep [A2 §5(f), A5 Caution 3].

**Three signature UX moments [A5]:** glass-box investigation replay [UX-F18, UX-F20, UX-F25]; policy-guarded approval card with potential-impact panel [UX-F26, UX-F27]; regulatory-clock auto-report + shift-handover card [UX-F34, UX-F41, UX-F32/F33].

## 5. Evidence pack (10 best, ID + source)

| # | Stat | ID | Source |
|---|---|---|---|
| 1 | India breach cost ₹220M, record, +13% | A1-F10/COMP-F15 | IBM India newsroom, 7 Aug 2025 |
| 2 | ₹22,845.73 cr citizen fraud losses 2024, +206% | A1-F17/UX-F45 | MoS Home, Lok Sabha, 22 Jul 2025 |
| 3 | 6-hour incident reporting mandate | SAFE-F09/COMP-F01 | CERT-In Directions PDF, 28 Apr 2022 |
| 4 | DPDP up to ₹250cr + ₹200cr, stackable, 72-hr report | A1-F40/COMP-F10 | DPDP Act Schedule + Rules, 13 Nov 2025 |
| 5 | SEBI orders NSE/BSE Market SOCs because small REs can't afford their own | A1-F42 | SEBI CSCRF circular, 20 Aug 2024 |
| 6 | ~300 cooperative banks offline, one attack | A1-F26 | Reuters + NPCI, Aug 2024 |
| 7 | Human 24×7 SOC $1M+/yr vs ₹25k-₹1L/month buyer budget | A1-F29 vs A1-F33 | Expel; bminfotrade (Med, validate) |
| 8 | AI+automation saves $2.2M/breach; 73% of Indian orgs under-use it | WIN-F28b, COMP-F15 | IBM 2024; IBM India 2025 |
| 9 | 66% of SOC teams can't keep pace; only 16% fully automate response | A1-F02/WIN-F29b | SANS 2024 SOC Survey |
| 10 | India cyber workforce gap 790,000, last official figure | WIN-F31 | ISC2, Oct 2023 (per ledger L1) |

## 6. Honest feasibility

**3-week MVP [ARCH-F02, A3 Stage 2]:** Week 1: BOTS v1 ingest → OCSF → Sigma + anomaly scores [DEMO-F01, PIPE-F01/F07]. Week 2: swarm (route/enrich/correlate/narrate) + OPA gate + dial config + append-only audit [AGT-F01..F08, SAFE-F03]. Week 3: compliance drafter, glass-box UI, injection attack+defense demo, eval harness, polish [COMP-F18, LAND-F23, AGT-F12].

**Simulated:** response actions hit mocked/lab endpoints, never production [PIPE-F09]; telemetry is BOTS replay plus Atomic Red Team in an isolated VM [DEMO-F02/F04]; connectors capped at 2-3, deep over broad [A5 Caution 3].

**Out of scope, stated on the slide:** multi-tenancy [ARCH-F05], honeypots [ARCH-F03], model fine-tuning (correction memory only), machine filing to CERT-In (no API exists [COMP-F14, COMP-F22]), full 600-technique ATT&CK coverage (curated set [PIPE-F08]), Indic UX beyond one sample narrative (roadmap).

**Fallback ladder [A3 thresholds]:** copilot shape if correlation is unstable by end of week 1; config-file dial if OPA slips; pre-recorded replay if venue hardware is risky. **Economics:** ~5¢/incident, our own instrumented [INFERENCE] per the A1-F58 gap [ARCH-F07].

## 7. Criterion map

**Novelty 9:** three verified unclaimed/single-claimant features plus zero SIH prior art [COMP-F20, LAND-F23, LAND-F26]. **Complexity 9:** OCSF + Sigma + orchestrator-worker + OPA + hardening + citations, every element necessary [PIPE-F01/F07, AGT-F01/F07, SAFE-F02/F03]. **Clarity 9:** one-breath pitch, dial diagram, survived evaluator #147 cold-read [H1-F02]. **Feasibility 9:** license-clean demo assets, free-tier pipeline, documented fallbacks [DEMO-F01..F04, WIN-F21]. **Sustainability 9:** open standards, portable artifacts, open-core precedents, C3iHub + Cyber Surakshit Bharat runway [A1-F51/F52/F55/F56]. **Scale of impact 9:** ₹220M breach cost, ₹22,845 cr losses, every CERT-In-covered org [A1-F10/F17, COMP-F02]. **UX 9:** all three A5 signature moments, peer-reviewed trust design [UX-F20/F27/F30]. **Future-work 9:** deception → multi-tenancy → regulator connectors → domain-agnostic engine, each evidence-backed [ARCH-F03/F05, COMP-F30, A2 §5(f)]. **Business 9:** regulator-manufactured channel, proven WTP band, ~5¢ marginal cost [A1-F42/F33/F47, ARCH-F07, WIN-F22].

## 8. The 15 hardest judge questions, strongest honest answers

1. **"Isn't this Microsoft/CrowdStrike?"** They cost $36k-$35k+/yr, aren't in Indian government clouds, and none drafts a CERT-In report; our buyer's entire budget is under their floor [LAND-F01b, LAND-F06, COMP-F20].
2. **"What happens when it's wrong and isolates a production server?"** It can't without approval: consequential actions sit behind the human gate, isolations carry rollback, and blast-radius rings cap exposure; the CrowdStrike outage is why staged rollout is designed in [SAFE-F04/F07, UX-F27].
3. **"Why AI, not rules?"** Rules run first: Sigma catches known patterns deterministically and cheaply; Claude reasons only over correlation and novel chains rules can't express [PIPE-F07, WIN-F13].
4. **"Hallucination?"** Every verdict must cite the exact log line via the Citations API, structured outputs validate machine paths, a 20-incident eval harness measures it, and humans gate consequences [AGT-F07/F08/F12].
5. **"An attacker writes 'ignore previous instructions' into a log."** That attack is peer-published and we demo it live: log content is quarantined data, never instructions, detectors flag it, egress is allow-listed, and the poisoned string appears visibly flagged inside the draft report [LAND-F23, SAFE-F02].
6. **"Data source? Realistic for India?"** CC0 BOTS and MIT Atomic Red Team for the demo, LANL labeled data for ground truth; real deployments ingest syslog/webhooks into OCSF [DEMO-F01/F02/F05, PIPE-F01/F03].
7. **"Your false-positive rate?"** Industry runs 46-80% by survey; we target the world-class <10% benchmark and will publish our measured rate on the labeled set rather than claim it [WIN-F29, L3].
8. **"Who is the ONE user?"** The IT head of a cooperative bank, the person whose institution was one of the 300 taken offline by C-Edge [A1-F26, WIN-F19].
9. **"Who pays?"** MSSPs and Market-SOC operators, white-label, per-device pricing inside the proven ₹250-₹1,000/device band [A1-F47, A1-F42, A1-F34].
10. **"Why now if DPDP enforcement is 2027?"** CERT-In's 6-hour rule has been law since 2022; DPDP is the closing runway that makes adoption urgent before May 2027, and breach costs hit a record now [SAFE-F09, COMP-F17a, A1-F10].
11. **"Are you replacing analysts?"** India is short 790,000 professionals; there is no one to replace. CITINEL does Tier-1 toil so scarce humans do judgment [WIN-F31, UX-F12].
12. **"Integrate or replace existing SIEM?"** Integrate: OCSF-native ingestion, Sigma-portable output, and everything we generate exports openly instead of locking in [PIPE-F01/F07, A2 §5(e)].
13. **"Air-gapped government networks?"** Roadmap: the model layer is an adapter; Claude powers the demo, a pluggable local model serves air-gapped deployments, and we won't claim parity we haven't measured [A2 §5(j)].
14. **"Feasible for students in 3 weeks?"** Yes, with proof: license-clean datasets, free-tier intel, a week-by-week plan, three documented fallbacks, and ~5¢/incident economics [DEMO-F01..F04, ARCH-F07, A3 thresholds].
15. **"A regulator won't accept a machine-drafted report."** Correct, and the design agrees: human sign-off is mandatory, the audit trail proves detect-time and report-time, and we draft, we never file [COMP-F21/F22/F23].

## 9. Open risks, final ledger, gap list

**Open risks:** (1) MOAT: an incumbent could ship CERT-In drafting in a quarter; unfalsifiable pre-market, answered by price floor + channel + open artifacts [cycle-3 VC]. (2) NOV 9 is conditional on gap #1 re-verification [COMP-F20]. (3) Demo failure risk, mitigated by the replay ladder. (4) Mock-eval calibration unknown until the first OSCode mock runs. (5) CLR is an execution risk: the one-liner must be delivered verbatim. (6) A1-F33/F34 pricing anchors are Med 1-SRC. (7) Free-tier caps in any live setting [PIPE-F04/F05]. (8) CITINEL name collision unverified.

**CONTRADICTION LEDGER FINAL:** L1 talent gap → cite 790K (ISC2 2023) only, hedge the rest. L2 incident counts → label every figure by denominator, never merge. L3 FP rates → ranges only, <10% as target. L4 alerts/day → peer-reviewed 3,832 for enterprise claims. L5 autonomy marketing → cite convergent behavior, not vendor percentages. L6 market size → ranges with scope ambiguity declared. L7 RBI window → "6 hours under Apr 2024 MDs." L8 CIMS → trust primary absence, draft-and-export design. L9 model naming → tier structure only until live check. L10 prototype → demo artifact mandatory. L11 template → H1-F02 governs Decode; WIN-F05 reserved for actual SIH. All eleven: RESOLVED or MANAGED, none blocking.

**RESEARCH GAP LIST FINAL (manual, before 11 Aug):** (1) fresh check no vendor shipped CERT-In/DPDP form auto-population, the NOV breaker [COMP-F20]; (2) CIMS portal existence [L8]; (3) live Anthropic model names/pricing [L9]; (4) full URLs for all 10 deck stats [A1 repair]; (5) CERT-In official 2024 annual total if cited; (6) Swytchcode/Render/n8n/Tavily current free-tier quotas [A3 gap]; (7) instrument own cost-per-incident and cost-per-report baselines, label [INFERENCE] [A1-F58, COMP-F31]; (8) CITINEL name/trademark scan; (9) validate ₹ pricing bands with 2-3 real MSSP quotes if reachable [A1-F33/F34]; (10) confirm the OSCode PS list link carries no additional PS4 description text beyond H1-F01; (11) submission portal mechanics and deadline hour. CLOSED: PS wording [H1-F01], template [H1-F02].

## 10. Sponsor-compatibility check

**Swytchcode:** natural, optional: Response Marshal and Scribe route agent→API execution (comms/ticketing + cloud response APIs, ≥2 ecosystems) through Swytchcode in Phase B; core survives without it, so no forced dependency. **Render:** natural: web service (glass-box UI) + background worker (pipeline) + managed Postgres/Redis = 3+ service types. **n8n:** natural: escalation, notification, and report-export flows as visible n8n workflows; policy authority stays OPA, n8n is orchestration glue, never the gate. **Tavily:** natural: the enrichment squad's live OSINT arm (IOC context, actor background, CVE chatter) feeding cited narratives. **Startuped:** natural: the channel-first B2B2X story plus C3iHub/Cyber Surakshit Bharat runway is a ready GTM track [A1-F55, A1-F56]. **No forced fits. Nothing redesigns in Phase B.**

---

**ENGAGEMENT COMPLETE.** CITINEL is the survivor: 81/90 after three full attack cycles, every 9 earned under fire, two honest conditions attached (gap #1, moat risk). Next concrete moves in order: run gap items 1-4, draft the 8 slides straight from this spec (the 100-150-word box and diagram spec already exist), then book the first OSCode mock eval and feed its transcript back here as H2 for a calibration pass.
