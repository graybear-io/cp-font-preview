"""Pytest fixtures for cp-font-preview tests."""

import json
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def sample_manifest_data() -> dict[str, Any]:
    """Return a sample manifest dictionary with all fields.

    Returns:
        Dictionary representing a typical font manifest
    """
    return {
        "version": "1.0",
        "source_font": "/System/Library/Fonts/Helvetica.ttc",
        "character_count": 10,
        "characters": "0123456789",
        "unicode_ranges": [
            "U+0030",
            "U+0031",
            "U+0032",
            "U+0033",
            "U+0034",
            "U+0035",
            "U+0036",
            "U+0037",
            "U+0038",
            "U+0039",
        ],
        "sizes": [16],
        "output_directory": "/tmp/test/output/digits",
        "generated_files": ["digits-16pt.pcf"],
        "formats": ["pcf"],
    }


@pytest.fixture
def minimal_manifest_data() -> dict[str, Any]:
    """Return a minimal manifest with only required fields.

    Returns:
        Dictionary with minimal manifest data
    """
    return {
        "output_directory": "/tmp/test/output",
        "generated_files": ["font-16pt.pcf"],
    }


@pytest.fixture
def temp_manifest_file(tmp_path: Path, sample_manifest_data: dict[str, Any]) -> Path:
    """Create a temporary manifest JSON file.

    Args:
        tmp_path: Pytest's temporary directory fixture
        sample_manifest_data: Sample manifest dictionary

    Returns:
        Path to the temporary manifest file
    """
    manifest_path = tmp_path / "test-manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(sample_manifest_data, f, indent=2)
    return manifest_path


@pytest.fixture
def temp_font_file(tmp_path: Path) -> Path:
    """Create a temporary mock font file.

    Args:
        tmp_path: Pytest's temporary directory fixture

    Returns:
        Path to the temporary font file (empty file, just for existence checks)
    """
    font_path = tmp_path / "test-font.pcf"
    font_path.touch()
    return font_path


@pytest.fixture
def mock_display(mocker):
    """Mock PyGameDisplay from blinka-displayio-pygamedisplay.

    Args:
        mocker: pytest-mock fixture

    Returns:
        Mock display object
    """
    mock = mocker.Mock()
    mock.check_quit.return_value = False
    mock.root_group = None
    return mock


@pytest.fixture
def mock_font(mocker):
    """Mock bitmap_font from adafruit_bitmap_font.

    Args:
        mocker: pytest-mock fixture

    Returns:
        Mock font object
    """
    return mocker.Mock()


@pytest.fixture
def mock_label(mocker):
    """Mock Label class from adafruit_display_text.

    Args:
        mocker: pytest-mock fixture

    Returns:
        Mock Label class
    """
    mock_label_instance = mocker.Mock()
    mock_label_instance.x = 0
    mock_label_instance.y = 0
    mock_label_class = mocker.Mock(return_value=mock_label_instance)
    return mock_label_class
