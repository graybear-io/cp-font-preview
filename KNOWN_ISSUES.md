# Known Issues

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
- PyPI package: https://pypi.org/project/blinka-displayio-pygamedisplay/
- GitHub repository: https://github.com/FoamyGuy/Blinka_Displayio_PyGameDisplay
- NumPy deprecation docs: https://numpy.org/doc/2.1/reference/generated/numpy.fromstring.html
