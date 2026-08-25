# CITINEL — Startuped.ai GTM Playbook (Best GTM / Launch Strategy)

*Prepared 25 Aug 2026. Everything below is the curated, finding-ID-traceable
GTM thesis for CITINEL, packaged so you can run it THROUGH the Startuped.ai
platform (that tool usage is what the "Best GTM / Launch Strategy" award judges).
Single overall winner across the whole event — so this has to be rigorous, not
generic. Honest by construction: numbers are ranges with scope declared (ledger
L6), the market sizing is left for Startuped's own market-research module to
quantify (that is literally the tool's job and the thing you must demonstrate),
and nothing here fabricates a metric.*

---

## How to use this file

1. **Part A** is the curated input — paste each block into the matching
   Startuped module. Do not invent new GTM thinking; CITINEL's positioning is
   already locked and adversarially verified. Run the *locked* thesis through
   the tool.
2. **Part B** is the click-by-click path on the website.
3. **Part C** is what to reflect back into the app + deck slide 13, so
   "Slide 13 is built from Startuped" becomes literally true.
4. **The award criterion is demonstrated USE.** You running these modules and
   exporting the outputs IS the proof-of-use artifact. This file makes the
   input world-class; the tool usage has to be yours.

---

## Part A — Curated GTM inputs (paste into Startuped modules)

### A1. Idea validation

> **Product:** CITINEL — an autonomous, glass-box AI Cyber SOC for India's
> cooperative banks and small NBFCs. It investigates every alert with cited
> evidence, acts only inside a readable per-action policy, and drafts the
> CERT-In 6-hour report and DPDP breach artifacts for human sign-off.
>
> **The validated problem:** cooperative banks and small NBFCs carry the *same*
> RBI 24×7 SOC mandate and CERT-In 6-hour reporting obligation as national
> banks, on a fraction of the budget. One 2024 ransomware attack (C-Edge /
> RansomEXX) took ~300 cooperative banks offline in a single incident [A1-F26].
> A compliant human SOC needs 8–12 analysts at $1M+/yr [A1-F29] against a
> ₹25k–₹1L/month buyer budget [A1-F33]. India is short ~790,000 cyber
> professionals (ISC2 2023) [WIN-F31].
>
> **The unmet gap (the wedge):** SIEMs know what happened but don't write the
> regulator's form; compliance tools write forms but don't know what happened.
> CITINEL is the only system where the investigation itself writes the draft —
> detection to regulator-ready report, one pipeline [COMP-F20, A2 §5(a)]. No
> named AI-SOC competitor drafts CERT-In or DPDP [verified, SDD §13 item 6].
>
> **Why now:** CERT-In's 6-hour rule has been law since 2022; DPDP's stackable
> ₹250cr + ₹200cr penalties land fully ~May 2027 (a *closing runway*, never
> current enforcement); the govt-funded PACS computerization program is
> connecting 63,000 cooperative societies to digital rails right now
> (₹2,516 cr, 50,455 already onboarded by Jan 2025) — newly exposing exactly
> this segment [SDD §17 finding 3].

### A2. Market research (let Startuped quantify — do NOT hardcode a TAM here)

> **Segment structure to size in the market-research module** (fill the numbers
> using Startuped's own research; report as ranges with scope declared):
> - **Core segment:** urban + rural cooperative banks and small NBFCs in India
>   subject to RBI cyber directions but below enterprise-SOC budget.
> - **Distribution multiplier (why the reachable market is larger than the
>   buyer count):** the B2B2X channel — MSSPs and SEBI-mandated Market-SOC
>   operators (NSE/BSE) — one integration reaches hundreds of banks
>   [A1-F42, A1-F47].
> - **Adjacent expansion (roadmap, don't over-claim):** SEBI-regulated small
>   entities, hospitals [A1-F45]; then AIOps/fraud skins on the same engine.
>
> **Ask Startuped to produce:** a defensible TAM/SAM/SOM with sources, and a
> competitive map. Seed the competitive map with: no named agentic-SOC
> competitor mentions CERT-In/DPDP/RBI/SEBI [SDD §13 item 6]; the closest
> incumbent (Dropzone) has pulled all pricing behind a sales wall and last
> disclosed ~$36k/yr — an order of magnitude above the Indian buyer band
> [SDD §13 items 10–12].

### A3. Product positioning

> **One-line position:** "The SOC that shows its evidence, obeys your policy,
> and beats the clock."
> **Category:** Autonomous Cyber SOC (agentic-SOC) — India-compliance-native.
> **For:** the IT head / CISO-equivalent of a cooperative bank or small NBFC —
> "one officer, a round-the-clock duty, alone" (persona ranked 19/20, A1-F45).
> **Unlike** global AI-SOC copilots (built for a different buyer and regulator,
> priced out of the segment) **and** India GRC tools (make humans type incident
> facts into forms), **CITINEL** is the only system where the investigation
> itself writes the regulator-ready draft [STATE §1.4, verbatim].
> **Proof, not promise:** every verdict cites the exact log line; response runs
> inside a readable OPA policy with a per-action autonomy dial; a poisoned log
> cannot hijack the AI; we draft, we never file.

### A4. GTM planning / channel

> **Motion: channel-first B2B2X, never direct-SMB** [A1-F47].
> - **Primary channel:** MSSPs and SEBI-mandated Market-SOC operators
>   white-label the engine — "they keep the customer, we keep the engine."
>   Per-device pricing in the proven ₹250–1,000/device/month band [A1-F34].
> - **Regulator-manufactured demand:** SEBI's CSCRF directs NSE/BSE to run
>   Market-SOCs onboarding small self-certification REs — a channel a regulator
>   already built [A1-F42, SDD §13 item 13].
> - **Non-dilutive runway to fund it:** Cyber Surakshit Bharat (1,637+ CISOs
>   trained — the adoption channel) [A1-F56]; C3iHub IIT Kanpur (₹30L cohort)
>   [A1-F55]; I4C (national coordination) [A1-F57].
> - **Anti-lock-in as a sales argument:** every generated Sigma rule + playbook
>   exports as an open, portable artifact — "take your detections and go."

### A5. Launch strategy

> **Sequencing (stage the wedge, don't boil the ocean):**
> 1. **Beachhead:** land 1–3 MSSP/Market-SOC partners; prove the compliance-
>    clock module (CERT-In 6-hour auto-draft) on their real incident flow.
> 2. **Expand:** add DPDP two-stage artifacts + the portable-Sigma flywheel;
>    publish the measured false-positive rate on a labeled set (never claimed).
> 3. **Scale story:** regulator-connector packs (RBI/SEBI/IRDAI/CEA/NCIIPC)
>    re-skinning one normalized incident record; then domain-agnostic engine
>    reuse (AIOps, fraud).
> **Honest framing rules that must survive into the launch narrative:** DPDP is
> a closing runway, never current enforcement; we draft, we never file;
> "CERT-In empanelled" is a services authorization for audit firms, never a
> product credential CITINEL claims [SDD §20].

---

## Part B — Baby steps on the Startuped.ai website

1. **Register the team for the event grant.** Go to
   `https://www.startuped.ai/forms/decode-sih-2026` and submit. The page states
   it emails "a join link with step-by-step instructions" — watch the inbox.
   If the grant does not apply, email the event host (komal@startuped.ai) to
   redeem the participant credits. *(Do not rely on a generic /pricing signup —
   use the event form so the grant attaches.)*
2. **Log in** with the join link; confirm the free access + credits show.
3. **Run the modules in this order, pasting the matching Part A block:**
   - **Idea validation** ← Part A1
   - **Market research** ← Part A2 (let the tool produce TAM/SAM/SOM + the
     competitive map; this is the module the criterion most wants to see used)
   - **Product positioning** ← Part A3
   - **GTM planning** ← Part A4
   - **Launch strategy** ← Part A5
4. **Export or screenshot each module's output.** These exports are the literal
   proof-of-use artifact the award requires. Save them to the repo under
   `docs/startuped-exports/` (create the folder) so they are versioned.
5. **Keep the dashboard ready to show live** at the Grand Finale — being able
   to open the platform and walk a judge through the run is stronger than a
   static screenshot.

---

## Part C — Reflect back into the product + deck

- **Deck slide 13 (Business Model Canvas):** rebuild it from the Startuped
  outputs so "Slide 13 is built from Startuped" is literally true, not
  approximately. Map: Customer Segments (A1/A2 personas) · Value Propositions
  (A3) · Channels (A4 B2B2X) · Revenue Streams (₹250–1,000/device band) · Key
  Partners (MSSPs, Market-SOCs, C3iHub) · Cost Structure (~5¢/incident
  instrumented, label [INFERENCE]).
- **In the app:** surface a one-screen "Business case" panel in the dashboard
  (Step 11) that states the buyer, the budget wedge, and the channel — so the
  GTM story is visible in the product a judge clicks through, not only on a
  slide.
- **Traceability:** every number that appears in a Startuped export and then in
  the deck must keep its finding ID / source, per the corpus's own discipline.

---

## Honesty guardrails (do not break these for a prize)

- **Market size only as ranges, scope declared** (ledger L6). If Startuped
  emits a single big TAM number, present it with its assumptions, not as fact.
- **No fabricated traction.** CITINEL has no customers yet; the GTM is a plan,
  not a track record. Say "planned / target," never imply signed partners.
- **The ~5¢/incident economics is your own instrumented figure** — label it
  [INFERENCE], and instrument it for real during the build (STATE §5 item 2).
- **Pricing anchors (₹250–1,000/device, ₹25k–1L/month budget)** are
  Med-confidence, single-source [A1-F33/F34]; one real MSSP quote upgrades them.
- **The award is judged on demonstrated USE of the tool** — the rigor of this
  input plus your actual module runs, not on claiming a guaranteed win.
