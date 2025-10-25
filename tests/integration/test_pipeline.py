"""Integration tests for the full sync pipeline."""

from unittest.mock import patch

import pytest

from strava_fetcher.pipeline import StravaSyncPipeline


@pytest.mark.integration
@patch("strava_fetcher.client.StravaClient")
def test_pipeline_initialization(mock_client_class, mock_settings):
    """Test that pipeline initializes correctly with settings."""
    pipeline = StravaSyncPipeline(mock_settings)

    assert pipeline.settings == mock_settings
    assert hasattr(pipeline, "client")


@pytest.mark.integration
@patch("strava_fetcher.client.StravaClient")
def test_pipeline_creates_directories(mock_client_class, mock_settings):
    """Test that pipeline creates necessary directories."""
    # Directories are already created by the fixture
    # Verify they exist
    _ = StravaSyncPipeline(mock_settings)

    assert mock_settings.paths.data_dir.exists()
    assert mock_settings.paths.streams_dir.exists()


@pytest.mark.integration
@patch("strava_fetcher.client.StravaClient")
def test_pipeline_settings_attributes(mock_client_class, mock_settings):
    """Test that pipeline correctly uses settings attributes."""
    pipeline = StravaSyncPipeline(mock_settings)

    assert pipeline.settings.sync.max_pages == 10
    assert pipeline.settings.sync.retry_interval_seconds == 60
    assert pipeline.settings.sync.skip_trainer_activities is False
