#!/usr/bin/env python3
"""Exercise every partner seam against a live CITINEL deployment, then read
back what actually landed.

A deployed console that has never been written to shows a judge empty panels:
no context, no sweep, no brief, no handover, no Swytchcode receipts. Every one
of those panels is filled by an authenticated POST, and until now filling them
meant a person remembering nine curl commands and the right confirm bodies.

The tool is deliberately paranoid about honesty. A step that could not run
because the deployment lacks a partner key is SKIPPED, not PASS -- it did not
land, and a summary that says otherwise is worse than no summary. A step that
returns HTTP 200 while the seam inside it reports `not_configured` is likewise
SKIPPED, because the panel stays empty either way. The closing SUMMARY does not
trust any of the step results: it re-reads the ledger and the artifact routes
from the deployment itself and reports what is there now.

Standard library only, so it runs on a bare box with no install step.

    export CITINEL_WRITE_TOKEN=...          # never a command-line argument
    python3 scripts/exercise_production.py
    python3 scripts/exercise_production.py --base-url http://localhost:8010
    python3 scripts/exercise_production.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "https://citinel-web.onrender.com"
WRITE_HEADER = "X-Citinel-Write-Token"

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIPPED"

#: Tavily Research states that mean "still working". Only "pending" is one the
#: deployment will poll again; the rest are a stuck artifact, see step_brief.
_BRIEF_IN_FLIGHT = ("in_progress", "queued", "running", "started", "processing")

#: Ledger actors that prove a partner seam ran. Read back in the summary rather
#: than inferred from step results, because a POST returning 200 is a claim and
#: a frame on the hash chain is the evidence for it.
PARTNER_ACTORS = {
    "gemini-sweep": "Gemini (long-context sweep)",
    "gemini-vision": "Gemini (vision)",
    "swytchcode": "Swytchcode (ticketing + comms)",
    "lyzr-triage": "Lyzr (triage lane)",
    "lyzr-verdict": "Lyzr (citation second opinion)",
    "lyzr-response": "Lyzr (proportionality review)",
    "n8n": "n8n (playbook)",
    "policy-gate": "CITINEL policy gate",
    "response-marshal": "CITINEL response marshal",
}


class Deployment:
    """Thin urllib client. The write token goes on writes only -- a read that
    does not need the credential should not carry it."""

    def __init__(self, base_url: str, token: str, timeout: float) -> None:
        self.base = base_url.rstrip("/")
        self._token = token
        self.timeout = timeout

    def redact(self, text: str) -> str:
        """Last line of defence before anything reaches stdout. The token is
        never printed by construction, but a deployment could echo it back in
        an error body, and CI logs are forever."""
        if self._token and self._token in text:
            return text.replace(self._token, "<redacted>")
        return text

    def request(self, method: str, path: str, body: Any = None,
                timeout: float | None = None) -> tuple[int, Any]:
        """Returns (status, parsed body). A transport failure is status 0 with
        the reason as the body, so callers never have to catch."""
        url = f"{self.base}{path}"
        data = None
        headers = {"Accept": "application/json"}
        if method != "GET":
            data = json.dumps(body or {}).encode("utf-8")
            headers["Content-Type"] = "application/json"
            headers[WRITE_HEADER] = self._token
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as r:
                raw = r.read().decode("utf-8", "replace")
                return r.status, _parse(raw)
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            return e.code, _parse(raw)
        except Exception as e:  # URLError, socket.timeout, ssl errors
            return 0, {"detail": f"{type(e).__name__}: {e}"}


def _parse(raw: str) -> Any:
    try:
        return json.loads(raw)
    except ValueError:
        return {"detail": raw[:400]}


def _state_of(v: Any) -> str:
    return str(v.get("state", "n/a")) if isinstance(v, dict) else str(v or "n/a")


def _detail(body: Any) -> str:
    if isinstance(body, dict):
        d = body.get("detail")
        if isinstance(d, (dict, list)):
            return json.dumps(d)[:300]
        if d:
            return str(d)[:300]
        return json.dumps(body)[:300]
    return str(body)[:300]


class Report:
    """Collects one line per step and decides the exit code."""

    def __init__(self, dep: Deployment) -> None:
        self.dep = dep
        self.rows: list[tuple[str, str, str, list[str]]] = []

    def record(self, verdict: str, name: str, call: str, notes: list[str]) -> str:
        self.rows.append((verdict, name, call, notes))
        n = len(self.rows)
        print(f"[{n}] {verdict:<7} {name}")
        print(f"          {self.dep.redact(call)}")
        for line in notes:
            print(f"          {self.dep.redact(line)}")
        print()
        return verdict

    @property
    def failed(self) -> int:
        return sum(1 for v, *_ in self.rows if v == FAIL)


def classify(status: int, body: Any) -> tuple[str, str] | None:
    """Map an HTTP result that is not a clean 2xx onto a verdict.

    The two 503s mean opposite things to an operator and must never be
    conflated: the write guard's 503 says the deployment refuses all writes,
    which is a hard stop, while a connector's 503 says one partner key is
    missing, which leaves the rest of the run meaningful.
    """
    if 200 <= status < 300:
        return None
    d = _detail(body)
    if status == 0:
        return FAIL, f"could not reach the deployment: {d}"
    if status == 401:
        return FAIL, ("token mismatch: the deployment has a CITINEL_WRITE_TOKEN "
                      "but it is not the one in your environment")
    if status == 503 and "CITINEL_WRITE_TOKEN" in d:
        return FAIL, ("write token not set on the deployment: CITINEL_WRITE_TOKEN "
                      "is unset there, so every write is refused (set it in the "
                      "service's environment, then redeploy)")
    if status == 503:
        return SKIP, f"deployment is missing a credential for this seam: {d}"
    return FAIL, f"HTTP {status}: {d}"


# --- the steps ----------------------------------------------------------------

def step_context(dep: Deployment, rep: Report, inc: str) -> None:
    call = f'POST /api/incidents/{inc}/context  {{"confirm": true}}'
    status, body = dep.request("POST", f"/api/incidents/{inc}/context",
                               {"confirm": True}, timeout=max(dep.timeout, 240))
    if (bad := classify(status, body)):
        rep.record(bad[0], "Tavily public context", call, [bad[1]])
        return
    queries = body.get("queries") or []
    prims = body.get("primitives_used") or []
    kinds = sorted({q.get("kind", "?") for q in queries})
    failed = [q for q in queries if q.get("status") != "ok"]
    notes = [
        f"primitives used: {', '.join(prims) or 'none'}  ({len(prims)} of 4 non-research)",
        f"query kinds: {', '.join(kinds) or 'none'}  ({len(queries)} queries)",
        f"{body.get('sources', 0)} search results, {body.get('pages_retrieved', 0)} "
        f"full pages retrieved, {body.get('credits_used', 0)} credits spent",
    ]
    if failed:
        notes.append(f"{len(failed)} query/queries did not return ok: "
                     + "; ".join(f"{q.get('kind')}={q.get('status')} {q.get('note','')}"[:90]
                                 for q in failed[:3]))
    # A missing primitive is the interesting case and the reason is in the
    # sub-call's own note, not in the query status -- map and crawl are a paid
    # Tavily tier, and a key without them returns 401 while search still works.
    missing = [p for p in ("search", "extract", "map", "crawl") if p not in prims]
    if missing:
        notes.append(f"not reached: {', '.join(missing)}")
        seen = set()
        for q in queries:
            for sub in ("attack_detail", "extracted"):
                note = (q.get(sub) or {}).get("note")
                if note and (sub, note) not in seen:
                    seen.add((sub, note))
                    notes.append(f"  {sub}: {note}")
    verdict = PASS if prims and not failed else (SKIP if not prims else FAIL)
    rep.record(verdict, "Tavily public context", call, notes)


def step_sweep(dep: Deployment, rep: Report, inc: str) -> None:
    call = f'POST /api/incidents/{inc}/sweep  {{"confirm": true}}'
    status, body = dep.request("POST", f"/api/incidents/{inc}/sweep",
                               {"confirm": True}, timeout=max(dep.timeout, 300))
    if (bad := classify(status, body)):
        rep.record(bad[0], "Gemini wide-lens sweep", call, [bad[1]])
        return
    inner = body.get("status", "")
    notes = [
        f"seam status: {inner}  model {body.get('model') or 'n/a'}",
        f"{body.get('findings_swept', 0)} of {body.get('findings_total', 0)} findings swept "
        f"(the investigation's own window reached {body.get('findings_examined', 0)})",
        f"blind-spot risk: {body.get('blind_spot_risk') or 'n/a'} · "
        f"{len(body.get('clusters') or [])} clusters, "
        f"{len(body.get('only_outside_window') or [])} outside-window items",
    ]
    if body.get("note"):
        notes.append(f"note: {body['note']}")
    verdict = {"ok": PASS, "not_configured": SKIP}.get(inner, FAIL)
    rep.record(verdict, "Gemini wide-lens sweep", call, notes)


def step_brief(dep: Deployment, rep: Report, inc: str, wait: float) -> None:
    call = (f'POST /api/incidents/{inc}/brief  {{"confirm": true}}'
            f'  then GET to advance (up to {int(wait)}s)')
    status, body = dep.request("POST", f"/api/incidents/{inc}/brief",
                               {"confirm": True}, timeout=max(dep.timeout, 180))
    if (bad := classify(status, body)):
        rep.record(bad[0], "Tavily Research brief", call, [bad[1]])
        return
    notes = [f"started: status {body.get('status')}, "
             f"request id {'present' if body.get('request_id') else 'absent'}"]
    if body.get("question"):
        notes.append(f"question: {str(body['question'])[:160]}")

    # The GET is the advance step, not a courtesy read: poll_brief() is what
    # moves a pending research run to completed and persists it.
    deadline = time.monotonic() + wait
    polls = 0
    while body.get("status") == "pending" and time.monotonic() < deadline:
        time.sleep(min(10.0, max(1.0, deadline - time.monotonic())))
        polls += 1
        gs, gb = dep.request("GET", f"/api/incidents/{inc}/brief")
        if 200 <= gs < 300:
            body = gb
        else:
            notes.append(f"poll failed: HTTP {gs} {_detail(gb)}")
            break
    final = body.get("status")
    notes.append(f"after {polls} advancing GET(s): status {final}, "
                 f"{len(body.get('content') or '')} chars, "
                 f"{len(body.get('sources') or [])} cited sources")
    if body.get("note"):
        notes.append(f"note: {body['note']}")
    if final in ("completed", "success", "ok"):
        verdict = PASS
    elif final == "pending":
        verdict = SKIP
        notes.append("still running at the deadline; the artifact exists and the "
                     "console's own GET will advance it -- raise --brief-wait to "
                     "watch it finish here")
    elif final in _BRIEF_IN_FLIGHT:
        # Confirmed against a live deployment 4 Sep 2026: Tavily answers the
        # first poll with "in_progress", poll_brief() stores that verbatim, and
        # every later GET short-circuits because it only re-polls on exactly
        # "pending". The brief panel then sits at in_progress forever. Reported
        # here rather than papered over -- no amount of polling from this side
        # moves it, so more waiting would only look like progress.
        verdict = SKIP
        notes.append(f"Tavily is still working, but the deployment stored "
                     f"{final!r} and only re-polls a brief whose stored status is "
                     f"exactly 'pending' -- so this artifact will not advance from "
                     f"a GET again. The panel shows {final}, not a finished brief.")
    else:
        verdict = FAIL
    rep.record(verdict, "Tavily Research brief", call, notes)


def step_draft(dep: Deployment, rep: Report, inc: str) -> None:
    call = f"GET /api/incidents/{inc}/draft?kind=certin"
    status, body = dep.request("GET", f"/api/incidents/{inc}/draft?kind=certin",
                               timeout=max(dep.timeout, 180))
    if (bad := classify(status, body)):
        rep.record(bad[0], "Lyzr draft review + PII guard", call, [bad[1]])
        return
    guard = body.get("guard") or {}
    review = body.get("review") or {}
    rstat = review.get("status", "absent")
    # The guard's findings carry masked identifiers. Only the types are printed:
    # a mask is a mitigation, not a licence to copy PII into a CI log.
    types = sorted({f.get("pii_type", "?") for f in (guard.get("findings") or [])})
    notes = [
        f"CITINEL PII guard: clean={guard.get('clean')} via {guard.get('checked_by', 'n/a')} · "
        f"{len(guard.get('findings') or [])} flag(s)"
        + (f" [{', '.join(types)}]" if types else ""),
        f"Lyzr draft review: {rstat} · {len(review.get('thin') or [])} field(s) called thin",
        f"rendered artifact: {len(body.get('rendered') or '')} chars",
        "Startuped signal citinel-reports-drafted emitted by this route",
    ]
    if review.get("summary"):
        notes.append(f"reviewer: {str(review['summary'])[:200]}")
    for t in (review.get("thin") or [])[:3]:
        notes.append(f"  thin: {t.get('key', '?')} — {str(t.get('why', ''))[:120]}")
    if review.get("detail"):
        notes.append(f"detail: {review['detail']}")
    if rstat in ("not_configured", "unavailable", "absent"):
        verdict = SKIP
        notes.append("the panel stays empty until the review agent id is set on "
                     "the deployment; the guard above is CITINEL's own and ran")
    else:
        verdict = PASS
    rep.record(verdict, "Lyzr draft review + PII guard", call, notes)


def step_corpus_review(dep: Deployment, rep: Report) -> None:
    call = 'POST /api/corpus/review  {"confirm": true}'
    status, body = dep.request("POST", "/api/corpus/review", {"confirm": True},
                               timeout=max(dep.timeout, 180))
    if (bad := classify(status, body)):
        rep.record(bad[0], "Lyzr corpus advisor", call, [bad[1]])
        return
    st = body.get("status", "absent")
    gaps = body.get("gaps") or []
    notes = [f"advisory status: {st} · {len(gaps)} coverage gap(s) named",
             f"written_at: {body.get('written_at', 'n/a')}"]
    if body.get("summary"):
        notes.append(f"advisory: {str(body['summary'])[:220]}")
    for g in gaps[:3]:
        notes.append(f"  gap: {g.get('area', '?')} — {str(g.get('why', ''))[:120]}")
    if body.get("detail"):
        notes.append(f"detail: {body['detail']}")
    verdict = SKIP if st in ("not_configured", "unavailable", "absent") else PASS
    rep.record(verdict, "Lyzr corpus advisor", call, notes)


def step_handover(dep: Deployment, rep: Report, inc: str) -> None:
    call = f'POST /api/incidents/{inc}/handover  {{"confirm": true}}'
    status, body = dep.request("POST", f"/api/incidents/{inc}/handover",
                               {"confirm": True}, timeout=max(dep.timeout, 180))
    if (bad := classify(status, body)):
        rep.record(bad[0], "Lyzr handover writer", call, [bad[1]])
        return
    st = body.get("status", "absent")
    notes = [f"note status: {st}",
             f"state {_state_of(body.get('state'))} · written from "
             f"{body.get('frames_used', 0)} ledger frames · "
             f"{len(body.get('open_items') or [])} open item(s)"]
    if body.get("summary"):
        notes.append(f"note: {str(body['summary'])[:220]}")
    for item in (body.get("open_items") or [])[:3]:
        notes.append(f"  open: {str(item)[:120]}")
    if body.get("detail"):
        notes.append(f"detail: {body['detail']}")
    verdict = SKIP if st in ("not_configured", "unavailable", "absent") else PASS
    rep.record(verdict, "Lyzr handover writer", call, notes)


def step_execute(dep: Deployment, rep: Report, inc: str, target: str) -> None:
    """isolate_host is the deliberate choice: policy clause 3.1 is tier assist
    with max_assets_auto 1, so a single-host proposal clears the gate on its
    own and actually executes -- which is what makes Swytchcode fire. A class
    the gate holds for approval would leave the receipts panel empty."""
    payload = {"incident_id": inc, "action_class": "isolate_host",
               "target": target, "assets_affected": 1}
    call = f"POST /api/actions/execute  isolate_host on {target} (assets_affected 1)"
    status, body = dep.request("POST", "/api/actions/execute", payload,
                               timeout=max(dep.timeout, 180))
    if status == 403:
        # A denial is the gate working, but nothing executed, so no receipts.
        rep.record(SKIP, "Policy gate + Swytchcode", call,
                   [f"the gate denied it: {_detail(body)}",
                    "gate frame written; no execution, so no Swytchcode receipts"])
        return
    if (bad := classify(status, body)):
        rep.record(bad[0], "Policy gate + Swytchcode", call, [bad[1]])
        return
    dec = body.get("decision") or {}
    receipt = body.get("receipt") or {}
    swytch = body.get("swytchcode") or []
    lyzr = body.get("lyzr_response_review") or {}
    notes = [
        f"gate verdict {dec.get('verdict', 'n/a')} under clause "
        f"{dec.get('clause_ref', 'n/a')} ({dec.get('engine', 'n/a')}) · "
        f"receipt {receipt.get('status', 'n/a')}, simulated={receipt.get('simulated')}",
        f"Swytchcode: {len(swytch)} receipt(s) — "
        + (" · ".join(f"{r.get('ecosystem_api', '?')}/{r.get('action', '?')}"
                      f"={r.get('status', '?')}" for r in swytch) or "none"),
        f"Lyzr proportionality review: {lyzr.get('status', 'absent')}"
        + (f" — {lyzr.get('assessment')}" if lyzr.get("assessment") else ""),
        # derive_state() returns the state plus the frames it was derived from;
        # only the state itself belongs on a one-line report.
        f"incident state now {_state_of(body.get('state'))} · "
        "Startuped signal citinel-actions-gated emitted",
    ]
    if lyzr.get("rationale"):
        notes.append(f"  rationale: {str(lyzr['rationale'])[:160]}")
    for r in swytch:
        if r.get("detail"):
            notes.append(f"  {r.get('ecosystem_api', '?')}: {str(r['detail'])[:140]}")
    if receipt.get("rollback_token"):
        notes.append("rollback token issued (value withheld from this log)")
    executed = receipt.get("status") == "executed"
    landed = [r for r in swytch if r.get("status") == "executed"]
    # Not a FAIL either way: the gate deciding and the action running is the
    # safety claim, and it held. Swytchcode going unauthenticated leaves the
    # receipts panel empty, which is a deployment gap, not a broken product.
    verdict = PASS if executed and landed else SKIP
    if executed and not landed:
        notes.append("the action executed, but no Swytchcode receipt came back "
                     "executed — that panel stays empty")
    rep.record(verdict, "Policy gate + Swytchcode", call, notes)


def step_n8n(dep: Deployment, rep: Report) -> None:
    call = "GET /api/n8n/executions"
    status, body = dep.request("GET", "/api/n8n/executions")
    if (bad := classify(status, body)):
        rep.record(bad[0], "n8n read path", call, [bad[1]])
        return
    st = body.get("status", "absent")
    runs = body.get("executions") or []
    notes = [f"connector status: {st} · {len(runs)} execution(s) readable"]
    if body.get("detail"):
        notes.append(f"detail: {body['detail']}")
    for r in runs[:3]:
        notes.append(f"  run {r.get('id', '?')} {r.get('status', '?')} "
                     f"{r.get('started_at', r.get('startedAt', ''))}")
    if st == "not_configured":
        verdict = SKIP
    elif st == "error":
        verdict = FAIL
    elif not runs:
        verdict = SKIP
        notes.append("reachable, but n8n has no runs to show — the panel is empty "
                     "until a playbook actually fires (sign off an incident)")
    else:
        verdict = PASS
    rep.record(verdict, "n8n read path", call, notes)


def step_startuped(dep: Deployment, rep: Report) -> None:
    call = "GET /api/startuped/signals"
    status, body = dep.request("GET", "/api/startuped/signals")
    if (bad := classify(status, body)):
        rep.record(bad[0], "Startuped signals", call, [bad[1]])
        return
    signals = body.get("signals") or []
    notes = [
        f"configured: {body.get('configured')} · {len(signals)} signal(s) declared",
        "keys: " + ", ".join(s.get("signal_key", "?") for s in signals),
        "this route declares what is sent; it exposes no send counter, so it "
        "cannot confirm the emissions the steps above triggered",
    ]
    verdict = PASS if signals and body.get("configured") else SKIP
    if not body.get("configured"):
        notes.append("no Startuped key on the deployment — emissions are no-ops")
    rep.record(verdict, "Startuped signals", call, notes)


# --- summary ------------------------------------------------------------------

def summarise(dep: Deployment, inc: str) -> None:
    print("=" * 78)
    print("SUMMARY — read back from the live deployment, not from the steps above")
    print("=" * 78)
    print()

    status, chain = dep.request("GET", f"/api/incidents/{inc}/audit")
    print(f"ledger frames on {inc}  (GET /api/incidents/{inc}/audit -> {status})")
    if 200 <= status < 300 and isinstance(chain, list):
        counts: dict[str, int] = {}
        for e in chain:
            a = e.get("actor", "?")
            counts[a] = counts.get(a, 0) + 1
        print(f"  {len(chain)} frames total")
        for actor, label in PARTNER_ACTORS.items():
            n = counts.get(actor, 0)
            mark = "yes" if n else " no"
            print(f"  [{mark}] {actor:<18} {n:>4}  {label}")
        print("  [--] tavily             n/a  Tavily writes no ledger frame by design; "
              "its evidence is the context/brief artifact, checked below")
    else:
        print(f"  unavailable: {dep.redact(_detail(chain))}")
    print()

    print("artifact routes a judge would click (GET, after the run):")
    for label, path in (
        ("public context", f"/api/incidents/{inc}/context"),
        ("wide-lens sweep", f"/api/incidents/{inc}/sweep"),
        ("research brief", f"/api/incidents/{inc}/brief"),
        ("handover note", f"/api/incidents/{inc}/handover"),
        ("corpus advisory", "/api/corpus/review"),
        ("swarm verdict", f"/api/incidents/{inc}/verdict"),
    ):
        st, b = dep.request("GET", path)
        extra = ""
        if 200 <= st < 300 and isinstance(b, dict):
            inner = b.get("status")
            bits = [f"status {inner}"] if inner else []
            for k in ("gathered_at", "fetched_at", "written_at"):
                if b.get(k):
                    bits.append(str(b[k]))
                    break
            extra = "  " + " · ".join(bits) if bits else ""
        elif st == 404:
            extra = "  nothing to show — this panel is still empty"
        else:
            extra = f"  {dep.redact(_detail(b))}"
        print(f"  {st:>3}  {label:<16} {path}{extra}")
    print()

    st, b = dep.request("GET", "/api/ledger/verify")
    if 200 <= st < 300 and isinstance(b, dict):
        print(f"ledger integrity: intact={b.get('intact')} — {b.get('message', '')}")
        w = b.get("witness") or {}
        if w:
            print(f"  witness: {w.get('status', 'n/a')} — "
                  f"{dep.redact(str(w.get('detail', ''))[:160])}")
    else:
        print(f"ledger integrity: unavailable (HTTP {st})")
    print()


# --- driver -------------------------------------------------------------------

def pick_incident(dep: Deployment, wanted: str | None) -> tuple[str, str] | None:
    """Resolve the incident to exercise and a host to isolate on it.

    The host must come from the incident actually being exercised, not from
    whichever record happens to be richest -- an isolate_host proposal naming
    a host from a different incident is a nonsense proposal that the gate would
    nonetheless wave through, and the receipt would name the wrong machine.

    With no --incident, the default is the record with the most findings,
    because the sweep's whole claim is about findings the investigation's
    evidence window never reached.
    """
    status, body = dep.request("GET", "/api/incidents?summary=true")
    if not (200 <= status < 300) or not isinstance(body, list) or not body:
        return None
    if wanted:
        chosen = next((i for i in body if i.get("incident_id") == wanted), None)
        if chosen is None:
            return None
    else:
        chosen = max(body, key=lambda i: i.get("finding_count", 0))
    hosts = chosen.get("hosts") or ["unspecified"]
    return chosen.get("incident_id", ""), hosts[0]


def dry_run(base: str, inc: str, target: str) -> None:
    print(f"DRY RUN — no request will be made. Base URL: {base}")
    print(f"Incident: {inc}   isolation target: {target}")
    print(f"Auth: {WRITE_HEADER} header on writes, read from CITINEL_WRITE_TOKEN "
          f"({'set' if os.environ.get('CITINEL_WRITE_TOKEN') else 'NOT SET'})")
    print()
    for i, line in enumerate([
        f'POST /api/incidents/{inc}/context   {{"confirm": true}}   Tavily search/extract/map/crawl',
        f'POST /api/incidents/{inc}/sweep     {{"confirm": true}}   Gemini long-context sweep',
        f'POST /api/incidents/{inc}/brief     {{"confirm": true}}   Tavily Research, then GET to advance',
        f"GET  /api/incidents/{inc}/draft?kind=certin              Lyzr review + PII guard + Startuped signal",
        'POST /api/corpus/review             {"confirm": true}   Lyzr corpus advisor',
        f'POST /api/incidents/{inc}/handover  {{"confirm": true}}   Lyzr handover writer',
        f'POST /api/actions/execute           {{"incident_id": "{inc}", "action_class": '
        f'"isolate_host", "target": "{target}", "assets_affected": 1}}   gate + Swytchcode',
        "GET  /api/n8n/executions                                 n8n read path",
        "GET  /api/startuped/signals                              what is reported",
    ], 1):
        print(f"[{i}] {line}")
    print()
    print("Then the summary would GET: "
          f"/api/incidents/{inc}/audit, .../context, .../sweep, .../brief, "
          ".../handover, /api/corpus/review, .../verdict, /api/ledger/verify")


def main() -> int:
    p = argparse.ArgumentParser(
        description="Exercise every CITINEL partner seam against a live deployment.",
        epilog="The write token is read from CITINEL_WRITE_TOKEN and is never a "
               "command-line argument, because arguments land in shell history "
               "and in every process listing on the box.")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.add_argument("--incident", default=None,
                   help="incident id to exercise (default: the one with the most findings)")
    p.add_argument("--target", default=None,
                   help="host for the isolate_host proposal (default: the incident's first host)")
    p.add_argument("--dry-run", action="store_true",
                   help="print what would be called and make no request")
    p.add_argument("--timeout", type=float, default=120.0,
                   help="per-request timeout in seconds (default 120; slow steps raise it)")
    p.add_argument("--brief-wait", type=float, default=90.0,
                   help="seconds to keep advancing the async research brief (default 90)")
    args = p.parse_args()

    token = os.environ.get("CITINEL_WRITE_TOKEN", "")
    if args.dry_run:
        dry_run(args.base_url, args.incident or "<discovered>",
                args.target or "<first host>")
        return 0
    if not token:
        print("CITINEL_WRITE_TOKEN is not set in this environment. Export it "
              "(do not pass it as an argument) and run again.", file=sys.stderr)
        return 2

    dep = Deployment(args.base_url, token, args.timeout)
    print(f"CITINEL partner-seam exercise — {dep.base}")
    st, health = dep.request("GET", "/healthz")
    if not (200 <= st < 300):
        print(f"deployment is not answering /healthz (HTTP {st}): "
              f"{dep.redact(_detail(health))}", file=sys.stderr)
        return 2

    inc, target = args.incident, args.target
    if not inc or not target:
        found = pick_incident(dep, inc)
        if not found:
            print(f"{inc} is not on this deployment" if inc else
                  "no incidents on this deployment; nothing to exercise",
                  file=sys.stderr)
            return 2
        inc, target = found[0], target or found[1]
    print(f"incident {inc} · isolation target {target}")
    print()

    rep = Report(dep)
    step_context(dep, rep, inc)
    step_sweep(dep, rep, inc)
    step_brief(dep, rep, inc, args.brief_wait)
    step_draft(dep, rep, inc)
    step_corpus_review(dep, rep)
    step_handover(dep, rep, inc)
    step_execute(dep, rep, inc, target)
    step_n8n(dep, rep)
    step_startuped(dep, rep)

    tally = {PASS: 0, FAIL: 0, SKIP: 0}
    for v, *_ in rep.rows:
        tally[v] += 1
    print(f"{tally[PASS]} passed · {tally[FAIL]} failed · {tally[SKIP]} skipped")
    print()

    summarise(dep, inc)

    if rep.failed:
        print(f"{rep.failed} step(s) failed.")
        return 1
    if tally[SKIP]:
        print(f"No failures, but {tally[SKIP]} step(s) did not fully land — what "
              "those panels show is explained above, and it is not a finished "
              "result.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
