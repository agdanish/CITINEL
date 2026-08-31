# CITINEL web — handoff manifest

Static HTML/CSS/JS. No build step. Serve this directory from FastAPI (`StaticFiles`) or any
plain file server. Nothing here is React-authored, TypeScript, or bundled; do not migrate it.

Entry point: **`Entry.dc.html`** (splash/auth) → **`Overview.dc.html`** (landing console).

---

## 1. The one file you edit to wire the backend

**`api.js`** — the only seam between the UI and the service.

| Task | Change |
| --- | --- |
| Backend not same-origin | `API.BASE = 'http://localhost:8000'` |
| Second real corpus incident id | `API.INCIDENT_SECONDARY` (currently the placeholder `INC-0418`) |
| Turn on a route once it exists | flip that entry's `live: false` → `true` in `API.ENDPOINTS` |

`API.get(name, ...args)` **always resolves** — never throws into a render. It returns
`{ok, data, source: 'live'|'scripted', error}`. An endpoint marked `live: false` short-circuits
with `source:'scripted'` and makes **no network call**, so flipping the flag is the entire
integration for that surface.

Wrappers: `API.incidents()`, `API.incident(id)`, `API.auditFor(id)`, `API.draftFor(id, kind)`,
`API.policy()`, `API.verifyLedger()`, `API.probe()`.

### Endpoints — live today

| Endpoint key | Path | Returns |
| --- | --- | --- |
| `health` | `GET /healthz` | `{status, service}` |
| `incidents` | `GET /api/incidents` | `Incident[]` |
| `incident` | `GET /api/incidents/{id}` | `Incident` · 404 unknown |
| `audit` | `GET /api/incidents/{id}/audit` | `AuditEntry[]` · 404 none |
| `draft` | `GET /api/incidents/{id}/draft?kind=certin\|dpdp` | `{draft, rendered}` |
| `policy` | `GET /api/policy` | `{name, version, policy_sha256, clauses[]}` |
| `ledgerVerify` | `GET /api/ledger/verify` | `{intact, message}` |

### Endpoints — seam built, route does not exist

| Endpoint key | Intended path | Blocked on |
| --- | --- | --- |
| `verdict` | `GET /api/incidents/{id}/verdict` | agent swarm (step 7) not running |
| `proposals` | `GET /api/incidents/{id}/proposals` | Response Marshal not running |
| `execute` | `POST /api/actions/execute` | mocks only, no route |
| `rollback` | `POST /api/actions/rollback/{token}` | no route |
| `evalRuns` | `GET /api/eval/runs` | eval harness not exposed |
| `corpusRules` | `GET /api/corpus/rules` | corpus not exposed |

Paths in the second table are the intended shape, not a contract the service keeps. Rename
freely — one `path` function each.

---

## 2. Page-by-page wiring status

`uses` = endpoint keys from `api.js`. **live** = route exists today. **pending** = seam only.
`scripted` = stays on demo data even after wiring, because no endpoint covers it.

| Page | uses (live) | uses (pending) | still scripted |
| --- | --- | --- | --- |
| `Entry.dc.html` | — | — | statutory clock; first-run vs returning session |
| `Shell.dc.html` | `incidents` | — | nav counts; annunciator strip |
| `Overview.dc.html` | `incidents`, `policy` | — | agent fleet traces; autonomy mandate; disposition feed |
| `Queue.dc.html` | `incidents` | — | lane A/B split reasoning |
| `Replay.dc.html` | `incident`, `audit` | `verdict` | citation chips; agent timeline; kill-chain narrative |
| `Confidence.dc.html` | — | `verdict` | supporting/counter ledger; retired-evidence trail |
| `Evidence.dc.html` | `incident` | — | external-source provenance; quarantine well |
| `Approvals.dc.html` | `policy` | `proposals`, `execute`, `rollback` | blast rings; intent preview; rollback tokens |
| `Corpus.dc.html` | — | `corpusRules` | accession bench; export packet |
| `Eval.dc.html` | — | `evalRuns` | FP rate + denominators; inferred cost |
| `Policy.dc.html` | `policy` | — | autonomy dials; change history |
| `Compliance.dc.html` | `draft`, `incident` | — | press mechanics; DPDP artifacts |
| `Audit.dc.html` | `audit`, `ledgerVerify` | — | detect→sign ribbon geometry |
| `Handover.dc.html` | `incidents`, `audit` | — | watch register; exceptions |
| `Executive.dc.html` | `incidents`, `policy`, `ledgerVerify` | — | board narrative; quarter figures |
| `Settings.dc.html` | `health` | — | connector roster; enrichment quota; mock endpoints |
| `Demo.dc.html` | — | — | entire walkthrough, by design |
| `Narrow.dc.html` | `incidents`, `audit` | — | mirrors the console it replaces |

This table is the human-readable form of `API.PAGES` in `api.js`. **Keep them in step** — the
on-screen badge is derived from the code, not from this file.

### The data-source badge

Every page shows a small placard in its header, injected by `api.js` and **derived, never
authored**:

- `DEMO DATA` — page has no live endpoint, or `/healthz` did not answer
- `MIXED · n LIVE / m SCRIPTED` — some routes wired, some not
- `LIVE · <endpoints>` — all of the page's endpoints exist and the service answered

Hover for detail. Do not hand-edit it: once some pages are wired and others aren't, an
unmarked mix misrepresents which numbers are real.

---

## 3. Incident ids

| Constant | Value | Note |
| --- | --- | --- |
| `API.INCIDENT_PRIMARY` | `INC-0417` | real — Cerber chain, 2,487 findings, the id on the submitted deck |
| `API.INCIDENT_SECONDARY` | `INC-0416` | real — 337 findings, hosts `we8105desk` / `we1149srv`, techniques T1133 / T1078 / T1110 (external-facing credential + brute-force chain) |

Every printed id in the UI sits on one of these two: **INC-0417 ×50, INC-0416 ×9**, so fetch
paths and on-screen ids match the corpus.

Other ids in the UI are scripted filler with no backend counterpart and are not fetched:
`INC-0846` (×17, RDP-relay incident in handover/queue/approvals), plus `INC-0698/0729/0762/
0771/0803/0818/0839/0842/0844/0845` as single-mention history rows in the corpus and handover
registers. If any of these should map to real records, rename them here and in the page files;
nothing in `api.js` references them.

**Known narrative mismatch on both ids, deliberate.** The scripted prose does not match the
real records:

| id | scripted prose | real record |
| --- | --- | --- |
| `INC-0417` | UPI mule-cashout chain, ₹18.4L held | Cerber ransomware chain, 2,487 findings |
| `INC-0416` | consent phishing to mailbox exfiltration | external-facing credential + brute-force chain, 337 findings |

The ids match; the narratives do not. Once `incident`/`audit` are wired the API supplies the
narrative and the scripted copy is discarded. Until then both pages read `DEMO DATA`, which is
what makes the mismatch safe to ship rather than misleading.

---

## 4. Shared runtime files

| File | Role | Backend relevance |
| --- | --- | --- |
| `api.js` | the seam · endpoints, page registry, badge | **edit this** |
| `support.js` | template runtime for `.dc.html` · do not edit | loads React from unpkg |
| `role.js` | Analyst/CISO depth · `localStorage` only | **deliberate MVP scope** — no real auth. Leave as-is |
| `ledger.js` | in-session append-only ledger for UI continuity | replace reads with `audit` when wiring Audit |
| `route.js` | below 720px redirects to `Narrow.dc.html` | relative `location.replace`, no config |
| `reveal.js` | keyboard reveal for truncated values | none |
| `motion.js` / `motion.css` | instrument animation | none |
| `a11y.css` | focus, reflow, reduced motion, short-height layout | none |
| `assets/` | brand marks (`mark-white.png`, `mark-navy.png`) | none |
| `_ds/citinel-design-system-.../` | design tokens + component bundle | none |

`.dc.html` files are plain HTML with a template runtime. Each declares
`data-citinel-page="<key>"` on its screen root — that attribute is how `api.js` finds the
page's registry entry. Preserve it.

---

## 5. Vendoring — one command to zero network calls

Two runtime dependencies load from public CDNs by default. **Both are vendored by a single
command**, which must be run once on a machine with outbound network:

    bash vendor/fetch-vendor.sh

After it completes the app makes **no outbound requests at page load**. Verify with the command
the script prints on exit:

    grep -rn 'unpkg\.com\|fonts\.googleapis' *.dc.html _ds/*/tokens/fonts.css
    # expected: no uncommented matches

`bash vendor/fetch-vendor.sh --revert` undoes the wiring and returns to the CDNs; downloaded
files stay on disk.

### What it vendors, and how

| Dependency | Default source | Local path | Mechanism |
| --- | --- | --- | --- |
| React 18.3.1 + ReactDOM | `unpkg.com` | `vendor/react/*.js` | `vendor/resources.js` sets `window.__resources`, a URL→path map `support.js` already consults before falling back to its CDN URLs. **`support.js` is never edited.** |
| Babel standalone | `unpkg.com` | `vendor/react/babel.min.js` | same map. Only fetched at all if a `.jsx` is ever imported; no screen does today. |
| Michroma, Orbitron, IBM Plex Sans | `fonts.googleapis.com` | `vendor/fonts/*.woff2` + `vendor/fonts.css` | script pulls the CSS Google serves a modern UA, downloads each `woff2`, rewrites `src` to the local file, links the sheet in every page, and comments out the `@import` in `tokens/fonts.css`. |

**Why a script and not committed binaries:** the download needs network once, from a machine
that has it. This design session had no outbound access, so the files are not in the tree yet.
Nothing is generated at page load — the script is a build step, not a runtime fetch.

**Until the script is run**, the two CDNs are live and the app depends on them being up. That is
the current state of the tree as shipped. If the display face fails to load, Michroma falls back
to Orbitron then a generic sans; the wider fallback metrics push some fixed-width placards to
wrap, which is the failure mode vendoring removes.

---

## 6. Verified for static serving

- Every stylesheet, script, image and inter-page link is a **relative path**. No absolute or
  root-relative references except the two CDNs in §5.
- Nav links are plain `<a href="Queue.dc.html">`; they work outside an iframe.
- `route.js` uses `location.replace('Narrow.dc.html?...')` — relative, no origin assumption.
- Removed from the project: `_audit/` (measurement harnesses), `uploads/` (source material for
  the brand crops in `assets/`), `screenshots/`. None were referenced by any page.
- `CLAUDE.md` and `DEPLOY.md` are documentation. Do not mount them as routes.

## 7. Claim discipline — inherited constraints

These are product requirements, not styling. If backend data contradicts them, the UI is wrong
to display it uncaveated:

- `Settings.dc.html` states plainly that response actions run against **simulated endpoints
  only**. Execution receipts carry `simulated=true`. Keep this until `execute` is real.
- The false-positive target on `Eval.dc.html` is a **target, never an achieved result**, and no
  rate publishes without its denominator.
- Nothing claims CERT-In empanelment. "We draft, a human signs, the bank files."
- Coverage is always bounded and numeric (`214/823`, `3,000 @ 7f31c0d`) — never a blanket claim.
- The audit log records structured decisions and tool calls only. **Never model reasoning** —
  `Audit.dc.html` states this on-screen. Do not add a chain-of-thought field to `AuditEntry`.

## 8. Not in this pass

Partner-credit integration (Render, Tavily, n8n, Swytchcode, Lyzr, Startuped, Codemate, Gemini)
is explicitly deferred and comes after this handoff.
