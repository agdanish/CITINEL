"""Typed contracts for the seven-agent swarm.

Every agent returns a validated object, never free prose. Three reasons this
is structural rather than stylistic:

* **The citation promise is checkable.** A Claim names the finding it rests on
  by index and quotes the exact span it relies on. `verify_citations` then
  re-reads the incident's own findings and confirms the quoted span is really
  there. A fabricated citation fails a string comparison -- it does not depend
  on the model being honest about its own sourcing. That check is what makes
  "every claim cites the log line proving it" a property of the system rather
  than a claim about the model.

* **The ledger stays a forensic record.** AGT-F06 / SAFE-F06: the audit log
  records structured decisions and tool calls, never model thinking summaries.
  These objects are what gets logged. There is deliberately no field anywhere
  in this module that carries reasoning narrative into the ledger.

* **The gate gets machine-readable input.** A ProposedAction maps exactly onto
  `PolicyGate.check(action_class, assets_affected, target_summary)`. The
  Response Marshal cannot propose an action the gate is unable to evaluate.

Claim discipline: a verdict here is CITINEL's assessment, not ground truth.
`Verdict.confidence` is the model's own stated confidence and is labelled as
such wherever it surfaces. Counter-evidence is a first-class field, never an
afterthought -- an investigation that found none must say so explicitly
(`counter_evidence: []` plus `counter_evidence_searched: true`), because an
empty column and an unasked question look identical otherwise.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

#: Below this length a "match" is a coincidence, not a citation. An empty or
#: single-character quoted_span passes a naive substring check against any
#: text -- `"" in evidence` is always True -- which turns the citation gate
#: into a no-op exactly where a fabricated or injection-steered claim would
#: aim. Enforced twice: as a pydantic constraint on the raw string (below),
#: and again in verify_citations() after whitespace normalization, so a
#: span that is all whitespace cannot slip through by collapsing to "".
MIN_SPAN_LENGTH = 8


class Lane(str, Enum):
    """Which lane an alert leaves triage in. Mirrors the queue's two lanes."""

    AUTO_CLOSE = "auto_close"   # deterministic layers explained it; no swarm needed
    ESCALATE = "escalate"       # rules could not explain it; the swarm investigates


class Support(str, Enum):
    SUPPORTING = "supporting"
    COUNTER = "counter"


class Citation(BaseModel):
    """A pointer into the incident's own findings, verifiable after the fact.

    `finding_index` indexes `Incident.findings`. `quoted_span` must appear
    verbatim in that finding's `evidence_raw`. Both are checked by
    `verify_citations` before any verdict is allowed to progress.
    """

    finding_index: int = Field(description="Index into the incident's findings list.")
    quoted_span: str = Field(
        min_length=MIN_SPAN_LENGTH,
        description="Exact substring of that finding's raw log line that supports "
                    "the claim. Must be copied verbatim, not paraphrased, and must "
                    f"be at least {MIN_SPAN_LENGTH} characters -- long enough to be "
                    "an identifying quote, not a coincidental one-word match."
    )

    model_config = {"extra": "forbid"}


class Claim(BaseModel):
    """One assertion, with the evidence it rests on attached."""

    text: str = Field(description="The assertion, in one plain sentence.")
    support: Support
    citations: list[Citation] = Field(
        default_factory=list,
        description="Every finding this claim rests on. A claim with no citation "
                    "is rejected before it reaches a human.",
    )

    model_config = {"extra": "forbid"}


class TriageDecision(BaseModel):
    """Triage Router output. Cheap, fast, and reversible by design."""

    lane: Lane
    rationale: str = Field(description="One sentence. Why this lane.")
    confidence: float = Field(ge=0.0, le=1.0)

    model_config = {"extra": "forbid"}


class KillChainStage(BaseModel):
    """One step of the assembled ATT&CK narrative."""

    technique_id: str = Field(description="ATT&CK technique id, e.g. T1059.001.")
    technique_name: str
    what_happened: str = Field(description="One sentence, in the bank's terms.")
    citations: list[Citation] = Field(default_factory=list)

    model_config = {"extra": "forbid"}


class Correlation(BaseModel):
    """Correlator output: the kill chain, assembled and ordered."""

    stages: list[KillChainStage]
    summary: str = Field(description="The chain in one paragraph, plain language.")
    hosts_involved: list[str] = Field(default_factory=list)

    model_config = {"extra": "forbid"}


class Verdict(BaseModel):
    """Verdict Narrator output. The two-column ledger, structurally enforced."""

    headline: str = Field(description="What happened, one sentence, no hedging.")
    claims: list[Claim] = Field(description="Supporting and counter claims together.")
    counter_evidence_searched: bool = Field(
        description="True only if counter-evidence was actively looked for. An "
                    "empty counter column with this false is an unasked question, "
                    "not a clean bill of health.",
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="CITINEL's own stated confidence. Not a probability of truth; "
                    "surfaced to humans labelled as an assessment.",
    )
    benign_explanation_considered: str = Field(
        description="The most plausible innocent explanation, and why it was or "
                    "was not ruled out.",
    )

    model_config = {"extra": "forbid"}

    def supporting(self) -> list[Claim]:
        return [c for c in self.claims if c.support is Support.SUPPORTING]

    def counter(self) -> list[Claim]:
        return [c for c in self.claims if c.support is Support.COUNTER]


class ProposedAction(BaseModel):
    """Response Marshal output. Shaped to fit the policy gate exactly.

    `action_class` must be a class the policy defines; the gate denies anything
    else rather than defaulting, so a hallucinated action class fails closed.
    """

    action_class: str = Field(description="Must match a policy clause action_class.")
    target: str = Field(description="The single asset or indicator acted on.")
    assets_affected: int = Field(
        ge=0, description="Blast radius. Drives the gate's automatic cap."
    )
    justification: str = Field(description="Why this action, in one sentence.")
    citations: list[Citation] = Field(default_factory=list)

    model_config = {"extra": "forbid"}


class CitationFailure(BaseModel):
    """One citation that did not survive verification."""

    claim_text: str
    reason: str
    finding_index: int
    quoted_span: str


def verify_citations(
    claims: list[Claim] | list[ProposedAction] | list[KillChainStage],
    findings: list[Any],
) -> list[CitationFailure]:
    """Re-read the evidence and confirm every quoted span is really there.

    Returns the failures; an empty list means every citation checks out. This
    runs on CITINEL's own findings, in process, with no model involved -- which
    is the point. A model that invents a plausible-looking log line cannot pass
    a substring check against the corpus it claims to be quoting.

    Whitespace is normalised before comparison (log rendering varies); nothing
    else is. A near-miss is a miss.
    """
    failures: list[CitationFailure] = []
    for item in claims:
        text = getattr(item, "text", None) or getattr(item, "what_happened", None) \
            or getattr(item, "justification", "")
        for cite in item.citations:
            if not 0 <= cite.finding_index < len(findings):
                failures.append(CitationFailure(
                    claim_text=text,
                    reason=f"finding_index {cite.finding_index} is out of range "
                           f"(incident has {len(findings)} findings)",
                    finding_index=cite.finding_index,
                    quoted_span=cite.quoted_span,
                ))
                continue
            evidence = getattr(findings[cite.finding_index], "evidence_raw", "") or ""
            norm_span = _norm(cite.quoted_span)
            if len(norm_span) < MIN_SPAN_LENGTH:
                failures.append(CitationFailure(
                    claim_text=text,
                    reason=f"quoted span is only {len(norm_span)} characters after "
                           f"whitespace normalisation (minimum {MIN_SPAN_LENGTH}) -- "
                           "too short to be a real citation, not just an empty one",
                    finding_index=cite.finding_index,
                    quoted_span=cite.quoted_span,
                ))
                continue
            if norm_span not in _norm(evidence):
                failures.append(CitationFailure(
                    claim_text=text,
                    reason="quoted span does not appear in the cited log line",
                    finding_index=cite.finding_index,
                    quoted_span=cite.quoted_span,
                ))
    return failures


def _norm(s: str) -> str:
    return " ".join(s.split())


def uncited(claims: list[Claim]) -> list[Claim]:
    """Claims carrying no citation at all. Rejected before a human sees them."""
    return [c for c in claims if not c.citations]
