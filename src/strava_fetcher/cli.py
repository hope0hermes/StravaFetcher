"""
Command-line interface for the Strava Fetcher package.

This module provides a CLI for running the Strava data synchronization pipeline,
allowing users to configure it via command-line arguments, environment variables,
or a configuration file.
"""

import logging

import click

from .exceptions import StravaFetcherError
from .pipeline import StravaSyncPipeline
from .settings import load_settings

# --- Basic Logger Setup ---
# A more sophisticated logging configuration can be added here later
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


@click.group()
def main():
    """Fetch and synchronize data from the Strava API."""


@main.command()
@click.option(
    "--config-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to a YAML configuration file.",
)
@click.option(
    "--client-id",
    help="Your Strava application's Client ID.",
)
@click.option(
    "--client-secret",
    help="Your Strava application's Client Secret.",
)
def sync(config_file: str | None, client_id: str | None, client_secret: str | None):
    """
    Run the full data synchronization pipeline.

    This command will:
    1. Fetch and cache all new activity summaries.
    2. Fetch and save detailed streams for all activities that don't have them.
    """
    click.echo("Starting the Strava data synchronization pipeline...")

    try:
        # 1. Load settings from all available sources
        settings = load_settings(config_file, client_id, client_secret)
        click.echo(f"Data will be stored in: {settings.paths.data_dir}")

        # 2. Initialize and run the pipeline
        pipeline = StravaSyncPipeline(settings)
        pipeline.run()

        click.secho("Synchronization completed successfully!", fg="green")

    except FileNotFoundError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
    except StravaFetcherError as e:
        click.secho(f"A pipeline error occurred: {e}", fg="red", err=True)
    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg="red", err=True)


if __name__ == "__main__":
    main()
