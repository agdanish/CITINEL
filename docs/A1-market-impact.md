# Market & Domain Research — "Autonomous Cyber SOC" (Decode SIH 2026, Track 3 "Bharat Pragati" PS4)

*Prepared for the idea-substance decision (Round 1, due 11 Aug 2026). Every finding carries an ID, confidence tag, and bias flags. India numbers are prioritized over global. Where sources conflict, ranges and both sources are given rather than an average.*

---

## Executive Summary
1. **The pain is quantified and India-record-high:** IBM's official India newsroom (Aug 7, 2025) confirms the average total organizational cost of a data breach in India reached an all-time high of **₹220 million in 2025 (13% higher than 2024's ₹195M)** — India recorded among the highest breach-cost growth, and "shadow AI" added roughly ₹17.9M per affected breach.
2. **SOC alert fatigue is structurally unsolvable by humans:** 20–40% of alerts are never investigated, ~46% are false positives (Microsoft SOC report), and 66% of SOC teams can't keep pace (SANS). This is the core problem the multi-agent swarm attacks.
3. **India's talent math forces autonomy, not assistance:** a widely repeated (though not primary-ISC2-confirmed) estimate says India needs ~3M cyber professionals against <200K trained — a ~15x gap. Autonomous triage is a necessity, not a luxury.
4. **Cybercrime losses are exploding:** MoS Home Affairs told the Lok Sabha (July 22, 2025) that citizen cyber-fraud losses were **₹22,845.73 crore in 2024 vs ₹7,465.18 crore in 2023 — a ~206% rise**.
5. **Regulation now CREATES buyers.** SEBI CSCRF (Aug 20, 2024) mandates a SOC for every regulated entity and — crucially — orders NSE & BSE to build a shared "Market SOC" *because small entities cannot afford their own*. RBI, IRDAI, and the DPDP Rules 2025 all impose 24×7 monitoring and/or 6-hour/72-hour breach-notification duties.
6. **The cost gap is the wedge:** a 24×7 human SOC needs 8–12 analysts and costs $1M+/year, but Indian small businesses can only spend ₹25,000–₹1,00,000/month — a chasm an autonomous, low-headcount SOC can profitably bridge.
7. **Willingness-to-pay is proven:** Indian managed-SOC already transacts at ₹250–₹1,000/device/month and ₹25k–₹1L/month for small firms.
8. **Best target-user ranking:** #1 Cooperative banks & small NBFCs, #2 Hospitals, #3 SEBI-regulated small entities — highest pain × regulatory urgency × judge resonance.
9. **Sustainability precedents exist:** Wazuh (open-core, 30M+ downloads/yr, unfunded) and TheHive→StrangeBee (open-core → commercial with an explicit MSSP license tier) are proven survival models.
10. **National alignment provides a funding runway:** C3iHub IIT Kanpur (₹30 lakh grants), Cyber Surakshit Bharat, and I4C all offer a "Bharat Pragati" narrative and non-dilutive capital.

---

## SECTION 1 — SOC Pain Quantified (Global + India)

**A1-F01 — 20–40% of alerts are never investigated; 61% of teams admit ignoring alerts later proven critical.** The 20–30% figure comes from CardinalOps; the 40%/61% figures from the AI SOC Market Landscape 2025 (cited via Dropzone AI). *Confidence: Med* — report the range "20–40%"; the upper bound is a vendor-aggregated secondary citation. [VENDOR][1-SRC]

**A1-F02 — 66% of SOC teams cannot keep pace with incoming alert volume (SANS 2024 & 2025 SOC Survey).** *Confidence: High* — repeatedly corroborated across independent sources.

**A1-F03 — ~46% of all alerts are false positives (Microsoft SOC 2026 report); the SANS 2025 Detection & Response Survey found 73% of teams name false positives as their single biggest detection challenge.** *Confidence: Med* — reported via a secondary blog citing Microsoft/SANS. [VENDOR]

**A1-F04 — The average organization receives ~960 alerts/day from ~28 different security tools.** Source: AI SOC Market Landscape 2025 via Dropzone. *Confidence: Low* — single secondary source. [1-SRC]

**A1-F05 — 70% of SOC analysts with ≤5 years' experience leave their role within three years (SANS 2024 SOC Survey).** *Confidence: Med* — vendor blog citing SANS. [VENDOR]

**A1-F06 — Tier-1 triage takes roughly 15–40 minutes per alert; known false positives close in under 2 minutes, novel alerts consume 20–30+ minutes.** Sources: Dropzone, Exaforce, Strike48 (consistent). A capacity model (Prophet Security) blends to ~7 min/alert average. *Confidence: High* — consistent range across multiple independent sources.

**A1-F07 — A Tier-1 analyst processes ~20–50 alerts per shift (SANS SOC research); at 10,000 alerts/day with six analysts, that's one alert every 17 seconds if working non-stop.** *Confidence: Med.*

**A1-F08 — IBM 2025: organizations averaged 158 days to identify a breach (lowest in nine years); global breach lifecycle ~241 days; AI + automation cut the breach lifecycle by ~80 days and saved ~$1.9M per incident.** *Confidence: High* — IBM primary, methodologically robust. [VENDOR-IBM]

**A1-F09 — India breach cost was ₹195M in 2024 (all-time high then), up 9% from ₹179M in 2023; detection & escalation remained the single largest cost component, and "cost of lost business" jumped ~45% YoY.** Source: IBM India newsroom (July 31, 2024). *Confidence: High.* [VENDOR-IBM]

**A1-F10 — India breach cost hit ₹220 million in 2025 — an all-time high, 13% higher than 2024 and among the highest worldwide.** Per IBM's India newsroom (Aug 7, 2025): "the average total organizational cost of data breach in India reached an all-time high of INR 220 million in 2025 (13% higher than last year)." Only 37% of Indian orgs reported having AI access controls; nearly 60% either lack AI-governance policies or are still developing them; "shadow AI" added materially to breach cost. *Confidence: High.* [VENDOR-IBM]

**A1-F11 — India cyber-talent gap widely cited as ~3M needed vs <200K trained (~15x); DSCI estimates 67% of Indian enterprises had significant incidents in 2024–25 due to understaffed teams.** **Important caveat from verification:** the exact "3M/<200K (15x)" figure traces to a career-mentoring site (Dheya) citing ISC2, *not* to a primary ISC2 India table — and the ISC2 2025 Workforce Study itself did **not** publish a numeric workforce-gap estimate this year. Treat as "widely repeated via DSCI/career sources but unconfirmed in the primary ISC2 2025 study." *Confidence: Low–Med.* [1-SRC]

**A1-F12 — ~40,000 cybersecurity vacancies were unfilled in India (WEF, 2023); the global active workforce stalled at ~5.5M with a ~4.7M gap (ISC2 2024).** *Confidence: High.* Historical/global baseline.

**A1-F13 — IBM Cost of a Data Breach India 2026 edition: NOT FOUND** — only the 2024 and 2025 India cuts are published as of research date (the report publishes annually in late July/early August, so a 2026 edition may appear after 11 Aug 2026). *Confidence: High on the absence.*

---

## SECTION 2 — India Threat Landscape 2024–2026

**A1-F14 — CERT-In handled 15,92,917 cyber incidents in 2023** (vs 13,91,457 in 2022 and 14,02,809 in 2021). *Confidence: Med* — 2023 figure via an academic paper citing the CERT-In 2023 report; 2021–22 via MediaNama/Statista citing CERT-In. Use 2021–22 as historical baseline.

**A1-F15 — 204,844 cybersecurity incidents pertaining to government organisations were reported to CERT-In in 2023** (MoS IT Jitin Prasada, Dec 2024). *Confidence: High* — ministerial statement.

**A1-F16 — NCRP cybercrime complaints climbed 4.52 lakh (2021) → 10.29 lakh (2022) → 15.96 lakh (2023) → 22.68 lakh (2024).** Source: MHA data via multiple outlets. *Confidence: High.*

**A1-F17 — Citizen cyber-fraud financial losses reported to NCRP: ₹2,290.24 crore (2022) → ₹7,465.18 crore (2023) → ₹22,845.73 crore (2024) — a ~206% single-year jump.** Per MoS Home Affairs Bandi Sanjay Kumar's written Lok Sabha reply (July 22, 2025): losses in 2024 were "₹22,845.73 crore as compared to ₹7,465.18 crore the previous year"; combined NCRP+CFCFRMS fraud incidents reached 36,37,288 in 2024. *Confidence: High* — government data. [1-SRC on the exact ministerial quote, but corroborated by multiple press reports]

**A1-F18 — Over ₹7,000 crore saved across 23+ lakh complaints via the Citizen Financial Cyber Fraud Reporting & Management System (CFCFRMS) since 2021** (MoS Home, Rajya Sabha, Dec 2025). *Confidence: High.*

**A1-F19 — I4C's Suspect Registry (launched 10 Sep 2024) holds 11+ lakh suspect identifiers; ~24 lakh mule accounts have been flagged, preventing further losses of ₹4,631 crore.** *Confidence: High.*

**A1-F20 — Sophos "State of Ransomware 2025" (released July 4, 2025; 378 Indian orgs surveyed Jan–Mar 2025): 53% of Indian firms paid ransom (down from 65%); median ransom payment dropped 79% to US$481,636 (~₹4 crore); median demand fell 52% from US$2M to US$961,289; average recovery cost US$1.01M (down from $1.35M).** *Confidence: High* — Sophos primary. [VENDOR]

**A1-F21 — Sophos 2024 (global): 59% hit by ransomware (down from 66%); mean recovery cost $2.73M (up 50% from $1.82M in 2023); 56% paid ransom; 46% of sub-$50M-revenue orgs got seven-figure ransom demands.** *Confidence: High.* [VENDOR]

**A1-F22 — Sophos 2025 (global): mean recovery cost fell 44% to $1.53M; 53% recovered within a week (up from 35%).** *Confidence: High.* [VENDOR]

**A1-F23 — AIIMS Delhi ransomware attack (23 Nov 2022): e-hospital services down ~2 weeks; 5 of ~100 servers breached; ~40 million patient records potentially exposed; investigated by NIA as possible cyber-terrorism.** *Confidence: High* — the canonical Indian healthcare cyber-disaster; use as the anchor story. Historical baseline. [multiple sources incl. ORF]

**A1-F24 — CERT-In India Ransomware Report 2022: 51% increase in ransomware attacks across sectors including critical infrastructure.** *Confidence: Med* — cited via ORF. [1-SRC]

**A1-F25 — Star Health Insurance breach (2024): data on ~31.2M customers (7.24 TB) exposed via Telegram chatbots — names, phone numbers, addresses, tax details, ID copies, medical test results and diagnoses.** Source: Reuters (Sept 20, 2024): the hacker (alias "xenZen") "possessed 7.24 terabytes of data related to over 31 million Star Health customers," and Reuters independently downloaded documents with "names, phone numbers, addresses, tax details, copies of ID cards, test results and medical diagnoses." *Confidence: High.* **Bias flag:** Star Health publicly stated "no widespread compromise" — corporate spin conflicting with Reuters' independent verification.

**A1-F26 — C-Edge Technologies / RansomEXX ransomware (Jul–Aug 2024) forced ~300 small cooperative & regional rural banks offline (~one-fifth of India's ~1,500 such banks), disrupting NPCI-linked payment systems.** Confirmed by NPCI statement (Aug 1, 2024) and Reuters: "Nearly 300 small Indian banks... forced to go offline... The attack had affected C-Edge Technologies." CloudSEK attributed it to the RansomEXX group via a misconfigured Jenkins server (CVE-2024-23897) at Brontoo Technology Solutions, a C-Edge collaborator (C-Edge is an SBI–TCS JV). NPCI temporarily isolated C-Edge; no direct financial loss was reported. *Confidence: High.* **This is the single best India-scale, recent, cooperative-bank disaster story for the pitch.**

**A1-F27 — WazirX crypto hack (18 Jul 2024): ~$230M stolen from a multi-signature wallet; attributed to North Korea's Lazarus Group.** Source: The Record (2024). *Confidence: High.*

**A1-F28 — India banks recorded 248 successful data breaches June 2018–March 2022 (41 public-sector, 205 private, 2 overseas).** Source: Parliament data via ORF. *Confidence: Med.* Historical baseline.

---

## SECTION 3 — The Structural Gap (HIGH PRIORITY)

### 3.1 What a human SOC costs

**A1-F29 — A competent 24×7 SOC needs a minimum of 8–12 full-time analysts; personnel alone runs $1.6–2.1M/year; technology (SIEM/EDR/threat-intel/SOAR) adds $500K–$1M+; advanced SOCs exceed $2–3M/year.** Source: Expel, corroborated by securityoperationscost.com. *Confidence: High.* [VENDOR — but two independent vendor sources agree]

**A1-F30 — A single 24/7 tier-1 coverage "seat" requires 5–6 FTEs (to cover shifts, PTO, sickness, training); staffing is 65–70% of total SOC cost.** Source: securityoperationscost.com. *Confidence: Med.* [1-SRC]

**A1-F31 — India SOC-analyst salaries (2026): fresher ₹3.5–6 LPA, mid-level (L2, ~3 yrs) ₹8–15 LPA, senior/lead ₹22 LPA+; Indeed lists an average of ~₹4.75 LPA.** *Confidence: High* on the range (multiple sources; individual specialist blogs are 1-SRC). Implication: even at Indian salaries, an 8–12-analyst 24×7 SOC costs roughly ₹1–2 crore/year in payroll alone — an order of magnitude above what the target buyers can pay.

**A1-F32 — SIEM total cost of ownership: staffing is typically 2–3× the license cost; a 3-year TCO for a 200-employee firm ranges from ~$115,700 (lightweight/cloud) to ~$2,345,000 (enterprise SIEM fully staffed).** Source: Graylog TCO analysis via Blumira. *Confidence: Med.* [VENDOR]

### 3.2 What the target buyers can actually afford (India SOC-as-a-Service pricing)

**A1-F33 — Managed SOC in India: ₹25,000–₹1,00,000/month (small business); ₹1–5 lakh/month (mid-size); ₹20 lakh+/month (large enterprise).** Source: bminfotrade SOC pricing guide 2026. *Confidence: Med.* [1-SRC]

**A1-F34 — Per-device Indian managed-SOC pricing: ₹250–₹1,000/device/month; per-user ₹500–₹2,000/user/month; log-volume ₹25,000–₹2,00,000/day.** Source: bminfotrade. *Confidence: Med.* [1-SRC]

**A1-F35 — Global SOCaaS benchmarks: ~$1,000–$10,000+/month, some as low as $11/device/month; MDR/SOC market context ~$10–30 per asset/month.** Sources: UnderDefense, Vectra, Eventus, Huntress. *Confidence: Med.* [VENDOR]

**A1-F36 — Indian MSSP outcome claim: Eventus Security reports reducing MTTD by 65%+ across mid-sized BFSI clients in Mumbai/Bangalore.** *Confidence: Low* — vendor self-report, unaudited. [VENDOR][1-SRC]

**The gap in one line:** a human 24×7 SOC costs ₹1 crore+ (A1-F29/F31); the target buyers can pay ₹25k–₹1L/month = ₹3–12 lakh/year (A1-F33). An autonomous, low-headcount SOC that lives inside that price umbrella *is the product*.

### 3.3 India MSSP market size — CONFLICTING (report the range)

**A1-F37 — Third-party market-sizing firms disagree by ~10x, almost certainly due to different scope definitions (pure managed-security vs broad cyber-services):**
- Market Research Future: **$1,628M (2024) → $3,501M (2035), 7.2% CAGR**
- BlueWeave Consulting: **reaching $1,470.8M by 2029, 13.5% CAGR**
- TechSci Research: **$15.32B (2025) → $31.32B (2031), 12.49% CAGR**

*Confidence: Low.* **Do not cite a single figure.** Cite the range and flag scope ambiguity. The directional signal — double-digit growth driven by compliance mandates — is consistent and defensible; the absolute number is not.

### 3.4 Regulations that CREATE buyers for automated SOC capability

**A1-F38 — CERT-In 6-hour incident-reporting directive (28 Apr 2022, still in force): entities must report specified cyber incidents to CERT-In within 6 hours of noticing them.** *Confidence: High* — well-established; RBI and IRDAI now echo the same 6-hour clock. (Primary directive text cited via secondary regulatory summaries.)

**A1-F39 — DPDP Act 2023 + DPDP Rules 2025 (notified 13 Nov 2025): phased rollout — the Data Protection Board took effect immediately; Consent Manager registration opens 13 Nov 2026; full substantive obligations (including breach notification) become enforceable 13 May 2027.** Source: PIB + multiple legal analyses. *Confidence: High.*

**A1-F40 — DPDP penalties: up to ₹250 crore for failure to implement reasonable security safeguards (Sec 8(5)); up to ₹200 crore for failure to notify a breach (Sec 8(6)); penalties stack per violation (a single breach can reach ~₹650 crore cumulative). Breach must be notified to the Board and affected Data Principals within 72 hours; minimum 1-year log retention.** *Confidence: High.* This is the hard financial forcing-function that turns "nice-to-have monitoring" into a board-level mandate.

**A1-F41 — SEBI CSCRF (circular SEBI/HO/ITD-1/ITD_CSC_EXT/P/CIR/2024/113 dated 20 Aug 2024): mandates that ALL Regulated Entities establish a SOC (own / group / Market SOC / third-party managed); MIIs & Qualified REs must measure SOC efficacy half-yearly, others yearly; adoption deadlines 1 Jan 2025 (previously-covered REs) and 1 Apr 2025 (newly-covered REs incl. AIFs, RAs, Merchant Bankers, VCFs).** *Confidence: High.*

**A1-F42 — SEBI "Market SOC" (M-SOC): NSE & BSE are explicitly mandated to build shared SOCs *because self-SOC is cost- and expertise-prohibitive for smaller REs*.** Per the CSCRF circular: "As compliance with the cybersecurity guidelines may be onerous for smaller REs due to the lack of knowledge and expertise in cybersecurity and the cost factor involved in setting up own SOC... CSCRF mandates NSE and BSE to set up Market SOC (M-SOC)"; the M-SOC provides 24×7 monitoring, SIEM, threat intel and log retention for small-size/self-certification REs. *Confidence: High.* **This is the single strongest external validation of the entire product thesis — a national regulator has literally defined the gap the idea fills.**

**A1-F43 — RBI: banks must operate a 24×7 Cyber SOC (C-SOC) for continuous log monitoring and real-time alerting.** Baseline = Cyber Security Framework for Banks (2016); Urban Cooperative Banks brought under a graded framework (2019); NBFC IT Framework (2017, stricter for NBFCs >₹500 crore assets); consolidated Master Directions on IT Governance, Risk, Controls & Assurance (Apr 2024). Significant incidents need an initial report within 6 hours via RBI's CIMS portal. *Confidence: High.*

**A1-F44 — IRDAI Information & Cyber Security Guidelines 2023 (issued 24 Apr 2023; strengthened via a 24 Mar 2025 circular): require ICT/application logs to be collected and analysed by a 24/7 SOC; 180-day rolling log retention; cyber incidents reported to IRDAI and CERT-In within 6 hours; a mandatory Cyber Crisis Management Plan; and separation of the SOC vendor from the forensic auditor.** Source: Deloitte India (2025) + IRDAI guideline PDF. *Confidence: High.* [SOC-quote via a vendor blog interpreting IRDAI, corroborated by the official PDF and Deloitte]

**Net effect:** every one of the top-3 target segments now sits under a legal requirement to run 24×7 monitoring and to report breaches within 6–72 hours — but cannot afford the human SOC that would satisfy it. That mismatch is the market.

---

## SECTION 4 — Target User Ranking (HIGHEST PRIORITY)

Each candidate scored 1–5 on four equally-weighted axes: **Pain** (frequency/severity of incidents), **Urgency** (regulatory-deadline pressure), **Ability-to-Adopt** (budget + tech readiness + procurement simplicity), and **Judge Resonance** ("Bharat Pragati"/scale-of-impact narrative for an SIH jury of industry engineers/PMs).

| Rank | Target user | Pain | Urgency | Adopt | Judge Resonance | Total /20 |
|------|-------------|:----:|:-------:|:-----:|:---------------:|:---------:|
| 1 | Cooperative banks & small NBFCs | 5 | 5 | 4 | 5 | **19** |
| 2 | Hospitals / healthcare providers | 5 | 4 | 3 | 5 | **17** |
| 3 | SEBI-regulated small entities (brokers, AIFs, RAs) | 4 | 5 | 4 | 4 | **17** |
| 4 | Tier-2/3 enterprises & MSMEs | 5 | 3 | 3 | 4 | **15** |
| 5 | Municipal bodies / smart cities | 4 | 3 | 2 | 5 | **14** |
| 6 | Educational institutions | 3 | 2 | 3 | 3 | **11** |
| — | Government departments / PSUs | 4 | 4 | 2 | 4 | 14 (long sales cycle) |
| — | MSSPs | — | — | 5 | 4 | **CHANNEL, not end-user** |

**A1-F45 — Justification for the top 3:**

- **#1 — Cooperative banks & small NBFCs (19/20).** The C-Edge/RansomEXX attack (A1-F26) is direct, recent proof that ~300 of these institutions share fragile shared infrastructure and lack real SOCs. RBI legally requires 24×7 monitoring (A1-F43), yet they cannot afford a $1M+ human SOC (A1-F29) — and Indian SOC salaries put even a lean team at ₹1–2 crore/year (A1-F31). Maximum regulatory urgency + demonstrated pain + the most emotionally resonant "protecting the common citizen's money / Bharat Pragati" story. **This is the recommended primary hackathon skin's flagship persona.**

- **#2 — Hospitals / healthcare providers (17/20).** AIIMS (A1-F23) is the canonical Indian cyber-disaster and an instant judge-recognizable anchor; Star Health (A1-F25) shows the data-leak dimension. Hospitals hold highly sensitive data now exposed to DPDP's ₹250-crore penalties (A1-F40) but run on near-zero security budgets and staff. Highest possible life-safety resonance; scored slightly lower on adoptability (fragmented procurement, legacy systems).

- **#3 — SEBI-regulated small entities (17/20).** CSCRF (A1-F41) *legally requires* them to have a SOC by 2025, and SEBI's own Market-SOC provision (A1-F42) is an official admission that they can't afford one. This is a regulator describing the exact product gap — the cleanest "compliance-driven, deadline-backed, defensible willingness-to-pay" segment.

**A1-F46 — Top-3 exact needs & willingness-to-pay.** All three need: (a) 24×7 monitoring without hiring 8–12 analysts; (b) *automated, evidence-backed incident reporting* to the relevant regulator within the 6-hour (CERT-In/RBI/IRDAI) or 72-hour (DPDP) window; (c) affordable, predictable per-device/per-user pricing. WTP evidence: Indian managed SOC already sells at ₹25,000–₹1,00,000/month for small firms (A1-F33) and ₹250–₹1,000/device/month (A1-F34) — a price umbrella an autonomous, low-headcount SOC can profitably undercut while widening the served market to buyers priced out today.

**A1-F47 — MSSPs as the go-to-market CHANNEL, not the end-user.** MSSPs themselves are throttled by the analyst shortage (A1-F11) and margin pressure. Selling the autonomous triage/response engine B2B2X *through* MSSPs (and through SEBI's mandated Market-SOC operators) scales far faster than direct SMB sales, aligns with the sponsor-credit ecosystem, and maximizes the "business potential" judging weight. **Recommended: architect the product so it can be deployed either direct-to-institution or white-labelled inside an MSSP/Market-SOC.**

---

## SECTION 5 — Sustainability Evidence (prefix A1-F5x)

**A1-F51 — Wazuh (open-source XDR/SIEM): founded 2015 by Santiago Bassett; per Wazuh's own site, 30M+ downloads/year and 200+ professionals (Tracxn lists 281 employees, 2026); started and remained *unfunded*, sustaining itself via paid managed-cloud subscriptions and support contracts while the core stays free (GPLv2 core, Apache-2.0 dashboard).** *Confidence: High.* (Download figure has grown from ~20M in a 2024 interview to 30M+ on the current site.) **Model precedent: free open-core + paid managed cloud/support — directly transferable, and compatible with the near-₹0 budget.**

**A1-F52 — TheHive → StrangeBee: TheHive was open-sourced 2014–2016 by a bank CSIRT team; the founders co-founded StrangeBee in late 2018; in 2022, TheHive 5 shifted to a proprietary/freemium model (Community free for personal/education/basic-commercial; Gold/Platinum paid; and an explicit MSSP license for partners), retiring the AGPLv3 open version.** *Confidence: High.* **Model precedent: open-source community adoption → commercial open-core with a dedicated MSSP tier — validates A1-F47's channel strategy.**

**A1-F53 — Data/playbook flywheel precedents: Sigma (community-contributed, vendor-neutral detection rules) and MISP (threat-sharing communities coordinated via CIRCL/EU) demonstrate that community-contributed detection content and shared threat intelligence compound in value over time.** *Confidence: Med* — general domain knowledge / project spec sites (permitted as technical documentation). **Design implication: the auto-generated playbooks and detection rules should be structured as a shareable, compounding corpus (Sigma-compatible) — this is the "sustainability + future-work" moat.**

**A1-F54 — AI-SOC economics: a 2025 Cloud Security Alliance benchmark (148 SOC analysts) found AI-assisted investigations were 45% faster for cloud alerts (58 vs 105 min) and 61% faster for identity/access alerts (30 vs 78 min), with accuracy improving 22–29% (85–97% vs 63–68% for manual); 94% of participants became AI advocates after hands-on use.** Source: CSA via Dropzone. *Confidence: Med.* [1-SRC via vendor] **This is the best available quantified proof that agentic AI triage works — cite it for the "technical complexity + feasibility" criteria.**

**A1-F55 — C3iHub (IIT Kanpur): a DST NM-ICPS Technology Innovation Hub; its flagship Cybersecurity Startup Incubation Program Cohort VII offers ₹30 lakh over two years (₹20L non-equity grant + ₹10L equity-based fellowship). Between 2020–2024 it nurtured 49 startups, deployed 15+ cybersecurity products, saw 60%+ commercialize, and trained 10,000+ individuals.** *Confidence: High.* **The single most concrete non-dilutive funding + credibility runway for a post-hackathon path; explicitly designed for exactly this kind of venture.**

**A1-F56 — Cyber Surakshit Bharat (MeitY/NeGD, launched 2018): a first-of-its-kind Government–industry PPP for CISO capacity-building; by May 2024, NeGD had run 44 batches training 1,637+ CISOs and frontline IT officials.** Source: PIB (2024). *Confidence: High.* **A ready-made government adoption/distribution channel to name in the sustainability + scale-of-impact narrative.**

**A1-F57 — I4C (Indian Cyber Crime Coordination Centre, MHA): scheme approved Oct 2018 with an initial outlay of ₹415.86 crore (~$43M); runs a 6-month fully residential "Cyber Commandos" training program.** *Confidence: Med* — the ₹415.86 crore Oct-2018 outlay is well-documented; a higher "current budget" figure (~₹782 crore) appears only on Wikipedia and should be verified against a primary MHA/PIB source before use. [1-SRC on budget]

**A1-F58 — LLM inference cost per alert triaged: NOT FOUND** as a published, authoritative (especially India-specific) benchmark. The qualitative direction is that per-token inference costs have fallen sharply year-on-year, but no citable "cost per alert" figure exists. *Confidence: High on the gap.* **Recommendation:** derive your own unit-economics estimate in the deck from token counts × current model pricing (with Claude/Bedrock as the intelligence layer) rather than citing a third-party number — and present it as an [INFERENCE], not a fact.

---

## Contradictions & Disputes Found
- **India MSSP market size (A1-F37):** MRF (~$1.6B, 2024), BlueWeave (~$1.47B by 2029), and TechSci ($15.3B, 2025) disagree by roughly 10x — near-certainly different scope definitions (narrow MSS vs broad cyber-services). Cite the range, not a point estimate.
- **Sophos recovery-cost trend:** the *global* mean recovery cost rose to $2.73M (2024) then fell to $1.53M (2025); the *India* 2025 figure is ~$1.01M. Use the India figure for India claims (A1-F20), never the global one.
- **Alerts-never-investigated (A1-F01):** ranges 20–30% (CardinalOps) to 40% (AI SOC Landscape 2025). Report as "20–40%."
- **Star Health (A1-F25):** Reuters-verified 31M-record/7.24TB leak vs the company's public "no widespread compromise" statement — a corporate-spin conflict, flagged.
- **India talent gap (A1-F11):** the headline "3M/<200K/15x" is widely repeated but is **not** confirmed in the primary ISC2 2025 study, which dropped its numeric gap estimate this year. Present it as a widely-cited estimate, hedged.

## What I Could NOT Verify (honest gaps)
- **IBM Cost of a Data Breach India 2026 edition (A1-F13)** — not yet published as of research date.
- **LLM inference cost per alert (A1-F58)** — no authoritative benchmark exists; derive your own.
- **Primary ISC2 2025 India source for "3M needed / <200K trained" (A1-F11)** — only secondary citations located; the primary study omitted the numeric gap.
- **CERT-In full-year 2024 & 2025 incident totals** — not confirmed as official annual figures (web-search budget was exhausted before confirmation).
- **Exact primary text of the CERT-In April 2022 6-hour directive (A1-F38)** — cited via secondary regulatory summaries, not the primary PDF.
- **I4C "current" budget (A1-F57)** — only the Oct-2018 ₹415.86 crore outlay is firmly sourced; the higher figure is Wikipedia-only.

## Top 10 Findings That Should Shape THE IDEA (by ID)
1. **A1-F42** — SEBI literally created a "Market SOC" because small entities can't afford one: a national regulator has defined your product gap. *Lead with this.*
2. **A1-F26** — C-Edge/RansomEXX (~300 cooperative banks offline) = concrete, recent, India-scale disaster story and your #1 persona's origin.
3. **A1-F11** — the ~15x talent gap makes *autonomous* (not merely AI-assisted) triage a necessity — the reason for a multi-agent swarm.
4. **A1-F40** — DPDP's ₹250-crore penalty + 72-hour breach notice = the hard financial forcing-function that manufactures buyers by May 2027.
5. **A1-F10** — ₹220M India breach cost (2025 record) + the AI-governance gap = quantified, IBM-sourced urgency.
6. **A1-F01 / A1-F02 / A1-F06** — 20–40% of alerts never investigated, 66% of teams can't keep pace, 15–40 min/alert = the precise pain the swarm eliminates.
7. **A1-F29 vs A1-F33/34** — $1M+ human SOC vs ₹25k/month affordability ceiling = the economic wedge; put both numbers on one slide.
8. **A1-F44 / A1-F43 / A1-F38** — a common 6-hour reporting clock across CERT-In/RBI/IRDAI makes *auto-generated, evidence-backed incident reports* a killer, cross-sector feature.
9. **A1-F55 / A1-F56** — C3iHub ₹30-lakh grant + Cyber Surakshit Bharat = a concrete, nameable post-hackathon sustainability & funding runway.
10. **A1-F51 / A1-F52 / A1-F54** — Wazuh & TheHive/StrangeBee prove the open-core → commercial survival model, and the CSA benchmark proves agentic triage actually works.

## Numbers & Facts Bank

| ID | Stat | Year | Source (domain) | Confidence |
|----|------|------|-----------------|-----------|
| A1-F01 | 20–40% of alerts never investigated; 61% ignored critical | 2025 | CardinalOps / AI SOC Landscape via dropzone.ai | Med |
| A1-F02 | 66% of SOC teams can't keep pace | 2024/25 | SANS SOC Survey (via dropzone.ai, worldinformatixcs.com) | High |
| A1-F03 | ~46% of alerts are false positives; 73% cite FPs as top challenge | 2025/26 | Microsoft SOC / SANS (via worldinformatixcs.com) | Med |
| A1-F04 | ~960 alerts/day from ~28 tools | 2025 | AI SOC Landscape via dropzone.ai | Low |
| A1-F05 | 70% of ≤5-yr analysts leave within 3 yrs | 2024 | SANS via dropzone.ai | Med |
| A1-F06 | 15–40 min tier-1 triage per alert | 2025/26 | dropzone.ai / exaforce.com / strike48.com | High |
| A1-F07 | 20–50 alerts per analyst per shift | 2025 | SANS via unihackers.com / networkershome.com | Med |
| A1-F08 | 158 days to identify; AI saves ~$1.9M / ~80 days | 2025 | IBM via cyberhaven.com | High |
| A1-F09 | India breach cost ₹195M (+9%) | 2024 | in.newsroom.ibm.com | High |
| A1-F10 | India breach cost ₹220M (+13%, record) | 2025 | in.newsroom.ibm.com | High |
| A1-F11 | ~3M needed vs <200K trained (~15x) — hedged | 2025 | ISC2 via dheya.com (primary unconfirmed) | Low–Med |
| A1-F12 | ~40,000 India vacancies (WEF); 5.5M workforce / 4.7M gap | 2023/24 | entrepreneur.com / isc2.org | High |
| A1-F14 | CERT-In handled 15,92,917 incidents | 2023 | ijirt.org citing CERT-In | Med |
| A1-F15 | 204,844 govt-org incidents | 2023 | deccanherald.com (MoS IT) | High |
| A1-F16 | NCRP complaints 22.68 lakh | 2024 | MHA via the420.in / industrialeconomist.com | High |
| A1-F17 | NCRP fraud losses ₹22,845.73 crore (+206%) | 2024 | MoS Home, Lok Sabha (via business-standard / the420.in) | High |
| A1-F18 | ₹7,000+ crore saved, 23+ lakh complaints (CFCFRMS) | 2025 | newsonair.gov.in | High |
| A1-F19 | Suspect Registry 11L+ IDs; 24L mule accounts | 2024 | angelone.in / industrialeconomist.com | High |
| A1-F20 | India ransom median $481,636; recovery $1.01M; 53% paid | 2025 | Sophos (theweek.in / sophos.com) | High |
| A1-F21 | Global recovery $2.73M; 59% hit; 56% paid | 2024 | sophos.com | High |
| A1-F22 | Global recovery fell to $1.53M | 2025 | sophos.com | High |
| A1-F23 | AIIMS ~40M records, ~2 weeks down | 2022 | orfonline.org / multiple | High |
| A1-F24 | +51% ransomware attacks (CERT-In) | 2022 | orfonline.org | Med |
| A1-F25 | Star Health 31.2M customers / 7.24 TB | 2024 | reuters.com | High |
| A1-F26 | C-Edge/RansomEXX ~300 banks offline | 2024 | reuters.com / NPCI | High |
| A1-F27 | WazirX ~$230M stolen (Lazarus) | 2024 | therecord.media | High |
| A1-F28 | 248 bank breaches Jun2018–Mar2022 | 2022 | orfonline.org (Parliament) | Med |
| A1-F29 | 24×7 SOC: 8–12 analysts, $1M+/yr | 2025/26 | expel.com / securityoperationscost.com | High |
| A1-F30 | 24/7 seat = 5–6 FTEs; staffing 65–70% | 2026 | securityoperationscost.com | Med |
| A1-F31 | India SOC salary ₹3.5–22 LPA; avg ~₹4.75 LPA | 2026 | indeed.com / networkershome.com | High |
| A1-F32 | SIEM 3-yr TCO $115.7K–$2.35M | 2025 | Graylog via blumira.com | Med |
| A1-F33 | India managed SOC ₹25k–₹1L/mo (small) | 2026 | bminfotrade.com | Med |
| A1-F34 | ₹250–₹1,000/device/month | 2026 | bminfotrade.com | Med |
| A1-F35 | Global SOCaaS $1k–$10k+/mo; from $11/device | 2026 | underdefense.com / vectra.ai | Med |
| A1-F37 | India MSS market $1.47B–$15.3B (CONFLICT) | 2024/25 | marketresearchfuture / blueweave / techsci | Low |
| A1-F38 | CERT-In 6-hour reporting directive | 2022 | secondary regulatory summaries | High |
| A1-F39 | DPDP Rules notified 13 Nov 2025; full 13 May 2027 | 2025 | pib.gov.in / ipleaders.in | High |
| A1-F40 | DPDP ₹250 cr penalty; 72-hr notice; 1-yr logs | 2025 | seclore.com / matters.ai / pib | High |
| A1-F41 | SEBI CSCRF SOC mandate; deadlines 2025 | 2024 | SEBI circular (lexology / taxguru) | High |
| A1-F42 | SEBI Market SOC (NSE/BSE) for small REs | 2024 | SEBI/CSCRF (irglobal / taxguru) | High |
| A1-F43 | RBI 24×7 C-SOC + 6-hr CIMS report | 2016–2024 | getastra.com / fluxforce.ai / myitmanager.in | High |
| A1-F44 | IRDAI 24/7 SOC, 180-day logs, 6-hr report | 2023/25 | deloitte.com / IRDAI PDF | High |
| A1-F51 | Wazuh 30M+ downloads/yr, unfunded, ~281 staff | 2026 | wazuh.com / tracxn.com | High |
| A1-F52 | TheHive→StrangeBee open-core shift + MSSP tier | 2022 | strangebee.com | High |
| A1-F53 | Sigma / MISP community flywheel precedent | 2024/26 | project spec sites | Med |
| A1-F54 | AI triage 45–61% faster, +22–29% accuracy (CSA, n=148) | 2025 | CSA via dropzone.ai | Med |
| A1-F55 | C3iHub ₹30L grant; 49 startups, 60%+ commercialized | 2025 | iitk.ac.in | High |
| A1-F56 | Cyber Surakshit Bharat 1,637+ CISOs, 44 batches | 2024 | pib.gov.in | High |
| A1-F57 | I4C ₹415.86 cr outlay (2018); Cyber Commandos 6-mo | 2018 | MHA/Wikipedia + c3ihub.org | Med |
| A1-F58 | LLM inference cost per alert | — | NOT FOUND | High (gap) |

---

### Bottom line for THE IDEA
The research **validates and sharpens** the working direction. The domain-agnostic "Autonomous Incident Intelligence Engine," skinned as a Cyber SOC, is aimed at a market where (a) the pain is quantified and record-high (A1-F10, F17), (b) a national regulator has *explicitly* declared that small entities cannot afford the human SOC they are now legally required to run (A1-F42) — the strongest possible external endorsement of the concept, and (c) proven open-core sustainability models and government funding rails (A1-F51/F52/F55/F56) support the "sustainability + business-potential" criteria.

**Recommended positioning:** lead the Round-1 idea with the **cooperative-bank persona** (C-Edge story + RBI mandate + Bharat Pragati resonance), make **auto-generated 6-hour/72-hour regulatory incident reports** the signature feature that no human-SOC competitor can match on cost, price it *inside* the ₹25k–₹1L/month Indian affordability band, and cite **SEBI's Market SOC** as third-party proof the market has already been defined by the state. Position **MSSPs/Market-SOC operators as the scaling channel**, and cite **C3iHub + Cyber Surakshit Bharat** as the concrete post-hackathon runway. Present LLM unit economics as your own [INFERENCE] (A1-F58 gap), and hedge the talent-gap headline (A1-F11).