"""Tests for the Sigma evaluator's matching semantics.

Each test pins one semantic that would fail silently if broken: wildcard
translation, case-insensitivity, CIDR containment, null handling, NOT logic,
logsource dispatch, and the end-to-end fire on a real ransomware command line.
"""

from __future__ import annotations

import io
import textwrap

from sigma.collection import SigmaCollection

from citinel.detect.fields import native_fields
from citinel.detect.sigma_engine import (
    CompiledRule,
    SigmaEngine,
    event_logsources,
    logsource_matches,
    rule_logsource,
)


def _compile_yaml(yaml_text: str) -> CompiledRule:
    col = SigmaCollection.from_yaml(textwrap.dedent(yaml_text))
    rule = col.rules[0]
    return CompiledRule(
        rule=rule,
        logsource=rule_logsource(rule),
        conditions=[c.parse() for c in rule.detection.parsed_condition],
    )


def _matches(cr: CompiledRule, fields: dict, raw: str = "") -> bool:
    eng = SigmaEngine()
    return bool(eng.match(fields, raw, [cr]))


BASE = """
    title: {title}
    id: 00000000-0000-0000-0000-00000000000{n}
    status: test
    logsource:
        category: process_creation
        product: windows
    detection:
        {detection}
    level: high
"""


def test_contains_wildcard_and_case_insensitivity():
    cr = _compile_yaml(BASE.format(title="contains", n=1, detection="""selection:
            CommandLine|contains: 'delete shadows'
        condition: selection"""))
    assert _matches(cr, {"CommandLine": 'vssadmin.exe DELETE SHADOWS /all'})
    assert not _matches(cr, {"CommandLine": "vssadmin.exe list shadows"})


def test_endswith_translates_to_anchored_suffix():
    cr = _compile_yaml(BASE.format(title="endswith", n=2, detection="""selection:
            Image|endswith: '\\\\vssadmin.exe'
        condition: selection"""))
    assert _matches(cr, {"Image": "C:\\Windows\\System32\\vssadmin.exe"})
    assert not _matches(cr, {"Image": "C:\\Windows\\System32\\vssadmin.exe.bak"})


def test_not_condition_excludes():
    cr = _compile_yaml(BASE.format(title="filter", n=3, detection="""selection:
            Image|endswith: '\\\\cmd.exe'
        filter:
            ParentImage|endswith: '\\\\explorer.exe'
        condition: selection and not filter"""))
    assert _matches(cr, {"Image": "C:\\cmd.exe", "ParentImage": "C:\\evil.exe"})
    assert not _matches(cr, {"Image": "C:\\cmd.exe", "ParentImage": "C:\\Windows\\explorer.exe"})


def test_cidr_containment():
    cr = _compile_yaml("""
    title: cidr
    id: 00000000-0000-0000-0000-000000000004
    status: test
    logsource:
        category: network_connection
        product: windows
    detection:
        selection:
            DestinationIp|cidr: '10.0.0.0/8'
        condition: selection
    level: high
    """)
    assert _matches(cr, {"DestinationIp": "10.20.30.40"})
    assert not _matches(cr, {"DestinationIp": "192.168.1.1"})
    assert not _matches(cr, {"DestinationIp": "not-an-ip"})


def test_null_matches_absent_field_only():
    cr = _compile_yaml(BASE.format(title="nulltest", n=5, detection="""selection:
            Image|endswith: '\\\\cmd.exe'
            User: null
        condition: selection"""))
    assert _matches(cr, {"Image": "C:\\cmd.exe"})
    assert not _matches(cr, {"Image": "C:\\cmd.exe", "User": "SYSTEM"})


def test_keyword_search_without_field_hits_raw():
    cr = _compile_yaml("""
    title: keyword
    id: 00000000-0000-0000-0000-000000000006
    status: test
    logsource:
        product: windows
        service: security
    detection:
        keywords:
            - 'mimikatz'
        condition: keywords
    level: high
    """)
    assert _matches(cr, {}, raw="something something MIMIKATZ something")
    assert not _matches(cr, {}, raw="clean line")


def test_logsource_dispatch_unspecified_matches_any():
    assert logsource_matches((None, "windows", None), ("process_creation", "windows", None))
    assert not logsource_matches(("registry_set", "windows", None),
                                 ("process_creation", "windows", None))


def test_sysmon_eid1_gets_process_creation_logsource():
    ls = event_logsources("sysmon", {"_EventID": "1"})
    assert ("process_creation", "windows", None) in ls


def test_security_4688_also_satisfies_process_creation():
    ls = event_logsources("winevent:security", {"EventCode": "4688"})
    assert ("process_creation", "windows", None) in ls


def test_end_to_end_cerber_shadow_deletion_fires():
    """The demo's Beat 1 in miniature: the real rule shape, the real command."""
    cr = _compile_yaml(BASE.format(title="shadows", n=7, detection="""selection_img:
            Image|endswith: '\\\\vssadmin.exe'
        selection_cli:
            CommandLine|contains|all:
                - 'delete'
                - 'shadows'
        condition: all of selection_*"""))
    body = (
        "<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>"
        "<System><EventID>1</EventID><Computer>we8105desk</Computer></System>"
        "<EventData>"
        "<Data Name='Image'>C:\\Windows\\System32\\vssadmin.exe</Data>"
        "<Data Name='CommandLine'>\"C:\\Windows\\system32\\vssadmin.exe\" delete shadows /all /quiet</Data>"
        "</EventData></Event>"
    )
    fields = native_fields("sysmon", body)
    assert fields["_EventID"] == "1"
    assert _matches(cr, fields, raw=body)
