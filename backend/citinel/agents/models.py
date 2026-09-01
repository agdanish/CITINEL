"""Model resolution under ledger rule L9: names from env, verified live.

CITINEL-STATE.md Section 5 item 6 makes a live model-name check a standing
duty whenever any build or deck asset names a model. `config.py` therefore
holds `triage_model` / `reasoning_model` as environment values with no
defaults, and this module is where they are turned into something callable.

The rule this module enforces: **a model id is never used until the API has
confirmed it exists.** Not "looks plausible", not "was current when this was
written" -- confirmed, this run, against `GET /v1/models`. A retired or
mistyped id then fails at startup with a readable message instead of at 3am
in the middle of an investigation.

`RECOMMENDED_AS_OF` below is documentation, deliberately not a fallback. If
the environment does not name a model, resolution raises and tells the
operator what the current recommendation was on the date this was written,
along with the instruction to verify it. Silently defaulting would be exactly
the drift L9 exists to prevent -- the code would keep working while quietly
using a model nobody chose.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from citinel.config import settings


class Role(str, Enum):
    """What a model is being asked to do. Two tiers, not seven."""

    TRIAGE = "triage"        # high volume, low stakes, cheap: the Router
    REASONING = "reasoning"  # the investigation: Correlator, Narrator, Marshal


#: What Anthropic's docs recommended when this module was written, with the
#: date attached so its staleness is visible rather than assumed. NOT a
#: default -- `resolve()` refuses to guess. Re-check with `citinel models`.
RECOMMENDED_AS_OF: dict[Role, tuple[str, str]] = {
    Role.TRIAGE: ("claude-haiku-4-5", "2026-08-25"),
    Role.REASONING: ("claude-opus-5", "2026-08-25"),
}


class ModelNotConfigured(Exception):
    """The environment does not name a model for this role."""


class ModelNotVerified(Exception):
    """A model id was configured but the API does not list it."""


@dataclass(frozen=True)
class VerifiedModel:
    """A model id the API confirmed exists, with what it told us about it.

    `capabilities` is whatever `GET /v1/models` reported. It drives whether
    the transport may send adaptive thinking and `output_config.effort`, which
    are NOT universal: they are 4.5+/4.6+-generation features, and sending
    them to a model that lacks them is a 400 on every single call.

    That gate used to key off the ROLE (reasoning = send them, triage =
    don't), which silently assumed the reasoning role always runs a top-tier
    model. It does not: `CITINEL_REASONING_MODEL` is operator-set, and
    configuring a cheaper model there -- an entirely reasonable cost
    decision -- broke every call with no hint as to why. Capability belongs
    to the model, not to the job we hired it for.
    """

    model_id: str
    role: Role
    display_name: str
    max_input_tokens: int | None
    max_output_tokens: int | None
    verified_at: str
    capabilities: tuple[str, ...] = ()

    def _has(self, *names: str) -> bool:
        """True only if the API positively reported one of these capabilities.

        Fails SAFE: an unknown or absent capabilities field means we do not
        send the parameter. Omitting adaptive thinking works on every model;
        sending it to one that lacks it fails the request outright. When
        uncertain, the quiet degradation is strictly better than the 400.
        """
        lowered = {c.lower() for c in self.capabilities}
        return any(n.lower() in lowered for n in names)

    @property
    def supports_adaptive_thinking(self) -> bool:
        # "thinking.supported" alone is not enough -- verified live, 1 Sep
        # 2026: Haiku 4.5 reports thinking.supported=true but only its
        # "enabled" type, not "adaptive" (Sonnet 5 supports both). Sending
        # {"type": "adaptive"} to a model that only implements "enabled" is
        # the exact 400 this capability check exists to prevent.
        return self._has("thinking.types.adaptive", "adaptive_thinking", "extended_thinking")

    @property
    def supports_effort(self) -> bool:
        return self._has("effort", "output_effort")

    def as_dict(self) -> dict[str, object]:
        return {
            "model_id": self.model_id,
            "role": self.role.value,
            "display_name": self.display_name,
            "max_input_tokens": self.max_input_tokens,
            "max_output_tokens": self.max_output_tokens,
            "verified_at": self.verified_at,
            "capabilities": list(self.capabilities),
            "supports_adaptive_thinking": self.supports_adaptive_thinking,
            "supports_effort": self.supports_effort,
        }


def configured(role: Role) -> str:
    """The model id the environment names for this role, or raise.

    Raises rather than defaulting. The message names the recommendation and
    its date so an operator can act on it without reading source.
    """
    value = settings.triage_model if role is Role.TRIAGE else settings.reasoning_model
    if value:
        return value
    env_var = f"CITINEL_{'TRIAGE' if role is Role.TRIAGE else 'REASONING'}_MODEL"
    rec, asof = RECOMMENDED_AS_OF[role]
    raise ModelNotConfigured(
        f"{env_var} is not set. CITINEL does not default to a model id "
        f"(ledger rule L9: model names are chosen deliberately and verified "
        f"live, never baked into source). As of {asof} the documented "
        f"recommendation for the {role.value} role was {rec!r} -- confirm it is "
        f"still current, then set {env_var} in .env."
    )


def _flatten_capabilities(raw: Any) -> tuple[str, ...]:
    """Turn the API's nested capabilities object into flat dotted names.

    Verified live, 1 Sep 2026: `GET /v1/models`'s `capabilities` field is not
    a flat list or a name->bool mapping -- both assumed by an earlier version
    of this function, which meant `VerifiedModel.capabilities` silently
    resolved to empty for every model, always, and `supports_effort` /
    `supports_adaptive_thinking` never fired even for a model (Sonnet 5) that
    genuinely supports both. The real shape is nested, e.g.
    `capabilities.effort.high.supported`,
    `capabilities.thinking.types.adaptive.supported`.

    One name is emitted per node whose OWN `supported` is `true`, at every
    depth (so both "effort" and "effort.high" can be present, or just
    "thinking" without "thinking.types.adaptive" when the group is on but a
    specific variant is not -- Haiku 4.5's actual shape). `.model_dump()` is
    used when available (the real SDK response object); a plain dict is
    accepted too so this stays testable with a fake.
    """
    if raw is None:
        return ()
    if hasattr(raw, "model_dump"):
        raw = raw.model_dump()
    if not isinstance(raw, dict):
        return ()

    names: list[str] = []

    def walk(node: Any, prefix: str) -> None:
        if not isinstance(node, dict):
            return
        if node.get("supported") is True:
            names.append(prefix)
        for key, value in node.items():
            if key == "supported":
                continue
            walk(value, f"{prefix}.{key}")

    for top_key, top_value in raw.items():
        walk(top_value, top_key)
    return tuple(names)


def verify(client, role: Role, *, now: str) -> VerifiedModel:
    """Confirm the configured id against the live model list. L9 in one call.

    `client` is an `anthropic.Anthropic`. `now` is passed in rather than read
    from the clock so callers control timestamping (the ledger stamps its own
    entries; nothing here reaches for wall-clock independently).
    """
    model_id = configured(role)
    available = {m.id: m for m in client.models.list()}
    if model_id not in available:
        raise ModelNotVerified(
            f"{model_id!r} (configured for the {role.value} role) is not in the "
            f"live model list. Available: {', '.join(sorted(available)) or '(none)'}. "
            "Either the id is mistyped or the model has been retired -- L9 exists "
            "to catch exactly this before a run depends on it."
        )
    m = available[model_id]
    caps = _flatten_capabilities(getattr(m, "capabilities", None))
    return VerifiedModel(
        model_id=model_id,
        role=role,
        display_name=getattr(m, "display_name", model_id),
        max_input_tokens=getattr(m, "max_input_tokens", None),
        max_output_tokens=getattr(m, "max_tokens", None),
        verified_at=now,
        capabilities=caps,
    )
