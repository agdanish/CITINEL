"""Tests for the policy gate and mock executor.

The load-bearing semantics: structural approval that no dial position can
relax, blast-radius escalation, shadow-executes-nothing, rollback that
genuinely reverses state, and the refusal to construct an executor when the
simulated-endpoints rail is off.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from citinel.audit.ledger import AuditLedger
from citinel.policy.actions import ActionExecutor, ExecutionRefused, MockEndpoints
from citinel.policy.gate import PolicyGate, Verdict

POLICY = Path(__file__).resolve().parents[2] / "policies" / "citinel-policy.yaml"


@pytest.fixture()
def gate() -> PolicyGate:
    return PolicyGate(POLICY)


@pytest.fixture()
def executor(tmp_path):
    return ActionExecutor(MockEndpoints(), AuditLedger(tmp_path / "l.jsonl"))


# --- gate semantics ---------------------------------------------------------

def test_enrichment_is_autonomous(gate):
    d = gate.check("enrich_ioc", 0, "hash abc123")
    assert d.verdict is Verdict.ALLOW
    assert d.clause_ref == "1.1"


def test_isolation_carries_a_rollback_token(gate):
    d = gate.check("isolate_host", 1, "we8105desk")
    assert d.verdict is Verdict.ALLOW_WITH_ROLLBACK
    assert d.rollback_token and d.rollback_token.startswith("rbk-")
    assert d.clause_ref == "3.1"


def test_account_disable_requires_approval_structurally(gate):
    """The deck's clause 4.2: approval at EVERY dial position."""
    d = gate.check("disable_account", 1, "svc-backup")
    assert d.verdict is Verdict.REQUIRE_APPROVAL
    assert d.clause_ref == "4.2"
    assert any("structural" in r for r in d.reasons)


def test_blast_radius_escalates_regardless_of_tier(gate):
    """Isolating 40 hosts is not 40 isolations; it is a human decision."""
    d = gate.check("isolate_host", 40, "subnet sweep")
    assert d.verdict is Verdict.REQUIRE_APPROVAL
    assert any("blast radius" in r for r in d.reasons)


def test_undefined_action_is_denied_not_defaulted(gate):
    d = gate.check("format_disk", 1, "c:")
    assert d.verdict is Verdict.DENY


def test_every_decision_names_its_clause_and_preview(gate):
    for cls in ("enrich_ioc", "isolate_host", "disable_account"):
        d = gate.check(cls, 1, "t")
        assert d.clause_ref != ""
        assert d.intent_preview
        assert d.engine == "yaml-inprocess"


# --- executor ---------------------------------------------------------------

def test_shadow_executes_nothing(gate, executor):
    d = gate.check("disable_account", 0, "svc-backup")
    # approval path -- but even a shadow-tier ALLOW would not touch state;
    # prove the account was not disabled by the check alone
    r = executor.execute("INC-0417", d, "svc-backup")
    assert r.status == "awaiting_approval"
    assert "svc-backup" not in executor.endpoints.disabled_accounts


def test_execute_and_rollback_round_trip(gate, executor):
    d = gate.check("isolate_host", 1, "we8105desk")
    r = executor.execute("INC-0417", d, "we8105desk")
    assert r.status == "executed" and r.simulated
    assert "we8105desk" in executor.endpoints.isolated_hosts
    rb = executor.rollback("INC-0417", r.rollback_token, "analyst")
    assert "we8105desk" not in executor.endpoints.isolated_hosts
    assert "reversed" in rb.detail


def test_approval_path_executes_after_human_click(gate, executor):
    d = gate.check("disable_account", 1, "svc-backup")
    held = executor.execute("INC-0417", d, "svc-backup")
    assert held.status == "awaiting_approval"
    done = executor.approve_and_execute("INC-0417", d, "svc-backup", "ciso@bank")
    assert done.status == "executed"
    assert "svc-backup" in executor.endpoints.disabled_accounts


def test_every_step_lands_in_the_ledger(gate, tmp_path):
    ledger = AuditLedger(tmp_path / "l.jsonl")
    ex = ActionExecutor(MockEndpoints(), ledger)
    d = gate.check("isolate_host", 1, "we8105desk")
    r = ex.execute("INC-0417", d, "we8105desk")
    ex.rollback("INC-0417", r.rollback_token, "analyst")
    kinds = [e.kind for e in ledger.entries_for("INC-0417")]
    assert kinds == ["policy_check", "action_executed", "action_rolled_back"]
    ok, _ = ledger.verify_chain()
    assert ok


def test_executor_refuses_to_exist_without_the_simulation_rail(tmp_path, monkeypatch):
    from citinel.config import settings
    monkeypatch.setattr(settings, "simulated_endpoints_only", False)
    with pytest.raises(ExecutionRefused):
        ActionExecutor(MockEndpoints(), AuditLedger(tmp_path / "l.jsonl"))


def test_receipts_are_always_stamped_simulated(gate, executor):
    for cls, target in (("enrich_ioc", "1.2.3.4"), ("block_ip", "185.151.160.15")):
        d = gate.check(cls, 1, target)
        r = executor.execute("INC-0417", d, target)
        assert r.simulated is True
        if r.status == "executed" and cls != "enrich_ioc":
            assert "[SIMULATED]" in r.detail
