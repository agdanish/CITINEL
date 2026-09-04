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

## The canonical-id bug this file used to contain

Both methods are scaffolded: `swy list tooling --json` reports
`github.issue.create` and `slack.chat.postmessage.create`, and those exact ids
are what the transport sends.

They were not, until 4 Sep. The module default, `render.yaml` and this file all
named `github.repo.issues.create` -- an id appearing in neither the scaffolded
registry nor GitHub's own 1,204-id definition. It named nothing at all.

The interesting part is the failure mode rather than the typo. The transport
classifies "tool not found" as `TransportUnavailable`, which the executor
records as a **`not_configured`** receipt. So the ticketing leg would not have
failed loudly. It would have written *"the Swytchcode runtime is not
scaffolded"* onto a tamper-evident audit ledger, on a deployment where the
runtime was scaffolded perfectly, sending an operator to re-run a scaffold that
was already correct. A false statement on the audit trail is the one failure
this product exists not to commit, and it would have arrived through an
integration rather than through the investigation.

Two things let it survive a full audit. The correct id was sitting in the local
`.env`, which is gitignored, so it reproduced only on Render and never on a
developer's machine. And `test_swytchcode_runtime.py` asserted the wrong id
inside a test named `test_the_arg_mapping_targets_real_canonical_ids`, so CI
certified the mismatch as correct. Both are fixed, with the three code and
config sites.

## What remains, precisely

Established by running the real binary on 4 Sep 2026, not by reading docs:

- **`swy login` is not required to execute.** The kernel's own help says it is
  "pure, deterministic, non-interactive, and offline-capable" and "never calls
  the registry". Login is for registry features and telemetry. The receipt that
  used to say otherwise was a misclassification, fixed below.
- **The GitHub leg works with no manual step.** CITINEL passes the PAT per call
  as the top-level `Authorization` argument, which is the shape the Python
  runtime documents. A dry run with CITINEL's exact arguments passes input
  validation, all three policies and credential resolution, and returns the
  request plan for `POST /repos/{owner}/{repo}/issues`.
- **The Slack leg needs a connected account, and that needs login.** The
  kernel ignores a per-call token for this provider and answers `missing
  credentials for Slack` for every placement, including both the runtime
  documents. Both providers are declared `oauth2` in the manifest, and
  connecting an OAuth provider runs through Swytchcode's own OAuth app and
  workspace, so `swy auth connect Slack` refuses until `swy login` has run.
  Login is therefore not needed to *execute* but is needed to *connect* Slack.
  The two manual steps, in order, on a machine with a browser:

  ```bash
  nvm use 20                 # swytchcode is installed under Node 20 only
  swy login                  # device-flow OAuth, one time
  cd ~/CITINEL/.swytchcode && swy auth connect Slack   # browser OAuth to Slack
  ```

  The existing `xoxb-` bot token is not used by this path. The connected
  account is stored as an encrypted blob in `~/.swytchcode/credentials.db`
  keyed by workspace and synced from Swytchcode's cloud. Whether the Render
  container can obtain it (most plausibly via `SWYTCHCODE_TOKEN` and a linked
  workspace) is **unproven**. Until it is, the Slack leg is demonstrable on a
  developer machine and not on the deployment.

## Two bugs the run found in CITINEL itself

**The classifier hid the real errors.** The CLI prints a telemetry notice on
every call, logged in or not, containing the words "Run `swytchcode login`".
The transport substring-matched the whole stderr stream, so that notice
satisfied its "not authenticated" check and every failure of every kind was
recorded on the ledger as `not_configured`. A broken policy definition and a
missing Slack credential were both written down as "the runtime is not
scaffolded", sending an operator to re-scaffold a runtime that was fine. The
transport now parses the single JSON error object the CLI emits and classifies
on its `category` field: `auth` is a deployment fact, `policy_denied` is the
guardrail working, and everything else is a failed action recorded with its
real reason.

**A policy that could not be evaluated.** The GitHub tool's request container is
itself named `body`, and GitHub's issue payload has its own `body` inside it.
The policy conditioned on `field: body`, and the kernel refused: "ambiguous
field resolution". Policy v1 does not support dotted paths (the validator says
so). The guard now conditions on `title`, which CITINEL always builds from the
target, so a ticket naming `cbs-prod` or `core-banking` is still blocked before
it leaves the process. Confirmed: a clean ticket passes, both forbidden titles
are `policy_denied` with CITINEL's own message.
