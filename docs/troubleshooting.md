# Troubleshooting

Common issues and solutions for cp-font-preview.

## Installation Issues

### SDL2 Not Found

**Error:**
```
SDL.h: No such file or directory
```

**Solution:**

See [System Libraries Installation](quick-start.md#system-libraries-installation) for platform-specific install instructions.

### pygame Installation Fails

**Error:**
```
error: command 'gcc' failed with exit status 1
```

**Solution:**

**macOS:**
```bash
# Install Xcode command line tools
xcode-select --install

# Then reinstall
uv sync --reinstall-package pygame
```

**Linux:**
```bash
# Install build essentials
sudo apt-get install build-essential python3-dev

# Then reinstall
uv sync --reinstall-package pygame
```

### Blinka Import Error

**Error:**
```
ModuleNotFoundError: No module named 'displayio'
```

**Solution:**

Ensure blinka-displayio-pygamedisplay is installed:
```bash
cd cp-font-preview
uv sync  # Reinstall all dependencies
```

If problem persists:
```bash
uv pip install blinka-displayio-pygamedisplay --force-reinstall
```

## Runtime Issues

### "Cannot load font"

**Error:**
```
Error: Font file not found: /path/to/font.pcf
```

**Solutions:**

1. **Check file exists:**
   ```bash
   ls -la /path/to/font.pcf
   ```

2. **Check manifest paths:**
   ```bash
   cp-font-preview info path/to/manifest.json
   ```

   Look for ✗ marks indicating missing files.

3. **Regenerate fonts:**
   ```bash
   cd ../cp-font-gen
   cp-font-gen generate --config config.yaml
   ```

4. **Check manifest location:**

   Manifest uses relative paths from `output_directory`. Ensure directory structure is intact.

### Empty/Blank Window

**Symptoms:** Window opens but shows nothing.

**Solutions:**

1. **Check characters in manifest:**
   ```bash
   cp-font-preview info manifest.json
   ```

   If "Character Count: 0", regenerate font with characters.

2. **Check font format:**

   Ensure font is PCF or BDF format. TTF/OTF are not supported.

3. **Check font size:**

   Very large fonts may render off-screen. Try larger window:
   ```bash
   cp-font-preview preview --manifest manifest.json --width 1600 --height 1200
   ```

### Watch Mode Not Working

**Symptoms:** Files change but preview doesn't update.

**Solutions:**

1. **Check file monitoring:**

   Look for "Reloading..." messages in terminal. If missing, watchdog may not be detecting changes.

2. **Regenerate fonts:**

   Watch mode monitors the directory containing the manifest. Ensure fonts are actually regenerating:
   ```bash
   # Check timestamps
   ls -lt output/myfont/
   ```

3. **Restart watch mode:**

   Sometimes file watchers get stuck:
   ```bash
   # Ctrl+C to stop
   # Restart
   cp-font-preview preview --manifest manifest.json --watch
   ```

4. **Check debounce timing:**

   If regeneration is very fast, changes may be debounced. Wait 1-2 seconds after regeneration.

### "Characters missing" or Showing Boxes

**Symptoms:** Some characters show as □ or are missing.

**Causes:**
- Font doesn't contain those characters
- Source font doesn't support those glyphs

**Solutions:**

1. **Check manifest characters:**
   ```bash
   cp-font-preview info manifest.json
   ```

2. **Verify source font:**

   Ensure source font used by cp-font-gen contains the glyphs:
   ```bash
   # Test in system font viewer
   open /path/to/source-font.ttf  # macOS
   ```

3. **Use different source font:**

   Edit cp-font-gen config to use font with better Unicode coverage:
   ```yaml
   source_font: "/Library/Fonts/Arial Unicode.ttf"
   ```

### Emoji Not Showing Color

**This is expected behavior.**

PCF and BDF formats are monochrome bitmap fonts. Emoji will appear as:
- White silhouettes on black background
- Single-color glyphs

This is how CircuitPython displays them on hardware. For color emoji:
- Use different font format (not supported by CircuitPython)
- Or use image sprites instead of text

### High CPU Usage

**Symptoms:** Fan spinning, high CPU usage during preview.

**Solutions:**

1. **Normal during display:**

   pygame runs at 60 FPS. Some CPU usage is expected.

2. **Close preview when not needed:**

   Don't leave preview running in background.

3. **Reduce window size:**
   ```bash
   cp-font-preview preview --manifest manifest.json --width 640 --height 480
   ```

## Display Issues

### Window Too Small

**Symptoms:** Characters cut off or not all visible.

**Solution:**

Increase window size:
```bash
cp-font-preview preview --manifest manifest.json --width 1600 --height 1200
```

Or reduce character set in font generation.

### Window Won't Open

**Error:**
```
pygame.error: No available video device
```

**Solutions:**

1. **Check display connection:**

   Ensure monitor is connected and working.

2. **Try different video driver:**
   ```bash
   SDL_VIDEODRIVER=x11 cp-font-preview preview --manifest manifest.json
   ```

3. **Run in virtual display (headless):**
   ```bash
   # Install Xvfb (Linux)
   sudo apt-get install xvfb

   # Run with virtual display
   xvfb-run cp-font-preview preview --manifest manifest.json
   ```

### Window Opens on Wrong Monitor

**Solution:**

Use SDL environment variable:
```bash
SDL_VIDEO_WINDOW_POS=0,0 cp-font-preview preview --manifest manifest.json
```

Or move window manually after opening.

## Performance Issues

### Slow Font Loading

**Symptoms:** Takes >5 seconds to open preview.

**Solutions:**

1. **Use PCF instead of BDF:**

   PCF is binary and loads faster. Ensure cp-font-gen generates PCF:
   ```yaml
   formats:
     - pcf  # Faster
     - bdf  # Slower
   ```

2. **Reduce character count:**

   Fewer glyphs = faster loading.

3. **Check disk speed:**

   Loading from network drives is slower. Copy fonts locally.

### Watch Mode Laggy

**Symptoms:** Delay between file change and reload.

**This is expected:**
- 500ms debounce prevents rapid reloads
- Font regeneration takes time
- Total delay is usually 1-2 seconds

**To improve:**
- Use faster disk (SSD)
- Generate smaller fonts
- Close other applications

## Integration Issues

### Manifest Not Found

**Error:**
```
Error: Manifest not found: path/to/manifest.json
```

**Solutions:**

1. **Check path:**
   ```bash
   ls path/to/manifest.json
   ```

2. **Generate fonts first:**
   ```bash
   cd ../cp-font-gen
   cp-font-gen generate --config config.yaml
   ```

   This creates the manifest.

3. **Use absolute paths:**
   ```bash
   cp-font-preview preview --manifest /full/path/to/manifest.json
   ```

### Wrong Font Displayed

**Symptoms:** Preview shows different font than expected.

**Cause:** When multiple sizes exist, first PCF file is used.

**Solution:**

Generate with single size, or edit manifest to list desired font first:
```json
{
  "generated_files": [
    "myfont-24pt.pcf",  ← This one will be used
    "myfont-16pt.pcf"
  ]
}
```

## Getting Help

If you're still stuck:

1. **Check version:**
   ```bash
   cp-font-preview --version
   ```

2. **Run info command:**
   ```bash
   cp-font-preview info manifest.json
   ```

   Share output when asking for help.

3. **Check dependencies:**
   ```bash
   uv pip list
   ```

4. **Look for error messages:**

   Run with verbose output (if available).

5. **Search issues:**

   Check GitHub issues for similar problems.

6. **Ask for help:**

   Open a GitHub issue with:
   - Full error message
   - Output of `info` command
   - Operating system and Python version
   - Steps to reproduce

## Known Limitations

These are expected behavior, not bugs:

1. **Emoji are monochrome** - PCF/BDF format limitation
2. **One size at a time** - Preview doesn't compare multiple sizes
3. **Grid layout only** - No alternative display modes yet
4. **16 columns hardcoded** - Not configurable currently
5. **No scrolling** - Large fonts may not fit in window

See [Development](development.md) for contributing improvements.

## Next Steps

- **[Configuration](configuration.md)** - Customize behavior
- **[User Guide](user-guide.md)** - Complete usage documentation
- **[Development](development.md)** - Report bugs or contribute fixes
