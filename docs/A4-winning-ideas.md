# Reverse-Engineering What Makes IDEAS Win Smart India Hackathon (SIH)-Style Evaluations
### Idea-substance intelligence brief for "Decode SIH 2026" Track 3 PS4 (Autonomous Cyber SOC)

## Executive Summary (10 bullets max)
- SIH scores ideas on 8 official criteria: novelty, complexity, clarity, feasibility/practicability, sustainability, scale of impact, user experience, and future-work potential (identical wording across sih.gov.in and college SPOC docs, 2022-2025). These are literally the scoring axes; the idea must be engineered to hit each one.
- The single most-cited idea-level rejection reason from SIH winners and reviewers is "solving the wrong problem": drifting to a broad or adjacent problem instead of addressing every word of the specific problem statement (Anish Prashun, SIH 2022 winner, 2025).
- Buzzword-stacking and "fancy tech for show" is a documented negative signal; judges reward tech that is necessary to solve the problem and can spot recycled/AI-generated content (Anish Prashun 2025; apnijanta 2025).
- Winners scope narrowly and pick a named end-user/customer; retrospectives show deliberate PS pre-filtering (monetization, TAM, "government not the sole customer") and 60% of time spent understanding the problem before coding (Dinesh A, two-time winner, dev.to 2024).
- A working prototype/demo at idea stage is a strong differentiator but NOT strictly required to win; a 2022 winner explicitly won "despite not having time to create an entire prototype" by solving the core issue (Anish Prashun 2025). The official idea round is a PPT/PDF, not code.
- Commercial/business viability carries heavy weight: one nodal-centre rubric weighted "commercial viability & cost-effectiveness" at 25% and "criticality/impact" at 25% (Anish Prashun 2025); SIH 2024 added an explicit startup/innovation emphasis.
- Judges grill AI ideas on data source, accuracy, why-not-rule-based, and failure/hallucination handling; security ideas on false positives, SOC integration, and "what happens when automation is wrong" (winner retrospectives + SOC domain benchmarks).
- Domain anchoring wins: winners research the sponsoring organisation and consult real domain experts (one consulted a lawyer for an e-courts PS) to inject the novelty judges reward (Arinjay Pathak, SIH 2022 winner, 2023).
- For the Cyber SOC PS specifically, real regulatory hooks signal rigor: CERT-In 2022 Directions (report incidents within 6 hours; 180-day India log retention); DPDP Act 2023 (up to ₹250 crore for failing to take reasonable security safeguards); India data-breach cost at an all-time high of INR 220 million in 2025 (IBM).
- Use the 20-check IDEA QUALITY CHECKLIST (Section 5) as a pre-submission gate; every check maps to a rubric criterion and a WIN finding ID.

## 1. Documented Rejection Reasons at SIH Idea Screening

**WIN-F01 — The official evaluation criteria are fixed and public.** "Evaluation criteria will include novelty of the idea, complexity, clarity and details in the prescribed format, feasibility, practicability, sustainability, scale of impact, user experience and potential for future work progression." Source: SIH guidelines reproduced verbatim across college SPOC pages (saranathan.ac.in SIH 2022) and sih.gov.in. Confidence: High (identical wording across official/college sources 2022-2025).

**WIN-F02 — "Solving the wrong problem" / drifting from the PS is the top idea-level rejection cause.** "Some teams do not fully solve the actual problem statement. Instead, they drift towards broader or unrelated issues. Stay laser-focused on the specific challenge given." And: "Carefully study and address every word in the official problem statement. If you drift away from this, even a great solution won't get selected. This is non-negotiable." Source: Anish Prashun (SIH 2022 winner who subsequently reviewed many submissions), 2025. Confidence: High (named winner + reviewer; corroborated by other retrospectives). [1-SRC for exact wording]

**WIN-F03 — Buzzword-stacking / unnecessary tech is a negative signal.** "Judges care more about how your tech solves the problem, not how fancy your stack is. Avoid the temptation to add buzzwords or trendy frameworks just for show." And: "Many teams overcomplicate their solutions, using too many technologies or buzzwords, losing sight of what really matters." Source: Anish Prashun 2025. Corroborated: "prove numbers, not buzzwords ... architecture with buzzwords but no integration story" listed as a failure mode (apnijanta 2025). Confidence: High (2 sources).

**WIN-F04 — Generic / AI-generated abstracts are penalized.** "Judges can spot recycled or AI-generated content. Use AI for support, but ensure your content is original and specific to your solution." And: "many teams rely too heavily on AI tools for content, which leads to generic and less compelling submissions." Source: Anish Prashun 2025. Confidence: Med (single named source, highly credible, consistent with the SIH template's explicit "Idea should be unique and novel" instruction).

**WIN-F05 — Idea template violations lose structural points.** The official SIH idea PPT template mandates max 6 slides (including title), points/diagrams over paragraphs, PDF upload only, and states explicitly: "Idea should be unique and novel." "A surprising number of teams miss the official template and lose valuable points on structure and clarity." Sources: official SIH Idea Submission Template (reproduced on SlideShare, SIH 2024); Anish Prashun 2025. Confidence: High.

**WIN-F06 — Track/category misalignment causes rejection.** "There are cases of misaligned submissions, for example, submitting for Track 1 when their solution fits Track 2." Source: Anish Prashun 2025. Confidence: Med [1-SRC].

**WIN-F07 — Feasibility-for-students / infeasible scope.** The SIH idea template requires a dedicated "FEASIBILITY AND VIABILITY" slide: "Analysis of the feasibility of the idea; Potential challenges and risks; Strategies for overcoming these challenges." Ideas that cannot show a realistic implementation path lose here. Source: official SIH Idea Submission Template, 2024. Confidence: High (structural requirement).

**WIN-F08 — Plagiarism / prior-code at idea stage is treated as cheating.** At the national idea stage teams "are only asked to present ideas, and the work might have been a way to show your skills to the university, but it will be considered as cheating by SIH, as you are allowed to code only during the finale." Source: Arinjay Pathak (SIH 2022 winner), 2023. Confidence: Med [1-SRC], consistent with SIH rules.

**WIN-F09 — Idea round is competitive by volume; only 500 ideas accepted per PS, then frozen.** "For each problem statement, only 500 ideas are submitted, which when done, the particular PS will freeze and no more idea submissions would be allowed." Source: GDSC-BITW SIH 2023 explainer, Medium 2023; corroborated apnijanta 2025. Confidence: High (2 sources). Implication: differentiation against hundreds of same-PS submissions is mandatory. Note: SIH FAQ (sih.gov.in) also caps each team at two idea submissions.

## 2. Case Studies: SIH 2022-2025 Winning Ideas

**WIN-F10 — "Pratyaksh" (Team DORA), SIH 2023 winner, Govt of Jharkhand PS "Real-Time Monitoring of Infrastructure" (SIH1370).** (a) Core idea: AI + GIS real-time construction monitoring that compares daily CCTV images to track build progress and material consumption, plus an end-to-end project-management system and a site-engineer mobile app. (b) Differentiation vs the obvious solution: instead of a generic status dashboard, they added computer-vision progress/material tracking and GIS mapping, and validated with real civil engineers and contractors; they explicitly selected the PS on business criteria: "no dependencies, standalone solutions, fewer competitors, government not being the sole customer, monetization potential, large Total Addressable Market (TAM), and no hardware." (c) Per-criterion strength [INFERENCE]: Novelty High (CV progress tracking), Feasibility High (stack chosen for 50-60% team familiarity), Scale of impact High (any infra project), Business potential High (chosen for TAM/monetization). (d) Retrospective: Dinesh A, dev.to, 2024. Confidence: High (first-person winner account).

**WIN-F11 — "Radar Vision" (team lead Chethan AC), SIH 2024 winner, PS 1606.** (a) Core idea: a full-stack prototype winning under PS 1606 (in the BEL "Conversational Image Recognition Chatbot" family per the SIH 2024 PS list). (b) Differentiation [INFERENCE]: strong end-to-end integration and disciplined iteration on mentor feedback across three evaluation rounds. (c) Per-criterion [INFERENCE]: User experience + integration High; the retrospective stresses "just building a great product wasn't enough ... Showcase our product effectively, impress the judges with innovation, sell our idea convincingly." (d) Retrospective: Chethan AC, Medium, 2025. Confidence: Med (winner account confirms win + PS; technical solution detail is thin).

**WIN-F12 — Team "Enthalpy," D. J. Sanghvi College of Engineering (Mumbai), SIH 2024 FIRST PRIZE, NTRO problem statement SIH1678 (nodal centre IIT Kharagpur).** Team members (all Third-Year IT): Surabhi Waingankar, Soham Patil, Sujal Choudhari, Anish Sharma, Ayush Upadhyay, Sagar Harsora. This is a concrete example of a student team winning a national-security (NTRO) software PS. Source: DJSCE official "SIH 2024 Grand Finale Winners" PDF (compiled by Dr. Vinaya Sawant, Head, Dept of IT), 2024; win corroborated by IIT Kharagpur's official post, 2024. Confidence: High for the win. The exact SIH1678 title and Enthalpy's solution approach were NOT FOUND.

**WIN-F13 — Case-study anchor: the NTRO cyber PS pattern (SIH 2023, SIH1451).** Verbatim PS: "Develop a AI/ML tool to detect whether a system / firewall / router / network is compromised. The technique should not rely only on IoCs (Indicators of Compromises) detection." Theme: Blockchain & Cybersecurity; Category: Software. Source: SIH 2023 official Software Problem Statements list, 2023. Relevance: SIH security PSs explicitly reward going beyond signature/IoC approaches, directly analogous to the Autonomous SOC PS4 (detection + autonomous response). A named winning team for SIH1451 was NOT FOUND. Confidence: High for PS text; NOT FOUND for winner.

**WIN-F14 — SIH 2024 NCIIPC cyber cohort at IIT Jammu.** IIT Jammu hosted roughly 28-30 teams tackling "critical cybersecurity challenges posed by the National Critical Information Infrastructure Protection Center (NCIIPC)"; six teams won ₹1 lakh each. Source: newsonair.gov.in (Govt of India), 2024. Relevance: confirms NCIIPC cyber-defence PSs are a live, winnable SIH category matching this brief. Named winning teams NOT FOUND. Confidence: High for existence; team detail NOT FOUND.

**WIN-F15 — DJSCE 2024 institutional sweep (5 software + 1 hardware first prizes).** Repeat institutional winning correlates with structured internal selection plus disciplined PS filtering (12 teams reached the finale; 6 won). Source: DJSCE SIH 2024 Grand Finale PDF, 2024. Confidence: High.

**WIN-F16 — "Solar Masters," Sir Padampat Singhania University (Udaipur), SIH 2024 winner (MathWorks PS).** Hardware/energy team; notable that MathWorks webinars/mentorship shaped the winning solution, illustrating the value of engaging the sponsoring organisation's resources. Source: MathWorks Student Lounge blog, 2025 [VENDOR]. Confidence: High (vendor-published winner interview).

**WIN-F17 — Historical baseline: 2019 supply-chain "Track & Trace" (Hindustan Unilever PS).** The team was initially rejected by judges as infeasible ("it is simply impossible to scan each product individually") and then pivoted; illustrates that judge skepticism about real-world feasibility/volume is decisive and recoverable. Source: Tanmay Bhatnagar, Medium (2019 finale). Confidence: Med (older; labelled historical baseline).

## 3. Winning-Idea Patterns With Evidence

**WIN-F18 — Winners scope narrower than the broad PS and pre-filter PSs on business criteria.** Explicit filter used by a two-time winner: "no dependencies, standalone solutions, fewer competitors, government not being the sole customer, monetization potential, large TAM, and no hardware." Source: Dinesh A, dev.to 2024. Confidence: High. Also: Arinjay Pathak went through "all 530+ problem statements" and filtered step-by-step before choosing (2023).

**WIN-F19 — A named target user/persona plus domain immersion drives the "novelty" judges reward.** "Research about them, and talk to people who are experienced in this domain ... my problem statement was about creating a keyword-based search for court cases. So my team consulted a lawyer ... This will help you bring novelty in your solution ... which will help you stand out from your competitors." Source: Arinjay Pathak, 2023. Corroborated by Dinesh A pitching to "friends, faculty, contractors, civil engineers, and ML specialists" (2024). Confidence: High (2 sources).

**WIN-F20 — Design-thinking / problem-first allocation of effort.** "We didn't immediately jump into solutions or coding. Instead, we followed a design thinking strategy, spending 60% of our time understanding the problem, defining user needs, ideating solutions, prototyping, and testing." Source: Dinesh A, 2024. Confidence: High.

**WIN-F21 — Prototype at idea stage: helpful, not mandatory.** Contrast within one credible source: (i) "Add a working prototype screenshot, video, or even a test use case ... Missing prototypes, no video, no screenshot, nothing ... is a critical error that immediately puts you at a disadvantage"; yet (ii) the same author's team "won despite not having time to create an entire prototype ... we solved the core issue." Reconciliation [INFERENCE]: a credible feasibility demonstration (even a mockup or test case) beats nothing, but convincingly solving the core problem can win at idea stage without a full build. Source: Anish Prashun 2025. Confidence: High.

**WIN-F22 — Commercial/business viability is heavily weighted.** One nodal-centre rubric: Innovation/Novelty 20%, Technology 15%, MVP/Prototype/Demo 15%, Criticality/Impact 25%, Commercial Viability & Cost-Effectiveness 25%. Source: Anish Prashun 2025 (reproducing the evaluation grid he was given). Corroborated by Dinesh A placing an "end to end implementation plan on BMC (Business Model Canvas)" which "earned brownie points" (2024). Confidence: High (2 sources). Caveat: this weighting is nodal/edition-specific, not the universal 8-criteria list [1-SRC for the exact percentages].

**WIN-F23 — Social-impact vs deep-tech framing: both win, but impact + government-deployability is the through-line.** SIH is explicitly deployment-oriented: "the Ministry of Education is committed to the further development, implementation, and deployment of SIH-winning ideas by effectively supporting the concerned ministries/departments." Source: sih.gov.in Project Implementation, 2024. Winning ideas frame impact for a government buyer and a real ministry. Confidence: High.

**WIN-F24 — The multi-stage finale rewards iteration and integration, not one-shot pitching.** The finale runs three judging rounds plus two mentoring sessions with rising weight (first round 20%, second 30%, third 50% at one nodal centre); "Integration is the key ... You are likely to surpass most of your competitors if all of your functionalities are integrated and working." Sources: Dinesh A 2024; Arinjay Pathak 2023. Confidence: High. Implication for the idea: design the idea so its components visibly integrate into one working whole.

**WIN-F25 — Standards/regulation name-dropping as a rigor signal [INFERENCE].** No SIH-specific source explicitly states "citing CERT-In raises your score." However, the official idea template mandates a "RESEARCH AND REFERENCES" slide, and judges demonstrably reward domain rigor and domain-expert grounding (WIN-F19). For a cyber SOC PS, anchoring to CERT-In 2022 Directions, DPDP Act 2023, MITRE ATT&CK, and NIST CSF is the concrete form that domain rigor takes on the references slide. Confidence: Med [INFERENCE from the template requirement + the documented domain-rigor reward pattern].

## Domain rigor bank for the Autonomous Cyber SOC idea (reference signals to embed)

**WIN-F26 — CERT-In 2022 Directions: 6-hour incident reporting + 180-day India-resident log retention.** Issued under sub-section (6) of section 70B of the IT Act, notified 28 April 2022 (No. 20(3)/2022-CERT-In), effective ~27/28 June 2022: entities must report specified cyber incidents "within six hours of noticing such incidents," and must "enable logs of all their ICT systems and maintain them securely for a rolling period of 180 days" within Indian jurisdiction. Sources: Trilegal analysis, 2022; Internet Society, 2022 (primary issuer: MeitY/CERT-In). Confidence: High (multiple sources). Product hook: an autonomous SOC that auto-drafts the CERT-In report inside the 6-hour window is a concrete, India-specific novelty no generic "agentic SOC" claims.

**WIN-F27 — DPDP Act 2023: penalties up to ₹250 crore for failing to take reasonable security safeguards.** The DPDP Act 2023 Schedule (Sl. 1, read with Section 8(5)) sets the highest slab at "up to ₹250 crore" for "failure to take reasonable security safeguards to prevent a personal data breach" (~USD 30 million); the adjacent slab is ₹200 crore for failure to notify a breach (Section 8(6)), and ₹150 crore for Significant Data Fiduciary obligations. DPDP Rules were notified by MeitY on 13 November 2025. Sources: EY India, 2023/2025; DPDP Act Schedule (dpdpa.com). Confidence: High (multiple sources). Product hook: this quantifies the financial cost of a missed/mishandled breach the SOC prevents.

**WIN-F28 — India data-breach cost at an all-time high.** Per IBM's Cost of a Data Breach (India): INR 179 million (2023) rose to INR 195 million (2024) and then to an all-time high of INR 220 million in 2025 (13% higher than 2024); the breach lifecycle in India fell to 263 days in 2025. Source: IBM newsroom India press releases, 2023/2024/2025 [VENDOR - IBM/Ponemon]. Confidence: High (primary vendor research, three consecutive years).

**WIN-F28b — Security AI + automation saved USD 2.2 million per breach (global).** IBM's 2024 report: when security AI and automation "were used extensively across prevention workflows organizations incurred an average $2.2 million less in breach costs, compared to those with no use in these workflows, the largest cost savings revealed in the 2024 report" (extensive users averaged $3.84M vs $5.72M for non-users). Source: IBM newsroom, 30 July 2024 [VENDOR]. Confidence: High. This is the single strongest quantified justification for building automated response.

**WIN-F29 — SOC alert fatigue / false-positive baseline (the pain the idea must quantify).** "False positive rates in enterprise SOCs frequently exceed 50% ... some organizations report rates as high as 80%" (CyberDefenders, 2024); world-class SOCs target "below 10%" false positives (Expel). Report as a range, not a point estimate. Sources: CyberDefenders 2024; Expel glossary [VENDOR flags on both]. Confidence: High (multiple sources, wide range).

**WIN-F29b — SANS 2024 SOC Survey: 66% of SOC teams cannot keep pace with alerts.** "66% of SOC teams reported they can't keep pace with the volume of alerts they receive" (SANS 2024 SOC Survey, author Chris Crowley, cited via Dropzone). A related SANS 2024 detection/response figure: "64% of SOC teams report being overwhelmed by false positives" and "only 16% of organizations have fully automated cyber response." Sources: Dropzone.ai citing SANS 2024; CardinalOps citing SANS 2024. Confidence: High. Product hook: the "only 16% fully automated response" gap is a direct market opening for an autonomous SOC.

**WIN-F30 — Agentic SOC is a validated 2025-2026 industry direction (novelty is real, but so is prior art).** CrowdStrike unveiled the "Agentic Security Platform ... the foundation powering the agentic SOC," including Charlotte AI AgentWorks ("the industry's first no-code platform" to build/deploy security agents), at Fal.Con on 16 September 2025; Gartner listed AI SOC agents as a representative category in its 2025 Innovation Insight report for the first time. Sources: CrowdStrike press release, 2025; UnderDefense market overview, 2026 [VENDOR]. Confidence: High. Implication: the multi-agent SOC pattern is credible AND has heavy commercial prior art, so the idea's novelty must come from an India-specific angle (CERT-In/DPDP automation, low-resource/offline, government cost), not from claiming to have invented the agentic SOC.

**WIN-F31 — India cybersecurity workforce gap: 790,000 (2023).** ISC2 2023 Cybersecurity Workforce Study: "India (up 40.2% to 790,000)," the highest workforce-gap increase in APAC that year (global gap a record 4 million; APAC 2.6 million). Source: ISC2, 31 October 2023. Confidence: High (ISC2 is the primary publisher). Note: ISC2 dropped country-level gap estimates in its 2025 study, so 790,000 (2023) is the latest official ISC2 India figure. Corroborating (secondary): the DSCI-SANS "India Cyber Security Skilling Landscape 2025-2026" reports a majority of Indian businesses cannot find enough skilled cyber staff. Product hook: an autonomous SOC directly attacks the analyst-shortage, an unusually strong scale-of-impact and business-potential argument.

## 4. Top-15 Questions SIH Judges/Mentors Ask on AI/Security Ideas

Derived from winner retrospectives describing judge Q&A (Tanmay Bhatnagar 2019; Dinesh A 2024; Chethan AC 2025, "Judges came around, grilling us with questions"), the SIH FAQ, and mapped onto AI/security domain benchmarks (Section 3). The 8 SIH criteria and the "grilling" behaviour are High-confidence; the exact AI/security phrasings are [INFERENCE] tailored to PS4.

1. What exactly in the problem statement are you solving, and which clauses are you NOT addressing? (WIN-F02)
2. Who is the ONE specific end-user? (e.g., tier-1 SOC analyst at a PSU bank / a district cyber cell / an NCIIPC-regulated body) (WIN-F19)
3. Why AI/ML here and not a simpler rule-based system? What does the ML actually add over signatures/IoCs? (WIN-F03, WIN-F13)
4. Where does your detection/training data come from, and is it realistic for an Indian government deployment? (WIN-F29)
5. What is your accuracy / false-positive rate, and what FP rate is acceptable to a real SOC? (WIN-F29)
6. What happens when the automation is WRONG, e.g., it auto-isolates a critical production server? (WIN-F29, WIN-F30)
7. How do you handle LLM hallucination in triage and response recommendations? (WIN-F04, WIN-F30)
8. How does this integrate with existing SOC tooling (SIEM/SOAR/XDR) rather than replace it? (WIN-F30)
9. Is there a human in the loop for high-impact actions, and where exactly is the policy boundary? (WIN-F30)
10. How is this feasible for a student team in the time and budget given? (WIN-F07)
11. Can it run offline / low-resource / on-prem for sensitive or air-gapped government networks? (WIN-F23)
12. What is the cost to a government buyer, and why is it cheaper than incumbents? (WIN-F22)
13. How does it comply with or leverage Indian regulation (CERT-In 6-hour rule, DPDP, 180-day logs)? (WIN-F26, WIN-F27)
14. What is the scale of impact, and can the sponsoring ministry actually deploy it? (WIN-F23)
15. What is the future-work and commercial roadmap (business potential)? (WIN-F22, WIN-F24)

Confidence: Med-High. The criteria and finale Q&A accounts are High; the precise AI/security phrasings are [INFERENCE] mapped from domain benchmarks onto documented judge behaviour.

## 5. IDEA QUALITY CHECKLIST (binary pass/fail; mapped to rubric + finding IDs)

1. Does the idea address EVERY clause of PS4 (threat detection AND automated incident response AND autonomy) with zero drift? [Clarity, Feasibility] (WIN-F02)
2. Is there ONE named primary user/persona (e.g., tier-1 SOC analyst at an Indian PSU bank or a CERT-In-regulated body)? [User experience, Scale of impact] (WIN-F19)
3. Is the novelty India-specific (CERT-In/DPDP automation, offline, government cost) rather than "we built an agentic SOC"? [Novelty] (WIN-F30, WIN-F25)
4. Can you justify AI/multi-agent over rule-based/IoC-only in one sentence tied to the pain? [Novelty, Complexity] (WIN-F03, WIN-F13)
5. Is every technology in the stack necessary (no buzzword padding)? [Complexity, Clarity] (WIN-F03)
6. Is the data source for detection specified and realistic for a govt deployment? [Feasibility] (WIN-F29)
7. Is a target false-positive rate / accuracy stated against a sourced benchmark (world-class <10%)? [Feasibility, Complexity] (WIN-F29)
8. Is there an explicit policy-guardrail / human-in-loop for high-impact auto-actions? [Feasibility, User experience] (WIN-F30)
9. Is LLM hallucination handling described (RAG grounding, confidence thresholds, verifiable actions)? [Complexity, Feasibility] (WIN-F04, WIN-F30)
10. Does it integrate with existing SIEM/SOAR/XDR instead of claiming to replace them? [Feasibility, Scale] (WIN-F30)
11. Is there a feasibility slide with risks + mitigations a student team can realistically build on free tiers/sponsor credits? [Feasibility] (WIN-F07)
12. Is there a working prototype OR a credible demo/test-case/mockup at idea stage? [Feasibility, User experience] (WIN-F21)
13. Is cost-to-government and cost-advantage quantified (near-₹0 build, open-source alignment)? [Sustainability, Business potential] (WIN-F22)
14. Does the references slide cite real standards/regs (CERT-In 2022, DPDP 2023, MITRE ATT&CK, NIST CSF, IEC 62443)? [Novelty, Clarity] (WIN-F25, WIN-F26, WIN-F27)
15. Is scale-of-impact framed for deployment by the sponsoring government body/ministry? [Scale of impact] (WIN-F23)
16. Is there an offline / low-resource mode for sensitive or air-gapped government networks? [Feasibility, Scale] (WIN-F23)
17. Is the content original (not AI-generated boilerplate) and within the 6-slide template? [Clarity] (WIN-F04, WIN-F05)
18. Is there a future-work + commercial roadmap (Business Model Canvas or equivalent)? [Future-work, Business potential] (WIN-F22, WIN-F24)
19. Is impact quantified with sourced numbers (₹220M breach cost, 790k analyst gap, 6-hour rule, $2.2M AI savings)? [Scale of impact, Novelty] (WIN-F28, WIN-F31, WIN-F26, WIN-F28b)
20. Does the idea avoid contradicting the sponsor tools it may later integrate (n8n, Render, Tavily, AWS Bedrock, Claude, Swytchcode, Startuped)? [Feasibility] (mission context)

## Contradictions & Disputes Found
- **Prototype necessity:** Anish Prashun (2025) both lists "missing prototype" as a critical error AND says his team won without a full prototype. Resolved: credible feasibility evidence beats none, but core-problem clarity can win at idea stage (WIN-F21).
- **SOC false-positive baseline varies widely by source:** >50% and up to 80% (CyberDefenders 2024); a 2023 study cited by StrangeBee reports ~83% of alerts are false alarms; world-class SOCs run below 10% (Expel). Report as a range, never a single point estimate (WIN-F29).
- **Team size:** older sources say 4-6 members; SIH 2023-2026 guidance says exactly 6 including at least one female member (some editions add a female-majority tiebreak). Current rule = 6 with ≥1 female (matches this brief's 3-6 with ≥1 female framing at the "Decode SIH" prep stage).
- **Rubric weights:** the universal SIH list is 8 unweighted criteria (WIN-F01); the 20/15/15/25/25 grid (WIN-F22) is nodal/edition-specific. Treat business/impact weighting as strong but not officially universal.

## What I Could NOT Verify (honest gaps)
- The exact TITLE of NTRO problem statement SIH1678 and what Team Enthalpy's winning solution actually did / how it differed from an obvious solution. NOT FOUND.
- A named winning team plus solution write-up for the SIH 2023 NTRO "detect compromised without IoCs" PS (SIH1451). NOT FOUND.
- Named winning teams for the IIT Jammu NCIIPC 2024 cyber problem statements. NOT FOUND.
- Any SIH-official document explicitly stating that citing standards/regulations increases score (WIN-F25 is [INFERENCE]).
- A primary DSCI/NASSCOM URL for the widely-circulated "~1 million India cyber shortage" figure (only low-quality secondary sources found; excluded from the numbers bank as unreliable).

## Top 10 Findings That Should Shape THE IDEA (by ID)
1. **WIN-F02** — Address every clause of the SOC PS (detect + auto-respond + autonomy); zero drift. This is the top rejection cause.
2. **WIN-F19** — Anchor to ONE named Indian user/organisation and do real domain immersion; this is where judged "novelty" comes from.
3. **WIN-F30** — Make novelty India-specific; the agentic SOC pattern has heavy commercial prior art (CrowdStrike, Gartner 2025).
4. **WIN-F29 / F29b** — Quantify the SOC pain (>50% false positives, only 16% fully automated response) and state your own target.
5. **WIN-F22** — Lead with cost-effectiveness and business potential; these are the heaviest-weighted axes at the nodal level.
6. **WIN-F26 / F27** — Wire in CERT-In 6-hour reporting and DPDP ₹250 crore exposure as concrete, defensible hooks.
7. **WIN-F21** — Bring a credible demo or test-case even at idea stage; a mockup beats nothing.
8. **WIN-F03 / F04** — Strip buzzwords; write original, specific content (judges detect recycled/AI text).
9. **WIN-F23** — Frame scale-of-impact for government deployment and include an offline / low-resource mode.
10. **WIN-F31 / F28 / F28b** — Use the 790k analyst gap, ₹220M breach cost, and $2.2M AI-savings figures to justify autonomy.

## Numbers & Facts Bank
| ID | Stat | Year | Source link | Confidence |
|----|------|------|-------------|------------|
| WIN-F01 | 8 official SIH evaluation criteria (novelty, complexity, clarity, feasibility, sustainability, scale, UX, future-work) | 2022-2025 | saranathan.ac.in; sih.gov.in | High |
| WIN-F09 | Max 500 ideas accepted per problem statement, then frozen | 2023 | medium.com/@gdsc.bitw; apnijanta.com | High |
| WIN-F22 | Nodal rubric: Impact 25%, Commercial viability 25%, Novelty 20%, Tech 15%, MVP 15% | 2025 | anishprashun.me | Med [1-SRC] |
| WIN-F26 | CERT-In: report incidents within 6 hours; 180-day India-resident log retention | 2022 | trilegal.com; internetsociety.org | High |
| WIN-F27 | DPDP Act 2023: up to ₹250 crore for failing reasonable security safeguards; ₹200 cr for non-notification | 2023 | ey.com; dpdpa.com | High |
| WIN-F28 | India avg data-breach cost: ₹179M (2023) → ₹195M (2024) → ₹220M (2025), all-time high | 2023-2025 | in.newsroom.ibm.com | High [VENDOR] |
| WIN-F28b | Security AI + automation saved $2.2M per breach (global; largest 2024 saving) | 2024 | newsroom.ibm.com | High [VENDOR] |
| WIN-F29 | Enterprise SOC false-positive rates >50%, up to 80%; world-class <10% | 2024 | cyberdefenders.org; expel.com | High |
| WIN-F29b | SANS 2024: 66% of SOC teams can't keep pace with alerts; only 16% fully automate response | 2024 | dropzone.ai / cardinalops (citing SANS 2024) | High |
| WIN-F30 | CrowdStrike "Agentic Security Platform / agentic SOC" launched 16 Sep 2025; Gartner named AI SOC agents 2025 | 2025 | crowdstrike.com; underdefense.com | High |
| WIN-F31 | India cybersecurity workforce gap 790,000 (up 40.2%) | 2023 | isc2.org | High |
| WIN-F12 | Team Enthalpy (DJSCE) won SIH 2024 first prize on NTRO PS SIH1678 (IIT Kharagpur nodal) | 2024 | djsce.ac.in | High |
| WIN-F13 | NTRO SIH1451: "detect whether a system/firewall/router/network is compromised ... not rely only on IoCs" | 2023 | SIH 2023 Software PS list (tcetmumbai.in) | High |
| WIN-F14 | IIT Jammu 2024: ~28-30 teams on NCIIPC cyber PSs; 6 winners at ₹1 lakh each | 2024 | newsonair.gov.in | High |
| WIN-F10 | SIH 2023 winner "Pratyaksh"/Team DORA: AI+GIS infra monitoring (Govt of Jharkhand SIH1370) | 2024 | dev.to/heisdinesh | High |
| WIN-F11 | SIH 2024 winner "Radar Vision" (Chethan AC), PS 1606 | 2025 | medium.com/@acchethan15 | Med |