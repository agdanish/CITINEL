"""Contract tests for OCSF normalization.

These lock the rules that are easy to break silently later: the type_uid
computation OCSF states as a MUST, the ban on deprecated classes, and the
requirement that a record carry everything the base event demands.
"""

from __future__ import annotations

import pytest

from citinel.ocsf import schema as S
from citinel.ocsf.normalize import normalize
from citinel.ocsf.validate import validate_record

# Classes OCSF deprecated. Emitting one would be valid-looking and wrong.
DEPRECATED = {2001, 3001, 3005, 4010, 4011, 4012}


def test_type_uid_is_class_times_100_plus_activity():
    assert S.type_uid(1007, 1) == 100701
    assert S.type_uid(201001, 4) == 20100104
    assert S.type_uid(4001, 6) == 400106


def test_no_deprecated_class_is_exported():
    exported = {
        v for k, v in vars(S).items()
        if k.isupper() and isinstance(v, int) and v > 1000
    }
    assert not (exported & DEPRECATED), f"deprecated OCSF class exported: {exported & DEPRECATED}"


def test_registry_classes_are_in_the_win_extension_namespace():
    # Guards against the 1008/1009 misremembering; 1008 is event log activity.
    assert S.REGISTRY_KEY_ACTIVITY == 201001
    assert S.REGISTRY_VALUE_ACTIVITY == 201002
    assert S.class_name(1008) == "event_log_actvity"


def test_activity_validation_rejects_undefined_activity():
    assert S.is_valid_activity(1007, 1) is True
    assert S.is_valid_activity(1007, 42) is False


@pytest.mark.parametrize("declared,expected", [
    ("1.9.0", True), ("1.0", True), ("2.5", False), ("", False), ("garbage", False),
])
def test_producer_version_branching(declared, expected):
    assert S.supports(declared) is expected


def _sysmon_process_create() -> dict:
    body = (
        "<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>"
        "<System><Provider Name='Microsoft-Windows-Sysmon'/><EventID>1</EventID>"
        "<Computer>we8105desk.waynecorpinc.local</Computer></System><EventData>"
        "<Data Name='Image'>C:\\Windows\\System32\\cmd.exe</Data>"
        "<Data Name='CommandLine'>cmd.exe /c whoami</Data>"
        "<Data Name='ProcessId'>4242</Data>"
        "<Data Name='ParentImage'>C:\\Windows\\explorer.exe</Data>"
        "<Data Name='Hashes'>SHA1=ABC,MD5=DEF</Data>"
        "</EventData></Event>"
    )
    return {"event_class": "sysmon", "body": body, "timestamp": "2016-08-24T10:15:11+00:00"}


def test_sysmon_process_create_maps_to_process_activity_launch():
    rec = normalize(_sysmon_process_create())
    assert rec is not None
    assert rec["class_uid"] == S.PROCESS_ACTIVITY
    assert rec["activity_id"] == 1                    # Launch
    assert rec["type_uid"] == 100701
    assert rec["category_uid"] == 1
    assert rec["process"]["file"]["name"] == "cmd.exe"
    assert rec["process"]["cmd_line"] == "cmd.exe /c whoami"
    assert rec["actor"]["process"]["file"]["path"].endswith("explorer.exe")
    assert {"algorithm": "SHA1", "value": "ABC"} in rec["file"]["hashes"]
    assert validate_record(rec) == []


def test_normalized_record_carries_every_required_base_attribute():
    rec = normalize(_sysmon_process_create())
    for attr in S.BASE_REQUIRED:
        assert rec.get(attr) is not None, f"missing {attr}"
    for attr in S.METADATA_REQUIRED:
        assert rec["metadata"].get(attr), f"missing metadata.{attr}"


def test_validator_catches_a_broken_type_uid():
    rec = normalize(_sysmon_process_create())
    rec["type_uid"] = 999
    problems = validate_record(rec)
    assert any("type_uid" in p for p in problems)


def test_validator_catches_a_category_mismatch():
    rec = normalize(_sysmon_process_create())
    rec["category_uid"] = 9
    assert any("category_uid" in p for p in validate_record(rec))


def test_failed_logon_is_not_informational():
    body = (
        "08/24/2016 10:15:11 AM\nLogName=Security\n"
        "SourceName=Microsoft Windows security auditing.\nEventCode=4625\n"
        "ComputerName=we8105desk.waynecorpinc.local\nMessage=An account failed to log on.\n"
    )
    rec = normalize({"event_class": "winevent:security", "body": body,
                     "timestamp": "2016-08-24T10:15:11+00:00"})
    assert rec["class_uid"] == S.AUTHENTICATION
    assert rec["severity_id"] == S.SEVERITY_MEDIUM
    assert rec["status_id"] == 2
