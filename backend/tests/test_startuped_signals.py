"""Startuped signals: aggregate product usage, and nothing about an incident.

The first four tests are the ones that matter. Startuped is a go-to-market
platform and CITINEL processes cooperative-bank security telemetry; a host or
an incident id crossing that boundary would be a real privacy failure wearing
an integration's clothes. The rest check that a marketing signal can never
slow down or break an investigation.
"""

from __future__ import annotations

import json

import pytest

from citinel.config import settings
from citinel.connectors.startuped import SIGNALS, emit, emit_quietly


@pytest.fixture
def keyed(monkeypatch):
    monkeypatch.setattr(settings, "startuped_api_key", "sk_test_x")


def _capture():
    sent = []

    def sender(method, url, headers, body):
        sent.append({"method": method, "url": url, "headers": headers, "body": body})
        return 200, {"id": "sig_1"}

    return sent, sender


def test_no_incident_content_is_ever_in_the_payload(keyed):
    """The whole point. Every field sent is inspected, not just the ones a
    caller happened to think about."""
    sent, sender = _capture()
    emit("citinel-incidents-investigated", 1, "swarm run completed", sender=sender)

    blob = json.dumps(sent[0]["body"]).lower()
    for leak in ("inc-", "incident_id", "192.168", "10.4.", "wrk-", "we8105",
                 "host", "finding", "evidence", "target"):
        assert leak not in blob, f"{leak!r} must never reach a marketing platform"


def test_the_payload_is_a_count_and_its_own_description_only(keyed):
    sent, sender = _capture()
    emit("citinel-signoffs", 3, "signed off", sender=sender)
    body = sent[0]["body"]
    assert body["signalValue"]["value"] == 3
    assert body["signalKey"] == "citinel-signoffs"
    # the only free text is CITINEL's own static description plus a fixed note
    assert body["description"] == SIGNALS["citinel-signoffs"]["description"]


def test_a_forbidden_field_is_refused_rather_than_stripped(keyed, monkeypatch):
    """Stripping would let a caller believe it sent something it did not."""
    from citinel.connectors import startuped as st

    original = st.SIGNALS["citinel-signoffs"]
    monkeypatch.setitem(st.SIGNALS, "citinel-signoffs", dict(original))

    sent, sender = _capture()
    # simulate a future edit widening the payload
    real_emit = st.emit

    def leaky(signal_key, count, note="", sender=None):
        return real_emit(signal_key, count, note, sender=sender)

    # directly exercise the guard
    assert st._clean({"name": "x", "host": "we8105desk"}) != {"name": "x", "host": "we8105desk"}
    assert isinstance(st._clean({"name": "x", "host": "we8105desk"}), str)
    assert st._clean({"name": "x", "incident_id": "INC-0417"}).startswith("refusing")


def test_the_org_fields_the_api_forbids_are_also_refused(keyed):
    from citinel.connectors import startuped as st
    for field in ("organizationId", "organizationSlug", "organizationDomain"):
        assert isinstance(st._clean({"name": "x", field: "y"}), str)


def test_an_unknown_signal_key_is_refused_before_any_call(keyed):
    sent, sender = _capture()
    out = emit("citinel-made-up", 1, sender=sender)
    assert out["status"] == "error" and sent == []


def test_no_key_sends_nothing_and_says_so(monkeypatch):
    monkeypatch.setattr(settings, "startuped_api_key", None)
    sent, sender = _capture()
    out = emit("citinel-signoffs", 1, sender=sender)
    assert out["status"] == "not_configured" and sent == []


def test_a_duplicate_signal_appends_to_the_time_series_instead_of_failing(keyed):
    """signalKey is unique per organisation, so the second run of a deployment
    must append a value rather than error."""
    calls = []

    def sender(method, url, headers, body):
        calls.append((method, url))
        return (409, {}) if method == "POST" else (200, {"id": "sig_1"})

    out = emit("citinel-incidents-investigated", 1, sender=sender)
    assert out["status"] == "sent"
    assert [m for m, _ in calls] == ["POST", "PUT"]
    assert calls[1][1].endswith("/citinel-incidents-investigated")


def test_an_expired_key_is_reported_as_such(keyed):
    out = emit("citinel-signoffs", 1, sender=lambda *a: (401, {}))
    assert out["status"] == "error" and "30 days" in out["detail"]


def test_a_marketing_signal_can_never_break_an_investigation(keyed, monkeypatch):
    """emit_quietly sits inside the incident path. Nothing it does may raise."""
    from citinel.connectors import startuped as st

    def boom(*a, **k):
        raise RuntimeError("startuped is down")

    monkeypatch.setattr(st, "emit", boom)
    emit_quietly("citinel-signoffs", 1)          # must not raise


def test_every_declared_signal_has_a_valid_api_type(keyed):
    valid = {"behavioral", "engagement", "conversion", "retention",
             "news-update", "measurement"}
    for key, meta in SIGNALS.items():
        assert meta["type"] in valid, f"{key} has an undocumented type"
        assert meta["name"] and meta["description"]
