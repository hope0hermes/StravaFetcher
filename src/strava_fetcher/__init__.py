"""A robust pipeline for syncing Strava activity data and streams locally."""

__version__ = "1.7.0"

from .client import StravaClient
from .exceptions import (
    APIError,
    ConfigError,
    RateLimitError,
    StravaFetcherError,
    UnauthorizedError,
)
from .models import Token
from .persistence import ActivityPersistence, TokenPersistence
from .pipeline import StravaSyncPipeline
from .settings import (
    PathSettings,
    Settings,
    StravaAPISettings,
    SyncSettings,
    load_settings,
)


def get_version() -> str:
    """Get the current version of strava_fetcher."""
    return __version__


def get_package_info() -> dict[str, str]:
    """Get package information including name and version."""
    return {
        "name": "strava-fetcher",
        "version": __version__,
        "description": "A robust pipeline for syncing Strava activity data",
    }

__all__ = [
    "get_version",
    "get_package_info",
    # Exceptions
    "StravaFetcherError",
    "APIError",
    "ConfigError",
    "RateLimitError",
    "UnauthorizedError",
    # Pipeline
    "StravaSyncPipeline",
    # Client & Models
    "StravaClient",
    "Token",
    # Persistence
    "TokenPersistence",
    "ActivityPersistence",
    # Settings
    "Settings",
    "StravaAPISettings",
    "PathSettings",
    "SyncSettings",
    "load_settings",
]
