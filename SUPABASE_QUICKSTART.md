# 🎮 Classroom World - Supabase Multiplayer

## Quick Start (Choose One)

### Option A: Automated Setup (Recommended)
```bash
cd /Users/arvingreenberggraff/code/battlegame
./setup_supabase.sh
```
The script will guide you through everything!

### Option B: Manual Setup

1. **Create Supabase Account** (2 min)
   - Visit: https://supabase.com
   - Sign up with GitHub
   - Create project: "classroom-world"
   - Free tier is perfect!

2. **Set Up Database** (1 min)
   - Go to SQL Editor
   - Run the SQL from `SUPABASE_SETUP.md`
   - Enable Realtime on `players` and `messages` tables

3. **Configure Game** (30 sec)
   - Open `docs/play/flowers_supabase.html`
   - Line 303: Paste your Project URL
   - Line 304: Paste your Anon Key
   - Save the file

4. **Test & Deploy**
   ```bash
   # Copy configured version to main file
   cp docs/play/flowers_supabase.html docs/play/flowers.html
   
   # Deploy
   git add .
   git commit -m "Add Supabase multiplayer"
   git push origin main
   ```

## Features

✅ **Real-time multiplayer** - See other players move instantly
✅ **Live chat** - Talk with other players in the same room
✅ **Multiple areas** - Classroom, Hallway, Playground, Gym
✅ **Interactive objects** - Desks, lockers, swings, hoops
✅ **Auto-cleanup** - Removes inactive players
✅ **Mobile support** - Touch controls for phones/tablets
✅ **Scalable** - Supports 30-40+ concurrent players

## Testing

1. Open game on your computer
2. Open same URL on phone
3. You should see both players!
4. Try chatting between devices

## Where to Get Credentials

**Project URL**: Settings → API → Project URL
- Looks like: `https://xxxxxxxxxxxxx.supabase.co`

**Anon Key**: Settings → API → Project API keys → anon public
- Looks like: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## Troubleshooting

**"Setup Required" error**
→ Replace `YOUR_PROJECT_URL_HERE` and `YOUR_ANON_KEY_HERE` in the HTML file

**Players not syncing**
→ Enable Realtime: Database → Replication → Toggle on `players` and `messages`

**"Failed to connect"**
→ Check credentials are correct (no extra spaces)
→ Make sure project is fully initialized (green status in Supabase)

**Console errors**
→ Press F12 to see browser console
→ Check if tables exist: Database → Tables → `players`, `messages`

## Files

- `docs/play/flowers.html` - Main game (deploy this)
- `docs/play/flowers_supabase.html` - Template with placeholder credentials
- `SUPABASE_SETUP.md` - Detailed setup guide with SQL
- `setup_supabase.sh` - Automated setup script

## Support

Full documentation: `SUPABASE_SETUP.md`
SQL queries: In the setup guide
Demo: https://yourusername.github.io/battlegame/docs/play/flowers.html

---

**Ready to play?** Follow the Quick Start above! 🚀
