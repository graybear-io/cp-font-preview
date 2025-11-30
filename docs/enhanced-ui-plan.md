# Enhanced UI Plan for cp-font-preview

## Overview

**Goal**: Transform the simple character grid preview into a comprehensive font testing tool

**Current State**:
- Simple title showing font family and character count
- Character grid (16 per row)
- Basic pygame window

**Target State**:
- Multi-section layout with metadata, sample text, character grid, and glyph detail
- Size selector to switch between generated sizes
- Interactive character selection
- Bounding box visualization

---

## Proposed Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ Font Metadata Section (Top, full width)                            │
│ Family: comprehensive-test  |  Chars: 94  |  Sizes: [12] 16 20     │
├──────────────────────────────────┬──────────────────────────────────┤
│ Sample Text (Left, 60%)          │ Glyph Detail (Right, 40%)        │
│                                  │                                  │
│ "The quick brown fox..."         │ Selected: 'A'                    │
│ "0123456789"                     │ Unicode: U+0041                  │
│ "Price: $49.99"                  │                                  │
│ "!@#$%^&*()"                     │ ┌──────────────────────┐         │
│                                  │ │                      │         │
│ Character Grid (Below)           │ │        [A]           │         │
│ ┌──────────────────────────┐    │ │                      │         │
│ │ ! " # $ % & ' ( ) * + ,  │    │ └──────────────────────┘         │
│ │ - . / 0 1 2 3 4 5 6 7 8  │    │                                  │
│ │ 9 : ; < = > ? @ A B C D  │    │ Bounds: 8w x 12h                 │
│ │ ... (scrollable)          │    │ Click any character to inspect  │
│ └──────────────────────────┘    │                                  │
└──────────────────────────────────┴──────────────────────────────────┘
```

**Dimensions**:
- Window: 1200x800 (expanded from 800x600)
- Metadata bar: Full width x 60px
- Left panel: 720px x 740px
- Right panel: 480px x 740px

---

## Implementation Phases

### Phase 1: Layout Restructure
**Goal**: Organize the display into distinct sections

**Tasks**:
1. Create section constants (positions, sizes)
2. Refactor `create_display()` to use section-based layout
3. Add background rectangles for each section
4. Move character grid to left panel only
5. Add section labels/headers

**Files to modify**:
- `src/cp_font_preview/preview.py`

**Success criteria**:
- Display shows distinct sections
- Character grid constrained to left panel
- Clean visual separation

---

### Phase 2: Font Metadata Display
**Goal**: Show comprehensive font information at the top

**Tasks**:
1. Extract all metadata from manifest (family, char count, sizes, formats)
2. Create metadata label with formatted text
3. Position at top of window
4. Style for readability

**Data to display**:
- Font family name
- Character count
- Available sizes (highlight current)
- Format (PCF/BDF)
- Source font path (truncated)

**Success criteria**:
- All metadata visible and readable
- Updates when font changes (watch mode)

---

### Phase 3: Size Selector
**Goal**: Allow switching between generated font sizes

**Tasks**:
1. Parse available sizes from manifest
2. Create size selector UI (buttons or clickable text)
3. Add mouse click detection for size buttons
4. Reload font when size changes
5. Highlight current size

**Technical approach**:
- Use pygame mouse events (`MOUSEBUTTONDOWN`)
- Store clickable regions for each size button
- Reload font file based on selected size

**Success criteria**:
- Can click to switch sizes
- Font reloads correctly
- Current size visually indicated

---

### Phase 4: Sample Text Renderer
**Goal**: Display realistic text samples in the left panel

**Tasks**:
1. Define sample text strings (pangrams, numbers, symbols)
2. Create text rendering function
3. Position sample text in left panel (above grid)
4. Allow scrolling if needed

**Sample texts**:
```python
SAMPLE_TEXTS = [
    "The quick brown fox jumps over the lazy dog",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "abcdefghijklmnopqrstuvwxyz",
    "0123456789",
    "!@#$%^&*()_+-=[]{}|;:',.<>?/",
    "Price: $19.99",
    "Temperature: 72°F",
]
```

**Success criteria**:
- Multiple sample texts displayed
- Text wraps or truncates properly
- Updates when size changes

---

### Phase 5: Character Grid Refinement
**Goal**: Make character grid interactive and visually improved

**Tasks**:
1. Add visual feedback on hover (if possible with displayio)
2. Make characters clickable
3. Highlight selected character
4. Optimize grid layout for available space

**Technical approach**:
- Track mouse position
- Calculate which character is under cursor
- Store selected character index
- Add highlight indicator

**Success criteria**:
- Can click on characters
- Selected character visually highlighted
- Grid fits in left panel properly

---

### Phase 6: Glyph Detail View
**Goal**: Show detailed information about selected character

**Tasks**:
1. Create glyph detail section in right panel
2. Show selected character enlarged
3. Draw bounding box around glyph
4. Display character metadata (unicode, dimensions)
5. Calculate and show glyph bounds

**Information to display**:
- Character itself (enlarged)
- Unicode code point (U+XXXX)
- Glyph dimensions (width x height in pixels)
- Bounding box visualization
- Character name (optional - requires unicode database)

**Technical approach**:
- Get glyph bitmap from font
- Scale up for visibility (2x or 3x)
- Draw bounding rectangle
- Calculate actual glyph bounds

**Success criteria**:
- Selected character shown large
- Bounding box visible
- Metadata accurate
- Updates when selection changes

---

### Phase 7: Polish & Testing
**Goal**: Refine UX and test edge cases

**Tasks**:
1. Add keyboard navigation (arrow keys to navigate grid)
2. Improve visual styling (colors, spacing)
3. Add help text / instructions
4. Test with various font sizes
5. Test with minimal and comprehensive fonts
6. Test watch mode with new layout
7. Performance optimization

**Edge cases to test**:
- Font with very few characters
- Font with many characters (scrolling)
- Very small font sizes (readability)
- Very large font sizes (scaling)
- Fonts missing certain glyphs

**Success criteria**:
- Smooth user experience
- All features work across font variations
- No visual glitches
- Acceptable performance

---

## Technical Considerations

### displayio Constraints
- **Limited interactivity**: displayio/Blinka doesn't have native click handlers
- **Solution**: Use pygame event handling directly
- **Mouse events**: Access via `display._display.get_event()` or similar

### Font Rendering
- **Bitmap fonts**: PCF/BDF don't scale well
- **Glyph bounds**: May need to parse font file directly
- **Solution**: Use fontTools library for glyph introspection

### Layout Management
- **Fixed positions**: displayio uses absolute positioning
- **Solution**: Calculate positions based on window size
- **Responsive**: Support different window sizes

### State Management
- **Current state**: Only font_path and characters
- **New state needed**:
  - Selected size index
  - Selected character index
  - Current font object
  - Clickable regions

---

## Code Structure Changes

### New Methods for FontPreview class:

```python
class FontPreview:
    def __init__(self, ...):
        # Add new state
        self.current_size_index = 0
        self.selected_char_index = 0
        self.available_sizes = []
        self.font_files = {}  # size -> path mapping
        self.clickable_regions = {}  # name -> (x, y, w, h)

    def create_metadata_section(self):
        """Create font metadata display at top."""
        pass

    def create_size_selector(self):
        """Create size selection buttons."""
        pass

    def create_sample_text_section(self):
        """Render sample text strings."""
        pass

    def create_character_grid(self):
        """Create interactive character grid (left panel)."""
        pass

    def create_glyph_detail_section(self):
        """Create glyph detail view (right panel)."""
        pass

    def handle_mouse_click(self, pos):
        """Handle mouse click events."""
        pass

    def handle_keyboard(self, key):
        """Handle keyboard navigation."""
        pass

    def switch_size(self, size_index):
        """Load and display different font size."""
        pass

    def select_character(self, char_index):
        """Update glyph detail view for selected character."""
        pass
```

### New Utility Module:

Create `src/cp_font_preview/layout.py`:
```python
"""Layout constants and utilities."""

# Section definitions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

METADATA_HEIGHT = 60
LEFT_PANEL_WIDTH = 720
RIGHT_PANEL_WIDTH = 480

# Colors
BG_COLOR = 0x222222
PANEL_BG_COLOR = 0x2A2A2A
TEXT_COLOR = 0xFFFFFF
HIGHLIGHT_COLOR = 0x4A9EFF
BORDER_COLOR = 0x444444

# Spacing
PADDING = 10
SECTION_GAP = 20
```

---

## Future Enhancements (Post-MVP)

1. **Export functionality**: Save preview as PNG
2. **Compare mode**: Show multiple sizes side-by-side
3. **Custom sample text**: User input for testing specific strings
4. **Font metrics**: Show baseline, ascent, descent
5. **Coverage analysis**: Highlight which characters are missing
6. **Kerning visualization**: Show character spacing
7. **Animation**: Smooth transitions between sizes

---

## Testing Plan

### Manual Testing Checklist
- [ ] Metadata displays correctly
- [ ] Size selector works and updates font
- [ ] Sample text renders for all sizes
- [ ] Character grid is interactive
- [ ] Glyph detail shows correct information
- [ ] Bounding box is accurate
- [ ] Watch mode works with new layout
- [ ] Keyboard navigation works
- [ ] Works with minimal font (10 chars)
- [ ] Works with comprehensive font (94+ chars)
- [ ] Performance is acceptable

### Automated Tests
- Unit tests for layout calculations
- Tests for size switching logic
- Tests for character selection logic
- Integration tests for full preview workflow

---

## Timeline Estimate

- **Phase 1** (Layout): ~2 hours
- **Phase 2** (Metadata): ~1 hour
- **Phase 3** (Size Selector): ~2 hours
- **Phase 4** (Sample Text): ~1 hour
- **Phase 5** (Grid Refinement): ~2 hours
- **Phase 6** (Glyph Detail): ~3 hours
- **Phase 7** (Polish): ~2 hours

**Total**: ~13 hours of development

---

## Questions to Resolve

1. Should we support window resizing?
2. How to handle fonts with 200+ characters? (pagination/scrolling)
3. Should glyph detail show multiple characters at once?
4. Do we need export functionality in v1?
5. Should we support BDF and PCF simultaneously or one at a time?

---

## Success Metrics

1. **Functionality**: All planned features working
2. **Usability**: Easy to test fonts visually
3. **Performance**: < 1 second to switch sizes
4. **Reliability**: No crashes with various fonts
5. **Code Quality**: Well-tested, maintainable code
