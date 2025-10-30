# SharedWorkflows Integration

## Overview

This document tracks the integration of the [SharedWorkflows v1.0.0](https://github.com/hope0hermes/SharedWorkflows/releases/tag/v1.0.0) repository into the StravaFetcher project. The SharedWorkflows repository contains reusable GitHub Actions and workflows for consistent CI/CD across multiple projects.

**Migration Date**: October 30, 2025  
**SharedWorkflows Version**: v1.0.0

## What Changed

### 1. Tests Workflow (`.github/workflows/tests.yml`)

**Before**: Manual Python setup, linting, and testing with inline commands (~60 lines)
**After**: Using `hope0hermes/SharedWorkflows/.github/workflows/reusable-tests.yml@v1.0.0` (~12 lines)

**Benefits**:
- **80% reduction in workflow code** - from ~60 lines to ~12 lines
- Consistent testing setup across all projects
- Automatic coverage artifact upload
- Centralized maintenance - updates to testing logic happen in SharedWorkflows
- Built-in concurrency control and skip logic for version bump commits

**Key Changes**:
- Removed all manual steps (checkout, Python setup, hatch installation, lint/test commands)
- Replaced with single reusable workflow call
- Configurable via simple inputs: `python-version`, `package-name`, `coverage-threshold`, etc.

### 2. Release Workflow (`.github/workflows/release.yml`)

**Before**: Manual version bump logic with complex inline bash scripts (~200 lines)
**After**: Using `hope0hermes/SharedWorkflows/.github/workflows/reusable-release.yml@v1.0.0` (~8 lines)

**Benefits**:
- **96% reduction in workflow code** - from ~200 lines to ~8 lines
- Complete automation of version management
- Modular and maintainable workflow
- Consistent version management strategy across projects
- Better error handling and logging

**Key Changes**:
- Removed all manual steps (Python setup, git config, skip checks, version analysis, hatch commands, changelog updates, PR creation)
- Replaced with single reusable workflow call
- Only requires `package-path` input and `PAT_TOKEN` secret
- All version bump logic centralized in SharedWorkflows

### 3. Create Release Workflow (`.github/workflows/create-release.yml`)

**Before**: Manual release creation with bash/gh CLI commands (~80 lines)
**After**: Using `hope0hermes/SharedWorkflows/.github/workflows/reusable-create-release.yml@v1.0.0` (~3 lines)

**Benefits**:
- **96% reduction in workflow code** - from ~80 lines to ~3 lines
- Simplified release creation
- Consistent release format across projects
- Better error handling
- Centralized maintenance

**Key Changes**:
- Removed all manual steps (checkout, git config, version extraction, release creation)
- Replaced with single reusable workflow call
- No configuration needed - completely self-contained
- Uses `extract-version` and `create-github-release` actions internally

### 4. Commit Lint Workflow (`.github/workflows/commitlint.yml`)

**Before**: Inline bash scripts for validation (~100 lines)
**After**: Using `hope0hermes/SharedWorkflows/.github/workflows/reusable-commitlint.yml@v1.0.0` (~3 lines)

**Benefits**:
- **97% reduction in workflow code** - from ~100 lines to ~3 lines
- Consistent commit message validation across projects
- Centralized updates to validation rules
- No maintenance required in individual projects

**Key Changes**:
- Removed all inline validation scripts
- Replaced with single reusable workflow call
- No configuration needed - completely self-contained

## Actions Used from SharedWorkflows v1.0.0

### Reusable Workflows (Recommended Approach)
All workflows in StravaFetcher now use **reusable workflows** from SharedWorkflows, which is the recommended pattern:

- **`reusable-tests.yml`**: Complete Python CI/CD testing pipeline
  - Inputs: `python-version`, `package-name`, `coverage-threshold`, `run-lint`, `run-tests`, `working-directory`, `pytest-args`
  - Includes: lint job + test job with coverage
  - Built-in: Skip logic for version bumps, concurrency control, artifact upload

- **`reusable-release.yml`**: Automated version bumping and PR creation
  - Inputs: `package-path`
  - Secrets: `PAT_TOKEN`
  - Handles: Skip checks, version analysis, version bumping, CHANGELOG updates, PR creation

- **`reusable-create-release.yml`**: GitHub Release creation
  - No inputs required
  - Handles: Version extraction from commits, release creation with CHANGELOG notes

- **`reusable-commitlint.yml`**: Commit message validation
  - No inputs required
  - Validates: PR titles and commit messages against Conventional Commits format

### Composite Actions (Used Internally by Reusable Workflows)
These actions are used internally by the reusable workflows above. You can also use them individually for custom workflows:

**Python CI/CD Actions:**
- `python-ci` - Complete Python CI pipeline (lint + test)
- `python-lint` - Python linting and formatting checks
- `python-test` - Python tests with coverage

**Version Management Actions:**
- `check-skip-conditions` - Determines if workflow should skip
- `determine-version-bump` - Analyzes commits for version bump type
- `bump-version` - Bumps version using hatch
- `update-changelog` - Updates CHANGELOG.md
- `create-version-pr` - Creates version bump PR
- `extract-version` - Extracts version from commit messages
- `create-github-release` - Creates GitHub Release with tag

## Configuration Details

### Tests Workflow Configuration
```yaml
jobs:
  test:
    uses: hope0hermes/SharedWorkflows/.github/workflows/reusable-tests.yml@v1.0.0
    with:
      python-version: "3.12"
      package-name: "strava-fetcher"
      coverage-threshold: 0
      run-lint: true
      run-tests: true
      working-directory: "."
```

### Release Workflow Configuration
```yaml
jobs:
  release:
    uses: hope0hermes/SharedWorkflows/.github/workflows/reusable-release.yml@v1.0.0
    with:
      package-path: "src/strava_fetcher/__init__.py"
    secrets:
      PAT_TOKEN: ${{ secrets.PAT_TOKEN }}
```

### Create Release Workflow Configuration
```yaml
jobs:
  create-release:
    uses: hope0hermes/SharedWorkflows/.github/workflows/reusable-create-release.yml@v1.0.0
```

### Commit Lint Workflow Configuration
```yaml
jobs:
  commitlint:
    uses: hope0hermes/SharedWorkflows/.github/workflows/reusable-commitlint.yml@v1.0.0
```

## Compatibility Notes

### Requirements
- Python project using hatch for version management
- Version stored in `src/strava_fetcher/__init__.py` as `__version__ = "x.y.z"`
- CHANGELOG.md following Keep a Changelog format
- Conventional Commits for version bump determination

### No Breaking Changes
All workflows maintain the same external behavior:
- Tests still run on PRs and main branch pushes
- Version bumps still triggered by conventional commits
- Releases still created automatically after version bump PR merges
- PAT_TOKEN secret requirement unchanged

## Testing Recommendations

1. **Test the Tests Workflow**
   - Create a feature branch
   - Make a change and open a PR
   - Verify lint and test checks run successfully

2. **Test the Release Workflow**
   - Merge a PR with `feat:` or `fix:` commit
   - Verify version bump PR is created
   - Check that version and CHANGELOG are updated correctly

3. **Test the Create Release Workflow**
   - Merge the version bump PR
   - Verify GitHub Release is created with correct version and notes

## Future Improvements

Potential enhancements for future migrations:
1. Consider creating a reusable workflow for commitlint
2. Add support for coverage thresholds in testing
3. Create shared actions for Python package publishing
4. Add support for release notes generation from commit types

## Rollback Plan

If issues arise, you can revert to the previous workflows:
1. The commit history preserves the old workflow files
2. Use `git checkout <previous-commit> -- .github/workflows/` to restore
3. All workflow logic is preserved in git history

## Support

For issues with SharedWorkflows actions:
- GitHub Repository: https://github.com/hope0hermes/SharedWorkflows
- Issues: https://github.com/hope0hermes/SharedWorkflows/issues
- Documentation: https://github.com/hope0hermes/SharedWorkflows/blob/main/README.md

## References

- SharedWorkflows v1.0.0 Release: https://github.com/hope0hermes/SharedWorkflows/releases/tag/v1.0.0
- SharedWorkflows Documentation: https://github.com/hope0hermes/SharedWorkflows/docs/
- Conventional Commits: https://www.conventionalcommits.org/
