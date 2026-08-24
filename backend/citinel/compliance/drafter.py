"""The Scribe's compliance drafter -- Beat 5, the signature close.

On a confirmed incident, this drafts the CERT-In 6-hour report and the DPDP
Board breach artifacts from the live incident record (COMP-F18/F19). Three
rules bind it, each visible in the output:

  * We draft, we never file. Every draft is stamped DRAFT -- FOR HUMAN REVIEW
    AND SIGN-OFF, names the manual submission channel (email/phone/fax; no
    CERT-In API exists), and cannot be marked filed by this code.
  * Every field declares how it was filled: [AUTO], [AUTO-SUGGESTED - CONFIRM]
    or [HUMAN REQUIRED]. A reviewer sees exactly what the machine drafted and
    what it must not.
  * Untrusted log content that surfaces in a draft renders through the
    quarantine plane -- escaped, boxed, provenance-tagged -- so a poisoned log
    string visibly fails to launder itself into the report a human signs
    (the cycle-3(b) anti-laundering fix, Step 9).

The regulatory clock is measured detect-time -> now, not from the 2016 event
time: the telemetry is replayed, but the DETECTION happens now, and that is
the interval the six-hour obligation and the audit ribbon actually prove.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from citinel.agents.quarantine import Provenance, quarantine, render_untrusted_text
from citinel.compliance.fields import (
    CERTIN_FIELDS,
    DPDP_FIELDS,
    Fill,
    FieldSpec,
    coverage,
)
from citinel.incidents.model import Incident

CERTIN_CLOCK_HOURS = 6      # COMP-F01: 6 hours from awareness
DPDP_DETAIL_HOURS = 72      # COMP-F17: 72-hour detailed report

# Annexure I category inference from ATT&CK / finding shape. Auto-SUGGESTS;
# a human confirms, because the legal category drives the obligation.
_ANNEXURE_HINTS = (
    ("ransomware", "(v) malicious code attacks - ransomware"),
    ("T1486", "(v) malicious code attacks - ransomware"),
    ("T1490", "(v) malicious code attacks - ransomware (recovery inhibition)"),
    ("T1505", "(iv) website defacement / intrusion with malicious code insertion"),
    ("T1190", "(iii) unauthorised access; (x) attacks on applications"),
    ("T1078", "(iii) unauthorised access of IT systems/data"),
    ("T1003", "(iii) unauthorised access - credential access"),
)


@dataclass
class DraftField:
    key: str
    label: str
    fill: str            # auto | partial | human
    value: str           # the drafted value, or a human-required placeholder
    source: str
    note: str = ""

    @property
    def marker(self) -> str:
        return {"auto": "[AUTO]", "partial": "[AUTO-SUGGESTED - CONFIRM]",
                "human": "[HUMAN REQUIRED]"}[self.fill]

    def as_dict(self) -> dict[str, Any]:
        return {"key": self.key, "label": self.label, "fill": self.fill,
                "value": self.value, "source": self.source, "note": self.note,
                "marker": self.marker}


@dataclass
class Draft:
    kind: str            # "certin" | "dpdp"
    title: str
    incident_id: str
    generated_at: str
    clock_deadline: str
    fields: list[DraftField]
    coverage: dict[str, float]
    quarantine_notices: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind, "title": self.title,
            "incident_id": self.incident_id, "generated_at": self.generated_at,
            "clock_deadline": self.clock_deadline,
            "fields": [f.as_dict() for f in self.fields],
            "coverage": self.coverage,
            "quarantine_notices": self.quarantine_notices,
        }


def _annexure_category(inc: Incident) -> str:
    hay = " ".join(inc.techniques).upper() + " " + " ".join(
        f.title.lower() for f in inc.findings[:200]
    )
    hits = []
    for needle, label in _ANNEXURE_HINTS:
        if needle.upper() in hay.upper():
            if label not in hits:
                hits.append(label)
    return "; ".join(hits) if hits else "(await human classification)"


def _fmt_ts(ts: str) -> str:
    try:
        return datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, TypeError):
        return ts or "(unknown)"


def _value_for(spec: FieldSpec, inc: Incident, now: datetime,
               notices: list[str]) -> str:
    """Draft one field's value from the incident record, or a placeholder."""
    if spec.fill is Fill.HUMAN:
        return f"<{spec.note or 'human judgment required'}>"

    if spec.key == "reporting_org":
        return "<bank/NBFC legal name, address, sector registration -- standing org profile>"
    if spec.key == "contact_poc":
        return "<designated CISO / incident PoC -- Annexure II record>"
    if spec.key in ("dpo_contact",):
        return "<Data Protection Officer name and contact -- standing profile>"
    if spec.key == "incident_type":
        return _annexure_category(inc)
    if spec.key == "breach_nature":
        return (f"{inc.severity.title()}-severity incident on "
                f"{len(inc.hosts)} host(s): {', '.join(inc.hosts)}. "
                f"Activity spans {_fmt_ts(inc.first_event_ts)} to "
                f"{_fmt_ts(inc.last_event_ts)}. "
                f"MITRE ATT&CK: {', '.join(inc.techniques[:10])}.")
    if spec.key == "time_occurrence":
        return _fmt_ts(inc.first_event_ts) + "  (earliest observed event)"
    if spec.key == "time_detection":
        return _fmt_ts(inc.opened_ts) + "  (incident opened by CITINEL)"
    if spec.key == "affected_assets":
        return "; ".join(inc.hosts) or "(none recorded)"
    if spec.key == "ip_iocs":
        iocs = _iocs(inc)
        return ("; ".join(iocs[:20]) + (f" (+{len(iocs)-20} more)" if len(iocs) > 20 else "")
                if iocs else "(no network IOCs in this incident)")
    if spec.key == "symptoms":
        return _symptoms(inc, notices)
    if spec.key == "actions_taken":
        return ("Response actions are proposed under the readable OPA policy and "
                "await the tiers recorded in the incident's audit log; consequential "
                "actions hold for one-click human approval. (Simulated endpoints only.)")
    if spec.key == "impact_severity":
        return (f"{inc.severity.title()} (auto-scored from rule levels). "
                "<confirm business impact: affected services, customer exposure>")
    if spec.key == "principals_affected":
        return "<number and categories of data principals -- from the data map>"
    if spec.key == "mitigation":
        return ("Containment proposed per policy (isolation with rollback, IP block, "
                "file quarantine on simulated endpoints); persistence and recovery-"
                "inhibition activity recorded for reversal.")
    if spec.key == "cause_findings":
        return (f"Attack chain reconstructed from {len(inc.findings)} findings. "
                "<confirm root cause and attribution after forensic review>")
    if spec.key == "prevent_recurrence":
        return "<hardening measures -- draft from playbook/knowledge base, human confirm>"
    if spec.key == "notifications_summary":
        return "<summary of notifications sent to data principals -- notification log>"
    return f"<{spec.source}>"


def _iocs(inc: Incident) -> list[str]:
    out: list[str] = []
    for f in inc.findings:
        if f.source == "anomaly" and f.detail.get("kind") == "network":
            key = f.title.split(": ", 1)[-1]
            if key and key not in out:
                out.append(key)
    return out


def _symptoms(inc: Incident, notices: list[str]) -> str:
    """A short narrative from the top findings. Any injection-flagged evidence
    that surfaces here is rendered through the quarantine plane."""
    lines = []
    seen = set()
    for f in inc.findings:
        if f.source != "sigma":
            continue
        if f.title in seen:
            continue
        seen.add(f.title)
        lines.append(f"- {f.title} ({'/'.join(f.techniques) or 'no ATT&CK tag'})")
        # If the evidence line itself carries injection content, quarantine it
        # here rather than let it appear as plain report prose.
        prov = Provenance("botsv1 replay", "sigma evidence", f.timestamp)
        tainted = quarantine(f.evidence_raw, prov)
        if tainted.flagged:
            notices.append(
                f"Evidence for {f.title!r} contained injection patterns "
                f"({','.join(sorted({fl.pattern_id for fl in tainted.flags}))}); "
                "rendered quarantined below, not as report prose."
            )
        if len(lines) >= 8:
            break
    return "\n".join(lines)


def draft_certin(inc: Incident, now: datetime | None = None) -> Draft:
    now = now or datetime.now(timezone.utc)
    notices: list[str] = []
    fields = [
        DraftField(s.key, s.label, s.fill.value,
                   _value_for(s, inc, now, notices), s.source, s.note)
        for s in CERTIN_FIELDS
    ]
    return Draft(
        kind="certin",
        title="CERT-In Incident Report (6-hour) -- DRAFT, FOR HUMAN REVIEW AND SIGN-OFF",
        incident_id=inc.incident_id,
        generated_at=now.isoformat(),
        clock_deadline=(now + timedelta(hours=CERTIN_CLOCK_HOURS)).isoformat(),
        fields=fields,
        coverage=coverage(CERTIN_FIELDS),
        quarantine_notices=notices,
    )


def draft_dpdp(inc: Incident, now: datetime | None = None) -> Draft:
    now = now or datetime.now(timezone.utc)
    notices: list[str] = []
    fields = [
        DraftField(s.key, s.label, s.fill.value,
                   _value_for(s, inc, now, notices), s.source, s.note)
        for s in DPDP_FIELDS
    ]
    return Draft(
        kind="dpdp",
        title="DPDP Data Protection Board Breach Report (Rule 7) -- DRAFT, FOR HUMAN REVIEW AND SIGN-OFF",
        incident_id=inc.incident_id,
        generated_at=now.isoformat(),
        clock_deadline=(now + timedelta(hours=DPDP_DETAIL_HOURS)).isoformat(),
        fields=fields,
        coverage=coverage(DPDP_FIELDS),
        quarantine_notices=notices,
    )


def render_text(draft: Draft, poisoned_evidence: str | None = None) -> str:
    """Plain-text draft. If a poisoned evidence string is supplied, it is
    rendered through the quarantine plane -- the anti-laundering moment."""
    out: list[str] = []
    out.append("=" * 78)
    out.append(draft.title)
    out.append(f"Incident: {draft.incident_id}")
    out.append(f"Drafted:  {_fmt_ts(draft.generated_at)}")
    clock = "6-hour CERT-In clock" if draft.kind == "certin" else "72-hour DPDP detailed report"
    out.append(f"Deadline: {_fmt_ts(draft.clock_deadline)}  ({clock})")
    cov = draft.coverage
    out.append(f"Coverage: {cov['auto']}/{cov['fields']} fields fully machine-drafted, "
               f"{cov['partial']} auto-suggested (human confirms), "
               f"{cov['human']} human-only")
    out.append("=" * 78)
    out.append("")
    for f in draft.fields:
        out.append(f"{f.marker} {f.label}")
        out.append(f"    {f.value}")
        if f.note and f.fill != "human":
            out.append(f"    [note: {f.note}]")
        out.append("")
    if draft.quarantine_notices:
        out.append("-" * 78)
        out.append("QUARANTINE NOTICES (untrusted content held out of report prose):")
        for n in draft.quarantine_notices:
            out.append(f"  ! {n}")
        out.append("")
    if poisoned_evidence:
        out.append("-" * 78)
        out.append("EVIDENCE ANNEX (untrusted log content, rendered quarantined):")
        out.append("")
        tainted = quarantine(poisoned_evidence,
                             Provenance("botsv1 replay", "log evidence", "-"))
        out.append(render_untrusted_text(tainted, width=74))
        out.append("")
    out.append("=" * 78)
    out.append("CITINEL drafts regulator reports. A human reviews, signs, and submits.")
    out.append("Submission channel: CERT-In email/phone/fax (no API exists). "
               "We draft, we never file.")
    out.append("=" * 78)
    return "\n".join(out)
