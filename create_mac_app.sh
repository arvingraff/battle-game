#!/bin/bash
# Creates a double-clickable BattleGame.app for macOS

echo "Creating BattleGame.app..."

# Create app structure
rm -rf BattleGame.app
mkdir -p BattleGame.app/Contents/MacOS
mkdir -p BattleGame.app/Contents/Resources

# Create the launcher script
cat > BattleGame.app/Contents/MacOS/BattleGame << 'LAUNCHER'
#!/bin/bash
cd "$(dirname "$0")/../Resources"
python3 battlegame.py
LAUNCHER

chmod +x BattleGame.app/Contents/MacOS/BattleGame

# Create Info.plist
cat > BattleGame.app/Contents/Info.plist << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>BattleGame</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.battlegame.app</string>
    <key>CFBundleName</key>
    <string>BattleGame</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

# Copy game files
cp battlegame.py BattleGame.app/Contents/Resources/
cp network.py BattleGame.app/Contents/Resources/
cp -r *.mp3 *.mp4 *.jpg *.png BattleGame.app/Contents/Resources/ 2>/dev/null || true

echo "✅ BattleGame.app created!"
echo "You can now double-click BattleGame.app to play!"
