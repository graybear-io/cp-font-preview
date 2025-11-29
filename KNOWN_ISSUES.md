# Known Issues

## CRITICAL: Bitmap Fonts Not Rendering

**Status**: Critical blocker - core functionality broken

**Issue**: Neither PCF nor BDF bitmap fonts render in the displayio/pygame window. The window displays correctly with a colored background, but text labels using bitmap fonts do not appear.

**Reproduction**:
```bash
# Both PCF and BDF fonts fail to render
uv run python test_bdf.py   # Shows dark gray background only
uv run python test_simple_display.py  # Shows dark gray background only
```

**Root Cause**: Incompatibility between `adafruit_bitmap_font` (PCF/BDF loading) and `blinka_displayio_pygamedisplay` (pygame rendering). The labels are created successfully and added to the display group, but do not render visually.

**Evidence**:
- Background TileGrid renders correctly (dark gray shows)
- Font objects load successfully (no errors)
- Label objects create successfully (position, color, text all set)
- Labels added to group (confirmed via len(group))
- refresh() and auto_refresh work
- But no text appears on screen

**Potential Solutions**:
1. **File upstream issue** with Adafruit about bitmap font rendering in Blinka
2. **Rewrite preview tool** to use pygame directly instead of displayio (bypasses the issue)
3. **Wait for upstream fix** (timeline unknown)

**Impact**: The entire cp-font-preview tool is non-functional until this is resolved.

---

## blinka-displayio-pygamedisplay NumPy Compatibility Issue

**Status**: Waiting for upstream release

**Issue**: The current PyPI release (v4.0.0) of `blinka-displayio-pygamedisplay` uses the deprecated `np.fromstring()` which was removed in NumPy 2.0, causing the error:
```
Error: The binary mode of fromstring is removed, use frombuffer instead
```

**Fix Status**:
- ✅ Fixed in main branch: https://github.com/FoamyGuy/Blinka_Displayio_PyGameDisplay/blob/main/blinka_displayio_pygamedisplay.py (line 155 now uses `np.frombuffer`)
- ❌ Not yet released to PyPI (latest is still v4.0.0 from April 29, 2025)

**Workaround**: Install directly from GitHub main branch instead of PyPI:
```toml
dependencies = [
    "blinka-displayio-pygamedisplay @ git+https://github.com/FoamyGuy/Blinka_Displayio_PyGameDisplay.git",
]
```

**References**:
- Upstream issue: https://github.com/FoamyGuy/Blinka_Displayio_PyGameDisplay/issues/26
- Our tracking issue: https://github.com/graybear-io/cp-font-preview/issues/1
- PyPI package: https://pypi.org/project/blinka-displayio-pygamedisplay/
- GitHub repository: https://github.com/FoamyGuy/Blinka_Displayio_PyGameDisplay
- NumPy deprecation docs: https://numpy.org/doc/2.1/reference/generated/numpy.fromstring.html
