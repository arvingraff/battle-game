#!/bin/bash

# Quick Deploy Script for GitHub Pages
# This script will guide you through deploying BattleGame to GitHub Pages

echo "🎮 BATTLEGAME - GitHub Pages Quick Deploy"
echo "=========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed!"
    echo "Please install git first:"
    echo "  brew install git"
    echo "Or download from: https://git-scm.com/downloads"
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Check if we're in the right directory
if [ ! -f "battlegame.py" ]; then
    echo "❌ Error: battlegame.py not found!"
    echo "Please run this script from the battlegame directory"
    exit 1
fi

echo "✅ In correct directory"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📂 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already initialized"
fi
echo ""

# Get GitHub username
echo "Please enter your GitHub username:"
read -p "Username: " GITHUB_USER

if [ -z "$GITHUB_USER" ]; then
    echo "❌ Username cannot be empty!"
    exit 1
fi

echo ""
echo "Repository will be created at:"
echo "https://github.com/$GITHUB_USER/battlegame"
echo ""

# Get repository name (optional)
echo "Repository name (press Enter for 'battlegame'):"
read -p "Name: " REPO_NAME
REPO_NAME=${REPO_NAME:-battlegame}

echo ""
echo "📝 Creating initial commit..."

# Add all files
git add .

# Create commit
git commit -m "Initial commit: BattleGame with Final Mode and GitHub Pages" || echo "Files already committed"

echo "✅ Files committed"
echo ""

# Add remote
echo "🔗 Connecting to GitHub..."
REMOTE_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

# Check if remote already exists
if git remote get-url origin &> /dev/null; then
    echo "Remote 'origin' already exists. Updating..."
    git remote set-url origin "$REMOTE_URL"
else
    git remote add origin "$REMOTE_URL"
fi

echo "✅ Remote configured: $REMOTE_URL"
echo ""

echo "🚀 Ready to push to GitHub!"
echo ""
echo "IMPORTANT: Before running the push command, make sure you have:"
echo "1. Created the repository on GitHub at: https://github.com/new"
echo "2. Named it '$REPO_NAME'"
echo "3. Set it as PUBLIC (required for free GitHub Pages)"
echo "4. Did NOT initialize with README"
echo ""
echo "Have you created the repository? (y/n)"
read -p "Answer: " CREATED

if [ "$CREATED" != "y" ] && [ "$CREATED" != "Y" ]; then
    echo ""
    echo "Please create the repository first:"
    echo "1. Go to: https://github.com/new"
    echo "2. Repository name: $REPO_NAME"
    echo "3. Description: Epic multiplayer combat game with Final Mode!"
    echo "4. Public: YES"
    echo "5. Initialize with README: NO"
    echo "6. Click 'Create repository'"
    echo ""
    echo "Then run this script again!"
    exit 0
fi

echo ""
echo "📤 Pushing to GitHub..."

# Rename branch to main if needed
git branch -M main

# Push
if git push -u origin main; then
    echo "✅ Successfully pushed to GitHub!"
else
    echo ""
    echo "❌ Push failed. This might be because:"
    echo "1. Repository doesn't exist yet"
    echo "2. Authentication failed (use Personal Access Token as password)"
    echo "3. Remote already has commits"
    echo ""
    echo "If authentication failed, create a Personal Access Token:"
    echo "1. Go to: https://github.com/settings/tokens"
    echo "2. Click 'Generate new token (classic)'"
    echo "3. Give it a name and select 'repo' scope"
    echo "4. Copy the token and use it as your password when pushing"
    echo ""
    exit 1
fi

echo ""
echo "🎨 Now enable GitHub Pages:"
echo "1. Go to: https://github.com/$GITHUB_USER/$REPO_NAME/settings/pages"
echo "2. Under 'Source', select 'Deploy from a branch'"
echo "3. Under 'Branch', select:"
echo "   - Branch: main"
echo "   - Folder: /docs"
echo "4. Click 'Save'"
echo "5. Wait 2-3 minutes for deployment"
echo ""
echo "Your site will be live at:"
echo "🌐 https://$GITHUB_USER.github.io/$REPO_NAME/"
echo ""
echo "🎉 Deployment complete! Your game is now on the internet!"
echo ""
echo "Would you like to open the repository settings in your browser? (y/n)"
read -p "Answer: " OPEN_BROWSER

if [ "$OPEN_BROWSER" = "y" ] || [ "$OPEN_BROWSER" = "Y" ]; then
    open "https://github.com/$GITHUB_USER/$REPO_NAME/settings/pages"
fi

echo ""
echo "✨ All done! Share your game with the world!"
