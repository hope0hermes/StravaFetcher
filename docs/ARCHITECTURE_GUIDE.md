# StravaFetcher Architecture Guide

## Overview

StravaFetcher is designed with a modular architecture that separates concerns and makes the codebase maintainable and extensible.

## Architecture Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Dependency Injection**: Components receive dependencies rather than creating them
3. **Configuration Management**: Centralized, type-safe configuration using Pydantic
4. **Error Handling**: Explicit exception hierarchy for different error types
5. **Testability**: Components can be tested in isolation with mocks

## System Architecture

```
┌─────────────────────────────────────┐
│        CLI (Entry Point)            │
│   Command-line interface & args     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     StravaSyncPipeline              │
│   Orchestrates the sync workflow    │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼──────┐  ┌────▼─────────┐
│ StravaClient│  │ Persistence  │
│  API calls  │  │ Data storage │
└─────────────┘  └──────────────┘
       │
┌──────▼──────────────────────────────┐
│          Settings                   │
│   Configuration management          │
└─────────────────────────────────────┘
```

## Component Details

### 1. CLI (`cli.py`)

**Purpose**: Command-line interface and entry point

**Responsibilities**:
- Parse command-line arguments
- Load configuration from multiple sources
- Initialize and run the pipeline
- Handle top-level errors

**Key Functions**:
```python
@click.command()
@click.option('--config-file', help='Path to YAML config file')
@click.option('--client-id', help='Strava API client ID')
def sync(config_file, client_id, ...):
    """Synchronize Strava data to local storage."""
    settings = load_settings(
        config_file=config_file,
        client_id=client_id,
        ...
    )
    pipeline = StravaSyncPipeline(settings)
    pipeline.sync_all_data()
```

**Usage**:
```bash
strava-fetcher sync --config-file config.yaml
```

### 2. Settings (`settings.py`)

**Purpose**: Type-safe configuration management

**Responsibilities**:
- Load configuration from environment variables
- Load configuration from YAML files
- Merge configuration with precedence rules
- Validate configuration values
- Provide default values

**Key Classes**:
```python
class StravaAPIConfig(BaseModel):
    """Strava API credentials."""
    client_id: SecretStr | None = None
    client_secret: SecretStr | None = None

class PathsConfig(BaseModel):
    """File system paths."""
    data_dir: Path = Path.home() / ".strava_fetcher" / "data"
    token_file: Path = ...
    activities_cache_file: Path = ...
    streams_dir: Path = ...

class SyncConfig(BaseModel):
    """Synchronization settings."""
    max_pages: int = 100
    retry_interval_seconds: int = 900
    skip_trainer_activities: bool = False

class Settings(BaseSettings):
    """Complete application settings."""
    strava_api: StravaAPIConfig
    paths: PathsConfig
    sync: SyncConfig
```

**Configuration Precedence** (highest to lowest):
1. Command-line arguments
2. YAML configuration file
3. Environment variables
4. Default values

### 3. StravaClient (`client.py`)

**Purpose**: Interface to Strava API

**Responsibilities**:
- OAuth2 authentication flow
- Token storage and refresh
- API request execution
- Rate limit handling
- Error handling and retries

**Key Methods**:
```python
class StravaClient:
    def __init__(self, settings: Settings):
        """Initialize client with settings."""

    def authorize(self) -> None:
        """Perform OAuth2 authorization flow."""

    def refresh_token(self) -> None:
        """Refresh access token if expired."""

    def get_activities(self, page: int = 1) -> list[dict]:
        """Fetch paginated activities."""

    def get_activity_streams(self, activity_id: int) -> dict:
        """Fetch time-series data for activity."""
```

**Error Handling**:
- Raises `UnauthorizedError` for 401 responses
- Raises `RateLimitError` for 429 responses
- Raises `APIError` for other API errors

### 4. Persistence (`persistence.py`)

**Purpose**: Local data storage and caching

**Responsibilities**:
- Save/load activities to/from CSV
- Save/load streams to/from individual CSV files
- Maintain activity cache state
- Organize file system structure

**Key Functions**:
```python
def save_activities_to_csv(
    activities: list[dict],
    filepath: Path
) -> None:
    """Save activities to CSV cache."""

def load_activities_from_csv(
    filepath: Path
) -> pd.DataFrame:
    """Load activities from CSV cache."""

def save_stream_to_csv(
    activity_id: int,
    stream_data: dict,
    streams_dir: Path
) -> None:
    """Save stream data for single activity."""

def get_cached_activity_ids(
    cache_file: Path
) -> set[int]:
    """Get set of activity IDs already cached."""
```

**File Organization**:
```
~/.strava_fetcher/data/
├── token.json              # OAuth tokens
├── activities.csv          # Activity cache
└── Streams/
    ├── stream_12345.csv   # Stream for activity 12345
    ├── stream_67890.csv
    └── ...
```

### 5. Pipeline (`pipeline.py`)

**Purpose**: Orchestrate the complete sync workflow

**Responsibilities**:
- Coordinate between client and persistence
- Implement sync logic (incremental updates)
- Handle pagination
- Log progress
- Error recovery

**Key Methods**:
```python
class StravaSyncPipeline:
    def __init__(self, settings: Settings):
        """Initialize with settings and dependencies."""
        self.settings = settings
        self.client = StravaClient(settings)

    def sync_all_data(self) -> None:
        """Execute complete synchronization."""
        self.sync_activities()
        self.sync_streams()

    def sync_activities(self) -> None:
        """Sync activity metadata."""
        # Get cached activity IDs
        cached_ids = get_cached_activity_ids(...)

        # Fetch new activities
        for page in range(1, max_pages):
            activities = self.client.get_activities(page)
            new_activities = [
                a for a in activities
                if a['id'] not in cached_ids
            ]
            save_activities_to_csv(new_activities, ...)

    def sync_streams(self) -> None:
        """Sync stream data for activities."""
        activities = load_activities_from_csv(...)
        for activity in activities:
            if not stream_exists(activity['id']):
                stream = self.client.get_activity_streams(
                    activity['id']
                )
                save_stream_to_csv(activity['id'], stream, ...)
```

### 6. Models (`models.py`)

**Purpose**: Data models and type definitions

**Responsibilities**:
- Define data structures
- Validate data formats
- Provide type hints

**Key Models**:
```python
class Activity(BaseModel):
    """Strava activity metadata."""
    id: int
    name: str
    type: str
    distance: float
    moving_time: int
    total_elevation_gain: float
    start_date: datetime

class TokenData(BaseModel):
    """OAuth token data."""
    access_token: str
    refresh_token: str
    expires_at: int

class StreamData(BaseModel):
    """Activity stream data."""
    time: list[int]
    distance: list[float] | None = None
    altitude: list[float] | None = None
    watts: list[int] | None = None
    heartrate: list[int] | None = None
```

### 7. Exceptions (`exceptions.py`)

**Purpose**: Custom exception hierarchy

**Exception Tree**:
```
StravaFetcherError (base)
├── ConfigError
├── APIError
│   ├── RateLimitError (429)
│   └── UnauthorizedError (401)
└── PersistenceError
```

**Usage**:
```python
from strava_fetcher.exceptions import RateLimitError

try:
    activities = client.get_activities()
except RateLimitError as e:
    logger.warning(f"Rate limited. Retry in {e.retry_after}s")
    time.sleep(e.retry_after)
```

## Data Flow

### Sync Activities Flow

```
1. CLI parses arguments
   ↓
2. Settings loads configuration
   ↓
3. Pipeline initializes
   ↓
4. Client authorizes with Strava
   ↓
5. Pipeline checks for cached activities
   ↓
6. For each page:
   - Client fetches activities
   - Filter out cached activities
   - Persistence saves to CSV
   ↓
7. Done
```

### Sync Streams Flow

```
1. Pipeline loads activities from cache
   ↓
2. For each activity:
   - Check if stream already exists
   - If not:
     - Client fetches stream data
     - Persistence saves to CSV
   - Handle rate limits (wait and retry)
   ↓
3. Done
```

## Extension Points

### Adding New Configuration Options

1. Add to appropriate config class in `settings.py`:
```python
class SyncConfig(BaseModel):
    new_option: bool = True
```

2. Use in pipeline or client:
```python
if self.settings.sync.new_option:
    # New behavior
```

### Adding New API Endpoints

1. Add method to `StravaClient`:
```python
def get_athlete_stats(self, athlete_id: int) -> dict:
    """Fetch athlete statistics."""
    return self._request("GET", f"/athletes/{athlete_id}/stats")
```

2. Use in pipeline:
```python
stats = self.client.get_athlete_stats(athlete_id)
```

### Adding New Storage Formats

1. Add functions to `persistence.py`:
```python
def save_activities_to_parquet(
    activities: pd.DataFrame,
    filepath: Path
) -> None:
    """Save activities in Parquet format."""
    activities.to_parquet(filepath)
```

2. Use in pipeline with configuration:
```python
if self.settings.storage.format == "parquet":
    save_activities_to_parquet(...)
```

## Best Practices

### 1. Dependency Injection

Always pass dependencies rather than creating them:

```python
# Good
class Pipeline:
    def __init__(self, settings: Settings, client: StravaClient):
        self.settings = settings
        self.client = client

# Avoid
class Pipeline:
    def __init__(self):
        self.settings = Settings()  # Hard to test
        self.client = StravaClient(self.settings)
```

### 2. Error Handling

Use specific exceptions and handle them appropriately:

```python
try:
    activities = client.get_activities()
except RateLimitError:
    logger.warning("Rate limited, waiting...")
    time.sleep(retry_interval)
except UnauthorizedError:
    logger.error("Token expired, re-authorize")
    client.authorize()
except APIError as e:
    logger.error(f"API error: {e}")
    raise
```

### 3. Logging

Use appropriate log levels:

```python
logger.debug("Fetching page 5")      # Detailed debugging
logger.info("Synced 100 activities") # Normal operation
logger.warning("Rate limited")       # Recoverable issues
logger.error("Failed to save")       # Errors
logger.critical("No credentials")    # Fatal errors
```

### 4. Type Hints

Always use type hints for better IDE support and catching errors:

```python
def process_activity(
    activity: dict,
    settings: Settings
) -> pd.DataFrame:
    """Process activity with type safety."""
    pass
```

## Testing Strategy

### Unit Tests

Test components in isolation:

```python
def test_client_handles_rate_limit(mock_settings):
    client = StravaClient(mock_settings)
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 429
        with pytest.raises(RateLimitError):
            client.get_activities()
```

### Integration Tests

Test component interactions:

```python
def test_pipeline_sync_workflow(tmp_path, mock_settings):
    mock_settings.paths.data_dir = tmp_path
    pipeline = StravaSyncPipeline(mock_settings)
    pipeline.sync_all_data()

    # Verify files created
    assert (tmp_path / "activities.csv").exists()
```

### Mocking External APIs

Always mock Strava API in tests:

```python
@patch('strava_fetcher.client.requests.get')
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = [{"id": 123}]
    client = StravaClient(settings)
    activities = client.get_activities()
    assert len(activities) == 1
```

## Troubleshooting

### Common Issues

**Token Expired**:
- Client automatically refreshes tokens
- If refresh fails, re-run with `--authorize`

**Rate Limit Exceeded**:
- Pipeline automatically waits and retries
- Adjust `retry_interval_seconds` in config

**Missing Data**:
- Check Strava privacy settings
- Some activities may not have streams

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or via environment:
```bash
export STRAVA_LOG_LEVEL=DEBUG
strava-fetcher sync
```

## Future Enhancements

Potential areas for improvement:

1. **Parallel Downloads**: Fetch multiple streams concurrently
2. **Incremental Sync**: Only fetch new data since last sync
3. **Data Validation**: Verify data integrity after download
4. **Webhook Support**: Real-time updates via Strava webhooks
5. **Export Formats**: Support JSON, Parquet, SQLite
6. **Activity Filtering**: Skip certain activity types
7. **Retry Strategies**: Exponential backoff for transient errors

## Resources

- [Strava API Documentation](https://developers.strava.com/docs/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Click Documentation](https://click.palletsprojects.com/)
