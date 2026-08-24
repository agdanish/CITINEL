# CITINEL — Partner & API Onboarding Checklist

*Prepared 25 Aug 2026 from a live-research pass (11 agents, all high-confidence,
verified against each partner's own pages and the Decode SIH 2026 event page).
Team AeroFyta, Decode SIH 2026. This is an operational checklist, not spec —
work through it in priority order. Credentials go into `.env` (gitignored),
never into source or chat.*

---

## Read this first — the reality that reframes "let's claim the credits"

**Today is 25 Aug 2026. Every gating date on the event has already passed:**
registration close and idea submission (**13 Aug** on the live page / 11 Aug in
our internal docs), and the shortlist announcement (**~16 Aug**, Top 80 on the
live page / Top 60 internally — the discrepancy in SDD §22 Q14 is still open).

What that means, precisely:

1. **The build-critical *sponsor prize* credits cannot be freshly "claimed" by
   signing up now.** On the live event page, Render's $50, Tavily's 8,000
   credits, n8n's 1-month Cloud Pro, and Codemate's 15-day Pro are each worded
   **"every *shortlisted* team"** — not "every participant." They are
   distributed to shortlisted teams via **private redemption links** (email /
   WhatsApp / Discord), not a public signup. So whether we can get them depends
   entirely on whether **AeroFyta made the shortlist** — which nothing in this
   repo records (SDD §22 Open Question 1, unresolved).

2. **But the build is NOT blocked on the shortlist.** Every partner CITINEL
   integrates has a **standing free tier large enough to develop and demo
   against**, independent of any prize. Tavily gives 1,000 credits/month free
   forever; n8n self-hosted is free and unlimited; Render's free tier needs no
   card; Lyzr grants $20/month to registered participants; VirusTotal and
   AbuseIPDB are free. We can build the whole pipeline and the whole demo on
   free tiers. The prize credits are a *bonus on top*, not a prerequisite.

3. **The one genuine build-blocker is not a sponsor at all — it's Anthropic.**
   Pay-as-you-go, needs a card and prepaid credits, no confirmed free tier. It
   is what Step 7 (the swarm) cannot run without.

**→ The single most important thing only Danish can resolve:** did Team AeroFyta
make the Top 80/60 shortlist? Check the team inbox, the OSCode WhatsApp group,
and Discord for a shortlist notice and any sponsor redemption links. This gates
the prize credits **and** whether there is a 5 Sep Grand Finale to build toward
at all. Everything below is ordered so the build proceeds regardless of the
answer.

---

## Priority-ordered actions

### P0 — Build-critical, do now (unblocks the pipeline)

| # | What | Who does it | Gate | env var |
|---|------|-------------|------|---------|
| 1 | **Anthropic API key** — add card, buy prepaid credits, create key | Danish | open, needs card | `CITINEL_ANTHROPIC_API_KEY` |
| 2 | **Tavily** free "Researcher" (1,000 cr/mo, no card) | any member | open now | `CITINEL_TAVILY_API_KEY` |
| 3 | **VirusTotal** free public API | any member | open now | `CITINEL_VIRUSTOTAL_API_KEY` |
| 4 | **AbuseIPDB** free Individual tier | any member | open now | `CITINEL_ABUSEIPDB_API_KEY` |

After P0, Step 7 (the swarm) and its Enrichment Squad can run live.

### P1 — Sponsor free tiers, claimable now (build + track eligibility)

| # | What | Gate | env var |
|---|------|------|---------|
| 5 | **n8n** self-hosted Community (free, unlimited) — for the Beat 5b flow | open now | `CITINEL_N8N_WEBHOOK_URL` |
| 6 | **Lyzr** — $20/mo auto-reset for registered participants *(still unconfirmed as a CITINEL stack addition — SDD Q15)* | participants | `CITINEL_LYZR_API_KEY` |
| 7 | **Swytchcode** — $100 via the Decode SIH **referral link** (get it from event channels) | participants | `CITINEL_SWYTCHCODE_API_KEY` |
| 8 | **Render** free tier (750 hrs/mo, no card) — for Step 12 deploy | open now | *(deploy config)* |
| 9 | **Startuped** participant grant — for GTM artifacts (not code) | participants | *(none)* |
| 10 | **Codemate** 14-day Pro trial — build-time only, not runtime | open now | *(none)* |

### P2 — Shortlist-gated prize credits (only if AeroFyta is shortlisted)

Redemption links are sent privately to shortlisted teams — check the inbox /
group chat. Do **not** block the build on these.

- Render **$50** · Tavily **8,000 credits** · n8n **1-month Cloud Pro** · Codemate **15-day Pro** (per member)

### P3 — Finale-only prizes (judged 5 Sep on the built product)

- "Best Use of X" awards: Render $600/500/400 · Swytchcode $1,000 · Tavily 10k/5k/3k · n8n 1-yr Pro · Lyzr ₹20,000 · Startuped ₹25,000 bundle · Codemate 3-mo Pro + PPI.

---

## Per-partner detail

### 1. Anthropic API (core — the real blocker)
- **URL:** https://platform.claude.com/settings/keys *(console.anthropic.com redirects here)*
- **Offer:** pay-as-you-go, **no confirmed free tier**. Prepaid credits, per-token pricing, expire 1 year, non-refundable. The commonly-cited ~$5 new-account credit is **unverified** (not in official docs).
- **Steps:** sign up + SMS verify → Billing: add card, buy credits (enable Auto-reload so the swarm doesn't stall) → API Keys: Create Key, copy once → `CITINEL_ANTHROPIC_API_KEY=…`.
- **Model IDs (live-checked 25 Aug 2026, satisfies ledger rule L9):** current GA family is `claude-fable-5`, `claude-opus-5` (docs-recommended default), `claude-sonnet-5`, `claude-haiku-4-5`. **Every ID is a pinned snapshot**, so L9 validation checks the literal configured string against `GET /v1/models` at runtime. Budget tip: `claude-haiku-4-5` or `claude-sonnet-5` for high-volume swarm agents, `claude-opus-5` for reasoning-heavy steps.
- **Smoke test:** `curl https://api.anthropic.com/v1/messages -H "x-api-key: $CITINEL_ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" -H "content-type: application/json" -d '{"model":"claude-sonnet-5","max_tokens":16,"messages":[{"role":"user","content":"ping"}]}'`

### 2. Tavily (sponsor — free tier powers the build)
- **URL:** https://app.tavily.com/home
- **Free tier:** "Researcher" plan, **1,000 credits/month, forever, no card**. Dev key 100 req/min, Prod key 1,000 req/min.
- **Steps:** sign up (Google/GitHub/email) → dashboard shows 1,000 credits → copy key (`tvly-…`) → `CITINEL_TAVILY_API_KEY=tvly-…`. Powers Step 7 Enrichment Squad.
- **Prize (separate, shortlist-gated):** 8,000 credits to shortlisted teams; 10k/5k/3k to track winners.

### 3. VirusTotal (enrichment — free, not a sponsor)
- **URL:** https://www.virustotal.com/gui/join-us
- **Caps (live-verified):** **4 req/min, 500/day**. These are exactly why CITINEL is cache-first + hash-dedup — the cap can never fire mid-demo.
- **Steps:** register → avatar menu → API key → `CITINEL_VIRUSTOTAL_API_KEY=…`. Header: `x-apikey`.

### 4. AbuseIPDB (enrichment — free, not a sponsor)
- **URL:** https://www.abuseipdb.com/register
- **Free tier:** 1,000 IP checks/day, no card, no expiry.
- **Steps:** register → https://www.abuseipdb.com/account/api → Create Key → `CITINEL_ABUSEIPDB_API_KEY=…`. Header: `Key`.

### 5. n8n (sponsor — self-hosted is free)
- **Build path (free, no gate):** self-hosted Community Edition via Docker — `docker volume create n8n_data` then run the `n8nio/n8n` container on :5678. Unlimited workflows/executions.
- **Beat 5b flow:** Webhook "Incident Signed" → Format Notification → Send Slack/Email → Export Signed PDF → Create Follow-up Ticket. Put the webhook production URL in `CITINEL_N8N_WEBHOOK_URL`.
- **Prize (shortlist-gated):** 1-month Cloud Pro. Managed trial (optional): https://app.n8n.cloud/register (14-day, no card).

### 6. Lyzr AI (sponsor — $20/mo for participants; **stack addition still unconfirmed, SDD Q15**)
- **URL:** https://studio.lyzr.ai/
- **Grant:** $20/mo auto-resetting for registered participants; standalone free tier 500 credits/mo. Provider-agnostic — set the agent model to Claude so it complements the swarm, not replaces it.
- **Steps:** sign up → org dropdown → Account & API Key → `CITINEL_LYZR_API_KEY=…`.
- **Decide first:** whether Lyzr enters the CITINEL stack at all (governance/observability layer over the 7 agents). Don't wire it until that's confirmed.

### 7. Swytchcode (sponsor — $100 needs the referral link)
- **URL:** https://app.swytchcode.com — **but the $100 requires the official Decode SIH referral link** distributed in event channels (WhatsApp/Discord). Get that link first.
- **To win the track:** must **scaffold with the Swytchcode CLI** (`swy`), not just call an API at runtime; Python or TS runtime SDK; ≥2 ecosystem APIs; AI agent; end-to-end app. Powers Response Marshal/Scribe agent→API execution.
- **Steps:** register participant → get referral link → create account via it → confirm $100 → install CLI (`curl -fsSL https://cli.swytchcode.com/install.sh | sh`) → `swy login` → add runtime SDK.

### 8. Render (sponsor — free tier builds; $50 is shortlist-gated)
- **URL:** https://dashboard.render.com/register — free tier, **no card**.
- **Build/deploy (Step 12):** Web Service + Background Worker + managed PostgreSQL + Key Value (Redis) = >1 service (satisfies "Best Use of Render"). Point the **QR-code URL** at the Render web service. **Note:** free web services spin down after 15 min (~30–60s cold start) — pre-warm before judging, or the QR demo stalls.
- **Prize:** $50 shortlist-gated; $600/500/400 at finale.

### 9. Startuped.ai (sponsor — GTM artifacts, not code)
- **URL:** https://www.startuped.ai/forms/decode-sih-2026 — participant grant delivered by email after registration ("join link with step-by-step instructions"). Fallback contact: komal@startuped.ai.
- **Use:** run CITINEL's *locked* positioning (A1-F45 persona, STATE §1.4 line, A1-F47/F42 channel) through the platform; export outputs into deck slides 8 & 13. No env var.

### 10. Codemate.ai (sponsor — build-time, not runtime)
- **URL:** https://app.codemate.ai — 14-day Pro trial for anyone now.
- **Prize:** 15-day Pro per shortlisted member; 3-month Pro + PPI for flagship-track winners. No CITINEL runtime dependency, no env var.

---

## `.env` mapping (fill as you go; file is gitignored)

```
CITINEL_ANTHROPIC_API_KEY=      # P0 #1 — the blocker
CITINEL_TRIAGE_MODEL=           # propose: claude-haiku-4-5   (L9: verify live)
CITINEL_REASONING_MODEL=        # propose: claude-opus-5      (L9: verify live)
CITINEL_TAVILY_API_KEY=         # P0 #2 — tvly-…
CITINEL_VIRUSTOTAL_API_KEY=     # P0 #3
CITINEL_ABUSEIPDB_API_KEY=      # P0 #4
CITINEL_N8N_WEBHOOK_URL=        # P1 #5 — self-hosted webhook URL
CITINEL_LYZR_API_KEY=           # P1 #6 — only if Lyzr is confirmed in-stack
CITINEL_SWYTCHCODE_API_KEY=     # P1 #7 — after referral-link signup
```

Render, Startuped and Codemate carry no runtime key (deploy config / GTM tool /
build-time tool respectively).

---

## Open items only Danish can close

1. **Did AeroFyta make the shortlist?** (Top 80/60 — SDD §22 Q1.) Gates all P2/P3 credits and the finale itself. Check inbox / WhatsApp / Discord.
2. **Get the Swytchcode referral link** from event channels (needed for the $100).
3. **Confirm Lyzr is in the CITINEL stack** before wiring it (SDD §22 Q15).
4. **Register for Startuped** to trigger the participant GTM grant email.
5. The 13 Aug/Top 80 vs 11 Aug/Top 60 discrepancy (SDD §22 Q14) — the live page
   says 13 Aug / Top 80; still not reconciled with internal docs.
