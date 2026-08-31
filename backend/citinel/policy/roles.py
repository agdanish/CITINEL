"""Role-adaptive projection: two roles, one record (deck slide 7, A5 UX-F11).

**What this is, precisely, and what it is NOT.**

This is *depth adaptation*, not access control. The spec's own words are
"role-adaptive explanation depth (Tier-1 concise / Tier-3 deep; Analyst view
vs CISO view over the same record)" and "two skins of screens 5-12" -- one
record, projected at two depths, for two people who are both authenticated
bank staff. Entry.dc.html states the split as the product intends it:

    ANALYST  the floor: queue, glass-box replay, the gate.
             every verdict opens to its log line.
    CISO     the position: statutory windows, value protected, ledger.
             citations one click deeper.

"One click deeper" is the load-bearing phrase. A CISO is not *forbidden* the
log lines -- they are one request away. Nothing here is a confidentiality
boundary, and this module deliberately does not pretend to be one:
`project()` changes the DEFAULT payload, never the permissible one, and
`expand=True` returns full analyst depth to either role.

Calling this "RBAC" would overclaim. Real role-based access control needs an
authentication model -- proving who the caller is -- and CITINEL has none:
SDD Section 22 Q10 ("Auth & roles ... no authentication/authorization model
exists anywhere. Single-tenant with two roles for MVP?") is an open question
Danish has not answered. Until it is answered, the role arrives from a
client-supplied header and is therefore self-asserted. A self-asserted role
is a fine basis for choosing how much detail to render; it is not a basis for
withholding anything, and this module's own docstring says so rather than
letting a future reader assume a security property that is not there.

**Why this lives in CITINEL's own policy layer and not in Lyzr.** SDD 15.3
lists RBAC as a Lyzr attachment point, but CITINEL's architecture is explicit
that the policy gate is the sole authority (policy/gate.py: "every proposed
action passes through here, no exceptions"). Routing authorization decisions
to an external control plane would contradict that, and would make an outage
in a third-party service a correctness problem for a bank's SOC. Lyzr's
genuine, non-conflicting attachment points -- the independent PII/hallucination
second opinion (connectors/lyzr.py: LyzrGuard) and fleet observability
(LyzrObserver) -- are both wired and do not have this problem, because a
second opinion and a dashboard can both fail safe. This one is CITINEL's own.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Role(str, Enum):
    ANALYST = "analyst"
    CISO = "ciso"

    @classmethod
    def parse(cls, raw: str | None) -> "Role":
        """Anything unrecognised becomes ANALYST -- the fuller projection.

        Defaulting to MORE detail on a malformed input is deliberate: this is
        a depth control, not a confidentiality control, so the failure mode of
        an unknown role must be 'show the operator everything' rather than
        'silently hide evidence from someone who may need it'.
        """
        if raw and raw.strip().lower() == "ciso":
            return cls.CISO
        return cls.ANALYST


@dataclass(frozen=True)
class Projection:
    """One role's default view of one record, plus how to get the rest."""

    role: Role
    data: dict[str, Any]
    depth: str                    # "full" | "position"
    omitted: list[str]            # field names not in this default payload
    expand_hint: str              # how the caller retrieves what was omitted

    def as_dict(self) -> dict[str, Any]:
        return {
            **self.data,
            "_projection": {
                "role": self.role.value,
                "depth": self.depth,
                "omitted": self.omitted,
                "expand_hint": self.expand_hint,
                "note": ("Depth adaptation, not access control: nothing here is "
                         "withheld for confidentiality. Re-request with "
                         "expand=true for full analyst depth."),
            },
        }


#: What the CISO projection folds away by default. Every one of these is
#: retrievable with expand=true -- the list exists to be *disclosed*, so the
#: UI can say "3 fields collapsed, one click deeper" rather than silently
#: rendering a thinner record that looks complete.
_CISO_COLLAPSED = ("findings",)


def project_incident(
    incident: dict[str, Any], role: Role, *, expand: bool = False,
) -> Projection:
    """Project one incident record at the depth its reader works in.

    ANALYST (or any role with expand=True) gets the record unchanged -- the
    floor works in log lines and the glass-box replay needs every finding.

    CISO gets the position: the same incident, same ids, same severity and
    statutory-relevant counts, with the per-finding array folded away and
    replaced by a count. `omitted` names exactly what was folded so the
    client can offer the one-click expansion the spec promises.
    """
    if role is Role.ANALYST or expand:
        return Projection(role=role, data=dict(incident), depth="full",
                          omitted=[], expand_hint="already at full depth")

    data = {k: v for k, v in incident.items() if k not in _CISO_COLLAPSED}
    findings = incident.get("findings") or []
    data["finding_count"] = len(findings)
    # The position view still needs the shape of the evidence, just not every
    # row of it: how many findings, spanning how many hosts, at what severity.
    data["technique_count"] = len(incident.get("techniques") or [])
    return Projection(
        role=role, data=data, depth="position",
        omitted=[f for f in _CISO_COLLAPSED if f in incident],
        expand_hint="re-request with expand=true, or open any citation chip",
    )
