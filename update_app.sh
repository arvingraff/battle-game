#!/bin/bash
echo "🔨 Rebuilding BattleGame with realistic guns in Capture the Flag..."
cd /Users/arvingreenberggraff/code/battlegame
/Users/arvingreenberggraff/Library/Python/3.9/bin/pyinstaller BattleGame.spec --noconfirm
echo ""
echo "✅ Build complete!"
echo "🧹 Removing quarantine..."
xattr -cr dist/BattleGame.app
echo "📦 Copying to Applications..."
rm -rf /Applications/BattleGame.app
cp -R dist/BattleGame.app /Applications/
xattr -cr /Applications/BattleGame.app
echo ""
echo "✨ All done! Your app in Applications has been updated with:"
echo "   - Online multiplayer in Battle Mode! 🌐"
echo "   - Online multiplayer in Coin Collection Mode! 🌐"
echo "   - Online multiplayer in Survival Mode! 🌐"
echo "   - Online multiplayer in Makka Pakka Mode! 🌐"
echo "   - Online multiplayer in Capture the Flag! 🌐"
echo "   - Realistic pistols in Capture the Flag"
echo "   - Flags return to base when shot"
echo "   - Players respawn at base when shot while carrying flag"
echo "   - Fixed Mom Mode"
echo ""
echo "Launch from Applications folder or Launchpad! 🎮"
