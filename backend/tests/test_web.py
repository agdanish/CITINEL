"""Tests for the web service -- the Render entry point that was missing.

TestClient boots the real FastAPI app in-process; these are the smoke tests
the Best-Use-of-Render audit asked for: the module must actually import and
serve, not just exist as a Dockerfile CMD string.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from citinel.web.app import app

client = TestClient(app)


def test_healthz_returns_ok_with_no_pipeline_dependency():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "citinel-web"}


def test_policy_endpoint_serves_the_real_gate_table():
    r = client.get("/api/policy")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "CITINEL response policy"
    assert any(c["clause"] == "4.2" for c in body["clauses"])


def test_incidents_endpoint_serves_real_incidents():
    r = client.get("/api/incidents")
    assert r.status_code == 200
    ids = {i["incident_id"] for i in r.json()}
    assert "INC-0417" in ids


def test_single_incident_404s_when_unknown():
    r = client.get("/api/incidents/INC-9999")
    assert r.status_code == 404


def test_audit_endpoint_reconstructs_the_chain():
    r = client.get("/api/incidents/INC-0417/audit")
    assert r.status_code == 200
    entries = r.json()
    assert len(entries) > 0
    assert all(e["case_id"] == "INC-0417" for e in entries)


def test_draft_endpoint_renders_a_real_draft(monkeypatch):
    # pinned no-Lyzr-key: a real key now lives in .env, and this test isn't
    # about the Lyzr second-check -- letting it leak in just makes this test
    # slow (a real network call) for no reason relevant to what it asserts.
    from citinel.config import settings
    monkeypatch.setattr(settings, "lyzr_api_key", None)
    r = client.get("/api/incidents/INC-0417/draft", params={"kind": "certin"})
    assert r.status_code == 200
    body = r.json()
    assert body["draft"]["incident_id"] == "INC-0417"
    assert "DRAFT" in body["rendered"]


def test_draft_endpoint_includes_a_real_guard_screen(monkeypatch):
    """Regression guard: this endpoint used to ship with NO PII screen applied
    at all, despite the guard machinery (agents/guard.py, connectors/lyzr.py)
    being fully built and having a CLI caller. A judge hitting this exact
    endpoint would never have seen it run.

    Pinned to no Lyzr key explicitly -- a real key now lives in .env for the
    live deploy, and without this the test made an actual network call to
    Lyzr (visible in a 30s+ runtime instead of ~instant), which is not what
    this test is checking and makes it flaky/slow for the wrong reason.
    """
    from citinel.config import settings
    monkeypatch.setattr(settings, "lyzr_api_key", None)
    r = client.get("/api/incidents/INC-0417/draft", params={"kind": "dpdp"})
    assert r.status_code == 200
    guard = r.json()["guard"]
    assert guard["checked_by"] == "citinel-local"  # no Lyzr key -- local tier still ran
    assert "clean" in guard and "findings" in guard


def test_ledger_verify_endpoint(monkeypatch):
    # pinned no-Lyzr-key: this endpoint's witness field calls LyzrLedgerMirror
    # for real once a key is configured -- not what this test checks.
    from citinel.config import settings
    monkeypatch.setattr(settings, "lyzr_api_key", None)
    r = client.get("/api/ledger/verify")
    assert r.status_code == 200
    assert r.json()["intact"] is True


# --- role-adaptive projection (two roles, one record) ------------------------

def test_incident_defaults_to_analyst_full_depth_with_no_role_header():
    r = client.get("/api/incidents/INC-0417")
    assert r.status_code == 200
    body = r.json()
    assert body["_projection"]["role"] == "analyst"
    assert body["_projection"]["depth"] == "full"
    assert "findings" in body


def test_ciso_gets_the_position_view_with_findings_folded_and_disclosed():
    r = client.get("/api/incidents/INC-0417", headers={"X-Citinel-Role": "ciso"})
    assert r.status_code == 200
    body = r.json()
    assert body["_projection"]["depth"] == "position"
    assert "findings" not in body
    # folded, and SAID to be folded -- never a thinner record that looks whole
    assert body["_projection"]["omitted"] == ["findings"]
    assert body["finding_count"] > 0


def test_ciso_expand_returns_full_depth_nothing_is_withheld():
    """The 'one click deeper' promise: this is depth adaptation, not access
    control, so expand must return everything to a CISO too."""
    r = client.get("/api/incidents/INC-0417?expand=true",
                   headers={"X-Citinel-Role": "ciso"})
    assert r.status_code == 200
    body = r.json()
    assert body["_projection"]["depth"] == "full"
    assert "findings" in body


def test_unknown_role_defaults_to_more_detail_not_less():
    r = client.get("/api/incidents/INC-0417", headers={"X-Citinel-Role": "wat"})
    assert r.json()["_projection"]["role"] == "analyst"
    assert "findings" in r.json()


# --- data-source honesty ------------------------------------------------------

def test_source_endpoint_reports_which_corpus_is_answering():
    """A seed-backed deployment must not pass as live. Regression guard for a
    deploy bug where a fresh Render service served an empty list with a 200,
    indistinguishable from a quiet night in the SOC."""
    r = client.get("/api/source")
    assert r.status_code == 200
    body = r.json()
    assert body["source"] in {"live", "seed"}
    assert body["description"]
    assert isinstance(body["incidents_file_present"], bool)


# --- eval harness: the credibility screen -------------------------------------

def test_eval_endpoint_serves_measurements_with_denominators():
    r = client.get("/api/eval")
    assert r.status_code == 200
    body = r.json()
    assert body["swarm_evaluated"] is False, "no swarm has run; must not claim otherwise"
    # every rate-style measurement carries the count it came from
    for m in body["measured"]:
        if "rate" in m:
            assert m.get("denominator"), f"{m['name']} published a rate with no denominator"


def test_eval_endpoint_refuses_to_publish_an_unmeasured_fp_rate():
    """The load-bearing one. CITINEL's <10% FP figure is a target that has
    never been measured; the endpoint must say UNMEASURED rather than supply
    a plausible number, and must say what is missing."""
    body = client.get("/api/eval").json()
    fp = [u for u in body["unmeasured"] if "false-positive" in u["name"]]
    assert fp, "the FP rate must be explicitly listed as unmeasured, not omitted"
    assert fp[0]["status"] == "UNMEASURED"
    assert fp[0]["required_to_measure"]

    # and it must not appear as a measurement anywhere
    names = " ".join(m["name"].lower() for m in body["measured"])
    assert "false-positive" not in names and "false positive" not in names


def test_paths_come_from_settings_not_from_file_location(monkeypatch, tmp_path):
    """Regression guard for the first live-deploy failure.

    app.py used to derive its paths from __file__. That holds in a source
    checkout and breaks the moment the package is pip-installed: the code
    then lives in site-packages, so the derived root pointed at
    /usr/local/lib/python3.11/ and the deployed service reported zero
    incidents, a 500 on /api/policy, and a 404 on the console -- while
    /healthz stayed green, so nothing looked wrong from the outside.

    Paths must track settings (CITINEL_DATA_DIR etc), which a container can
    state explicitly, rather than the module's own location on disk.
    """
    import importlib
    from citinel.config import settings

    fake_root = tmp_path / "somewhere-else"
    (fake_root / "data").mkdir(parents=True)
    (fake_root / "policies").mkdir()

    # Monkeypatch the ONE shared settings object directly -- not
    # importlib.reload(citinel.config), which constructs a second,
    # disconnected Settings instance that every module already holding a
    # `from citinel.config import settings` reference (worker/run.py,
    # connectors/lyzr.py, cli.py, ...) would NOT pick up. That happened here
    # once and silently split "the" settings singleton into two objects for
    # the rest of the test session -- later tests' monkeypatch.setattr(settings,
    # ...) patched the new copy while already-imported modules kept reading
    # the old one, so e.g. test_worker.py started making real Lyzr network
    # calls, but only when run as part of the full suite, never in isolation.
    monkeypatch.setattr(settings, "data_dir", fake_root / "data")
    monkeypatch.setattr(settings, "policy_dir", fake_root / "policies")

    import citinel.web.app as app_mod
    importlib.reload(app_mod)

    assert app_mod.SEED_DIR == fake_root / "data" / "seed"
    assert app_mod.POLICY_PATH == fake_root / "policies" / "citinel-policy.yaml"
    assert "python3" not in str(app_mod.SEED_DIR), "path derived from interpreter location"

    # Restore for the rest of the suite: undo the settings patch (pytest would
    # do this at teardown anyway, but app_mod's module-level constants were
    # computed at reload time above and need recomputing against the real
    # settings before any later test imports/reuses this same module object).
    monkeypatch.undo()
    importlib.reload(app_mod)


def test_root_redirects_to_the_console_entry_point():
    """The deck's QR code points at "/". StaticFiles(html=True) serves
    index.html at a root and this console has none -- its entry point is
    Entry.dc.html -- so without an explicit redirect the QR code lands a
    judge on a 404."""
    from fastapi.testclient import TestClient
    import citinel.web.app as app_mod

    if not app_mod.STATIC_DIR.is_dir():
        import pytest
        pytest.skip("console not present in this checkout")
    r = TestClient(app_mod.app).get("/", follow_redirects=False)
    assert r.status_code in (307, 308)
    assert r.headers["location"].endswith("Entry.dc.html")


def test_console_files_are_always_revalidated_but_api_is_left_alone():
    """DEPLOY.md's stale-file defect, closed at the server: every console file
    is served `Cache-Control: no-cache` so a browser revalidates it on each
    load (a 304 via ETag, not a re-download), while JSON routes carry no such
    header. Without this, a browser that saw yesterday's api.js keeps it for
    hours after a deploy and silently renders the old wiring."""
    import citinel.web.app as app_mod

    if not app_mod.STATIC_DIR.is_dir():
        pytest.skip("dashboard/static not present in this checkout")
    ui = client.get("/api.js")
    assert ui.status_code == 200
    assert ui.headers.get("cache-control") == "no-cache"
    api = client.get("/api/policy")
    assert api.status_code == 200
    assert "cache-control" not in api.headers
