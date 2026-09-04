"""Every asset the left rail names must exist and be served.

nav.js builds the rail in JavaScript, so the brand mark it references is a
string in a script rather than a `<img>` in a page the console tests already
walk. A typo or a renamed file therefore fails nowhere: no route 404s, no test
notices, and the rail simply paints an empty box in the top-left corner of
every screen -- on a laptop that has never loaded the old file, which is
exactly the demo laptop. These tests hold nav.js to the files on disk.

The `<picture>` pairing is checked too. The rail serves webp with a png
fallback; losing the png would show nothing at all in a browser without webp,
and losing the webp would quietly ship the heavier file to everyone.
"""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

import citinel.web.app as app_mod

client = TestClient(app_mod.app)

_TYPES = {".png": "image/png", ".webp": "image/webp"}


def _nav_js() -> str:
    if not app_mod.STATIC_DIR.is_dir() or not (app_mod.STATIC_DIR / "nav.js").is_file():
        pytest.skip("dashboard/static (with nav.js) not present in this checkout")
    return (app_mod.STATIC_DIR / "nav.js").read_text(encoding="utf-8")


def _referenced(nav: str) -> list[str]:
    return sorted(set(re.findall(r"'(assets/[A-Za-z0-9._/-]+)'", nav)))


def test_rail_names_at_least_the_two_marks():
    """Open shows the lockup, closed shows the falcon. Both are load-bearing."""
    refs = _referenced(_nav_js())
    assert refs, "nav.js references no assets at all; the rail lost its brand mark"
    assert any("mark-white" in r for r in refs), f"no lockup for the open rail: {refs}"
    assert any("falcon" in r for r in refs), f"no falcon for the collapsed rail: {refs}"


def test_every_asset_the_rail_names_exists_on_disk():
    for ref in _referenced(_nav_js()):
        path = app_mod.STATIC_DIR / ref
        assert path.is_file(), f"nav.js references {ref}, which is not in dashboard/static"
        assert path.stat().st_size > 0, f"{ref} is empty"


def test_every_asset_the_rail_names_is_served():
    for ref in _referenced(_nav_js()):
        r = client.get("/" + ref)
        assert r.status_code == 200, f"GET /{ref} answered {r.status_code}"
        expected = _TYPES.get(ref[ref.rfind("."):])
        if expected:
            assert r.headers["content-type"].startswith(expected), \
                f"/{ref} served as {r.headers['content-type']}, expected {expected}"


def test_each_mark_ships_both_a_webp_and_a_png():
    """A <source type=image/webp> with no <img> fallback paints nothing where
    webp is unsupported; a png with no webp ships the heavy file to everyone."""
    refs = _referenced(_nav_js())
    stems = {r[: r.rfind(".")] for r in refs if r.endswith((".png", ".webp"))}
    for stem in sorted(stems):
        assert stem + ".webp" in refs, f"{stem} is named without its webp source"
        assert stem + ".png" in refs, f"{stem} is named without its png fallback"


def test_the_collapsed_rail_does_not_ship_the_full_size_falcon():
    """falcon-white.png is 236 KB for a 24px icon in a rail that loads on every
    screen. The rail must name a downscaled copy, not the master artwork."""
    for ref in _referenced(_nav_js()):
        size = (app_mod.STATIC_DIR / ref).stat().st_size
        assert size <= 64_000, \
            f"{ref} is {size} bytes; the rail loads on every screen, use a downscaled copy"
