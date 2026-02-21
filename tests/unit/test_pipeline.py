"""Unit tests for the sync pipeline — incremental fetching logic."""

from unittest.mock import MagicMock, call, patch

import pandas as pd
import pytest
from pydantic import SecretStr

from strava_fetcher.models import Token
from strava_fetcher.pipeline import StravaSyncPipeline


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_token() -> Token:
    return Token(
        access_token="test_access",
        refresh_token="test_refresh",
        expires_at=9999999999,
    )


def _make_activities_df(start_dates: list[str], ids: list[int] | None = None) -> pd.DataFrame:
    """Build a minimal activities DataFrame with ``id`` and ``start_date``."""
    if ids is None:
        ids = list(range(1, len(start_dates) + 1))
    return pd.DataFrame({"id": ids, "start_date": start_dates})


# ---------------------------------------------------------------------------
# _get_after_epoch
# ---------------------------------------------------------------------------


class TestGetAfterEpoch:
    """Tests for ``StravaSyncPipeline._get_after_epoch``."""

    def test_returns_none_for_none_dataframe(self, mock_settings):
        pipeline = StravaSyncPipeline(mock_settings)
        assert pipeline._get_after_epoch(None) is None

    def test_returns_none_for_empty_dataframe(self, mock_settings):
        pipeline = StravaSyncPipeline(mock_settings)
        assert pipeline._get_after_epoch(pd.DataFrame()) is None

    def test_returns_none_when_no_start_date_column(self, mock_settings):
        pipeline = StravaSyncPipeline(mock_settings)
        df = pd.DataFrame({"id": [1, 2]})
        assert pipeline._get_after_epoch(df) is None

    def test_returns_epoch_for_valid_dates(self, mock_settings):
        pipeline = StravaSyncPipeline(mock_settings)
        df = _make_activities_df([
            "2024-01-15T08:30:00Z",
            "2024-06-20T12:00:00Z",
            "2024-03-01T06:00:00Z",
        ])
        epoch = pipeline._get_after_epoch(df)
        assert epoch is not None
        # 2024-06-20T12:00:00Z is the most recent
        expected = int(pd.Timestamp("2024-06-20T12:00:00Z").timestamp())
        assert epoch == expected

    def test_returns_none_for_unparseable_dates(self, mock_settings):
        pipeline = StravaSyncPipeline(mock_settings)
        df = pd.DataFrame({"id": [1], "start_date": ["not-a-date"]})
        # Should not raise; returns None as fallback
        assert pipeline._get_after_epoch(df) is None

    def test_returns_none_for_all_nat(self, mock_settings):
        pipeline = StravaSyncPipeline(mock_settings)
        df = pd.DataFrame({"id": [1], "start_date": [None]})
        assert pipeline._get_after_epoch(df) is None


# ---------------------------------------------------------------------------
# _sync_activities — incremental vs full
# ---------------------------------------------------------------------------


class TestSyncActivitiesIncremental:
    """Tests for incremental / full activity synchronization."""

    def _setup_pipeline(self, mock_settings, existing_df=None):
        """Create pipeline with mocked persistence and client."""
        pipeline = StravaSyncPipeline(mock_settings)
        pipeline.activity_persistence = MagicMock()
        pipeline.activity_persistence.read_cache.return_value = existing_df
        pipeline.client = MagicMock()
        return pipeline

    def test_incremental_passes_after_epoch(self, mock_settings):
        """When cache has dates, ``after`` epoch should be sent to the client."""
        existing = _make_activities_df(
            ["2024-01-15T08:30:00Z", "2024-06-20T12:00:00Z"],
            ids=[100, 200],
        )
        pipeline = self._setup_pipeline(mock_settings, existing_df=existing)
        # Return one new activity, then empty page
        pipeline.client.get_activities.side_effect = [
            [{"id": 300, "start_date": "2024-07-01T10:00:00Z"}],
            [],
        ]

        pipeline._sync_activities(_make_token(), full=False)

        expected_epoch = int(pd.Timestamp("2024-06-20T12:00:00Z").timestamp())
        first_call = pipeline.client.get_activities.call_args_list[0]
        assert first_call.kwargs.get("after") == expected_epoch or \
            first_call[1].get("after") == expected_epoch or \
            (len(first_call[0]) > 3 and first_call[0][3] == expected_epoch) or \
            first_call == call(
                _make_token().access_token, 1, per_page=100, after=expected_epoch,
            )

    def test_full_flag_skips_after_epoch(self, mock_settings):
        """With ``full=True``, ``after`` should be None even when cache exists."""
        existing = _make_activities_df(
            ["2024-06-20T12:00:00Z"],
            ids=[100],
        )
        pipeline = self._setup_pipeline(mock_settings, existing_df=existing)
        pipeline.client.get_activities.return_value = []

        pipeline._sync_activities(_make_token(), full=True)

        first_call = pipeline.client.get_activities.call_args_list[0]
        # after should be None
        _, kwargs = first_call
        assert kwargs.get("after") is None

    def test_first_run_no_cache(self, mock_settings):
        """First run — no cache at all — should fetch without ``after``."""
        pipeline = self._setup_pipeline(mock_settings, existing_df=None)
        pipeline.client.get_activities.return_value = []

        pipeline._sync_activities(_make_token(), full=False)

        first_call = pipeline.client.get_activities.call_args_list[0]
        _, kwargs = first_call
        assert kwargs.get("after") is None

    def test_dedup_still_works(self, mock_settings):
        """Cache + new page with overlapping IDs → written df has unique IDs."""
        existing = _make_activities_df(
            ["2024-01-15T08:30:00Z", "2024-06-20T12:00:00Z"],
            ids=[100, 200],
        )
        pipeline = self._setup_pipeline(mock_settings, existing_df=existing)
        # API returns an overlap (id 200) plus a new one (id 300)
        pipeline.client.get_activities.side_effect = [
            [
                {"id": 200, "start_date": "2024-06-20T12:00:00Z"},
                {"id": 300, "start_date": "2024-07-01T10:00:00Z"},
            ],
            [],
        ]

        pipeline._sync_activities(_make_token(), full=False)

        written_df = pipeline.activity_persistence.write_cache.call_args[0][0]
        assert list(sorted(written_df["id"].tolist())) == [100, 200, 300]

    def test_no_activities_at_all(self, mock_settings):
        """Empty cache + empty API → nothing written."""
        pipeline = self._setup_pipeline(mock_settings, existing_df=None)
        pipeline.client.get_activities.return_value = []

        pipeline._sync_activities(_make_token(), full=False)

        pipeline.activity_persistence.write_cache.assert_not_called()


# ---------------------------------------------------------------------------
# run() forwards full flag
# ---------------------------------------------------------------------------


class TestRunForwardsFullFlag:
    """Verify ``run(full=...)`` propagates to ``_sync_activities``."""

    @patch.object(StravaSyncPipeline, "_get_valid_token", return_value=_make_token())
    @patch.object(StravaSyncPipeline, "_sync_streams")
    @patch.object(StravaSyncPipeline, "_sync_activities")
    def test_run_passes_full_true(self, mock_sync_act, mock_sync_str, mock_token, mock_settings):
        pipeline = StravaSyncPipeline(mock_settings)
        pipeline.run(full=True)
        mock_sync_act.assert_called_once_with(_make_token(), full=True)

    @patch.object(StravaSyncPipeline, "_get_valid_token", return_value=_make_token())
    @patch.object(StravaSyncPipeline, "_sync_streams")
    @patch.object(StravaSyncPipeline, "_sync_activities")
    def test_run_defaults_to_incremental(self, mock_sync_act, mock_sync_str, mock_token, mock_settings):
        pipeline = StravaSyncPipeline(mock_settings)
        pipeline.run()
        mock_sync_act.assert_called_once_with(_make_token(), full=False)
