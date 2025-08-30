import os
from pathlib import Path

import pytest
import yaml
from pydantic import SecretStr

from strava_fetcher.settings import load_settings


@pytest.fixture
def temp_config_file(tmp_path: Path) -> Path:
    """Create a temporary YAML config file for testing."""
    config_path = tmp_path / "config.yaml"
    return config_path


def test_load_from_env_vars(monkeypatch):
    """Test that settings are correctly loaded from environment variables."""
    monkeypatch.setenv("STRAVA_CLIENT_ID", "env_client_id")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "env_client_secret")

    settings = load_settings()

    assert settings.strava_api.client_id.get_secret_value() == "env_client_id"
    assert settings.strava_api.client_secret.get_secret_value() == "env_client_secret"


def test_load_from_yaml(temp_config_file: Path):
    """Test that settings are correctly loaded from a YAML file."""
    config_data = {
        "strava_api": {
            "client_id": "yaml_client_id",
            "client_secret": "yaml_client_secret",
        }
    }
    with open(temp_config_file, "w") as f:
        yaml.dump(config_data, f)

    settings = load_settings(config_file=str(temp_config_file))

    assert settings.strava_api.client_id.get_secret_value() == "yaml_client_id"
    assert settings.strava_api.client_secret.get_secret_value() == "yaml_client_secret"


def test_yaml_overrides_env_vars(monkeypatch, temp_config_file: Path):
    """Test that YAML settings override environment variables."""
    monkeypatch.setenv("STRAVA_CLIENT_ID", "env_client_id")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "env_client_secret")

    config_data = {
        "strava_api": {
            "client_id": "yaml_client_id",
            "client_secret": "yaml_client_secret",
        }
    }
    with open(temp_config_file, "w") as f:
        yaml.dump(config_data, f)

    settings = load_settings(config_file=str(temp_config_file))

    assert settings.strava_api.client_id.get_secret_value() == "yaml_client_id"
    assert settings.strava_api.client_secret.get_secret_value() == "yaml_client_secret"


def test_cli_args_override_yaml_and_env_vars(monkeypatch, temp_config_file: Path):
    """Test that direct CLI arguments override both YAML and environment variables."""
    monkeypatch.setenv("STRAVA_CLIENT_ID", "env_client_id")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "env_client_secret")

    config_data = {
        "strava_api": {
            "client_id": "yaml_client_id",
            "client_secret": "yaml_client_secret",
        }
    }
    with open(temp_config_file, "w") as f:
        yaml.dump(config_data, f)

    settings = load_settings(
        config_file=str(temp_config_file),
        client_id="cli_client_id",
        client_secret="cli_client_secret",
    )

    assert settings.strava_api.client_id.get_secret_value() == "cli_client_id"
    assert settings.strava_api.client_secret.get_secret_value() == "cli_client_secret"


def test_no_config():
    """Test that settings are None when no configuration is provided."""
    # Unset environment variables to ensure a clean test
    if "STRAVA_CLIENT_ID" in os.environ:
        del os.environ["STRAVA_CLIENT_ID"]
    if "STRAVA_CLIENT_SECRET" in os.environ:
        del os.environ["STRAVA_CLIENT_SECRET"]

    settings = load_settings()

    assert settings.strava_api.client_id is None
    assert settings.strava_api.client_secret is None


def test_load_from_yaml_with_int_client_id(temp_config_file: Path):
    """Test that an integer client_id is correctly coerced to a string."""
    config_data = {
        "strava_api": {
            "client_id": 12345,
            "client_secret": "yaml_client_secret",
        }
    }
    with open(temp_config_file, "w") as f:
        yaml.dump(config_data, f)

    settings = load_settings(config_file=str(temp_config_file))

    assert settings.strava_api.client_id.get_secret_value() == "12345"
    assert isinstance(settings.strava_api.client_id, SecretStr)
