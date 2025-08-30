"""
Data models for the Strava Fetcher package.

This module defines the data structures used throughout the application,
ensuring type safety and clear contracts between different components.
"""

import time

from pydantic import BaseModel, SecretStr


class Token(BaseModel):
    """
    Represents a Strava OAuth2 token set.
    """

    access_token: SecretStr
    refresh_token: SecretStr
    expires_at: int  # Unix timestamp

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """
        Checks if the token is expired or close to expiring.

        Args:
            buffer_seconds: A buffer to consider the token expired ahead of time.

        Returns:
            True if the token is expired, False otherwise.
        """
        return self.expires_at < (time.time() + buffer_seconds)
