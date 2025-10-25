"""
Shared pytest fixtures for StravaFetcher tests.

This module provides reusable fixtures for:
- Test configuration and settings
- Mock Strava API responses
- Temporary directories and files
- Sample data (activities, streams, tokens)
"""

from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest
import yaml
from pydantic import SecretStr

from strava_fetcher.settings import (
    PathSettings,
    Settings,
    StravaAPISettings,
    SyncSettings,
)

# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def temp_config_file(tmp_path: Path) -> Path:
    """Create a temporary YAML config file for testing."""
    config_path = tmp_path / "config.yaml"
    return config_path


@pytest.fixture
def sample_config_dict() -> dict:
    """Provide a sample configuration dictionary."""
    return {
        "strava_api": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
        },
        "paths": {
            "data_dir": "data",
            "token_file": "data/token.json",
            "activities_cache_file": "data/activities.csv",
            "streams_dir": "data/Streams",
        },
        "sync": {
            "max_pages": 10,
            "retry_interval_seconds": 60,
            "skip_trainer_activities": False,
        },
    }


@pytest.fixture
def sample_config_file(tmp_path: Path, sample_config_dict: dict) -> Path:
    """Create a temporary config file with sample data."""
    config_path = tmp_path / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(sample_config_dict, f)
    return config_path


@pytest.fixture
def mock_settings(tmp_path: Path) -> Settings:
    """Provide mock settings for testing."""
    # Create necessary directories and files for PathSettings validation
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    streams_dir = data_dir / "Streams"
    streams_dir.mkdir(parents=True, exist_ok=True)

    token_file = data_dir / "token.json"
    token_file.touch()

    activities_file = data_dir / "activities.csv"
    activities_file.touch()

    return Settings(
        strava_api=StravaAPISettings(
            client_id=SecretStr("test_client_id"),
            client_secret=SecretStr("test_client_secret"),
        ),
        paths=PathSettings(
            data_dir=data_dir,
            token_file=token_file,
            activities_cache_file=activities_file,
            streams_dir=streams_dir,
        ),
        sync=SyncSettings(
            max_pages=10,
            retry_interval_seconds=60,
            skip_trainer_activities=False,
        ),
    )


@pytest.fixture
def mock_settings_no_credentials(tmp_path: Path) -> Settings:
    """Provide mock settings without API credentials."""
    # Create necessary directories and files for PathSettings validation
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    streams_dir = data_dir / "Streams"
    streams_dir.mkdir(parents=True, exist_ok=True)

    token_file = data_dir / "token.json"
    token_file.touch()

    activities_file = data_dir / "activities.csv"
    activities_file.touch()

    return Settings(
        strava_api=StravaAPISettings(
            client_id=None,
            client_secret=None,
        ),
        paths=PathSettings(
            data_dir=data_dir,
            token_file=token_file,
            activities_cache_file=activities_file,
            streams_dir=streams_dir,
        ),
    )


# ============================================================================
# Mock API Response Fixtures
# ============================================================================


@pytest.fixture
def mock_token_response() -> dict:
    """Provide a mock OAuth token response."""
    return {
        "token_type": "Bearer",
        "expires_at": 1234567890,
        "expires_in": 21600,
        "refresh_token": "mock_refresh_token",
        "access_token": "mock_access_token",
        "athlete": {
            "id": 12345,
            "username": "test_athlete",
            "firstname": "Test",
            "lastname": "Athlete",
        },
    }


@pytest.fixture
def mock_activity_response() -> list[dict]:
    """Provide a mock activities API response."""
    return [
        {
            "id": 12345678,
            "name": "Morning Ride",
            "type": "Ride",
            "distance": 25000.0,
            "moving_time": 3600,
            "elapsed_time": 3900,
            "total_elevation_gain": 250.0,
            "start_date": "2024-01-15T08:30:00Z",
            "start_date_local": "2024-01-15T08:30:00Z",
            "timezone": "(GMT+00:00) Europe/London",
            "achievement_count": 5,
            "kudos_count": 12,
            "average_speed": 6.944,
            "max_speed": 12.5,
            "has_heartrate": True,
            "average_heartrate": 145.0,
            "max_heartrate": 178.0,
            "elev_high": 150.0,
            "elev_low": 50.0,
            "trainer": False,
            "commute": False,
            "manual": False,
            "private": False,
        },
        {
            "id": 12345679,
            "name": "Evening Run",
            "type": "Run",
            "distance": 8000.0,
            "moving_time": 2400,
            "elapsed_time": 2500,
            "total_elevation_gain": 50.0,
            "start_date": "2024-01-16T18:00:00Z",
            "start_date_local": "2024-01-16T18:00:00Z",
            "timezone": "(GMT+00:00) Europe/London",
            "achievement_count": 2,
            "kudos_count": 8,
            "average_speed": 3.333,
            "max_speed": 4.5,
            "has_heartrate": True,
            "average_heartrate": 155.0,
            "max_heartrate": 180.0,
            "trainer": False,
            "commute": False,
            "manual": False,
            "private": False,
        },
    ]


@pytest.fixture
def mock_stream_response() -> dict:
    """Provide a mock stream data API response."""
    return {
        "time": {"data": list(range(0, 3600, 1))},
        "distance": {"data": [i * 7.0 for i in range(3600)]},
        "altitude": {"data": [100.0 + (i % 100) * 0.5 for i in range(3600)]},
        "velocity_smooth": {"data": [7.0 + (i % 10) * 0.5 for i in range(3600)]},
        "heartrate": {"data": [140 + (i % 40) for i in range(3600)]},
        "cadence": {"data": [80 + (i % 20) for i in range(3600)]},
        "watts": {"data": [200 + (i % 100) for i in range(3600)]},
        "temp": {"data": [20.0 + (i % 5) * 0.5 for i in range(3600)]},
        "moving": {"data": [True] * 3600},
        "grade_smooth": {"data": [0.0 + (i % 20) * 0.1 for i in range(3600)]},
    }


@pytest.fixture
def mock_rate_limit_response() -> Mock:
    """Provide a mock rate limit (429) response."""
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.json.return_value = {
        "message": "Rate Limit Exceeded",
        "errors": [
            {
                "resource": "Application",
                "field": "rate limit",
                "code": "exceeded",
            }
        ],
    }
    return mock_response


@pytest.fixture
def mock_unauthorized_response() -> Mock:
    """Provide a mock unauthorized (401) response."""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {
        "message": "Authorization Error",
        "errors": [
            {
                "resource": "Athlete",
                "field": "access_token",
                "code": "invalid",
            }
        ],
    }
    return mock_response


# ============================================================================
# Data Fixtures - Activities
# ============================================================================


@pytest.fixture
def sample_activity() -> dict:
    """Provide a single sample activity."""
    return {
        "id": 12345678,
        "name": "Morning Ride",
        "type": "Ride",
        "distance": 25000.0,
        "moving_time": 3600,
        "elapsed_time": 3900,
        "total_elevation_gain": 250.0,
        "start_date": "2024-01-15T08:30:00Z",
        "average_speed": 6.944,
        "max_speed": 12.5,
        "has_heartrate": True,
        "average_heartrate": 145.0,
        "trainer": False,
    }


@pytest.fixture
def sample_activities_df() -> pd.DataFrame:
    """Provide a sample activities DataFrame."""
    return pd.DataFrame(
        {
            "id": [12345678, 12345679, 12345680],
            "name": ["Morning Ride", "Evening Run", "Weekend Long"],
            "type": ["Ride", "Run", "Ride"],
            "distance": [25000.0, 8000.0, 80000.0],
            "moving_time": [3600, 2400, 14400],
            "elapsed_time": [3900, 2500, 15000],
            "total_elevation_gain": [250.0, 50.0, 1200.0],
            "start_date": [
                "2024-01-15T08:30:00Z",
                "2024-01-16T18:00:00Z",
                "2024-01-20T09:00:00Z",
            ],
            "trainer": [False, False, False],
        }
    )


@pytest.fixture
def sample_activities_csv(tmp_path: Path, sample_activities_df: pd.DataFrame) -> Path:
    """Create a temporary activities CSV file."""
    csv_path = tmp_path / "activities.csv"
    sample_activities_df.to_csv(csv_path, index=False)
    return csv_path


# ============================================================================
# Data Fixtures - Streams
# ============================================================================


@pytest.fixture
def sample_stream_data() -> dict:
    """Provide sample stream data."""
    return {
        "time": list(range(3600)),
        "distance": [i * 7.0 for i in range(3600)],
        "altitude": [100.0 + (i % 100) * 0.5 for i in range(3600)],
        "heartrate": [140 + (i % 40) for i in range(3600)],
        "watts": [200 + (i % 100) for i in range(3600)],
        "cadence": [80 + (i % 20) for i in range(3600)],
    }


@pytest.fixture
def sample_stream_df(sample_stream_data: dict) -> pd.DataFrame:
    """Provide sample stream DataFrame."""
    return pd.DataFrame(sample_stream_data)


@pytest.fixture
def sample_stream_csv(tmp_path: Path, sample_stream_df: pd.DataFrame) -> Path:
    """Create a temporary stream CSV file."""
    csv_path = tmp_path / "stream_12345678.csv"
    sample_stream_df.to_csv(csv_path, index=False)
    return csv_path


# ============================================================================
# Data Fixtures - Tokens
# ============================================================================


@pytest.fixture
def sample_token_data() -> dict:
    """Provide sample OAuth token data."""
    return {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_at": 1234567890,
        "token_type": "Bearer",
    }


@pytest.fixture
def sample_token_file(tmp_path: Path, sample_token_data: dict) -> Path:
    """Create a temporary token JSON file."""
    import json

    token_path = tmp_path / "token.json"
    with open(token_path, "w") as f:
        json.dump(sample_token_data, f)
    return token_path


# ============================================================================
# Temporary Directory Fixtures
# ============================================================================


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Create a temporary data directory structure."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "Streams").mkdir()
    return data_dir


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


# ============================================================================
# Test Data Directories
# ============================================================================


@pytest.fixture
def test_data_dir() -> Path:
    """Provide path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def fixtures_dir() -> Path:
    """Provide path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"
