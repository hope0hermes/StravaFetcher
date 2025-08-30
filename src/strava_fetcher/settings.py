"""
Centralized configuration management for the Strava Fetcher package.

This module defines the data structures for all settings, loading them from
a combination of a YAML file, environment variables, and command-line arguments.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Annotated, Any

import yaml
from pydantic import (
    BaseModel,
    BeforeValidator,
    DirectoryPath,
    Field,
    FilePath,
    SecretStr,
    ValidationError,
)
from pydantic_settings import BaseSettings

from .exceptions import ConfigError


def to_str(v: Any) -> str | None:
    if v is None:
        return None
    return str(v)


StrOrNone = Annotated[SecretStr | None, BeforeValidator(to_str)]


class StravaAPISettings(BaseSettings):
    """Settings related to the Strava API credentials."""

    client_id: StrOrNone = None
    client_secret: StrOrNone = None


class PathSettings(BaseModel):
    """Settings related to file system paths for data storage."""

    data_dir: DirectoryPath = Field(
        default=Path.home() / ".strava_fetcher" / "data",
        description="Base directory for all data files.",
    )
    token_file: FilePath | None = Field(
        default=None, description="Path to the Strava token file."
    )
    activities_cache_file: FilePath | None = Field(
        default=None, description="Path to the activities summary cache file."
    )
    streams_dir: DirectoryPath | None = Field(
        default=None, description="Directory to store activity stream files."
    )

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.token_file is None:
            self.token_file = self.data_dir / "token.json"
        if self.activities_cache_file is None:
            self.activities_cache_file = self.data_dir / "activities.csv"
        if self.streams_dir is None:
            self.streams_dir = self.data_dir / "Streams"


class SyncSettings(BaseModel):
    """Settings related to the data synchronization process."""

    max_pages: int = Field(
        default=100, gt=0, description="Maximum number of activity pages to fetch."
    )
    retry_interval_seconds: int = Field(
        default=900, gt=0, description="Seconds to wait after hitting a rate limit."
    )
    skip_trainer_activities: bool = Field(
        default=False, description="If True, skip streams for 'trainer' activities."
    )


class Settings(BaseModel):
    """Main container for all application settings."""

    strava_api: StravaAPISettings = Field(default_factory=StravaAPISettings)
    paths: PathSettings = Field(default_factory=PathSettings)
    sync: SyncSettings = Field(default_factory=SyncSettings)

    @classmethod
    def from_yaml(cls, file_path: Path) -> Settings:
        """Load settings from a YAML file."""
        if not file_path.is_file():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        with open(file_path) as f:
            config_data = yaml.safe_load(f) or {}

        try:
            strava_api_data = config_data.pop("strava_api", {})
            strava_api_settings = StravaAPISettings(**strava_api_data)

            return cls(strava_api=strava_api_settings, **config_data)
        except ValidationError as e:
            # Capture the full traceback and re-raise with a custom error
            raise ConfigError(
                f"Invalid configuration in {file_path}: {e}", original_exc=e
            ) from e

    def ensure_paths_exist(self) -> None:
        """Create all necessary data directories if they don't exist."""
        self.paths.data_dir.mkdir(parents=True, exist_ok=True)
        if self.paths.streams_dir is not None:
            self.paths.streams_dir.mkdir(parents=True, exist_ok=True)
        # Ensure parent directory for token and activities file exists
        if self.paths.token_file is not None:
            self.paths.token_file.parent.mkdir(parents=True, exist_ok=True)
        if self.paths.activities_cache_file is not None:
            self.paths.activities_cache_file.parent.mkdir(parents=True, exist_ok=True)


def load_settings(
    config_file: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
) -> Settings:
    """
    Load settings from a YAML file, environment variables, or direct arguments.
    """
    if config_file is not None:
        logging.info(f"Loading settings from {config_file}")
        settings = Settings.from_yaml(Path(config_file))
    else:
        logging.info("Loading settings from default values.")
        settings = Settings()

    # Load from environment variables if not already set
    if settings.strava_api.client_id is None:
        client_id_env = os.getenv("STRAVA_CLIENT_ID")
        if client_id_env:
            settings.strava_api.client_id = SecretStr(client_id_env)

    if settings.strava_api.client_secret is None:
        client_secret_env = os.getenv("STRAVA_CLIENT_SECRET")
        if client_secret_env:
            settings.strava_api.client_secret = SecretStr(client_secret_env)

    # Override with direct arguments if provided
    if client_id:
        settings.strava_api.client_id = SecretStr(client_id)
    if client_secret:
        settings.strava_api.client_secret = SecretStr(client_secret)

    # Ensure all data paths are created
    settings.ensure_paths_exist()

    return settings
