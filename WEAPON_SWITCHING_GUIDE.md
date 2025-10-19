# Weapon Switching Guide - Coin Collection Mode Battle

## Overview
I've successfully implemented **manual weapon switching** in Coin Collection Mode battle! Players can now press buttons to switch between different weapons, and the weapon graphics update immediately on screen.

## How It Works

### Player 1 Controls
- **Q** = Switch to Default weapon (AK-47 style)
- **E** = Switch to Bazooka (if you have bazooka ammo)
- **R** = Switch to Kannon (if you have kannon ammo)
- **SPACE** = Fire current weapon

### Player 2 Controls
- **O** = Switch to Default weapon (AK-47 style)
- **P** = Switch to Bazooka (if you have bazooka ammo)
- **L** = Switch to Kannon (if you have kannon ammo)
- **RIGHT SHIFT** = Fire current weapon

## Weapon Visuals

### Default Weapon (AK-47 Style)
- Gray metal body with brown wooden stock
- Classic assault rifle appearance
- Unlimited ammo
- 1 damage per shot

### Bazooka
- Large green tube with orange/yellow tip
- Brown handle grip
- 2 damage per shot
- Limited ammo (purchased in shop)

### Kannon
- Large gray barrel with gold/yellow tip
- Gray handle grip
- 3 damage per shot
- Limited ammo (purchased in shop)

## Visual Feedback

The game provides **real-time visual feedback**:

1. **Weapon Graphics**: The weapon held by your character changes instantly when you press Q/E/R (P1) or O/P/L (P2)
2. **On-Screen Display**: Bottom of screen shows:
   - "P1 Weapon: DEFAULT" / "BAZOOKA" / "KANNON"
   - "P2 Weapon: DEFAULT" / "BAZOOKA" / "KANNON"
3. **Ammo Counter**: Top of screen shows remaining bazooka and kannon shots
4. **Instructions**: Bottom of screen shows the control keys

## How to Use in Game

1. **Play Coin Collection Mode** from the main menu
2. **Collect coins** to earn money (30 seconds)
3. **Shop Phase**: Buy bazookas (10 coins), kannons (20 coins), or extra lives (10 coins)
4. **Battle Phase**: 
   - Press Q/E/R (P1) or O/P/L (P2) to switch weapons
   - Watch your character's weapon change on screen
   - Fire with SPACE (P1) or RIGHT SHIFT (P2)
   - When you run out of special ammo, switch back to default with Q or O

## Technical Details

- Weapons switch **instantly** on button press
- You can switch weapons **even while moving**
- Each weapon has **distinct visual appearance**
- Weapon selection is **tracked separately** for each player
- Can't select bazooka/kannon if you have 0 ammo left
- Shooting consumes ammo from currently selected weapon

## Tips

- **Save special weapons** for when you really need them!
- **Switch strategically** - use default to conserve ammo
- **Kannon is strongest** but most expensive - use wisely
- **Watch your ammo counter** to know when to switch back to default
- **Default weapon never runs out** - it's always available

Enjoy the enhanced weapon system! 🎮🔫💥
