"""The single place CITINEL talks to a model. Everything else goes through it.

Concentrating every API call here buys four things that matter to this build:

* **Refusals AND truncation are handled, not ignored.** CITINEL feeds attacker
  telemetry -- ransomware command lines, credential-dumping traces, injection
  payloads -- to a safety-trained model. `stop_reason: "refusal"` with a cyber
  category is a realistic, expected outcome for this workload, not an exotic
  edge case, and a large fenced-evidence prompt can legitimately truncate at
  `max_tokens`. This module checks `stop_reason` BEFORE attempting to parse
  anything as the expected schema -- the SDK's own `messages.parse()` helper
  does not do this (it runs `TypeAdapter.validate_json()` unconditionally on
  every text block, which raises `pydantic.ValidationError` on a refusal's
  plain-language decline or on truncated JSON, before this module ever sees a
  response object). That failure mode was caught by adversarial review of this
  file's first draft; `client.beta.messages.create()` plus a stop-reason-gated
  manual parse is what actually delivers "never raises on refusal", not
  `.parse()`.

* **The audit ledger stays forensic.** AGT-F06: thinking summaries are a
  summary, not a record. `AgentCall` carries no reasoning text, and
  `ledger_payload()` is the only thing written to the ledger -- decisions and
  tool calls, never narrative.

* **Untrusted content cannot reach a prompt unfenced.** `user_blocks` accepts
  `TaintedText`, and fences it. Passing a bare `str` of log content is a type
  error at the call site rather than a silent injection surface.

* **Ledger rule L9 is unavoidable.** The constructor takes a `VerifiedModel`,
  which can only be produced by a live check against `GET /v1/models`. There
  is no code path that sends a model id this process has not confirmed.

Effort and adaptive thinking are REASONING-role-only (`EFFORT_BY_ROLE` has no
TRIAGE entry). `output_config.effort` and `thinking: {"type": "adaptive"}` are
4.5+/4.6+-generation features; the documented triage recommendation in
`models.py` is `claude-haiku-4-5`, which accepts neither, and sending them
unconditionally to whatever model an operator configures for the cheap
high-volume role is a request-shape error the API returns as a 400 -- caught
by adversarial review, not by assumption. The reasoning role's model
(`claude-opus-5` by documented recommendation) supports both.

Not yet exercised against the live API: no Anthropic key exists in this repo
yet (Step 7's blocker). `tests/test_agents_scaffold.py` drives every branch
here -- refusal, truncation/no-text, malformed JSON, and success -- through a
fake client that returns response shapes matching the installed SDK's actual
types, so the control flow is tested even though the live wire format is not;
the first real run must still confirm that.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence, TypeVar

from anthropic import transform_schema
from pydantic import BaseModel

from citinel.agents.models import Role, VerifiedModel
from citinel.agents.quarantine import TaintedText, fence

T = TypeVar("T", bound=BaseModel)

#: Effort applies to the reasoning role only -- see module docstring. A role
#: with no entry here gets no `output_config.effort` and no `thinking` param.
EFFORT_BY_ROLE: dict[Role, str] = {
    Role.REASONING: "high",
}

#: Beta flag for server-side refusal fallbacks (scalar "default" form).
FALLBACK_BETA = "server-side-fallback-2026-07-01"

#: stop_reason values that mean "a full, schema-valid answer is expected and
#: present". Anything else (refusal, max_tokens, pause_turn, tool_use without
#: a final answer, ...) means don't attempt to validate the text as the
#: output schema -- doing so on a decline or a truncated response is exactly
#: what raised ValidationError out of the SDK's own parse() helper.
_COMPLETE_STOP_REASONS = frozenset({"end_turn", "stop_sequence"})


@dataclass
class AgentCall:
    """The record of one model call. Structured facts only -- no reasoning text.

    This is what the ledger sees. Deliberately missing: any field that could
    carry a thinking summary or free-form model narrative into a forensic
    record (AGT-F06). `parsed` is `None` whenever a schema-valid answer is not
    available for ANY reason -- refused, truncated, no text block, or text
    that failed schema validation -- `unusable_reason` says which.
    """

    agent: str
    model_id: str
    role: Role
    stop_reason: str | None
    input_tokens: int = 0
    output_tokens: int = 0
    refused: bool = False
    refusal_category: str | None = None
    served_by: str | None = None      # set when a refusal fallback actually ran
    request_id: str | None = None
    parsed: Any = None
    unusable_reason: str | None = None  # why parsed is None, when not a refusal
    fenced_provenance: list[str] = field(default_factory=list)

    @property
    def usable(self) -> bool:
        """True only when `parsed` is a validated instance of the output schema."""
        return not self.refused and self.parsed is not None

    def ledger_payload(self) -> dict[str, Any]:
        """Exactly what gets appended under the `tool_call` entry kind."""
        return {
            "agent": self.agent,
            "model_id": self.model_id,
            "role": self.role.value,
            "stop_reason": self.stop_reason,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "refused": self.refused,
            "refusal_category": self.refusal_category,
            "served_by": self.served_by,
            "request_id": self.request_id,
            "usable": self.usable,
            "unusable_reason": self.unusable_reason,
            "evidence_provenance": self.fenced_provenance,
        }


class Transport:
    """Wraps one verified model. One instance per role, reused across agents."""

    def __init__(
        self,
        client: Any,
        model: VerifiedModel,
        *,
        max_tokens: int = 16000,
        use_refusal_fallback: bool = True,
    ) -> None:
        self.client = client
        self.model = model
        self.max_tokens = max_tokens
        self.use_refusal_fallback = use_refusal_fallback

    # -- prompt construction -------------------------------------------------

    @staticmethod
    def user_blocks(
        instruction: str,
        evidence: Sequence[TaintedText] = (),
    ) -> tuple[list[dict[str, str]], list[str]]:
        """Build the user turn. Evidence is fenced; instruction never is.

        Returns the content blocks and the provenance labels of everything
        fenced, so the caller can record which evidence a call actually saw.

        The type signature is the safeguard: `evidence` is `TaintedText`, so
        raw log content -- or anything else attacker-influenceable -- cannot
        be concatenated into a prompt by accident. It arrives wrapped or it
        does not arrive.
        """
        blocks: list[dict[str, str]] = [{"type": "text", "text": instruction}]
        provenance: list[str] = []
        for t in evidence:
            if not isinstance(t, TaintedText):
                raise TypeError(
                    "evidence must be TaintedText -- log content (and anything "
                    "derived from it, like a finding title) reaches a prompt "
                    "through the quarantine plane or not at all"
                )
            blocks.append({"type": "text", "text": fence(t)})
            provenance.append(t.provenance.label())
        return blocks, provenance

    # -- the call ------------------------------------------------------------

    def parse(
        self,
        *,
        agent: str,
        system: str,
        instruction: str,
        output_format: type[T],
        evidence: Sequence[TaintedText] = (),
    ) -> AgentCall:
        """One structured call. Returns an AgentCall; never raises on refusal
        or on a truncated/unparsable response.

        A refusal, a truncation, or a malformed answer is a result, not an
        exception: the pipeline needs to record it, degrade, and carry on.
        Transport failures (network, auth, a retired model) do raise -- those
        are broken plumbing, not results.

        Deliberately does NOT use `client.messages.parse()` / the beta
        equivalent: that helper validates every text block against
        `output_format` unconditionally, before returning, which raises
        `pydantic.ValidationError` out of the SDK itself on a refusal or a
        `max_tokens` truncation. Calling `.create()` and checking `stop_reason`
        first is what actually makes "never raises" true.
        """
        blocks, provenance = self.user_blocks(instruction, evidence)
        # transform_schema (not a bare model_json_schema()) is what actually
        # produces a schema the API's strict json_schema format accepts --
        # it recursively sets additionalProperties: false, inlines $defs
        # correctly, and drops constraints the API doesn't support (folding
        # them into the description instead of sending an invalid schema).
        output_config: dict[str, Any] = {
            "format": {"type": "json_schema", "schema": transform_schema(output_format)},
        }
        if self.model.role in EFFORT_BY_ROLE:
            output_config["effort"] = EFFORT_BY_ROLE[self.model.role]

        kwargs: dict[str, Any] = {
            "model": self.model.model_id,
            "max_tokens": self.max_tokens,
            # Stable per agent, so it caches. Volatile evidence goes in the
            # user turn, after the cached prefix.
            "system": [{
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }],
            "messages": [{"role": "user", "content": blocks}],
            "output_config": output_config,
        }
        if self.model.role in EFFORT_BY_ROLE:
            # Adaptive thinking is a 4.6+-generation feature, same floor as
            # effort. Only sent for the role documented to use a model that
            # supports it (see module docstring).
            kwargs["thinking"] = {"type": "adaptive"}

        if self.use_refusal_fallback:
            # Cyber telemetry is exactly the workload that can trip a policy
            # decline. Opting in means the API re-runs the request on a
            # fallback model inside the same call rather than returning empty.
            kwargs["betas"] = [FALLBACK_BETA]
            kwargs["fallbacks"] = "default"
            response = self.client.beta.messages.create(**kwargs)
        else:
            response = self.client.messages.create(**kwargs)

        return self._to_call(agent, response, provenance, output_format)

    def _to_call(
        self, agent: str, response: Any, provenance: list[str], output_format: type[T],
    ) -> AgentCall:
        stop_reason = getattr(response, "stop_reason", None)
        refused = stop_reason == "refusal"
        category = None
        if refused:
            details = getattr(response, "stop_details", None)
            category = getattr(details, "category", None) if details else None

        usage = getattr(response, "usage", None)
        served_by = None
        if usage is not None and getattr(usage, "iterations", None):
            if any(getattr(i, "type", None) == "fallback_message"
                   for i in usage.iterations):
                served_by = getattr(response, "model", None)

        parsed: T | None = None
        unusable_reason: str | None = None
        if not refused:
            if stop_reason not in _COMPLETE_STOP_REASONS:
                unusable_reason = f"stop_reason={stop_reason!r}, not a completed answer"
            else:
                text = _first_text(response)
                if text is None:
                    unusable_reason = "no text content block in the response"
                else:
                    try:
                        parsed = output_format.model_validate_json(text)
                    except (ValueError, TypeError) as exc:
                        # Covers both invalid JSON and schema-valid-JSON-that-
                        # fails-pydantic-validation. Never re-raise here: an
                        # unparsable answer is a routine outcome for this
                        # module, not broken plumbing.
                        unusable_reason = f"response text failed schema validation: {exc}"

        return AgentCall(
            agent=agent,
            model_id=self.model.model_id,
            role=self.model.role,
            stop_reason=stop_reason,
            input_tokens=getattr(usage, "input_tokens", 0) if usage else 0,
            output_tokens=getattr(usage, "output_tokens", 0) if usage else 0,
            refused=refused,
            refusal_category=category,
            served_by=served_by,
            request_id=getattr(response, "_request_id", None),
            parsed=parsed,
            unusable_reason=unusable_reason,
            fenced_provenance=provenance,
        )


def _first_text(response: Any) -> str | None:
    """The first `text`-type content block's text, or None if there isn't one.

    A response can be all-thinking-blocks (adaptive thinking with no answer
    yet emitted) or empty on some non-`end_turn` stops; both are `None` here,
    never a crash.
    """
    for block in getattr(response, "content", None) or []:
        if getattr(block, "type", None) == "text":
            text = getattr(block, "text", None)
            if text:
                return text
    return None
