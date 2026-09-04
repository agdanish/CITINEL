# CITINEL demo drill: practising all 40, honestly

*Written 5 September 2026. Companion to `CITINEL-UVP-MASTER-LIST.md`, which says
WHAT the 40 items are. This one says HOW to check each, and what to say.*

## The honest split, read this first

You cannot demonstrate all 40 in the app. Twenty have something to click. Twenty
are external research about competitors, regulations and published papers, and
there is nothing in CITINEL to show for them. Pretending otherwise is the exact
failure this product exists to refuse.

| Group | Count | What you do |
|---|---|---|
| **A. Show it live** | 10 | Open a screen or a URL. A judge can follow along. |
| **B. Show it in the app or the code** | 10 | Open a screen, or open one file if pushed |
| **C. Say it, cite it, do not fake it** | 20 | A sentence plus where the evidence lives |

Every item below is **DO / SEE / SAY**. Practise the DO until it is muscle memory,
because fumbling for a URL in front of a jury costs more than the point is worth.

**Before any of this:** the laptop must be armed and the rail's dot green. If a
screen ever shows a red **AUTHORED DEMO** banner, stop and reload. That banner
means you are looking at sample content, not this deployment's record.

---

# Group A · The ten differentiators you show live

## KD1 · Verdicts cite the exact log line, and unsupported claims are deleted

**What it is (plain):** the AI is not allowed to say anything it cannot quote. If a
claim's quote is not literally in the evidence it was shown, the claim is thrown
away, not flagged for a human to catch later.

**DO**
1. Open Replay for INC-0417
2. Point at the NARRATOR panel, lower left
3. Click any claim

**SEE** Each claim carries a yellow citation chip naming the host, the log source
and the record number, and the raw log line opens underneath it. The header reads
`0 claims dropped by the citation gate`. Verified live: 6 claims, each with
`finding_index` and `quoted_span`.

**SAY** "Every sentence here quotes a log line. If the quote is not in the
evidence, we delete the claim rather than flag it. Zero were dropped on this run,
and the count is on screen either way."

## KD2 · The model's observations are marked as not-evidence, in the data

**What it is:** when Gemini reads all 2,487 findings, its summary is tagged in the
payload as `not_evidence`, so no verdict can ever rest on it.

**DO**
1. Same Replay screen, scroll the right column to **WIDE-LENS SWEEP · GEMINI**
2. Or open `https://citinel-web.onrender.com/api/incidents/INC-0417/sweep`

**SEE** "context only, never evidence: no verdict, lane or gate decision moves
because of it". Verified live: `not_evidence` is present in the JSON.

**SAY** "A model looked at everything. We wrote into the data itself that this is
context and never evidence, so it cannot quietly become a fact."

## KD3 · A hash-chained ledger with an outside witness

**What it is:** every action is a linked block. A second, independent service keeps
its own count, so someone replacing the whole file still gets caught.

**DO**
1. Open `https://citinel-web.onrender.com/api/ledger/verify`
2. Or open the AUDIT screen and press WALK THE CHAIN

**SEE** `chain intact: 5,798 entries` plus a witness status.

**SAY** "The chain proves nothing was edited. The witness proves nothing was
swapped wholesale, which the chain alone cannot see."

**If the witness says `unavailable`:** that is the Lyzr call timing out. Say so.
"The witness is a third party and right now it is not answering. We report that
rather than pretend it agreed." That is a strong answer, not a weak one.

## KD4 · One agent cannot launder text into another

**What it is:** the Correlator's summary is fenced as untrusted before the Narrator
reads it, so a poisoned log cannot travel between agents as if it were clean.

**DO**
1. Replay, watch the filmstrip lanes CORRELATE then NARRATE
2. If pushed for proof: `agents/pipeline.py`, `correlator_summary_evidence`

**SEE** The lanes are separate stages with the fence between them.

**SAY** "Agent output is treated as untrusted input by the next agent. We found and
fixed a real bug here on 4 September, which is why we know the rule is
load-bearing."

## KD5 · Outbound traffic is a deny-by-default list of exact hosts

**What it is:** CITINEL can only talk to a fixed list of addresses, over https. A
malicious log cannot make it call somewhere else.

**DO**
1. Open the CONNECTORS screen
2. Or, if pushed, `agents/quarantine.py`

**SEE** The connector list with configured status.

**SAY** "Six destinations behind an exact-host allow-list, the operator-configured
ones pinned to their host, three more reached through a policy-gated CLI. Not
'everything is behind an allow-list', that would be sloppy."

## KD6 · We say out loud what we did not look at, then go and look

**What it is:** the swarm examined 40 findings out of 2,487. Rather than hide that,
the screen states it, then a wide-lens pass reads the rest.

**DO**
1. Replay, right column, **WIDE-LENS SWEEP**
2. Read the scale line under the bar

**SEE** `40 examined by the investigation · 2,487 on the record · 2,447 read only
by the sweep`, with a BLIND SPOT HIGH tag.

**SAY** "Most tools show you what they found. This one shows you what it did not
look at, then closes the gap and tells you what turned up."

## KD7 · The analytics connector refuses to carry incident content

**What it is:** the growth-metrics integration can send counts and nothing else. It
refuses any field that could leak a hostname or a log line.

**DO** Open `https://citinel-web.onrender.com/api/startuped/signals`

**SEE** Signals with descriptions like "Counts only; no incident content".

**SAY** "The privacy boundary is in the code, not in a policy document. The
connector refuses fields rather than stripping them."

## KD8 · The policy gate, with rollback tokens and blast-radius caps

**What it is:** every proposed action passes a readable rulebook first. The rule
that decided is shown, with the blast radius drawn.

**DO**
1. Open APPROVALS
2. Click a card
3. Press **EXPAND DECISION TRACE**

**SEE** The clause, the tier, the asset cap, the rollback position, and a ring
diagram of declared blast radius against the clause's automatic cap.

**SAY** "A bank's IT head can read this rule and change it. It is not a confidence
score hidden inside a vendor's model."

**Never say** these actions touched real infrastructure. Every endpoint is
simulated and the card says so.

## KD9 · Writes fail closed, and the two failures are distinguishable

**What it is:** an unarmed device cannot change anything, and the error tells you
which problem you have.

**DO**
1. Open Settings, press CLEAR
2. Try any action
3. Re-arm afterwards

**SEE** One plain sentence. Verified live: a write with no token returns **401**.
A deployment with writes switched off returns **503**.

**SAY** "Wrong token and no token are different failures, and we made them say
different things, because a demo laptop that silently lost write access is how you
get a nasty surprise on stage."

## KD10 · No measurement appears without its denominator

**What it is:** never "40 findings examined". Always "40 of 2,487".

**DO** Point at any number on any screen.

**SEE** `40 of 2,487`. `8 auto + 2 suggested of 10`. `16 of 16 connectors`.
`chain intact: 5,798 entries`.

**SAY** "Every number on every screen carries what it is out of. A percentage
without a denominator is a marketing number."

---

# Group B · Ten you can still show, in the app or the code

| # | What it is, plainly | DO | SAY |
|---|---|---|---|
| 3 | The autonomy rulebook is readable policy-as-code, not a hidden threshold | POLICY screen | "The rule is a document you can read and change" |
| 4 | Confidence is shown with its own counter-evidence, never as a lone clean number | CONFIDENCE screen | "It shows what argues against the verdict, and calls it confidence, not certainty" |
| 5 | The audit trail is structurally separate from the AI's reasoning | AUDIT screen, then Replay | "Two different things. Most tools never have to separate them because they never show reasoning" |
| 9 | Known threats are caught without any AI being involved | QUEUE screen | "Sigma fires deterministically before a model is called. If the AI is down, detection still works" |
| 14 | Rules export in a portable open format, not locked to us | CORPUS, EXPORT | "You can take the detection content and leave. That is deliberate" |
| 16 | Machine-drafted rules face a mandatory human review gate | CORPUS review queue | "Nothing the machine writes joins the corpus without a human passing it" |
| 18 | Autonomy is set per action class, not per deployment | POLICY, per-clause tiers | "Reversible things run themselves. Consequential things wait. Same system, different classes" |
| 19 | Blast-radius rings designed in from day one | APPROVALS ring diagram | "Modelled on the CrowdStrike July 2024 lesson. Designed in, not bolted on after a failure" |
| 20 | A poisoned log cannot launder itself into the signed report | COMPLIANCE field 08, and the printed report | "It is reproduced verbatim, fenced, labelled attacker-controlled, and no field of the report rests on it" |
| 8 | The compliance clock was built ahead of the duty coming into force | Printed report, STATUTORY BASIS block | "Rules gazetted 13 November 2025, Rule 7 activates about eighteen months later. We built ahead of it" |

**The printable report is your strongest single artefact.** Open
`/Report.dc.html?id=INC-0419&kind=certin`, press Cmd+P, hand a judge the PDF. It
carries the statute, the clock, the submission channels, every field with its
source, the masked identifiers awaiting a redaction decision, and a signature
block. Items 8 and 20 both live on that one page.

---

# Group C · Twenty you say and cite, with nothing to click

These are competitor research, regulation and published papers. There is no screen.
Say the sentence, name the source, and if a judge wants more, the citation is in
`CITINEL-UVP-MASTER-LIST.md`.

**The strongest three, use these:**
- **No competitor drafts CERT-In or DPDP.** In a 2026 twelve-platform agentic-SOC comparison, none mentions CERT-In, DPDP, RBI or SEBI anywhere. Caveat if pushed: it is one comparison article's silence, not an exhaustive per-vendor audit.
- **The nearest claimant does not hold up.** A competitor's public claim to auto-generate the DPDP breach PDF with a dual clock failed independent verification 0-3.
- **PACS is a real, funded national rail for exactly this segment.** 63,000 societies, ₹2,516 crore, approved 29 June 2022. Do NOT quote the "67,930 sanctioned / ₹741.34 crore" figures. Those were checked and refuted.

**Say with the caveat attached, always:**
- The prompt-injection benchmark, 0.0% hijack rate against up to 86.2%. One non-peer-reviewed preprint, 30 trials per model. Say "illustrative, not certified". If you drop the caveat and a judge knows the paper, you lose more than the point was worth.

**The rest** are economics (10 to 13), sustainability precedent (15, 17), and design
validation from published research (21, 22, 24 to 30). Use them only if a judge
opens the topic. Do not volunteer twenty research citations at a jury.

---

# The four things you must never say

1. **Any false-positive rate as achieved.** You MAY say: "the industry runs 46 to 80 percent by survey; we target under 10 percent and publish our measured rate on labeled data rather than claim one." You may NOT say you hit it. It is unmeasured.
2. **That anything was filed.** CITINEL drafts, a human signs, the bank files.
3. **That a response action touched real infrastructure.** All simulated.
4. **That the Slack leg works.** It does not. The ticketing leg does. The ledger says `not_configured` rather than claiming a message was sent, and that is the product working correctly in public.

# If something breaks on stage

- **A screen shows the red AUTHORED DEMO banner** → "That is our own guard telling us the live record did not load. Reload." Then reload. Do not present that screen.
- **The witness says unavailable** → "A third party is not answering, and we report that rather than assume agreement."
- **A receipt says not_configured** → "That is the Slack credential, and the ledger refuses to claim a message was sent. That refusal is the feature."
- **Compliance takes ~20 seconds to load** → say nothing, it is warm after the morning pre-flight. If it is cold it can take 50.
