# ULTIMATE HACK SEQUENCE GUIDE

## Overview
This document describes the complete secret hack sequence that unlocks hidden game modes through a series of easter eggs and cheat codes.

## The Complete Sequence

### Step 1: Play Sheep Mode
- Go to Sheep Mode (must be unlocked from shop first)
- **Tracker**: `secret_hack['sheep_mode_played'] = True`

### Step 2: Enter "whoppa gang" in Sheep Mode
- While in Sheep Mode, type: **whoppa gang**
- You'll see a confirmation message
- **Tracker**: `secret_hack['whoppa_gang_entered'] = True`

### Step 3: Exit Sheep Mode with Music Still Playing
- Press ESC to exit Sheep Mode
- If Gangnam Style music is still playing, the hack continues
- **Tracker**: `secret_hack['music_still_playing'] = True`

### Step 4: Enter Battle Mode After Music Persists
- From main menu, select **"Battle Mode"**
- You'll see the "Play Local" / "Play Online" screen
- **Tracker**: `secret_hack['entered_battle_after_music'] = True` (automatically set when entering)

### Step 5: Press "lllooolll" in Battle Mode Lobby
- While on the Battle Mode lobby screen (with Play Local/Play Online buttons)
- Type: **lllooolll**
- The screen will display "**skibidi**" in large yellow text for 2 seconds
- You'll automatically return to the main menu
- **Note**: You don't need to actually play a battle! Just enter the code on the lobby screen.
- **Tracker**: `secret_hack['skibidi_triggered'] = True`

### Step 6: Press "jjj" in Main Menu
- Back at main menu, type: **jjj**
- A wolf appears and eats all the menu buttons!
- All game modes become unplayable (blocked)
- Warning appears: "The wolf ate all the buttons! Nothing works..."
- **Tracker**: `secret_hack['wolf_ate_buttons'] = True`

### Step 7: Press "qqq" in Main Menu
- While buttons are disabled, type: **qqq**
- The wolf vomits up a new button: "**Grass Mode**"
- Grass Mode appears in the menu before the Shop
- **Tracker**: `secret_hack['grass_mode_unlocked'] = True`

### Step 8: Enter Grass Mode and Press "ttt"
- Select and enter Grass Mode
- You'll see a peaceful grassy field
- Type: **ttt**
- The wolf vomits up another new mode: "**Combine Mode**"
- Combine Mode appears in the menu
- **Tracker**: `secret_hack['combine_mode_unlocked'] = True`

### Step 9: Enter Combine Mode
- Select Combine Mode from the menu
- Currently shows a placeholder: "Coming soon..."
- **Awaiting user instructions for Combine Mode functionality**

## Technical Details

### Global Tracker
```python
secret_hack = {
    'sheep_mode_played': False,
    'whoppa_gang_entered': False,
    'music_still_playing': False,
    'skibidi_triggered': False,
    'wolf_ate_buttons': False,
    'grass_mode_unlocked': False,
    'combine_mode_unlocked': False,
    'entered_battle_after_music': False
}
```

### Key Features
- **Sequential Unlocking**: Each step requires previous steps to be completed
- **Visual Feedback**: Animations for wolf eating/vomiting buttons
- **Menu Blocking**: When wolf eats buttons, all standard game modes are blocked
- **Dynamic Menu**: Grass Mode and Combine Mode appear only when unlocked

### Code Locations
- **Main tracker**: Lines 21-30 (global `secret_hack` dictionary)
- **Battle Mode hack**: `run_game_with_upgrades()` function
- **Main menu hacks**: `mode_lobby()` function  
- **Wolf animations**: `wolf_eat_animation()` and `wolf_vomit_animation()` functions
- **New modes**: `grass_mode()` and `combine_mode()` functions

## Notes
- The hack sequence is robust and cannot be triggered out of order
- Normal cheat codes still work if hack conditions aren't met
- All animations are smooth and provide clear visual feedback
- Combine Mode is ready for your next instructions!
