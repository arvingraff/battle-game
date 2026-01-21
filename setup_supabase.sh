#!/bin/bash

echo "🚀 Supabase Multiplayer Setup for Classroom World"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "SUPABASE_SETUP.md" ]; then
    echo "❌ Please run this script from the battlegame root directory"
    exit 1
fi

echo "📋 Setup Steps:"
echo ""
echo "1️⃣  Create Supabase Account"
echo "   → Go to: https://supabase.com"
echo "   → Sign up with GitHub (fastest)"
echo ""
echo "2️⃣  Create New Project"
echo "   → Name: classroom-world (or anything)"
echo "   → Choose Free tier"
echo "   → Wait ~2 minutes for initialization"
echo ""
echo "3️⃣  Get Your Credentials"
echo "   → Settings → API"
echo "   → Copy: Project URL & anon public key"
echo ""
echo "4️⃣  Set Up Database"
echo "   → SQL Editor → New Query"
echo "   → Copy/paste SQL from SUPABASE_SETUP.md"
echo "   → Run the query"
echo ""
echo "5️⃣  Enable Realtime"
echo "   → Database → Replication"
echo "   → Enable: players & messages tables"
echo ""

read -p "Have you completed steps 1-5? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please complete the steps above first!"
    echo "Full guide: SUPABASE_SETUP.md"
    exit 0
fi

echo ""
echo "📝 Enter Your Supabase Credentials"
echo "=================================="
echo ""

read -p "Project URL (e.g., https://xxxxx.supabase.co): " SUPABASE_URL
read -p "Anon Key (starts with eyJhbGc...): " SUPABASE_KEY

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "❌ Both URL and Key are required!"
    exit 1
fi

echo ""
echo "🔧 Updating game files..."

# Update the Supabase version
sed -i.bak "s|const SUPABASE_URL = 'YOUR_PROJECT_URL_HERE';|const SUPABASE_URL = '$SUPABASE_URL';|g" docs/play/flowers_supabase.html
sed -i.bak "s|const SUPABASE_KEY = 'YOUR_ANON_KEY_HERE';|const SUPABASE_KEY = '$SUPABASE_KEY';|g" docs/play/flowers_supabase.html

# Copy to main game file
cp docs/play/flowers_supabase.html docs/play/flowers.html

echo "✅ Configuration complete!"
echo ""
echo "🧪 Testing locally..."
echo ""
echo "Opening game in browser..."
open docs/play/flowers.html 2>/dev/null || xdg-open docs/play/flowers.html 2>/dev/null || echo "Please open: docs/play/flowers.html"

echo ""
read -p "Does the game work locally? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  Check browser console (F12) for errors"
    echo "   Common issues:"
    echo "   - Wrong URL or Key"
    echo "   - Database tables not created"
    echo "   - Realtime not enabled"
    exit 1
fi

echo ""
echo "🚀 Deploying to GitHub Pages..."
echo ""

git add .
git commit -m "Add Supabase multiplayer support"
git push origin main

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "🎮 Your game is live at:"
echo "   https://$(git config user.name).github.io/battlegame/docs/play/flowers.html"
echo ""
echo "📱 Test with multiple devices:"
echo "   - Open on your phone"
echo "   - Open in another browser"
echo "   - Share with friends!"
echo ""
echo "🎉 Enjoy your multiplayer game!"
