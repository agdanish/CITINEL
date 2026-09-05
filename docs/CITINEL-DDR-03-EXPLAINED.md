# CITINEL
## Security and threat model, explained

*A plain-English reading of due-diligence sheet 03, "The attacker's text is the
payload." Every box, every arrow, every word on that sheet, in short sentences.
Read once, top to bottom.*

---

# The title, top left

**"The attacker's text is the payload, not the attacker's malware."**

- Most people fear the attacker's software. Malware.
- This sheet says the real danger is different.
- The danger is the attacker's **words**.
- Those words arrive inside normal log lines.
- Our AI reads those logs to do its job.
- So an attacker can write instructions into a log.
- The AI might obey them by mistake.
- This sheet shows how we stop that.

**Payload** means the harmful part that gets delivered.

# The big number 4, top right

- A log line must cross **four boundaries**.
- Only then does it reach the ledger.
- Each boundary is a wall. Each wall does one job.
- The diagram below shows all four.

---

# The main diagram: one log line's journey

The heading says **defence in depth**. That means many layers, not one lock. If
one layer fails, the next one still holds.

## The starting box, far left

**"untrusted attacker-controlled text, arriving as ordinary telemetry"**

- **Telemetry** means machine logs and events.
- A log line arrives. It looks normal.
- But an attacker may have written it.
- We do not know yet. So we trust nothing.
- The arrow says **"carries: raw log line."**
- Raw means untouched. Exactly as it arrived.

## Band 1 · The taint envelope

- **Taint** means marked as possibly dirty.
- **Envelope** means we wrap it in a cover.
- Every log string gets wrapped as **TaintedText**.
- The wrapper holds four facts about the text.
- **Source**: where it came from.
- **Event class**: what kind of event.
- **Timestamp**: when it happened.
- **Detail**: the actual content.
- This is called **provenance**. It means origin history.
- The provenance travels with the text everywhere.
- The text can never lose its label.
- Arrow out: **"carries: wrapped string + provenance."**

## Band 2 · The deterministic injection detector

- **Injection** means sneaking instructions into data.
- **Deterministic** means plain code. Not AI.
- Same input always gives the same answer.
- The big **12** means twelve attack patterns.
- Their names are **INJ-001 to INJ-012**.
- The patterns look for six kinds of trick.
- **Instruction override**: "ignore your previous orders."
- **Role reassignment**: "you are now the admin."
- **Benign-marking**: "mark this as safe."
- **Logging suppression**: "do not record this."
- **Credential exfiltration**: "send me the passwords."
- **Fetch primitives**: "go download this file."

**The rule in the bold box**

- **"It flags and never filters."**
- Flag means put a warning label on.
- Filter means remove or change the text.
- We only label. We never change.
- Editing the evidence makes it false.
- A false record is worse than a dangerous one.

**The two small boxes**

- Clean line: **passes, unmarked**. No label needed.
- Matches a pattern: **flag attached, text unchanged**.
- Arrow out: **"carries: flagged text, never edited."**

## Band 3 · The inter-agent fence

- **Inter-agent** means between two AI agents.
- **Agent A** reads the evidence and drafts a summary.
- That summary is written by an AI model.
- Arrow: **"carries: model-written summary."**
- Now comes the **re-quarantine wall**.
- **Quarantine** means isolate as untrusted.
- **Re-quarantine** means do it again.
- Agent A's summary is treated as untrusted too.
- **Agent B** receives it already re-quarantined.
- Why? Agent A might have been fooled.
- If so, its summary could carry the poison.
- Re-quarantining stops the poison spreading.
- Arrow out: **"carries: re-quarantined summary."**

## Band 4 · The egress allow-list

- **Egress** means traffic going out.
- **Allow-list** means the only permitted destinations.
- **"Six doors, exact host."**
- Six websites the system may talk to.
- Nothing else. Ever.

**The six doors**

- `api.anthropic.com`: the Claude AI models.
- `www.virustotal.com`: checks if files are known-bad.
- `api.abuseipdb.com`: checks if IP addresses are known-bad.
- `api.tavily.com`: searches the public web.
- `generativelanguage.googleapis.com`: Google Gemini AI.
- `www.startuped.ai`: receives product usage counts only.

**The red line**

- 🔴 **"unlisted host, refused, dead end."**
- Any other address is blocked. Full stop.
- Even if a log line asks for it.

**The annotation**

- **Exact-host matching.** The name must match perfectly.
- **HTTPS only.** Encrypted connections only.
- **No wildcards.** No "anything.example.com."
- **No suffix matching.** "evil-anthropic.com" does not pass.
- Arrow out: **"carries: chained entry, appended."**

## The ledger, far right box

- **Ledger** means the permanent record book.
- Every action gets written here.
- **SHA-256** is a fingerprint method for data.
- **Chained** means each entry links to the last.
- **Append-only** means add only. Never edit. Never delete.
- Change one entry, the whole chain breaks.

## The grey line under the diagram

**Runtime detail** means settings applied when the system starts.

- **Lyzr's** address is added at start-up, from its configured URL.
- **n8n** is pinned to one configured instance.
- **Swytchcode, GitHub and Slack** are reached differently.
- Through a **policy-gated CLI subprocess**.
- CLI means a command-line tool.
- Subprocess means a separate program.
- Policy-gated means a rulebook checks it first.

---

# The four panels in the middle row

## Panel 1 · What verify_chain cannot detect

- **verify_chain** is our chain checker.
- It recomputes every fingerprint.
- It catches edits, deletions and reorders.
- But one attack beats it.
- **Wholesale file replacement.**
- The attacker rewrites the whole file from the start.
- Every link matches. The chain looks perfect.
- But the whole thing is fake.
- So we need a second witness. Outside.
- **Lyzr** holds the head fingerprint remotely.
- It also holds the entry count.
- If the file is swapped, Lyzr disagrees.
- The screen shows **diverged**.

**The annotation about the bug**

- A witness that is just slow is **lagging**.
- That is not **tampering**.
- We once mixed those two up.
- The executive screen said "tamper" on a good ledger.
- We fixed it. The fix is commit `5699f9e`.
- We show our own bug on purpose.

## Panel 2 · Fail-closed writes

- **Fail-closed** means: when unsure, lock the door.
- **Writes** means any change to the system.
- **Middleware** is a checkpoint every request passes.
- It catches every request that is not a read.
- Reads are called **GET**. They are always allowed.
- Under **/api/** means every system endpoint.
- Two possible refusals.

**503**

- The write token is not set on the server.
- Writes are switched off completely.
- The system is a safe read-only demo.

**401**

- A token was sent. It is wrong.
- It was compared with `secrets.compare_digest`.
- Not with a plain equals sign.
- compare_digest takes the same time every time.
- Attackers cannot guess from timing.

**The annotation**

- 503 and 401 look different on purpose.
- "Switched off" and "not allowed" are different facts.
- The caller deserves to know which one.

## Panel 3 · The privacy boundary, a one-way valve

- **One-way valve**: things flow out, never in.
- **Startuped** is a product-analytics partner.
- We send it usage numbers. Nothing else.

**The dashed box, refused**

- incident_id, host, ip, finding and kin.
- **Kin** means anything similar to those.
- These are **refused, not stripped**.
- Refused means the whole send is rejected.
- Stripped would mean remove that field and continue.

**The solid box, allowed**

- Only five counts leave.
- Investigated. Cited. Gated. Drafted. Signed off.
- Just numbers. No names. No details.

**The annotation**

- Refusing is safer than stripping.
- A stripper might miss one field.
- It would fail silently. Nobody notices.
- A refusal never fails silently.

## Panel 4 · The PII guard, what it will not decide

- **PII** means personal identifiable information.
- Things that reveal who a person is.
- The guard detects six kinds.
- Email. PAN card numbers. Windows SIDs.
- Domain accounts. Indian mobile numbers. Aadhaar numbers.
- **In context** means it checks surrounding text too.
- It **masks** them before returning. Hides part of them.

**The annotation**

- **Redaction** means permanently blacking out.
- That is the signer's call. A human decides.
- The guard **mitigates**. It reduces risk.
- It **never solves**. It does not decide.
- It refuses to decide for the human.

---

# The two panels at the bottom

## Panel 5 · The attack-then-defence case: INJ-005

- INJ-005 is one of our twelve patterns.
- We found a bug in our own detector.

**Before**

- INJ-005 matched normal Windows Event XML.
- Specifically `<System>` elements in **Sysmon** logs.
- Sysmon is a Windows monitoring tool.
- So normal logs were flagged as attacks.
- **False positives.** Crying wolf.
- We found it by running real data through.
- The **BOTS corpus** is real attack data from Splunk.
- Not by reading the code. By testing.

**After**

- We narrowed the pattern.
- Now it only matches **LLM control tokens**.
- Those are special markers AI models understand.
- Normal logs pass. Real attacks still get caught.

**The annotation**

- A detector that cries wolf gets switched off.
- Nobody keeps a noisy alarm on.
- So false alarms are a security problem too.

## Panel 6 · What we do not claim

*This is the honesty box.*

- 🔴 **No penetration test** has been done.
- Nobody has tried to break in professionally.
- 🔴 **No formal verification.** No mathematical proof.
- 🔴 **False-positive rate is unmeasured.** We have no number.
- 🔴 **Response actions hit simulated endpoints.**
- We never touch a real bank system.
- These defences are **designed and tested**.
- They are **not independently audited**.
- Nobody outside has checked them yet.

---

# The footer

**Left:** "AEROFYTA · sits beside your SIEM · the bank keeps its SIEM. We draft, we
never file."

- **AeroFyta** is the team name.
- **SIEM** is the bank's existing security log system.
- We do not replace it. We sit next to it.
- We write drafts. A human files them.

**Right:** "Every number, path and identifier on this sheet is sourced from the
CITINEL engineering record."

- Nothing here is invented.
- Every fact comes from the real codebase.

---

# The one-paragraph version

- A log line arrives. We trust nothing.
- We wrap it with its origin. Band one.
- We scan for twelve attack patterns. Band two.
- We label but never edit.
- One AI's output is re-isolated before the next AI. Band three.
- Only six exact websites may be contacted. Band four.
- Everything is written to an unbreakable chain.
- An outside witness guards against total replacement.
- Writes fail closed. Two clear error codes.
- Private data never leaves. Refused, not stripped.
- Personal identifiers are masked. Humans decide redaction.
- We found and fixed our own false alarm.
- We say plainly what has not been tested.

---

# Small glossary

| Word | Simple meaning |
|---|---|
| SOC | The security team's control room |
| Telemetry | Machine logs and events |
| Payload | The harmful thing being delivered |
| Provenance | Where something came from |
| Taint | Marked as possibly unsafe |
| Injection | Sneaking commands into data |
| Deterministic | Plain code, same answer every time |
| Agent | One AI worker with one job |
| Quarantine | Isolate as untrusted |
| Egress | Traffic leaving the system |
| Allow-list | The only permitted destinations |
| Host | A website's exact address |
| Ledger | The permanent record book |
| SHA-256 | A data fingerprint method |
| Append-only | Add only, never edit or delete |
| Witness | An outside party holding a copy |
| Middleware | A checkpoint every request passes |
| Token | A secret password for writes |
| PII | Data that identifies a person |
| Redaction | Permanently blacking out text |
| False positive | A false alarm |
| Simulated endpoint | A fake target, not a real system |
