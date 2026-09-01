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
    # These defaults assume the repo layout, which holds for local runs and
    # tests. They do NOT hold once the package is pip-installed: the code then
    # lives in site-packages and any path derived from __file__ points into
    # the interpreter's own directory, not the project. That is a real bug
    # this deployment hit -- the container looked for its corpus under
    # /usr/local/lib/python3.11/data/. Every deployment therefore sets these
    # explicitly (CITINEL_DATA_DIR / CITINEL_POLICY_DIR / CITINEL_STATIC_DIR,
    # see deploy/Dockerfile.*) rather than trusting the derived default.
    data_dir: Path = REPO_ROOT / "data"
    policy_dir: Path = REPO_ROOT / "policies"
    static_dir: Path = REPO_ROOT / "dashboard" / "static"
    evals_dir: Path = REPO_ROOT / "evals"

    # --- safety rails (defaults are the safe end, by design) ---------------
    # PIPE-F09: response actions run only against simulated endpoints. This
    # defaults to True and the demo never turns it off. See SDD Section 5.1.
    simulated_endpoints_only: bool = True

    # SDD Section 16 finding 9 / Gartner: a conservative default is the correct
    # engineering posture, not a hackathon compromise to relax later.
    default_autonomy: AutonomyTier = AutonomyTier.SHADOW

    # Off by default, deliberately -- see worker/run.py's own comment at the
    # call site. build_incidents() rebuilds incidents.jsonl from scratch every
    # cycle with no persisted memory of which incidents the swarm already
    # investigated; auto-running unconditionally risks silently re-billing
    # every incident every time detections.jsonl changes. A lightweight
    # already-processed marker file mitigates but does not eliminate this
    # (see _already_processed() in worker/run.py) -- explicit opt-in and a
    # hard per-cycle cap are the real safety rails here, chosen over
    # unconditional auto-run.
    auto_swarm: bool = Field(default=False)
    auto_swarm_max_per_cycle: int = Field(default=3)

    # --- credentials (names only; values come from the environment) --------
    anthropic_api_key: str | None = Field(default=None)
    # Required by newer identity-linked API keys -- confirmed live, 1 Sep 2026:
    # the API rejects such a key with 400 invalid_request_error unless every
    # request names the workspace it acts in. Optional here because a classic
    # (non-identity-linked) key does not need it; sent as a header only when set.
    anthropic_workspace_id: str | None = Field(default=None)
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
    # Lyzr Agent API endpoint. The exact host must be taken from the operator's
    # Lyzr Studio (it is set per deployment), so it is configured rather than
    # hardcoded; the connector adds this host to the egress allow-list only
    # when it is explicitly set.
    # The real chat endpoint (confirmed against a deployed agent's own "Agent
    # API" tab, not the docs -- see connectors/lyzr.py's _chat_payload) is a
    # fixed https://agent-prod.studio.lyzr.ai/v3/inference/chat/, the same
    # for every agent; lyzr_agent_id below (sent in the request body) is what
    # actually selects which agent answers.
    lyzr_guard_url: str | None = Field(default=None)
    lyzr_agent_id: str | None = Field(default=None)

    @property
    def has_swarm_credentials(self) -> bool:
        return bool(self.anthropic_api_key)


settings = Settings()
