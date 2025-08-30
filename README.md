# Strava Data Sync & Analysis Package

This package provides a robust and flexible solution for synchronizing your Strava
activity data and streams to local storage. Designed for developers and data enthusiasts,
it handles the complexities of Strava's OAuth2 authentication, API rate limits,
and data persistence, allowing you to focus on analyzing your athletic performance.

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
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    Install the package in editable mode with development dependencies:
    ```bash
    python -m pip install -e .[dev]
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
