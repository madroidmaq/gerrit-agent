# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gerrit Agent Skill is an AI-powered code review platform that integrates cutting-edge Code Agents with Gerrit Code Review. It provides both a command-line tool (inspired by GitHub CLI) and Claude Agent Skills for automated code analysis. Built using Python and Click framework.

## Development Commands

### Environment Setup
```bash
# Install dependencies using uv (recommended)
uv sync

# Install with dev dependencies
uv sync --extra dev
```

### Running the CLI
```bash
# Run using uv
uv run gerrit --help

# Or install locally with pip
pip install -e .
gerrit --help
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/gerrit_cli --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_client.py

# Run specific test function
uv run pytest tests/test_client.py::test_function_name
```

### Code Quality
```bash
# Format code (line length: 100)
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

## Architecture

### CLI Structure
The CLI uses Click's command group pattern with context passing:
- `cli.py`: Main entry point that loads `GerritConfig` from environment and stores it in `ctx.obj["config"]`
- Command groups are registered via `main.add_command()` at the bottom of `cli.py`
- All commands receive config via Click context: `ctx.obj["config"]`

### Configuration Management
- Environment-based configuration using `python-dotenv`
- Config loaded once at CLI startup in `cli.py:main()`
- Priority: `GERRIT_TOKEN` > `GERRIT_PASSWORD` for authentication
- Config validation happens in `GerritConfig.validate()` method

### API Client Pattern
The `GerritClient` class:
- Uses httpx with Basic Auth for HTTP requests
- Implements context manager protocol (`__enter__`/`__exit__`) for proper connection cleanup
- Always use client as context manager: `with GerritClient(...) as client:`
- All API endpoints auto-prepend `/a/` prefix for authenticated requests
- Response parsing strips Gerrit's `)]}'\n` XSSI protection prefix before JSON parsing

### Formatter System
Abstract base class pattern for output formatters:
- `Formatter` base class in `formatters/base.py` defines interface
- Concrete implementations: `TableFormatter` (using rich) and `JSONFormatter`
- Factory function `get_formatter(format_type)` returns appropriate formatter
- Commands use: `formatter = get_formatter(output_format); output = formatter.format_changes(changes)`

### Git Operations
Helper functions in `utils/helpers.py` wrap git commands:
- All git commands use `run_git_command()` wrapper that returns `(success: bool, output: str)`
- Pattern for error handling: `success, msg = some_git_operation(); if not success: handle_error(msg)`
- Git operations are defensive with validation checks (e.g., `check_git_repository()` before operations)

### Error Handling
Custom exception hierarchy in `utils/exceptions.py`:
- `GerritCliError`: Base exception class
- `ConfigError`, `ApiError`, `AuthenticationError`, `NotFoundError`: Specific error types
- `ApiError` includes `status_code` attribute for HTTP errors
- Commands catch `GerritCliError` and display user-friendly messages with `sys.exit(1)`

### Data Models
Pydantic models in `client/models.py` for type-safe API responses:
- All Gerrit API responses are validated through Pydantic models
- Use `model_validate()` to parse API responses: `Change.model_validate(api_data)`
- Models use snake_case field names with `Field(alias="...")` for Gerrit's JSON field names

## Important Implementation Patterns

### Command Structure
Each command follows this pattern:
1. Get config from context: `config = ctx.obj["config"]`
2. Validate arguments
3. Create API client with context manager
4. Call API methods
5. Format and display results
6. Handle errors with try/except for `GerritCliError`

### Gerrit Change Fetch Implementation
The `change fetch` command implements a complex workflow:
1. Validates current directory is a git repository
2. Fetches change info from Gerrit API
3. Verifies remote URL matches change project (heuristic check)
4. Handles uncommitted changes (stash/cancel/force)
5. Computes ref spec: `refs/changes/{last_two:02d}/{change_number}/1`
6. Fetches and creates local review branch

When modifying fetch logic, maintain these safety checks in order.

### Testing with respx
Tests use `respx` library to mock httpx requests for API testing.

## Configuration Notes

- Required env vars: `GERRIT_URL`, `GERRIT_USERNAME`, and `GERRIT_PASSWORD` or `GERRIT_TOKEN`
- Config is loaded in `cli.py` before any command executes
- Help commands (`--help`) skip config loading check
- Always use `.env` file for local development (copy from `.env.example`)

## Tech Stack

- **CLI**: Click 8.1+ (command groups, context passing, options)
- **HTTP**: httpx (async-capable, context manager pattern)
- **Models**: Pydantic 2.0+ (validation, serialization)
- **Output**: Rich (tables, styling, console output)
- **Config**: python-dotenv (environment variable management)
- **Package Manager**: uv (fast Python package installer)
