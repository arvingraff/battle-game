# Audio Configuration Guide

## Music Tracks by Game Mode

### 🎵 Battle Mode
**File:** `fart.mp3`
- Plays during all battle phases
- Loops continuously
- Intense combat music

### 💰 Coin Collection Mode
**File:** `coin.mp3`
- Plays during the 30-second coin collection phase
- Loops continuously
- Upbeat collection music
- Automatically stops when entering shop phase

### 🛒 Shop Phase
**Music:** Continues with `coin.mp3` or transitions to battle music
- After shop, transitions to battle music when battle starts

### 🎬 Video Features
- **Cute Video:** Uses its own embedded audio
- **Grandma Video:** Uses its own embedded audio

## Audio File Requirements

### Expected Files in Game Directory:
1. `fart.mp3` - Battle mode background music
2. `coin.mp3` - Coin collection mode music
3. `coolwav.mp3` - (If used for other features)

### Technical Details
- **Format:** MP3
- **Looping:** All game music loops with `-1` parameter
- **Volume:** Default pygame mixer volume
- **Error Handling:** Game continues if audio file is missing (prints error message)

## Music Behavior

### Mode Transitions
1. **Main Menu → Battle Mode**
   - Stops any playing music
   - Loads and plays `fart.mp3`

2. **Main Menu → Coin Collection Mode**
   - Stops any playing music
   - Loads and plays `coin.mp3`

3. **Coin Collection → Shop**
   - Music continues playing

4. **Shop → Battle**
   - Stops `coin.mp3`
   - Loads and plays `fart.mp3`

5. **Battle → Main Menu**
   - Stops battle music
   - Silent in menu

### Manual Control
- **Play Music:** Option in main menu to start music
- **Stop Music:** Option in main menu to stop music
- Both options toggle music for testing/preference

## Implementation Notes

### Code Locations
- **Battle Music:** Set in `run_game_with_upgrades()` function
- **Coin Music:** Set in `run_coin_collection_and_shop()` function
- **Manual Control:** In `mode_lobby()` menu options

### Error Handling
```python
try:
    pygame.mixer.music.stop()
    pygame.mixer.music.load('coin.mp3')
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Error playing coin collection music: {e}")
```

## User Experience

### What Players Hear:
- ✅ **Battle Mode:** Intense combat soundtrack
- ✅ **Coin Collection:** Fun, upbeat collection music
- ✅ **Smooth Transitions:** No audio gaps between modes
- ✅ **Consistent Volume:** Balanced across all tracks
- ✅ **Loop Quality:** Seamless music loops

## Troubleshooting

### No Audio Playing?
1. Check that audio files exist in game directory
2. Verify file names match exactly (case-sensitive)
3. Ensure files are valid MP3 format
4. Check system audio is not muted
5. Look for error messages in console

### Audio Cuts Off?
- This is intentional when switching modes
- Music stops before loading new track
- Prevents audio overlap

### Want Different Music?
- Replace MP3 files with same filenames
- Keep same format (MP3)
- Maintain reasonable file sizes
- Test loop points for seamless playback

## Future Enhancements

### Potential Additions:
- 🎵 Unique shop music
- 🎵 Victory/defeat music stings
- 🎵 Menu background music
- 🎵 Survival mode music
- 🔊 Sound effects for:
  - Shooting
  - Coin collection
  - Weapon switching
  - Shop purchases
  - Character selection

---

**Current Status:** ✅ Coin Collection Mode now uses `coin.mp3` music!
