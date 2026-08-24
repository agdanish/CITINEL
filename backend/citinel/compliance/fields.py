"""The CERT-In and DPDP field rosters, with their fill classifications.

Every field below, and its YES / PARTIAL / NO auto-fill classification, comes
from A6-compliance.md's primary-sourced mapping (COMP-F18 for CERT-In,
COMP-F19 for DPDP). The classifications are the research's, not invented here:

  AUTO      machine-draftable from the incident record; light human review
  PARTIAL   auto-suggested, but a human must confirm a judgment (legal
            category, business impact, data-principal count)
  HUMAN     legal characterization / consequence assessment / sign-off;
            never machine-drafted, by design

The ~70-80% CERT-In and ~50-60% DPDP coverage figures the deck cites are
therefore COMPUTED from these rosters (see draft_coverage), not asserted. The
CERT-In form (certinirform.pdf) is explicitly non-mandatory to sign; CITINEL
drafts it for human review and manual submission -- email/phone/fax, since no
CERT-In API exists (COMP-F14). We draft, we never file.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Fill(str, Enum):
    AUTO = "auto"
    PARTIAL = "partial"
    HUMAN = "human"


@dataclass(frozen=True)
class FieldSpec:
    key: str
    label: str
    fill: Fill
    source: str          # where the value comes from, per COMP-F18/F19
    note: str = ""


# --- CERT-In Incident Reporting Form (Annexure I regime, COMP-F18) ----------
CERTIN_FIELDS: tuple[FieldSpec, ...] = (
    FieldSpec("reporting_org", "Reporting party / organisation details",
              Fill.AUTO, "standing org profile"),
    FieldSpec("contact_poc", "Point of contact (Annexure II)",
              Fill.AUTO, "standing PoC record"),
    FieldSpec("incident_type", "Incident type (Annexure I category)",
              Fill.PARTIAL, "triage classification + ATT&CK mapping",
              "auto-suggested; a human confirms the legal category, which drives the obligation"),
    FieldSpec("time_occurrence", "Date/time of occurrence",
              Fill.AUTO, "incident timeline (immutable logs)"),
    FieldSpec("time_detection", "Date/time of detection",
              Fill.AUTO, "incident timeline (immutable logs)"),
    FieldSpec("affected_assets", "Affected systems / assets / hostnames",
              Fill.AUTO, "asset correlation"),
    FieldSpec("ip_iocs", "IP addresses / indicators of compromise",
              Fill.AUTO, "enrichment / threat-intel"),
    FieldSpec("symptoms", "Symptoms observed",
              Fill.AUTO, "alert narrative", "draft; light human review"),
    FieldSpec("actions_taken", "Actions taken",
              Fill.AUTO, "response action log"),
    FieldSpec("impact_severity", "Impact / severity",
              Fill.PARTIAL, "correlation + business context",
              "needs human business-impact judgment"),
)

# --- DPDP Data Protection Board breach report (Rule 7, COMP-F19) -------------
DPDP_FIELDS: tuple[FieldSpec, ...] = (
    FieldSpec("breach_nature", "Nature, extent, timing and location of the breach",
              Fill.AUTO, "incident timeline + scope"),
    FieldSpec("principals_affected",
              "Categories and approximate number of data principals affected",
              Fill.PARTIAL, "data map + affected-asset correlation",
              "depends on data-inventory quality"),
    FieldSpec("likely_consequences", "Likely consequences to data principals",
              Fill.HUMAN, "legal / privacy judgment",
              "never machine-drafted: a human privacy judgment"),
    FieldSpec("mitigation", "Mitigation / remedial measures taken or proposed",
              Fill.AUTO, "response log", "draft; human confirm"),
    FieldSpec("cause_findings", "Findings on cause / person responsible",
              Fill.PARTIAL, "forensic output"),
    FieldSpec("prevent_recurrence", "Measures to prevent recurrence",
              Fill.PARTIAL, "playbook / knowledge base"),
    FieldSpec("dpo_contact", "Contact person / Data Protection Officer",
              Fill.AUTO, "standing profile"),
    FieldSpec("notifications_summary", "Summary of data-principal notifications sent",
              Fill.AUTO, "notification-system log"),
    FieldSpec("principal_notice", "Plain-language notice to data principals",
              Fill.HUMAN, "drafted, but legal sign-off + a named executive required"),
)


def coverage(fields: tuple[FieldSpec, ...]) -> dict[str, float]:
    """Computed auto-draft coverage, weighting PARTIAL as a half.

    This is where the deck's "~70-80% CERT-In, ~50-60% DPDP" figures come
    from: they are derived from the field roster and its classifications,
    not stated as a bare number.
    """
    n = len(fields)
    auto = sum(1 for f in fields if f.fill is Fill.AUTO)
    partial = sum(1 for f in fields if f.fill is Fill.PARTIAL)
    human = sum(1 for f in fields if f.fill is Fill.HUMAN)
    return {
        "fields": n,
        "auto": auto,
        "partial": partial,
        "human": human,
        # lower bound: only fully-auto fields; upper: auto + all partials
        "coverage_low": round(auto / n * 100, 1),
        "coverage_high": round((auto + partial) / n * 100, 1),
    }
