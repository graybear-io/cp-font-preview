#!/usr/bin/env python3
"""Test if BDF fonts render."""

import displayio
from blinka_displayio_pygamedisplay import PyGameDisplay
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import time

# Create display
display = PyGameDisplay(width=800, height=600)
display.auto_refresh = True

# Create group
group = displayio.Group()

# Add background
color_bitmap = displayio.Bitmap(800, 600, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x222222  # Dark gray
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
group.append(bg_sprite)

# Try loading the BDF font
font_path = "/Users/bear/cp-projects/cp-font-gen/output/digits/digits-16pt.bdf"
print(f"Loading BDF font: {font_path}")
font = bitmap_font.load_font(font_path)
print(f"Font loaded: {font}")

# Create a simple label
text_label = label.Label(font, text="BDF: 0123456789", color=0xFFFFFF)
text_label.x = 50
text_label.y = 100
print(f"Label created at ({text_label.x}, {text_label.y})")
group.append(text_label)

# Set root group and refresh
display.root_group = group
display.refresh()

print(f"\nIf you see 'BDF: 0123456789' in white text, BDF fonts work!")
print("Close window to exit...")

# Event loop
while True:
    if display.check_quit():
        break
    display.refresh()
    time.sleep(0.01)
