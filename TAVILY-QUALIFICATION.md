# CITINEL × Tavily — qualification dossier

*Written 4 Sep 2026. This track published its criteria, so this dossier maps
each one directly.*

> **To qualify, teams must:** integrate Tavily APIs into their project · use
> real-time web search, AI retrieval, or knowledge augmentation · demonstrate a
> creative and impactful implementation

---

## Criterion 1 — Integrate Tavily APIs

**All five of Tavily's primitives**, each used where it earns its place rather
than to raise a count:

| Primitive | Endpoint | What it does here |
|---|---|---|
| **Search** | `/search` | every planned query, with `include_answer` so Tavily's own synthesis returns too |
| **Extract** | `/extract` | the regulatory source's full page text, so a reader gets the actual CERT-In/DPDP wording inline rather than a link they may never open |
| **Map** | `/map` | the ATT&CK page read as taxonomy — which sub-technique pages MITRE publishes *right now*, live, instead of a hardcoded list that goes stale |
| **Crawl** | `/crawl` | that technique page **and the pages it links to**, as full text — where Extract reads one page, Crawl reads a neighbourhood |
| **Research** | `/research` | the only primitive that answers a *question* rather than returning pages |

Map and Crawl run for the **first technique query only**, so the added cost is
a fixed +2 calls per gather no matter how many techniques a run found. The
persisted payload records `primitives_used` from what actually happened, not
from what is possible.

**A real bug this found.** The code read `body["answer"]` without ever sending
`include_answer`. Tavily only returns that field when asked, so Tavily's own
synthesised answer was silently absent from every query the product had ever
run. Fixed.

## Criterion 2 — Real-time web search, AI retrieval, knowledge augmentation

All three, and they are genuinely different things here:

- **Real-time web search** — four query kinds planned from the *persisted
  verdict*, not from a static list: `technique`, `rule`, `regulatory`,
  `campaign`. The campaign query fires only when two or more distinct
  techniques were correlated, because a campaign question is meaningless for
  one technique.
- **AI retrieval** — Extract and Crawl pull full document text, and Research
  runs several searches of its own and reasons across them.
- **Knowledge augmentation** — the retrieved regulatory text is rendered
  *inline on the Compliance desk*, next to the draft it governs. A compliance
  officer reads the actual wording without leaving the console.

## Criterion 3 — Creative and impactful

**The creative part is the Research brief.** Search finds documents about a
technique. Research answers the question a CISO actually asks, built from what
the investigation found rather than from an incident id:

> *"A SOC at an Indian cooperative bank has an incident showing these MITRE
> ATT&CK techniques together: … The detections that fired were: … What attack
> pattern does this combination typically indicate, what do incident responders
> who have handled it recommend doing first, and what should this bank check
> for that it may not have looked at yet? Cite your sources."*

It is asynchronous by design: started, then advanced one poll per call. Nothing
holds an HTTP worker open waiting for a research run, because that would put
the console's own timeout in charge of whether the answer is allowed to exist.

**The impactful part is where it lands.** Tavily output is not a sidebar. The
regulatory text sits on the Compliance desk beside the CERT-In draft; the
technique context sits on Replay beside the verdict; every result carries its
query, its URL and its fetch time in an `ExternalCitationChip`.

**And a line it never crosses.** Everything Tavily returns is labelled
`not_evidence` in the payload itself. A claim's citation still points only at
`Citation.finding_index` into the incident's own findings. Tavily makes the
verdict *readable*; it can never make it *true*. For a product whose whole
thesis is cited evidence, an OSINT result quietly becoming support would
undermine the thing it exists to prove.

## Where to look

| Claim | Check |
|---|---|
| the connector, all five primitives | `backend/citinel/connectors/enrichment.py` |
| query planning + provenance | `backend/citinel/agents/context.py` |
| the Research brief | `backend/citinel/agents/brief.py`, `test_tavily_research.py` (6 tests) |
| gathered context, live | `GET /api/incidents/INC-0417/context` |
| on screen | Replay → "PUBLIC CONTEXT · TAVILY"; Compliance → "REGULATORY GUIDANCE · TAVILY" |

## Honest limits — read this before demoing

**`CITINEL_TAVILY_API_KEY` is not set on the live deployment.** Every Tavily
surface therefore reports `not_configured` in production right now: all five
primitives, all four query kinds, both screens. The code is complete, deployed
and tested; the key is the only thing missing, and it is the single
highest-value thing outstanding on any track.

*(The seed corpus ships with context already gathered for INC-0416 and
INC-0417, so the Replay panel has real data to show. But a live gather, and
anything on the Compliance desk, needs the key.)*

- Credits are real: one per uncached query, plus the fixed +2 for Map and Crawl
  on a gather, plus one Research run. The enrichment cache answers repeats.
- Research is async; a brief may read `pending` on first load and needs a
  second look. That is the API's shape, not a defect.
- No Tavily result is evidence. This is deliberate and permanent.
