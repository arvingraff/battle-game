# Leaderboard System Documentation 🏆

## Overview
BattleGame now features comprehensive leaderboards for both **Survival Mode** and **Escape Mom Mode**!

## Features

### 📊 Two Separate Leaderboards

1. **Survival Mode Leaderboard**
   - Tracks team scores from Survival Mode
   - Shows player names, scores, levels reached, and player count
   - Top 10 scores saved

2. **Mom Mode Leaderboard**
   - Tracks individual survival times in Escape Mom Mode
   - Shows player name and seconds survived
   - Top 10 times saved

### 🎮 How to Access

**From Main Menu:**
- Select "Survival Leaderboard" to view Survival Mode high scores
- Select "Mom Mode Leaderboard" to view Escape Mom Mode high scores

### 💾 Score Saving

**Survival Mode:**
- Automatically saves team scores (existing feature)
- Includes: team names, score, level, player count, timestamp

**Mom Mode (NEW!):**
- After getting caught by mom, you'll be prompted to enter your name
- Enter up to 15 characters for your name
- Press ENTER to save your score
- Press ESC to skip name entry
- Your survival time is saved to the leaderboard

### 🏅 Leaderboard Display

**Rankings:**
- 🥇 **#1** - Gold color (255, 215, 0)
- 🥈 **#2** - Silver color (192, 192, 192)
- 🥉 **#3** - Bronze color (205, 127, 50)
- **#4-10** - White/gray color (180, 180, 180)

**Mom Mode Display Format:**
```
RANK    NAME              TIME SURVIVED
#1      YourName          127s
#2      Player2           98s
#3      Speedrun          45s
```

**Survival Mode Display Format:**
```
RANK    NAMES             SCORE    LEVEL
#1      Team Alpha        30       2
#2      Solo Joe          25       2
#3      Duo Squad         20       1
```

## Data Storage

### Files:
- `survival_highscores.json` - Survival mode scores
- `mom_mode_highscores.json` - Mom mode scores

### Location:
- Development: `/Users/arvingreenberggraff/code/battlegame/`
- App Bundle: `BattleGame.app/Contents/MacOS/`

### Format:
```json
[
  {
    "name": "PlayerName",
    "score": 127,
    "timestamp": "2025-11-12 14:30:00"
  }
]
```

## Implementation Details

### Functions Added:

1. **`load_highscores(mode='survival')`**
   - Loads scores from appropriate JSON file
   - Returns empty list if file doesn't exist
   - Handles both 'survival' and 'mom' modes

2. **`save_highscore(name, score, mode='survival', extra_data=None)`**
   - Saves new score with name and timestamp
   - Automatically sorts by score (descending)
   - Keeps only top 10 scores
   - Returns updated score list

3. **`show_leaderboard(mode='survival')`**
   - Displays full-screen leaderboard
   - Different titles/colors for each mode
   - Interactive "Back" button
   - ESC key to exit

### Menu Integration:

**Main Menu Options Updated:**
- Added "Survival Leaderboard" option
- Added "Mom Mode Leaderboard" option
- Both accessible via menu selection or ENTER key

### Mom Mode Integration:

**Game Over Screen Enhanced:**
- Shows "SHE CAUGHT YOU!" title
- Displays survival time
- Name entry prompt with input box
- Real-time text input with cursor
- Confirmation message after saving
- Back to menu button

## User Experience

### Name Entry Flow:
1. Get caught by mom 😱
2. Watch terrifying jumpscare
3. See game over screen with survival time
4. Enter your name (up to 15 chars)
5. Press ENTER to save
6. See "Score saved! Thanks, [name]!" message
7. Return to menu

### Leaderboard Viewing:
1. Select leaderboard from main menu
2. View top 10 scores with rankings
3. Color-coded medals for top 3
4. Press ESC or click "Back" to return

## Technical Notes

- Scores are sorted automatically by value (highest first)
- Timestamps use format: "YYYY-MM-DD HH:MM:SS"
- JSON files created automatically if missing
- Write failures (in bundled app) handled gracefully
- Max 15 characters for player names
- Input validation for printable characters only

## Future Enhancements

Potential additions:
- Online leaderboards (sync across devices)
- More detailed stats (date/time filters)
- Export/share scores
- Achievement badges
- Difficulty multipliers
- Weekly/monthly rankings

---

**Have fun competing for the top spot! 🎮🏆**
