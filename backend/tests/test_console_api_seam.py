"""The console's seam registry, checked against the routes that actually exist.

Four routes shipped with no entry in dashboard/static/api.js, so no screen could
reach them: the registry is hand-maintained and nothing held it to the router.
These tests close that by evaluating api.js's own path functions in node and
asking Starlette whether each result resolves -- a typo or a renamed route fails
here instead of silently painting DEMO DATA on a screen that had a route all along.
"""

from __future__ import annotations

import json
import shutil
import subprocess

import pytest
from starlette.routing import Match, Mount

import citinel.web.app as app_mod
from citinel.web.app import app

# Sample arguments the path functions are called with. Any slash-free value works:
# the assertion is on which route template matches, never on the value.
_EXTRACT_JS = r"""
global.window = {};
global.document = { readyState: 'complete',
                    querySelector: function () { return null; },
                    addEventListener: function () {} };
global.location = { search: '' };
global.setInterval = function () { return 0; };
global.clearInterval = function () {};
new Function(require('fs').readFileSync(process.argv[2], 'utf8'))();
var API = global.window.CITINEL_API;
var out = [];
Object.keys(API.ENDPOINTS).forEach(function (name) {
  var ep = API.ENDPOINTS[name];
  out.push({ name: name, live: !!ep.live, method: ep.method || 'GET',
             url: ep.path('INC-0417', 'certin') });
});
out.sort(function (a, b) { return a.name < b.name ? -1 : 1; });
console.log(JSON.stringify({
  endpoints: out,
  pages: API.PAGES,
  wrappers: ['briefFor', 'requestBrief', 'visualsFor', 'readVisual',
             'n8nExecutions', 'startupedSignals'].filter(
    function (f) { return typeof API[f] === 'function'; })
}));
"""


@pytest.fixture(scope="module")
def seam(tmp_path_factory) -> dict:
    if not app_mod.STATIC_DIR.is_dir():
        pytest.skip("dashboard/static not present in this checkout")
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available; api.js cannot be evaluated here")
    script = tmp_path_factory.mktemp("seam") / "extract.js"
    script.write_text(_EXTRACT_JS)
    api_js = app_mod.STATIC_DIR / "api.js"
    r = subprocess.run([node, str(script), str(api_js)],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"api.js did not evaluate under node:\n{r.stderr}"
    return json.loads(r.stdout)


def _resolves(method: str, path: str) -> bool:
    """Does a real API route serve this path?

    The static Mount that serves the console answers any GET path at all, so
    counting it here would make every GET assertion below pass unconditionally --
    including one pointed at a route that does not exist. Mounts are excluded on
    purpose; test_the_route_check_can_actually_fail holds that line.
    """
    scope = {"type": "http", "method": method, "path": path,
             "headers": [], "root_path": "", "query_string": b""}
    return any(route.matches(scope)[0] is Match.FULL
               for route in app.routes if not isinstance(route, Mount))


def test_the_route_check_can_actually_fail():
    assert _resolves("GET", "/api/policy")
    assert not _resolves("GET", "/api/no-such-route")
    assert not _resolves("POST", "/api/policy")


def test_every_live_endpoint_points_at_a_route_that_exists(seam):
    """`live: true` is a claim about the running service. A registry entry whose
    path resolves to nothing sends the screen to a 404 and the reader to a badge
    that blames the page."""
    broken = [
        f"{e['name']}: {e['method']} {e['url']}"
        for e in seam["endpoints"]
        if e["live"] and not _resolves(e["method"], e["url"].split("?")[0])
    ]
    assert not broken, "seam entries with no matching route: " + "; ".join(broken)


@pytest.mark.parametrize("name,method,path", [
    ("brief", "GET", "/api/incidents/INC-0417/brief"),
    ("briefStart", "POST", "/api/incidents/INC-0417/brief"),
    ("visual", "GET", "/api/incidents/INC-0417/visual"),
    ("visualRead", "POST", "/api/incidents/INC-0417/visual"),
    ("n8nExecutions", "GET", "/api/n8n/executions"),
    ("startupedSignals", "GET", "/api/startuped/signals"),
])
def test_the_four_late_routes_are_in_the_seam(seam, name, method, path):
    """Regression on the omission itself: a route can exist and still be
    unreachable from every screen, which is the state these four were in."""
    entry = next((e for e in seam["endpoints"] if e["name"] == name), None)
    assert entry is not None, f"{name} is missing from api.js ENDPOINTS"
    assert entry["live"] is True
    assert entry["method"] == method
    assert entry["url"].split("?")[0] == path
    assert _resolves(method, path)


def test_the_new_reads_are_declared_by_the_pages_that_show_them(seam):
    """The badge counts only what a page declares, so an endpoint absent from
    PAGES.uses can be read live and still report DEMO DATA."""
    pages = seam["pages"]
    assert "brief" in pages["replay"]["uses"]
    assert "visual" in pages["replay"]["uses"]
    assert "n8nExecutions" in pages["audit"]["uses"]
    assert "startupedSignals" in pages["settings"]["uses"]


def test_page_registry_names_only_endpoints_that_exist(seam):
    """A typo in PAGES.uses is invisible at runtime: verdictFor() skips unknown
    names, so the page quietly reports a smaller denominator than it declares."""
    known = {e["name"] for e in seam["endpoints"]}
    unknown = [f"{page} -> {u}" for page, cfg in seam["pages"].items()
               for u in cfg["uses"] if u not in known]
    assert not unknown, "PAGES.uses names no such endpoint: " + "; ".join(unknown)


def test_the_wrappers_the_pages_will_call_are_defined(seam):
    """Pages call the wrappers, not API.get by name; a missing one is a TypeError
    inside a render."""
    assert seam["wrappers"] == ["briefFor", "requestBrief", "visualsFor",
                                "readVisual", "n8nExecutions", "startupedSignals"]
