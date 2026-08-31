"""CITINEL's combined web service: the glass-box dashboard + the API, one process.

This is the actual Render "web" service entry point (deploy/render.yaml's own
comment: "web: glass-box dashboard + API" -- one service, not two). It exists
as a separate top-level module, not inside backend/citinel/, because the
dashboard's static files are themselves a top-level project component
(HANDOFF.md, the export from Claude Design) -- this file is just the seam
that serves them on the same origin as the real API, so api.js's same-origin
fetch calls need no CORS configuration and no base-URL override.

Single source of truth for API routes: this module adds nothing to
`citinel.web.app`'s app object except the static mount and the root redirect.
citinel/web/app.py stays importable standalone (tests/test_web.py exercises
it directly, with no static files involved) -- mounting here, in a module
that imports it, cannot change that file's own behavior.

Route ordering matters and is safe here: `/healthz` and `/api/*` are already
registered on `app` by the time this module imports it, and Starlette matches
routes in registration order -- the static mount added below can only ever
catch what those explicit routes don't.
"""

from __future__ import annotations

from pathlib import Path

from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from citinel.web.app import app

STATIC_DIR = Path(__file__).resolve().parent / "static"
ENTRY_POINT = "Entry.dc.html"


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """HANDOFF.md names Entry.dc.html as the entry point; there is no index.html."""
    return RedirectResponse(url=f"/{ENTRY_POINT}")


# Registered last, so it only ever catches what /healthz and /api/* don't.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="dashboard")
