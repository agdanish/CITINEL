"""The policy gate: every proposed action passes through here, no exceptions.

Implements the readable per-action-class policy (SAFE-F03) with the
Shadow/Assist/Autonomous dial per action class (SAFE-F04), blast-radius caps
(SAFE-F07) and structural approval requirements that no dial position can
relax (SDD Section 17 finding 1: turning autonomy up must never quietly turn
safeguards down).

Engine note, stated plainly: the canonical policy is the signed YAML file at
policies/citinel-policy.yaml, evaluated in-process. This is the fallback
ladder's pre-committed second rung (CITINEL-STATE.md Section 1.7: "signed YAML
config enforcing identical per-action semantics if OPA integration slips") --
chosen here because the build machine has no OPA binary or Docker. The same
policy ships as policies/citinel.rego; wiring the real OPA engine over it is
deploy-time work (Step 12), with a conformance test that both engines return
identical decisions. Which engine produced a decision is recorded on the
decision itself, so nothing is silently substituted.

The gate returns a decision; it never executes anything itself. Execution and
rollback live in actions.py, and both write to the audit ledger under the
incident's case id.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from citinel.config import AutonomyTier


class Verdict(str, Enum):
    ALLOW = "allow"                        # execute now
    ALLOW_WITH_ROLLBACK = "allow_with_rollback"  # execute now, token attached
    REQUIRE_APPROVAL = "require_approval"  # wait for a human click
    SHADOW = "shadow"                      # log the proposal, execute nothing
    DENY = "deny"                          # not permitted at all


@dataclass(frozen=True)
class Clause:
    ref: str
    action_class: str
    description: str
    tier: AutonomyTier
    approval_always: bool
    max_assets_auto: int
    reversible: bool


@dataclass
class Decision:
    verdict: Verdict
    clause_ref: str
    action_class: str
    reasons: list[str]
    intent_preview: str            # plain-language pre-execution summary
    rollback_token: str | None = None
    engine: str = "yaml-inprocess" # which policy engine decided; never hidden
    decided_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "clause_ref": self.clause_ref,
            "action_class": self.action_class,
            "reasons": self.reasons,
            "intent_preview": self.intent_preview,
            "rollback_token": self.rollback_token,
            "engine": self.engine,
            "decided_at": self.decided_at,
        }


class PolicyError(Exception):
    pass


class PolicyGate:
    """Loads the signed policy once; answers every proposal deterministically."""

    def __init__(self, policy_path: Path) -> None:
        self.policy_path = policy_path
        raw = policy_path.read_bytes()
        #: Integrity fingerprint of the exact policy text in force. Recorded
        #: with every decision batch so an audit can prove which rulebook was
        #: active ("signed YAML" per the fallback ladder).
        self.policy_sha256 = hashlib.sha256(raw).hexdigest()
        doc = yaml.safe_load(raw)
        self.name = doc["policy"]["name"]
        self.version = int(doc["policy"]["version"])
        self.clauses: dict[str, Clause] = {}
        self.by_class: dict[str, Clause] = {}
        for ref, c in doc["clauses"].items():
            clause = Clause(
                ref=str(ref),
                action_class=c["action_class"],
                description=c["description"],
                tier=AutonomyTier(c["tier"]),
                approval_always=(c["approval"] == "always"),
                max_assets_auto=int(c["max_assets_auto"]),
                reversible=bool(c["reversible"]),
            )
            self.clauses[clause.ref] = clause
            if clause.action_class in self.by_class:
                raise PolicyError(f"duplicate action_class {clause.action_class}")
            self.by_class[clause.action_class] = clause

    # -- the gate ------------------------------------------------------------

    def check(
        self,
        action_class: str,
        assets_affected: int,
        target_summary: str,
    ) -> Decision:
        """Decide one proposed action. Pure function of policy + inputs."""
        clause = self.by_class.get(action_class)
        if clause is None:
            return Decision(
                verdict=Verdict.DENY,
                clause_ref="-",
                action_class=action_class,
                reasons=[f"no policy clause defines action class {action_class!r}; "
                         "undefined actions are denied, not defaulted"],
                intent_preview=f"DENIED: {action_class} is not in the policy.",
            )

        reasons: list[str] = []
        preview = (
            f"About to {clause.description.lower()} -- target: {target_summary}; "
            f"assets affected: {assets_affected}; clause {clause.ref} "
            f"({clause.tier.value} tier)."
        )

        # 1. Structural approval outranks every dial position.
        if clause.approval_always:
            reasons.append(
                f"clause {clause.ref} requires human approval at every dial "
                "position; this is structural and no tier setting relaxes it"
            )
            return Decision(Verdict.REQUIRE_APPROVAL, clause.ref, action_class,
                            reasons, preview)

        # 2. Blast-radius ring: too wide means a human decides, whatever the tier.
        if assets_affected > clause.max_assets_auto:
            reasons.append(
                f"blast radius {assets_affected} exceeds the automatic cap of "
                f"{clause.max_assets_auto} for clause {clause.ref}; escalating "
                "to approval (SAFE-F07)"
            )
            return Decision(Verdict.REQUIRE_APPROVAL, clause.ref, action_class,
                            reasons, preview)

        # 3. The dial.
        if clause.tier is AutonomyTier.SHADOW:
            reasons.append(f"clause {clause.ref} is in shadow: proposal logged, "
                           "nothing executes")
            return Decision(Verdict.SHADOW, clause.ref, action_class, reasons, preview)

        if clause.tier is AutonomyTier.ASSIST:
            if clause.reversible:
                token = f"rbk-{secrets.token_hex(8)}"
                reasons.append(
                    f"clause {clause.ref} is in assist: executing with rollback "
                    f"token {token}"
                )
                return Decision(Verdict.ALLOW_WITH_ROLLBACK, clause.ref,
                                action_class, reasons, preview,
                                rollback_token=token)
            reasons.append(
                f"clause {clause.ref} is in assist and the action is "
                "irreversible: executing within its hard asset cap, no token "
                "possible; the cap is the safeguard"
            )
            return Decision(Verdict.ALLOW, clause.ref, action_class, reasons, preview)

        reasons.append(f"clause {clause.ref} is autonomous for this class")
        return Decision(Verdict.ALLOW, clause.ref, action_class, reasons, preview)

    # -- introspection (what the UI renders) ----------------------------------

    def table(self) -> list[dict[str, Any]]:
        return [
            {
                "clause": c.ref,
                "action_class": c.action_class,
                "description": c.description,
                "tier": c.tier.value,
                "approval": "always" if c.approval_always else "never",
                "max_assets_auto": c.max_assets_auto,
                "reversible": c.reversible,
            }
            for c in sorted(self.clauses.values(), key=lambda c: c.ref)
        ]
