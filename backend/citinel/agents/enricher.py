"""The Enricher: turns indicators into context via a real tool-use loop.

Deliberately a different shape from the other four agents. Router,
Correlator, Narrator and Marshal each make one structured-output call
(`Transport.parse`) -- ask a question, get back a validated object. The
Enricher's job is different in kind: decide WHICH indicators in the evidence
are worth looking up, call the right allow-listed connector for each, read
what came back, and stop when there is nothing left worth checking. That is
a tool-use conversation, not a single Q&A -- multiple turns, model-driven,
bounded so a model that keeps requesting tools cannot hang the pipeline.

Citation integrity is deliberately NOT extended to cover enrichment results.
`contracts.Citation` cites `incident.findings` by index, and that contract
has already been through adversarial review; widening it to also cite
external lookups is a bigger, riskier change than this pass takes on. Instead
the Enricher's findings become one more quarantined evidence block --
exactly the same pattern `pipeline.correlator_summary_evidence` already uses
for the Correlator's own output -- so Correlator and Narrator can read and
reason about them, but every CLAIM a human sees still traces back to a real
finding in the incident record, never to an enrichment lookup. Enrichment
informs; it does not become the citable evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from citinel.agents.quarantine import Provenance, TaintedText, quarantine
from citinel.agents.transport import AgentCall
from citinel.connectors.base import EnrichmentCache
from citinel.connectors.enrichment import EnrichmentSquad

#: Circuit breaker. A model that never stops requesting tools is a routine
#: failure mode to guard against, not a hypothetical -- the loop below has no
#: other exit condition besides "the model stopped asking for tools".
MAX_TOOL_ITERATIONS = 6

TOOLS: list[dict[str, Any]] = [
    {
        "name": "check_ip",
        "description": "VirusTotal + AbuseIPDB reputation for one IP address "
                       "that actually appears in the evidence.",
        "input_schema": {
            "type": "object",
            "properties": {"ip": {"type": "string", "description": "e.g. 185.151.160.15"}},
            "required": ["ip"],
        },
    },
    {
        "name": "check_hash",
        "description": "VirusTotal reputation for one file hash that actually "
                       "appears in the evidence.",
        "input_schema": {
            "type": "object",
            "properties": {"file_hash": {"type": "string", "description": "a SHA-256 hash"}},
            "required": ["file_hash"],
        },
    },
    {
        "name": "search_context",
        "description": "Real-time OSINT search for public context on a technique, "
                       "campaign, or indicator (Tavily).",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
]


@dataclass
class EnrichmentRun:
    """Everything one Enricher pass produced, including what it never used."""

    calls: list[AgentCall] = field(default_factory=list)
    lookups: list[dict[str, Any]] = field(default_factory=list)
    stopped_reason: str = ""
    evidence: TaintedText | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "call_count": len(self.calls),
            "lookups": self.lookups,
            "stopped_reason": self.stopped_reason,
        }


def _execute(squad: EnrichmentSquad, name: str, tool_input: dict[str, Any]) -> tuple[str, list[dict]]:
    """Run one tool call for real, against the real connectors.

    Returns (text for the tool_result block, raw EnrichmentResult dicts for
    the ledger). Never raises: an unknown/malformed tool call becomes a
    tool_result the model can read and correct from, not a crashed pipeline --
    the same "routine outcome, not broken plumbing" standard transport.py
    applies to refusals.
    """
    try:
        if name == "check_ip":
            results = squad.enrich_ip(str(tool_input["ip"]))
        elif name == "check_hash":
            results = squad.enrich_hash(str(tool_input["file_hash"]))
        elif name == "search_context":
            results = squad.enrich_context(str(tool_input["query"]))
        else:
            return f"unknown tool {name!r}", []
    except (KeyError, TypeError) as e:
        return f"malformed arguments for {name}: {e}", []

    dicts = [r.as_dict() for r in results]
    lines = []
    for r in results:
        if r.status == "not_configured":
            lines.append(f"{r.provider}: not configured, skipped")
        elif r.status != "ok":
            lines.append(f"{r.provider}: {r.status} -- {r.verdict or 'no detail'}")
        else:
            lines.append(f"{r.provider}: {r.verdict}"
                         + (f" (score {r.score})" if r.score is not None else "")
                         + f" [{r.source_url}]")
    return "\n".join(lines) or "no results", dicts


def run_enricher(
    transport: Any,
    squad: EnrichmentSquad,
    *,
    system: str,
    instruction: str,
    evidence: Sequence[TaintedText],
    case_id: str,
) -> EnrichmentRun:
    """Drive the tool-use conversation to completion, or to the iteration cap.

    `transport` supplies the verified client/model (Transport's own fields --
    duck-typed rather than importing Transport, so this stays testable
    against a fake with the same shape). Every turn is recorded as an
    AgentCall for the ledger, matching how the other four agents' single
    calls are recorded -- multi-turn here just means multiple AgentCalls
    under the same agent name.
    """
    run = EnrichmentRun()
    blocks, provenance = transport.user_blocks(instruction, evidence)
    messages: list[dict[str, Any]] = [{"role": "user", "content": blocks}]

    for _ in range(MAX_TOOL_ITERATIONS):
        response = transport.client.messages.create(
            model=transport.model.model_id,
            max_tokens=transport.max_tokens,
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=messages,
            tools=TOOLS,
        )
        stop_reason = getattr(response, "stop_reason", None)
        content = getattr(response, "content", None) or []
        usage = getattr(response, "usage", None)

        call = AgentCall(
            agent="enricher", model_id=transport.model.model_id, role=transport.model.role,
            stop_reason=stop_reason,
            input_tokens=getattr(usage, "input_tokens", 0) if usage else 0,
            output_tokens=getattr(usage, "output_tokens", 0) if usage else 0,
            refused=(stop_reason == "refusal"),
            fenced_provenance=provenance,
        )
        run.calls.append(call)

        if stop_reason == "refusal":
            run.stopped_reason = "model refused"
            break

        tool_uses = [b for b in content if getattr(b, "type", None) == "tool_use"]
        if not tool_uses:
            run.stopped_reason = f"stop_reason={stop_reason!r}, no further tool calls"
            break

        # The assistant turn (including its tool_use blocks) must be replayed
        # verbatim before the tool_result turn -- the API requires the full
        # prior turn, not just a summary of it.
        messages.append({"role": "assistant", "content": content})

        result_blocks = []
        for tu in tool_uses:
            name = getattr(tu, "name", "")
            tool_input = getattr(tu, "input", {}) or {}
            text, dicts = _execute(squad, name, tool_input)
            run.lookups.append({"tool": name, "input": tool_input, "results": dicts})
            result_blocks.append({
                "type": "tool_result",
                "tool_use_id": getattr(tu, "id", ""),
                "content": text,
            })
        messages.append({"role": "user", "content": result_blocks})
    else:
        run.stopped_reason = f"hit the {MAX_TOOL_ITERATIONS}-iteration cap"

    if run.lookups:
        summary = "\n\n".join(
            f"tool={l['tool']} input={l['input']}\n" + "\n".join(
                f"  {r.get('provider')}: {r.get('verdict') or r.get('status')}"
                for r in l["results"]
            )
            for l in run.lookups
        )
        run.evidence = quarantine(
            summary,
            Provenance(source="enricher-agent-output", event_class="enrichment",
                      timestamp="", detail=f"enricher-summary:{case_id}"),
        )
    return run
