"""Where Settings read from, and what they refuse to read.

Decided 2 Sep 2026 after an adversarial review: unprefixed conventional names
are NOT accepted (the OS environment outranks every dotenv file, so a generic
key on a developer's shell would silently replace the project's own); blank
values mean unset; hosted secret-file mounts are dotenv sources. Names only.
"""
import os

from citinel.config import Settings


def _clear(monkeypatch, suffix: str) -> None:
    for k in list(os.environ):
        if k.upper().endswith(suffix):
            monkeypatch.delenv(k, raising=False)


def test_unprefixed_name_is_not_read(monkeypatch):
    _clear(monkeypatch, "TAVILY_API_KEY")
    monkeypatch.setenv("TAVILY_API_KEY", "conventional")
    assert Settings(_env_file=None).tavily_api_key is None


def test_prefixed_name_is_read(monkeypatch):
    _clear(monkeypatch, "TAVILY_API_KEY")
    monkeypatch.setenv("CITINEL_TAVILY_API_KEY", "documented")
    assert Settings(_env_file=None).tavily_api_key == "documented"


def test_dotenv_sources_include_hosted_secret_file_mounts():
    paths = [str(p) for p in Settings.model_config["env_file"]]
    assert paths[-1] == "/etc/secrets/.env"
    assert "/app/.env" in paths


def test_a_dotenv_file_is_read_and_the_os_environment_still_wins(tmp_path, monkeypatch):
    _clear(monkeypatch, "TAVILY_API_KEY")
    f = tmp_path / ".env"
    f.write_text("CITINEL_TAVILY_API_KEY=from-file\n", encoding="utf-8")
    assert Settings(_env_file=f).tavily_api_key == "from-file"
    monkeypatch.setenv("CITINEL_TAVILY_API_KEY", "from-os")
    assert Settings(_env_file=f).tavily_api_key == "from-os"


def test_a_blank_variable_does_not_wipe_a_real_value(tmp_path, monkeypatch):
    _clear(monkeypatch, "TAVILY_API_KEY")
    f = tmp_path / ".env"
    f.write_text("CITINEL_TAVILY_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setenv("CITINEL_TAVILY_API_KEY", "")
    assert Settings(_env_file=f).tavily_api_key == "from-file"
    blank = tmp_path / "blank.env"
    blank.write_text("CITINEL_TAVILY_API_KEY=\n", encoding="utf-8")
    monkeypatch.delenv("CITINEL_TAVILY_API_KEY", raising=False)
    assert Settings(_env_file=(f, blank)).tavily_api_key == "from-file"


def test_a_whitespace_only_value_does_not_crash_an_enum_or_bool_field(monkeypatch):
    """env_ignore_empty only catches the exact empty string; a single stray
    space used to reach pydantic's own coercion and abort the whole process
    at import time for every enum/bool safety-rail field. Confirmed live,
    2 Sep 2026, for all four before this validator: default_autonomy
    (enum), simulated_endpoints_only, auto_swarm, ui_swarm_enabled (bool)."""
    monkeypatch.setenv("CITINEL_DEFAULT_AUTONOMY", " ")
    monkeypatch.setenv("CITINEL_SIMULATED_ENDPOINTS_ONLY", " ")
    monkeypatch.setenv("CITINEL_AUTO_SWARM", "\t")
    monkeypatch.setenv("CITINEL_UI_SWARM_ENABLED", "  ")
    s = Settings(_env_file=None)
    assert s.default_autonomy.value == "shadow"  # falls back to the coded default
    assert s.simulated_endpoints_only is True
    assert s.auto_swarm is False
    assert s.ui_swarm_enabled is True


def test_a_whitespace_only_credential_is_treated_as_unset(monkeypatch):
    _clear(monkeypatch, "TAVILY_API_KEY")
    monkeypatch.setenv("CITINEL_TAVILY_API_KEY", "   ")
    assert Settings(_env_file=None).tavily_api_key is None
