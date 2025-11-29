"""Font preview using displayio and pygame."""

import time
from pathlib import Path

import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from blinka_displayio_pygamedisplay import PyGameDisplay


class FontPreview:
    """Preview a bitmap font in a pygame window."""

    def __init__(
        self, font_path: str, characters: str, font_info: dict, width: int = 800, height: int = 600
    ):
        """Initialize the font preview window.

        Args:
            font_path: Path to PCF or BDF font file
            characters: String of characters to display
            font_info: Dictionary with font metadata
            width: Window width in pixels
            height: Window height in pixels
        """
        self.font_path = Path(font_path)
        self.characters = characters
        self.font_info = font_info
        self.width = width
        self.height = height
        self.display: PyGameDisplay | None = None
        self.main_group: displayio.Group | None = None

    def create_display(self):
        """Create the pygame display and displayio groups."""
        self.display = PyGameDisplay(width=self.width, height=self.height)
        self.main_group = displayio.Group()

        # Load the font
        try:
            font = bitmap_font.load_font(str(self.font_path))
        except Exception as e:
            print(f"Error loading font: {e}")
            return False

        # Add title
        title_text = (
            f"{self.font_info['font_family']} - {self.font_info['character_count']} characters"
        )
        title = label.Label(font, text=title_text, color=0xFFFFFF, scale=1)
        title.x = 10
        title.y = 15
        if self.main_group is not None:
            self.main_group.append(title)

        # Display characters in a grid
        chars_per_row = 16
        x_spacing = 40
        y_spacing = 40
        start_y = 50

        for i, char in enumerate(self.characters):
            if char == "\n":  # Skip newlines
                continue

            row = i // chars_per_row
            col = i % chars_per_row

            x = 10 + (col * x_spacing)
            y = start_y + (row * y_spacing)

            # Skip if we're off the bottom of the screen
            if y > self.height - 40:
                break

            try:
                char_label = label.Label(font, text=char, color=0xFFFFFF)
                char_label.x = x
                char_label.y = y
                if self.main_group is not None:
                    self.main_group.append(char_label)
            except Exception as e:
                # Character might not be in font, skip it
                print(f"Warning: Could not display character '{char}': {e}")
                continue

        if self.display is not None and self.main_group is not None:
            self.display.root_group = self.main_group
        return True

    def run(self, watch_callback=None):
        """Run the preview window.

        Args:
            watch_callback: Optional function to check for updates
        """
        if not self.create_display():
            return

        print(f"\nPreviewing: {self.font_path}")
        print(f"Font: {self.font_info['font_family']}")
        print(f"Characters: {self.font_info['character_count']}")
        print(f"Sizes: {self.font_info['sizes']}")
        print("\nClose window to exit\n")

        while True:
            if self.display is not None and self.display.check_quit():
                break

            # Check for updates if watch mode is enabled
            if watch_callback and watch_callback():
                print("Font updated! Reloading...")
                self.main_group = None
                if not self.create_display():
                    break

            time.sleep(0.01)

    def close(self):
        """Clean up resources."""
        if self.display:
            self.display = None


def preview_font(
    font_path: str, characters: str, font_info: dict, width: int = 800, height: int = 600
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
