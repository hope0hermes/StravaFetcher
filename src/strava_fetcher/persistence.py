"""
Handles all file I/O operations for the Strava Fetcher package.

This module provides a clean separation of concerns for data persistence,
allowing other components to remain unaware of the underlying storage details.
"""

import json
import logging
from pathlib import Path

import pandas as pd

from .models import Token


class TokenPersistence:
    """Manages reading and writing the Strava token file."""

    def __init__(self, token_path: Path | None):
        self.token_path = token_path

    def read(self) -> Token | None:
        """
        Read the token from the file system.

        Returns:
            A Token object if the file exists and is valid, otherwise None.

        """
        if self.token_path is None or not self.token_path.is_file():
            logging.info("Token file not found at %s.", self.token_path)
            return None
        try:
            with open(self.token_path, encoding="utf-8") as f:
                token_data = json.load(f)
            return Token(**token_data)
        except (json.JSONDecodeError, TypeError) as e:
            logging.warning(
                "Could not read or validate token file at %s: %s", self.token_path, e
            )
            return None

    def write(self, token: Token) -> None:
        """Write token to the file system, ensuring secret values are preserved."""
        if self.token_path is None:
            return
        try:
            self.token_path.parent.mkdir(parents=True, exist_ok=True)

            # Create a dictionary with the actual secret values for serialization
            token_dict_to_save = {
                "access_token": token.access_token.get_secret_value(),
                "refresh_token": token.refresh_token.get_secret_value(),
                "expires_at": token.expires_at,
            }

            with open(self.token_path, "w", encoding="utf-8") as f:
                json.dump(token_dict_to_save, f, indent=4)

            logging.info("Token successfully written to %s", self.token_path)
        except OSError as e:
            logging.error("Failed to write token to %s: %s", self.token_path, e)
            raise


class ActivityPersistence:
    """Manages reading and writing activity and stream data."""

    def __init__(self, cache_file: Path | None, streams_dir: Path | None):
        self.cache_file = cache_file
        self.streams_dir = streams_dir

    def read_cache(self) -> pd.DataFrame | None:
        """Read the activity summary cache file."""
        if self.cache_file is None or not self.cache_file.is_file():
            return None
        return pd.read_csv(self.cache_file, sep=";")

    def write_cache(self, activities_df: pd.DataFrame) -> None:
        """Write the activity summary cache file."""
        if self.cache_file is None:
            return
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        activities_df.to_csv(self.cache_file, sep=";", index=False)

    def get_existing_stream_ids(self) -> set[int]:
        """Return a set of activity IDs for which stream files already exist."""
        if self.streams_dir is None or not self.streams_dir.is_dir():
            return set()
        return {
            int(f.stem.replace("stream_", ""))
            for f in self.streams_dir.glob("stream_*.csv")
            if f.is_file() and f.stat().st_size > 0
        }

    def write_stream(self, activity_id: int, stream_df: pd.DataFrame) -> None:
        """Write a single activity stream to a CSV file."""
        if self.streams_dir is None:
            return
        self.streams_dir.mkdir(parents=True, exist_ok=True)
        outfile = self.streams_dir / f"stream_{activity_id:09d}.csv"
        stream_df.to_csv(outfile, sep=";", index=True)
