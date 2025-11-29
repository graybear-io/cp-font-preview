# Development Guide

Documentation for developers working on cp-font-preview.

## Architecture

### Package Structure

```text
cp-font-preview/
├── pyproject.toml              # Project config & entry point
├── src/cp_font_preview/        # Main package
│   ├── __init__.py             # Version and exports
│   ├── cli.py                  # Click CLI commands
│   ├── manifest.py             # Manifest loading & parsing
│   ├── preview.py              # Font preview display (pygame)
│   └── watcher.py              # File watching for auto-reload
├── tests/                      # Test suite
├── docs/                       # Documentation
└── justfile                    # Command shortcuts
```

### Module Responsibilities

**cli.py** - Click command definitions

- `preview` - Main preview command with watch mode
- `info` - Display manifest metadata

**manifest.py** - Manifest handling

- `load_manifest()` - Parse JSON manifest
- `get_font_paths()` - Resolve font file paths
- `get_characters()` - Extract character string
- `get_font_info()` - Extract metadata

**preview.py** - Display logic

- `FontPreview` - Main preview class
- pygame window management
- displayio integration
- Character grid rendering

**watcher.py** - File monitoring

- `FontWatcher` - watchdog-based file monitor
- Debounced change detection
- Background thread management

## Technology Stack

- **Click 8.0+** - CLI framework
- **PyYAML 6.0+** - Config parsing
- **Blinka displayio** - CircuitPython compatibility layer
- **pygame** - Display backend via blinka-displayio-pygamedisplay
- **watchdog 3.0+** - File system monitoring
- **pytest 7.0+** - Testing framework
- **uv** - Package management

### External Dependencies

- **SDL2** - System library for pygame
- **Adafruit CircuitPython libraries** - Font rendering

## Setup for Development

### 1. Clone and Install

```bash
git clone https://github.com/graybear-io/cp-font-preview.git
cd cp-font-preview
uv sync  # Creates .venv, installs deps + package in editable mode
```

### 2. Verify Installation

```bash
# Check CLI works
uv run cp-font-preview --version

# Generate a test font
cd ../cp-font-gen/examples/minimal
uv run cp-font-gen generate --config config.yaml

# Preview it
cd ../../cp-font-preview
uv run cp-font-preview preview --manifest ../cp-font-gen/examples/minimal/output/digits/digits-manifest.json
```

### 3. Activate Environment (optional)

```bash
source .venv/bin/activate
cp-font-preview --help
```

Or use `uv run` for everything:

```bash
uv run cp-font-preview --help
uv run pytest
```

## Using the Justfile

The project includes a `justfile` with common development commands. Run `just` to see all available commands:

```bash
just  # Show all commands
```

### Common Just Commands

**Setup & Verification:**

```bash
just install                # Sync dependencies
```

**Testing:**

```bash
just test                   # Run tests
just test-cov               # Run tests with coverage
```

**Code Quality:**

```bash
just fmt                    # Format code with ruff
just fmt-check              # Check formatting (CI-friendly)
just lint                   # Lint code with ruff
just lint-fix               # Lint and auto-fix issues
just typecheck              # Type check with mypy
just check-all              # Run all checks (lint + typecheck + test)
just pre-commit             # Full workflow (format + lint-fix + test)
```

**Preview:**

```bash
just preview MANIFEST       # Preview specific manifest
just watch MANIFEST         # Watch specific manifest
just preview-minimal        # Preview minimal example
just preview-emoji          # Preview emoji example
```

## Code Quality Tools

The project uses modern Python tooling for code quality:

### Ruff - Formatting & Linting

**Ruff** is an extremely fast Python linter and formatter:

- Replaces: black, isort, flake8, pylint, pyupgrade
- Configuration: See `[tool.ruff]` in `pyproject.toml`

**Usage:**

```bash
just fmt                   # Auto-format all code
just fmt-check             # Check if code is formatted (CI)
just lint                  # Check for linting issues
just lint-fix              # Auto-fix linting issues
```

### Mypy - Type Checking

**Mypy** performs static type analysis:

- Configuration: See `[tool.mypy]` in `pyproject.toml`

**Usage:**

```bash
just typecheck             # Run type checking
```

### Pre-commit Hooks (Optional)

**Setup:**

```bash
uv run pre-commit install  # One-time setup
```

**Manual run:**

```bash
just pre-commit            # Run full workflow manually
```

### Recommended Workflow

**During development:**

```bash
# Make changes
just fmt                   # Format code
just lint-fix              # Fix auto-fixable issues
just test                  # Run tests
```

**Before committing:**

```bash
just pre-commit            # Format + lint + test
# or
just check-all             # Lint + typecheck + test (stricter)
```

## Running Tests

### Basic Testing

```bash
# Run all tests
just test

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_manifest.py

# Run specific test
uv run pytest tests/test_manifest.py::test_load_manifest
```

### Coverage

```bash
# Run with coverage
just test-cov

# Generate HTML coverage report
uv run pytest --cov=cp_font_preview --cov-report=html
open htmlcov/index.html
```

## Writing Tests

Tests use pytest and are located in `tests/`.

### Example Test

```python
# tests/test_manifest.py
import pytest
from pathlib import Path
from cp_font_preview.manifest import load_manifest, get_characters

def test_load_manifest(tmp_path):
    """Test loading a valid manifest."""
    manifest_file = tmp_path / "test-manifest.json"
    manifest_file.write_text('''{
        "font_family": "test",
        "characters": "ABC",
        "output_directory": "/tmp",
        "generated_files": ["test.pcf"]
    }''')

    manifest = load_manifest(str(manifest_file))
    assert manifest["font_family"] == "test"
    assert manifest["characters"] == "ABC"

def test_get_characters():
    """Test character extraction."""
    manifest = {"characters": "ABC123"}
    chars = get_characters(manifest)
    assert chars == "ABC123"
```

### Testing pygame Code

For testing preview.py (pygame), use mocks:

```python
from unittest.mock import Mock, patch
import pytest

@patch('cp_font_preview.preview.pygame')
@patch('cp_font_preview.preview.displayio')
def test_font_preview_init(mock_displayio, mock_pygame):
    """Test FontPreview initialization."""
    from cp_font_preview.preview import FontPreview

    preview = FontPreview(
        font_path="test.pcf",
        characters="ABC",
        font_info={"font_family": "test"},
        width=800,
        height=600
    )

    assert preview.width == 800
    assert preview.height == 600
```

## Code Style

### Conventions

- **PEP 8** style guide
- **Type hints** for function signatures
- **Docstrings** for public functions
- **Clear variable names** over brevity

### Example

```python
def load_manifest(manifest_path: str) -> dict:
    """Load and parse a font manifest JSON file.

    Args:
        manifest_path: Path to manifest JSON file

    Returns:
        Parsed manifest dictionary

    Raises:
        FileNotFoundError: If manifest file doesn't exist
        ValueError: If JSON is invalid
    """
    # Implementation
```

## Adding Features

### 1. New CLI Command

Edit `src/cp_font_preview/cli.py`:

```python
@cli.command()
@click.option('--option', help='Description')
def mycommand(option):
    """Command description."""
    # Implementation
```

Add to justfile:

```just
# My new command
mycommand OPTION:
    uv run cp-font-preview mycommand --option {{OPTION}}
```

### 2. New Display Feature

Edit `src/cp_font_preview/preview.py`:

```python
class FontPreview:
    def add_feature(self):
        """Add new display feature."""
        # Implementation
```

Write tests:

```python
def test_new_feature():
    """Test the new display feature."""
    # Mock pygame and test
```

### 3. New Manifest Field

1. Add field to manifest in cp-font-gen
2. Update `manifest.py` to parse it
3. Use in relevant module
4. Document in configuration.md
5. Add tests

## Using as a Library

The package can be imported and used programmatically:

```python
from cp_font_preview import load_manifest, FontPreview
from pathlib import Path

# Load manifest
manifest_data = load_manifest('manifest.json')

# Get font info
from cp_font_preview.manifest import get_characters, get_font_paths, get_font_info

characters = get_characters(manifest_data)
font_paths = get_font_paths(manifest_data)
font_info = get_font_info(manifest_data)

# Create and run preview
font_file = font_paths[0]
preview = FontPreview(
    str(font_file),
    characters,
    font_info,
    width=1024,
    height=768
)

try:
    preview.run()
finally:
    preview.close()
```

## Debugging

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Debug CLI Commands

```bash
# Add --help to any command
uv run cp-font-preview preview --help

# Use Python debugger
uv run python -m pdb -m cp_font_preview.cli preview --manifest manifest.json
```

### Debug Display Issues

```bash
# Check SDL environment
SDL_VIDEODRIVER=x11 uv run cp-font-preview preview --manifest manifest.json

# Run with pygame debugging
PYGAME_DEBUG=1 uv run cp-font-preview preview --manifest manifest.json
```

## Release Process

1. Update version in `src/cp_font_preview/__init__.py`
2. Update version in `pyproject.toml`
3. Run full test suite: `just test-cov`
4. Update CHANGELOG.md
5. Commit changes
6. Tag release: `git tag v1.0.1`
7. Push: `git push && git push --tags`

## Common Tasks

### Add a New Test

```bash
# Create test file
touch tests/test_new_feature.py

# Write tests
# Run them
just test
```

### Check Test Coverage

```bash
just test-cov
# Look for uncovered lines in output
```

### Update Dependencies

```bash
# Edit pyproject.toml dependencies
# Then sync
uv sync
```

### Clean Everything

```bash
just clean        # Remove venv and lock file
uv sync          # Reinstall
```

## Display Architecture

Understanding how preview rendering works:

```text
1. CLI (cli.py)
   ↓
2. Load Manifest (manifest.py)
   ↓
3. Create FontPreview (preview.py)
   ↓
4. Initialize pygame window
   ↓
5. Load font via Blinka displayio
   ↓
6. Create character grid using displayio.Group
   ↓
7. Render loop (60 FPS)
   ↓
8. Optional: Watch mode (watcher.py)
   → Detect file changes
   → Reload manifest
   → Update display
```

## Performance Considerations

- Font loading is cached by Blinka
- Display runs at 60 FPS (pygame)
- Watch mode has 500ms debounce
- Large character sets may slow rendering

## Troubleshooting Development Issues

### Import Errors

```bash
# Package not installed
uv sync

# Old version cached
just clean
uv sync
```

### Tests Failing

```bash
# Run with verbose output
uv run pytest -v

# Run single test
uv run pytest tests/test_manifest.py::test_name -v

# Check for print statements
uv run pytest -s
```

### CLI Not Working

```bash
# Verify installation
uv run cp-font-preview --version

# Check entry point
grep "cp-font-preview" pyproject.toml

# Reinstall
uv sync --reinstall
```

### pygame Issues

```bash
# Check SDL2 installed
brew list | grep sdl2  # macOS
dpkg -l | grep sdl2    # Linux

# Reinstall pygame
uv pip install pygame --force-reinstall
```

## Contributing Guidelines

1. **Fork** the repository
2. **Create a branch** for your feature
3. **Write tests** for new functionality
4. **Ensure tests pass**: `just test`
5. **Format and lint**: `just pre-commit`
6. **Update documentation** as needed
7. **Submit pull request** with clear description

## Future Improvements

Ideas for contributions:

- **Scrollable view** for large character sets
- **Side-by-side size comparison** for multiple font sizes
- **Custom color schemes** for display
- **Character search/filter** to highlight specific glyphs
- **Screenshot/export** functionality
- **Font metrics overlay** showing glyph dimensions
- **Configurable grid columns**

See TODO.md for tracked feature requests.

## Resources

### Python Tools

- [Click Documentation](https://click.palletsprojects.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [uv Documentation](https://docs.astral.sh/uv/)

### Display Libraries

- [pygame Documentation](https://www.pygame.org/docs/)
- [Blinka displayio](https://github.com/adafruit/Adafruit_Blinka_Displayio)
- [CircuitPython displayio](https://docs.circuitpython.org/en/latest/shared-bindings/displayio/)

### CircuitPython

- [CircuitPython Docs](https://docs.circuitpython.org/)
- [Adafruit Learn](https://learn.adafruit.com/)
- [Bitmap Font Guide](https://learn.adafruit.com/custom-fonts-for-pyportal-circuitpython-display)
