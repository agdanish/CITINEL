# 🛡️ CITINEL — Autonomous Cyber SOC

> **The SOC that shows its evidence, obeys your policy, and beats the clock.**

CITINEL (**CITE** + **SENTINEL**) is an autonomous Security Operations Center where Claude-powered agents investigate every alert with **cited evidence**, act only inside a **per-action policy humans can read**, and draft India's mandatory **CERT-In 6-hour report** and **DPDP breach artifacts** the moment an incident is confirmed.

Built for **Decode SIH 2026** · Track 3 *Bharat Pragati* · **PS4: "Autonomous Cyber SOC for AI-powered threat detection and automated incident response."**

---

## Why

In 2024, one ransomware attack took **~300 Indian cooperative banks offline**. RBI requires them to run a 24×7 SOC; a human one costs **₹1–2 crore a year** against budgets of **₹25k–₹1L a month**. India's average breach now costs a record **₹220M** (IBM, 2025) — while a 6-hour CERT-In clock and DPDP's stackable **₹250cr + ₹200cr** penalties tick over every incident.

**The gap CITINEL closes:** SIEMs know what happened but don't write the regulator's form. Compliance tools write forms but don't know what happened. CITINEL is the only system where **the investigation itself writes the draft** — detection to regulator-ready report, one pipeline.

## What it does

| # | Feature | In one line |
|---|---|---|
| 1 | **Glass-box cited triage** | Sigma rules catch known threats deterministically; Claude agents correlate the rest into a MITRE ATT&CK kill-chain narrative where every verdict cites the exact log line proving it |
| 2 | **Readable autonomy dial** | Per-action-class OPA policy: enrichment runs automatically, isolation runs with rollback, consequential actions wait for one-click human approval — Shadow → Assist → Autonomous, with blast-radius rings |
| 3 | **Injection-hardened pipeline** | All log content is quarantined as untrusted data — a poisoned log cannot hijack the AI (attack-vs-defense demo included) |
| 4 | **Compliance clock** | On confirmation, CERT-In 6-hour and DPDP breach drafts are generated from the live incident record for human sign-off |

## Architecture (summary)

```
Telemetry (syslog/webhook · BOTS replay) → OCSF normalizer → Sigma engine + anomaly scoring
        → Agent swarm: Sentinel (orchestrator) · Triage Router · Enrichment Squad
          · Correlator · Verdict Narrator · Response Marshal · Scribe
        → OPA policy gate + autonomy dial → simulated response endpoints
        → Append-only audit log → Compliance drafter → Glass-box dashboard
```

Full spec: **`docs/CITINEL-MASTER-KB.md` §2** (agent roles, safety design, evidence pack, fallback ladder).

## Repo structure

```
citinel/
├── ppt/        # Round-1 ideation deck (official Decode SIH template, PDF)
├── docs/       # Single source of truth — read CITINEL-MASTER-KB.md first
│   ├── CITINEL-MASTER-KB.md      # Everything: hackathon facts, locked idea spec, rubric
│   ├── CITINEL-STATE.md          # Live state file (emitted by the orchestrator)
│   ├── A1-market-impact.md       # India threat & market evidence
│   ├── A2-competition.md         # Competitive landscape & white-space
│   ├── A3-technical.md           # Architecture & feasibility research
│   ├── A4-winning-ideas.md       # SIH evaluation intelligence
│   ├── A5-analyst-ux.md          # SOC analyst workflow & UX research
│   ├── A6-compliance.md          # CERT-In / DPDP deep dive
│   └── orchestrator-phase0-4.md  # Idea tournament + red-team record
└── (build)     # backend/ · dashboard/ · policies/ · connectors/ — per KB §2.5
```

## Demo & data

License-clean and simulation-only: **Splunk BOTS** (CC0) telemetry replay, **Atomic Red Team** (MIT) in an isolated VM, response actions against mocked endpoints. No production systems are ever touched.

## Team

Decode SIH 2026 entry · Chennai Institute of Technology.
Evaluated on the MIC/AICTE SIH rubric: novelty · technical complexity · clarity & format · feasibility · practicability · sustainability · scale of impact · user experience · future progression.

---

*CITINEL drafts regulator reports; humans review and file them. Detection targets and false-positive rates are measured on labeled datasets and reported as ranges — never claimed.*

## Session records (continuity across Claude Code accounts)

| File | What it is |
|---|---|
| `SESSION-2026-09-03-04-FINDINGS.md` | every bug, fix, decision, proof and pending item from 3 to 4 Sep 2026, with commit hashes; read this first |
| `SESSION-2026-09-03-04-CHAT-LOG.md` | the complete chat of that session, every user and Claude turn, credentials redacted |
| `MEMORY-EXPORT.md` | Claude Code's persistent memory for this project, with restore steps |

`../scripts/preflight.py` is the read-only GO/NO-GO check for the live console. The next-session entry point is `../NEXT-SESSION-PROMPT.md`; the team procedure for a new laptop is `../RUNBOOK-NEW-LAPTOP.md`.

