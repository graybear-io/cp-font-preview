# Hybrid Approach Decision

**Date**: 2025-11-29

## Decision

Use a **hybrid pygame + Blinka/displayio** approach with clear separation of concerns:

- **Pygame**: UI framework, layout, interactions, sample text (system fonts)
- **Blinka/displayio**: PCF/BDF bitmap font rendering only (character grid + glyph detail)

## Rationale

### Why Hybrid?
1. **Validates real font rendering**: Blinka/displayio shows how fonts will actually look on CircuitPython hardware
2. **Keeps UI simple**: Pygame handles all interactions, no displayio limitations
3. **Development velocity**: Easy to implement complex UI with pygame
4. **Best of both worlds**: CircuitPython-compatible font rendering + modern UI

### Why Not Pure Pygame?
- Would miss testing actual PCF/BDF rendering behavior
- Wouldn't validate CircuitPython font display accurately
- Less informative for embedded development

### Why Not Pure Blinka/displayio?
- displayio has limited interactivity (no native click handlers)
- Harder to implement complex UI layouts
- Slower development
- Performance concerns

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Main Window (pygame)                │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Metadata Bar (pygame)                               │ │
│ │ - Text rendering with system fonts                  │ │
│ │ - Size selector buttons                             │ │
│ │ - Font info display                                 │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌──────────────────────────┬──────────────────────────┐ │
│ │ Left Panel (pygame)      │ Right Panel (pygame)     │ │
│ │                          │                          │ │
│ │ Sample Text (pygame)     │ Glyph Detail             │ │
│ │ - System fonts           │ (Blinka Surface)         │ │
│ │ - Pangrams, test strings │ ┌────────────────────┐   │ │
│ │                          │ │  [A]               │   │ │
│ │ Character Grid           │ │  PCF/BDF rendered  │   │ │
│ │ (Blinka Surface)         │ │  with Blinka       │   │ │
│ │ ┌────────────────────┐   │ └────────────────────┘   │ │
│ │ │ A B C D E F ...    │   │                          │ │
│ │ │ PCF/BDF rendered   │   │ - Unicode info (pygame)  │ │
│ │ │ with Blinka        │   │ - Dimensions (pygame)    │ │
│ │ └────────────────────┘   │ - Bounding box (pygame)  │ │
│ └──────────────────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Technical Implementation

### Pygame Components
- **Window management**: pygame.display
- **Layout/panels**: pygame.draw rectangles
- **UI text**: pygame.font (system fonts)
- **Buttons**: pygame rects + click detection
- **Mouse events**: pygame.event
- **Bounding boxes**: pygame.draw.rect
- **Background/decorations**: pygame surfaces

### Blinka Components
- **Font loading**: adafruit_bitmap_font.bitmap_font
- **Character rendering**: displayio.Label
- **Surface creation**: Render to pygame-compatible surface

### Integration Points

**Blinka → Pygame Surface:**
```python
# Option 1: Render Blinka to offscreen, blit to pygame
blinka_display = PyGameDisplay(width=w, height=h, auto_refresh=False)
# ... render characters with displayio ...
pygame_surface = blinka_display.get_surface()
main_screen.blit(pygame_surface, (x, y))

# Option 2: Direct pixel access
# Render Blinka display, extract pixels, create pygame surface
```

**Character Grid Flow:**
1. Load PCF/BDF font with Blinka
2. Create offscreen Blinka display for grid area
3. Render characters with displayio.Label
4. Convert to pygame surface
5. Blit to main window
6. Handle clicks with pygame (map position to character)

**Glyph Detail Flow:**
1. User clicks character (pygame event)
2. Create offscreen Blinka display
3. Render large character with displayio.Label
4. Convert to pygame surface
5. Blit to detail panel
6. Draw bounding box with pygame
7. Show metadata with pygame fonts

## Benefits of This Approach

### Development
- ✓ Fast iteration on UI layout (pygame is straightforward)
- ✓ Easy debugging (standard pygame tools)
- ✓ No fighting with displayio limitations

### Functionality
- ✓ All planned features achievable
- ✓ Smooth interactions
- ✓ Good performance

### CircuitPython Validation
- ✓ Real PCF/BDF rendering via Blinka
- ✓ Tests actual font display behavior
- ✓ Validates glyph coverage
- ✓ Shows actual character appearance

### Flexibility
- ✓ Can add features easily (export, compare mode, etc.)
- ✓ Can optimize performance where needed
- ✓ Can extend UI without Blinka constraints

## Constraints

### Must Use Blinka For:
- Character grid display (PCF/BDF fonts)
- Glyph detail character (PCF/BDF fonts)

### Must Use Pygame For:
- Window management
- Layout and panels
- All UI chrome (buttons, labels, borders)
- Sample text (can use system fonts)
- Mouse/keyboard input handling
- Animation/transitions

### Can Use Either:
- Background colors (prefer pygame for simplicity)
- Decorative elements (prefer pygame)
- Debug overlays (prefer pygame)

## Implementation Strategy

### Phase 1: Pygame Framework
Build the complete UI with pygame + system fonts:
- Window setup
- Layout (panels, sections)
- Metadata display
- Size selector buttons
- Sample text rendering
- Character grid (placeholder with system fonts)
- Glyph detail (placeholder with system fonts)
- All interactions working

**Deliverable**: Fully functional preview with system fonts (like mockup)

### Phase 2: Blinka Integration
Replace placeholders with Blinka font rendering:
- Character grid: Use Blinka to render PCF/BDF
- Glyph detail: Use Blinka to render large character
- Keep all UI chrome as pygame

**Deliverable**: Hybrid preview with real PCF/BDF rendering

### Phase 3: Polish
- Performance optimization
- Visual refinement
- Testing with various fonts
- Documentation

## Testing Plan

### Unit Tests
- Blinka surface creation
- Font loading with Blinka
- Surface conversion (Blinka → pygame)

### Integration Tests
- Character grid rendering
- Glyph detail rendering
- Size switching
- Click detection

### Manual Tests
- Test with minimal font (10 chars)
- Test with comprehensive font (94+ chars)
- Test all sizes (12pt, 16pt, 20pt)
- Test interactions (clicks, size switching)
- Visual inspection of font rendering

## Future Considerations

### Possible Optimizations
- Cache rendered Blinka surfaces
- Only re-render Blinka parts when font changes
- Use dirty rect updates for pygame

### Potential Issues
- Blinka rendering performance (if slow, cache aggressively)
- Surface conversion overhead (benchmark and optimize)
- Font loading time (load on demand, show loading indicator)

### Enhancement Opportunities
- Side-by-side comparison: Multiple Blinka surfaces
- Animation: Smooth size transitions
- Export: Save Blinka-rendered images

## Success Criteria

- ✓ All UI features working smoothly
- ✓ Real PCF/BDF fonts displaying correctly via Blinka
- ✓ Performance acceptable (< 1s to switch sizes)
- ✓ No visual glitches
- ✓ Accurate representation of CircuitPython font rendering

## Questions Resolved

**Q**: Why not pure pygame?
**A**: Need to validate actual PCF/BDF rendering behavior for CircuitPython

**Q**: Why not pure Blinka?
**A**: displayio too limited for complex interactive UI

**Q**: Can we mix rendering approaches?
**A**: Yes! Blinka surfaces can be converted to pygame surfaces

**Q**: What about performance?
**A**: Blinka only renders small areas (grid + detail), rest is fast pygame

**Q**: Will this inform embedded development?
**A**: Yes! The font rendering is what matters, and that's using Blinka
