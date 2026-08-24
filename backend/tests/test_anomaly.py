"""Tests for the anomaly scorer's semantics.

Each pins a behaviour that was actually wrong at least once during
development or would fail silently: the weaker network scale, the correlated-
novelty cap, burst windowing, aggregation dedup, and the extension-mismatch
signal that ranks a payload above boot noise.
"""

from __future__ import annotations

import json

from citinel.detect.anomaly import (
    BURST_COUNT,
    ESCALATE_AT,
    Population,
    _net_rarity,
    _rarity,
    score_stream,
)


def _sysmon_proc(image, parent="C:\\Windows\\explorer.exe", host="host1", n=0):
    return {
        "event_class": "sysmon",
        "timestamp": f"2016-08-24T10:00:{n:02d}+00:00",
        "body": (
            "<Event xmlns='x'><System><EventID>1</EventID>"
            f"<Computer>{host}</Computer></System><EventData>"
            f"<Data Name='Image'>{image}</Data>"
            f"<Data Name='ParentImage'>{parent}</Data>"
            "</EventData></Event>"
        ),
    }


def _failed_logon(host, account, n):
    return {
        "event_class": "winevent:security",
        "timestamp": f"2016-08-24T10:00:{n:02d}+00:00",
        "body": (
            f"08/24/2016 10:00:{n:02d} AM\nLogName=Security\nEventCode=4625\n"
            f"ComputerName={host}\nAccountName={account}\n"
        ),
    }


def _run(events, tmp_path, pop=None):
    cache = tmp_path / "cache.jsonl"
    with cache.open("w") as fh:
        for e in events:
            fh.write(json.dumps(e) + "\n")
    out = tmp_path / "anom.jsonl"
    report = score_stream(cache, pop or Population(events=len(events)), out)
    rows = [json.loads(l) for l in out.open()]
    return report, rows


def test_rarity_tiers():
    assert _rarity(1, 1000, "f", "x").contribution == 0.7
    assert _rarity(5, 1000, "f", "x").contribution == 0.4
    assert _rarity(6, 1000, "f", "x") is None


def test_no_single_network_signal_crosses_the_bar():
    # The 10,141-escalation flood fix: each network signal alone stays below
    # ESCALATE_AT, so escalation requires corroboration.
    strongest = _net_rarity(1, 1000, "f", "x").contribution
    assert strongest < ESCALATE_AT


def test_correlated_novelty_is_capped(tmp_path):
    # A never-seen image + never-seen pair + first-seen: novelty alone must not
    # stack past the cap and outrank an independent signal.
    pop = Population(events=100)
    _, rows = _run([_sysmon_proc("C:\\Windows\\System32\\newboot.exe")], tmp_path, pop)
    assert len(rows) == 1
    assert rows[0]["score"] <= 0.7 + 1e-9


def test_extension_mismatch_outranks_boot_noise(tmp_path):
    pop = Population(events=100)
    _, rows = _run(
        [
            _sysmon_proc("C:\\Windows\\System32\\newboot.exe", n=1),
            _sysmon_proc("C:\\Users\\bob\\AppData\\Roaming\\121214.tmp", n=2),
        ],
        tmp_path, pop,
    )
    assert rows[0]["key"].endswith("121214.tmp")
    assert rows[0]["score"] > rows[1]["score"]
    assert any(r["feature"] == "exec_extension_mismatch" for r in rows[0]["reasons"])


def test_burst_fires_at_threshold_not_before(tmp_path):
    below = [_failed_logon("h", "svc", n) for n in range(BURST_COUNT - 1)]
    _, rows = _run(below, tmp_path)
    assert rows == []
    at = [_failed_logon("h", "svc", n) for n in range(BURST_COUNT)]
    _, rows = _run(at, tmp_path)
    assert len(rows) == 1 and rows[0]["kind"] == "auth_burst"


def test_burst_window_expires(tmp_path):
    # Same count of failures spread over > BURST_WINDOW_S must not fire.
    events = []
    for i in range(BURST_COUNT):
        e = _failed_logon("h", "svc", 0)
        e["timestamp"] = f"2016-08-24T{10+i:02d}:00:00+00:00"  # one per hour
        events.append(e)
    _, rows = _run(events, tmp_path)
    assert rows == []


def test_autorun_write_escalates(tmp_path):
    ev = {
        "event_class": "winregistry",
        "timestamp": "2016-08-24T10:48:41+00:00",
        "body": (
            '08/24/2016 10:48:41.707\nevent_status="(0)ok"\npid=3828\n'
            'process_image="c:\\Users\\bob\\AppData\\Roaming\\121214.tmp"\n'
            'registry_type="SetValue"\n'
            'key_path="HKU\\S-1-5-21\\software\\microsoft\\windows\\currentversion\\run\\osk"\n'
        ),
    }
    _, rows = _run([ev], tmp_path)
    assert len(rows) == 1
    assert rows[0]["kind"] == "persistence"
    assert "currentversion\\run" in rows[0]["key"]


def test_aggregation_dedups_repeat_launches(tmp_path):
    pop = Population(events=100)
    events = [_sysmon_proc("C:\\evil\\x.tmp", n=i) for i in range(10)]
    report, rows = _run(events, tmp_path, pop)
    assert len(rows) == 1
    assert rows[0]["count"] == 10
    assert report.escalations == 1
