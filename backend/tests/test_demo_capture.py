"""Step 14: demo fallback capture. capture_fixtures() against a fake client
(no network, no real server); the ?demo=1 middleware against the real app
with a manifest injected in place -- confirms it replays a fixture exactly,
never touches a write route or an excluded read route, and leaves an
un-demoed request computing live as before."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

import citinel.web.app as app_mod
from citinel.web.demo_capture import capture_fixtures, find_fixture, load_fixtures

from tests.conftest import WRITE_HEADERS

client = TestClient(app_mod.app)


class _FakeResponse:
    def __init__(self, status_code: int, body):
        self.status_code = status_code
        self._body = body

    def json(self):
        return self._body


class _FakeClient:
    def __init__(self, answers: dict[str, tuple[int, object]]):
        self.answers = answers
        self.requested: list[str] = []

    def get(self, path: str) -> _FakeResponse:
        self.requested.append(path)
        status, body = self.answers.get(path, (404, {"detail": "not found"}))
        return _FakeResponse(status, body)


def test_capture_fixtures_walks_every_route_once_per_incident():
    fake = _FakeClient({
        "/api/policy": (200, {"name": "citinel-policy"}),
        "/api/corpus": (200, {"rules_total": 3302}),
        "/api/eval": (200, {"measured": []}),
        "/api/incidents?summary=true": (200, [{"incident_id": "INC-A"}, {"incident_id": "INC-B"}]),
        "/api/incidents/INC-A": (200, {"incident_id": "INC-A"}),
        "/api/incidents/INC-A/audit": (200, []),
        "/api/incidents/INC-A/verdict": (404, {"detail": "no verdict"}),
        "/api/incidents/INC-A/draft": (200, {"draft": {}}),
        "/api/incidents/INC-A/context": (404, {"detail": "no context"}),
        "/api/incidents/INC-A/handover": (404, {"detail": "no handover"}),
        "/api/incidents/INC-B": (200, {"incident_id": "INC-B"}),
        "/api/incidents/INC-B/audit": (200, []),
        "/api/incidents/INC-B/verdict": (200, {"mode": "full"}),
        "/api/incidents/INC-B/draft": (200, {"draft": {}}),
        "/api/incidents/INC-B/context": (200, {"queries": []}),
        "/api/incidents/INC-B/handover": (200, {"status": "ok"}),
    })
    manifest = capture_fixtures(fake, ["INC-A", "INC-B"])
    assert manifest["incident_ids"] == ["INC-A", "INC-B"]
    assert "captured_at" in manifest
    routes = manifest["routes"]
    # incident-independent routes captured exactly once, not per incident
    assert fake.requested.count("/api/policy") == 1
    assert fake.requested.count("/api/corpus") == 1
    # per-incident routes captured once per incident, at the real path
    assert routes["/api/incidents/INC-A/verdict"] == {"status_code": 404, "body": {"detail": "no verdict"}}
    assert routes["/api/incidents/INC-B/verdict"] == {"status_code": 200, "body": {"mode": "full"}}
    # /api/source, connectors, ledger/verify, and every write route are never requested
    assert not any(p == "/api/source" or "connectors" in p or "ledger/verify" in p for p in fake.requested)
    assert "/api/incidents/INC-A/swarm" not in fake.requested


def test_load_fixtures_missing_or_malformed_is_none(tmp_path):
    assert load_fixtures(tmp_path / "nope.json") is None
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert load_fixtures(bad) is None
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"routes": {"/x": {"status_code": 200, "body": 1}}}), encoding="utf-8")
    assert load_fixtures(good) == {"routes": {"/x": {"status_code": 200, "body": 1}}}


def test_find_fixture_matches_the_literal_path_only():
    manifest = {"routes": {"/api/incidents/INC-A/verdict": {"status_code": 200, "body": {"a": 1}}}}
    assert find_fixture(manifest, "/api/incidents/INC-A/verdict") == {"status_code": 200, "body": {"a": 1}}
    assert find_fixture(manifest, "/api/incidents/INC-B/verdict") is None
    assert find_fixture(None, "/anything") is None


@pytest.fixture
def demo_manifest(monkeypatch):
    manifest = {
        "captured_at": "2026-09-02T00:00:00+00:00",
        "incident_ids": ["INC-CAP"],
        "routes": {
            "/api/incidents/INC-CAP/verdict": {"status_code": 200, "body": {"captured": True, "mode": "full"}},
            "/api/incidents?summary=true": {"status_code": 200, "body": [{"incident_id": "INC-CAP"}]},
        },
    }
    monkeypatch.setattr(app_mod, "DEMO_MANIFEST", manifest)
    return manifest


def test_demo_equals_1_replays_the_captured_fixture(demo_manifest):
    r = client.get("/api/incidents/INC-CAP/verdict?demo=1")
    assert r.status_code == 200
    assert r.json() == {"captured": True, "mode": "full"}
    assert r.headers["X-Citinel-Demo"] == "1"


def test_demo_equals_1_preserves_a_captured_non_200_status(demo_manifest):
    demo_manifest["routes"]["/api/incidents/INC-CAP/handover"] = {"status_code": 404, "body": {"detail": "no handover"}}
    r = client.get("/api/incidents/INC-CAP/handover?demo=1")
    assert r.status_code == 404
    assert r.json() == {"detail": "no handover"}
    assert r.headers["X-Citinel-Demo"] == "1"


def test_without_demo_param_the_route_computes_live_even_with_a_manifest_present(demo_manifest, sandbox):
    r = client.get("/api/incidents/INC-CAP/verdict")
    assert r.status_code == 404  # no real verdict was ever saved for INC-CAP in the sandbox
    assert "X-Citinel-Demo" not in r.headers


def test_demo_equals_1_on_an_uncaptured_path_falls_through_to_live(demo_manifest, sandbox):
    r = client.get("/api/policy?demo=1")
    assert r.status_code == 200
    assert "X-Citinel-Demo" not in r.headers
    assert "name" in r.json()


def test_demo_equals_1_never_serves_a_fixture_for_a_write_route(demo_manifest, sandbox):
    """capture_fixtures() only ever issues GETs, so no fixture keyed to a
    write route's path can exist -- but confirm the middleware itself also
    only ever consults the manifest for a GET, even if one were hand-added."""
    demo_manifest["routes"]["/api/actions/deny"] = {"status_code": 200, "body": {"denied": True, "faked": True}}
    r = client.post("/api/actions/deny?demo=1", json={
        "incident_id": "INC-T1", "action_class": "notify", "target": "x", "by": "t", "reason": "r",
    }, headers=WRITE_HEADERS)
    assert r.status_code == 200
    assert r.json().get("faked") is not True  # the real handler ran, not the planted fixture


def test_demo_equals_1_never_serves_connectors_ledger_verify_or_source_even_if_hand_added(demo_manifest, sandbox, monkeypatch):
    """Defense in depth beyond capture_fixtures() never requesting these: even
    a hand-edited manifest containing these keys must not be servable, since
    they exist specifically to always reflect this process's live state.
    /api/source is included because it reports demo-capture availability
    itself -- replaying a frozen copy of it would be self-contradictory the
    moment a capture exists that its own frozen answer denies."""
    demo_manifest["routes"]["/api/connectors"] = {"status_code": 200, "body": {"faked": True}}
    demo_manifest["routes"]["/api/ledger/verify"] = {"status_code": 200, "body": {"faked": True}}
    demo_manifest["routes"]["/api/source"] = {"status_code": 200, "body": {"faked": True}}
    for name in ("lyzr_api_key", "lyzr_guard_url", "lyzr_agent_id"):
        monkeypatch.setattr(app_mod.settings, name, None)
    r1 = client.get("/api/connectors?demo=1")
    r2 = client.get("/api/ledger/verify?demo=1")
    r3 = client.get("/api/source?demo=1")
    assert r1.json().get("faked") is not True
    assert r2.json().get("faked") is not True
    assert r3.json().get("faked") is not True
    assert "demo_capture" in r3.json()


def test_source_reports_demo_capture_availability(demo_manifest, sandbox):
    body = client.get("/api/source").json()
    assert body["demo_capture"] == {
        "available": True, "captured_at": "2026-09-02T00:00:00+00:00",
        "incident_ids": ["INC-CAP"], "routes_captured": 2,
    }


def test_source_reports_demo_capture_unavailable_when_no_manifest(sandbox, monkeypatch):
    monkeypatch.setattr(app_mod, "DEMO_MANIFEST", None)
    body = client.get("/api/source").json()
    assert body["demo_capture"] == {
        "available": False, "captured_at": None, "incident_ids": [], "routes_captured": 0,
    }
