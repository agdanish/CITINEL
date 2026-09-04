# CITINEL × Startuped.ai — qualification dossier

*Written 4 Sep 2026. The track asks teams to demonstrate that Startuped.ai was
used for idea validation, market research, GTM planning, product positioning
and launch strategy. This file is the evidence index for that claim.*

**It is deliberately split into two halves, and the split is the point.**
Part 1 is already true and checkable by anyone with the repo. Part 2 is not
true yet — it needs you to run five modules — and every slot in it is marked
`[AWAITING YOUR EXPORT]` rather than filled with something plausible. A
dossier that asserted usage that had not happened would be the one thing
guaranteed to lose this track if a judge clicked through.

---

## Part 1 — What is already demonstrable

### 1.1 CITINEL is instrumented with Startuped's Signal API

Not a screenshot of a dashboard: running code, deployed, tested. This is the
depth-of-use the platform's own team said decides the award.

> *"the team with 530 XPs does not automatically win… which team has made most
> use or best use of Startuped for their own good… it might happen that one of
> the teams with a bit lower XP has used platform in a much better way."*
> — Startuped session, 24 Aug 2026

| Where | What |
|---|---|
| `backend/citinel/connectors/startuped.py` | the connector |
| `backend/tests/test_startuped_signals.py` | 10 tests, incl. leakage guards |
| `GET /api/startuped/signals` | live route publishing exactly what is sent |
| `GET /api/connectors` | reports `startuped` alongside every other integration |

**Five signals**, each appended as an aggregate count at the moment the product
does the thing:

| Signal key | Type | Fires when |
|---|---|---|
| `citinel-incidents-investigated` | behavioral | a swarm run completes |
| `citinel-verdicts-cited` | conversion | a verdict's claims survive citation |
| `citinel-actions-gated` | behavioral | a proposal goes through the policy gate |
| `citinel-reports-drafted` | conversion | a CERT-In or DPDP artifact is drafted |
| `citinel-signoffs` | retention | a named human signs an incident off |

Those five answer the question a GTM platform exists to ask — is anyone using
this, and which part — as a funnel: incidents in, verdicts cited, actions
gated, reports drafted, humans signing. Adoption of the differentiating
feature is directly readable as `verdicts-cited ÷ incidents-investigated`.

### 1.2 The integration is privacy-safe by construction, not by intention

This is the part worth showing a judge, because most integrations do not do it.

Startuped is a go-to-market platform. CITINEL processes cooperative-bank
security telemetry. **No incident id, host, IP, finding, evidence, target or
account name can leave through this connector.** The guard *refuses* a
forbidden field rather than stripping it — stripping would let a caller
believe it sent something it did not — and the test inspects the whole
serialised body for leakage rather than the fields someone remembered to
check.

`GET /api/startuped/signals` publishes that claim so it can be checked rather
than taken on trust. A marketing signal also cannot slow, break or alter an
investigation: every call is best-effort and silent on failure, with a test
asserting it.

### 1.3 What the research corrected

Three things in circulation about this platform are wrong, and building to
them would have produced an integration against an API that does not exist:

- **The Signal API is not event tracking.** No webhook receiver, no
  `track(event, properties)`, and the docs state there is no native lead or
  account association. It is CRUD for named records with a time series.
- **"Magic URLs" do not exist** in the public API. `/{leads,accounts}/{id}/links`
  are entity-relationship edges between records, not trackable short links.
- **The Python SDK has no signals resource.** `startuped-ai` exposes auth,
  leads, deals, accounts, contacts, tasks, credits and agents — signals are
  raw HTTP only.

Naming these is itself evidence of depth: it is what reading a platform
properly looks like, as opposed to citing its marketing page.

---

## Part 2 — The five criteria

Inputs are locked and adversarially verified in `STARTUPED-GTM-PLAYBOOK.md`
(25 Aug), which maps 1:1 onto the criteria published later. **Run the module,
export the output, drop it in.** Do not improve the thesis while running it —
the point is to put the locked thesis through the tool.

### 2.1 Idea validation
**Input:** Playbook §A1 — CITINEL for India's cooperative banks and small
NBFCs, carrying the same RBI 24×7 SOC mandate and CERT-In 6-hour obligation as
national banks on a fraction of the budget.
**Startuped output:** `[AWAITING YOUR EXPORT]`

### 2.2 Market research
**Input:** Playbook §A2 — deliberately does *not* hardcode a TAM, because
quantifying it is the module's job and the thing the criterion wants to see
used.
**Startuped output:** `[AWAITING YOUR EXPORT]`
**Guardrail:** if it emits one large TAM, present it as a range with its
assumptions stated (ledger rule L6). Never as fact.

### 2.3 Product positioning
**Input:** Playbook §A3.
**Startuped output:** `[AWAITING YOUR EXPORT]`

### 2.4 GTM planning
**Input:** Playbook §A4 — B2B2X through MSSPs and Market-SOCs.
**Startuped output:** `[AWAITING YOUR EXPORT]`

### 2.5 Launch strategy
**Input:** Playbook §A5.
**Startuped output:** `[AWAITING YOUR EXPORT]`

### How to run it

```
1. https://www.startuped.ai/forms/decode-sih-2026   (verified live 4 Sep)
   Firstname*, Lastname, Email*, Phone, University*, Degree Program*
   -> they email a join link
2. Log in; confirm the grant credits show
3. Run the five modules in the order above, pasting each Playbook block
4. Export or screenshot each output
5. Save under docs/startuped-exports/ so they are versioned with the code
6. Replace each [AWAITING YOUR EXPORT] slot with the real output
```

Also: **Dashboard → API Keys** to mint an `sk_…` key for the integration in
Part 1. Keys are shown once and expire in 30 days by default — mint it close
to the finale, not before.

---

## The pitch, in five sentences

CITINEL used Startuped for the thinking *and* wired itself to the platform.
The GTM thesis was run through the five modules rather than written in a deck,
so positioning and market sizing are the tool's output, not our assertions.
The product then reports its own adoption back as five aggregate signals, so
Startuped can see the funnel from incidents investigated to humans signing
off. That integration is built to a privacy boundary a security product cannot
cross, and it publishes what it sends so the claim is checkable. Most
integrations show a dashboard; this one shows a connector, its tests, and the
line it refuses to cross.

---

## Honesty guardrails carried over from the playbook

- Market size as ranges with scope declared. No single confident TAM.
- **No fabricated traction.** CITINEL has no customers. The GTM is a plan, not
  a track record — "planned/target", never an implied signed partner.
- The ~5¢/incident economics is our own instrumented figure, labelled
  `[INFERENCE]`.
- Pricing anchors (₹250–1,000/device) are Med-confidence, single-source.
- The award is judged on demonstrated use. Part 1 is real today; Part 2 is not
  until you run it, and this file says so on its face.
