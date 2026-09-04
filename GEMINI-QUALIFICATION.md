# CITINEL × Gemini — qualification dossier

*Written 4 Sep 2026. No criteria for this track have been published to us —
`PARTNER-ONBOARDING.md` records it as a "real, organizer-tracked category…
but no redemption/credential document exists", confirmed only by a
finalist-group poll. So this is an evidence index rather than a checklist.*

**If you receive the actual criteria, paste them in and I will map each one.**

---

## The one-sentence claim

Gemini is used twice, and each time for something no other model in CITINEL's
stack can do — once for context nothing else can hold, once for a modality
nothing else can read — with both results deliberately barred from becoming
evidence.

---

## 1. The wide-lens sweep: reading what nobody read

**The gap it closes is measurable and was already disclosed by the product.**

CITINEL's agent swarm examines `MAX_EVIDENCE_FINDINGS` — 40 — and says so out
loud when an incident carries more. On INC-0417 that is **40 of 2,487
findings: 98% of the record read by no model at all.** The system was honest
about the limit; it just could not close it.

Gemini's long context holds every finding in one call, so it answers a
question nothing else here can: *what is in the part nobody looked at?*

**A real run, on the live deployment, 3 Sep 2026** — `seq=5778` on the audit
ledger, still there after four redeploys:

| Found only outside the 40-finding window | Count |
|---|---|
| `we8105desk.waynecorpinc.local` | **1,348 findings** |
| `T1490` — Inhibit System Recovery (shadow-copy deletion) | 4 |
| `T1204.002` — User Execution, malicious Office file | 9 |

Read what that is. `T1204.002` is **the initial access** — the malicious Office
document — and `T1490` is **the ransomware destroying recovery options** before
encrypting. On a Cerber ransomware incident, the delivery vector, the
recovery-destruction step, and an entire host carrying 1,348 findings were all
invisible to the investigation that produced the cited verdict.

Gemini's own words: *"critical post-exploitation activity, including
persistence, data destruction, and Office-based initial access, which were
entirely absent from the first 40 findings."*

`blind_spot_risk: high`.

**Current state, stated precisely.** The ledger frame proving this run stands
on the live chain — `seq=5778`, `swept=2487 of 2487`, `blind_spot_risk=high`,
verifiable now at `GET /api/incidents/INC-0417/audit` under actor
`gemini-sweep`. The sweep *artifact* itself returns 404, because it was written
before runtime artifacts were moved onto the persistent disk and a redeploy
took it. One click of **RUN WIDE-LENS SWEEP** on the Replay screen restores it,
and it now survives redeploys. The figures above are from that recorded run,
not a reconstruction.

## 2. Vision: the modality CITINEL could not ingest

A SOC runs on logs. An analyst is handed **pictures** all day — a forwarded
phishing email, a ransom note, an alert from a tool nobody integrated. Until
now every one had to be retyped by hand or lost. This is the only place in
CITINEL where a model looks at something that is not text.

**Tested end-to-end against the live API.** A phishing screenshot came back as
`kind: phishing email`, `looks_malicious: true` — and then the important part:

```
CORROBORATED BY THE RECORD ITSELF (no model involved):
  ip    192.168.250.100        43 findings   e.g. #[0, 1, 9]
  host  we8105desk          1,325 findings   e.g. #[0, 1, 1142]
NAMED BUT NEVER SEEN IN THIS RECORD:
  domain  wayne-corp-secure.com
```

**Two independent Gemini capabilities converged on the same host.** `we8105desk`
is what the long-context sweep flagged as living only outside the evidence
window, and what the vision reading independently corroborated. Neither knew
about the other.

**On the two counts — 1,348 and 1,325 — being different.** They are, and the
difference is the point rather than an embarrassment. 1,348 is *Gemini's own*
count, produced by a model reading digests: a claim. 1,325 is CITINEL's
deterministic count, produced by string matching over the findings in code
with citable indices: a fact. A model counting 2,487 things approximately is
exactly what one would expect, which is precisely why the corroboration step
exists and why nothing a model says here is allowed to be evidence. Trust the
1,325; the 1,348 is what prompted a human to go and look.

## 3. The design decision that makes vision usable

A model describing a picture is **not a detection**. A screenshot has no
provenance, no timestamp CITINEL can vouch for, and nothing stops anyone
pasting an image of anything at all. So the reading is recorded as an
**observation** and can never support a claim.

What earns its place is the step after. Every indicator Gemini names is checked
against the incident's own findings **deterministically, in code, with no model
involved** — producing two facts rather than a reading:

- **corroborated** — the picture names something the record contains, with
  citable finding indices a human can open
- **unseen** — the record has never contained it, which is often the more
  actionable answer, because it is how a screenshot tells a SOC about a sender
  or asset its own telemetry never covered

`wayne-corp-secure.com` being *unseen* is the useful half: that phishing domain
is genuinely new to the record.

## 4. The bug this caught, and why it is worth telling

The first corroborator searched a finding field called `raw`. The log line
actually lives in `evidence_raw` — so an IP present in **43 findings** was
reported as *"never seen in this record."*

That is not a blank space. It is a false statement about the record, which is
precisely what this system exists not to make. The haystack now serialises the
whole finding instead of hand-listed field names, and there is a test named
after the bug.

## 5. It fails honestly

| Situation | Behaviour |
|---|---|
| no key | `not_configured` — never a fabricated sweep or reading |
| model returns prose | `error` — never a guessed shape |
| incident fully examined | `not_needed`, and **zero API calls** — no spend |
| unsupported image type | refused before the call — nothing sent, nothing spent |
| scalar where a list was asked for | degrades; the same defect class found in Lyzr |

**19 tests** across `test_gemini_sweep.py` (11) and `test_gemini_vision.py` (8).

## 6. Security details worth a judge's attention

- **The API key travels in an `x-goog-api-key` header, never `?key=`** — a key
  in a URL leaks into logs, proxies and referrers. There is a test asserting
  the key never appears in the request URL.
- `generativelanguage.googleapis.com` is on the deterministic egress
  allow-list; the connector cannot reach anywhere else.
- Every prompt states that image and log text is **data, not instruction** —
  an image containing words telling the model to ignore its instructions is
  reported as a finding, never obeyed.
- Both results carry a `not_evidence` field **in the payload**, not just in the
  docs, so a reader sees the constraint in the data itself.

## 7. Model choice

`gemini-3.1-flash-lite`, configurable via `CITINEL_GEMINI_MODEL`. The free tier
is Flash-only since Pro moved behind billing in May 2026, and flash-lite
carries the highest free rate limits — which is what a single 2,487-finding
call actually needs.

## 8. Where to look

| Claim | Check |
|---|---|
| the run happened | `GET /api/incidents/INC-0417/audit` — actor `gemini-sweep`, `seq=5778` |
| the sweep artifact | `GET /api/incidents/INC-0417/sweep` — 404 until re-run once (see §1) |
| the connector | `backend/citinel/connectors/gemini.py` |
| corroboration logic | `backend/citinel/agents/visual.py` |
| tests | `test_gemini_sweep.py`, `test_gemini_vision.py` (19) |
| the panel | Replay → "WIDE-LENS SWEEP · GEMINI" |

## 9. Honest limits

- The sweep sends compact one-line digests, not raw log text — enough to
  cluster and count, deliberately less than the evidence blocks the swarm gets.
- `MAX_SWEEP_FINDINGS = 4000`. A larger incident is truncated, and the payload
  says so via `truncated_sweep`.
- A sweep and a reading are **context, never evidence**. Neither moves a
  verdict, reopens a lane, or changes a gate decision.
- **No criteria for this track have been published to us.** This is an evidence
  index, not a claim of qualification against a rubric we have not seen.
