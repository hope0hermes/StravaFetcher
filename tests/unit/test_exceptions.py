"""Unit tests for exceptions module."""

import pytest

from strava_fetcher.exceptions import (
    APIError,
    ConfigError,
    RateLimitError,
    StravaFetcherError,
    UnauthorizedError,
)


@pytest.mark.unit
def test_base_exception():
    """Test base StravaFetcherError exception."""
    error = StravaFetcherError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


@pytest.mark.unit
def test_config_error():
    """Test ConfigError exception."""
    error = ConfigError("Configuration error")
    assert isinstance(error, StravaFetcherError)
    assert str(error) == "Configuration error"


@pytest.mark.unit
def test_config_error_with_original_exception():
    """Test ConfigError with original exception."""
    original = ValueError("Original error")
    error = ConfigError("Config failed", original_exc=original)

    assert isinstance(error, StravaFetcherError)
    assert error.original_exc == original


@pytest.mark.unit
def test_api_error():
    """Test APIError exception."""
    error = APIError(status_code=500, message="Server error")

    assert isinstance(error, StravaFetcherError)
    assert error.status_code == 500
    assert "500" in str(error)
    assert "Server error" in str(error)


@pytest.mark.unit
def test_api_error_without_message():
    """Test APIError without custom message."""
    error = APIError(status_code=404)

    assert error.status_code == 404
    assert "404" in str(error)
    assert "Unknown error" in str(error)


@pytest.mark.unit
def test_rate_limit_error():
    """Test RateLimitError exception."""
    error = RateLimitError()

    assert isinstance(error, APIError)
    assert isinstance(error, StravaFetcherError)
    assert error.status_code == 429
    assert "rate limit" in str(error).lower()


@pytest.mark.unit
def test_rate_limit_error_custom_message():
    """Test RateLimitError with custom message."""
    error = RateLimitError(message="Custom rate limit message")

    assert error.status_code == 429
    assert "Custom rate limit message" in str(error)


@pytest.mark.unit
def test_unauthorized_error():
    """Test UnauthorizedError exception."""
    error = UnauthorizedError()

    assert isinstance(error, APIError)
    assert isinstance(error, StravaFetcherError)
    assert error.status_code == 401
    assert "401" in str(error)


@pytest.mark.unit
def test_exception_hierarchy():
    """Test that exception hierarchy is correct."""
    # All custom exceptions should inherit from StravaFetcherError
    assert issubclass(ConfigError, StravaFetcherError)
    assert issubclass(APIError, StravaFetcherError)
    assert issubclass(RateLimitError, APIError)
    assert issubclass(UnauthorizedError, APIError)

    # And ultimately from Exception
    assert issubclass(StravaFetcherError, Exception)
