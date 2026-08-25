"""Governance guard: an independent PII / hallucination screen before sign-off.

Part of the Lyzr governance/observability layer (SDD Section 15.3), but the
deterministic layer here is CITINEL's own and always runs; Lyzr is the second,
independent opinion on top (connectors/lyzr.py), not a replacement.

Why this earns its place rather than decorating: a DPDP breach report that
inadvertently contains personal data is the exact failure DPDP exists to
prevent. Auto-drafted fields and the evidence a reviewer reads can carry
personal identifiers pulled straight from logs -- usernames, Windows SIDs,
emails. Screening the whole document a human is about to sign, and flagging
those for a redaction decision, is real safety work.

Claim discipline (matches the rest of CITINEL): this MITIGATES, it never solves.
It is a second automated screen, not a guarantee; human review stays mandatory.
Detected values are MASKED in the guard's own output so the guard never itself
re-leaks the PII it found. Technical IOCs (IP addresses, hashes, hostnames) are
deliberately NOT treated as PII -- they are the legitimate evidence of the
incident, not personal data to redact.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Each pattern has a stable id, a confidence, and a masker. High-confidence
# types are unambiguous; medium types can false-positive and say so.
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
_INDIAN_MOBILE = re.compile(r"(?<!\d)(?:\+?91[\-\s]?)?[6-9]\d{9}(?!\d)")
_PAN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
_AADHAAR = re.compile(r"(?<!\d)\d{4}\s?\d{4}\s?\d{4}(?!\d)")
_SID = re.compile(r"\bS-1-5-21(?:-\d+){3,4}\b", re.IGNORECASE)
# Domain-qualified Windows account (e.g. bob.smith.WAYNECORPINC): specific
# enough not to match "vssadmin.exe" (lowercase extension).
_DOMAIN_ACCOUNT = re.compile(r"\b[a-z][a-z0-9]+\.[a-z][a-z0-9]+\.[A-Z]{3,}\b")


def _mask_email(s: str) -> str:
    user, _, domain = s.partition("@")
    return f"{user[:1]}***@{domain}"


def _mask_generic(s: str) -> str:
    digits = re.sub(r"\s", "", s)
    return f"{digits[:2]}***{digits[-2:]}" if len(digits) > 4 else "***"


def _mask_sid(s: str) -> str:
    return "S-1-5-21-***-" + s.rsplit("-", 1)[-1]


def _mask_account(s: str) -> str:
    parts = s.split(".")
    return f"{parts[0][:1]}***.{parts[-1]}"


# A context regex (5th element) means the match only counts as PII if one of
# these keywords appears within CONTEXT_WINDOW characters. Bare 12/10-digit runs
# are rampant in log evidence (PIDs, ports, byte counts, epoch timestamps), so a
# numeric PII type must be corroborated by a nearby label -- otherwise the guard
# cries wolf on every process id. Structurally-specific types (email, PAN, SID,
# domain-qualified account) are unambiguous and stand alone.
CONTEXT_WINDOW = 24
_MOBILE_CTX = re.compile(r"mobile|phone|contact|tel\b|cell|whatsapp", re.I)
_AADHAAR_CTX = re.compile(r"aadha?ar|\buid\b|uidai", re.I)

_PATTERNS = (
    ("email", "high", _EMAIL, _mask_email, None),
    ("pan", "high", _PAN, lambda s: f"{s[:2]}***{s[-1]}", None),
    ("windows_sid", "high", _SID, _mask_sid, None),
    ("domain_account", "medium", _DOMAIN_ACCOUNT, _mask_account, None),
    ("indian_mobile", "high", _INDIAN_MOBILE, _mask_generic, _MOBILE_CTX),
    ("aadhaar", "medium", _AADHAAR, _mask_generic, _AADHAAR_CTX),
)


@dataclass
class PIIFinding:
    pii_type: str
    confidence: str
    masked: str
    context_field: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"pii_type": self.pii_type, "confidence": self.confidence,
                "masked": self.masked, "context_field": self.context_field}


@dataclass
class GuardResult:
    clean: bool
    findings: list[PIIFinding] = field(default_factory=list)
    checked_by: str = "citinel-local"
    note: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"clean": self.clean, "checked_by": self.checked_by,
                "note": self.note, "findings": [f.as_dict() for f in self.findings]}

    def summary(self) -> str:
        if self.clean:
            return f"no PII detected ({self.checked_by})"
        by_type: dict[str, int] = {}
        for f in self.findings:
            by_type[f.pii_type] = by_type.get(f.pii_type, 0) + 1
        parts = ", ".join(f"{n}x {t}" for t, n in sorted(by_type.items()))
        return f"{len(self.findings)} PII item(s) flagged for redaction decision: {parts}"


def screen_text(text: str, context_field: str = "") -> list[PIIFinding]:
    """Return masked PII findings in one string. Dedups identical matches."""
    findings: list[PIIFinding] = []
    seen: set[tuple[str, str]] = set()
    for pii_type, confidence, rx, masker, ctx in _PATTERNS:
        for m in rx.finditer(text):
            if ctx is not None:
                lo = max(0, m.start() - CONTEXT_WINDOW)
                hi = min(len(text), m.end() + CONTEXT_WINDOW)
                if not ctx.search(text[lo:hi]):
                    continue          # numeric match with no corroborating label
            raw = m.group(0)
            key = (pii_type, raw)
            if key in seen:
                continue
            seen.add(key)
            findings.append(PIIFinding(pii_type, confidence, masker(raw), context_field))
    return findings


def screen_draft(draft, extra_evidence: str = "") -> GuardResult:
    """Screen everything a human reviewing this draft would read.

    Screens the auto-drafted field values (the prose that gets signed) plus any
    evidence text the reviewer sees. Human-required placeholder fields (which
    contain <angle-bracket instructions>, not data) are skipped -- there is no
    PII in a placeholder yet.
    """
    findings: list[PIIFinding] = []
    for f in draft.fields:
        if f.fill == "human" or f.value.strip().startswith("<"):
            continue
        findings.extend(screen_text(f.value, context_field=f.key))
    if extra_evidence:
        findings.extend(screen_text(extra_evidence, context_field="evidence"))

    clean = len(findings) == 0
    note = (
        "No inadvertent PII detected in the auto-drafted fields. Human review "
        "of the human-required fields remains mandatory."
        if clean else
        "Personal identifiers found in material the signer will read. These are "
        "flagged for a redaction decision before this report is filed -- "
        "especially relevant for a DPDP breach report. This screen mitigates, "
        "it never solves; human sign-off remains mandatory."
    )
    return GuardResult(clean=clean, findings=findings, checked_by="citinel-local", note=note)
