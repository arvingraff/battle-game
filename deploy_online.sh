#!/bin/bash

# BattleGame - Deploy to Web Script
# This script helps you deploy your game online!

echo "🎮 BATTLEGAME WEB DEPLOYMENT 🎮"
echo "================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "⚠️  Git is not installed. Please install git first:"
    echo "    brew install git"
    exit 1
fi

# Check if python is available
if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python3 is not installed."
    exit 1
fi

echo "Choose deployment method:"
echo ""
echo "1) GitHub Pages (Recommended - Free & Easy!)"
echo "2) Create Python Web Server (Local testing)"
echo "3) Export for Itch.io upload"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "📦 Setting up GitHub Pages deployment..."
        echo ""
        echo "STEPS TO DEPLOY:"
        echo "1. Create a GitHub account at https://github.com if you don't have one"
        echo "2. Create a new repository called 'battlegame'"
        echo "3. Run these commands:"
        echo ""
        echo "   cd /Users/arvingreenberggraff/code/battlegame"
        echo "   git init"
        echo "   git add ."
        echo "   git commit -m 'Initial commit - BattleGame!'"
        echo "   git branch -M main"
        echo "   git remote add origin https://github.com/YOUR_USERNAME/battlegame.git"
        echo "   git push -u origin main"
        echo ""
        echo "4. Go to your repository settings on GitHub"
        echo "5. Navigate to Pages section"
        echo "6. Select 'main' branch and '/web' folder"
        echo "7. Your game will be live at: https://YOUR_USERNAME.github.io/battlegame/"
        echo ""
        read -p "Press Enter to continue..."
        ;;
    2)
        echo ""
        echo "🌐 Starting local web server..."
        echo ""
        echo "Your game will be available at: http://localhost:8000"
        echo "Press Ctrl+C to stop the server"
        echo ""
        cd web
        python3 -m http.server 8000
        ;;
    3)
        echo ""
        echo "📦 Creating Itch.io package..."
        echo ""
        
        # Create itch folder
        mkdir -p itch_upload
        
        # Copy necessary files
        cp battlegame.py itch_upload/
        cp -r *.mp3 *.jpg *.mp4 *.png itch_upload/ 2>/dev/null
        cp web/index.html itch_upload/
        
        # Create README
        cat > itch_upload/README.txt << 'EOF'
BattleGame - Upload to Itch.io

STEPS:
1. Go to https://itch.io and create an account
2. Create a new project
3. Upload all files from this folder
4. Set as "HTML" project
5. Set "index.html" as the main file
6. Publish!

Your game will be playable online!
EOF
        
        echo "✅ Files ready in 'itch_upload' folder!"
        echo "   Follow the instructions in itch_upload/README.txt"
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

echo ""
echo "✨ Done! Good luck with your game! ✨"
