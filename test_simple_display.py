#!/usr/bin/env python3
"""Simple test to see if displayio text rendering works at all."""

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

# Try loading the PCF font
font_path = "/Users/bear/cp-projects/cp-font-gen/output/digits/digits-16pt.pcf"
print(f"Loading font: {font_path}")
font = bitmap_font.load_font(font_path)
print(f"Font loaded: {font}")

# Create a simple label
text_label = label.Label(font, text="0123", color=0xFFFFFF)
text_label.x = 100
text_label.y = 100
print(f"Label created: {text_label}")
print(f"Label position: ({text_label.x}, {text_label.y})")
print(f"Label color: {text_label.color}")
print(f"Label text: '{text_label.text}'")
group.append(text_label)

# Set root group and refresh
display.root_group = group
display.refresh()

print(f"\nGroup has {len(group)} items")
print("Display setup complete. Window should show dark gray background and '0123' text.")
print("If you only see dark gray, the bitmap font isn't rendering.")
print("\nClose window to exit...")

# Event loop
while True:
    if display.check_quit():
        break
    display.refresh()
    time.sleep(0.01)
