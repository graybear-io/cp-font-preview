# cp-font-preview: CircuitPython Font Preview Tool
#
# Uses uv to automatically manage Python environment

# Show available commands
default:
    @just --list

# Install/sync dependencies
sync:
    uv sync

# Show help
help:
    @uv run cp-font-preview --help

# Show version
version:
    @uv run cp-font-preview --version

# Show info about a manifest
info MANIFEST:
    uv run cp-font-preview info {{MANIFEST}}

# Preview a font (requires manifest path)
preview MANIFEST:
    uv run cp-font-preview preview --manifest {{MANIFEST}}

# Preview with watch mode
watch MANIFEST:
    uv run cp-font-preview preview --manifest {{MANIFEST}} --watch

# Preview the minimal example
preview-minimal:
    uv run cp-font-preview preview --manifest ../cp-font-gen/examples/minimal/output/digits/digits-manifest.json

# Preview the emoji example
preview-emoji:
    uv run cp-font-preview preview --manifest ../cp-font-gen/examples/emoji/output/emoji/emoji-manifest.json

# Watch the minimal example
watch-minimal:
    uv run cp-font-preview preview --manifest ../cp-font-gen/examples/minimal/output/digits/digits-manifest.json --watch

# Run tests
test:
    uv run python -m pytest

# Run tests with coverage
test-cov:
    uv run python -m pytest --cov=cp_font_preview --cov-report=term-missing

# Run tests in watch mode
test-watch:
    uv run python -m pytest_watch

# Format code with ruff
fmt:
    uv run ruff format .

# Check formatting without changing files
fmt-check:
    uv run ruff format --check .

# Lint code with ruff
lint:
    uv run ruff check .

# Lint and auto-fix issues
lint-fix:
    uv run ruff check --fix .

# Type check with mypy
typecheck:
    uv run mypy src/

# Run all quality checks (lint + typecheck + test)
check-all: lint typecheck test
    @echo "✓ All checks passed!"

# Format, lint, and test - full pre-commit workflow
pre-commit: fmt lint-fix test
    @echo "✓ Code formatted, linted, and tested!"

# Clean Python cache files
clean-cache:
    @echo "Removing Python cache files and directories..."
    find . -type d -name "__pycache__" -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -not -path "./.venv/*" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -not -path "./.venv/*" -delete 2>/dev/null || true
    rm -rf .pytest_cache .ruff_cache .mypy_cache
    rm -rf .coverage htmlcov
    rm -rf dist build src/*.egg-info
    find . -type f -name ".DS_Store" -delete 2>/dev/null || true
    @echo "✓ Cache cleaned"

# Clean everything (cache and venv)
clean: clean-cache
    @echo "Removing virtual environment..."
    rm -rf .venv uv.lock
    @echo "✓ Full clean complete"
