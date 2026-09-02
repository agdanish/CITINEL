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

from pydantic import AliasChoices, Field
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


def _env(name: str) -> AliasChoices:
    """The documented CITINEL_-prefixed name first, the conventional unprefixed
    name second. An operator who sets ANTHROPIC_API_KEY on Render instead of
    CITINEL_ANTHROPIC_API_KEY is then not silently ignored (confirmed live,
    2 Sep 2026: every connector read "not configured" on a deployment whose
    environment the operator had filled in). validation_alias bypasses
    env_prefix, so the prefixed form must be spelled out here."""
    return AliasChoices(f"CITINEL_{name}", name)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Later entries win over earlier ones; the OS environment wins over
        # all of them. The two extra paths are where a hosted deployment puts
        # an uploaded secret file (Render mounts secret files under
        # /etc/secrets/ and, for Docker services, nowhere near this package's
        # REPO_ROOT, which is site-packages-derived once pip-installed).
        env_file=(REPO_ROOT / ".env", Path("/app/.env"), Path("/etc/secrets/.env")),
        env_prefix="CITINEL_",
        extra="ignore",
        # Fields below carry explicit aliases; this keeps Settings(field=...)
        # working in code and tests.
        populate_by_name=True,
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

    # The console's own "run the swarm" control. On by default: a console that
    # cannot run its pipeline is a mockup. Every run is real model spend (about
    # 86K input / 35K output tokens for INC-0417), so the route demands an
    # explicit {"confirm": true} body and runs one incident at a time.
    ui_swarm_enabled: bool = Field(default=True)

    # --- credentials (names only; values come from the environment) --------
    anthropic_api_key: str | None = Field(default=None, validation_alias=_env("ANTHROPIC_API_KEY"))
    # Required by newer identity-linked API keys -- confirmed live, 1 Sep 2026:
    # the API rejects such a key with 400 invalid_request_error unless every
    # request names the workspace it acts in. Optional here because a classic
    # (non-identity-linked) key does not need it; sent as a header only when set.
    anthropic_workspace_id: str | None = Field(default=None, validation_alias=_env("ANTHROPIC_WORKSPACE_ID"))
    tavily_api_key: str | None = Field(default=None, validation_alias=_env("TAVILY_API_KEY"))
    virustotal_api_key: str | None = Field(default=None, validation_alias=_env("VIRUSTOTAL_API_KEY"))
    abuseipdb_api_key: str | None = Field(default=None, validation_alias=_env("ABUSEIPDB_API_KEY"))

    # Model identifiers, resolved from env so the L9 live-check duty is not
    # silently baked into source. Unset until Step 7 verifies them live.
    triage_model: str | None = Field(default=None, validation_alias=_env("TRIAGE_MODEL"))
    reasoning_model: str | None = Field(default=None, validation_alias=_env("REASONING_MODEL"))

    # --- sponsor integrations (Step 12; names only, values from env) -------
    n8n_webhook_url: str | None = Field(default=None, validation_alias=_env("N8N_WEBHOOK_URL"))
    swytchcode_api_key: str | None = Field(default=None, validation_alias=_env("SWYTCHCODE_API_KEY"))
    lyzr_api_key: str | None = Field(default=None, validation_alias=_env("LYZR_API_KEY"))
    # Lyzr Agent API endpoint. The exact host must be taken from the operator's
    # Lyzr Studio (it is set per deployment), so it is configured rather than
    # hardcoded; the connector adds this host to the egress allow-list only
    # when it is explicitly set.
    # The real chat endpoint (confirmed against a deployed agent's own "Agent
    # API" tab, not the docs -- see connectors/lyzr.py's _chat_payload) is a
    # fixed https://agent-prod.studio.lyzr.ai/v3/inference/chat/, the same
    # for every agent; lyzr_agent_id below (sent in the request body) is what
    # actually selects which agent answers.
    lyzr_guard_url: str | None = Field(default=None, validation_alias=_env("LYZR_GUARD_URL"))
    lyzr_agent_id: str | None = Field(default=None, validation_alias=_env("LYZR_AGENT_ID"))
    # Additional Lyzr Studio agents, each with its own id and its own job in
    # the pipeline (connectors/lyzr_agents.py). Optional one by one: an unset
    # id means that seam reports not_configured rather than faking an answer.
    lyzr_triage_agent_id: str | None = Field(default=None, validation_alias=_env("LYZR_TRIAGE_AGENT_ID"))
    lyzr_review_agent_id: str | None = Field(default=None, validation_alias=_env("LYZR_REVIEW_AGENT_ID"))
    lyzr_handover_agent_id: str | None = Field(default=None, validation_alias=_env("LYZR_HANDOVER_AGENT_ID"))

    @property
    def has_swarm_credentials(self) -> bool:
        return bool(self.anthropic_api_key)


settings = Settings()
