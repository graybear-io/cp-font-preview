"""CLI for cp-font-preview."""

import sys

import click

from . import __version__
from .layout import WINDOW_HEIGHT, WINDOW_WIDTH
from .manifest import (
    get_characters,
    get_font_info,
    get_font_paths,
    load_manifest,
    validate_manifest_for_preview,
)
from .preview import FontPreview, preview_font_blinka
from .watcher import FontWatcher


@click.group()
@click.version_option(version=__version__)
def cli():
    """cp-font-preview: Preview CircuitPython bitmap fonts locally"""
    pass


@cli.command()
@click.option("--manifest", "-m", required=True, help="Path to font manifest JSON file")
@click.option(
    "--watch", "-w", is_flag=True, help="Watch for changes and auto-reload (interactive mode only)"
)
@click.option(
    "--mode",
    type=click.Choice(["interactive", "blinka"]),
    default="interactive",
    help="Preview mode: interactive (pygame, full UI) or blinka (non-interactive, accurate rendering)",
)
@click.option("--width", default=WINDOW_WIDTH, help=f"Window width (default: {WINDOW_WIDTH})")
@click.option("--height", default=WINDOW_HEIGHT, help=f"Window height (default: {WINDOW_HEIGHT})")
def preview(manifest, watch, mode, width, height):
    """Preview generated fonts in a window."""

    # Load and validate manifest
    try:
        manifest_data = load_manifest(manifest)
    except FileNotFoundError:
        click.echo(f"Error: Manifest not found: {manifest}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error loading manifest: {e}", err=True)
        sys.exit(1)

    # Validate manifest has usable font files
    validation_error = validate_manifest_for_preview(manifest_data, manifest)
    if validation_error:
        click.echo(f"Error: {validation_error}", err=True)
        sys.exit(1)

    # Get font files (validated to exist)
    font_paths = get_font_paths(manifest_data)
    pcf_files = [f for f in font_paths if f.suffix == ".pcf" and f.exists()]
    bdf_files = [f for f in font_paths if f.suffix == ".bdf" and f.exists()]

    # Prefer PCF over BDF
    font_file = pcf_files[0] if pcf_files else bdf_files[0]

    # Get character string
    characters = get_characters(manifest_data)
    if not characters:
        click.echo("Warning: No characters found in manifest", err=True)
        characters = "ABCabc123"  # Fallback

    # Get font info
    font_info = get_font_info(manifest_data)

    # Blinka mode: simple non-interactive display
    if mode == "blinka":
        if watch:
            click.echo("Warning: Watch mode not supported in Blinka mode", err=True)

        try:
            preview_font_blinka(str(font_file), characters, font_info, width=width, height=height)
        except KeyboardInterrupt:
            click.echo("\nExiting...")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        return

    # Interactive mode: full pygame UI
    font_preview = FontPreview(str(font_file), characters, font_info, width=width, height=height)

    # Setup watch mode if requested
    watcher = None
    reload_requested = [False]  # Use list for mutability in closure

    def on_change():
        reload_requested[0] = True

    def check_reload():
        if reload_requested[0]:
            reload_requested[0] = False
            # Reload manifest
            try:
                nonlocal manifest_data, characters, font_info
                manifest_data = load_manifest(manifest)
                characters = get_characters(manifest_data)
                font_info = get_font_info(manifest_data)
                font_preview.characters = characters
                font_preview.font_info = font_info
                return True
            except Exception as e:
                click.echo(f"Error reloading: {e}", err=True)
                return False
        return False

    if watch:
        watcher = FontWatcher(manifest, on_change)
        watcher.start()

    # Run preview
    try:
        if watch:
            font_preview.run(watch_callback=check_reload)
        else:
            font_preview.run()
    except KeyboardInterrupt:
        click.echo("\nExiting...")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    finally:
        if watcher:
            watcher.stop()
        font_preview.close()


@cli.command()
@click.argument("manifest_path", type=click.Path(exists=True))
def info(manifest_path):
    """Show information about a font manifest."""
    try:
        manifest_data = load_manifest(manifest_path)
        font_info = get_font_info(manifest_data)
        characters = get_characters(manifest_data)

        click.echo(f"Font Family: {font_info['font_family']}")
        click.echo(f"Sizes: {', '.join(map(str, font_info['sizes']))}")
        click.echo(f"Formats: {', '.join(font_info['formats'])}")
        click.echo(f"Character Count: {font_info['character_count']}")
        click.echo(f"\nCharacters: {characters[:50]}{'...' if len(characters) > 50 else ''}")

        # Show font files
        font_paths = get_font_paths(manifest_data)
        click.echo("\nFont Files:")
        for font_path in font_paths:
            exists = "✓" if font_path.exists() else "✗"
            click.echo(f"  {exists} {font_path}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
