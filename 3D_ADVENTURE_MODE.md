# 3D Adventure Mode - Feature Documentation

## Overview
The **3D Adventure Mode** is a complex, fully-featured pseudo-3D dungeon crawler with ray-casting graphics, real-time combat, exploration, and RPG elements. This mode transforms the battle game into an immersive first-person adventure experience.

## Status
✅ **FULLY IMPLEMENTED AND WORKING** (Fixed December 2025)
- All code errors resolved
- Successfully integrated into main game
- Available from main menu via "3D Adventure" option
- Fully packaged in app bundle

## Core Features

### 🎮 Gameplay Mechanics

#### Ray-Casting 3D Rendering
- **First-person perspective** with smooth 3D view
- **Real-time ray-casting** engine (120 rays per frame)
- **Distance-based shading** for depth perception
- **Textured walls, doors, and obstacles**
- **Ceiling and floor rendering** with distinct colors
- **60 FPS performance** target

#### Movement System
- **WASD controls** for navigation
  - W: Move forward
  - S: Move backward
  - A: Rotate left
  - D: Rotate right
- **Collision detection** prevents walking through walls
- **Smooth rotation** with configurable speed
- **Realistic movement speed** balanced for exploration

#### Player Stats & Progression
- **Health System** (HP)
  - Starting: 100 HP
  - Maximum: Increases with level
  - Visual health bar in UI
- **Mana System** (MP)
  - Starting: 50 MP
  - Maximum: 50 MP
  - Reserved for future magic abilities
- **Experience Points (EXP)**
  - Gain 20 EXP per enemy defeated
  - Level up at: Current Level × 100 EXP
- **Level System**
  - Start at Level 1
  - Each level grants +20 max HP
  - Full HP restore on level up
- **Gold Currency**
  - Earned from treasures and enemies
  - +10 gold per enemy defeated
  - Variable amounts from treasure chests
- **Inventory System**
  - Collect items from treasures
  - Equipment tracking (weapons, potions, etc.)
  - Currently equipped weapon display

### 🗺️ World Design

#### Map Layout (16×16 Grid)
The world features a complex dungeon with multiple rooms and corridors:
- **Walls (1)** - Impassable stone barriers
- **Open Floor (0)** - Walkable space
- **Doors (2)** - Can be opened with 'E' key
- **Treasure Chests (3)** - Contain valuable items
- **Enemies (4)** - Hostile creatures to defeat
- **NPCs (5)** - Friendly characters with dialogue
- **Portals (6)** - Reserved for future teleportation

#### Interactive Elements

**Doors**
- Locked initially
- Press 'E' to open
- Visual feedback on interaction
- Converts to open floor when unlocked

**Treasure Chests**
4 treasure locations with unique rewards:
1. **Gold Sword** - Enhanced weapon (14, 1)
2. **50 Gold** - Currency boost (2, 6)
3. **Health Potion** - HP restoration (10, 9)
4. **Magic Staff** - Magical weapon (6, 14)

**NPCs**
- **Elder** (2, 2): "Welcome hero! Seek the ancient treasures."
- **Merchant** (14, 10): "I have potions for sale!"
- Dialogue appears as on-screen messages
- Interaction range: 1.5 units

### ⚔️ Combat System

#### Enemy Types & Stats
1. **Goblin** (10.5, 4.5)
   - Health: 30 HP
   - Type: Melee fighter
   - Red sprite indicator

2. **Orc** (14.5, 6.5)
   - Health: 40 HP
   - Type: Tough warrior
   - Red sprite indicator

3. **Skeleton** (1.5, 9.5)
   - Health: 25 HP
   - Type: Undead minion
   - Red sprite indicator

4. **Dragon** (12.5, 12.5)
   - Health: 50 HP
   - Type: Boss enemy
   - Red sprite indicator

#### Combat Mechanics
- **Auto-targeting**: Nearest enemy within 2 units
- **Attack Key**: SPACE bar to attack
- **Damage Formula**: 10 + (Player Level × 5)
- **Combat Feedback**: Damage numbers and messages
- **Defeat Rewards**: +20 EXP, +10 Gold per enemy
- **Enemy Respawn**: No respawning (permanent defeat)

### 🎨 User Interface

#### HUD Elements
**Top Left:**
- Health bar (red) with current/max HP
- Mana bar (blue) with current/max MP
- Visual bar fill indicates percentage

**Top Right:**
- Current Level
- EXP progress (current/required)
- Gold count
- Equipped weapon name

**Center Screen:**
- Combat indicator when enemy is near
- Enemy name and health display
- Attack prompt: "Press SPACE to attack!"

**Bottom Center:**
- Message display area
- Interaction feedback
- Loot notifications
- Quest updates (future)

**Bottom:**
- Control hints bar
- Always visible for player reference

#### Mini-Map (Toggle with 'M')
- **200×200 pixel overlay** (top right)
- **Grid representation** of dungeon
- **Color coding:**
  - Gray: Walls
  - Brown: Doors
  - Gold: Treasures
  - Green: NPCs
  - Dark: Empty space
- **Player indicator**: Red dot with direction line
- **Enemy markers**: Red dots
- **Real-time updates** with player movement

### 🎯 Sprite Rendering

#### 3D Sprite System
- **Billboard sprites** always face player
- **Painter's algorithm** sorting (far to near)
- **Distance-based sizing** for perspective
- **Smooth screen positioning** based on angle
- **Color indicators** by sprite type:
  - Red circles: Enemies
  - Gold circles: Treasures
  - Green circles: NPCs

#### Sprite Visibility
- **Maximum draw distance**: 16 units
- **Field of view check**: Only visible sprites rendered
- **Occlusion**: Sprites behind walls are hidden
- **Depth shading**: Darker sprites appear further away

### 🎮 Controls Reference

| Key | Action |
|-----|--------|
| W | Move Forward |
| S | Move Backward |
| A | Rotate Left |
| D | Rotate Right |
| E | Interact (open doors, loot chests, talk to NPCs) |
| SPACE | Attack (when enemy is nearby) |
| M | Toggle Mini-Map |
| ESC | Exit to Main Menu |

### 📊 Game Progression

#### Starting Conditions
- Spawn position: (5.0, 5.0)
- Facing direction: 0.0 radians (East)
- Starting level: 1
- Starting health: 100 HP
- Starting mana: 50 MP
- Starting gold: 0
- Starting weapon: Sword

#### Objectives
1. **Explore the dungeon** - Navigate the maze
2. **Defeat all enemies** - 4 unique enemy types
3. **Collect treasures** - 4 hidden chests
4. **Talk to NPCs** - Learn about the world
5. **Level up** - Gain strength through combat
6. **Find the portal** - Ultimate goal (future update)

### 🔧 Technical Specifications

#### Performance
- **Target FPS**: 60
- **Ray Count**: 120 rays per frame
- **Maximum Depth**: 16.0 units
- **Field of View**: π/3 radians (~60 degrees)
- **Move Speed**: 3.0 units/second
- **Rotation Speed**: 3.0 radians/second

#### Graphics Settings
- **Screen Resolution**: Fullscreen (adaptive)
- **3D View**: Ray-casting with distance shading
- **Ceiling Color**: (50, 50, 80) - Dark blue
- **Floor Color**: (40, 60, 40) - Dark green
- **Wall Shading**: Distance-based (0-255)
- **UI Background**: (20, 20, 30) - Dark gray-blue

#### Message System
- **Display Duration**: 2-4 seconds (context-dependent)
- **Message Types**: Combat, loot, interaction, level-up
- **Visual Style**: Large yellow text with dark background
- **Fade Out**: Automatic after timer expires

### 🎨 Visual Effects

#### Lighting & Shading
- **Distance fog**: Objects fade with distance
- **Wall shading**: Darker walls at greater distances
- **Sprite darkening**: Consistent depth perception
- **Color variation**: Different tiles have unique colors

#### Animation Elements
- **Smooth rotation**: No frame skipping
- **Fluid movement**: Delta-time based updates
- **Sprite scaling**: Real-time size adjustments
- **UI animations**: Bar fills, message fades

### 🚀 Future Enhancements (Planned)

#### Potential Additions
- [ ] **Magic System**: Use mana for spells
- [ ] **Quest System**: Track multiple objectives
- [ ] **Boss Battles**: Enhanced enemy encounters
- [ ] **Merchant System**: Buy/sell items
- [ ] **Portal Network**: Fast travel between areas
- [ ] **Multiple Dungeons**: Expanded world
- [ ] **Save/Load System**: Persistent progress
- [ ] **Sound Effects**: Combat and ambient audio
- [ ] **Music Tracks**: Dynamic background music
- [ ] **Particle Effects**: Spell casting, hits
- [ ] **Item Drops**: Random loot from enemies
- [ ] **Character Classes**: Different playstyles
- [ ] **Difficulty Settings**: Easy, Normal, Hard

### 📝 Code Architecture

#### Main Function: `adventure_3d_mode()`
- Located at global scope in `battlegame.py`
- Self-contained game loop
- No external dependencies except pygame/math
- Clean exit back to main menu

#### Key Data Structures
```python
player = {
    'x': float,           # X position
    'y': float,           # Y position
    'angle': float,       # Facing direction (radians)
    'health': int,        # Current HP
    'max_health': int,    # Maximum HP
    'mana': int,          # Current MP
    'max_mana': int,      # Maximum MP
    'inventory': list,    # Items collected
    'equipped_weapon': str,  # Current weapon
    'gold': int,          # Currency
    'level': int,         # Experience level
    'exp': int,           # Experience points
    'quests': list        # Active quests (future)
}

world_map = [[int]]      # 16×16 grid of tile types
enemies = [dict]         # List of enemy objects
npcs = [dict]            # List of NPC objects
treasures = [dict]       # List of treasure objects
sprites = [dict]         # Rendered sprite list
```

## Conclusion

The 3D Adventure Mode is a **fully-featured dungeon crawler** that demonstrates advanced game development techniques including ray-casting, sprite rendering, combat systems, and RPG progression. It provides a compelling alternative gameplay experience within the BattleGame project.

**Status**: ✅ Production Ready
**Accessibility**: Main Menu → "3D Adventure"
**Platform**: macOS (packaged app)
**Last Updated**: December 2025
