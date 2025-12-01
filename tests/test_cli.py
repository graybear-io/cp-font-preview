"""Tests for cli.py module."""

import json
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from cp_font_preview import __version__
from cp_font_preview.cli import cli


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def manifest_with_font(tmp_path: Path, sample_manifest_data: dict[str, Any]) -> Path:
    """Create a manifest file and corresponding font file.

    Args:
        tmp_path: Pytest's temporary directory fixture
        sample_manifest_data: Sample manifest data

    Returns:
        Path to the manifest file
    """
    # Update output directory to tmp_path
    sample_manifest_data["output_directory"] = str(tmp_path)

    # Create manifest file
    manifest_path = tmp_path / "test-manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(sample_manifest_data, f)

    # Create font file
    font_path = tmp_path / "digits-16pt.pcf"
    font_path.touch()

    return manifest_path


class TestCLIBasics:
    """Tests for basic CLI functionality."""

    def test_cli_version(self, runner: CliRunner):
        """Test --version flag displays correct version."""
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert __version__ in result.output

    def test_cli_help(self, runner: CliRunner):
        """Test --help flag displays help text."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "cp-font-preview" in result.output
        assert "preview" in result.output
        assert "info" in result.output

    def test_preview_help(self, runner: CliRunner):
        """Test preview --help displays preview command help."""
        result = runner.invoke(cli, ["preview", "--help"])

        assert result.exit_code == 0
        assert "--manifest" in result.output
        assert "--watch" in result.output
        assert "--width" in result.output
        assert "--height" in result.output


class TestPreviewCommandErrors:
    """Tests for preview command error handling."""

    def test_preview_missing_manifest_flag(self, runner: CliRunner):
        """Test that preview command requires --manifest flag."""
        result = runner.invoke(cli, ["preview"])

        assert result.exit_code != 0
        assert "Error" in result.output or "Missing option" in result.output

    def test_preview_manifest_not_found(self, runner: CliRunner):
        """Test error handling when manifest file doesn't exist."""
        result = runner.invoke(cli, ["preview", "--manifest", "/nonexistent/manifest.json"])

        assert result.exit_code == 1
        assert "Error" in result.output
        assert "Manifest not found" in result.output

    def test_preview_manifest_invalid_json(self, runner: CliRunner, tmp_path: Path):
        """Test error handling for malformed JSON in manifest."""
        invalid_manifest = tmp_path / "invalid.json"
        invalid_manifest.write_text("{invalid json")

        result = runner.invoke(cli, ["preview", "--manifest", str(invalid_manifest)])

        assert result.exit_code == 1
        assert "Error loading manifest" in result.output

    def test_preview_no_fonts_in_manifest(self, runner: CliRunner, tmp_path: Path):
        """Test error when manifest has no font files."""
        manifest = tmp_path / "empty-manifest.json"
        manifest.write_text(json.dumps({"output_directory": str(tmp_path), "generated_files": []}))

        result = runner.invoke(cli, ["preview", "--manifest", str(manifest)])

        assert result.exit_code == 1
        assert "No font files found" in result.output

    def test_preview_no_pcf_or_bdf(self, runner: CliRunner, tmp_path: Path):
        """Test error when no PCF or BDF files in manifest."""
        manifest_data = {
            "output_directory": str(tmp_path),
            "generated_files": ["font.txt", "font.otf"],  # Wrong formats
        }
        manifest = tmp_path / "no-bitmap-fonts.json"
        with open(manifest, "w") as f:
            json.dump(manifest_data, f)

        result = runner.invoke(cli, ["preview", "--manifest", str(manifest)])

        assert result.exit_code == 1
        assert "not found on disk" in result.output

    def test_preview_font_file_not_exists(self, runner: CliRunner, tmp_path: Path):
        """Test error when font file referenced in manifest doesn't exist."""
        manifest_data = {
            "output_directory": str(tmp_path),
            "generated_files": ["nonexistent-font.pcf"],
        }
        manifest = tmp_path / "missing-font-manifest.json"
        with open(manifest, "w") as f:
            json.dump(manifest_data, f)

        result = runner.invoke(cli, ["preview", "--manifest", str(manifest)])

        assert result.exit_code == 1
        assert "not found on disk" in result.output


class TestPreviewCommandLogic:
    """Tests for preview command logic and behavior."""

    def test_preview_no_characters_fallback(self, runner: CliRunner, tmp_path: Path, mocker):
        """Test that missing characters uses fallback 'ABCabc123'."""
        # Create manifest without characters
        manifest_data = {
            "output_directory": str(tmp_path),
            "generated_files": ["test-font.pcf"],
        }
        manifest = tmp_path / "no-chars-manifest.json"
        with open(manifest, "w") as f:
            json.dump(manifest_data, f)

        # Create font file
        font_file = tmp_path / "test-font.pcf"
        font_file.touch()

        # Mock FontPreview to avoid pygame initialization
        mock_preview = mocker.patch("cp_font_preview.cli.FontPreview")
        mock_instance = mocker.Mock()
        mock_preview.return_value = mock_instance

        runner.invoke(cli, ["preview", "--manifest", str(manifest)])

        # Check that FontPreview was called with fallback characters
        assert mock_preview.called
        call_args = mock_preview.call_args
        assert call_args[0][1] == "ABCabc123"  # characters argument

    def test_preview_prefers_pcf_over_bdf(self, runner: CliRunner, tmp_path: Path, mocker):
        """Test that PCF files are preferred over BDF files."""
        manifest_data = {
            "output_directory": str(tmp_path),
            "generated_files": ["font.bdf", "font.pcf"],  # BDF listed first
            "characters": "ABC",
        }
        manifest = tmp_path / "both-formats-manifest.json"
        with open(manifest, "w") as f:
            json.dump(manifest_data, f)

        # Create both font files
        (tmp_path / "font.bdf").touch()
        (tmp_path / "font.pcf").touch()

        # Mock FontPreview
        mock_preview = mocker.patch("cp_font_preview.cli.FontPreview")
        mock_instance = mocker.Mock()
        mock_preview.return_value = mock_instance

        runner.invoke(cli, ["preview", "--manifest", str(manifest)])

        # Check that PCF was selected
        assert mock_preview.called
        pcf_path = tmp_path / "font.pcf"
        assert str(pcf_path) in str(mock_preview.call_args[0][0])

    def test_preview_uses_bdf_if_no_pcf(self, runner: CliRunner, tmp_path: Path, mocker):
        """Test that BDF files are used if no PCF available."""
        manifest_data = {
            "output_directory": str(tmp_path),
            "generated_files": ["font.bdf"],  # Only BDF
            "characters": "ABC",
        }
        manifest = tmp_path / "bdf-only-manifest.json"
        with open(manifest, "w") as f:
            json.dump(manifest_data, f)

        # Create BDF font file
        (tmp_path / "font.bdf").touch()

        # Mock FontPreview
        mock_preview = mocker.patch("cp_font_preview.cli.FontPreview")
        mock_instance = mocker.Mock()
        mock_preview.return_value = mock_instance

        runner.invoke(cli, ["preview", "--manifest", str(manifest)])

        # Check that BDF was selected
        assert mock_preview.called
        bdf_path = tmp_path / "font.bdf"
        assert str(bdf_path) in str(mock_preview.call_args[0][0])

    def test_preview_with_custom_dimensions(self, runner: CliRunner, tmp_path: Path, mocker):
        """Test --width and --height options."""
        manifest_data = {
            "output_directory": str(tmp_path),
            "generated_files": ["font.pcf"],
            "characters": "ABC",
        }
        manifest = tmp_path / "test-manifest.json"
        with open(manifest, "w") as f:
            json.dump(manifest_data, f)

        (tmp_path / "font.pcf").touch()

        # Mock FontPreview
        mock_preview = mocker.patch("cp_font_preview.cli.FontPreview")
        mock_instance = mocker.Mock()
        mock_preview.return_value = mock_instance

        runner.invoke(
            cli, ["preview", "--manifest", str(manifest), "--width", "1024", "--height", "768"]
        )

        # Check that custom dimensions were passed
        assert mock_preview.called
        call_kwargs = mock_preview.call_args[1]
        assert call_kwargs["width"] == 1024
        assert call_kwargs["height"] == 768

    def test_preview_watch_mode(self, runner: CliRunner, tmp_path: Path, mocker):
        """Test that --watch flag initializes FontWatcher."""
        manifest_data = {
            "output_directory": str(tmp_path),
            "generated_files": ["font.pcf"],
            "characters": "ABC",
        }
        manifest = tmp_path / "test-manifest.json"
        with open(manifest, "w") as f:
            json.dump(manifest_data, f)

        (tmp_path / "font.pcf").touch()

        # Mock components
        mock_preview = mocker.patch("cp_font_preview.cli.FontPreview")
        mock_watcher = mocker.patch("cp_font_preview.cli.FontWatcher")
        mock_instance = mocker.Mock()
        mock_preview.return_value = mock_instance
        mock_watcher_instance = mocker.Mock()
        mock_watcher.return_value = mock_watcher_instance

        runner.invoke(cli, ["preview", "--manifest", str(manifest), "--watch"])

        # Check that FontWatcher was created and started
        assert mock_watcher.called
        assert mock_watcher_instance.start.called
        assert mock_watcher_instance.stop.called  # Called in finally block


class TestInfoCommand:
    """Tests for info command."""

    def test_info_command_success(self, runner: CliRunner, manifest_with_font: Path):
        """Test info command displays manifest information."""
        result = runner.invoke(cli, ["info", str(manifest_with_font)])

        assert result.exit_code == 0
        assert "Font Family:" in result.output
        assert "digits" in result.output
        assert "Sizes:" in result.output
        assert "16" in result.output
        assert "Formats:" in result.output
        assert "pcf" in result.output
        assert "Character Count:" in result.output
        assert "10" in result.output

    def test_info_command_shows_characters(self, runner: CliRunner, manifest_with_font: Path):
        """Test that info command displays character string."""
        result = runner.invoke(cli, ["info", str(manifest_with_font)])

        assert result.exit_code == 0
        assert "Characters:" in result.output
        assert "0123456789" in result.output

    def test_info_command_truncates_long_characters(self, runner: CliRunner, tmp_path: Path):
        """Test that long character strings are truncated with '...'."""
        # Create manifest with >50 characters
        long_chars = "A" * 60
        manifest_data = {
            "output_directory": str(tmp_path),
            "generated_files": ["font.pcf"],
            "characters": long_chars,
        }
        manifest = tmp_path / "long-chars-manifest.json"
        with open(manifest, "w") as f:
            json.dump(manifest_data, f)

        (tmp_path / "font.pcf").touch()

        result = runner.invoke(cli, ["info", str(manifest)])

        assert result.exit_code == 0
        assert "..." in result.output
        # Should show first 50 chars plus ...
        assert long_chars[:50] in result.output

    def test_info_command_shows_file_existence(self, runner: CliRunner, tmp_path: Path):
        """Test that info shows ✓ for existing files and ✗ for missing."""
        manifest_data = {
            "output_directory": str(tmp_path),
            "generated_files": ["exists.pcf", "missing.pcf"],
        }
        manifest = tmp_path / "test-manifest.json"
        with open(manifest, "w") as f:
            json.dump(manifest_data, f)

        # Create only one font file
        (tmp_path / "exists.pcf").touch()

        result = runner.invoke(cli, ["info", str(manifest)])

        assert result.exit_code == 0
        assert "✓" in result.output  # For existing file
        assert "✗" in result.output  # For missing file

    def test_info_command_file_not_found(self, runner: CliRunner):
        """Test info command with non-existent manifest."""
        result = runner.invoke(cli, ["info", "/nonexistent/manifest.json"])

        # Click returns exit code 2 for argument validation failures
        assert result.exit_code == 2
        assert "Error" in result.output or "does not exist" in result.output

    def test_info_command_invalid_manifest(self, runner: CliRunner, tmp_path: Path):
        """Test info command with invalid JSON."""
        invalid_manifest = tmp_path / "invalid.json"
        invalid_manifest.write_text("{invalid")

        result = runner.invoke(cli, ["info", str(invalid_manifest)])

        assert result.exit_code == 1
        assert "Error" in result.output
