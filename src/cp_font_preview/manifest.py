"""Manifest file reading and parsing."""

import json
from pathlib import Path
from typing import Any


def load_manifest(manifest_path: str) -> dict[str, Any]:
    """Load and parse a font manifest file.

    Args:
        manifest_path: Path to manifest JSON file

    Returns:
        Parsed manifest dictionary

    Raises:
        FileNotFoundError: If manifest doesn't exist
        json.JSONDecodeError: If manifest is invalid JSON
    """
    manifest_file = Path(manifest_path)

    if not manifest_file.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with open(manifest_file) as f:
        return json.load(f)


def get_font_paths(manifest: dict[str, Any]) -> list[Path]:
    """Get full paths to all generated font files from manifest.

    Args:
        manifest: Parsed manifest dictionary

    Returns:
        List of Path objects for each font file
    """
    output_dir = Path(manifest["output_directory"])
    font_files = manifest["generated_files"]

    return [output_dir / filename for filename in font_files]


def get_characters(manifest: dict[str, Any]) -> str:
    """Get the character string from manifest.

    Args:
        manifest: Parsed manifest dictionary

    Returns:
        String of all characters in the font
    """
    return manifest.get("characters", "")


def get_font_info(manifest: dict[str, Any]) -> dict[str, Any]:
    """Extract font metadata from manifest.

    Args:
        manifest: Parsed manifest dictionary

    Returns:
        Dictionary with font_family, sizes, formats, character_count
    """
    # Derive font family from manifest path or use default
    font_files = manifest.get("generated_files", [])
    if font_files:
        # Extract font family from filename (e.g., "emoji-32pt.pcf" -> "emoji")
        first_file = font_files[0]
        font_family = first_file.rsplit("-", 1)[0] if "-" in first_file else "unknown"
    else:
        font_family = "unknown"

    return {
        "font_family": font_family,
        "sizes": manifest.get("sizes", []),
        "formats": manifest.get("formats", []),
        "character_count": manifest.get("character_count", 0),
    }


def validate_manifest_for_preview(manifest: dict[str, Any], manifest_path: str) -> str | None:
    """Validate that manifest has usable font files for preview.

    Args:
        manifest: Parsed manifest dictionary
        manifest_path: Path to manifest file (for error messages)

    Returns:
        Error message string if validation fails, None if valid
    """
    # Check if generated_files list exists and is not empty
    generated_files = manifest.get("generated_files", [])
    if not generated_files:
        return (
            f"No font files found in manifest: {manifest_path}\n"
            "  Manifest has empty generated_files list\n"
            "  Font generation may have failed - check cp-font-gen output"
        )

    # Check if any PCF or BDF files exist on disk
    font_paths = get_font_paths(manifest)
    pcf_files = [f for f in font_paths if f.suffix == ".pcf" and f.exists()]
    bdf_files = [f for f in font_paths if f.suffix == ".bdf" and f.exists()]

    if not pcf_files and not bdf_files:
        # Files listed but don't exist on disk
        return (
            f"Font files listed in manifest but not found on disk: {manifest_path}\n"
            f"  Expected files in: {font_paths[0].parent if font_paths else 'unknown'}"
        )

    return None
