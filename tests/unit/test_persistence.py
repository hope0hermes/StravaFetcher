"""Unit tests for persistence module."""

from pathlib import Path

import pytest

from strava_fetcher.models import Token
from strava_fetcher.persistence import TokenPersistence


@pytest.mark.unit
def test_token_persistence_read_nonexistent(tmp_path: Path):
    """Test reading token from non-existent file."""
    token_path = tmp_path / "token.json"
    persistence = TokenPersistence(token_path)

    token = persistence.read()

    assert token is None


@pytest.mark.unit
def test_token_persistence_write_and_read(tmp_path: Path, sample_token_data: dict):
    """Test writing and reading a token."""
    token_path = tmp_path / "token.json"
    persistence = TokenPersistence(token_path)

    # Create and write token
    token = Token(**sample_token_data)
    persistence.write(token)

    # Verify file exists
    assert token_path.exists()

    # Read back and verify
    read_token = persistence.read()
    assert read_token is not None
    assert read_token.access_token == token.access_token
    assert read_token.refresh_token == token.refresh_token


@pytest.mark.unit
def test_token_persistence_invalid_json(tmp_path: Path):
    """Test reading token from file with invalid JSON."""
    token_path = tmp_path / "token.json"

    # Write invalid JSON
    with open(token_path, "w") as f:
        f.write("not valid json")

    persistence = TokenPersistence(token_path)
    token = persistence.read()

    assert token is None


@pytest.mark.unit
def test_token_persistence_creates_directory(tmp_path: Path, sample_token_data: dict):
    """Test that persistence creates necessary directories."""
    token_path = tmp_path / "nested" / "dir" / "token.json"
    persistence = TokenPersistence(token_path)

    # Write token to nested path
    token = Token(**sample_token_data)
    persistence.write(token)

    # Verify directory was created
    assert token_path.parent.exists()
    assert token_path.exists()


@pytest.mark.unit
def test_token_persistence_none_path():
    """Test TokenPersistence with None path."""
    persistence = TokenPersistence(None)

    # Should not raise exceptions
    token = persistence.read()
    assert token is None

    # Writing should also be safe
    sample_token = Token(
        access_token="test",
        refresh_token="test",
        expires_at=123456,
        token_type="Bearer",
    )
    persistence.write(sample_token)  # Should not raise
