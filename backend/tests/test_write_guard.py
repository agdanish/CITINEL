"""The write-authentication guard itself, in isolation from the sandbox
fixture's own token injection -- a bare client, so every state a real
deployment can be in is exercised on purpose: token never configured,
token configured but wrong, token configured and correct. Confirmed live
2 Sep 2026 that with no guard at all, an anonymous caller could forge a
human_signoff naming a real person and close an incident on their
authority; this is the fix for that finding."""

from __future__ import annotations

from fastapi.testclient import TestClient

import citinel.web.app as app_mod
from citinel.config import settings

client = TestClient(app_mod.app)

WRITE_ROUTES = [
    ("post", "/api/actions/execute", {"incident_id": "INC-T1", "action_class": "notify", "target": "x"}),
    ("post", "/api/actions/deny", {"incident_id": "INC-T1", "action_class": "notify", "by": "a", "reason": "r"}),
    ("post", "/api/actions/rollback/rbk-xyz", {"incident_id": "INC-T1"}),
    ("post", "/api/incidents/INC-T1/signoff", {"signed_by": "a@x"}),
    ("post", "/api/incidents/INC-T1/reopen", {"by": "a@x", "reason": "r"}),
    ("post", "/api/incidents/INC-T1/swarm", {"confirm": True}),
    ("post", "/api/incidents/INC-T1/context", {"confirm": True}),
    ("post", "/api/incidents/INC-T1/handover", {"confirm": True}),
]


def test_every_write_route_is_503_with_no_token_configured(monkeypatch):
    """Unset CITINEL_WRITE_TOKEN means writes are OFF, not open -- a
    deployment that forgot to set it is a safe read-only demo."""
    monkeypatch.setattr(settings, "write_token", None)
    for method, path, body in WRITE_ROUTES:
        r = getattr(client, method)(path, json=body)
        assert r.status_code == 503, f"{path} -> {r.status_code}, expected 503"
        assert "not configured" in r.json()["detail"]


def test_every_write_route_is_401_with_the_wrong_token(monkeypatch):
    monkeypatch.setattr(settings, "write_token", "the-real-token")
    for method, path, body in WRITE_ROUTES:
        r = getattr(client, method)(path, json=body, headers={"X-Citinel-Write-Token": "guessed-wrong"})
        assert r.status_code == 401, f"{path} -> {r.status_code}, expected 401"
        r2 = getattr(client, method)(path, json=body)  # no header at all
        assert r2.status_code == 401, f"{path} with no header -> {r2.status_code}, expected 401"


def test_the_correct_token_reaches_the_real_handler(monkeypatch, sandbox):
    """sandbox already sets write_token to TEST_WRITE_TOKEN; confirm the
    guard actually lets a correctly-authenticated write through rather than
    merely not-blocking it for the wrong reason."""
    from tests.conftest import TEST_WRITE_TOKEN
    r = client.post("/api/actions/execute",
                     json={"incident_id": "INC-T1", "action_class": "notify", "target": "SOC", "assets_affected": 0},
                     headers={"X-Citinel-Write-Token": TEST_WRITE_TOKEN})
    assert r.status_code == 200, r.text
    assert r.json()["receipt"]["status"] == "executed"


def test_get_routes_are_never_gated_regardless_of_token_state(monkeypatch, sandbox):
    """The whole point of the console is public read access -- a login wall
    on GET would defeat the glass-box premise the product is built on."""
    monkeypatch.setattr(settings, "write_token", None)  # writes fully off
    for path in ("/api/incidents", "/api/incidents?summary=true", "/api/source",
                 "/api/policy", "/api/corpus", "/api/connectors", "/api/ledger/verify"):
        r = client.get(path)
        assert r.status_code != 503, f"{path} was blocked by the write guard"
        assert r.status_code != 401, f"{path} was blocked by the write guard"


def test_healthz_and_static_console_files_are_never_gated(monkeypatch):
    monkeypatch.setattr(settings, "write_token", None)
    assert client.get("/healthz").status_code == 200
    assert client.get("/Overview.dc.html").status_code == 200


def test_the_guard_compares_the_token_safely_not_by_naive_equality(monkeypatch):
    """secrets.compare_digest, not `==` -- constant-time so a wrong guess
    cannot be narrowed down by how long the comparison takes. This test
    can't measure timing, but it can confirm the real comparator is used
    rather than a lookalike that would silently accept a prefix match."""
    import inspect
    src = inspect.getsource(app_mod._guard_writes)
    assert "secrets.compare_digest" in src
    assert " == token" not in src and " == expected" not in src
