# Quick Match Feature Guide

## Overview
The **Quick Match** feature provides automatic matchmaking for online battles. Both players can simply click "Quick Match" and the game will automatically connect them without needing to manually enter IP addresses or decide who hosts.

## How It Works

### For Both Players
1. From the main menu, select any online-enabled game mode:
   - Battle Mode
   - Coin Collection Mode
   - Survival Mode
   - Makka Pakka Mode

2. Click **"Play Online"**

3. Click **"Quick Match"**

### Behind the Scenes
When you click Quick Match, the game:

1. **Scans the local network** (2-3 seconds)
   - Searches for any available game hosts on your local network
   - Shows "Searching for available players..." message

2. **If a host is found:**
   - Automatically connects as a client
   - Shows "Found player! Connecting..." message
   - Both players enter their names simultaneously
   - Proceeds to character selection and game

3. **If no host is found:**
   - Automatically becomes a host
   - Shows "No players found - Hosting game..."
   - Displays your IP address
   - Waits for another player to join
   - When someone joins, both enter names and play

### Key Features

✅ **No IP Entry Required**: Just click and play!

✅ **Smart Auto-Hosting**: If no one is hosting, you become the host automatically

✅ **Synchronized Name Entry**: Both players enter names at the same time, no waiting for turns

✅ **Fallback Support**: If connection to a found host fails, automatically becomes host instead

✅ **Cancel Anytime**: Press ESC during scanning or waiting to return to the menu

## Example Scenarios

### Scenario 1: Two Players Press Quick Match Simultaneously
- **Player A** clicks Quick Match → Scans → No hosts found → Becomes host
- **Player B** clicks Quick Match → Scans → Finds Player A → Connects as client
- **Result**: Connected and ready to play!

### Scenario 2: Player Already Hosting
- **Player A** is already hosting (via "Host Game" button)
- **Player B** clicks Quick Match → Finds Player A → Connects
- **Result**: Connected and ready to play!

### Scenario 3: Connection Fails
- **Player B** finds **Player A** but connection fails
- **Player B** automatically becomes a host instead
- Another player can then find and join Player B
- **Result**: Seamless fallback, no manual intervention needed

## Technical Details

### Network Scanning
- Scans the local network (192.168.x.x or 10.0.x.x)
- Checks for hosts on port 50007
- Timeout: 3 seconds
- Uses multithreading for fast parallel scanning

### Connection Priority
- Always tries to join an existing host first
- Only becomes a host if no one else is available
- This minimizes wait times and ensures players connect quickly

### Compatible Modes
Quick Match works with all online game modes:
- ⚔️ **Battle Mode** (mode_type=0)
- 💰 **Coin Collection Mode** (mode_type=1)
- 🧟 **Survival Mode** (mode_type=2)
- 🧼 **Makka Pakka Mode** (mode_type=3)

## Tips for Best Results

1. **Same Network**: Both players should be on the same local network (WiFi/LAN)
2. **Firewall**: Make sure port 50007 is not blocked
3. **Timing**: Works best when both players click Quick Match around the same time
4. **Patience**: Wait 3-5 seconds during the scan before canceling

## Troubleshooting

**"No players found"**
- Wait a few seconds, another player may be scanning too
- Make sure you're on the same local network
- Check firewall settings

**"Connection failed"**
- The other player may have canceled
- Network issue occurred
- Game will automatically become host as fallback

**Can't find each other**
- Both might have become hosts at the same time
- One player should cancel and try again
- Or use manual "Host Game" / "Join Game" instead

## Traditional Method Still Available

If Quick Match doesn't work for your situation, you can still use:
- **Host Game**: Manually host and share your IP
- **Join Game**: Manually enter the host's IP address

Both methods are still available in the online menu for maximum flexibility!

---

**Enjoy seamless online gaming! 🎮**
