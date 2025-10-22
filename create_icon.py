#!/usr/bin/env python3
"""
Create a cool icon for BattleGame
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create a 1024x1024 image (high res for icon)
size = 1024
img = Image.new('RGB', (size, size), color='#1a1a2e')

draw = ImageDraw.Draw(img)

# Draw a cool gradient background
for i in range(size):
    color_value = int(26 + (i / size) * 40)
    draw.line([(0, i), (size, i)], fill=(color_value, color_value, color_value + 20))

# Draw a large star burst effect
center = size // 2
for angle in range(0, 360, 15):
    import math
    rad = math.radians(angle)
    x1 = center + int(math.cos(rad) * 100)
    y1 = center + int(math.sin(rad) * 100)
    x2 = center + int(math.cos(rad) * 450)
    y2 = center + int(math.sin(rad) * 450)
    draw.line([(x1, y1), (x2, y2)], fill=(255, 200, 0, 100), width=3)

# Draw a cool circle border
draw.ellipse([50, 50, size-50, size-50], outline=(255, 215, 0), width=15)
draw.ellipse([80, 80, size-80, size-80], outline=(255, 100, 50), width=10)

# Draw gun crosshair
cross_size = 200
cross_width = 20
draw.rectangle([center - cross_width//2, center - cross_size, 
                center + cross_width//2, center + cross_size], fill=(255, 50, 50))
draw.rectangle([center - cross_size, center - cross_width//2, 
                center + cross_size, center + cross_width//2], fill=(255, 50, 50))

# Draw center circle
draw.ellipse([center-80, center-80, center+80, center+80], fill=(50, 50, 50))
draw.ellipse([center-60, center-60, center+60, center+60], fill=(255, 215, 0))
draw.ellipse([center-40, center-40, center+40, center+40], fill=(255, 50, 50))

# Try to add text
try:
    # Try to use a bold font if available
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 140)
except:
    # Fallback to default font
    font = ImageFont.load_default()

# Draw text "BG" (Battle Game)
text = "BG"
# Get text bounding box to center it
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
text_x = (size - text_width) // 2
text_y = size - 200

# Draw text with shadow
draw.text((text_x + 5, text_y + 5), text, fill=(0, 0, 0), font=font)
draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)

# Save as PNG first
img.save('icon.png')
print("Icon created as icon.png!")
print("\nTo convert to .icns format for macOS:")
print("Run: mkdir icon.iconset")
print("Then copy icon.png to various sizes and run: iconutil -c icns icon.iconset")
