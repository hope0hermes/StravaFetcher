# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-10-25

### Changed
- fix: trigger checks after pr creation (#21) (4f8017c)
- fix: trigger checks after creating version bump PR (#18) (7850782)
- fix: trigger checks on version bump PRs (#16) (595fb1b)
- fix: update Python version badge to 3.12+ (#13) (1f61918)
- fix: use PAT_TOKEN with fallback in checkout step (#11) (9a86a4b)
- fix: skip release workflow for version bump commits (#10) (871fc62)
- fix: use PAT_TOKEN for creating PRs in release workflow (#9) (3cc8183)
- fix: add automated GitHub Release creation workflow (#8) (dcac032)
- fix: create version bump PR instead of direct push to main (#7) (3de0211)
- fix: resolve YAML syntax errors in release workflow (#6) (2a585b8)
- fix: correct sed command escaping in release workflow YAML (#5) (d080c53)
- fix: update release workflow regex to handle GitHub PR merge format (#4) (1c0d5eb)
- feat!: implement professional development infrastructure and GitHub integration (#3) (88ee5af)


### Added

#### GitHub Integration & CI/CD
- Automated semantic versioning based on Conventional Commits
- GitHub Actions workflow for automated releases
- GitHub Actions workflow for continuous integration testing
- Commit message linting to enforce Conventional Commits format
- Automatic CHANGELOG updates on release

#### Documentation
- Comprehensive VERSION_MANAGEMENT.md guide
- Detailed TESTING_STRATEGY.md documentation
- Complete ARCHITECTURE_GUIDE.md with system design
- Enhanced README with badges, contributing guidelines, and roadmap
- Examples directory with configuration templates and guides

#### Testing Infrastructure
- Comprehensive test fixtures in conftest.py
- Organized test structure (unit/, integration/, fixtures/)
- pytest configuration with coverage reporting
- Test markers for better organization (unit, integration, slow)

#### Development Tools
- pytest-cov for test coverage reporting
- pylint for code quality analysis
- pydocstyle for docstring linting
- Enhanced ruff configuration with docstring formatting
- Comprehensive pyproject.toml with all tool configurations

#### Configuration Management
- Dynamic version management with hatch
- Enhanced .gitignore for better coverage
- Example configuration files with detailed comments

## [0.1.0-beta] - 2024-10-XX

### Added

#### Core Features
- Complete Strava OAuth2 authentication flow with automatic token management
- Robust activity synchronization with local caching
- Stream data fetching for detailed time-series metrics
- Intelligent rate limit handling with automatic retry
- Flexible configuration system supporting environment variables, YAML files, and CLI arguments

#### Configuration & Settings
- Pydantic-based settings with type validation
- YAML configuration file support
- Environment variable overrides with `STRAVA_` prefix
- Configurable paths for data storage, tokens, and cache files
- Support for custom retry intervals and pagination limits

#### CLI Interface
- `strava-fetcher sync`: Execute full data synchronization pipeline
- Command-line argument support for all configuration options
- Rich logging and error handling

#### Data Management
- Local CSV cache for activities
- Organized stream data storage by activity ID
- Efficient incremental updates (skip already downloaded data)
- Automatic cache validation and updates

#### Error Handling
- Custom exception hierarchy for clear error types
- Graceful handling of API errors
- Comprehensive logging throughout the pipeline
- Retry logic for transient failures

#### Development Tools
- Hatch-based project management
- Ruff for fast linting and formatting
- MyPy for static type checking
- Pytest for testing
- Support for Python 3.10, 3.11, and 3.12

### Technical Details

**Core Dependencies:**
- requests >=2.31.0 for HTTP requests to Strava API
- pandas >=2.0.0 for data manipulation
- pydantic ~2.11.7 & pydantic-settings ~2.10.1 for configuration
- click >=8.0.0 for CLI interface
- PyYAML >=6.0.1 for configuration files

**Package Structure:**
```
src/strava_fetcher/
├── cli.py           # Command-line interface
├── client.py        # Strava API client
├── exceptions.py    # Custom exceptions
├── models.py        # Pydantic data models
├── persistence.py   # Data storage and caching
├── pipeline.py      # Synchronization pipeline
└── settings.py      # Configuration management
```

[0.1.0-beta]: https://github.com/hope0hermes/StravaFetcher/releases/tag/v0.1.0-beta
