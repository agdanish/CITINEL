# CITINEL
## Partner track videos: Tavily, Lyzr, Swytchcode

*Three two-minute recordings. One person records the screen. One person records
the voice. Every word in **BOLD CAPITALS** is printed on the screen, so the
camera person can find it by eye. Every voice line is under twelve words, so the
audio stays crisp at ElevenLabs pace. Each script is written to the track's own
published criteria, and claims nothing the live app cannot show.*

---

# Before any recording

## The screen setup, once

1. Use a laptop window at least 1500 pixels wide.
2. Switch the role toggle to **ANALYST**. CISO hides detail.
3. Arm the laptop: **CONNECTORS**, **ARM THIS DEVICE**, name, token, **SAVE**.
4. Confirm the green dot and **ARMED** at the foot of the rail.
5. Open **REPLAY** for **INC-0417**. Confirm the chip reads **STATE CAUGHT**.
6. If it reads CLOSED, click **REOPEN FOR RE-INVESTIGATION**, OK, OK.
7. Open **COMPLIANCE** once and wait 20 seconds. This warms the drafter.
8. Close every other tab. Hide bookmarks. Full screen the browser.

## The voice setup, once

- Record each script as one file. Do not stitch.
- Speak at a steady pace. About 140 words a minute.
- Pause one full second at every line marked **[beat]**.
- ElevenLabs: stability 55, similarity 75, style 20. Pick a calm voice.
- Export as WAV. Name it `tavily.wav`, `lyzr.wav`, `swytchcode.wav`.

## The rule that protects every video

- 🔴 Never say a prize is certain. Say "built to the track's criteria".
- 🔴 Never say a false-positive rate. It is unmeasured.
- 🔴 Never say an action touched a real system. All simulated.
- 🔴 Never say the Slack leg works unless it executed on screen that day.

---

# VIDEO 1 · TAVILY · Best Use of Tavily track

## The one sentence

*Tavily is the only thing in CITINEL allowed to read the open web, and nothing it
returns is ever allowed to become evidence.*

## Before this take

1. On **REPLAY** for INC-0417, scroll the right column to **THREAT BRIEF · TAVILY RESEARCH**.
2. Click **REQUEST THREAT BRIEF** now, before recording. Research is asynchronous.
3. Wait until the button reads **ASK AGAIN** and a brief with sources is shown.
4. Scroll up to **PUBLIC CONTEXT · TAVILY**. Confirm it reads *last gathered* with a date.
5. Scroll back to the top of the page. Start recording.

## The take

| Time | CAMERA does | VOICE says |
|---|---|---|
| 0:00 | Show **REPLAY** for INC-0417. Hover the header. | This is CITINEL. An AI security operations centre for Indian cooperative banks. |
| 0:06 | Point at the **ENRICH** lane, labelled **Enrichment Squad**. | Its investigation runs in stages. One stage reads the open web. |
| 0:12 | Hold on the lane. | That stage is Tavily. Nothing else in this system may touch the internet. |
| 0:18 | Scroll the right column to **PUBLIC CONTEXT · TAVILY**. | Here is what Tavily gathered for this incident. |
| 0:24 | Point at the note: **18 sources for 6 queries**. | Eighteen sources. Six queries. Six credits. Every number carries its denominator. |
| 0:31 | Point at one query row, then its citation chips. | Each row is one attack technique the correlator named. |
| 0:37 | Point at a chip marked **EXTRACTED ·** | Tavily Search found the page. Tavily Extract read the full text. |
| 0:43 | Point at a chip marked **CRAWLED ·** | Tavily Crawl followed the site. That is a page read, not a link found. |
| 0:49 | Point at the words **mapped live from ATT&CK**. | Tavily Map pulled sub-technique pages live from the MITRE site. |
| 0:55 | Click **GATHER PUBLIC CONTEXT**. Show **SEARCHING…** | Watch it run live. One credit per uncached query. **[beat]** |
| 1:03 | Scroll down to **THREAT BRIEF · TAVILY RESEARCH**. | And this is the fifth primitive. Research. |
| 1:09 | Point at **THE QUESTION PUT TO THE OPEN WEB**. | Search finds documents. Research answers a question. |
| 1:15 | Point at the brief and its sources list. | It ran several searches on its own and wrote this brief, with sources. |
| 1:22 | Point at the words **context only, never evidence**. | Now the line we never cross. **[beat]** |
| 1:28 | Hold. | Everything Tavily returns is labelled context. Never evidence. |
| 1:34 | Click any claim in **NARRATOR · EVERY CLAIM CARRIES ITS LINE**. Show the yellow chip. | A verdict claim must quote the bank's own log line. Not a web page. |
| 1:41 | Click **COMPLIANCE**. Wait. Scroll left column to **REGULATORY GUIDANCE · TAVILY**. | Same discipline on the regulator's form. Tavily fetches CERT-In and DPDP guidance. |
| 1:49 | Click **READ FULL TEXT · TAVILY EXTRACT**. | Extract brings the full guidance text to the signer. |
| 1:55 | Click **CONNECTORS**. Point at the **tavily** row and **web search**. | Five Tavily primitives. One egress door. Zero evidence laundering. That is best use. |

**Voice word count: about 265.**

## Why this meets the track, criterion by criterion

| Tavily asks for | CITINEL shows |
|---|---|
| Integrate Tavily APIs | All five primitives: Search with `include_answer`, Extract, Map, Crawl, Research with async polling. `primitives_used` is recorded per gather from what actually ran. |
| Real-time search, AI retrieval, knowledge augmentation | Live gather on camera. Research brief answering a question. ATT&CK sub-techniques mapped live. Regulatory guidance fetched for the signer. |
| Creative and impactful | Tavily output is tagged `not_evidence` in the payload. No verdict, lane or gate decision can bind to it. Web context informs the analyst but can never forge a citation. |

## If something goes wrong

- **REQUEST THREAT BRIEF** still reads **RESEARCHING…**: skip to 1:22. Say "the brief is still running; Research is asynchronous by design."
- **GATHER** returns an error: say "the gather degraded to not configured and the screen says so." Continue.

---

# VIDEO 2 · LYZR · Best Use of Lyzr AI Award

## The one sentence

*Seven Lyzr agents check CITINEL's own agents from outside, and one of them
guards the ledger against an attack the ledger cannot see.*

## Before this take

1. Open Lyzr Studio in a second browser tab. Sign in.
2. On the Studio **Home**, confirm all seven agents are listed by name.
3. Confirm credits are not near zero. Top up if under two.
4. In CITINEL, open **AUDIT** and scroll to the witness line. It should read **agreed** or **lagging**.
5. Open **COMPLIANCE** for INC-0419 once. Wait 20 seconds. Warm.
6. Return to **CONNECTORS**. Start recording there.

## The take

| Time | CAMERA does | VOICE says |
|---|---|---|
| 0:00 | Show **CONNECTORS**. Scroll to the seven rows starting **lyzr**. | CITINEL runs twelve AI agents across two vendors. |
| 0:06 | Point at each: **lyzr**, **lyzr-triage**, **lyzr-review**, **lyzr-handover**, **lyzr-verdict**, **lyzr-response**, **lyzr-corpus**. | Seven are Lyzr. Each one has its own job. |
| 0:14 | Hold on the rows. | Not seven prompts against one endpoint. Seven Studio agents. Seven ids. |
| 0:20 | Switch to the Lyzr Studio tab. Show **Home** with the agent list. | Here they are in Lyzr Studio. |
| 0:26 | Point at **CITINEL Triage Second Opinion**, then **CITINEL Verdict Auditor**. | Triage Second Opinion. Verdict Auditor. Draft Reviewer. Handover Writer. |
| 0:33 | Point at **CITINEL Response Reviewer**, **CITINEL Corpus Advisor**, **CITINEL Compliance Monitor**. | Response Reviewer. Corpus Advisor. And the Compliance Monitor, which is also the witness. |
| 0:40 | Click one agent. Click the **Deploy** tab. Show **Agent API**. | Each is called through the Agent API. Each id lives in one environment variable. |
| 0:47 | Switch back to CITINEL. Click **REPLAY** for INC-0417. Scroll right column to the panel starting **LYZR**. | Why a second vendor at all. **[beat]** |
| 0:54 | Point at **independent triage · lane escalate · confidence** and the **AGREES** tag. | A checker inside the system shares its blind spots. Independence is the point. |
| 1:01 | Hold. | Here Lyzr triaged the incident beside our own router. Both go on the ledger. |
| 1:07 | Click **COMPLIANCE**. Wait. Scroll to a field tagged **LYZR · THIN**. | On the regulator's form, the Lyzr Draft Reviewer reads every field before a human signs. |
| 1:15 | Point at the text beginning **lyzr review:** | It flags a thin field. It never fills one in. |
| 1:21 | Scroll to the guard box. Point at the sentence ending **the Lyzr second opinion.** | Personal data is checked twice. Our deterministic guard, and Lyzr, independently. |
| 1:28 | Click **AUDIT**. Scroll to the witness line. | Now the part the ledger cannot do alone. **[beat]** |
| 1:35 | Point at **witness** and its status, **agreed**. | Our hash chain catches edits. It cannot catch a whole file swapped out. |
| 1:42 | Hold. | So the Lyzr Compliance Monitor holds the head hash remotely. Substitution shows as diverged. |
| 1:49 | Click **CORPUS**. Point at **COVERAGE ADVISORY · LYZR**. | And the Corpus Advisor reviews detection coverage. One call. Advisory only. |
| 1:55 | Click **CONNECTORS** again. Hold on the seven rows. | Seven agents. Seven jobs. They advise and witness. They never gate. That is best use. |

**Voice word count: about 275.**

## Why this meets the award

| Lyzr asks for | CITINEL shows |
|---|---|
| Build AI agents on the Lyzr platform | Seven Studio agents, each with its own Role, Goal and hardened Instructions. Recipes in `LYZR-AGENT-CONFIG.md`. |
| Deploy and integrate into the project | Each called via the Agent API through `connectors/lyzr_agents.py`, host added to the egress allow-list only when configured. All seven `configured=true` on the live deployment. |
| Innovative solution | The ledger witness: an external agent holding the chain head so wholesale replacement is detectable, which `verify_chain` structurally cannot do. And adversarial second opinions that were stricter than the pipeline five times on 4 September. |
| Production readiness | Every seam degrades to `not_configured` or `unavailable` honestly. No agent can block an action. The gate is code. |

## If something goes wrong

- Witness reads **unavailable**: say "Lyzr Studio is not answering right now, and we report that rather than assume agreement." Continue.
- A **LYZR · THIN** tag is absent: point at the top-left line beginning **Lyzr draft review:** instead.
- Studio credits are exhausted: skip the Studio tab entirely. Everything else still shows.

---

# VIDEO 3 · SWYTCHCODE · Best Use of Swytchcode track

## The one sentence

*Swytchcode is the hand that carries out an approved action, under a policy
that can stop it even after the AI gate said yes.*

## Before this take

1. Optional but strongly recommended: renew the Slack session **within four hours** of recording. Steps are in `RUNBOOK-NEW-LAPTOP.md` section 2c. Without it, the comms leg reads `not_configured` and the script has a line for that.
2. Open a terminal in the repo. Run `nvm use 20`. Run `swy --version`. It prints 2.20.15.
3. Keep the terminal open in a second window, font size large.
4. In CITINEL, open **APPROVALS**. Pick a card for **INC-0416** that reads **AUTONOMOUS**, for example **enrich_ioc**.
5. Do not arm the key yet. Start recording on **CONNECTORS**.

**This take creates a real GitHub issue in your repository. That is the proof.**

## The take

| Time | CAMERA does | VOICE says |
|---|---|---|
| 0:00 | Show **CONNECTORS**. Point at **OUTLETS · WHAT CITINEL CAN ACTUALLY TOUCH**. | CITINEL proposes response actions. It never runs them by itself. |
| 0:07 | Point at the badge **EVERY OUTLET IS BLANKED**. | Every endpoint here is simulated. The bank's systems are never touched. |
| 0:13 | Switch to the terminal. Type `swy --version`. Press Enter. | This is the Swytchcode CLI. Version two point twenty. Built into our image. |
| 0:20 | Type `swy policy list`. Press Enter. | Three Swytchcode policies. Written by us. Validated by the CLI. |
| 0:27 | Open `.swytchcode/integrations/policies.json`. Point at the three ids. | No core banking name in a ticket. No message without a destination. No ticket without its incident. |
| 0:35 | Open `.swytchcode/tooling.json`. Point at **GitHub.github** and **Slack.slack**. | Two ecosystem APIs. GitHub for tickets. Slack for comms. |
| 0:42 | Switch to CITINEL. Click **APPROVALS**. Click the **INC-0416 · enrich_ioc** card. | Now the workflow. **[beat]** A Claude agent proposed this action. |
| 0:49 | Point at **GOVERNING CLAUSE**. | The policy gate adjudicated it against a named clause. |
| 0:55 | Click **EXPAND DECISION TRACE**. Scroll to **INTENT PREVIEW**. | Before firing, the intent is spelled out. |
| 1:01 | Point at the line **hand the executed action to Swytchcode ticketing + comms**. | And the last line says who carries it out. Swytchcode. |
| 1:07 | Point at **WILL NOT DO**. | And what it must never do. |
| 1:12 | Click the key dial **KEY SAFE**. Show **KEY ARMED**. | Two steps to fire. Deliberately. |
| 1:17 | Click **APPROVE AND FIRE**. Wait for the receipt. | Watch the chain. Gate, then Swytchcode policy, then the API. **[beat]** |
| 1:25 | Point at the receipt line beginning **swytchcode:** | Ticketing executed. A real issue, through the Python runtime. |
| 1:31 | If it reads **comms executed**, point at it. If it reads **not_configured**, point at it. | *(if executed)* Comms executed. Slack notified. *(if not)* Comms reports not configured. The ledger says so rather than claiming a send. |
| 1:39 | Switch to a browser tab on `github.com/agdanish/CITINEL/issues`. Show the newest issue. | Here is the ticket. Title, incident id, the governing clause. Created by Swytchcode. |
| 1:47 | Point at the title, **[CITINEL] enrich_ioc on** the target. | Swytchcode's own argument is that API success is not correct behaviour. |
| 1:53 | Switch back. Click **FIND IT IN THE LEDGER**. Show the two **swytchcode** frames. | So its policy runs after our gate approves. A second guard, outside the agent's own reasoning. That is best use. |

**Voice word count: about 280.**

## Why this meets the track, requirement by requirement

| Swytchcode requires | CITINEL shows |
|---|---|
| Build with the Swytchcode CLI | `swy` 2.20.15 installed in `deploy/Dockerfile.web`. Policies validated with `swy policy validate`. Bundles committed. |
| Python or TypeScript runtime | `swytchcode-runtime` from PyPI, wired in `connectors/swytchcode_runtime_transport.py`. |
| At least two external ecosystem APIs | `github.issue.create` and `slack.chat.postmessage.create`, both registered in `tooling.json`. GitHub proven live: issue `agdanish/CITINEL#1` on ledger frame 5795. |
| An AI-powered workflow or agent | Claude Marshal proposes, OPA gate adjudicates, Swytchcode policy checks, API executes. Twelve AI agents upstream of the transport. |
| Functional end-to-end | Approve on screen, receipt on screen, issue on GitHub, frames on the ledger. Reproducible on camera. |

## The honest line on Slack

The Slack credential never expires. The login session that unlocks it lasts four
hours and nothing renews it. If the session is fresh, comms executes on camera.
If not, the receipt reads `not_configured` and the ledger refuses to claim a
send. Both outcomes are the control working. Say whichever one is on screen.

## If something goes wrong

- **APPROVE AND FIRE** is greyed: the key is not armed. Click the dial again.
- Receipt reads **policy_blocked**: that is a Swytchcode policy refusing after the gate approved. Say "a blocked action is the guardrail working." It is the strongest possible moment.
- GitHub page shows no new issue: refresh once. The receipt carries the issue URL in the ledger frame.

---

# The three sentences that close each video

- **Tavily.** "Five primitives, one egress door, zero evidence laundering."
- **Lyzr.** "Seven agents that advise and witness, and never gate."
- **Swytchcode.** "A second guard that can stop an action after the AI said yes."

Each is true, checkable on the live deployment, and phrased as what the system does, not what it hopes to win.
