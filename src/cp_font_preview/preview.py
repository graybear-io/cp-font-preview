"""Font preview using hybrid pygame + Blinka approach."""

from pathlib import Path

import displayio
import pygame
import terminalio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from blinka_displayio_pygamedisplay import PyGameDisplay

from .layout import (
    BG_COLOR,
    BORDER_COLOR,
    BUTTON_ACTIVE,
    BUTTON_INACTIVE,
    CHAR_CELL_SIZE,
    HIGHLIGHT_COLOR,
    LEFT_PANEL_BG,
    LEFT_PANEL_WIDTH,
    METADATA_BG,
    METADATA_HEIGHT,
    PADDING,
    PANEL_HEIGHT,
    RIGHT_PANEL_BG,
    RIGHT_PANEL_WIDTH,
    SAMPLE_TEXTS,
    TEXT_COLOR,
    TEXT_SECONDARY,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


class FontPreview:
    """Preview a bitmap font in a pygame window with enhanced UI."""

    def __init__(
        self,
        font_path: str,
        characters: str,
        font_info: dict,
        width: int = WINDOW_WIDTH,
        height: int = WINDOW_HEIGHT,
    ):
        """Initialize the font preview window.

        Args:
            font_path: Path to PCF or BDF font file
            characters: String of characters to display
            font_info: Dictionary with font metadata
            width: Window width in pixels (default: 1200)
            height: Window height in pixels (default: 800)
        """
        self.font_path = Path(font_path)
        self.characters = characters
        self.font_info = font_info
        self.width = width
        self.height = height

        # State
        self.current_size_index = 0
        self.selected_char_index = 0
        self.available_sizes = font_info.get("sizes", [])
        self.font_files = {}  # Will map size -> path

        # State change tracking (dirty flags)
        self.dirty_flags = {
            "metadata": True,
            "sample_text": True,
            "character_grid": True,
            "glyph_detail": True,
        }
        self.force_full_redraw = True  # Force redraw on first frame

        # Cached rendered surfaces
        self.cached_surfaces = {
            "character_grid": None,
            "glyph_detail": None,
        }

        # UI elements
        self.screen: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None
        self.size_buttons: dict[int, pygame.Rect] = {}
        self.char_grid_positions: dict[str, pygame.Rect] = {}

        # Fonts for UI chrome (pygame system fonts)
        self.font_small: pygame.font.Font | None = None
        self.font_medium: pygame.font.Font | None = None
        self.font_large: pygame.font.Font | None = None
        self.font_huge: pygame.font.Font | None = None

        # Blinka font for PCF/BDF rendering (Phase 2)
        self.loaded_font = None  # adafruit_bitmap_font.BitmapFont
        self.font_loaded = False

    def initialize_pygame(self) -> bool:
        """Initialize pygame and create the window."""
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption(
                f"Font Preview - {self.font_info.get('font_family', 'Unknown')}"
            )
            self.clock = pygame.time.Clock()

            # Load system fonts for UI chrome
            self.font_small = pygame.font.SysFont("Arial", 14)
            self.font_medium = pygame.font.SysFont("Arial", 18)
            self.font_large = pygame.font.SysFont("Arial", 24)
            self.font_huge = pygame.font.SysFont("Arial", 72)

            return True
        except Exception as e:
            print(f"Error initializing pygame: {e}")
            return False

    def load_font(self, font_path: Path | str) -> bool:
        """Load a PCF or BDF font using Blinka.

        Args:
            font_path: Path to the PCF or BDF font file

        Returns:
            True if font loaded successfully, False otherwise
        """
        try:
            font_path = Path(font_path)
            if not font_path.exists():
                print(f"Font file not found: {font_path}")
                return False

            print(f"Loading font: {font_path}")
            self.loaded_font = bitmap_font.load_font(str(font_path))
            self.font_loaded = True
            print(f"Font loaded successfully: {font_path.name}")
            return True
        except Exception as e:
            print(f"Error loading font {font_path}: {e}")
            self.font_loaded = False
            return False

    def mark_dirty(self, *sections: str):
        """Mark one or more sections as needing redraw.

        Args:
            sections: Names of sections to mark dirty (metadata, sample_text,
                     character_grid, glyph_detail, or 'all' for everything)
        """
        for section in sections:
            if section == "all":
                for key in self.dirty_flags:
                    self.dirty_flags[key] = True
                self.force_full_redraw = True
            elif section in self.dirty_flags:
                self.dirty_flags[section] = True

    def needs_redraw(self) -> bool:
        """Check if any section needs redrawing."""
        return self.force_full_redraw or any(self.dirty_flags.values())

    def render_character_grid_surface(self) -> pygame.Surface | None:
        """Render the character grid using PCF/BDF fonts via Blinka.

        PHASE 2: Creates offscreen Blinka display, renders characters using
                adafruit_bitmap_font, and converts to pygame surface.

        Returns:
            pygame.Surface with rendered character grid, or None on error.
        """
        # Calculate grid dimensions
        chars_per_row = 16
        num_rows = (len(self.characters) + chars_per_row - 1) // chars_per_row

        # Limit rows to fit in panel
        max_rows = (PANEL_HEIGHT - 250) // CHAR_CELL_SIZE
        num_rows = min(num_rows, max_rows)

        grid_width = chars_per_row * CHAR_CELL_SIZE
        grid_height = num_rows * CHAR_CELL_SIZE

        # Clear old positions
        self.char_grid_positions.clear()

        # PHASE 2: Use Blinka if font is loaded, otherwise fallback to pygame
        if self.font_loaded and self.loaded_font:
            try:
                # Create offscreen Blinka display (hidden window)
                blinka_display = PyGameDisplay(
                    width=grid_width,
                    height=grid_height,
                    auto_refresh=False,
                    flags=pygame.HIDDEN,
                )

                # Create group for content
                group = displayio.Group()

                # Background
                bg_bitmap = displayio.Bitmap(grid_width, grid_height, 1)
                bg_palette = displayio.Palette(1)
                bg_palette[0] = (
                    (LEFT_PANEL_BG[0] << 16) | (LEFT_PANEL_BG[1] << 8) | LEFT_PANEL_BG[2]
                )
                bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
                group.append(bg_sprite)

                # Render each character
                for i, char in enumerate(self.characters[: chars_per_row * num_rows]):
                    if char == "\n":
                        continue

                    row = i // chars_per_row
                    col = i % chars_per_row

                    x = col * CHAR_CELL_SIZE + CHAR_CELL_SIZE // 2
                    y = row * CHAR_CELL_SIZE + CHAR_CELL_SIZE // 2

                    # Highlight selected character with Blinka
                    if i == self.selected_char_index:
                        hl_bitmap = displayio.Bitmap(CHAR_CELL_SIZE, CHAR_CELL_SIZE, 1)
                        hl_palette = displayio.Palette(1)
                        hl_palette[0] = (
                            (HIGHLIGHT_COLOR[0] << 16)
                            | (HIGHLIGHT_COLOR[1] << 8)
                            | HIGHLIGHT_COLOR[2]
                        )
                        hl_sprite = displayio.TileGrid(
                            hl_bitmap,
                            pixel_shader=hl_palette,
                            x=col * CHAR_CELL_SIZE,
                            y=row * CHAR_CELL_SIZE,
                        )
                        group.append(hl_sprite)

                    # Render character with Blinka
                    try:
                        char_label = label.Label(
                            self.loaded_font,
                            text=char,
                            color=(TEXT_COLOR[0] << 16) | (TEXT_COLOR[1] << 8) | TEXT_COLOR[2],
                        )
                        char_label.x = x
                        char_label.y = y
                        group.append(char_label)

                        # Store clickable region
                        char_rect = pygame.Rect(
                            col * CHAR_CELL_SIZE,
                            row * CHAR_CELL_SIZE,
                            CHAR_CELL_SIZE,
                            CHAR_CELL_SIZE,
                        )
                        self.char_grid_positions[char] = char_rect
                    except Exception:
                        # Character might not be in font
                        continue

                # Set root group and render
                blinka_display.root_group = group
                blinka_display.refresh()

                # Get the underlying pygame surface
                pygame_surface = blinka_display.display
                return pygame_surface.copy()

            except Exception as e:
                print(f"Error rendering character grid with Blinka: {e}")
                # Fall through to pygame fallback

        # FALLBACK: Use pygame system fonts if Blinka not available
        if not self.font_large:
            return None

        surface = pygame.Surface((grid_width, grid_height))
        surface.fill(LEFT_PANEL_BG)

        for i, char in enumerate(self.characters[: chars_per_row * num_rows]):
            if char == "\n":
                continue

            row = i // chars_per_row
            col = i % chars_per_row

            x = col * CHAR_CELL_SIZE
            y = row * CHAR_CELL_SIZE

            if i == self.selected_char_index:
                highlight_rect = pygame.Rect(x - 2, y - 2, CHAR_CELL_SIZE, CHAR_CELL_SIZE)
                pygame.draw.rect(surface, HIGHLIGHT_COLOR, highlight_rect)

            try:
                text_surf = self.font_large.render(char, True, TEXT_COLOR)
                text_rect = text_surf.get_rect(
                    center=(x + CHAR_CELL_SIZE // 2, y + CHAR_CELL_SIZE // 2)
                )
                surface.blit(text_surf, text_rect)
                char_rect = pygame.Rect(x, y, CHAR_CELL_SIZE, CHAR_CELL_SIZE)
                self.char_grid_positions[char] = char_rect
            except Exception:
                continue

        return surface

    def render_glyph_detail_surface(self, char: str) -> pygame.Surface | None:
        """Render a single large glyph using PCF/BDF fonts via Blinka.

        PHASE 2: Creates offscreen Blinka display, renders the glyph using
                adafruit_bitmap_font, and converts to pygame surface.

        Args:
            char: Character to render

        Returns:
            pygame.Surface with rendered glyph, or None on error.
        """
        box_size = 200

        # PHASE 2: Use Blinka if font is loaded, otherwise fallback to pygame
        if self.font_loaded and self.loaded_font:
            try:
                # Create offscreen Blinka display (hidden window)
                blinka_display = PyGameDisplay(
                    width=box_size,
                    height=box_size,
                    auto_refresh=False,
                    flags=pygame.HIDDEN,
                )

                # Create group for content
                group = displayio.Group()

                # Background
                bg_bitmap = displayio.Bitmap(box_size, box_size, 1)
                bg_palette = displayio.Palette(1)
                bg_palette[0] = (
                    (RIGHT_PANEL_BG[0] << 16) | (RIGHT_PANEL_BG[1] << 8) | RIGHT_PANEL_BG[2]
                )
                bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
                group.append(bg_sprite)

                # Render large character with Blinka
                try:
                    # Create label with the PCF/BDF font
                    glyph_label = label.Label(
                        self.loaded_font,
                        text=char,
                        color=(TEXT_COLOR[0] << 16) | (TEXT_COLOR[1] << 8) | TEXT_COLOR[2],
                        scale=3,  # Scale up for detail view
                    )
                    # Center in box
                    glyph_label.x = box_size // 2
                    glyph_label.y = box_size // 2
                    group.append(glyph_label)
                except Exception:
                    # Character might not be in font, add error message
                    pass

                # Set root group and render
                blinka_display.root_group = group
                blinka_display.refresh()

                # Get the underlying pygame surface
                pygame_surface = blinka_display.display.copy()

                # Draw bounding box on top using pygame
                pygame.draw.rect(pygame_surface, BORDER_COLOR, (0, 0, box_size, box_size), 2)

                return pygame_surface

            except Exception as e:
                print(f"Error rendering glyph with Blinka: {e}")
                # Fall through to pygame fallback

        # FALLBACK: Use pygame system fonts if Blinka not available
        if not self.font_huge:
            return None

        surface = pygame.Surface((box_size, box_size))
        surface.fill(RIGHT_PANEL_BG)

        # Draw bounding box
        pygame.draw.rect(surface, BORDER_COLOR, (0, 0, box_size, box_size), 2)

        # Render large character centered
        try:
            large_text = self.font_huge.render(char, True, TEXT_COLOR)
            text_rect = large_text.get_rect(center=(box_size // 2, box_size // 2))
            surface.blit(large_text, text_rect)
        except Exception:
            # Character might not render
            if self.font_small:
                error_text = self.font_small.render(
                    f"Cannot render '{char}'", True, (255, 100, 100)
                )
                error_rect = error_text.get_rect(center=(box_size // 2, box_size // 2))
                surface.blit(error_text, error_rect)

        return surface

    def draw_section_bg(self, x: int, y: int, width: int, height: int, color: tuple[int, int, int]):
        """Draw a colored background section."""
        if self.screen:
            pygame.draw.rect(self.screen, color, (x, y, width, height))

    def draw_metadata_section(self):
        """Draw the top metadata bar with font info and size selector."""
        if not self.screen or not self.font_medium or not self.font_small:
            return

        y = 0

        # Draw background
        self.draw_section_bg(0, y, self.width, METADATA_HEIGHT, METADATA_BG)

        # Font info text
        family = self.font_info.get("font_family", "Unknown")
        char_count = self.font_info.get("character_count", len(self.characters))
        font_format = self.font_path.suffix.upper().lstrip(".")

        info_text = f"Font: {family}  |  Characters: {char_count}  |  Format: {font_format}"
        text_surface = self.font_medium.render(info_text, True, TEXT_COLOR)
        self.screen.blit(text_surface, (PADDING * 2, 20))

        # Size selector buttons
        if self.available_sizes:
            x_start = 600
            btn_width = 70
            btn_height = 30
            btn_spacing = 80
            self.size_buttons.clear()

            for i, size in enumerate(self.available_sizes):
                x = x_start + (i * btn_spacing)
                y_btn = 15

                # Button background
                is_active = i == self.current_size_index
                color = BUTTON_ACTIVE if is_active else BUTTON_INACTIVE
                btn_rect = pygame.Rect(x, y_btn, btn_width, btn_height)
                pygame.draw.rect(self.screen, color, btn_rect)
                pygame.draw.rect(self.screen, TEXT_COLOR, btn_rect, 1)

                # Button text
                btn_text = f"{size}pt"
                text_surf = self.font_small.render(btn_text, True, TEXT_COLOR)
                text_rect = text_surf.get_rect(center=(x + btn_width // 2, y_btn + btn_height // 2))
                self.screen.blit(text_surf, text_rect)

                # Store clickable region
                self.size_buttons[size] = btn_rect

            # Instructions - positioned after the last button
            inst_x = x_start + (len(self.available_sizes) * btn_spacing) + 10
            inst_text = "← Click size to switch"
            text_surf = self.font_small.render(inst_text, True, TEXT_SECONDARY)
            self.screen.blit(text_surf, (inst_x, 25))

    def draw_sample_text_section(self):
        """Draw sample text strings in the left panel."""
        if not self.screen or not self.font_medium:
            return

        x = PADDING * 2
        y = METADATA_HEIGHT + PADDING * 2

        # Section label
        label_surf = self.font_medium.render("Sample Text:", True, TEXT_COLOR)
        self.screen.blit(label_surf, (x, y))
        y += 35

        # Get current size for display
        current_size = (
            self.available_sizes[self.current_size_index] if self.available_sizes else "N/A"
        )

        # Render sample texts
        samples = list(SAMPLE_TEXTS)
        samples.append(f"Current size: {current_size}pt")

        for sample in samples:
            text_surf = self.font_medium.render(sample, True, TEXT_COLOR)
            self.screen.blit(text_surf, (x, y))
            y += 25

    def draw_character_grid(self):
        """Draw the interactive character grid in the left panel."""
        if not self.screen or not self.font_medium:
            return

        x_start = PADDING * 2
        y_start = METADATA_HEIGHT + 220

        # Section label
        label_surf = self.font_medium.render("Character Grid (click to select):", True, TEXT_COLOR)
        self.screen.blit(label_surf, (x_start, y_start))
        y_start += 30

        # Re-render grid surface if dirty
        if self.dirty_flags["character_grid"] or self.cached_surfaces["character_grid"] is None:
            self.cached_surfaces["character_grid"] = self.render_character_grid_surface()
            self.dirty_flags["character_grid"] = False

        # Blit cached surface to screen
        if self.cached_surfaces["character_grid"]:
            self.screen.blit(self.cached_surfaces["character_grid"], (x_start, y_start))

    def draw_glyph_detail_section(self):
        """Draw the glyph detail view in the right panel."""
        if not self.screen or not self.font_small:
            return

        x_start = LEFT_PANEL_WIDTH + PADDING * 2
        y_start = METADATA_HEIGHT + PADDING * 2

        # Section label
        label_surf = self.font_medium.render("Glyph Detail:", True, TEXT_COLOR)
        self.screen.blit(label_surf, (x_start, y_start))
        y_start += 35

        # Get selected character
        if 0 <= self.selected_char_index < len(self.characters):
            selected_char = self.characters[self.selected_char_index]

            # Character info
            info_lines = [
                f"Character: '{selected_char}'",
                f"Unicode: U+{ord(selected_char):04X}",
                f"Decimal: {ord(selected_char)}",
                "",
            ]

            y = y_start
            for line in info_lines:
                if line:
                    text_surf = self.font_small.render(line, True, TEXT_COLOR)
                    self.screen.blit(text_surf, (x_start, y))
                y += 20

            # Re-render glyph surface if dirty
            if self.dirty_flags["glyph_detail"] or self.cached_surfaces["glyph_detail"] is None:
                self.cached_surfaces["glyph_detail"] = self.render_glyph_detail_surface(
                    selected_char
                )
                self.dirty_flags["glyph_detail"] = False

            # Blit cached surface to screen
            if self.cached_surfaces["glyph_detail"]:
                box_x = x_start + 120
                box_y = y + 10
                self.screen.blit(self.cached_surfaces["glyph_detail"], (box_x, box_y))

                # Get glyph dimensions from cached surface (approximate)
                # In Phase 2, we'll get accurate dimensions from Blinka
                box_size = 200
                y = box_y + box_size + 20
                dims_text = f"Rendered in {box_size}×{box_size}px box"
                text_surf = self.font_small.render(dims_text, True, TEXT_SECONDARY)
                self.screen.blit(text_surf, (x_start, y))

    def draw_all(self):
        """Draw the complete UI."""
        if not self.screen:
            return

        # Background
        self.screen.fill(BG_COLOR)

        # Panel backgrounds
        self.draw_section_bg(0, METADATA_HEIGHT, LEFT_PANEL_WIDTH, PANEL_HEIGHT, LEFT_PANEL_BG)
        self.draw_section_bg(
            LEFT_PANEL_WIDTH, METADATA_HEIGHT, RIGHT_PANEL_WIDTH, PANEL_HEIGHT, RIGHT_PANEL_BG
        )

        # Draw all sections
        self.draw_metadata_section()
        self.draw_sample_text_section()
        self.draw_character_grid()
        self.draw_glyph_detail_section()

        # Update display
        pygame.display.flip()

    def handle_size_change(self, new_size_index: int):
        """Handle font size change event.

        Args:
            new_size_index: Index of the new size in available_sizes
        """
        if new_size_index != self.current_size_index and 0 <= new_size_index < len(
            self.available_sizes
        ):
            self.current_size_index = new_size_index
            new_size = self.available_sizes[new_size_index]
            print(f"Size changed to {new_size}pt")

            # Mark affected sections as dirty
            self.mark_dirty("metadata", "character_grid", "glyph_detail", "sample_text")

            # PHASE 2: Reload font file for new size (if mapping available)
            font_path = self.font_files.get(new_size)
            if font_path:
                self.load_font(font_path)
                # Invalidate cached surfaces
                self.cached_surfaces["character_grid"] = None
                self.cached_surfaces["glyph_detail"] = None
            else:
                print("  Note: Font files mapping not available, keeping current font")

    def handle_character_selection(self, char_index: int):
        """Handle character selection event.

        Args:
            char_index: Index of the character in self.characters
        """
        if char_index != self.selected_char_index and 0 <= char_index < len(self.characters):
            self.selected_char_index = char_index
            char = self.characters[char_index]
            print(f"Character selected: '{char}' (U+{ord(char):04X})")

            # Mark affected sections as dirty
            self.mark_dirty("character_grid", "glyph_detail")

    def handle_font_reload(self):
        """Handle font file reload event (for watch mode).

        This is called when the font file changes on disk.
        """
        print("Font file changed, reloading...")

        # Mark all sections as dirty
        self.mark_dirty("all")

        # Invalidate cached surfaces
        self.cached_surfaces["character_grid"] = None
        self.cached_surfaces["glyph_detail"] = None

        # PHASE 2: Reload font from disk
        self.load_font(self.font_path)

    def handle_click(self, pos: tuple[int, int]) -> bool:
        """Handle mouse click events.

        Args:
            pos: (x, y) position of the click

        Returns:
            True if the click triggered an action, False otherwise
        """
        # Check size buttons
        for size, rect in self.size_buttons.items():
            if rect.collidepoint(pos):
                # Find the index of this size
                try:
                    new_index = self.available_sizes.index(size)
                    self.handle_size_change(new_index)
                    return True
                except ValueError:
                    pass

        # Check character grid (adjust for grid position offset)
        grid_x_offset = PADDING * 2
        grid_y_offset = METADATA_HEIGHT + 250

        for char, rect in self.char_grid_positions.items():
            # Adjust rect position to screen coordinates
            screen_rect = rect.copy()
            screen_rect.x += grid_x_offset
            screen_rect.y += grid_y_offset

            if screen_rect.collidepoint(pos):
                # Find the actual index in self.characters
                try:
                    char_index = self.characters.index(char)
                    self.handle_character_selection(char_index)
                    return True
                except ValueError:
                    pass

        return False

    def run(self, watch_callback=None):
        """Run the preview window with event-driven rendering.

        Args:
            watch_callback: Optional function to check for updates
        """
        if not self.initialize_pygame():
            return

        # PHASE 2: Load the PCF/BDF font
        print(f"\nPreviewing: {self.font_path}")
        # TODO: Fix Blinka integration - PyGameDisplay creates conflicting windows
        # self.load_font(self.font_path)
        print("Note: Using pygame fallback rendering (Blinka integration needs architectural fix)")

        print(f"Font: {self.font_info.get('font_family', 'Unknown')}")
        print(f"Characters: {self.font_info.get('character_count', len(self.characters))}")
        print(f"Sizes: {self.available_sizes}")
        print(f"Using Blinka rendering: {self.font_loaded}")
        print("\nControls:")
        print("  - Click size buttons to switch between font sizes")
        print("  - Click any character in the grid to inspect it")
        print("  - Close window to exit\n")

        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            # Check for updates if watch mode is enabled
            if watch_callback and watch_callback():
                self.handle_font_reload()

            # Only redraw if something changed (event-driven rendering)
            if self.needs_redraw():
                self.draw_all()
                self.force_full_redraw = False

            # Cap at 60 FPS (but only actually draws when needed)
            if self.clock:
                self.clock.tick(60)

        self.close()

    def close(self):
        """Clean up resources."""
        pygame.quit()


def preview_font(
    font_path: str,
    characters: str,
    font_info: dict,
    width: int = WINDOW_WIDTH,
    height: int = WINDOW_HEIGHT,
):
    """Convenience function to preview a font.

    Args:
        font_path: Path to font file
        characters: Characters to display
        font_info: Font metadata
        width: Window width
        height: Window height
    """
    preview = FontPreview(font_path, characters, font_info, width, height)
    try:
        preview.run()
    finally:
        preview.close()


def preview_font_blinka(
    font_path: str,
    characters: str,
    font_info: dict,
    width: int = WINDOW_WIDTH,
    height: int = WINDOW_HEIGHT,
):
    """Non-interactive Blinka preview showing actual PCF/BDF rendering.

    This mode creates a single PyGameDisplay window with Blinka rendering
    to show how fonts actually appear on CircuitPython hardware.

    Args:
        font_path: Path to PCF or BDF font file
        characters: String of characters to display
        font_info: Font metadata dictionary
        width: Window width (default: 1200)
        height: Window height (default: 800)
    """
    import time
    from pathlib import Path

    font_path = Path(font_path)
    print("\nBlinka Preview Mode")
    print(f"Font: {font_info.get('font_family', 'Unknown')}")
    print(f"Path: {font_path}")
    print(f"Characters: {len(characters)} total")
    print("\nRendering with actual PCF/BDF bitmap font...")
    print("Close window to exit\n")

    try:
        # Load font
        loaded_font = bitmap_font.load_font(str(font_path))

        # Create display
        display = PyGameDisplay(width=width, height=height)
        display.auto_refresh = True

        # Create group
        group = displayio.Group()

        # Background
        bg_bitmap = displayio.Bitmap(width, height, 1)
        bg_palette = displayio.Palette(1)
        bg_palette[0] = 0x222222  # Dark gray
        bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
        group.append(bg_sprite)

        # Title (use baseline font for UI elements)
        title_text = f"{font_info.get('font_family', 'Font')} - Blinka Preview"
        title_label = label.Label(terminalio.FONT, text=title_text[:40], color=0xFFFFFF)
        title_label.x = 20
        title_label.y = 30
        group.append(title_label)

        # Render characters in grid
        chars_per_row = 32
        cell_size = 30
        start_x = 20
        start_y = 80

        for i, char in enumerate(characters[:256]):  # Limit to 256 chars
            if char == "\n":
                continue

            row = i // chars_per_row
            col = i % chars_per_row

            x = start_x + (col * cell_size)
            y = start_y + (row * cell_size)

            # Check bounds
            if y > height - cell_size:
                break

            try:
                char_label = label.Label(loaded_font, text=char, color=0xFFFFFF)
                char_label.x = x
                char_label.y = y
                group.append(char_label)
            except Exception:
                # Character might not be in font
                continue

        # Set root group and display
        display.root_group = group
        display.refresh()

        # Event loop
        while True:
            if display.check_quit():
                break
            display.refresh()
            time.sleep(0.01)

    except Exception as e:
        print(f"Error in Blinka preview: {e}")
        raise
