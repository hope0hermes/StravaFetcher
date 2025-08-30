"""
Orchestrates the full Strava data synchronization pipeline.

This module contains the main `StravaSyncPipeline` class, which brings together
all the components of the package to perform the following steps:
1. Ensure a valid Strava access token is available.
2. Synchronize all activity summaries.
3. Synchronize all missing activity streams.
"""

import logging
import time

import click
import pandas as pd

from .client import StravaClient
from .exceptions import ConfigError, RateLimitError, UnauthorizedError
from .models import Token
from .persistence import ActivityPersistence, TokenPersistence
from .settings import Settings


class StravaSyncPipeline:
    """Orchestrates the synchronization of Strava data."""

    def __init__(self, settings: Settings, max_auth_attempts: int = 3):
        self.settings = settings
        self.client = StravaClient(settings.strava_api)
        self.token_persistence = TokenPersistence(settings.paths.token_file)
        self.activity_persistence = ActivityPersistence(
            settings.paths.activities_cache_file, settings.paths.streams_dir
        )
        self.max_auth_attempts = max_auth_attempts
        self._auth_attempts = 0

    def _get_valid_token(self) -> Token:
        """
        Ensures a valid Strava token is available, refreshing it if necessary.
        If no token exists, it guides the user through the authorization process.
        """
        token = self.token_persistence.read()

        if token and not token.is_expired():
            logging.info("Using existing, valid Strava token.")
            return token

        if token and token.is_expired():
            logging.info("Strava token has expired. Refreshing...")
            try:
                new_token = self.client.refresh_token(token.refresh_token)
                self.token_persistence.write(new_token)
                return new_token
            except UnauthorizedError:
                logging.warning("Token refresh failed. Please re-authorize.")
                self._auth_attempts += 1
                if self._auth_attempts >= self.max_auth_attempts:
                    raise ConfigError(
                        f"Exceeded maximum {self.max_auth_attempts} re-authorization "
                        "attempts."
                    ) from None
                # Fall through to re-authorization

        # --- Full Authorization Flow ---
        auth_url = self.client.get_authorization_url()
        click.echo("Please authorize this application to access your Strava data:")
        click.echo(f"1. Open this URL in your browser:\n   {auth_url}")
        click.echo("2. Authorize the app and copy the 'code' from the redirected URL.")
        auth_code = click.prompt("3. Paste the authorization code here").strip()

        new_token = self.client.exchange_auth_code_for_token(auth_code)
        self.token_persistence.write(new_token)
        logging.info("New Strava token obtained and saved.")
        self._auth_attempts = 0  # Reset attempts on successful authorization
        return new_token

    def _sync_activities(self, token: Token) -> None:
        """Synchronizes all activity summaries."""
        logging.info("Starting activity summary synchronization.")

        existing_activities_df = self.activity_persistence.read_cache()
        all_activities = []
        if existing_activities_df is not None:
            all_activities.append(existing_activities_df)

        for page in range(1, self.settings.sync.max_pages + 1):
            logging.info(f"Fetching activity page {page}...")
            activities = self.client.get_activities(
                token.access_token, page, per_page=100
            )
            if not activities:
                logging.info("No more activities found. Stopping.")
                break
            all_activities.append(pd.json_normalize(activities))

        if not all_activities:
            logging.info("No activities found to synchronize.")
            return

        combined_df = (
            pd.concat(all_activities)
            .drop_duplicates(subset="id")
            .reset_index(drop=True)
        )
        self.activity_persistence.write_cache(combined_df)
        logging.info(
            f"Activity cache updated with {len(combined_df)} total activities."
        )

    def _sync_streams(self, token: Token) -> None:
        """Synchronizes all missing activity streams."""
        logging.info("Starting activity stream synchronization.")

        activities_df = self.activity_persistence.read_cache()
        if activities_df is None or activities_df.empty:
            logging.warning("No activities found in cache. Cannot sync streams.")
            return

        existing_stream_ids = self.activity_persistence.get_existing_stream_ids()
        activities_to_sync = activities_df[
            ~activities_df["id"].isin(existing_stream_ids)
        ]

        if activities_to_sync.empty:
            logging.info("All activity streams are already up to date.")
            return

        logging.info(f"Found {len(activities_to_sync)} activities needing streams.")

        for _, activity in activities_to_sync.iterrows():
            activity_id = activity["id"]
            if self.settings.sync.skip_trainer_activities and activity.get(
                "trainer", False
            ):
                logging.info(f"Skipping trainer activity {activity_id}.")
                continue

            logging.info(f"Fetching streams for activity {activity_id}...")
            try:
                streams_data = self.client.get_activity_streams(
                    token.access_token, activity_id
                )
                stream_df = pd.DataFrame(
                    {k: v["data"] for k, v in streams_data.items()}
                )
                self.activity_persistence.write_stream(activity_id, stream_df)
            except RateLimitError:
                wait_time = self.settings.sync.retry_interval_seconds
                logging.warning(f"Rate limit hit. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                # Re-raise to be handled by the main run loop
                raise
            except Exception as e:
                logging.error(
                    f"Failed to fetch streams for activity {activity_id}: {e}"
                )

    def run(self) -> None:
        """Executes the full data synchronization pipeline."""
        logging.info("--- Starting Strava Data Synchronization ---")

        try:
            token = self._get_valid_token()
            self._sync_activities(token)

            while True:
                try:
                    self._sync_streams(token)
                    break  # Exit loop if sync completes without rate limit error
                except RateLimitError:
                    continue  # Loop will restart after waiting

        except Exception as e:
            logging.critical(f"A critical error occurred: {e}", exc_info=True)
            raise

        logging.info("--- Strava Data Synchronization Completed ---")
