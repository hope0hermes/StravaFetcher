"""Custom exceptions for the Strava Fetcher package."""


class StravaFetcherError(Exception):
    """Base exception for all errors raised by this package."""


class ConfigError(StravaFetcherError):
    """Raised for configuration-related errors."""

    def __init__(
        self,
        message: str | None = "Configuration error occurred.",
        original_exc: Exception | None = None,
    ):
        super().__init__(message)
        self.original_exc = original_exc


class APIError(StravaFetcherError):
    """Raised for errors communicating with the Strava API."""

    def __init__(self, status_code: int, message: str | None = None):
        self.status_code = status_code
        super().__init__(f"API Error {status_code}: {message or 'Unknown error'}")


class RateLimitError(APIError):
    """Raised specifically when the Strava API rate limit is exceeded."""

    def __init__(self, message: str = "Strava API rate limit exceeded."):
        super().__init__(status_code=429, message=message)


class UnauthorizedError(APIError):
    """Raised for 401 Unauthorized errors, typically due to an invalid token."""

    def __init__(
        self, message: str = "Unauthorized. The access token may be invalid or expired."
    ):
        super().__init__(status_code=401, message=message)
