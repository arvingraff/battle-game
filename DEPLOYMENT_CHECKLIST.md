# 🎯 BattleGame GitHub Pages Deployment Checklist

Use this checklist to deploy your game to GitHub Pages step by step!

## ☐ Pre-Deployment (5 minutes)

- [ ] I have a GitHub account (or created one at https://github.com)
- [ ] Git is installed on my Mac (check with `git --version`)
- [ ] I'm in the battlegame folder in Terminal
- [ ] I've read GITHUB_PAGES_SETUP.md

## ☐ Create GitHub Repository (2 minutes)

- [ ] Went to https://github.com/new
- [ ] Named repository: `battlegame` (or my preferred name)
- [ ] Set description: "Epic multiplayer combat game with Final Mode!"
- [ ] Selected **Public** (required for free GitHub Pages)
- [ ] **Did NOT** check "Initialize with README"
- [ ] Clicked "Create repository"
- [ ] Saved the repository URL (e.g., https://github.com/username/battlegame)

## ☐ Deploy Using Script (EASIEST METHOD)

Just run this in Terminal:

```bash
./deploy_to_github.sh
```

The script will:
- ✅ Check if git is installed
- ✅ Initialize git repository
- ✅ Ask for your GitHub username
- ✅ Create initial commit
- ✅ Configure remote
- ✅ Push to GitHub
- ✅ Give you instructions for GitHub Pages setup

**OR** follow manual steps below...

## ☐ Manual Deployment (if script doesn't work)

### Initialize Git
- [ ] Opened Terminal in battlegame folder
- [ ] Ran: `git init`
- [ ] Ran: `git add .`
- [ ] Ran: `git commit -m "Initial commit: BattleGame"`

### Connect to GitHub
Replace YOUR_USERNAME with actual username:

- [ ] Ran: `git remote add origin https://github.com/YOUR_USERNAME/battlegame.git`
- [ ] Ran: `git branch -M main`
- [ ] Ran: `git push -u origin main`
- [ ] Entered credentials (Personal Access Token as password)

## ☐ Enable GitHub Pages (2 minutes)

- [ ] Went to: https://github.com/YOUR_USERNAME/battlegame/settings/pages
- [ ] Under "Source", selected "Deploy from a branch"
- [ ] Under "Branch":
  - [ ] Selected: `main`
  - [ ] Selected folder: `/docs`
- [ ] Clicked "Save"
- [ ] Waited 2-3 minutes for deployment

## ☐ Verify Deployment (1 minute)

- [ ] Refreshed GitHub Pages settings page
- [ ] Saw message: "Your site is live at..."
- [ ] Clicked the link
- [ ] Saw the BattleGame landing page
- [ ] Download button works

## ☐ Create Release Package (Optional but Recommended)

Makes it easier for users to download:

- [ ] Ran: `./create_release.sh`
- [ ] Checked that `releases/BattleGame-v1.0.zip` was created
- [ ] Went to: https://github.com/YOUR_USERNAME/battlegame/releases/new
- [ ] Created new release:
  - [ ] Tag: `v1.0`
  - [ ] Title: `BattleGame v1.0 - Epic Release!`
  - [ ] Description: Added features and modes
  - [ ] Attached the .zip file
  - [ ] Clicked "Publish release"

## ☐ Update Download Link (Optional)

If you created a release:

- [ ] Opened `docs/index.html`
- [ ] Found the download button link
- [ ] Changed it to: `https://github.com/YOUR_USERNAME/battlegame/releases/download/v1.0/BattleGame-v1.0.zip`
- [ ] Saved the file
- [ ] Ran: `git add docs/index.html`
- [ ] Ran: `git commit -m "Update download link to release"`
- [ ] Ran: `git push`

## ☐ Share Your Game! 🎉

- [ ] Copied my site URL: `https://YOUR_USERNAME.github.io/battlegame/`
- [ ] Shared on social media
- [ ] Sent to friends
- [ ] Posted on Reddit/Discord
- [ ] Celebrated! 🎊

## 🆘 Troubleshooting

### Git not found
```bash
# Install git
brew install git
```

### Authentication failed
- Use Personal Access Token instead of password
- Create at: https://github.com/settings/tokens
- Select "repo" scope
- Copy and use as password

### 404 on GitHub Pages
- Wait 5-10 minutes after first setup
- Hard refresh browser (Cmd+Shift+R)
- Check `/docs` folder is selected in settings

### Push rejected
- Repository might already have commits
- Try: `git pull origin main --rebase`
- Then: `git push origin main`

## 📝 Notes

**My GitHub username:** ________________

**My repository URL:** https://github.com/________________/battlegame

**My GitHub Pages URL:** https://________________.github.io/battlegame/

**Date deployed:** ________________

---

## 🎯 Quick Commands Reference

```bash
# Deploy for first time
./deploy_to_github.sh

# Create release package
./create_release.sh

# Update after changes
git add .
git commit -m "Description of changes"
git push

# Check status
git status

# View remote
git remote -v

# View commit history
git log --oneline
```

---

**Need help?** Check GITHUB_PAGES_SETUP.md for detailed instructions!
