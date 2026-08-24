"""Action execution against simulated endpoints, under the audit ledger.

PIPE-F09 is absolute: response actions run only against mocks -- a mock
firewall, a mock directory, a mock EDR. Every receipt is stamped SIMULATED so
no output of this module can be mistaken for a real infrastructure change,
on screen or in a draft report. The demo says "we hit mocks, we say so".

Execution and rollback both write to the audit ledger under the incident's
case id: policy_check -> action_executed -> (optionally) action_rolled_back
is the visible spine of demo Beat 3.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from citinel.audit.ledger import AuditLedger
from citinel.config import settings
from citinel.policy.gate import Decision, Verdict


class ExecutionRefused(Exception):
    pass


@dataclass
class Receipt:
    action_class: str
    target: str
    status: str                 # executed | proposed_only | awaiting_approval
    simulated: bool
    rollback_token: str | None
    detail: str
    at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def as_dict(self) -> dict[str, Any]:
        return {
            "action_class": self.action_class, "target": self.target,
            "status": self.status, "simulated": self.simulated,
            "rollback_token": self.rollback_token, "detail": self.detail,
            "at": self.at,
        }


class MockEndpoints:
    """The simulated bank infrastructure. State lives in memory; rollback
    genuinely reverses it, so the rollback token is real behaviour, not
    theatre."""

    def __init__(self) -> None:
        self.isolated_hosts: set[str] = set()
        self.blocked_ips: set[str] = set()
        self.quarantined: set[str] = set()
        self.disabled_accounts: set[str] = set()
        self.revoked_sessions: set[str] = set()
        self.notifications: list[str] = []
        self._undo: dict[str, tuple[str, str]] = {}  # token -> (kind, target)

    def apply(self, action_class: str, target: str, token: str | None) -> str:
        if action_class == "isolate_host":
            self.isolated_hosts.add(target)
            detail = f"[SIMULATED] firewall rule added: {target} fully isolated"
        elif action_class == "block_ip":
            self.blocked_ips.add(target)
            detail = f"[SIMULATED] perimeter deny rule added for {target}"
        elif action_class == "quarantine_file":
            self.quarantined.add(target)
            detail = f"[SIMULATED] file hash {target} quarantined on matching hosts"
        elif action_class == "disable_account":
            self.disabled_accounts.add(target)
            detail = f"[SIMULATED] directory account {target} disabled"
        elif action_class == "revoke_sessions":
            self.revoked_sessions.add(target)
            detail = f"[SIMULATED] all sessions for {target} revoked"
        elif action_class == "notify":
            self.notifications.append(target)
            detail = f"[SIMULATED] notification sent: {target}"
        elif action_class in ("enrich_ioc", "query_logs"):
            detail = f"[SIMULATED] lookup performed for {target}"
        else:
            raise ExecutionRefused(f"mock endpoints do not implement {action_class}")
        if token:
            self._undo[token] = (action_class, target)
        return detail

    def rollback(self, token: str) -> str:
        if token not in self._undo:
            raise ExecutionRefused(f"unknown rollback token {token}")
        kind, target = self._undo.pop(token)
        if kind == "isolate_host":
            self.isolated_hosts.discard(target)
        elif kind == "block_ip":
            self.blocked_ips.discard(target)
        elif kind == "quarantine_file":
            self.quarantined.discard(target)
        elif kind == "disable_account":
            self.disabled_accounts.discard(target)
        return f"[SIMULATED] rollback applied: {kind} on {target} reversed"


class ActionExecutor:
    """Carries a gate decision to its outcome, writing the ledger throughout."""

    def __init__(self, endpoints: MockEndpoints, ledger: AuditLedger) -> None:
        if not settings.simulated_endpoints_only:
            # Refusing to construct is the point: there is no code path in
            # this repository that talks to real infrastructure (PIPE-F09).
            raise ExecutionRefused(
                "simulated_endpoints_only is disabled; this build refuses to "
                "run response actions in that configuration"
            )
        self.endpoints = endpoints
        self.ledger = ledger

    def execute(self, case_id: str, decision: Decision, target: str) -> Receipt:
        self.ledger.append(case_id, "policy-gate", "policy_check",
                           decision.as_dict())

        if decision.verdict is Verdict.DENY:
            raise ExecutionRefused("; ".join(decision.reasons))

        if decision.verdict is Verdict.SHADOW:
            return Receipt(decision.action_class, target, "proposed_only",
                           True, None, "shadow tier: proposal logged, nothing executed")

        if decision.verdict is Verdict.REQUIRE_APPROVAL:
            return Receipt(decision.action_class, target, "awaiting_approval",
                           True, None,
                           f"held for one-click human approval (clause "
                           f"{decision.clause_ref})")

        detail = self.endpoints.apply(decision.action_class, target,
                                      decision.rollback_token)
        self.ledger.append(case_id, "response-marshal", "action_executed", {
            "action_class": decision.action_class, "target": target,
            "clause_ref": decision.clause_ref, "simulated": True,
            "rollback_token": decision.rollback_token, "detail": detail,
        })
        return Receipt(decision.action_class, target, "executed", True,
                       decision.rollback_token, detail)

    def approve_and_execute(self, case_id: str, decision: Decision,
                            target: str, approver: str) -> Receipt:
        """The one-click human approval path for REQUIRE_APPROVAL decisions."""
        if decision.verdict is not Verdict.REQUIRE_APPROVAL:
            raise ExecutionRefused("approve_and_execute is only for approval-held actions")
        self.ledger.append(case_id, approver, "human_signoff", {
            "approved": decision.as_dict(), "target": target,
        })
        detail = self.endpoints.apply(decision.action_class, target, None)
        self.ledger.append(case_id, "response-marshal", "action_executed", {
            "action_class": decision.action_class, "target": target,
            "clause_ref": decision.clause_ref, "simulated": True,
            "approved_by": approver, "detail": detail,
        })
        return Receipt(decision.action_class, target, "executed", True, None, detail)

    def rollback(self, case_id: str, token: str, actor: str) -> Receipt:
        detail = self.endpoints.rollback(token)
        self.ledger.append(case_id, actor, "action_rolled_back",
                           {"rollback_token": token, "detail": detail})
        return Receipt("rollback", token, "executed", True, None, detail)
