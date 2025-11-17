"""A robust pipeline for syncing Strava activity data and streams locally."""

__version__ = "1.5.0"

from .cli import main
from .exceptions import (
    APIError,
    ConfigError,
    RateLimitError,
    StravaFetcherError,
    UnauthorizedError,
)
from .pipeline import StravaSyncPipeline
from .settings import Settings


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
    "main",
    "StravaFetcherError",
    "APIError",
    "ConfigError",
    "RateLimitError",
    "UnauthorizedError",
    "StravaSyncPipeline",
    "Settings",
]
