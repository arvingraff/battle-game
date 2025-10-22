#!/usr/bin/env python3
import os
import subprocess

# Convert PNG to ICNS using macOS built-in tools
png_file = "icon.png"
iconset_dir = "icon.iconset"

# Create iconset directory
os.makedirs(iconset_dir, exist_ok=True)

# Generate different sizes for the iconset
sizes = [16, 32, 128, 256, 512]
for size in sizes:
    # Standard resolution
    cmd1 = f"sips -z {size} {size} {png_file} --out {iconset_dir}/icon_{size}x{size}.png"
    subprocess.run(cmd1, shell=True)
    # Retina resolution
    cmd2 = f"sips -z {size*2} {size*2} {png_file} --out {iconset_dir}/icon_{size}x{size}@2x.png"
    subprocess.run(cmd2, shell=True)

# Convert iconset to icns
subprocess.run(f"iconutil -c icns {iconset_dir}", shell=True)

print("✅ icon.icns created successfully!")
