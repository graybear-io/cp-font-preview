"""Tests for manifest.py module."""

import json
from pathlib import Path
from typing import Any

import pytest

from cp_font_preview.manifest import (
    get_characters,
    get_font_info,
    get_font_paths,
    load_manifest,
    validate_manifest_for_preview,
)


class TestLoadManifest:
    """Tests for load_manifest function."""

    def test_load_manifest_success(self, temp_manifest_file: Path, sample_manifest_data: dict):
        """Test loading a valid manifest file."""
        result = load_manifest(str(temp_manifest_file))
        assert result == sample_manifest_data
        assert result["character_count"] == 10
        assert result["characters"] == "0123456789"

    def test_load_manifest_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            load_manifest("/nonexistent/path/manifest.json")

    def test_load_manifest_invalid_json(self, tmp_path: Path):
        """Test that JSONDecodeError is raised for malformed JSON."""
        invalid_manifest = tmp_path / "invalid.json"
        invalid_manifest.write_text("{invalid json content")

        with pytest.raises(json.JSONDecodeError):
            load_manifest(str(invalid_manifest))


class TestGetFontPaths:
    """Tests for get_font_paths function."""

    def test_get_font_paths(self, sample_manifest_data: dict):
        """Test extracting font paths from manifest."""
        paths = get_font_paths(sample_manifest_data)

        assert len(paths) == 1
        assert isinstance(paths[0], Path)
        assert paths[0].name == "digits-16pt.pcf"

    def test_get_font_paths_absolute(self, sample_manifest_data: dict):
        """Test that font paths are properly joined with output directory."""
        paths = get_font_paths(sample_manifest_data)

        expected = Path("/tmp/test/output/digits/digits-16pt.pcf")
        assert paths[0] == expected

    def test_get_font_paths_multiple_files(self):
        """Test extracting multiple font files."""
        manifest = {
            "output_directory": "/tmp/fonts",
            "generated_files": ["font-16pt.pcf", "font-24pt.pcf", "font-32pt.bdf"],
        }

        paths = get_font_paths(manifest)

        assert len(paths) == 3
        assert paths[0] == Path("/tmp/fonts/font-16pt.pcf")
        assert paths[1] == Path("/tmp/fonts/font-24pt.pcf")
        assert paths[2] == Path("/tmp/fonts/font-32pt.bdf")

    def test_get_font_paths_empty_list(self):
        """Test handling empty generated_files list."""
        manifest = {"output_directory": "/tmp/fonts", "generated_files": []}

        paths = get_font_paths(manifest)

        assert paths == []


class TestGetCharacters:
    """Tests for get_characters function."""

    def test_get_characters(self, sample_manifest_data: dict):
        """Test extracting character string from manifest."""
        characters = get_characters(sample_manifest_data)

        assert characters == "0123456789"

    def test_get_characters_missing_key(self):
        """Test that missing 'characters' key returns empty string."""
        manifest: dict[str, Any] = {"output_directory": "/tmp"}

        characters = get_characters(manifest)

        assert characters == ""

    def test_get_characters_empty_string(self):
        """Test handling empty characters string."""
        manifest = {"characters": ""}

        characters = get_characters(manifest)

        assert characters == ""

    def test_get_characters_unicode(self):
        """Test extracting unicode characters."""
        manifest = {"characters": "こんにちは世界🌍"}

        characters = get_characters(manifest)

        assert characters == "こんにちは世界🌍"


class TestGetFontInfo:
    """Tests for get_font_info function."""

    def test_get_font_info_complete(self, sample_manifest_data: dict):
        """Test extracting font metadata from complete manifest."""
        info = get_font_info(sample_manifest_data)

        assert info["font_family"] == "digits"
        assert info["sizes"] == [16]
        assert info["formats"] == ["pcf"]
        assert info["character_count"] == 10

    def test_get_font_info_font_family_extraction(self):
        """Test parsing font family from filename."""
        test_cases = [
            (["emoji-32pt.pcf"], "emoji"),
            (["helvetica-16pt.bdf"], "helvetica"),
            (["my-custom-font-24pt.pcf"], "my-custom-font"),
        ]

        for files, expected_family in test_cases:
            manifest = {"generated_files": files}
            info = get_font_info(manifest)
            assert info["font_family"] == expected_family

    def test_get_font_info_no_files(self):
        """Test handling empty generated_files list."""
        manifest: dict[str, Any] = {"generated_files": []}

        info = get_font_info(manifest)

        assert info["font_family"] == "unknown"

    def test_get_font_info_minimal(self):
        """Test extracting info from manifest with only required fields."""
        manifest: dict[str, Any] = {"generated_files": ["test-12pt.pcf"]}

        info = get_font_info(manifest)

        assert info["font_family"] == "test"
        assert info["sizes"] == []
        assert info["formats"] == []
        assert info["character_count"] == 0

    def test_get_font_info_no_hyphen_in_filename(self):
        """Test handling filename without hyphen (no size info)."""
        manifest = {"generated_files": ["test.pcf"]}

        info = get_font_info(manifest)

        assert info["font_family"] == "unknown"

    def test_get_font_info_multiple_sizes(self):
        """Test extracting multiple sizes from manifest."""
        manifest = {
            "generated_files": ["font-16pt.pcf"],
            "sizes": [16, 24, 32],
            "formats": ["pcf", "bdf"],
            "character_count": 100,
        }

        info = get_font_info(manifest)

        assert info["sizes"] == [16, 24, 32]
        assert info["formats"] == ["pcf", "bdf"]
        assert info["character_count"] == 100


class TestValidateManifestForPreview:
    """Tests for validate_manifest_for_preview function."""

    def test_validate_empty_generated_files(self):
        """Test validation fails when generated_files is empty."""
        manifest = {"generated_files": [], "output_directory": "/tmp"}
        error = validate_manifest_for_preview(manifest, "test.json")

        assert error is not None
        assert "No font files found" in error
        assert "empty generated_files list" in error
        assert "test.json" in error

    def test_validate_missing_generated_files_key(self):
        """Test validation fails when generated_files key is missing."""
        manifest: dict[str, Any] = {"output_directory": "/tmp"}
        error = validate_manifest_for_preview(manifest, "test.json")

        assert error is not None
        assert "No font files found" in error

    def test_validate_files_dont_exist(self, tmp_path: Path):
        """Test validation fails when files listed but don't exist on disk."""
        manifest = {
            "generated_files": ["font-16pt.pcf", "font-16pt.bdf"],
            "output_directory": str(tmp_path),
        }
        error = validate_manifest_for_preview(manifest, "test.json")

        assert error is not None
        assert "not found on disk" in error
        assert str(tmp_path) in error

    def test_validate_success_with_pcf(self, tmp_path: Path):
        """Test validation passes when valid PCF file exists."""
        font_file = tmp_path / "font-16pt.pcf"
        font_file.touch()

        manifest = {"generated_files": ["font-16pt.pcf"], "output_directory": str(tmp_path)}
        error = validate_manifest_for_preview(manifest, "test.json")

        assert error is None

    def test_validate_success_with_bdf(self, tmp_path: Path):
        """Test validation passes when valid BDF file exists."""
        font_file = tmp_path / "font-16pt.bdf"
        font_file.touch()

        manifest = {"generated_files": ["font-16pt.bdf"], "output_directory": str(tmp_path)}
        error = validate_manifest_for_preview(manifest, "test.json")

        assert error is None

    def test_validate_success_with_multiple_files(self, tmp_path: Path):
        """Test validation passes when at least one valid file exists."""
        pcf_file = tmp_path / "font-16pt.pcf"
        pcf_file.touch()

        manifest = {
            "generated_files": ["font-16pt.pcf", "font-24pt.pcf"],
            "output_directory": str(tmp_path),
        }
        error = validate_manifest_for_preview(manifest, "test.json")

        assert error is None
