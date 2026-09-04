"""A wrong address on the console gets the console's own 404, not a JSON stub.

StaticFiles is mounted at "/" as a catch-all, and until the exception
handler in web/app.py existed a mistyped screen name (or a stale bookmark,
or a QR code with a typo) answered with FastAPI's raw {"detail": "Not Found"}.
The console now serves dashboard/static/404.dc.html for any non-API 404,
while /api/* and /healthz keep the JSON contract every machine caller, the
demo-capture fixtures and the rest of this suite rely on.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import citinel.web.app as app_mod

client = TestClient(app_mod.app)


def _needs_console() -> None:
    if not app_mod.STATIC_DIR.is_dir() or not (app_mod.STATIC_DIR / "404.dc.html").is_file():
        pytest.skip("dashboard/static (with 404.dc.html) not present in this checkout")


def test_unknown_console_path_gets_the_branded_page():
    _needs_console()
    r = client.get("/definitely-not-a-page")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("text/html")
    # Same revalidation rule as every other console file (DEPLOY.md's
    # stale-file defect): a redeployed 404 page must not be served from a
    # heuristic browser cache either.
    assert r.headers.get("cache-control") == "no-cache"
    assert "CITINEL" in r.text
    assert "Overview.dc.html" in r.text
    for screen in ("Queue.dc.html", "Audit.dc.html", "Overview.dc.html"):
        assert screen in r.text, f"404 page should link to {screen}"


def test_nested_unknown_path_gets_the_same_page():
    """A deep wrong path must get the page too -- and the page carries
    <base href="/"> precisely so its relative sheet/script/asset references
    resolve against the console root from any depth."""
    _needs_console()
    r = client.get("/some/deep/nonsense/path")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("text/html")
    assert '<base href="/">' in r.text


def test_api_404_keeps_the_json_contract(sandbox):
    """Machine callers (api.js, fixtures, this suite) read r.json()["detail"]
    on a 404 and must never be handed an HTML document instead."""
    r = client.get("/api/incidents/NOPE-0000")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/json")
    assert "detail" in r.json()
    assert "NOPE-0000" in r.json()["detail"]


def test_healthz_is_untouched():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "citinel-web"}


def test_a_real_screen_is_still_served():
    _needs_console()
    r = client.get("/Overview.dc.html")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert 'data-citinel-page="overview"' in r.text
