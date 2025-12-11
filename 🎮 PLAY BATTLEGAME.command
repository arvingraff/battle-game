#!/bin/bash
# BattleGame Easy Launcher - Just double-click!

# Get the directory where this script is
cd "$(dirname "$0")"

# Clear the screen
clear

echo "╔════════════════════════════════════════╗"
echo "║     🎮  BATTLEGAME LAUNCHER  🎮       ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Starting game..."
echo ""

# Launch the game
python3 battlegame.py

echo ""
echo "════════════════════════════════════════"
echo "Game closed."
echo "You can close this window now."
echo "════════════════════════════════════════"
