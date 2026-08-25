"""Runtime configuration for CITINEL.

Every external credential is read from the environment, never from a file in
the repository. `.env.example` at the repo root lists every variable name with
no values; the real `.env` is gitignored and is Danish's to populate.

Model names are deliberately NOT hardcoded here. CITINEL-STATE.md Section 5
item 6 makes a live Anthropic model-name check a standing duty (ledger rule
L9) whenever any build or deck asset names a model, so the names arrive from
the environment and are verified at the point they are actually used.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class AutonomyTier(str, Enum):
    """The dial, per CITINEL-STATE.md Section 1.4 item 3.

    Set per action class, never globally: SDD Section 13 item 18. Raising a
    tier must never quietly lower a safeguard (SDD Section 17 finding 1).
    """

    SHADOW = "shadow"          # propose only, execute nothing
    ASSIST = "assist"          # execute reversible actions, carry a rollback token
    AUTONOMOUS = "autonomous"  # execute without waiting, still policy-gated


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_prefix="CITINEL_",
        extra="ignore",
    )

    # --- paths -------------------------------------------------------------
    data_dir: Path = REPO_ROOT / "data"
    policy_dir: Path = REPO_ROOT / "policies"

    # --- safety rails (defaults are the safe end, by design) ---------------
    # PIPE-F09: response actions run only against simulated endpoints. This
    # defaults to True and the demo never turns it off. See SDD Section 5.1.
    simulated_endpoints_only: bool = True

    # SDD Section 16 finding 9 / Gartner: a conservative default is the correct
    # engineering posture, not a hackathon compromise to relax later.
    default_autonomy: AutonomyTier = AutonomyTier.SHADOW

    # --- credentials (names only; values come from the environment) --------
    anthropic_api_key: str | None = Field(default=None)
    tavily_api_key: str | None = Field(default=None)
    virustotal_api_key: str | None = Field(default=None)
    abuseipdb_api_key: str | None = Field(default=None)

    # Model identifiers, resolved from env so the L9 live-check duty is not
    # silently baked into source. Unset until Step 7 verifies them live.
    triage_model: str | None = Field(default=None)
    reasoning_model: str | None = Field(default=None)

    # --- sponsor integrations (Step 12; names only, values from env) -------
    n8n_webhook_url: str | None = Field(default=None)
    swytchcode_api_key: str | None = Field(default=None)
    lyzr_api_key: str | None = Field(default=None)

    @property
    def has_swarm_credentials(self) -> bool:
        return bool(self.anthropic_api_key)


settings = Settings()
