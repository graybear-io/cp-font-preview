# Quick Start

Get cp-font-preview running in 5 minutes.

## Prerequisites

### System Libraries Installation

cp-font-preview uses pygame which requires SDL2 libraries:

| **SDL2 Libraries** | Operating System |
|------|---------------------|
| macOS | [Homebrew](https://formulae.brew.sh/formula/sdl2)<br/>`brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf` |
| Linux (Debian/Ubuntu) | [apt](https://packages.debian.org/search?keywords=libsdl2-dev)<br/>`sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev` |
| Linux (Fedora/RHEL) | [dnf](https://packages.fedoraproject.org/search?query=SDL2-devel)<br/>`sudo dnf install SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel` |
| Windows | Usually bundled with pygame. See [Troubleshooting](troubleshooting.md#sdl2-issues) if needed. |

### Python

- Python 3.10 or later
- uv (recommended) or pip

## Installation

### Option 1: Clone and Use

```bash
git clone https://github.com/graybear-io/cp-font-preview.git
cd cp-font-preview
uv sync          # Creates .venv and installs dependencies
```

### Option 2: Install as Package (Future)

```bash
pip install cp-font-preview  # When published
```

## First Preview

### 1. Generate a Font

First, generate a font using cp-font-gen:

```bash
cd ../cp-font-gen/examples/minimal
uv run cp-font-gen generate --config config.yaml
```

This creates `output/digits/digits-manifest.json`.

### 2. Preview the Font

```bash
cd ../../../cp-font-preview
uv run cp-font-preview preview --manifest ../cp-font-gen/examples/minimal/output/digits/digits-manifest.json
```

A pygame window opens showing all characters in a grid!

### 3. Try Watch Mode

Watch mode automatically reloads when fonts change:

```bash
# Terminal 1: Start preview with watch mode
uv run cp-font-preview preview --manifest ../cp-font-gen/examples/minimal/output/digits/digits-manifest.json --watch

# Terminal 2: Regenerate the font
cd ../cp-font-gen/examples/minimal
# Edit config.yaml to add more characters...
uv run cp-font-gen generate --config config.yaml
# → Preview window automatically updates!
```

## Quick Reference

### Commands

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

### Using Justfile

```bash
# Show available commands
just

# Preview specific examples
just preview-minimal
just preview-emoji

# Watch mode for quick iteration
just watch-minimal
```

## Next Steps

- **[User Guide](user-guide.md)** - Complete usage documentation
- **[Configuration](configuration.md)** - Customize window and behavior
- **[Troubleshooting](troubleshooting.md)** - Fix common issues
