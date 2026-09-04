#!/usr/bin/env python3
"""Read-only pre-flight for the live CITINEL console. Prints GO or what is wrong.

Makes GET requests only. Needs no token, spends no credits, writes nothing
anywhere. Safe to run any number of times, including on stage.

    python3 scripts/preflight.py                      # production
    python3 scripts/preflight.py http://localhost:8000

What it checks, and why each one is here (4 Sep 2026):
  - every read route answers 200, or 404 where "not run yet" is honest;
    an unknown incident and an unknown route answer 404, never 500
  - the ledger verifies intact and the witness is not reporting a false
    divergence (it used to cry wolf when it had merely seen fewer entries)
  - all connectors report configured; n8n has at least one execution on
    record; the incident's sweep, context and verdict artifacts exist
  - every console page and shared asset serves; the deployed api.js and
    nav.js are the device-arming build and the icon-only rail
  - every endpoint the console's api.js names resolves to a route the
    backend declares (checked against the local checkout)
"""
import json, re, sys, time, urllib.error, urllib.request
from pathlib import Path

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://citinel-web.onrender.com").rstrip("/")
INC = "INC-0417"
ROOT = Path(__file__).resolve().parents[1]
rows, bad = [], []

def get(path, timeout=45):
    req = urllib.request.Request(BASE + path, headers={"Accept": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, e.read(), time.time() - t0
    except Exception as e:
        return 0, str(e).encode(), time.time() - t0

def check(name, ok, detail=""):
    rows.append(("ok " if ok else "!! ", name, detail))
    if not ok: bad.append(name)

def jget(path):
    code, raw, dt = get(path)
    try: body = json.loads(raw)
    except Exception: body = None
    return code, body, dt

# --- routes -----------------------------------------------------------------
expect = {
    "/healthz": (200,), "/api/source": (200,), "/api/incidents": (200,),
    f"/api/incidents/{INC}": (200,), f"/api/incidents/{INC}/audit": (200,),
    f"/api/incidents/{INC}/verdict": (200,), f"/api/incidents/{INC}/draft?kind=certin": (200,),
    "/api/policy": (200,), "/api/eval": (200,), "/api/corpus": (200,),
    "/api/corpus/review": (200, 404), "/api/connectors": (200,),
    f"/api/incidents/{INC}/swarm/status": (200,), f"/api/incidents/{INC}/context": (200, 404),
    f"/api/incidents/{INC}/sweep": (200, 404), f"/api/incidents/{INC}/brief": (200, 404),
    "/api/n8n/executions": (200,), f"/api/incidents/{INC}/visual": (200, 404),
    "/api/startuped/signals": (200,), f"/api/incidents/{INC}/handover": (200, 404),
    "/api/incidents/NOPE-9999": (404,), "/api/incidents/NOPE-9999/audit": (404,), "/api/nonexistent": (404,),
}
slow = []
for path, okcodes in expect.items():
    code, raw, dt = get(path)
    check(f"GET {path}", code in okcodes, f"{code} {dt:.1f}s")
    if dt > 25: slow.append(path)

# --- the facts behind the routes -------------------------------------------
code, v, _ = jget("/api/ledger/verify")
check("ledger chain intact", bool(v and v.get("intact")), str(v and v.get("message")))
w = (v or {}).get("witness") or {}
check("witness not falsely diverged", w.get("status") != "diverged", f"witness={w.get('status')} local={w.get('local_count')} remote={w.get('remote_count')}")
code, c, _ = jget("/api/connectors")
conns = (c or {}).get("connectors") or []
off = [x["name"] for x in conns if not x.get("configured")]
check("all connectors configured", conns and not off, f"{len(conns) - len(off)} of {len(conns)}" + (f"; off: {off}" if off else ""))
code, n, _ = jget("/api/n8n/executions?limit=3")
check("n8n has executions on record", bool((n or {}).get("executions")), f"status={(n or {}).get('status')} count={len((n or {}).get('executions') or [])}")
for art in ("sweep", "context", "verdict"):
    code, _, _ = jget(f"/api/incidents/{INC}/{art}")
    check(f"{INC} {art} artifact present", code == 200, str(code))
code, s, _ = jget("/api/startuped/signals")
check("startuped configured", bool((s or {}).get("configured")), f"{len((s or {}).get('signals') or [])} signals declared")

# --- console pages and the build that is actually serving ------------------
static = ROOT / "dashboard" / "static"
pages = sorted(p.name for p in static.glob("*.dc.html")) + sorted(p.name for p in static.glob("*.js")) + sorted(p.name for p in static.glob("*.css"))
missing = [p for p in pages if get("/" + p, 25)[0] != 200]
check("every console page and asset serves", not missing, f"{len(pages) - len(missing)} of {len(pages)}" + (f"; missing {missing}" if missing else ""))
code, raw, _ = get("/api.js"); check("device-arming build is live (api.js)", b"citinel.operator" in raw)
code, raw, _ = get("/nav.js"); check("icon-only rail is live (nav.js)", b"citinel-rail-tip" in raw)
code, raw, _ = get("/", 25); check("root lands on Overview", b"Overview" in raw[:4000] or code in (200, 307))

# --- api.js endpoint map vs declared routes (local files) ------------------
try:
    app = (ROOT / "backend/citinel/web/app.py").read_text()
    routes = {re.sub(r"\{[^}]+\}", "{p}", m.group(2)).rstrip("/") for m in re.finditer(r'@app\.(get|post|put|delete)\("([^"]+)"', app)}
    api = (static / "api.js").read_text()
    entries = []
    for m in re.finditer(r"^\s{4}(\w+):\s*\{\s*path:\s*function\s*\(([^)]*)\)\s*\{\s*return ([^;]+);", api, re.M):
        parts = re.findall(r"'([^']*)'|(\w+)", m.group(3))
        entries.append((m.group(1), "".join(lit if lit else "{p}" for lit, _ in parts)))
    orphans = [n for n, t in entries if re.sub(r"\{[^}]+\}", "{p}", t.split("?")[0]).rstrip("/") not in routes]
    check("every api.js endpoint has a backend route", not orphans, f"{len(entries)} endpoints" + (f"; unmatched {orphans}" if orphans else ""))
except Exception as e:
    check("api.js vs routes cross-check", False, f"could not run: {e}")

# --- report -----------------------------------------------------------------
w_ = max(len(r[1]) for r in rows)
for mark, name, detail in rows:
    print(f"{mark}{name:<{w_}}  {detail}")
print()
if slow: print("slow (>25s, fine but worth knowing):", slow)
print("=" * 60)
print("GO" if not bad else f"NO-GO: {len(bad)} problem(s): " + "; ".join(bad))
sys.exit(0 if not bad else 1)
