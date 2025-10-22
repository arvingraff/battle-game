#!/bin/bash
cd /Users/arvingreenberggraff/code/battlegame
echo "🔨 Building optimized BattleGame..."
/Users/arvingreenberggraff/Library/Python/3.9/bin/pyinstaller BattleGame.spec --noconfirm
echo "✅ Build complete!"
echo "🧹 Removing quarantine..."
xattr -cr dist/BattleGame.app
echo "📦 Copying to Applications..."
rm -rf /Applications/BattleGame.app
cp -R dist/BattleGame.app /Applications/
xattr -cr /Applications/BattleGame.app
echo "✨ Done! Launch from Applications folder or Launchpad"
echo "   Should now open in 2-3 seconds!"
