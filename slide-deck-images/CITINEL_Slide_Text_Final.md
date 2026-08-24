# CITINEL — FINAL TYPED TEXT · ALL 15 SLIDES
*Every word a judge reads outside the images. Kickers, headings and callout labels already exist — nothing below repeats them. Blocks are copy-ready for Canva. [FILL] marks details not in the knowledge base. The 20-critic loop ran three passes internally; only final text ships.*

---

## Slide 1: Cover
*12/12 beyond printed title block · CLR, NOV primed*

```
Track 3 · Bharat Pragati · PS4
"Autonomous Cyber SOC for AI-powered threat detection and automated incident response"
```

```
PRESENTED BY: [FILL: team name] · [FILL: institute]
```

---

## Slide 2: Team Members
*≤8 words per member · FEA, CLR*

```
[FILL: Name], lead — builds agentic systems professionally; owns the swarm
[FILL: Name] — ingest and Open Cybersecurity Schema Framework (OCSF) pipeline
[FILL: Name] — Sigma detections and the anomaly scoring layer
[FILL: Name] — Open Policy Agent (OPA) gate and audit log
[FILL: Name] — glass-box interface and investigation replay
[FILL: Name] — compliance drafter and the evaluation harness
```

---

## Slide 3: Problem Statement
*88/90 · CLR, IMP, NOV, FEA*

**Problem Title**
```
Track 3 · Bharat Pragati · PS4: "Autonomous Cyber SOC for AI-powered threat detection and automated incident response."
```

**What does this Problem Aim to Solve?**
```
It aims to give small banks a security team that never sleeps. AI agents detect threats, prove every verdict from raw log lines, respond inside a human-readable policy, and draft the regulator's report before the six-hour clock lapses.
```

**Why did your team choose this?**
```
One 2024 ransomware hit on shared vendor C-Edge froze one in five of India's cooperative banks in a day. SEBI now mandates shared Security Operations Centres (SOCs) because smaller entities cannot afford their own. Our lead builds agentic systems professionally — the hardest clause here is our craft.
```

---

## Slide 4: Real-World Problem Alignment
*100/100 · IMP, PRA, SUS, FUT, FEA*

**Who faces this issue?**
```
The Information Technology (IT) head of a cooperative bank or small Non-Banking Financial Company (NBFC) — one officer, a round-the-clock duty, alone.
```

**What's the current gap in the system?**
```
A compliant Security Operations Centre (SOC) needs eight to twelve analysts. On 31 July 2026 the Reserve Bank of India (RBI) made round-the-clock monitoring an explicit mandate for India's banks, effective immediately.
```

**How does your proposed solution fill that gap practically?**
```
CITINEL does the tier-one toil with cited evidence, executes reversible actions, escalates consequential ones for one click, and leaves a regulator-ready draft awaiting a human signature.
```

**If possible, mention if it connects to any existing schemes.**
```
Digital India sets the umbrella. Cyber Surakshit Bharat trains the officers we serve. C3iHub incubates cybersecurity ventures; I4C coordinates national fraud data.
```

---

## Slide 5: Scale of Impact
*35/35 · IMP, CLR*

```
Three regulated sectors share the same wound: banking, health, and securities. The damage compounds yearly while defence stands still. Every figure on this page reappears on the evidence page with its publisher, date, and denominator.
```

---

## Slide 6: Proposed Solution
*Box 130/100–150 (locked, verbatim) · features 12·11·12·10 · differentiator 18/20 · NOV, CLR, UX*

**What are you Building?**
```
CITINEL is an autonomous Cyber SOC that investigates every alert with cited evidence, acts only inside a policy humans can read, and beats India's regulatory clocks. Alerts from bank systems normalize to OCSF; Sigma rules catch known threats deterministically; Claude agents correlate the rest into a MITRE ATT&CK kill-chain narrative where every verdict cites the exact log line proving it. Response actions pass a per-action policy: enrichment runs automatically, host isolation runs with rollback, disabling a production account waits for one-click human approval. The pipeline treats all log content as untrusted data, so a poisoned log cannot hijack the AI. On confirmation, it drafts the CERT-In 6-hour report and DPDP breach artifacts for human sign-off. Built for cooperative banks that RBI requires to run a 24×7 SOC they cannot afford.
```

**What are the 3-4 Key Features?**
```
Glass-box cited triage — every verdict cites the exact log line proving it.
Readable autonomy dial — Shadow, Assist, Autonomous, set separately per action class.
Injection-hardened pipeline — log content is data, never instructions, attacked live on stage.
Compliance-clock module — CERT-In and DPDP drafts auto-filled, human signature mandatory.
```

**What makes it different or innovative?**
```
Global AI-SOCs don't draft a CERT-In or DPDP report; India's compliance tools make humans type the facts in.
```

---

## Slide 7: User Experience
*22/25 · UX, TCX*

```
Watch one incident end to end: the citation chip opens the raw line, the approval card shows blast radius before you click.
```

---

## Slide 8: Tech Stack & Architecture
*26·19·21·22 (≤30 each) · TCX, FEA, SUS, PRA*

**Tech Stack**
```
Python services; Open Cybersecurity Schema Framework (OCSF) events; Sigma engine, 3,000+ community rules; seven Claude agents; Open Policy Agent (OPA) gate; PostgreSQL and Redis on Render.
```

**APIs/Libraries**
```
VirusTotal, AbuseIPDB and GeoIP enrichment; Tavily live search; Swytchcode agent-to-API execution; n8n export flows — policy authority never leaves OPA.
```

**Deployment Plan**
```
Render: web service, background worker, managed PostgreSQL and Redis. Always-on demo URL. Attack replays run only in an isolated virtual machine.
```

**High-level Block Diagram OR Architecture**
```
Full architecture on the next slide. Response actions hit simulated endpoints by design; our measured cost per incident is a few cents.
```

---

## Slide 9: Architecture Diagram
*14/15 · TCX, CLR, UX*

```
One record in, one signed report out; consequential actions stop at the human gate.
```

---

## Slide 10: Feasibility
*39/40 · FEA, CLR, PRA*

```
Stage one runs on open-licence data. If correlation wobbles, agents recommend, humans drive; if the policy engine slips, a signed config file enforces the same rules. We will publish our measured false-positive rate; the target is under ten percent.
```

---

## Slide 11: Practicability
*40/40 · PRA, FEA, SUS*

```
Ingestion is syslog and webhooks — nothing at the branch changes. Threat-intel lookups respect free-tier caps by caching. Pricing sits inside the per-device band Indian managed-security providers already charge. Demo actions strike laboratory mocks — declared on the slide, not buried.
```

---

## Slide 12: Sustainability
*40/40 · SUS, FUT, FEA*

```
Detections export as open Sigma rules anyone can take elsewhere. Wazuh and TheHive proved open-core security survives commercially; we follow that path. Every machine-drafted rule passes human review before joining the corpus. C3iHub's incubation grant is our named, non-dilutive runway.
```

---

## Slide 13: Business Model & Roadmap
*30/30 · FUT, SUS, PRA*

```
White-label licensing to managed-security providers and the exchanges' security operations centres — they keep the customer, we keep the engine. We instrument our own unit economics; nothing is quoted from vendors.
```

---

## Slide 14: Thank You
*22/35 · FEA, CLR*

```
Running now at [FILL: Render demo URL]. Replay incident INC-0417 end to end. Test us with your worst incident.
```

```
[FILL: lead name] · [FILL: email] · [FILL: phone]
```

---

## Slide 15: Evidence & References
*20 lines, one per citation chip, in chip order (Clocks → Damage → Shortfall → Proof) · CLR, NOV, SUS*

```
1  CERT-In Directions No. 20(3)/2022, 28 Apr 2022 — cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf
2  RBI (Commercial Banks) Directions 2026, para 182, 31 Jul 2026 — rbi.org.in
3  RBI (Commercial Banks) Directions 2026, paras 221–223, 31 Jul 2026 — rbi.org.in
4  SEBI CSCRF, Circular P/CIR/2024/113, 20 Aug 2024 — sebi.gov.in
5  DPDP Rules 2025, G.S.R. 846(E), Rule 7(2)(b), 13 Nov 2025 — meity.gov.in
6  IBM Cost of a Data Breach, India cut, 3 Aug 2026 — in.newsroom.ibm.com
7  IBM Cost of a Data Breach, India cut, 3 Aug 2026 — in.newsroom.ibm.com
8  IBM Cost of a Data Breach, global, 29 Jul 2026 — newsroom.ibm.com
9  Reuters, J. Kalra, 31 Jul 2024 (regulatory officials' figure) — reuters.com
10 DPDP Act 2023, Schedule, s.33(1); enforceable ~May 2027 — meity.gov.in
11 ISC2 Cybersecurity Workforce Study 2023, Fig 2-B — isc2.org
12 Vectra AI / Sapio Research, n=1,450, 10 Feb 2026 — vectra.ai
13 SANS SOC Survey 2026, n=444, 15 Jun 2026 — sans.org
14 IBM India 2026, no-automation cohort — in.newsroom.ibm.com
15 MoS Home Affairs, Lok Sabha reply, 22 Jul 2025 (NCRP complaints, not incidents) — business-standard.com
16 Cloud Security Alliance benchmark, n=148, 7 Oct 2025 — cloudsecurityalliance.org
17 OpenSec, arXiv:2601.21083, 28 Jan 2026 (preprint) — arxiv.org/abs/2601.21083
18 Gartner Summit press release, 2 Jun 2026 — gartner.com/en/newsroom
19 OWASP GenAI Top 10 for LLM Applications 2026, LLM01 — genai.owasp.org
20 CISA, NSA & Five Eyes partners, agentic AI guidance, 1 May 2026 — cyber.gov.au
```

---

## RUBRIC COVERAGE MATRIX
*✓ = scored by typed text on that slide · **bold** = strongest slide for the criterion*

| Criterion | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Novelty | ✓ | | ✓ | | | **✓** | | | ✓ | | | | | | ✓ |
| Technical complexity | | | | | | ✓ | ✓ | ✓ | **✓** | | | | | | |
| Clarity of presentation | ✓ | ✓ | ✓ | | ✓ | ✓ | | | ✓ | ✓ | | | | ✓ | **✓** |
| Feasibility | | ✓ | ✓ | ✓ | | | | ✓ | | **✓** | ✓ | ✓ | | ✓ | |
| Practicability | | | | ✓ | | | | ✓ | | ✓ | **✓** | | ✓ | | |
| Sustainability | | | | ✓ | | | | ✓ | | | ✓ | **✓** | ✓ | | ✓ |
| Scale of impact | | | ✓ | ✓ | **✓** | | | | | | | | | | |
| User experience | | | | | | ✓ | **✓** | | ✓ | | | | | | |
| Future progression | | | | ✓ | | | | | | | | ✓ | **✓** | | |
