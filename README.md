# cp-font-preview

Preview CircuitPython bitmap fonts locally before deploying to hardware.

**Visualize fonts instantly** with pygame + Blinka - no microcontroller needed.

## Quick Start

### Prerequisites

**SDL2 libraries:** See [System Libraries Installation](docs/quick-start.md#system-libraries-installation) for platform-specific install instructions.

### Installation

```bash
cd cp-font-preview
uv sync          # Install dependencies
```

### First Preview

```bash
# 1. Generate a font (using cp-font-gen)
cd ../cp-font-gen/examples/minimal
uv run cp-font-gen generate --config config.yaml

# 2. Preview it
cd ../../cp-font-preview
uv run cp-font-preview preview --manifest ../cp-font-gen/examples/minimal/output/digits/digits-manifest.json
```

A pygame window opens showing all characters in a grid!

## Watch Mode - Rapid Iteration

```bash
# Terminal 1: Start preview with auto-reload
uv run cp-font-preview preview --manifest path/to/manifest.json --watch

# Terminal 2: Edit and regenerate
# → Preview updates automatically!
```

## Commands

```bash
# Preview a font
cp-font-preview preview --manifest path/to/manifest.json

# Preview with watch mode
cp-font-preview preview --manifest path/to/manifest.json --watch

# Show font info
cp-font-preview info path/to/manifest.json

# Custom window size
cp-font-preview preview --manifest path/to/manifest.json --width 1024 --height 768
```

## Using Justfile

```bash
just                    # Show all commands
just preview MANIFEST   # Preview a manifest
just watch MANIFEST     # Watch mode
just preview-minimal    # Preview minimal example
```

## Features

- **Character Grid** - See all glyphs at once (16 per row)
- **Watch Mode** - Auto-reload when fonts regenerate
- **Manifest-Driven** - Works with cp-font-gen output
- **Multiple Formats** - PCF and BDF support
- **CircuitPython Compatible** - Uses Blinka displayio

## Typical Workflow

```bash
# 1. Generate fonts
cd cp-font-gen
cp-font-gen generate --config examples/emoji/config.yaml

# 2. Preview
cd ../cp-font-preview
cp-font-preview preview --manifest ../cp-font-gen/examples/emoji/output/emoji/emoji-manifest.json

# 3. Iterate
# → Edit config
# → Regenerate
# → Preview updates (if using --watch)

# 4. Deploy
cp ../cp-font-gen/output/emoji/*.pcf /Volumes/CIRCUITPY/fonts/
```

## Documentation

- **[Quick Start](docs/quick-start.md)** - Get running in 5 minutes
- **[User Guide](docs/user-guide.md)** - Comprehensive usage documentation
- **[Configuration](docs/configuration.md)** - Window settings and watch mode
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[Development](docs/development.md)** - Contributing and development setup

## Requirements

- Python 3.10+
- SDL2 libraries
- pygame (via Blinka displayio)
- Font files (PCF or BDF format)

## Limitations

- **Emoji rendering**: Monochrome only (PCF/BDF limitation)
- **One size at a time**: Doesn't compare multiple sizes
- **Grid layout only**: 16 columns, not configurable

See [Troubleshooting](docs/troubleshooting.md) for more details.

## Related Tools

- **[cp-font-gen](../cp-font-gen/)** - Generate minimal CircuitPython fonts

## License

MIT
