"""Deterministic Sigma detection over normalized telemetry.

This is the layer that closes known threats before any model is involved
(PIPE-F07). It is the load-bearing half of CITINEL's "rules first, AI second"
design: most alerts should terminate here, cheaply and explainably, and only
what rules cannot express should reach the agent swarm.

pySigma is a rule *conversion* library -- it turns Sigma YAML into backend
query languages and ships no in-memory matcher. So pySigma is used for what it
is genuinely authoritative about (parsing and validating rules) and the
evaluator below walks the resulting condition AST directly.

Two design decisions worth stating plainly:

1. Rules are evaluated against the event's NATIVE field names, not its OCSF
   field names. Sigma rules are written against Sysmon's `Image` and Windows'
   `EventCode`; re-expressing 3,302 community rules in OCSF terms would be a
   lossy translation of someone else's carefully-reviewed detection logic. The
   OCSF record is what the finding is attached TO, not what it is matched
   against. Both views are carried on the same event.

2. Rule dispatch is by logsource. A rule declaring `category: process_creation,
   product: windows` is only evaluated against events that actually are Windows
   process creations, which is both correct and the difference between a
   tractable run and a 3-billion-comparison one.

The corpus is pinned to a specific SigmaHQ release rather than tracked, per SDD
Section 16 finding 3, and every rule is re-validated locally at load time
instead of trusting upstream merge state.
"""

from __future__ import annotations

import ipaddress
import re
import warnings
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

warnings.filterwarnings("ignore", module="sigma")

from sigma.collection import SigmaCollection  # noqa: E402
from sigma.conditions import (  # noqa: E402
    ConditionAND,
    ConditionFieldEqualsValueExpression,
    ConditionNOT,
    ConditionOR,
    ConditionValueExpression,
)
from sigma.rule import SigmaRule  # noqa: E402
from sigma.types import (  # noqa: E402
    SigmaBool,
    SigmaCIDRExpression,
    SigmaExpansion,
    SigmaFieldReference,
    SigmaNull,
    SigmaNumber,
    SigmaRegularExpression,
    SigmaString,
    SpecialChars,
)

#: The pinned SigmaHQ release this engine is built against. Changing it is a
#: deliberate act, not a background update.
SIGMA_RELEASE = "r2026-07-01"


# --------------------------------------------------------------------------
# Logsource classification: which Sigma logsources does an event belong to?
# --------------------------------------------------------------------------

#: Sysmon event id -> the Sigma logsource category it satisfies.
_SYSMON_LOGSOURCE = {
    1: "process_creation",
    2: "file_change",
    3: "network_connection",
    5: "process_termination",
    6: "driver_load",
    7: "image_load",
    8: "create_remote_thread",
    9: "raw_access_thread",
    10: "process_access",
    11: "file_event",
    12: "registry_add",
    13: "registry_set",
    14: "registry_rename",
    15: "create_stream_hash",
    17: "pipe_created",
    18: "pipe_created",
    19: "wmi_event",
    20: "wmi_event",
    21: "wmi_event",
    22: "dns_query",
    23: "file_delete",
    25: "process_tampering",
    26: "file_delete",
}

#: A Sigma logsource key: (category, product, service). None means "unspecified",
#: which in Sigma means "matches any".
LogSource = tuple[str | None, str | None, str | None]


def event_logsources(event_class: str, fields: dict[str, str]) -> list[LogSource]:
    """Every Sigma logsource this event legitimately satisfies."""
    out: list[LogSource] = []

    if event_class == "sysmon":
        eid = _int(fields.get("_EventID"))
        category = _SYSMON_LOGSOURCE.get(eid) if eid is not None else None
        if category:
            out.append((category, "windows", None))
            # Registry rules commonly declare the umbrella `registry_event`.
            if category.startswith("registry_"):
                out.append(("registry_event", "windows", None))
        out.append((None, "windows", "sysmon"))

    elif event_class == "winevent:security":
        out.append((None, "windows", "security"))
        # 4688 is the built-in equivalent of a Sysmon process creation, and a
        # large body of process_creation rules apply to it.
        if _int(fields.get("EventCode")) == 4688:
            out.append(("process_creation", "windows", None))

    elif event_class == "winevent:system":
        out.append((None, "windows", "system"))
    elif event_class == "winevent:application":
        out.append((None, "windows", "application"))
    elif event_class == "winregistry":
        out.append(("registry_event", "windows", None))
        out.append(("registry_set", "windows", None))
    elif event_class == "iis":
        out.append(("webserver", None, None))
    elif event_class.startswith("suricata:") or event_class.startswith("stream:"):
        out.append(("firewall", None, None))
    elif event_class.startswith("fortinet:"):
        out.append(("firewall", None, None))

    return out


def rule_logsource(rule: SigmaRule) -> LogSource:
    ls = rule.logsource
    return (ls.category, ls.product, ls.service)


def logsource_matches(rule_ls: LogSource, event_ls: LogSource) -> bool:
    """Sigma logsource semantics: an unspecified field on the rule matches anything."""
    for r, e in zip(rule_ls, event_ls):
        if r is not None and r != e:
            return False
    return True


# --------------------------------------------------------------------------
# Value matching
# --------------------------------------------------------------------------

@lru_cache(maxsize=200_000)
def _compile(pattern: str, ignorecase: bool = True) -> re.Pattern:
    return re.compile(pattern, re.IGNORECASE if ignorecase else 0)


def _sigma_string_to_regex(s: SigmaString) -> str:
    parts: list[str] = []
    for p in s.s:
        if isinstance(p, str):
            parts.append(re.escape(p))
        elif p == SpecialChars.WILDCARD_MULTI:
            parts.append(".*")
        elif p == SpecialChars.WILDCARD_SINGLE:
            parts.append(".")
    return "\\A" + "".join(parts) + "\\Z"


def _as_text(value: Any) -> str:
    return value if isinstance(value, str) else ("" if value is None else str(value))


def _int(v: Any) -> int | None:
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


def match_value(observed: Any, expected: Any, fields: dict[str, str]) -> bool:
    """Does one observed field value satisfy one Sigma value expression?"""
    if isinstance(expected, SigmaNull):
        return observed is None or observed == ""

    if observed is None:
        return False

    if isinstance(expected, SigmaString):
        return bool(_compile(_sigma_string_to_regex(expected)).match(_as_text(observed)))

    if isinstance(expected, SigmaNumber):
        obs = _int(observed)
        if obs is not None:
            return obs == int(expected.number)
        return _as_text(observed) == str(expected.number)

    if isinstance(expected, SigmaRegularExpression):
        flags = 0
        try:
            flags = expected.sigma_to_python_flags() if callable(
                getattr(expected, "sigma_to_python_flags", None)
            ) else 0
        except Exception:
            flags = 0
        return bool(re.search(expected.to_plain(), _as_text(observed), flags | re.IGNORECASE))

    if isinstance(expected, SigmaCIDRExpression):
        try:
            return ipaddress.ip_address(_as_text(observed).strip()) in ipaddress.ip_network(
                expected.cidr, strict=False
            )
        except ValueError:
            return False

    if isinstance(expected, SigmaExpansion):
        return any(match_value(observed, v, fields) for v in expected.values)

    if isinstance(expected, SigmaBool):
        return _as_text(observed).strip().lower() in (
            ("true", "1", "yes") if expected.boolean else ("false", "0", "no")
        )

    if isinstance(expected, SigmaFieldReference):
        other = lookup(fields, expected.field)
        if other is None:
            return False
        a, b = _as_text(observed).lower(), _as_text(other).lower()
        if expected.starts_with:
            return a.startswith(b)
        if expected.ends_with:
            return a.endswith(b)
        return a == b

    return False


#: Sigma field names that differ from what the source actually calls them.
_FIELD_ALIASES = {
    "eventid": ("EventCode", "_EventID"),
    "eventcode": ("EventCode", "_EventID"),
    "computername": ("ComputerName", "Computer"),
    "commandline": ("CommandLine",),
    "parentcommandline": ("ParentCommandLine",),
}


def lookup(fields: dict[str, str], name: str) -> Any:
    """Resolve a Sigma field name against an event's native fields."""
    if name in fields:
        return fields[name]
    low = name.lower()
    for alias in _FIELD_ALIASES.get(low, ()):
        if alias in fields:
            return fields[alias]
    # Case-insensitive fallback; source systems are inconsistent about casing.
    for k, v in fields.items():
        if k.lower() == low:
            return v
    return None


# --------------------------------------------------------------------------
# Condition evaluation
# --------------------------------------------------------------------------

def evaluate(node: Any, fields: dict[str, str], raw: str) -> bool:
    """Walk one parsed Sigma condition against an event."""
    if isinstance(node, ConditionAND):
        return all(evaluate(a, fields, raw) for a in node.args)
    if isinstance(node, ConditionOR):
        return any(evaluate(a, fields, raw) for a in node.args)
    if isinstance(node, ConditionNOT):
        return not any(evaluate(a, fields, raw) for a in node.args)
    if isinstance(node, ConditionFieldEqualsValueExpression):
        return match_value(lookup(fields, node.field), node.value, fields)
    if isinstance(node, ConditionValueExpression):
        # A keyword search with no field: Sigma matches it anywhere in the event.
        v = node.value
        if isinstance(v, SigmaString):
            pattern = _sigma_string_to_regex(v).replace("\\A", "").replace("\\Z", "")
            return bool(_compile(pattern).search(raw))
        return match_value(raw, v, fields)
    return False


# --------------------------------------------------------------------------
# Rule index
# --------------------------------------------------------------------------

@dataclass
class CompiledRule:
    rule: SigmaRule
    logsource: LogSource
    conditions: list[Any]

    @property
    def title(self) -> str:
        return self.rule.title or "(untitled)"

    @property
    def rule_id(self) -> str:
        return str(self.rule.id) if self.rule.id else ""

    @property
    def level(self) -> str:
        return str(self.rule.level).lower().replace("sigmalevel.", "") if self.rule.level else "informational"

    @property
    def techniques(self) -> list[str]:
        return [t.name.upper() for t in (self.rule.tags or [])
                if getattr(t, "namespace", "") == "attack" and str(t.name).lower().startswith("t")]


@dataclass
class LoadReport:
    files: int = 0
    loaded: int = 0
    parse_failures: int = 0
    unsupported: int = 0
    by_level: dict[str, int] = field(default_factory=dict)
    failures: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"{self.loaded:,} rules compiled from {self.files:,} files "
            f"({self.parse_failures:,} parse failures, {self.unsupported:,} unsupported)"
        )


class SigmaEngine:
    """Loads a pinned Sigma corpus and matches events against it."""

    def __init__(self) -> None:
        self.rules: list[CompiledRule] = []
        self.report = LoadReport()

    def load(self, rules_root: Path) -> LoadReport:
        files = sorted(rules_root.rglob("*.yml"))
        self.report.files = len(files)
        collection = SigmaCollection.load_ruleset([rules_root])

        for rule in collection.rules:
            try:
                conditions = [c.parse() for c in rule.detection.parsed_condition]
            except Exception as exc:  # a rule we cannot evaluate is reported, not hidden
                self.report.parse_failures += 1
                if len(self.report.failures) < 10:
                    self.report.failures.append(f"{rule.title}: {type(exc).__name__}")
                continue
            compiled = CompiledRule(rule=rule, logsource=rule_logsource(rule), conditions=conditions)
            self.rules.append(compiled)
            self.report.loaded += 1
            lvl = compiled.level
            self.report.by_level[lvl] = self.report.by_level.get(lvl, 0) + 1

        return self.report

    def rules_for(self, logsources: Iterable[LogSource]) -> list[CompiledRule]:
        ls = list(logsources)
        return [r for r in self.rules if any(logsource_matches(r.logsource, e) for e in ls)]

    def match(self, fields: dict[str, str], raw: str, candidates: list[CompiledRule]) -> list[CompiledRule]:
        hits = []
        for cr in candidates:
            try:
                if any(evaluate(c, fields, raw) for c in cr.conditions):
                    hits.append(cr)
            except Exception:
                continue
        return hits
