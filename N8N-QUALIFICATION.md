# CITINEL × n8n — qualification dossier

*Written 4 Sep 2026. This track published its criteria, so this dossier maps
each one directly.*

> **Teams must:** integrate n8n into their hackathon project · demonstrate how
> workflow automation improves the project's functionality, efficiency, or
> user experience

---

## Criterion 1 — Integrate n8n

Three integration paths, in three directions. Most entries have one.

| Direction | Path | What it does |
|---|---|---|
| CITINEL → n8n | webhook | sign-off fires the escalation playbook and reads back which channels succeeded |
| CITINEL ← n8n | `GET /api/v1/executions` | playbook runs become citable evidence inside CITINEL |
| n8n → CITINEL | `POST /api/incidents/{id}/n8n/resume` | a paused playbook asks CITINEL for a human decision |
| n8n → CITINEL | `POST /api/n8n/error` | a failed playbook reports itself onto the audit trail |

The webhook and the REST API are **two different planes**, and n8n is explicit
that neither does the other's job: the API manages and reads workflows but
documents no endpoint that runs one, while a webhook triggers a run and cannot
be queried afterwards. Using only one leaves an automated action that no
reviewer can inspect. Both are used.

`citinel-n8n` also runs as a **self-hosted service in CITINEL's own Render
blueprint** with a 1GB persistent disk for its workflows and credentials — n8n
is part of the deployed system, not an external account someone logged into.

## Criterion 2 — How automation improves the product

### It makes automated action auditable

This is the strongest claim here. **An automated action inspectable only inside
another tool is not auditable** — precisely the blind spot this product exists
to close everywhere else. So:

- dispatch captures the `execution_id` a playbook returns (via
  `{{ $execution.id }}` in a Respond to Webhook node), which makes a specific
  run citable and replayable rather than merely reported
- `GET /api/n8n/executions` reads runs back with their id, state, mode and
  timestamps, to sit beside the ledger frames
- a `401` reports **a rejected key**, not an empty list — "no executions" and
  "unusable credential" are different facts about a deployment, and conflating
  them would let a broken integration look like a quiet one

### It inverts the approval, which improves the analyst's experience

Rather than CITINEL asking a human and then telling n8n, **the playbook parks
itself on a Wait node and hands over its own `$execution.resumeUrl`.** The
analyst answers on CITINEL's Approvals screen — never leaving the console —
and the workflow branches on what they decided.

**n8n holds the workflow state. CITINEL holds the human.** Each does the thing
it is actually good at. Every resume is a ledger frame under the approver's own
name, so a human decision that changes what a machine does next is recorded
where every other such decision lives.

The resume URL is **never constructed by CITINEL**. Its shape is undocumented —
a community example shows `/webhook-waiting/<id>`, but that is not a contract.
The playbook supplies the URL and CITINEL calls it back.

### It lets the SOC see its own automation failing

n8n's Error Trigger posts to `POST /api/n8n/error`, which records the failed
workflow, the node that failed and the message against the incident the
playbook was working on. **A SOC that cannot see its own automation failing has
the same blind spot it hunts for everywhere else.**

### It stays glue, never the gate

n8n owns the visible escalation workflow. OPA remains the sole policy
authority. Nothing in an n8n playbook can approve an action the gate refused —
and the connector refuses a non-https webhook outright, so a signed incident
payload cannot travel in clear text.

## Criterion 3 — Efficiency

- One sign-off fans out to notify, export and ticket without CITINEL
  implementing any of the three.
- The playbook is editable by an operator in n8n's UI without touching CITINEL,
  which is the actual argument for workflow automation over hardcoding.
- The connector **refuses to claim success** unless the response names which
  channels succeeded. An earlier version defaulted to claiming all three; that
  was wrong, and the audit ledger recorded it being wrong.

## Where to look

| Claim | Check |
|---|---|
| dispatch + execution id | `backend/citinel/connectors/n8n.py` |
| the read and resume planes | `backend/citinel/connectors/n8n_api.py` |
| tests | `backend/tests/test_n8n_bidirectional.py` (12) |
| the service | `deploy/render.yaml` → `citinel-n8n`, disk `n8n-data` |
| live | `GET /api/n8n/executions`, `GET /api/connectors` |

## Honest limits

- **The webhook plane is configured in production; the API plane is not.**
  `GET /api/n8n/executions` reports `not_configured` until
  `CITINEL_N8N_API_URL` and `CITINEL_N8N_API_KEY` are set in the
  `citinel-shared` env group. Settings → n8n API → Create an API key.
- **The Wait-node playbook must exist in n8n for the resume path to have
  anything to resume.** CITINEL's side is built and tested; the workflow is
  drawn in n8n's UI, and that half is not done.
- API keys have full account access unless you are on Enterprise, where scopes
  exist. Treat the key accordingly.
- An expired Wait reports `expired`, not an error — a `Limit Wait Time` will
  have already moved the workflow on, and that is not a failure.
