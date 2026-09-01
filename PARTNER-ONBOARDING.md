# CITINEL — Partner & API Onboarding Checklist

*Prepared 25 Aug 2026, rewritten 31 Aug 2026 with real, official redemption
steps (organizer PDFs forwarded by Danish, not inferred from public pages).
Team AeroFyta, Decode SIH 2026, **confirmed finalist**. This is an operational
checklist, not spec — work through it in priority order. Credentials and
voucher codes go into `.env` (gitignored) once redeemed; the codes below are
single-use-per-team or per-member and came from the organizer directly —
don't post this file's contents outside the team.*

---

## Read this first — what changed 31 Aug 2026

**The shortlist question is closed.** AeroFyta is a confirmed finalist (the
team is in a WhatsApp group literally named "Finalist Decode SIH 2026," with
finale logistics already being discussed). Every "P2 — only if shortlisted"
item below is now simply P1 — claimable now, not conditional.

**Six of eight partners now have official, organizer-issued redemption
steps** (not the public event page's general wording) — Render, Tavily,
Swytchcode, Startuped, n8n, Codemate. Lyzr's participant grant and Gemini
have no equivalent document; treat those as lower-confidence until something
more specific turns up.

**One real deadline, easy to miss:** the Render credits portal
(`credits-portal-mmdm.onrender.com`) **auto-closes 2 Sep 2026** — that's 3
days before the 5 Sep finale. Do this one first, this week, not "eventually."

**The one genuine build-blocker is still Anthropic**, not any sponsor. It's
pay-as-you-go, needs a card, no confirmed free tier — and Step 7 (the swarm)
cannot run without it. Nothing below changes that; it stays P0 #1.

**None of these can be redeemed by Claude.** Every step here needs a human to
create an account, verify an email, or enter payment info — actions Claude
is not able to do on anyone's behalf. Claude's part is: keep this checklist
accurate, and wire whatever key/URL results into the actual connector code
the moment it exists in `.env`.

---

## Priority-ordered actions

### P0 — Build-critical, do first (unblocks Step 7)

| # | What | Who | Gate | env var |
|---|------|-----|------|---------|
| 1 | **Anthropic API key** — add card, buy prepaid credits, create key | Danish | needs a card | `CITINEL_ANTHROPIC_API_KEY` |
| 2 | **VirusTotal** free public API | any member | open now | `CITINEL_VIRUSTOTAL_API_KEY` |
| 3 | **AbuseIPDB** free Individual tier | any member | open now | `CITINEL_ABUSEIPDB_API_KEY` |

### P1 — Time-sensitive, real credits, do this week

| # | What | Who | Deadline | env var |
|---|------|-----|----------|---------|
| 4 | **Render** — sign up via UTM link, generate code at the credits portal, paste into Billing → Credit Balance. $50, no card. | **every member** | **portal closes 2 Sep 2026** | *(deploy config, no key)* |
| 5 | **Tavily** — sign up, Billing tab → "Project" plan → code `Decode26` → 8,000 credits, free 2 months | **every member** | not stated, don't delay | `CITINEL_TAVILY_API_KEY` |
| 6 | **n8n** — redeem the Cloud Pro voucher (below) at n8n's voucher-redemption page | **team leader only, once** | voucher expires 1 week after the event | `CITINEL_N8N_WEBHOOK_URL` |
| 7 | **Codemate** — QR scan → sign up with team-leader email → verify → log in at codemate.ai | **team leader only, once** | not stated | *(build-time, no key)* |
| 8 | **Swytchcode** — register via the Decode SIH Google Form → $100 credits | **every member** | not stated | `CITINEL_SWYTCHCODE_API_KEY` |
| 9 | **Startuped** — sign up via the event URL → they email access | **every member** | not stated | *(none, GTM tool)* |

### P2 — Lower confidence, no official doc yet

| # | What | Status |
|---|------|--------|
| 10 | **Lyzr** — $20/mo grant for registered participants | Carried from the 25 Aug pass; no organizer redemption doc has surfaced alongside the other 6. Confirm before relying on it. |
| 11 | **Gemini** | Real, organizer-tracked category (confirmed by a finalist-group poll — 29 other-team votes), but no redemption/credential document exists. Most likely just a standard Google AI Studio key obtained independently, not a hackathon-specific voucher. |

### P3 — Finale-only prizes (judged 5 Sep on the built product)

"Best Use of X": Render $600/500/400 · Swytchcode $1,000 · Tavily 10k/5k/3k ·
n8n 1-yr Pro · Lyzr ₹20,000 · Startuped ₹25,000 bundle · Codemate 3-mo Pro +
PPI · plus whatever Gemini/CodeMate's own tracks judge on. Eligibility is
necessary, not sufficient — none of this is a guaranteed win regardless of
how completely the checklist above gets worked through.

---

## Per-partner detail

### 1. Anthropic API (core — the real blocker)
- **URL:** https://platform.claude.com/settings/keys
- **Offer:** pay-as-you-go, no confirmed free tier. Prepaid credits, expire 1 year, non-refundable.
- **Steps:** sign up + SMS verify → Billing: add card, buy credits (Auto-reload on) → API Keys: Create Key → `CITINEL_ANTHROPIC_API_KEY=…`.
- **Model IDs (L9-verified 25 Aug 2026):** `claude-fable-5`, `claude-opus-5` (default), `claude-sonnet-5`, `claude-haiku-4-5`. Every ID is a pinned snapshot, checked live against `GET /v1/models` at runtime — don't trust this list by the time you read it, `models.py` does the real check.
- **Smoke test:** `curl https://api.anthropic.com/v1/messages -H "x-api-key: $CITINEL_ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" -H "content-type: application/json" -d '{"model":"claude-sonnet-5","max_tokens":16,"messages":[{"role":"user","content":"ping"}]}'`

### 2. VirusTotal (enrichment — free, not a sponsor)
- **URL:** https://www.virustotal.com/gui/join-us
- **Caps:** 4 req/min, 500/day — exactly why CITINEL is cache-first + hash-dedup.
- **Steps:** register → avatar menu → API key → `CITINEL_VIRUSTOTAL_API_KEY=…`. Header: `x-apikey`.

### 3. AbuseIPDB (enrichment — free, not a sponsor)
- **URL:** https://www.abuseipdb.com/register
- **Free tier:** 1,000 IP checks/day, no card.
- **Steps:** register → https://www.abuseipdb.com/account/api → Create Key → `CITINEL_ABUSEIPDB_API_KEY=…`. Header: `Key`.

### 4. Render — **do this one first, real deadline**
- **Step 1 — sign up:** https://dashboard.render.com/register?utm_source=events&utm_medium=events&utm_campaign=2026_event_decode_sih_2026
- **Step 2 — generate your code:** https://credits-portal-mmdm.onrender.com/claim/decode-sih-2026 (generate once per person)
- **Step 3 — redeem:** workspace → Billing → Credit Balance → paste the code. No card required. $50, expires 12 months after redemption per the organizer's own screenshot.
- **Deadline: portal auto-closes 2 Sep 2026.** Every team member should do this individually before then.
- **Build use (Step 12):** Web Service + Background Worker + managed Postgres + Key Value = >1 service, satisfies "Best Use of Render." Point the deck's QR code at the live web service. Free services cold-start after 15 min idle — pre-warm before judging.

### 5. Tavily — the real prize code, separate from the standing free tier
- **URL:** tavily.com
- **Standing free tier (no code needed):** 1,000 credits/month forever, no card.
- **Decode SIH promo (better — do this instead of just the free tier):** sign up → Billing tab → click the "Project" monthly plan → enter code **`Decode26`** → 8,000 credits, free for 2 months → redeem the API key from the dashboard → `CITINEL_TAVILY_API_KEY=tvly-…`.
- Powers Step 7's Enrichment Squad.

### 6. n8n — one redemption per team, leader only
- **Voucher code:** `2026-COMMUNITY-HACKATHON-INDIA-BAE35BA1`
- **Redeem at:** https://n8n.notion.site/voucher-code
- **Only one team member (the leader) should do this.** Grants one month of Cloud Pro, expires **one week after the event**.
- **Requires a credit card.** If the team would rather not enter one, a 14-day free trial (starter, not Pro) is available with just a login — a real tradeoff, not a bug: full Pro needs a card, the card-free path is the lesser tier.
- **Beat 5b flow:** Webhook "Incident Signed" → Format Notification → Send Slack/Email → Export Signed PDF → Create Follow-up Ticket. Webhook URL → `CITINEL_N8N_WEBHOOK_URL`.

### 7. Codemate — one redemption per team, leader only
- **Steps:** scan the organizer's QR code (Google Lens) → sign up with the **team leader's email**, set a password → verify the email (fill Organisation = college name, Organisation size = first option, Designation = student/developer) → check verification status → go to https://codemate.ai/ → "Get Started" → log in with the same email/password.
- Build-time tool (used to write code, not called at runtime) — no `.env` key.

### 8. Swytchcode
- **URL:** https://forms.gle/vdNBiUvfKfz3H9zD8 (Google Form, not a referral link as previously assumed — this is the actual, correct mechanism)
- **Offer:** $100 credits per team member, valid for the hackathon.
- **Confirmed live in the 26 Aug partner Q&A (not just the form's promise):** if the team form was already filled, credits are already allocated and usable through the 5 Sep finale — worth checking the account directly rather than assuming a separate claim step is still pending. Full notes: `PARTNER-SESSION-NOTES.md`.
- **To win the track specifically:** scaffold with the Swytchcode CLI (`swy`), not just call the API at runtime; ≥2 ecosystem APIs; AI agent; end-to-end app. Powers Response Marshal/Scribe agent→API execution. The live demo's exact shape — policy guardrail blocking one specific action, zero code changes needed — maps directly onto the already-written but unwired `connectors/swytchcode.py: SwytchcodeExecutor`; wiring that in is the concrete path to the track, not a new integration.
- Install: `curl -fsSL https://cli.swytchcode.com/install.sh | sh` → `swy login` → `CITINEL_SWYTCHCODE_API_KEY=…`.

### 9. Startuped.ai
- **URL:** https://www.startuped.ai/events/decode-sih-2026 — sign up, they email required access.
- **Use:** run CITINEL's locked positioning (persona, differentiation line, channel strategy) through the platform; export into deck material. No `.env` key. *(Deck work is currently deprioritized — do the signup now if convenient, the actual platform run can wait.)*

### 10. Lyzr AI — code complete, offer confirmed live (still no organizer PDF)
- **URL:** https://studio.lyzr.ai/
- $20/mo for registered participants, **confirmed twice in the 25 Aug partner session by a Lyzr engineer live-demoing it** — "every month it resets to $20," and it resets again right around finale week, so the team gets a fresh $20 for the finale regardless of what's spent before. Still no organizer redemption PDF the way the other 6 partners have, but this is stronger evidence than the original research-pass guess.
- **The Studio agent `CITINEL_LYZR_AGENT_ID` needs (answering `pii_guard` + `ledger_head`) now has a concrete recipe**, not just "this is Studio config": the 25 Aug demo walks through building a multi-agent system with exactly this shape (define role/goal/instructions per agent, expose a capability as a custom tool via its OpenAPI schema when it's not in the built-in catalog). Full notes: `PARTNER-SESSION-NOTES.md`.
- **The exact copy-paste Role/Goal/Instructions, which Studio toggles to set, and a known open gap in the memory design are in `LYZR-AGENT-CONFIG.md`** — produced by a research + red-team pass (1 Sep) once it became clear `pii_guard`'s "input" is untrusted attacker telemetry, not trusted text, and needed hardening against prompt injection specifically.
- **Integration status: all four SDD §15.3 attachment points now resolved**, and every one degrades to a no-op without a key, so nothing here blocks on the credential:

  | # | Attachment point | Status |
  |---|---|---|
  | 1 | Fleet observability | **Built + wired.** `LyzrObserver` receives start / tool_call / finish events from `SwarmPipeline`; `NullObserver` is the default. |
  | 2 | Hallucination & PII guard | **Built + wired.** `LyzrGuard` adds an independent second opinion on top of CITINEL's own deterministic screen, before compliance sign-off. |
  | 3 | RBAC | **Deliberately NOT Lyzr.** Implemented in CITINEL's own `policy/roles.py` instead — routing authorization to an external control plane would contradict "the policy gate is the sole authority," and would make a third-party outage a correctness problem for a bank's SOC. Reasoning is in that module's docstring. This is a considered decline, not a gap. |
  | 4 | Immutable audit log | **Built + wired.** `LyzrLedgerMirror` is an external *witness*: it mirrors every committed entry and `compare()` reconciles the local chain head against it. Closes a real, narrow gap — a self-contained hash chain cannot detect wholesale file replacement, because a rewritten chain verifies against itself. Surfaced on `/api/ledger/verify` as a separate `witness` field, never merged into the local `intact` boolean. |

- **What still needs the key:** all four run as no-ops until `CITINEL_LYZR_API_KEY` + `CITINEL_LYZR_GUARD_URL` + `CITINEL_LYZR_AGENT_ID` are set. The Lyzr-side agent must answer two tasks — `pii_guard` and `ledger_head` (returning `{head, count}`) — which is Studio configuration, not code.
- **Honest limit:** the request/response shapes for those two tasks are CITINEL's own contract, written against Lyzr's documented Agent API pattern but **never executed against the live service**. First real run must confirm them.

### 11. Gemini — real category, no redemption mechanism found
- No signup form, code, or credential doc has appeared alongside the other 6 official PDFs. Likely just requires an independently-obtained Google AI Studio API key rather than a hackathon-specific grant. Revisit if the organizers post something more specific.

---

## `.env` mapping (fill as you go; file is gitignored)

```
CITINEL_ANTHROPIC_API_KEY=      # P0 #1 — the blocker
CITINEL_TRIAGE_MODEL=           # propose: claude-haiku-4-5   (L9: verify live)
CITINEL_REASONING_MODEL=        # propose: claude-opus-5      (L9: verify live)
CITINEL_VIRUSTOTAL_API_KEY=     # P0 #2
CITINEL_ABUSEIPDB_API_KEY=      # P0 #3
CITINEL_TAVILY_API_KEY=         # P1 #5 — tvly-…, redeem via code Decode26
CITINEL_N8N_WEBHOOK_URL=        # P1 #6 — after voucher redemption, leader only
CITINEL_SWYTCHCODE_API_KEY=     # P1 #8 — after form signup
CITINEL_LYZR_API_KEY=           # P2 #10 — only if Lyzr is confirmed in-stack
```

Render, Codemate, and Startuped carry no runtime key.

---

## Open items only Danish can close

1. **Who is "team leader" for the n8n and Codemate one-per-team redemptions?** Both explicitly say only one member should do this — needs a named person before either gets redeemed, to avoid two people accidentally burning both attempts.
2. **Confirm Lyzr's offer is still live** — no official doc accompanied it this round.
3. ~~Whether Lyzr enters the CITINEL stack at all~~ (SDD §22 Q15) — **resolved in the affirmative and built**: all four §15.3 attachment points are code-complete (§10 above), three as Lyzr integrations and one as a reasoned decline. Every one is a no-op without the key, so the build carries no dependency on the credential arriving. What remains is purely operational: get the key, configure the Studio agent to answer `pii_guard` and `ledger_head`.
4. Gemini — watch for an organizer doc; nothing actionable yet beyond an independently-obtained API key.
