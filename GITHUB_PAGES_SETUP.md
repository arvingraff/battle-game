# 🚀 BattleGame - GitHub Pages Setup Guide

This guide will help you deploy BattleGame to GitHub Pages so everyone can access and download it!

## 📋 Prerequisites

- A GitHub account (free) - Sign up at https://github.com
- Git installed on your Mac (check by running `git --version` in Terminal)

## 🎯 Step-by-Step Deployment

### Step 1: Create a GitHub Repository

1. Go to https://github.com and sign in
2. Click the **+** button in the top right corner
3. Select **New repository**
4. Name it `battlegame` (or any name you prefer)
5. Add a description: "Epic multiplayer combat game with Final Mode!"
6. Choose **Public** (required for free GitHub Pages)
7. **DO NOT** check "Initialize with README" (we already have one)
8. Click **Create repository**

### Step 2: Initialize Git (if not already done)

Open Terminal in your battlegame folder and run:

```bash
cd /Users/arvingreenberggraff/code/battlegame

# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: BattleGame with Final Mode"
```

### Step 3: Connect to GitHub and Push

Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/battlegame.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note:** You may need to authenticate with GitHub. If prompted:
- Username: Your GitHub username
- Password: Use a Personal Access Token (not your password)
  - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
  - Generate new token with `repo` scope
  - Copy and paste when prompted for password

### Step 4: Enable GitHub Pages

1. Go to your repository on GitHub: `https://github.com/YOUR_USERNAME/battlegame`
2. Click **Settings** (top menu)
3. Scroll down and click **Pages** (left sidebar)
4. Under "Source", select **Deploy from a branch**
5. Under "Branch", select:
   - Branch: `main`
   - Folder: `/docs`
6. Click **Save**

### Step 5: Wait and Access Your Site

1. GitHub Pages will build your site (takes 1-3 minutes)
2. Refresh the Pages settings page
3. You'll see: "Your site is live at https://YOUR_USERNAME.github.io/battlegame/"
4. Click the link to view your site!

## 🎮 What's Published

Your GitHub Pages site will show:
- ✨ Beautiful landing page with game description
- 📥 Download button for the game
- 📖 Features list
- 🎯 Controls guide
- 🎪 Screenshots section (you can add images later)

## 📦 What Users Will Download

When users click "Download BattleGame", they'll get:
- The `battlegame.py` file
- They'll need Python and Pygame installed to run it

## 🔄 Updating Your Site

Whenever you make changes:

```bash
# Stage changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push
```

GitHub Pages will automatically rebuild your site in a few minutes!

## 🎨 Optional: Create a Downloadable Package

You can create a .zip file with everything users need:

```bash
# Create a releases folder
mkdir -p releases

# Create a zip with game files
zip -r releases/BattleGame-v1.0.zip battlegame.py network.py *.mp3 *.jpg *.png *.mp4 requirements.txt README.md -x "*.pyc" -x "__pycache__/*" -x "venv-mobile/*" -x "build/*"
```

Then:
1. Go to your GitHub repository
2. Click **Releases** → **Create a new release**
3. Tag: `v1.0`
4. Title: `BattleGame v1.0 - Epic Release!`
5. Description: Add features and changes
6. Attach `releases/BattleGame-v1.0.zip`
7. Click **Publish release**

Update the download link in `docs/index.html` to point to the release!

## 🌟 Pro Tips

### Add Screenshots
1. Take screenshots of your game (Cmd+Shift+4 on Mac)
2. Add them to the `docs` folder
3. Update `docs/index.html` to display them

### Custom Domain (Optional)
If you want `battlegame.com` instead of `username.github.io/battlegame`:
1. Buy a domain (Google Domains, Namecheap, etc.)
2. In GitHub Pages settings, add custom domain
3. Configure DNS settings as GitHub instructs

### Track Visitors (Optional)
Add Google Analytics to see how many people visit:
1. Create Google Analytics account
2. Add tracking code to `docs/index.html`

## 🆘 Troubleshooting

### "Permission denied" when pushing
- Use Personal Access Token instead of password
- Or set up SSH keys (https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

### 404 error on GitHub Pages
- Wait 5-10 minutes after first setup
- Check that `/docs` folder is selected in Pages settings
- Make sure `index.html` is in the `docs` folder

### Changes not showing
- GitHub Pages caching can take a few minutes
- Hard refresh: Cmd+Shift+R
- Check commit was pushed: `git log --oneline`

## 📱 Share Your Game!

Once live, share your link:
- Twitter/X
- Reddit (r/pygame, r/Python, r/gamedev)
- Discord servers
- Facebook
- Friends and family!

## 🎊 You're Done!

Your game is now live on the internet! 🎉

URL format: `https://YOUR_USERNAME.github.io/battlegame/`

Everyone can visit, learn about it, and download it!

---

**Need Help?** Check the conversation history or ask for assistance with any step!
