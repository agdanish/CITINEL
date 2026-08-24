"""Validate normalized records against the pinned OCSF contract.

Same discipline as telemetry extraction: a record is only counted as good if
it can be checked, and every failure is categorised and reported rather than
absorbed. The checks come from the schema snapshot, not from assumption:

  * every attribute OCSF marks required on the base event is present
  * metadata carries the two attributes OCSF marks required on it
  * type_uid equals class_uid * 100 + activity_id, which the schema states
    producers MUST compute
  * activity_id is one the class actually defines
  * category_uid matches the category the schema assigns that class
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from citinel.ocsf import schema as S


@dataclass
class ValidationReport:
    checked: int = 0
    valid: int = 0
    by_class: Counter = field(default_factory=Counter)
    failures: Counter = field(default_factory=Counter)
    examples: dict[str, str] = field(default_factory=dict)

    @property
    def invalid(self) -> int:
        return self.checked - self.valid

    def summary(self) -> str:
        pct = (self.valid / self.checked * 100) if self.checked else 0.0
        return f"{self.valid:,} of {self.checked:,} records valid ({pct:.2f}%)"


def validate_record(rec: dict[str, Any]) -> list[str]:
    """Return a list of contract violations. Empty means valid."""
    problems: list[str] = []

    for attr in S.BASE_REQUIRED:
        if rec.get(attr) is None:
            problems.append(f"missing required base attribute: {attr}")

    md = rec.get("metadata")
    if not isinstance(md, dict):
        problems.append("metadata is not an object")
    else:
        for attr in S.METADATA_REQUIRED:
            if not md.get(attr):
                problems.append(f"missing required metadata.{attr}")
        declared = md.get("version", "")
        if declared and not S.supports(declared):
            problems.append(f"unsupported metadata.version: {declared}")

    class_uid = rec.get("class_uid")
    activity_id = rec.get("activity_id")
    if isinstance(class_uid, int):
        if S.class_name(class_uid) is None:
            problems.append(f"unknown class_uid: {class_uid}")
        else:
            expected_cat = S.category_uid(class_uid)
            if rec.get("category_uid") != expected_cat:
                problems.append(
                    f"category_uid {rec.get('category_uid')} != {expected_cat} for class {class_uid}"
                )
            if isinstance(activity_id, int):
                if not S.is_valid_activity(class_uid, activity_id):
                    problems.append(
                        f"activity_id {activity_id} not defined for class {class_uid}"
                    )
                expected_type = S.type_uid(class_uid, activity_id)
                if rec.get("type_uid") != expected_type:
                    problems.append(
                        f"type_uid {rec.get('type_uid')} != class_uid*100+activity_id "
                        f"({expected_type})"
                    )

    t = rec.get("time")
    if not isinstance(t, int) or t <= 0:
        problems.append(f"time is not a positive epoch-millisecond integer: {t!r}")

    return problems


def validate_stream(records) -> ValidationReport:
    report = ValidationReport()
    for rec in records:
        report.checked += 1
        name = S.class_name(rec.get("class_uid", -1)) or f"uid:{rec.get('class_uid')}"
        report.by_class[name] += 1
        problems = validate_record(rec)
        if problems:
            for p in problems:
                key = p.split(":")[0]
                report.failures[key] += 1
                report.examples.setdefault(key, p)
        else:
            report.valid += 1
    return report
