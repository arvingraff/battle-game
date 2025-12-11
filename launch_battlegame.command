#!/bin/bash
# BattleGame Auto-Launcher

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "🎮 Starting BattleGame..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python from https://www.python.org/downloads/"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if pygame is installed
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "📦 Installing Pygame..."
    pip3 install pygame
fi

# Check if files exist
if [ ! -f "battlegame.py" ]; then
    echo "❌ battlegame.py not found!"
    read -p "Press Enter to exit..."
    exit 1
fi

if [ ! -f "network.py" ]; then
    echo "❌ network.py not found!"
    read -p "Press Enter to exit..."
    exit 1
fi

# Launch the game
echo "✅ Launching BattleGame..."
echo ""
python3 battlegame.py

echo ""
echo "Game closed. Press Enter to exit..."
read
