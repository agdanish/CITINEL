# CITINEL
## Complete knowledge base

*Every sentence is under ten words. Read once, top to bottom.*

---

# 1 · The problem

- Indian cooperative banks are attacked constantly.
- RBI requires them to run 24x7 security monitoring.
- A human security team costs crores each year.
- Their whole IT budget is under Rs 1 lakh monthly.
- So the requirement is real. The money is not.
- In 2024, one attack took 300 cooperative banks offline.

## The regulatory clock

- CERT-In requires an incident report within six hours.
- The clock starts when you notice. Not when you finish.
- DPDP requires a breach report to the Board.
- Penalties stack. Rs 250 crore plus Rs 200 crore.
- Missing the form is a separate offence from the breach.

## The gap nobody fills

- SIEM tools know what happened.
- They do not write the regulator's form.
- Compliance tools write forms.
- They do not know what happened.
- CITINEL is one pipeline covering both.

**Keywords** cooperative bank, RBI, CERT-In, DPDP, six-hour clock, budget gap,
Section 70B, Rule 7

---

# 2 · What CITINEL is, in one line

- An autonomous Security Operations Centre.
- It investigates alerts and cites its evidence.
- It drafts the regulator's form automatically.
- A named human always signs before filing.

## The name

- CITINEL is CITE plus SENTINEL.
- The sentinel that cites its evidence.
- Every claim quotes the log line proving it.

**Keywords** glass-box, autonomous SOC, cited verdict, human sign-off

---

# 3 · End-to-end flow

*This is the most important section. Learn this order.*

## Stage 1 · Input arrives

- Raw logs enter the system.
- Sources are syslog, webhook, or replayed corpus files.
- Our demo replays Splunk BOTS data. It is licence-clean.
- Input is messy. Every vendor formats differently.

## Stage 2 · Normalise

- Code converts every log to one standard shape.
- That standard is called OCSF.
- Now a Windows log and a firewall log look alike.
- No AI is involved yet.

## Stage 3 · Detect

- Two detectors run on the normalised events.
- Sigma rules match known attack patterns exactly.
- The anomaly scorer flags unusual behaviour statistically.
- Both are deterministic code. No model is called.
- A match becomes a finding with its exact log line.

## Stage 4 · Group into an incident

- Related findings are grouped into one incident.
- Our demo incident holds 2,487 findings.
- The incident now has an identity and a clock.

## Stage 5 · Quarantine

- Every log line is treated as untrusted input.
- Attacker text cannot instruct our agents.
- Content is fenced with a random, unforgeable marker.
- Taint travels with the data everywhere it goes.

## Stage 6 · Investigate with agents

- Seven roles now run in sequence.
- Five of them call a model. Two are plain code.
- Section 4 explains each one.

## Stage 7 · Verify citations

- The Narrator produces claims.
- Each claim must quote its evidence exactly.
- Code checks each quote against the evidence supplied.
- A claim that fails is deleted, not flagged.
- This is the citation gate.

## Stage 8 · Propose response

- The Marshal proposes actions. It does not run them.
- Example actions are block IP or revoke sessions.
- Each proposal names its target and blast radius.

## Stage 9 · Policy gate

- A readable rulebook adjudicates each proposal.
- Each clause names an action class and tier.
- Reversible actions may run unattended.
- Consequential actions wait for a named human.
- Approved reversible actions receive a rollback token.

## Stage 10 · Execute against simulation

- Approved actions hit simulated endpoints only.
- No real bank system is ever touched.
- The interface states this: EVERY OUTLET IS BLANKED.

## Stage 11 · Draft the regulator's form

- The record is drafted into the CERT-In form.
- Ten fields. Eight automatic. Two suggested.
- The personal-data question is refused by the machine.
- That one is a legal decision for a human.

## Stage 12 · Human signs

- A named human answers the legal question.
- They type their name and attest.
- This writes a sign-off frame to the ledger.

## Stage 13 · Automate after sign-off

- n8n fires only after a human signs.
- It notifies the CISO and opens a ticket.
- It returns which channels actually succeeded.

## Stage 14 · Record everything

- Every step above is written to a ledger.
- The ledger is hash-chained and append-only.
- Nothing can be edited or deleted.

## Output

- A cited verdict with a kill chain.
- A set of proposed actions with policy decisions.
- A drafted CERT-In report and DPDP artefacts.
- A printable PDF for the bank to file.
- An unbreakable audit trail of the whole thing.

**Keywords** OCSF, Sigma, anomaly scorer, quarantine, citation gate, OPA policy,
rollback token, hash-chained ledger, simulated endpoint

---

# 4 · The seven agents

*Source: `agents/pipeline.py`, line 3.*

**Full chain** Sentinel to Router to Enricher to Correlator to Narrator to Marshal
to Scribe.

## Important honesty point

- Seven roles exist. Only five call a model.
- Sentinel and Scribe are deterministic code.
- The docstring says why. A model would reduce reliability.
- Say "seven roles, five thinking agents". Never "seven AI agents".

## 1 · Sentinel · orchestrator · code only

- Owns the case from start to finish.
- Sequences the five thinking agents in order.
- Records every stage to the ledger.
- Never calls a model.

## 2 · Router · triage · model

- Reads the incident summary.
- Decides which lane it belongs in.
- Escalates only what needs deeper work.
- Cheap model. Saves cost on easy cases.

## 3 · Enricher · context · model with tools

- The only multi-turn agent.
- Calls external threat-intelligence services.
- Uses Tavily, VirusTotal and AbuseIPDB.
- Asks, reads the answer, then asks again.
- Records what each provider actually answered.

## 4 · Correlator · kill chain · model

- Joins scattered findings into one attack story.
- Maps each step to MITRE ATT&CK.
- Output is fenced before the Narrator sees it.
- That fence blocks agent-to-agent laundering.

## 5 · Narrator · verdict · model

- Writes the human-readable verdict.
- Every claim must quote its evidence.
- Also states counter-evidence explicitly.
- Its output faces the citation gate.

## 6 · Marshal · response · model

- Proposes actions the incident justifies.
- Names target, action class and blast radius.
- Proposes only. It never executes.

## 7 · Scribe · recording · code only

- Writes the compliance artefacts.
- Assembles the drafted forms from the record.
- Never calls a model.

## How they interconnect

- Sentinel calls each agent in strict order.
- Output of one becomes fenced input to the next.
- No agent talks to another directly.
- Every handoff is recorded in the ledger.
- Any agent can fail without stopping the chain.
- A failed stage is recorded as degraded, not hidden.

**Keywords** orchestrator, triage lane, multi-turn tool use, kill chain, MITRE
ATT&CK, citation gate, provenance fence, degradation

---

# 5 · The nine partners

*All nine are wired and proven with real calls.*

## 1 · Anthropic · the thinking

- Provides the Claude models for five agents.
- Two models used. Haiku for triage. Sonnet for reasoning.
- Cheap model first. Expensive model only when needed.
- Both model IDs verified live at startup.
- **Why chosen** strongest resistance to prompt injection in 2026 benchmarking.

## 2 · Lyzr · the second opinion

- Seven independent agents, separate from ours.
- Triage, review, handover, verdict, response, corpus, witness.
- They check our work from outside.
- **Key role** the ledger witness.
- It keeps its own count of ledger entries.
- That catches someone replacing the whole file.
- Our own chain check cannot see that attack.
- **Why chosen** independence. A checker inside the system proves nothing.

## 3 · Tavily · the open web

- Searches public sources for context.
- Looks up each attack technique that fired.
- Also fetches CERT-In and DPDP guidance.
- Returns real URLs with fetch timestamps.
- **Why chosen** the Enricher needs current public information.
- Threat intelligence changes daily. Our corpus does not.

## 4 · Google Gemini · the wide lens

- Reads all 2,487 findings in one call.
- Our investigation examined only 40.
- Gemini covers the 2,447 we did not examine.
- Also reads analyst screenshots as images.
- **Critical rule** its output is tagged not_evidence.
- No verdict can ever rest on it.
- **Why chosen** very long context window. Cheap per token.

## 5 · n8n · the automation

- Fires only after a human signs off.
- Notifies the CISO. Opens a ticket.
- Returns which channels actually succeeded.
- We also read executions back as evidence.
- **Why chosen** banks already run workflow tools.
- We integrate rather than replace.

## 6 · Swytchcode · the safe transport

- Executes ticketing and messaging after approval.
- Runs through a policy-gated command line.
- GitHub ticketing works on the live deployment.
- Slack messaging is not configured. We say so.
- **Why chosen** one gated transport for many providers.

## 7 · VirusTotal · file and IP reputation

- Checks file hashes against 75 engines.
- Checks IP addresses for known badness.
- Used by the Enricher during investigation.
- **Why chosen** the largest public reputation corpus.

## 8 · AbuseIPDB · IP abuse reports

- Returns community abuse confidence for an IP.
- Example result: 100 percent over 256 reports.
- Used by the Enricher alongside VirusTotal.
- **Why chosen** community reporting VirusTotal does not cover.

## 9 · Startuped · product signals

- Receives aggregate usage counts only.
- Five named signals. Nothing else.
- **Critical rule** it refuses any incident content.
- Refusal, not redaction. The field is rejected.
- **Why chosen** growth measurement without a privacy hole.

## Reached through Swytchcode

- **Slack** messaging destination. Currently not configured.
- **GitHub** ticketing destination. Working live.

## Hosting

- **Render** runs the web service and worker.
- A persistent disk holds the ledger.
- A cron job checks for tampering every six hours.

**Keywords** model tiering, independent witness, OSINT, long context, not_evidence,
policy-gated transport, aggregate-only telemetry

---

# 6 · The sixteen screens

*Grouped by when you use them.*

## Group A · See the situation

**1 OVERVIEW** every clock, every incident, fleet health.
**2 QUEUE** new detections. Rule-caught versus needs-investigation.
**16 SHELL** the app frame and the state legend.

## Group B · Understand one incident

**3 REPLAY** scrub the investigation like a video. The key screen.
**4 CONFIDENCE** how sure, plus what argues against.
**5 EVIDENCE** raw log lines and chain of custody.

## Group C · Decide and act

**6 POLICY** the readable rulebook.
**7 APPROVALS** the gate. Approve or deny with blast radius.

## Group D · Comply and file

**8 COMPLIANCE** the CERT-In and DPDP drafting desk.
**9 REPORT** the printable PDF for filing.

## Group E · Prove and improve

**10 AUDIT** the hash-chained ledger.
**11 CORPUS** rule collection and human review bench.
**12 EVAL** what we measured and what we did not.

## Group F · Operate and report

**13 HANDOVER** the shift note from the ledger.
**14 EXEC** the board view.
**15 CONNECTORS** every external service and its status.
**DEMO** a scripted teaching walkthrough of detection.

**Keywords** incident lifecycle, glass-box, shift handover, board view

---

# 7 · The forty differentiators, by screen

*Ten are code a judge can check. Thirty are researched claims.*

| Screen | Item | Name |
|---|---|---|
| REPLAY | !!KD1!! | Quote-Bound Claim Elimination Gate |
| REPLAY | !!KD4!! | Inter-Agent Provenance Fencing |
| REPLAY | !!U1!! | Per-Claim Log-Line Citation Requirement |
| REPLAY right | !!KD2!! | Payload-Level Evidence Class Tagging |
| REPLAY right | !!KD6!! | Declared Blind-Spot Closure Sweep |
| AUDIT | !!KD3!! | Hash-Chained Ledger with External Witness |
| AUDIT | !!U5!! | Reasoning-Independent Audit Substrate |
| CONNECTORS | !!KD5!! | Deterministic Exact-Host Egress Allow-List |
| CONNECTORS | !!KD7!! | Field-Refusing Telemetry Privacy Boundary |
| APPROVALS | !!KD8!! | Rollback-Tokened Blast-Radius Policy Gate |
| APPROVALS | !!U19!! | Day-One Blast-Radius Ring Design |
| Write guard | !!KD9!! | Fail-Closed Distinguishable Write Denial |
| OVERVIEW, EVAL | !!KD10!! | Denominator-Mandatory Metric Rendering |
| POLICY | !!U3!! | Human-Readable Policy-as-Code Gating |
| POLICY, APPROVALS | !!U18!! | Per-Action-Class Autonomy Assignment |
| CONFIDENCE | !!U4!! | Counter-Evidence-Paired Confidence Disclosure |
| CONFIDENCE | !!U22!! | Calibrated Self-Assessment Trust Uplift |
| DEMO, QUEUE | !!U9!! | LLM-Independent Deterministic Detection Floor |
| DEMO, EVIDENCE, COMPLIANCE | !!U20!! | Anti-Laundering Quarantine Through Signature |
| COMPLIANCE, REPORT | !!U8!! | Pre-Enforcement Regulatory Clock Readiness |
| CORPUS | !!U14!! | Licence-Free Portable Detection Export |
| CORPUS | !!U16!! | Mandatory Human Accession Review Gate |
| CORPUS | !!U15!! | Proven Open-Core SOC Viability Precedent |
| CORPUS | !!U17!! | Precedented Detection-Content Bounty Economics |

## Spoken only, no screen

| Item | Name |
|---|---|
| !!U2!! | Injection-Resistant Foundation Model Selection |
| !!U6!! | India-Regulator Form Drafting White Space |
| !!U7!! | Adversarially Refuted Competitor Parity Claim |
| !!U10!! | Transparent Price Band Against Quote-Walls |
| !!U11!! | Competitor-Sourced Human-Analyst Cost Benchmark |
| !!U12!! | Order-of-Magnitude Buyer-Band Displacement |
| !!U13!! | Regulator-Built B2B2X Distribution Channel |
| !!U21!! | Risk-Calibrated Trust Dial Evidence |
| !!U23!! | Government-Funded PACS Distribution Rail |
| !!U24!! | Confabulation-Resistant Aggregation Design Choice |
| !!U25!! | Scaffolding-Level Reversible Improvement Loop |
| !!U26!! | Anti-Corruption Layer Boundary Pattern |
| !!U27!! | Self-Verification Refusal by Architecture |
| !!U28!! | Base-Model Attack Inheritance Mitigation |
| !!U29!! | Multi-Layer Hybrid Defence Convergence |
| !!U30!! | Low-Latency Consensus Reference Protocol |

## The four headline features

| Item | Name |
|---|---|
| !!H1!! | Glass-Box Cited Triage Pipeline |
| !!H2!! | Readable Per-Class Autonomy Dial |
| !!H3!! | Injection-Hardened Quarantine Plane |
| !!H4!! | Regulator-Ready Compliance Clock |

---

# 8 · Quality gates

*Places where the system refuses to proceed.*

## Gate 1 · The citation gate

- Runs after the Narrator writes claims.
- Checks each quoted span against supplied evidence.
- A failing claim is deleted from the verdict.
- Not flagged. Not downranked. Deleted.

## Gate 2 · The quarantine fence

- Runs on all log content at ingest.
- Wraps untrusted text in a random marker.
- The marker changes every call. It cannot be forged.
- Taint propagates through every derived value.

## Gate 3 · The egress allow-list

- Runs before any outbound network call.
- Deny by default. Exact hostnames only. HTTPS only.
- A malicious log cannot redirect our traffic.

## Gate 4 · The policy gate

- Runs on every proposed action.
- Adjudicates against a named clause.
- Enforces an asset cap per action class.
- Blast radius is floored, never lowered by the caller.

## Gate 5 · The write guard

- Runs on every write request.
- No token returns 401. Writes disabled returns 503.
- Fail closed. The two failures are distinguishable.

## Gate 6 · The human sign-off

- Runs before any compliance artefact is final.
- One field the machine refuses to answer.
- A named human must attest.

## Gate 7 · The accession bench

- Runs before a rule joins the corpus.
- Machine-drafted rules await human determination.

**Keywords** fail closed, deny by default, taint propagation, asset cap, attestation

---

# 9 · The evaluation harness

- Located outside the package, at `evals/harness/run.py`.
- Measures the deterministic layers only.
- Its design rule is structural, not cosmetic.
- The false-positive rate is a target, never an achieved result.
- The EVAL screen shows what was measured.
- It also shows an explicit unmeasured list.
- Nothing on that list is claimed elsewhere.

## The honest numbers

- Industry false-positive rate is 46 to 80 percent.
- That range comes from published surveys.
- Our target is under 10 percent.
- We have not measured ours yet. We say so.

**Keywords** eval harness, labelled data, target versus achieved, denominator

---

# 10 · Evaluation criteria mapping

*What each judging axis wants, and our strongest answer.*

## Axis 1 · Problem Alignment and Functional Scope

**They want** clear problem understanding, features aligned to it.

- Our problem statement is Section 1. It is specific and sourced.
- PS4 names five terms. All five are built.
- Autonomous: the per-class autonomy dial.
- Cyber SOC: sixteen operational screens.
- AI-powered: five thinking agents on live models.
- Threat detection: 3,302 Sigma rules plus anomaly scoring.
- Automated response: policy gate with rollback tokens.
- **Show** QUEUE, then REPLAY, then APPROVALS.
- **Honest gap** demo data is generic, not banking-specific.

## Axis 2 · Technical Execution and Working Prototype

**They want** operational status, live demonstration, stability.

- It is deployed and public. Not a slide deck.
- Sixteen screens. Sixteen connectors. All configured.
- 420 automated tests pass.
- Eleven external services proven with real calls.
- A read-only pre-flight prints GO or names the fault.
- **Show** the live URL, then AUDIT for the ledger.
- **Honest gap** response actions hit simulated endpoints.

## Axis 3 · UI and UX

**They want** intuitive layout, clear flow, visual polish.

- One design system across all sixteen screens.
- Every screen names its own data source.
- A live chip shows when data is real.
- A red banner appears when it is not.
- Role toggle switches analyst and CISO depth.
- **Show** REPLAY scrubbing, then CONFIDENCE.
- **Honest gap** three backend features have no console control.

## Axis 4 · Innovation, Market Readiness, Scalability

**They want** uniqueness, impact, scale, deployment readiness.

- No competitor drafts CERT-In or DPDP forms.
- That is our strongest defensible claim.
- The nearest claimant failed independent verification.
- The architecture is stateless behind a persistent ledger.
- Already deployed on managed infrastructure.
- **Show** COMPLIANCE, then the printed report.
- **Honest gap** impact is unvalidated. No bank telemetry yet.

## Axis 5 · Team Dynamics and Presentation

**They want** clarity, equal participation, Q&A defence.

- Assign one screen group per speaker.
- Everyone must know the four never-say rules.
- The strongest answer is always the honest one.
- **Show** different speakers on different screens.
- **Honest gap** roles were not assigned in advance.

**Keywords** PS4 terms, deployed prototype, design system, defensible moat, honest
concession

---

# 11 · The four things to never say

- 🔴 Never state an achieved false-positive rate.
- 🔴 Never say anything was filed with a regulator.
- 🔴 Never say a real machine was touched.
- 🔴 Never say the Slack transport works.

## What to say instead

- 🟢 "Industry runs 46 to 80 percent. We target under 10."
- 🟢 "CITINEL drafts. A human signs. The bank files."
- 🟢 "Every endpoint is simulated. The screen says so."
- 🟢 "Ticketing works. Messaging does not. The ledger says so."

---

# 12 · One-paragraph summary

- A log arrives and is normalised to OCSF.
- Sigma rules and an anomaly scorer detect threats deterministically.
- Findings group into an incident with a legal clock.
- All content is quarantined as untrusted.
- Five model agents investigate under one code orchestrator.
- Every claim must quote its evidence or be deleted.
- Proposed actions pass a readable policy gate.
- A human approves. Simulated endpoints execute.
- The record drafts the CERT-In and DPDP forms.
- A named human signs. Automation fires afterwards.
- Everything is written to a hash-chained ledger.
- An independent witness guards against wholesale replacement.

**That is CITINEL, end to end.**
