# Partner Session Notes — structured from 3 recordings, 1 Sep 2026

*Source: three Google Meet recordings Danish shared as pasted transcripts
(Swytchcode 26 Aug, Lyzr 25 Aug, Startuped 24 Aug). This file is the cleaned,
structured record — read this instead of re-transcribing the recordings
again. Raw recordings still live in Danish's Drive if verbatim quotes beyond
what's captured here are ever needed.*

---

## 1. Swytchcode — Integration & Credits Q&A (26 Aug 2026, presenter: Chetali, Dev Engineer)

### What Swytchcode actually is
An execution/reliability layer between an AI agent and real APIs — not a
tool-calling framework, a *safety* layer on top of one. Three problems it
targets, in the presenter's own framing:

1. **Parameter/endpoint hallucination** — models guess wrong field names or
   invent endpoints; Swytchcode gives the agent the real API definition
   instead of letting it guess.
2. **Silent correctness failures** — the running example: an agent sends the
   *same* email 35 times to the same person. Every individual call succeeds
   (valid params, valid auth, 200 response) — there is no error anywhere,
   yet the outcome is a disaster. This is presented as the core reason
   Swytchcode exists: **API success ≠ correct agent behavior.**
3. **No guardrails** — nothing stops the agent from doing something it
   technically *can* do but shouldn't.

### Three concrete mechanisms (asked about directly in Round 2, so likely a
judging rubric)
- **Policy guardrails** — declarative rules ("agent can read Gmail but not
  delete") enforced *before* an operation executes, not after.
- **Built-in authentication** — Swytchcode owns token storage/refresh; you
  connect the service once, don't manage keys yourself.
- **Idempotency** — repeat calls don't multiply side effects (the 35-email
  problem, solved).

### Scale claim
280+ providers, 75,000+ endpoints, Serper recently added (voice agents).

### Three ways to integrate, in the presenter's own recommended order for
newcomers
1. **MCP server** — explicitly recommended as easiest for a team new to
   Swytchcode ("I'll recommend to use MCP server. It will help you a lot").
2. **Runtime + SDK** — native integrations for OpenAI/Vercel/Anthropic SDKs
   and LangGraph; JS/TS/Python SDK support.
3. **CLI** (`swy`) — full manual control: `swy init`, `swy get <toolkit>`,
   `swy run connect <service>`, `swy policy add`. This is what the live demo
   used, and what **PARTNER-ONBOARDING.md already correctly identifies** as
   what's needed to win the track specifically ("scaffold with the CLI, not
   just call the API at runtime").

### Live demo (Gmail assistant, OpenAI SDK)
`swy init` → `swy get gmail` → `swy run connect gmail` (opens an OAuth
screen) → add a method (`Gmail.users.send.create`) → send a real email →
**then** `swy policy add` blocking that same recipient → re-run → the send
is blocked and the agent surfaces the exact policy message, with *zero*
code or prompt changes. This is the single clearest live proof-point in any
of the three sessions: policy enforcement demonstrably intercepts an agent
action outside the agent's own reasoning.

### Credits — the fact worth acting on
> *"if you have filled that form then we have already allocated credits to
> you guys uh for this month and uh till the grand finale... switch code
> credits are free for you for this month or like the 5th of September."*

Reads as: if the team form was already filled (per PARTNER-ONBOARDING.md
step 8), credits are already live and usable through the 5 Sep finale — not
a separate claim step still pending. Worth a 2-minute check (log in, see if
credits show) rather than assuming the form-fill alone didn't grant them.

---

## 2. Lyzr AI — Credits & How to Build (25 Aug 2026, presenter: Prasad)

### Core mental model taught (useful framing, not Lyzr-specific)
LLM = "water, takes the shape of the container" — answers, never acts.
Agent = LLM + **autonomy** to reason about *what* to do and actually do it.
Four components of any agent, platform-agnostic: **model, memory,
tools/knowledge, orchestration.** Five configuration primitives: **role,
goal, instructions, model, tools.**

Three ways to ground an agent in real context: knowledge base (unstructured
— PDFs, docs, RAG), data query (structured — DB/CSV, converts to
text-to-SQL live), tool calling (external APIs). Multi-agent only once a
single agent's prompt gets unmanageably complex or tools start overlapping
— "90% of the job gets done by a single agent." Manager-pattern
orchestration: one router agent with *no* tools of its own, several
tool-bearing sub-agents underneath it.

### Live demo — directly relevant, it's the exact shape CITINEL needs
Built a 4-agent HR system end-to-end in Lyzr Studio:
1. **Policy support agent** — knowledge base (PDF handbook, uploaded and
   chunked live).
2. **Employee info agent** — live MongoDB connection via a "semantic data
   model" (auto-generates a schema description, then answers in real
   text-to-SQL against the actual database — shown working live).
3. **Support ticket agent** — Gmail as a *tool*, added via the Tools panel;
   **for a tool not in the built-in catalog, "add as a custom tool" takes a
   plain OpenAPI schema, pasted in.**
4. **Manager agent** — no tools, only instructions naming which sub-agent to
   invoke for which intent; routes a single multi-part query across all
   three sub-agents automatically.

**This is the concrete recipe CITINEL needs for `CITINEL_LYZR_AGENT_ID`.**
`connectors/lyzr.py` needs a Studio agent that answers two tasks —
`pii_guard` and `ledger_head` (returning `{head, count}`) — and this demo is
a literal walkthrough of building exactly that kind of thing: define
role/goal/instructions, no knowledge base needed for either task, expose
each as a custom tool via its OpenAPI shape if CITINEL's own endpoints need
to be called back into. PARTNER-ONBOARDING.md previously said "this is
Studio configuration, not code" with no further detail — this demo *is* the
detail.

### Credits — the fact worth acting on
> *"you'll get $20 by default and every month it resets to $20."*
> *"we have 5 days for August. So you can utilize those 20 credits in those
> five days and then again it will reset to $20 again... when you're
> building for the finale you actually have new credits with you."*

Confirmed **twice**, in a live product session — not just claimed in a
webpage. This upgrades Lyzr from PARTNER-ONBOARDING.md's current "P2 —
lower confidence, no organizer redemption doc" status: there's still no
official PDF the way the other 6 partners have, but the $20/mo mechanic is
now confirmed working by a Lyzr employee demonstrating it live, and the
credit resets *again* right around the finale window — meaning the team
gets a fresh $20 specifically for finale week regardless of what's spent
before then.

Pricing model: execution-based (cost scales with agent complexity/tool
calls), not flat — reinforces keeping `LyzrGuard`/`LyzrLedgerMirror` calls
minimal and single-purpose rather than elaborate.

---

## 3. Startuped.ai — Platform, Workflow & Credits Q&A (24 Aug 2026, presenter: Kumal)

### What it is
A GTM/marketing execution platform, gamified with an XP checklist: accounts
(companies), leads (contacts), campaigns, "magic URLs" (trackable links),
forms, social scheduling (Instagram/LinkedIn/X, AI-generated 8-second video
clips + images using granted credits), Signal APIs (webhook-style event
tracking — e.g. every call/form-submit on your own product pings Startuped).
Developer access unlocks JS/Python SDKs + an MCP server.

### The one platform-mechanics fact worth logging
> *"I realized that a lot of you were getting stuck on the pay wall... we
> removed that friction."*

The paywall reported as an obstacle before is gone as of this session —
worth a fresh look if it was previously written off as blocked.

### The judging-criteria insight — this is the important part, and it
**generalizes beyond Startuped**
Direct Q&A exchange, presenter answering "how are XPs calculated":

> *"the team with 530 XPS does not automatically win... because then we'll
> see how well... which team has made most use or best use of startup for
> their own good... it might happen that one of the teams with a bit lower
> XP has used platform in a much better way. So it might happen. So we'll
> judge it based on that."*

Explicit: raw activity volume is not the win condition, genuine depth of
use is. See **Winning Potential Analysis** below — this is the same
principle the Render-services research workflow independently converged on
a few hours earlier tonight, from a completely different partner, unprompted.
Two independent sources agreeing on "judges reward genuine integration over
volume" is a strong enough signal to treat as a general rule across *all*
partner tracks, not just Render and not just Startuped.

### Relevance to CITINEL specifically
Low-priority per existing project guidance (deck/GTM work deprioritized
until asked for) — nothing here changes that scoping. Two things worth
knowing when that work resumes: the paywall's gone, and AI video/image
generation is available inside the same credit grant if a demo asset is
ever needed cheaply.

---

## Winning Potential Analysis

### 1. The strongest single finding: two "dormant" partner integrations already have real code waiting

Tonight's earlier Render-services research workflow found, independently
and before these transcripts were read, that `connectors/swytchcode.py`
(`SwytchcodeExecutor`) and `connectors/lyzr.py` (`LyzrGuard`,
`LyzrObserver`, `LyzrLedgerMirror`) are **fully written but have zero call
sites anywhere in the codebase** — dormant, waiting on Step 7.

These transcripts now supply the exact missing piece for both:
- Swytchcode's demo shows precisely the policy-guardrail pattern
  `SwytchcodeExecutor` is designed to sit behind (it already "refuses
  anything not already ALLOW/ALLOW_WITH_ROLLBACK" — that's the same
  guardrail-before-execution idea Swytchcode's own pitch is built around).
- Lyzr's demo shows exactly how to build the `pii_guard`/`ledger_head`
  Studio agent `connectors/lyzr.py` is waiting for.

**This reframes both partner tracks:** the highest-leverage move for
winning Swytchcode's and Lyzr's "best use" prizes isn't a new integration —
it's finishing the wiring on code that already exists, using the exact
recipes these two sessions just handed over. This is the same "wire what's
already there, don't build new decoration" conclusion the Render research
reached tonight, now showing up a second time from unrelated evidence.

### 2. A validated, cross-partner judging principle

Startuped's presenter stated explicitly that raw activity (XP) doesn't win
— depth and genuineness of integration does. That is *exactly* the
reasoning already applied tonight when rejecting the "10 Render services"
idea and when the research workflow's judges rejected all four proposed
new services for being insufficiently wired. Independent confirmation from
a partner's own judging criteria, not just an internal project preference.
**Practical implication:** every remaining partner-integration decision
should be screened the same way — "would a judge see this actually being
used, or does it just exist" — and this now has an actual partner's stated
words behind it, not just this project's own house style.

### 3. Two credit uncertainties resolved from earlier tonight
- Swytchcode: credits are live-through-finale if the team form was already
  submitted, per the presenter directly (not just the PDF's promise).
- Lyzr: the $20/mo mechanic is confirmed working, resets again right around
  the finale — de-risks the "no official redemption doc" concern raised in
  memory ([[project-citinel-anthropic-key-blocker]],
  [[project-citinel-sponsor-tracks]]) even without a PDF equivalent to the
  other 6 partners.

### 4. What this does *not* change
Step 7 (the agent swarm) is still the correct next build priority per
Danish's own "later we will improvise Step 7" — these transcripts don't
argue otherwise. What they do is de-risk and concretize the Swytchcode/Lyzr
wiring work that will sit *alongside* Step 7 once it starts (both connectors
are natural callers from inside the swarm/action-executor path), so when
that work happens it can move fast instead of starting from "what does a
Lyzr custom agent even look like."
