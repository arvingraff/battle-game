# ❓ BattleGame GitHub Pages - Frequently Asked Questions

## 🚀 Deployment Questions

### Q: Do I need to pay for GitHub or GitHub Pages?
**A:** No! Both are completely free for public repositories. You only pay if you want:
- Private repositories with Pages (GitHub Pro - $4/month)
- Custom domains (separate, ~$10-15/year)

### Q: How long does deployment take?
**A:** 
- Initial setup: 10-15 minutes (one time)
- Each update: 2-3 minutes for GitHub Pages to rebuild
- Total first-time deployment: ~20 minutes including repository creation

### Q: What if I don't have a GitHub account?
**A:** 
1. Go to https://github.com
2. Click "Sign up"
3. It's free and takes 2 minutes
4. You'll need an email address

### Q: Can I use a different name instead of "battlegame"?
**A:** Yes! You can name your repository anything:
- `epic-battle-game`
- `my-awesome-game`
- `final-mode-game`

Your URL will be: `YOUR_USERNAME.github.io/REPO_NAME`

## 🔧 Technical Questions

### Q: What's a Personal Access Token and why do I need it?
**A:** GitHub no longer accepts passwords for command-line operations. A PAT is a secure alternative:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name it "BattleGame Deploy"
4. Check "repo" scope
5. Generate and copy the token
6. Use it as your password when pushing to GitHub

**Important:** Save it somewhere secure! GitHub won't show it again.

### Q: What's the difference between the repository and GitHub Pages?
**A:**
- **Repository:** Stores all your code files (like Google Drive for code)
- **GitHub Pages:** Serves the `/docs` folder as a public website

Both are on GitHub, but serve different purposes.

### Q: Why does the website only show /docs and not the whole game?
**A:** 
- The game is a Python application (requires Python to run)
- Websites run in browsers (HTML/CSS/JavaScript)
- `/docs/index.html` is a landing/download page, not the game itself
- Users download the game files and run them locally

### Q: Can people play the game directly in their browser?
**A:** Not with the current setup. The game is written in Python/Pygame and needs to be downloaded and run locally. To make it browser-playable, you'd need to:
- Rewrite it in JavaScript (huge project)
- Use something like Pygame Zero Web (experimental)
- Use PyScript (slow, experimental)

For now, download-and-play is the standard approach.

## 📥 Download Questions

### Q: What do users need to run the game after downloading?
**A:** 
- Python 3.7 or higher
- Pygame library (`pip install pygame`)
- All included files in the same folder

The `INSTALL.txt` in the download package has full instructions.

### Q: How big is the download?
**A:** Usually 5-20 MB depending on your audio/video files. Check with:
```bash
ls -lh releases/BattleGame-v1.0.zip
```

### Q: Can Mac/Windows/Linux users all play?
**A:** Yes! Python and Pygame work on all platforms. The game is cross-platform.

## 🔄 Update Questions

### Q: How do I update the game after deployment?
**A:** 
```bash
# Make your changes to files
# Then:
git add .
git commit -m "Description of changes"
git push
```

GitHub Pages will automatically update in 2-3 minutes.

### Q: How do I create a new version/release?
**A:**
1. Update version in `create_release.sh` (VERSION="1.1")
2. Run `./create_release.sh`
3. Go to GitHub → Releases → Create new release
4. Tag: `v1.1`, attach the new .zip
5. Publish!

### Q: Do users automatically get updates?
**A:** No, they need to:
- Visit your site and download the new version
- Or you can add an auto-update checker in the game (advanced)

## 🌐 Website Questions

### Q: Can I customize the landing page?
**A:** Absolutely! Edit `/docs/index.html`:
- Change colors, text, layout
- Add screenshots/videos
- Add more sections
- Change fonts/styles

### Q: How do I add screenshots?
**A:**
1. Take screenshots of your game (Cmd+Shift+4 on Mac)
2. Save them in `/docs` folder (e.g., `screenshot1.png`)
3. Edit `docs/index.html` to display them:
```html
<img src="screenshot1.png" alt="Game screenshot">
```
4. Commit and push

### Q: Can I get my own domain like battlegame.com?
**A:** Yes!
1. Buy a domain from Google Domains, Namecheap, etc. (~$10-15/year)
2. In GitHub Pages settings, enter your custom domain
3. Configure DNS settings as GitHub instructs
4. Your site will be at battlegame.com instead of username.github.io/battlegame

### Q: How do I track how many people visit?
**A:** Add Google Analytics:
1. Create account at https://analytics.google.com
2. Get tracking code
3. Add it to `docs/index.html` in the `<head>` section
4. View stats in Google Analytics dashboard

## 🆘 Troubleshooting Questions

### Q: I get "Permission denied" when pushing
**A:** Common fixes:
1. Use Personal Access Token instead of password
2. Or set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
3. Check if repository exists on GitHub
4. Make sure you have write access

### Q: GitHub Pages shows 404 error
**A:**
1. Wait 5-10 minutes (first deployment takes time)
2. Check Pages settings: Branch = `main`, Folder = `/docs`
3. Make sure `index.html` exists in `/docs` folder
4. Hard refresh browser (Cmd+Shift+R)

### Q: Changes I made aren't showing on the website
**A:**
1. Did you `git push`? Check with `git status`
2. Wait 2-3 minutes for GitHub Pages to rebuild
3. Hard refresh browser (Cmd+Shift+R)
4. Check if the file is in `/docs` folder (only /docs is published)

### Q: The deploy script doesn't work
**A:**
1. Make sure script is executable: `chmod +x deploy_to_github.sh`
2. Run from the battlegame folder
3. Check git is installed: `git --version`
4. If it still fails, follow manual steps in GITHUB_PAGES_SETUP.md

### Q: Download link doesn't work
**A:**
1. If linking to a release, make sure the release exists
2. Check the URL is correct
3. URL format: `https://github.com/USERNAME/REPO/releases/download/v1.0/BattleGame-v1.0.zip`
4. Make sure the .zip file was uploaded to the release

## 📊 Advanced Questions

### Q: Can I host a multiplayer server?
**A:** GitHub Pages only hosts static websites, not game servers. For multiplayer:
- Use a cloud service (AWS, DigitalOcean, Heroku)
- Use a dedicated game server host
- Players can host locally and share IP (your current setup)

### Q: How many people can download/visit?
**A:** GitHub Pages limits:
- Bandwidth: 100 GB/month (very generous)
- Storage: 1 GB max (your game is probably <100 MB)
- For most hobby projects, you'll never hit these limits

### Q: Can I make money from this?
**A:** 
- GitHub Pages itself is free
- You could add:
  - Donation buttons (Ko-fi, Patreon)
  - Paid downloads (Gumroad, Itch.io)
  - Ads (not recommended for user experience)

### Q: Can others contribute to my game?
**A:** Yes! GitHub is built for collaboration:
1. Others can fork your repository
2. Make changes
3. Submit pull requests
4. You review and merge their changes

### Q: Should I make the repository private?
**A:** 
- Private repos can't use free GitHub Pages
- If you want free Pages, keep it public
- Your code is visible, but that's normal for open-source games

## 🎮 Game-Specific Questions

### Q: Will Final Mode work after download?
**A:** Yes! Everything is included:
- All game modes
- Secret codes
- Audio files
- Assets

### Q: Can I update just the landing page without affecting the game?
**A:** Yes:
1. Edit `docs/index.html`
2. Commit and push
3. Only the website updates, not the downloadable game

To update the game in downloads, create a new release.

### Q: How do I tell people about the secret code (6776)?
**A:** Add it to:
- README.md (with spoiler warning)
- Landing page (in a "Secrets" section)
- In-game hints
- Social media posts

## 📱 Sharing Questions

### Q: What's the best way to share my game?
**A:** Share your GitHub Pages link:
```
https://YOUR_USERNAME.github.io/battlegame/
```

Places to share:
- Reddit: r/pygame, r/Python, r/gamedev
- Twitter/X with #gamedev #pygame hashtags
- Discord servers for game development
- Friends and family
- Gaming forums

### Q: Can I submit to game websites?
**A:** Yes! Sites like:
- Itch.io (upload your .zip)
- GameJolt
- IndieDB
- Link to your GitHub Pages site

### Q: How do I get feedback?
**A:** 
- GitHub Issues (built-in)
- Reddit posts
- Discord communities
- YouTube playthrough videos
- Let friends test and comment

## 🎯 Quick Answers

| Question | Answer |
|----------|--------|
| Cost? | Free |
| Time to deploy? | 20 minutes first time |
| Need coding skills? | Basic git commands |
| Works on all OS? | Yes (Python is cross-platform) |
| Automatic updates? | No, users re-download |
| Multiplayer server? | Not on GitHub Pages |
| Custom domain? | Yes, extra cost |
| Private repository? | Not with free Pages |

## 🆘 Still Need Help?

1. Check the error message carefully
2. Search Google: "github pages [your error]"
3. Check GitHub Docs: https://docs.github.com/pages
4. Ask on:
   - Stack Overflow
   - GitHub Community Forum
   - Reddit r/github

## 🎉 Success Checklist

✅ Repository created  
✅ Code pushed to GitHub  
✅ GitHub Pages enabled  
✅ Website is live  
✅ Download works  
✅ Game runs after download  
✅ Shared with friends  
✅ Getting players!  

---

**Have a question not answered here?** Ask in the conversation!
