# India's Cyber-Incident Compliance Burden: Is "Auto-Drafted Regulator-Ready Reporting" a Winning Differentiator for Decode SIH 2026 Track 3 PS4?

## Executive Summary
- India runs the world's most aggressive cyber-incident reporting regime: CERT-In's 6-hour clock (2022), stacked with DPDP's 72-hour Data Protection Board report (Rules notified 13 Nov 2025), plus sector overlays from RBI, SEBI, IRDAI, CEA, and NCIIPC. A single breach can trigger 3+ separate filings on different clocks. [COMP-F01, COMP-F17]
- Verdict: "auto-drafted regulator-ready reporting" is a WINNING DIFFERENTIATOR for this hackathon, but only if scoped as auto-draft-plus-human-in-the-loop, because no tool today verifiably auto-populates the specific CERT-In or DPDP forms from SOC incident data. [COMP-F20, COMP-F21]
- The gap is real: CERT-In accepts reports only by email/phone/fax with a non-mandatory PDF form; there is no public API, no corroborated CERT-In "CIMS" submission portal, and no STIX/TAXII/IODEF acceptance. Machine-to-machine submission is absent. [COMP-F14, COMP-F22]
- The pain is large and measurable: IBM's Cost of a Data Breach Report 2025 found the average total organizational cost of a data breach in India reached an all-time high of INR 220 million in 2025, up 13% from INR 195m in 2024, and PIB reports cybersecurity incidents surged from 10.29 lakh in 2022 to 22.68 lakh in 2024. [COMP-F15, COMP-F16]
- Penalties escalate the stakes: CERT-In non-compliance is up to 1 lakh rupees + 1 year imprisonment (the Jan Vishwas Bill 2023 proposes raising the fine to up to 1 crore); DPDP exposes up to 250 crore (safeguards failure) + 200 crore (notification failure), and these stack per instance. [COMP-F06, COMP-F10, COMP-F11]
- Most report fields ARE machine-draftable from a resolved incident record (who, when detected, what happened, affected systems, IPs, actions taken); the residual human-judgment fields are legal characterization, data-principal consequences, and sign-off. [COMP-F18, COMP-F19]
- Existing SOAR/SIEM/GRC tools (Cortex XSOAR, Securonix, ManageEngine Log360, Sprinto, Scrut) offer generic case management, alerting, and static breach-notification templates, but not India-form auto-population from incident data. BreachRx is closest globally but generic. [COMP-F13, COMP-F20]
- DPDP requires notifying every affected data principal with no materiality threshold (unlike GDPR), a distinctive India obligation that multiplies notification volume and strengthens the automation case. [COMP-F09]
- Dual/triple reporting is explicitly acknowledged by practitioners: notifying one regulator does not satisfy another; each expects its own format and channel. This fragmentation is exactly what a domain-agnostic engine can normalize. [COMP-F12, COMP-F17]
- Biggest risk to the idea: regulators may not accept machine-drafted reports as-filed and liability sits with the filer, so the demo must show human review/approval and an immutable audit trail, not full autonomy. [COMP-F21, COMP-F23]

## 1. CERT-In 2022 Directions in Operational Detail

**Legal basis and effective date.** CERT-In issued Directions No. 20(3)/2022-CERT-In on 28 April 2022 under Section 70B(6) of the IT Act, 2000, effective 60 days later (27/28 June 2022). This is verified against the CERT-In primary PDF. [COMP-F01] Confidence: High (primary source).

**Who must report (covered entities).** Verbatim: "Any service provider, intermediary, data centre, body corporate and Government organisation." The wording is broad enough to cover essentially every organization operating IT systems in India. Specific extra obligations fall on Data Centres, VPS providers, Cloud Service providers, and VPN Service providers, plus virtual asset service/exchange/custodian wallet providers. [COMP-F02] Confidence: High (primary).

**The 6-hour timeline and trigger.** Direction (ii): entities "shall mandatorily report cyber incidents as mentioned in Annexure I to CERT-In within 6 hours of noticing such incidents or being brought to notice about such incidents." The trigger is awareness/notice, not completion of investigation. FAQs clarify entities may provide information available at time of reporting and supplement later within a reasonable period. [COMP-F03] Confidence: High (primary + FAQ commentary).

**Reportable incident types (Annexure I, 20 categories).** Verbatim from the primary PDF: (i) targeted scanning/probing of critical networks/systems; (ii) compromise of critical systems/information; (iii) unauthorised access of IT systems/data; (iv) website defacement or intrusion and unauthorised changes such as inserting malicious code/links; (v) malicious code attacks (virus/worm/Trojan/Bots/Spyware/Ransomware/Cryptominers); (vi) attacks on servers (Database, Mail, DNS) and network devices (Routers); (vii) identity theft, spoofing and phishing; (viii) DoS and DDoS; (ix) attacks on critical infrastructure, SCADA, OT and wireless networks; (x) attacks on applications (E-Governance, E-Commerce); (xi) data breach; (xii) data leak; (xiii) attacks on IoT devices; (xiv) attacks affecting digital payment systems; (xv) attacks through malicious mobile apps; (xvi) fake mobile apps; (xvii) unauthorised access to social media accounts; (xviii) attacks affecting cloud computing systems; (xix) attacks affecting Big Data, Blockchain, virtual assets, exchanges, custodian wallets, Robotics, 3D/4D printing, additive manufacturing, drones; (xx) attacks affecting AI and ML systems. [COMP-F04] Confidence: High (primary).

**Report fields / format / channels.** Channels per the Directions: email (incident@cert-in.org.in), Phone (1800-11-4949), and Fax (1800-11-6969); methods/formats are also published on cert-in.org.in. The Incident Reporting Form (certinirform.pdf) collects: reporting party identity, organisation details, incident classification/type, date/time of occurrence and detection, affected systems/assets, IP addresses, symptoms observed, actions taken, and contact info. The form explicitly states filling/signing it is NOT mandatory; relevant information may be provided in free-form communication. [COMP-F05] Confidence: High (primary form + Directions).

**Penalties (Section 70B(7)).** Non-compliance can invite imprisonment up to 1 year and/or fine up to INR 1,00,000 (1 lakh). The Jan Vishwas (Amendment of Provisions) Bill, 2023 proposed raising the fine to up to INR 1 crore (not yet in force as of research). [COMP-F06] Confidence: High (multiple legal sources + primary Direction reference).

**Log retention, NTP, KYC.** Direction (iv): enable logs of all ICT systems, maintained securely for a rolling 180 days, within Indian jurisdiction. Direction (i): sync all ICT clocks to NIC/NPL NTP servers. Direction (v): Data Centres/VPS/Cloud/VPN providers must register and retain subscriber KYC (validated names, hire period, IPs allotted, email/IP/timestamp at onboarding, purpose, validated address/contacts, ownership) for 5 years after cancellation. Direction (vi): virtual asset providers retain KYC and transaction records 5 years. [COMP-F07] Confidence: High (primary).

**FAQ clarifications.** CERT-In's FAQs clarified: enterprise/corporate VPNs are exempt from the subscriber-log mandate; logs may be stored outside India (with an indicative list of ICT logs); the 6-hour rule applies to Annexure I incidents; and information available at reporting time suffices with later supplementation. [COMP-F08] Confidence: High (Saikrishna summary of official FAQ).

**Compliance-rate reality and VPN exits.** Multiple no-log VPN providers physically removed India servers rather than comply: ExpressVPN, Surfshark, NordVPN, Proton VPN, Hide.me, and IPVanish (mid-2022). CERT-In extended the enforcement deadline to 25 September 2022 after industry pushback (TechCrunch). In January 2025, I4C reportedly ordered Apple/Google to remove certain VPN apps from Indian stores. Underreporting is widely acknowledged (DSCI/NASSCOM 2024 commentary). No widely-published monetary enforcement action under 70B(7) has surfaced; MeitY issued a notice to Apple over a state-sponsored-attack warning. [COMP-F24] Confidence: Med-High (quality press; enforcement-absence is an inference from lack of published cases).

## 2. DPDP Act 2023 + DPDP Rules 2025 Status

**Rules status.** DPDP Rules 2025 were officially notified on 13 November 2025, starting an approximately 18-month enforcement runway; core breach-notification obligations (Rules 6 and 7) become fully enforceable around May 2027 under phased implementation, with full compliance required by mid-May 2027 (Fisher Phillips; Matters.ai). [COMP-F17a] Confidence: High (multiple 2025-2026 sources).

**Two-stage breach notification (Rule 7 operationalizing Section 8(6)).** Stage 1: on becoming aware, notify the Data Protection Board of India "without delay" with a description including nature, extent, timing, and location of the breach and its likely impact; also notify affected Data Principals. Stage 2: within 72 hours (extendable on written request), submit an updated/detailed report covering broad facts and causes, mitigation measures taken/proposed, findings on the person who caused it, steps to prevent recurrence, and a summary of notifications sent to data principals. The clock starts at awareness, not investigation completion, and runs continuously including weekends and holidays. [COMP-F09a] Confidence: High (Rule 7 text via multiple sources).

**Data-principal notification (no materiality threshold).** Unlike GDPR (which allows skipping individual notice for low-risk breaches under Article 34), DPDP requires notifying every affected data principal regardless of severity, in plain language: description of the breach, data exposed, protective measures the principal can take, and Fiduciary contact details. [COMP-F09] Confidence: High.

**Penalty schedule (Schedule to the Act).** Up to 250 crore for failure to implement reasonable security safeguards (Section 8(5)); up to 200 crore for failure to notify the Board/Data Principals (Section 8(6)); up to 200 crore for children's-data violations (Section 9); up to 150 crore for Significant Data Fiduciary obligation failures (Section 10); up to 50 crore residual; up to 10,000 for data-principal duty breaches (Section 15). Penalties are fixed-rupee ceilings (not turnover-based), assessed per instance, and STACK: one incident can combine 250cr + 200cr exposure. [COMP-F10, COMP-F11] Confidence: High (multiple sources; Schedule).

**Evidence/artifacts an organization must produce.** Breach description (nature/extent/timing/location), likely consequences to data principals, mitigation and remedial measures, findings on cause/actor, steps to prevent recurrence, contact person, and a summary of data-principal notifications. Practitioners recommend an immutable audit log proving detection time, report time, and actions taken as the Fiduciary's defense before the Board. [COMP-F19] Confidence: High.

**Significant Data Fiduciary obligations.** SDFs (designated by the Government on volume/sensitivity criteria) carry additional obligations (DPIAs, data audits, appointment of a DPO and independent auditor); failure carries up to 150 crore exposure. [COMP-F10] Confidence: High.

**Interplay with CERT-In (dual/triple burden).** The DPDP obligation does NOT replace CERT-In's 6-hour IT Act obligation. A single personal-data breach triggers: CERT-In (6 hours), the DPDP Board (without delay + 72-hour detailed report), and data principals, plus any sector regulator. Practitioners repeatedly stress notifying one does not satisfy another. [COMP-F12, COMP-F17] Confidence: High.

## 3. Sector Overlays

**RBI (banks).** Cyber Security Framework (circular DBS.CO/CSITE/BC.11/33.01.001/2015-16, 2 June 2016): board-approved policy, 24/7 SOC (C-SOC), a Cyber Crisis Management Plan (CCMP), and reporting of incidents to RBI's CSITE cell within 2 to 6 hours of detection. The April 2024 Master Directions on IT Governance, Risk, Controls and Assurance Practices consolidated requirements, made the CCMP mandatory for all covered entities, and tightened significant-incident reporting to within 6 hours. NBFCs are covered via the November 2023 IT Governance Master Direction, tiered by NBFC layer (Base/Middle/Upper). [COMP-F25] Confidence: High.

**SEBI (CSCRF, 20 August 2024).** Consolidated framework issued via SEBI/HO/ITD-1/ITD_CSC_EXT/P/CIR/2024/113 dated 20 August 2024, a 205-page master document replacing the earlier "Broad Guidelines on Cyber Security and Cyber Resilience" (2015/2018). Five resilience goals (Anticipate, Withstand, Contain, Recover, Evolve); applies to roughly 22 categories of Regulated Entities (MIIs, brokers, DPs, AMCs, KRAs, RTAs, portfolio managers, etc.) on a graded/tiered basis. Incident reporting: report to SEBI and CERT-In within 6 hours of detection; full details on the SEBI Incident Reporting Portal within 24 hours; forensic/root-cause report for High/Critical incidents within 75 days. A SOC is required for all tiers above Self-Certification; smaller REs may use the exchange-operated Market SOC (M-SOC); RTAs with fewer than 100 clients are exempt from the SOC/M-SOC requirement. CSCRF came into force 1 January 2025 for entities with a prior SEBI cyber circular and 1 April 2025 for the rest, with SEBI granting deadline extensions on 28 March 2025 and again later in 2025 (e.g., other REs extended to 31 August 2025). [COMP-F26] Confidence: High.

**IRDAI (Information and Cyber Security Guidelines 2023, 24 April 2023).** Applies to insurers, intermediaries, and repositories. Under policy 2.10 "Incident and Problem Management," para 3.5: "Organization shall mandatorily report cyber-incidents to Cert-In within 6 hours of noticing or being brought to notice about such incidents with a copy to IRDAI and other concerned regulators/authorities." A 13 June 2023 circular reprimanded REs for not adhering to the 6-hour timeline and for not copying IRDAI. VAPT is required twice yearly, with annual audit by CERT-In empanelled auditors. [COMP-F27] Confidence: High.

**CEA / power sector.** CEA (Cyber Security in Power Sector) Regulations were framed under Section 177 of the Electricity Act, 2003; the draft was issued in 2024 (building on the 2021 Guidelines). Establishes CSIRT-Power (operational since April 2023) plus sectoral CERTs (thermal, hydro, transmission, distribution, grid operation, renewables). Mandates a CISO + Alternate CISO (Indian nationals), a CCMP, and reporting of incidents to CSIRT-Power, CERT-In, and NCIIPC within prescribed timeframes; sabotage classified as a cyber incident must be reported within 24 hours. Requires bi-annual IT audits and an annual OT audit. [COMP-F28] Confidence: High (draft-status caveat).

**NCIIPC (protected systems / CII).** Under Section 70A, NCIIPC protects Critical Information Infrastructure. Designated entities must nominate a 24x7 SPOC/CISO, report incidents (free-form acceptable for the initial window with the structured NCIIPC form to follow within 24 hours), and submit a detailed root-cause/remediation report within 30 days; CII validation audit at least every two years; toll-free help desk 1800-11-4430. Power-sector CISOs must report sabotage on Protected Systems to NCIIPC within 24 hours of occurrence. [COMP-F29] Confidence: Med-High (guidance documents, some non-statutory).

**Comparative table (regulator | covered entity | trigger | timeline | channel/format | penalty).**

| Regulator | Covered entity | Trigger | Timeline | Channel/format | Penalty |
|---|---|---|---|---|---|
| CERT-In | All service providers/intermediaries/data centres/body corporates/govt | Awareness of Annexure I incident | 6 hours | Email/phone/fax + PDF form | Up to 1 lakh + 1 yr (proposed up to 1 crore) |
| DPDP / DPB | Data Fiduciaries | Awareness of personal data breach | Without delay + 72-hr detailed report | Board (per Rules) + data principals | Up to 250cr + 200cr (stackable) |
| RBI | Banks, NBFCs | Detection of incident | 2 to 6 hours (6 hr tightened 2024) | CSITE cell | Supervisory action, monetary penalties |
| SEBI | ~22 RE categories | Detection | 6 hr to SEBI+CERT-In; 24 hr full; 75 days forensic | SEBI Incident Reporting Portal | Daily penalties, trading restrictions |
| IRDAI | Insurers/intermediaries | Noticing | 6 hours (to CERT-In, copy IRDAI) | CERT-In + IRDAI | Inspection/enforcement |
| CEA/CSIRT-Power | Power-sector responsible entities | Detection; sabotage | Prescribed; 24 hrs for sabotage | CSIRT-Power + CERT-In + NCIIPC | Under Electricity Act |
| NCIIPC | CII/protected systems | Detection; sabotage | Initial window + structured form 24 hrs; 30-day RCA | NCIIPC form/portal, secure email | Directions under 70A |

[COMP-F30] Confidence: High (compiled from above).

## 4. Today's Reality: How Reports Get Produced and the Tooling Landscape

**Who writes reports today.** Manual and human-driven: SOC analysts assemble the technical facts; CISOs/DPOs decide reportability and sign off; legal/compliance draft the regulator-facing language. Practitioners repeatedly recommend pre-drafted templates so teams "fill in facts" rather than write from scratch at hour 50 of an incident. [COMP-F13a] Confidence: High.

**Cost/scale of the burden.** IBM's Cost of a Data Breach Report 2025 (press release, Bengaluru, 7 August 2025) states: "the average total organizational cost of data breach in India reached an all-time high of INR 220 million in 2025 (13% higher than last year)," the highest worldwide, up from INR 195m (2024) and INR 179m (2023). The same report notes "The India average breach lifecycle...dropped to 263 days, a 15-day reduction from 2024," with the research sector costliest at INR 289m, transportation at INR 288m, and industrial at INR 264m. On incident volume, PIB's "Curbing Cyber Frauds in Digital India" (PRID 2176146) states: "The surge in cybersecurity incidents from 10.29 lakh in 2022 to 22.68 lakh in 2024 reflects the growing scale and complexity of digital threats in India"; CERT-In separately recorded 1,592,917 incidents in 2023 (Lok Sabha), and PIB (NoteId 157049) reports that "In 2025, CERT-In handled over 29.44 lakh cyber incidents, issuing 1,530 alerts, 390 vulnerability notes, and 65 advisories." Critically for this idea, IBM 2025 found that "using AI and security automation less than halved the cost of a data breach. Yet despite the proven benefit, 73% of those surveyed reported limited or no use of AI and security automation." [COMP-F15, COMP-F16] Confidence: High (IBM primary press + PIB/Lok Sabha).

**Published time/cost PER REPORT.** NOT FOUND: no DSCI, vendor, or law-firm figure quantifying analyst-hours or rupee cost to prepare a single CERT-In or DPDP report. Only qualitative statements exist (report prep "can consume the 6-hour window"), plus program-level implementation cost ranges (SME CERT-In setup cited at INR 50,000-5 lakh; DPDP GRC platforms ~INR 4-5 lakh/year). This is itself a finding: the burden is universally described as heavy but has never been quantified per-report, leaving room for the team to instrument and publish its own baseline in the demo. [COMP-F31] Confidence: High (documented absence).

**Tooling landscape (the gap check).**
- Generic SOAR/SIEM: Cortex XSOAR, Securonix SOAR, Splunk SOAR, and IBM QRadar SOAR provide alert ingestion, playbooks, case management, and auto-documentation, but NO pre-built CERT-In-form or DPDP-Board-report content pack was found in their marketplaces/docs. ManageEngine Log360 markets CERT-In 6-hour readiness via detection/alerting, not form auto-drafting. [COMP-F13] Confidence: High.
- Indian GRC (Sprinto, Scrut, VComply, Consentin): DPDP control mapping, DSAR workflows, and static breach-notification templates/policies; "breach notification automation" here is workflow/procedure, not incident-data-driven form population. [COMP-F20a] Confidence: High.
- BreachRx (global): the closest. It generates tailored regulatory-notification formats and lists CERT-In as a supported regulation, but it is generic (response-plan and notification generation), not CERT-In-form field population from SOC data. One small Indian vendor (CreativeCyber) markets an AI that "draft[s] a compliant initial report from the incident details in under 30 seconds," but this is an unverified marketing claim on a blog, not a demonstrably shipped product. [COMP-F20] Confidence: Med (vendor marketing).
- Sequretek, CloudSEK: XDR/SOAR and threat-intel respectively (CloudSEK signed an MoC with CERT-In for threat-intel collaboration); NOT FOUND for report auto-drafting. [COMP-F13] Confidence: High.

**CERT-In's own tooling / machine submission.** Submission is manual: email/phone/fax + the non-mandatory PDF form. There is NO confirmed public API, NO corroborated CERT-In "CIMS" incident-submission portal (a few practitioner blogs reference notifying CERT-In "through the CIMS portal," but this is not corroborated by CERT-In primary sources; treat as disputed), and NO evidence CERT-In accepts STIX/TAXII or IODEF for incident reporting. By contrast, SEBI does operate an Incident Reporting Portal for its REs, so channel maturity varies by regulator. [COMP-F14, COMP-F22] Confidence: Med-High (documented absence + disputed CIMS reference).

## 5. Feasibility of Auto-Generation (Field Mapping)

Given a resolved incident's structured data (alerts, entities, timeline, MITRE ATT&CK mapping, affected assets, IOCs, actions taken), most report fields are machine-draftable; a minority need human/legal judgment.

**(a) CERT-In Incident Reporting Form field mapping:**
- Reporting party / org details -> standing org profile -> YES (pre-populated); no human review beyond validity.
- Contact / Point of Contact -> Annexure II PoC record -> YES.
- Incident type/classification (Annexure I category) -> triage/threat-classification agent output + ATT&CK mapping -> PARTIAL (auto-suggest; human confirms legal category, since category drives the obligation).
- Date/time of occurrence and detection -> SIEM/timeline -> YES (from immutable logs).
- Affected systems/assets, hostnames, locations -> asset inventory + correlation -> YES.
- IP addresses / IOCs -> enrichment/threat-intel agent -> YES.
- Symptoms observed -> alert narrative -> YES (draft), light human review.
- Actions taken -> response-agent action log / playbook execution -> YES.
- Impact / severity -> correlation + business context -> PARTIAL (needs human business-impact judgment).
[COMP-F18] Confidence: High (form fields are primary-sourced; the mapping is INFERENCE).

**(b) DPDP Board breach report content mapping (Rule 7):**
- Nature/extent/timing/location of breach -> incident timeline + scope -> YES (draft).
- Categories and approximate number of data principals affected -> data-map + affected-asset correlation -> PARTIAL (depends on data-inventory quality).
- Likely consequences to data principals -> legal/privacy judgment -> NO (human).
- Mitigation/remedial measures taken/proposed -> response log -> YES (draft), human confirm.
- Findings on cause/person responsible -> forensic output -> PARTIAL.
- Measures to prevent recurrence -> playbook/knowledge agent -> PARTIAL.
- Contact person / DPO -> standing profile -> YES.
- Summary of data-principal notifications sent -> notification-system log -> YES.
- Data-principal plain-language notice -> knowledge/LLM agent -> PARTIAL (draft; legal sign-off + named executive required).
[COMP-F19] Confidence: High (content items primary-sourced; the mapping is INFERENCE).

**Structured standards that help.** STIX/TAXII (OASIS) for threat intel, OCSF for normalized events, and IODEF (RFC 7970) for CSIRT incident exchange can internally normalize incident data and auto-feed report fields. HOWEVER, CERT-In does not (per available evidence) accept any of these as a submission format, so the engine's value is in DRAFTING for human review + manual submission, not machine filing. [COMP-F22] Confidence: Med-High.

**Net feasibility [INFERENCE]:** Roughly 70-80% of CERT-In form fields and roughly 50-60% of DPDP report content are credibly auto-draftable from a resolved incident record; the remainder is legal characterization, consequence assessment, and sign-off, which mandates human-in-the-loop. This is a strong, demoable feasibility profile: high enough to impress, honest enough to survive scrutiny. [COMP-F18, COMP-F19] Confidence: Med (inference).

## 6. Verdict

**"Auto-drafted regulator-ready reporting" is a WINNING DIFFERENTIATOR for Decode SIH 2026 Track 3 PS4, conditional on human-in-the-loop framing.** Justification:

1. Burden size/pain (scale of impact): The regime is uniquely severe (6-hour CERT-In + 72-hour DPDP + sector overlays), incidents are at 22.68 lakh/year and CERT-In handled 29.44 lakh in 2025, breach cost is INR 220m, and yet 73% of Indian orgs make limited/no use of AI/automation. The reporting task is manual, time-boxed, and high-stakes. [COMP-F01, COMP-F15, COMP-F16, COMP-F17]

2. Absence of existing solutions (novelty): No tool verifiably auto-populates the CERT-In or DPDP forms from incident data; SOAR/GRC offer generic case management and static templates only. This is a genuine open gap, not a crowded space. [COMP-F13, COMP-F20, COMP-F14]

3. Feasibility of a credible demo: Most fields map directly from a resolved incident record; a live demo can show a resolved incident auto-producing a CERT-In draft + a DPDP Board draft + a data-principal notice, each awaiting one-click human approval. [COMP-F18, COMP-F19]

4. Alignment with judging criteria: novelty (open gap), feasibility (high field-mapping), scale of impact (every India org + all regulated sectors), and business potential (compliance automation is a paid GRC category; India-specific auto-drafting is unserved). [COMP-F13, COMP-F30]

5. Risks: regulators may not accept machine-drafted reports as-filed; legal liability sits with the filer; the human-judgment fields (legal category, consequences, sign-off) cannot be fully automated; and no CERT-In API means submission stays manual. Mitigate by positioning as "draft + human approve + immutable audit trail + one-click export to each channel," never "autonomous filing." [COMP-F21, COMP-F22, COMP-F23]

**Where it would be a DISTRACTION:** if built as full autonomous filing, or if over-invested at the expense of the core detection/triage/response engine. It should be ONE high-visibility, differentiated MODULE (a "compliance co-pilot") on top of the autonomous SOC, not the whole product. The strategic fit with the "Autonomous Incident Intelligence Engine" is excellent: the multi-agent swarm already produces exactly the structured incident record (timeline, ATT&CK mapping, IOCs, actions) that the reporting module consumes, so the marginal build cost is low and the demo payoff is high. [COMP-F21] Confidence: High (reasoned synthesis).

**Recommended staging for the build:**
- Stage 1 (must-have for demo): auto-draft the CERT-In 6-hour report from a resolved incident, with a human-approval gate and an immutable audit log of detect-time/report-time. This alone lands the differentiator.
- Stage 2 (high-value add): add the DPDP two-stage Board report + plain-language data-principal notice generator, showcasing the no-materiality-threshold multiplication of notices.
- Stage 3 (scale story): pluggable "regulator connectors" (RBI/SEBI/IRDAI/CEA/NCIIPC) that re-skin the same normalized incident record into each regulator's timeline/format, demonstrating the domain-agnostic engine thesis.
- Benchmarks that would CHANGE this recommendation: if CERT-In publishes a machine-submission API/structured-format spec (would shift value from drafting toward integration), or if a named vendor ships verified CERT-In/DPDP form auto-population (would erode the novelty claim, requiring a sharper wedge such as multi-regulator normalization or sector depth).

## Contradictions & Disputes Found
- CERT-In "CIMS portal": some practitioner blogs (e.g., skeletos.io, indusface) reference notifying CERT-In "through the CIMS portal," but CERT-In primary documents and the targeted gap-check found only email/phone/fax + PDF; no corroborated CERT-In CIMS incident-submission portal exists. Treated as disputed/unverified. [COMP-F14]
- Incident-count sources differ by definition: CERT-In "cyber security incidents" (1.59m in 2023, Lok Sabha; 29.44 lakh in 2025, PIB) vs PIB "cybersecurity incidents" (22.68 lakh in 2024) vs NCRP cybercrime complaints (~1.5m). Different denominators; reported as a range, not averaged. [COMP-F16]
- RBI timeline is stated both as "2 to 6 hours" (2016 framework, multiple sources) and "within 6 hours" (2024 Master Directions tightening). Both are reported. [COMP-F25]

## What I Could NOT Verify (honest gaps)
- Any published analyst-hours or rupee cost to prepare a single CERT-In/DPDP report (NOT FOUND). [COMP-F31]
- Any published monetary enforcement action/penalty actually levied under Section 70B(7) for failure to report (appears absent; this is an inference, not a confirmed fact). [COMP-F24]
- The exact DPDP Board submission mechanism/format (portal vs email) under the final Rules; the Rules are notified but operational submission specifics were not fully confirmed. [COMP-F17a]
- Whether the CEA Power Sector Regulations 2024 have moved from draft to final notification as of mid-2026 (last confirmed as draft). [COMP-F28]
- The precise CERT-In FAQ list of ICT logs and full VPN-exemption text (summarized via law-firm sources, not read verbatim). [COMP-F08]

## Top 10 Findings That Should Shape THE IDEA
1. COMP-F14: No CERT-In API / structured submission; email/phone/fax + PDF only. Build DRAFT + manual export, not machine filing.
2. COMP-F20: No tool verifiably auto-drafts India regulator forms from incident data. This open gap IS the differentiator.
3. COMP-F18/F19: ~70-80% of CERT-In fields and ~50-60% of DPDP content are auto-draftable = demoable feasibility.
4. COMP-F17: Dual/triple reporting on different clocks (6hr / 72hr / sector). A normalization engine is the killer feature.
5. COMP-F10/F11: DPDP penalties up to 250cr + 200cr, stackable = quantifiable ROI story for judges.
6. COMP-F04: 20 Annexure I categories map cleanly onto triage/threat-classification agent output.
7. COMP-F21/F23: Human-in-the-loop is legally mandatory; frame as a compliance co-pilot with an audit trail.
8. COMP-F15/F16: INR 220m breach cost, 22.68 lakh incidents (2024), 29.44 lakh handled (2025) = scale-of-impact narrative; 73% under-use automation.
9. COMP-F30: Sector overlays (RBI/SEBI/IRDAI/CEA/NCIIPC) = pluggable-connector story for a domain-agnostic engine.
10. COMP-F09: DPDP no-materiality-threshold data-principal notice = automation multiplies value.

## Numbers & Facts Bank
| ID | Stat | Year | Source link | Confidence |
|---|---|---|---|---|
| COMP-F01 | CERT-In 6-hour reporting, Directions No. 20(3)/2022, s.70B(6) | 2022 | https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf | High |
| COMP-F04 | 20 Annexure I reportable incident categories (verbatim) | 2022 | https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf | High |
| COMP-F05 | CERT-In form fields + channels (email; phone 1800-11-4949; fax 1800-11-6969); form not mandatory | 2022 | https://www.cert-in.org.in/PDF/certinirform.pdf | High |
| COMP-F06 | 70B(7): up to 1 lakh + 1 yr; Jan Vishwas proposes up to 1 crore | 2022/2023 | https://ksandk.com/newsletter/increased-penalties-for-failure-to-comply-with-2022-cert/ ; https://natlawreview.com/article/cyber-security-india-revamps-rules-mandatory-incident-reporting-allied-compliances | High |
| COMP-F07 | 180-day log retention in India; NTP sync; 5-yr KYC | 2022 | https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf | High |
| COMP-F08 | FAQ: enterprise VPNs exempt; logs may be stored outside India | 2022 | https://www.saikrishnaassociates.com/cert-in-publishes-frequently-asked-questions-in-furtherance-of-its-cyber-security-directions/ | High |
| COMP-F09 | DPDP no materiality threshold; notify every data principal | 2025 | https://myitmanager.in/dpdp-act-data-breach-notification-india/ ; https://www.seclore.com/fundamentals/dpdp-rules-2025-compliance-guide/ | High |
| COMP-F09a | Rule 7 two-stage: "without delay" + 72-hr detailed report | 2025 | https://www.dpdpa.com/dpdparules/rule7.html ; https://www.medianama.com/2025/11/223-data-breach-reporting-timeline-of-dpdp-rules-2025-explained/ | High |
| COMP-F10 | DPDP up to 250cr (safeguards), 200cr (notification), 150cr (SDF) | 2023/2025 | https://www.matters.ai/article/dpdp-breach-notification ; https://www.tcsa.in/frameworks/dpdp/penalties-enforcement | High |
| COMP-F11 | Penalties stack per instance | 2023 | https://dpdpact.co.in/dpdp-act-penalties-enforcement-in-india/ ; https://ispectratechnologies.com/hub/dpdp/dpdp-penalties.html | High |
| COMP-F15 | India breach cost INR 220m (2025), 195m (2024), 179m (2023); lifecycle 263 days; automation less than halves cost, 73% under-use | 2025 | https://in.newsroom.ibm.com/2025-08-07-India-Records-Highest-Average-Cost-of-a-Data-Breach-IBM | High |
| COMP-F16 | India incidents 10.29 lakh (2022) to 22.68 lakh (2024); 1.59m in 2023; 29.44 lakh handled 2025 | 2024/2025 | https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2176146 ; https://apacnewsnetwork.com/2024/12/indias-cybersecurity-incidents-hit-1-59-million-in-2023-cert-in/ | High |
| COMP-F17a | DPDP Rules notified 13 Nov 2025; enforcement ~May 2027 | 2025 | https://www.matters.ai/article/dpdp-breach-notification ; https://www.fisherphillips.com/en/insights/insights/indias-new-data-privacy-rules-are-here | High |
| COMP-F20 | No verified auto-drafting of CERT-In/DPDP forms from incident data; BreachRx closest, generic | 2024/2026 | https://www.breachrx.com/regulations/india-cert-in-directive/ | Med |
| COMP-F22 | No CERT-In STIX/TAXII/IODEF/API acceptance (email/fax only) | 2022/2026 | https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf | Med-High |
| COMP-F24 | VPN exits (Express/Nord/Surfshark/Proton/Hide.me/IPVanish); deadline extended to 25 Sep 2022 | 2022 | https://techcrunch.com/2022/06/27/india-delays-strict-new-vpn-rules-by-3-months ; https://www.medianama.com/2022/06/223-surfshark-expressvpn-exit-india-cybersecurity-directions/ | High |
| COMP-F25 | RBI 2-6 hr (2016), 6 hr tightened (2024 Master Directions) | 2016/2024 | https://www.fluxforce.ai/regulations/rbi-cyber-security-framework-banks ; https://myitmanager.in/rbi-cybersecurity-guidelines-2026-banks-nbfcs/ | High |
| COMP-F26 | SEBI CSCRF (circular 2024/113, 20 Aug 2024): 6 hr + 24 hr full + 75-day forensic; M-SOC; phased deadlines | 2024/2025 | https://www.indusface.com/blog/decoding-sebis-cscrf/ ; https://vcisodesk.com/sebi-cscrf-implementation-guide-regulated-entities-india/ | High |
| COMP-F27 | IRDAI 6 hr to CERT-In copy IRDAI (policy 2.10, para 3.5) | 2023 | https://taxguru.in/corporate-law/irdai-guidelines-reporting-cyber-security-incidents.html | High |
| COMP-F28 | CEA CSIRT-Power; 24 hr sabotage reporting (draft 2024) | 2024 | https://payatu.com/blog/draft-cea-cybersecurity-regulation-india-power-sector/ ; https://shieldworkz.com/blogs/safeguarding-power-infrastructure-decoding-the-draft-cea-cyber-security-regulations | Med-High |
| COMP-F29 | NCIIPC 24x7 SPOC; structured form 24 hr; 30-day RCA; sabotage 24 hr | current | https://ringsafe.in/nciipc-guidelines/ ; https://en.wikipedia.org/wiki/National_Critical_Information_Infrastructure_Protection_Centre | Med-High |
| COMP-F31 | Per-report time/cost NOT FOUND; SME CERT-In setup INR 50k-5 lakh | 2026 | https://www.incorpx.io/blog/cert-in-cybersecurity-compliance-2026 | Med |