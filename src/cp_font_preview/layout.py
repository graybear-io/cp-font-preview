"""Layout constants and utilities for the enhanced UI."""

# Window dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Section heights and widths
METADATA_HEIGHT = 60
LEFT_PANEL_WIDTH = 720
RIGHT_PANEL_WIDTH = 480
PANEL_HEIGHT = WINDOW_HEIGHT - METADATA_HEIGHT  # 740

# Colors (RGB tuples for pygame)
BG_COLOR = (34, 34, 34)  # 0x222222
METADATA_BG = (51, 51, 51)  # 0x333333
LEFT_PANEL_BG = (42, 42, 42)  # 0x2A2A2A
RIGHT_PANEL_BG = (46, 46, 46)  # 0x2E2E2E
TEXT_COLOR = (255, 255, 255)  # 0xFFFFFF
TEXT_SECONDARY = (180, 180, 180)  # Lighter gray for secondary text
BUTTON_INACTIVE = (68, 68, 68)  # 0x444444
BUTTON_ACTIVE = (74, 158, 255)  # 0x4A9EFF
BORDER_COLOR = (255, 0, 0)  # Red for bounding boxes
HIGHLIGHT_COLOR = (74, 158, 255)  # 0x4A9EFF

# Spacing and padding
PADDING = 10
SECTION_GAP = 20
CHAR_CELL_SIZE = 40  # Width and height for character grid cells

# Sample text strings
SAMPLE_TEXTS = [
    "The quick brown fox jumps over the lazy dog",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "abcdefghijklmnopqrstuvwxyz",
    "0123456789",
    "!@#$%^&*()_+-=[]{}|;:',.<>?/",
    "Price: $19.99",
]
