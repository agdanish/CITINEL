"""Regressions for the defects found auditing the five newest backend seams.

Each test is named after the bug it locks. They are grouped by the seam rather
than by defect class because that is how the next reader will arrive here --
having broken one file and wanting to know what it was supposed to guarantee.

The unifying property: every one of these produced a CONFIDENT WRONG ANSWER
rather than an error. A count that says the automation layer did nothing, an
indicator "corroborated" against findings that never contained it, a policy
block written down as a generic failure, a hostname handed to a marketing
platform. Silence and a plausible number are the failure mode this product
exists to argue against, so they are the ones worth pinning.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from citinel.agents.brief import MAX_POLL_ERRORS, poll_brief
from citinel.agents.visual import corroborate
from citinel.config import settings
from citinel.connectors.n8n_api import list_executions, resume
from citinel.connectors.startuped import emit
from citinel.incidents.model import Finding, Incident
from citinel.web.app import app
from tests.conftest import WRITE_HEADERS

client = TestClient(app)


# ---------------------------------------------------------------------------
# startuped.py -- the boundary that is supposed to be absolute
# ---------------------------------------------------------------------------

@pytest.fixture
def keyed(monkeypatch):
    monkeypatch.setattr(settings, "startuped_api_key", "sk_test_x")


def _capture():
    sent = []

    def sender(method, url, headers, body):
        sent.append(body)
        return 200, {"id": "sig_1"}

    return sent, sender


def test_a_note_carrying_incident_content_never_reaches_startuped(keyed):
    """The reproduced hole. `_clean` screens top-level KEYS, but the only free
    text that actually crosses is the note, nested inside signalValue where
    that screen could not see it. A host, an IP and an incident id went
    straight through."""
    sent, sender = _capture()
    out = emit("citinel-signoffs", 1,
               "host we8105desk at 10.4.7.112 for INC-0417", sender=sender)
    assert out["status"] == "refused", "incident content must never be sent"
    assert sent == [], "nothing may leave the process at all"


@pytest.mark.parametrize("note", [
    "10.4.7.112",                       # an IP
    "INC-0417",                         # an incident id
    "we8105desk.bank.local",            # an FQDN
    "target WRK-2214",                  # a host, upper-cased
    "evidence EventCode=4624",          # a log line
])
def test_every_shape_of_incident_content_is_refused_in_a_note(keyed, note):
    sent, sender = _capture()
    assert emit("citinel-signoffs", 1, note, sender=sender)["status"] == "refused"
    assert sent == []


def test_the_reason_codes_the_product_actually_emits_still_go_through(keyed):
    """The screen has to be tight enough to stop a hostname and loose enough
    that the five real call sites keep working, or it just breaks the seam."""
    for note in ("swarm run completed", "verdict produced with cited claims",
                 "gate verdict allow_with_rollback", "certin artifact drafted for sign-off",
                 "dpdp artifact drafted for sign-off",
                 "incident signed off by a named human"):
        sent, sender = _capture()
        assert emit("citinel-signoffs", 1, note, sender=sender)["status"] == "sent", note
        assert sent[0]["signalValue"]["note"] == note


def test_the_draft_route_cannot_push_its_query_string_across_the_boundary(sandbox, keyed):
    """How the hole was reachable: GET /draft?kind=<anything> interpolated a
    caller-supplied query string into the note. The route resolves kind to one
    of two artifacts, so the note must say which artifact -- not what the
    caller typed."""
    sent, sender = _capture()
    import citinel.connectors.startuped as st

    captured = []
    real = st.emit
    monkey = lambda k, c, n="": captured.append(n)
    original_quiet = st.emit_quietly
    try:
        st.emit_quietly = monkey
        import citinel.web.app as app_mod
        app_mod.emit_quietly = monkey
        r = client.get("/api/incidents/INC-T1/draft",
                       params={"kind": "host we8105desk at 10.4.7.112"})
        assert r.status_code == 200
    finally:
        st.emit_quietly = original_quiet
        import citinel.web.app as app_mod
        app_mod.emit_quietly = original_quiet
    assert captured == ["dpdp artifact drafted for sign-off"]
    assert "we8105desk" not in captured[0]
    assert real is st.emit and sent == []


def test_a_forbidden_key_nested_below_the_top_level_is_also_refused(keyed):
    from citinel.connectors import startuped as st
    nested = {"name": "x", "signalValue": {"value": 1, "host": "we8105desk"}}
    assert isinstance(st._clean(nested), str)


def test_an_uncoercible_count_is_reported_not_raised(keyed):
    """emit documents "Never raises" and sits behind call sites in the incident
    path. int(count) used to run before the try block."""
    sent, sender = _capture()
    out = emit("citinel-signoffs", None, sender=sender)   # must not raise
    assert out["status"] == "error" and sent == []


# ---------------------------------------------------------------------------
# n8n_api.py
# ---------------------------------------------------------------------------

@pytest.fixture
def n8n_on(monkeypatch):
    monkeypatch.setattr(settings, "n8n_api_url", "https://x.app.n8n.cloud")
    monkeypatch.setattr(settings, "n8n_api_key", "n8n-key")


def test_a_malformed_resume_url_does_not_escape_as_a_valueerror(n8n_on):
    """urlparse RAISES on a malformed authority rather than returning an empty
    hostname, and this URL arrives in a request body. Unguarded it 500ed the
    resume route."""
    out = resume("https://[abc/w/1", "approve", "a", sender=lambda *a: (200, {}))
    assert out["status"] == "error" and "unparseable" in out["detail"]


def test_the_resume_route_answers_a_malformed_url_instead_of_500ing(sandbox, n8n_on):
    r = client.post("/api/incidents/INC-T1/n8n/resume", headers=WRITE_HEADERS,
                    json={"resume_url": "https://[abc/w/1", "decision": "approve",
                          "approver": "ciso@bank"})
    assert r.status_code == 200
    assert r.json()["status"] == "error"


def test_a_resume_url_must_belong_to_this_deployments_own_n8n(n8n_on):
    """The docstring said the URL "could not be redirected by a poisoned log".
    True of a log, but the route reads it from the request body -- so without
    this check any caller could have CITINEL POST an approver's name to any
    https host it named."""
    calls = []
    out = resume("https://attacker.example/collect", "approve", "ciso@bank",
                 sender=lambda *a: (calls.append(1), (200, {}))[1])
    assert out["status"] == "refused" and calls == []
    assert "attacker.example" in out["detail"]


def test_a_resume_is_refused_outright_when_no_n8n_is_configured(monkeypatch):
    monkeypatch.setattr(settings, "n8n_api_url", None)
    calls = []
    out = resume("https://x.app.n8n.cloud/w/1", "approve", "a",
                 sender=lambda *a: (calls.append(1), (200, {}))[1])
    assert out["status"] == "refused" and calls == []


def test_the_execution_limit_is_clamped_once_and_used_for_the_slice(n8n_on):
    """The clamp applied to the request and the RAW limit to the slice, so
    ?limit=0 asked n8n for a row and threw it away -- answering "ok" with no
    executions, which reads as an automation layer that did nothing."""
    rows = {"data": [{"id": i} for i in range(5)]}
    seen = {}

    def sender(method, url, headers, params, body):
        seen.update(params)
        return 200, rows

    out = list_executions(limit=0, sender=sender)
    assert seen["limit"] == 1
    assert out["status"] == "ok" and len(out["executions"]) == 1

    out = list_executions(limit=-1, sender=sender)
    assert len(out["executions"]) == 1, "a negative limit must not drop the last run"

    out = list_executions(limit=3, sender=sender)
    assert [e["id"] for e in out["executions"]] == ["0", "1", "2"]


def test_the_executions_read_answers_inside_the_consoles_own_abort():
    """The console aborts this GET at 20s (BULK_TIMEOUT_MS) and the connector's
    own client waited exactly 20s, so a slow n8n could only ever produce a
    client-side abort -- never the honest error the connector was written to
    return. The server has to give up first."""
    import inspect

    from citinel.connectors import n8n_api
    src = inspect.getsource(n8n_api.list_executions)
    timeout = int(src.split("httpx.Client(timeout=")[1].split(")")[0])
    assert timeout < 20, "must be strictly under the console's 20s abort"


# ---------------------------------------------------------------------------
# brief.py
# ---------------------------------------------------------------------------

def _pending(tmp_path):
    p = tmp_path / "brief" / "INC-T1.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"incident_id": "INC-T1", "status": "pending",
                             "request_id": "req-1", "content": "", "sources": []}))
    return p


class _Tav:
    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls = 0

    def research_poll(self, rid):
        self.calls += 1
        return self.replies[min(self.calls - 1, len(self.replies) - 1)]


def test_one_failed_poll_does_not_destroy_a_research_run_that_is_still_running(tmp_path):
    """A failed poll is not a failed run. The status was written straight
    through, and the pending guard then short-circuited every later call -- so
    a single dropped connection on the GET the console polls permanently
    orphaned a Tavily run whose request id was still perfectly good."""
    _pending(tmp_path)
    tav = _Tav({"status": "error", "content": "", "sources": [],
                "detail": "Tavily research poll failed: ConnectError"},
               {"status": "completed", "content": "the brief", "sources": [],
                "response_time": 4.2})

    first = poll_brief("INC-T1", tmp_path, tmp_path, connector=tav)
    assert first["status"] == "pending", "a transient poll error must stay pending"
    assert first["poll_errors"] == 1
    assert "ConnectError" in first["note"]

    second = poll_brief("INC-T1", tmp_path, tmp_path, connector=tav)
    assert second["status"] == "completed" and second["content"] == "the brief"
    assert second["poll_errors"] == 0
    assert tav.calls == 2, "the second call must actually have polled"


def test_a_run_that_never_resolves_is_eventually_given_up_on(tmp_path):
    """Staying pending forever would be its own lie. Bounded, and it says so."""
    _pending(tmp_path)
    tav = _Tav({"status": "error", "content": "", "sources": [], "detail": "gone"})
    for _ in range(MAX_POLL_ERRORS):
        out = poll_brief("INC-T1", tmp_path, tmp_path, connector=tav)
    assert out["status"] == "error"
    assert f"{MAX_POLL_ERRORS} failed polls" in out["note"]


def test_a_genuine_failed_run_is_still_recorded_as_failed(tmp_path):
    _pending(tmp_path)
    tav = _Tav({"status": "failed", "content": "", "sources": []})
    out = poll_brief("INC-T1", tmp_path, tmp_path, connector=tav)
    assert out["status"] == "failed"


# ---------------------------------------------------------------------------
# visual.py -- the half of the feature that is supposed to be checkable
# ---------------------------------------------------------------------------

def _incident_with(n=3):
    inc = Incident(incident_id="INC-T1")
    for i in range(n):
        inc.add_finding(Finding(
            source="sigma", title="Suspicious Logon", level="high",
            timestamp="2016-08-10T20:54:24+00:00", host=f"h{i}.example",
            techniques=["T1078"], detail={"rule_id": "r-1078-logon"},
            evidence_raw="EventCode=4624 Account=opr_kiosk SourceIP=10.4.7.112"))
    return inc


def test_an_indicator_matching_a_field_name_is_not_reported_as_corroborated():
    """The mirror-image of the `raw` vs `evidence_raw` bug this module was
    written to fix. Searching the finding's JSON TEXT means the field names are
    in the haystack, so "host" matched every finding on the record and came
    back corroborated with indices a reader could open and find nothing in."""
    inc = _incident_with(3)
    # "source" is deliberately absent: SourceIP= makes it a genuine hit on
    # content, and the point of the fix is exactly that distinction.
    names = ("host", "detail", "evidence_raw", "techniques", "timestamp")
    out = corroborate(inc, [{"type": "other", "value": v} for v in names])
    assert out["corroborated"] == [], "a field name is not record content"
    assert len(out["unseen"]) == len(names)


def test_real_content_is_still_found_wherever_it_lives_on_the_finding():
    """The fix must not reintroduce the miss it replaced: values from every
    field, including nested detail, still have to match."""
    inc = _incident_with(3)
    out = corroborate(inc, [
        {"type": "ip", "value": "10.4.7.112"},          # inside evidence_raw
        {"type": "host", "value": "h1.example"},        # a scalar field
        {"type": "other", "value": "opr_kiosk"},        # inside the log line
        {"type": "other", "value": "T1078"},            # inside a list field
        {"type": "other", "value": "r-1078-logon"},     # inside nested detail
    ])
    hits = {r["value"]: r["finding_count"] for r in out["corroborated"]}
    assert hits == {"10.4.7.112": 3, "h1.example": 1, "opr_kiosk": 3,
                    "T1078": 3, "r-1078-logon": 3}
    assert out["unseen"] == []


# ---------------------------------------------------------------------------
# swytchcode_runtime_transport.py
# ---------------------------------------------------------------------------

def test_a_policy_block_is_not_downgraded_to_a_generic_error_by_an_empty_message(monkeypatch):
    """What lands here lands on a permanent ledger. `message.splitlines()[0]`
    raises IndexError on an empty string; the executor's broad except swallowed
    it and wrote "error", so a real policy block -- the thing this integration
    exists to demonstrate -- would have been recorded as something going
    wrong."""
    from citinel.connectors import swytchcode_runtime_transport as t

    class FakeErr(Exception):
        message = ""
        details = {"category": "policy_blocked", "suggested_action": "ask a human"}

    import swytchcode_runtime
    monkeypatch.setattr(swytchcode_runtime, "SwytchcodeError", FakeErr, raising=False)

    def boom(*a, **k):
        raise FakeErr()

    monkeypatch.setattr(swytchcode_runtime, "exec", boom, raising=False)

    status, body = t.runtime_sender("comms", "notify_response_team", {"message": "x"})
    assert status == 403 and body["policy_blocked"] is True
    assert body["suggested_action"] == "ask a human"


def test_a_non_dict_details_does_not_turn_a_policy_block_into_an_error(monkeypatch):
    """`details` is a shape a third-party SDK controls. A list made
    details.get() raise inside the handler, with the same result."""
    from citinel.connectors import swytchcode_runtime_transport as t

    class FakeErr(Exception):
        message = "blocked by policy: names core banking infrastructure"
        details = ["not", "a", "dict"]

    import swytchcode_runtime
    monkeypatch.setattr(swytchcode_runtime, "SwytchcodeError", FakeErr, raising=False)

    def boom(*a, **k):
        raise FakeErr()

    monkeypatch.setattr(swytchcode_runtime, "exec", boom, raising=False)

    status, body = t.runtime_sender("comms", "notify_response_team", {"message": "x"})
    assert status == 403 and body["policy_blocked"] is True
    assert "core banking" in body["message"]
