#!/bin/bash

# BattleGame Release Package Creator
# This script creates a .zip file ready for users to download

echo "🎮 Creating BattleGame Release Package..."

# Create releases directory
mkdir -p releases

# Version number
VERSION="1.0"
RELEASE_NAME="BattleGame-v${VERSION}"

# Create temporary directory
TEMP_DIR="temp_release"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR/$RELEASE_NAME"

echo "📦 Copying game files..."

# Copy essential game files
cp battlegame.py "$TEMP_DIR/$RELEASE_NAME/"
cp network.py "$TEMP_DIR/$RELEASE_NAME/"
cp README.md "$TEMP_DIR/$RELEASE_NAME/"

# Copy all audio files
cp *.mp3 "$TEMP_DIR/$RELEASE_NAME/" 2>/dev/null || echo "No .mp3 files found"
cp *.MP4 "$TEMP_DIR/$RELEASE_NAME/" 2>/dev/null || echo "No .MP4 files found"
cp *.mp4 "$TEMP_DIR/$RELEASE_NAME/" 2>/dev/null || echo "No .mp4 files found"

# Copy all image files
cp *.png "$TEMP_DIR/$RELEASE_NAME/" 2>/dev/null || echo "No .png files found"
cp *.jpg "$TEMP_DIR/$RELEASE_NAME/" 2>/dev/null || echo "No .jpg files found"

# Create a requirements.txt if it doesn't exist
if [ ! -f requirements.txt ]; then
    echo "pygame>=2.0.0" > "$TEMP_DIR/$RELEASE_NAME/requirements.txt"
else
    cp requirements.txt "$TEMP_DIR/$RELEASE_NAME/"
fi

# Create an installation guide
cat > "$TEMP_DIR/$RELEASE_NAME/INSTALL.txt" << 'EOF'
🎮 BATTLEGAME INSTALLATION GUIDE
================================

Thank you for downloading BattleGame!

REQUIREMENTS:
- Python 3.7 or higher
- Pygame library

INSTALLATION STEPS:

1. Install Python (if not already installed):
   - Visit https://www.python.org/downloads/
   - Download and install Python 3.7 or higher
   - Make sure "Add Python to PATH" is checked during installation

2. Install Pygame:
   Open Terminal (Mac/Linux) or Command Prompt (Windows) and run:
   
   pip install pygame
   
   Or if you have the requirements.txt file:
   
   pip install -r requirements.txt

3. Run the game:
   
   python battlegame.py
   
   Or double-click battlegame.py (if Python is associated with .py files)

CONTROLS:
- See README.md for full controls and game modes
- Press '6776' after certain transformations to unlock Final Mode!

TROUBLESHOOTING:
- If 'python' command not found, try 'python3'
- If 'pip' command not found, try 'pip3'
- Make sure all files are in the same folder

ENJOY THE GAME! 🎉
EOF

# Create the zip file
echo "🗜️  Creating zip archive..."
cd "$TEMP_DIR"
zip -r "../releases/${RELEASE_NAME}.zip" "$RELEASE_NAME"
cd ..

# Clean up
rm -rf "$TEMP_DIR"

echo "✅ Release package created: releases/${RELEASE_NAME}.zip"
echo ""
echo "📊 Package contents:"
unzip -l "releases/${RELEASE_NAME}.zip"
echo ""
echo "🚀 Next steps:"
echo "1. Test the package by extracting and running it"
echo "2. Upload to GitHub Releases"
echo "3. Update the download link in docs/index.html to point to the release"
echo ""
echo "GitHub Release URL format:"
echo "https://github.com/YOUR_USERNAME/battlegame/releases/download/v${VERSION}/${RELEASE_NAME}.zip"
