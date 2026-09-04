# Next session prompt (written 4 Sep 2026, evening, for a NEW Claude Code account)

You are picking up CITINEL, an autonomous glass-box AI Cyber SOC for Indian
cooperative banks, the night before the Decode SIH 2026 grand finale (5 Sep).
The previous account's weekly limit ran out; nothing from that chat is in your
context. Everything you need is in this repository.

## Read, in this order (fifteen minutes)
1. `docs/SESSION-2026-09-03-04-FINDINGS.md`: state, every bug and fix with commit hashes, the eleven services and how each was proven, what is pending.
2. `RUNBOOK-NEW-LAPTOP.md`: how a laptop is armed before any write works; demo-day rules.
3. `HANDOFF-MEMORY.md` §21 and §22, then earlier sections only as needed.
4. `docs/MEMORY-EXPORT.md`: Claude's memory. On this Mac the memory directory already exists at `/Users/danish/.claude/projects/-Users-danish-CITINEL/memory/` and loads by itself; on another machine, restore it as that file says.
5. `docs/SESSION-2026-09-03-04-CHAT-LOG.md` only when you need the exact wording of something; it is the whole chat.

## Ground truth before believing any of it
```bash
git log --oneline -5 && git status --porcelain
curl -s https://citinel-web.onrender.com/healthz
curl -s https://citinel-web.onrender.com/api/connectors | python3 -c "import json,sys; c=json.load(sys.stdin)['connectors']; print(sum(x['configured'] for x in c),'of',len(c),'configured')"
cd backend && .venv/bin/python -m pytest -q | tail -1      # 414 passing at handoff; use the venv, system python is 3.9
```

## First tasks
1. Ask Danish whether Part 3 of the runbook finished on 4 Sep evening and what the Approvals receipt line said. If it said `comms executed` with a `ts`, Slack on Render is proven; if it named a reason, fix that first.
2. Push the two unpushed commits (`9152bd5`, `5f687ba`) once nothing is running in production: `git push origin build/stage-1`. Every push deploys and restarts the service.
3. Verify production from outside: `python3 scripts/preflight.py` (read-only, prints GO or the exact problems), then the probes in the findings doc §2 and §10.
4. Make sure Auto-Deploy is OFF on the four Render services before the demo (Danish's step; ask).
5. Demo morning: Danish arms the demo laptop (runbook part A). Check the green dot in the rail. Do not run the swarm on stage unless scripted.

## How Danish works
No em dashes in anything you write. Baby steps for every manual action, one action per line. Do not over-complicate. Be brutally honest; never guarantee a judged prize. Verify against real data, not by reading code. Haiku for subagents by default; ask before Sonnet or Opus. Do not bring up the pitch deck unprompted. Render secrets are Danish's to set; never handle credential values.

## Do not
- Do not fabricate a metric, count or name. The false-positive rate is unmeasured; sign-offs are drafts; response actions hit simulated endpoints.
- Do not spend Anthropic credits (a swarm run) or Render resources without asking.
- Do not sign off an incident on the live ledger for a test without reopening it after.
- Do not push while Danish may be mid-way through a production run.
