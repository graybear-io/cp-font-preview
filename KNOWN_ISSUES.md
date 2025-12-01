# Known Issues

## Hybrid Pygame + Blinka Architecture Limitation

**Status**: Architectural constraint requiring design decision

**Issue**: Cannot create multiple pygame displays simultaneously. PyGameDisplay creates actual pygame windows, and pygame only supports one display at a time. This prevents the hybrid approach where we wanted:
- Main pygame window for UI chrome (buttons, panels, interactions)
- Offscreen Blinka displays for PCF/BDF font rendering

**Root Cause**:
- `PyGameDisplay` from Blinka creates actual pygame display windows
- Calling `pygame.display.set_mode()` or creating new `PyGameDisplay` replaces the previous display
- Cannot have "offscreen" Blinka rendering alongside main pygame window

**Current Workaround**: Using pure pygame with system fonts (fallback mode)
- ✅ Full UI functionality works perfectly
- ✅ Event-driven architecture proven
- ✅ All interactions (click, select, resize) working
- ❌ Does not show actual PCF/BDF bitmap rendering

**Proposed Solution**: Two-mode system
1. **Interactive Mode** (pygame): Full UI with all interactions, uses system fonts
2. **Blinka Mode** (displayio): Non-interactive display showing actual PCF/BDF rendering

This gives users both:
- Accurate font rendering validation (Blinka mode)
- Interactive testing and exploration (pygame mode)

**Implementation Plan**:
- Add `--mode` CLI flag: `interactive` (default) or `blinka`
- Interactive mode: Current pygame-based UI
- Blinka mode: Simple non-interactive window showing font with actual rendering

**Alternative Approaches Considered**:
1. Pure Blinka: Loses complex UI interactions
2. Single display hybrid: Would require rewriting all UI in displayio primitives
3. Extract Blinka rendering: Not possible with current API

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
