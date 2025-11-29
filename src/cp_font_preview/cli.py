"""CLI for cp-font-preview."""

import sys

import click

from . import __version__
from .manifest import get_characters, get_font_info, get_font_paths, load_manifest
from .preview import FontPreview
from .watcher import FontWatcher


@click.group()
@click.version_option(version=__version__)
def cli():
    """cp-font-preview: Preview CircuitPython bitmap fonts locally"""
    pass


@cli.command()
@click.option("--manifest", "-m", required=True, help="Path to font manifest JSON file")
@click.option("--watch", "-w", is_flag=True, help="Watch for changes and auto-reload")
@click.option("--width", default=800, help="Window width (default: 800)")
@click.option("--height", default=600, help="Window height (default: 600)")
def preview(manifest, watch, width, height):
    """Preview generated fonts in a window."""

    # Load manifest
    try:
        manifest_data = load_manifest(manifest)
    except FileNotFoundError:
        click.echo(f"Error: Manifest not found: {manifest}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error loading manifest: {e}", err=True)
        sys.exit(1)

    # Get font files
    font_paths = get_font_paths(manifest_data)
    if not font_paths:
        click.echo("Error: No font files found in manifest", err=True)
        sys.exit(1)

    # Use first PCF file found
    pcf_files = [f for f in font_paths if f.suffix == ".pcf"]
    if not pcf_files:
        # Try BDF files
        bdf_files = [f for f in font_paths if f.suffix == ".bdf"]
        if not bdf_files:
            click.echo("Error: No PCF or BDF files found", err=True)
            sys.exit(1)
        font_file = bdf_files[0]
    else:
        font_file = pcf_files[0]

    if not font_file.exists():
        click.echo(f"Error: Font file not found: {font_file}", err=True)
        sys.exit(1)

    # Get character string
    characters = get_characters(manifest_data)
    if not characters:
        click.echo("Warning: No characters found in manifest", err=True)
        characters = "ABCabc123"  # Fallback

    # Get font info
    font_info = get_font_info(manifest_data)

    # Create preview
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
