# Testing Strategy

This document outlines the testing philosophy and practices for StravaFetcher.

## Overview

StravaFetcher uses a comprehensive testing strategy to ensure reliability and maintainability:

- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: Tests for component interactions
- **Test Coverage**: Measure and improve code coverage
- **Continuous Integration**: Automated testing on every PR

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_client.py
│   ├── test_settings.py
│   ├── test_persistence.py
│   └── test_pipeline.py
├── integration/             # Integration tests
│   └── test_full_sync.py
└── fixtures/                # Test data
    └── sample_config.yaml
```

## Running Tests

### Run All Tests

```bash
# Using hatch (recommended)
hatch run test:default

# Using pytest directly
pytest
```

### Run with Coverage

```bash
# Full coverage report
hatch run test:cov

# Generate HTML report
pytest --cov=src/strava_fetcher --cov-report=html
open htmlcov/index.html  # View in browser
```

### Run Specific Tests

```bash
# Run single test file
pytest tests/unit/test_settings.py

# Run specific test
pytest tests/unit/test_settings.py::test_load_from_env_vars

# Run tests matching pattern
pytest -k "test_settings"

# Run only unit tests
pytest -m unit

# Run integration tests
pytest -m integration
```

### Run with Verbose Output

```bash
pytest -v                    # Verbose
pytest -vv                   # Very verbose
pytest -vv --tb=short        # Short traceback
pytest -x                    # Stop on first failure
pytest --pdb                 # Drop into debugger on failure
```

## Test Markers

Tests can be marked with decorators to categorize them:

```python
import pytest

@pytest.mark.unit
def test_fast_isolated():
    """Fast unit test."""
    pass

@pytest.mark.integration
def test_components_together():
    """Integration test."""
    pass

@pytest.mark.slow
def test_long_running():
    """Test that takes time."""
    pass
```

Run specific markers:
```bash
pytest -m unit           # Only unit tests
pytest -m "not slow"     # Skip slow tests
```

## Writing Tests

### Unit Test Example

```python
# tests/unit/test_client.py
import pytest
from strava_fetcher.client import StravaClient
from strava_fetcher.exceptions import APIError

def test_client_handles_rate_limit(mock_settings):
    """Test that client properly handles rate limits."""
    client = StravaClient(mock_settings)

    # Test implementation
    with pytest.raises(APIError):
        client.get_activities()
```

### Using Fixtures

```python
# tests/conftest.py
import pytest
from strava_fetcher.settings import Settings

@pytest.fixture
def mock_settings():
    """Provide mock settings for testing."""
    return Settings(
        strava_api={"client_id": "test_id", "client_secret": "test_secret"}
    )

# tests/unit/test_something.py
def test_with_fixture(mock_settings):
    """Test uses the fixture."""
    assert mock_settings.strava_api.client_id == "test_id"
```

### Mocking External APIs

```python
from unittest.mock import Mock, patch

@patch('strava_fetcher.client.requests.get')
def test_api_call(mock_get):
    """Test API call with mocked response."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response

    # Test code here
```

## Coverage Goals

### Current Coverage

Check current coverage:
```bash
hatch run test:cov
```

### Coverage Targets

| Component | Target | Priority |
|-----------|--------|----------|
| Core Logic (client, pipeline) | 80%+ | High |
| Settings & Configuration | 90%+ | High |
| Data Persistence | 80%+ | Medium |
| CLI Interface | 60%+ | Medium |
| Exception Handling | 70%+ | Medium |

### Improving Coverage

1. **Identify gaps**:
   ```bash
   pytest --cov=src/strava_fetcher --cov-report=html
   open htmlcov/index.html
   ```

2. **Add tests for uncovered lines**:
   - Focus on critical paths first
   - Test error conditions
   - Test edge cases

3. **Use coverage exclusions sparingly**:
   ```python
   def debug_only():  # pragma: no cover
       """This only runs in debug mode."""
       pass
   ```

## Test Best Practices

### 1. Test Naming

Use descriptive names that explain what is being tested:

```python
# Good
def test_client_retries_on_rate_limit():
    pass

def test_settings_load_from_env_vars():
    pass

# Avoid
def test_client():
    pass

def test_1():
    pass
```

### 2. Test Structure

Follow the **Arrange-Act-Assert** pattern:

```python
def test_something():
    # Arrange - Set up test data and conditions
    settings = Settings()
    client = StravaClient(settings)

    # Act - Execute the code being tested
    result = client.get_activities()

    # Assert - Verify the outcome
    assert len(result) > 0
    assert result[0]["type"] == "Ride"
```

### 3. Test Independence

Each test should be independent:

```python
# Good - Each test sets up its own data
def test_first():
    data = create_test_data()
    assert process(data) == expected

def test_second():
    data = create_test_data()
    assert validate(data) == True

# Avoid - Tests depend on execution order
counter = 0
def test_increment():
    global counter
    counter += 1
    assert counter == 1  # Fails if run out of order
```

### 4. Test Data

Use fixtures for reusable test data:

```python
@pytest.fixture
def sample_activity():
    return {
        "id": 12345,
        "name": "Morning Ride",
        "type": "Ride",
        "distance": 25000,
    }

def test_process_activity(sample_activity):
    result = process(sample_activity)
    assert result["distance_km"] == 25.0
```

### 5. Parameterized Tests

Test multiple inputs efficiently:

```python
@pytest.mark.parametrize("input,expected", [
    (100, "100.0m"),
    (1000, "1.0km"),
    (5280, "5.3km"),
])
def test_format_distance(input, expected):
    assert format_distance(input) == expected
```

## Continuous Integration

### GitHub Actions

Tests run automatically on:
- Every push to a PR
- When PR is merged to main

See `.github/workflows/tests.yml` for configuration.

### Local Pre-commit Checks

Before pushing, run:

```bash
# Run all checks
hatch run lint:default  # Linting and type checking
hatch run test:cov      # Tests with coverage

# Or run individually
ruff check .            # Linting
ruff format .           # Formatting
mypy src/strava_fetcher # Type checking
pytest                  # Tests
```

## Troubleshooting

### Tests Pass Locally But Fail in CI

1. Check Python version (CI uses 3.12)
2. Check for missing dependencies
3. Check for environment-specific code
4. Verify test data paths are relative

### Slow Tests

1. Mark slow tests:
   ```python
   @pytest.mark.slow
   def test_long_operation():
       pass
   ```

2. Skip in development:
   ```bash
   pytest -m "not slow"
   ```

3. Run slow tests in CI only

### Flaky Tests

If tests fail intermittently:
1. Check for race conditions
2. Use mocks instead of real APIs
3. Add proper waits for async operations
4. Ensure test isolation

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Python Testing Best Practices](https://realpython.com/pytest-python-testing/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
