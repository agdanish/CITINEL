"""CITINEL eval harness: measure the deterministic layers, honestly.

This is the credibility screen's data source (SDD Section 11 item 14). Its
design constraint is the project's own standing rule -- "the FP rate is a
TARGET, not an achieved result" (CITINEL-STATE.md Section 5.1) -- so the
harness is built to make that distinction structural rather than a caption:

  * Everything it reports is computed from real files on disk. No number here
    is authored, estimated, or carried over from a previous run.
  * Every rate ships with its denominator. A percentage without the count it
    came from is not a measurement, and the UI is forbidden from publishing
    one (HANDOFF.md Section 7).
  * What it CANNOT measure, it says so and explains exactly what is missing.
    The false-positive rate is the headline example: computing one requires a
    labeled corpus (evals/labeled/), and that corpus does not exist. The
    harness therefore reports FP as UNMEASURED with the specific
    precondition, rather than substituting a plausible-looking figure.

That last point is the whole reason this file exists in this shape. A
skeptical judge asking "where does 8% come from?" is the moment a fabricated
metric costs more than an honest gap would have. An UNMEASURED field with a
stated precondition survives that question; an invented number does not.

Scope: the deterministic half only -- Sigma matching and anomaly scoring,
which need no API key and no model. Agent-swarm evaluation (verdict quality,
citation accuracy) requires Step 7 and is deliberately out of scope here;
`swarm_evaluated: false` records that rather than leaving it ambiguous.

Run:  python evals/harness/run.py           # human summary
      python evals/harness/run.py --json    # machine-readable report
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "data" / "cache"
DETECTIONS = CACHE / "detections.jsonl"
ANOMALIES = CACHE / "anomalies.jsonl"
LABELED = REPO_ROOT / "evals" / "labeled"

#: MITRE ATT&CK Enterprise technique count for the version the corpus is
#: tagged against. Used ONLY as a coverage denominator, and reported with the
#: version attached so the ratio can never be quoted bare.
ATTACK_VERSION = "v16.1"
ATTACK_TECHNIQUE_TOTAL = 823


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


@dataclass
class Measured:
    """One measurement, always carrying the denominator it came from."""

    name: str
    value: float | int
    denominator: int | None
    unit: str = ""
    note: str = ""

    def as_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "value": self.value, "unit": self.unit}
        if self.denominator is not None:
            d["denominator"] = self.denominator
            d["rate"] = round(self.value / self.denominator, 6) if self.denominator else None
        if self.note:
            d["note"] = self.note
        return d

    def line(self) -> str:
        if self.denominator is not None:
            pct = (self.value / self.denominator * 100) if self.denominator else 0.0
            base = f"{self.value:,} / {self.denominator:,}  ({pct:.2f}%)"
        elif self.unit == "sha256":
            base = self.note          # the value IS the note for a fingerprint
        else:
            base = f"{self.value:,}{(' ' + self.unit) if self.unit else ''}"
        out = f"  {self.name:<44} {base}"
        if self.note and self.unit != "sha256":
            out += f"\n  {'':<44} -> {self.note}"
        return out


@dataclass
class Unmeasured:
    """Something this harness deliberately does NOT claim to have measured."""

    name: str
    reason: str
    required_to_measure: str

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "status": "UNMEASURED",
                "reason": self.reason,
                "required_to_measure": self.required_to_measure}


@dataclass
class EvalReport:
    generated_at: str
    measured: list[Measured] = field(default_factory=list)
    unmeasured: list[Unmeasured] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    swarm_evaluated: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "scope": "deterministic layers only (Sigma + anomaly scoring)",
            "swarm_evaluated": self.swarm_evaluated,
            "provenance": self.provenance,
            "measured": [m.as_dict() for m in self.measured],
            "unmeasured": [u.as_dict() for u in self.unmeasured],
        }


def build_report() -> EvalReport:
    detections = _read_jsonl(DETECTIONS)
    anomalies = _read_jsonl(ANOMALIES)

    report = EvalReport(generated_at=datetime.now(timezone.utc).isoformat())

    # -- provenance: what was actually measured, so a run is reproducible ----
    # Hashing the inputs makes "same corpus" checkable rather than asserted;
    # two runs quoting different numbers can be told apart from two runs of
    # different data.
    report.provenance = {
        "detections_file": str(DETECTIONS.relative_to(REPO_ROOT)),
        "detections_sha256": _sha256(DETECTIONS),
        "anomalies_file": str(ANOMALIES.relative_to(REPO_ROOT)),
        "anomalies_sha256": _sha256(ANOMALIES),
        "attack_version": ATTACK_VERSION,
    }

    if not detections and not anomalies:
        report.unmeasured.append(Unmeasured(
            "everything",
            "no detection or anomaly output found on disk",
            f"run the pipeline first: `citinel detect-run` and `citinel "
            f"detect-anomaly` write {DETECTIONS.name} and {ANOMALIES.name}",
        ))
        return report

    # -- volume ---------------------------------------------------------------
    report.measured.append(Measured(
        "sigma detections", len(detections), None, "detections"))
    report.measured.append(Measured(
        "anomaly escalations", len(anomalies), None, "escalations"))

    # -- rule concentration: the alert-fatigue signal -------------------------
    # A corpus where a handful of rules produce most detections is the exact
    # shape that buries analysts. Reporting the top-rule share makes that
    # visible instead of hiding it inside a single total.
    by_rule = Counter(d.get("rule_title", "(unknown)") for d in detections)
    if by_rule:
        top_title, top_n = by_rule.most_common(1)[0]
        report.measured.append(Measured(
            "detections from the single noisiest rule", top_n, len(detections),
            note=f"rule: {top_title}"))
        report.measured.append(Measured(
            "distinct rules that fired", len(by_rule), None, "rules"))

    # -- severity distribution ------------------------------------------------
    by_level = Counter(d.get("level", "unknown") for d in detections)
    for level in ("critical", "high", "medium", "low", "informational"):
        if by_level.get(level):
            report.measured.append(Measured(
                f"severity: {level}", by_level[level], len(detections)))

    # -- ATT&CK coverage, with its denominator --------------------------------
    techniques = {t for d in detections for t in (d.get("techniques") or [])}
    report.measured.append(Measured(
        f"ATT&CK techniques observed ({ATTACK_VERSION})",
        len(techniques), ATTACK_TECHNIQUE_TOTAL,
        note="observed in this corpus run; not a claim about total coverage"))

    # -- hosts ----------------------------------------------------------------
    hosts = {d.get("host") for d in detections if d.get("host")}
    report.measured.append(Measured("hosts with >=1 detection", len(hosts), None, "hosts"))

    # -- determinism: the property that makes any of this re-checkable --------
    fingerprint = _fingerprint(detections)
    report.measured.append(Measured(
        "detection-set fingerprint", 0, None, unit="sha256",
        note=f"{fingerprint[:32]}...  (re-running on the same corpus must "
             "reproduce this exactly)"))

    # -- what this harness does NOT claim -------------------------------------
    labeled_files = [p for p in LABELED.glob("*.jsonl")] if LABELED.exists() else []
    if not labeled_files:
        report.unmeasured.append(Unmeasured(
            "false-positive rate",
            "no labeled ground-truth corpus exists (evals/labeled/ is empty), so "
            "no detection can be classified as a true or false positive. The "
            "under-10% figure in the product is a TARGET and has never been "
            "measured; publishing a rate here without labels would fabricate it.",
            "a labeled set: one JSONL row per detection in evals/labeled/ with "
            "{detection_id, verdict: 'tp'|'fp'} decided by a human analyst "
            "reviewing the raw evidence. See labeled/README.md for the schema.",
        ))
        report.unmeasured.append(Unmeasured(
            "true-positive / recall rate",
            "same missing precondition, plus recall additionally requires "
            "knowing which real attacks the corpus contains that CITINEL did "
            "NOT detect -- absent from any output by construction.",
            "the labeled set above, plus an independently-sourced list of the "
            "attacks present in the corpus (BOTS v1 has published solutions "
            "that could seed this).",
        ))

    report.unmeasured.append(Unmeasured(
        "cost per incident",
        "the agent swarm (Step 7) is not running, so no model tokens have been "
        "spent and there is no per-incident cost to measure.",
        "a completed swarm run; AgentCall already records input/output tokens "
        "per call, so this becomes measurable the moment Step 7 executes.",
    ))
    report.unmeasured.append(Unmeasured(
        "verdict quality / citation accuracy",
        "requires the agent swarm (Step 7), which is blocked on an API key.",
        "Step 7 running; the citation gate in agents/pipeline.py already "
        "records verified-vs-dropped claims, which is the natural input.",
    ))

    return report


def _sha256(path: Path) -> str:
    if not path.exists():
        return "(absent)"
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _fingerprint(detections: list[dict[str, Any]]) -> str:
    """Order-independent fingerprint of the detection set."""
    keys = sorted(
        f"{d.get('rule_id')}|{d.get('timestamp')}|{d.get('host')}"
        for d in detections
    )
    return hashlib.sha256("\n".join(keys).encode()).hexdigest()


def render(report: EvalReport) -> str:
    out = [
        "CITINEL eval harness -- deterministic layers",
        f"generated {report.generated_at}",
        "",
        "MEASURED (every rate carries its denominator)",
    ]
    out += [m.line() for m in report.measured]
    out += ["", "NOT MEASURED (stated, not omitted)"]
    for u in report.unmeasured:
        out.append(f"  {u.name}")
        out.append(f"    why: {u.reason}")
        out.append(f"    needs: {u.required_to_measure}")
        out.append("")
    out.append(f"swarm evaluated: {report.swarm_evaluated}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--out", type=Path, help="write the JSON report here too")
    args = ap.parse_args(argv)

    report = build_report()
    if args.json:
        print(json.dumps(report.as_dict(), indent=2))
    else:
        print(render(report))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report.as_dict(), indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
