"""
Handles all direct communication with the Strava API.

This module provides a Strava API client that is responsible for making
all HTTP requests, handling responses, and raising appropriate exceptions
for any API errors.
"""

import logging
from typing import Any

import requests
from pydantic import SecretStr

from .exceptions import APIError, ConfigError, RateLimitError, UnauthorizedError
from .models import Token
from .settings import StravaAPISettings

STRAVA_API_BASE_URL = "https://www.strava.com/api/v3"
STRAVA_OAUTH_URL = "https://www.strava.com/oauth"


# Default timeout for all HTTP requests (connect, read) in seconds.
DEFAULT_TIMEOUT = (10, 30)


class StravaClient:
    """A client for interacting with the Strava API."""

    def __init__(self, api_settings: StravaAPISettings):
        self.api_settings = api_settings
        self.session = requests.Session()

    def _get_required_client_id(self) -> str:
        if self.api_settings.client_id is None:
            raise ConfigError("Strava Client ID is not configured.")
        return self.api_settings.client_id.get_secret_value()

    def _get_required_client_secret(self) -> str:
        if self.api_settings.client_secret is None:
            raise ConfigError("Strava Client Secret is not configured.")
        return self.api_settings.client_secret.get_secret_value()

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle the response from the Strava API, raising exceptions for errors."""
        if response.status_code == 401:
            raise UnauthorizedError()
        if response.status_code == 429:
            raise RateLimitError()
        if not response.ok:
            raise APIError(response.status_code, response.text)
        return response.json()

    def get_authorization_url(self) -> str:
        """Construct the Strava authorization URL for the user."""
        redirect_uri = "http://localhost"
        scope = "profile:read_all,activity:read_all"
        return (
            f"{STRAVA_OAUTH_URL}/authorize?"
            f"client_id={self._get_required_client_id()}"
            f"&response_type=code&redirect_uri={redirect_uri}"
            f"&approval_prompt=force&scope={scope}"
        )

    def exchange_auth_code_for_token(self, auth_code: str) -> Token:
        """Exchange an authorization code for a full token."""
        response = self.session.post(
            f"{STRAVA_OAUTH_URL}/token",
            data={
                "client_id": self._get_required_client_id(),
                "client_secret": self._get_required_client_secret(),
                "code": auth_code,
                "grant_type": "authorization_code",
            },
            timeout=DEFAULT_TIMEOUT,
        )
        token_data = self._handle_response(response)
        return Token(**token_data)

    def refresh_token(self, refresh_token: SecretStr) -> Token:
        """Refresh an expired access token."""
        logging.info("Refreshing Strava access token.")
        response = self.session.post(
            f"{STRAVA_OAUTH_URL}/token",
            data={
                "client_id": self._get_required_client_id(),
                "client_secret": self._get_required_client_secret(),
                "grant_type": "refresh_token",
                "refresh_token": refresh_token.get_secret_value(),
            },
            timeout=DEFAULT_TIMEOUT,
        )
        token_data = self._handle_response(response)
        return Token(**token_data)

    def get_activities(
        self,
        access_token: SecretStr,
        page: int,
        per_page: int,
        after: int | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch a single page of activities.

        Args:
            access_token: OAuth access token.
            page: Page number (1-indexed).
            per_page: Number of activities per page.
            after: Only return activities after this epoch timestamp.
        """
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if after is not None:
            params["after"] = after

        response = self.session.get(
            f"{STRAVA_API_BASE_URL}/athlete/activities",
            headers={"Authorization": f"Bearer {access_token.get_secret_value()}"},
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        return self._handle_response(response)

    def get_activity(
        self, access_token: SecretStr, activity_id: int
    ) -> dict[str, Any]:
        """Fetch metadata for a single activity by ID.

        Args:
            access_token: OAuth access token.
            activity_id: Strava activity ID.

        Returns:
            Activity metadata dict.
        """
        response = self.session.get(
            f"{STRAVA_API_BASE_URL}/activities/{activity_id}",
            headers={"Authorization": f"Bearer {access_token.get_secret_value()}"},
            timeout=DEFAULT_TIMEOUT,
        )
        return self._handle_response(response)

    def get_activity_streams(
        self, access_token: SecretStr, activity_id: int
    ) -> dict[str, Any]:
        """Fetch the streams for a single activity."""
        stream_keys = [
            "time",
            "distance",
            "latlng",
            "altitude",
            "velocity_smooth",
            "heartrate",
            "cadence",
            "watts",
            "moving",
            "grade_smooth",
        ]
        response = self.session.get(
            f"{STRAVA_API_BASE_URL}/activities/{activity_id}/streams",
            headers={"Authorization": f"Bearer {access_token.get_secret_value()}"},
            params={"keys": ",".join(stream_keys), "key_by_type": "true"},
            timeout=DEFAULT_TIMEOUT,
        )
        return self._handle_response(response)
