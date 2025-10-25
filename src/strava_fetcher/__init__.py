"""A robust pipeline for syncing Strava activity data and streams locally."""

__version__ = "1.0.2"

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

__all__ = [
    "main",
    "StravaFetcherError",
    "APIError",
    "ConfigError",
    "RateLimitError",
    "UnauthorizedError",
    "StravaSyncPipeline",
    "Settings",
]
