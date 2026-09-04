# CITINEL
## Operator walkthrough and differentiator map

*A working reference for the sixteen console screens, the order they are exercised
in, and the forty catalogued differentiators each one evidences. Every interface
string quoted below was extracted from the deployed `.dc.html` sources, so the
words in this document match the words on the glass.*

**Deployment** `https://citinel-web.onrender.com`
**Build** branch `build/stage-1`, sixteen screens, sixteen connectors, 420 tests.

---

## The catalogue

Forty items across four tiers. Every one carries a code and a name. The codes are
used throughout this document and in the matrix at the end.

| Tier | Count | Source | Evidential strength |
|---|---|---|---|
| **KD** Key differentiators | 10 | findings §13 | Executable. Verifiable from the console or the source in under a minute. |
| **U1 to U20** Validated UVPs | 20 | SDD §13 | 106-agent adversarial pass. Tiered Verified, Existing, or External-hedged. |
| **U21 to U30** Additional UVPs | 10 | SDD §17 | Second adversarial pass. Unconventional and cross-domain. |
| **H1 to H4** Headline features | 4 | README | Product-level restatements of the above. |

**Reading convention.** Catalogued items appear in !!dark red!! throughout. An
item is named at the screen that evidences it, and only restated where a second
screen provides independent corroboration.

**Presentation classes.** `P1` core demonstration path. `P2` secondary, shown if
the slot allows. `P3` responsive, shown only under questioning.

---

## Headline features

These four are the product-level summary. Each decomposes into items proved on
specific screens.

| Code | Name | Decomposes into |
|---|---|---|
| !!H1 · Glass-Box Cited Triage Pipeline!! | Deterministic detection, then cited agentic correlation | KD1, KD4, U1, U9 |
| !!H2 · Readable Per-Class Autonomy Dial!! | Policy-as-code gating with blast-radius bounds | KD8, U3, U18, U19 |
| !!H3 · Injection-Hardened Quarantine Plane!! | Untrusted-by-default log handling through signature | KD2, KD5, U20, U28 |
| !!H4 · Regulator-Ready Compliance Clock!! | CERT-In and DPDP artefacts drafted from the record | U6, U7, U8 |

---

# Section 0 · Deployment preconditions

**Function.** Establish that the service is warm, the regulatory clock is live, and
the operating device holds write authority.

**Sequence**

1. Execute `python3 scripts/preflight.py`. Require the terminal to print **GO**.
2. In Render, select `citinel-web` and trigger **Manual Deploy** once.
3. Allow 90 seconds for container restart.
4. Navigate to `/Settings.dc.html`.
5. Locate **ARM THIS DEVICE**.
6. Enter operator name in field one, write token in field two.
7. Select **SAVE**.
8. Confirm the rail footer reads **ARMED** above the operator name, with a green indicator.

**Failure mode.** A footer reading **READ-ONLY** indicates the token did not
persist. Repeat steps 6 and 7.

**Why the redeploy is mandatory.** The demonstration incident carries a six-hour
statutory window measured from container boot. Without a morning restart the
primary dial renders as breached rather than counting down.

---

# Section 1 · OVERVIEW · P1

**Function.** Fleet-level state: every open incident, every statutory clock, and
the health of the agent estate on one surface.

**Route** `/` or **OVERVIEW**.

**Sequence**

1. Observe the primary countdown at the head of the screen.
2. Locate **EVERY RUNNING CLOCK**.
3. Locate **AGENT FLEET**.
4. Locate **TRIAGE LANES**.
5. Locate **DISPOSITION FEED**.
6. Note the **RULEBOOK** control. Defer activation to Section 7.

**On-screen artefacts.** **EVERY RUNNING CLOCK** · **AGENT FLEET** ·
**TRIAGE LANES** · **DISPOSITION FEED** · **RULEBOOK** · **GO TO**

**Items evidenced**

!!KD10 · Denominator-Mandatory Metric Rendering!! No quantity is rendered without
its population. The constraint is enforced at every render site, not applied
editorially.

**Assertion.** "This is the CERT-In six-hour window running against a live record.
Every quantity on this surface carries its denominator, because a rate without a
population is a marketing figure and we do not render one."

---

# Section 2 · DEMO · P1

**Function.** A deterministic, scripted trace of the ingest-to-signature path. Used
to establish mechanism before live data is shown. Declares its own scripted status.

**Route** **DEMO**.

**Sequence**

1. Read the header banner **DEMO MODE · SCRIPTED PERFORMANCE, NOT LIVE DATA** aloud.
2. Locate the **PROMPT BOOK** control column.
3. Locate the stage heading **RAW TELEMETRY → OCSF NORMALISE → MATCH**.
4. Advance with **NEXT CUE ▸**.
5. Halt at **DETERMINISTIC MATCH · RULE FIRED**. Note the rule identifier and corpus revision.
6. Advance. Halt at **ANOMALY SCORER · THE REST**.
7. Locate **THE LINE BOTH SYSTEMS RECEIVE · IDENTICAL BYTES**.
8. Locate **OPA BLAST CAP · 250** and the node count beneath it.
9. Advance to **THE REMNANT, INSIDE THE DRAFT THE HUMAN SIGNS**.
10. Read the disclosure panel **WHAT THIS DOES AND DOES NOT SHOW**.
11. Exit via **◀ RETURN TO LIVE OPERATION**.

**Items evidenced**

!!U9 · LLM-Independent Deterministic Detection Floor!! The Sigma layer resolves the
match before any model is invoked. Detection availability is not coupled to model
availability.

!!U20 · Anti-Laundering Quarantine Through Signature!! The adversarial string is
traced from ingest to the human-signed artefact and remains fenced and attributed
at every stage.

**Assertion.** "Both pipelines receive identical bytes. Ours resolves the match
deterministically before a model is called. Then observe the operator-supplied
string travel the full length of the pipeline into the document a human signs,
still fenced, still attributed."

**Disclosure.** Read **WHAT THIS DOES AND DOES NOT SHOW** aloud. Volunteering the
boundary is stronger than being cornered on it.

---

# Section 3 · QUEUE · P1

**Function.** The live intake surface. Separates rule-resolved detections from
those escalated for agentic investigation.

**Route** **QUEUE**.

**Sequence**

1. Locate **THE BELT · HELD FOR THE SWARM** and its ordering note **discharge end at the left · oldest first**.
2. Locate **THE BIN · POSTED BY SIGMA, NO MODEL INVOLVED**.
3. Read that second heading verbatim.
4. Select incident **INC-0417**.

**Items evidenced**

!!U9 · LLM-Independent Deterministic Detection Floor!! Corroborated independently
of Section 2. The claim is asserted by the interface itself, not by the presenter.

**Assertion.** "The heading states the property. Posted by Sigma, no model
involved. Known-threat coverage survives total model unavailability. The agentic
layer is reserved for what rules cannot characterise."

---

# Section 4 · REPLAY · P1

**Function.** Deterministic replay of the investigation, frame-addressable, with
per-claim citation binding. The primary evidential surface.

**Route** **REPLAY**.

**Sequence**

1. Confirm the state chip reads **STATE CAUGHT**.
2. Locate **VIEWING GATE · INCIDENT ARC AT SHUTTLE**.
3. Locate **PIPELINE FILMSTRIP · DRAG TO SHUTTLE**.
4. Scrub the shuttle left to right.
5. Observe lane activation order: **EVIDENCE**, **TRIAGE**, **ENRICH**, **CORRELATE**, **NARRATE**, **PROPOSE**, **GATE**.
6. Locate **NARRATOR · EVERY CLAIM CARRIES ITS LINE**.
7. Read the drop count in the subheading.
8. Select any claim.
9. Inspect the citation chip: host, log source, record number.
10. Inspect the raw line rendered beneath it.
11. Use **OPEN IN EVIDENCE VIEWER** for full-record inspection.
12. Locate **CORRELATOR · KILL CHAIN, ATT&CK v16**.

**On-screen result.** Six claims, each citation-bound. Subheading reads
**0 claims dropped by the citation gate**.

**Items evidenced**

!!KD1 · Quote-Bound Claim Elimination Gate!! A claim whose quoted span is absent
from the evidence supplied to the model is deleted from the verdict. It is not
annotated, downranked, or surfaced for human adjudication.

!!U1 · Per-Claim Log-Line Citation Requirement!! Explainability is a structural
precondition of the pipeline rather than a presentation layer.

!!KD4 · Inter-Agent Provenance Fencing!! The Correlator's output is fenced as
untrusted before the Narrator consumes it, closing agent-to-agent laundering.

**Assertion.** "Every proposition quotes a log line. Where the quoted span is
absent from the supplied evidence, the claim is deleted rather than flagged."

**Under questioning.** "Four of the eighteen defects found on 4 September were
violations of exactly these constraints. That is the evidence that they are
load-bearing rather than decorative."

---

# Section 4b · REPLAY, right column · P1

**Function.** Disclosure of investigative coverage limits, and the corroboration
layer applied beyond them.

**Sequence**

1. Remain on **REPLAY**. Scroll the right column.
2. Locate **PUBLIC CONTEXT · TAVILY**.
3. Locate **WIDE-LENS SWEEP · GEMINI** and the coverage scale beneath the bar.
4. Note the **BLIND SPOT HIGH** classification.
5. Locate **THREAT BRIEF · TAVILY RESEARCH** and **THE QUESTION PUT TO THE OPEN WEB**.
6. Locate **ANALYST IMAGE · GEMINI VISION**.
7. Read **WHAT THE MODEL SAW · OBSERVATION, CARRIES NOTHING**.

**On-screen result.** "40 examined by the investigation · 2,487 on the record ·
2,447 read only by the sweep".

**Items evidenced**

!!KD6 · Declared Blind-Spot Closure Sweep!! Unexamined population is declared
before it is closed. The disclosure precedes the remedy.

!!KD2 · Payload-Level Evidence Class Tagging!! Model output carries `not_evidence`
in the serialised payload. No verdict, lane, or gate decision can bind to it.

**Assertion.** "Most systems present what was found. This one first declares what
was not examined, then closes it. And the panel heading states the constraint:
observation, carries nothing. Model output is classified in the payload as context
and can never be promoted to evidence."

---

# Section 5 · CONFIDENCE · P2

**Function.** Verdict confidence rendered alongside its contradicting evidence and
the adjudication record of rejected material.

**Route** **CONFIDENCE**.

**Sequence**

1. Read **CONFIDENCE IN THE VERDICT · NOT IN THE OUTCOME**.
2. Locate the **SUPPORTING** column and the **SUPPORTS** count.
3. Locate the **COUNTER-EVIDENCE** column and the **COUNTERS** count.
4. Where empty, note **NONE FOUND · COLUMN LEFT OPEN**.
5. Locate **DISCARD TRAY · EVIDENCE CHECKED, THEN CUT**.
6. Inspect **THE LINE, AS IT WOULD HAVE BEEN CITED**.
7. Inspect **WHY IT CAME OFF THE PAN**, **CUT BY**, **CUT AT**.
8. Follow **SEE THE CUTS IN THE LEDGER** for the audit binding.
9. Return via **◀ RETURN TO REPLAY**.

**Items evidenced**

!!U4 · Counter-Evidence-Paired Confidence Disclosure!! Confidence is never rendered
as an isolated scalar. The contradicting set is rendered adjacently, and an empty
set is declared rather than suppressed.

!!U22 · Calibrated Self-Assessment Trust Uplift!! Disclosing calibrated confidence
rather than a raw score produced measured trust gains of 34 to 52 percent at
identical underlying accuracy, while reducing both under-reliance and over-reliance.

**Assertion.** "The verdict argues against itself and exposes the adjudication. The
discard tray retains what was rejected, the reason, the adjudicator and the
timestamp. An empty counter-evidence column is declared, not removed."

---

# Section 6 · EVIDENCE · P2

**Function.** Primary record inspection with custody attestation and quarantined
rendering of operator-supplied content.

**Route** **EVIDENCE**.

**Sequence**

1. Read the framing heading **WOULD THIS STAND UP**.
2. Locate **CHAIN OF CUSTODY**.
3. Locate **INTEGRITY COMPARATOR**.
4. Locate **ATTACKER-CONTROLLED FIELD · QUARANTINED**.
5. Read the fenced content verbatim.
6. Follow **FIND THIS ENTRY IN THE LEDGER**.

**Items evidenced**

!!U20 · Anti-Laundering Quarantine Through Signature!! The adversarial payload is
reproduced byte-exact within a provenance fence. It is neither sanitised nor
elided.

**Assertion.** "That is a live prompt-injection attempt resident in the evidence
set. It is reproduced exactly as received, fenced and attributed. Sanitising it
would produce a false record, which is a worse failure than displaying it."

---

# Section 7 · POLICY · P2

**Function.** The authorisation rulebook. Per-clause action classes, tiers and
automatic caps, rendered as a readable document.

**Route** **POLICY**.

**Sequence**

1. Locate **POLICY SUMMARY**.
2. Inspect the column headers: **CLAUSE**, **ACTION CLASS**, **DESCRIPTION**, **TIER**.
3. Select a clause and read its identifier and tier.

**Items evidenced**

!!U3 · Human-Readable Policy-as-Code Gating!! Authorisation is a readable artefact
under version control, not a confidence threshold internal to a vendor model.

!!U18 · Per-Action-Class Autonomy Assignment!! Autonomy is bound to the action
class rather than the deployment. Reversible classes execute unattended while
consequential classes hold, within one configuration.

**Assertion.** "This is the authorisation surface. A bank's IT function reads it
and amends it. Risk appetite is expressed here, not inferred from a model score."

---

# Section 8 · APPROVALS · P1

**Function.** The policy gate. Per-proposal adjudication with blast-radius bounds,
reversal path and a two-stage human commit.

**Route** **APPROVALS**.

**Sequence**

1. Locate **SHOT QUEUE**. Select a proposal.
2. Read **SHOT PLAN**. The inner ring is declared blast radius; the dashed boundary is the clause cap.
3. Read **WHAT IT DOES, IN WORDS**.
4. Read **ASSETS AFFECTED**.
5. Read **GOVERNING CLAUSE** and **PRECEDENT AND AUTHORITY**.
6. Activate **EXPAND DECISION TRACE**.
7. Read **REVERSAL PATH**. Where reversible, note **ROLLBACK TOKEN** and **ROLL BACK NOW**.
8. Read **INTENT PREVIEW**, then the **WILL DO** and **WILL NOT DO** columns.
9. Locate the key control in the commit bar, reading **KEY SAFE**.
10. Rotate the key. Confirm it reads **KEY ARMED** and the commit control reads **APPROVE AND FIRE**.
11. Do not commit unless the demonstration script requires it.
12. Use **SEE WHY · REPLAY AT THE PROPOSAL** to return to the evidential basis.

**Items evidenced**

!!KD8 · Rollback-Tokened Blast-Radius Policy Gate!! Each proposal is adjudicated
against a named clause with an asset cap, and reversible classes are issued a
rollback token at execution.

!!U19 · Day-One Blast-Radius Ring Design!! Staged radius bounds were specified at
design time against the July 2024 8.5 million-device precedent, not retrofitted
after failure.

!!U18 · Per-Action-Class Autonomy Assignment!! Corroborated here in execution,
having been declared in Section 7.

**Assertion.** "The clause that adjudicated is printed. Not a score. And the
**WILL NOT DO** column enumerates the action's excluded scope before commitment.
The key is deliberately a separate stage from the commit control."

**Constraint.** Do not represent these executions as reaching production
infrastructure. The connectors surface declares **EVERY OUTLET IS BLANKED**.

---

# Section 9 · COMPLIANCE · P1

**Function.** Statutory artefact generation. The investigation record is drafted
into the CERT-In and DPDP forms with per-field provenance.

**Route** **COMPLIANCE**.

**Sequence**

1. Allow 20 seconds without interaction. The drafter runs both guards and an
   independent review; cold latency reaches 50 seconds.
2. Check for the banner **AUTHORED DEMO · NOT THIS DEPLOYMENT'S RECORD**.
3. If present, reload and wait. Do not present the screen in that state.
4. Confirm the **LIVE** chip.
5. Read the clock and the reference **watch it on Overview**.
6. Read **PRE-FILL MAP** and **of the form drafted by machine**.
7. Locate **REGULATORY GUIDANCE · TAVILY**, **INCIDENT ARC**, **OTHER CLOCKS ON THIS INCIDENT**.
8. Read the artefact title **CERT-IN 6-HOUR REPORT**.
9. Traverse the numbered fields.
10. Halt at **ESCAPED REMNANT CARRIED INTO FIELD 08**.
11. Halt at the field tagged **HUMAN REQUIRED**.
12. Read **DPDP ARTIFACT SET** and **DPDP · THE CALL IS YOURS**.
13. Read **WHO FILES THIS**.
14. Locate the **EXPORT** panel.

**Items evidenced**

!!U20 · Anti-Laundering Quarantine Through Signature!! Terminal corroboration. The
adversarial string reaches the signature artefact fenced, and no field of the
report binds to it.

!!U8 · Pre-Enforcement Regulatory Clock Readiness!! The DPDP breach duty was
gazetted 13 November 2025 with Rule 7 activating approximately eighteen months
later. The clock precedes enforcement.

!!KD10 · Denominator-Mandatory Metric Rendering!! Coverage is rendered as
"8 auto plus 2 suggested of 10", never as a bare percentage.

**Assertion.** "The investigation drafts the statutory form. Every machine-filled
field names the record it derives from. The personal-data determination is a legal
finding, so the drafter refuses it and the interface states that the call is
yours. CITINEL drafts, a named human signs, the bank files. No configuration of
this product makes the third step ours."

---

# Section 10 · Statutory artefact export · P1

**Function.** Print-fidelity rendering of the filing, with statutory basis,
submission channels and a signature block.

**Route** **PRINT · SAVE AS PDF** within the **EXPORT** panel, or
`/Report.dc.html?id=INC-0419&kind=certin`.

**Sequence**

1. Activate **PRINT · SAVE AS PDF**.
2. Await assembly. Elapsed time is rendered during the wait.
3. Confirm the stamp **DRAFT · FOR HUMAN REVIEW AND SIGN-OFF**.
4. Read **STATUTORY BASIS AND CLOCK**.
5. Read **HOW THIS IS SUBMITTED**.
6. Read **SIGN-OFF**.
7. Print to PDF.

**Items evidenced**

!!U8 · Pre-Enforcement Regulatory Clock Readiness!! The instrument, its issuing
section and its commencement are printed with the internal finding identifier they
derive from.

!!U20 · Anti-Laundering Quarantine Through Signature!! The fence survives to paper.

**Assertion.** "This is the artefact the bank files. It states the direction it is
made under, the six-hour trigger, and the three published channels. It stamps
DRAFT until a named human signs, and that stamp survives printing."

---

# Section 11 · AUDIT · P1

**Function.** The append-only record. Hash-chained, frame-addressable, with an
independent external witness.

**Route** **AUDIT**.

**Sequence**

1. Inspect the milestone ribbon.
2. Use **QUERY THE REEL** to address a frame by sequence number.
3. Inspect columns **FRAME**, **TIME IST**, **KIND**, **ACTOR**, **STRUCTURED RECORD · PREV → THIS**.
4. Read the previous and current digests on the selected row.
5. **CLEAR THE QUERY**.
6. Read the scope panel **THE LEDGER IS NOT THE MODEL**, and its **RECORDED** and **NEVER RECORDED** lists.
7. Read **WHAT THIS BENCH CANNOT DO**.
8. Locate **AUTOMATION RUNS · n8n**.
9. Execute **WALK THE CHAIN**.
10. Use **EXPORT REEL · JSONL** for raw disclosure.

**Items evidenced**

!!KD3 · Hash-Chained Ledger with External Witness!! Chain verification detects
mutation. An independent witness maintaining its own count detects wholesale
substitution, which chain verification structurally cannot.

!!U5 · Reasoning-Independent Audit Substrate!! The audit record is architecturally
distinct from model output. The distinction is rendered as a named panel.

**Assertion.** "The chain establishes that no frame was altered. The witness is a
separate service holding its own count, so substitution of the entire file is still
detected. The scope panel states what this ledger records and what it never
records."

**Degraded state.** A witness reporting `unavailable` is a third-party timeout.
State it: "the witness is not responding, and we report that rather than assume
concurrence."

---

# Section 12 · CORPUS · P2

**Function.** Detection-content lifecycle. Machine-drafted rules, human accession
review, and portable export.

**Route** **CORPUS**.

**Sequence**

1. Locate **THE COLLECTION** and **COLLECTION LABEL**.
2. Locate **ACCESSION BENCH · AWAITING DETERMINATION**.
3. Locate **DUPLICATE PACKET** and **PACKET WRITTEN · NOT SENT**.
4. Locate **COVERAGE ADVISORY · LYZR**.
5. Execute the export control.

**Items evidenced**

!!U16 · Mandatory Human Accession Review Gate!! Machine-drafted rules are held on
the accession bench pending human determination. Nothing enters the corpus
unreviewed.

!!U14 · Licence-Free Portable Detection Export!! Export is standard-format Sigma,
portable by construction rather than gated by licence tier.

!!U15 · Proven Open-Core SOC Viability Precedent!! A fully unpaywalled GPL core is
commercially demonstrated at the infrastructure layer.

!!U17 · Precedented Detection-Content Bounty Economics!! Paid community detection
contribution has operated as a commercial pattern since 2019.

**Assertion.** "Machine-drafted rules are held for human determination before
accession. Export is open Sigma, so the detection content leaves with the customer.
That is a deliberate constraint on our own lock-in."

---

# Section 13 · EVAL · P1

**Function.** Measurement disclosure. What has been measured, on what population,
and an explicit enumeration of what has not.

**Route** **EVAL**.

**Sequence**

1. Locate **MEASURED STATISTICS** and its **METRIC** and **VALUE** columns.
2. Locate **SOURCE** and **MEASUREMENT SCOPE**.
3. Locate **NOT YET MEASURED · CLAIMED NOWHERE IN THIS PRODUCT**.
4. Read that heading verbatim.
5. Where the harness reports nothing, note **NO RATE PUBLISHED · THE HARNESS REPORTS NO MEASUREMENT**.

**Items evidenced**

!!KD10 · Denominator-Mandatory Metric Rendering!! Terminal expression. The
constraint is elevated to a dedicated surface enumerating the unmeasured set.

**Assertion.** "That heading is the product's measurement discipline stated as an
interface element. There is an enumerated unmeasured set, and nothing within it is
asserted anywhere else in the system. The false-positive rate is a member of that
set. Industry survey range is 46 to 80 percent. Our target is under 10, and we will
publish a measured rate against labelled data rather than assert one now."

**This is the highest-value assertion in the demonstration. Rehearse it verbatim.**

---

# Section 14 · HANDOVER · P2

**Function.** Shift-transfer artefact generated from the ledger rather than
composed by the outgoing operator.

**Route** **HANDOVER**.

**Sequence**

1. Locate **PASSED THIS WATCH · ACTIONS TAKEN, IN ORDER**.
2. Locate **STILL IN SECTION · TRANSFERS WITH THE WATCH** and its **OPEN**, **NEXT MOVE**, **EXPOSURE** columns.
3. Locate **BLOCKED AT THE GATE**.
4. Locate **WATCH LIST · TIME SENSITIVE**, ordered **soonest first**.
5. Locate **EXCEPTIONS THIS WATCH**.
6. Locate **RELIEVED BY** and **REGISTER PAGE**.
7. Note the disclosure **not persisted · no user backend**.

**Assertion.** "A SOC operates in shifts. This artefact is generated from the
ledger, so the incoming operator inherits the recorded sequence rather than a
recollection. And where a capability is unbuilt, the interface declares it."

---

# Section 15 · EXEC · P2

**Function.** Board-level projection. Posture, policy fingerprint and ledger
integrity without evidential detail.

**Route** **EXEC**.

**Sequence**

1. Note **board copy · printable as produced**.
2. Read the lifecycle statement **CAUGHT. CITED. GATED. ACTIONED. CLOSED.**
3. Locate **INCIDENT BOARD · LIVE STATE**.
4. Locate **RESPONSE POLICY & LEDGER INTEGRITY**.
5. Read **policy version**, **sha256**, **ledger state**, **witness**.
6. Note the provenance footnote naming `/api/incidents`.

**Assertion.** "Same record, different consumer. A board requires the policy
fingerprint and ledger integrity, not log lines. The surface prints the endpoint
its figures derive from, so nothing here is unverifiable."

---

# Section 16 · CONNECTORS · P1

**Function.** External surface declaration. Every inbound source, every outbound
capability, and the egress constraint.

**Route** **CONNECTORS**.

**Sequence**

1. Note the build identifier **rig 2026.08.23-rc4**.
2. Locate **INLETS · WHAT FLOWS IN**.
3. Locate **HEADER TANK · ENRICHMENT BUDGET** and its per-**day** allocation.
4. Locate **CACHE · PER EXTERNAL SOURCE**.
5. Locate **OUTLETS · WHAT CITINEL CAN ACTUALLY TOUCH**.
6. Read the badge **EVERY OUTLET IS BLANKED** aloud.
7. Inspect columns **FLANGE**, **RESPONSE ACTION**, **WHAT THE MOCK DOES**, **LAST RUN**.
8. Locate **DEMO FALLBACK CAPTURE**.
9. Open `/api/startuped/signals` for the telemetry contract.

**Items evidenced**

!!KD5 · Deterministic Exact-Host Egress Allow-List!! Egress is deny-by-default
against exact hostnames over https. Operator-configured destinations are pinned to
their configured host.

!!KD7 · Field-Refusing Telemetry Privacy Boundary!! The analytics connector refuses
any field capable of carrying incident content. Refusal, not redaction.

**Assertion.** "Six destinations behind an exact-host allow-list, operator-
configured destinations pinned to their host, three further destinations mediated
by a policy-gated subprocess. Not 'everything behind an allow-list', which would be
imprecise."

**Under questioning on response transport.** "The ticketing leg executes against
the live deployment and creates a real issue. The messaging leg does not, and the
ledger records `not_configured` rather than asserting delivery. That refusal is the
control operating correctly."

---

# Section 17 · Write authority · P3

**Function.** Demonstration of fail-closed write semantics and distinguishable
denial states.

**Sequence**

1. Open **CONNECTORS**, locate **ARM THIS DEVICE**, select **CLEAR**.
2. Attempt any write action.
3. Read the returned sentence.
4. Re-arm: operator name, token, **SAVE**.

**Items evidenced**

!!KD9 · Fail-Closed Distinguishable Write Denial!! Absent authority returns 401.
A deployment with writes disabled returns 503. The two failures are separable by
the operator without inspection.

**Assertion.** "Absent token and disabled deployment are distinct conditions and
return distinct responses. A demonstration device that silently lost write
authority is a predictable failure we chose to make visible."

---

# Section 18 · Non-interface differentiators

Items evidenced by external research rather than by the console. Deploy under
questioning only.

## Regulatory positioning

!!U6 · India-Regulator Form Drafting White Space!! Across a 2026 twelve-platform
agentic-SOC comparison, no named platform references CERT-In, DPDP, RBI or SEBI.
*Qualification: one comparison's omission, not an exhaustive per-vendor audit.*

!!U7 · Adversarially Refuted Competitor Parity Claim!! A competitor's published
claim to auto-generate the DPDP breach artefact with a dual clock failed
independent verification, nought to three.

## Buyer economics

!!U10 · Transparent Price Band Against Quote-Walls!! The closest comparable
platform has withdrawn all pricing behind a sales-quote wall across every tier.

!!U11 · Competitor-Sourced Human-Analyst Cost Benchmark!! A competitor's own
pricing surface caps a tier at the stated average annual output of a human tier-1
analyst, validating the cost baseline independently.

!!U12 · Order-of-Magnitude Buyer-Band Displacement!! The last disclosed incumbent
price exceeds the target segment's annual budget band by roughly an order of
magnitude. *Present as historical; current pricing is not public.*

!!U13 · Regulator-Built B2B2X Distribution Channel!! SEBI's CSCRF directs the
exchanges to operate Market-SOCs onboarding small regulated entities. No named
competitor is documented as addressing this channel.

## Sustainability and lock-in

!!U15 · Proven Open-Core SOC Viability Precedent!! Corroborates Section 12.
!!U17 · Precedented Detection-Content Bounty Economics!! Corroborates Section 12.

## Model and architecture selection

!!U2 · Injection-Resistant Foundation Model Selection!! Independent 2026
benchmarking recorded a 0.0 percent verbatim-hijack rate against a worst-case 86.2
percent across eight models. *Qualification, always spoken: a single
non-peer-reviewed preprint, regex-based classifier, thirty trials per model.
Illustrative, not certified.*

!!U21 · Risk-Calibrated Trust Dial Evidence!! Autonomous-vehicle research validates
the adjustable-autonomy pattern and simultaneously measures increased risk at
higher settings. Deploy the warning alongside the validation.

!!U24 · Confabulation-Resistant Aggregation Design Choice!! Naive majority voting
between model agents is empirically unstable under shared bias, so vote frequency
is not treated as a correctness signal.

!!U25 · Scaffolding-Level Reversible Improvement Loop!! Durable improvement is
achievable through prompt, memory and control-logic changes without parameter
updates. Faster and reversible.

!!U26 · Anti-Corruption Layer Boundary Pattern!! The domain-driven mediation
pattern is the authoritative name for the isolation boundary between the core and
external systems.

!!U27 · Self-Verification Refusal by Architecture!! Model self-verification carries
documented self-deception and reward-tampering risk, and fails specifically under
confident error. The policy gate and mandatory human signature are the structural
response.

!!U28 · Base-Model Attack Inheritance Mitigation!! Approximately two-thirds of
attacks against tool-using agents are inherited from the base model. Alignment does
not transfer once an agent acquires tools, memory and autonomy.

!!U29 · Multi-Layer Hybrid Defence Convergence!! No single defence is robust across
scalability, adversarial robustness, overhead and coverage. The quarantine plane,
detector, egress allow-list and human gate constitute the layered response.

!!U30 · Low-Latency Consensus Reference Protocol!! A consensus protocol achieving
1.2 to 20 times lower latency within 2.5 percent accuracy exists as a reference
should multi-agent verdict aggregation be introduced.

## Market context

!!U23 · Government-Funded PACS Distribution Rail!! The PACS computerisation
programme covers 63,000 societies at ₹2,516 crore, approved 29 June 2022, on a
common NABARD-built platform serving precisely the target segment.
*Excluded: the "67,930 sanctioned" and "₹741.34 crore released" figures were
checked and refuted. Do not cite them.*

---

# Section 19 · Assertion constraints

Four statements are prohibited. Each is either unmeasured or untrue, and each is
recoverable by a judge in minutes.

1. **Any false-positive rate as achieved.** Unmeasured. State the target and the industry survey range.
2. **That any artefact was filed.** CITINEL drafts, a human signs, the bank files.
3. **That a response action reached production infrastructure.** All executions are simulated. The interface declares **EVERY OUTLET IS BLANKED**.
4. **That the messaging transport is operational.** It is not. Ticketing is. The ledger records `not_configured`.

---

# Section 20 · Degraded-state responses

| Observed state | Response | Action |
|---|---|---|
| **AUTHORED DEMO** banner | "Our own guard is reporting that the live record did not load." | Reload. Do not present. |
| Witness `unavailable` | "The witness is not responding. We report that rather than assume concurrence." | Continue. |
| Receipt `not_configured` | "The ledger refuses to assert delivery. That refusal is the control operating." | Continue. |
| Compliance latency | No commentary for 20 seconds. | Warm after the morning pre-flight. |
| Unclassified failure | "Whatever occurred, the ledger recorded it." | Open **AUDIT**. |

---

# Section 21 · Item to screen matrix

| Item | Name | Screen |
|---|---|---|
| !!KD1!! | Quote-Bound Claim Elimination Gate | 4 REPLAY |
| !!KD2!! | Payload-Level Evidence Class Tagging | 4b REPLAY right |
| !!KD3!! | Hash-Chained Ledger with External Witness | 11 AUDIT |
| !!KD4!! | Inter-Agent Provenance Fencing | 4 REPLAY |
| !!KD5!! | Deterministic Exact-Host Egress Allow-List | 16 CONNECTORS |
| !!KD6!! | Declared Blind-Spot Closure Sweep | 4b REPLAY right |
| !!KD7!! | Field-Refusing Telemetry Privacy Boundary | 16 CONNECTORS |
| !!KD8!! | Rollback-Tokened Blast-Radius Policy Gate | 8 APPROVALS |
| !!KD9!! | Fail-Closed Distinguishable Write Denial | 17 Write authority |
| !!KD10!! | Denominator-Mandatory Metric Rendering | 1 OVERVIEW, 9 COMPLIANCE, 13 EVAL |
| !!U1!! | Per-Claim Log-Line Citation Requirement | 4 REPLAY |
| !!U2!! | Injection-Resistant Foundation Model Selection | 18 spoken |
| !!U3!! | Human-Readable Policy-as-Code Gating | 7 POLICY |
| !!U4!! | Counter-Evidence-Paired Confidence Disclosure | 5 CONFIDENCE |
| !!U5!! | Reasoning-Independent Audit Substrate | 11 AUDIT |
| !!U6!! | India-Regulator Form Drafting White Space | 18 spoken |
| !!U7!! | Adversarially Refuted Competitor Parity Claim | 18 spoken |
| !!U8!! | Pre-Enforcement Regulatory Clock Readiness | 9 COMPLIANCE, 10 export |
| !!U9!! | LLM-Independent Deterministic Detection Floor | 2 DEMO, 3 QUEUE |
| !!U10!! | Transparent Price Band Against Quote-Walls | 18 spoken |
| !!U11!! | Competitor-Sourced Human-Analyst Cost Benchmark | 18 spoken |
| !!U12!! | Order-of-Magnitude Buyer-Band Displacement | 18 spoken |
| !!U13!! | Regulator-Built B2B2X Distribution Channel | 18 spoken |
| !!U14!! | Licence-Free Portable Detection Export | 12 CORPUS |
| !!U15!! | Proven Open-Core SOC Viability Precedent | 12 CORPUS |
| !!U16!! | Mandatory Human Accession Review Gate | 12 CORPUS |
| !!U17!! | Precedented Detection-Content Bounty Economics | 12 CORPUS |
| !!U18!! | Per-Action-Class Autonomy Assignment | 7 POLICY, 8 APPROVALS |
| !!U19!! | Day-One Blast-Radius Ring Design | 8 APPROVALS |
| !!U20!! | Anti-Laundering Quarantine Through Signature | 2 DEMO, 6 EVIDENCE, 9 COMPLIANCE, 10 export |
| !!U21!! | Risk-Calibrated Trust Dial Evidence | 18 spoken |
| !!U22!! | Calibrated Self-Assessment Trust Uplift | 5 CONFIDENCE |
| !!U23!! | Government-Funded PACS Distribution Rail | 18 spoken |
| !!U24!! | Confabulation-Resistant Aggregation Design Choice | 18 spoken |
| !!U25!! | Scaffolding-Level Reversible Improvement Loop | 18 spoken |
| !!U26!! | Anti-Corruption Layer Boundary Pattern | 18 spoken |
| !!U27!! | Self-Verification Refusal by Architecture | 18 spoken |
| !!U28!! | Base-Model Attack Inheritance Mitigation | 18 spoken |
| !!U29!! | Multi-Layer Hybrid Defence Convergence | 18 spoken |
| !!U30!! | Low-Latency Consensus Reference Protocol | 18 spoken |
| !!H1!! | Glass-Box Cited Triage Pipeline | 2, 3, 4 |
| !!H2!! | Readable Per-Class Autonomy Dial | 7, 8 |
| !!H3!! | Injection-Hardened Quarantine Plane | 2, 6, 9, 16 |
| !!H4!! | Regulator-Ready Compliance Clock | 9, 10 |

**Distribution.** Twenty items are evidenced on the console. Twenty are deployed
under questioning. The four headline features are compositions of the first group.

---

# Section 22 · Reduced demonstration path

Seven interactions covering the six highest-value items where the slot is
compressed.

1. **QUEUE**. Indicate **THE BIN · POSTED BY SIGMA, NO MODEL INVOLVED**. Evidences !!U9!!.
2. **REPLAY**. Select a claim. Expose the citation chip. Evidences !!KD1!!.
3. **REPLAY** right column. **WIDE-LENS SWEEP · GEMINI**, 40 of 2,487. Evidences !!KD6!! and !!KD2!!.
4. **APPROVALS**. **EXPAND DECISION TRACE**, then **WILL NOT DO**. Evidences !!KD8!!.
5. **COMPLIANCE**. Field 08, fenced adversarial content. Evidences !!U20!!.
6. **EVAL**. Read **NOT YET MEASURED · CLAIMED NOWHERE IN THIS PRODUCT**. Evidences !!KD10!!.
7. **AUDIT**. **WALK THE CHAIN**. Evidences !!KD3!!.
