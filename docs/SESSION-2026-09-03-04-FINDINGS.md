# CITINEL session record, 3 to 4 September 2026

*Written 4 Sep 2026 for a new Claude Code account picking this project up. Every
fact here was verified in the session it describes; where something is only
believed, it says so. Companion files: `SESSION-2026-09-03-04-CHAT-LOG.md` (the
complete chat), `MEMORY-EXPORT.md` (Claude's memory), `../HANDOFF-MEMORY.md`
sections 21 and 22, `../NEXT-SESSION-PROMPT.md`, `../RUNBOOK-NEW-LAPTOP.md`.*

## 1. State at handoff

| | |
|---|---|
| Live console | https://citinel-web.onrender.com (Render, branch `build/stage-1`, Docker) |
| Branch head | `5f687ba` locally; `47e7235` on origin. **Two commits unpushed**: `9152bd5` (icon-only rail) and `5f687ba` (runbook). Push was held because a deploy restarts the service and Danish may have been mid-way through a swarm run. |
| Tests | 414 passing: `cd backend && .venv/bin/python -m pytest -q`. The system `python3` is 3.9 and cannot import the package; always use the venv. |
| Bugs found by running things, 4 Sep | 18, all fixed, all pushed except the rail commit above |
| External services proven live | 11 of 11 (see section 5) |
| Finale | Decode SIH 2026 grand finale, 5 Sep 2026 |

## 2. Ground truth before believing any document

```bash
git log --oneline -5 && git status --porcelain
curl -s https://citinel-web.onrender.com/healthz
curl -s https://citinel-web.onrender.com/api/connectors | python3 -c "import json,sys; c=json.load(sys.stdin)['connectors']; print(sum(x['configured'] for x in c),'of',len(c),'configured')"
curl -s https://citinel-web.onrender.com/api/n8n/executions?limit=3
curl -s -o /dev/null -w '%{http_code}\n' https://citinel-web.onrender.com/api/incidents/INC-0417/sweep
curl -s https://citinel-web.onrender.com/api/ledger/verify
curl -s https://citinel-web.onrender.com/api.js | grep -c citinel.operator     # 1 = device-arming build is live
```

## 3. What was built on 3 Sep (commits 087757f to 6e25c68)

- **Gemini**, two capabilities, both barred from being evidence: `connectors/gemini.py` (`x-goog-api-key` header, never `?key=`; test asserts the key is absent from the URL), `agents/sweep.py` (long-context sweep of every finding past the 40-finding evidence window; live run on INC-0417 swept 2,487 of 2,487, `blind_spot_risk: high`) and `agents/visual.py` (analyst image read, then deterministic corroboration against the record with citable finding indices). Bug found and fixed there: the corroborator searched a field named `raw`; the log line lives in `evidence_raw`, so an IP present in 43 findings was reported "never seen". Haystack now walks every finding value.
- **Lyzr**: seven agent seams (`lyzr_agents.py`: triage, review, handover, verdict, response, corpus; plus the base guard/witness). `_as_list()` guard for scalar-where-list replies. Studio recipes in `LYZR-AGENT-CONFIG.md`.
- **Tavily**: all five primitives (search with `include_answer`, extract, map, crawl, research with async polling).
- **n8n bidirectional** (`n8n_api.py`): read executions back as evidence; resume a Wait node from the Approvals screen. SSRF fix: a resume URL must share the host of `CITINEL_N8N_API_URL`; `urlparse` ValueError guarded.
- **Startuped** (`startuped.py`): five named signals, aggregate counts only; refuses (never strips) any field that could carry incident content; the one free-text field is regex-gated.
- **Swytchcode**: real runtime transport via the `swy` CLI, two ecosystem APIs (GitHub issue, Slack message), three policies in `.swytchcode/integrations/policies.json`.
- **Render**: `deploy/render.yaml` blueprint with env group `citinel-shared`, persistent disk at `/var/citinel` for the ledger and artifacts (`settings.ledger_path`, `settings.artifacts_dir` resolvers; 19 artifact sites moved), cron `citinel-ledger-watch`. Disk persistence proven: a ledger frame survived four redeploys.
- **Dockerfile.web**: Node plus `swytchcode@2.20.15`, extras `[swarm,api,detect]` (pysigma had been missing and `/api/corpus` was 500 in production).
- **Six qualification dossiers**: `STARTUPED-`, `LYZR-`, `GEMINI-`, `TAVILY-`, `N8N-`, `SWYTCHCODE-QUALIFICATION.md`.
- **Audit workflows** closed 23 findings plus 9 defects the verifiers found in code written hours earlier.

## 4. What was found and fixed on 4 Sep

Two adversarial bug-hunt workflows (five finder lenses each on Haiku, verifiers on the session model) and then an end-to-end audit that ran every seam for real. Each row: the defect, the false statement it would have produced, the commit.

| # | Where | Defect | Commit |
|---|---|---|---|
| 1 | `swytchcode_runtime_transport.py`, `render.yaml`, a test, the dossier | Ticketing id `github.repo.issues.create` exists nowhere; "tool not found" classified as `not_configured`, so a scaffolded runtime would be recorded as unscaffolded | `e302a24` |
| 2 | `lyzr.py` compare() | `int()` on a model-supplied `count` raised out of `GET /api/ledger/verify`, taking down the deterministic chain result | `e302a24` |
| 3 | `enrichment.py` Tavily search | `body.get()` on a non-dict body and `.get()` on scalar result rows raised into the incident path | `e302a24` |
| 4 | `lyzr.py` `_lyzr_allow`, `n8n.py` dispatch | `urlparse` raises on a malformed authority; two guards that looked total were not | `e302a24` |
| 5 | `app.py` `/api/n8n/error` | `or {}` is not a guard; a scalar `execution` 500ed the route whose job is to record failures | `e302a24` |
| 6 | `pipeline.py` Correlator and Narrator instructions | told the model there were n evidence blocks when n+1 were sent; a citation of the extra block was dropped for a false reason | `e302a24` |
| 7 | `Approvals.dc.html:210` | the only ternary inside a template hole in the console; border collapsed to none in both states | `e302a24` |
| 8 | `test_web_ops.py:115` | `assert ... or True` | `e302a24` |
| 9 | `lyzr.py` witness | a witness that has seen fewer entries than the local chain reported `diverged`, `tamper_suspected: true`; Executive led with that word on an intact ledger. Now `lagging`; the suspicious direction (remote >= local, different head) still alarms | `5699f9e` |
| 10 | `cli.py` `swarm run` | `NameError` on every invocation: the sink import was missing; no test reached the line | `33b3b67` |
| 11 | `pipeline.py` enricher frame | recorded which providers were asked, never what they answered; now per-provider `outcomes` | `33b3b67` |
| 12 | `swytchcode_runtime_transport.py` | Slack answers HTTP 200 with `ok: false`; the kernel wraps the body; a refused message went out as 200 and the ledger said "comms executed" | `25f583f` |
| 13 | `swytchcode.py` receipt | a failed action carried only "HTTP 502", not the provider's reason | `25f583f` |
| 14 | `enrichment.py`, `quarantine.py` | `api.virustotal.com` is NXDOMAIN at VirusTotal's own nameservers; every lookup ever made had failed silently (0 cache entries vs 29 for AbuseIPDB). Now `www.virustotal.com`; a test asserts connector and allow-list name the same host | `0aca361` |
| 15 | `swytchcode_runtime_transport.py` | an omitted `message` sent Slack an empty body (`no_text`); now composes the attribution line | `de194bb` |
| 16 | `.gitignore` | the 3.5 MB Swytchcode integration bundles were ignored; the container could not execute either leg ("bundle missing") | `b460038` |
| 17 | `.env` (local) | `CITINEL_N8N_WEBHOOK_URL` held a UUID path from a deleted workflow; CITINEL's sign-off had never reached n8n. Correct path: `/webhook/citinel-signoff`. Render's copy is `sync: false` and was set by Danish on 4 Sep evening (Part 1) | local only |
| 18 | console token layer | the operator token lived per browser tab; a demo laptop lost write access on every tab close with no visible sign | `47e7235` |

Three misdiagnoses made and corrected out loud: VirusTotal was called "ISP DNS filtering" (it was a retired hostname); "login not needed" for Slack (login is not needed to execute, it is needed to connect an OAuth provider); `no_text` blamed on CITINEL (the probe passed the wrong parameter name).

## 5. External services, each proven by a real call through CITINEL's own code

| Service | Proof |
|---|---|
| Anthropic | both model ids verified against `/v1/models` (`claude-haiku-4-5-20251001`, `claude-sonnet-5`); one real turn each; a full swarm run on INC-0417 (6 calls, 113,989 in / 31,112 out, 8 claims cited, 4 proposals) |
| Tavily | fresh search, 5 real URLs |
| Gemini | vision read a real logo as `kind: logo`; sweep 2,487 of 2,487 |
| Lyzr | all 7 agents answered; verdict audit 3 agree, 5 stricter than the pipeline, per claim with notes |
| n8n | sign-off from CITINEL: `channels ["ciso","ticket"]`, `execution_id 2`, read back via the REST plane |
| Startuped | real emit returned `sent` |
| AbuseIPDB | `abuse confidence 100% over 256 reports` |
| VirusTotal | after the host fix: EICAR 66 of 75 engines, a Tor exit 13 of 90 |
| Swytchcode | CLI 2.20.15, three policies valid, both canonical ids listed; logged in as Danish |
| Slack | one real post to `C0BUY5T2R7U`, `ts 1788519986.233539`, from a clean HOME `ts 1788522673.967219` |
| GitHub | per-call Authorization passes validation, policies and credential resolution in dry run; no real issue was created |

Egress: six hosts on the static allow-list (`quarantine.py`), Lyzr added at runtime from its configured URL, n8n pinned to the configured host, three (Swytchcode, GitHub, Slack) reached through a subprocess.

## 6. Swytchcode on Render, the whole path

Established by real sends from a clean HOME, never by `--explain` (which skips credential resolution and passes everything):

- The kernel keeps the connected Slack account in `~/.swytchcode/credentials.db`, encrypted under a key that on macOS lives in the Keychain (no `credkey` file exists on a Mac) and on Linux in a `credkey` file, looked up through the identity in `auth.json`.
- **Exactly `credentials.db` + `credkey` + `auth.json` resolve Slack. Any two do not.** A live session, `SWYTCHCODE_TOKEN`, and the per-call token are neither needed nor sufficient. GitHub needs none of this.
- Danish produced a file-keyed store by running `swy login` and `swy auth connect Slack` with `HOME=/tmp/swyhome` (macOS asked for a Keychain; Cancel pushed the CLI to the file key). Files rescued to `~/citinel-render-secrets/`.
- Render delivers them as Secret Files pasted as base64 text: `swy-credentials.db.b64`, `swy-credkey.b64`, `swy-auth.json.b64`. `Dockerfile.web` decodes them into `~/.swytchcode` at boot (`541812a`, `d554211`). Danish uploaded them on 4 Sep evening (Part 2).
- **Not yet proven on Render**: an approved action on the live Approvals screen with the receipt reading `comms executed` and a `ts`. That is Part 3 step 22 in `RUNBOOK-NEW-LAPTOP.md` terms; the result was not reported before the account change.

## 7. Console changes

- **Left rail** (`nav.js`, `e8d6317` then `9152bd5`): on every screen, mounted beside `#dc-root` outside the DC runtime; icon-only by default at 44px; hover or focus shows a translucent label beside that icon; the top control expands persistently (localStorage `citinel.rail`); glyphs are Direction A from the "CITINEL Rail Icons" canvas (https://claude.ai/code/artifact/7f2a2f4d-e1d6-4c47-aaca-61d93a9b7d90); footer shows `ARMED · NAME` or `READ-ONLY`.
- **Entry screen removed**; `/` redirects to Overview; tests updated.
- **Device arming** (`api.js`, `Settings.dc.html`, `47e7235`): operator name + token in localStorage `citinel.operator`, 12-hour lifetime, CLEAR forgets, every write carries `by` and sign-off `signed_by`, 401 and 503 mapped to one plain sentence each. All name prompts default to the armed name.
- **Sweep, context, handover, corpus advisory, Gemini vision** all have routes; **no console control exists** for the corpus advisory write (Corpus only reads) or for submitting an image to Gemini vision, or for the n8n resume route. Backend proven, UI missing.

## 8. Time zones (assessed, not changed)

Backend is clean UTC (19 aware `now()` calls, zero naive). Console is inconsistent: Audit and Compliance shift +330 min correctly; `Approvals.dc.html:1076` slices the UTC hour and labels it IST; `Handover.dc.html:500` labels browser-local hours as UTC; 15 `toLocale*` calls carry no `timeZone`; Settings says the quota "resets 00:00 IST" (VirusTotal resets on the UTC day). Recommendation given: one shared formatter pinned to `Asia/Kolkata`, IST primary with UTC beside it, display zone as a setting. About 40 lines plus 15 call sites. Danish did not decide.

## 9. Credentials that should be rotated after the finale

Screenshots shared in chat showed Render secrets in plain text, and one Gemini key was pasted into the chat (redacted from the log). Rotate `CITINEL_ANTHROPIC_API_KEY`, `CITINEL_N8N_API_KEY` (full-account scope), `CITINEL_SWY_GITHUB_TOKEN`, `CITINEL_GEMINI_API_KEY`, and `CITINEL_WRITE_TOKEN` (rotating it disarms every laptop at once). `auth.json` in Render's secret files is Danish's Swytchcode account credential.

## 10. Pending, in priority order

1. Confirm Part 3 finished (Danish's report of the Approvals receipt line), then `git push origin build/stage-1` for `9152bd5` and `5f687ba`.
2. Verify production from outside after Part 3: sweep 200, context fresh, verdict updated, handover 200, `/api/n8n/executions` grew, Startuped signals carry values, the new enricher frame shows VirusTotal `ok`.
3. Auto-Deploy off on the four Render services before the demo; on again after.
4. Demo day: arm the demo laptop (runbook part A); never re-run the swarm on stage unless scripted.
5. After the event: CLEAR or rotate the write token; rotate the keys in section 9.
6. Later: the three missing console controls in section 7; the time-zone formatter in section 8; real per-person login to replace the shared operator token.

## 11. Danish's standing preferences (from Claude's memory, verbatim in `MEMORY-EXPORT.md`)

No em dashes. Baby steps for anything manual. Do not over-complicate. Be brutally honest; never guarantee a judged prize. Verify against real data, not code reading. Default Haiku for subagents; ask before Sonnet or Opus. Every push to `build/stage-1` is a deploy. Use partner credits on genuinely wired seams. Do not bring up the pitch deck unprompted. Render-side secrets are Danish's to set; Claude never handles credential values.

## 12. Claims that must never be made

The false-positive rate is unmeasured. Sign-offs are drafts ("we draft, we never file"). Response actions hit simulated endpoints. No prize is guaranteed. The deck's QR code resolves to Danish's portfolio, not a prototype. Nothing a model says is evidence; only deterministic corroboration with citable indices is.

## 13. Pitch-facing facts established on 4 Sep (only in the chat until now)

**Differentiators a judge can check by opening a URL**, ten, distinct from the 33 externally sourced UVPs in `CITINEL-SDD.md` §13 and §17 (most of which are positioning, not code):

| # | Differentiator | Where to check |
|---|---|---|
| 1 | Citation-verified verdicts: a claim whose quote is absent from the cited finding is dropped, not flagged | `agents/pipeline.py` citation verification; `GET /api/incidents/INC-0417/verdict` |
| 2 | Observation vs fact enforced in the payload: Gemini's sweep and vision carry `not_evidence` in the data; corroboration is deterministic with citable indices | `agents/sweep.py`, `agents/visual.py` |
| 3 | Hash-chained ledger with an independent witness that can see wholesale replacement `verify_chain` cannot | `audit/ledger.py`, `connectors/lyzr.py` compare() |
| 4 | Inter-agent laundering closed: the Correlator's summary is fenced before the Narrator sees it | `agents/pipeline.py` correlator_summary_evidence |
| 5 | Deterministic egress allow-list, exact host, https only | `agents/quarantine.py` |
| 6 | Blind-spot disclosure then closure: 40 of 2,487 findings examined, said out loud, then swept | Replay screen, `GET .../sweep` |
| 7 | Privacy boundary in code: the Startuped connector refuses any field that could carry incident content | `connectors/startuped.py` |
| 8 | Policy gate with rollback tokens and blast-radius caps; OPA trace expandable | Approvals screen, `POST /api/actions/execute` |
| 9 | Fail-closed writes with distinguishable failures: 503 unset vs 401 wrong | `web/app.py` `_guard_writes` |
| 10 | No measurement without its denominator | every screen |

Honest framing that goes with it: four of the eighteen bugs found on 4 Sep were violations of rows 1 to 4, which shows the rules are load-bearing and that they need testing, not trust.

**Egress precision for the stage**: six external destinations sit behind the static allow-list (Anthropic, VirusTotal, AbuseIPDB, Tavily, Gemini, Startuped); Lyzr's host is added at runtime from its configured URL; n8n is pinned to the configured instance host; Swytchcode, GitHub and Slack are reached through a policy-gated CLI subprocess. Say "six behind an exact-host allow-list, the operator-configured ones pinned to their host, three mediated by a policy-gated CLI", not "everything behind an allow-list".

**Environment surface**: 40 variables total; 28 external across 9 third-party services (Lyzr 9, Swytchcode 8, n8n 3, Anthropic 2, Gemini 2, Tavily 1, Startuped 1, VirusTotal 1, AbuseIPDB 1); 27 of the 50 blueprint keys are `sync: false` (hand-set in Render); seven blueprint keys are absent from the local `.env` by design (`CITINEL_WRITE_TOKEN`, `CITINEL_LEDGER_PATH`, `CITINEL_ARTIFACTS_DIR`, `CITINEL_ROLE`, `CITINEL_WEB_URL`, `CITINEL_AUTO_SWARM`, `CITINEL_AUTO_SWARM_MAX_PER_CYCLE`); `CITINEL_DATABASE_URL` is declared, empty and inert.

## 14. Identifiers and contracts for the night something breaks

- **n8n**: instance `hritikmb.app.n8n.cloud`, workflow "CITINEL Beat 5b" id `71UYwPBAgRPjr5ZG`, production webhook path `citinel-signoff` (the `/webhook-test/` URL only works while "Listen for test event" is armed). The Respond to Webhook node must return JSON `{"channels": ["ciso","ticket"], "execution_id": "{{ $execution.id }}"}`; `dispatch_signed` refuses to claim success without `channels`. In this n8n build **Publish** is the activation control, not a Save/Active toggle. `CITINEL_N8N_API_URL` must be the origin only.
- **Slack**: workspace xzashr (team `T0BUGPTTBC7`), channel `C0BUY5T2R7U`, posts arrive from the Swytchcode app, bot id `B0BV2ELUAL9`. `not_in_channel` means the app was removed from the channel: `/invite @Swytchcode`. `no_text` means the caller omitted `message`.
- **Swytchcode**: CLI 2.20.15 installed only under Node 20 (`nvm use 20`; nvm's default is lts/* = v24 where `swy` does not exist). Canonical ids `github.issue.create`, `slack.chat.postmessage.create`. `swy auth status` shows connected providers. `--explain` skips credential resolution; never use it to prove credentials.
- **Render**: services `citinel-web` (Docker, disk `citinel-ledger` at `/var/citinel`, `CITINEL_WRITE_TOKEN` set on the service itself), `citinel-pipeline` (worker), `citinel-ledger-watch` (cron `0 */6 * * *`), `citinel-n8n`; database `citinel-postgres` exists and nothing reads it. Env group `citinel-shared` (31 vars). Secret Files on citinel-web: `swy-credentials.db.b64`, `swy-credkey.b64`, `swy-auth.json.b64`.
- **Lyzr**: seven agent ids in env (`CITINEL_LYZR_AGENT_ID` plus `_TRIAGE_`, `_REVIEW_`, `_HANDOVER_`, `_VERDICT_`, `_RESPONSE_`, `_CORPUS_`), all answering live on 4 Sep. The witness reports `unavailable` when the Studio call times out; that is honest, not an alarm.
- **Anthropic**: `claude-haiku-4-5-20251001` (triage) and `claude-sonnet-5` (reasoning), both verified against `/v1/models` at boot; identity-linked keys need `anthropic-workspace-id`, which `agents/build.py` sends.
- **Rail icons**: Direction A was built without Danish choosing; B (the ring) and C (terminal codes) remain on the canvas https://claude.ai/code/artifact/7f2a2f4d-e1d6-4c47-aaca-61d93a9b7d90 and are a one-list swap in `nav.js`.

## 15. Testing writes locally without touching real data

`.claude/launch.json`'s `citinel-dashboard` entry runs the real data directory on port 8000 with no write token, so every write there answers 503 and nothing is written. To exercise writes for real, run the app with a scratch ledger and artifacts and a token you choose:

```bash
S=/tmp/citinel-scratch; mkdir -p $S/artifacts; cp data/seed/ledger.jsonl $S/; cp -R data/seed/swarm data/seed/context $S/artifacts/
CITINEL_WRITE_TOKEN=local-verify-token CITINEL_LEDGER_PATH=$S/ledger.jsonl CITINEL_ARTIFACTS_DIR=$S/artifacts \
  backend/.venv/bin/uvicorn citinel.web.app:app --host 127.0.0.1 --port 8099
```

Then POST with `X-Citinel-Write-Token: local-verify-token`. Every write route was proven this way on 4 Sep. A swarm run costs real Anthropic credits even locally; `citinel swarm run INC-0417 --incidents-dir <scratch>` was about 114K input and 31K output tokens.

## 16. The read-only pre-flight

`python3 scripts/preflight.py` (GETs only, no token, no spend) checks every read route, the ledger, the witness, all connectors, n8n executions, the incident's artifacts, every console page, that the deployed api.js and nav.js are the current builds, and that every console endpoint has a backend route. It prints GO or the exact problems. **Run it on the demo morning before arming the laptop.**

At 22:20 IST on 4 Sep it reported NO-GO on one item, `INC-0417 sweep artifact present: 404`, with the ledger still at 5,778 entries and n8n at the two executions from testing. That means Part 3 of the runbook had not been run at that time.
