import pygame
import sys
import os
import time
import random
import threading
import math
import socket
import json
from network import NetworkHost, NetworkClient

pygame.init()

# Helper function to get the actual local IP address (not 127.0.0.1)
def get_local_ip():
    """Get the actual local network IP address"""
    try:
        # Method 1: Connect to external address to find which interface is used
        # This doesn't actually send data, just determines routing
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        # Connect to Google DNS (doesn't matter if unreachable)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            # Method 2: Get hostname IP (fallback)
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            # If we get localhost, try to find a better IP
            if local_ip.startswith('127.'):
                # Method 3: Check all network interfaces
                for info in socket.getaddrinfo(hostname, None):
                    ip = info[4][0]
                    if not ip.startswith('127.') and ':' not in ip:  # Skip localhost and IPv6
                        return ip
            return local_ip
        except Exception:
            return "127.0.0.1"  # Last resort fallback

# Helper function to get the correct path for bundled files
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Leaderboard functions
def load_highscores(mode='survival'):
    """Load high scores from JSON file"""
    filename = 'mom_mode_highscores.json' if mode == 'mom' else 'survival_highscores.json'
    try:
        with open(resource_path(filename), 'r') as f:
            return json.load(f)
    except:
        return []

def save_highscore(name, score, mode='survival', extra_data=None):
    """Save a new high score"""
    filename = 'mom_mode_highscores.json' if mode == 'mom' else 'survival_highscores.json'
    
    # Load existing scores
    scores = load_highscores(mode)
    
    # Create new score entry
    new_entry = {
        'name': name,
        'score': score,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add extra data if provided
    if extra_data:
        new_entry.update(extra_data)
    
    # Add to list
    scores.append(new_entry)
    
    # Sort by score (descending)
    scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Keep only top 10
    scores = scores[:10]
    
    # Save back to file
    try:
        with open(resource_path(filename), 'w') as f:
            json.dump(scores, f, indent=2)
    except:
        pass  # If can't write (in bundled app), that's okay
    
    return scores

def show_leaderboard(mode='survival'):
    """Display the leaderboard for survival or mom mode"""
    scores = load_highscores(mode)
    
    title = "ESCAPE MOM MODE - LEADERBOARD" if mode == 'mom' else "SURVIVAL MODE - LEADERBOARD"
    title_color = (255, 50, 50) if mode == 'mom' else (100, 200, 255)
    
    running = True
    while running:
        screen.fill((20, 20, 30))
        
        # Title
        title_text = lobby_font.render(title, True, title_color)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
        
        # Column headers
        if mode == 'mom':
            headers = font.render("RANK    NAME              TIME SURVIVED", True, (200, 200, 200))
        else:
            headers = font.render("RANK    NAMES             SCORE    LEVEL", True, (200, 200, 200))
        screen.blit(headers, (WIDTH//2 - headers.get_width()//2, 150))
        
        # Scores
        if scores:
            for i, entry in enumerate(scores):
                y_pos = 220 + i * 50
                rank = f"#{i+1}"
                
                if mode == 'mom':
                    name = entry.get('name', 'Unknown')[:15]
                    score_val = entry.get('score', 0)
                    score_text = f"{score_val}s"
                    line = f"{rank:<8}{name:<18}{score_text}"
                else:
                    names = entry.get('names', entry.get('name', 'Unknown'))[:15]
                    score_val = entry.get('score', 0)
                    level = entry.get('level', 1)
                    line = f"{rank:<8}{names:<18}{score_val:<9}{level}"
                
                # Color based on rank
                if i == 0:
                    color = (255, 215, 0)  # Gold
                elif i == 1:
                    color = (192, 192, 192)  # Silver
                elif i == 2:
                    color = (205, 127, 50)  # Bronze
                else:
                    color = (180, 180, 180)  # White
                
                score_text_render = font.render(line, True, color)
                screen.blit(score_text_render, (WIDTH//2 - score_text_render.get_width()//2, y_pos))
        else:
            # No scores yet
            no_scores = font.render("No scores yet! Be the first!", True, (150, 150, 150))
            screen.blit(no_scores, (WIDTH//2 - no_scores.get_width()//2, 300))
        
        # Back button
        back_button = pygame.Rect(WIDTH//2 - 100, HEIGHT - 120, 200, 60)
        pygame.draw.rect(screen, (100, 50, 150), back_button)
        pygame.draw.rect(screen, (150, 100, 200), back_button, 3)
        back_text = font.render("Back", True, (255, 255, 255))
        screen.blit(back_text, (back_button.centerx - back_text.get_width()//2, 
                                back_button.centery - back_text.get_height()//2))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    running = False

def adventure_3d_mode():
    """Complex 3D adventure mode with exploration, combat, quests, and items"""
    
    # Show tutorial/intro first
    show_tutorial = True
    tutorial_page = 0
    tutorial_pages = [
        {
            'title': 'WELCOME TO THE DUNGEON',
            'text': [
                'You are a brave hero who has entered',
                'the cursed dungeon of the Dark Lord.',
                '',
                'Your quest: Defeat all 4 evil creatures,',
                'collect the 4 ancient treasures,',
                'and escape through the magic portal!',
                '',
                'Press ENTER to continue...'
            ]
        },
        {
            'title': 'CONTROLS',
            'text': [
                'W - Move Forward',
                'S - Move Backward',
                'A - Turn Left',
                'D - Turn Right',
                '',
                'E - Interact (doors, chests, NPCs)',
                'SPACE - Attack enemies',
                'M - Toggle Map',
                '',
                'Press ENTER to start adventure...'
            ]
        }
    ]
    
    while show_tutorial:
        screen.fill((10, 10, 20))
        
        page = tutorial_pages[tutorial_page]
        
        # Title
        title = lobby_font.render(page['title'], True, (255, 200, 100))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # Text content
        y_offset = 220
        for line in page['text']:
            if line:
                text = font.render(line, True, (220, 220, 220))
                screen.blit(text, (WIDTH//2 - text.get_width()//2, y_offset))
            y_offset += 40
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    tutorial_page += 1
                    if tutorial_page >= len(tutorial_pages):
                        show_tutorial = False
                if event.key == pygame.K_ESCAPE:
                    return
    
    # Player state
    player = {
        'x': 5.0,
        'y': 5.0,
        'angle': 0.0,
        'health': 100,
        'max_health': 100,
        'mana': 50,
        'max_mana': 50,
        'inventory': [],
        'equipped_weapon': 'Rusty Sword',
        'gold': 0,
        'level': 1,
        'exp': 0,
        'quests': [
            {'name': 'Defeat 4 Monsters', 'progress': 0, 'target': 4, 'complete': False},
            {'name': 'Collect 4 Treasures', 'progress': 0, 'target': 4, 'complete': False},
            {'name': 'Find the Portal', 'progress': 0, 'target': 1, 'complete': False}
        ]
    }
            
    # World map (1 = wall, 0 = floor, 2 = door, 3 = treasure, 4 = enemy, 5 = NPC, 6 = portal)
    world_map = [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,1,0,0,0,0,0,0,0,3,1],
        [1,0,5,0,1,0,1,0,1,1,1,1,1,0,0,1],
        [1,0,0,0,1,0,0,0,0,0,0,0,1,0,0,1],
        [1,1,2,1,1,0,1,1,1,0,4,0,1,0,0,1],
        [1,0,0,0,0,0,1,0,0,0,1,1,1,0,0,1],
        [1,0,3,0,1,0,2,0,1,0,0,0,0,0,4,1],
        [1,0,0,0,1,0,1,0,1,1,1,1,1,1,1,1],
        [1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,1],
        [1,4,0,0,0,0,1,1,1,0,3,0,1,0,0,1],
        [1,0,0,1,1,0,1,0,0,0,1,0,1,0,5,1],
        [1,0,0,0,0,0,2,0,1,0,1,0,0,0,0,1],
        [1,0,4,0,1,0,1,0,1,0,0,0,1,1,1,1],
        [1,0,0,0,1,0,0,0,0,0,1,0,0,0,6,1],
        [1,0,0,0,1,0,3,0,1,0,1,0,4,0,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ]
    
    # Enemies with detailed stats
    enemies = [
        {
            'x': 10.5, 'y': 4.5, 'health': 30, 'max_health': 30,
            'type': 'goblin', 'alive': True, 'name': 'Cave Goblin',
            'color': (100, 180, 100), 'damage': 8, 'gold_drop': 15,
            'description': 'A small but fierce creature'
        },
        {
            'x': 14.5, 'y': 6.5, 'health': 50, 'max_health': 50,
            'type': 'orc', 'alive': True, 'name': 'Brutal Orc',
            'color': (150, 100, 80), 'damage': 12, 'gold_drop': 25,
            'description': 'A powerful warrior from the north'
        },
        {
            'x': 1.5, 'y': 9.5, 'health': 35, 'max_health': 35,
            'type': 'skeleton', 'alive': True, 'name': 'Undead Warrior',
            'color': (200, 200, 200), 'damage': 10, 'gold_drop': 20,
            'description': 'An ancient skeleton brought to life'
        },
        {
            'x': 12.5, 'y': 12.5, 'health': 80, 'max_health': 80,
            'type': 'dragon', 'alive': True, 'name': 'Shadow Dragon',
            'color': (180, 50, 50), 'damage': 20, 'gold_drop': 50,
            'description': 'The dungeon boss - approach with caution!'
        }
    ]
    
    # NPCs with quests
    npcs = [
        {
            'x': 2.5, 'y': 2.5, 'name': 'Wise Elder', 
            'dialogue': [
                'Greetings, brave hero!',
                'Four evil creatures plague this dungeon.',
                'Defeat them all and find the treasures.',
                'Only then can you escape through the portal!',
                'May fortune guide your blade.'
            ],
            'talked': False
        },
        {
            'x': 14.5, 'y': 10.5, 'name': 'Mysterious Merchant',
            'dialogue': [
                'Ah, a customer in this dark place!',
                'I would sell you potions, but alas...',
                'The monsters took all my wares!',
                'Find the health potions in the chests.',
                'Good luck, you will need it!'
            ],
            'talked': False
        }
    ]
    
    # Treasures with better descriptions
    treasures = [
        {
            'x': 14.5, 'y': 1.5, 'opened': False, 
            'contents': 'Golden Sword', 'type': 'weapon',
            'description': 'A magnificent blade that glows with power!',
            'bonus': 'Damage +10'
        },
        {
            'x': 2.5, 'y': 6.5, 'opened': False,
            'contents': '50 Gold', 'type': 'gold',
            'description': 'A chest full of ancient coins!',
            'bonus': '+50 Gold'
        },
        {
            'x': 10.5, 'y': 9.5, 'opened': False,
            'contents': 'Health Potion', 'type': 'potion',
            'description': 'A glowing red potion that restores vitality!',
            'bonus': 'HP +30 immediately'
        },
        {
            'x': 6.5, 'y': 14.5, 'opened': False,
            'contents': 'Mystic Staff', 'type': 'weapon',
            'description': 'A staff crackling with magical energy!',
            'bonus': 'Damage +15, Mana +20'
        }
    ]
    
    clock = pygame.time.Clock()
    move_speed = 3.5
    rot_speed = 3.0
    fov = math.pi / 3
    max_depth = 20.0
    
    # Enhanced UI colors
    ui_bg = (15, 15, 25)
    ui_border = (120, 120, 180)
    health_color = (220, 40, 40)
    mana_color = (40, 120, 220)
    exp_color = (255, 200, 50)
    
    # Visual effects
    damage_numbers = []  # Floating damage numbers
    hit_flash = 0  # Screen flash on hit
    footstep_sound_timer = 0
    
    # Quest tracking
    show_quest_panel = False
    portal_revealed = False
    
    running = True
    show_map = False
    message = ""
    message_timer = 0
    combat_target = None
    dialogue_lines = []
    dialogue_timer = 0
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Update timers
        if message_timer > 0:
            message_timer -= dt
            if message_timer <= 0:
                message = ""
        
        if dialogue_timer > 0:
            dialogue_timer -= dt
            if dialogue_timer <= 0:
                dialogue_lines = []
        
        if hit_flash > 0:
            hit_flash -= dt * 5
        
        # Update damage numbers
        for dmg in damage_numbers[:]:
            dmg['timer'] -= dt
            dmg['y'] -= dt * 50
            if dmg['timer'] <= 0:
                damage_numbers.remove(dmg)
        
        # Handle input
        keys = pygame.key.get_pressed()
        
        # Movement with collision
        move_x, move_y = 0, 0
        moved = False
        if keys[pygame.K_w]:
            move_x = math.cos(player['angle']) * move_speed * dt
            move_y = math.sin(player['angle']) * move_speed * dt
            moved = True
        if keys[pygame.K_s]:
            move_x = -math.cos(player['angle']) * move_speed * dt
            move_y = -math.sin(player['angle']) * move_speed * dt
            moved = True
        if keys[pygame.K_a]:
            player['angle'] -= rot_speed * dt
        if keys[pygame.K_d]:
            player['angle'] += rot_speed * dt
        
        # Collision detection
        new_x = player['x'] + move_x
        new_y = player['y'] + move_y
        map_x = int(new_x)
        map_y = int(new_y)
        
        if 0 <= map_x < len(world_map[0]) and 0 <= map_y < len(world_map):
            if world_map[map_y][map_x] not in [1, 2]:  # Not a wall or door
                player['x'] = new_x
                player['y'] = new_y
        
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_m:
                    show_map = not show_map
                if event.key == pygame.K_q:
                    show_quest_panel = not show_quest_panel
                if event.key == pygame.K_e:
                    # Interact with objects
                    check_x = player['x'] + math.cos(player['angle']) * 1.5
                    check_y = player['y'] + math.sin(player['angle']) * 1.5
                    cx, cy = int(check_x), int(check_y)
                    
                    if 0 <= cx < len(world_map[0]) and 0 <= cy < len(world_map):
                        tile = world_map[cy][cx]
                        if tile == 2:  # Door
                            world_map[cy][cx] = 0
                            message = "✓ Unlocked a mysterious door!"
                            message_timer = 2.0
                        elif tile == 3:  # Treasure
                            for treasure in treasures:
                                if int(treasure['x']) == cx and int(treasure['y']) == cy and not treasure['opened']:
                                    treasure['opened'] = True
                                    
                                    # Apply treasure effects
                                    if treasure['type'] == 'weapon':
                                        player['equipped_weapon'] = treasure['contents']
                                        message = f"⚔ Equipped: {treasure['contents']}!"
                                    elif treasure['type'] == 'gold':
                                        amount = int(treasure['contents'].split()[0])
                                        player['gold'] += amount
                                        message = f"💰 Found {amount} Gold!"
                                    elif treasure['type'] == 'potion':
                                        player['health'] = min(player['max_health'], player['health'] + 30)
                                        message = f"❤ Health Restored! Found {treasure['contents']}"
                                    
                                    player['inventory'].append(treasure['contents'])
                                    
                                    # Update quest
                                    for quest in player['quests']:
                                        if 'Treasure' in quest['name'] and not quest['complete']:
                                            quest['progress'] += 1
                                            if quest['progress'] >= quest['target']:
                                                quest['complete'] = True
                                                message = "🎉 Quest Complete: Collect 4 Treasures!"
                                                message_timer = 4.0
                                    
                                    message_timer = 3.0
                                    world_map[cy][cx] = 0
                                    
                                    # Show treasure details
                                    dialogue_lines = [
                                        f"═══ {treasure['contents'].upper()} ═══",
                                        treasure['description'],
                                        f"Bonus: {treasure['bonus']}"
                                    ]
                                    dialogue_timer = 5.0
                        elif tile == 5:  # NPC
                            for npc in npcs:
                                if int(npc['x']) == cx and int(npc['y']) == cy:
                                    if not npc['talked']:
                                        npc['talked'] = True
                                        dialogue_lines = [f"═══ {npc['name']} ═══"] + npc['dialogue']
                                        dialogue_timer = 8.0
                                    else:
                                        message = f"{npc['name']}: Good luck on your journey!"
                                        message_timer = 2.0
                        elif tile == 6:  # Portal
                            # Check if all quests complete
                            all_complete = all(q['complete'] for q in player['quests'])
                            if all_complete:
                                dialogue_lines = [
                                    "═══ VICTORY! ═══",
                                    "You have completed all quests!",
                                    "The portal glows with energy...",
                                    "You escape the cursed dungeon!",
                                    "",
                                    "Press ESC to return to menu"
                                ]
                                dialogue_timer = 999
                            else:
                                message = "⚠ The portal is sealed! Complete all quests first."
                                message_timer = 3.0
                
                if event.key == pygame.K_SPACE:
                    # Attack
                    if combat_target and combat_target['alive']:
                        # Calculate damage based on weapon
                        base_damage = 10 + player['level'] * 5
                        if 'Golden Sword' in player['equipped_weapon']:
                            base_damage += 10
                        elif 'Mystic Staff' in player['equipped_weapon']:
                            base_damage += 15
                        
                        damage = base_damage + random.randint(-2, 5)
                        combat_target['health'] -= damage
                        
                        # Add floating damage number
                        damage_numbers.append({
                            'x': WIDTH // 2,
                            'y': HEIGHT // 3,
                            'damage': damage,
                            'timer': 1.5,
                            'color': (255, 100, 100)
                        })
                        
                        hit_flash = 0.3
                        
                        message = f"⚔ Hit {combat_target['name']} for {damage} damage!"
                        message_timer = 1.5
                        
                        if combat_target['health'] <= 0:
                            combat_target['alive'] = False
                            exp_gain = 20 + player['level'] * 5
                            gold_gain = combat_target.get('gold_drop', 10)
                            player['exp'] += exp_gain
                            player['gold'] += gold_gain
                            
                            message = f"💀 Defeated {combat_target['name']}! +{exp_gain} EXP, +{gold_gain} Gold"
                            message_timer = 3.0
                            combat_target = None
                            
                            # Update quest
                            for quest in player['quests']:
                                if 'Monster' in quest['name'] and not quest['complete']:
                                    quest['progress'] += 1
                                    if quest['progress'] >= quest['target']:
                                        quest['complete'] = True
                                        message = "🎉 Quest Complete: Defeat 4 Monsters!"
                                        message_timer = 4.0
                                        # Reveal portal
                                        portal_revealed = True
                                        for quest2 in player['quests']:
                                            if 'Portal' in quest2['name']:
                                                quest2['progress'] = 1
                            
                            # Level up check
                            if player['exp'] >= player['level'] * 100:
                                player['level'] += 1
                                player['max_health'] += 20
                                player['health'] = player['max_health']
                                dialogue_lines = [
                                    "✨ LEVEL UP! ✨",
                                    f"You are now Level {player['level']}!",
                                    f"Max Health: {player['max_health']}",
                                    "You feel stronger!"
                                ]
                                dialogue_timer = 4.0
                        else:
                            # Enemy counter-attack
                            enemy_damage = combat_target.get('damage', 5)
                            player['health'] -= enemy_damage
                            damage_numbers.append({
                                'x': WIDTH // 2,
                                'y': HEIGHT // 2,
                                'damage': enemy_damage,
                                'timer': 1.5,
                                'color': (255, 50, 50)
                            })
                            hit_flash = 0.5
                            
                            if player['health'] <= 0:
                                dialogue_lines = [
                                    "💀 GAME OVER 💀",
                                    "You have been defeated...",
                                    "The dungeon claims another victim.",
                                    "",
                                    "Press ESC to return to menu"
                                ]
                                dialogue_timer = 999
        
        # Check for nearby enemies
        combat_target = None
        for enemy in enemies:
            if enemy['alive']:
                dist = math.sqrt((enemy['x'] - player['x'])**2 + (enemy['y'] - player['y'])**2)
                if dist < 2.5:
                    combat_target = enemy
                    break
        
        # === RENDER 3D VIEW ===
        # Draw gradient sky/ceiling
        for i in range(HEIGHT//2):
            shade = int(30 + (i / (HEIGHT//2)) * 50)
            pygame.draw.line(screen, (shade, shade, shade + 30), (0, i), (WIDTH, i))
        
        # Draw gradient floor
        for i in range(HEIGHT//2):
            shade = int(20 + (i / (HEIGHT//2)) * 40)
            pygame.draw.line(screen, (shade, shade + 20, shade), (0, HEIGHT//2 + i), (WIDTH, HEIGHT//2 + i))
        
        # Ray casting with enhanced graphics
        num_rays = 150
        for ray in range(num_rays):
            ray_angle = player['angle'] - fov / 2 + (ray / num_rays) * fov
            
            # Cast ray
            for depth in range(int(max_depth * 10)):
                test_depth = depth / 10.0
                test_x = player['x'] + math.cos(ray_angle) * test_depth
                test_y = player['y'] + math.sin(ray_angle) * test_depth
                
                tx, ty = int(test_x), int(test_y)
                
                if 0 <= tx < len(world_map[0]) and 0 <= ty < len(world_map):
                    if world_map[ty][tx] == 1:  # Wall
                        # Calculate wall height
                        distance = test_depth * math.cos(ray_angle - player['angle'])
                        wall_height = min(HEIGHT, int(HEIGHT / (distance + 0.0001) * 0.6))
                        
                        # Enhanced wall shading with texture-like effect
                        shade = max(30, 255 - int(distance * 15))
                        
                        # Add fake brick pattern
                        brick_offset = int((test_x + test_y) * 2) % 2
                        brick_shade = shade - brick_offset * 20
                        
                        # Different shades for N/S vs E/W walls
                        if abs(math.cos(ray_angle)) > abs(math.sin(ray_angle)):
                            color = (brick_shade // 2, brick_shade // 2, brick_shade // 1.5)
                        else:
                            color = (brick_shade // 2.5, brick_shade // 2.5, brick_shade // 1.8)
                        
                        wall_top = HEIGHT // 2 - wall_height // 2
                        wall_bottom = HEIGHT // 2 + wall_height // 2
                        
                        x_pos = int(ray * (WIDTH / num_rays))
                        pygame.draw.line(screen, color, (x_pos, wall_top), (x_pos, wall_bottom), max(1, int(WIDTH / num_rays) + 1))
                        
                        # Add shadow at top and bottom of walls
                        shadow_color = tuple(c // 3 for c in color)
                        pygame.draw.line(screen, shadow_color, (x_pos, wall_top), (x_pos, wall_top + 2))
                        pygame.draw.line(screen, shadow_color, (x_pos, wall_bottom - 2), (x_pos, wall_bottom))
                        break
                    elif world_map[ty][tx] == 2:  # Door
                        distance = test_depth * math.cos(ray_angle - player['angle'])
                        wall_height = min(HEIGHT, int(HEIGHT / (distance + 0.0001) * 0.6))
                        shade = max(30, 220 - int(distance * 15))
                        # Wooden door color
                        color = (shade // 2, shade // 3, shade // 6)
                        
                        wall_top = HEIGHT // 2 - wall_height // 2
                        wall_bottom = HEIGHT // 2 + wall_height // 2
                        x_pos = int(ray * (WIDTH / num_rays))
                        pygame.draw.line(screen, color, (x_pos, wall_top), (x_pos, wall_bottom), max(1, int(WIDTH / num_rays) + 1))
                        
                        # Door handle in middle
                        if ray % 10 == 5:
                            handle_y = HEIGHT // 2
                            pygame.draw.circle(screen, (180, 150, 50), (x_pos, handle_y), 2)
                        break
        
        # Draw sprites (enemies, treasures, NPCs) with realistic colors
        sprites = []
        
        # Add enemies with their custom colors
        for enemy in enemies:
            if enemy['alive']:
                sprites.append({
                    'x': enemy['x'],
                    'y': enemy['y'],
                    'type': 'enemy',
                    'color': enemy['color'],
                    'data': enemy
                })
        
        # Add treasures
        for treasure in treasures:
            if not treasure['opened']:
                sprites.append({
                    'x': treasure['x'],
                    'y': treasure['y'],
                    'type': 'treasure',
                    'color': (255, 215, 0),
                    'data': treasure
                })
        
        # Add NPCs
        for npc in npcs:
            sprites.append({
                'x': npc['x'],
                'y': npc['y'],
                'type': 'npc',
                'color': (100, 200, 255),
                'data': npc
            })
        
        # Always show portal (but it looks different when sealed vs active)
        sprites.append({
            'x': 14.5,
            'y': 13.5,
            'type': 'portal',
            'color': (150, 100, 255) if portal_revealed else (80, 50, 100),  # Brighter when active
            'data': {'name': 'Portal (Active)' if portal_revealed else 'Sealed Portal'},
            'active': portal_revealed
        })
        
        # Sort sprites by distance (painter's algorithm)
        for sprite in sprites:
            dx = sprite['x'] - player['x']
            dy = sprite['y'] - player['y']
            sprite['distance'] = math.sqrt(dx*dx + dy*dy)
            sprite['angle'] = math.atan2(dy, dx) - player['angle']
        
        sprites.sort(key=lambda s: s['distance'], reverse=True)
        
        # Draw sprites with enhanced realism
        for sprite in sprites:
            if sprite['distance'] < max_depth:
                # Normalize angle
                angle = sprite['angle']
                while angle < -math.pi: angle += 2 * math.pi
                while angle > math.pi: angle -= 2 * math.pi
                
                if abs(angle) < fov / 2 + 0.5:
                    size = min(HEIGHT, int(HEIGHT / (sprite['distance'] + 0.0001) * 0.4))
                    screen_x = WIDTH // 2 + int((angle / (fov / 2)) * (WIDTH // 2))
                    screen_y = HEIGHT // 2
                    
                    shade = max(40, 255 - int(sprite['distance'] * 12))
                    color = tuple(int(c * shade / 255) for c in sprite['color'])
                    
                    # Draw sprite with more detail
                    if sprite['type'] == 'enemy':
                        # Body
                        pygame.draw.ellipse(screen, color, (screen_x - size//2, screen_y - size, size, size * 1.5))
                        # Head
                        head_color = tuple(min(255, c + 20) for c in color)
                        pygame.draw.circle(screen, head_color, (screen_x, screen_y - size - size//4), size//3)
                        # Eyes (red glow)
                        eye_size = max(2, size // 15)
                        pygame.draw.circle(screen, (255, 50, 50), (screen_x - size//8, screen_y - size - size//4), eye_size)
                        pygame.draw.circle(screen, (255, 50, 50), (screen_x + size//8, screen_y - size - size//4), eye_size)
                        # Health bar above enemy
                        if 'health' in sprite['data'] and 'max_health' in sprite['data']:
                            bar_width = size
                            bar_height = 4
                            bar_x = screen_x - bar_width // 2
                            bar_y = screen_y - size - size//2 - 15
                            # Background
                            pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
                            # Health
                            health_pct = sprite['data']['health'] / sprite['data']['max_health']
                            health_width = int(bar_width * health_pct)
                            health_bar_color = (255, 50, 50) if health_pct < 0.3 else (255, 200, 50) if health_pct < 0.7 else (50, 255, 50)
                            pygame.draw.rect(screen, health_bar_color, (bar_x, bar_y, health_width, bar_height))
                    
                    elif sprite['type'] == 'treasure':
                        # Chest shape with glow
                        glow_color = tuple(min(255, c + 50) for c in color)
                        pygame.draw.circle(screen, glow_color, (screen_x, screen_y - size//2), size//2 + 5, 2)
                        pygame.draw.rect(screen, color, (screen_x - size//2, screen_y - size//2, size, size//2))
                        pygame.draw.rect(screen, tuple(c // 2 for c in color), (screen_x - size//2, screen_y - size//2, size, size//2), 2)
                        # Lock
                        pygame.draw.circle(screen, (200, 180, 100), (screen_x, screen_y - size//4), max(2, size//10))
                    
                    elif sprite['type'] == 'npc':
                        # Friendly character
                        pygame.draw.ellipse(screen, color, (screen_x - size//3, screen_y - size, size//1.5, size * 1.5))
                        head_color = tuple(min(255, c + 30) for c in color)
                        pygame.draw.circle(screen, head_color, (screen_x, screen_y - size - size//4), size//3)
                        # Friendly eyes
                        pygame.draw.circle(screen, (50, 50, 50), (screen_x - size//10, screen_y - size - size//4), max(2, size//20))
                        pygame.draw.circle(screen, (50, 50, 50), (screen_x + size//10, screen_y - size - size//4), max(2, size//20))
                        # Speech bubble indicator
                        pygame.draw.circle(screen, (255, 255, 255), (screen_x + size//2, screen_y - size), max(3, size//8))
                        pygame.draw.circle(screen, color, (screen_x + size//2, screen_y - size), max(2, size//10))
                    
                    elif sprite['type'] == 'portal':
                        # Portal effect - different for sealed vs active
                        is_active = sprite.get('active', False)
                        
                        if is_active:
                            # Active portal: Bright swirling effect
                            time_offset = pygame.time.get_ticks() / 500
                            for i in range(3):
                                radius = size // 2 + int(math.sin(time_offset + i) * 10)
                                portal_color = tuple(int(c * (0.5 + i * 0.2)) for c in sprite['color'])
                                pygame.draw.circle(screen, portal_color, (screen_x, screen_y - size//2), radius, 3)
                            # Center glow - bright purple
                            pygame.draw.circle(screen, (200, 150, 255), (screen_x, screen_y - size//2), size//4)
                            # Particles around active portal
                            for j in range(5):
                                particle_angle = (time_offset + j) % (2 * math.pi)
                                px = screen_x + int(math.cos(particle_angle) * size // 2)
                                py = screen_y - size//2 + int(math.sin(particle_angle) * size // 2)
                                pygame.draw.circle(screen, (255, 200, 255), (px, py), max(1, size//20))
                        else:
                            # Sealed portal: Dark, static
                            pygame.draw.circle(screen, (60, 40, 80), (screen_x, screen_y - size//2), size//2)
                            pygame.draw.circle(screen, (80, 50, 100), (screen_x, screen_y - size//2), size//2, 3)
                            # Lock symbol in center
                            pygame.draw.rect(screen, (100, 60, 120), (screen_x - size//8, screen_y - size//2 - size//8, size//4, size//4))
                            pygame.draw.circle(screen, (100, 60, 120), (screen_x, screen_y - size//2 - size//8), size//8)
        
        # Apply hit flash effect
        if hit_flash > 0:
            flash_surface = pygame.Surface((WIDTH, HEIGHT))
            flash_surface.fill((255, 0, 0))
            flash_surface.set_alpha(int(hit_flash * 100))
            screen.blit(flash_surface, (0, 0))
        
        # === DRAW UI ===
        # Health bar with gradient
        pygame.draw.rect(screen, ui_bg, (10, 10, 220, 35))
        pygame.draw.rect(screen, ui_border, (10, 10, 220, 35), 3)
        health_pct = player['health'] / player['max_health']
        health_width = int(200 * health_pct)
        # Color changes based on health
        if health_pct > 0.6:
            bar_color = (50, 220, 50)
        elif health_pct > 0.3:
            bar_color = (220, 200, 50)
        else:
            bar_color = (220, 50, 50)
        pygame.draw.rect(screen, bar_color, (15, 15, health_width, 25))
        health_text = font.render(f"❤ {player['health']}/{player['max_health']}", True, (255, 255, 255))
        screen.blit(health_text, (20, 17))
        
        # Mana bar
        pygame.draw.rect(screen, ui_bg, (10, 50, 220, 30))
        pygame.draw.rect(screen, ui_border, (10, 50, 220, 30), 3)
        mana_width = int(200 * (player['mana'] / player['max_mana']))
        pygame.draw.rect(screen, mana_color, (15, 55, mana_width, 20))
        mana_text = font.render(f"✦ {player['mana']}/{player['max_mana']}", True, (255, 255, 255))
        screen.blit(mana_text, (20, 55))
        
        # EXP bar
        pygame.draw.rect(screen, ui_bg, (10, 85, 220, 25))
        pygame.draw.rect(screen, ui_border, (10, 85, 220, 25), 3)
        exp_width = int(200 * (player['exp'] % (player['level'] * 100)) / (player['level'] * 100))
        pygame.draw.rect(screen, exp_color, (15, 90, exp_width, 15))
        exp_text = name_font.render(f"EXP: {player['exp']}/{player['level'] * 100}", True, (255, 255, 255))
        screen.blit(exp_text, (20, 90))
        
        # Player stats panel (top right)
        stats_bg = pygame.Rect(WIDTH - 250, 10, 240, 140)
        pygame.draw.rect(screen, ui_bg, stats_bg)
        pygame.draw.rect(screen, ui_border, stats_bg, 3)
        
        stats_text = [
            f"⭐ Level: {player['level']}",
            f"💰 Gold: {player['gold']}",
            f"⚔ Weapon:",
            f"  {player['equipped_weapon']}",
            f"📦 Items: {len(player['inventory'])}"
        ]
        for i, text in enumerate(stats_text):
            color = (255, 255, 200) if i < 2 else (200, 200, 255) if i > 2 else (255, 200, 100)
            stat = name_font.render(text, True, color)
            screen.blit(stat, (WIDTH - 240, 20 + i * 25))
        
        # Combat indicator with enemy details
        if combat_target:
            combat_bg = pygame.Rect(WIDTH // 2 - 200, 10, 400, 90)
            pygame.draw.rect(screen, (60, 20, 20), combat_bg)
            pygame.draw.rect(screen, (200, 50, 50), combat_bg, 3)
            
            enemy_name = combat_target.get('name', combat_target['type'])
            combat_text = font.render(f"⚠ {enemy_name.upper()} ⚠", True, (255, 200, 100))
            screen.blit(combat_text, (WIDTH // 2 - combat_text.get_width() // 2, 15))
            
            # Enemy health bar
            enemy_health_pct = combat_target['health'] / combat_target.get('max_health', combat_target['health'])
            enemy_bar_width = 300
            enemy_bar_x = WIDTH // 2 - enemy_bar_width // 2
            pygame.draw.rect(screen, (40, 40, 40), (enemy_bar_x, 50, enemy_bar_width, 15))
            pygame.draw.rect(screen, (200, 50, 50), (enemy_bar_x, 50, int(enemy_bar_width * enemy_health_pct), 15))
            pygame.draw.rect(screen, (255, 100, 100), (enemy_bar_x, 50, enemy_bar_width, 15), 2)
            
            enemy_hp = name_font.render(f"HP: {combat_target['health']}/{combat_target.get('max_health', combat_target['health'])}", True, (255, 255, 255))
            screen.blit(enemy_hp, (WIDTH // 2 - enemy_hp.get_width() // 2, 52))
            
            hint = name_font.render("Press SPACE to attack!", True, (255, 255, 100))
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 73))
        
        # Draw floating damage numbers
        for dmg in damage_numbers:
            alpha = int(255 * dmg['timer'] / 1.5)
            dmg_text = lobby_font.render(f"-{dmg['damage']}", True, dmg['color'])
            dmg_text.set_alpha(alpha)
            screen.blit(dmg_text, (dmg['x'] - dmg_text.get_width() // 2, int(dmg['y'])))
        
        # Quest panel (press Q to toggle)
        if show_quest_panel:
            panel_width = 400
            panel_height = 300
            panel_x = WIDTH // 2 - panel_width // 2
            panel_y = HEIGHT // 2 - panel_height // 2
            
            pygame.draw.rect(screen, (20, 20, 40), (panel_x, panel_y, panel_width, panel_height))
            pygame.draw.rect(screen, (150, 150, 200), (panel_x, panel_y, panel_width, panel_height), 4)
            
            title = lobby_font.render("QUEST LOG", True, (255, 200, 100))
            screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 20))
            
            y_offset = panel_y + 80
            for quest in player['quests']:
                status = "✓" if quest['complete'] else "○"
                color = (100, 255, 100) if quest['complete'] else (255, 255, 255)
                
                quest_text = font.render(f"{status} {quest['name']}", True, color)
                screen.blit(quest_text, (panel_x + 30, y_offset))
                
                progress_text = name_font.render(f"   Progress: {quest['progress']}/{quest['target']}", True, (200, 200, 200))
                screen.blit(progress_text, (panel_x + 30, y_offset + 30))
                
                y_offset += 70
            
            close_text = name_font.render("Press Q to close", True, (150, 150, 150))
            screen.blit(close_text, (panel_x + panel_width // 2 - close_text.get_width() // 2, panel_y + panel_height - 35))
        
        # Dialogue box
        if dialogue_lines:
            box_width = min(800, WIDTH - 100)
            box_height = 60 + len(dialogue_lines) * 35
            box_x = WIDTH // 2 - box_width // 2
            box_y = HEIGHT // 2 - box_height // 2
            
            pygame.draw.rect(screen, (10, 10, 30), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, (180, 180, 220), (box_x, box_y, box_width, box_height), 4)
            
            y_offset = box_y + 20
            for i, line in enumerate(dialogue_lines):
                if i == 0:  # Title
                    line_text = lobby_font.render(line, True, (255, 200, 100))
                else:
                    line_text = name_font.render(line, True, (220, 220, 220))
                screen.blit(line_text, (box_x + box_width // 2 - line_text.get_width() // 2, y_offset))
                y_offset += 35 if i == 0 else 30
        
        # Message
        if message and not dialogue_lines:
            msg_surface = font.render(message, True, (255, 255, 150))
            msg_bg = pygame.Rect(WIDTH // 2 - msg_surface.get_width() // 2 - 15, HEIGHT - 100,
                               msg_surface.get_width() + 30, 50)
            pygame.draw.rect(screen, (30, 30, 50), msg_bg)
            pygame.draw.rect(screen, (150, 150, 200), msg_bg, 2)
            screen.blit(msg_surface, (WIDTH // 2 - msg_surface.get_width() // 2, HEIGHT - 87))
        
        # Controls hint (bottom)
        controls = name_font.render("WASD:Move | E:Interact | M:Map | Q:Quests | SPACE:Attack | ESC:Exit", True, (130, 130, 180))
        screen.blit(controls, (WIDTH // 2 - controls.get_width() // 2, HEIGHT - 30))
        
        # Mini map (enhanced)
        if show_map:
            map_size = 250
            map_scale = map_size / len(world_map)
            map_x = WIDTH - map_size - 30
            map_y = 120
            
            # Map background
            pygame.draw.rect(screen, (15, 15, 30), (map_x - 5, map_y - 25, map_size + 10, map_size + 30))
            pygame.draw.rect(screen, (120, 120, 180), (map_x - 5, map_y - 25, map_size + 10, map_size + 30), 3)
            
            # Map title
            map_title = name_font.render("DUNGEON MAP", True, (200, 200, 255))
            screen.blit(map_title, (map_x + map_size // 2 - map_title.get_width() // 2, map_y - 20))
            
            # Draw tiles
            for y in range(len(world_map)):
                for x in range(len(world_map[0])):
                    tile_x = map_x + x * map_scale
                    tile_y = map_y + y * map_scale
                    
                    if world_map[y][x] == 1:
                        color = (80, 80, 80)  # Walls
                    elif world_map[y][x] == 2:
                        color = (120, 80, 40)  # Doors
                    elif world_map[y][x] == 3:
                        color = (255, 215, 0)  # Treasures
                    elif world_map[y][x] == 5:
                        color = (100, 200, 255)  # NPCs
                    elif world_map[y][x] == 6:
                        color = (150, 100, 255)  # Portal
                    else:
                        color = (30, 30, 40)  # Floor
                    
                    pygame.draw.rect(screen, color, (tile_x, tile_y, map_scale, map_scale))
                    pygame.draw.rect(screen, (50, 50, 60), (tile_x, tile_y, map_scale, map_scale), 1)
            
            # Draw player
            player_map_x = map_x + player['x'] * map_scale
            player_map_y = map_y + player['y'] * map_scale
            pygame.draw.circle(screen, (255, 255, 0), (int(player_map_x), int(player_map_y)), 5)
            pygame.draw.circle(screen, (255, 200, 0), (int(player_map_x), int(player_map_y)), 3)
            
            # Draw direction indicator
            dir_x = player_map_x + math.cos(player['angle']) * 15
            dir_y = player_map_y + math.sin(player['angle']) * 15
            pygame.draw.line(screen, (255, 255, 100), (player_map_x, player_map_y), (dir_x, dir_y), 3)
            
            # Draw enemies
            for enemy in enemies:
                if enemy['alive']:
                    ex = map_x + enemy['x'] * map_scale
                    ey = map_y + enemy['y'] * map_scale
                    pygame.draw.circle(screen, (255, 100, 100), (int(ex), int(ey)), 4)
                    pygame.draw.circle(screen, (200, 50, 50), (int(ex), int(ey)), 2)
        
        pygame.display.flip()

# Countdown and player name input functions remain the same...


# Load background image for battle mode
try:
    battle_background = pygame.image.load(resource_path('ball.jpg'))
    has_battle_background = True
except:
    has_battle_background = False
    print("ball.jpg not found, using solid color background for battle mode")

# Set fullscreen mode
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("2 Player Battle Game")
clock = pygame.time.Clock()

# Scale background to screen size if loaded
if has_battle_background:
    battle_background = pygame.transform.scale(battle_background, (WIDTH, HEIGHT))

# Game state variables (moved inside run_game)
player1 = None
player2 = None
player1_health = 5
player2_health = 5
speed = 6
p1_right = True
p2_right = False
bullets = []  # Each bullet: {'rect': ..., 'dir': ..., 'owner': ...}

font = pygame.font.SysFont(None, 48)
lobby_font = pygame.font.SysFont(None, 64)
name_font = pygame.font.SysFont(None, 28)  # Small font for character names

player1_shots = 0
player2_shots = 0
player1_reload_time = 0
player2_reload_time = 0
RELOAD_LIMIT = 3
RELOAD_DURATION = 3  # seconds

coin_rects = []  # For coin collection mode

# --- ONLINE NAME/CHARACTER SELECTION ---
def online_get_name_and_character(player_label, mode):
    name = get_player_name(f"{player_label}, enter your name:", HEIGHT//2 - 120)
    if mode == 0:
        options = [0, 1, 2]
        names = ["Classic Mafia", "Mafia Boss", "Mafia Hitman"]
        draw_func = draw_mafia_character
    else:
        options = [0, 1, 2]
        names = ["Jungle Explorer", "Desert Adventurer", "Arctic Explorer"]
        draw_func = draw_explorer_character
    selected = 0
    done = False
    preview_y = HEIGHT//2+20
    preview_xs = [WIDTH//2-180, WIDTH//2, WIDTH//2+180]
    name_y_offset = 120
    while not done:
        screen.fill((30,30,30))
        title = lobby_font.render(f"{player_label}: Choose Your Character (Enter to confirm)", True, (255,255,255))
        screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-160))
        for i, style in enumerate(options):
            highlight = (255,255,0) if i==selected else (80,80,80)
            pygame.draw.rect(screen, highlight, (preview_xs[i]-50, preview_y-70, 100, 140), 4)
            draw_func(screen, preview_xs[i], preview_y, style)
            name_text = name_font.render(names[i], True, highlight)
            screen.blit(name_text, (preview_xs[i]-name_text.get_width()//2, preview_y+name_y_offset))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected = (selected-1)%len(options)
                if event.key == pygame.K_RIGHT:
                    selected = (selected+1)%len(options)
                if event.key == pygame.K_RETURN:
                    done = True
    return name, selected
# --- END ONLINE NAME/CHARACTER SELECTION ---

# Mode selection lobby with Exit button

def mode_lobby():
    selected = 0
    options = ["Battle Mode", "Coin Collection Mode", "Makka Pakka Mode", "Escape Mom Mode", "Capture the Flag", "Survival Mode", "3D Adventure", "Relax Mode", "Survival Leaderboard", "Mom Mode Leaderboard", "Play Music", "Stop Music", "Watch Cute Video", "Watch Grandma", "Exit"]
    music_playing = False
    pygame.mixer.music.stop()  # Ensure no music plays automatically
    while True:
        screen.fill((30, 30, 30))
        title = lobby_font.render("Choose Game Mode", True, (255,255,255))
        screen.blit(title, (WIDTH//2-title.get_width()//2, 50))
        for i, opt in enumerate(options):
            color = (255,255,0) if i==selected else (200,200,200)
            opt_text = font.render(opt, True, color)
            screen.blit(opt_text, (WIDTH//2-opt_text.get_width()//2, 120+i*50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected-1)%len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected+1)%len(options)
                if event.key == pygame.K_RETURN:
                    if options[selected] == "Exit":
                        pygame.quit()
                        sys.exit()
                    elif options[selected] == "Survival Leaderboard":
                        show_leaderboard('survival')
                    elif options[selected] == "Mom Mode Leaderboard":
                        show_leaderboard('mom')
                    elif options[selected] == "Play Music":
                        try:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(resource_path('playmusic.mp3'))
                            pygame.mixer.music.play(-1)
                            music_playing = True
                        except Exception as e:
                            print(f"Error playing music: {e}")
                    elif options[selected] == "Stop Music":
                        pygame.mixer.music.stop()
                        music_playing = False
                    elif options[selected] == "Watch Cute Video":
                        watch_cute_video()
                    elif options[selected] == "Watch Grandma":
                        watch_grandma()
                    elif options[selected] == "Relax Mode":
                        relax_mode()
                    elif options[selected] == "3D Adventure":
                        adventure_3d_mode()
                    else:
                        pygame.mixer.music.stop()
                        if options[selected] == "Battle Mode":
                            return 0
                        elif options[selected] == "Coin Collection Mode":
                            return 1
                        elif options[selected] == "Makka Pakka Mode":
                            return 3
                        elif options[selected] == "Escape Mom Mode":
                            return 4
                        elif options[selected] == "Capture the Flag":
                            return 5
                        elif options[selected] == "Survival Mode":
                            return 2

def watch_cute_video():
    """Play cute video - fallback to animation if video can't play"""
    import os
    
    video_path = resource_path('cutevideo.mp4')
    
    # Fallback to OpenCV
    try:
        import cv2
        
        print(f"[DEBUG] Loading video with OpenCV: {video_path}")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise RuntimeError("OpenCV could not open video file")
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        clock = pygame.time.Clock()
        
        playing = True
        while playing:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to pygame surface
            frame = frame.swapaxes(0, 1)
            frame_surface = pygame.surfarray.make_surface(frame)
            
            # Scale to fit screen
            video_rect = frame_surface.get_rect()
            scale_factor = min(WIDTH / video_rect.width, HEIGHT / video_rect.height)
            new_width = int(video_rect.width * scale_factor)
            new_height = int(video_rect.height * scale_factor)
            
            scaled_frame = pygame.transform.scale(frame_surface, (new_width, new_height))
            
            # Center on screen
            screen.fill((0, 0, 0))
            x = (WIDTH - new_width) // 2
            y = (HEIGHT - new_height) // 2
            screen.blit(scaled_frame, (x, y))
            
            pygame.display.flip()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    playing = False
            
            clock.tick(fps)
        
        cap.release()
        return
        
    except Exception as e:
        print(f"[DEBUG] OpenCV failed: {e}")
    
    # Final fallback: show cute bouncing emoji animation
    clock = pygame.time.Clock()
    
    # Bouncing emojis
    emojis = ["🎬", "📹", "🎥", "🎞️"]
    emoji_idx = 0
    emoji_y = HEIGHT // 2
    emoji_vel = 4
    emoji_timer = 0
    
    # Floating particles
    particles = []
    for _ in range(20):
        particles.append({
            'x': random.randint(0, WIDTH),
            'y': random.randint(0, HEIGHT),
            'speed': random.uniform(0.5, 2),
            'size': random.randint(2, 6)
        })
    
    waiting = True
    while waiting:
        # Bounce emoji
        emoji_y += emoji_vel
        if emoji_y > HEIGHT // 2 + 40 or emoji_y < HEIGHT // 2 - 40:
            emoji_vel = -emoji_vel
            emoji_idx = (emoji_idx + 1) % len(emojis)
        
        # Update particles
        for p in particles:
            p['y'] += p['speed']
            if p['y'] > HEIGHT:
                p['y'] = 0
                p['x'] = random.randint(0, WIDTH)
        
        emoji_timer += 1
        
        # Draw
        screen.fill((25, 25, 40))
        
        # Draw particles
        for p in particles:
            alpha = int(128 + 127 * math.sin(emoji_timer * 0.05 + p['x']))
            color = (100, 100, 150, alpha)
            pygame.draw.circle(screen, color[:3], (int(p['x']), int(p['y'])), p['size'])
        
        # Main message
        title_text = pygame.font.SysFont(None, 72).render("Video Player", True, (255, 200, 100))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 150))
        
        error_text = lobby_font.render("Videos require special codecs", True, (200, 200, 200))
        screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2 - 80))
        
        info_text = font.render("(Video playback not available in this build)", True, (150, 150, 150))
        screen.blit(info_text, (WIDTH//2 - info_text.get_width()//2, HEIGHT//2 - 40))
        
        # Bouncing emoji
        emoji_font = pygame.font.SysFont(None, 100)
        emoji_text = emoji_font.render(emojis[emoji_idx], True, (255, 255, 255))
        screen.blit(emoji_text, (WIDTH//2 - emoji_text.get_width()//2, int(emoji_y)))
        
        hint_text = font.render("Press any key to continue", True, (100, 255, 100))
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, HEIGHT//2 + 120))
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        
        clock.tick(60)

def watch_grandma():
    """Play grandma video with lala music - fallback to animation if video can't play"""
    import os
    
    # Start music
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(resource_path('lala.mp3'))
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Error playing grandma music: {e}")
    
    video_path = resource_path('grandma.mp4')
    
    # Fallback to OpenCV
    try:
        import cv2
        
        print(f"[DEBUG] Loading grandma.mp4 with OpenCV: {video_path}")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise RuntimeError("OpenCV could not open video file")
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        clock = pygame.time.Clock()
        exit_button_rect = pygame.Rect(WIDTH//2-100, HEIGHT-120, 200, 60)
        
        running = True
        while running:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video for loop
            
            while running:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = frame.swapaxes(0, 1)
                frame_surface = pygame.surfarray.make_surface(frame)
                
                # Scale to fit screen
                video_rect = frame_surface.get_rect()
                scale_factor = min(WIDTH / video_rect.width, HEIGHT / video_rect.height)
                new_width = int(video_rect.width * scale_factor)
                new_height = int(video_rect.height * scale_factor)
                
                scaled_frame = pygame.transform.scale(frame_surface, (new_width, new_height))
                
                screen.fill((0, 0, 0))
                x = (WIDTH - new_width) // 2
                y = (HEIGHT - new_height) // 2
                screen.blit(scaled_frame, (x, y))
                
                # Draw exit button
                pygame.draw.rect(screen, (255, 0, 0), exit_button_rect)
                exit_text = lobby_font.render("Exit", True, (255, 255, 255))
                screen.blit(exit_text, (exit_button_rect.centerx - exit_text.get_width()//2, 
                                       exit_button_rect.centery - exit_text.get_height()//2))
                
                pygame.display.flip()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        cap.release()
                        pygame.mixer.music.stop()
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if exit_button_rect.collidepoint(event.pos):
                            running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        running = False
                
                clock.tick(fps)
        
        cap.release()
        pygame.mixer.music.stop()
        return
        
    except Exception as e:
        print(f"[DEBUG] OpenCV failed: {e}")
    
    # Final fallback: show message with dancing emoji animation
    pygame.mixer.music.stop()
    clock = pygame.time.Clock()
    emoji_y = HEIGHT // 2
    emoji_vel = 3
    
    waiting = True
    while waiting:
        # Bounce emoji
        emoji_y += emoji_vel
        if emoji_y > HEIGHT // 2 + 30 or emoji_y < HEIGHT // 2 - 30:
            emoji_vel = -emoji_vel
        
        screen.fill((30, 30, 30))
        error_text = lobby_font.render("Video playback not available", True, (255, 200, 100))
        screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2 - 100))
        
        emoji_text = pygame.font.SysFont(None, 80).render("👵", True, (255, 255, 255))
        screen.blit(emoji_text, (WIDTH//2 - emoji_text.get_width()//2, int(emoji_y)))
        
        hint_text = font.render("Press any key to continue", True, (150, 150, 150))
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, HEIGHT//2 + 100))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        
        clock.tick(60)

def relax_mode():
    """Relaxing mode menu - choose between Letter Rain or Counting Sheep"""
    # Show submenu to choose mode
    choice = relax_mode_menu()
    if choice == 'letters':
        letter_rain_mode()
    elif choice == 'sheep':
        counting_sheep_mode()

def relax_mode_menu():
    """Menu to select which relax mode to play"""
    clock = pygame.time.Clock()
    selected = 0
    options = ['Letter Rain', 'Counting Sheep', 'Back']
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Draw background
        screen.fill((20, 20, 40))
        
        # Draw title
        title = pygame.font.SysFont(None, 72).render("Relax Mode", True, (200, 200, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # Draw options
        for i, option in enumerate(options):
            color = (255, 255, 150) if i == selected else (150, 150, 200)
            text = lobby_font.render(option, True, color)
            y_pos = 250 + i * 80
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y_pos))
            
            # Draw selector
            if i == selected:
                selector = lobby_font.render(">", True, (255, 255, 150))
                screen.blit(selector, (WIDTH//2 - text.get_width()//2 - 50, y_pos))
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if selected == 0:
                        return 'letters'
                    elif selected == 1:
                        return 'sheep'
                    else:
                        return None
        
        pygame.display.flip()
    
    return None

def letter_rain_mode():
    """Relaxing letter rain mode - press letters to see satisfying animations"""
    clock = pygame.time.Clock()
    
    # Particle system for letter rain
    letters = []
    forming_letters = []
    current_letter = None
    phase = 'idle'  # 'idle', 'raining', 'forming', 'showing'
    phase_timer = 0
    
    # Rainbow colors for fun
    colors = [
        (255, 100, 100), (255, 200, 100), (255, 255, 100),
        (100, 255, 100), (100, 200, 255), (200, 100, 255),
        (255, 100, 200)
    ]
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        phase_timer += dt
        
        # Draw background with subtle gradient
        for y in range(HEIGHT):
            shade = int(20 + 15 * math.sin(y * 0.01 + phase_timer))
            pygame.draw.line(screen, (shade, shade, shade + 20), (0, y), (WIDTH, y))
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                # Check if it's a letter
                if event.unicode.isalpha():
                    current_letter = event.unicode.upper()
                    phase = 'raining'
                    phase_timer = 0
                    letters = []
                    forming_letters = []
                    
                    # Create raining letters (more for denser formation)
                    for _ in range(120):
                        letters.append({
                            'char': current_letter,
                            'x': random.randint(0, WIDTH),
                            'y': random.randint(-HEIGHT, 0),
                            'speed': random.uniform(100, 300),
                            'size': random.randint(20, 60),
                            'rotation': random.uniform(0, 360),
                            'rot_speed': random.uniform(-180, 180),
                            'color': random.choice(colors),
                            'alpha': 255
                        })
        
        # Update phase
        if phase == 'raining':
            # Update falling letters
            for letter in letters:
                letter['y'] += letter['speed'] * dt
                letter['rotation'] += letter['rot_speed'] * dt
            
            # After 2 seconds, start forming
            if phase_timer > 2.0:
                phase = 'forming'
                phase_timer = 0
                
                # Create target positions forming the big letter
                forming_letters = []
                big_letter_points = get_letter_formation_points(current_letter, WIDTH//2, HEIGHT//2, 400)
                
                for i, letter in enumerate(letters[:len(big_letter_points)]):
                    target = big_letter_points[i % len(big_letter_points)]
                    forming_letters.append({
                        'char': letter['char'],
                        'x': letter['x'],
                        'y': letter['y'],
                        'target_x': target[0],
                        'target_y': target[1],
                        'size': letter['size'],
                        'target_size': 24,  # Uniform smaller size for cleaner look
                        'rotation': letter['rotation'],
                        'color': letter['color'],
                        'alpha': 255
                    })
                letters = []
        
        elif phase == 'forming':
            # Move letters to form the big letter
            all_in_place = True
            for letter in forming_letters:
                # Lerp to target position
                dx = letter['target_x'] - letter['x']
                dy = letter['target_y'] - letter['y']
                ds = letter['target_size'] - letter['size']
                
                letter['x'] += dx * 5 * dt
                letter['y'] += dy * 5 * dt
                letter['size'] += ds * 3 * dt
                letter['rotation'] *= 0.85  # Faster rotation decay for cleaner look
                
                # Snap rotation to 0 when close
                if abs(letter['rotation']) < 5:
                    letter['rotation'] = 0
                
                if abs(dx) > 3 or abs(dy) > 3:
                    all_in_place = False
            
            if all_in_place or phase_timer > 2.5:
                phase = 'showing'
                phase_timer = 0
                # Ensure all rotations are 0 for final display
                for letter in forming_letters:
                    letter['rotation'] = 0
        
        elif phase == 'showing':
            # Subtle pulse for the formed letter
            pulse = 1.0 + 0.05 * math.sin(phase_timer * 3)  # Smaller pulse for cleaner look
            for letter in forming_letters:
                letter['alpha'] = int(220 + 35 * math.sin(phase_timer * 2))
            
            # After 3 seconds, fade out
            if phase_timer > 3.0:
                for letter in forming_letters:
                    letter['alpha'] = max(0, letter['alpha'] - 300 * dt)
                
                if forming_letters and forming_letters[0]['alpha'] <= 0:
                    phase = 'idle'
                    forming_letters = []
                    current_letter = None
        
        # Draw letters
        for letter in letters:
            draw_rotated_letter(screen, letter['char'], letter['x'], letter['y'], 
                              letter['size'], letter['rotation'], letter['color'], letter.get('alpha', 255))
        
        for letter in forming_letters:
            pulse = 1.0
            if phase == 'showing':
                pulse = 1.0 + 0.1 * math.sin(phase_timer * 3)
            draw_rotated_letter(screen, letter['char'], letter['x'], letter['y'], 
                              int(letter['size'] * pulse), letter['rotation'], 
                              letter['color'], letter.get('alpha', 255))
        
        # Draw instructions
        if phase == 'idle':
            title = pygame.font.SysFont(None, 72).render("Relax Mode", True, (200, 200, 255))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
            
            instruction = lobby_font.render("Press any letter key", True, (150, 150, 200))
            screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT//2))
            
            hint = font.render("ESC to exit", True, (100, 100, 150))
            screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 80))
        
        pygame.display.flip()

def draw_rotated_letter(surface, char, x, y, size, rotation, color, alpha=255):
    """Draw a rotated letter with alpha transparency"""
    try:
        # Use a bold sans serif font for cleaner letters
        letter_font = pygame.font.SysFont('Arial,Helvetica,sans-serif', int(size), bold=True)
        text = letter_font.render(char, True, color)
        
        # Create a surface with per-pixel alpha
        text_with_alpha = text.copy()
        text_with_alpha.set_alpha(int(alpha))
        
        # Rotate (only if rotation is not 0 for performance)
        if abs(rotation) > 0.1:
            rotated = pygame.transform.rotate(text_with_alpha, rotation)
        else:
            rotated = text_with_alpha
            
        rect = rotated.get_rect(center=(int(x), int(y)))
        
        surface.blit(rotated, rect)
    except Exception as e:
        # Silently fail if there's an issue
        pass

def get_letter_formation_points(letter, center_x, center_y, size):
    """Get points that form the shape of a letter"""
    points = []
    
    try:
        # Create letter patterns - use bold font for better definition
        if letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            # Render the letter large and sample points from it
            letter_font = pygame.font.SysFont('Arial,Helvetica,sans-serif', size, bold=True)
            text = letter_font.render(letter, True, (255, 255, 255))
            text_rect = text.get_rect(center=(center_x, center_y))
            
            # Sample points from the letter surface with better distribution
            width = text.get_width()
            height = text.get_height()
            
            # Grid-based sampling for more even distribution
            for x in range(0, width, 3):
                for y in range(0, height, 3):
                    try:
                        pixel = text.get_at((x, y))
                        if pixel[3] > 128:  # Alpha > 128
                            # Add some randomness to avoid perfect grid
                            jitter_x = random.uniform(-1.5, 1.5)
                            jitter_y = random.uniform(-1.5, 1.5)
                            world_x = text_rect.left + x + jitter_x
                            world_y = text_rect.top + y + jitter_y
                            points.append((world_x, world_y))
                    except:
                        pass
    except Exception as e:
        print(f"Error creating letter formation: {e}")
    
    # If we didn't get enough points, add some in the letter area
    if len(points) < 50:
        for _ in range(50 - len(points)):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0, size * 0.3)
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            points.append((px, py))
    
    return points

def draw_realistic_sheep(surface, x, y, leg_phase, rotation=0):
    """Draw a more realistic sheep with wool texture, proper proportions, and animated legs"""
    # Sheep colors
    wool_color = (245, 245, 240)  # Off-white wool
    wool_shadow = (220, 220, 215)
    face_color = (40, 35, 35)  # Dark grey/black face
    leg_color = (35, 30, 30)
    
    # Create a temporary surface for rotation
    sheep_surface = pygame.Surface((100, 80), pygame.SRCALPHA)
    
    # Draw on temporary surface (centered at 50, 40)
    center_x, center_y = 50, 40
    
    # Body - woolly texture with multiple circles
    body_x = center_x - 5
    body_y = center_y - 10
    
    # Main body ellipse with wool puffs
    for i in range(8):
        angle = (i / 8) * 2 * math.pi
        puff_x = body_x + 18 * math.cos(angle)
        puff_y = body_y + 12 * math.sin(angle)
        pygame.draw.circle(sheep_surface, wool_shadow, (int(puff_x), int(puff_y)), 10)
    
    # Core body
    pygame.draw.ellipse(sheep_surface, wool_color, (body_x - 20, body_y - 15, 40, 30))
    
    # Add wool texture details
    for _ in range(12):
        offset_x = random.randint(-15, 15)
        offset_y = random.randint(-10, 10)
        pygame.draw.circle(sheep_surface, wool_shadow, 
                         (body_x + offset_x, body_y + offset_y), random.randint(3, 6))
    
    # Legs with joints and walking animation
    leg_positions = [
        (body_x - 12, body_y + 15),  # Front left
        (body_x + 8, body_y + 15),   # Front right
        (body_x - 8, body_y + 15),   # Back left
        (body_x + 12, body_y + 15)   # Back right
    ]
    
    for i, (leg_x, leg_y) in enumerate(leg_positions):
        # Alternate leg movement
        if i % 2 == 0:
            leg_swing = 8 * math.sin(leg_phase)
        else:
            leg_swing = 8 * math.sin(leg_phase + math.pi)
        
        # Upper leg
        upper_end_x = leg_x + leg_swing // 2
        upper_end_y = leg_y + 10
        pygame.draw.line(sheep_surface, leg_color, (leg_x, leg_y), 
                        (upper_end_x, upper_end_y), 4)
        
        # Lower leg
        lower_end_x = upper_end_x + leg_swing // 2
        lower_end_y = upper_end_y + 12
        pygame.draw.line(sheep_surface, leg_color, (upper_end_x, upper_end_y), 
                        (lower_end_x, lower_end_y), 3)
        
        # Hoof
        pygame.draw.circle(sheep_surface, (20, 20, 20), (lower_end_x, lower_end_y), 2)
    
    # Head
    head_x = center_x + 20
    head_y = center_y - 15
    
    # Wool on head (top of head)
    pygame.draw.circle(sheep_surface, wool_color, (head_x - 5, head_y - 8), 8)
    pygame.draw.circle(sheep_surface, wool_shadow, (head_x - 8, head_y - 6), 5)
    
    # Face (elongated)
    pygame.draw.ellipse(sheep_surface, face_color, (head_x - 2, head_y - 5, 14, 18))
    
    # Ears
    # Left ear
    ear_points_l = [
        (head_x - 2, head_y - 3),
        (head_x - 6, head_y - 6),
        (head_x - 3, head_y + 2)
    ]
    pygame.draw.polygon(sheep_surface, face_color, ear_points_l)
    pygame.draw.polygon(sheep_surface, (60, 50, 50), 
                       [(p[0]+1, p[1]+1) for p in ear_points_l[:-1]] + [ear_points_l[-1]])
    
    # Right ear
    ear_points_r = [
        (head_x + 12, head_y - 3),
        (head_x + 16, head_y - 6),
        (head_x + 13, head_y + 2)
    ]
    pygame.draw.polygon(sheep_surface, face_color, ear_points_r)
    
    # Eyes
    pygame.draw.circle(sheep_surface, (255, 255, 255), (head_x + 2, head_y + 2), 3)
    pygame.draw.circle(sheep_surface, (0, 0, 0), (head_x + 3, head_y + 2), 2)
    pygame.draw.circle(sheep_surface, (255, 255, 255), (head_x + 8, head_y + 2), 3)
    pygame.draw.circle(sheep_surface, (0, 0, 0), (head_x + 9, head_y + 2), 2)
    
    # Nose
    pygame.draw.circle(sheep_surface, (20, 20, 20), (head_x + 5, head_y + 10), 2)
    
    # Mouth - gentle smile
    pygame.draw.arc(sheep_surface, (60, 50, 50), 
                   (head_x + 2, head_y + 8, 8, 6), 0, math.pi, 1)
    
    # Tail - small wool puff
    tail_x = body_x - 22
    tail_y = body_y - 5
    pygame.draw.circle(sheep_surface, wool_shadow, (tail_x, tail_y), 6)
    pygame.draw.circle(sheep_surface, wool_color, (tail_x - 1, tail_y - 1), 5)
    
    # Rotate the surface if needed
    if abs(rotation) > 0.1:
        sheep_surface = pygame.transform.rotate(sheep_surface, rotation)
    
    # Blit to main surface
    rect = sheep_surface.get_rect(center=(x, y))
    surface.blit(sheep_surface, rect)

def counting_sheep_mode():
    """Peaceful counting sheep game - watch sheep jump over a fence"""
    clock = pygame.time.Clock()
    
    # Sheep state
    sheep_list = []
    count = 0
    spawn_timer = 0
    spawn_interval = 2.5  # Seconds between sheep
    animation_time = 0
    
    # Fence position
    fence_x = WIDTH // 2
    fence_y = HEIGHT // 2 + 50
    fence_height = 100
    
    # Moon
    moon_x = WIDTH - 150
    moon_y = 100
    
    # Stars - fixed positions for consistency
    stars = []
    random.seed(42)  # Fixed seed for consistent star positions
    for _ in range(80):
        stars.append({
            'x': random.randint(0, WIDTH),
            'y': random.randint(0, HEIGHT // 2 + 50),
            'brightness': random.randint(150, 255),
            'twinkle_speed': random.uniform(1, 3),
            'size': random.choice([1, 1, 1, 2])  # Mostly small, some bigger
        })
    random.seed()  # Reset seed
    
    # Cloud decorations
    clouds = []
    for _ in range(7):
        clouds.append({
            'x': random.randint(0, WIDTH),
            'y': random.randint(40, 180),
            'size': random.randint(40, 80),
            'speed': random.uniform(8, 20),
            'puffiness': random.uniform(0.8, 1.2)
        })
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        spawn_timer += dt
        animation_time += dt
        
        # Draw gradient night sky
        for y in range(HEIGHT):
            if y < HEIGHT // 2:
                # Sky gradient from dark blue to lighter blue
                ratio = y / (HEIGHT // 2)
                r = int(10 + 20 * ratio)
                g = int(10 + 30 * ratio)
                b = int(40 + 50 * ratio)
                pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
            else:
                # Ground area
                screen.fill((15, 60, 15), (0, y, WIDTH, 1))
        
        # Draw twinkling stars
        for star in stars:
            twinkle = abs(math.sin(animation_time * star['twinkle_speed']))
            brightness = int(star['brightness'] * (0.5 + 0.5 * twinkle))
            blue_tint = min(255, brightness + 20)  # Clamp to 255
            color = (brightness, brightness, blue_tint)
            if star['size'] == 2:
                # Draw bigger stars as small crosses
                pygame.draw.circle(screen, color, (star['x'], star['y']), 2)
                pygame.draw.line(screen, color, (star['x']-2, star['y']), (star['x']+2, star['y']))
                pygame.draw.line(screen, color, (star['x'], star['y']-2), (star['x'], star['y']+2))
            else:
                pygame.draw.circle(screen, color, (star['x'], star['y']), star['size'])
        
        # Draw moon with glow
        for i in range(5, 0, -1):
            glow_brightness = 240 - i*10
            pygame.draw.circle(screen, (glow_brightness, glow_brightness, max(0, 200 - i*5)), 
                             (moon_x, moon_y), 35 + i*3)
        pygame.draw.circle(screen, (240, 240, 220), (moon_x, moon_y), 35)
        # Moon craters
        pygame.draw.circle(screen, (220, 220, 200), (moon_x - 8, moon_y - 5), 8)
        pygame.draw.circle(screen, (220, 220, 200), (moon_x + 10, moon_y + 8), 6)
        pygame.draw.circle(screen, (220, 220, 200), (moon_x + 5, moon_y - 12), 5)
        
        # Draw and update clouds
        for cloud in clouds:
            cloud['x'] += cloud['speed'] * dt
            if cloud['x'] > WIDTH + cloud['size'] * 2:
                cloud['x'] = -cloud['size'] * 2
            
            # Draw cloud as multiple overlapping circles for fluffy effect
            base_color = (200, 200, 230)
            for i in range(5):
                offset_x = (i - 2) * cloud['size'] // 4
                offset_y = random.randint(-5, 5) if i % 2 == 0 else 0
                puff_size = int(cloud['size'] // 2 * cloud['puffiness'])
                pygame.draw.circle(screen, base_color, 
                                 (int(cloud['x'] + offset_x), int(cloud['y'] + offset_y)), 
                                 puff_size)
        
        # Draw rolling hills in background
        hill_color = (25, 90, 25)
        for i in range(3):
            hill_y = HEIGHT // 2 + 80 + i * 30
            points = []
            for x in range(0, WIDTH + 100, 50):
                y_offset = 30 * math.sin((x + animation_time * 20) / 100 + i)
                points.append((x, hill_y + y_offset))
            points.append((WIDTH, HEIGHT))
            points.append((0, HEIGHT))
            if len(points) > 2:
                pygame.draw.polygon(screen, hill_color, points)
        
        # Draw ground with grass texture
        ground_y = HEIGHT // 2 + 100
        pygame.draw.rect(screen, (20, 80, 20), (0, ground_y, WIDTH, HEIGHT))
        # Grass blades
        for i in range(0, WIDTH, 10):
            grass_height = random.randint(3, 8)
            pygame.draw.line(screen, (30, 100, 30), 
                           (i, ground_y), (i, ground_y - grass_height), 1)
        
        # Draw wooden fence with more detail
        fence_color = (101, 67, 33)  # Dark brown
        fence_light = (139, 90, 43)  # Light brown
        # Posts with 3D effect
        for i in range(5):
            post_x = fence_x - 60 + i * 30
            # Shadow
            pygame.draw.rect(screen, (60, 40, 20), (post_x + 2, fence_y + 2, 8, fence_height))
            # Post
            pygame.draw.rect(screen, fence_color, (post_x, fence_y, 8, fence_height))
            # Highlight
            pygame.draw.rect(screen, fence_light, (post_x, fence_y, 2, fence_height))
        # Horizontal bars with 3D effect
        for bar_y in [fence_y + 20, fence_y + 50, fence_y + 80]:
            # Shadow
            pygame.draw.rect(screen, (60, 40, 20), (fence_x - 60 + 2, bar_y + 2, 140, 8))
            # Bar
            pygame.draw.rect(screen, fence_color, (fence_x - 60, bar_y, 140, 8))
            # Highlight
            pygame.draw.rect(screen, fence_light, (fence_x - 60, bar_y, 140, 2))
        
        # Spawn new sheep
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            count += 1
            sheep_list.append({
                'x': -80,
                'y': fence_y + 80,  # Start on ground
                'jump_phase': 0,  # 0=walking, 1=jumping, 2=landed
                'target_y': fence_y + 80,
                'speed': 120,
                'num': count,
                'leg_phase': random.uniform(0, math.pi * 2),  # For walking animation
                'body_bob': 0,  # Bobbing up and down while walking
                'rotation': 0  # For mid-air rotation
            })
        
        # Update and draw sheep
        for sheep in sheep_list[:]:
            sheep['x'] += sheep['speed'] * dt
            
            # Walking leg animation
            if sheep['jump_phase'] == 0:
                sheep['leg_phase'] += 8 * dt
                sheep['body_bob'] = 2 * math.sin(sheep['leg_phase'] * 2)
            
            # Jumping animation
            if sheep['jump_phase'] == 0:  # Walking to fence
                if sheep['x'] > fence_x - 120:
                    sheep['jump_phase'] = 1
                    sheep['jump_start_x'] = sheep['x']
                    sheep['jump_start_y'] = sheep['y']
            elif sheep['jump_phase'] == 1:  # Jumping over fence
                # Arc motion
                progress = (sheep['x'] - sheep['jump_start_x']) / 220
                if progress < 1.0:
                    # Parabolic arc
                    sheep['y'] = sheep['jump_start_y'] - 140 * math.sin(progress * math.pi)
                    # Slight rotation during jump
                    sheep['rotation'] = -15 * math.sin(progress * math.pi)
                    sheep['body_bob'] = 0
                else:
                    sheep['jump_phase'] = 2
                    sheep['y'] = fence_y + 80
                    sheep['rotation'] = 0
                    sheep['leg_phase'] = 0
            elif sheep['jump_phase'] == 2:  # Landed, walking away
                sheep['leg_phase'] += 8 * dt
                sheep['body_bob'] = 2 * math.sin(sheep['leg_phase'] * 2)
            
            # Draw realistic sheep
            draw_realistic_sheep(screen, int(sheep['x']), int(sheep['y'] + sheep['body_bob']), 
                               sheep['leg_phase'], sheep['rotation'])
            
            # Remove sheep that are off screen
            if sheep['x'] > WIDTH + 100:
                sheep_list.remove(sheep)
        
        # Draw count
        count_text = pygame.font.SysFont(None, 100).render(str(count), True, (255, 255, 200))
        screen.blit(count_text, (WIDTH - count_text.get_width() - 30, 30))
        
        # Draw instruction
        if count == 0:
            instruction = lobby_font.render("Watch the sheep jump...", True, (200, 200, 220))
            screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT - 100))
        
        hint = font.render("ESC to exit | SPACE for next sheep", True, (150, 150, 170))
        screen.blit(hint, (20, HEIGHT - 40))
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                # Spacebar to spawn sheep faster
                elif event.key == pygame.K_SPACE:
                    spawn_timer = spawn_interval
        
        pygame.display.flip()

# Countdown and player name input functions remain the same...

def start_countdown():
    try:
        sound = pygame.mixer.Sound(resource_path('321go.mp3'))
        sound.play()
    except Exception as e:
        print(f"Error playing countdown sound: {e}")
    # Use provided timings for each cue (in ms)
    timings = [980, 960, 980, 910]  # ms for 3, 2, 1, GO!
    steps = [3,2,1,"GO!"]
    for idx, i in enumerate(steps):
        screen.fill((30, 30, 30))
        countdown_font = pygame.font.SysFont(None, 180)
        text = countdown_font.render(str(i), True, (255,255,0))
        screen.blit(text, (WIDTH//2-text.get_width()//2, HEIGHT//2-text.get_height()//2))
        pygame.display.flip()
        pygame.time.wait(timings[idx])

# Lobby to get player names
def get_player_name(prompt, ypos):
    name = ""
    active = True
    while active:
        screen.fill((30, 30, 30))
        prompt_text = lobby_font.render(prompt, True, (255,255,255))
        screen.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, ypos))
        name_text = font.render(name, True, (255,255,255))
        screen.blit(name_text, (WIDTH//2 - name_text.get_width()//2, ypos+80))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key <= 127 and event.unicode.isprintable():
                    name += event.unicode
    return name

def online_host_or_join():
    """Select whether to host or join an online game"""
    while True:
        screen.fill((30, 30, 30))
        title = lobby_font.render("Online Mode", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 180))
        
        host_rect = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 40, 200, 80)
        join_rect = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 - 40, 200, 80)
        back_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 60)
        
        pygame.draw.rect(screen, (0, 180, 0), host_rect)
        pygame.draw.rect(screen, (0, 120, 255), join_rect)
        pygame.draw.rect(screen, (100, 100, 100), back_rect)
        
        host_text = font.render("Host Game", True, (255, 255, 255))
        join_text = font.render("Join Game", True, (255, 255, 255))
        back_text = font.render("Back", True, (255, 255, 255))
        
        screen.blit(host_text, (host_rect.centerx - host_text.get_width()//2, host_rect.centery - host_text.get_height()//2))
        screen.blit(join_text, (join_rect.centerx - join_text.get_width()//2, join_rect.centery - join_text.get_height()//2))
        screen.blit(back_text, (back_rect.centerx - back_text.get_width()//2, back_rect.centery - back_text.get_height()//2))
        
        info = name_font.render("Host: Wait for other player to join your IP", True, (200, 200, 200))
        info2 = name_font.render("Join: Connect to host's IP address", True, (200, 200, 200))
        screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2 + 60))
        screen.blit(info2, (WIDTH//2 - info2.get_width()//2, HEIGHT//2 + 90))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if host_rect.collidepoint(event.pos):
                    return 'host'
                if join_rect.collidepoint(event.pos):
                    return 'join'
                if back_rect.collidepoint(event.pos):
                    return None

def get_ip_address():
    """Get IP address input from user"""
    ip = ""
    active = True
    while active:
        screen.fill((30, 30, 30))
        prompt_text = lobby_font.render("Enter Host IP Address:", True, (255, 255, 255))
        screen.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, HEIGHT//2 - 80))
        
        info = name_font.render("(Example: 192.168.1.100)", True, (200, 200, 200))
        screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2 - 30))
        
        ip_text = font.render(ip, True, (255, 255, 255))
        screen.blit(ip_text, (WIDTH//2 - ip_text.get_width()//2, HEIGHT//2 + 20))
        
        cancel_text = name_font.render("Press ESC to cancel", True, (150, 150, 150))
        screen.blit(cancel_text, (WIDTH//2 - cancel_text.get_width()//2, HEIGHT//2 + 80))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and ip:
                    active = False
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    ip = ip[:-1]
                elif event.unicode in '0123456789.':
                    ip += event.unicode
    return ip

def online_character_select_and_countdown(net, is_host, mode):
    """Online character selection - each player chooses only their own character"""
    if mode == 0:
        options = [0, 1, 2]
        names = ["Classic Mafia", "Mafia Boss", "Mafia Hitman"]
        draw_func = draw_mafia_character
    elif mode == 1:
        options = [0, 1, 2]
        names = ["Jungle Explorer", "Desert Adventurer", "Arctic Explorer"]
        draw_func = draw_explorer_character
    else:
        options = [0, 1, 2]
        names = ["Military", "Scientist", "Apocalypse"]
        draw_func = draw_survivor_character
    
    my_character = None
    opponent_character = None
    selected = 0
    preview_y = HEIGHT//2 + 20
    preview_xs = [WIDTH//2 - 220, WIDTH//2, WIDTH//2 + 220]
    name_y_offset = 120
    clock = pygame.time.Clock()
    
    # Character selection phase
    while my_character is None or opponent_character is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    net.close()
                    return None, None
                if my_character is None:
                    if event.key == pygame.K_LEFT:
                        selected = (selected - 1) % len(options)
                    if event.key == pygame.K_RIGHT:
                        selected = (selected + 1) % len(options)
                    if event.key == pygame.K_RETURN:
                        my_character = selected
                        net.send({'type': 'character_choice', 'character': my_character})
        
        data = net.recv()
        if data and data.get('type') == 'character_choice':
            opponent_character = data.get('character')
        
        screen.fill((30, 30, 30))
        if my_character is None:
            title = lobby_font.render("Choose Your Character (Enter to confirm)", True, (255, 255, 255))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 160))
            for i, style in enumerate(options):
                highlight = (255, 255, 0) if i == selected else (80, 80, 80)
                pygame.draw.rect(screen, highlight, (preview_xs[i] - 50, preview_y - 70, 100, 140), 4)
                draw_func(screen, preview_xs[i], preview_y, style)
                name_text = name_font.render(names[i], True, highlight)
                screen.blit(name_text, (preview_xs[i] - name_text.get_width()//2, preview_y + name_y_offset))
        else:
            chosen_text = lobby_font.render(f"You chose: {names[my_character]}", True, (0, 255, 0))
            screen.blit(chosen_text, (WIDTH//2 - chosen_text.get_width()//2, HEIGHT//2 - 80))
            if opponent_character is None:
                waiting_text = font.render("Waiting for opponent to choose...", True, (255, 255, 0))
                screen.blit(waiting_text, (WIDTH//2 - waiting_text.get_width()//2, HEIGHT//2))
            else:
                ready_text = font.render("Both players ready!", True, (0, 255, 0))
                screen.blit(ready_text, (WIDTH//2 - ready_text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        clock.tick(60)
    
    # Countdown - BOTH players play it simultaneously
    if is_host:
        pygame.time.wait(500)
        net.send({'type': 'start_countdown'})
        start_countdown()
    else:
        # Wait for host signal to start countdown
        screen.fill((30, 30, 30))
        waiting_msg = lobby_font.render("Get Ready...", True, (255, 255, 0))
        screen.blit(waiting_msg, (WIDTH//2 - waiting_msg.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        start_time = pygame.time.get_ticks()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            data = net.recv()
            if data and data.get('type') == 'start_countdown':
                waiting = False
                # Play countdown immediately
                start_countdown()
            if pygame.time.get_ticks() - start_time > 5000:
                waiting = False
            pygame.time.wait(50)
    
    return my_character, opponent_character

# Character selection function

def character_select(mode):
    # Three character options per mode
    if mode == 0:
        options = [0, 1, 2]  # Mafia styles
        names = ["Classic Mafia", "Mafia Boss", "Mafia Hitman"]
        draw_func = draw_mafia_character
    elif mode == 1:
        options = [0, 1, 2]  # Explorer styles
        names = ["Jungle Explorer", "Desert Adventurer", "Arctic Explorer"]
        draw_func = draw_explorer_character
    else:  # mode == 2 (Survival mode)
        options = [0, 1, 2]  # Survivor styles
        names = ["Military", "Scientist", "Apocalypse"]  # Shorter names to prevent overlap
        draw_func = draw_survivor_character
    selected1 = 0
    selected2 = 0
    p1_done = False
    p2_done = False
    preview_y = HEIGHT//2+20
    preview_xs = [WIDTH//2-220, WIDTH//2, WIDTH//2+220]  # Wider spacing to prevent text overlap
    name_y_offset = 120  # Move names further down
    while not p1_done:
        screen.fill((30,30,30))
        title = lobby_font.render("Player 1: Choose Your Character (Enter to confirm)", True, (255,255,255))
        screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-160))
        for i, style in enumerate(options):
            highlight = (255,255,0) if i==selected1 else (80,80,80)
            pygame.draw.rect(screen, highlight, (preview_xs[i]-50, preview_y-70, 100, 140), 4)
            draw_func(screen, preview_xs[i], preview_y, style)
            # Draw name below preview, spaced further down, smaller font
            name_text = name_font.render(names[i], True, highlight)
            screen.blit(name_text, (preview_xs[i]-name_text.get_width()//2, preview_y+name_y_offset))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected1 = (selected1-1)%len(options)
                if event.key == pygame.K_RIGHT:
                    selected1 = (selected1+1)%len(options)
                if event.key == pygame.K_RETURN:
                    p1_done = True
    while not p2_done:
        screen.fill((30,30,30))
        title = lobby_font.render("Player 2: Choose Your Character (Enter to confirm)", True, (255,255,255))
        screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-160))
        for i, style in enumerate(options):
            highlight = (255,0,0) if i==selected2 else (80,80,80)
            pygame.draw.rect(screen, highlight, (preview_xs[i]-50, preview_y-70, 100, 140), 4)
            draw_func(screen, preview_xs[i], preview_y, style)
            # Draw name below preview, spaced further down, smaller font
            name_text = name_font.render(names[i], True, highlight)
            screen.blit(name_text, (preview_xs[i]-name_text.get_width()//2, preview_y+name_y_offset))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected2 = (selected2-1)%len(options)
                if event.key == pygame.K_RIGHT:
                    selected2 = (selected2+1)%len(options)
                if event.key == pygame.K_RETURN:
                    p2_done = True
    return [selected1, selected2]

def character_select_single_player(mode):
    # Character selection for single player mode
    if mode == 0:
        options = [0, 1, 2]  # Mafia styles
        names = ["Classic Mafia", "Mafia Boss", "Mafia Hitman"]
        draw_func = draw_mafia_character
    elif mode == 1:
        options = [0, 1, 2]  # Explorer styles
        names = ["Jungle Explorer", "Desert Adventurer", "Arctic Explorer"]
        draw_func = draw_explorer_character
    else:  # mode == 2 (Survival mode)
        options = [0, 1, 2]  # Survivor styles
        names = ["Military", "Scientist", "Apocalypse"]
        draw_func = draw_survivor_character
    
    selected = 0
    done = False
    preview_y = HEIGHT//2+20
    preview_xs = [WIDTH//2-220, WIDTH//2, WIDTH//2+220]
    name_y_offset = 120
    
    while not done:
        screen.fill((30,30,30))
        title = lobby_font.render("Choose Your Character (Enter to confirm)", True, (255,255,255))
        screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-160))
        
        for i, style in enumerate(options):
            highlight = (255,255,0) if i==selected else (80,80,80)
            pygame.draw.rect(screen, highlight, (preview_xs[i]-50, preview_y-70, 100, 140), 4)
            draw_func(screen, preview_xs[i], preview_y, style)
            name_text = name_font.render(names[i], True, highlight)
            screen.blit(name_text, (preview_xs[i]-name_text.get_width()//2, preview_y+name_y_offset))
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected = (selected-1)%len(options)
                if event.key == pygame.K_RIGHT:
                    selected = (selected+1)%len(options)
                if event.key == pygame.K_RETURN:
                    done = True
    
    return [selected]

def character_select_three_player(mode):
    # Character selection for three players
    if mode == 0:
        options = [0, 1, 2]  # Mafia styles
        names = ["Classic Mafia", "Mafia Boss", "Mafia Hitman"]
        draw_func = draw_mafia_character
    elif mode == 1:
        options = [0, 1, 2]  # Explorer styles
        names = ["Jungle Explorer", "Desert Adventurer", "Arctic Explorer"]
        draw_func = draw_explorer_character
    else:  # mode == 2 (Survival mode)
        options = [0, 1, 2]  # Survivor styles
        names = ["Military", "Scientist", "Apocalypse"]
        draw_func = draw_survivor_character
    
    selected1, selected2, selected3 = 0, 0, 0
    p1_done, p2_done, p3_done = False, False, False
    preview_y = HEIGHT//2+20
    preview_xs = [WIDTH//2-220, WIDTH//2, WIDTH//2+220]
    name_y_offset = 120
    
    # Player 1 selection
    while not p1_done:
        screen.fill((30,30,30))
        title = lobby_font.render("Player 1: Choose Your Character (Enter to confirm)", True, (255,255,255))
        screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-160))
        
        for i, style in enumerate(options):
            highlight = (255,255,0) if i==selected1 else (80,80,80)
            pygame.draw.rect(screen, highlight, (preview_xs[i]-50, preview_y-70, 100, 140), 4)
            draw_func(screen, preview_xs[i], preview_y, style)
            # Draw name below preview, spaced further down, smaller font
            name_text = name_font.render(names[i], True, highlight)
            screen.blit(name_text, (preview_xs[i]-name_text.get_width()//2, preview_y+name_y_offset))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected1 = (selected1-1)%len(options)
                if event.key == pygame.K_RIGHT:
                    selected1 = (selected1+1)%len(options)
                if event.key == pygame.K_RETURN:
                    p1_done = True
    
    # Player 2 selection
    while not p2_done:
        screen.fill((30,30,30))
        title = lobby_font.render("Player 2: Choose Your Character (Enter to confirm)", True, (255,255,255))
        screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-160))
        
        for i, style in enumerate(options):
            highlight = (255,0,0) if i==selected2 else (80,80,80)
            pygame.draw.rect(screen, highlight, (preview_xs[i]-50, preview_y-70, 100, 140), 4)
            draw_func(screen, preview_xs[i], preview_y, style)
            # Draw name below preview, spaced further down, smaller font
            name_text = name_font.render(names[i], True, highlight)
            screen.blit(name_text, (preview_xs[i]-name_text.get_width()//2, preview_y+name_y_offset))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected2 = (selected2-1)%len(options)
                if event.key == pygame.K_RIGHT:
                    selected2 = (selected2+1)%len(options)
                if event.key == pygame.K_RETURN:
                    p2_done = True
    
    # Player 3 selection
    while not p3_done:
        screen.fill((30,30,30))
        title = lobby_font.render("Player 3: Choose Your Character (Enter to confirm)", True, (255,255,255))
        screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-160))
        
        for i, style in enumerate(options):
            highlight = (0,255,0) if i==selected3 else (80,80,80)
            pygame.draw.rect(screen, highlight, (preview_xs[i]-50, preview_y-70, 100, 140), 4)
            draw_func(screen, preview_xs[i], preview_y, style)
            # Draw name below preview, spaced further down, smaller font
            name_text = name_font.render(names[i], True, highlight)
            screen.blit(name_text, (preview_xs[i]-name_text.get_width()//2, preview_y+name_y_offset))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected3 = (selected3-1)%len(options)
                if event.key == pygame.K_RIGHT:
                    selected3 = (selected3+1)%len(options)
                if event.key == pygame.K_RETURN:
                    p3_done = True
    
    return [selected1, selected2, selected3]
# Drawing functions for each character

def draw_mafia_character(screen, x, y, style):
    if style == 0:  # Classic Mafia Don - Ultra Realistic
        # Realistic Italian-American head with proper anatomy and depth
        head_color = (218, 178, 128)
        pygame.draw.ellipse(screen, head_color, (x-16, y-38, 32, 42))
        # Multiple layers of shading for 3D depth
        pygame.draw.ellipse(screen, (200, 160, 110), (x-14, y-36, 28, 38))  # Face shading
        pygame.draw.ellipse(screen, (210, 170, 120), (x-12, y-34, 24, 34))  # Mid-tone highlight
        # Nose bridge shadow
        pygame.draw.ellipse(screen, (195, 155, 105), (x-3, y-28, 6, 12))
        
        # Strong Italian jawline and cheekbones
        pygame.draw.polygon(screen, (190, 150, 100), [(x-12, y-8), (x-8, y-4), (x+8, y-4), (x+12, y-8)])
        pygame.draw.arc(screen, (185, 145, 95), (x-14, y-20, 12, 8), 3.8, 5.5, 2)  # Left cheekbone
        pygame.draw.arc(screen, (185, 145, 95), (x+2, y-20, 12, 8), 3.8, 5.5, 2)   # Right cheekbone
        
        # Professional fedora with authentic details and shadows
        hat_color = (45, 45, 45)
        # Shadow under brim first
        pygame.draw.ellipse(screen, (15, 15, 15), (x-18, y-40, 36, 8))  # Deep shadow
        pygame.draw.ellipse(screen, hat_color, (x-18, y-48, 36, 12))     # Crown
        pygame.draw.ellipse(screen, (35, 35, 35), (x-16, y-46, 32, 8))  # Crown top
        pygame.draw.ellipse(screen, (55, 55, 55), (x-15, y-47, 30, 6))  # Crown highlight
        pygame.draw.ellipse(screen, hat_color, (x-22, y-42, 44, 6))     # Brim
        # Brim shadow gradient
        pygame.draw.ellipse(screen, (25, 25, 25), (x-20, y-41, 40, 4))
        pygame.draw.rect(screen, (200, 0, 0), (x-16, y-44, 32, 4))     # Red band
        pygame.draw.rect(screen, (180, 0, 0), (x-14, y-43, 28, 2))     # Band highlight
        pygame.draw.rect(screen, (220, 20, 20), (x-13, y-44, 2, 3))    # Band shine
        
        # Luxury aviator sunglasses with reflections
        pygame.draw.polygon(screen, (20, 20, 20), [(x-12, y-26), (x-2, y-26), (x-2, y-18), (x-12, y-18)])
        pygame.draw.polygon(screen, (20, 20, 20), [(x+2, y-26), (x+12, y-26), (x+12, y-18), (x+2, y-18)])
        pygame.draw.line(screen, (255, 215, 0), (x-2, y-22), (x+2, y-22), 2)  # Gold bridge
        # Lens reflections
        pygame.draw.line(screen, (100, 100, 150), (x-10, y-24), (x-6, y-20), 2)
        pygame.draw.line(screen, (100, 100, 150), (x+4, y-24), (x+8, y-20), 2)
        
        # Realistic thick eyebrows (visible above glasses)
        for i in range(8):
            pygame.draw.line(screen, (60, 40, 20), (x-12+i*2, y-30), (x-11+i*2, y-32), 1)
            pygame.draw.line(screen, (60, 40, 20), (x+4+i*2, y-30), (x+5+i*2, y-32), 1)
        
        # Authentic Italian mustache with detail
        pygame.draw.ellipse(screen, (80, 42, 20), (x-8, y-12, 16, 6))
        pygame.draw.ellipse(screen, (60, 32, 15), (x-7, y-11, 14, 4))
        # Mustache curl details
        pygame.draw.arc(screen, (80, 42, 20), (x-10, y-10, 6, 6), 0, 3.14, 2)
        pygame.draw.arc(screen, (80, 42, 20), (x+4, y-10, 6, 6), 0, 3.14, 2)
        
        # Realistic neck
        pygame.draw.rect(screen, head_color, (x-6, y-8, 12, 15))
        
        # Luxury Italian suit with fine details and fabric texture
        suit_color = (25, 25, 25)
        pygame.draw.rect(screen, suit_color, (x-16, y+5, 32, 40))
        # Subtle fabric texture lines
        for i in range(y+7, y+43, 3):
            pygame.draw.line(screen, (35, 35, 35), (x-15, i), (x+15, i), 1)
        # Suit highlights on shoulders
        pygame.draw.ellipse(screen, (40, 40, 40), (x-14, y+6, 8, 6))
        pygame.draw.ellipse(screen, (40, 40, 40), (x+6, y+6, 8, 6))
        pygame.draw.polygon(screen, (20, 20, 20), [(x-12, y+5), (x-8, y), (x+8, y), (x+12, y+5)])  # Lapels
        # Lapel shadows
        pygame.draw.line(screen, (10, 10, 10), (x-10, y+2), (x-8, y+8), 2)
        pygame.draw.line(screen, (10, 10, 10), (x+10, y+2), (x+8, y+8), 2)
        
        # Crisp white dress shirt with realistic folds
        pygame.draw.rect(screen, (255, 255, 255), (x-6, y+5, 12, 35))
        pygame.draw.rect(screen, (240, 240, 240), (x-5, y+6, 10, 33))  # Shirt shading
        # Shirt fold lines
        pygame.draw.line(screen, (230, 230, 230), (x-4, y+15), (x+4, y+15), 1)
        pygame.draw.line(screen, (230, 230, 230), (x-3, y+25), (x+3, y+25), 1)
        
        # Italian silk tie with pattern
        tie_color = (150, 0, 0)
        pygame.draw.polygon(screen, tie_color, [(x-2, y+12), (x+2, y+12), (x+3, y+35), (x-3, y+35)])
        # Tie pattern
        for i in range(4):
            pygame.draw.line(screen, (180, 30, 30), (x-1, y+15+i*5), (x+1, y+15+i*5), 1)
        
        # Gold pocket square
        pygame.draw.rect(screen, (255, 215, 0), (x+8, y+12, 6, 6))
        pygame.draw.polygon(screen, (230, 190, 0), [(x+8, y+12), (x+11, y+12), (x+10, y+15)])
        
        # Suit buttons
        for btn in range(3):
            pygame.draw.circle(screen, (200, 200, 200), (x-10, y+15+btn*8), 2)
            pygame.draw.circle(screen, (180, 180, 180), (x-10, y+15+btn*8), 1)
        
        # Gold pinky ring
        pygame.draw.circle(screen, (255, 215, 0), (x+12, y+25), 3)
        pygame.draw.circle(screen, (200, 0, 0), (x+12, y+25), 2)  # Ruby center
        
        # Realistic arms in suit sleeves
        pygame.draw.ellipse(screen, suit_color, (x-22, y+10, 10, 25))
        pygame.draw.ellipse(screen, suit_color, (x+12, y+10, 10, 25))
        
        # Hands with realistic skin tone
        pygame.draw.ellipse(screen, head_color, (x-25, y+30, 8, 12))
        pygame.draw.ellipse(screen, head_color, (x+17, y+30, 8, 12))
        
        # Professional Italian leather shoes
        shoe_color = (40, 20, 10)
        pygame.draw.ellipse(screen, shoe_color, (x-14, y+42, 14, 8))
        pygame.draw.ellipse(screen, shoe_color, (x, y+42, 14, 8))
        pygame.draw.ellipse(screen, (80, 40, 20), (x-13, y+43, 12, 6))  # Shoe shine
        pygame.draw.ellipse(screen, (80, 40, 20), (x+1, y+43, 12, 6))
    elif style == 1:  # Mafia Boss - Ultra Realistic
        # Commanding presence with weathered features
        head_color = (210, 170, 120)
        pygame.draw.ellipse(screen, head_color, (x-18, y-40, 36, 45))
        pygame.draw.ellipse(screen, (190, 150, 100), (x-16, y-38, 32, 41))  # Face shading
        
        # Prominent boss jawline and features
        pygame.draw.polygon(screen, (180, 140, 90), [(x-14, y-8), (x-10, y-2), (x+10, y-2), (x+14, y-8)])
        pygame.draw.arc(screen, (175, 135, 85), (x-16, y-22, 14, 10), 3.8, 5.5, 3)  # Strong cheekbones
        pygame.draw.arc(screen, (175, 135, 85), (x+2, y-22, 14, 10), 3.8, 5.5, 3)
        
        # Imposing boss hat with luxury details
        hat_color = (30, 30, 30)
        pygame.draw.ellipse(screen, hat_color, (x-24, y-58, 48, 16))     # Large crown
        pygame.draw.ellipse(screen, (20, 20, 20), (x-22, y-56, 44, 12))  # Crown top
        pygame.draw.ellipse(screen, hat_color, (x-28, y-48, 56, 8))     # Wide brim
        pygame.draw.rect(screen, (150, 150, 150), (x-22, y-54, 44, 4))  # Silver band
        
        # Luxury hat feather
        pygame.draw.polygon(screen, (255, 255, 0), [(x+15, y-58), (x+22, y-75), (x+18, y-58)])
        pygame.draw.line(screen, (200, 200, 0), (x+16, y-70), (x+20, y-60), 2)
        
        # Thick authoritative eyebrows
        for i in range(10):
            pygame.draw.line(screen, (50, 30, 15), (x-15+i*2, y-32), (x-14+i*2, y-35), 2)
            pygame.draw.line(screen, (50, 30, 15), (x+5+i*2, y-32), (x+6+i*2, y-35), 2)
        
        # Intense boss eyes with authority
        pygame.draw.ellipse(screen, (255, 255, 255), (x-12, y-26, 10, 8))
        pygame.draw.ellipse(screen, (255, 255, 255), (x+2, y-26, 10, 8))
        pygame.draw.ellipse(screen, (60, 60, 60), (x-9, y-24, 4, 5))     # Dark gray eyes
        pygame.draw.ellipse(screen, (60, 60, 60), (x+5, y-24, 4, 5))
        pygame.draw.ellipse(screen, (0, 0, 0), (x-8, y-23, 2, 3))       # Pupils
        pygame.draw.ellipse(screen, (0, 0, 0), (x+6, y-23, 2, 3))
        
        # Eye bags and wrinkles from years of command
        pygame.draw.arc(screen, (170, 130, 80), (x-12, y-18, 10, 6), 0, 3.14, 1)
        pygame.draw.arc(screen, (170, 130, 80), (x+2, y-18, 10, 6), 0, 3.14, 1)
        
        # Gold monocle with chain
        pygame.draw.circle(screen, (255, 215, 0), (x+8, y-22), 8, 3)
        pygame.draw.circle(screen, (230, 190, 0), (x+8, y-22), 6, 1)
        pygame.draw.line(screen, (255, 215, 0), (x+8, y-14), (x+12, y-8), 2)  # Chain
        pygame.draw.circle(screen, (255, 215, 0), (x+12, y-8), 2)  # Chain end
        
        # Serious authoritative mouth
        pygame.draw.arc(screen, (160, 80, 80), (x-6, y-14, 12, 6), 3.8, 5.5, 2)
        pygame.draw.line(screen, (140, 60, 60), (x-4, y-12), (x+4, y-12), 1)
        
        # Premium cigar with detail
        pygame.draw.rect(screen, (139, 69, 19), (x-12, y-10, 20, 6))
        pygame.draw.rect(screen, (160, 80, 30), (x-11, y-9, 18, 4))  # Cigar wrapper
        pygame.draw.circle(screen, (255, 100, 0), (x+8, y-7), 3)     # Glowing tip
        pygame.draw.circle(screen, (255, 200, 100), (x+8, y-7), 2)   # Bright center
        # Smoke wisps
        for i in range(3):
            pygame.draw.circle(screen, (200, 200, 200), (x+12+i*3, y-12-i*2), 1)
        
        # Gold jewelry - chain and watch
        pygame.draw.arc(screen, (255, 215, 0), (x-12, y+15, 32, 20), 3.14, 2*3.14, 4)
        pygame.draw.rect(screen, (255, 215, 0), (x-28, y+22, 10, 8))    # Gold watch
        pygame.draw.rect(screen, (200, 200, 200), (x-27, y+23, 8, 6))   # Watch face
        
        # Multiple gold rings
        pygame.draw.circle(screen, (255, 215, 0), (x+15, y+28), 4)      # Pinky ring
        pygame.draw.circle(screen, (255, 215, 0), (x+12, y+30), 3)      # Ring finger
        pygame.draw.circle(screen, (200, 0, 0), (x+15, y+28), 2)        # Ruby
        pygame.draw.circle(screen, (0, 100, 0), (x+12, y+30), 2)        # Emerald
        
        # Luxury pinstripe suit
        suit_color = (20, 20, 20)
        pygame.draw.rect(screen, suit_color, (x-20, y+5, 40, 45))
        
        # Pinstripes with precision
        for i in range(-18, 20, 6):
            pygame.draw.line(screen, (180, 180, 180), (x+i, y+5), (x+i, y+50), 1)
            pygame.draw.line(screen, (160, 160, 160), (x+i+2, y+5), (x+i+2, y+50), 1)
        
        # White dress shirt
        pygame.draw.rect(screen, (255, 255, 255), (x-8, y+5, 16, 40))
        pygame.draw.rect(screen, (240, 240, 240), (x-7, y+6, 14, 38))  # Shirt shading
        
        # Expensive silk tie
        tie_color = (100, 0, 100)
        pygame.draw.polygon(screen, tie_color, [(x-3, y+15), (x+3, y+15), (x+4, y+40), (x-4, y+40)])
        # Tie pattern - paisley design
        for i in range(3):
            pygame.draw.arc(screen, (150, 50, 150), (x-2, y+18+i*8, 4, 6), 0, 3.14, 1)
        
        # Suit vest buttons
        for btn in range(4):
            pygame.draw.circle(screen, (200, 200, 200), (x-12, y+18+btn*6), 2)
            pygame.draw.circle(screen, (180, 180, 180), (x-12, y+18+btn*6), 1)
        
        # Realistic neck
        pygame.draw.rect(screen, head_color, (x-8, y-5, 16, 18))
        
        # Professional shoes with shine
        shoe_color = (30, 15, 5)
        pygame.draw.ellipse(screen, shoe_color, (x-16, y+47, 16, 10))
        pygame.draw.ellipse(screen, shoe_color, (x, y+47, 16, 10))
        pygame.draw.ellipse(screen, (80, 40, 20), (x-15, y+48, 14, 8))  # Leather shine
        pygame.draw.ellipse(screen, (80, 40, 20), (x+1, y+48, 14, 8))
    elif style == 2:  # Mafia Hitman - Ultra Realistic
        # Lean, dangerous assassin appearance
        head_color = (205, 165, 115)
        pygame.draw.ellipse(screen, head_color, (x-15, y-38, 30, 40))
        pygame.draw.ellipse(screen, (185, 145, 95), (x-13, y-36, 26, 36))  # Face shading
        
        # Sharp angular features
        pygame.draw.polygon(screen, (175, 135, 85), [(x-10, y-8), (x-6, y-2), (x+6, y-2), (x+10, y-8)])
        pygame.draw.line(screen, (165, 125, 75), (x-8, y-15), (x+8, y-15), 1)  # Cheek definition
        
        # Slicked-back professional hair
        pygame.draw.arc(screen, (20, 20, 20), (x-15, y-42, 30, 20), 3.5, 5.8, 8)
        pygame.draw.arc(screen, (40, 40, 40), (x-13, y-40, 26, 16), 3.6, 5.7, 4)  # Hair highlight
        
        # Sharp, calculating eyes
        pygame.draw.ellipse(screen, (255, 255, 255), (x-10, y-28, 8, 6))
        pygame.draw.ellipse(screen, (255, 255, 255), (x+2, y-28, 8, 6))
        pygame.draw.ellipse(screen, (70, 70, 70), (x-8, y-26, 4, 4))     # Cold gray eyes
        pygame.draw.ellipse(screen, (70, 70, 70), (x+4, y-26, 4, 4))
        pygame.draw.ellipse(screen, (0, 0, 0), (x-7, y-25, 2, 2))       # Pupils
        pygame.draw.ellipse(screen, (0, 0, 0), (x+5, y-25, 2, 2))
        
        # Tactical eyebrows
        for i in range(6):
            pygame.draw.line(screen, (40, 25, 15), (x-12+i*2, y-30), (x-11+i*2, y-32), 1)
            pygame.draw.line(screen, (40, 25, 15), (x+2+i*2, y-30), (x+3+i*2, y-32), 1)
        
        # Professional tactical sunglasses
        pygame.draw.polygon(screen, (15, 15, 15), [(x-12, y-26), (x-2, y-26), (x-2, y-20), (x-12, y-20)])
        pygame.draw.polygon(screen, (15, 15, 15), [(x+2, y-26), (x+12, y-26), (x+12, y-20), (x+2, y-20)])
        pygame.draw.line(screen, (100, 100, 100), (x-2, y-23), (x+2, y-23), 2)  # Bridge
        # Lens reflection
        pygame.draw.line(screen, (80, 80, 120), (x-10, y-24), (x-6, y-22), 1)
        pygame.draw.line(screen, (80, 80, 120), (x+4, y-24), (x+8, y-22), 1)
        
        # Serious, controlled expression
        pygame.draw.line(screen, (150, 100, 80), (x-4, y-12), (x+4, y-12), 2)
        
        # 5 o'clock shadow for rugged look
        for shadow_x in range(x-8, x+8, 2):
            for shadow_y in range(y-12, y-2, 2):
                if (shadow_x + shadow_y) % 3 == 0:
                    pygame.draw.circle(screen, (100, 70, 50), (shadow_x, shadow_y), 1)
        
        # Small scar detail
        pygame.draw.line(screen, (160, 120, 90), (x+6, y-18), (x+8, y-15), 1)
        
        # Professional earpiece
        pygame.draw.circle(screen, (50, 50, 50), (x+13, y-15), 3)
        pygame.draw.circle(screen, (30, 30, 30), (x+13, y-15), 2)
        pygame.draw.line(screen, (100, 100, 100), (x+13, y-12), (x+13, y-8), 1)  # Wire
        
        # Tactical neck gear
        pygame.draw.rect(screen, head_color, (x-6, y-8, 12, 15))
        pygame.draw.rect(screen, (40, 40, 40), (x-8, y-2, 16, 4))  # Tactical collar
        
        # Professional black tactical suit
        suit_color = (15, 15, 15)
        pygame.draw.rect(screen, suit_color, (x-16, y+5, 32, 42))
        pygame.draw.polygon(screen, (10, 10, 10), [(x-12, y+5), (x-8, y+2), (x+8, y+2), (x+12, y+5)])  # Collar
        
        # Tactical vest details
        pygame.draw.rect(screen, (25, 25, 25), (x-14, y+8, 28, 25))
        pygame.draw.line(screen, (40, 40, 40), (x-12, y+10), (x+12, y+10), 1)  # Vest line
        pygame.draw.line(screen, (40, 40, 40), (x-12, y+20), (x+12, y+20), 1)
        pygame.draw.line(screen, (40, 40, 40), (x-12, y+30), (x+12, y+30), 1)
        
        # Tactical gear attachments
        pygame.draw.rect(screen, (60, 60, 60), (x-12, y+12, 4, 6))  # Left pocket
        pygame.draw.rect(screen, (60, 60, 60), (x+8, y+12, 4, 6))   # Right pocket
        pygame.draw.circle(screen, (80, 80, 80), (x-8, y+15), 2)    # Button/fastener
        pygame.draw.circle(screen, (80, 80, 80), (x+8, y+15), 2)
        
        # White tactical shirt underneath
        pygame.draw.rect(screen, (240, 240, 240), (x-6, y+6, 12, 8))
        
        # Dark tactical tie
        tie_color = (60, 0, 0)
        pygame.draw.polygon(screen, tie_color, [(x-2, y+14), (x+2, y+14), (x+3, y+32), (x-3, y+32)])
        pygame.draw.line(screen, (80, 20, 20), (x, y+16), (x, y+30), 1)  # Tie center
        
        # Professional black gloves
        pygame.draw.ellipse(screen, (20, 20, 20), (x-20, y+28, 8, 12))
        pygame.draw.ellipse(screen, (20, 20, 20), (x+12, y+28, 8, 12))
        # Glove details
        pygame.draw.line(screen, (40, 40, 40), (x-18, y+30), (x-18, y+36), 1)
        pygame.draw.line(screen, (40, 40, 40), (x+14, y+30), (x+14, y+36), 1)
        
        # Tactical arms
        pygame.draw.ellipse(screen, suit_color, (x-22, y+10, 10, 25))
        pygame.draw.ellipse(screen, suit_color, (x+12, y+10, 10, 25))
        
        # Professional tactical boots
        boot_color = (20, 20, 20)
        pygame.draw.ellipse(screen, boot_color, (x-14, y+45, 14, 10))
        pygame.draw.ellipse(screen, boot_color, (x, y+45, 14, 10))
        pygame.draw.ellipse(screen, (40, 40, 40), (x-13, y+46, 12, 8))  # Boot details
        pygame.draw.ellipse(screen, (40, 40, 40), (x+1, y+46, 12, 8))
        # Boot laces
        for lace in range(3):
            pygame.draw.line(screen, (80, 80, 80), (x-11+lace*3, y+47), (x-10+lace*3, y+51), 1)
            pygame.draw.line(screen, (80, 80, 80), (x+3+lace*3, y+47), (x+4+lace*3, y+51), 1)
    # End of draw_mafia_character function

def draw_explorer_character(screen, x, y, style):
    if style == 0:  # Jungle Explorer - Ultra Realistic
        # Realistic human head with proper anatomy
        head_color = (210, 180, 140)
        pygame.draw.ellipse(screen, head_color, (x-16, y-38, 32, 42))
        pygame.draw.ellipse(screen, (195, 165, 125), (x-14, y-36, 28, 38))  # Face shading
        
        # Detailed realistic eyes
        pygame.draw.ellipse(screen, (255, 255, 255), (x-10, y-28, 8, 6))  # Left eye
        pygame.draw.ellipse(screen, (255, 255, 255), (x+2, y-28, 8, 6))   # Right eye
        pygame.draw.ellipse(screen, (70, 130, 180), (x-8, y-26, 4, 4))    # Left iris (blue)
        pygame.draw.ellipse(screen, (70, 130, 180), (x+4, y-26, 4, 4))    # Right iris
        pygame.draw.ellipse(screen, (0, 0, 0), (x-7, y-25, 2, 2))         # Left pupil
        pygame.draw.ellipse(screen, (0, 0, 0), (x+5, y-25, 2, 2))         # Right pupil
        
        # Realistic eyebrows with hair texture
        for i in range(6):
            pygame.draw.line(screen, (101, 67, 33), (x-10+i*2, y-30), (x-9+i*2, y-32), 1)
            pygame.draw.line(screen, (101, 67, 33), (x+2+i*2, y-30), (x+3+i*2, y-32), 1)
        
        # Realistic nose with shading
        pygame.draw.polygon(screen, (190, 160, 120), [(x-1, y-22), (x+1, y-22), (x+2, y-18), (x-2, y-18)])
        pygame.draw.line(screen, (170, 140, 100), (x-1, y-20), (x+1, y-20), 1)
        
        # Natural mouth
        pygame.draw.ellipse(screen, (205, 92, 92), (x-4, y-15, 8, 4))
        pygame.draw.line(screen, (180, 75, 75), (x-3, y-13), (x+3, y-13), 1)
        
        # Stubble/beard texture
        for beard_x in range(x-8, x+8, 2):
            for beard_y in range(y-12, y-5, 2):
                if (beard_x + beard_y) % 3 == 0:
                    pygame.draw.circle(screen, (80, 50, 30), (beard_x, beard_y), 1)
        
        # Professional Safari Hat
        hat_color = (139, 69, 19)
        pygame.draw.ellipse(screen, hat_color, (x-18, y-45, 36, 12))
        pygame.draw.ellipse(screen, (101, 67, 33), (x-16, y-43, 32, 8))
        pygame.draw.ellipse(screen, hat_color, (x-22, y-40, 44, 6))  # Brim
        pygame.draw.rect(screen, (205, 133, 63), (x-15, y-42, 30, 3))  # Hat band
        pygame.draw.rect(screen, (184, 134, 11), (x+8, y-43, 4, 5))   # Buckle
        
        # Realistic neck
        pygame.draw.rect(screen, head_color, (x-6, y-8, 12, 15))
        
        # Professional Safari Shirt with details
        shirt_color = (34, 139, 34)
        pygame.draw.rect(screen, shirt_color, (x-14, y+5, 28, 35))
        pygame.draw.polygon(screen, (28, 115, 28), [(x-10, y+5), (x-6, y), (x+6, y), (x+10, y+5)])  # Collar
        pygame.draw.rect(screen, (28, 115, 28), (x-2, y+5, 4, 30))  # Button placket
        
        # Shirt buttons
        for btn in range(5):
            pygame.draw.circle(screen, (240, 230, 140), (x, y+8+btn*6), 2)
            pygame.draw.circle(screen, (200, 190, 100), (x, y+8+btn*6), 1)
        
        # Chest pockets
        pygame.draw.rect(screen, (28, 115, 28), (x-12, y+12, 8, 6))
        pygame.draw.rect(screen, (28, 115, 28), (x+4, y+12, 8, 6))
        
        # Realistic arms
        pygame.draw.ellipse(screen, head_color, (x-22, y+8, 10, 25))
        pygame.draw.ellipse(screen, head_color, (x+12, y+8, 10, 25))
        
        # Hands with fingers
        pygame.draw.ellipse(screen, head_color, (x-25, y+30, 8, 12))
        pygame.draw.ellipse(screen, head_color, (x+17, y+30, 8, 12))
        for finger in range(3):
            pygame.draw.line(screen, (180, 150, 110), (x-23+finger*2, y+32), (x-23+finger*2, y+38), 1)
            pygame.draw.line(screen, (180, 150, 110), (x+19+finger*2, y+32), (x+19+finger*2, y+38), 1)
        
        # Utility Belt
        pygame.draw.rect(screen, (101, 67, 33), (x-15, y+35, 30, 4))
        pygame.draw.rect(screen, (184, 134, 11), (x-3, y+34, 6, 6))  # Buckle
        pygame.draw.rect(screen, (101, 67, 33), (x-13, y+36, 4, 6))  # Pouch
        pygame.draw.rect(screen, (101, 67, 33), (x+9, y+36, 4, 6))   # Pouch
        
        # Cargo Pants
        pants_color = (107, 142, 35)
        pygame.draw.rect(screen, pants_color, (x-12, y+40, 24, 30))
        pygame.draw.rect(screen, (85, 115, 25), (x-11, y+45, 6, 8))  # Cargo pocket
        pygame.draw.rect(screen, (85, 115, 25), (x+5, y+45, 6, 8))   # Cargo pocket
        
        # Legs
        pygame.draw.rect(screen, pants_color, (x-10, y+70, 8, 25))
        pygame.draw.rect(screen, pants_color, (x+2, y+70, 8, 25))
        
        # Professional Hiking Boots
        boot_color = (101, 67, 33)
        pygame.draw.ellipse(screen, boot_color, (x-14, y+90, 12, 8))
        pygame.draw.ellipse(screen, boot_color, (x+2, y+90, 12, 8))
        pygame.draw.ellipse(screen, (60, 40, 20), (x-15, y+95, 14, 4))  # Soles
        pygame.draw.ellipse(screen, (60, 40, 20), (x+1, y+95, 14, 4))
        
        # Boot laces
        for lace in range(4):
            pygame.draw.line(screen, (255, 255, 255), (x-11+lace*2, y+90), (x-10+lace*2, y+94), 1)
            pygame.draw.line(screen, (255, 255, 255), (x+5+lace*2, y+90), (x+6+lace*2, y+94), 1)

    elif style == 1:  # Desert Adventurer - Ultra Realistic
        # Sun-weathered desert explorer with authentic gear
        
        # Head with sun-tanned, weathered skin
        head_color = (222, 184, 135)
        pygame.draw.ellipse(screen, head_color, (x-16, y-38, 32, 42))
        pygame.draw.ellipse(screen, (200, 165, 115), (x-14, y-36, 28, 38))
        
        # Intense desert eyes with squint lines
        pygame.draw.ellipse(screen, (255, 255, 255), (x-10, y-28, 8, 5))  # Squinted from sun
        pygame.draw.ellipse(screen, (255, 255, 255), (x+2, y-28, 8, 5))
        pygame.draw.ellipse(screen, (139, 69, 19), (x-8, y-26, 4, 3))     # Brown eyes
        pygame.draw.ellipse(screen, (139, 69, 19), (x+4, y-26, 4, 3))
        pygame.draw.ellipse(screen, (0, 0, 0), (x-7, y-25, 2, 2))         # Left pupil
        pygame.draw.ellipse(screen, (0, 0, 0), (x+5, y-25, 2, 2))         # Right pupil
        
        # Sun wrinkles and weathering
        pygame.draw.line(screen, (180, 150, 100), (x-12, y-30), (x-8, y-28), 1)  # Crow's feet
        pygame.draw.line(screen, (180, 150, 100), (x+8, y-28), (x+12, y-30), 1)
        pygame.draw.line(screen, (180, 150, 100), (x-4, y-20), (x+4, y-20), 1)   # Forehead line
        
        # Wide-brim desert sun hat
        hat_color = (210, 180, 140)
        pygame.draw.ellipse(screen, hat_color, (x-25, y-42, 50, 8))    # Wide brim
        pygame.draw.ellipse(screen, hat_color, (x-16, y-45, 32, 12))   # Crown
        pygame.draw.ellipse(screen, (190, 160, 120), (x-14, y-43, 28, 8))
        pygame.draw.rect(screen, (139, 69, 19), (x-15, y-42, 30, 3))  # Hat band
        pygame.draw.rect(screen, (184, 134, 11), (x+8, y-43, 4, 5))   # Buckle
        
        # Protective neck scarf/shemagh
        scarf_color = (245, 245, 220)
        pygame.draw.polygon(screen, scarf_color, [(x-12, y-8), (x+12, y-8), (x+8, y+5), (x-8, y+5)])
        for i in range(3):
            pygame.draw.line(screen, (220, 220, 200), (x-10+i*7, y-6), (x-8+i*7, y+3), 1)
        
        # Desert clothing - light colored and breathable
        shirt_color = (245, 245, 220)
        pygame.draw.rect(screen, shirt_color, (x-14, y+5, 28, 35))
        pygame.draw.polygon(screen, (225, 225, 200), [(x-10, y+5), (x-6, y), (x+6, y), (x+10, y+5)])
        pygame.draw.rect(screen, (225, 225, 200), (x-2, y+5, 4, 30))
        
        # Arms with sun protection
        pygame.draw.ellipse(screen, head_color, (x-22, y+8, 10, 25))
        pygame.draw.ellipse(screen, head_color, (x+12, y+8, 10, 25))
        
        # Desert pants
        pants_color = (210, 180, 140)
        pygame.draw.rect(screen, pants_color, (x-12, y+40, 24, 30))
        
        # Legs
        pygame.draw.rect(screen, pants_color, (x-10, y+70, 8, 25))
        pygame.draw.rect(screen, pants_color, (x+2, y+70, 8, 25))
        
        # Desert boots
        boot_color = (139, 69, 19)
        pygame.draw.ellipse(screen, boot_color, (x-14, y+90, 12, 8))
        pygame.draw.ellipse(screen, boot_color, (x+2, y+90, 12, 8))
        
    elif style == 2:  # Arctic Explorer - Ultra Realistic
        # Head with cold-weather gear
        head_color = (255, 230, 200)
        pygame.draw.ellipse(screen, head_color, (x-16, y-38, 32, 42))
        
        # Eyes
        pygame.draw.ellipse(screen, (255, 255, 255), (x-10, y-28, 8, 6))
        pygame.draw.ellipse(screen, (255, 255, 255), (x+2, y-28, 8, 6))
        pygame.draw.ellipse(screen, (70, 130, 180), (x-8, y-26, 4, 4))
        pygame.draw.ellipse(screen, (70, 130, 180), (x+4, y-26, 4, 4))
        
        # Cold weather hood/hat
        pygame.draw.ellipse(screen, (25, 25, 112), (x-20, y-45, 40, 15))
        pygame.draw.ellipse(screen, (255, 255, 255), (x-18, y-43, 36, 8))  # Fur trim
        
        # Heavy winter clothing
        coat_color = (25, 25, 112)
        pygame.draw.rect(screen, coat_color, (x-16, y+5, 32, 40))
        
        # Arms
        pygame.draw.ellipse(screen, coat_color, (x-24, y+8, 12, 30))
        pygame.draw.ellipse(screen, coat_color, (x+12, y+8, 12, 30))
        
        # Insulated pants
        pygame.draw.rect(screen, (47, 79, 79), (x-14, y+45, 28, 25))
        
        # Legs
        pygame.draw.rect(screen, (47, 79, 79), (x-12, y+70, 10, 25))
        pygame.draw.rect(screen, (47, 79, 79), (x+2, y+70, 10, 25))
        
        # Heavy winter boots
        pygame.draw.ellipse(screen, (139, 69, 19), (x-16, y+90, 16, 10))
        pygame.draw.ellipse(screen, (139, 69, 19), (x, y+90, 16, 10))
        # Smile
        pygame.draw.arc(screen, (255,0,0), (x-7, y-10, 14, 10), 3.14, 2*3.14, 3)
        # Blue parka
        pygame.draw.rect(screen, (0,191,255), (x-18, y+10, 36, 18))
        # Mittens
        pygame.draw.rect(screen, (135,206,250), (x-10, y+3, 20, 38))
        # Boots
        pygame.draw.ellipse(screen, (135,206,250), (x-12, y+38, 12, 8))
        pygame.draw.ellipse(screen, (135,206,250), (x+0, y+38, 12, 8))
    # ...add arms, legs, shoes as needed...

# Drawing functions for realistic survivor characters

def draw_survivor_character(screen, x, y, style):
    if style == 0:  # Military Survivor
        # Head with helmet
        pygame.draw.ellipse(screen, (224, 172, 105), (x-15, y-35, 30, 38))
        # Military helmet (olive green)
        pygame.draw.ellipse(screen, (85, 107, 47), (x-16, y-45, 32, 20))
        pygame.draw.rect(screen, (85, 107, 47), (x-12, y-50, 24, 8))
        # Eyes
        pygame.draw.circle(screen, (0,0,0), (x-6, y-25), 2)
        pygame.draw.circle(screen, (0,0,0), (x+6, y-25), 2)
        # Mouth (serious expression)
        pygame.draw.line(screen, (0,0,0), (x-4, y-15), (x+4, y-15), 2)
        # Military uniform (camouflage colors)
        pygame.draw.rect(screen, (85, 107, 47), (x-14, y+3, 28, 38))
        pygame.draw.rect(screen, (60, 80, 40), (x-10, y+8, 8, 20))
        pygame.draw.rect(screen, (60, 80, 40), (x+2, y+8, 8, 20))
        # Belt with pouches
        pygame.draw.rect(screen, (139, 69, 19), (x-14, y+20, 28, 4))
        pygame.draw.rect(screen, (80, 40, 20), (x-8, y+18, 6, 8))
        pygame.draw.rect(screen, (80, 40, 20), (x+2, y+18, 6, 8))
        # Arms (holding rifle)
        pygame.draw.line(screen, (224, 172, 105), (x-20, y+10), (x-25, y+20), 8)
        pygame.draw.line(screen, (224, 172, 105), (x+20, y+10), (x+25, y+20), 8)
        # Legs (military pants)
        pygame.draw.line(screen, (85, 107, 47), (x-5, y+41), (x-5, y+70), 8)
        pygame.draw.line(screen, (85, 107, 47), (x+5, y+41), (x+5, y+70), 8)
        # Military boots
        pygame.draw.ellipse(screen, (0,0,0), (x-12, y+68, 14, 8))
        pygame.draw.ellipse(screen, (0,0,0), (x-2, y+68, 14, 8))
        
    elif style == 1:  # Scientist Survivor
        # Head with glasses
        pygame.draw.ellipse(screen, (224, 172, 105), (x-15, y-35, 30, 38))
        # Glasses
        pygame.draw.circle(screen, (255,255,255), (x-8, y-25), 6, 2)
        pygame.draw.circle(screen, (255,255,255), (x+8, y-25), 6, 2)
        pygame.draw.line(screen, (0,0,0), (x-2, y-25), (x+2, y-25), 2)
        # Eyes behind glasses
        pygame.draw.circle(screen, (0,0,0), (x-8, y-25), 2)
        pygame.draw.circle(screen, (0,0,0), (x+8, y-25), 2)
        # Worried expression
        pygame.draw.arc(screen, (0,0,0), (x-6, y-18, 12, 8), 0, 3.14, 2)
        # Lab coat (white with stains)
        pygame.draw.rect(screen, (240, 240, 240), (x-14, y+3, 28, 38))
        pygame.draw.rect(screen, (200, 200, 200), (x-6, y+3, 12, 38))  # Front opening
        # Blood stains
        pygame.draw.circle(screen, (139, 0, 0), (x-8, y+15), 3)
        pygame.draw.circle(screen, (139, 0, 0), (x+6, y+25), 2)
        # Shirt underneath
        pygame.draw.rect(screen, (100, 150, 200), (x-8, y+8, 16, 15))
        # Arms (shaking)
        pygame.draw.line(screen, (224, 172, 105), (x-20, y+10), (x-22, y+25), 8)
        pygame.draw.line(screen, (224, 172, 105), (x+20, y+10), (x+22, y+25), 8)
        # Legs (dress pants)
        pygame.draw.line(screen, (50, 50, 50), (x-5, y+41), (x-5, y+70), 8)
        pygame.draw.line(screen, (50, 50, 50), (x+5, y+41), (x+5, y+70), 8)
        # Dress shoes
        pygame.draw.ellipse(screen, (0,0,0), (x-12, y+68, 14, 8))
        pygame.draw.ellipse(screen, (0,0,0), (x-2, y+68, 14, 8))
        
    elif style == 2:  # Post-Apocalyptic Survivor
        # Head with bandana
        pygame.draw.ellipse(screen, (224, 172, 105), (x-15, y-35, 30, 38))
        # Bandana (red)
        pygame.draw.polygon(screen, (139, 0, 0), [(x-16, y-42), (x+16, y-42), (x+12, y-35), (x-12, y-35)])
        # Scars and dirt
        pygame.draw.line(screen, (139, 0, 0), (x-10, y-28), (x-5, y-20), 2)
        pygame.draw.circle(screen, (101, 67, 33), (x+8, y-22), 3)
        # Eyes (determined)
        pygame.draw.circle(screen, (0,0,0), (x-6, y-25), 2)
        pygame.draw.circle(screen, (0,0,0), (x+6, y-25), 2)
        # Grim mouth
        pygame.draw.line(screen, (0,0,0), (x-3, y-15), (x+3, y-13), 2)
        # Leather jacket (worn)
        pygame.draw.rect(screen, (101, 67, 33), (x-14, y+3, 28, 38))
        # Metal studs
        pygame.draw.circle(screen, (192, 192, 192), (x-8, y+8), 2)
        pygame.draw.circle(screen, (192, 192, 192), (x+8, y+8), 2)
        # Torn shirt underneath
        pygame.draw.rect(screen, (139, 0, 0), (x-8, y+15, 16, 15))
        pygame.draw.line(screen, (0,0,0), (x-3, y+20), (x+3, y+25), 3)  # Tear
        # Arms (muscular, with tattoos)
        pygame.draw.line(screen, (224, 172, 105), (x-20, y+10), (x-25, y+25), 10)
        pygame.draw.line(screen, (224, 172, 105), (x+20, y+10), (x+25, y+25), 10)
        # Tattoo (skull)
        pygame.draw.circle(screen, (0,0,0), (x-22, y+15), 3)
        # Legs (ripped jeans)
        pygame.draw.line(screen, (72, 61, 139), (x-5, y+41), (x-5, y+70), 8)
        pygame.draw.line(screen, (72, 61, 139), (x+5, y+41), (x+5, y+70), 8)
        # Rips in jeans
        pygame.draw.line(screen, (224, 172, 105), (x-5, y+50), (x-5, y+55), 3)
        pygame.draw.line(screen, (224, 172, 105), (x+5, y+60), (x+5, y+65), 3)
        # Combat boots
        pygame.draw.ellipse(screen, (0,0,0), (x-12, y+68, 14, 10))
        pygame.draw.ellipse(screen, (0,0,0), (x-2, y+68, 14, 10))
        # Boot laces
        pygame.draw.line(screen, (139, 69, 19), (x-8, y+70), (x-4, y+70), 1)
        pygame.draw.line(screen, (139, 69, 19), (x+2, y+70), (x+6, y+70), 1)

# Realistic and Creepy Monster Drawing Functions for Survival Mode

def draw_zombie_monster(screen, x, y, size, damage_flash=False):
    """Draw a terrifying zombie monster"""
    flash_color = (255, 100, 100) if damage_flash else (60, 80, 40)
    
    # Body (decaying flesh)
    pygame.draw.ellipse(screen, flash_color, (x-size//3, y-size//3, size//1.5, size))
    
    # Head (grotesque)
    head_color = (80, 100, 60) if not damage_flash else (120, 140, 100)
    pygame.draw.ellipse(screen, head_color, (x-size//4, y-size//2, size//2, size//3))
    
    # Glowing red eyes
    pygame.draw.circle(screen, (255, 0, 0), (x-size//8, y-size//3), 3)
    pygame.draw.circle(screen, (255, 0, 0), (x+size//8, y-size//3), 3)
    pygame.draw.circle(screen, (255, 255, 255), (x-size//8, y-size//3), 1)
    pygame.draw.circle(screen, (255, 255, 255), (x+size//8, y-size//3), 1)
    
    # Gaping mouth with teeth
    pygame.draw.ellipse(screen, (0, 0, 0), (x-size//6, y-size//6, size//3, size//8))
    # Sharp teeth
    for i in range(3):
        tooth_x = x - size//8 + i * (size//12)
        pygame.draw.polygon(screen, (255, 255, 200), [(tooth_x, y-size//6), 
                           (tooth_x+2, y-size//6+6), (tooth_x-2, y-size//6+6)])
    
    # Decaying arms reaching out
    pygame.draw.line(screen, (60, 80, 40), (x-size//3, y-size//6), (x-size//2, y), 6)
    pygame.draw.line(screen, (60, 80, 40), (x+size//3, y-size//6), (x+size//2, y), 6)
    
    # Clawed hands
    pygame.draw.circle(screen, (40, 60, 20), (x-size//2, y), 4)
    pygame.draw.circle(screen, (40, 60, 20), (x+size//2, y), 4)
    
    # Blood drips
    if not damage_flash:
        for i in range(2):
            drip_x = x + random.randint(-size//4, size//4)
            pygame.draw.line(screen, (139, 0, 0), (drip_x, y+size//3), (drip_x, y+size//2), 2)

def draw_demon_monster(screen, x, y, size, damage_flash=False):
    """Draw a demonic creature with horns and flames"""
    flash_color = (255, 100, 100) if damage_flash else (120, 20, 20)
    
    # Body (dark red/black)
    pygame.draw.ellipse(screen, flash_color, (x-size//3, y-size//3, size//1.5, size))
    
    # Head with horns
    head_color = (100, 0, 0) if not damage_flash else (150, 50, 50)
    pygame.draw.ellipse(screen, head_color, (x-size//4, y-size//2, size//2, size//3))
    
    # Demonic horns
    pygame.draw.polygon(screen, (40, 40, 40), [(x-size//6, y-size//2), 
                       (x-size//4, y-size//1.5), (x-size//8, y-size//2.2)])
    pygame.draw.polygon(screen, (40, 40, 40), [(x+size//6, y-size//2), 
                       (x+size//4, y-size//1.5), (x+size//8, y-size//2.2)])
    
    # Burning eyes
    pygame.draw.circle(screen, (255, 100, 0), (x-size//8, y-size//3), 4)
    pygame.draw.circle(screen, (255, 100, 0), (x+size//8, y-size//3), 4)
    pygame.draw.circle(screen, (255, 255, 0), (x-size//8, y-size//3), 2)
    pygame.draw.circle(screen, (255, 255, 0), (x+size//8, y-size//3), 2)
    
    # Fanged mouth
    pygame.draw.ellipse(screen, (0, 0, 0), (x-size//5, y-size//8, size//2.5, size//6))
    # Large fangs
    pygame.draw.polygon(screen, (255, 255, 255), [(x-size//10, y-size//8), 
                       (x-size//12, y-size//20), (x-size//15, y-size//8)])
    pygame.draw.polygon(screen, (255, 255, 255), [(x+size//10, y-size//8), 
                       (x+size//12, y-size//20), (x+size//15, y-size//8)])
    
    # Clawed arms
    pygame.draw.line(screen, (80, 20, 20), (x-size//3, y-size//6), (x-size//1.8, y+size//6), 8)
    pygame.draw.line(screen, (80, 20, 20), (x+size//3, y-size//6), (x+size//1.8, y+size//6), 8)
    
    # Sharp claws
    for claw_offset in [-2, 0, 2]:
        pygame.draw.line(screen, (200, 200, 200), (x-size//1.8, y+size//6), 
                        (x-size//1.6, y+size//4+claw_offset), 2)
        pygame.draw.line(screen, (200, 200, 200), (x+size//1.8, y+size//6), 
                        (x+size//1.6, y+size//4+claw_offset), 2)

def draw_spider_monster(screen, x, y, size, damage_flash=False):
    """Draw a giant spider creature"""
    flash_color = (255, 100, 100) if damage_flash else (40, 40, 40)
    
    # Main body (abdomen)
    pygame.draw.ellipse(screen, flash_color, (x-size//4, y-size//6, size//2, size//2))
    
    # Head section
    head_color = (60, 60, 60) if not damage_flash else (100, 100, 100)
    pygame.draw.ellipse(screen, head_color, (x-size//6, y-size//3, size//3, size//4))
    
    # Multiple eyes (8 eyes like a real spider)
    eye_positions = [(x-size//12, y-size//4), (x+size//12, y-size//4),
                    (x-size//8, y-size//3.5), (x+size//8, y-size//3.5),
                    (x-size//15, y-size//5), (x+size//15, y-size//5),
                    (x-size//20, y-size//6), (x+size//20, y-size//6)]
    
    for eye_x, eye_y in eye_positions:
        pygame.draw.circle(screen, (255, 0, 0), (eye_x, eye_y), 2)
        pygame.draw.circle(screen, (255, 255, 255), (eye_x, eye_y), 1)
    
    # Eight hairy legs
    leg_color = (30, 30, 30) if not damage_flash else (70, 70, 70)
    for i in range(4):
        # Left legs
        leg_angle = i * 0.3 - 0.5
        leg_end_x = x - size//2 - int(size//3 * (1 + leg_angle))
        leg_end_y = y + int(size//4 * leg_angle)
        pygame.draw.line(screen, leg_color, (x-size//4, y), (leg_end_x, leg_end_y), 4)
        
        # Right legs
        leg_end_x = x + size//2 + int(size//3 * (1 + leg_angle))
        pygame.draw.line(screen, leg_color, (x+size//4, y), (leg_end_x, leg_end_y), 4)
        
        # Leg segments (joints)
        mid_x = x + int((leg_end_x - x) * 0.6)
        mid_y = y + int((leg_end_y - y) * 0.6)
        pygame.draw.circle(screen, leg_color, (mid_x, mid_y), 2)
    
    # Fangs/chelicerae
    pygame.draw.line(screen, (200, 200, 200), (x-size//12, y-size//6), (x-size//20, y-size//12), 3)
    pygame.draw.line(screen, (200, 200, 200), (x+size//12, y-size//6), (x+size//20, y-size//12), 3)

def draw_ghost_monster(screen, x, y, size, damage_flash=False):
    """Draw a translucent ghostly apparition"""
    alpha = 180 if not damage_flash else 255
    
    # Create a surface for transparency effects
    ghost_surface = pygame.Surface((size, size))
    ghost_surface.set_alpha(alpha)
    
    # Ghostly body (wispy and ethereal)
    body_color = (200, 200, 255) if not damage_flash else (255, 200, 200)
    pygame.draw.ellipse(ghost_surface, body_color, (size//4, size//3, size//2, size//1.5))
    
    # Wispy tail
    for i in range(3):
        tail_y = size//1.5 + i * (size//8)
        tail_width = size//2 - i * (size//8)
        if tail_width > 0:
            pygame.draw.ellipse(ghost_surface, body_color, 
                              (size//2 - tail_width//2, tail_y, tail_width, size//6))
    
    # Hollow, dark eye sockets
    pygame.draw.circle(ghost_surface, (0, 0, 0), (size//2 - size//8, size//2), 6)
    pygame.draw.circle(ghost_surface, (0, 0, 0), (size//2 + size//8, size//2), 6)
    
    # Glowing eyes inside sockets
    pygame.draw.circle(ghost_surface, (0, 255, 255), (size//2 - size//8, size//2), 3)
    pygame.draw.circle(ghost_surface, (0, 255, 255), (size//2 + size//8, size//2), 3)
    
    # Gaping mouth
    pygame.draw.ellipse(ghost_surface, (0, 0, 0), (size//2 - size//12, size//1.8, size//6, size//8))
    
    screen.blit(ghost_surface, (x - size//2, y - size//2))
    
    # Add floating particles around the ghost
    if not damage_flash:
        for i in range(4):
            particle_x = x + random.randint(-size//2, size//2)
            particle_y = y + random.randint(-size//2, size//2)
            pygame.draw.circle(screen, (150, 150, 255), (particle_x, particle_y), 1)

def draw_monster_by_type(screen, monster, damage_flash=False):
    """Draw a monster based on its type"""
    x, y = monster['rect'].center
    size = monster['rect'].width
    monster_type = monster.get('type', 'zombie')
    
    if monster_type == 'zombie':
        draw_zombie_monster(screen, x, y, size, damage_flash)
    elif monster_type == 'demon':
        draw_demon_monster(screen, x, y, size, damage_flash)
    elif monster_type == 'spider':
        draw_spider_monster(screen, x, y, size, damage_flash)
    elif monster_type == 'ghost':
        draw_ghost_monster(screen, x, y, size, damage_flash)
    else:
        # Fallback to zombie if type is unknown
        draw_zombie_monster(screen, x, y, size, damage_flash)

# Main game loop refactored into a function

def run_game(mode, player1_name, player2_name, char_choices, network=None, is_host=False, online=False):
    # Start original background music
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(resource_path('fart.mp3'))
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Error playing background music: {e}")
    # Initialize game state variables for each session
    player1 = pygame.Rect(100, HEIGHT//2, 50, 50)
    player2 = pygame.Rect(WIDTH-150, HEIGHT//2, 50, 50)
    player1_health = 5
    player2_health = 5
    speed = 6
    p1_right = True
    p2_right = False
    bullets = []
    player1_shots = 0
    player2_shots = 0
    player1_reload_time = 0
    player2_reload_time = 0
    RELOAD_LIMIT = 3
    RELOAD_DURATION = 3
    coin_rects = []
    player1_score = 0
    player2_score = 0
    coin_timer = 0
    if mode == 1:
        coin_timer = time.time() + 60
        for _ in range(10):
            x = random.randint(60, WIDTH-60)
            y = random.randint(100, HEIGHT-60)
            coin_rects.append(pygame.Rect(x, y, 24, 24))
    start_countdown()
    while True:
        now = time.time()
        if mode == 1 and now > coin_timer:
            winner = "Player 1" if player1_score > player2_score else ("Player 2" if player2_score > player1_score else "Tie")
            win_text = font.render(f"{winner} Wins!" if winner != "Tie" else "Tie!", True, (0,255,0))
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            return 'lobby'
        # Online networking - Ultra-optimized binary protocol
        if online:
            if is_host:
                # Only sync every 2 frames for position (30Hz), instant for bullets
                if not hasattr(player1, '_net_frame_count'):
                    player1._net_frame_count = 0
                    player1._last_x = player1.x
                    player1._last_y = player1.y
                    player1._last_health = player1_health
                
                player1._net_frame_count += 1
                
                # Build compact state - only send what changed
                my_state = {}
                
                # Position updates every 2 frames (30Hz) or if significant change (>5px)
                if player1._net_frame_count % 2 == 0 or abs(player1.x - player1._last_x) > 5 or abs(player1.y - player1._last_y) > 5:
                    my_state['p'] = [player1.x, player1.y, int(p1_right)]
                    player1._last_x = player1.x
                    player1._last_y = player1.y
                
                # Health updates only when changed
                if player1_health != player1._last_health:
                    my_state['h'] = player1_health
                    player1._last_health = player1_health
                
                # Bullets - only new ones
                new_bullets = [b for b in bullets if b['owner']==1 and not hasattr(b, '_synced')]
                if new_bullets:
                    my_state['b'] = [[b['rect'].x, b['rect'].y, b['dir']] for b in new_bullets]
                    for b in new_bullets:
                        b['_synced'] = True
                
                if my_state:  # Only send if there's something to send
                    network.send(my_state)
                # Receive updates
                try:
                    data = network.recv()
                    if data and isinstance(data, dict):
                        # Position update
                        if 'p' in data:
                            # Smooth interpolation for remote player
                            if not hasattr(player2, '_target_x'):
                                player2._target_x = data['p'][0]
                                player2._target_y = data['p'][1]
                            else:
                                player2._target_x = data['p'][0]
                                player2._target_y = data['p'][1]
                            
                            # Interpolate smoothly (reduce jitter)
                            player2.x = int(player2.x * 0.7 + player2._target_x * 0.3)
                            player2.y = int(player2.y * 0.7 + player2._target_y * 0.3)
                            p2_right = bool(data['p'][2])
                        
                        # Health update
                        if 'h' in data:
                            player2_health = data['h']
                        
                        # Bullets
                        if 'b' in data:
                            for bdata in data['b']:
                                # Check if bullet doesn't already exist
                                if not any(abs(b['rect'].x-bdata[0])<5 and abs(b['rect'].y-bdata[1])<5 and b['owner']==2 for b in bullets):
                                    bullets.append({'rect': pygame.Rect(bdata[0], bdata[1], 10, 10), 'dir': bdata[2], 'owner': 2})
                except:
                    pass
            else:
                # Client side - same optimizations
                if not hasattr(player2, '_net_frame_count'):
                    player2._net_frame_count = 0
                    player2._last_x = player2.x
                    player2._last_y = player2.y
                    player2._last_health = player2_health
                
                player2._net_frame_count += 1
                
                my_state = {}
                
                # Position updates every 2 frames or significant change
                if player2._net_frame_count % 2 == 0 or abs(player2.x - player2._last_x) > 5 or abs(player2.y - player2._last_y) > 5:
                    my_state['p'] = [player2.x, player2.y, int(p2_right)]
                    player2._last_x = player2.x
                    player2._last_y = player2.y
                
                # Health updates only when changed
                if player2_health != player2._last_health:
                    my_state['h'] = player2_health
                    player2._last_health = player2_health
                
                # Bullets - only new ones
                new_bullets = [b for b in bullets if b['owner']==2 and not hasattr(b, '_synced')]
                if new_bullets:
                    my_state['b'] = [[b['rect'].x, b['rect'].y, b['dir']] for b in new_bullets]
                    for b in new_bullets:
                        b['_synced'] = True
                
                if my_state:
                    network.send(my_state)
                try:
                    data = network.recv()
                    if data and isinstance(data, dict):
                        # Position update with interpolation
                        if 'p' in data:
                            if not hasattr(player1, '_target_x'):
                                player1._target_x = data['p'][0]
                                player1._target_y = data['p'][1]
                            else:
                                player1._target_x = data['p'][0]
                                player1._target_y = data['p'][1]
                            
                            # Smooth interpolation
                            player1.x = int(player1.x * 0.7 + player1._target_x * 0.3)
                            player1.y = int(player1.y * 0.7 + player1._target_y * 0.3)
                            p1_right = bool(data['p'][2])
                        
                        # Health update
                        if 'h' in data:
                            player1_health = data['h']
                        
                        # Bullets
                        if 'b' in data:
                            for bdata in data['b']:
                                if not any(abs(b['rect'].x-bdata[0])<5 and abs(b['rect'].y-bdata[1])<5 and b['owner']==1 for b in bullets):
                                    bullets.append({'rect': pygame.Rect(bdata[0], bdata[1], 10, 10), 'dir': bdata[2], 'owner': 1})
                except:
                    pass
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if mode == 0:
                if event.type == pygame.KEYDOWN:
                    # Player 1 weapon switching
                    if event.key == pygame.K_q:
                        p1_selected_weapon = "default"
                    elif event.key == pygame.K_e and p1_bazooka_left > 0:
                        p1_selected_weapon = "bazooka"
                    elif event.key == pygame.K_r and p1_kannon_left > 0:
                        p1_selected_weapon = "kannon"
                    # Player 2 weapon switching
                    elif event.key == pygame.K_o:
                        p2_selected_weapon = "default"
                    elif event.key == pygame.K_p and p2_bazooka_left > 0:
                        p2_selected_weapon = "bazooka"
                    elif event.key == pygame.K_l and p2_kannon_left > 0:
                        p2_selected_weapon = "kannon"
                    # Player 1 shoot (space only)
                    elif event.key == pygame.K_SPACE:
                        if player1_shots < RELOAD_LIMIT and now > player1_reload_time:
                            bx = player1.right if p1_right else player1.left - 10
                            # Determine weapon type and damage based on selected weapon
                            weapon_type = "default"
                            damage = 1
                            if p1_selected_weapon == "bazooka" and p1_bazooka_left > 0:
                                weapon_type = "bazooka"
                                damage = 2
                                p1_bazooka_left -= 1
                            elif p1_selected_weapon == "kannon" and p1_kannon_left > 0:
                                weapon_type = "kannon"
                                damage = 3
                                p1_kannon_left -= 1
                            bullets.append({'rect': pygame.Rect(bx, player1.centery-5, 10, 10), 'dir': 1 if p1_right else -1, 'owner': 1, 'weapon': weapon_type, 'damage': damage})
                            player1_shots += 1
                            if player1_shots == RELOAD_LIMIT:
                                player1_reload_time = now + RELOAD_DURATION
                    # Player 2 shoot (right shift)
                    if event.key == pygame.K_RSHIFT:
                        if player2_shots < RELOAD_LIMIT and now > player2_reload_time:
                            bx = player2.right if p2_right else player2.left - 10
                            # Determine weapon type and damage based on selected weapon
                            weapon_type = "default"
                            damage = 1
                            if p2_selected_weapon == "bazooka" and p2_bazooka_left > 0:
                                weapon_type = "bazooka"
                                damage = 2
                                p2_bazooka_left -= 1
                            elif p2_selected_weapon == "kannon" and p2_kannon_left > 0:
                                weapon_type = "kannon"
                                damage = 3
                                p2_kannon_left -= 1
                            bullets.append({'rect': pygame.Rect(bx, player2.centery-5, 10, 10), 'dir': 1 if p2_right else -1, 'owner': 2, 'weapon': weapon_type, 'damage': damage})
                            player2_shots += 1
                            if player2_shots == RELOAD_LIMIT:
                                player2_reload_time = now + RELOAD_DURATION
                    else:
                        pass  # Optionally show reload message

            else:
                # No shooting in coin mode
                pass
        # Reset shots after reload
        if player1_shots == RELOAD_LIMIT and now > player1_reload_time:
            player1_shots = 0
        if player2_shots == RELOAD_LIMIT and now > player2_reload_time:
            player2_shots = 0

        keys = pygame.key.get_pressed()
        
        # Online mode: Each player only controls their own character
        if net is not None:
            if is_host:
                # Host controls player1 only (WASD)
                if keys[pygame.K_a]:
                    player1.x -= speed
                    p1_right = False
                if keys[pygame.K_d]:
                    player1.x += speed
                    p1_right = True
                if keys[pygame.K_w]:
                    player1.y -= speed
                if keys[pygame.K_s]:
                    player1.y += speed
            else:
                # Client controls player2 only (Arrow keys)
                if keys[pygame.K_LEFT]:
                    player2.x -= speed
                    p2_right = False
                if keys[pygame.K_RIGHT]:
                    player2.x += speed
                    p2_right = True
                if keys[pygame.K_UP]:
                    player2.y -= speed
                if keys[pygame.K_DOWN]:
                    player2.y += speed
        else:
            # Local mode: Both players can be controlled
            # Player 1 controls (WASD)
            if keys[pygame.K_a]:
                player1.x -= speed
                p1_right = False
            if keys[pygame.K_d]:
                player1.x += speed
                p1_right = True
            if keys[pygame.K_w]:
                player1.y -= speed
            if keys[pygame.K_s]:
                player1.y += speed

            # Player 2 controls (Arrow keys)
            if keys[pygame.K_LEFT]:
                player2.x -= speed
                p2_right = False
            if keys[pygame.K_RIGHT]:
                player2.x += speed
                p2_right = True
            if keys[pygame.K_UP]:
                player2.y -= speed
            if keys[pygame.K_DOWN]:
                player2.y += speed

        # Update bullets
        for bullet in bullets[:]:
            bullet['rect'].x += bullet['dir'] * 8
            if bullet['rect'].right < 0 or bullet['rect'].left > WIDTH:
                bullets.remove(bullet)

        # Clamp players to screen
        if player1.left < 0:
            player1.left = 0
        if player1.right > WIDTH:
            player1.right = WIDTH
        if player1.top < 0:
            player1.top = 0
        if player1.bottom > HEIGHT:
            player1.bottom = HEIGHT
        if player2.left < 0:
            player2.left = 0
        if player2.right > WIDTH:
            player2.right = WIDTH
        if player2.top < 0:
            player2.top = 0
        if player2.bottom > HEIGHT:
            player2.bottom = HEIGHT

        # Coin collection logic
        if mode == 1:
            # Check for coin collection using full body hitbox
            player1_body = pygame.Rect(player1.centerx-20, player1.centery-35, 40, 110)
            player2_body = pygame.Rect(player2.centerx-20, player2.centery-35, 40, 110)
            for coin in coin_rects[:]:
                if player1_body.colliderect(coin):
                    player1_score += 1
                    coin_rects.remove(coin)
                elif player2_body.colliderect(coin):
                    player2_score += 1
                    coin_rects.remove(coin)
            # Respawn coins if needed
            while len(coin_rects) < 10:
                x = random.randint(60, WIDTH-60)
                y = random.randint(100, HEIGHT-60)
                coin_rects.append(pygame.Rect(x, y, 24, 24))

        # Draw everything
        if mode == 0 and has_battle_background:
            screen.blit(battle_background, (0, 0))
        else:
            screen.fill((30, 30, 30))
        # Draw map border
        print(f"Error playing background music: {e}")
    # Initialize game state variables for each session
    player1 = pygame.Rect(100, HEIGHT//2, 50, 50)
    player2 = pygame.Rect(WIDTH-150, HEIGHT//2, 50, 50)
    player1_health = 5
    player2_health = 5
    speed = 6
    p1_right = True
    p2_right = False
    bullets = []
    player1_shots = 0
    player2_shots = 0
    player1_reload_time = 0
    player2_reload_time = 0
    RELOAD_LIMIT = 3
    RELOAD_DURATION = 3
    coin_rects = []
    player1_score = 0
    player2_score = 0
    coin_timer = 0
    if mode == 1:
        coin_timer = time.time() + 30
        for _ in range(10):
            x = random.randint(60, WIDTH-60)
            y = random.randint(100, HEIGHT-60)
            coin_rects.append(pygame.Rect(x, y, 24, 24))

    # --- SYNCHRONIZED COUNTDOWN FOR ONLINE ---
    if online and network:
        if is_host:
            # Wait for client ready, then send 'start'
            network.recv()  # Wait for client 'ready'
            network.send('start')
        else:
            network.send('ready')
            network.recv()  # Wait for host 'start'
    start_countdown()
    countdown_done = True

    while True:
        now = time.time()
        # --- NETWORK SYNC (ONLINE BATTLE MODE) ---
        if online and network:
            # Send local state: x,y,right,health,bullets
            if is_host:
                my_bullets = '|'.join(f"{b['rect'].x},{b['rect'].y},{b['dir']},{b['owner']}" for b in bullets if b['owner']==1)
                my_state = f"{player1.x},{player1.y},{p1_right},{player1_health};{my_bullets}"
                network.send(my_state)
                try:
                    data = network.recv()
                    if data:
                        parts = data.split(';')
                        vals = parts[0].split(',')
                        if len(vals) >= 4:
                            player2.x = int(vals[0])
                            player2.y = int(vals[1])
                            p2_right = vals[2] == 'True'
                            player2_health = int(vals[3])
                        # Bullets from client
                        if len(parts) > 1 and parts[1]:
                            for bstr in parts[1].split('|'):
                                bx, by, bdir, bowner = bstr.split(',')
                                # Only add if not already present
                                if not any(abs(b['rect'].x-int(bx))<5 and abs(b['rect'].y-int(by))<5 and b['owner']==2 for b in bullets):
                                    bullets.append({'rect': pygame.Rect(int(bx), int(by), 10, 10), 'dir': int(bdir), 'owner': int(bowner)})
                except:
                    pass
            else:
                my_bullets = '|'.join(f"{b['rect'].x},{b['rect'].y},{b['dir']},{b['owner']}" for b in bullets if b['owner']==2)
                my_state = f"{player2.x},{player2.y},{p2_right},{player2_health};{my_bullets}"
                network.send(my_state)
                try:
                    data = network.recv()
                    if data:
                        parts = data.split(';')
                        vals = parts[0].split(',')
                        if len(vals) >= 4:
                            player1.x = int(vals[0])
                            player1.y = int(vals[1])
                            p1_right = vals[2] == 'True'
                            player1_health = int(vals[3])
                        # Bullets from host
                        if len(parts) > 1 and parts[1]:
                            for bstr in parts[1].split('|'):
                                bx, by, bdir, bowner = bstr.split(',')
                                if not any(abs(b['rect'].x-int(bx))<5 and abs(b['rect'].y-int(by))<5 and b['owner']==1 for b in bullets):
                                    bullets.append({'rect': pygame.Rect(int(bx), int(by), 10, 10), 'dir': int(bdir), 'owner': int(bowner)})
                except:
                    pass
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if mode == 0:
                if event.type == pygame.KEYDOWN:
                    # Player 1 weapon switching
                    if event.key == pygame.K_q:
                        p1_selected_weapon = "default"
                    elif event.key == pygame.K_e and p1_bazooka_left > 0:
                        p1_selected_weapon = "bazooka"
                    elif event.key == pygame.K_r and p1_kannon_left > 0:
                        p1_selected_weapon = "kannon"
                    # Player 2 weapon switching
                    elif event.key == pygame.K_o:
                        p2_selected_weapon = "default"
                    elif event.key == pygame.K_p and p2_bazooka_left > 0:
                        p2_selected_weapon = "bazooka"
                    elif event.key == pygame.K_l and p2_kannon_left > 0:
                        p2_selected_weapon = "kannon"
                    # Player 1 shoot (space only)
                    elif event.key == pygame.K_SPACE:
                        if player1_shots < RELOAD_LIMIT and now > player1_reload_time:
                            bx = player1.right if p1_right else player1.left - 10
                            # Determine weapon type and damage based on selected weapon
                            weapon_type = "default"
                            damage = 1
                            if p1_selected_weapon == "bazooka" and p1_bazooka_left > 0:
                                weapon_type = "bazooka"
                                damage = 2
                                p1_bazooka_left -= 1
                            elif p1_selected_weapon == "kannon" and p1_kannon_left > 0:
                                weapon_type = "kannon"
                                damage = 3
                                p1_kannon_left -= 1
                            bullets.append({'rect': pygame.Rect(bx, player1.centery-5, 10, 10), 'dir': 1 if p1_right else -1, 'owner': 1, 'weapon': weapon_type, 'damage': damage})
                            player1_shots += 1
                            if player1_shots == RELOAD_LIMIT:
                                player1_reload_time = now + RELOAD_DURATION
                    # Player 2 shoot (right shift)
                    if event.key == pygame.K_RSHIFT:
                        if player2_shots < RELOAD_LIMIT and now > player2_reload_time:
                            bx = player2.right if p2_right else player2.left - 10
                            # Determine weapon type and damage based on selected weapon
                            weapon_type = "default"
                            damage = 1
                            if p2_selected_weapon == "bazooka" and p2_bazooka_left > 0:
                                weapon_type = "bazooka"
                                damage = 2
                                p2_bazooka_left -= 1
                            elif p2_selected_weapon == "kannon" and p2_kannon_left > 0:
                                weapon_type = "kannon"
                                damage = 3
                                p2_kannon_left -= 1
                            bullets.append({'rect': pygame.Rect(bx, player2.centery-5, 10, 10), 'dir': 1 if p2_right else -1, 'owner': 2, 'weapon': weapon_type, 'damage': damage})
                            player2_shots += 1
                            if player2_shots == RELOAD_LIMIT:
                                player2_reload_time = now + RELOAD_DURATION
                    else:
                        pass  # Optionally show reload message

            else:
                # No shooting in coin mode
                pass
        # Reset shots after reload
        if player1_shots == RELOAD_LIMIT and now > player1_reload_time:
            player1_shots = 0
        if player2_shots == RELOAD_LIMIT and now > player2_reload_time:
            player2_shots = 0

        keys = pygame.key.get_pressed()
        # Player 1 controls (WASD)
        if keys[pygame.K_a]:
            player1.x -= speed
            p1_right = False
        if keys[pygame.K_d]:
            player1.x += speed
            p1_right = True
        if keys[pygame.K_w]:
            player1.y -= speed
        if keys[pygame.K_s]:
            player1.y += speed
        # Player 2 controls (Arrow keys)
        if keys[pygame.K_LEFT]:
            player2.x -= speed
            p2_right = False
        if keys[pygame.K_RIGHT]:
            player2.x += speed
            p2_right = True
        if keys[pygame.K_UP]:
            player2.y -= speed
        if keys[pygame.K_DOWN]:
            player2.y += speed

        # Define hitboxes for both players (covering the whole body)
        player1_hitbox = pygame.Rect(player1.centerx-20, player1.centery-35, 40, 110)
        player2_hitbox = pygame.Rect(player2.centerx-20, player2.centery-35, 40, 110)

        # Move bullets
        for bullet in bullets[:]:
            bullet['rect'].x += bullet['dir'] * 12
            # Remove if off screen
            if bullet['rect'].right < 0 or bullet['rect'].left > WIDTH:
                bullets.remove(bullet)
            # Collision with players (use full body hitbox)
            elif bullet['owner'] == 1 and bullet['rect'].colliderect(player2_hitbox):
                damage = bullet.get('damage', 1)  # Use weapon damage: bazooka=2, kannon=3, default=1
                player2_health -= damage
                bullets.remove(bullet)
            elif bullet['owner'] == 2 and bullet['rect'].colliderect(player1_hitbox):
                damage = bullet.get('damage', 1)  # Use weapon damage: bazooka=2, kannon=3, default=1
                player1_health -= damage
                bullets.remove(bullet)

        # Collision: if players touch, reduce health (battle mode only)
        if mode == 0 and player1.colliderect(player2):
            player1_health -= 1
            player2_health -= 1
            player1.x = 100
            player1.y = HEIGHT//2
            player2.x = WIDTH-150
            player2.y = HEIGHT//2

        # Border collision: stop player from going out of bounds
        if player1.left < 0:
            player1.left = 0
        if player1.right > WIDTH:
            player1.right = WIDTH
        if player1.top < 0:
            player1.top = 0
        if player1.bottom > HEIGHT:
            player1.bottom = HEIGHT
        if player2.left < 0:
            player2.left = 0
        if player2.right > WIDTH:
            player2.right = WIDTH
        if player2.top < 0:
            player2.top = 0
        if player2.bottom > HEIGHT:
            player2.bottom = HEIGHT

        # Coin collection logic
        if mode == 1:
            # Check for coin collection using full body hitbox
            player1_body = pygame.Rect(player1.centerx-20, player1.centery-35, 40, 110)
            player2_body = pygame.Rect(player2.centerx-20, player2.centery-35, 40, 110)
            for coin in coin_rects[:]:
                if player1_body.colliderect(coin):
                    player1_score += 1
                    coin_rects.remove(coin)
                elif player2_body.colliderect(coin):
                    player2_score += 1
                    coin_rects.remove(coin)
            # Respawn coins if needed
            while len(coin_rects) < 10:
                x = random.randint(60, WIDTH-60)
                y = random.randint(100, HEIGHT-60)
                coin_rects.append(pygame.Rect(x, y, 24, 24))

        # Draw everything
        screen.fill((30, 30, 30))
        # Draw map border
        border_color = (200, 200, 200)
        border_thickness = 8
        pygame.draw.rect(screen, border_color, (0, 0, WIDTH, HEIGHT), border_thickness)


        # Draw Player 1 (Cool, stylish)
        # Head (skin tone, sunglasses)
        pygame.draw.ellipse(screen, (224, 172, 105), (player1.centerx-15, player1.centery-35, 30, 38))
        pygame.draw.rect(screen, (0,0,0), (player1.centerx-12, player1.centery-28, 24, 8))
        pygame.draw.rect(screen, (30,144,255), (player1.centerx-12, player1.centery-28, 24, 8), 2)
        pygame.draw.arc(screen, (255,255,255), (player1.centerx-7, player1.centery-10, 14, 8), 3.14, 2*3.14, 2)
        pygame.draw.rect(screen, (0,255,255), (player1.centerx-15, player1.centery-35, 30, 8))
        pygame.draw.rect(screen, (0, 0, 200), (player1.centerx-10, player1.centery+3, 20, 38))
        pygame.draw.polygon(screen, (255,255,0), [(player1.centerx, player1.centery+10), (player1.centerx+6, player1.centery+30), (player1.centerx-6, player1.centery+30)])
        pygame.draw.line(screen, (224, 172, 105), (player1.centerx-20, player1.centery+10), (player1.centerx+20, player1.centery+10), 8)
        pygame.draw.circle(screen, (224, 172, 105), (player1.centerx-20, player1.centery+10), 5)
        pygame.draw.circle(screen, (224, 172, 105), (player1.centerx+20, player1.centery+10), 5)
        pygame.draw.line(screen, (0,0,0), (player1.centerx-5, player1.centery+41), (player1.centerx-5, player1.centery+70), 8)
        pygame.draw.line(screen, (0,0,0), (player1.centerx+5, player1.centery+41), (player1.centerx+5, player1.centery+70), 8)
        pygame.draw.ellipse(screen, (0,0,200), (player1.centerx-12, player1.centery+68, 14, 8))
        pygame.draw.ellipse(screen, (0,0,200), (player1.centerx-2, player1.centery+68, 14, 8))

        # Draw Player 2 (Cool, stylish)
        # Head (skin tone, sunglasses)
        pygame.draw.ellipse(screen, (224, 172, 105), (player2.centerx-15, player2.centery-35, 30, 38))
        pygame.draw.rect(screen, (0,0,0), (player2.centerx-12, player2.centery-28,  24, 8))
        pygame.draw.rect(screen, (255,0,0), (player2.centerx-12, player2.centery-28, 24, 8), 2)
        pygame.draw.arc(screen, (255,255,255), (player2.centerx-7, player2.centery-10, 14, 8), 3.14, 2*3.14, 2)
        pygame.draw.rect(screen, (255,255,0), (player2.centerx-15, player2.centery-35, 30, 8))
        pygame.draw.rect(screen, (200, 0, 0), (player2.centerx-10, player2.centery+3, 20, 38))
        pygame.draw.polygon(screen, (255,255,0), [(player2.centerx, player2.centery+18), (player2.centerx+6, player2.centery+30), (player2.centerx-6, player2.centery+30)])
        pygame.draw.line(screen, (224, 172, 105), (player2.centerx-20, player2.centery+10), (player2.centerx+20, player2.centery+10), 8)
        pygame.draw.circle(screen, (224, 172, 105), (player2.centerx-20, player2.centery+10), 5)
        pygame.draw.circle(screen, (224, 172, 105), (player2.centerx+20, player2.centery+10), 5)
        pygame.draw.line(screen, (0,0,0), (player2.centerx-5, player2.centery+41), (player2.centerx-5, player2.centery+70), 8)
        pygame.draw.line(screen, (0,0,0), (player2.centerx+5, player2.centery+41), (player2.centerx+5, player2.centery+70), 8)
        pygame.draw.ellipse(screen, (200,0,0), (player2.centerx-12, player2.centery+68, 14, 8))
        pygame.draw.ellipse(screen, (200,0,0), (player2.centerx-2, player2.centery+68, 14, 8))

        # Draw characters using selected styles
        if mode == 0:
            draw_mafia_character(screen, player1.centerx, player1.centery, char_choices[0])
            draw_mafia_character(screen, player2.centerx, player2.centery, char_choices[1])
        else:
            draw_explorer_character(screen, player1.centerx, player1.centery, char_choices[0])
            draw_explorer_character(screen, player2.centerx, player2.centery, char_choices[1])
        # Draw Player 1 name above head
        name_text1 = font.render(player1_name, True, (0,0,255))
        screen.blit(name_text1, (player1.centerx - name_text1.get_width()//2, player1.centery-60))

        # Draw Player 2 name above head
        name_text2 = font.render(player2_name, True, (255,0,0))
        screen.blit(name_text2, (player2.centerx - name_text2.get_width()//2, player2.centery-60))

        # Draw guns only in battle mode
        if mode == 0:
            # Gun follows hand (up/down movement)
            gun_offset_y1 = player1.centery+10
            gun_offset_y2 = player2.centery+10
            
            # Use simple default weapon for basic run_game function
            p1_weapon = "default"
            p2_weapon = "default"
            
            # Draw Player 1 weapon
            hand_x1 = player1.centerx + (20 if p1_right else -20)
            draw_weapon(screen, hand_x1, gun_offset_y1, p1_right, p1_weapon)
            
            # Draw Player 2 weapon
            hand_x2 = player2.centerx + (20 if p2_right else -20)
            draw_weapon(screen, hand_x2, gun_offset_y2, p2_right, p2_weapon)

        # Draw bullets
        for bullet in bullets:
            pygame.draw.rect(screen, (255,255,0), bullet['rect'])
        # Show shots and health only in battle mode
        if mode == 0:
            health_text = font.render(f"P1 Health: {player1_health}  P2 Health: {player2_health}", True, (255,255,255))
            screen.blit(health_text, (WIDTH//2 - health_text.get_width()//2, 20))
            if player1_shots < RELOAD_LIMIT and now > player1_reload_time:
                p1_status = f"P1 Shots: {RELOAD_LIMIT - player1_shots}"
            else:
                p1_status = "P1 Reloading..."
            if player2_shots < RELOAD_LIMIT and now > player2_reload_time:
                p2_status = f"P2 Shots: {RELOAD_LIMIT - player2_shots}"
            else:
                p2_status = "P2 Reloading..."
            p1_status_text = font.render(p1_status, True, (0,0,255))
            p2_status_text = font.render(p2_status, True, (255,0,0))
            screen.blit(p1_status_text, (40, 20))
            screen.blit(p2_status_text, (WIDTH-40-p2_status_text.get_width(), 20))

        # Win logic
        if player1_health <= 0 and player2_health <= 0:
            win_text = font.render("Tie!", True, (0,255,0))
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.mixer.music.stop()
            return 'lobby'  # Return to lobby after tie
        if player1_health <= 0:
            win_text = font.render("Player 2 Wins!", True, (255, 0, 0))
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.mixer.music.stop()
            return 'lobby'  # Return to lobby after P2 wins
        if player2_health <= 0:
            win_text = font.render("Player 1 Wins!", True, (0, 0, 255))
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.mixer.music.stop()
            return 'lobby'  # Return to lobby after P1 wins

        # Draw coins in coin mode
        if mode == 1:
            for coin in coin_rects:
                pygame.draw.circle(screen, (255,215,0), coin.center, 12)
            # Show scores and timer
            score_text = font.render(f"{player1_name}: {player1_score}   {player2_name}: {player2_score}", True, (255,255,255))
            screen.blit(score_text, (WIDTH//2-score_text.get_width()//2, 20))
            timer_text = font.render(f"Time left: {max(0,int(coin_timer-now))}", True, (255,255,255))
            screen.blit(timer_text, (WIDTH//2-timer_text.get_width()//2, 60))
            # End game after 30 seconds
            if now > coin_timer:
                winner = player1_name if player1_score > player2_score else player2_name if player2_score > player1_score else "Tie!"
                win_text = font.render(f"Winner: {winner}", True, (0,255,0))
                screen.blit(win_text, (WIDTH//2-win_text.get_width()//2, HEIGHT//2))
                pygame.display.flip()
                pygame.time.wait(3000)
                pygame.mixer.music.stop()
                # Go to shop, then battle mode
                run_coin_collection_and_shop(player1_name, player2_name, char_choices)
                return

        pygame.display.flip()
        clock.tick(60)

# Re-add Coin Collection mode

def run_coin_collection_and_shop(player1_name, player2_name, char_choices):
    # Play coin collection music
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(resource_path('coin.mp3'))
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Error playing coin collection music: {e}")
    
    # Coin collection phase
    player1_score = 0
    player2_score = 0
    paper_rects = []
    paper_timer = time.time() + 30
    player1 = pygame.Rect(100, HEIGHT//2, 50, 50)
    player2 = pygame.Rect(WIDTH-150, HEIGHT//2, 50, 50)
    speed = 6
    for _ in range(10):
        x = random.randint(60, WIDTH-60)
        y = random.randint(100, HEIGHT-60)
        paper_rects.append(pygame.Rect(x, y, 24, 24))
    start_countdown()
    while time.time() < paper_timer:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: player1.x -= speed
        if keys[pygame.K_d]: player1.x += speed
        if keys[pygame.K_w]: player1.y -= speed
        if keys[pygame.K_s]: player1.y += speed
        if keys[pygame.K_LEFT]: player2.x -= speed
        if keys[pygame.K_RIGHT]: player2.x += speed
        if keys[pygame.K_UP]: player2.y -= speed
        if keys[pygame.K_DOWN]: player2.y += speed
        player1.clamp_ip(pygame.Rect(0,0,WIDTH,HEIGHT))
        player2.clamp_ip(pygame.Rect(0,0,WIDTH,HEIGHT))
        p1_body = pygame.Rect(player1.centerx-20, player1.centery-35, 40, 110)
        p2_body = pygame.Rect(player2.centerx-20, player2.centery-35, 40, 110)
        for paper in paper_rects[:]:
            if p1_body.colliderect(paper):
                player1_score += 1
                paper_rects.remove(paper)
            elif p2_body.colliderect(paper):
                player2_score += 1
                paper_rects.remove(paper)
        while len(paper_rects) < 10:
            x = random.randint(60, WIDTH-60)
            y = random.randint(100, HEIGHT-60)
            paper_rects.append(pygame.Rect(x, y, 24, 24))
        screen.fill((30,30,30))
        for paper in paper_rects:
            # Draw realistic dollar bill
            # Main bill body (authentic dollar green)
            pygame.draw.rect(screen, (133, 187, 101), paper)
            
            # Border - ornate frame (darker green)
            pygame.draw.rect(screen, (85, 120, 65), paper, 2)
            
            # Inner decorative border
            inner_rect = pygame.Rect(paper.x+2, paper.y+2, paper.width-4, paper.height-4)
            pygame.draw.rect(screen, (100, 150, 80), inner_rect, 1)
            
            # Central seal/medallion (left side)
            seal_x = paper.x + paper.width // 4
            seal_y = paper.centery
            pygame.draw.circle(screen, (70, 100, 55), (seal_x, seal_y), 4)
            pygame.draw.circle(screen, (100, 150, 80), (seal_x, seal_y), 3)
            
            # Dollar sign in center (large, prominent)
            dollar_font = pygame.font.SysFont(None, 28)
            dollar_text = dollar_font.render("$", True, (70, 100, 55))
            screen.blit(dollar_text, (paper.centerx - dollar_text.get_width()//2, paper.centery - dollar_text.get_height()//2))
            
            # Decorative corners
            pygame.draw.circle(screen, (85, 120, 65), (paper.x+3, paper.y+3), 1)
            pygame.draw.circle(screen, (85, 120, 65), (paper.right-3, paper.y+3), 1)
            pygame.draw.circle(screen, (85, 120, 65), (paper.x+3, paper.bottom-3), 1)
            pygame.draw.circle(screen, (85, 120, 65), (paper.right-3, paper.bottom-3), 1)
            
            # Serial number lines (top and bottom)
            pygame.draw.line(screen, (90, 130, 70), (paper.x+3, paper.y+2), (paper.right-3, paper.y+2), 1)
            pygame.draw.line(screen, (90, 130, 70), (paper.x+3, paper.bottom-2), (paper.right-3, paper.bottom-2), 1)
            
            # Watermark effect (subtle lighter area)
            watermark_rect = pygame.Rect(paper.right-8, paper.y+2, 6, paper.height-4)
            watermark_surface = pygame.Surface((watermark_rect.width, watermark_rect.height))
            watermark_surface.set_alpha(30)
            watermark_surface.fill((200, 220, 180))
            screen.blit(watermark_surface, watermark_rect)
            
            # Highlight shine effect
            shine_surface = pygame.Surface((paper.width-6, 2))
            shine_surface.set_alpha(40)
            shine_surface.fill((255, 255, 255))
            screen.blit(shine_surface, (paper.x+3, paper.y+3))
        draw_explorer_character(screen, player1.centerx, player1.centery, char_choices[0])
        draw_explorer_character(screen, player2.centerx, player2.centery, char_choices[1])
        score_text = font.render(f"{player1_name}: {player1_score}   {player2_name}: {player2_score}", True, (255,255,255))
        screen.blit(score_text, (WIDTH//2-score_text.get_width()//2, 20))
        timer_text = font.render(f"Time left: {int(paper_timer-time.time())}", True, (255,255,255))
        screen.blit(timer_text, (WIDTH//2-timer_text.get_width()//2, 60))
        pygame.display.flip()
        clock.tick(60)
    # Shop phase
    shop_items = ["Bazooka (10)", "Kannon (20)", "Extra Life (10)"]
    p1_paper = player1_score
    p2_paper = player2_score
    p1_bazooka = 0
    p2_bazooka = 0
    p1_kannon = 0
    p2_kannon = 0
    p1_life = 0
    p2_life = 0
    for player, paper, bazooka, kannon, life, name in [(1, p1_paper, p1_bazooka, p1_kannon, p1_life, player1_name), (2, p2_paper, p2_bazooka, p2_kannon, p2_life, player2_name)]:
        done = False
        selected = 0
        while not done:
            screen.fill((30,30,30))
            shop_text = lobby_font.render(f"{name}'s Shop - Paper: {paper}", True, (0,255,0))
            screen.blit(shop_text, (WIDTH//2-shop_text.get_width()//2, HEIGHT//2-160))
            for i, item in enumerate(shop_items):
                color = (0,255,0) if i==selected else (200,200,200)
                item_text = font.render(item, True, color)
                screen.blit(item_text, (WIDTH//2-item_text.get_width()//2, HEIGHT//2-40+i*60))
            info_text = font.render("Enter: Buy, Esc: Done, Up/Down: Select", True, (255,255,255))
            screen.blit(info_text, (WIDTH//2-info_text.get_width()//2, HEIGHT-80))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected-1)%len(shop_items)
                    if event.key == pygame.K_DOWN:
                        selected = (selected+1)%len(shop_items)
                    if event.key == pygame.K_RETURN:
                        if selected == 0 and paper >= 10:
                            bazooka += 1
                            paper -= 10
                        if selected == 1 and paper >= 20:
                            kannon += 1
                            paper -= 20
                        if selected == 2 and paper >= 10:
                            life += 1
                            paper -= 10
                    if event.key == pygame.K_ESCAPE:
                        done = True
        if player == 1:
            p1_bazooka, p1_kannon, p1_life = bazooka, kannon, life
        else:
            p2_bazooka, p2_kannon, p2_life = bazooka, kannon, life
    # After shop, let players choose mafia character for battle
    mafia_choices = character_select(0)  # 0 = mafia mode
    # Start battle mode with upgrades and selected mafia
    result = run_game_with_upgrades(player1_name, player2_name, mafia_choices, p1_bazooka, p2_bazooka, p1_kannon, p2_kannon, p1_life, p2_life, mode=0)
    return

def draw_weapon(screen, x, y, right, weapon):
    # Draws ultra-realistic weapons with museum-quality detail
    if weapon == "bazooka":
        # Ultra-realistic RPG-7 Bazooka with extreme detail
        if right:
            # Main launch tube (olive green military grade)
            pygame.draw.rect(screen, (75, 83, 32), (x, y-9, 50, 18))
            # Tube highlights and shadows for 3D effect
            pygame.draw.rect(screen, (95, 103, 52), (x, y-9, 50, 4))  # Top highlight
            pygame.draw.rect(screen, (55, 63, 22), (x, y+5, 50, 4))  # Bottom shadow
            
            # Warhead cone (detailed rocket tip)
            pygame.draw.polygon(screen, (180, 50, 30), [(x+50, y), (x+65, y-2), (x+65, y+10), (x+50, y+9)])
            pygame.draw.polygon(screen, (220, 70, 50), [(x+50, y), (x+65, y-2), (x+57, y+4)])  # Highlight
            
            # Warhead stabilizing fins
            pygame.draw.polygon(screen, (160, 45, 25), [(x+58, y-8), (x+62, y-12), (x+62, y-2)])
            pygame.draw.polygon(screen, (160, 45, 25), [(x+58, y+17), (x+62, y+20), (x+62, y+11)])
            
            # Front sight and grip assembly
            pygame.draw.rect(screen, (40, 40, 40), (x+8, y-12, 3, 6))  # Front sight post
            pygame.draw.circle(screen, (50, 50, 50), (x+10, y-13), 2)  # Sight hood
            
            # Trigger guard and trigger mechanism
            pygame.draw.rect(screen, (30, 30, 30), (x+15, y+8, 8, 2))  # Guard bottom
            pygame.draw.rect(screen, (30, 30, 30), (x+15, y+2, 2, 8))  # Guard front
            pygame.draw.rect(screen, (30, 30, 30), (x+21, y+2, 2, 8))  # Guard back
            pygame.draw.rect(screen, (200, 180, 50), (x+17, y+5, 3, 4))  # Trigger (gold)
            
            # Wooden pistol grip with realistic grain
            pygame.draw.ellipse(screen, (101, 67, 33), (x+10, y+9, 16, 14))
            pygame.draw.rect(screen, (101, 67, 33), (x+12, y+10, 12, 12))
            # Wood grain details
            pygame.draw.line(screen, (85, 55, 28), (x+13, y+12), (x+13, y+20), 1)
            pygame.draw.line(screen, (85, 55, 28), (x+16, y+11), (x+16, y+21), 1)
            pygame.draw.line(screen, (85, 55, 28), (x+19, y+12), (x+19, y+20), 1)
            pygame.draw.line(screen, (85, 55, 28), (x+22, y+13), (x+22, y+19), 1)
            
            # Rear iron sight
            pygame.draw.rect(screen, (40, 40, 40), (x-5, y-10, 4, 8))
            pygame.draw.rect(screen, (60, 60, 60), (x-4, y-8, 2, 4))  # Sight notch
            
            # Strap mounts (metal loops)
            pygame.draw.circle(screen, (50, 50, 50), (x+5, y), 3, 2)
            pygame.draw.circle(screen, (50, 50, 50), (x+40, y), 3, 2)
            
            # Tube reinforcement bands
            pygame.draw.rect(screen, (50, 50, 50), (x+20, y-9, 2, 18))
            pygame.draw.rect(screen, (50, 50, 50), (x+35, y-9, 2, 18))
            
            # Venturi nozzle at back
            pygame.draw.rect(screen, (60, 60, 60), (x-8, y-6, 8, 12))
            pygame.draw.circle(screen, (30, 30, 30), (x-4, y), 4)  # Nozzle opening
            
        else:  # Left-facing
            # Main launch tube (olive green military grade)
            pygame.draw.rect(screen, (75, 83, 32), (x-50, y-9, 50, 18))
            # Tube highlights and shadows
            pygame.draw.rect(screen, (95, 103, 52), (x-50, y-9, 50, 4))
            pygame.draw.rect(screen, (55, 63, 22), (x-50, y+5, 50, 4))
            
            # Warhead cone
            pygame.draw.polygon(screen, (180, 50, 30), [(x-50, y), (x-65, y-2), (x-65, y+10), (x-50, y+9)])
            pygame.draw.polygon(screen, (220, 70, 50), [(x-50, y), (x-65, y-2), (x-57, y+4)])
            
            # Warhead fins
            pygame.draw.polygon(screen, (160, 45, 25), [(x-58, y-8), (x-62, y-12), (x-62, y-2)])
            pygame.draw.polygon(screen, (160, 45, 25), [(x-58, y+17), (x-62, y+20), (x-62, y+11)])
            
            # Front sight
            pygame.draw.rect(screen, (40, 40, 40), (x-11, y-12, 3, 6))
            pygame.draw.circle(screen, (50, 50, 50), (x-10, y-13), 2)
            
            # Trigger guard and trigger
            pygame.draw.rect(screen, (30, 30, 30), (x-23, y+8, 8, 2))
            pygame.draw.rect(screen, (30, 30, 30), (x-17, y+2, 2, 8))
            pygame.draw.rect(screen, (30, 30, 30), (x-23, y+2, 2, 8))
            pygame.draw.rect(screen, (200, 180, 50), (x-20, y+5, 3, 4))
            
            # Wooden pistol grip with grain
            pygame.draw.ellipse(screen, (101, 67, 33), (x-26, y+9, 16, 14))
            pygame.draw.rect(screen, (101, 67, 33), (x-24, y+10, 12, 12))
            pygame.draw.line(screen, (85, 55, 28), (x-13, y+12), (x-13, y+20), 1)
            pygame.draw.line(screen, (85, 55, 28), (x-16, y+11), (x-16, y+21), 1)
            pygame.draw.line(screen, (85, 55, 28), (x-19, y+12), (x-19, y+20), 1)
            pygame.draw.line(screen, (85, 55, 28), (x-22, y+13), (x-22, y+19), 1)
            
            # Rear sight
            pygame.draw.rect(screen, (40, 40, 40), (x+1, y-10, 4, 8))
            pygame.draw.rect(screen, (60, 60, 60), (x+2, y-8, 2, 4))
            
            # Strap mounts
            pygame.draw.circle(screen, (50, 50, 50), (x-5, y), 3, 2)
            pygame.draw.circle(screen, (50, 50, 50), (x-40, y), 3, 2)
            
            # Reinforcement bands
            pygame.draw.rect(screen, (50, 50, 50), (x-22, y-9, 2, 18))
            pygame.draw.rect(screen, (50, 50, 50), (x-37, y-9, 2, 18))
            
            # Venturi nozzle
            pygame.draw.rect(screen, (60, 60, 60), (x, y-6, 8, 12))
            pygame.draw.circle(screen, (30, 30, 30), (x+4, y), 4)
            
    elif weapon == "kannon":
        # Ultra-realistic Artillery Cannon with museum-grade detail
        if right:
            # Main barrel (battleship gray steel)
            pygame.draw.rect(screen, (105, 105, 105), (x, y-11, 45, 22))
            # Barrel highlights (top shine)
            pygame.draw.rect(screen, (145, 145, 145), (x, y-11, 45, 5))
            # Barrel shadows (bottom)
            pygame.draw.rect(screen, (75, 75, 75), (x, y+6, 45, 5))
            
            # Muzzle brake/flash suppressor (detailed gold-brass finish)
            pygame.draw.rect(screen, (184, 134, 11), (x+45, y-13, 8, 26))
            # Muzzle brake vents (4 rectangular cuts)
            pygame.draw.rect(screen, (30, 30, 30), (x+46, y-11, 6, 4))
            pygame.draw.rect(screen, (30, 30, 30), (x+46, y-5, 6, 4))
            pygame.draw.rect(screen, (30, 30, 30), (x+46, y+1, 6, 4))
            pygame.draw.rect(screen, (30, 30, 30), (x+46, y+7, 6, 4))
            # Muzzle highlights
            pygame.draw.rect(screen, (255, 215, 0), (x+45, y-13, 8, 3))
            
            # Bore opening (dark inner barrel)
            pygame.draw.circle(screen, (20, 20, 20), (x+53, y), 6)
            pygame.draw.circle(screen, (40, 40, 40), (x+53, y), 4)
            # Rifling effect
            pygame.draw.circle(screen, (30, 30, 30), (x+53, y), 3, 1)
            
            # Barrel reinforcement rings (heavy artillery style)
            pygame.draw.rect(screen, (85, 85, 85), (x+10, y-11, 3, 22))
            pygame.draw.rect(screen, (85, 85, 85), (x+20, y-11, 3, 22))
            pygame.draw.rect(screen, (85, 85, 85), (x+30, y-11, 3, 22))
            pygame.draw.rect(screen, (85, 85, 85), (x+40, y-11, 3, 22))
            
            # Breech mechanism (back of cannon)
            pygame.draw.rect(screen, (90, 90, 90), (x-10, y-8, 10, 16))
            pygame.draw.circle(screen, (70, 70, 70), (x-5, y), 6)
            pygame.draw.circle(screen, (50, 50, 50), (x-5, y), 3)  # Breech handle
            
            # Recoil compensator housing
            pygame.draw.rect(screen, (95, 95, 95), (x+5, y-14, 35, 3))
            pygame.draw.rect(screen, (95, 95, 95), (x+5, y+11, 35, 3))
            
            # Mounting bracket (connects to turret/vehicle)
            pygame.draw.rect(screen, (80, 80, 80), (x-5, y-5, 8, 10))
            pygame.draw.circle(screen, (100, 100, 100), (x-3, y-2), 2)  # Bolt
            pygame.draw.circle(screen, (100, 100, 100), (x-3, y+2), 2)  # Bolt
            
            # Elevation gear teeth
            for i in range(5):
                pygame.draw.rect(screen, (70, 70, 70), (x-8+i*2, y+12, 1, 3))
            
            # Sighting scope mount
            pygame.draw.rect(screen, (60, 60, 60), (x+15, y-16, 8, 4))
            pygame.draw.circle(screen, (40, 40, 60), (x+19, y-14), 2)  # Scope lens
            
            # Shell ejection port
            pygame.draw.rect(screen, (50, 50, 50), (x-8, y-3, 3, 6))
            
            # Warning stripes on barrel (yellow/black hazard)
            pygame.draw.polygon(screen, (255, 220, 0), [(x+25, y-11), (x+28, y-11), (x+25, y-8)])
            pygame.draw.polygon(screen, (0, 0, 0), [(x+28, y-11), (x+31, y-11), (x+28, y-8)])
            
        else:  # Left-facing
            # Main barrel
            pygame.draw.rect(screen, (105, 105, 105), (x-45, y-11, 45, 22))
            pygame.draw.rect(screen, (145, 145, 145), (x-45, y-11, 45, 5))
            pygame.draw.rect(screen, (75, 75, 75), (x-45, y+6, 45, 5))
            
            # Muzzle brake
            pygame.draw.rect(screen, (184, 134, 11), (x-53, y-13, 8, 26))
            pygame.draw.rect(screen, (30, 30, 30), (x-52, y-11, 6, 4))
            pygame.draw.rect(screen, (30, 30, 30), (x-52, y-5, 6, 4))
            pygame.draw.rect(screen, (30, 30, 30), (x-52, y+1, 6, 4))
            pygame.draw.rect(screen, (30, 30, 30), (x-52, y+7, 6, 4))
            pygame.draw.rect(screen, (255, 215, 0), (x-53, y-13, 8, 3))
            
            # Bore opening
            pygame.draw.circle(screen, (20, 20, 20), (x-53, y), 6)
            pygame.draw.circle(screen, (40, 40, 40), (x-53, y), 4)
            pygame.draw.circle(screen, (30, 30, 30), (x-53, y), 3, 1)
            
            # Reinforcement rings
            pygame.draw.rect(screen, (85, 85, 85), (x-13, y-11, 3, 22))
            pygame.draw.rect(screen, (85, 85, 85), (x-23, y-11, 3, 22))
            pygame.draw.rect(screen, (85, 85, 85), (x-33, y-11, 3, 22))
            pygame.draw.rect(screen, (85, 85, 85), (x-43, y-11, 3, 22))
            
            # Breech mechanism
            pygame.draw.rect(screen, (90, 90, 90), (x, y-8, 10, 16))
            pygame.draw.circle(screen, (70, 70, 70), (x+5, y), 6)
            pygame.draw.circle(screen, (50, 50, 50), (x+5, y), 3)
            
            # Recoil compensator
            pygame.draw.rect(screen, (95, 95, 95), (x-40, y-14, 35, 3))
            pygame.draw.rect(screen, (95, 95, 95), (x-40, y+11, 35, 3))
            
            # Mounting bracket
            pygame.draw.rect(screen, (80, 80, 80), (x-3, y-5, 8, 10))
            pygame.draw.circle(screen, (100, 100, 100), (x+3, y-2), 2)
            pygame.draw.circle(screen, (100, 100, 100), (x+3, y+2), 2)
            
            # Elevation gear
            for i in range(5):
                pygame.draw.rect(screen, (70, 70, 70), (x+6-i*2, y+12, 1, 3))
            
            # Sighting scope
            pygame.draw.rect(screen, (60, 60, 60), (x-23, y-16, 8, 4))
            pygame.draw.circle(screen, (40, 40, 60), (x-19, y-14), 2)
            
            # Shell ejection port
            pygame.draw.rect(screen, (50, 50, 50), (x+5, y-3, 3, 6))
            
            # Warning stripes
            pygame.draw.polygon(screen, (255, 220, 0), [(x-25, y-11), (x-28, y-11), (x-25, y-8)])
            pygame.draw.polygon(screen, (0, 0, 0), [(x-28, y-11), (x-31, y-11), (x-28, y-8)])
            
    else:
        # Ultra-realistic AK-47 assault rifle with extreme detail
        if right:
            # Wooden stock (rich walnut brown with grain)
            pygame.draw.rect(screen, (101, 67, 33), (x-20, y-5, 18, 10))
            # Wood grain detail
            pygame.draw.line(screen, (85, 55, 28), (x-18, y-4), (x-18, y+4), 1)
            pygame.draw.line(screen, (85, 55, 28), (x-14, y-3), (x-14, y+5), 1)
            pygame.draw.line(screen, (85, 55, 28), (x-10, y-4), (x-10, y+4), 1)
            pygame.draw.line(screen, (85, 55, 28), (x-6, y-3), (x-6, y+5), 1)
            
            # Receiver (stamped steel, dark gunmetal)
            pygame.draw.rect(screen, (65, 65, 65), (x-2, y-6, 32, 12))
            # Receiver top cover highlights
            pygame.draw.rect(screen, (85, 85, 85), (x-2, y-6, 32, 2))
            pygame.draw.rect(screen, (45, 45, 45), (x-2, y+4, 32, 2))
            
            # Dust cover rivets (authentic AK detail)
            pygame.draw.circle(screen, (55, 55, 55), (x+5, y-4), 1)
            pygame.draw.circle(screen, (55, 55, 55), (x+15, y-4), 1)
            pygame.draw.circle(screen, (55, 55, 55), (x+25, y-4), 1)
            
            # Barrel (extending forward)
            pygame.draw.rect(screen, (75, 75, 75), (x+30, y-3, 18, 6))
            pygame.draw.rect(screen, (95, 95, 95), (x+30, y-3, 18, 1))  # Top shine
            
            # Gas tube above barrel
            pygame.draw.rect(screen, (70, 70, 70), (x+32, y-7, 14, 3))
            # Gas tube rings
            pygame.draw.rect(screen, (60, 60, 60), (x+34, y-7, 1, 3))
            pygame.draw.rect(screen, (60, 60, 60), (x+40, y-7, 1, 3))
            
            # Front sight post
            pygame.draw.rect(screen, (50, 50, 50), (x+46, y-8, 2, 6))
            pygame.draw.circle(screen, (60, 60, 60), (x+47, y-9), 2)  # Sight hood
            pygame.draw.rect(screen, (200, 180, 50), (x+46, y-6, 2, 2))  # Gold tritium dot
            
            # Muzzle device (slant brake)
            pygame.draw.polygon(screen, (60, 60, 60), [(x+48, y-2), (x+52, y-4), (x+52, y+3), (x+48, y+3)])
            pygame.draw.circle(screen, (30, 30, 30), (x+52, y), 2)  # Bore
            
            # Magazine (curved banana mag - iconic AK feature)
            pygame.draw.polygon(screen, (120, 90, 50), [(x+8, y+6), (x+18, y+8), (x+18, y+20), (x+8, y+18)])
            # Magazine ribs
            pygame.draw.line(screen, (100, 75, 40), (x+10, y+8), (x+10, y+18), 1)
            pygame.draw.line(screen, (100, 75, 40), (x+14, y+8), (x+14, y+19), 1)
            # Magazine base plate
            pygame.draw.rect(screen, (80, 60, 30), (x+8, y+18, 10, 2))
            
            # Pistol grip (black polymer)
            pygame.draw.polygon(screen, (40, 40, 40), [(x+10, y+6), (x+16, y+6), (x+14, y+16), (x+8, y+14)])
            # Grip texture lines
            for i in range(5):
                pygame.draw.line(screen, (30, 30, 30), (x+10, y+7+i*2), (x+13, y+7+i*2), 1)
            
            # Trigger guard (stamped steel)
            pygame.draw.rect(screen, (60, 60, 60), (x+15, y+5, 2, 8))
            pygame.draw.rect(screen, (60, 60, 60), (x+15, y+13, 8, 2))
            pygame.draw.rect(screen, (60, 60, 60), (x+21, y+5, 2, 10))
            
            # Trigger (gold finish)
            pygame.draw.rect(screen, (200, 180, 50), (x+17, y+8, 3, 4))
            
            # Charging handle
            pygame.draw.rect(screen, (55, 55, 55), (x+20, y-8, 6, 3))
            pygame.draw.circle(screen, (65, 65, 65), (x+23, y-7), 2)
            
            # Rear sight (tangent style)
            pygame.draw.rect(screen, (50, 50, 50), (x+24, y-10, 3, 6))
            pygame.draw.rect(screen, (70, 70, 70), (x+25, y-8, 1, 3))  # Sight notch
            
            # Selector switch (safety lever)
            pygame.draw.rect(screen, (180, 50, 50), (x+4, y-8, 8, 2))  # Red safety indicator
            
            # Sling mount
            pygame.draw.circle(screen, (55, 55, 55), (x-5, y+2), 3, 2)
            pygame.draw.circle(screen, (55, 55, 55), (x+28, y-2), 3, 2)
            
        else:  # Left-facing
            # Wooden stock
            pygame.draw.rect(screen, (101, 67, 33), (x+2, y-5, 18, 10))
            pygame.draw.line(screen, (85, 55, 28), (x+18, y-4), (x+18, y+4), 1)
            pygame.draw.line(screen, (85, 55, 28), (x+14, y-3), (x+14, y+5), 1)
            pygame.draw.line(screen, (85, 55, 28), (x+10, y-4), (x+10, y+4), 1)
            pygame.draw.line(screen, (85, 55, 28), (x+6, y-3), (x+6, y+5), 1)
            
            # Receiver
            pygame.draw.rect(screen, (65, 65, 65), (x-30, y-6, 32, 12))
            pygame.draw.rect(screen, (85, 85, 85), (x-30, y-6, 32, 2))
            pygame.draw.rect(screen, (45, 45, 45), (x-30, y+4, 32, 2))
            
            # Rivets
            pygame.draw.circle(screen, (55, 55, 55), (x-5, y-4), 1)
            pygame.draw.circle(screen, (55, 55, 55), (x-15, y-4), 1)
            pygame.draw.circle(screen, (55, 55, 55), (x-25, y-4), 1)
            
            # Barrel
            pygame.draw.rect(screen, (75, 75, 75), (x-48, y-3, 18, 6))
            pygame.draw.rect(screen, (95, 95, 95), (x-48, y-3, 18, 1))
            
            # Gas tube
            pygame.draw.rect(screen, (70, 70, 70), (x-46, y-7, 14, 3))
            pygame.draw.rect(screen, (60, 60, 60), (x-35, y-7, 1, 3))
            pygame.draw.rect(screen, (60, 60, 60), (x-41, y-7, 1, 3))
            
            # Front sight
            pygame.draw.rect(screen, (50, 50, 50), (x-48, y-8, 2, 6))
            pygame.draw.circle(screen, (60, 60, 60), (x-47, y-9), 2)
            pygame.draw.rect(screen, (200, 180, 50), (x-48, y-6, 2, 2))
            
            # Muzzle device
            pygame.draw.polygon(screen, (60, 60, 60), [(x-48, y-2), (x-52, y-4), (x-52, y+3), (x-48, y+3)])
            pygame.draw.circle(screen, (30, 30, 30), (x-52, y), 2)
            
            # Magazine
            pygame.draw.polygon(screen, (120, 90, 50), [(x-8, y+6), (x-18, y+8), (x-18, y+20), (x-8, y+18)])
            pygame.draw.line(screen, (100, 75, 40), (x-10, y+8), (x-10, y+18), 1)
            pygame.draw.line(screen, (100, 75, 40), (x-14, y+8), (x-14, y+19), 1)
            pygame.draw.rect(screen, (80, 60, 30), (x-18, y+18, 10, 2))
            
            # Pistol grip
            pygame.draw.polygon(screen, (40, 40, 40), [(x-10, y+6), (x-16, y+6), (x-14, y+16), (x-8, y+14)])
            for i in range(5):
                pygame.draw.line(screen, (30, 30, 30), (x-10, y+7+i*2), (x-13, y+7+i*2), 1)
            
            # Trigger guard
            pygame.draw.rect(screen, (60, 60, 60), (x-17, y+5, 2, 8))
            pygame.draw.rect(screen, (60, 60, 60), (x-23, y+13, 8, 2))
            pygame.draw.rect(screen, (60, 60, 60), (x-23, y+5, 2, 10))
            
            # Trigger
            pygame.draw.rect(screen, (200, 180, 50), (x-20, y+8, 3, 4))
            
            # Charging handle
            pygame.draw.rect(screen, (55, 55, 55), (x-26, y-8, 6, 3))
            pygame.draw.circle(screen, (65, 65, 65), (x-23, y-7), 2)
            
            # Rear sight
            pygame.draw.rect(screen, (50, 50, 50), (x-27, y-10, 3, 6))
            pygame.draw.rect(screen, (70, 70, 70), (x-26, y-8, 1, 3))
            
            # Selector switch
            pygame.draw.rect(screen, (180, 50, 50), (x-12, y-8, 8, 2))
            
            # Sling mounts
            pygame.draw.circle(screen, (55, 55, 55), (x+5, y+2), 3, 2)
            pygame.draw.circle(screen, (55, 55, 55), (x-28, y-2), 3, 2)

# Main game with upgrades

def run_game_with_upgrades(player1_name, player2_name, char_choices, p1_bazooka, p2_bazooka, p1_kannon, p2_kannon, p1_life, p2_life, mode=0, net=None, is_host=False):
    # Battle mode with upgrades: bazooka/kannon = 2 shots each, then normal
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(resource_path('fart.mp3'))
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Error playing background music: {e}")
    player1 = pygame.Rect(100, HEIGHT//2, 50, 50)
    player2 = pygame.Rect(WIDTH-150, HEIGHT//2, 50, 50)
    player1_health = 5 + p1_life
    player2_health = 5 + p2_life
    speed = 6
    p1_right = True
    p2_right = False
    bullets = []
    player1_shots = 0
    player2_shots = 0
    player1_reload_time = 0
    player2_reload_time = 0
    RELOAD_LIMIT = 3
    RELOAD_DURATION = 3
    p1_bazooka_left = 2 * p1_bazooka
    p2_bazooka_left = 2 * p2_bazooka
    p1_kannon_left = 2 * p1_kannon
    p2_kannon_left = 2 * p2_kannon
    # Add weapon selection tracking
    p1_selected_weapon = "default"
    p2_selected_weapon = "default"
    # Cheat code tracking
    p1_cheat_code = ""  # Player 1 cheat: xxxzzzccc
    p2_cheat_code = ""  # Player 2 cheat: lllooolll
    
    # Network sync optimization - track last sent state
    last_p1_x, last_p1_y, last_p1_health = player1.x, player1.y, player1_health
    last_p2_x, last_p2_y, last_p2_health = player2.x, player2.y, player2_health
    last_p1_right, last_p2_right = p1_right, p2_right
    sync_counter = 0  # Send updates every N frames
    
    # Interpolation for smoother remote player movement (ULTRA optimized)
    target_p1_x, target_p1_y = player1.x, player1.y
    target_p2_x, target_p2_y = player2.x, player2.y
    interp_speed = 0.3  # Enhanced 70/30 weighted interpolation for ultra-smooth movement
    
    # Send position updates only when moved significantly (ULTRA optimized)
    position_threshold = 5  # pixels - adaptive sync rate for better responsiveness
    
    # Don't play countdown again if coming from online (already played)
    if net is None:
        start_countdown()
    
    while True:
        now = time.time()
        sync_counter += 1
        
        # ONLINE SYNC - Send and receive game state (optimized - reduced frequency + delta threshold)
        if net is not None:
            if is_host:
                # Only send if something changed significantly (every 3 frames OR significant movement)
                moved_significantly = (abs(player1.x - last_p1_x) > position_threshold or 
                                      abs(player1.y - last_p1_y) > position_threshold)
                health_changed = player1_health != last_p1_health
                direction_changed = p1_right != last_p1_right
                has_new_bullets = any(b['owner'] == 1 for b in bullets)
                
                # ULTRA: Adaptive 30Hz sync (every 2 frames) for better responsiveness
                if (sync_counter % 2 == 0 and (moved_significantly or health_changed or direction_changed)) or has_new_bullets:
                    # Send only changed data (delta compression concept)
                    update = {'type': 'game_state'}
                    if moved_significantly:
                        update['p1_x'] = player1.x
                        update['p1_y'] = player1.y
                    if health_changed:
                        update['p1_health'] = player1_health
                    if direction_changed:
                        update['p1_right'] = p1_right
                    if has_new_bullets:
                        # Only send new bullets (those created this frame)
                        new_bullets = []
                        for b in bullets:
                            if b['owner'] == 1:
                                bx, by = b['rect'].x, b['rect'].y
                                # Check if this bullet is "new" (near player position)
                                if abs(bx - player1.x) < 60 and abs(by - player1.y) < 60:
                                    new_bullets.append((bx, by, b['dir'], b.get('weapon', 'default'), b.get('damage', 1)))
                        if new_bullets:
                            update['bullets_p1'] = new_bullets
                    
                    if len(update) > 1:  # Only send if there's actual data
                        net.send(update)
                        last_p1_x, last_p1_y, last_p1_health, last_p1_right = player1.x, player1.y, player1_health, p1_right
                
                # Receive player2 state from client (check every frame for responsiveness)
                data = net.recv()
                if data and data.get('type') == 'game_state':
                    # Use interpolation for smooth movement
                    if 'p2_x' in data:
                        target_p2_x = data['p2_x']
                        player2.x = int(player2.x + (target_p2_x - player2.x) * interp_speed)
                    if 'p2_y' in data:
                        target_p2_y = data['p2_y']
                        player2.y = int(player2.y + (target_p2_y - player2.y) * interp_speed)
                    if 'p2_health' in data:
                        player2_health = data['p2_health']
                    if 'p2_right' in data:
                        p2_right = data['p2_right']
                    # Add client's bullets
                    for bx, by, bdir, weapon, damage in data.get('bullets_p2', []):
                        if not any(b['owner'] == 2 and abs(b['rect'].x - bx) < 10 and abs(b['rect'].y - by) < 10 for b in bullets):
                            bullets.append({
                                'rect': pygame.Rect(bx, by, 10, 10),
                                'dir': bdir,
                                'owner': 2,
                                'weapon': weapon,
                                'damage': damage
                            })
            else:
                # Client controls player2 - only send if something changed significantly
                moved_significantly = (abs(player2.x - last_p2_x) > position_threshold or 
                                      abs(player2.y - last_p2_y) > position_threshold)
                health_changed = player2_health != last_p2_health
                direction_changed = p2_right != last_p2_right
                has_new_bullets = any(b['owner'] == 2 for b in bullets)
                
                # ULTRA: Adaptive 30Hz sync (every 2 frames) for better responsiveness
                if (sync_counter % 2 == 0 and (moved_significantly or health_changed or direction_changed)) or has_new_bullets:
                    # Send only changed data
                    update = {'type': 'game_state'}
                    if moved_significantly:
                        update['p2_x'] = player2.x
                        update['p2_y'] = player2.y
                    if health_changed:
                        update['p2_health'] = player2_health
                    if direction_changed:
                        update['p2_right'] = p2_right
                    if has_new_bullets:
                        # Only send new bullets
                        new_bullets = []
                        for b in bullets:
                            if b['owner'] == 2:
                                bx, by = b['rect'].x, b['rect'].y
                                if abs(bx - player2.x) < 60 and abs(by - player2.y) < 60:
                                    new_bullets.append((bx, by, b['dir'], b.get('weapon', 'default'), b.get('damage', 1)))
                        if new_bullets:
                            update['bullets_p2'] = new_bullets
                    
                    if len(update) > 1:
                        net.send(update)
                        last_p2_x, last_p2_y, last_p2_health, last_p2_right = player2.x, player2.y, player2_health, p2_right
                
                # Receive player1 state from host (check every frame)
                data = net.recv()
                if data and data.get('type') == 'game_state':
                    # Use interpolation for smooth movement
                    if 'p1_x' in data:
                        target_p1_x = data['p1_x']
                        player1.x = int(player1.x + (target_p1_x - player1.x) * interp_speed)
                    if 'p1_y' in data:
                        target_p1_y = data['p1_y']
                        player1.y = int(player1.y + (target_p1_y - player1.y) * interp_speed)
                    if 'p1_health' in data:
                        player1_health = data['p1_health']
                    if 'p1_right' in data:
                        p1_right = data['p1_right']
                    # Add host's bullets
                    for bx, by, bdir, weapon, damage in data.get('bullets_p1', []):
                        if not any(b['owner'] == 1 and abs(b['rect'].x - bx) < 10 and abs(b['rect'].y - by) < 10 for b in bullets):
                            bullets.append({
                                'rect': pygame.Rect(bx, by, 10, 10),
                                'dir': bdir,
                                'owner': 1,
                                'weapon': weapon,
                                'damage': damage
                            })
        
        # (No online/network sync in this function)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if mode == 0:
                if event.type == pygame.KEYDOWN:
                    # Cheat code detection
                    key_name = pygame.key.name(event.key)
                    
                    # Player 1 cheat code: xxxzzzccc
                    if key_name in ['x', 'z', 'c']:
                        p1_cheat_code += key_name
                        # Keep only last 9 characters
                        if len(p1_cheat_code) > 9:
                            p1_cheat_code = p1_cheat_code[-9:]
                        # Check if cheat code matches
                        if p1_cheat_code == "xxxzzzccc":
                            player2_health = 0  # Player 1 wins!
                    else:
                        # Reset if wrong key pressed
                        if event.key not in [pygame.K_SPACE, pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d, 
                                            pygame.K_q, pygame.K_e, pygame.K_r,
                                            pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
                                            pygame.K_o, pygame.K_p, pygame.K_l, pygame.K_RETURN]:
                            p1_cheat_code = ""
                    
                    # Player 2 cheat code: lllooolll
                    if key_name in ['l', 'o']:
                        p2_cheat_code += key_name
                        # Keep only last 9 characters
                        if len(p2_cheat_code) > 9:
                            p2_cheat_code = p2_cheat_code[-9:]
                        # Check if cheat code matches
                        if p2_cheat_code == "lllooolll":
                            player1_health = 0  # Player 2 wins!
                    else:
                        # Reset if wrong key pressed (but allow l,o,p for weapon switching)
                        if event.key not in [pygame.K_SPACE, pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d, 
                                            pygame.K_q, pygame.K_e, pygame.K_r,
                                            pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
                                            pygame.K_o, pygame.K_p, pygame.K_l, pygame.K_RETURN]:
                            p2_cheat_code = ""
                    
                    # Player 1 weapon switching
                    if event.key == pygame.K_q:
                        p1_selected_weapon = "default"
                    elif event.key == pygame.K_e and p1_bazooka_left > 0:
                        p1_selected_weapon = "bazooka"
                    elif event.key == pygame.K_r and p1_kannon_left > 0:
                        p1_selected_weapon = "kannon"
                    # Player 2 weapon switching
                    elif event.key == pygame.K_o:
                        p2_selected_weapon = "default"
                    elif event.key == pygame.K_p and p2_bazooka_left > 0:
                        p2_selected_weapon = "bazooka"
                    elif event.key == pygame.K_l and p2_kannon_left > 0:
                        p2_selected_weapon = "kannon"
                    # Player 1 shoot (space only)
                    elif event.key == pygame.K_SPACE:
                        if player1_shots < RELOAD_LIMIT and now > player1_reload_time:
                            bx = player1.right if p1_right else player1.left - 10
                            # Determine weapon type and damage based on selected weapon
                            weapon_type = "default"
                            damage = 1
                            if p1_selected_weapon == "bazooka" and p1_bazooka_left > 0:
                                weapon_type = "bazooka"
                                damage = 2
                                p1_bazooka_left -= 1
                            elif p1_selected_weapon == "kannon" and p1_kannon_left > 0:
                                weapon_type = "kannon"
                                damage = 3
                                p1_kannon_left -= 1
                            bullets.append({'rect': pygame.Rect(bx, player1.centery-5, 10, 10), 'dir': 1 if p1_right else -1, 'owner': 1, 'weapon': weapon_type, 'damage': damage})
                            player1_shots += 1
                            if player1_shots == RELOAD_LIMIT:
                                player1_reload_time = now + RELOAD_DURATION
                    # Player 2 shoot (right shift)
                    if event.key == pygame.K_RSHIFT:
                        if player2_shots < RELOAD_LIMIT and now > player2_reload_time:
                            bx = player2.right if p2_right else player2.left - 10
                            # Determine weapon type and damage based on selected weapon
                            weapon_type = "default"
                            damage = 1
                            if p2_selected_weapon == "bazooka" and p2_bazooka_left > 0:
                                weapon_type = "bazooka"
                                damage = 2
                                p2_bazooka_left -= 1
                            elif p2_selected_weapon == "kannon" and p2_kannon_left > 0:
                                weapon_type = "kannon"
                                damage = 3
                                p2_kannon_left -= 1
                            bullets.append({'rect': pygame.Rect(bx, player2.centery-5, 10, 10), 'dir': 1 if p2_right else -1, 'owner': 2, 'weapon': weapon_type, 'damage': damage})
                            player2_shots += 1
                            if player2_shots == RELOAD_LIMIT:
                                player2_reload_time = now + RELOAD_DURATION
                    else:
                        pass  # Optionally show reload message

            else:
                # No shooting in coin mode
                pass
        # Reset shots after reload
        if player1_shots == RELOAD_LIMIT and now > player1_reload_time:
            player1_shots = 0
        if player2_shots == RELOAD_LIMIT and now > player2_reload_time:
            player2_shots = 0

        keys = pygame.key.get_pressed()
        # Player 1 controls (WASD)
        if keys[pygame.K_a]:
            player1.x -= speed
            p1_right = False
        if keys[pygame.K_d]:
            player1.x += speed
            p1_right = True
        if keys[pygame.K_w]:
            player1.y -= speed
        if keys[pygame.K_s]:
            player1.y += speed
        # Player 2 controls (Arrow keys)
        if keys[pygame.K_LEFT]:
            player2.x -= speed
            p2_right = False
        if keys[pygame.K_RIGHT]:
            player2.x += speed
            p2_right = True
        if keys[pygame.K_UP]:
            player2.y -= speed
        if keys[pygame.K_DOWN]:
            player2.y += speed

        # Define hitboxes for both players (covering the whole body)
        player1_hitbox = pygame.Rect(player1.centerx-20, player1.centery-35, 40, 110)
        player2_hitbox = pygame.Rect(player2.centerx-20, player2.centery-35, 40, 110)

        # Move bullets
        for bullet in bullets[:]:
            bullet['rect'].x += bullet['dir'] * 12
            # Remove if off screen
            if bullet['rect'].right < 0 or bullet['rect'].left > WIDTH:
                bullets.remove(bullet)
            # Collision with players (use full body hitbox)
            elif bullet['owner'] == 1 and bullet['rect'].colliderect(player2_hitbox):
                damage = bullet.get('damage', 1)  # Use weapon damage: bazooka=2, kannon=3, default=1
                player2_health -= damage
                bullets.remove(bullet)
            elif bullet['owner'] == 2 and bullet['rect'].colliderect(player1_hitbox):
                damage = bullet.get('damage', 1)  # Use weapon damage: bazooka=2, kannon=3, default=1
                player1_health -= damage
                bullets.remove(bullet)

        # Collision: if players touch, reduce health (battle mode only)
        if mode == 0 and player1.colliderect(player2):
            player1_health -= 1
            player2_health -= 1
            player1.x = 100
            player1.y = HEIGHT//2
            player2.x = WIDTH-150
            player2.y = HEIGHT//2

        # Border collision: stop player from going out of bounds
        if player1.left < 0:
            player1.left = 0
        if player1.right > WIDTH:
            player1.right = WIDTH
        if player1.top < 0:
            player1.top = 0
        if player1.bottom > HEIGHT:
            player1.bottom = HEIGHT
        if player2.left < 0:
            player2.left = 0
        if player2.right > WIDTH:
            player2.right = WIDTH
        if player2.top < 0:
            player2.top = 0
        if player2.bottom > HEIGHT:
            player2.bottom = HEIGHT

        # Coin collection logic
        if mode == 1:
            # Check for coin collection using full body hitbox
            player1_body = pygame.Rect(player1.centerx-20, player1.centery-35, 40, 110)
            player2_body = pygame.Rect(player2.centerx-20, player2.centery-35, 40, 110)
            for coin in coin_rects[:]:
                if player1_body.colliderect(coin):
                    player1_score += 1
                    coin_rects.remove(coin)
                elif player2_body.colliderect(coin):
                    player2_score += 1
                    coin_rects.remove(coin)
            # Respawn coins if needed
            while len(coin_rects) < 10:
                x = random.randint(60, WIDTH-60)
                y = random.randint(100, HEIGHT-60)
                coin_rects.append(pygame.Rect(x, y, 24, 24))

        # Draw everything
        if mode == 0 and has_battle_background:
            screen.blit(battle_background, (0, 0))
        else:
            screen.fill((30, 30, 30))
        # Draw map border
        border_color = (200, 200, 200)
        border_thickness = 8
        pygame.draw.rect(screen, border_color, (0, 0, WIDTH, HEIGHT), border_thickness)


        # Draw Player 1 (Cool, stylish)
        # Head (skin tone, sunglasses)
        pygame.draw.ellipse(screen, (224, 172, 105), (player1.centerx-15, player1.centery-35, 30, 38))
        pygame.draw.rect(screen, (0,0,0), (player1.centerx-12, player1.centery-28, 24, 8))
        pygame.draw.rect(screen, (30,144,255), (player1.centerx-12, player1.centery-28, 24, 8), 2)
        pygame.draw.arc(screen, (255,255,255), (player1.centerx-7, player1.centery-10, 14, 8), 3.14, 2*3.14, 2)
        pygame.draw.rect(screen, (0,255,255), (player1.centerx-15, player1.centery-35, 30, 8))
        pygame.draw.rect(screen, (0, 0, 200), (player1.centerx-10, player1.centery+3, 20, 38))
        pygame.draw.polygon(screen, (255,255,0), [(player1.centerx, player1.centery+10), (player1.centerx+6, player1.centery+30), (player1.centerx-6, player1.centery+30)])
        pygame.draw.line(screen, (224, 172, 105), (player1.centerx-20, player1.centery+10), (player1.centerx+20, player1.centery+10), 8)
        pygame.draw.circle(screen, (224, 172, 105), (player1.centerx-20, player1.centery+10), 5)
        pygame.draw.circle(screen, (224, 172, 105), (player1.centerx+20, player1.centery+10), 5)
        pygame.draw.line(screen, (0,0,0), (player1.centerx-5, player1.centery+41), (player1.centerx-5, player1.centery+70), 8)
        pygame.draw.line(screen, (0,0,0), (player1.centerx+5, player1.centery+41), (player1.centerx+5, player1.centery+70), 8)
        pygame.draw.ellipse(screen, (0,0,200), (player1.centerx-12, player1.centery+68, 14, 8))
        pygame.draw.ellipse(screen, (0,0,200), (player1.centerx-2, player1.centery+68, 14, 8))

        # Draw Player 2 (Cool, stylish)
        # Head (skin tone, sunglasses)
        pygame.draw.ellipse(screen, (224, 172, 105), (player2.centerx-15, player2.centery-35, 30, 38))
        pygame.draw.rect(screen, (0,0,0), (player2.centerx-12, player2.centery-28,  24, 8))
        pygame.draw.rect(screen, (255,0,0), (player2.centerx-12, player2.centery-28, 24, 8), 2)
        pygame.draw.arc(screen, (255,255,255), (player2.centerx-7, player2.centery-10, 14, 8), 3.14, 2*3.14, 2)
        pygame.draw.rect(screen, (255,255,0), (player2.centerx-15, player2.centery-35, 30, 8))
        pygame.draw.rect(screen, (200, 0, 0), (player2.centerx-10, player2.centery+3, 20, 38))
        pygame.draw.polygon(screen, (255,255,0), [(player2.centerx, player2.centery+18), (player2.centerx+6, player2.centery+30), (player2.centerx-6, player2.centery+30)])
        pygame.draw.line(screen, (224, 172, 105), (player2.centerx-20, player2.centery+10), (player2.centerx+20, player2.centery+10), 8)
        pygame.draw.circle(screen, (224, 172, 105), (player2.centerx-20, player2.centery+10), 5)
        pygame.draw.circle(screen, (224, 172, 105), (player2.centerx+20, player2.centery+10), 5)
        pygame.draw.line(screen, (0,0,0), (player2.centerx-5, player2.centery+41), (player2.centerx-5, player2.centery+70), 8)
        pygame.draw.line(screen, (0,0,0), (player2.centerx+5, player2.centery+41), (player2.centerx+5, player2.centery+70), 8)
        pygame.draw.ellipse(screen, (200,0,0), (player2.centerx-12, player2.centery+68, 14, 8))
        pygame.draw.ellipse(screen, (200,0,0), (player2.centerx-2, player2.centery+68, 14, 8))

        # Draw characters using selected styles
        if mode == 0:
            draw_mafia_character(screen, player1.centerx, player1.centery, char_choices[0])
            draw_mafia_character(screen, player2.centerx, player2.centery, char_choices[1])
        else:
            draw_explorer_character(screen, player1.centerx, player1.centery, char_choices[0])
            draw_explorer_character(screen, player2.centerx, player2.centery, char_choices[1])
        # Draw Player 1 name above head
        name_text1 = font.render(player1_name, True, (0,0,255))
        screen.blit(name_text1, (player1.centerx - name_text1.get_width()//2, player1.centery-60))

        # Draw Player 2 name above head
        name_text2 = font.render(player2_name, True, (255,0,0))
        screen.blit(name_text2, (player2.centerx - name_text2.get_width()//2, player2.centery-60))

        # Draw guns only in battle mode
        if mode == 0:
            # Gun follows hand (up/down movement)
            gun_offset_y1 = player1.centery+10
            gun_offset_y2 = player2.centery+10
            
            # Use the currently selected weapon for display
            p1_weapon = p1_selected_weapon
            p2_weapon = p2_selected_weapon
            
            # Draw Player 1 weapon
            hand_x1 = player1.centerx + (20 if p1_right else -20)
            draw_weapon(screen, hand_x1, gun_offset_y1, p1_right, p1_weapon)
            
            # Draw Player 2 weapon
            hand_x2 = player2.centerx + (20 if p2_right else -20)
            draw_weapon(screen, hand_x2, gun_offset_y2, p2_right, p2_weapon)

        # Draw bullets
        for bullet in bullets:
            pygame.draw.rect(screen, (255,255,0), bullet['rect'])
        # Show health and shots
        health_text = font.render(f"P1 Health: {player1_health}  P2 Health: {player2_health}", True, (255,255,255))
        screen.blit(health_text, (WIDTH//2 - health_text.get_width()//2, 20))
        if player1_shots < RELOAD_LIMIT and now > player1_reload_time:
            p1_status = f"P1 Shots: {RELOAD_LIMIT - player1_shots}"
        else:
            p1_status = "P1 Reloading..."
        if player2_shots < RELOAD_LIMIT and now > player2_reload_time:
            p2_status = f"P2 Shots: {RELOAD_LIMIT - player2_shots}"
        else:
            p2_status = "P2 Reloading..."
        # Show bazooka/kannon shots left (only if player has upgrades)
        if p1_bazooka + p1_kannon > 0 or p2_bazooka + p2_kannon > 0:
            upgrade_text1 = font.render(f"Bazooka:{p1_bazooka_left} Kannon:{p1_kannon_left}", True, (0,255,0))
            upgrade_text2 = font.render(f"Bazooka:{p2_bazooka_left} Kannon:{p2_kannon_left}", True, (255,255,0))
            screen.blit(upgrade_text1, (40, 60))
            screen.blit(upgrade_text2, (WIDTH-40-upgrade_text2.get_width(), 60))
        p1_status_text = font.render(p1_status, True, (0,0,255))
        p2_status_text = font.render(p2_status, True, (255,0,0))
        screen.blit(p1_status_text, (40, 20))
        screen.blit(p2_status_text, (WIDTH-40-p2_status_text.get_width(), 20))
        # Show weapon switch instructions (only if player has upgrades)
        if p1_bazooka + p1_kannon > 0 or p2_bazooka + p2_kannon > 0:
            instructions1 = font.render("P1: Q=Default, E=Bazooka, R=Kannon", True, (0,255,0))
            instructions2 = font.render("P2: O=Default, P=Bazooka, L=Kannon", True, (255,255,0))
            screen.blit(instructions1, (40, HEIGHT-80))
            screen.blit(instructions2, (WIDTH-40-instructions2.get_width(), HEIGHT-80))
            # Show current selected weapons (only if upgrades available)
            current_weapon1 = font.render(f"P1 Weapon: {p1_selected_weapon.upper()}", True, (0,255,255))
            current_weapon2 = font.render(f"P2 Weapon: {p2_selected_weapon.upper()}", True, (255,0,255))
            screen.blit(current_weapon1, (40, HEIGHT-40))
            screen.blit(current_weapon2, (WIDTH-40-current_weapon2.get_width(), HEIGHT-40))
        # Win logic
        if player1_health <= 0 and player2_health <= 0:
            win_text = font.render("Tie!", True, (0,255,0))
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.mixer.music.stop()
            return 'lobby'  # Return to lobby after tie
        if player1_health <= 0:
            win_text = font.render("Player 2 Wins!", True, (255, 0, 0))
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.mixer.music.stop()
            return 'lobby'  # Return to lobby after P2 wins
        if player2_health <= 0:
            win_text = font.render("Player 1 Wins!", True, (0, 0, 255))
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.mixer.music.stop()
            return 'lobby'  # Return to lobby after P1 wins
        pygame.display.flip()
        clock.tick(60)

def point_in_polygon(x, y, poly):
    # Ray casting algorithm for point-in-polygon
    n = len(poly)
    inside = False
    px, py = x, y
    for i in range(n):
        j = (i-1)%n
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj-xi)*(py-yi)/(yj-yi)+xi):
            inside = not inside
    return inside

def draw_monster(screen, rect, color, hp):
    # Even more realistic and menacing monster
    import pygame.gfxdraw
    import math
    t = pygame.time.get_ticks() // 100 % 6
    breath = 4 + math.sin(t) * 2
    # Body polygon
    body_points = [
        (rect.left+8, rect.top+10+breath),
        (rect.left+rect.width//4, rect.top),
        (rect.centerx, rect.top+random.randint(0,8)),
        (rect.right-rect.width//4, rect.top),
        (rect.right-8, rect.top+10+breath),
        (rect.right, rect.centery-10),
        (rect.right-8, rect.bottom-18),
        (rect.centerx+random.randint(-8,8), rect.bottom-8-breath),
        (rect.left+8, rect.bottom-18),
        (rect.left, rect.centery-10)
    ]
    pygame.gfxdraw.filled_polygon(screen, body_points, color)
    # Arms (left/right): rectangles
    left_arm_rect = pygame.Rect(rect.left-18, rect.centery+8, 18, 18)
    right_arm_rect = pygame.Rect(rect.right, rect.centery+8, 18, 18)
    pygame.draw.rect(screen, color, left_arm_rect)
    pygame.draw.rect(screen, color, right_arm_rect)
    # Legs (left/right): rectangles
    left_leg_rect = pygame.Rect(rect.left+8, rect.bottom-4, 12, 24)
    right_leg_rect = pygame.Rect(rect.right-20, rect.bottom-4, 12, 24)
    pygame.draw.rect(screen, color, left_leg_rect)
    pygame.draw.rect(screen, color, right_leg_rect)
    # Head: ellipse
    head_rect = pygame.Rect(rect.centerx-18, rect.top-18, 36, 28)
    pygame.draw.ellipse(screen, color, head_rect)
    # Scales/bumpy skin
    for i in range(8):
        scale_x = rect.left+random.randint(10,rect.width-20)
        scale_y = rect.top+random.randint(10,rect.height-20)
        pygame.draw.ellipse(screen, (max(color[0]-30,0), max(color[1]-30,0), max(color[2]-30,0)), (scale_x, scale_y, 8, 5))
    # Spikes on back
    for i in range(5):
        spike_x = rect.left+20+i*rect.width//6
        pygame.draw.polygon(screen, (60,60,60), [(spike_x, rect.top+8), (spike_x+8, rect.top-12), (spike_x+16, rect.top+8)])
    # Asymmetrical horns
    pygame.draw.polygon(screen, (120,120,120), [(rect.left+18, rect.top+10), (rect.left+8, rect.top-18), (rect.left+28, rect.top+10)])
    pygame.draw.polygon(screen, (120,120,120), [(rect.right-18, rect.top+10), (rect.right-8, rect.top-28), (rect.right-28, rect.top+10)])
    # Arms (clawed)
    arm_y = rect.centery+8
    pygame.draw.line(screen, color, (rect.left, arm_y), (rect.left-18, arm_y+18), 10)
    pygame.draw.line(screen, color, (rect.right, arm_y), (rect.right+18, arm_y+18), 10)
    pygame.draw.line(screen, (80,80,80), (rect.left-18, arm_y+18), (rect.left-28, arm_y+28), 5)
    pygame.draw.line(screen, (80,80,80), (rect.right+18, arm_y+18), (rect.right+28, arm_y+28), 5)
    # Veins/muscle lines
    pygame.draw.arc(screen, (120,60,60), (rect.left+20, rect.centery, 18, 8), 0, math.pi, 2)
    pygame.draw.arc(screen, (120,60,60), (rect.right-38, rect.centery, 18, 8), 0, math.pi, 2)
    # Legs (clawed)
    leg_y = rect.bottom-4
    pygame.draw.line(screen, color, (rect.left+14, leg_y), (rect.left+14, leg_y+18), 8)
    pygame.draw.line(screen, color, (rect.right-14, leg_y), (rect.right+14, leg_y+18), 8)
    pygame.draw.line(screen, (80,80,80), (rect.left+14, leg_y+18), (rect.left+8, leg_y+28), 4)
    pygame.draw.line(screen, (80,80,80), (rect.right-14, leg_y+18), (rect.right-8, leg_y+28), 4)
    # Face: angry eyes, jagged mouth, scars
    eye_y = rect.top + rect.height//3
    # Bloodshot/glowing eyes
    pygame.draw.ellipse(screen, (200,0,0), (rect.left+rect.width//4-8, eye_y-8, 16, 12))
    pygame.draw.ellipse(screen, (255,255,0), (rect.left+rect.width//4-2, eye_y-2, 8, 6))
    pygame.draw.ellipse(screen, (200,0,0), (rect.right-rect.width//4-8, eye_y-8, 16, 12))
    pygame.draw.ellipse(screen, (255,255,0), (rect.right-rect.width//4-2, eye_y-2, 8, 6))
    pygame.draw.line(screen, (120,0,0), (rect.left+rect.width//4-8, eye_y-8), (rect.left+rect.width//4+8, eye_y-12), 3)
    pygame.draw.line(screen, (120,0,0), (rect.right-rect.width//4-8, eye_y-12), (rect.right-rect.width//4+8, eye_y-8), 3)
    # Slitted pupils
    pygame.draw.line(screen, (0,0,0), (rect.left+rect.width//4+2, eye_y), (rect.left+rect.width//4+2, eye_y+6), 2)
    pygame.draw.line(screen, (0,0,0), (rect.right-rect.width//4+2, eye_y), (rect.right-rect.width//4+2, eye_y+6), 2)
    # Scars
    pygame.draw.line(screen, (120,60,60), (rect.centerx-10, rect.centery-8), (rect.centerx+10, rect.centery-2), 2)
    pygame.draw.line(screen, (120,60,60), (rect.centerx-8, rect.centery+8), (rect.centerx+12, rect.centery+12), 2)
    # Mouth: jagged, sharp teeth, drool/blood
    mouth_rect = pygame.Rect(rect.centerx-18, rect.bottom-28, 36, 16)
    pygame.draw.arc(screen, (120,0,0), mouth_rect, 3.14, 2*3.14, 5)
    for i in range(6):
        tooth_x = mouth_rect.left+4+i*6
        pygame.draw.polygon(screen, (255,255,255), [(tooth_x, mouth_rect.bottom-2), (tooth_x+4, mouth_rect.bottom-2), (tooth_x+2, mouth_rect.bottom+6)])
    # Drool
    pygame.draw.arc(screen, (100,200,255), (mouth_rect.left+10, mouth_rect.bottom-2, 8, 8), 0, math.pi, 2)
    # Blood
    pygame.draw.arc(screen, (200,0,0), (mouth_rect.right-18, mouth_rect.bottom-2, 8, 8), 0, math.pi, 2)
    # Health above head
    hp_text = font.render(f"HP: {hp}", True, (255,255,0))
    screen.blit(hp_text, (rect.centerx-hp_text.get_width()//2, rect.top-24))
    # Return all body part polygons/rects for collision
    return {
        'body': body_points,
        'left_arm': left_arm_rect,
        'right_arm': right_arm_rect,
        'left_leg': left_leg_rect,
        'right_leg': right_leg_rect,
        'head': head_rect
    }

def run_survival_mode(num_players, player1_name, player2_name, player3_name, char_choices, upgrades1, upgrades2):
    # Survival mode supporting 1, 2, or 3 players
    level = 1
    score = 0
    speed = 8
    monsters = []
    monster_speed = 1
    monster_size = 40
    bullets = []
    font_big = pygame.font.SysFont(None, 72)
    barrier = {'rect': pygame.Rect(60, HEIGHT-200, WIDTH-120, 24), 'hp': 50}
    
    # Initialize player positions based on player count
    players = []
    if num_players == 1:
        players.append(pygame.Rect(WIDTH//2, HEIGHT-120, 50, 50))
    elif num_players == 2:
        players.append(pygame.Rect(WIDTH//3, HEIGHT-120, 50, 50))
        players.append(pygame.Rect(2*WIDTH//3, HEIGHT-120, 50, 50))
    elif num_players == 3:
        players.append(pygame.Rect(WIDTH//4, HEIGHT-120, 50, 50))
        players.append(pygame.Rect(WIDTH//2, HEIGHT-120, 50, 50))
        players.append(pygame.Rect(3*WIDTH//4, HEIGHT-120, 50, 50))
    
    running = True
    start_countdown()
    while running:
        # Spawn fewer monsters per level, slower scaling
        if not monsters:
            for _ in range(2 + level//2):  # 2 + level//2 monsters per wave (slower increase)
                x = random.randint(60, WIDTH-60)
                y = random.randint(-300, -40)
                
                # Choose monster type based on level and randomness
                monster_types = ['zombie', 'demon', 'spider', 'ghost']
                if level < 3:
                    # Early levels: mostly zombies and spiders
                    monster_type = random.choice(['zombie', 'zombie', 'spider'])
                elif level < 6:
                    # Mid levels: add demons
                    monster_type = random.choice(['zombie', 'spider', 'demon'])
                else:
                    # Higher levels: all types including ghosts
                    monster_type = random.choice(monster_types)
                
                # Different monster types have different stats
                if monster_type == 'zombie':
                    hp = 2 + level//4
                    size = monster_size
                    speed_mult = 1.0
                elif monster_type == 'demon':
                    hp = 3 + level//3  # Tougher
                    size = int(monster_size * 1.2)  # Bigger
                    speed_mult = 1.3  # Faster
                elif monster_type == 'spider':
                    hp = 1 + level//5  # Weaker but fast
                    size = int(monster_size * 0.8)  # Smaller
                    speed_mult = 1.5  # Much faster
                elif monster_type == 'ghost':
                    hp = 1 + level//6  # Very weak but hard to hit
                    size = monster_size
                    speed_mult = 0.8  # Slower but phases
                
                monsters.append({
                    'rect': pygame.Rect(x, y, size, size), 
                    'hp': hp, 
                    'max_hp': hp,
                    'type': monster_type,
                    'speed_mult': speed_mult,
                    'damage_flash': 0  # For damage visual effects
                })
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Player 1 shoot (space)
                if event.key == pygame.K_SPACE and len(players) >= 1:
                    bullets.append({'rect': pygame.Rect(players[0].centerx-5, players[0].top-10, 10, 20), 'dir': -1, 'owner': 1})
                # Player 2 shoot (right shift)
                if event.key == pygame.K_RSHIFT and len(players) >= 2:
                    bullets.append({'rect': pygame.Rect(players[1].centerx-5, players[1].top-10, 10, 20), 'dir': -1, 'owner': 2})
                # Player 3 shoot (enter)
                if event.key == pygame.K_RETURN and len(players) >= 3:
                    bullets.append({'rect': pygame.Rect(players[2].centerx-5, players[2].top-10, 10, 20), 'dir': -1, 'owner': 3})
        
        keys = pygame.key.get_pressed()
        
        # Player 1 controls (WASD)
        if len(players) >= 1:
            if keys[pygame.K_a]: players[0].x -= speed
            if keys[pygame.K_d]: players[0].x += speed
            players[0].clamp_ip(pygame.Rect(0,0,WIDTH,HEIGHT))
        
        # Player 2 controls (Arrow keys)
        if len(players) >= 2:
            if keys[pygame.K_LEFT]: players[1].x -= speed
            if keys[pygame.K_RIGHT]: players[1].x += speed
            players[1].clamp_ip(pygame.Rect(0,0,WIDTH,HEIGHT))
        
        # Player 3 controls (IJKL)
        if len(players) >= 3:
            if keys[pygame.K_j]: players[2].x -= speed
            if keys[pygame.K_l]: players[2].x += speed
            players[2].clamp_ip(pygame.Rect(0,0,WIDTH,HEIGHT))
        
        # Move monsters with different behaviors
        for m in monsters:
            base_speed = monster_speed + level//6
            actual_speed = base_speed * m['speed_mult']
            
            if m['type'] == 'zombie':
                # Zombies move straight down, simple and relentless
                m['rect'].y += actual_speed
            elif m['type'] == 'demon':
                # Demons move toward the nearest player
                nearest_player = min(players, key=lambda p: abs(p.centerx - m['rect'].centerx))
                if m['rect'].centerx < nearest_player.centerx:
                    m['rect'].x += actual_speed * 0.5
                elif m['rect'].centerx > nearest_player.centerx:
                    m['rect'].x -= actual_speed * 0.5
                m['rect'].y += actual_speed
            elif m['type'] == 'spider':
                # Spiders move in zigzag pattern
                m['rect'].y += actual_speed
                m['rect'].x += int(10 * math.sin(m['rect'].y * 0.1))  # Zigzag movement
            elif m['type'] == 'ghost':
                # Ghosts phase through some attacks and move erratically
                m['rect'].y += actual_speed
                if random.random() < 0.1:  # 10% chance to phase sideways
                    m['rect'].x += random.randint(-30, 30)
            
            # Reduce damage flash timer
            if m['damage_flash'] > 0:
                m['damage_flash'] -= 1
        
        # Move bullets
        for bullet in bullets[:]:
            bullet['rect'].y += bullet['dir'] * 16
            if bullet['rect'].bottom < 0:
                bullets.remove(bullet)
        
        # Bullet-monster collision
        for bullet in bullets[:]:
            hit = False
            for m in monsters[:]:
                # Simple rectangular collision detection (faster than complex body parts)
                if bullet['rect'].colliderect(m['rect']):
                    # Special ghost behavior - 30% chance to phase through bullets
                    if m['type'] == 'ghost' and random.random() < 0.3:
                        continue  # Bullet phases through ghost
                    
                    m['hp'] -= 1
                    m['damage_flash'] = 5  # Flash red for 5 frames
                    
                    if m['hp'] <= 0:
                        monsters.remove(m)
                        # Different score values for different monsters
                        if m['type'] == 'zombie':
                            score += 1
                        elif m['type'] == 'demon':
                            score += 3  # Tougher monsters give more points
                        elif m['type'] == 'spider':
                            score += 2  # Fast monsters give good points
                        elif m['type'] == 'ghost':
                            score += 5  # Hardest to hit, most points
                    
                    hit = True
                    break
            if hit and bullet in bullets:
                bullets.remove(bullet)
        
        # Monster-barrier collision
        for m in monsters[:]:
            if m['rect'].colliderect(barrier['rect']):
                barrier['hp'] -= 1
                monsters.remove(m)
        
        # Monster-base collision
        for m in monsters[:]:
            if m['rect'].bottom >= HEIGHT-10:
                barrier['hp'] -= 1
                monsters.remove(m)
        
        if barrier['hp'] <= 0:
            running = False
        
        # Draw everything
        screen.fill((15,15,25))  # Even darker, more ominous background
        
        # Add creepy atmospheric effects
        # Flickering fog effect
        if random.random() < 0.3:
            fog_alpha = random.randint(20, 50)
            fog_surface = pygame.Surface((WIDTH, HEIGHT))
            fog_surface.set_alpha(fog_alpha)
            fog_surface.fill((40, 40, 60))
            screen.blit(fog_surface, (0, 0))
        
        # Random lightning flashes
        if random.random() < 0.02:  # 2% chance per frame
            lightning_surface = pygame.Surface((WIDTH, HEIGHT))
            lightning_surface.set_alpha(100)
            lightning_surface.fill((200, 200, 255))
            screen.blit(lightning_surface, (0, 0))
        
        # Draw all players based on number of players
        for i, player in enumerate(players):
            if i < len(char_choices):
                draw_survivor_character(screen, player.centerx, player.centery, char_choices[i])
        
        pygame.draw.rect(screen, (100,100,255), barrier['rect'])
        barrier_hp = font.render(f"Barrier HP: {barrier['hp']}", True, (255,255,255))
        screen.blit(barrier_hp, (barrier['rect'].centerx-barrier_hp.get_width()//2, barrier['rect'].top-30))
        
        for m in monsters:
            # Draw realistic creepy monsters with damage flash effects
            damage_flash = m['damage_flash'] > 0
            draw_monster_by_type(screen, m, damage_flash)
        
        for bullet in bullets:
            pygame.draw.rect(screen, (255,255,0), bullet['rect'])
        
        score_text = font.render(f"Score: {score}", True, (255,255,255))
        screen.blit(score_text, (40, 20))
        level_text = font.render(f"Level: {level}", True, (0,255,0))
        screen.blit(level_text, (WIDTH-200, 20))
        
        # Show player names and controls
        if num_players >= 1:
            p1_text = font.render(f"{player1_name}: WASD + Space", True, (255,255,255))
            screen.blit(p1_text, (20, HEIGHT-40))
        if num_players >= 2:
            p2_text = font.render(f"{player2_name}: Arrows + RShift", True, (255,255,255))
            screen.blit(p2_text, (20, HEIGHT-60))
        if num_players >= 3:
            p3_text = font.render(f"{player3_name}: IJKL + Enter", True, (255,255,255))
            screen.blit(p3_text, (20, HEIGHT-80))
        
        if not monsters:
            # Level up
            level += 1
            monster_speed += 0.5  # slower speed increase per level
            monster_size = max(30, monster_size-1)  # slower size reduction
            pygame.time.wait(1000)
        
        if not running:
            # Game over screen with back to menu button
            while True:
                screen.fill((20,20,30))
                gameover_text = font_big.render("Game Over!", True, (255,0,0))
                screen.blit(gameover_text, (WIDTH//2-gameover_text.get_width()//2, HEIGHT//2-60))
                
                final_score_text = lobby_font.render(f"Final Score: {score}", True, (255,255,255))
                screen.blit(final_score_text, (WIDTH//2-final_score_text.get_width()//2, HEIGHT//2-10))
                
                final_level_text = lobby_font.render(f"Reached Level: {level}", True, (0,255,0))
                screen.blit(final_level_text, (WIDTH//2-final_level_text.get_width()//2, HEIGHT//2+20))
                
                back_rect = pygame.Rect(WIDTH//2-80, HEIGHT//2+60, 160, 40)
                pygame.draw.rect(screen, (100,100,100), back_rect)
                back_text = font.render("Back to Menu", True, (255,255,255))
                screen.blit(back_text, (back_rect.centerx-back_text.get_width()//2, back_rect.centery-back_text.get_height()//2))
                
                pygame.display.flip()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if back_rect.collidepoint(event.pos):
                            pygame.mixer.music.stop()
                            return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            pygame.mixer.music.stop()
                            return
        
        pygame.display.flip()
        clock.tick(60)

# Makka Pakka Mode Functions
def draw_makka_pakka(screen, x, y, color):
    """Draw a VERY realistic Makka Pakka character from In the Night Garden"""
    # Makka Pakka's signature stone/beige body color
    makka_pakka_beige = (235, 220, 195)
    makka_pakka_darker = (215, 200, 175)
    makka_pakka_shadow = (195, 180, 155)
    
    # MUCH ROUNDER body - Makka Pakka is very round and squat!
    # Main body (almost perfectly round)
    pygame.draw.circle(screen, makka_pakka_shadow, (x, y-5), 26)  # Shadow base
    pygame.draw.circle(screen, makka_pakka_beige, (x, y-8), 25)
    pygame.draw.circle(screen, makka_pakka_darker, (x, y-8), 23)  # Inner shading
    pygame.draw.circle(screen, (225, 210, 185), (x-5, y-12), 18)  # Highlight (top-left)
    
    # Textured belly pattern (circular dots - Makka Pakka's signature!)
    pygame.draw.circle(screen, (215, 200, 175), (x, y-3), 16)
    for i in range(3):
        for j in range(3):
            if i == 1 and j == 1:  # Center
                continue
            cx = x - 8 + i * 8
            cy = y - 10 + j * 8
            pygame.draw.circle(screen, (205, 190, 165), (cx, cy), 3)
            pygame.draw.circle(screen, (195, 180, 155), (cx, cy), 2)
            pygame.draw.circle(screen, (225, 210, 185), (cx-1, cy-1), 1)  # Shine
    
    # DISTINCTIVE ROUND HEAD - much bigger and rounder than before!
    pygame.draw.circle(screen, makka_pakka_shadow, (x, y-33), 22)  # Head shadow
    pygame.draw.circle(screen, makka_pakka_beige, (x, y-35), 20)
    pygame.draw.circle(screen, makka_pakka_darker, (x, y-35), 18)  # Shading
    pygame.draw.circle(screen, (225, 210, 185), (x-4, y-38), 14)  # Highlight
    
    # Makka Pakka's VERY DISTINCTIVE small round ears
    # Left ear
    pygame.draw.circle(screen, makka_pakka_beige, (x-18, y-36), 5)
    pygame.draw.circle(screen, (205, 190, 165), (x-18, y-36), 3)
    # Right ear
    pygame.draw.circle(screen, makka_pakka_beige, (x+18, y-36), 5)
    pygame.draw.circle(screen, (205, 190, 165), (x+18, y-36), 3)
    
    # Makka Pakka's HUGE adorable eyes - his most recognizable feature!
    # Much BIGGER eyes (he has very large eyes for his face)
    # Left eye
    pygame.draw.circle(screen, (255, 255, 255), (x-8, y-37), 8)
    pygame.draw.circle(screen, (240, 240, 240), (x-8, y-37), 7)
    pygame.draw.circle(screen, (60, 50, 40), (x-7, y-36), 5)  # Large dark pupil
    pygame.draw.circle(screen, (30, 25, 20), (x-7, y-36), 4)
    pygame.draw.circle(screen, (255, 255, 255), (x-5, y-38), 2)  # Big shine
    # Right eye
    pygame.draw.circle(screen, (255, 255, 255), (x+8, y-37), 8)
    pygame.draw.circle(screen, (240, 240, 240), (x+8, y-37), 7)
    pygame.draw.circle(screen, (60, 50, 40), (x+9, y-36), 5)  # Large dark pupil
    pygame.draw.circle(screen, (30, 25, 20), (x+9, y-36), 4)
    pygame.draw.circle(screen, (255, 255, 255), (x+11, y-38), 2)  # Big shine
    
    # Small distinctive button nose (very small compared to eyes!)
    pygame.draw.circle(screen, (190, 160, 135), (x, y-29), 3)
    pygame.draw.circle(screen, (170, 140, 115), (x, y-29), 2)
    pygame.draw.circle(screen, (210, 180, 155), (x-1, y-30), 1)  # Nose shine
    
    # Makka Pakka's characteristic WIDE smile (always happy!)
    pygame.draw.arc(screen, (120, 100, 80), (x-9, y-27, 18, 12), 3.14, 6.28, 3)
    # Smile highlight
    pygame.draw.arc(screen, (100, 80, 60), (x-8, y-26, 16, 10), 3.14, 6.28, 2)
    
    # VERY rosy cheeks (Makka Pakka has prominent rosy cheeks!)
    pygame.draw.circle(screen, (255, 180, 160), (x-14, y-30), 5)
    pygame.draw.circle(screen, (255, 200, 180), (x-14, y-30), 4)
    pygame.draw.circle(screen, (255, 180, 160), (x+14, y-30), 5)
    pygame.draw.circle(screen, (255, 200, 180), (x+14, y-30), 4)
    
    # Makka Pakka's ICONIC bobble hat with long antenna!
    hat_color = color if color != (255, 255, 255) else (200, 150, 100)
    hat_light = tuple(min(255, c+40) for c in hat_color)
    hat_dark = tuple(max(0, c-20) for c in hat_color)
    
    # Striped hat rim (Makka Pakka's hat has texture)
    pygame.draw.ellipse(screen, hat_dark, (x-16, y-52, 32, 10))
    pygame.draw.ellipse(screen, hat_color, (x-15, y-51, 30, 8))
    pygame.draw.ellipse(screen, hat_light, (x-14, y-50, 28, 6))
    # Stripe details
    for i in range(4):
        pygame.draw.line(screen, hat_dark, (x-12+i*6, y-49), (x-10+i*6, y-49), 2)
    
    # Hat dome (rounder)
    pygame.draw.circle(screen, hat_color, (x, y-57), 11)
    pygame.draw.circle(screen, hat_light, (x-2, y-59), 8)
    pygame.draw.circle(screen, hat_dark, (x+3, y-55), 6)
    
    # LONG antenna with bobble (very distinctive!)
    pygame.draw.line(screen, (120, 100, 80), (x, y-57), (x, y-72), 3)
    pygame.draw.line(screen, (140, 120, 100), (x-1, y-57), (x-1, y-72), 1)  # Highlight
    # Bobble on top (color-coded for player)
    pygame.draw.circle(screen, hat_dark, (x, y-75), 7)
    pygame.draw.circle(screen, hat_color, (x, y-76), 6)
    pygame.draw.circle(screen, hat_light, (x-2, y-77), 4)
    pygame.draw.circle(screen, (255, 255, 255), (x-2, y-78), 2)  # Shine
    
    # SHORT STUBBY arms (Makka Pakka has very short arms!)
    arm_color = makka_pakka_beige
    # Left arm
    pygame.draw.ellipse(screen, makka_pakka_shadow, (x-30, y-6, 14, 18))
    pygame.draw.ellipse(screen, arm_color, (x-29, y-7, 12, 16))
    pygame.draw.ellipse(screen, makka_pakka_darker, (x-28, y-6, 10, 14))
    # Right arm  
    pygame.draw.ellipse(screen, makka_pakka_shadow, (x+16, y-6, 14, 18))
    pygame.draw.ellipse(screen, arm_color, (x+17, y-7, 12, 16))
    pygame.draw.ellipse(screen, makka_pakka_darker, (x+18, y-6, 10, 14))
    
    # Round mittened hands
    pygame.draw.circle(screen, makka_pakka_shadow, (x-29, y+10), 7)
    pygame.draw.circle(screen, arm_color, (x-29, y+9), 6)
    pygame.draw.circle(screen, makka_pakka_darker, (x-29, y+9), 5)
    pygame.draw.circle(screen, makka_pakka_shadow, (x+29, y+10), 7)
    pygame.draw.circle(screen, arm_color, (x+29, y+9), 6)
    pygame.draw.circle(screen, makka_pakka_darker, (x+29, y+9), 5)
    
    # Makka Pakka's ICONIC SPONGE (bright yellow with holes!)
    sponge_yellow = (255, 245, 120)
    sponge_dark = (235, 225, 100)
    pygame.draw.rect(screen, sponge_dark, (x-41, y+3, 13, 13), border_radius=2)
    pygame.draw.rect(screen, sponge_yellow, (x-40, y+4, 11, 11), border_radius=2)
    # Sponge holes (very characteristic!)
    for sx in range(3):
        for sy in range(3):
            hole_x = x-38 + sx*4
            hole_y = y+6 + sy*4
            pygame.draw.circle(screen, (210, 200, 80), (hole_x, hole_y), 1)
    # Sponge shine
    pygame.draw.rect(screen, (255, 255, 220), (x-39, y+5, 4, 2))
    
    # OG-POG (stone bag) - Makka Pakka ALWAYS carries his Og-Pog!
    bag_brown = (160, 130, 100)
    bag_light = (180, 150, 120)
    pygame.draw.ellipse(screen, (140, 110, 80), (x+20, y+6, 16, 20))
    pygame.draw.ellipse(screen, bag_brown, (x+21, y+7, 14, 18))
    pygame.draw.ellipse(screen, bag_light, (x+22, y+8, 12, 16))
    # Bag opening
    pygame.draw.ellipse(screen, (100, 80, 60), (x+23, y+8, 10, 5))
    # Strap across body
    pygame.draw.arc(screen, (140, 110, 80), (x+8, y-10, 24, 24), 0, 3.14, 3)
    # Stones peeking out (gray stones!)
    pygame.draw.circle(screen, (140, 140, 135), (x+25, y+9), 3)
    pygame.draw.circle(screen, (120, 120, 115), (x+29, y+10), 2)
    pygame.draw.circle(screen, (160, 160, 155), (x+27, y+11), 2)
    
    # SHORT LEGS (Makka Pakka has very short stubby legs!)
    pygame.draw.ellipse(screen, makka_pakka_shadow, (x-11, y+20, 10, 16))
    pygame.draw.ellipse(screen, makka_pakka_beige, (x-10, y+19, 8, 14))
    pygame.draw.ellipse(screen, makka_pakka_shadow, (x+1, y+20, 10, 16))
    pygame.draw.ellipse(screen, makka_pakka_beige, (x+2, y+19, 8, 14))
    
    # Round feet
    pygame.draw.ellipse(screen, makka_pakka_shadow, (x-13, y+32, 12, 8))
    pygame.draw.ellipse(screen, makka_pakka_darker, (x-12, y+31, 10, 6))
    pygame.draw.ellipse(screen, makka_pakka_shadow, (x+1, y+32, 12, 8))
    pygame.draw.ellipse(screen, makka_pakka_darker, (x+2, y+31, 10, 6))
    pygame.draw.circle(screen, (150, 150, 150), (x+24, y+8), 3)
    pygame.draw.circle(screen, (130, 130, 130), (x+26, y+12), 2)
    
    # Short stumpy legs
    leg_color = makka_pakka_beige
    pygame.draw.ellipse(screen, leg_color, (x-12, y+22, 10, 16))
    pygame.draw.ellipse(screen, leg_color, (x+2, y+22, 10, 16))
    pygame.draw.ellipse(screen, makka_pakka_darker, (x-11, y+23, 8, 14))
    pygame.draw.ellipse(screen, makka_pakka_darker, (x+3, y+23, 8, 14))
    
    # Little brown shoes/feet
    pygame.draw.ellipse(screen, (139, 90, 60), (x-14, y+34, 12, 8))
    pygame.draw.ellipse(screen, (139, 90, 60), (x+2, y+34, 12, 8))
    pygame.draw.ellipse(screen, (160, 110, 80), (x-13, y+35, 10, 6))
    pygame.draw.ellipse(screen, (160, 110, 80), (x+3, y+35, 10, 6))

def run_makka_pakka_mode(player1_name, player2_name):
    """Makka Pakka Mode: Players run around washing faces to score points!"""
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(resource_path('fart.mp3'))
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Error playing Makka Pakka music: {e}")
    
    # Initialize players
    player1 = pygame.Rect(WIDTH//4, HEIGHT//2, 50, 50)
    player2 = pygame.Rect(3*WIDTH//4, HEIGHT//2, 50, 50)
    
    # Game state
    player1_score = 0
    player2_score = 0
    speed = 7
    game_duration = 90
    end_time = time.time() + game_duration
    
    # Create dirty faces
    faces = []
    for _ in range(15):
        face = {
            'rect': pygame.Rect(random.randint(60, WIDTH-60), random.randint(60, HEIGHT-60), 40, 40),
            'dirty': True,
            'washer': None,
            'wash_progress': 0  # Track washing progress (0-10)
            }
        faces.append(face)
    
    # Track button press states to detect new presses
    p1_shoot_pressed = False
    p2_shoot_pressed = False
    
    running = True
    
    while running:
        now = time.time()
        time_left = max(0, end_time - now)
        
        if time_left <= 0:
            break
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'lobby'
            if event.type == pygame.MOUSEBUTTONDOWN:
                back_rect = pygame.Rect(10, 10, 100, 40)
                if back_rect.collidepoint(event.pos):
                    return 'lobby'
        
        # Player controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player1.y > 60:
            player1.y -= speed
        if keys[pygame.K_s] and player1.y < HEIGHT - 60:
            player1.y += speed
        if keys[pygame.K_a] and player1.x > 10:
            player1.x -= speed
        if keys[pygame.K_d] and player1.x < WIDTH - 60:
            player1.x += speed
        
        if keys[pygame.K_UP] and player2.y > 60:
            player2.y -= speed
        if keys[pygame.K_DOWN] and player2.y < HEIGHT - 60:
            player2.y += speed
        if keys[pygame.K_LEFT] and player2.x > 10:
            player2.x -= speed
        if keys[pygame.K_RIGHT] and player2.x < WIDTH - 60:
            player2.x += speed
        
        # Check shooting buttons (Space for P1, Right Shift for P2)
        p1_shoot_now = keys[pygame.K_SPACE]
        p2_shoot_now = keys[pygame.K_RSHIFT]
        
        # Detect new button presses
        p1_new_press = p1_shoot_now and not p1_shoot_pressed
        p2_new_press = p2_shoot_now and not p2_shoot_pressed
        
        p1_shoot_pressed = p1_shoot_now
        p2_shoot_pressed = p2_shoot_now
        
        # Check washing - need to press button while near face
        # Can wash dirty faces OR steal other player's faces!
        for face in faces:
            # Player 1 washing/stealing
            if player1.colliderect(face['rect']):
                if p1_new_press:
                    # If it's dirty or belongs to player 2, start washing
                    if face['dirty'] or face['washer'] == 2:
                        face['wash_progress'] += 1
                        if face['wash_progress'] >= 10:
                            # If stealing from player 2, decrease their score
                            if face['washer'] == 2:
                                player2_score = max(0, player2_score - 1)
                            # Claim the face for player 1
                            face['dirty'] = False
                            face['washer'] = 1
                            face['wash_progress'] = 0
                            player1_score += 1
            # Player 2 washing/stealing
            elif player2.colliderect(face['rect']):
                if p2_new_press:
                    # If it's dirty or belongs to player 1, start washing
                    if face['dirty'] or face['washer'] == 1:
                        face['wash_progress'] += 1
                        if face['wash_progress'] >= 10:
                            # If stealing from player 1, decrease their score
                            if face['washer'] == 1:
                                player1_score = max(0, player1_score - 1)
                            # Claim the face for player 2
                            face['dirty'] = False
                            face['washer'] = 2
                            face['wash_progress'] = 0
                            player2_score += 1
            else:
                # Reset progress if no one is near (so you can't resume later)
                if face['wash_progress'] > 0 and face['wash_progress'] < 10:
                    face['wash_progress'] = 0
        
        # Draw
        screen.fill((173, 216, 230))
        
        # Draw grass
        for i in range(0, WIDTH, 20):
            for j in range(0, HEIGHT, 20):
                grass_shade = (34 + random.randint(-10, 10), 139 + random.randint(-20, 20), 34 + random.randint(-10, 10))
                pygame.draw.circle(screen, grass_shade, (i, j), 3)
        
        # Draw faces
        for face in faces:
            if face['dirty']:
                # Dirty unwashed face - GREEN!
                pygame.draw.ellipse(screen, (50, 200, 50), face['rect'])
                pygame.draw.ellipse(screen, (30, 150, 30), (face['rect'].x+5, face['rect'].y+5, 30, 30))
                pygame.draw.circle(screen, (0, 0, 0), (face['rect'].x+12, face['rect'].y+15), 3)
                pygame.draw.circle(screen, (0, 0, 0), (face['rect'].x+28, face['rect'].y+15), 3)
                pygame.draw.arc(screen, (0, 0, 0), (face['rect'].x+10, face['rect'].y+25, 20, 10), 0, 3.14, 2)
                
                # Draw washing progress bar if being washed
                if face['wash_progress'] > 0:
                    bar_width = 40
                    bar_height = 6
                    bar_x = face['rect'].x
                    bar_y = face['rect'].y - 10
                    # Background bar (gray)
                    pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
                    # Progress bar (blue)
                    progress_width = int((face['wash_progress'] / 10) * bar_width)
                    pygame.draw.rect(screen, (0, 200, 255), (bar_x, bar_y, progress_width, bar_height))
                    # Border
                    pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)
            else:
                # Clean washed face - color matches the player who owns it!
                if face['washer'] == 1:
                    # Player 1's face - RED
                    face_color = (255, 100, 100)
                    face_shade = (200, 50, 50)
                elif face['washer'] == 2:
                    # Player 2's face - BLUE
                    face_color = (100, 100, 255)
                    face_shade = (50, 50, 200)
                else:
                    # Default (shouldn't happen)
                    face_color = (255, 220, 177)
                    face_shade = (255, 182, 193)
                
                pygame.draw.ellipse(screen, face_color, face['rect'])
                pygame.draw.ellipse(screen, face_shade, (face['rect'].x+5, face['rect'].y+5, 30, 30))
                pygame.draw.circle(screen, (0, 0, 0), (face['rect'].x+12, face['rect'].y+15), 3)
                pygame.draw.circle(screen, (0, 0, 0), (face['rect'].x+28, face['rect'].y+15), 3)
                pygame.draw.arc(screen, (0, 0, 0), (face['rect'].x+10, face['rect'].y+20, 20, 10), 3.14, 6.28, 2)
                
                # Sparkles
                for _ in range(3):
                    sx = face['rect'].x + random.randint(-5, 45)
                    sy = face['rect'].y + random.randint(-5, 45)
                    pygame.draw.circle(screen, (255, 255, 255), (sx, sy), 2)
                
                # Show progress bar if being stolen
                if face['wash_progress'] > 0:
                    bar_width = 40
                    bar_height = 6
                    bar_x = face['rect'].x
                    bar_y = face['rect'].y - 10
                    # Background bar (gray)
                    pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
                    # Progress bar - show color of player stealing it
                    progress_width = int((face['wash_progress'] / 10) * bar_width)
                    steal_color = (255, 0, 0) if face['washer'] == 2 else (0, 0, 255)  # Opposite player's color
                    pygame.draw.rect(screen, steal_color, (bar_x, bar_y, progress_width, bar_height))
                    # Border
                    pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Draw characters
        draw_makka_pakka(screen, player1.x+25, player1.y+25, (255, 0, 0))
        draw_makka_pakka(screen, player2.x+25, player2.y+25, (0, 0, 255))
        
        # Draw name tags above their heads (above the antenna bobble)
        p1_text = name_font.render(player1_name, True, (255, 255, 255))
        p2_text = name_font.render(player2_name, True, (255, 255, 255))
        # Draw background for name ags (positioned above the taller antenna)
        p1_bg = pygame.Rect(player1.x+25-p1_text.get_width()//2-4, player1.y-60, p1_text.get_width()+8, p1_text.get_height()+4)
        p2_bg = pygame.Rect(player2.x+25-p2_text.get_width()//2-4, player2.y-60, p2_text.get_width()+8, p2_text.get_height()+4)
        pygame.draw.rect(screen, (255, 0, 0), p1_bg, border_radius=5)
        pygame.draw.rect(screen, (0, 0, 255), p2_bg, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), p1_bg, 2, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), p2_bg, 2, border_radius=5)
        screen.blit(p1_text, (player1.x+25-p1_text.get_width()//2, player1.y-58))
        screen.blit(p2_text, (player2.x+25-p2_text.get_width()//2, player2.y-58))
        
        # Draw UI
        score_text = font.render(f"{player1_name}: {player1_score}  |  {player2_name}: {player2_score}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH//2-score_text.get_width()//2, 60))
        
        timer_text = lobby_font.render(f"Time: {int(time_left)}s", True, (255, 215, 0))
        screen.blit(timer_text, (WIDTH//2-timer_text.get_width()//2, 10))
        
        # Back button
        back_rect = pygame.Rect(10, 10, 100, 40)
        pygame.draw.rect(screen, (100, 100, 100), back_rect)
        back_text = name_font.render("Back (ESC)", True, (255, 255, 255))
        screen.blit(back_text, (back_rect.centerx-back_text.get_width()//2, back_rect.centery-back_text.get_height()//2))
        
        pygame.display.flip()
        clock.tick(60)
    
    # Game over screen
    while True:
        screen.fill((50, 50, 50))
        
        title = lobby_font.render("Game Over!", True, (255, 215, 0))
        screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-150))
        
        if player1_score > player2_score:
            winner_text = lobby_font.render(f"{player1_name} Wins!", True, (0, 255, 0))
        elif player2_score > player1_score:
            winner_text = lobby_font.render(f"{player2_name} Wins!", True, (0, 255, 0))
        else:
            winner_text = lobby_font.render("It's a Tie!", True, (255, 255, 0))
        screen.blit(winner_text, (WIDTH//2-winner_text.get_width()//2, HEIGHT//2-80))
        
        final_score = font.render(f"{player1_name}: {player1_score} faces  |  {player2_name}: {player2_score} faces", True, (255, 255, 255))
        screen.blit(final_score, (WIDTH//2-final_score.get_width()//2, HEIGHT//2-20))
        
        back_button = pygame.Rect(WIDTH//2-100, HEIGHT//2+40, 200, 60)
        pygame.draw.rect(screen, (0, 150, 0), back_button)
        back_text = font.render("Back to Menu", True, (255, 255, 255))
        screen.blit(back_text, (back_button.centerx-back_text.get_width()//2, back_button.centery-back_text.get_height()//2))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    return 'lobby'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return 'lobby'

# Capture the Flag Mode
def run_capture_the_flag(player1_name, player2_name):
    """Capture the Flag - steal the opponent's flag and bring it to your base!"""
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(resource_path('fart.mp3'))
        pygame.mixer.music.play(-1)
    except:
        pass
    
    # Players
    player1 = pygame.Rect(50, HEIGHT//2, 50, 50)
    player2 = pygame.Rect(WIDTH-100, HEIGHT//2, 50, 50)
    player1_spawn = pygame.Rect(50, HEIGHT//2, 50, 50)  # Spawn positions
    player2_spawn = pygame.Rect(WIDTH-100, HEIGHT//2, 50, 50)
    speed = 6
    p1_right = True
    p2_right = False
    
    # Bullets
    bullets = []
    player1_shots = 0
    player2_shots = 0
    RELOAD_LIMIT = 3
    player1_reload_time = 0
    player2_reload_time = 0
    RELOAD_DURATION = 2
    
    # Flags (at each player's base)
    flag1_home = pygame.Rect(30, HEIGHT//2 - 20, 30, 40)  # Player 1's flag home
    flag2_home = pygame.Rect(WIDTH-60, HEIGHT//2 - 20, 30, 40)  # Player 2's flag home
    
    flag1_pos = flag1_home.copy()  # Current position of flag 1
    flag2_pos = flag2_home.copy()  # Current position of flag 2
    
    flag1_carrier = None  # Who's carrying flag 1 (None, 'p1', or 'p2')
    flag2_carrier = None  # Who's carrying flag 2
    
    # Scores
    p1_captures = 0
    p2_captures = 0
    winning_score = 3  # First to 3 captures wins
    
    # Obstacles/walls
    walls = [
        pygame.Rect(WIDTH//2 - 20, 100, 40, 200),
        pygame.Rect(WIDTH//2 - 20, HEIGHT - 300, 40, 200),
        pygame.Rect(200, HEIGHT//2 - 20, 100, 40),
        pygame.Rect(WIDTH - 300, HEIGHT//2 - 20, 100, 40),
    ]
    
    while True:
        now = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'lobby'
                # Player 1 shoot (SPACE)
                elif event.key == pygame.K_SPACE:
                    if player1_shots < RELOAD_LIMIT and now > player1_reload_time:
                        bx = player1.right if p1_right else player1.left - 10
                        bullets.append({'rect': pygame.Rect(bx, player1.centery-5, 10, 10), 'dir': 1 if p1_right else -1, 'owner': 1})
                        player1_shots += 1
                        if player1_shots >= RELOAD_LIMIT:
                            player1_reload_time = now + RELOAD_DURATION
                            player1_shots = 0
                # Player 2 shoot (ENTER)
                elif event.key == pygame.K_RETURN:
                    if player2_shots < RELOAD_LIMIT and now > player2_reload_time:
                        bx = player2.right if p2_right else player2.left - 10
                        bullets.append({'rect': pygame.Rect(bx, player2.centery-5, 10, 10), 'dir': 1 if p2_right else -1, 'owner': 2})
                        player2_shots += 1
                        if player2_shots >= RELOAD_LIMIT:
                            player2_reload_time = now + RELOAD_DURATION
                            player2_shots = 0
        
        # Player 1 controls (WASD)
        keys = pygame.key.get_pressed()
        old_p1 = player1.copy()
        if keys[pygame.K_w]:
            player1.y -= speed
        if keys[pygame.K_s]:
            player1.y += speed
        if keys[pygame.K_a]:
            player1.x -= speed
            p1_right = False
        if keys[pygame.K_d]:
            player1.x += speed
            p1_right = True
        
        # Player 2 controls (Arrow keys)
        old_p2 = player2.copy()
        if keys[pygame.K_UP]:
            player2.y -= speed
        if keys[pygame.K_DOWN]:
            player2.y += speed
        if keys[pygame.K_LEFT]:
            player2.x -= speed
            p2_right = False
        if keys[pygame.K_RIGHT]:
            player2.x += speed
            p2_right = True
        
        # Keep players in bounds
        player1.x = max(0, min(WIDTH-50, player1.x))
        player1.y = max(0, min(HEIGHT-50, player1.y))
        player2.x = max(0, min(WIDTH-50, player2.x))
        player2.y = max(0, min(HEIGHT-50, player2.y))
        
        # Wall collisions
        for wall in walls:
            if player1.colliderect(wall):
                player1.x, player1.y = old_p1.x, old_p1.y
            if player2.colliderect(wall):
                player2.x, player2.y = old_p2.x, old_p2.y
        
        # Move bullets
        for bullet in bullets[:]:
            bullet['rect'].x += bullet['dir'] * 12
            # Remove if off screen
            if bullet['rect'].right < 0 or bullet['rect'].left > WIDTH:
                bullets.remove(bullet)
            # Collision with players - makes them drop flag and return it to base
            elif bullet['owner'] == 1 and bullet['rect'].colliderect(player2):
                # Player 1 shot Player 2
                if flag1_carrier == 'p2':
                    flag1_carrier = None  # Drop flag 1
                    flag1_pos = flag1_home.copy()  # Return flag to base
                    player2.x, player2.y = player2_spawn.x, player2_spawn.y  # Respawn player 2
                bullets.remove(bullet)
            elif bullet['owner'] == 2 and bullet['rect'].colliderect(player1):
                # Player 2 shot Player 1
                if flag2_carrier == 'p1':
                    flag2_carrier = None  # Drop flag 2
                    flag2_pos = flag2_home.copy()  # Return flag to base
                    player1.x, player1.y = player1_spawn.x, player1_spawn.y  # Respawn player 1
                bullets.remove(bullet)
            # Bullets collide with walls
            else:
                for wall in walls:
                    if bullet['rect'].colliderect(wall):
                        if bullet in bullets:
                            bullets.remove(bullet)
                        break
        
        # Flag pickup logic
        # Player 1 trying to pick up Player 2's flag
        if flag2_carrier is None and player1.colliderect(flag2_pos):
            flag2_carrier = 'p1'
        
        # Player 2 trying to pick up Player 1's flag
        if flag1_carrier is None and player2.colliderect(flag1_pos):
            flag1_carrier = 'p2'
        
        # Update flag positions if being carried
        if flag1_carrier == 'p2':
            flag1_pos.center = player2.center
        elif flag1_carrier is None:
            flag1_pos = flag1_home.copy()
        
        if flag2_carrier == 'p1':
            flag2_pos.center = player1.center
        elif flag2_carrier is None:
            flag2_pos = flag2_home.copy()
        
        # Tagging opponent drops their flag
        if player1.colliderect(player2):
            if flag1_carrier == 'p2':
                flag1_carrier = None  # Drop flag 1
            if flag2_carrier == 'p1':
                flag2_carrier = None  # Drop flag 2
        
        # Capture scoring
        # Player 1 scores if they bring flag 2 to their base
        if flag2_carrier == 'p1' and player1.colliderect(flag1_home):
            p1_captures += 1
            flag2_carrier = None
            flag2_pos = flag2_home.copy()
        
        # Player 2 scores if they bring flag 1 to their base
        if flag1_carrier == 'p2' and player2.colliderect(flag2_home):
            p2_captures += 1
            flag1_carrier = None
            flag1_pos = flag1_home.copy()
        
        # Check for winner
        if p1_captures >= winning_score or p2_captures >= winning_score:
            # Show winner screen
            winner = player1_name if p1_captures >= winning_score else player2_name
            while True:
                screen.fill((30, 30, 50))
                winner_text = lobby_font.render(f"{winner} WINS!", True, (255, 215, 0))
                screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, HEIGHT//2 - 100))
                
                score_text = font.render(f"Final Score: {p1_captures} - {p2_captures}", True, (255, 255, 255))
                screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 30))
                
                back_button = pygame.Rect(WIDTH//2-100, HEIGHT//2+40, 200, 60)
                pygame.draw.rect(screen, (0, 150, 0), back_button)
                back_text = font.render("Back to Menu", True, (255, 255, 255))
                screen.blit(back_text, (back_button.centerx-back_text.get_width()//2, back_button.centery-back_text.get_height()//2))
                
                pygame.display.flip()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                            return 'lobby'
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if back_button.collidepoint(event.pos):
                            return 'lobby'
        
        # Drawing
        screen.fill((40, 80, 40))  # Green grass field
        
        # Draw bases
        pygame.draw.rect(screen, (0, 100, 200), (0, 0, 100, HEIGHT))  # Player 1 base (blue)
        pygame.draw.rect(screen, (200, 0, 0), (WIDTH-100, 0, 100, HEIGHT))  # Player 2 base (red)
        
        # Draw walls
        for wall in walls:
            pygame.draw.rect(screen, (100, 100, 100), wall)
            pygame.draw.rect(screen, (70, 70, 70), wall, 3)
        
        # Draw flags
        # Flag 1 (blue flag for player 1's base)
        pygame.draw.rect(screen, (150, 100, 50), (flag1_pos.x, flag1_pos.y + 20, 5, 20))  # Pole
        pygame.draw.polygon(screen, (0, 100, 255), [
            (flag1_pos.x + 5, flag1_pos.y),
            (flag1_pos.x + 30, flag1_pos.y + 10),
            (flag1_pos.x + 5, flag1_pos.y + 20)
        ])
        
        # Flag 2 (red flag for player 2's base)
        pygame.draw.rect(screen, (150, 100, 50), (flag2_pos.x, flag2_pos.y + 20, 5, 20))  # Pole
        pygame.draw.polygon(screen, (255, 0, 0), [
            (flag2_pos.x + 5, flag2_pos.y),
            (flag2_pos.x + 30, flag2_pos.y + 10),
            (flag2_pos.x + 5, flag2_pos.y + 20)
        ])
        
        # Draw players
        # Player 1 (blue) with realistic gun
        pygame.draw.circle(screen, (0, 150, 255), player1.center, 25)
        pygame.draw.circle(screen, (255, 220, 180), (player1.centerx, player1.centery - 5), 15)
        pygame.draw.circle(screen, (0, 0, 0), (player1.centerx - 5, player1.centery - 8), 3)
        pygame.draw.circle(screen, (0, 0, 0), (player1.centerx + 5, player1.centery - 8), 3)
        pygame.draw.arc(screen, (0, 0, 0), (player1.centerx - 5, player1.centery, 10, 5), 3.14, 0, 2)
        
        # Realistic pistol for Player 1
        gun_length = 35
        gun_height = 12
        if p1_right:
            # Gun body
            gun_body = pygame.Rect(player1.right, player1.centery - gun_height//2, gun_length, gun_height)
            pygame.draw.rect(screen, (40, 40, 40), gun_body)
            pygame.draw.rect(screen, (20, 20, 20), gun_body, 2)
            # Barrel
            barrel = pygame.Rect(player1.right + gun_length, player1.centery - 4, 12, 8)
            pygame.draw.rect(screen, (25, 25, 25), barrel)
            # Trigger guard
            pygame.draw.circle(screen, (40, 40, 40), (player1.right + 8, player1.centery + 8), 5, 2)
            # Grip texture
            for i in range(3):
                pygame.draw.line(screen, (30, 30, 30), (player1.right + 5 + i*3, player1.centery + gun_height//2), 
                               (player1.right + 5 + i*3, player1.centery + gun_height//2 + 6), 1)
        else:
            # Gun body
            gun_body = pygame.Rect(player1.left - gun_length, player1.centery - gun_height//2, gun_length, gun_height)
            pygame.draw.rect(screen, (40, 40, 40), gun_body)
            pygame.draw.rect(screen, (20, 20, 20), gun_body, 2)
            # Barrel
            barrel = pygame.Rect(player1.left - gun_length - 12, player1.centery - 4, 12, 8)
            pygame.draw.rect(screen, (25, 25, 25), barrel)
            # Trigger guard
            pygame.draw.circle(screen, (40, 40, 40), (player1.left - 8, player1.centery + 8), 5, 2)
            # Grip texture
            for i in range(3):
                pygame.draw.line(screen, (30, 30, 30), (player1.left - 5 - i*3, player1.centery + gun_height//2), 
                               (player1.left - 5 - i*3, player1.centery + gun_height//2 + 6), 1)
        
        # Player 2 (red) with realistic gun
        pygame.draw.circle(screen, (255, 50, 50), player2.center, 25)
        pygame.draw.circle(screen, (255, 220, 180), (player2.centerx, player2.centery - 5), 15)
        pygame.draw.circle(screen, (0, 0, 0), (player2.centerx - 5, player2.centery - 8), 3)
        pygame.draw.circle(screen, (0, 0, 0), (player2.centerx + 5, player2.centery - 8), 3)
        pygame.draw.arc(screen, (0, 0, 0), (player2.centerx - 5, player2.centery, 10, 5), 3.14, 0, 2)
        
        # Realistic pistol for Player 2
        if p2_right:
            # Gun body
            gun_body2 = pygame.Rect(player2.right, player2.centery - gun_height//2, gun_length, gun_height)
            pygame.draw.rect(screen, (40, 40, 40), gun_body2)
            pygame.draw.rect(screen, (20, 20, 20), gun_body2, 2)
            # Barrel
            barrel2 = pygame.Rect(player2.right + gun_length, player2.centery - 4, 12, 8)
            pygame.draw.rect(screen, (25, 25, 25), barrel2)
            # Trigger guard
            pygame.draw.circle(screen, (40, 40, 40), (player2.right + 8, player2.centery + 8), 5, 2)
            # Grip texture
            for i in range(3):
                pygame.draw.line(screen, (30, 30, 30), (player2.right + 5 + i*3, player2.centery + gun_height//2), 
                               (player2.right + 5 + i*3, player2.centery + gun_height//2 + 6), 1)
        else:
            # Gun body
            gun_body2 = pygame.Rect(player2.left - gun_length, player2.centery - gun_height//2, gun_length, gun_height)
            pygame.draw.rect(screen, (40, 40, 40), gun_body2)
            pygame.draw.rect(screen, (20, 20, 20), gun_body2, 2)
            # Barrel
            barrel2 = pygame.Rect(player2.left - gun_length - 12, player2.centery - 4, 12, 8)
            pygame.draw.rect(screen, (25, 25, 25), barrel2)
            # Trigger guard
            pygame.draw.circle(screen, (40, 40, 40), (player2.left - 8, player2.centery + 8), 5, 2)
            # Grip texture
            for i in range(3):
                pygame.draw.line(screen, (30, 30, 30), (player2.left - 5 - i*3, player2.centery + gun_height//2), 
                               (player2.left - 5 - i*3, player2.centery + gun_height//2 + 6), 1)
        
        # Draw player names
        name1 = name_font.render(player1_name, True, (255, 255, 255))
        screen.blit(name1, (player1.centerx - name1.get_width()//2, player1.y - 30))
        
        name2 = name_font.render(player2_name, True, (255, 255, 255))
        screen.blit(name2, (player2.centerx - name2.get_width()//2, player2.y - 30))
        
        # Draw bullets
        for bullet in bullets:
            pygame.draw.rect(screen, (255, 255, 0), bullet['rect'])
        
        # Draw score
        score_text = font.render(f"{player1_name}: {p1_captures}  |  {player2_name}: {p2_captures}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))
        
        # Show shots remaining
        if player1_shots < RELOAD_LIMIT and now > player1_reload_time:
            p1_status = f"P1 Shots: {RELOAD_LIMIT - player1_shots}"
        else:
            p1_status = "P1 Reloading..."
        if player2_shots < RELOAD_LIMIT and now > player2_reload_time:
            p2_status = f"P2 Shots: {RELOAD_LIMIT - player2_shots}"
        else:
            p2_status = "P2 Reloading..."
        
        shots_text = name_font.render(f"{p1_status}  |  {p2_status}", True, (200, 200, 200))
        screen.blit(shots_text, (WIDTH//2 - shots_text.get_width()//2, 50))
        
        # Instructions
        inst_text = name_font.render("Shoot (SPACE/ENTER) or Tag opponent to make them drop flag!", True, (255, 255, 150))
        screen.blit(inst_text, (WIDTH//2 - inst_text.get_width()//2, HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)

# Escape Mom Horror Mode
def run_escape_mom_mode():
    """ULTRA SCARY horror mode - escape from a terrifying angry mother in pitch-black corridors!"""
    try:
        pygame.mixer.music.stop()
        # Eerie silence is scarier than music
    except:
        pass
    
    # Player (child)
    player = pygame.Rect(WIDTH//2, HEIGHT//2, 30, 40)
    player_speed = 5
    camera_shake_x = 0
    camera_shake_y = 0
    
    # Mother (nightmare chaser)
    mom = pygame.Rect(random.randint(0, WIDTH), random.randint(0, HEIGHT), 40, 60)
    mom_speed = 1.5  # Slower for fairer gameplay
    mom_visible = False  # She lurks in complete darkness!
    mom_last_seen = 0
    mom_teleport_timer = time.time()
    mom_invisible_mode = False
    mom_invisible_timer = time.time()
    
    # MULTIPLE MOMS appear later (nightmare multiplied!)
    extra_moms = []
    spawn_mom_timer = time.time()
    
    # Corridor walls (simpler maze)
    walls = []
    # Create a simpler, more navigable maze
    for i in range(10):  # Fewer walls = easier to navigate
        if random.random() < 0.5:
            # Vertical wall
            w = pygame.Rect(random.randint(100, WIDTH-200), random.randint(100, HEIGHT-200), 20, random.randint(100, 250))
        else:
            # Horizontal wall
            w = pygame.Rect(random.randint(100, WIDTH-200), random.randint(100, HEIGHT-200), random.randint(100, 250), 20)
        walls.append(w)
    
    # REACHING HANDS from walls!
    wall_hands = []
    for i in range(4):  # Fewer hands, less overwhelming
        hand_wall = random.choice(walls)
        hand_x = hand_wall.x + random.randint(0, hand_wall.width)
        hand_y = hand_wall.y + random.randint(0, hand_wall.height)
        wall_hands.append({'x': hand_x, 'y': hand_y, 'timer': time.time(), 'visible': False})
    
    # Game state
    survived_time = 0
    start_time = time.time()
    caught = False
    heartbeat_sound = 0
    light_flicker = 0
    screen_glitch = False
    whisper_timer = time.time()
    breathing_intensity = 0
    footstep_timer = time.time()
    child_cry_timer = time.time()
    fog_intensity = 0
    
    # Game state
    survived_time = 0
    start_time = time.time()
    caught = False
    heartbeat_sound = 0
    light_flicker = 0
    screen_glitch = False
    whisper_timer = time.time()
    breathing_intensity = 0
    footstep_timer = time.time()
    child_cry_timer = time.time()
    fog_intensity = 0
    
    # Blood trails (false trails to confuse player)
    blood_trails = []
    for i in range(15):
        trail_x = random.randint(100, WIDTH-100)
        trail_y = random.randint(100, HEIGHT-100)
        trail_angle = random.random() * 6.28
        blood_trails.append({'x': trail_x, 'y': trail_y, 'angle': trail_angle})
    
    # Darkness vignette (MUCH darker)
    try:
        darkness_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    except Exception as e:
        print(f"Error creating darkness surface: {e}")
        darkness_surface = pygame.Surface((WIDTH, HEIGHT))
    
    # Static/glitch surface
    glitch_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    # Fog/mist surface
    fog_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    while not caught:
        now = time.time()
        survived_time = now - start_time
        
        # Darkness increases over time (getting scarier!)
        darkness_level = min(240, 200 + int(survived_time * 5))  # Even DARKER
        light_radius = max(60, 130 - int(survived_time * 3))  # Light gets tiny
        
        # Fog increases over time (vision obscured)
        fog_intensity = min(120, int(survived_time * 4))
        
        # Camera shake when mom is close
        dx = player.x - mom.x
        dy = player.y - mom.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < 200:
            shake_power = int((200 - dist) / 10)
            camera_shake_x = random.randint(-shake_power, shake_power)
            camera_shake_y = random.randint(-shake_power, shake_power)
        else:
            camera_shake_x = 0
            camera_shake_y = 0
        
        # SPAWN ADDITIONAL MOMS AFTER 30 SECONDS (ULTIMATE HORROR!)
        if survived_time > 30 and now - spawn_mom_timer > 20 and len(extra_moms) < 3:
            new_mom = {
                'rect': pygame.Rect(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50), 40, 60),
                'speed': mom_speed * 0.8,  # Slightly slower
                'visible': False,
                'last_seen': 0
            }
            extra_moms.append(new_mom)
            spawn_mom_timer = now
            screen_glitch = True  # Screen glitches when new mom appears!
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'lobby'
        
        # Player controls
        keys = pygame.key.get_pressed()
        old_x, old_y = player.x, player.y
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player.y -= player_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player.y += player_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player.x -= player_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player.x += player_speed
        
        # Keep player in bounds
        player.x = max(10, min(WIDTH-40, player.x))
        player.y = max(10, min(HEIGHT-50, player.y))
        
        # Check wall collisions
        for wall in walls:
            if player.colliderect(wall):
                player.x, player.y = old_x, old_y
                break
        
        # Mom AI - relentless hunter
        dx = player.x - mom.x
        dy = player.y - mom.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        # Mom can go INVISIBLE randomly (you only hear her!)
        if now - mom_invisible_timer > random.randint(20, 35):
            mom_invisible_mode = not mom_invisible_mode
            mom_invisible_timer = now
            if mom_invisible_mode:
                screen_glitch = True  # Glitch when she vanishes!
        
        # Mom speeds up when close (but not too much!)
        chase_speed = mom_speed
        if dist < 300:
            chase_speed = mom_speed * 1.2  # Slightly faster when close
        if dist < 150:
            chase_speed = mom_speed * 1.5  # Moderate speed when very close
        
        # Mom moves toward player with scary precision
        if dist > 0:
            mom.x += (dx / dist) * chase_speed
            mom.y += (dy / dist) * chase_speed
        
        # Mom can TELEPORT randomly (nightmare fuel!)
        if now - mom_teleport_timer > random.randint(15, 25):
            # Teleport to a random spot near player (but not too close)
            angle = random.random() * 6.28
            teleport_dist = random.randint(250, 400)
            mom.x = player.x + math.cos(angle) * teleport_dist
            mom.y = player.y + math.sin(angle) * teleport_dist
            mom.x = max(50, min(WIDTH-50, mom.x))
            mom.y = max(50, min(HEIGHT-50, mom.y))
            mom_teleport_timer = now
            screen_glitch = True  # Screen glitches when she teleports!
        
        # Mom collision with walls
        mom_old_x, mom_old_y = mom.x, mom.y
        for wall in walls:
            if mom.colliderect(wall):
                # Mom can phase through walls MORE often (she's supernatural!)
                if random.random() < 0.5:  # 50% chance to phase through
                    pass  # She goes through walls like a ghost!
                else:
                    mom.x, mom.y = mom_old_x, mom_old_y
                break
        
        # Check if mom is close (she becomes visible - SCARY!)
        if dist < 250:
            if not mom_invisible_mode:
                mom_visible = True
            mom_last_seen = now
            breathing_intensity = int((250 - dist) / 2.5)  # Breathing gets louder
            
            # FOOTSTEP SOUNDS when she's close!
            footstep_speed = max(0.3, dist / 300)  # Faster footsteps when closer
            if now - footstep_timer > footstep_speed:
                footstep_timer = now
                # Visual footstep indicator
                print("\a")  # System beep for footstep
        elif now - mom_last_seen > 1.5:
            mom_visible = False
            breathing_intensity = 0
        
        # Extra moms AI
        for extra_mom in extra_moms:
            e_dx = player.x - extra_mom['rect'].x
            e_dy = player.y - extra_mom['rect'].y
            e_dist = math.sqrt(e_dx*e_dx + e_dy*e_dy)
            
            # Move toward player
            if e_dist > 0:
                extra_mom['rect'].x += (e_dx / e_dist) * extra_mom['speed']
                extra_mom['rect'].y += (e_dy / e_dist) * extra_mom['speed']
            
            # Visibility
            if e_dist < 250:
                extra_mom['visible'] = True
                extra_mom['last_seen'] = now
            elif now - extra_mom['last_seen'] > 1.5:
                extra_mom['visible'] = False
            
            # Check collision
            if player.colliderect(extra_mom['rect']):
                caught = True
        
        # CHILD CRYING SOUNDS echo through corridors
        if now - child_cry_timer > random.randint(12, 20):
            child_cry_timer = now
            # Visual crying indicator (you hear distant crying)
            # This adds to the psychological horror
        
        # Caught!
        if player.colliderect(mom):
            caught = True
        
        # Drawing
        # Complete darkness background
        screen.fill((0, 0, 5))  # Even MORE pitch black
        
        # Apply camera shake to everything
        shake_offset_x = camera_shake_x
        shake_offset_y = camera_shake_y
        
        # Draw blood trails (creepy false trails)
        for trail in blood_trails:
            for i in range(20):
                trail_x = int(trail['x'] + math.cos(trail['angle']) * i * 5) + shake_offset_x
                trail_y = int(trail['y'] + math.sin(trail['angle']) * i * 5) + shake_offset_y
                size = max(1, 8 - i // 3)
                pygame.draw.circle(screen, (100, 0, 0), (trail_x, trail_y), size)
        
        # Draw blood trails (creepy false trails)
        for trail in blood_trails:
            for i in range(20):
                trail_x = int(trail['x'] + math.cos(trail['angle']) * i * 5) + shake_offset_x
                trail_y = int(trail['y'] + math.sin(trail['angle']) * i * 5) + shake_offset_y
                size = max(1, 8 - i // 3)
                pygame.draw.circle(screen, (100, 0, 0), (trail_x, trail_y), size)
        
        # Flickering light effect (lights are failing!)
        light_flicker += 1
        if light_flicker % 180 < 3 or (dist < 200 and light_flicker % 60 < 2):
            # Brief flash of light when she's near (MORE SCARY!)
            screen.fill((20, 20, 25))
        
        # Draw walls (barely visible in darkness) with shake
        for wall in walls:
            wall_color = (40, 40, 50) if light_flicker % 180 < 3 else (25, 25, 35)
            shaken_wall = wall.move(shake_offset_x, shake_offset_y)
            pygame.draw.rect(screen, wall_color, shaken_wall)
            pygame.draw.rect(screen, (20, 20, 30), shaken_wall, 2)
        
        # REACHING HANDS FROM WALLS (nightmare fuel!)
        for hand in wall_hands:
            hand_dist = math.sqrt((hand['x'] - player.x)**2 + (hand['y'] - player.y)**2)
            
            # Hands become visible randomly or when player is close
            if hand_dist < 150 or (now - hand['timer'] > random.randint(5, 15) and random.random() < 0.1):
                hand['visible'] = True
                hand['timer'] = now
            elif now - hand['timer'] > 2:
                hand['visible'] = False
            
            if hand['visible']:
                # Draw creepy hand reaching from wall
                hand_x = hand['x'] + shake_offset_x
                hand_y = hand['y'] + shake_offset_y
                
                # Palm
                pygame.draw.circle(screen, (200, 180, 170), (hand_x, hand_y), 15)
                
                # Five fingers reaching toward player
                angle_to_player = math.atan2(player.y - hand_y, player.x - hand_x)
                for finger in range(5):
                    finger_angle = angle_to_player + (finger - 2) * 0.3
                    finger_length = 30 + random.randint(-5, 5)
                    finger_end_x = int(hand_x + math.cos(finger_angle) * finger_length)
                    finger_end_y = int(hand_y + math.sin(finger_angle) * finger_length)
                    pygame.draw.line(screen, (200, 180, 170), (hand_x, hand_y), (finger_end_x, finger_end_y), 6)
                    # Fingernails (dark)
                    pygame.draw.circle(screen, (80, 60, 60), (finger_end_x, finger_end_y), 3)
        
        # Draw player (small terrified child) with shake
        player_draw_x = player.x + shake_offset_x
        player_draw_y = player.y + shake_offset_y
        
        # Head (pale with fear)
        pygame.draw.circle(screen, (255, 240, 200), (player.centerx + shake_offset_x, player_draw_y+10), 8)
        # Eyes (WIDE with terror)
        pygame.draw.circle(screen, (255, 255, 255), (player.centerx-4 + shake_offset_x, player_draw_y+8), 4)
        pygame.draw.circle(screen, (255, 255, 255), (player.centerx+4 + shake_offset_x, player_draw_y+8), 4)
        pygame.draw.circle(screen, (0, 0, 0), (player.centerx-4 + shake_offset_x, player_draw_y+8), 2)
        pygame.draw.circle(screen, (0, 0, 0), (player.centerx+4 + shake_offset_x, player_draw_y+8), 2)
        # Trembling mouth (crying)
        pygame.draw.arc(screen, (0, 0, 0), (player.centerx-5 + shake_offset_x, player_draw_y+12, 10, 8), 0, 3.14, 2)
        # Tears
        if dist < 150:
            pygame.draw.line(screen, (150, 200, 255), (player.centerx-4 + shake_offset_x, player_draw_y+12), 
                           (player.centerx-4 + shake_offset_x, player_draw_y+20), 2)
            pygame.draw.line(screen, (150, 200, 255), (player.centerx+4 + shake_offset_x, player_draw_y+12), 
                           (player.centerx+4 + shake_offset_x, player_draw_y+20), 2)
        # Body (pajamas - trembling)
        body_shake_x = random.randint(-1, 1) if dist < 150 else 0
        body_shake_y = random.randint(-1, 1) if dist < 150 else 0
        pygame.draw.rect(screen, (100, 150, 200), (player_draw_x+5+body_shake_x, player_draw_y+18+body_shake_y, 20, 22))
        
        # Draw mom (NIGHTMARE when visible!)
        if (mom_visible or light_flicker % 180 < 3) and not mom_invisible_mode:
            # Horrifying distorted mother figure
            distortion = random.randint(-3, 3) if dist < 100 else 0
            
            mom_draw_x = mom.x + shake_offset_x
            mom_draw_y = mom.y + shake_offset_y
            mom_center_x = mom.centerx + shake_offset_x
            mom_center_y = mom.centery + shake_offset_y
            
            # Shadow/aura of dread around her
            for i in range(3):
                pygame.draw.circle(screen, (100, 0, 0, 30), (mom_center_x, mom_center_y), 60 + i * 20, 3)
            
            # Head (decaying, pale)
            pygame.draw.circle(screen, (200, 180, 180), (mom_center_x+distortion, mom_draw_y+15), 14)
            
            # GLOWING RED EYES (no pupils - pure evil!)
            pygame.draw.circle(screen, (255, 0, 0), (mom_center_x-8+distortion, mom_draw_y+12), 6)
            pygame.draw.circle(screen, (200, 0, 0), (mom_center_x-8+distortion, mom_draw_y+12), 4)
            pygame.draw.circle(screen, (255, 0, 0), (mom_center_x+8+distortion, mom_draw_y+12), 6)
            pygame.draw.circle(screen, (200, 0, 0), (mom_center_x+8+distortion, mom_draw_y+12), 4)
            # Eye glow effect
            pygame.draw.circle(screen, (255, 100, 100, 100), (mom_center_x-8, mom_draw_y+12), 12)
            pygame.draw.circle(screen, (255, 100, 100, 100), (mom_center_x+8, mom_draw_y+12), 12)
            
            # Angry twisted mouth (impossible grin)
            pygame.draw.arc(screen, (180, 0, 0), (mom_center_x-10, mom_draw_y+18, 20, 12), 3.14, 6.28, 4)
            # Teeth showing
            for t in range(8):
                tooth_x = mom_center_x - 8 + t * 2
                pygame.draw.line(screen, (255, 255, 200), (tooth_x, mom_draw_y+22), (tooth_x, mom_draw_y+26), 1)
            
            # Body (tattered dress)
            pygame.draw.rect(screen, (80, 40, 40), (mom_draw_x+8, mom_draw_y+27, 24, 33))
            # Rips in dress
            for i in range(5):
                rip_y = mom_draw_y + 30 + i * 6
                pygame.draw.line(screen, (60, 20, 20), (mom_draw_x+10, rip_y), (mom_draw_x+30, rip_y), 2)
            
            # Arms reaching out (longer, skeletal)
            pygame.draw.line(screen, (200, 180, 180), (mom_center_x-12, mom_draw_y+30), (mom_center_x-35, mom_draw_y+20), 8)
            pygame.draw.line(screen, (200, 180, 180), (mom_center_x+12, mom_draw_y+30), (mom_center_x+35, mom_draw_y+20), 8)
            # Claw-like hands
            for finger in range(3):
                pygame.draw.line(screen, (180, 160, 160), (mom_center_x-35, mom_draw_y+20), 
                               (mom_center_x-40+finger*3, mom_draw_y+15), 3)
                pygame.draw.line(screen, (180, 160, 160), (mom_center_x+35, mom_draw_y+20), 
                               (mom_center_x+37-finger*3, mom_draw_y+15), 3)
            
            # Warning messages when she's near!
            if dist < 150:
                warning = lobby_font.render("SHE SEES YOU!", True, (255, 0, 0))
                warning_shake_x = random.randint(-5, 5)
                warning_shake_y = random.randint(-5, 5)
                screen.blit(warning, (WIDTH//2-warning.get_width()//2+warning_shake_x, 50+warning_shake_y))
            if dist < 80:
                panic = lobby_font.render("RUN!!!", True, (255, 50, 50))
                screen.blit(panic, (WIDTH//2-panic.get_width()//2, 100))
        
        # Draw EXTRA MOMS (multiplying nightmare!)
        for extra_mom in extra_moms:
            if extra_mom['visible'] or light_flicker % 180 < 3:
                e_distortion = random.randint(-2, 2)
                e_rect = extra_mom['rect']
                e_draw_x = e_rect.x + shake_offset_x
                e_draw_y = e_rect.y + shake_offset_y
                e_center_x = e_rect.centerx + shake_offset_x
                e_center_y = e_rect.centery + shake_offset_y
                
                # Simplified but still terrifying mom
                # Head
                pygame.draw.circle(screen, (200, 180, 180), (e_center_x+e_distortion, e_draw_y+15), 14)
                # Red eyes
                pygame.draw.circle(screen, (255, 0, 0), (e_center_x-8, e_draw_y+12), 6)
                pygame.draw.circle(screen, (255, 0, 0), (e_center_x+8, e_draw_y+12), 6)
                # Body
                pygame.draw.rect(screen, (80, 40, 40), (e_draw_x+8, e_draw_y+27, 24, 33))
                # Arms
                pygame.draw.line(screen, (200, 180, 180), (e_center_x-12, e_draw_y+30), (e_center_x-35, e_draw_y+20), 8)
                pygame.draw.line(screen, (200, 180, 180), (e_center_x+12, e_draw_y+30), (e_center_x+35, e_draw_y+20), 8)
        
        # Invisible mom warning!
        if mom_invisible_mode and dist < 200:
            invisible_warning = font.render("*FOOTSTEPS APPROACHING*", True, (200, 0, 0))
            screen.blit(invisible_warning, (WIDTH//2-invisible_warning.get_width()//2, HEIGHT//2))
        
        # Screen glitch effect when she teleports
        if screen_glitch:
            glitch_surface.fill((0, 0, 0, 0))
            for i in range(20):
                glitch_y = random.randint(0, HEIGHT)
                glitch_height = random.randint(5, 30)
                pygame.draw.rect(glitch_surface, (255, 0, 0, random.randint(50, 150)), 
                               (0, glitch_y, WIDTH, glitch_height))
            screen.blit(glitch_surface, (0, 0))
            if random.random() < 0.3:
                screen_glitch = False
        
        # INTENSE darkness overlay (almost blind!)
        darkness_surface.fill((0, 0, 0))
        darkness_surface.set_alpha(darkness_level)
        
        # Create a tiny circle of light around player (getting smaller over time!)
        light_center = player.center
        for radius in range(light_radius, 0, -4):
            alpha = int(darkness_level * (1 - radius/light_radius))
            pygame.draw.circle(darkness_surface, (0, 0, 0, max(0, alpha)), light_center, radius)
        
        screen.blit(darkness_surface, (0, 0))
        
        # FOG/MIST overlay (obscures vision even more!)
        fog_surface.fill((0, 0, 0, 0))
        for i in range(30):
            fog_x = random.randint(0, WIDTH)
            fog_y = random.randint(0, HEIGHT)
            fog_size = random.randint(40, 120)
            pygame.draw.circle(fog_surface, (40, 40, 50, fog_intensity), (fog_x, fog_y), fog_size)
        screen.blit(fog_surface, (0, 0))
        
        # UI
        time_text = font.render(f"Survived: {int(survived_time)}s", True, (255, 200, 200))
        screen.blit(time_text, (20, 20))
        
        # Show extra mom counter if any exist
        if len(extra_moms) > 0:
            mom_count = font.render(f"MOMS: {len(extra_moms) + 1}!", True, (255, 100, 100))
            screen.blit(mom_count, (20, 50))
        
        tip_text = name_font.render("RUN! Press ESC to escape to menu", True, (200, 150, 150))
        screen.blit(tip_text, (WIDTH//2-tip_text.get_width()//2, HEIGHT-30))
        
        # Child crying echo effect
        if int(now - child_cry_timer) < 2:  # Show for 2 seconds
            cry_text = name_font.render("*distant child crying*", True, (150, 150, 200, 150))
            cry_x = WIDTH//2 - cry_text.get_width()//2 + random.randint(-3, 3)
            cry_y = HEIGHT//4 + random.randint(-3, 3)
            screen.blit(cry_text, (cry_x, cry_y))
        
        # Pulsing heartbeat effect when mom is close
        if dist < 200:
            heartbeat_sound += 1
            pulse_size = 15 + int((200-dist) / 10)  # Bigger pulse when closer
            if heartbeat_sound % max(10, int(dist/10)) < 5:  # Faster heartbeat when closer
                pygame.draw.circle(screen, (255, 0, 0), (30, HEIGHT-50), pulse_size, 3)
                pygame.draw.circle(screen, (200, 0, 0), (30, HEIGHT-50), pulse_size-3, 2)
        
        # Breathing indicator (when she's VERY close)
        if breathing_intensity > 0:
            breath_text = name_font.render("*breathing sounds*", True, (255, 100, 100, breathing_intensity))
            screen.blit(breath_text, (WIDTH//2-breath_text.get_width()//2, HEIGHT//2-200))
        
        # Random whispers appear (MORE VARIETY AND TERROR!)
        if now - whisper_timer > random.randint(8, 15):
            whisper_timer = now
            whispers = [
                "I'M COMING...", 
                "YOU CAN'T HIDE...", 
                "FOUND YOU...", 
                "STOP RUNNING...",
                "COME HERE...",
                "I SEE YOU...",
                "NO ESCAPE...",
                "YOU'RE MINE...",
                "MOMMY'S HERE...",
                "DON'T RUN FROM MOTHER...",
                "I'M RIGHT BEHIND YOU...",
                "THERE'S NO WAY OUT..."
            ]
            whisper = random.choice(whispers)
            # Show whisper for a moment
            if random.random() < 0.4:
                whisper_text = font.render(whisper, True, (150, 0, 0))
                whisper_x = random.randint(100, WIDTH-200)
                whisper_y = random.randint(100, HEIGHT-200)
                screen.blit(whisper_text, (whisper_x, whisper_y))
        
        pygame.display.flip()
        clock.tick(60)
    
    # ULTRA TERRIFYING JUMPSCARE! Maximum horror!
    jumpscare_time = time.time()
    jumpscare_duration = 4.5  # 4.5 seconds of PURE TERROR (longer!)
    
    # PRE-JUMPSCARE: Brief freeze frame (psychological horror)
    freeze_frame = screen.copy()
    for freeze_frame_count in range(15):  # 0.25 seconds of eerie stillness
        screen.blit(freeze_frame, (0, 0))
        # Darken gradually
        dark_overlay = pygame.Surface((WIDTH, HEIGHT))
        dark_overlay.set_alpha(freeze_frame_count * 15)
        dark_overlay.fill((0, 0, 0))
        screen.blit(dark_overlay, (0, 0))
        
        # Warning text fades in
        if freeze_frame_count > 5:
            warning_alpha = min(255, (freeze_frame_count - 5) * 25)
            warning_text = lobby_font.render("NO...", True, (255, 0, 0))
            warning_surf = pygame.Surface(warning_text.get_size(), pygame.SRCALPHA)
            warning_surf.fill((255, 0, 0, warning_alpha))
            warning_text.set_alpha(warning_alpha)
            screen.blit(warning_text, (WIDTH//2 - warning_text.get_width()//2, HEIGHT//2 - 50))
        
        pygame.display.flip()
        clock.tick(60)
    
    # SUDDEN BLACK SCREEN (builds tension)
    screen.fill((0, 0, 0))
    pygame.display.flip()
    time.sleep(0.3)  # Brief silence...
    
    # Play scary scream sound at MAXIMUM VOLUME
    try:
        pygame.mixer.music.load(resource_path("scary-scream.mp3"))
        pygame.mixer.music.set_volume(1.0)  # MAX VOLUME!
        pygame.mixer.music.play()
    except:
        # Fallback to system beeps
        for _ in range(20):
            print("\a")  # System beep
    
    while time.time() - jumpscare_time < jumpscare_duration:
        elapsed = time.time() - jumpscare_time
        progress = elapsed / jumpscare_duration
        
        # INTENSE rapid flashing for shock effect (MORE EXTREME!)
        flash_speed = int((time.time() - jumpscare_time) * 40)  # Faster flashing!
        if flash_speed % 2 == 0:
            screen.fill((0, 0, 0))
        else:
            # Increasingly red and violent
            red_intensity = int(150 + progress * 105)
            screen.fill((red_intensity, 0, 0))
        
        # SCREEN INVERSION effect (disorienting!)
        if int(elapsed * 20) % 7 < 2:
            screen.fill((255, 255, 255))  # Blinding white flash
        
        # MORE Static noise effect (TV static horror)
        if random.random() < 0.6:  # More frequent
            for i in range(400):  # More static particles
                static_x = random.randint(0, WIDTH)
                static_y = random.randint(0, HEIGHT)
                static_color = random.randint(0, 255)
                pygame.draw.circle(screen, (static_color, 0, 0), (static_x, static_y), random.randint(1, 3))
        
        # GLITCH LINES across screen
        for i in range(random.randint(5, 15)):
            glitch_y = random.randint(0, HEIGHT)
            glitch_height = random.randint(2, 20)
            glitch_color = (random.randint(200, 255), 0, 0)
            pygame.draw.rect(screen, glitch_color, (0, glitch_y, WIDTH, glitch_height))
        
        # Mom grows MASSIVE and DISTORTED (even BIGGER!)
        scale = 40 + (progress * 30)  # Grows from 40x to 70x size (HUGE!)
        face_size = int(600 * scale / 40)  # Even more massive
        
        # FACE LUNGES AT YOU (moves forward!)
        lunge_offset = int(progress * 150)  # Face gets closer!
        face_x = WIDTH // 2 + random.randint(-15, 15) + int(math.sin(elapsed * 10) * 20)  # More shake + sway
        face_y = HEIGHT // 2 + random.randint(-15, 15) - lunge_offset  # Moves toward you!
        
        # Face rotation effect (unnatural twisting!)
        rotation_angle = math.sin(elapsed * 8) * 0.3
        
        # GROTESQUE DECAYING HEAD with pulsing veins (MORE DETAILED!)
        pulse = int(15 * math.sin(elapsed * 20))  # Faster, bigger pulse
        
        # Multiple layers of rotting skin
        for layer in range(3):
            layer_size = face_size//2 + pulse - (layer * 15)
            decay_color = (
                220 + int(35 * progress) - layer * 20,
                140 - int(80 * progress) - layer * 30,
                140 - int(80 * progress) - layer * 30
            )
            pygame.draw.circle(screen, decay_color, (face_x, face_y), layer_size)
        
        # MORE Rotting flesh effect (disgusting!)
        for i in range(100):  # Double the rot spots!
            rot_x = face_x + random.randint(-face_size//2, face_size//2)
            rot_y = face_y + random.randint(-face_size//2, face_size//2)
            rot_color = random.choice([
                (120, 80, 60),
                (100, 60, 40),
                (80, 40, 20),
                (60, 20, 10)
            ])
            pygame.draw.circle(screen, rot_color, (rot_x, rot_y), random.randint(3, 15))
        
        # MAGGOTS/INSECTS crawling on face!
        for i in range(30):
            maggot_angle = random.random() * 6.28
            maggot_dist = random.randint(0, face_size//2)
            maggot_x = int(face_x + math.cos(maggot_angle + elapsed * 2) * maggot_dist)
            maggot_y = int(face_y + math.sin(maggot_angle + elapsed * 2) * maggot_dist)
            pygame.draw.circle(screen, (220, 220, 180), (maggot_x, maggot_y), random.randint(2, 4))
        
        # Deep dark circles and wrinkles (MORE PRONOUNCED!)
        pygame.draw.ellipse(screen, (40, 20, 40), (face_x - 200, face_y - 140, 160, 100))
        pygame.draw.ellipse(screen, (40, 20, 40), (face_x + 40, face_y - 140, 160, 100))
        pygame.draw.ellipse(screen, (20, 10, 20), (face_x - 190, face_y - 130, 140, 80))
        pygame.draw.ellipse(screen, (20, 10, 20), (face_x + 50, face_y - 130, 140, 80))
        
        # ENORMOUS BLOODSHOT DEMON EYES - staring INTO YOUR SOUL!
        eye_size = int(140 + progress * 70)  # Even BIGGER eyes!
        eye_spacing = int(180 + progress * 60)
        
        # Eyes FOLLOW you with unnatural movement
        eye_offset_x = int(math.sin(elapsed * 6) * 10)
        eye_offset_y = int(math.cos(elapsed * 6) * 10)
        
        # Left eye - HORRIFYING
        # Bloodshot sclera (yellowed, diseased)
        pygame.draw.ellipse(screen, (255, 255, 180), (face_x - eye_spacing - eye_size//2, face_y - 140, eye_size, eye_size + 50))
        pygame.draw.ellipse(screen, (240, 240, 140), (face_x - eye_spacing - eye_size//2 + 10, face_y - 130, eye_size - 20, eye_size + 30))
        
        # MASSIVE network of blood veins in eye (grotesque!)
        for i in range(60):  # More veins!
            vein_angle = random.random() * 6.28
            vein_length = random.randint(30, eye_size//2)
            vein_start_x = face_x - eye_spacing
            vein_start_y = face_y - 90
            vein_end_x = int(vein_start_x + math.cos(vein_angle) * vein_length)
            vein_end_y = int(vein_start_y + math.sin(vein_angle) * vein_length)
            vein_thickness = random.randint(2, 6)
            pygame.draw.line(screen, (200, 0, 0), (vein_start_x, vein_start_y), (vein_end_x, vein_end_y), vein_thickness)
        
        # Bloodshot RED iris - pulsing violently
        iris_size = int(70 + progress * 30 + pulse)
        iris_x = face_x - eye_spacing + eye_offset_x
        iris_y = face_y - 90 + eye_offset_y
        
        # Multiple iris layers (depth)
        pygame.draw.circle(screen, (255, 0, 0), (iris_x, iris_y), iris_size)
        pygame.draw.circle(screen, (220, 0, 0), (iris_x, iris_y), iris_size - 10)
        pygame.draw.circle(screen, (180, 0, 0), (iris_x, iris_y), iris_size - 20)
        
        # Dilated pupil (pure evil) - expands over time
        pupil_size = int(40 + progress * 20)
        pygame.draw.circle(screen, (0, 0, 0), (iris_x, iris_y), pupil_size)
        
        # Demonic glint with color shift
        glint_color = (255, int(100 + progress * 155), int(100 + progress * 155))
        pygame.draw.circle(screen, glint_color, (iris_x + 15, iris_y - 12), 10)
        pygame.draw.circle(screen, (255, 255, 255), (iris_x + 15, iris_y - 12), 5)
        
        # Right eye - EQUALLY TERRIFYING
        pygame.draw.ellipse(screen, (255, 255, 180), (face_x + eye_spacing - eye_size//2, face_y - 140, eye_size, eye_size + 50))
        pygame.draw.ellipse(screen, (240, 240, 140), (face_x + eye_spacing - eye_size//2 + 10, face_y - 130, eye_size - 20, eye_size + 30))
        
        # Blood veins in right eye
        for i in range(60):
            vein_angle = random.random() * 6.28
            vein_length = random.randint(30, eye_size//2)
            vein_start_x = face_x + eye_spacing
            vein_start_y = face_y - 90
            vein_end_x = int(vein_start_x + math.cos(vein_angle) * vein_length)
            vein_end_y = int(vein_start_y + math.sin(vein_angle) * vein_length)
            vein_thickness = random.randint(2, 6)
            pygame.draw.line(screen, (200, 0, 0), (vein_start_x, vein_start_y), (vein_end_x, vein_end_y), vein_thickness)
        
        iris_x_right = face_x + eye_spacing + eye_offset_x
        iris_y_right = face_y - 90 + eye_offset_y
        pygame.draw.circle(screen, (255, 0, 0), (iris_x_right, iris_y_right), iris_size)
        pygame.draw.circle(screen, (220, 0, 0), (iris_x_right, iris_y_right), iris_size - 10)
        pygame.draw.circle(screen, (180, 0, 0), (iris_x_right, iris_y_right), iris_size - 20)
        pygame.draw.circle(screen, (0, 0, 0), (iris_x_right, iris_y_right), pupil_size)
        pygame.draw.circle(screen, glint_color, (iris_x_right + 15, iris_y_right - 12), 10)
        pygame.draw.circle(screen, (255, 255, 255), (iris_x_right + 15, iris_y_right - 12), 5)
        pygame.draw.circle(screen, (220, 0, 0), (face_x + eye_spacing, face_y - 80), iris_size)
        pygame.draw.circle(screen, (150, 0, 0), (face_x + eye_spacing, face_y - 80), iris_size - 10)
        pygame.draw.circle(screen, (0, 0, 0), (face_x + eye_spacing, face_y - 80), int(35 + progress * 10))
        pygame.draw.circle(screen, (255, 100, 100), (face_x + eye_spacing + 12, face_y - 88), 8)
        
        # MASSIVE network of blood veins spreading everywhere!
        for i in range(40):
            vein_angle = random.random() * 6.28
            vein_length = random.randint(40, 120)
            thickness = random.randint(2, 5)
            # Left eye veins
            start_x = face_x - eye_spacing
            start_y = face_y - 80
            end_x = int(start_x + math.cos(vein_angle) * vein_length)
            end_y = int(start_y + math.sin(vein_angle) * vein_length)
            pygame.draw.line(screen, (180, 0, 0), (start_x, start_y), (end_x, end_y), thickness)
            # Right eye veins
            start_x = face_x + eye_spacing
            end_x = int(start_x + math.cos(vein_angle) * vein_length)
            end_y = int(start_y + math.sin(vein_angle) * vein_length)
            pygame.draw.line(screen, (180, 0, 0), (start_x, start_y), (end_x, end_y), thickness)
        
        # MASSIVE ANGRY EYEBROWS (furious)
        pygame.draw.line(screen, (40, 20, 20), (face_x - eye_spacing - 80, face_y - 180), 
                        (face_x - eye_spacing + 60, face_y - 120), 25)
        pygame.draw.line(screen, (40, 20, 20), (face_x + eye_spacing - 60, face_y - 120), 
                        (face_x + eye_spacing + 80, face_y - 180), 25)
        
        # Deep angry wrinkles across forehead
        for i in range(8):
            y_pos = face_y - 200 + i * 18
            thickness = random.randint(3, 6)
            pygame.draw.line(screen, (120, 80, 80), (face_x - 120, y_pos), (face_x + 120, y_pos + 8), thickness)
        
        # GAPING MOUTH - grows IMPOSSIBLY WIDE to devour you!
        mouth_width = int(250 + progress * 150)  # MASSIVE mouth
        mouth_height = int(220 + progress * 120)  # Opens HUGE
        mouth_y = int(face_y + 40 - progress * 30)  # Lunges toward you
        
        # Throat of ABSOLUTE DARKNESS (the void)
        pygame.draw.ellipse(screen, (0, 0, 0), (face_x - mouth_width//2, mouth_y, mouth_width, mouth_height))
        pygame.draw.ellipse(screen, (10, 0, 0), (face_x - mouth_width//2 + 30, mouth_y + 30, mouth_width - 60, mouth_height - 60))
        # Inner darkness pulsing
        inner_darkness = int(mouth_width - 100 + pulse * 2)
        pygame.draw.ellipse(screen, (5, 0, 0), (face_x - inner_darkness//2, mouth_y + 50, inner_darkness, mouth_height - 100))
        
        # Wet disgusting tongue
        tongue_points = [
            (face_x - 60, mouth_y + mouth_height - 60),
            (face_x, mouth_y + mouth_height - 30),
            (face_x + 60, mouth_y + mouth_height - 60),
            (face_x + 50, mouth_y + mouth_height - 20),
            (face_x - 50, mouth_y + mouth_height - 20)
        ]
        pygame.draw.polygon(screen, (200, 100, 120), tongue_points)
        # Tongue texture
        for i in range(10):
            pygame.draw.line(screen, (180, 80, 100), (face_x - 40, mouth_y + mouth_height - 50 + i * 5), 
                           (face_x + 40, mouth_y + mouth_height - 50 + i * 5), 2)
        
        # Dripping saliva (disgusting)
        if int(elapsed * 15) % 4 < 2:
            for drip in range(6):
                drip_x = face_x - 80 + drip * 30
                drip_length = random.randint(40, 100)
                pygame.draw.line(screen, (220, 220, 255, 200), (drip_x, mouth_y + 30), 
                               (drip_x, mouth_y + 30 + drip_length), 4)
                pygame.draw.circle(screen, (220, 220, 255), (drip_x, mouth_y + 30 + drip_length), 4)
        
        # HORRIFYING SHARP TEETH (many more rows!)
        teeth_count = 20
        # Top teeth (long and sharp)
        for i in range(teeth_count):
            tooth_x = face_x - mouth_width//2 + 30 + i * (mouth_width - 60) // teeth_count
            tooth_width = 18
            tooth_height = int(45 + progress * 30)
            # Sharp tooth shape
            pygame.draw.polygon(screen, (255, 255, 200), [
                (tooth_x, mouth_y + 10),
                (tooth_x + tooth_width, mouth_y + 10),
                (tooth_x + tooth_width//2, mouth_y + tooth_height)
            ])
            # Decay and stains
            pygame.draw.polygon(screen, (230, 230, 160), [
                (tooth_x + 3, mouth_y + 10),
                (tooth_x + tooth_width - 3, mouth_y + 10),
                (tooth_x + tooth_width//2, mouth_y + tooth_height - 8)
            ])
            # Blood on teeth
            if random.random() < 0.4:
                pygame.draw.line(screen, (150, 0, 0), (tooth_x + tooth_width//2, mouth_y + 15), 
                               (tooth_x + tooth_width//2, mouth_y + tooth_height), 3)
            
            # Bottom teeth (equally terrifying)
            tooth_x_bottom = face_x - mouth_width//2 + 40 + i * (mouth_width - 80) // teeth_count
            pygame.draw.polygon(screen, (255, 255, 200), [
                (tooth_x_bottom, mouth_y + mouth_height - tooth_height),
                (tooth_x_bottom + tooth_width, mouth_y + mouth_height - tooth_height),
                (tooth_x_bottom + tooth_width//2, mouth_y + mouth_height - 10)
            ])
        
        # Blood and gore around mouth
        for i in range(40):
            stain_x = face_x - mouth_width//2 + random.randint(-30, mouth_width + 30)
            stain_y = mouth_y + random.randint(-20, mouth_height + 20)
            pygame.draw.circle(screen, (100, 0, 0), (stain_x, stain_y), random.randint(4, 12))
        
        # Deep CRACKS and VEINS across the entire face
        for i in range(60):
            crack_start_x = face_x + random.randint(-face_size//2, face_size//2)
            crack_start_y = face_y + random.randint(-face_size//2, face_size//2)
            crack_end_x = crack_start_x + random.randint(-80, 80)
            crack_end_y = crack_start_y + random.randint(-80, 80)
            pygame.draw.line(screen, (120, 0, 0), (crack_start_x, crack_start_y), (crack_end_x, crack_end_y), random.randint(3, 6))
        
        # Matted, stringy hair (like from a horror movie)
        for i in range(50):
            hair_x = face_x + random.randint(-face_size//2, face_size//2)
            hair_y = face_y - face_size//2 + random.randint(-40, 40)
            hair_length = random.randint(60, 150)
            hair_thickness = random.randint(3, 7)
            pygame.draw.line(screen, (15, 10, 10), (hair_x, hair_y), 
                           (hair_x + random.randint(-30, 30), hair_y - hair_length), hair_thickness)
        
        # EXTREME shake effect - screen violently trembles (EVEN MORE INTENSE!)
        shake_intensity = int(25 + progress * 50)  # Stronger shake!
        shake_x = random.randint(-shake_intensity, shake_intensity)
        shake_y = random.randint(-shake_intensity, shake_intensity)
        
        # MULTIPLE OVERLAPPING SCARY FACES (hallucination effect!)
        if progress > 0.5 and random.random() < 0.3:
            for ghost_face in range(3):
                ghost_x = WIDTH // 2 + random.randint(-200, 200)
                ghost_y = HEIGHT // 2 + random.randint(-200, 200)
                ghost_size = random.randint(50, 150)
                ghost_alpha = random.randint(50, 150)
                # Ghostly additional faces
                pygame.draw.circle(screen, (255, 0, 0, ghost_alpha), (ghost_x, ghost_y), ghost_size)
                pygame.draw.circle(screen, (255, 0, 0), (ghost_x - 20, ghost_y - 10), 15)
                pygame.draw.circle(screen, (255, 0, 0), (ghost_x + 20, ghost_y - 10), 15)
        
        # TERRIFYING text messages (MORE VARIETY AND HORROR!)
        text_shake_x = shake_x + random.randint(-10, 10)
        text_shake_y = shake_y + random.randint(-10, 10)
        
        if progress < 0.2:
            jumpscare_text = lobby_font.render("SHE CAUGHT YOU!", True, (255, 255, 255))
            screen.blit(jumpscare_text, (WIDTH//2 - jumpscare_text.get_width()//2 + text_shake_x, 60 + text_shake_y))
        elif progress < 0.35:
            jumpscare_text = lobby_font.render("NO ESCAPE!", True, (255, 200, 200))
            screen.blit(jumpscare_text, (WIDTH//2 - jumpscare_text.get_width()//2 + text_shake_x, 60 + text_shake_y))
            warning2 = font.render("YOU SHOULD HAVE RUN FASTER...", True, (200, 0, 0))
            screen.blit(warning2, (WIDTH//2 - warning2.get_width()//2 - text_shake_x//2, HEIGHT - 150 - text_shake_y//2))
        elif progress < 0.55:
            jumpscare_text = lobby_font.render("SHE'S DEVOURING YOU!", True, (255, int(50 + progress * 200), int(50 + progress * 200)))
            screen.blit(jumpscare_text, (WIDTH//2 - jumpscare_text.get_width()//2 + text_shake_x, 60 + text_shake_y))
            warning2 = font.render("FEEL HER TEETH CRUSHING YOUR BONES...", True, (150, 0, 0))
            screen.blit(warning2, (WIDTH//2 - warning2.get_width()//2 + text_shake_x//3, HEIGHT - 150 + text_shake_y//3))
        elif progress < 0.75:
            jumpscare_text = lobby_font.render("YOU'RE BEING EATEN ALIVE!", True, (255, 0, 0))
            screen.blit(jumpscare_text, (WIDTH//2 - jumpscare_text.get_width()//2 + text_shake_x, 60 + text_shake_y))
            warning2 = font.render("ETERNAL DARKNESS AWAITS...", True, (100, 0, 0))
            screen.blit(warning2, (WIDTH//2 - warning2.get_width()//2 - text_shake_x//2, HEIGHT - 150 - text_shake_y//2))
        else:
            jumpscare_text = lobby_font.render("CONSUMED BY MOTHER", True, (200, 0, 0))
            screen.blit(jumpscare_text, (WIDTH//2 - jumpscare_text.get_width()//2 + text_shake_x, 60 + text_shake_y))
            warning2 = font.render("YOU ARE HERS NOW...", True, (80, 0, 0))
            screen.blit(warning2, (WIDTH//2 - warning2.get_width()//2 + text_shake_x//2, HEIGHT - 150 + text_shake_y//2))
        
        # RANDOM HORRIFYING MESSAGES flash across screen
        if random.random() < 0.15:
            random_messages = [
                "HELP ME",
                "IT HURTS", 
                "PLEASE NO",
                "I CAN'T BREATHE",
                "MOMMY NO",
                "SAVE ME",
                "TOO LATE"
            ]
            flash_msg = font.render(random.choice(random_messages), True, (255, 255, 255))
            flash_x = random.randint(50, WIDTH - 200)
            flash_y = random.randint(100, HEIGHT - 100)
            screen.blit(flash_msg, (flash_x, flash_y))
        
        pygame.display.flip()
        clock.tick(60)
        
        # Allow emergency exit (some people can't handle this level of horror!)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'lobby'
    
    # After jumpscare, show normal game over screen with name entry
    player_name = ""
    entering_name = True
    name_saved = False
    
    while True:
        screen.fill((20, 0, 0))  # Red tint
        
        gameover = lobby_font.render("SHE CAUGHT YOU!", True, (255, 0, 0))
        screen.blit(gameover, (WIDTH//2-gameover.get_width()//2, HEIGHT//2-200))
        
        time_survived_text = font.render(f"You survived for {int(survived_time)} seconds", True, (255, 255, 255))
        screen.blit(time_survived_text, (WIDTH//2-time_survived_text.get_width()//2, HEIGHT//2-130))
        
        # Name entry section
        if entering_name and not name_saved:
            prompt = font.render("Enter your name for the leaderboard:", True, (200, 200, 200))
            screen.blit(prompt, (WIDTH//2-prompt.get_width()//2, HEIGHT//2-60))
            
            # Name input box
            name_box = pygame.Rect(WIDTH//2-200, HEIGHT//2, 400, 50)
            pygame.draw.rect(screen, (50, 20, 20), name_box)
            pygame.draw.rect(screen, (150, 50, 50), name_box, 3)
            
            name_text = font.render(player_name + "_", True, (255, 255, 255))
            screen.blit(name_text, (name_box.x + 10, name_box.y + 10))
            
            hint = name_font.render("Press ENTER to submit", True, (150, 150, 150))
            screen.blit(hint, (WIDTH//2-hint.get_width()//2, HEIGHT//2+70))
        elif name_saved:
            saved_msg = font.render(f"Score saved! Thanks, {player_name}!", True, (100, 255, 100))
            screen.blit(saved_msg, (WIDTH//2-saved_msg.get_width()//2, HEIGHT//2-20))
        
        back_button = pygame.Rect(WIDTH//2-100, HEIGHT//2+120, 200, 60)
        pygame.draw.rect(screen, (100, 0, 0), back_button)
        back_text = font.render("Back to Menu", True, (255, 255, 255))
        screen.blit(back_text, (back_button.centerx-back_text.get_width()//2, back_button.centery-back_text.get_height()//2))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if entering_name and not name_saved:
                    if event.key == pygame.K_RETURN and player_name.strip():
                        # Save the score
                        save_highscore(player_name.strip(), int(survived_time), mode='mom')
                        name_saved = True
                        entering_name = False
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        # Skip name entry
                        entering_name = False
                    elif len(player_name) < 15 and event.unicode.isprintable():
                        player_name += event.unicode
                else:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        return 'lobby'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return 'lobby'

# Main program loop
while True:
    mode = mode_lobby()
    if mode == 0:
        # Show Play Local / Play Online selection
        selected = 0
        options = ["Play Local", "Play Online"]
        while True:
            screen.fill((30, 30, 30))
            title = lobby_font.render("Battle Mode", True, (255,255,255))
            screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-120))
            local_rect = pygame.Rect(WIDTH//2-220, HEIGHT//2, 200, 80)
            pygame.draw.rect(screen, (0,180,0), local_rect)
            local_text = font.render("Play Local", True, (255,255,255))
            screen.blit(local_text, (local_rect.centerx-local_text.get_width()//2, local_rect.centery-local_text.get_height()//2))
            online_rect = pygame.Rect(WIDTH//2+20, HEIGHT//2, 200, 80)
            pygame.draw.rect(screen, (0,120,255), online_rect)
            online_text = font.render("Play Online", True, (255,255,255))
            screen.blit(online_text, (online_rect.centerx-online_text.get_width()//2, online_rect.centery-online_text.get_height()//2))
            back_rect = pygame.Rect(WIDTH//2-100, HEIGHT-100, 200, 60)
            pygame.draw.rect(screen, (100,100,100), back_rect)
            back_text = font.render("Back", True, (255,255,255))
            screen.blit(back_text, (back_rect.centerx-back_text.get_width()//2, back_rect.centery-back_text.get_height()//2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        break  # Return to main menu with ESC key
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_rect.collidepoint(event.pos):
                        break  # Return to main menu
                    if local_rect.collidepoint(event.pos):
                        player1_name = get_player_name("Player 1, enter your name:", HEIGHT//2 - 120)
                        player2_name = get_player_name("Player 2, enter your name:", HEIGHT//2 + 40)
                        char_choices = character_select(0)  # Mafia mode
                        # Go straight to battle, no shop, no upgrades
                        result = run_game_with_upgrades(player1_name, player2_name, char_choices, 0, 0, 0, 0, 0, 0, mode=0)
                        if result == 'lobby':
                            break  # Return to main menu
                    if online_rect.collidepoint(event.pos):
                        # Online mode for Battle Mode
                        role = online_host_or_join()
                        if role == 'host':
                            # Host enters name BEFORE waiting for connection
                            player_name = get_player_name("Host: Enter your name:", HEIGHT//2)
                            
                            # Show waiting screen with IP
                            local_ip = get_local_ip()
                            
                            screen.fill((30, 30, 30))
                            wait_text = lobby_font.render("Waiting for player to join...", True, (255, 255, 0))
                            screen.blit(wait_text, (WIDTH//2 - wait_text.get_width()//2, HEIGHT//2 - 100))
                            ip_text = font.render(f"Your IP: {local_ip}", True, (255, 255, 255))
                            screen.blit(ip_text, (WIDTH//2 - ip_text.get_width()//2, HEIGHT//2 - 30))
                            port_text = font.render("Port: 50007", True, (255, 255, 255))
                            screen.blit(port_text, (WIDTH//2 - port_text.get_width()//2, HEIGHT//2 + 10))
                            cancel_text = name_font.render("Press ESC to cancel", True, (150, 150, 150))
                            screen.blit(cancel_text, (WIDTH//2 - cancel_text.get_width()//2, HEIGHT//2 + 60))
                            pygame.display.flip()
                            
                            try:
                                net = NetworkHost()
                                # Wait for connection with cancel option
                                waiting = True
                                while waiting and not net.conn:
                                    for ev in pygame.event.get():
                                        if ev.type == pygame.QUIT:
                                            net.close()
                                            pygame.quit()
                                            sys.exit()
                                        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                                            net.close()
                                            waiting = False
                                            continue
                                    pygame.time.wait(100)
                                
                                if net.conn:
                                    my_char, opp_char = online_character_select_and_countdown(net, True, 0)
                                    if my_char is not None and opp_char is not None:
                                        char_choices = [my_char, opp_char]
                                        run_game_with_upgrades(player_name, "Opponent", char_choices, 0, 0, 0, 0, 0, 0, mode=0, net=net, is_host=True)
                                    net.close()
                            except Exception as e:
                                screen.fill((30, 30, 30))
                                error_text = font.render(f"Connection error: {str(e)}", True, (255, 0, 0))
                                screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
                                pygame.display.flip()
                                pygame.time.wait(2000)
                        elif role == 'join':
                            host_ip = get_ip_address()
                            if host_ip:
                                screen.fill((30, 30, 30))
                                conn_text = lobby_font.render("Connecting...", True, (255, 255, 0))
                                screen.blit(conn_text, (WIDTH//2 - conn_text.get_width()//2, HEIGHT//2))
                                pygame.display.flip()
                                
                                try:
                                    net = NetworkClient(host_ip)
                                    player_name = get_player_name("Enter your name:", HEIGHT//2)
                                    my_char, opp_char = online_character_select_and_countdown(net, False, 0)
                                    if my_char is not None and opp_char is not None:
                                        char_choices = [opp_char, my_char]
                                        run_game_with_upgrades("Opponent", player_name, char_choices, 0, 0, 0, 0, 0, 0, mode=0, net=net, is_host=False)
                                    net.close()
                                except Exception as e:
                                    screen.fill((30, 30, 30))
                                    error_text = font.render(f"Connection error: {str(e)}", True, (255, 0, 0))
                                    screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
                                    pygame.display.flip()
                                    pygame.time.wait(2000)
                        break
            else:
                continue
            break  # Always return to main menu after game ends
    elif mode == 1:
        # Coin Collection Mode: Play Local / Play Online
       
        selected = 0
        options = ["Play Local", "Play Online"]
        while True:
            screen.fill((30, 30, 30))
            title = lobby_font.render("Coin Collection Mode", True, (255,255,255))
            screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-120))
            local_rect = pygame.Rect(WIDTH//2-220, HEIGHT//2, 200, 80)
            online_rect = pygame.Rect(WIDTH//2+20, HEIGHT//2, 200, 80)
            pygame.draw.rect(screen, (0,180,0), local_rect)
            pygame.draw.rect(screen, (0,120,255), online_rect)
            local_text = font.render("Play Local", True, (255,255,255))
            online_text = font.render("Play Online", True, (255,255,255))
            screen.blit(local_text, (local_rect.centerx-local_text.get_width()//2, local_rect.centery-local_text.get_height()//2))
            screen.blit(online_text, (online_rect.centerx-online_text.get_width()//2, online_rect.centery-online_text.get_height()//2))
            back_rect = pygame.Rect(WIDTH//2-100, HEIGHT-100, 200, 60)
            pygame.draw.rect(screen, (100,100,100), back_rect)
            back_text = font.render("Back", True, (255,255,255))
            screen.blit(back_text, (back_rect.centerx-back_text.get_width()//2, back_rect.centery-back_text.get_height()//2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if local_rect.collidepoint(event.pos):
                        player1_name = get_player_name("Player 1, enter your name:", HEIGHT//2 - 120)
                        player2_name = get_player_name("Player 2, enter your name:", HEIGHT//2 + 40)
                        char_choices = character_select(1)
                        run_coin_collection_and_shop(player1_name, player2_name, char_choices)
                        break
                    if online_rect.collidepoint(event.pos):
                        # Online mode for Coin Collection
                        role = online_host_or_join()
                        if role == 'host':
                            # Host enters name BEFORE waiting for connection
                            player_name = get_player_name("Host: Enter your name:", HEIGHT//2)
                            
                            # Show waiting screen with IP
                            local_ip = get_local_ip()
                            
                            screen.fill((30, 30, 30))
                            wait_text = lobby_font.render("Waiting for player to join...", True, (255, 255, 0))
                            screen.blit(wait_text, (WIDTH//2 - wait_text.get_width()//2, HEIGHT//2 - 100))
                            ip_text = font.render(f"Your IP: {local_ip}", True, (255, 255, 255))
                            screen.blit(ip_text, (WIDTH//2 - ip_text.get_width()//2, HEIGHT//2 - 30))
                            port_text = font.render("Port: 50007", True, (255, 255, 255))
                            screen.blit(port_text, (WIDTH//2 - port_text.get_width()//2, HEIGHT//2 + 10))
                            cancel_text = name_font.render("Press ESC to cancel", True, (150, 150, 150))
                            screen.blit(cancel_text, (WIDTH//2 - cancel_text.get_width()//2, HEIGHT//2 + 60))
                            pygame.display.flip()
                            
                            try:
                                net = NetworkHost()
                                # Wait for connection with cancel option
                                waiting = True
                                while waiting and not net.conn:
                                    for ev in pygame.event.get():
                                        if ev.type == pygame.QUIT:
                                            net.close()
                                            pygame.quit()
                                            sys.exit()
                                        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                                            net.close()
                                            waiting = False
                                            continue
                                    pygame.time.wait(100)
                                
                                if net.conn:
                                    char_choices = character_select(1)
                                    # Simplified online - just play locally for now
                                    run_coin_collection_and_shop(player_name, "Opponent", char_choices)
                                    net.close()
                            except Exception as e:
                                screen.fill((30, 30, 30))
                                error_text = font.render(f"Connection error: {str(e)}", True, (255, 0, 0))
                                screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
                                pygame.display.flip()
                                pygame.time.wait(2000)
                        elif role == 'join':
                            host_ip = get_ip_address()
                            if host_ip:
                                screen.fill((30, 30, 30))
                                conn_text = lobby_font.render("Connecting...", True, (255, 255, 0))
                                screen.blit(conn_text, (WIDTH//2 - conn_text.get_width()//2, HEIGHT//2))
                                pygame.display.flip()
                                
                                try:
                                    net = NetworkClient(host_ip)
                                    player_name = get_player_name("Enter your name:", HEIGHT//2)
                                    char_choices = character_select(1)
                                    # Simplified online - just play locally for now
                                    run_coin_collection_and_shop("Opponent", player_name, char_choices)
                                    net.close()
                                except Exception as e:
                                    screen.fill((30, 30, 30))
                                    error_text = font.render(f"Connection error: {str(e)}", True, (255, 0, 0))
                                    screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
                                    pygame.display.flip()
                                    pygame.time.wait(2000)
                        break
                    if back_rect.collidepoint(event.pos):
                        break
            else:
                continue
            break  # Always return to main menu after game ends
    elif mode == 2:
        # Show Play Local / Play Online selection for Survival Mode
        selected = 0
        options = ["Play Local", "Play Online"]
        while True:
            screen.fill((30, 30, 30))
            title = lobby_font.render("Survival Mode", True, (255,255,255))
            screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-120))
            
            local_rect = pygame.Rect(WIDTH//2-220, HEIGHT//2, 200, 80)
            online_rect = pygame.Rect(WIDTH//2+20, HEIGHT//2, 200, 80)
            pygame.draw.rect(screen, (0,180,0), local_rect)
            pygame.draw.rect(screen, (0,120,255), online_rect)
            local_text = font.render("Play Local", True, (255,255,255))
            online_text = font.render("Play Online", True, (255,255,255))
            screen.blit(local_text, (local_rect.centerx-local_text.get_width()//2, local_rect.centery-local_text.get_height()//2))
            screen.blit(online_text, (online_rect.centerx-online_text.get_width()//2, online_rect.centery-online_text.get_height()//2))
            
            back_rect = pygame.Rect(WIDTH//2-100, HEIGHT-100, 200, 60)
            pygame.draw.rect(screen, (100,100,100), back_rect)
            back_text = font.render("Back", True, (255,255,255))
            screen.blit(back_text, (back_rect.centerx-back_text.get_width()//2, back_rect.centery-back_text.get_height()//2))
            
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if local_rect.collidepoint(event.pos):
                        # Go to local player count selection
                        while True:
                            screen.fill((30, 30, 30))
                            title = lobby_font.render("Survival Mode - Local Play", True, (255,255,255))
                            screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-180))
                            
                            subtitle = font.render("Select Number of Players:", True, (200,200,200))
                            screen.blit(subtitle, (WIDTH//2-subtitle.get_width()//2, HEIGHT//2-120))
                            
                            # Player count buttons
                            one_player_rect = pygame.Rect(WIDTH//2-300, HEIGHT//2-30, 180, 60)
                            two_player_rect = pygame.Rect(WIDTH//2-90, HEIGHT//2-30, 180, 60)
                            three_player_rect = pygame.Rect(WIDTH//2+120, HEIGHT//2-30, 180, 60)
                            
                            pygame.draw.rect(screen, (0,120,180), one_player_rect)
                            pygame.draw.rect(screen, (0,180,0), two_player_rect)
                            pygame.draw.rect(screen, (180,120,0), three_player_rect)
                            
                            one_text = font.render("1 Player", True, (255,255,255))
                            two_text = font.render("2 Players", True, (255,255,255))
                            three_text = font.render("3 Players", True, (255,255,255))
                            
                            screen.blit(one_text, (one_player_rect.centerx-one_text.get_width()//2, one_player_rect.centery-one_text.get_height()//2))
                            screen.blit(two_text, (two_player_rect.centerx-two_text.get_width()//2, two_player_rect.centery-two_text.get_height()//2))
                            screen.blit(three_text, (three_player_rect.centerx-three_text.get_width()//2, three_player_rect.centery-three_text.get_height()//2))
                            
                            local_back_rect = pygame.Rect(WIDTH//2-100, HEIGHT-100, 200, 60)
                            pygame.draw.rect(screen, (100,100,100), local_back_rect)
                            local_back_text = font.render("Back", True, (255,255,255))
                            screen.blit(local_back_text, (local_back_rect.centerx-local_back_text.get_width()//2, local_back_rect.centery-local_back_text.get_height()//2))
                            
                            pygame.display.flip()
                            for local_event in pygame.event.get():
                                if local_event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                if local_event.type == pygame.MOUSEBUTTONDOWN:
                                    if one_player_rect.collidepoint(local_event.pos):
                                        # 1 Player mode
                                        player1_name = get_player_name("Enter your name for Survival Mode:", HEIGHT//2)
                                        char_choices = character_select_single_player(2)  # 2 = survivor mode
                                        run_survival_mode(1, player1_name, "", "", char_choices, [], [])
                                        break
                                    if two_player_rect.collidepoint(local_event.pos):
                                        # 2 Player mode
                                        player1_name = get_player_name("Player 1, enter your name for Survival Mode:", HEIGHT//2-60)
                                        player2_name = get_player_name("Player 2, enter your name for Survival Mode:", HEIGHT//2+60)
                                        char_choices = character_select(2)  # 2 = survivor mode
                                        run_survival_mode(2, player1_name, player2_name, "", char_choices, [], [])
                                        break
                                    if three_player_rect.collidepoint(local_event.pos):
                                        # 3 Player mode
                                        player1_name = get_player_name("Player 1, enter your name for Survival Mode:", HEIGHT//2-90)
                                        player2_name = get_player_name("Player 2, enter your name for Survival Mode:", HEIGHT//2-30)
                                        player3_name = get_player_name("Player 3, enter your name for Survival Mode:", HEIGHT//2+30)
                                        char_choices = character_select_three_player(2)  # 2 = survivor mode
                                        run_survival_mode(3, player1_name, player2_name, player3_name, char_choices, [], [])
                                        break
                                    if local_back_rect.collidepoint(local_event.pos):
                                        break
                            else:
                                continue
                            break  # Return to local/online selection
                        break
                    elif online_rect.collidepoint(event.pos):
                        # Online mode for Survival
                        role = online_host_or_join()
                        if role == 'host':
                            # Host enters name BEFORE waiting for connection
                            player_name = get_player_name("Host: Enter your name:", HEIGHT//2)
                            
                            # Show waiting screen with IP
                            local_ip = get_local_ip()
                            
                            screen.fill((30, 30, 30))
                            wait_text = lobby_font.render("Waiting for player to join...", True, (255, 255, 0))
                            screen.blit(wait_text, (WIDTH//2 - wait_text.get_width()//2, HEIGHT//2 - 100))
                            ip_text = font.render(f"Your IP: {local_ip}", True, (255, 255, 255))
                            screen.blit(ip_text, (WIDTH//2 - ip_text.get_width()//2, HEIGHT//2 - 30))
                            port_text = font.render("Port: 50007", True, (255, 255, 255))
                            screen.blit(port_text, (WIDTH//2 - port_text.get_width()//2, HEIGHT//2 + 10))
                            cancel_text = name_font.render("Press ESC to cancel", True, (150, 150, 150))
                            screen.blit(cancel_text, (WIDTH//2 - cancel_text.get_width()//2, HEIGHT//2 + 60))
                            pygame.display.flip()
                            
                            try:
                                net = NetworkHost()
                                # Wait for connection with cancel option
                                waiting = True
                                while waiting and not net.conn:
                                    for ev in pygame.event.get():
                                        if ev.type == pygame.QUIT:
                                            net.close()
                                            pygame.quit()
                                            sys.exit()
                                        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                                            net.close()
                                            waiting = False
                                            continue
                                    pygame.time.wait(100)
                                
                                if net.conn:
                                    player1_name = get_player_name("Enter your name:", HEIGHT//2)
                                    char_choices = character_select_single_player(2)
                                    # Simplified online - just play locally for now
                                    run_survival_mode(1, player1_name, "", "", char_choices, [], [])
                                    net.close()
                            except Exception as e:
                                screen.fill((30, 30, 30))
                                error_text = font.render(f"Connection error: {str(e)}", True, (255, 0, 0))
                                screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
                                pygame.display.flip()
                                pygame.time.wait(2000)
                        elif role == 'join':
                            host_ip = get_ip_address()
                            if host_ip:
                                screen.fill((30, 30, 30))
                                conn_text = lobby_font.render("Connecting...", True, (255, 255, 0))
                                screen.blit(conn_text, (WIDTH//2 - conn_text.get_width()//2, HEIGHT//2))
                                pygame.display.flip()
                                
                                try:
                                    net = NetworkClient(host_ip)
                                    player_name = get_player_name("Enter your name:", HEIGHT//2)
                                    char_choices = character_select_single_player(2)
                                    # Simplified online - just play locally for now
                                    run_survival_mode(1, player_name, "", "", char_choices, [], [])
                                    net.close()
                                except Exception as e:
                                    screen.fill((30, 30, 30))
                                    error_text = font.render(f"Connection error: {str(e)}", True, (255, 0, 0))
                                    screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
                                    pygame.display.flip()
                                    pygame.time.wait(2000)
                        break
                    if back_rect.collidepoint(event.pos):
                        break
            else:
                continue
            break  # Always return to main menu after game ends
    elif mode == 3:
        # Makka Pakka Mode - Face Washing Game
        while True:
            screen.fill((30, 30, 30))
            title = lobby_font.render("Makka Pakka Mode", True, (255, 215, 0))
            screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-150))
            
            subtitle = font.render("Wash faces and steal them from your opponent!", True, (200, 200, 200))
            screen.blit(subtitle, (WIDTH//2-subtitle.get_width()//2, HEIGHT//2-100))
            
            # Show instructions
            instr1 = name_font.render("Player 1: WASD to move, SPACE to wash (RED)", True, (255, 0, 0))
            instr2 = name_font.render("Player 2: Arrow Keys to move, RIGHT SHIFT to wash (BLUE)", True, (0, 0, 255))
            instr3 = name_font.render("Wash green faces OR steal your opponent's colored faces!", True, (255, 255, 0))
            instr4 = name_font.render("Press wash button 10 times near any face to claim it!", True, (150, 255, 150))
            screen.blit(instr1, (WIDTH//2-instr1.get_width()//2, HEIGHT//2-60))
            screen.blit(instr2, (WIDTH//2-instr2.get_width()//2, HEIGHT//2-30))
            screen.blit(instr3, (WIDTH//2-instr3.get_width()//2, HEIGHT//2))
            screen.blit(instr4, (WIDTH//2-instr4.get_width()//2, HEIGHT//2+30))
            
            # Start button
            start_rect = pygame.Rect(WIDTH//2-100, HEIGHT//2+70, 200, 60)
            pygame.draw.rect(screen, (0, 180, 0), start_rect)
            start_text = font.render("Start Game", True, (255, 255, 255))
            screen.blit(start_text, (start_rect.centerx-start_text.get_width()//2, start_rect.centery-start_text.get_height()//2))
            
            # Back button
            back_rect = pygame.Rect(WIDTH//2-100, HEIGHT-100, 200, 60)
            pygame.draw.rect(screen, (100, 100, 100), back_rect)
            back_text = font.render("Back", True, (255, 255, 255))
            screen.blit(back_text, (back_rect.centerx-back_text.get_width()//2, back_rect.centery-back_text.get_height()//2))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_rect.collidepoint(event.pos):
                        # Get player names and start
                        player1_name = get_player_name("Player 1, enter your name:", HEIGHT//2 - 120)
                        player2_name = get_player_name("Player 2, enter your name:", HEIGHT//2 + 40)
                        result = run_makka_pakka_mode(player1_name, player2_name)
                        if result == 'lobby':
                            break
                    if back_rect.collidepoint(event.pos):
                        break
            else:
                continue
            break
    elif mode == 4:
        # Escape Mom Horror Mode
        while True:
            screen.fill((20, 20, 30))
            title = lobby_font.render("ESCAPE MOM MODE", True, (255, 50, 50))
            screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-180))
            
            warning = font.render("WARNING: SCARY CONTENT!", True, (255, 100, 100))
            screen.blit(warning, (WIDTH//2-warning.get_width()//2, HEIGHT//2-130))
            
            subtitle = font.render("Run through dark corridors and escape from an angry mother!", True, (200, 200, 200))
            screen.blit(subtitle, (WIDTH//2-subtitle.get_width()//2, HEIGHT//2-90))
            
            # Show instructions
            instr1 = name_font.render("You are a child running through dark hallways", True, (180, 180, 180))
            instr2 = name_font.render("She's hunting you but you can't see her in the dark...", True, (180, 180, 180))
            instr3 = name_font.render("Use WASD or Arrow Keys to run and escape!", True, (255, 255, 150))
            instr4 = name_font.render("Survive as long as you can!", True, (255, 150, 150))
            screen.blit(instr1, (WIDTH//2-instr1.get_width()//2, HEIGHT//2-40))
            screen.blit(instr2, (WIDTH//2-instr2.get_width()//2, HEIGHT//2-10))
            screen.blit(instr3, (WIDTH//2-instr3.get_width()//2, HEIGHT//2+20))
            screen.blit(instr4, (WIDTH//2-instr4.get_width()//2, HEIGHT//2+50))
            
            # Start button
            start_rect = pygame.Rect(WIDTH//2-100, HEIGHT//2+90, 200, 60)
            pygame.draw.rect(screen, (150, 0, 0), start_rect)
            start_text = font.render("Start Game", True, (255, 255, 255))
            screen.blit(start_text, (start_rect.centerx-start_text.get_width()//2, start_rect.centery-start_text.get_height()//2))
            
            # Back button
            back_rect = pygame.Rect(WIDTH//2-100, HEIGHT-100, 200, 60)
            pygame.draw.rect(screen, (100, 100, 100), back_rect)
            back_text = font.render("Back", True, (255, 255, 255))
            screen.blit(back_text, (back_rect.centerx-back_text.get_width()//2, back_rect.centery-back_text.get_height()//2))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_rect.collidepoint(event.pos):
                        result = run_escape_mom_mode()
                        if result == 'lobby':
                            break
                    if back_rect.collidepoint(event.pos):
                        break
            else:
                continue
            break
    elif mode == 3:
        # Makka Pakka Mode - Face Washing Game - Show Play Local / Play Online
        while True:
            screen.fill((30, 30, 30))
            title = lobby_font.render("Makka Pakka Mode", True, (255, 215, 0))
            screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-180))
            
            subtitle = font.render("Wash faces and steal them from your opponent!", True, (200, 200, 200))
            screen.blit(subtitle, (WIDTH//2-subtitle.get_width()//2, HEIGHT//2-130))
            
            local_rect = pygame.Rect(WIDTH//2-220, HEIGHT//2-40, 200, 80)
            online_rect = pygame.Rect(WIDTH//2+20, HEIGHT//2-40, 200, 80)
            pygame.draw.rect(screen, (0,180,0), local_rect)
            pygame.draw.rect(screen, (0,120,255), online_rect)
            local_text = font.render("Play Local", True, (255,255,255))
            online_text = font.render("Play Online", True, (255,255,255))
            screen.blit(local_text, (local_rect.centerx-local_text.get_width()//2, local_rect.centery-local_text.get_height()//2))
            screen.blit(online_text, (online_rect.centerx-online_text.get_width()//2, online_rect.centery-online_text.get_height()//2))
            
            back_rect = pygame.Rect(WIDTH//2-100, HEIGHT-100, 200, 60)
            pygame.draw.rect(screen, (100,100,100), back_rect)
            back_text = font.render("Back", True, (255,255,255))
            screen.blit(back_text, (back_rect.centerx-back_text.get_width()//2, back_rect.centery-back_text.get_height()//2))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if local_rect.collidepoint(event.pos):
                        # Local play
                        player1_name = get_player_name("Player 1, enter your name:", HEIGHT//2 - 120)
                        player2_name = get_player_name("Player 2, enter your name:", HEIGHT//2 + 40)
                        result = run_makka_pakka_mode(player1_name, player2_name)
                        if result == 'lobby':
                            break
                    if online_rect.collidepoint(event.pos):
                        # Online mode for Makka Pakka
                        role = online_host_or_join()
                        if role == 'host':
                            # Host enters name BEFORE waiting for connection
                            player_name = get_player_name("Host: Enter your name:", HEIGHT//2)
                            
                            # Show waiting screen with IP
                            local_ip = get_local_ip()
                            
                            screen.fill((30, 30, 30))
                            wait_text = lobby_font.render("Waiting for player to join...", True, (255, 255, 0))
                            screen.blit(wait_text, (WIDTH//2 - wait_text.get_width()//2, HEIGHT//2 - 100))
                            ip_text = font.render(f"Your IP: {local_ip}", True, (255, 255, 255))
                            screen.blit(ip_text, (WIDTH//2 - ip_text.get_width()//2, HEIGHT//2 - 30))
                            port_text = font.render("Port: 50007", True, (255, 255, 255))
                            screen.blit(port_text, (WIDTH//2 - port_text.get_width()//2, HEIGHT//2 + 10))
                            cancel_text = name_font.render("Press ESC to cancel", True, (150, 150, 150))
                            screen.blit(cancel_text, (WIDTH//2 - cancel_text.get_width()//2, HEIGHT//2 + 60))
                            pygame.display.flip()
                            
                            try:
                                net = NetworkHost()
                                # Wait for connection with cancel option
                                waiting = True
                                while waiting and not net.conn:
                                    for ev in pygame.event.get():
                                        if ev.type == pygame.QUIT:
                                            net.close()
                                            pygame.quit()
                                            sys.exit()
                                        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                                            net.close()
                                            waiting = False
                                            continue
                                    pygame.time.wait(100)
                                
                                if net.conn:
                                    # Simplified online - just play locally for now
                                    run_makka_pakka_mode(player_name, "Opponent")
                                    net.close()
                            except Exception as e:
                                screen.fill((30, 30, 30))
                                error_text = font.render(f"Connection error: {str(e)}", True, (255, 0, 0))
                                screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
                                pygame.display.flip()
                                pygame.time.wait(2000)
                        elif role == 'join':
                            host_ip = get_ip_address()
                            if host_ip:
                                screen.fill((30, 30, 30))
                                conn_text = lobby_font.render("Connecting...", True, (255, 255, 0))
                                screen.blit(conn_text, (WIDTH//2 - conn_text.get_width()//2, HEIGHT//2))
                                pygame.display.flip()
                                
                                try:
                                    net = NetworkClient(host_ip)
                                    player_name = get_player_name("Enter your name:", HEIGHT//2)
                                    # Simplified online - just play locally for now
                                    run_makka_pakka_mode("Opponent", player_name)
                                    net.close()
                                except Exception as e:
                                    screen.fill((30, 30, 30))
                                    error_text = font.render(f"Connection error: {str(e)}", True, (255, 0, 0))
                                    screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
                                    pygame.display.flip()
                                    pygame.time.wait(2000)
                        break
                    if back_rect.collidepoint(event.pos):
                        break
            else:
                continue
            break
    elif mode == 5:
        # 3D Adventure Mode
        adventure_3d_mode()
        # Capture the Flag Mode - Show Play Local / Play Online
        while True:
            screen.fill((30, 60, 30))
            title = lobby_font.render("CAPTURE THE FLAG", True, (255, 215, 0))
            screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-180))
            
            subtitle = font.render("Steal the enemy flag and bring it to your base!", True, (200, 200, 200))
            screen.blit(subtitle, (WIDTH//2-subtitle.get_width()//2, HEIGHT//2-130))
            
            local_rect = pygame.Rect(WIDTH//2-220, HEIGHT//2-40, 200, 80)
            online_rect = pygame.Rect(WIDTH//2+20, HEIGHT//2-40, 200, 80)
            pygame.draw.rect(screen, (0,180,0), local_rect)
            pygame.draw.rect(screen, (0,120,255), online_rect)
            local_text = font.render("Play Local", True, (255,255,255))
            online_text = font.render("Play Online", True, (255,255,255))
            screen.blit(local_text, (local_rect.centerx-local_text.get_width()//2, local_rect.centery-local_text.get_height()//2))
            screen.blit(online_text, (online_rect.centerx-online_text.get_width()//2, online_rect.centery-online_text.get_height()//2))
            
            back_rect = pygame.Rect(WIDTH//2-100, HEIGHT-100, 200, 60)
            pygame.draw.rect(screen, (100,100,100), back_rect)
            back_text = font.render("Back", True, (255,255,255))
            screen.blit(back_text, (back_rect.centerx-back_text.get_width()//2, back_rect.centery-back_text.get_height()//2))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if local_rect.collidepoint(event.pos):
                        # Local play
                        player1_name = get_player_name("Player 1, enter your name:", HEIGHT//2 - 120)
                        player2_name = get_player_name("Player 2, enter your name:", HEIGHT//2 + 40)
                        result = run_capture_the_flag(player1_name, player2_name)
                        if result == 'lobby':
                            break
                    if online_rect.collidepoint(event.pos):
                        # Online mode for Capture the Flag
                        role = online_host_or_join()
                        if role == 'host':
                            # Host enters name BEFORE waiting for connection
                            player_name = get_player_name("Host: Enter your name:", HEIGHT//2)
                            
                            # Show waiting screen with IP
                            local_ip = get_local_ip()
                            
                            screen.fill((30, 30, 30))
                            wait_text = lobby_font.render("Waiting for player to join...", True, (255, 255, 0))
                            screen.blit(wait_text, (WIDTH//2 - wait_text.get_width()//2, HEIGHT//2 - 100))
                            ip_text = font.render(f"Your IP: {local_ip}", True, (255, 255, 255))
                            screen.blit(ip_text, (WIDTH//2 - ip_text.get_width()//2, HEIGHT//2 - 30))
                            port_text = font.render("Port: 50007", True, (255, 255, 255))
                            screen.blit(port_text, (WIDTH//2 - port_text.get_width()//2, HEIGHT//2 + 10))
                            cancel_text = name_font.render("Press ESC to cancel", True, (150, 150, 150))
                            screen.blit(cancel_text, (WIDTH//2 - cancel_text.get_width()//2, HEIGHT//2 + 60))
                            pygame.display.flip()
                            
                            try:
                                net = NetworkHost()
                                # Wait for connection with cancel option
                                waiting = True
                                while waiting and not net.conn:
                                    for ev in pygame.event.get():
                                        if ev.type == pygame.QUIT:
                                            net.close()
                                            pygame.quit()
                                            sys.exit()
                                        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                                            net.close()
                                            waiting = False
                                            continue
                                    pygame.time.wait(100)
                                
                                if net.conn:
                                    # Simplified online - just play locally for now
                                    run_capture_the_flag(player_name, "Opponent")
                                    net.close()
                            except Exception as e:
                                screen.fill((30, 30, 30))
                                error_text = font.render(f"Connection error: {str(e)}", True, (255, 0, 0))
                                screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
                                pygame.display.flip()
                                pygame.time.wait(2000)
                        elif role == 'join':
                            host_ip = get_ip_address()
                            if host_ip:
                                screen.fill((30, 30, 30))
                                conn_text = lobby_font.render("Connecting...", True, (255, 255, 0))
                                screen.blit(conn_text, (WIDTH//2 - conn_text.get_width()//2, HEIGHT//2))
                                pygame.display.flip()
                                
                                try:
                                    net = NetworkClient(host_ip)
                                    player_name = get_player_name("Enter your name:", HEIGHT//2)
                                    # Simplified online - just play locally for now
                                    run_capture_the_flag("Opponent", player_name)
                                    net.close()
                                except Exception as e:
                                    screen.fill((30, 30, 30))
                                    error_text = font.render(f"Connection error: {str(e)}", True, (255, 0, 0))
                                    screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
                                    pygame.display.flip()
                                    pygame.time.wait(2000)
                        break
                    if back_rect.collidepoint(event.pos):
                        break
            else:
                continue
            break











