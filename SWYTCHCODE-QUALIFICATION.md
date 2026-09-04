# CITINEL × Swytchcode — qualification dossier

*Written 4 Sep 2026. This track published five explicit requirements, so this
dossier scores each one honestly — including the ones not yet met.*

---

## Scorecard

| # | Requirement | State |
|---|---|---|
| 1 | Build the solution using the Swytchcode CLI | **done** |
| 2 | Use the Python or TypeScript runtime | **done** |
| 3 | Integrate ≥2 external APIs from the ecosystem | **half** — Slack registered, GitHub fetched but not added |
| 4 | Include an AI-powered workflow or AI agent | **done** |
| 5 | Demonstrate a functional end-to-end application | **blocked on 3** |

**One command closes the gap.** See "What remains" at the end.

---

## 1. Built with the CLI ✅

`swy init` scaffolded `.swytchcode/` in the repo root. The lightweight config
is committed and the regenerable bundles are gitignored, following
Swytchcode's own published `.gitignore` guidance, so `swy bootstrap`
reconstructs a clone.

Three policies live in `.swytchcode/integrations/policies.json` and are
accepted by the real validator:

```
› policies.json is valid (3 policies).
```

## 2. Python runtime ✅

`swytchcode-runtime` (PyPI), wired as the transport in
`backend/citinel/connectors/swytchcode_runtime_transport.py`. It is a
subprocess wrapper around the `swy` binary rather than an HTTP client — its own
README calls it *"a pipe, not a brain"* — so the binary must be present and the
project scaffolded, and the connector reports exactly that when it is not.

## 3. Two ecosystem APIs — a genuine division of labour ⚠️

| CITINEL role | Ecosystem API | Job |
|---|---|---|
| `ticketing` | GitHub Issues | an incident ticket a human can pick up |
| `comms` | Slack | the response team hears about it |

Two calls to one service would not be two APIs. These do different jobs at
different moments, and `execute_for_decision` invokes both.

**Current state:** `tooling.json` registers `Slack.slack` with
`slack.chat.postmessage.create`. GitHub's bundle is fetched
(`.swytchcode/integrations/GitHub/`) but is **not registered as a tool**, so
only one of the two is live.

**Credentials are headless.** They travel per call rather than through an OAuth
browser flow — which is what Swytchcode's own multi-API example does. Nothing a
demo machine has to be logged into.

**A real correctness fix came out of reading the scaffolding.** Slack's
registered tool declares its credential parameter as `token`; Swytchcode's
GitHub example passes `Authorization`. The transport had assumed one shape for
both, which would have put the credential in a field the tool never reads —
and the call would then have failed for a reason looking like anything except
the real one. It now reads the declared parameter name out of `tooling.json`,
which the CLI writes and which is the only authority.

## 4. AI agent ✅

Comfortably. A seven-agent Claude swarm, seven Lyzr Studio agents, Gemini for
long-context sweeps and vision. Swytchcode sits **downstream** of all of it, as
the execution path for actions the agents proposed.

## 5. End-to-end — and why the policy layer is the real story ⚠️

Blocked only by requirement 3.

Swytchcode's own pitch is that **API success is not the same as correct agent
behaviour** — their running example being an agent that sent the same email
thirty-five times, every call returning 200, the outcome a disaster. That is
the same argument CITINEL makes about cited evidence, which is why this fits
without bending anything.

**The layering, which is the point:**

```
Claude swarm proposes  →  OPA gate decides  →  Swytchcode policy  →  API call
                          (the authority)      (the second guard)
```

Swytchcode never overrides OPA — `execute_for_decision` refuses anything not
ALLOW or ALLOW_WITH_ROLLBACK, and does so **before any transport is touched**.
It is the hand, never the head. And because Swytchcode evaluates *before* the
request leaves, a block proves an action can be stopped **outside the agent's
own reasoning, under a gate that had already approved it**. That is defence in
depth a judge can watch happen.

`policy_blocked` is a first-class receipt status for exactly this reason — a
blocked action is the guardrail working, not a failure, and the audit ledger
must not describe it as one.

**The three policies:**

| Policy | Blocks |
|---|---|
| `citinel-no-core-banking-in-ticket` | a ticket naming core banking infrastructure |
| `citinel-no-unaddressed-comms` | a notification with no destination — the shape of the repeated-send failure Swytchcode exists to prevent |
| `citinel-ticket-must-name-its-incident` | an unattributable ticket |

## Two things the real tooling taught that the docs did not

1. **The validator rejects dotted field paths in v1.** `body.title` had to
   become `title`. Only running `swy policy validate` surfaced this.
2. **The CLI writes progress onto the same stream as its errors**, so an
   unauthenticated call's text contains the word "policy" incidentally. A loose
   match wrote *"a policy stopped this"* onto the permanent audit ledger when
   in truth nobody was logged in. Auth state is now classified before policy
   state, matched on the documented action type rather than a substring, and
   there is a test named after that confusion.

## Where to look

| Claim | Check |
|---|---|
| CLI scaffolding | `.swytchcode/tooling.json`, `swy policy list` |
| the policies | `.swytchcode/integrations/policies.json`, `swy policy validate` |
| the runtime transport | `backend/citinel/connectors/swytchcode_runtime_transport.py` |
| gate-refusal + policy handling | `backend/citinel/connectors/swytchcode.py` |
| tests | `backend/tests/test_swytchcode_runtime.py` (8) |
| live | `GET /api/connectors` → `swytchcode` |

## What remains

```bash
swy add method github.repo.issues.create     # closes requirement 3
swy list tooling --json                      # confirm the real canonical ids
```

Canonical ids differ between Swytchcode's docs and their own examples, so that
second command is the authority. If the id differs from the default, set
`CITINEL_SWY_TICKET_METHOD`.

Then in Render's `citinel-shared` group: `CITINEL_SWY_GITHUB_TOKEN` (a PAT with
repo scope), `CITINEL_SWY_SLACK_TOKEN`, `CITINEL_SWY_SLACK_CHANNEL`.

**Until then the seam reports `not_configured` and executes nothing** — which
is the honest state, and deliberately so: a configured key with no reachable
runtime used to produce `error` receipts on the permanent audit ledger that
read like transient failures, making a configured deployment strictly worse
than an unconfigured one. That was fixed.
