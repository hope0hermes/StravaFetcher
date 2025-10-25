# StravaFetcher 🏃‍♂️💾

A robust and flexible solution for synchronizing your Strava activity data and streams to local storage. Designed for developers and data enthusiasts, it handles the complexities of Strava's OAuth2 authentication, API rate limits, and data persistence, allowing you to focus on analyzing your athletic performance.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why StravaFetcher?

StravaFetcher takes the complexity out of syncing your Strava data locally. Whether you're building custom analytics, training dashboards, or backing up your activities, StravaFetcher provides:

- **Effortless OAuth2 Management**: Complete authentication flow with automatic token refresh
- **Intelligent Caching**: Incremental updates that only fetch new data
- **Robust Rate Limiting**: Automatic handling of Strava's API limits with smart retries
- **Flexible Configuration**: Environment variables, YAML files, or CLI arguments
- **Clean Data Storage**: Organized CSV files ready for analysis with pandas or other tools

---

## Features

* **Effortless Strava OAuth2 Management:** Handles the entire authorization flow,
token storage, and automatic token refreshing.
* **Flexible Configuration Handling:** Supports a robust configuration hierarchy: command-line arguments take precedence, followed by a YAML configuration file, and finally environment variables for sensitive credentials.
* **Comprehensive Activity Synchronization:** Pulls your entire Strava activity
history, including summaries, and efficiently updates a local cache to keep your
data current.
* **Detailed Stream Data Fetching:** Downloads time-series data (streams) for each
activity, offering metrics like heart rate, power, speed, cadence, and GPS coordinates.
* **Intelligent Caching:** Skips already downloaded activities and streams, ensuring
efficient updates and minimizing API calls.
* **API Rate Limit Handling:** Automatically pauses and retries requests when Strava's
API rate limits are encountered, ensuring smooth data acquisition for large datasets.
* **Configurable and Extensible:** Built with `Pydantic` for clear data structures and validation,
allowing easy customization of paths, retry intervals, and logging behavior.
* **Modular Design:** Clean separation of concerns with dedicated classes for
credentials, token management, activity fetching, stream fetching, and an overarching
synchronization pipeline.

---

## Installation

### Prerequisites

* Python 3.8+
* A Strava API application:
    1.  Go to [Strava API Applications](https://www.strava.com/settings/api).
    2.  Click "Create Your App".
    3.  Fill in the details. Set the **Authorization Callback Domain** to `localhost`.
    4.  Note down your `Client ID` and `Client Secret`.

### Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```
    (Replace `your-username/your-repo-name` with your actual repository details.)

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the package:**

    Install in editable mode with development dependencies:
    ```bash
    pip install -e ".[dev]"
    ```

    Or for basic usage only:
    ```bash
    pip install -e .
    ```

---

## Configuration

The `strava_fetcher` package uses a flexible configuration system managed by the `load_settings` function, which consolidates settings from multiple sources with a clear precedence.

### Configuration Precedence

Settings, particularly your Strava API `Client ID` and `Client Secret`, are loaded in the following order of preference (highest to lowest):

1.  **Command-Line Arguments:**
    Values provided directly to the CLI command (e.g., `--client-id`, `--client-secret`) take the highest precedence. This is ideal for one-off overrides or testing.

    ```bash
    python -m strava_fetcher sync --config-file path/to/config.yaml --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
    ```

2.  **YAML Configuration File:**
    A YAML file (e.g., `config.yaml`) can define most application settings. If a `config-file` is specified, settings within it will override environment variables.

    Example `config.yaml`:
    ```yaml
    strava_api:
      # client_id and client_secret can be defined here to override environment variables
      # client_id: your_client_id_from_yaml
      # client_secret: your_client_secret_from_yaml
    paths:
      data_dir: /path/to/your/data
      token_file: /path/to/your/data/token.json
      activities_cache_file: /path/to/your/data/activities.csv
      streams_dir: /path/to/your/data/Streams
    sync:
      max_pages: 100
      retry_interval_seconds: 900
      skip_trainer_activities: false
    ```
    To use a configuration file:
    ```bash
    python -m strava_fetcher sync --config-file path/to/config.yaml
    ```

3.  **Environment Variables:**
    For sensitive credentials like `Client ID` and `Client Secret`, environment variables (`STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`) are the recommended method for production and deployment. These are used if not overridden by command-line arguments or the YAML file.

    ```bash
    export STRAVA_CLIENT_ID="your_client_id_here"
    export STRAVA_CLIENT_SECRET="your_client_secret_here"
    # Then run your application without specifying them on the command line or in YAML
    python -m strava_fetcher sync
    ```

### Default Paths

If not specified in the configuration file, default paths for data storage are:
*   `data_dir`: `~/.strava_fetcher/data`
*   `token_file`: `~/.strava_fetcher/data/token.json`
*   `activities_cache_file`: `~/.strava_fetcher/data/activities.csv`
*   `streams_dir`: `~/.strava_fetcher/data/Streams`

---

## Usage

The core functionality is encapsulated in the `StravaSyncPipeline` class, which
orchestrates the entire data synchronization process.

### 1. Initial Authorization

The first time you run the pipeline, it will prompt you to authorize your application
with Strava through your web browser. Follow the instructions in the console to
complete this step. The package will then automatically store the necessary tokens
for future use.

### 2. Running the Synchronization Pipeline

The primary way to interact with the package is via its command-line interface.

### Running the Synchronization Pipeline via CLI

To run the full data synchronization pipeline, use the `strava-fetcher sync` command. You can configure it using command-line arguments, a YAML file, or environment variables as described in the [Configuration](#configuration) section.

```bash
# Basic usage: Loads settings from environment variables or default values
python -m strava_fetcher sync

# Using a configuration file
python -m strava_fetcher sync --config-file path/to/your/config.yaml

# Overriding credentials via command-line arguments
python -m strava_fetcher sync --client-id YOUR_ID --client-secret YOUR_SECRET
```

### Running the Synchronization Pipeline via Python Script

For more advanced programmatic control, you can instantiate `StravaSyncPipeline` directly.

```python
# main_sync_script.py
import logging
from pathlib import Path
from strava_sync_pipeline import StravaSyncPipeline

# Configure basic logging for console output
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    logging.info("Starting Strava Data Sync Pipeline.")

    # Basic usage: Uses credentials from env vars or Data/credentials.yml
    # and defaults for all paths and intervals.
    pipeline = StravaSyncPipeline()
    pipeline.sync_all_data()

    # --- OR ---

    # --- OR ---

    # Advanced usage: Load settings with a custom config file or overrides
    # from strava_fetcher.settings import load_settings
    #
    # # Example: Load from a specific config file, potentially overriding client_id via CLI
    # custom_settings = load_settings(
    #     config_file="./my_custom_config.yaml",
    #     # client_id="override_client_id_here", # Optional: override via direct argument
    #     # client_secret="override_client_secret_here", # Optional: override via direct argument
    # )
    # custom_pipeline = StravaSyncPipeline(settings=custom_settings)
    # custom_pipeline.sync_all_data()

    logging.info("Strava Data Sync Pipeline completed.")
```

---

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

| Document | Description |
|----------|-------------|
| [`VERSION_MANAGEMENT.md`](docs/VERSION_MANAGEMENT.md) | Automated versioning with Conventional Commits |
| [`ARCHITECTURE_GUIDE.md`](docs/ARCHITECTURE_GUIDE.md) | System architecture and component details |
| [`TESTING_STRATEGY.md`](docs/TESTING_STRATEGY.md) | Testing approach and best practices |

See also [`examples/`](examples/) for sample configurations and usage patterns.

---

## 🧪 Testing

StravaFetcher uses pytest for testing with comprehensive coverage.

### Run All Tests

```bash
# Using hatch (recommended)
hatch run test:default

# Run with coverage
hatch run test:cov

# Using pytest directly
pytest
```

### Run Specific Tests

```bash
# Run single test file
pytest tests/unit/test_settings.py

# Run specific test
pytest tests/unit/test_settings.py::test_load_from_env_vars

# Run with verbose output
pytest -v
```

### Test Coverage

Check current test coverage:
```bash
hatch run test:cov
```

View HTML coverage report:
```bash
pytest --cov=src/strava_fetcher --cov-report=html
open htmlcov/index.html
```

See [`docs/TESTING_STRATEGY.md`](docs/TESTING_STRATEGY.md) for more details.

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `pytest`
5. **Run linting**: `ruff check .`
6. **Commit your changes**: `git commit -m 'feat: add amazing feature'`
7. **Push to the branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Commit Message Format

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning:

```bash
# New feature (minor version bump)
git commit -m "feat: add batch stream fetching"

# Bug fix (patch version bump)
git commit -m "fix: correct rate limit handling"

# Breaking change (major version bump)
git commit -m "feat!: redesign Settings API"

# Other changes (no version bump)
git commit -m "docs: update README"
git commit -m "chore: update dependencies"
```

See [`docs/VERSION_MANAGEMENT.md`](docs/VERSION_MANAGEMENT.md) for details.

### Code Quality

This project uses:
- **Ruff** for linting and formatting
- **MyPy** for type checking
- **Pylint** for code quality analysis
- **Pytest** for testing

Run quality checks:
```bash
# Format code
ruff format .

# Check for issues
ruff check .

# Type checking
mypy src/strava_fetcher

# Lint with pylint
pylint src/strava_fetcher

# Run all checks (as in CI)
hatch run lint:default
```

---

## 🔄 Version Management

This project uses automated semantic versioning based on commit messages. When a PR is merged to `main`:

1. Commit messages are analyzed
2. Version is bumped automatically (major/minor/patch)
3. `CHANGELOG.md` is updated
4. Git tag is created
5. GitHub Release is published

**Current Version:** Check with `hatch version` or see [`CHANGELOG.md`](CHANGELOG.md)

See [`docs/VERSION_MANAGEMENT.md`](docs/VERSION_MANAGEMENT.md) for complete details.

---

## 🛣️ Roadmap

### Planned Features

- [ ] **Parallel Downloads**: Concurrent stream fetching for faster sync
- [ ] **Webhook Support**: Real-time updates via Strava webhooks
- [ ] **Export Formats**: JSON, Parquet, and SQLite support
- [ ] **Activity Filtering**: Advanced filtering by type, date, or other criteria
- [ ] **Data Validation**: Integrity checks for downloaded data
- [ ] **Progress Tracking**: Enhanced progress bars and ETA calculations

### Recently Added

- ✅ Automated versioning with Conventional Commits
- ✅ Comprehensive GitHub Actions CI/CD
- ✅ Full test infrastructure with pytest
- ✅ Detailed documentation and examples
- ✅ Dynamic version management with hatch

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

**Technologies:**
- [Strava API](https://developers.strava.com/) for providing comprehensive athlete data
- [Pydantic](https://docs.pydantic.dev/) for robust configuration management
- [Click](https://click.palletsprojects.com/) for elegant CLI interface
- [Pandas](https://pandas.pydata.org/) for efficient data handling

**Inspiration:**
- The need for local, analyzable Strava data
- Open-source data analysis tools
- The Python data science ecosystem

---

## 📧 Contact

- **Author**: Israel Barragan
- **Email**: abraham0vidal@gmail.com
- **GitHub**: [@hope0hermes](https://github.com/hope0hermes)
- **Issues**: [GitHub Issues](https://github.com/hope0hermes/StravaFetcher/issues)

---

**Happy Syncing! 🚴‍♂️📊**

