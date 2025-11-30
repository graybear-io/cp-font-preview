"""Font preview using hybrid pygame + Blinka approach."""

import time
from pathlib import Path

import pygame

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

    def draw_section_bg(
        self, x: int, y: int, width: int, height: int, color: tuple[int, int, int]
    ):
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
                text_rect = text_surf.get_rect(
                    center=(x + btn_width // 2, y_btn + btn_height // 2)
                )
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
            self.available_sizes[self.current_size_index]
            if self.available_sizes
            else "N/A"
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
        if not self.screen or not self.font_large:
            return

        x_start = PADDING * 2
        y_start = METADATA_HEIGHT + 220

        # Section label
        label_surf = self.font_medium.render(
            "Character Grid (click to select):", True, TEXT_COLOR
        )
        self.screen.blit(label_surf, (x_start, y_start))
        y_start += 30

        # Character grid
        chars_per_row = 16
        self.char_grid_positions.clear()

        for i, char in enumerate(self.characters):
            if char == "\n":  # Skip newlines
                continue

            row = i // chars_per_row
            col = i % chars_per_row

            x = x_start + (col * CHAR_CELL_SIZE)
            y = y_start + (row * CHAR_CELL_SIZE)

            # Check if we're still in the left panel bounds
            if y > METADATA_HEIGHT + PANEL_HEIGHT - CHAR_CELL_SIZE:
                break

            # Highlight selected character
            if i == self.selected_char_index:
                highlight_rect = pygame.Rect(
                    x - 2, y - 2, CHAR_CELL_SIZE, CHAR_CELL_SIZE
                )
                pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, highlight_rect)

            # Draw character
            try:
                text_surf = self.font_large.render(char, True, TEXT_COLOR)
                text_rect = text_surf.get_rect(
                    center=(x + CHAR_CELL_SIZE // 2, y + CHAR_CELL_SIZE // 2)
                )
                self.screen.blit(text_surf, text_rect)

                # Store clickable region
                char_rect = pygame.Rect(x, y, CHAR_CELL_SIZE, CHAR_CELL_SIZE)
                self.char_grid_positions[char] = char_rect
            except Exception:
                # Character might not render, skip it
                continue

    def draw_glyph_detail_section(self):
        """Draw the glyph detail view in the right panel."""
        if not self.screen or not self.font_small or not self.font_huge:
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

            # Large character with bounding box
            box_y = y + 10
            box_size = 200
            box_x = x_start + 120

            # Draw bounding box
            box_rect = pygame.Rect(box_x, box_y, box_size, box_size)
            pygame.draw.rect(self.screen, BORDER_COLOR, box_rect, 2)

            # Draw large character centered in box
            try:
                large_text = self.font_huge.render(selected_char, True, TEXT_COLOR)
                text_rect = large_text.get_rect(
                    center=(box_x + box_size // 2, box_y + box_size // 2)
                )
                self.screen.blit(large_text, text_rect)

                # Glyph dimensions
                glyph_width, glyph_height = large_text.get_size()

                y = box_y + box_size + 20
                dims_text = f"Rendered size: {glyph_width}w × {glyph_height}h"
                text_surf = self.font_small.render(dims_text, True, TEXT_COLOR)
                self.screen.blit(text_surf, (x_start, y))
            except Exception:
                # Character might not render
                error_text = f"Cannot render '{selected_char}'"
                text_surf = self.font_small.render(error_text, True, (255, 100, 100))
                self.screen.blit(text_surf, (x_start, box_y + box_size // 2))

    def draw_all(self):
        """Draw the complete UI."""
        if not self.screen:
            return

        # Background
        self.screen.fill(BG_COLOR)

        # Panel backgrounds
        self.draw_section_bg(
            0, METADATA_HEIGHT, LEFT_PANEL_WIDTH, PANEL_HEIGHT, LEFT_PANEL_BG
        )
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
                    if new_index != self.current_size_index:
                        self.current_size_index = new_index
                        print(f"Switched to {size}pt (index {new_index})")
                        # TODO: In Phase 2, reload the actual font file here
                        return True
                except ValueError:
                    pass

        # Check character grid
        for char, rect in self.char_grid_positions.items():
            if rect.collidepoint(pos):
                # Find the actual index in self.characters
                try:
                    char_index = self.characters.index(char)
                    if char_index != self.selected_char_index:
                        self.selected_char_index = char_index
                        print(f"Selected character: '{char}' (U+{ord(char):04X})")
                        return True
                except ValueError:
                    pass

        return False

    def run(self, watch_callback=None):
        """Run the preview window.

        Args:
            watch_callback: Optional function to check for updates
        """
        if not self.initialize_pygame():
            return

        print(f"\nPreviewing: {self.font_path}")
        print(f"Font: {self.font_info.get('font_family', 'Unknown')}")
        print(f"Characters: {self.font_info.get('character_count', len(self.characters))}")
        print(f"Sizes: {self.available_sizes}")
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
                elif event.type == pygame.MOUSEBUTTONDOWN and self.handle_click(event.pos):
                    # Redraw on interaction
                    pass

            # Check for updates if watch mode is enabled
            if watch_callback and watch_callback():
                print("Font updated! Reloading...")
                # TODO: Implement font reloading in Phase 2

            # Draw everything
            self.draw_all()

            # Cap at 60 FPS
            if self.clock:
                self.clock.tick(60)

            time.sleep(0.01)

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
