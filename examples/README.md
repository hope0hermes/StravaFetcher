# StravaFetcher Examples

This directory contains example files to help you get started with StravaFetcher.

## Files

### `config_example.yaml`

Example configuration file showing all available settings:

- **Strava API**: Client credentials for API access
- **Data paths**: Where to store your Strava data locally
- **Sync settings**: Pagination, retry intervals, activity filtering

**Usage:**

1. Copy this file to your project root: `cp examples/config_example.yaml config.yaml`
2. Edit `config.yaml` with your Strava API credentials
3. Optionally customize paths and sync settings
4. Run StravaFetcher with your configuration:
   ```bash
   strava-fetcher sync --config-file config.yaml
   ```

**Getting Strava API Credentials:**

1. Go to [Strava API Applications](https://www.strava.com/settings/api)
2. Click "Create Your App"
3. Fill in the required details:
   - Application Name: Your app name
   - Website: Your website or GitHub repo
   - Authorization Callback Domain: `localhost`
4. Note your **Client ID** and **Client Secret**
5. Add them to your `config.yaml` or set as environment variables

## Configuration Options

### Strava API

```yaml
strava_api:
  client_id: "your_client_id_here"
  client_secret: "your_client_secret_here"
```

These credentials are required to authenticate with Strava's API. You can also set them as environment variables:
- `STRAVA_CLIENT_ID`
- `STRAVA_CLIENT_SECRET`

### Paths

```yaml
paths:
  data_dir: "~/.strava_fetcher/data"
  token_file: "~/.strava_fetcher/data/token.json"
  activities_cache_file: "~/.strava_fetcher/data/activities.csv"
  streams_dir: "~/.strava_fetcher/data/Streams"
```

Customize where your Strava data is stored. Default paths are shown above.

### Sync Settings

```yaml
sync:
  max_pages: 100                    # Maximum pages of activities to fetch
  retry_interval_seconds: 900       # Wait time when rate limited (15 min)
  skip_trainer_activities: false    # Filter out virtual/trainer rides
```

- `max_pages`: Limits how many pages of activities to fetch (200 activities per page)
- `retry_interval_seconds`: How long to wait when hitting Strava's rate limits
- `skip_trainer_activities`: Set to `true` to exclude indoor trainer activities

## Environment Variables

You can also configure StravaFetcher using environment variables with the `STRAVA_` prefix:

```bash
# API credentials
export STRAVA_CLIENT_ID="your_client_id"
export STRAVA_CLIENT_SECRET="your_client_secret"

# Paths
export STRAVA_DATA_DIR="/custom/path/to/data"
export STRAVA_STREAMS_DIR="/custom/path/to/streams"

# Sync settings
export STRAVA_MAX_PAGES="50"
export STRAVA_RETRY_INTERVAL_SECONDS="600"
export STRAVA_SKIP_TRAINER_ACTIVITIES="true"
```

## Usage Examples

### Basic Sync

```bash
# Using environment variables
strava-fetcher sync

# Using config file
strava-fetcher sync --config-file config.yaml
```

### Custom Paths

```bash
# Override specific settings
strava-fetcher sync \
  --config-file config.yaml \
  --data-dir ./my_strava_data
```

### Complete Override

```bash
# Override everything via CLI
strava-fetcher sync \
  --client-id YOUR_ID \
  --client-secret YOUR_SECRET \
  --data-dir ./data \
  --max-pages 50
```

## Configuration Precedence

Settings are loaded in this order (highest to lowest priority):

1. **Command-line arguments**: Direct CLI flags
2. **YAML configuration file**: Settings in your config file
3. **Environment variables**: `STRAVA_*` environment variables
4. **Default values**: Built-in defaults

## Tips

- **Keep credentials secure**: Never commit your `config.yaml` with real credentials to version control
- **Use environment variables in CI/CD**: Set `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` as secrets
- **Start with defaults**: The default settings work well for most users
- **Adjust retry interval**: Strava's rate limits are 100 requests per 15 minutes and 1000 per day
- **Monitor your usage**: Check the logs to see how many API calls you're making

## Troubleshooting

**"No client_id or client_secret found"**
- Make sure you've set your Strava API credentials either in the config file or as environment variables

**"Rate limit exceeded"**
- StravaFetcher will automatically wait and retry
- You can adjust `retry_interval_seconds` if needed

**"Unauthorized"**
- Your access token may have expired
- Delete `token.json` and re-authorize

**Activities not syncing**
- Check your Strava privacy settings
- Some activities may be private or hidden

## Additional Resources

- [Strava API Documentation](https://developers.strava.com/docs/)
- [StravaFetcher Documentation](../docs/)
- [GitHub Issues](https://github.com/hope0hermes/StravaFetcher/issues)
