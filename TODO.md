# TODO

## Test Coverage Improvements

**Current Status**: 43 tests passing (increased from 37)

### Completed ✅
- test_manifest.py (23 tests, 100% coverage) - Added 6 validation tests
- test_cli.py (20 tests, 80% coverage)

### Pending
- [ ] **test_preview.py** - Add tests for FontPreview class (currently 16% coverage)
  - Mock pygame/displayio interactions
  - Test font loading and rendering
  - Test display management

- [ ] **test_watcher.py** - Add tests for FontWatcher class (currently 32% coverage)
  - Test file watching functionality
  - Test callback triggers on file changes
  - Test observer lifecycle

**Goal**: Increase overall coverage to 70%+

## Known Issues
See `KNOWN_ISSUES.md` for dependency blockers.
