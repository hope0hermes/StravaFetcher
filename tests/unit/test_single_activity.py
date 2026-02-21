"""Tests for single-activity fetch support (Phase 5)."""

from unittest.mock import MagicMock, PropertyMock, patch

import pandas as pd
import pytest

from strava_fetcher.pipeline import StravaSyncPipeline


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = MagicMock()
    settings.strava_api = MagicMock()
    settings.paths.token_file = MagicMock()
    settings.paths.activities_cache_file = MagicMock()
    settings.paths.streams_dir = MagicMock()
    settings.sync.skip_trainer_activities = False
    return settings


@pytest.fixture
def pipeline(mock_settings):
    """Create a StravaSyncPipeline with mocked dependencies."""
    with patch.object(StravaSyncPipeline, "__init__", lambda self, *a, **kw: None):
        p = StravaSyncPipeline.__new__(StravaSyncPipeline)
        p.settings = mock_settings
        p.client = MagicMock()
        p.token_persistence = MagicMock()
        p.activity_persistence = MagicMock()
        p.max_auth_attempts = 3
        p._auth_attempts = 0
        return p


class TestFetchSingleActivity:
    """Tests for StravaSyncPipeline.fetch_single_activity()."""

    def test_fetches_metadata_and_stream(self, pipeline):
        """Happy path: fetches metadata, appends to cache, gets stream."""
        token = MagicMock()
        pipeline._get_valid_token = MagicMock(return_value=token)
        pipeline.client.get_activity.return_value = {
            "id": 99999, "name": "Test Ride"
        }
        pipeline.client.get_activity_streams.return_value = {
            "time": {"data": [0, 1, 2]},
            "watts": {"data": [100, 200, 150]},
        }
        pipeline.activity_persistence.read_cache.return_value = pd.DataFrame(
            {"id": [11111], "name": ["Old Ride"]}
        )
        pipeline.activity_persistence.get_existing_stream_ids.return_value = set()

        pipeline.fetch_single_activity(99999)

        pipeline.client.get_activity.assert_called_once_with(
            token.access_token, 99999
        )
        pipeline.activity_persistence.write_cache.assert_called_once()
        written_df = pipeline.activity_persistence.write_cache.call_args[0][0]
        assert 99999 in written_df["id"].values
        assert 11111 in written_df["id"].values

        pipeline.activity_persistence.write_stream.assert_called_once()

    def test_skips_stream_if_exists(self, pipeline):
        """Doesn't re-fetch stream if already on disk."""
        token = MagicMock()
        pipeline._get_valid_token = MagicMock(return_value=token)
        pipeline.client.get_activity.return_value = {"id": 99999, "name": "Test"}
        pipeline.activity_persistence.read_cache.return_value = None
        pipeline.activity_persistence.get_existing_stream_ids.return_value = {99999}

        pipeline.fetch_single_activity(99999)

        pipeline.client.get_activity_streams.assert_not_called()
        pipeline.activity_persistence.write_stream.assert_not_called()

    def test_deduplicates_existing_activity(self, pipeline):
        """Activity already in cache: update + deduplicate."""
        token = MagicMock()
        pipeline._get_valid_token = MagicMock(return_value=token)
        pipeline.client.get_activity.return_value = {
            "id": 11111, "name": "Updated Ride"
        }
        pipeline.activity_persistence.read_cache.return_value = pd.DataFrame(
            {"id": [11111], "name": ["Old Ride"]}
        )
        pipeline.activity_persistence.get_existing_stream_ids.return_value = {11111}

        pipeline.fetch_single_activity(11111)

        written_df = pipeline.activity_persistence.write_cache.call_args[0][0]
        assert len(written_df) == 1  # deduplicated
        assert written_df.iloc[0]["id"] == 11111

    def test_first_activity_no_existing_cache(self, pipeline):
        """Works when there's no existing activities cache."""
        token = MagicMock()
        pipeline._get_valid_token = MagicMock(return_value=token)
        pipeline.client.get_activity.return_value = {"id": 12345, "name": "First"}
        pipeline.activity_persistence.read_cache.return_value = None
        pipeline.activity_persistence.get_existing_stream_ids.return_value = set()
        pipeline.client.get_activity_streams.return_value = {
            "time": {"data": [0]}, "moving": {"data": [True]}
        }

        pipeline.fetch_single_activity(12345)

        written_df = pipeline.activity_persistence.write_cache.call_args[0][0]
        assert len(written_df) == 1
        assert written_df.iloc[0]["id"] == 12345
        pipeline.activity_persistence.write_stream.assert_called_once()
