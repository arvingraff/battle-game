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

# Network scanning and quick match imports
import socket
import threading

pygame.init()

# Session-based purchases (resets each time game starts)
session_purchases = {'relax_mode': False, 'shop_unlocked': False}

# SAVE/LOAD FUNCTIONS FOR PERSISTENCE
def save_secret_hack():
    """Save secret hack progress to a file"""
    try:
        save_path = os.path.join(os.path.expanduser('~'), '.battlegame_secrets.json')
        with open(save_path, 'w') as f:
            json.dump(secret_hack, f)
    except:
        pass  # Fail silently if can't save

def load_secret_hack():
    """Load secret hack progress from file"""
    try:
        save_path = os.path.join(os.path.expanduser('~'), '.battlegame_secrets.json')
        if os.path.exists(save_path):
            with open(save_path, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

# SECRET HACK TRACKER - Load saved progress or start fresh
saved_secrets = load_secret_hack()
secret_hack = {
    'sheep_mode_played': saved_secrets.get('sheep_mode_played', False),
    'whoppa_gang_entered': saved_secrets.get('whoppa_gang_entered', False),
    'music_still_playing': False,  # Don't persist music
    'skibidi_triggered': saved_secrets.get('skibidi_triggered', False),
    'wolf_ate_buttons': False,  # Don't persist wolf state
    'grass_mode_unlocked': False,  # Reset each session - must do hack sequence!
    'combine_mode_unlocked': False, # Reset each session - must do hack sequence!
    'entered_battle_after_music': saved_secrets.get('entered_battle_after_music', False),
    'everything_restored': False,  # Don't persist restoration
    'became_human': False,  # Don't persist - resets each session!
    'became_italian': False,  # Secret transformation - press 67 when human!
    'god_mode_unlocked': saved_secrets.get('god_mode_unlocked', False),  # PERMANENT REWARD for completing Combine Mode!
    'final_mode_unlocked': True,  # THE ULTIMATE MODE - Unlocked for testing 'arvin' code!
    'post_credits_scene_unlocked': False, # New 3D horror area after credits
    'explosion_triggered': False,  # Explosion animation state
}

# Key buffer for main menu hack detection
menu_key_buffer = ""

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

def scan_for_hosts(timeout=2):
    """Scan local network for available game hosts"""
    import time
    found_hosts = []
    local_ip = get_local_ip()
    if not local_ip:
        return []
    
    # Get network prefix (e.g., 192.168.1.)
    ip_parts = local_ip.split('.')
    network_prefix = '.'.join(ip_parts[:3]) + '.'
    
    def check_host(ip):
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.settimeout(0.5)
            result = test_sock.connect_ex((ip, 50007))
            test_sock.close()
            if result == 0:
                found_hosts.append(ip)
        except:
            pass
    
    # Scan common IP range (last octet 1-254)
    threads = []
    for i in range(1, 255):
        ip = network_prefix + str(i)
        if ip != local_ip:  # Don't scan ourselves
            thread = threading.Thread(target=check_host, args=(ip,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
    
    # Wait for scan to complete
    start_time = time.time()
    for thread in threads:
        remaining = timeout - (time.time() - start_time)
        if remaining > 0:
            thread.join(timeout=remaining)
    
    return found_hosts

def quick_match_flow(mode_type=0):
    """Quick match: auto-connect by scanning for hosts, or becoming a host if none found"""
    import time
    # Show searching screen
    screen.fill((30, 30, 30))
    search_text = lobby_font.render("Quick Match", True, (255, 215, 0))
    screen.blit(search_text, (WIDTH//2 - search_text.get_width()//2, HEIGHT//2 - 120))
    
    status_text = font.render("Searching for available players...", True, (255, 255, 255))
    screen.blit(status_text, (WIDTH//2 - status_text.get_width()//2, HEIGHT//2 - 30))
    
    cancel_text = name_font.render("Press ESC to cancel", True, (150, 150, 150))
    screen.blit(cancel_text, (WIDTH//2 - cancel_text.get_width()//2, HEIGHT//2 + 60))
    
    pygame.display.flip()
    
    # Check for cancel during scan
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return None
    
    # Scan for hosts
    found_hosts = scan_for_hosts(timeout=3)
    
    if found_hosts:
        # Found a host, try to join
        host_ip = found_hosts[0]  # Connect to first available host
        
        screen.fill((30, 30, 30))
        conn_text = lobby_font.render(f"Found player! Connecting...", True, (0, 255, 0))
        screen.blit(conn_text, (WIDTH//2 - conn_text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        
        try:
            net = NetworkClient(host_ip)
            pygame.time.wait(500)
            
            # Send initial connection packet so host detects us
            net.send({'type': 'client_ready', 'status': 'connected'})
            pygame.time.wait(200)
            
            # Client enters name (synchronized with host)
            player_name = get_player_name_online("Enter your name:", HEIGHT//2, net, False)
            
            my_char, opp_char = online_character_select_and_countdown(net, False, mode_type)
            if my_char is not None and opp_char is not None:
                char_choices = [opp_char, my_char]
                result = run_game_with_upgrades("Opponent", player_name, char_choices, 0, 0, 0, 0, 0, 0, mode=mode_type, net=net, is_host=False)
            net.close()
            return 'played'
        except Exception as e:
            screen.fill((30, 30, 30))
            error_text = font.render(f"Connection failed: {str(e)}", True, (255, 0, 0))
            screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
            retry_text = name_font.render("Becoming host instead...", True, (255, 255, 0))
            screen.blit(retry_text, (WIDTH//2 - retry_text.get_width()//2, HEIGHT//2 + 50))
            pygame.display.flip()
            pygame.time.wait(1500)
            # Fall through to hosting
    
    # No host found, become a host
    local_ip = get_local_ip()
    
    screen.fill((30, 30, 30))
    host_text = lobby_font.render("No players found - Hosting game...", True, (255, 215, 0))
    screen.blit(host_text, (WIDTH//2 - host_text.get_width()//2, HEIGHT//2 - 100))
    ip_text = font.render(f"Your IP: {local_ip}", True, (255, 255, 255))
    screen.blit(ip_text, (WIDTH//2 - ip_text.get_width()//2, HEIGHT//2))
    wait_text = name_font.render("Waiting for someone to join...", True, (200, 200, 200))
    screen.blit(wait_text, (WIDTH//2 - wait_text.get_width()//2, HEIGHT//2 + 50))
    cancel_text2 = name_font.render("Press ESC to cancel", True, (150, 150, 150))
    screen.blit(cancel_text2, (WIDTH//2 - cancel_text2.get_width()//2, HEIGHT//2 + 100))
    pygame.display.flip()
    
    try:
        net = NetworkHost()
        # Wait for connection with cancel option
        waiting = True
        connection_detected = False
        start_wait = time.time()
        
        # For UDP hosts, wait for first data packet to detect connection
        while waiting and not connection_detected:
            # Redraw waiting screen
            screen.fill((30, 30, 30))
            host_text = lobby_font.render("No players found - Hosting game...", True, (255, 215, 0))
            screen.blit(host_text, (WIDTH//2 - host_text.get_width()//2, HEIGHT//2 - 100))
            ip_text = font.render(f"Your IP: {local_ip}", True, (255, 255, 255))
            screen.blit(ip_text, (WIDTH//2 - ip_text.get_width()//2, HEIGHT//2))
            wait_text = name_font.render("Waiting for someone to join...", True, (200, 200, 200))
            screen.blit(wait_text, (WIDTH//2 - wait_text.get_width()//2, HEIGHT//2 + 50))
            cancel_text2 = name_font.render("Press ESC to cancel", True, (150, 150, 150))
            screen.blit(cancel_text2, (WIDTH//2 - cancel_text2.get_width()//2, HEIGHT//2 + 100))
            pygame.display.flip()
            
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    net.close()
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    net.close()
                    return None
            
            # Check for connection (TCP uses net.conn, UDP uses client_addr)
            if net.use_udp:
                # For UDP, try to receive data to detect client
                data = net.recv()
                if data or net.client_addr:
                    connection_detected = True
            else:
                # Pretty gradient background (clamped RGB)
                for y in range(HEIGHT):
                    shade = int(200 + 55 * math.sin(y * 0.005))
                    r = max(0, min(255, shade))
                    g = max(0, min(255, shade - 20))
                    b = max(0, min(255, shade + 20))
                    pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
                # Pretty gradient background (clamp channels to valid 0-255 values)
                for y in range(HEIGHT):
                    shade = int(200 + 55 * math.sin(y * 0.005))
                    r = max(0, min(255, shade))
                    g = max(0, min(255, shade - 20))
                    b = max(0, min(255, shade + 20))
                    pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
                # For TCP, check if connection exists
                if net.conn:
                    connection_detected = True
            
            pygame.time.wait(100)
        
        if connection_detected:
            # Show connection successful message
            screen.fill((30, 30, 30))
            connected_text = lobby_font.render("Player Connected! Starting...", True, (0, 255, 0))
            screen.blit(connected_text, (WIDTH//2 - connected_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(1000)
            
            # Host enters name (synchronized with client)
            player_name = get_player_name_online("Enter your name:", HEIGHT//2, net, True)
            
            my_char, opp_char = online_character_select_and_countdown(net, True, mode_type)
            if my_char is not None and opp_char is not None:
                char_choices = [my_char, opp_char]
                result = run_game_with_upgrades(player_name, "Opponent", char_choices, 0, 0, 0, 0, 0, 0, mode=mode_type, net=net, is_host=True)
            net.close()
            return 'played'
    except Exception as e:
        screen.fill((30, 30, 30))
        error_text = font.render(f"Hosting error: {str(e)}", True, (255, 0, 0))
        screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(2000)
        return None

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


def post_credits_scene(screen):
    """
    POST-CREDITS SCENE - A creepy 3D exploration area
    Triggered after 'arvin' credits sequence.
    """
    
    # STOP ALL MUSIC - silence is terrifying
    pygame.mixer.music.stop()
    
    # Setup 3D variables
    player_pos = {'x': 0, 'y': 0, 'z': 0}
    player_angle = 0
    
    # Generate some creepy pillars
    pillars = []
    for _ in range(50):
        pillars.append({
            'x': random.uniform(-1000, 1000),
            'z': random.uniform(-1000, 1000),
            'w': random.uniform(20, 100),
            'h': random.uniform(100, 400),
            'color': (random.randint(10, 50), 0, 0) # Dark red
        })
        
    running = True
    clock = pygame.time.Clock()
    jumpscare_triggered = False
    jumpscare_timer = 0
    step_timer = 0
    
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Jumpscare logic
        if jumpscare_triggered:
            jumpscare_timer += dt
            if jumpscare_timer > 3.0:
                return 'jumpscare' # Exit back to menu (or loop)
            
            # Draw jumpscare
            jumpscare_timer += dt
            if jumpscare_timer > 3.0:
                running = False # Exit back to menu
            
            # Draw jumpscare
            screen.fill((0, 0, 0))
            
            # Ultra terrifying face with multiple layers
            flicker = int(jumpscare_timer * 20) % 2 == 0
            
            if flicker:
                # Main giant face - blood red with veins
                pygame.draw.circle(screen, (180, 0, 0), (WIDTH//2, HEIGHT//2), 400)
                pygame.draw.circle(screen, (255, 0, 0), (WIDTH//2, HEIGHT//2), 380)
                pygame.draw.circle(screen, (200, 0, 0), (WIDTH//2, HEIGHT//2), 360)
                
                # Horrible glowing eyes with multiple rings
                for i in range(5):
                    eye_size = 80 - i*15
                    eye_color = (255 - i*50, 255 - i*50, 255 - i*50)
                    pygame.draw.circle(screen, eye_color, (WIDTH//2 - 120, HEIGHT//2 - 60), eye_size)
                    pygame.draw.circle(screen, eye_color, (WIDTH//2 + 120, HEIGHT//2 - 60), eye_size)
                
                # Pitch black pupils that stare into your soul
                pygame.draw.circle(screen, (0, 0, 0), (WIDTH//2 - 120, HEIGHT//2 - 60), 40)
                pygame.draw.circle(screen, (0, 0, 0), (WIDTH//2 + 120, HEIGHT//2 - 60), 40)
                
                # Bloodshot veins in eyes
                for _ in range(10):
                    vein_start_x = WIDTH//2 - 120 + random.randint(-60, 60)
                    vein_start_y = HEIGHT//2 - 60 + random.randint(-60, 60)
                    vein_end_x = WIDTH//2 - 120 + random.randint(-80, 80)
                    vein_end_y = HEIGHT//2 - 60 + random.randint(-80, 80)
                    pygame.draw.line(screen, (150, 0, 0), (vein_start_x, vein_start_y), (vein_end_x, vein_end_y), 2)
                    
                    vein_start_x = WIDTH//2 + 120 + random.randint(-60, 60)
                    vein_start_y = HEIGHT//2 - 60 + random.randint(-60, 60)
                    vein_end_x = WIDTH//2 + 120 + random.randint(-80, 80)
                    vein_end_y = HEIGHT//2 - 60 + random.randint(-80, 80)
                    pygame.draw.line(screen, (150, 0, 0), (vein_start_x, vein_start_y), (vein_end_x, vein_end_y), 2)
                
                # Horrifying jagged mouth - multiple layers
                mouth_points = [
                    (WIDTH//2 - 150, HEIGHT//2 + 80),
                    (WIDTH//2 - 100, HEIGHT//2 + 120),
                    (WIDTH//2 - 50, HEIGHT//2 + 100),
                    (WIDTH//2, HEIGHT//2 + 130),
                    (WIDTH//2 + 50, HEIGHT//2 + 100),
                    (WIDTH//2 + 100, HEIGHT//2 + 120),
                    (WIDTH//2 + 150, HEIGHT//2 + 80),
                    (WIDTH//2 + 100, HEIGHT//2 + 60),
                    (WIDTH//2, HEIGHT//2 + 70),
                    (WIDTH//2 - 100, HEIGHT//2 + 60),
                ]
                pygame.draw.polygon(screen, (0, 0, 0), mouth_points)
                pygame.draw.polygon(screen, (100, 0, 0), mouth_points, 5)
                
                # Dripping effect
                for i in range(5):
                    drip_x = WIDTH//2 - 150 + i * 75
                    drip_y = HEIGHT//2 + 130 + random.randint(0, 50)
                    pygame.draw.circle(screen, (150, 0, 0), (drip_x, drip_y), 5)
                
                # Sharp teeth
                for i in range(10):
                    tooth_x = WIDTH//2 - 140 + i * 30
                    tooth_points = [
                        (tooth_x, HEIGHT//2 + 80),
                        (tooth_x + 10, HEIGHT//2 + 110),
                        (tooth_x + 20, HEIGHT//2 + 80)
                    ]
                    pygame.draw.polygon(screen, (255, 255, 255), tooth_points)
                
                # Distorted SCREAMING text with glitch effect
                s_font = pygame.font.Font(None, 250)
                text = s_font.render("FOUND YOU!", True, (255, 255, 255))
                
                # Glitch effect - multiple overlapping texts
                screen.blit(text, (WIDTH//2 - text.get_width()//2 + random.randint(-10, 10), HEIGHT//2 + 200 + random.randint(-5, 5)))
                text_red = s_font.render("FOUND YOU!", True, (255, 0, 0))
                screen.blit(text_red, (WIDTH//2 - text_red.get_width()//2 + random.randint(-8, 8), HEIGHT//2 + 200 + random.randint(-5, 5)))
                
                # Additional scary text
                small_font = pygame.font.Font(None, 80)
                msgs = ["YOU CAN'T ESCAPE", "I SEE YOU", "FOREVER", "NO WAY OUT"]
                for idx, msg in enumerate(msgs):
                    angle = (jumpscare_timer * 50 + idx * 90) % 360
                    x = WIDTH//2 + int(math.cos(math.radians(angle)) * 400)
                    y = HEIGHT//2 + int(math.sin(math.radians(angle)) * 300)
                    msg_surf = small_font.render(msg, True, (200, 0, 0))
                    screen.blit(msg_surf, (x - msg_surf.get_width()//2, y))
                
                # Play scary sound if just triggered
                if jumpscare_timer < 0.1:
                    try:
                        pygame.mixer.Sound("scary-scream.mp3").play()
                    except:
                        pass
                        
            pygame.display.flip()
            continue
            
        # Normal game logic
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEMOTION:
                dx, dy = event.rel
                player_angle += dx * 0.002
                
        # Movement
        keys = pygame.key.get_pressed()
        speed = 5
        moved = False
        
        if keys[pygame.K_w]:
            player_pos['x'] += math.sin(player_angle) * speed
            player_pos['z'] += math.cos(player_angle) * speed
            moved = True
        if keys[pygame.K_s]:
            player_pos['x'] -= math.sin(player_angle) * speed
            player_pos['z'] -= math.cos(player_angle) * speed
            moved = True
        if keys[pygame.K_a]:
            player_pos['x'] -= math.cos(player_angle) * speed
            player_pos['z'] += math.sin(player_angle) * speed
            moved = True
        if keys[pygame.K_d]:
            player_pos['x'] += math.cos(player_angle) * speed
            player_pos['z'] -= math.sin(player_angle) * speed
            moved = True
            
        # Walking sound / footsteps effect
        if moved:
            step_timer += dt
            if step_timer > 0.5:
                step_timer = 0
                # Could play footstep sound here
        
        # Random jumpscare trigger (or if you walk too far)
        if random.random() < 0.001 or (abs(player_pos['x']) > 800 or abs(player_pos['z']) > 800):
             jumpscare_triggered = True
             
        # Rendering
        screen.fill((15, 15, 20)) # Slightly lighter so you can see a bit more
        
        # Floor grid - 3D projection
        for i in range(-10, 11):
            # Simple line drawing perspective isn't trivial without a full engine, 
            # let's stick to object rendering sorted by depth
            pass
            
        # Draw pillars relative to player
        objects_to_draw = []
        
        for p in pillars:
            # Transform relative to player
            rx = p['x'] - player_pos['x']
            rz = p['z'] - player_pos['z']
            
            # Rotate around player
            tx = rx * math.cos(-player_angle) - rz * math.sin(-player_angle)
            tz = rx * math.sin(-player_angle) + rz * math.cos(-player_angle)
            
            if tz > 10: # Only draw in front of camera
                proj_scale = 400 / tz
                screen_x = WIDTH // 2 + tx * proj_scale
                screen_y = HEIGHT // 2
                
                w = p['w'] * proj_scale
                h = p['h'] * proj_scale
                
                dist = math.sqrt(rx*rx + rz*rz)
                shade = max(0, min(255, 255 - dist/4))
                color = (shade * (p['color'][0]/255), 0, 0)
                
                objects_to_draw.append({
                    'depth': tz,
                    'rect': (screen_x - w/2, screen_y - h/2, w, h),
                    'color': color
                })
                
        # Sort by depth (painters algorithm)
        objects_to_draw.sort(key=lambda o: o['depth'], reverse=True)
        
        for o in objects_to_draw:
            pygame.draw.rect(screen, o['color'], o['rect'])
            
        # Fog/Darkness overlay
        # fade = pygame.Surface((WIDTH, HEIGHT))
        # fade.fill((0,0,0))
        # fade.set_alpha(50) 
        # screen.blit(fade, (0,0))

        # Crosshair
        pygame.draw.circle(screen, (50, 50, 50), (WIDTH//2, HEIGHT//2), 2)
        
        # Instructions
        if not jumpscare_triggered:
            font = pygame.font.Font(None, 30)
            text = font.render("Where am I? (WASD to move)", True, (100, 100, 100))
            screen.blit(text, (20, HEIGHT - 50))

        pygame.display.flip()
        
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    
def credits_sequence(screen):
    """
    ULTIMATE CREDITS SEQUENCE
    Triggered by code 'arvin' after unlocking final mode (6776).
    Movie-like credits showing the creator and story.
    """
    import time
    
    # Store previous font scaling
    old_mode = screen.get_size()
    
    # Fade out
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill((0, 0, 0))
    for alpha in range(0, 255, 5):
        fade.set_alpha(alpha)
        screen.blit(fade, (0, 0))
        pygame.display.flip()
        pygame.time.wait(10)
        
    # Credits content
    lines = [
        ("EXECUTIVE PRODUCER", 60, (255, 215, 0)),
        ("ARVIN GREENBERG GRAFF", 90, (255, 255, 255)),
        ("", 40, (0,0,0)), 
        ("CREATED BY", 50, (200, 200, 200)),
        ("ARVIN", 80, (0, 255, 255)),
        ("", 40, (0,0,0)),
        ("LEAD PROGRAMMER", 50, (200, 200, 200)),
        ("ARVIN", 70, (0, 255, 0)),
        ("", 40, (0,0,0)),
        ("STORY & CONCEPT", 50, (200, 200, 200)),
        ("ARVIN", 70, (255, 100, 100)),
        ("", 80, (0,0,0)),
        ("SPECIAL THANKS TO", 50, (200, 200, 200)),
        ("MOM & DAD", 70, (255, 0, 255)),
        ("", 80, (0,0,0)),
        ("BATTLEGAME DELUXE", 100, (255, 215, 0)),
        ("THE ULTIMATE EDITION", 60, (150, 150, 150)),
        ("", 150, (0,0,0)),
        ("THANKS FOR PLAYING!", 80, (50, 255, 50))
    ]
    
    # Star field background
    stars = []
    for _ in range(200):
        stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)])
        
    start_time = time.time()
    scroll_y = HEIGHT + 50
    
    # Music switch
    pygame.mixer.music.stop()
    # Try to play emotional music if available, otherwise just use silence/sound effects
    try:
        if os.path.exists("coolwav.mp3"):
            pygame.mixer.music.load("coolwav.mp3")
            pygame.mixer.music.play(-1)
    except:
        pass
        
    running = True
    while running:
        current_time = time.time()
        
        # Event handling (press ESC to skip)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    running = False
                    
        # Update background
        screen.fill((0, 5, 20)) # Dark blue/black space
        
        # Draw stars
        for star in stars:
            star[1] += 0.5 # Move down slowly (simulating moving up)
            if star[1] > HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, WIDTH)
            pygame.draw.circle(screen, (255, 255, 255), (int(star[0]), int(star[1])), star[2])
            
        # Draw text
        current_y = scroll_y
        for text, size, color in lines:
            if current_y > -100 and current_y < HEIGHT + 100:
                try:
                    c_font = pygame.font.Font(None, size)
                    shadow = c_font.render(text, True, (0, 0, 0))
                    surf = c_font.render(text, True, color)
                    
                    # Center text
                    rect = surf.get_rect(center=(WIDTH//2, current_y))
                    s_rect = shadow.get_rect(center=(WIDTH//2 + 3, current_y + 3))
                    
                    screen.blit(shadow, s_rect)
                    screen.blit(surf, rect)
                except:
                    pass
            current_y += size + 20
            
        # Scroll up
        scroll_y -= 1.5
        
        # End condition
        if scroll_y < -(len(lines) * 100 + 500):
            running = False
            
        pygame.display.flip()
        pygame.time.wait(10)
        
    # Restore music
    try:
        pygame.mixer.music.load(background_music)
        pygame.mixer.music.play(-1)
    except:
        pass


def explosion_sequence(screen):
    """EPIC EXPLOSION ANIMATION - Everything explodes in ultra-realistic detail!"""
    import random
    
    # Explosion particles
    particles = []
    shockwaves = []
    
    # Create initial explosion center
    explosion_centers = [
        (WIDTH // 2, HEIGHT // 2),
        (WIDTH // 4, HEIGHT // 4),
        (3 * WIDTH // 4, HEIGHT // 4),
        (WIDTH // 4, 3 * HEIGHT // 4),
        (3 * WIDTH // 4, 3 * HEIGHT // 4),
    ]
    
    # Pre-explosion flash
    for flash_intensity in range(0, 255, 15):
        screen.fill((flash_intensity, flash_intensity, flash_intensity))
        flash_font = pygame.font.Font(None, 120)
        flash_text = flash_font.render("!", True, (255, 0, 0))
        screen.blit(flash_text, (WIDTH // 2 - flash_text.get_width() // 2, HEIGHT // 2 - 60))
        pygame.display.flip()
        pygame.time.wait(20)
    
    # Main explosion animation - 180 frames (3 seconds at 60fps)
    for frame in range(180):
        screen.fill((10, 5, 0))  # Dark background
        
        # Add new particles every few frames
        if frame % 2 == 0:
            for center_x, center_y in explosion_centers:
                for _ in range(15):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(2, 15)
                    particles.append({
                        'x': center_x,
                        'y': center_y,
                        'vx': math.cos(angle) * speed,
                        'vy': math.sin(angle) * speed,
                        'life': random.uniform(0.8, 1.5),
                        'max_life': random.uniform(0.8, 1.5),
                        'size': random.randint(3, 12),
                        'color': random.choice([
                            (255, 150, 0),  # Orange
                            (255, 80, 0),   # Red-orange
                            (255, 200, 0),  # Yellow
                            (200, 0, 0),    # Red
                            (255, 255, 100), # Bright yellow
                        ])
                    })
        
        # Add shockwaves
        if frame % 10 == 0 and frame < 60:
            for center_x, center_y in explosion_centers:
                shockwaves.append({
                    'x': center_x,
                    'y': center_y,
                    'radius': 10,
                    'max_radius': random.randint(200, 400),
                    'speed': random.uniform(8, 15),
                    'alpha': 255
                })
        
        # Update and draw shockwaves
        for wave in shockwaves[:]:
            wave['radius'] += wave['speed']
            wave['alpha'] = max(0, int(255 * (1 - wave['radius'] / wave['max_radius'])))
            
            if wave['radius'] >= wave['max_radius']:
                shockwaves.remove(wave)
            else:
                # Draw expanding shockwave ring
                if wave['alpha'] > 0:
                    for thickness in range(5):
                        color = (255, 150 - thickness * 20, 0)
                        try:
                            pygame.draw.circle(screen, color, 
                                             (int(wave['x']), int(wave['y'])), 
                                             int(wave['radius']) + thickness, 2)
                        except:
                            pass
        
        # Update and draw particles
        for particle in particles[:]:
            # Physics
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.3  # Gravity
            particle['vx'] *= 0.98  # Air resistance
            particle['life'] -= 1/60
            
            if particle['life'] <= 0 or particle['y'] > HEIGHT + 50:
                particles.remove(particle)
            else:
                # Calculate alpha based on remaining life
                life_ratio = particle['life'] / particle['max_life']
                
                # Draw particle with glow effect
                size = int(particle['size'] * life_ratio)
                if size > 0 and 0 <= particle['x'] < WIDTH and 0 <= particle['y'] < HEIGHT:
                    # Outer glow
                    glow_color = (particle['color'][0], particle['color'][1] // 2, 0)
                    try:
                        pygame.draw.circle(screen, glow_color, 
                                         (int(particle['x']), int(particle['y'])), 
                                         size + 3)
                        # Core
                        pygame.draw.circle(screen, particle['color'], 
                                         (int(particle['x']), int(particle['y'])), 
                                         size)
                        # Bright center
                        if size > 2:
                            pygame.draw.circle(screen, (255, 255, 200), 
                                             (int(particle['x']), int(particle['y'])), 
                                             size // 2)
                    except:
                        pass
        
        # Flash overlay for extra impact
        if frame < 30:
            flash_alpha = int(255 * (1 - frame / 30))
            flash_surface = pygame.Surface((WIDTH, HEIGHT))
            flash_surface.set_alpha(flash_alpha)
            flash_surface.fill((255, 200, 0))
            screen.blit(flash_surface, (0, 0))
        
        # Epic text reveals
        if 60 < frame < 150:
            reveal_alpha = min(255, (frame - 60) * 8)
            reveal_font = pygame.font.Font(None, 150)
            reveal_text = reveal_font.render("FINAL MODE", True, (255, 0, 0))
            text_surface = pygame.Surface(reveal_text.get_size())
            text_surface.fill((0, 0, 0))
            text_surface.blit(reveal_text, (0, 0))
            text_surface.set_alpha(reveal_alpha)
            screen.blit(text_surface, (WIDTH // 2 - reveal_text.get_width() // 2, HEIGHT // 2 - 80))
        
        pygame.display.flip()
        pygame.time.wait(16)  # ~60fps
    
    # Final fade to black
    for fade in range(0, 255, 10):
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.set_alpha(fade)
        fade_surface.fill((0, 0, 0))
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(20)


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
            headers = font.render("RANK    NAME          TIME      DATE", True, (200, 200, 200))
        else:
            headers = font.render("RANK    NAME          SCORE    LEVEL    DATE", True, (200, 200, 200))
        screen.blit(headers, (WIDTH//2 - headers.get_width()//2, 150))
        
        # Scores
        if scores:
            for i, entry in enumerate(scores):
                y_pos = 220 + i * 50
                rank = f"#{i+1}"
                
                # Format date (show just the date, not time)
                timestamp = entry.get('timestamp', 'N/A')
                if timestamp != 'N/A':
                    try:
                        date_only = timestamp.split(' ')[0]  # Get just YYYY-MM-DD
                    except:
                        date_only = timestamp[:10] if len(timestamp) >= 10 else timestamp
                else:
                    date_only = 'N/A'
                
                if mode == 'mom':
                    name = entry.get('name', 'Unknown')[:12]
                    score_val = entry.get('score', 0)
                    score_text = f"{score_val}s"
                    line = f"{rank:<8}{name:<14}{score_text:<10}{date_only}"
                else:
                    names = entry.get('names', entry.get('name', 'Unknown'))[:12]
                    score_val = entry.get('score', 0)
                    level = entry.get('level', 1)
                    line = f"{rank:<8}{names:<14}{score_val:<9}{level:<9}{date_only}"
                
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
    max_depth = 16.0  # Reduced for performance
    
    # Enhanced UI colors
    ui_bg = (15, 15, 25)
    ui_border = (120, 120, 180)
    health_color = (220, 40, 40)
    mana_color = (40, 120, 220)
    exp_color = (255, 200, 50)
    
    # Performance optimizations
    num_rays = 100  # Reduced from 150 for better FPS
    ray_quality = 0.2  # Step size for ray casting
    
    # Visual effects
    damage_numbers = []  # Floating damage numbers
    hit_flash = 0  # Screen flash on hit
    footstep_sound_timer = 0
    
    # Quest tracking
    show_quest_panel = False
    portal_revealed = False
    
    # Game state
    game_over = False
    victory = False
    attack_animation = 0.0  # Timer for attack animations
    
    running = True
    show_map = False
    message = ""
    message_timer = 0
    combat_target = None
    dialogue_lines = []
    dialogue_timer = 0
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        # If game over or victory, only allow ESC to exit
        if game_over or victory:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
            
            # Just render the final screen
            screen.fill((10, 10, 20))
            
            if game_over:
                # Death screen
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.fill((20, 0, 0))
                overlay.set_alpha(200)
                screen.blit(overlay, (0, 0))
                
                title = lobby_font.render("💀 GAME OVER 💀", True, (255, 50, 50))
                screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
                
                lines = [
                    "You have been defeated...",
                    "The dungeon claims another victim.",
                    "",
                    "Press ESC to return to menu"
                ]
                y_offset = HEIGHT // 2
                for line in lines:
                    text = font.render(line, True, (255, 200, 200))
                    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
                    y_offset += 40
            
            elif victory:
                # Victory screen
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.fill((20, 0, 40))
                overlay.set_alpha(200)
                screen.blit(overlay, (0, 0))
                
                title = lobby_font.render("✨ VICTORY! ✨", True, (255, 215, 0))
                screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
                
                lines = [
                    "You have completed all quests!",
                    "The portal glows with energy...",
                    "You escape the cursed dungeon!",
                    "",
                    "Press ESC to return to menu"
                ]
                y_offset = HEIGHT // 2
                for line in lines:
                    text = font.render(line, True, (200, 255, 200))
                    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
                    y_offset += 40
            
            pygame.display.flip()
            continue
        
        # Normal game continues...
        
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
                    
                    # Check if interacting with portal (by proximity to portal coordinates)
                    portal_x, portal_y = 14.5, 13.5
                    dist_to_portal = math.sqrt((check_x - portal_x)**2 + (check_y - portal_y)**2)
                    
                    if dist_to_portal < 1.5:  # Close enough to portal
                        # Check if monsters are defeated (not all quests, just monsters)
                        monsters_complete = False
                        for quest in player['quests']:
                            if 'Monster' in quest['name'] and quest['complete']:
                                monsters_complete = True
                                break
                        
                        if monsters_complete:
                            # Complete the portal quest
                            for quest in player['quests']:
                                if 'Portal' in quest['name']:
                                    quest['complete'] = True
                            
                            # Victory!
                            victory = True
                        else:
                            message = "⚠ The portal is sealed! Defeat all 4 monsters first."
                            message_timer = 3.0
                    
                    elif 0 <= cx < len(world_map[0]) and 0 <= cy < len(world_map):
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
                
                if event.key == pygame.K_SPACE:
                    # Attack
                    if combat_target and combat_target['alive']:
                        # Trigger attack animation
                        attack_animation = 0.5  # 0.5 seconds of animation
                        
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
                                game_over = True
                                player['health'] = 0  # Don't go negative
        
        # Check for nearby enemies
        combat_target = None
        for enemy in enemies:
            if enemy['alive']:
                dist = math.sqrt((enemy['x'] - player['x'])**2 + (enemy['y'] - player['y'])**2)
                if dist < 2.5:
                    combat_target = enemy
                    break
        
        # Check if near portal for hand interaction hint
        portal_x, portal_y = 14.5, 13.5
        dist_to_portal = math.sqrt((portal_x - player['x'])**2 + (portal_y - player['y'])**2)
        near_portal = dist_to_portal < 3.0
        
        # === RENDER 3D VIEW ===
        # Simple but effective sky gradient (optimized)
        screen.fill((30, 40, 60))  # Sky color
        pygame.draw.rect(screen, (20, 30, 25), (0, HEIGHT//2, WIDTH, HEIGHT//2))  # Floor
        
        # Optimized ray casting - fewer rays, faster rendering
        for ray in range(num_rays):
            ray_angle = player['angle'] - fov / 2 + (ray / num_rays) * fov
            
            # Cast ray with larger steps for speed
            for depth in range(0, int(max_depth / ray_quality)):
                test_depth = depth * ray_quality
                test_x = player['x'] + math.cos(ray_angle) * test_depth
                test_y = player['y'] + math.sin(ray_angle) * test_depth
                
                tx, ty = int(test_x), int(test_y)
                
                if 0 <= tx < len(world_map[0]) and 0 <= ty < len(world_map):
                    if world_map[ty][tx] == 1:  # Wall
                        # Calculate wall height
                        distance = test_depth * math.cos(ray_angle - player['angle'])
                        wall_height = min(HEIGHT, int(HEIGHT / (distance + 0.0001) * 0.65))
                        
                        # Simple but effective lighting
                        shade = max(20, 255 - int(distance * 18))
                        
                        # Simple brick effect
                        brick_offset = int((test_x + test_y) * 2) % 2
                        brick_shade = shade - brick_offset * 15
                        
                        # Wall orientation shading
                        if abs(math.cos(ray_angle)) > abs(math.sin(ray_angle)):
                            color = (brick_shade // 2, brick_shade // 2.2, brick_shade // 1.8)
                        else:
                            color = (brick_shade // 1.8, brick_shade // 2, brick_shade // 1.6)
                        
                        wall_top = HEIGHT // 2 - wall_height // 2
                        wall_bottom = HEIGHT // 2 + wall_height // 2
                        
                        x_pos = int(ray * (WIDTH / num_rays))
                        line_width = max(1, int(WIDTH / num_rays) + 1)
                        pygame.draw.line(screen, color, (x_pos, wall_top), (x_pos, wall_bottom), line_width)
                        break
                    elif world_map[ty][tx] == 2:  # Door - simple wooden style
                        distance = test_depth * math.cos(ray_angle - player['angle'])
                        wall_height = min(HEIGHT, int(HEIGHT / (distance + 0.0001) * 0.65))
                        shade = max(20, 200 - int(distance * 15))
                        
                        # Wooden door color
                        color = (shade // 2, shade // 3, shade // 6)
                        
                        wall_top = HEIGHT // 2 - wall_height // 2
                        wall_bottom = HEIGHT // 2 + wall_height // 2
                        x_pos = int(ray * (WIDTH / num_rays))
                        line_width = max(1, int(WIDTH / num_rays) + 1)
                        pygame.draw.line(screen, color, (x_pos, wall_top), (x_pos, wall_bottom), line_width)
                        
                        # Door handle
                        if distance < 3.0 and ray % 8 == 4:
                            pygame.draw.circle(screen, (180, 150, 50), (x_pos, HEIGHT // 2), 2)
                        break
        
        # Draw sprites (enemies, treasures, NPCs) - optimized
        sprites = []
        
        # Add enemies
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
                        enemy_type = sprite['data'].get('type', 'unknown')
                        
                        # GOBLIN - Small, hunched, greenish
                        if enemy_type == 'goblin':
                            # Small hunched body
                            pygame.draw.ellipse(screen, color, (screen_x - size//3, screen_y - size//2, size//1.5, size))
                            # Big head
                            head_color = tuple(min(255, int(c * 1.2)) for c in color)
                            pygame.draw.ellipse(screen, head_color, (screen_x - size//2.5, screen_y - size - size//3, size//1.2, size//1.5))
                            # Pointed ears
                            pygame.draw.polygon(screen, head_color, [
                                (screen_x - size//2, screen_y - size - size//4),
                                (screen_x - size//1.5, screen_y - size - size//3),
                                (screen_x - size//2.5, screen_y - size)
                            ])
                            pygame.draw.polygon(screen, head_color, [
                                (screen_x + size//2, screen_y - size - size//4),
                                (screen_x + size//1.5, screen_y - size - size//3),
                                (screen_x + size//2.5, screen_y - size)
                            ])
                            # Beady yellow eyes
                            eye_size = max(3, size // 12)
                            pygame.draw.circle(screen, (255, 255, 50), (screen_x - size//6, screen_y - size - size//6), eye_size)
                            pygame.draw.circle(screen, (0, 0, 0), (screen_x - size//6, screen_y - size - size//6), eye_size//2)
                            pygame.draw.circle(screen, (255, 255, 50), (screen_x + size//6, screen_y - size - size//6), eye_size)
                            pygame.draw.circle(screen, (0, 0, 0), (screen_x + size//6, screen_y - size - size//6), eye_size//2)
                            # Sharp teeth
                            for i in range(3):
                                tooth_x = screen_x - size//6 + i * size//6
                                pygame.draw.polygon(screen, (255, 255, 255), [
                                    (tooth_x, screen_y - size + size//8),
                                    (tooth_x - size//20, screen_y - size),
                                    (tooth_x + size//20, screen_y - size)
                                ])
                        
                        # ORC - Big, muscular, brutish
                        elif enemy_type == 'orc':
                            # Massive muscular body
                            pygame.draw.rect(screen, color, (screen_x - size//2, screen_y - size, size, size * 1.3))
                            # Broad shoulders
                            pygame.draw.rect(screen, tuple(int(c * 0.9) for c in color), 
                                           (screen_x - size//1.5, screen_y - size - size//4, size * 1.3, size//3))
                            # Large square head
                            head_color = tuple(min(255, int(c * 1.1)) for c in color)
                            pygame.draw.rect(screen, head_color, (screen_x - size//2.5, screen_y - size - size//1.5, size//1.2, size//1.3))
                            # Tusks
                            pygame.draw.polygon(screen, (255, 255, 220), [
                                (screen_x - size//4, screen_y - size - size//4),
                                (screen_x - size//3, screen_y - size + size//6),
                                (screen_x - size//5, screen_y - size)
                            ])
                            pygame.draw.polygon(screen, (255, 255, 220), [
                                (screen_x + size//4, screen_y - size - size//4),
                                (screen_x + size//3, screen_y - size + size//6),
                                (screen_x + size//5, screen_y - size)
                            ])
                            # Angry red eyes
                            eye_size = max(2, size // 14)
                            pygame.draw.circle(screen, (255, 100, 100), (screen_x - size//8, screen_y - size - size//3), eye_size)
                            pygame.draw.circle(screen, (255, 0, 0), (screen_x - size//8, screen_y - size - size//3), eye_size//2)
                            pygame.draw.circle(screen, (255, 100, 100), (screen_x + size//8, screen_y - size - size//3), eye_size)
                            pygame.draw.circle(screen, (255, 0, 0), (screen_x + size//8, screen_y - size - size//3), eye_size//2)
                            # War paint
                            pygame.draw.line(screen, (150, 50, 50), (screen_x - size//3, screen_y - size - size//2), 
                                           (screen_x + size//3, screen_y - size - size//2), max(1, size//20))
                        
                        # SKELETON - Thin, bony, undead
                        elif enemy_type == 'skeleton':
                            # Ribcage
                            for i in range(4):
                                rib_y = screen_y - size + i * size//5
                                pygame.draw.ellipse(screen, color, (screen_x - size//3, rib_y, size//1.5, size//8), 2)
                            # Spine
                            pygame.draw.line(screen, color, (screen_x, screen_y - size), (screen_x, screen_y + size//4), max(2, size//15))
                            # Pelvis
                            pygame.draw.arc(screen, color, (screen_x - size//3, screen_y - size//6, size//1.5, size//3), 0, math.pi, max(2, size//15))
                            # Skull
                            pygame.draw.circle(screen, (240, 240, 240), (screen_x, screen_y - size - size//3), size//2.5)
                            # Dark eye sockets with green glow
                            pygame.draw.circle(screen, (20, 20, 20), (screen_x - size//8, screen_y - size - size//3), size//10)
                            pygame.draw.circle(screen, (50, 255, 50), (screen_x - size//8, screen_y - size - size//3), size//15)
                            pygame.draw.circle(screen, (20, 20, 20), (screen_x + size//8, screen_y - size - size//3), size//10)
                            pygame.draw.circle(screen, (50, 255, 50), (screen_x + size//8, screen_y - size - size//3), size//15)
                            # Nose hole
                            pygame.draw.polygon(screen, (20, 20, 20), [
                                (screen_x, screen_y - size - size//4),
                                (screen_x - size//15, screen_y - size - size//6),
                                (screen_x + size//15, screen_y - size - size//6)
                            ])
                            # Teeth
                            for i in range(6):
                                tooth_x = screen_x - size//4 + i * size//10
                                pygame.draw.rect(screen, (20, 20, 20), (tooth_x, screen_y - size - size//8, size//20, size//12))
                            # Bone arms
                            pygame.draw.line(screen, color, (screen_x - size//2, screen_y - size//2), 
                                           (screen_x - size//1.5, screen_y - size), max(2, size//18))
                            pygame.draw.line(screen, color, (screen_x + size//2, screen_y - size//2), 
                                           (screen_x + size//1.5, screen_y - size), max(2, size//18))
                        
                        # DRAGON - Large, scaly, wings
                        elif enemy_type == 'dragon':
                            # Massive scaly body
                            for i in range(3):
                                scale_y = screen_y - size + i * size//3
                                scale_color = tuple(max(20, int(c * (0.8 + i * 0.1))) for c in color)
                                pygame.draw.ellipse(screen, scale_color, (screen_x - size//1.8, scale_y, size//0.9, size//2.5))
                            # Wings spread
                            wing_color = tuple(int(c * 0.7) for c in color)
                            # Left wing
                            pygame.draw.polygon(screen, wing_color, [
                                (screen_x - size//3, screen_y - size),
                                (screen_x - size * 1.2, screen_y - size//2),
                                (screen_x - size//2, screen_y - size//3)
                            ])
                            # Right wing
                            pygame.draw.polygon(screen, wing_color, [
                                (screen_x + size//3, screen_y - size),
                                (screen_x + size * 1.2, screen_y - size//2),
                                (screen_x + size//2, screen_y - size//3)
                            ])
                            # Wing membranes
                            pygame.draw.polygon(screen, tuple(int(c * 0.5) for c in color), [
                                (screen_x - size//3, screen_y - size),
                                (screen_x - size * 1.2, screen_y - size//2),
                                (screen_x - size//2, screen_y - size//3)
                            ], 1)
                            # Dragon head with horns
                            head_color = tuple(min(255, int(c * 1.2)) for c in color)
                            pygame.draw.ellipse(screen, head_color, (screen_x - size//2.5, screen_y - size * 1.4, size//1.2, size//1.8))
                            # Horns
                            pygame.draw.polygon(screen, (80, 80, 80), [
                                (screen_x - size//4, screen_y - size * 1.5),
                                (screen_x - size//3, screen_y - size * 1.8),
                                (screen_x - size//5, screen_y - size * 1.4)
                            ])
                            pygame.draw.polygon(screen, (80, 80, 80), [
                                (screen_x + size//4, screen_y - size * 1.5),
                                (screen_x + size//3, screen_y - size * 1.8),
                                (screen_x + size//5, screen_y - size * 1.4)
                            ])
                            # Fierce orange/red eyes
                            eye_size = max(4, size // 10)
                            pygame.draw.circle(screen, (255, 150, 0), (screen_x - size//8, screen_y - size * 1.3), eye_size)
                            pygame.draw.circle(screen, (255, 0, 0), (screen_x - size//8, screen_y - size * 1.3), eye_size//3)
                            pygame.draw.circle(screen, (255, 150, 0), (screen_x + size//8, screen_y - size * 1.3), eye_size)
                            pygame.draw.circle(screen, (255, 0, 0), (screen_x + size//8, screen_y - size * 1.3), eye_size//3)
                            # Smoke from nostrils
                            for j in range(2):
                                smoke_offset = (pygame.time.get_ticks() / 200 + j) % 20
                                smoke_alpha = max(0, 150 - smoke_offset * 10)
                                smoke_x = screen_x - size//8 + j * size//4
                                smoke_y = screen_y - size * 1.2 - smoke_offset
                                if smoke_alpha > 0:
                                    pygame.draw.circle(screen, (100, 100, 100), (int(smoke_x), int(smoke_y)), max(2, size//15))
                            # Sharp teeth
                            for i in range(5):
                                tooth_x = screen_x - size//3 + i * size//7
                                pygame.draw.polygon(screen, (255, 255, 255), [
                                    (tooth_x, screen_y - size * 1.15),
                                    (tooth_x - size//25, screen_y - size * 1.05),
                                    (tooth_x + size//25, screen_y - size * 1.05)
                                ])
                        
                        # Health bar above enemy
                        if 'health' in sprite['data'] and 'max_health' in sprite['data']:
                            bar_width = size * 1.2
                            bar_height = max(4, size // 20)
                            bar_x = screen_x - bar_width // 2
                            bar_y = screen_y - size * 1.6 if enemy_type == 'dragon' else screen_y - size * 1.2
                            # Background
                            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
                            # Health
                            health_pct = sprite['data']['health'] / sprite['data']['max_health']
                            health_width = int(bar_width * health_pct)
                            health_bar_color = (255, 50, 50) if health_pct < 0.3 else (255, 200, 50) if health_pct < 0.7 else (50, 255, 50)
                            pygame.draw.rect(screen, health_bar_color, (bar_x, bar_y, health_width, bar_height))
                            pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 1)
                            # Enemy name above health bar
                            enemy_name = sprite['data'].get('name', '')
                            if enemy_name and size > 30:
                                name_text = name_font.render(enemy_name, True, (255, 255, 255))
                                name_text.set_alpha(200)
                                screen.blit(name_text, (screen_x - name_text.get_width()//2, bar_y - 18))
                    
                    elif sprite['type'] == 'treasure':
                        # Different chest appearance based on treasure type
                        treasure_type = sprite['data'].get('type', 'gold')
                        
                        if treasure_type == 'weapon':
                            # Golden ornate weapon chest
                            chest_color = (255, 215, 0)
                            # Pulsing golden glow
                            glow_intensity = int(abs(math.sin(pygame.time.get_ticks() / 300)) * 50)
                            glow_color = tuple(min(255, c + glow_intensity) for c in chest_color)
                            pygame.draw.circle(screen, glow_color, (screen_x, screen_y - size//2), size//2 + 8, 3)
                            pygame.draw.circle(screen, glow_color, (screen_x, screen_y - size//2), size//2 + 5, 2)
                            # Main chest body - golden
                            pygame.draw.rect(screen, chest_color, (screen_x - size//2, screen_y - size//2, size, size//2))
                            # Lid with decorations
                            pygame.draw.polygon(screen, tuple(min(255, c + 30) for c in chest_color), [
                                (screen_x - size//2, screen_y - size//2),
                                (screen_x, screen_y - size//1.5),
                                (screen_x + size//2, screen_y - size//2)
                            ])
                            # Ornate lock
                            pygame.draw.circle(screen, (180, 150, 50), (screen_x, screen_y - size//4), max(3, size//8))
                            pygame.draw.circle(screen, (255, 215, 0), (screen_x, screen_y - size//4), max(2, size//12))
                            # Decorative gems
                            for i in range(3):
                                gem_x = screen_x - size//4 + i * size//4
                                pygame.draw.circle(screen, (255, 50, 50), (gem_x, screen_y - size//2.5), max(2, size//20))
                        
                        elif treasure_type == 'gold':
                            # Standard gold chest with coins
                            chest_color = (200, 160, 50)
                            # Simple glow
                            pygame.draw.circle(screen, (255, 215, 0), (screen_x, screen_y - size//2), size//2 + 5, 2)
                            # Wooden chest
                            pygame.draw.rect(screen, chest_color, (screen_x - size//2, screen_y - size//2, size, size//2))
                            # Metal bands
                            pygame.draw.rect(screen, (120, 100, 60), (screen_x - size//2, screen_y - size//3, size, size//15))
                            pygame.draw.rect(screen, (120, 100, 60), (screen_x - size//2, screen_y - size//8, size, size//15))
                            # Simple lock
                            pygame.draw.circle(screen, (150, 130, 70), (screen_x, screen_y - size//4), max(2, size//10))
                            # Coin symbol on top
                            if size > 20:
                                pygame.draw.circle(screen, (255, 215, 0), (screen_x, screen_y - size//1.8), size//8)
                                pygame.draw.circle(screen, chest_color, (screen_x, screen_y - size//1.8), size//12)
                        
                        elif treasure_type == 'potion':
                            # Red magical chest with potion symbol
                            chest_color = (180, 50, 50)
                            # Red magical aura
                            aura_pulse = int(abs(math.sin(pygame.time.get_ticks() / 400)) * 40)
                            aura_color = (255, 50 + aura_pulse, 50 + aura_pulse)
                            pygame.draw.circle(screen, aura_color, (screen_x, screen_y - size//2), size//2 + 6, 2)
                            # Main chest
                            pygame.draw.rect(screen, chest_color, (screen_x - size//2, screen_y - size//2, size, size//2))
                            # Glowing red cross (health symbol)
                            cross_size = size//6
                            pygame.draw.rect(screen, (255, 100, 100), (screen_x - cross_size//2, screen_y - size//2.5 - cross_size, 
                                           cross_size//2, cross_size * 2))
                            pygame.draw.rect(screen, (255, 100, 100), (screen_x - cross_size, screen_y - size//2.5 - cross_size//2, 
                                           cross_size * 2, cross_size//2))
                            # Mystical lock
                            pygame.draw.circle(screen, (200, 100, 100), (screen_x, screen_y - size//4), max(3, size//9))
                            pygame.draw.circle(screen, (255, 150, 150), (screen_x, screen_y - size//4), max(1, size//15))
                        
                        else:  # Default/other treasures
                            # Purple magical chest
                            chest_color = (150, 100, 200)
                            # Purple mystical glow
                            glow_pulse = int(abs(math.sin(pygame.time.get_ticks() / 350)) * 60)
                            glow_color = (150 + glow_pulse, 100 + glow_pulse, 200 + glow_pulse)
                            pygame.draw.circle(screen, glow_color, (screen_x, screen_y - size//2), size//2 + 7, 2)
                            # Main chest
                            pygame.draw.rect(screen, chest_color, (screen_x - size//2, screen_y - size//2, size, size//2))
                            # Magical runes
                            for i in range(4):
                                rune_y = screen_y - size//2.5 + i * size//12
                                pygame.draw.line(screen, (200, 150, 255), (screen_x - size//6, rune_y), 
                                               (screen_x + size//6, rune_y), max(1, size//30))
                            # Ornate magical lock
                            pygame.draw.circle(screen, (180, 130, 220), (screen_x, screen_y - size//4), max(3, size//8))
                            pygame.draw.circle(screen, (220, 180, 255), (screen_x, screen_y - size//4), max(2, size//12))
                            # Star symbol
                            if size > 25:
                                for i in range(5):
                                    angle = i * 2 * math.pi / 5 - math.pi / 2
                                    x1 = screen_x + int(math.cos(angle) * size//10)
                                    y1 = screen_y - size//4 + int(math.sin(angle) * size//10)
                                    pygame.draw.circle(screen, (255, 255, 150), (x1, y1), max(1, size//40))
                    
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
        
        # === DRAW FIRST-PERSON HANDS/ARMS ===
        # This draws your hands at the bottom of the screen
        
        # Determine hand animation based on actions
        time_ms = pygame.time.get_ticks()
        bob_offset = int(math.sin(time_ms / 200) * 5) if moved else 0  # Walking bob
        
        # RIGHT HAND - Holding weapon (sword/staff)
        right_hand_x = WIDTH - 250
        right_hand_y = HEIGHT - 200 + bob_offset
        
        # Draw arm (brown sleeve)
        arm_points = [
            (right_hand_x + 150, HEIGHT),
            (right_hand_x + 120, HEIGHT - 100),
            (right_hand_x + 80, HEIGHT - 150),
            (right_hand_x + 60, HEIGHT - 180),
            (right_hand_x + 40, HEIGHT - 180),
            (right_hand_x + 60, HEIGHT - 150),
            (right_hand_x + 100, HEIGHT - 100),
            (right_hand_x + 130, HEIGHT)
        ]
        pygame.draw.polygon(screen, (80, 60, 40), arm_points)  # Brown sleeve
        pygame.draw.polygon(screen, (60, 45, 30), arm_points, 2)  # Outline
        
        # Draw hand (skin color)
        hand_x = right_hand_x + 50
        hand_y = right_hand_y - 30
        pygame.draw.ellipse(screen, (220, 180, 150), (hand_x, hand_y, 60, 80))  # Palm
        
        # Fingers gripping the weapon
        finger_base_x = hand_x + 10
        for i in range(4):
            finger_x = finger_base_x + i * 12
            finger_y = hand_y + 20
            # Finger segments
            pygame.draw.ellipse(screen, (200, 160, 130), (finger_x, finger_y, 10, 25))
            pygame.draw.ellipse(screen, (200, 160, 130), (finger_x, finger_y + 20, 9, 20))
        
        # Thumb
        pygame.draw.ellipse(screen, (210, 170, 140), (hand_x + 50, hand_y + 30, 15, 30))
        
        # Draw weapon in hand
        weapon_name = player['equipped_weapon']
        
        # Calculate attack animation offset
        attack_offset = 0
        attack_glow_intensity = 0
        if attack_animation > 0:
            # Progress from 0 (start) to 1 (end) of animation
            attack_progress = 1 - (attack_animation / 0.5)
            # Swing forward then back (parabolic motion)
            attack_offset = int(math.sin(attack_progress * math.pi) * 60)
            attack_glow_intensity = attack_progress
        
        if 'Staff' in weapon_name or 'Mystic' in weapon_name:
            # Magic Staff - purple glow
            staff_x = hand_x + 25 - attack_offset // 2
            staff_y = hand_y - 150 - attack_offset
            # Staff shaft
            pygame.draw.line(screen, (80, 50, 30), (staff_x, staff_y + 200), (staff_x, staff_y), 8)
            # Magical crystal on top
            for j in range(3):
                glow_size = 25 + j * 8
                # Increase glow during attack
                if attack_animation > 0:
                    glow_size = int(glow_size * (1 + attack_glow_intensity * 1.5))
                glow_alpha = 100 - j * 30
                crystal_color = (150 + j * 20, 100, 255 - j * 30)
                # Brighter during attack
                if attack_animation > 0:
                    crystal_color = tuple(min(255, c + int(attack_glow_intensity * 100)) for c in crystal_color)
                pygame.draw.circle(screen, crystal_color, (staff_x, staff_y), glow_size // 2)
            # Glow particles
            particle_time = time_ms / 300
            particle_count = 5 if attack_animation <= 0 else 15  # More particles during attack
            for p in range(particle_count):
                angle = (particle_time + p * 1.2) % (2 * math.pi)
                radius = 30 if attack_animation <= 0 else 30 + attack_glow_intensity * 40
                px = int(staff_x + math.cos(angle) * radius)
                py = int(staff_y + math.sin(angle) * radius)
                particle_color = (200, 150, 255) if attack_animation <= 0 else (255, 200, 255)
                pygame.draw.circle(screen, particle_color, (px, py), 3 if attack_animation <= 0 else 5)
            # Magic blast effect during attack
            if attack_animation > 0:
                blast_radius = int(attack_glow_intensity * 80)
                for ring in range(3):
                    blast_color = (200 - ring * 30, 150 - ring * 30, 255)
                    blast_alpha = int((1 - attack_glow_intensity) * 150)
                    pygame.draw.circle(screen, blast_color, (staff_x, staff_y - 30), blast_radius + ring * 15, 3)
        else:
            # Sword (default or Golden Sword)
            blade_x = hand_x + 30 - attack_offset
            blade_y = hand_y - 120 - attack_offset // 2
            
            # Blade
            if 'Golden' in weapon_name:
                blade_color = (255, 215, 0)  # Gold
                shine_color = (255, 255, 200)
            else:
                blade_color = (180, 180, 200)  # Steel
                shine_color = (220, 220, 240)
            
            # Enhance colors during attack
            if attack_animation > 0:
                blade_color = tuple(min(255, c + int(attack_glow_intensity * 80)) for c in blade_color)
                shine_color = (255, 255, 255)
            
            # Draw blade with shine
            blade_points = [
                (blade_x, blade_y),
                (blade_x - 15, blade_y + 100),
                (blade_x - 10, blade_y + 120),
                (blade_x + 10, blade_y + 120),
                (blade_x + 15, blade_y + 100)
            ]
            pygame.draw.polygon(screen, blade_color, blade_points)
            # Shine line on blade
            pygame.draw.line(screen, shine_color, (blade_x, blade_y + 10), (blade_x, blade_y + 100), 2)
            
            # Sword trail/slash effect during attack
            if attack_animation > 0:
                # Draw motion blur/slash trail
                for trail in range(3):
                    trail_offset = trail * 15
                    trail_alpha = int(255 * (1 - trail * 0.3) * attack_glow_intensity)
                    trail_color = (255, 255, 200) if 'Golden' in weapon_name else (200, 200, 255)
                    trail_blade_x = blade_x + trail_offset
                    trail_blade_y = blade_y + trail_offset // 2
                    pygame.draw.line(screen, trail_color, 
                                   (trail_blade_x, trail_blade_y), 
                                   (trail_blade_x - 10, trail_blade_y + 100), 
                                   max(1, 4 - trail))
            
            # Guard/crossguard
            pygame.draw.rect(screen, (100, 80, 60), (blade_x - 25, blade_y + 120, 50, 8))
            
            # Handle
            pygame.draw.rect(screen, (60, 40, 20), (blade_x - 8, blade_y + 128, 16, 40))
            # Leather grip wrapping
            for wrap in range(5):
                wrap_y = blade_y + 130 + wrap * 7
                pygame.draw.line(screen, (80, 50, 25), (blade_x - 8, wrap_y), (blade_x + 8, wrap_y), 2)
            
            # Pommel
            pygame.draw.circle(screen, (150, 120, 80), (blade_x, blade_y + 172), 10)
        
        # LEFT HAND - Open hand for interactions
        left_hand_x = 150
        left_hand_y = HEIGHT - 250 + bob_offset
        
        # Draw arm (brown sleeve)
        left_arm_points = [
            (left_hand_x - 150, HEIGHT),
            (left_hand_x - 120, HEIGHT - 100),
            (left_hand_x - 80, HEIGHT - 120),
            (left_hand_x - 60, HEIGHT - 140),
            (left_hand_x - 40, HEIGHT - 140),
            (left_hand_x - 60, HEIGHT - 120),
            (left_hand_x - 100, HEIGHT - 100),
            (left_hand_x - 130, HEIGHT)
        ]
        pygame.draw.polygon(screen, (80, 60, 40), left_arm_points)
        pygame.draw.polygon(screen, (60, 45, 30), left_arm_points, 2)
        
        # Draw left hand (open palm)
        lhand_x = left_hand_x - 60
        lhand_y = left_hand_y
        pygame.draw.ellipse(screen, (220, 180, 150), (lhand_x, lhand_y, 70, 90))  # Palm
        
        # Open fingers (extended)
        # Thumb
        pygame.draw.ellipse(screen, (210, 170, 140), (lhand_x - 10, lhand_y + 35, 18, 35))
        pygame.draw.ellipse(screen, (200, 160, 130), (lhand_x - 15, lhand_y + 60, 15, 25))
        
        # Index finger (pointing/ready to press E)
        pygame.draw.ellipse(screen, (200, 160, 130), (lhand_x + 20, lhand_y - 10, 12, 30))
        pygame.draw.ellipse(screen, (200, 160, 130), (lhand_x + 22, lhand_y - 35, 11, 28))
        pygame.draw.ellipse(screen, (190, 150, 120), (lhand_x + 23, lhand_y - 58, 10, 25))
        
        # Middle finger
        pygame.draw.ellipse(screen, (200, 160, 130), (lhand_x + 35, lhand_y - 15, 12, 32))
        pygame.draw.ellipse(screen, (200, 160, 130), (lhand_x + 37, lhand_y - 42, 11, 30))
        pygame.draw.ellipse(screen, (190, 150, 120), (lhand_x + 38, lhand_y - 67, 10, 27))
        
        # Ring finger
        pygame.draw.ellipse(screen, (200, 160, 130), (lhand_x + 50, lhand_y - 10, 11, 30))
        pygame.draw.ellipse(screen, (200, 160, 130), (lhand_x + 51, lhand_y - 35, 10, 28))
        pygame.draw.ellipse(screen, (190, 150, 120), (lhand_x + 52, lhand_y - 58, 9, 25))
        
        # Pinky finger
        pygame.draw.ellipse(screen, (200, 160, 130), (lhand_x + 63, lhand_y, 10, 25))
        pygame.draw.ellipse(screen, (200, 160, 130), (lhand_x + 64, lhand_y - 20, 9, 22))
        pygame.draw.ellipse(screen, (190, 150, 120), (lhand_x + 65, lhand_y - 38, 8, 20))
        
        # Add interaction hint near left hand when near objects (but NOT during combat)
        near_object = near_portal and combat_target is None
        if near_object:
            hint_text = name_font.render("Press E", True, (255, 255, 100))
            pygame.draw.rect(screen, (0, 0, 0, 128), (lhand_x - 20, lhand_y - 100, 100, 30))
            screen.blit(hint_text, (lhand_x - 10, lhand_y - 95))
            # Finger highlights when ready to interact
            pygame.draw.circle(screen, (255, 255, 100), (lhand_x + 25, lhand_y - 50), 3)
        
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

def scary_doll_sequence(screen, dolls, music_playing):
    """Horror sequence - scary doll chops off doll heads and comes at the player!"""
    clock = pygame.time.Clock()
    
    # Play scary scream sound
    try:
        scream_sound = pygame.mixer.Sound(resource_path('scary-scream.mp3'))
        scream_sound.play()
    except:
        pass
    
    # Phase 1: Screen goes dark
    for darkness in range(0, 255, 15):
        screen.fill((0, 0, 0))
        
        # Draw dolls getting darker
        for doll in dolls:
            alpha = 255 - darkness
            if alpha > 0:
                draw_doll(screen, doll['x'], doll['y'], doll, doll['scale'], 0)
        
        # Dark overlay
        dark_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dark_surf.fill((0, 0, 0, darkness))
        screen.blit(dark_surf, (0, 0))
        
        pygame.display.flip()
        clock.tick(30)
        
        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
    
    # Wait in darkness
    pygame.time.wait(500)
    
    # Phase 2: Scary doll appears from the left
    scary_doll = {
        'x': -100,
        'y': HEIGHT // 2,
        'size': 80,
        'mouth_open': 0
    }
    
    # Falling heads
    falling_heads = []
    
    # Animate scary doll moving across
    for frame in range(180):
        dt = clock.tick(60) / 1000.0
        
        # Dark red background with flashing (clamped to valid range)
        flash = max(0, min(255, int(20 + 30 * math.sin(frame * 0.3))))
        screen.fill((flash, 0, 0))
        
        # Move scary doll
        scary_doll['x'] += 5
        scary_doll['mouth_open'] = abs(math.sin(frame * 0.3)) * 30
        
        # Draw normal dolls (before scary doll reaches them)
        for i, doll in enumerate(dolls):
            if scary_doll['x'] < doll['x'] - 50:
                # Doll is still intact, but shaking
                shake_x = doll['x'] + random.uniform(-2, 2)
                shake_y = doll['y'] + random.uniform(-2, 2)
                draw_doll(screen, shake_x, shake_y, doll, doll['scale'], frame * 0.1)
            elif scary_doll['x'] >= doll['x'] - 50 and scary_doll['x'] < doll['x'] + 50:
                # Doll is being attacked - head falls off!
                if not any(h['doll_index'] == i for h in falling_heads):
                    falling_heads.append({
                        'x': doll['x'],
                        'y': doll['y'] - 25,
                        'vx': random.uniform(-100, 100),
                        'vy': -200,
                        'rotation': 0,
                        'rot_speed': random.uniform(-360, 360),
                        'doll_index': i,
                        'color': doll['color'],
                        'hair_color': doll['hair_color']
                    })
                
                # Draw headless body
                draw_headless_doll(screen, doll['x'], doll['y'], doll)
            else:
                # Doll is already attacked - just headless body
                draw_headless_doll(screen, doll['x'], doll['y'], doll)
        
        # Update and draw falling heads
        for head in falling_heads:
            head['vy'] += 600 * dt  # Gravity
            head['x'] += head['vx'] * dt
            head['y'] += head['vy'] * dt
            head['rotation'] += head['rot_speed'] * dt
            
            if head['y'] < HEIGHT + 50:
                draw_severed_head(screen, head['x'], head['y'], head['rotation'], head['color'], head['hair_color'])
        
        # Draw scary doll
        draw_scary_doll(screen, scary_doll['x'], scary_doll['y'], scary_doll['size'], scary_doll['mouth_open'], frame)
        
        pygame.display.flip()
        
        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
    
    # Phase 3: Scary doll rushes toward camera
    for zoom in range(60):
        screen.fill((10, 0, 0))
        
        # Doll gets BIGGER and closer
        size = scary_doll['size'] + zoom * 15
        mouth_open = 20 + zoom * 2
        
        # Center of screen
        draw_scary_doll(screen, WIDTH // 2, HEIGHT // 2, size, mouth_open, zoom * 3)
        
        # Blood splatter effect
        if zoom > 30:
            for _ in range(5):
                splat_x = random.randint(0, WIDTH)
                splat_y = random.randint(0, HEIGHT)
                splat_size = random.randint(5, 20)
                pygame.draw.circle(screen, (150, 0, 0), (splat_x, splat_y), splat_size)
        
        pygame.display.flip()
        clock.tick(30)
        
        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
    
    # Final jumpscare - flash red
    for _ in range(3):
        screen.fill((255, 0, 0))
        pygame.display.flip()
        pygame.time.wait(100)
        screen.fill((0, 0, 0))
        pygame.display.flip()
        pygame.time.wait(100)
    
    # Show creepy message
    screen.fill((0, 0, 0))
    message1 = lobby_font.render("They weren't really your friends...", True, (200, 0, 0))
    message2 = lobby_font.render("Were they?", True, (150, 0, 0))
    screen.blit(message1, (WIDTH // 2 - message1.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(message2, (WIDTH // 2 - message2.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.flip()
    pygame.time.wait(2000)

def draw_headless_doll(surface, x, y, doll):
    """Draw a doll without a head (horror mode)"""
    scale = doll['scale']
    
    # Body (same as normal)
    if doll['outfit'] == 'dress':
        dress_points = [
            (x, y - 10 * scale),
            (x - 25 * scale, y + 30 * scale),
            (x - 30 * scale, y + 50 * scale),
            (x + 30 * scale, y + 50 * scale),
            (x + 25 * scale, y + 30 * scale)
        ]
        pygame.draw.polygon(surface, doll['color'], dress_points)
    elif doll['outfit'] == 'princess':
        pygame.draw.polygon(surface, doll['color'], [
            (x, y - 10 * scale),
            (x - 35 * scale, y + 50 * scale),
            (x + 35 * scale, y + 50 * scale)
        ])
    elif doll['outfit'] == 'superhero':
        pygame.draw.rect(surface, doll['color'], (int(x - 20 * scale), int(y - 10 * scale), 
                                                   int(40 * scale), int(60 * scale)))
    else:
        pygame.draw.rect(surface, doll['color'], (int(x - 18 * scale), int(y - 10 * scale), 
                                                   int(36 * scale), int(30 * scale)))
    
    # Arms
    arm_color = (255, 220, 180)
    pygame.draw.circle(surface, arm_color, (int(x - 25 * scale), int(y + 5 * scale)), int(8 * scale))
    pygame.draw.circle(surface, arm_color, (int(x + 25 * scale), int(y + 5 * scale)), int(8 * scale))
    
    # Neck stump with blood
    pygame.draw.circle(surface, (255, 220, 180), (int(x), int(y - 10 * scale)), int(12 * scale))
    pygame.draw.circle(surface, (150, 0, 0), (int(x), int(y - 10 * scale)), int(10 * scale))
    # Blood drips
    for i in range(3):
        drip_x = x + random.uniform(-10, 10) * scale
        drip_y = y - 10 * scale + i * 8 * scale
        pygame.draw.circle(surface, (150, 0, 0), (int(drip_x), int(drip_y)), int(3 * scale))

def draw_severed_head(surface, x, y, rotation, color, hair_color):
    """Draw a severed doll head (horror mode)"""
    # Create surface for head
    head_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
    
    # Head
    pygame.draw.circle(head_surf, (255, 220, 180), (25, 25), 18)
    
    # Hair
    hair_points = [
        (5, 25), (10, 10), (25, 5), (40, 10), (45, 25)
    ]
    pygame.draw.polygon(head_surf, hair_color, hair_points)
    
    # Dead eyes (X's)
    pygame.draw.line(head_surf, (0, 0, 0), (15, 20), (20, 25), 2)
    pygame.draw.line(head_surf, (0, 0, 0), (20, 20), (15, 25), 2)
    pygame.draw.line(head_surf, (0, 0, 0), (30, 20), (35, 25), 2)
    pygame.draw.line(head_surf, (0, 0, 0), (35, 20), (30, 25), 2)
    
    # Open mouth (screaming)
    pygame.draw.circle(head_surf, (0, 0, 0), (25, 32), 6)
    
    # Blood on neck
    pygame.draw.circle(head_surf, (150, 0, 0), (25, 43), 8)
    
    # Rotate and draw
    rotated = pygame.transform.rotate(head_surf, rotation)
    rect = rotated.get_rect(center=(int(x), int(y)))
    surface.blit(rotated, rect)

def draw_scary_doll(surface, x, y, size, mouth_open, frame):
    """Draw the terrifying scary doll"""
    
    # Shadow/aura
    for i in range(5):
        alpha = 50 - i * 10
        shadow_surf = pygame.Surface((int(size * 2.5), int(size * 3)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, alpha), shadow_surf.get_rect())
        surface.blit(shadow_surf, (int(x - size * 1.25), int(y - size * 1.5)))
    
    # Body - dark tattered dress
    dress_points = [
        (x, y),
        (x - size * 0.6, y + size * 1.2),
        (x - size * 0.7, y + size * 1.5),
        (x + size * 0.7, y + size * 1.5),
        (x + size * 0.6, y + size * 1.2)
    ]
    pygame.draw.polygon(surface, (30, 10, 30), dress_points)
    # Torn edges
    for i in range(5):
        tear_x = x - size * 0.7 + i * size * 0.35
        tear_y = y + size * 1.5
        pygame.draw.line(surface, (20, 5, 20), (tear_x, tear_y), (tear_x - 5, tear_y + 10), 2)
    
    # Arms - long and creepy
    arm_color = (180, 180, 160)
    # Left arm reaching out
    pygame.draw.line(surface, arm_color, (int(x - size * 0.3), int(y + size * 0.2)), 
                    (int(x - size * 1.2), int(y + size * 0.8)), int(size * 0.15))
    # Claw hand
    for finger in range(3):
        finger_x = x - size * 1.2 - finger * 8
        finger_y = y + size * 0.8
        pygame.draw.line(surface, (150, 150, 130), (int(x - size * 1.2), int(y + size * 0.8)),
                        (int(finger_x), int(finger_y + 15)), 3)
    
    # Right arm
    pygame.draw.line(surface, arm_color, (int(x + size * 0.3), int(y + size * 0.2)), 
                    (int(x + size * 1.2), int(y + size * 0.8)), int(size * 0.15))
    
    # Head - pale and creepy
    pygame.draw.circle(surface, (200, 200, 190), (int(x), int(y - size * 0.3)), int(size * 0.5))
    
    # Creepy hair - black and stringy
    for i in range(8):
        hair_x = x + math.sin(i + frame * 0.05) * size * 0.4
        hair_start_y = y - size * 0.8
        hair_end_y = y - size * 0.3 + random.uniform(0, size * 0.6)
        pygame.draw.line(surface, (10, 10, 10), (int(hair_x), int(hair_start_y)),
                        (int(hair_x), int(hair_end_y)), 3)
    
    # Eyes - GLOWING RED
    eye_glow_size = int(size * 0.15)
    # Left eye with glow
    for glow in range(3):
        glow_alpha = 100 - glow * 30
        glow_surf = pygame.Surface((eye_glow_size * 2, eye_glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 0, 0, glow_alpha), (eye_glow_size, eye_glow_size), 
                          eye_glow_size + glow * 5)
        surface.blit(glow_surf, (int(x - size * 0.2 - eye_glow_size), int(y - size * 0.4 - eye_glow_size)))
    pygame.draw.circle(surface, (255, 0, 0), (int(x - size * 0.2), int(y - size * 0.4)), int(size * 0.1))
    pygame.draw.circle(surface, (150, 0, 0), (int(x - size * 0.2), int(y - size * 0.4)), int(size * 0.05))
    
    # Right eye with glow
    for glow in range(3):
        glow_alpha = 100 - glow * 30
        glow_surf = pygame.Surface((eye_glow_size * 2, eye_glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 0, 0, glow_alpha), (eye_glow_size, eye_glow_size), 
                          eye_glow_size + glow * 5)
        surface.blit(glow_surf, (int(x + size * 0.2 - eye_glow_size), int(y - size * 0.4 - eye_glow_size)))
    pygame.draw.circle(surface, (255, 0, 0), (int(x + size * 0.2), int(y - size * 0.4)), int(size * 0.1))
    pygame.draw.circle(surface, (150, 0, 0), (int(x + size * 0.2), int(y - size * 0.4)), int(size * 0.05))
    
    # Mouth - BLOODY with sharp teeth
    mouth_y = y - size * 0.2
    mouth_height = int(size * 0.3 + mouth_open)
    pygame.draw.ellipse(surface, (0, 0, 0), (int(x - size * 0.2), int(mouth_y), 
                                              int(size * 0.4), mouth_height))
    pygame.draw.ellipse(surface, (100, 0, 0), (int(x - size * 0.18), int(mouth_y + 2), 
                                                int(size * 0.36), mouth_height - 4))
    
    # Sharp teeth
    num_teeth = 6
    for i in range(num_teeth):
        tooth_x = x - size * 0.15 + i * (size * 0.3 / num_teeth)
        # Top teeth
        tooth_points_top = [
            (tooth_x, mouth_y),
            (tooth_x - 3, mouth_y + 10),
            (tooth_x + 3, mouth_y + 10)
        ]
        pygame.draw.polygon(surface, (255, 255, 240), tooth_points_top)
        
        # Bottom teeth
        tooth_points_bottom = [
            (tooth_x, mouth_y + mouth_height),
            (tooth_x - 3, mouth_y + mouth_height - 10),
            (tooth_x + 3, mouth_y + mouth_height - 10)
        ]
        pygame.draw.polygon(surface, (255, 255, 240), tooth_points_bottom)
    
    # Blood on teeth and mouth
    for _ in range(8):
        blood_x = x + random.uniform(-size * 0.15, size * 0.15)
        blood_y = mouth_y + random.uniform(0, mouth_height)
        pygame.draw.circle(surface, (150, 0, 0), (int(blood_x), int(blood_y)), random.randint(1, 3))

def dilly_dolly_mode():
    """Whimsical Dilly Dolly Mode - Play with adorable dolls, dress them up, and watch them dance!"""
    clock = pygame.time.Clock()
    
    # Doll state
    dolls = []
    for i in range(5):
        dolls.append({
            'x': 150 + i * 150,
            'y': HEIGHT // 2,
            'vy': 0,
            'bouncing': False,
            'outfit': 'dress',  # 'dress', 'princess', 'superhero', 'casual'
            'color': random.choice([(255, 180, 200), (180, 200, 255), (200, 255, 180), (255, 220, 150), (220, 180, 255)]),
            'hair_color': random.choice([(139, 69, 19), (255, 215, 0), (0, 0, 0), (255, 100, 100), (150, 75, 0)]),
            'name': random.choice(['Lily', 'Rose', 'Daisy', 'Bella', 'Luna', 'Star', 'Angel', 'Joy', 'Hope']),
            'dancing': False,
            'dance_offset': 0,
            'hat': None,  # 'crown', 'bow', 'star', 'flower'
            'accessory': None,  # 'necklace', 'wand', 'wings'
            'scale': 1.0,
            'wiggle': 0
        })
    
    # UI State
    selected_doll = 0
    mode = 'play'  # 'play', 'dress', 'dance', 'tea'
    animation_time = 0
    
    # Confetti system
    confetti = []
    
    # Music playing flag
    music_playing = False
    
    # Sparkles
    sparkles = []
    
    # Tea party setup
    tea_table_y = HEIGHT - 200
    tea_cups = []
    cookies = []
    for i in range(5):
        tea_cups.append({
            'x': 150 + i * 150,
            'y': tea_table_y + 50,
            'filled': False,
            'steam': []
        })
        cookies.append({
            'x': 150 + i * 150,
            'y': tea_table_y + 100,
            'eaten': False
        })
    
    # Cheat code tracking
    cheat_input = ""
    rainbow_mode = False
    giant_mode = False
    sparkle_mode = False
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        animation_time += dt
        
        # Rainbow background in rainbow mode
        if rainbow_mode:
            hue = (animation_time * 50) % 360
            r = int(127.5 + 127.5 * math.sin(math.radians(hue)))
            g = int(127.5 + 127.5 * math.sin(math.radians(hue + 120)))
            b = int(127.5 + 127.5 * math.sin(math.radians(hue + 240)))
            screen.fill((r, g, b))
        else:
            # Pretty gradient background (clamped RGB channels)
            for y in range(HEIGHT):
                shade = int(200 + 55 * math.sin(y * 0.005))
                r = max(0, min(255, shade))
                g = max(0, min(255, shade - 20))
                b = max(0, min(255, shade + 20))
                pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
        
        # Draw clouds
        for i in range(8):
            cloud_x = (100 + i * 150 + animation_time * 10) % (WIDTH + 200) - 100
            cloud_y = 50 + i * 30
            for j in range(3):
                pygame.draw.circle(screen, (255, 255, 255, 150), (int(cloud_x + j * 20), int(cloud_y)), 20)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Stop music if playing
                    if music_playing:
                        pygame.mixer.music.stop()
                    return
                
                # Cheat code tracking
                if event.unicode.isalpha():
                    cheat_input += event.unicode.lower()
                    if len(cheat_input) > 10:
                        cheat_input = cheat_input[-10:]
                    
                    # Check for cheat codes
                    if 'rainbow' in cheat_input:
                        rainbow_mode = not rainbow_mode
                        cheat_input = ""
                        # Create confetti burst
                        for _ in range(100):
                            confetti.append({
                                'x': WIDTH // 2,
                                'y': HEIGHT // 2,
                                'vx': random.uniform(-300, 300),
                                'vy': random.uniform(-400, -100),
                                'color': random.choice([(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100), (255, 100, 255)]),
                                'size': random.randint(3, 8),
                                'rotation': random.uniform(0, 360),
                                'rot_speed': random.uniform(-360, 360)
                            })
                    
                    elif 'giant' in cheat_input:
                        giant_mode = not giant_mode
                        cheat_input = ""
                        for doll in dolls:
                            if giant_mode:
                                doll['scale'] = 2.0
                            else:
                                doll['scale'] = 1.0
                    
                    elif 'sparkle' in cheat_input:
                        sparkle_mode = not sparkle_mode
                        cheat_input = ""
                    
                    elif 'lllooolll' in cheat_input:
                        # SCARY DOLL HORROR MODE!
                        cheat_input = ""
                        scary_doll_sequence(screen, dolls, music_playing)
                        # Stop music if playing
                        if music_playing:
                            pygame.mixer.music.stop()
                        # Return to main menu
                        return
                
                # Mode switching
                if event.key == pygame.K_1:
                    mode = 'play'
                    # Stop dancing and music when switching to play mode
                    for doll in dolls:
                        doll['dancing'] = False
                    if music_playing:
                        pygame.mixer.music.stop()
                        music_playing = False
                elif event.key == pygame.K_2:
                    mode = 'dress'
                    # Stop dancing and music when switching to dress mode
                    for doll in dolls:
                        doll['dancing'] = False
                    if music_playing:
                        pygame.mixer.music.stop()
                        music_playing = False
                elif event.key == pygame.K_3:
                    mode = 'dance'
                    # All dolls start dancing!
                    for doll in dolls:
                        doll['dancing'] = True
                    # Play music
                    if not music_playing:
                        try:
                            music_path = resource_path('playmusic.mp3')
                            pygame.mixer.music.load(music_path)
                            pygame.mixer.music.play(-1)
                            music_playing = True
                        except:
                            pass
                elif event.key == pygame.K_4:
                    mode = 'tea'
                    # Stop dancing and music when switching to tea mode
                    for doll in dolls:
                        doll['dancing'] = False
                    if music_playing:
                        pygame.mixer.music.stop()
                        music_playing = False
                
                # Doll selection
                if event.key == pygame.K_LEFT:
                    selected_doll = (selected_doll - 1) % len(dolls)
                elif event.key == pygame.K_RIGHT:
                    selected_doll = (selected_doll + 1) % len(dolls)
                
                # Play mode actions
                if mode == 'play':
                    if event.key == pygame.K_SPACE:
                        # Make selected doll bounce
                        dolls[selected_doll]['bouncing'] = True
                        dolls[selected_doll]['vy'] = -500
                        # Add sparkles
                        for _ in range(20):
                            sparkles.append({
                                'x': dolls[selected_doll]['x'],
                                'y': dolls[selected_doll]['y'],
                                'vx': random.uniform(-100, 100),
                                'vy': random.uniform(-200, -50),
                                'life': 1.0,
                                'color': random.choice([(255, 255, 100), (255, 200, 255), (200, 255, 255)])
                            })
                    
                    if event.key == pygame.K_w:
                        # Make all dolls wave
                        for doll in dolls:
                            doll['wiggle'] = 10
                
                # Dress mode actions
                elif mode == 'dress':
                    if event.key == pygame.K_o:
                        # Change outfit
                        outfits = ['dress', 'princess', 'superhero', 'casual']
                        current = outfits.index(dolls[selected_doll]['outfit'])
                        dolls[selected_doll]['outfit'] = outfits[(current + 1) % len(outfits)]
                    
                    if event.key == pygame.K_h:
                        # Change hat
                        hats = [None, 'crown', 'bow', 'star', 'flower']
                        current_hat = dolls[selected_doll]['hat']
                        if current_hat is None:
                            dolls[selected_doll]['hat'] = 'crown'
                        else:
                            idx = hats.index(current_hat)
                            dolls[selected_doll]['hat'] = hats[(idx + 1) % len(hats)]
                    
                    if event.key == pygame.K_a:
                        # Change accessory
                        accessories = [None, 'necklace', 'wand', 'wings']
                        current_acc = dolls[selected_doll]['accessory']
                        if current_acc is None:
                            dolls[selected_doll]['accessory'] = 'necklace'
                        else:
                            idx = accessories.index(current_acc)
                            dolls[selected_doll]['accessory'] = accessories[(idx + 1) % len(accessories)]
                    
                    if event.key == pygame.K_c:
                        # Random color
                        dolls[selected_doll]['color'] = (
                            random.randint(150, 255),
                            random.randint(150, 255),
                            random.randint(150, 255)
                        )
                
                # Tea party mode
                elif mode == 'tea':
                    if event.key == pygame.K_SPACE:
                        # Pour tea for selected doll
                        tea_cups[selected_doll]['filled'] = True
                        # Add steam particles
                        for _ in range(5):
                            tea_cups[selected_doll]['steam'].append({
                                'y': 0,
                                'offset': random.uniform(-5, 5),
                                'speed': random.uniform(20, 40),
                                'life': 1.0
                            })
                    
                    if event.key == pygame.K_e:
                        # Eat cookie
                        if not cookies[selected_doll]['eaten']:
                            cookies[selected_doll]['eaten'] = True
                            # Add crumbs
                            for _ in range(15):
                                sparkles.append({
                                    'x': cookies[selected_doll]['x'],
                                    'y': cookies[selected_doll]['y'],
                                    'vx': random.uniform(-50, 50),
                                    'vy': random.uniform(-100, 0),
                                    'life': 0.8,
                                    'color': (210, 180, 140)
                                })
        
        # Update dolls
        for i, doll in enumerate(dolls):
            # Bouncing physics
            if doll['bouncing']:
                doll['vy'] += 1000 * dt  # Gravity
                doll['y'] += doll['vy'] * dt
                
                # Floor bounce
                floor_y = HEIGHT // 2 if mode != 'tea' else tea_table_y - 80
                if doll['y'] >= floor_y:
                    doll['y'] = floor_y
                    doll['vy'] = -doll['vy'] * 0.6  # Bounce with damping
                    if abs(doll['vy']) < 50:
                        doll['bouncing'] = False
                        doll['vy'] = 0
            
            # Dancing animation
            if doll['dancing']:
                doll['dance_offset'] = math.sin(animation_time * 5 + i * 0.5) * 20
            else:
                doll['dance_offset'] = 0
            
            # Wiggle decay
            if doll['wiggle'] > 0:
                doll['wiggle'] -= dt * 10
        
        # Update confetti
        for c in confetti[:]:
            c['vy'] += 500 * dt  # Gravity
            c['x'] += c['vx'] * dt
            c['y'] += c['vy'] * dt
            c['rotation'] += c['rot_speed'] * dt
            
            if c['y'] > HEIGHT:
                confetti.remove(c)
        
        # Update sparkles
        for s in sparkles[:]:
            s['x'] += s['vx'] * dt
            s['y'] += s['vy'] * dt
            s['vy'] += 200 * dt  # Gravity
            s['life'] -= dt
            
            if s['life'] <= 0:
                sparkles.remove(s)
        
        # Sparkle mode - continuous sparkles
        if sparkle_mode and random.random() < 0.3:
            for doll in dolls:
                if random.random() < 0.1:
                    sparkles.append({
                        'x': doll['x'] + random.uniform(-20, 20),
                        'y': doll['y'] - 40 + random.uniform(-20, 20),
                        'vx': random.uniform(-30, 30),
                        'vy': random.uniform(-80, -20),
                        'life': 0.8,
                        'color': random.choice([(255, 255, 100), (255, 200, 255), (200, 255, 255), (100, 255, 255)])
                    })
        
        # Update tea steam
        if mode == 'tea':
            for cup in tea_cups:
                if cup['filled']:
                    for steam in cup['steam'][:]:
                        steam['y'] -= steam['speed'] * dt
                        steam['life'] -= dt * 0.3
                        if steam['life'] <= 0:
                            cup['steam'].remove(steam)
                    
                    # Add new steam
                    if random.random() < 0.2:
                        cup['steam'].append({
                            'y': 0,
                            'offset': random.uniform(-5, 5),
                            'speed': random.uniform(20, 40),
                            'life': 1.0
                        })
        
        # Draw confetti
        for c in confetti:
            size = c['size']
            rotated_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.rect(rotated_surface, c['color'], (size // 2, size // 2, size, size))
            rotated = pygame.transform.rotate(rotated_surface, c['rotation'])
            rect = rotated.get_rect(center=(int(c['x']), int(c['y'])))
            screen.blit(rotated, rect)
        
        # Draw sparkles
        for s in sparkles:
            alpha = int(s['life'] * 255)
            color = (*s['color'], alpha)
            size = int(3 + s['life'] * 4)
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (size, size), size)
            screen.blit(surf, (int(s['x'] - size), int(s['y'] - size)))
        
        # Draw tea party table
        if mode == 'tea':
            # Tablecloth
            pygame.draw.rect(screen, (255, 200, 200), (50, tea_table_y, WIDTH - 100, 150))
            pygame.draw.rect(screen, (255, 150, 150), (50, tea_table_y, WIDTH - 100, 150), 3)
            
            # Draw tea cups and cookies
            for i, (cup, cookie) in enumerate(zip(tea_cups, cookies)):
                # Tea cup
                cup_color = (255, 255, 255) if cup['filled'] else (230, 230, 230)
                pygame.draw.ellipse(screen, cup_color, (cup['x'] - 15, cup['y'] - 10, 30, 20))
                pygame.draw.rect(screen, cup_color, (cup['x'] - 15, cup['y'] - 5, 30, 15))
                pygame.draw.ellipse(screen, (200, 200, 200), (cup['x'] - 15, cup['y'] - 10, 30, 20), 2)
                
                # Tea liquid
                if cup['filled']:
                    pygame.draw.ellipse(screen, (139, 69, 19), (cup['x'] - 12, cup['y'] - 8, 24, 15))
                
                # Handle
                pygame.draw.arc(screen, (200, 200, 200), (cup['x'] + 10, cup['y'] - 5, 15, 20), -math.pi/2, math.pi/2, 3)
                
                # Steam
                for steam in cup['steam']:
                    steam_alpha = int(steam['life'] * 150)
                    steam_y = cup['y'] - 20 - steam['y']
                    steam_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                    pygame.draw.circle(steam_surf, (200, 200, 200, steam_alpha), (3, 3), 3)
                    screen.blit(steam_surf, (int(cup['x'] + steam['offset'] - 3), int(steam_y)))
                
                # Cookie
                if not cookie['eaten']:
                    pygame.draw.circle(screen, (210, 180, 140), (cookie['x'], cookie['y']), 12)
                    # Chocolate chips
                    random.seed(i * 123)  # Consistent chips per cookie
                    for _ in range(5):
                        chip_x = cookie['x'] + random.randint(-8, 8)
                        chip_y = cookie['y'] + random.randint(-8, 8)
                        pygame.draw.circle(screen, (101, 67, 33), (chip_x, chip_y), 2)
                    random.seed()  # Reset seed
        
        # Draw dolls
        for i, doll in enumerate(dolls):
            draw_x = doll['x']
            draw_y = doll['y'] + doll['dance_offset']
            scale = doll['scale']
            
            # Wiggle effect
            wiggle_offset = math.sin(animation_time * 20) * doll['wiggle']
            draw_x += wiggle_offset
            
            # Draw doll with outfit
            draw_doll(screen, draw_x, draw_y, doll, scale, animation_time)
            
            # Selection indicator
            if i == selected_doll:
                indicator_y = draw_y + 60 * scale + 10
                pygame.draw.polygon(screen, (255, 255, 100), [
                    (draw_x, indicator_y),
                    (draw_x - 10, indicator_y + 15),
                    (draw_x + 10, indicator_y + 15)
                ])
                
                # Draw name
                name_text = font.render(doll['name'], True, (255, 255, 255))
                name_bg = pygame.Surface((name_text.get_width() + 10, name_text.get_height() + 5), pygame.SRCALPHA)
                pygame.draw.rect(name_bg, (0, 0, 0, 150), name_bg.get_rect(), border_radius=5)
                screen.blit(name_bg, (draw_x - name_text.get_width() // 2 - 5, draw_y - 90))
                screen.blit(name_text, (draw_x - name_text.get_width() // 2, draw_y - 88))
        
        # Draw UI
        draw_dilly_dolly_ui(screen, mode, selected_doll, dolls, rainbow_mode, giant_mode, sparkle_mode)
        
        pygame.display.flip()
    
    # Stop music when leaving
    if music_playing:
        pygame.mixer.music.stop()

def draw_doll(surface, x, y, doll, scale=1.0, time=0):
    """Draw a cute doll with outfit, hat, and accessories"""
    
    # Body (dress/outfit)
    if doll['outfit'] == 'dress':
        # Pretty dress
        dress_points = [
            (x, y - 10 * scale),
            (x - 25 * scale, y + 30 * scale),
            (x - 30 * scale, y + 50 * scale),
            (x + 30 * scale, y + 50 * scale),
            (x + 25 * scale, y + 30 * scale)
        ]
        pygame.draw.polygon(surface, doll['color'], dress_points)
        # Dress details
        pygame.draw.circle(surface, (255, 255, 255), (int(x - 10 * scale), int(y + 20 * scale)), int(3 * scale))
        pygame.draw.circle(surface, (255, 255, 255), (int(x + 10 * scale), int(y + 20 * scale)), int(3 * scale))
        pygame.draw.circle(surface, (255, 255, 255), (int(x), int(y + 35 * scale)), int(3 * scale))
    
    elif doll['outfit'] == 'princess':
        # Royal princess dress
        pygame.draw.polygon(surface, doll['color'], [
            (x, y - 10 * scale),
            (x - 35 * scale, y + 50 * scale),
            (x + 35 * scale, y + 50 * scale)
        ])
        # Gold trim
        pygame.draw.line(surface, (255, 215, 0), (int(x - 30 * scale), int(y + 45 * scale)), 
                        (int(x + 30 * scale), int(y + 45 * scale)), int(3 * scale))
    
    elif doll['outfit'] == 'superhero':
        # Superhero suit
        pygame.draw.rect(surface, doll['color'], (int(x - 20 * scale), int(y - 10 * scale), 
                                                   int(40 * scale), int(60 * scale)))
        # Cape
        cape_points = [
            (x - 15 * scale, y - 5 * scale),
            (x - 35 * scale, y + 40 * scale),
            (x - 25 * scale, y + 50 * scale)
        ]
        pygame.draw.polygon(surface, (255, 50, 50), cape_points)
        # Logo
        pygame.draw.circle(surface, (255, 255, 0), (int(x), int(y + 10 * scale)), int(8 * scale))
        pygame.draw.circle(surface, doll['color'], (int(x), int(y + 10 * scale)), int(5 * scale))
    
    else:  # casual
        # Casual t-shirt and pants
        pygame.draw.rect(surface, doll['color'], (int(x - 18 * scale), int(y - 10 * scale), 
                                                   int(36 * scale), int(30 * scale)))
        pygame.draw.rect(surface, (100, 100, 200), (int(x - 18 * scale), int(y + 20 * scale), 
                                                     int(36 * scale), int(30 * scale)))
    
    # Arms
    arm_color = (255, 220, 180)
    pygame.draw.circle(surface, arm_color, (int(x - 25 * scale), int(y + 5 * scale)), int(8 * scale))
    pygame.draw.circle(surface, arm_color, (int(x + 25 * scale), int(y + 5 * scale)), int(8 * scale))
    
    # Head
    pygame.draw.circle(surface, arm_color, (int(x), int(y - 25 * scale)), int(20 * scale))
    
    # Hair
    hair_points = [
        (x - 20 * scale, y - 25 * scale),
        (x - 15 * scale, y - 40 * scale),
        (x, y - 45 * scale),
        (x + 15 * scale, y - 40 * scale),
        (x + 20 * scale, y - 25 * scale)
    ]
    pygame.draw.polygon(surface, doll['hair_color'], hair_points)
    
    # Face
    # Eyes
    eye_y = y - 28 * scale
    pygame.draw.circle(surface, (0, 0, 0), (int(x - 7 * scale), int(eye_y)), int(3 * scale))
    pygame.draw.circle(surface, (0, 0, 0), (int(x + 7 * scale), int(eye_y)), int(3 * scale))
    # Eye shine
    pygame.draw.circle(surface, (255, 255, 255), (int(x - 6 * scale), int(eye_y - 1 * scale)), int(1 * scale))
    pygame.draw.circle(surface, (255, 255, 255), (int(x + 8 * scale), int(eye_y - 1 * scale)), int(1 * scale))
    
    # Smile
    smile_rect = pygame.Rect(int(x - 8 * scale), int(y - 23 * scale), int(16 * scale), int(8 * scale))
    pygame.draw.arc(surface, (255, 100, 100), smile_rect, 0, math.pi, int(2 * scale))
    
    # Rosy cheeks
    cheek_surf = pygame.Surface((int(8 * scale), int(8 * scale)), pygame.SRCALPHA)
    pygame.draw.circle(cheek_surf, (255, 180, 180, 100), (int(4 * scale), int(4 * scale)), int(4 * scale))
    surface.blit(cheek_surf, (int(x - 18 * scale), int(y - 25 * scale)))
    surface.blit(cheek_surf, (int(x + 10 * scale), int(y - 25 * scale)))
    
    # Hat
    if doll['hat'] == 'crown':
        # Golden crown
        crown_points = [
            (x - 15 * scale, y - 40 * scale),
            (x - 12 * scale, y - 50 * scale),
            (x - 5 * scale, y - 45 * scale),
            (x, y - 52 * scale),
            (x + 5 * scale, y - 45 * scale),
            (x + 12 * scale, y - 50 * scale),
            (x + 15 * scale, y - 40 * scale)
        ]
        pygame.draw.polygon(surface, (255, 215, 0), crown_points)
        # Jewels
        pygame.draw.circle(surface, (255, 50, 50), (int(x), int(y - 48 * scale)), int(3 * scale))
    
    elif doll['hat'] == 'bow':
        # Pretty bow
        bow_color = (255, 100, 150)
        pygame.draw.circle(surface, bow_color, (int(x - 10 * scale), int(y - 45 * scale)), int(8 * scale))
        pygame.draw.circle(surface, bow_color, (int(x + 10 * scale), int(y - 45 * scale)), int(8 * scale))
        pygame.draw.circle(surface, bow_color, (int(x), int(y - 45 * scale)), int(5 * scale))
    
    elif doll['hat'] == 'star':
        # Star on head
        star_points = []
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2
            radius = (10 * scale) if i % 2 == 0 else (5 * scale)
            star_x = x + radius * math.cos(angle)
            star_y = y - 50 * scale + radius * math.sin(angle)
            star_points.append((star_x, star_y))
        pygame.draw.polygon(surface, (255, 255, 100), star_points)
    
    elif doll['hat'] == 'flower':
        # Flower crown
        for i in range(5):
            petal_x = x + math.cos(i * 2 * math.pi / 5 + time * 2) * 12 * scale
            petal_y = y - 45 * scale + math.sin(i * 2 * math.pi / 5 + time * 2) * 12 * scale
            pygame.draw.circle(surface, (255, 150, 200), (int(petal_x), int(petal_y)), int(5 * scale))
        pygame.draw.circle(surface, (255, 255, 100), (int(x), int(y - 45 * scale)), int(6 * scale))
    
    # Accessories
    if doll['accessory'] == 'necklace':
        # Pearl necklace
        for i in range(5):
            pearl_x = x - 10 * scale + i * 5 * scale
            pearl_y = y - 5 * scale
            pygame.draw.circle(surface, (255, 255, 255), (int(pearl_x), int(pearl_y)), int(3 * scale))
    
    elif doll['accessory'] == 'wand':
        # Magic wand
        wand_x = x + 30 * scale
        wand_y = y + 10 * scale
        pygame.draw.line(surface, (139, 69, 19), (int(x + 25 * scale), int(y + 5 * scale)), 
                        (int(wand_x), int(wand_y)), int(3 * scale))
        # Star on wand
        star_points = []
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2 + time * 3
            radius = (8 * scale) if i % 2 == 0 else (4 * scale)
            star_x = wand_x + radius * math.cos(angle)
            star_y = wand_y + radius * math.sin(angle)
            star_points.append((star_x, star_y))
        pygame.draw.polygon(surface, (255, 255, 100), star_points)
    
    elif doll['accessory'] == 'wings':
        # Fairy wings
        wing_color = (200, 200, 255, 150)
        wing_surf = pygame.Surface((int(40 * scale), int(30 * scale)), pygame.SRCALPHA)
        # Left wing
        pygame.draw.ellipse(wing_surf, wing_color, (0, int(5 * scale), int(20 * scale), int(25 * scale)))
        # Right wing  
        pygame.draw.ellipse(wing_surf, wing_color, (int(20 * scale), int(5 * scale), int(20 * scale), int(25 * scale)))
        surface.blit(wing_surf, (int(x - 20 * scale), int(y - 15 * scale)))

def draw_dilly_dolly_ui(surface, mode, selected_doll, dolls, rainbow_mode, giant_mode, sparkle_mode):
    """Draw UI for Dilly Dolly Mode"""
    
    # Mode indicator
    mode_names = {
        'play': 'PLAY MODE - Space: Bounce, W: Wave',
        'dress': 'DRESS MODE - O: Outfit, H: Hat, A: Accessory, C: Color',
        'dance': 'DANCE MODE - Let them dance!',
        'tea': 'TEA PARTY - Space: Pour Tea, E: Eat Cookie'
    }
    
    mode_text = lobby_font.render(mode_names[mode], True, (255, 255, 255))
    mode_bg = pygame.Surface((mode_text.get_width() + 20, mode_text.get_height() + 10), pygame.SRCALPHA)
    pygame.draw.rect(mode_bg, (100, 50, 150, 200), mode_bg.get_rect(), border_radius=10)
    surface.blit(mode_bg, (WIDTH // 2 - mode_text.get_width() // 2 - 10, 10))
    surface.blit(mode_text, (WIDTH // 2 - mode_text.get_width() // 2, 15))
    
    # Mode buttons
    modes = [('1', 'Play'), ('2', 'Dress'), ('3', 'Dance'), ('4', 'Tea')]
    button_y = HEIGHT - 60
    for i, (key, name) in enumerate(modes):
        button_x = 100 + i * 180
        color = (150, 200, 255) if mode == name.lower() else (100, 100, 150)
        pygame.draw.rect(surface, color, (button_x, button_y, 150, 40), border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), (button_x, button_y, 150, 40), 3, border_radius=8)
        
        button_text = font.render(f"{key}: {name}", True, (255, 255, 255))
        surface.blit(button_text, (button_x + 75 - button_text.get_width() // 2, button_y + 10))
    
    # Active cheats indicator
    if rainbow_mode or giant_mode or sparkle_mode:
        cheat_y = HEIGHT - 100
        cheats_text = "Active: "
        if rainbow_mode:
            cheats_text += "RAINBOW "
        if giant_mode:
            cheats_text += "GIANT "
        if sparkle_mode:
            cheats_text += "SPARKLE "
        
        cheat_render = font.render(cheats_text, True, (255, 255, 100))
        cheat_bg = pygame.Surface((cheat_render.get_width() + 10, cheat_render.get_height() + 5), pygame.SRCALPHA)
        pygame.draw.rect(cheat_bg, (150, 50, 200, 200), cheat_bg.get_rect(), border_radius=5)
        surface.blit(cheat_bg, (WIDTH // 2 - cheat_render.get_width() // 2 - 5, cheat_y))
        surface.blit(cheat_render, (WIDTH // 2 - cheat_render.get_width() // 2, cheat_y + 2))
    
    # Instructions
    instr_text = font.render("Left/Right: Select Doll | ESC: Exit", True, (255, 255, 255))
    instr_bg = pygame.Surface((instr_text.get_width() + 10, instr_text.get_height() + 5), pygame.SRCALPHA)
    pygame.draw.rect(instr_bg, (0, 0, 0, 150), instr_bg.get_rect(), border_radius=5)
    surface.blit(instr_bg, (10, 10))
    surface.blit(instr_text, (15, 12))

def ultimate_satisfaction_mode():
    """The most satisfying game ever - bubble wrap, slime, dominoes, and paint mixing!"""
    clock = pygame.time.Clock()
    
    # Bubble wrap grid
    bubble_size = 40
    cols = WIDTH // bubble_size
    rows = (HEIGHT - 150) // bubble_size
    bubbles = [[True for _ in range(cols)] for _ in range(rows)]
    
    # Slime particles
    slime_particles = []
    
    # Domino chain
    dominoes = []
    
    # Paint drops
    paint_drops = []
    
    # Counters
    bubbles_popped = 0
    slime_squished = 0
    dominoes_fallen = 0
    
    # Current mode
    current_mode = 'bubbles'
    mode_names = ['Bubble Wrap', 'Slime Squish', 'Domino Chain', 'Paint Mix']
    mode_index = 0
    
    # Setup dominoes
    def reset_dominoes():
        dominoes.clear()
        for i in range(20):
            dominoes.append({
                'x': 100 + i * 50,
                'y': HEIGHT // 2,
                'angle': 0,
                'falling': False,
                'fall_speed': 0
            })
    
    reset_dominoes()
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Beautiful gradient background (optimized)
        screen.fill((120, 160, 210))
        for y in range(0, HEIGHT, 5):
            r = int(100 + 50 * math.sin(y * 0.01))
            g = int(150 + 50 * math.sin(y * 0.01 + 2))
            b = int(200 + 50 * math.sin(y * 0.01 + 4))
            pygame.draw.rect(screen, (r, g, b), (0, y, WIDTH, 5))
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_TAB:
                    # Switch modes
                    mode_index = (mode_index + 1) % 4
                    current_mode = ['bubbles', 'slime', 'dominoes', 'paint'][mode_index]
                elif event.key == pygame.K_r:
                    # Reset current mode
                    if current_mode == 'bubbles':
                        bubbles = [[True for _ in range(cols)] for _ in range(rows)]
                    elif current_mode == 'slime':
                        slime_particles.clear()
                    elif current_mode == 'dominoes':
                        reset_dominoes()
                    elif current_mode == 'paint':
                        paint_drops.clear()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                if current_mode == 'bubbles':
                    # Pop bubble
                    col = mx // bubble_size
                    row = my // bubble_size
                    if 0 <= row < rows and 0 <= col < cols and bubbles[row][col]:
                        bubbles[row][col] = False
                        bubbles_popped += 1
                        # Pop particles
                        for _ in range(20):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = random.uniform(50, 150)
                            slime_particles.append({
                                'x': float(col * bubble_size + bubble_size // 2),
                                'y': float(row * bubble_size + bubble_size // 2),
                                'vx': math.cos(angle) * speed,
                                'vy': math.sin(angle) * speed,
                                'life': 1.0,
                                'size': random.randint(2, 6),
                                'color': (100 + random.randint(0, 155), 200, 255)
                            })
                
                elif current_mode == 'slime':
                    # Create slime explosion
                    for _ in range(50):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(20, 100)
                        slime_particles.append({
                            'x': float(mx),
                            'y': float(my),
                            'vx': math.cos(angle) * speed,
                            'vy': math.sin(angle) * speed,
                            'life': 2.0,
                            'size': random.randint(3, 10),
                            'color': (random.randint(100, 255), random.randint(200, 255), random.randint(100, 255))
                        })
                    slime_squished += 1
                
                elif current_mode == 'dominoes':
                    # Knock over domino
                    for i, domino in enumerate(dominoes):
                        if abs(mx - domino['x']) < 25 and abs(my - domino['y']) < 40:
                            if not domino['falling']:
                                domino['falling'] = True
                                domino['fall_speed'] = 200
                            break
                
                elif current_mode == 'paint':
                    # Drop paint
                    paint_drops.append({
                        'x': float(mx),
                        'y': float(my),
                        'vx': random.uniform(-50, 50),
                        'vy': random.uniform(50, 150),
                        'size': random.randint(15, 30),
                        'color': [random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)],
                        'life': 3.0
                    })
        
        # === BUBBLE WRAP MODE ===
        if current_mode == 'bubbles':
            for row in range(rows):
                for col in range(cols):
                    x = col * bubble_size
                    y = row * bubble_size
                    
                    if bubbles[row][col]:
                        # Unpopped bubble
                        pygame.draw.circle(screen, (150, 150, 180), (x + bubble_size // 2 + 2, y + bubble_size // 2 + 2), bubble_size // 3)
                        pygame.draw.circle(screen, (200, 220, 255), (x + bubble_size // 2, y + bubble_size // 2), bubble_size // 3)
                        pygame.draw.circle(screen, (255, 255, 255), (x + bubble_size // 2 - 5, y + bubble_size // 2 - 5), bubble_size // 8)
                        pygame.draw.circle(screen, (150, 170, 200), (x + bubble_size // 2, y + bubble_size // 2), bubble_size // 3, 2)
        
        # === SLIME MODE ===
        elif current_mode == 'slime':
            inst = lobby_font.render("Click anywhere to squish slime!", True, (255, 255, 255))
            screen.blit(inst, (WIDTH // 2 - inst.get_width() // 2, 50))
        
        # === DOMINO MODE ===
        elif current_mode == 'dominoes':
            # Update dominoes
            for i, domino in enumerate(dominoes):
                if domino['falling']:
                    domino['angle'] += domino['fall_speed'] * dt
                    if domino['angle'] >= 90:
                        domino['angle'] = 90
                        # Trigger next domino
                        if i + 1 < len(dominoes) and not dominoes[i + 1]['falling']:
                            dominoes[i + 1]['falling'] = True
                            dominoes[i + 1]['fall_speed'] = 250
                            dominoes_fallen += 1
                
                # Draw domino
                domino_surf = pygame.Surface((40, 80), pygame.SRCALPHA)
                pygame.draw.rect(domino_surf, (240, 240, 250), (0, 0, 40, 80))
                pygame.draw.rect(domino_surf, (50, 50, 100), (0, 0, 40, 80), 3)
                for dy in [20, 40, 60]:
                    pygame.draw.circle(domino_surf, (50, 50, 100), (20, dy), 4)
                
                if domino['angle'] > 0:
                    domino_surf = pygame.transform.rotate(domino_surf, -domino['angle'])
                
                rect = domino_surf.get_rect(center=(domino['x'], domino['y']))
                screen.blit(domino_surf, rect)
        
        # === PAINT MIX MODE ===
        elif current_mode == 'paint':
            inst = lobby_font.render("Click to drop paint and watch it mix!", True, (255, 255, 255))
            screen.blit(inst, (WIDTH // 2 - inst.get_width() // 2, 50))
            
            # Update paint drops
            for drop in paint_drops[:]:
                drop['y'] += drop['vy'] * dt
                drop['x'] += drop['vx'] * dt
                drop['vy'] += 200 * dt  # Gravity
                drop['life'] -= dt
                
                # Bounce off bottom
                if drop['y'] > HEIGHT - 100:
                    drop['y'] = HEIGHT - 100
                    drop['vy'] *= -0.5
                    drop['vx'] *= 0.8
                
                # Bounce off sides
                if drop['x'] < drop['size'] or drop['x'] > WIDTH - drop['size']:
                    drop['vx'] *= -0.5
                
                # Mix with nearby drops
                for other in paint_drops:
                    if other != drop:
                        dx = other['x'] - drop['x']
                        dy = other['y'] - drop['y']
                        dist = math.sqrt(dx * dx + dy * dy)
                        if dist < drop['size'] + other['size']:
                            # Mix colors
                            for i in range(3):
                                drop['color'][i] = (drop['color'][i] + other['color'][i]) // 2
                
                if drop['life'] <= 0:
                    paint_drops.remove(drop)
                else:
                    # Draw paint drop
                    for glow in range(3):
                        glow_size = drop['size'] + glow * 5
                        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                        color = drop['color']
                        glow_alpha = int(255 * min(1, drop['life'])) // (glow + 1)
                        pygame.draw.circle(glow_surf, (color[0], color[1], color[2], glow_alpha), (glow_size, glow_size), glow_size)
                        screen.blit(glow_surf, (int(drop['x']) - glow_size, int(drop['y']) - glow_size))
        
        # Update and draw particles (used in multiple modes)
        for particle in slime_particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] += 200 * dt  # Gravity
            particle['life'] -= dt
            
            if particle['life'] <= 0 or particle['y'] > HEIGHT:
                slime_particles.remove(particle)
            else:
                alpha = int(255 * particle['life'])
                size = particle['size']
                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                color = particle['color']
                if isinstance(color, (list, tuple)) and len(color) >= 3:
                    pygame.draw.circle(surf, (color[0], color[1], color[2], alpha), (size, size), size)
                screen.blit(surf, (int(particle['x']) - size, int(particle['y']) - size))
        
        # Draw UI
        ui_bg = pygame.Surface((WIDTH, 100))
        ui_bg.fill((0, 0, 0))
        ui_bg.set_alpha(180)
        screen.blit(ui_bg, (0, 0))
        
        # Title
        title = pygame.font.SysFont(None, 60).render(f"✨ {mode_names[mode_index]} ✨", True, (255, 255, 100))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))
        
        # Instructions
        instructions = [("TAB", "Switch Mode"), ("R", "Reset"), ("ESC", "Exit")]
        x_offset = 50
        for key, action in instructions:
            key_text = font.render(f"[{key}]", True, (255, 255, 150))
            action_text = font.render(action, True, (200, 200, 255))
            screen.blit(key_text, (x_offset, 65))
            screen.blit(action_text, (x_offset + key_text.get_width() + 10, 65))
            x_offset += key_text.get_width() + action_text.get_width() + 40
        
        # Stats
        stats_text = font.render(f"Bubbles: {bubbles_popped} | Slime: {slime_squished} | Dominoes: {dominoes_fallen}", True, (150, 255, 150))
        screen.blit(stats_text, (WIDTH - stats_text.get_width() - 20, 65))
        
        pygame.display.flip()



# Countdown and player name input functions remain the same...


# Load background image for battle mode
try:
    battle_background = pygame.image.load(resource_path('ball.jpg'))
    has_battle_background = True
except:
    has_battle_background = False
    print("ball.jpg not found, using solid color background for battle mode")

def classroom_adventure_menu():
    """PEACEFUL CLASSROOM MODE - Appears BEFORE main game. Type 'jaaaa' to skip to battle mode"""
    clock = pygame.time.Clock()
    
    # Peaceful colors
    SKY_BLUE = (135, 206, 250)
    GRASS_GREEN = (34, 139, 34)
    YELLOW = (255, 255, 0)
    GOLD = (255, 215, 0)
    PINK = (255, 192, 203)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    LIGHT_BLUE = (173, 216, 230)
    
    key_buffer = ""
    server_code = ""  # Player types server code here
    
    while True:
        screen.fill(SKY_BLUE)
        
        # Draw grass at bottom
        pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - 150, WIDTH, 150))
        
        # Draw cute flowers
        for i in range(20):
            flower_x = i * (WIDTH // 20) + 50
            flower_y = HEIGHT - 100
            # Petals (4 circles around center)
            pygame.draw.circle(screen, PINK, (flower_x - 10, flower_y), 8)
            pygame.draw.circle(screen, YELLOW, (flower_x + 10, flower_y), 8)
            pygame.draw.circle(screen, PINK, (flower_x, flower_y - 10), 8)
            pygame.draw.circle(screen, YELLOW, (flower_x, flower_y + 10), 8)
            # Center
            pygame.draw.circle(screen, GOLD, (flower_x, flower_y), 8)
            # Stem
            pygame.draw.line(screen, GRASS_GREEN, (flower_x, flower_y), (flower_x, flower_y + 30), 3)
        
        # Title with shadow
        title_font = pygame.font.SysFont(None, 120)
        subtitle_font = pygame.font.SysFont(None, 60)
        instruction_font = pygame.font.SysFont(None, 40)
        
        # Shadow
        shadow_text = title_font.render("CLASSROOM ADVENTURE", True, (100, 100, 100))
        shadow_rect = shadow_text.get_rect(center=(WIDTH//2 + 3, HEIGHT//4 + 3))
        screen.blit(shadow_text, shadow_rect)
        
        # Title
        title_text = title_font.render("CLASSROOM ADVENTURE", True, GOLD)
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = subtitle_font.render("A Peaceful Game for Your Entire Class!", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH//2, HEIGHT//3 + 50))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Instructions
        option_y = HEIGHT//2 + 20
        instruction_text = subtitle_font.render("Enter Server Code to Join:", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(WIDTH//2, option_y))
        screen.blit(instruction_text, instruction_rect)
        
        # Server code input box
        input_box_rect = pygame.Rect(WIDTH//2 - 150, option_y + 60, 300, 80)
        pygame.draw.rect(screen, LIGHT_BLUE, input_box_rect)
        pygame.draw.rect(screen, GOLD, input_box_rect, 5)
        
        # Display typed server code
        code_font = pygame.font.SysFont(None, 100)
        if server_code:
            code_text = code_font.render(server_code, True, BLACK)
        else:
            code_text = code_font.render("___", True, (150, 150, 150))
        code_rect = code_text.get_rect(center=input_box_rect.center)
        screen.blit(code_text, code_rect)
        
        # Server options below
        info_y = option_y + 180
        info_font = pygame.font.SysFont(None, 50)
        info1 = info_font.render("Server 1: Type '123'", True, PINK)
        info1_rect = info1.get_rect(center=(WIDTH//2, info_y))
        screen.blit(info1, info1_rect)
        
        info2 = info_font.render("Server 2: Type '321'", True, YELLOW)
        info2_rect = info2.get_rect(center=(WIDTH//2, info_y + 60))
        screen.blit(info2, info2_rect)
        
        # Secret instruction at bottom (hidden/small)
        secret_text = instruction_font.render("(Secret code unlocks Battle Mode)", True, (150, 150, 150))
        secret_rect = secret_text.get_rect(center=(WIDTH//2, HEIGHT - 80))
        screen.blit(secret_text, secret_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                # Handle backspace
                if event.key == pygame.K_BACKSPACE:
                    server_code = server_code[:-1]
                    key_buffer = key_buffer[:-1] if key_buffer else ""
                
                # Handle number input for server codes
                elif event.unicode.isdigit():
                    if len(server_code) < 3:
                        server_code += event.unicode
                        key_buffer += event.unicode.lower()
                    
                    # Check if valid server code entered
                    if server_code == "123":
                        return 'server1'
                    elif server_code == "321":
                        return 'server2'
                
                # Track all key presses for secret code
                elif event.unicode:
                    key_buffer += event.unicode.lower()
                    if len(key_buffer) > 10:
                        key_buffer = key_buffer[-10:]
                    
                    # Check for secret code "jaaaa" - ONLY way to get to battle mode!
                    if "jaaaa" in key_buffer:
                        return  # Skip to talking intro
        
        clock.tick(60)

def play_classroom_game(server_name):
    """The actual peaceful classroom game - collaborative and fun!"""
    import socket
    import threading
    import json
    
    clock = pygame.time.Clock()
    
    # Colors
    SKY_BLUE = (135, 206, 250)
    GRASS_GREEN = (34, 139, 34)
    YELLOW = (255, 255, 0)
    GOLD = (255, 215, 0)
    PINK = (255, 192, 203)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    ORANGE = (255, 165, 0)
    RED = (255, 0, 0)
    BLUE = (0, 100, 255)
    PURPLE = (160, 32, 240)
    
    # Player setup
    player_x = WIDTH // 2
    player_y = HEIGHT - 200
    player_speed = 5
    
    # Ask for player name
    player_name = ""
    entering_name = True
    
    while entering_name:
        screen.fill(SKY_BLUE)
        pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - 150, WIDTH, 150))
        
        title_font = pygame.font.SysFont(None, 80)
        title_text = title_font.render("Enter Your Name:", True, GOLD)
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
        screen.blit(title_text, title_rect)
        
        name_font = pygame.font.SysFont(None, 100)
        name_display = player_name if player_name else "___"
        name_text = name_font.render(name_display, True, WHITE)
        name_rect = name_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(name_text, name_rect)
        
        hint_font = pygame.font.SysFont(None, 40)
        hint = hint_font.render("Press ENTER when done", True, WHITE)
        hint_rect = hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
        screen.blit(hint, hint_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name.strip():
                    entering_name = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 15 and event.unicode.isprintable():
                    player_name += event.unicode
    
    # Network setup
    other_players = {}  # Dictionary of {player_id: {name, x, y, color}}
    my_player_id = str(random.randint(1000, 9999))
    
    # Server ports - different for each server
    server_port = 5556 if server_name == "Server 1" else 5557
    
    # UDP socket for multiplayer
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(0.001)
    
    try:
        sock.bind(('', server_port))
    except:
        pass  # If binding fails, can still send
    
    # Random color for this player
    player_colors = [PINK, ORANGE, RED, BLUE, PURPLE, YELLOW]
    my_color = random.choice(player_colors)
    
    def receive_updates():
        """Background thread to receive other players' positions"""
        while running:
            try:
                data, addr = sock.recvfrom(1024)
                msg = json.loads(data.decode())
                
                if msg['id'] != my_player_id:  # Don't add ourselves
                    other_players[msg['id']] = {
                        'name': msg['name'],
                        'x': msg['x'],
                        'y': msg['y'],
                        'color': tuple(msg['color'])
                    }
            except:
                pass
    
    # Start background thread
    running = True
    listener_thread = threading.Thread(target=receive_updates, daemon=True)
    listener_thread.start()
    
    # Collectible flowers
    flowers = []
    for i in range(15):
        flowers.append({
            'x': random.randint(50, WIDTH - 50),
            'y': random.randint(100, HEIGHT - 200),
            'collected': False
        })
    
    score = 0
    last_broadcast = 0
    
    running = True
    while running:
        screen.fill(SKY_BLUE)
        
        # Draw grass
        pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - 150, WIDTH, 150))
        
        # Draw flowers to collect
        for flower in flowers:
            if not flower['collected']:
                # Draw flower
                x, y = flower['x'], flower['y']
                pygame.draw.circle(screen, PINK, (x - 10, y), 8)
                pygame.draw.circle(screen, YELLOW, (x + 10, y), 8)
                pygame.draw.circle(screen, PINK, (x, y - 10), 8)
                pygame.draw.circle(screen, YELLOW, (x, y + 10), 8)
                pygame.draw.circle(screen, GOLD, (x, y), 10)
        
        # Draw OTHER REAL PLAYERS from network!
        for player_id, other in list(other_players.items()):
            pygame.draw.circle(screen, other['color'], (int(other['x']), int(other['y'])), 20)
            name_font = pygame.font.SysFont(None, 30)
            name_text = name_font.render(other['name'], True, WHITE)
            screen.blit(name_text, (other['x'] - name_text.get_width()//2, other['y'] - 40))
        
        # Draw MY player
        pygame.draw.circle(screen, my_color, (player_x, player_y), 25)
        pygame.draw.circle(screen, WHITE, (player_x - 8, player_y - 5), 5)  # Eye
        pygame.draw.circle(screen, WHITE, (player_x + 8, player_y - 5), 5)  # Eye
        pygame.draw.circle(screen, BLACK, (player_x - 8, player_y - 5), 3)  # Pupil
        pygame.draw.circle(screen, BLACK, (player_x + 8, player_y - 5), 3)  # Pupil
        
        # Draw my name
        my_name_font = pygame.font.SysFont(None, 35)
        my_name_text = my_name_font.render(player_name, True, GOLD)
        screen.blit(my_name_text, (player_x - my_name_text.get_width()//2, player_y - 50))
        
        # Draw UI
        title_font = pygame.font.SysFont(None, 60)
        title_text = title_font.render(f"Connected to {server_name}!", True, GOLD)
        screen.blit(title_text, (20, 20))
        
        score_font = pygame.font.SysFont(None, 50)
        score_text = score_font.render(f"Flowers: {score}/15 | Players: {len(other_players) + 1}", True, WHITE)
        screen.blit(score_text, (20, 80))
        
        instruction_font = pygame.font.SysFont(None, 40)
        inst = instruction_font.render("WASD to move • Collect all flowers! • ESC to leave", True, WHITE)
        screen.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT - 30))
        
        pygame.display.flip()
        
        # Broadcast my position to other players
        current_time = pygame.time.get_ticks()
        if current_time - last_broadcast > 50:  # Every 50ms
            try:
                my_data = {
                    'id': my_player_id,
                    'name': player_name,
                    'x': player_x,
                    'y': player_y,
                    'color': list(my_color)
                }
                sock.sendto(json.dumps(my_data).encode(), ('<broadcast>', server_port))
                last_broadcast = current_time
            except:
                pass
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    sock.close()
                    return  # Exit classroom game
        
        # Handle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player_y -= player_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player_y += player_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player_x += player_speed
        
        # Keep player on screen
        player_x = max(25, min(WIDTH - 25, player_x))
        player_y = max(25, min(HEIGHT - 160, player_y))
        
        # Check flower collection
        for flower in flowers:
            if not flower['collected']:
                distance = ((player_x - flower['x'])**2 + (player_y - flower['y'])**2)**0.5
                if distance < 35:
                    flower['collected'] = True
                    score += 1
        
        # Remove players who haven't sent data in a while (disconnected)
        current_time = pygame.time.get_ticks()
        # (We'd add timeout logic here if needed)
        
        # Win condition
        if score >= 15:
            running = False
            sock.close()
            
            screen.fill(SKY_BLUE)
            win_font = pygame.font.SysFont(None, 100)
            win_text = win_font.render("ALL FLOWERS COLLECTED!", True, GOLD)
            win_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            screen.blit(win_text, win_rect)
            
            congrats_font = pygame.font.SysFont(None, 60)
            congrats = congrats_font.render("Great teamwork everyone! 🌸", True, WHITE)
            congrats_rect = congrats.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            screen.blit(congrats, congrats_rect)
            
            pygame.display.flip()
            pygame.time.wait(3000)
            return
        
        clock.tick(60)

def talking_intro():
    """EPIC TALKING INTRO with voice narration and animated presenter before main menu"""
    import os
    
    # Intro messages with voice (EPIC MOVIE TRAILER STYLE!)
    intro_scenes = [
        {
            'text': 'IN A WORLD...',
            'voice': 'In a world of chaos and epic battles',
            'duration': 3.0,
            'effect': 'fade_in',
            'man_action': 'point_left',
            'man_text': 'Epic Battles!'
        },
        {
            'text': 'WHERE WARRIORS CLASH',
            'voice': 'Where warriors clash in legendary combat',
            'duration': 3.5,
            'effect': 'zoom',
            'man_action': 'point_right',
            'man_text': 'Legendary!'
        },
        {
            'text': 'ONE GAME STANDS ABOVE ALL',
            'voice': 'ONE GAME stands above all others',
            'duration': 3.5,
            'effect': 'pulse',
            'man_action': 'point_up',
            'man_text': 'The Best!'
        },
        {
            'text': 'BATTLEGAME',
            'voice': 'BATTLEGAME! The ultimate showdown!',
            'duration': 3.5,
            'effect': 'shake',
            'man_action': 'excited',
            'man_text': 'WOW!'
        },
        {
            'text': 'CHOOSE YOUR DESTINY',
            'voice': 'Choose your destiny, select your fighter',
            'duration': 3.0,
            'effect': 'spiral',
            'man_action': 'point_center',
            'man_text': 'Pick Wisely!'
        },
        {
            'text': 'ARE YOU READY?',
            'voice': 'Are... you... READY?',
            'duration': 3.5,
            'effect': 'explode',
            'man_action': 'dramatic',
            'man_text': "LET'S GO!"
        }
    ]
    
    clock = pygame.time.Clock()
    
    # Draw the presenter/announcer man
    def draw_presenter(x, y, action, text, progress):
        """Draw animated presenter pointing at things"""
        scale = 1.0
        
        # Body (suit)
        body_color = (50, 50, 80)
        pygame.draw.rect(screen, body_color, (int(x - 30), int(y), 60, 100))
        
        # Legs
        pygame.draw.rect(screen, (30, 30, 60), (int(x - 25), int(y + 100), 20, 60))
        pygame.draw.rect(screen, (30, 30, 60), (int(x + 5), int(y + 100), 20, 60))
        
        # Shoes
        pygame.draw.ellipse(screen, (0, 0, 0), (int(x - 30), int(y + 150), 25, 15))
        pygame.draw.ellipse(screen, (0, 0, 0), (int(x + 5), int(y + 150), 25, 15))
        
        # Tie
        pygame.draw.polygon(screen, (200, 50, 50), [
            (x, y + 10),
            (x - 8, y + 30),
            (x, y + 70),
            (x + 8, y + 30)
        ])
        
        # Head (skin tone)
        head_color = (255, 220, 180)
        pygame.draw.circle(screen, head_color, (int(x), int(y - 20)), 35)
        
        # Hair (professional cut)
        hair_color = (80, 60, 40)
        pygame.draw.arc(screen, hair_color, (int(x - 35), int(y - 55), 70, 40), 0, math.pi, 15)
        
        # Face
        # Eyes
        eye_y = y - 25
        pygame.draw.circle(screen, (255, 255, 255), (int(x - 12), int(eye_y)), 8)
        pygame.draw.circle(screen, (255, 255, 255), (int(x + 12), int(eye_y)), 8)
        pygame.draw.circle(screen, (50, 100, 200), (int(x - 12), int(eye_y)), 5)
        pygame.draw.circle(screen, (50, 100, 200), (int(x + 12), int(eye_y)), 5)
        pygame.draw.circle(screen, (0, 0, 0), (int(x - 12), int(eye_y)), 3)
        pygame.draw.circle(screen, (0, 0, 0), (int(x + 12), int(eye_y)), 3)
        
        # Eyebrows (dramatic)
        pygame.draw.line(screen, (60, 40, 20), (int(x - 20), int(eye_y - 12)), (int(x - 5), int(eye_y - 10)), 3)
        pygame.draw.line(screen, (60, 40, 20), (int(x + 20), int(eye_y - 12)), (int(x + 5), int(eye_y - 10)), 3)
        
        # Mouth (animated)
        mouth_open = abs(math.sin(progress * 15)) * 15
        mouth_rect = pygame.Rect(int(x - 12), int(y - 5), 24, int(10 + mouth_open))
        pygame.draw.arc(screen, (100, 50, 50), mouth_rect, 0, math.pi, 3)
        
        # Microphone in hand
        mic_x = x + 40
        mic_y = y + 30
        pygame.draw.line(screen, (80, 80, 80), (int(x + 30), int(y + 25)), (int(mic_x), int(mic_y)), 5)
        pygame.draw.circle(screen, (200, 200, 200), (int(mic_x), int(mic_y)), 12)
        pygame.draw.circle(screen, (150, 150, 150), (int(mic_x), int(mic_y)), 8)
        
        # Arms with different actions
        arm_color = head_color
        
        if action == 'point_left':
            # Right arm holding mic
            pygame.draw.line(screen, arm_color, (int(x + 25), int(y + 15)), (int(x + 30), int(y + 25)), 12)
            # Left arm pointing LEFT
            angle = -150 + math.sin(progress * 5) * 10
            arm_end_x = x - 50 + math.cos(math.radians(angle)) * 70
            arm_end_y = y + 20 + math.sin(math.radians(angle)) * 70
            pygame.draw.line(screen, arm_color, (int(x - 25), int(y + 15)), (int(arm_end_x), int(arm_end_y)), 12)
            # Pointing finger
            pygame.draw.circle(screen, arm_color, (int(arm_end_x), int(arm_end_y)), 6)
            
        elif action == 'point_right':
            # Left arm holding mic (switched)
            pygame.draw.line(screen, arm_color, (int(x - 25), int(y + 15)), (int(x - 30), int(y + 25)), 12)
            # Right arm pointing RIGHT
            angle = -30 + math.sin(progress * 5) * 10
            arm_end_x = x + 50 + math.cos(math.radians(angle)) * 70
            arm_end_y = y + 20 + math.sin(math.radians(angle)) * 70
            pygame.draw.line(screen, arm_color, (int(x + 25), int(y + 15)), (int(arm_end_x), int(arm_end_y)), 12)
            # Pointing finger
            pygame.draw.circle(screen, arm_color, (int(arm_end_x), int(arm_end_y)), 6)
            
        elif action == 'point_up':
            # Right arm holding mic
            pygame.draw.line(screen, arm_color, (int(x + 25), int(y + 15)), (int(x + 30), int(y + 25)), 12)
            # Left arm pointing UP
            bounce = math.sin(progress * 10) * 15
            pygame.draw.line(screen, arm_color, (int(x - 25), int(y + 15)), (int(x - 20), int(y - 60 + bounce)), 12)
            # Pointing finger
            pygame.draw.circle(screen, arm_color, (int(x - 20), int(y - 60 + bounce)), 6)
            
        elif action == 'point_center':
            # Right arm holding mic
            pygame.draw.line(screen, arm_color, (int(x + 25), int(y + 15)), (int(x + 30), int(y + 25)), 12)
            # Left arm pointing at screen center
            center_point_x = WIDTH // 2
            center_point_y = HEIGHT // 2
            pygame.draw.line(screen, arm_color, (int(x - 25), int(y + 15)), (int(center_point_x - 100), int(center_point_y)), 12)
            # Pointing finger
            pygame.draw.circle(screen, arm_color, (int(center_point_x - 100), int(center_point_y)), 6)
            
        elif action == 'excited':
            # Both arms up in excitement
            bounce = math.sin(progress * 12) * 20
            pygame.draw.line(screen, arm_color, (int(x - 25), int(y + 15)), (int(x - 40), int(y - 40 + bounce)), 12)
            pygame.draw.line(screen, arm_color, (int(x + 25), int(y + 15)), (int(x + 40), int(y - 40 - bounce)), 12)
            # Hands
            pygame.draw.circle(screen, arm_color, (int(x - 40), int(y - 40 + bounce)), 8)
            pygame.draw.circle(screen, arm_color, (int(x + 40), int(y - 40 - bounce)), 8)
            
        elif action == 'dramatic':
            # Dramatic pose - one arm across chest
            pygame.draw.line(screen, arm_color, (int(x - 25), int(y + 15)), (int(x + 20), int(y + 30)), 12)
            # Other arm extended dramatically
            extend = progress * 100
            pygame.draw.line(screen, arm_color, (int(x + 25), int(y + 15)), (int(x + 60 + extend), int(y - 20)), 12)
            pygame.draw.circle(screen, arm_color, (int(x + 60 + extend), int(y - 20)), 8)
        
        # Speech bubble with text
        if text:
            bubble_x = x + 100
            bubble_y = y - 80
            bubble_width = len(text) * 15 + 40
            bubble_height = 50
            
            # Bubble background
            pygame.draw.ellipse(screen, (255, 255, 255), (int(bubble_x), int(bubble_y), bubble_width, bubble_height))
            pygame.draw.ellipse(screen, (0, 0, 0), (int(bubble_x), int(bubble_y), bubble_width, bubble_height), 3)
            
            # Bubble pointer
            pygame.draw.polygon(screen, (255, 255, 255), [
                (bubble_x, bubble_y + 35),
                (x + 30, y - 10),
                (bubble_x + 20, bubble_y + 30)
            ])
            pygame.draw.line(screen, (0, 0, 0), (int(bubble_x), int(bubble_y + 35)), (int(x + 30), int(y - 10)), 3)
            
            # Text inside bubble
            bubble_text = font.render(text, True, (0, 0, 0))
            screen.blit(bubble_text, (int(bubble_x + 20), int(bubble_y + 15)))
    
    for scene in intro_scenes:
        # Speak the text using macOS 'say' command with GRANDPA VOICE
        # Using "Grandpa" - wise old man telling an epic tale!
        selected_voice = "Grandpa (English (US))"
        
        # Good speed for dramatic effect (140 = slow and wise)
        dramatic_voice = scene['voice']
        speech_rate = 140
        # Start voice in background again, but increase scene duration to match
        os.system(f'say -v "{selected_voice}" -r {speech_rate} "{dramatic_voice}" &')
        
        # Calculate how long the voice will actually take
        word_count = len(dramatic_voice.split())
        voice_duration = (word_count / speech_rate) * 60  # words / words-per-min * 60 seconds
        
        # Use the longer of voice duration or original duration
        actual_duration = max(scene['duration'], voice_duration + 0.5)  # +0.5 second buffer
        
        start_time = pygame.time.get_ticks() / 1000
        
        while (pygame.time.get_ticks() / 1000 - start_time) < actual_duration:
            # Check for skip
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    os.system('killall say')  # Stop voice
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        os.system('killall say')  # Stop voice
                        return  # Skip intro
            
            # Calculate animation progress (0 to 1)
            progress = (pygame.time.get_ticks() / 1000 - start_time) / actual_duration
            
            # Epic cinematic background
            for y in range(HEIGHT):
                # Animated gradient
                time_offset = pygame.time.get_ticks() / 1000
                shade = int(10 + 30 * math.sin(y * 0.01 + time_offset))
                r = max(0, min(255, shade))
                g = max(0, min(255, shade // 2))
                b = max(0, min(255, shade + 20))
                pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
            
            # Draw moving stars/particles
            for i in range(80):
                star_time = (pygame.time.get_ticks() / 50 + i * 10) % WIDTH
                star_x = star_time
                star_y = (i * 137) % HEIGHT
                brightness = int(128 + 127 * math.sin(pygame.time.get_ticks() / 300 + i))
                star_size = 2 + int(math.sin(i) * 2)
                pygame.draw.circle(screen, (brightness, brightness, brightness), (int(star_x), star_y), star_size)
            
            # Draw presenter man
            man_x = 200
            man_y = HEIGHT - 200
            draw_presenter(man_x, man_y, scene['man_action'], scene['man_text'], progress)
            
            # Apply effect based on scene
            if scene['effect'] == 'fade_in':
                alpha = int(255 * progress)
                title_font = pygame.font.Font(None, 120)
                text = title_font.render(scene['text'], True, (255, 255, 255))
                text.set_alpha(alpha)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 60))
            
            elif scene['effect'] == 'zoom':
                scale = 0.5 + (progress * 1.5)
                title_font = pygame.font.Font(None, int(120 * scale))
                text = title_font.render(scene['text'], True, (255, 215, 0))
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            
            elif scene['effect'] == 'pulse':
                pulse = 1 + 0.2 * math.sin(progress * 10)
                title_font = pygame.font.Font(None, int(150 * pulse))
                text = title_font.render(scene['text'], True, (255, 100, 100))
                # Glow effect
                for glow in range(3):
                    glow_surf = text.copy()
                    glow_surf.set_alpha(80 - glow * 20)
                    screen.blit(glow_surf, (WIDTH // 2 - text.get_width() // 2 - glow * 2, HEIGHT // 2 - text.get_height() // 2 - glow * 2))
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            
            elif scene['effect'] == 'shake':
                shake_x = math.sin(progress * 30) * 20
                shake_y = math.cos(progress * 25) * 15
                title_font = pygame.font.Font(None, 140)
                text = title_font.render(scene['text'], True, (255, 50, 50))
                # Add glow for BATTLEGAME
                for glow in range(4):
                    glow_surf = text.copy()
                    glow_surf.set_alpha(100 - glow * 20)
                    screen.blit(glow_surf, (int(WIDTH // 2 - text.get_width() // 2 + shake_x - glow * 3), 
                                           int(HEIGHT // 2 - 50 + shake_y - glow * 3)))
                screen.blit(text, (int(WIDTH // 2 - text.get_width() // 2 + shake_x), int(HEIGHT // 2 - 50 + shake_y)))
            
            elif scene['effect'] == 'spiral':
                angle = progress * 720  # Two full rotations
                title_font = pygame.font.Font(None, 110)
                for i, char in enumerate(scene['text']):
                    char_angle = angle + i * 20
                    radius = 200 * (1 - progress)
                    x = WIDTH // 2 + math.cos(math.radians(char_angle)) * radius
                    y = HEIGHT // 2 + math.sin(math.radians(char_angle)) * radius
                    color_shift = int(128 + 127 * math.sin(i + progress * 10))
                    char_surf = title_font.render(char, True, (color_shift, 255 - color_shift, 255))
                    screen.blit(char_surf, (int(x) - 20, int(y) - 30))
            
            elif scene['effect'] == 'explode':
                # Particles exploding outward
                title_font = pygame.font.Font(None, 160)
                text = title_font.render(scene['text'], True, (255, 255, 100))
                
                # Draw main text with shake
                shake = int(10 * (1 - progress))
                text_x = WIDTH // 2 - text.get_width() // 2 + random.randint(-shake, shake)
                text_y = HEIGHT // 2 - 60 + random.randint(-shake, shake)
                
                # Explosion glow
                for glow in range(5):
                    glow_surf = text.copy()
                    glow_surf.set_alpha(120 - glow * 20)
                    screen.blit(glow_surf, (text_x - glow * 4, text_y - glow * 4))
                
                screen.blit(text, (text_x, text_y))
                
                # Particles
                num_particles = int(progress * 150)
                for i in range(num_particles):
                    angle = (i / num_particles) * 2 * math.pi
                    distance = progress * 400
                    px = int(WIDTH // 2 + math.cos(angle) * distance)
                    py = int(HEIGHT // 2 + math.sin(angle) * distance)
                    particle_color = (255, int(255 * (1 - progress)), 0)
                    particle_size = max(2, int(8 * (1 - progress)))
                    pygame.draw.circle(screen, particle_color, (px, py), particle_size)
            
            # Skip hint
            skip_text = font.render("Press SPACE or ENTER to skip intro", True, (200, 200, 200))
            screen.blit(skip_text, (WIDTH // 2 - skip_text.get_width() // 2, HEIGHT - 50))
            
            pygame.display.flip()
            clock.tick(60)
        
        # Small pause between scenes
        pygame.time.wait(500)
    
    # Final fade to black
    for fade in range(0, 255, 10):
        screen.fill((0, 0, 0))
        fade_surf = pygame.Surface((WIDTH, HEIGHT))
        fade_surf.set_alpha(fade)
        fade_surf.fill((0, 0, 0))
        screen.blit(fade_surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    
    # Make sure voice is stopped
    os.system('killall say')

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

# Shop/Purchase functions
def load_purchases():
    """Load purchased items - now session-based, resets every time game starts"""
    # Don't load from file - purchases reset each session!
    return {'relax_mode': False, 'shop_unlocked': False}

def save_purchase(item_name):
    """Save a purchased item - only for current session"""
    # Don't save to file - just return updated dict for this session
    purchases = load_purchases()
    purchases[item_name] = True
    return purchases

def unlock_shop():
    """Unlock the shop with secret code"""
    global session_purchases
    session_purchases['shop_unlocked'] = True

# Track unlock progress
unlock_progress = {
    'found_secret_game': False,
    'clicked_shop_word': False,
    'entered_lllooolll': False,
    'answered_math': False
}

def do_mom_jumpscare(initial_message="SHE CAUGHT YOU!"):
    """The ULTRA TERRIFYING mom jumpscare from Escape Mom Mode!"""
    # Play scary scream sound at MAXIMUM VOLUME
    try:
        pygame.mixer.music.load(resource_path("scary-scream.mp3"))
        pygame.mixer.music.set_volume(1.0)  # MAX VOLUME!
        pygame.mixer.music.play()
    except:
        # Fallback to system beeps
        for _ in range(20):
            print("\a")  # System beep
    
    jumpscare_time = time.time()
    jumpscare_duration = 4.5  # 4.5 seconds of PURE TERROR
    
    while time.time() - jumpscare_time < jumpscare_duration:
        elapsed = time.time() - jumpscare_time
        progress = elapsed / jumpscare_duration
        
        # INTENSE rapid flashing for shock effect
        flash_speed = int((time.time() - jumpscare_time) * 40)
        if flash_speed % 2 == 0:
            screen.fill((0, 0, 0))
        else:
            red_intensity = int(150 + progress * 105)
            screen.fill((red_intensity, 0, 0))
        
        # SCREEN INVERSION effect
        if int(elapsed * 20) % 7 < 2:
            screen.fill((255, 255, 255))  # Blinding white flash
        
        # Static noise effect
        if random.random() < 0.6:
            for i in range(400):
                static_x = random.randint(0, WIDTH)
                static_y = random.randint(0, HEIGHT)
                static_color = random.randint(0, 255)
                pygame.draw.circle(screen, (static_color, 0, 0), (static_x, static_y), random.randint(1, 3))
        
        # GLITCH LINES
        for i in range(random.randint(5, 15)):
            glitch_y = random.randint(0, HEIGHT)
            glitch_height = random.randint(2, 20)
            glitch_color = (random.randint(200, 255), 0, 0)
            pygame.draw.rect(screen, glitch_color, (0, glitch_y, WIDTH, glitch_height))
        
        # Mom grows MASSIVE and DISTORTED
        scale = 40 + (progress * 30)
        face_size = int(600 * scale / 40)
        
        # FACE LUNGES AT YOU
        lunge_offset = int(progress * 150)
        face_x = WIDTH // 2 + random.randint(-15, 15) + int(math.sin(elapsed * 10) * 20)
        face_y = HEIGHT // 2 + random.randint(-15, 15) - lunge_offset
        
        # GROTESQUE HEAD with pulsing veins
        pulse = int(15 * math.sin(elapsed * 20))
        
        # Multiple layers of rotting skin
        for layer in range(3):
            layer_size = face_size//2 + pulse - (layer * 15)
            decay_color = (
                220 + int(35 * progress) - layer * 20,
                140 - int(80 * progress) - layer * 30,
                140 - int(80 * progress) - layer * 30
            )
            pygame.draw.circle(screen, decay_color, (face_x, face_y), layer_size)
        
        # Rotting flesh effect
        for i in range(100):
            rot_x = face_x + random.randint(-face_size//2, face_size//2)
            rot_y = face_y + random.randint(-face_size//2, face_size//2)
            rot_color = random.choice([
                (120, 80, 60),
                (100, 60, 40),
                (80, 40, 20),
                (60, 20, 10)
            ])
            pygame.draw.circle(screen, rot_color, (rot_x, rot_y), random.randint(3, 15))
        
        # ENORMOUS BLOODSHOT DEMON EYES
        eye_size = int(140 + progress * 70)
        eye_spacing = int(180 + progress * 60)
        eye_offset_x = int(math.sin(elapsed * 6) * 10)
        eye_offset_y = int(math.cos(elapsed * 6) * 10)
        
        # Left eye
        pygame.draw.ellipse(screen, (255, 255, 180), (face_x - eye_spacing - eye_size//2, face_y - 140, eye_size, eye_size + 50))
        
        # Blood veins in left eye
        for i in range(60):
            vein_angle = random.random() * 6.28
            vein_length = random.randint(30, eye_size//2)
            vein_start_x = face_x - eye_spacing
            vein_start_y = face_y - 90
            vein_end_x = int(vein_start_x + math.cos(vein_angle) * vein_length)
            vein_end_y = int(vein_start_y + math.sin(vein_angle) * vein_length)
            vein_thickness = random.randint(2, 6)
            pygame.draw.line(screen, (200, 0, 0), (vein_start_x, vein_start_y), (vein_end_x, vein_end_y), vein_thickness)
        
        # Iris and pupil (left)
        iris_size = int(70 + progress * 30 + pulse)
        iris_x = face_x - eye_spacing + eye_offset_x
        iris_y = face_y - 90 + eye_offset_y
        pygame.draw.circle(screen, (255, 0, 0), (iris_x, iris_y), iris_size)
        pygame.draw.circle(screen, (220, 0, 0), (iris_x, iris_y), iris_size - 10)
        pygame.draw.circle(screen, (180, 0, 0), (iris_x, iris_y), iris_size - 20)
        pupil_size = int(40 + progress * 20)
        pygame.draw.circle(screen, (0, 0, 0), (iris_x, iris_y), pupil_size)
        
        # Right eye
        pygame.draw.ellipse(screen, (255, 255, 180), (face_x + eye_spacing - eye_size//2, face_y - 140, eye_size, eye_size + 50))
        
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
        
        # GAPING MOUTH - grows IMPOSSIBLY WIDE
        mouth_width = int(250 + progress * 150)
        mouth_height = int(220 + progress * 120)
        mouth_y = int(face_y + 40 - progress * 30)
        
        # Throat of darkness
        pygame.draw.ellipse(screen, (0, 0, 0), (face_x - mouth_width//2, mouth_y, mouth_width, mouth_height))
        pygame.draw.ellipse(screen, (10, 0, 0), (face_x - mouth_width//2 + 30, mouth_y + 30, mouth_width - 60, mouth_height - 60))
        
        # HORRIFYING SHARP TEETH
        teeth_count = 20
        for i in range(teeth_count):
            tooth_x = face_x - mouth_width//2 + 30 + i * (mouth_width - 60) // teeth_count
            tooth_width = 18
            tooth_height = int(45 + progress * 30)
            pygame.draw.polygon(screen, (255, 255, 200), [
                (tooth_x, mouth_y + 10),
                (tooth_x + tooth_width, mouth_y + 10),
                (tooth_x + tooth_width//2, mouth_y + tooth_height)
            ])
            
            # Bottom teeth
            tooth_x_bottom = face_x - mouth_width//2 + 40 + i * (mouth_width - 80) // teeth_count
            pygame.draw.polygon(screen, (255, 255, 200), [
                (tooth_x_bottom, mouth_y + mouth_height - tooth_height),
                (tooth_x_bottom + tooth_width, mouth_y + mouth_height - tooth_height),
                (tooth_x_bottom + tooth_width//2, mouth_y + mouth_height - 10)
            ])
        
        # EXTREME shake effect
        shake_intensity = int(25 + progress * 50)
        shake_x = random.randint(-shake_intensity, shake_intensity)
        shake_y = random.randint(-shake_intensity, shake_intensity)
        
        # TERRIFYING text messages
        text_shake_x = shake_x + random.randint(-10, 10)
        text_shake_y = shake_y + random.randint(-10, 10)
        
        if progress < 0.25:
            jumpscare_text = lobby_font.render(initial_message, True, (255, 255, 255))
            screen.blit(jumpscare_text, (WIDTH//2 - jumpscare_text.get_width()//2 + text_shake_x, 60 + text_shake_y))
        elif progress < 0.5:
            jumpscare_text = lobby_font.render("NO ESCAPE!", True, (255, 200, 200))
            screen.blit(jumpscare_text, (WIDTH//2 - jumpscare_text.get_width()//2 + text_shake_x, 60 + text_shake_y))
        elif progress < 0.75:
            jumpscare_text = lobby_font.render("SHE'S WATCHING!", True, (255, int(50 + progress * 200), int(50 + progress * 200)))
            screen.blit(jumpscare_text, (WIDTH//2 - jumpscare_text.get_width()//2 + text_shake_x, 60 + text_shake_y))
        else:
            jumpscare_text = lobby_font.render("START OVER!", True, (200, 0, 0))
            screen.blit(jumpscare_text, (WIDTH//2 - jumpscare_text.get_width()//2 + text_shake_x, 60 + text_shake_y))
        
        pygame.display.flip()
        clock.tick(60)
    
    # Stop the scream
    try:
        pygame.mixer.music.stop()
    except:
        pass

def secret_hunt_game():
    """Secret game where you need to find and click 'shop' text"""
    global unlock_progress
    
    running = True
    # Random positions for distraction texts
    import random
    
    # Create many random texts, one of which is "shop"
    texts = []
    shop_rect = None
    text_rects = []  # Store all text rects for wrong click detection
    
    for i in range(30):
        random_words = ["game", "mode", "coin", "battle", "fun", "play", "wolf", "secret", "code", "hidden"]
        word = random.choice(random_words)
        x = random.randint(50, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        texts.append({'word': word, 'x': x, 'y': y, 'color': (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))})
    
    # Add the special "shop" text in a random position
    shop_x = random.randint(200, WIDTH - 200)
    shop_y = random.randint(200, HEIGHT - 200)
    texts.append({'word': 'shop', 'x': shop_x, 'y': shop_y, 'color': (255, 50, 255)})
    
    # Shuffle so shop isn't last
    random.shuffle(texts)
    
    while running:
        screen.fill((10, 10, 30))
        
        # Title
        title = lobby_font.render("??? SECRET SPACE ???", True, (100, 255, 100))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        
        hint = name_font.render("Find something interesting...", True, (150, 150, 150))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 70))
        
        # Clear text_rects for this frame
        text_rects = []
        
        # Draw all texts
        for text_data in texts:
            text_surf = font.render(text_data['word'], True, text_data['color'])
            text_rect = text_surf.get_rect(topleft=(text_data['x'], text_data['y']))
            screen.blit(text_surf, text_rect)
            
            # Store all rects for click detection
            text_rects.append({'rect': text_rect, 'word': text_data['word']})
            
            # Store shop rect for click detection
            if text_data['word'] == 'shop':
                shop_rect = text_rect
        
        # Exit hint
        exit_hint = name_font.render("Press ESC to exit", True, (100, 100, 100))
        screen.blit(exit_hint, (WIDTH//2 - exit_hint.get_width()//2, HEIGHT - 40))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if clicked on shop
                if shop_rect and shop_rect.collidepoint(event.pos):
                    unlock_progress['clicked_shop_word'] = True
                    # Show success message
                    screen.fill((10, 10, 30))
                    success = lobby_font.render("✓ YOU FOUND IT!", True, (100, 255, 100))
                    screen.blit(success, (WIDTH//2 - success.get_width()//2, HEIGHT//2 - 40))
                    hint_text = font.render("Now exit and continue your journey...", True, (200, 200, 200))
                    screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, HEIGHT//2 + 20))
                    pygame.display.flip()
                    pygame.time.wait(2000)
                    running = False
                else:
                    # Check if clicked on ANY other word (wrong word)
                    clicked_wrong = False
                    for text_info in text_rects:
                        if text_info['word'] != 'shop' and text_info['rect'].collidepoint(event.pos):
                            clicked_wrong = True
                            break
                    
                    if clicked_wrong:
                        # FULL MOM MODE JUMPSCARE!
                        do_mom_jumpscare("WRONG WORD!!!")
                        
                        # Reset progress and return to main menu
                        unlock_progress['found_secret_game'] = False
                        unlock_progress['clicked_shop_word'] = False
                        unlock_progress['entered_lllooolll'] = False
                        unlock_progress['answered_math'] = False
                        
                        # Show message
                        screen.fill((50, 0, 0))
                        reset_text = lobby_font.render("PROGRESS RESET!", True, (255, 50, 50))
                        screen.blit(reset_text, (WIDTH//2 - reset_text.get_width()//2, HEIGHT//2 - 40))
                        back_text = font.render("Returning to main menu...", True, (200, 200, 200))
                        screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT//2 + 20))
                        pygame.display.flip()
                        pygame.time.wait(2000)
                        
                        running = False
                        # The function will return and shop_menu will close, going back to main menu
                    running = False

def math_challenge():
    """Show impossible math question, but real answer is xxxzzzccc"""
    global unlock_progress, session_purchases
    
    running = True
    answer_input = ""
    code_input = ""
    
    while running:
        screen.fill((40, 10, 10))
        
        # Scary title
        title = lobby_font.render("🔢 FINAL CHALLENGE 🔢", True, (255, 100, 100))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # The impossible math question
        question = lobby_font.render("3666373 × 6736746 = ?", True, (255, 255, 100))
        screen.blit(question, (WIDTH//2 - question.get_width()//2, 200))
        
        warning = name_font.render("(You must solve this to unlock the shop)", True, (200, 100, 100))
        screen.blit(warning, (WIDTH//2 - warning.get_width()//2, 260))
        
        # Show input
        input_box = pygame.Rect(WIDTH//2 - 200, 350, 400, 50)
        pygame.draw.rect(screen, (50, 50, 50), input_box)
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)
        
        answer_text = font.render(answer_input, True, (255, 255, 255))
        screen.blit(answer_text, (input_box.x + 10, input_box.y + 10))
        
        hint = name_font.render("Type your answer and press ENTER", True, (150, 150, 150))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 420))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Secret code detection (xxxzzzccc)
                if event.unicode and event.unicode.isprintable():
                    code_input += event.unicode
                    answer_input += event.unicode
                    # Keep only last 9 characters for code
                    if len(code_input) > 9:
                        code_input = code_input[-9:]
                    # Check for secret bypass code
                    if code_input.endswith("xxxzzzccc"):
                        unlock_progress['answered_math'] = True
                        session_purchases['shop_unlocked'] = True
                        # Epic unlock animation!
                        screen.fill((10, 50, 10))
                        unlock1 = lobby_font.render("🎉 YOU DISCOVERED THE SECRET! 🎉", True, (100, 255, 100))
                        screen.blit(unlock1, (WIDTH//2 - unlock1.get_width()//2, HEIGHT//2 - 100))
                        unlock2 = font.render("You didn't need to solve the math...", True, (200, 255, 200))
                        screen.blit(unlock2, (WIDTH//2 - unlock2.get_width()//2, HEIGHT//2 - 40))
                        unlock3 = font.render("The real answer was typing: xxxzzzccc", True, (255, 255, 100))
                        screen.blit(unlock3, (WIDTH//2 - unlock3.get_width()//2, HEIGHT//2))
                        unlock4 = lobby_font.render("🔓 SHOP UNLOCKED! 🔓", True, (255, 215, 0))
                        screen.blit(unlock4, (WIDTH//2 - unlock4.get_width()//2, HEIGHT//2 + 60))
                        pygame.display.flip()
                        pygame.time.wait(4000)
                        running = False
                        return
                
                if event.key == pygame.K_BACKSPACE:
                    answer_input = answer_input[:-1]
                elif event.key == pygame.K_RETURN:
                    # Check if they actually calculated it (won't work!)
                    try:
                        user_answer = int(answer_input)
                        correct_answer = 3666373 * 6736746
                        if user_answer == correct_answer:
                            # Even correct answer doesn't unlock!
                            screen.fill((40, 10, 10))
                            fail = lobby_font.render("🤔 CORRECT... BUT...", True, (255, 200, 100))
                            screen.blit(fail, (WIDTH//2 - fail.get_width()//2, HEIGHT//2 - 40))
                            fail2 = font.render("Something seems off... Try again?", True, (200, 200, 200))
                            screen.blit(fail2, (WIDTH//2 - fail2.get_width()//2, HEIGHT//2 + 20))
                            pygame.display.flip()
                            pygame.time.wait(2000)
                            answer_input = ""
                            code_input = ""
                        else:
                            # Wrong answer
                            screen.fill((40, 10, 10))
                            fail = lobby_font.render("❌ WRONG!", True, (255, 50, 50))
                            screen.blit(fail, (WIDTH//2 - fail.get_width()//2, HEIGHT//2))
                            pygame.display.flip()
                            pygame.time.wait(1000)
                            answer_input = ""
                            code_input = ""
                    except ValueError:
                        # Not a number
                        answer_input = ""
                        code_input = ""
                
                elif event.key == pygame.K_ESCAPE:
                    running = False

def shop_menu():
    """Display the shop where players can buy features - requires complex secret hunt!"""
    global session_purchases, unlock_progress
    
    # Check if shop is unlocked
    if not session_purchases.get('shop_unlocked', False):
        # Show cryptic locked message
        running = True
        code_input = ""  # Track secret code input
        while running:
            screen.fill((20, 20, 40))
            
            # Locked title
            title_text = lobby_font.render("🔒 SHOP LOCKED", True, (255, 50, 50))
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 150))
            
            # Show cryptic hints based on progress
            y_pos = 250
            
            if not unlock_progress['found_secret_game']:
                hint1 = font.render("The journey begins with three of the same...", True, (200, 200, 200))
                screen.blit(hint1, (WIDTH//2 - hint1.get_width()//2, y_pos))
                hint2 = name_font.render("Think simple... just three.", True, (100, 100, 150))
                screen.blit(hint2, (WIDTH//2 - hint2.get_width()//2, y_pos + 35))
            elif not unlock_progress['clicked_shop_word']:
                hint1 = font.render("✓ Secret space discovered!", True, (100, 255, 100))
                screen.blit(hint1, (WIDTH//2 - hint1.get_width()//2, y_pos))
                hint2 = font.render("Find the word you seek in the secret space...", True, (200, 200, 200))
                screen.blit(hint2, (WIDTH//2 - hint2.get_width()//2, y_pos + 35))
            elif not unlock_progress['entered_lllooolll']:
                hint1 = font.render("✓ Secret word found!", True, (100, 255, 100))
                screen.blit(hint1, (WIDTH//2 - hint1.get_width()//2, y_pos))
                hint2 = font.render("Now... what makes wolves dance?", True, (200, 200, 200))
                screen.blit(hint2, (WIDTH//2 - hint2.get_width()//2, y_pos + 35))
                hint3 = name_font.render("(Remember Makka Pakka Mode...)", True, (100, 100, 150))
                screen.blit(hint3, (WIDTH//2 - hint3.get_width()//2, y_pos + 70))
            else:
                hint1 = font.render("✓ All steps complete!", True, (100, 255, 100))
                screen.blit(hint1, (WIDTH//2 - hint1.get_width()//2, y_pos))
                hint2 = font.render("Solve the final challenge...", True, (200, 200, 200))
                screen.blit(hint2, (WIDTH//2 - hint2.get_width()//2, y_pos + 35))
            
            # Warning
            warning = font.render("⚠️ This shop is VERY well hidden... ⚠️", True, (255, 100, 100))
            screen.blit(warning, (WIDTH//2 - warning.get_width()//2, 450))
            
            # Back button
            back_button = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 60)
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
                    # Secret code detection
                    if event.unicode and event.unicode.isprintable():
                        code_input += event.unicode
                        # Keep only last 9 characters
                        if len(code_input) > 9:
                            code_input = code_input[-9:]
                        
                        # Debug: Show what's being typed (for testing)
                        print(f"Code input: {code_input}")
                        
                        # Step 1: Check for "ttt" to enter secret game
                        if "ttt" in code_input and not unlock_progress['found_secret_game']:
                            unlock_progress['found_secret_game'] = True
                            code_input = ""
                            secret_hunt_game()  # Launch secret game
                            # After returning from secret game, don't break the loop
                            # just continue showing the locked screen with updated progress
                        
                        # Step 2: Check for "lllooolll" after finding shop word
                        elif "lllooolll" in code_input and unlock_progress['clicked_shop_word'] and not unlock_progress['entered_lllooolll']:
                            unlock_progress['entered_lllooolll'] = True
                            code_input = ""
                            # Show progress message
                            screen.fill((20, 20, 40))
                            progress = lobby_font.render("✓ CODE ACCEPTED!", True, (100, 255, 100))
                            screen.blit(progress, (WIDTH//2 - progress.get_width()//2, HEIGHT//2 - 40))
                            next_text = font.render("Proceeding to final challenge...", True, (255, 255, 255))
                            screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 20))
                            pygame.display.flip()
                            pygame.time.wait(2000)
                            # Launch math challenge
                            math_challenge()
                            # After math challenge, check if unlocked and exit
                            if session_purchases.get('shop_unlocked', False):
                                running = False
                    
                    if event.key == pygame.K_ESCAPE:
                        running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        running = False
        
        # If shop was just unlocked, call shop_menu again to show the shop
        if session_purchases.get('shop_unlocked', False):
            shop_menu()
        return
    
    # Shop is unlocked - show shop
    running = True
    scroll_offset = 0  # For scrolling through items
    
    # Define all shop items
    shop_items = [
        {'name': 'Relax Mode', 'key': 'relax_mode', 'price': '0 NOK (FREE!)', 'desc': 'Peaceful sheep counting, letter rain, satisfaction games!'},
        {'name': 'Makka Pakka Mode', 'key': 'makka_pakka_mode', 'price': '0 NOK (FREE!)', 'desc': 'Wash faces and steal them from your opponent!'},
        {'name': 'Escape Mom Mode', 'key': 'escape_mom_mode', 'price': '0 NOK (FREE!)', 'desc': 'SCARY! Run from an angry mother in dark corridors!'},
        {'name': 'Capture the Flag', 'key': 'capture_flag_mode', 'price': '0 NOK (FREE!)', 'desc': 'Team-based flag capture action!'},
        {'name': 'Survival Mode', 'key': 'survival_mode', 'price': '0 NOK (FREE!)', 'desc': 'Survive endless waves of enemies!'},
        {'name': '3D Adventure', 'key': 'adventure_3d_mode', 'price': '0 NOK (FREE!)', 'desc': 'Explore a 3D world!'},
        {'name': 'Dilly Dolly Mode', 'key': 'dilly_dolly_mode', 'price': '0 NOK (FREE!)', 'desc': 'The simple Dilly Dolly experience!'},
    ]
    
    while running:
        screen.fill((20, 20, 40))
        
        # Title
        title_text = lobby_font.render("🛒 SECRET SHOP", True, (255, 215, 0))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 30))
        
        subtitle = font.render("All Game Modes Unlocked - FREE!", True, (100, 255, 100))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 90))
        
        # Display items
        y_pos = 150
        for idx, item in enumerate(shop_items):
            if session_purchases.get(item['key'], False):
                # Already purchased
                status_text = font.render(f"✅ {item['name']} - UNLOCKED!", True, (100, 255, 100))
                screen.blit(status_text, (WIDTH//2 - status_text.get_width()//2, y_pos))
            else:
                # Not purchased yet - show buy button
                item_text = font.render(f"🔒 {item['name']}", True, (255, 255, 255))
                screen.blit(item_text, (WIDTH//2 - item_text.get_width()//2, y_pos))
                
                desc_text = name_font.render(item['desc'], True, (200, 200, 200))
                screen.blit(desc_text, (WIDTH//2 - desc_text.get_width()//2, y_pos + 30))
                
                # Buy button
                buy_button = pygame.Rect(WIDTH//2 - 100, y_pos + 55, 200, 40)
                pygame.draw.rect(screen, (50, 150, 50), buy_button)
                pygame.draw.rect(screen, (100, 255, 100), buy_button, 3)
                buy_text = font.render("UNLOCK FREE", True, (255, 255, 255))
                screen.blit(buy_text, (buy_button.centerx - buy_text.get_width()//2, 
                                      buy_button.centery - buy_text.get_height()//2))
                
                # Store button rect for click detection
                item['button_rect'] = buy_button
            
            y_pos += 110
        
        # Info text
        info1 = font.render("🎉 You unlocked the secret shop! All modes are FREE!", True, (255, 215, 0))
        screen.blit(info1, (WIDTH//2 - info1.get_width()//2, HEIGHT - 150))
        
        info2 = name_font.render("(Unlocks reset when you restart the game)", True, (150, 150, 150))
        screen.blit(info2, (WIDTH//2 - info2.get_width()//2, HEIGHT - 120))
        
        # Back button
        back_button = pygame.Rect(WIDTH//2 - 100, HEIGHT - 80, 200, 50)
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
                else:
                    # Check if any buy button was clicked
                    for item in shop_items:
                        if not session_purchases.get(item['key'], False) and 'button_rect' in item:
                            if item['button_rect'].collidepoint(event.pos):
                                # Purchase confirmed!
                                session_purchases[item['key']] = True
                                # Show unlock message
                                screen.fill((20, 20, 40))
                                unlock_text = lobby_font.render(f"✅ {item['name']} UNLOCKED!", True, (100, 255, 100))
                                screen.blit(unlock_text, (WIDTH//2 - unlock_text.get_width()//2, HEIGHT//2 - 40))
                                enjoy = font.render("Enjoy your new game mode!", True, (200, 200, 200))
                                screen.blit(enjoy, (WIDTH//2 - enjoy.get_width()//2, HEIGHT//2 + 20))
                                pygame.display.flip()
                                pygame.time.wait(1500)

def show_locked_message():
    """Show message that a game mode is locked"""
    running = True
    while running:
        screen.fill((30, 20, 20))
        
        # Locked icon
        lock_text = pygame.font.SysFont(None, 150).render("🔒", True, (255, 100, 100))
        screen.blit(lock_text, (WIDTH//2 - lock_text.get_width()//2, 100))
        
        # Message
        title = lobby_font.render("MODE LOCKED", True, (255, 100, 100))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 280))
        
        msg1 = font.render("Visit the 🛒 Shop to unlock this game mode", True, (200, 200, 200))
        screen.blit(msg1, (WIDTH//2 - msg1.get_width()//2, 350))
        
        msg2 = font.render("But first... you must unlock the shop itself!", True, (255, 215, 0))
        screen.blit(msg2, (WIDTH//2 - msg2.get_width()//2, 390))
        
        price = pygame.font.SysFont(None, 70).render("FREE when unlocked!", True, (100, 255, 100))
        screen.blit(price, (WIDTH//2 - price.get_width()//2, 440))
        
        # OK button
        ok_button = pygame.Rect(WIDTH//2 - 100, HEIGHT - 150, 200, 60)
        pygame.draw.rect(screen, (100, 50, 150), ok_button)
        pygame.draw.rect(screen, (150, 100, 200), ok_button, 3)
        ok_text = font.render("OK", True, (255, 255, 255))
        screen.blit(ok_text, (ok_button.centerx - ok_text.get_width()//2, 
                              ok_button.centery - ok_text.get_height()//2))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ok_button.collidepoint(event.pos):
                    running = False

def final_mode():
    """FINAL MODE - The ULTIMATE 3D ultra-realistic MEGA experience!
    MASSIVE scale, photorealistic 3D graphics with TRUE DEPTH, epic gameplay, boss battles!"""
    import random
    import math
    
    clock = pygame.time.Clock()
    
    # MASSIVE WORLD STATE - TRUE 3D PERSPECTIVE with depth sorting
    camera_x = 0  # World camera position X
    camera_z = -800  # Camera distance from player (3D depth)
    world_size = 5000  # MASSIVE world width
    horizon_y = HEIGHT // 4  # Horizon line for 3D perspective
    fov = 600  # Field of view for 3D projection
    
    # ULTRA-REALISTIC WORLD STATE - Dynamic environment
    time_of_day = 0.5  # 0=midnight, 0.5=noon, 1=midnight (cycles)
    weather = 'clear'  # clear, rain, storm, fog, snow
    wind_strength = 0.0
    wind_direction = 0.0
    
    # PLAYER - MASSIVE & Ultra detailed with TRUE 3D position
    player = {
        'x': 0,  # World X position
        'y': 0,  # World Y position (0 = ground level)
        'z': 0,  # World Z position (depth, 0 = center)
        'vx': 0,
        'vy': 0,
        'vz': 0,
        'size': 80,  # Base size (scales with depth)
        'health': 300,  # Much more health
        'max_health': 300,
        'stamina': 150,
        'max_stamina': 150,
        'energy': 150,
        'max_energy': 150,
        'shield': 0,  # Shield points
        'max_shield': 100,
        'attack_power': 25,
        'attack_cooldown': 0,
        'invincible': 0,
        'special_attack_cooldown': 0,
        'rage_mode': 0,  # Rage mode timer
    }
    
    # CAMERA SYSTEM - Cinematic with 3D shake and dynamic effects
    camera_shake = 0
    camera_shake_x = 0
    camera_shake_y = 0
    camera_zoom = 1.0
    camera_target_zoom = 1.0
    camera_rotation = 0
    motion_blur = 0
    
    # Helper function for 3D to 2D projection (TRUE PERSPECTIVE)
    def project_3d(world_x, world_y, world_z):
        """Project 3D world coordinates to 2D screen coordinates with perspective"""
        # Relative to camera
        rel_x = world_x - camera_x
        rel_z = world_z - camera_z
        
        # Perspective division
        if rel_z > 10:  # Avoid division by zero
            scale = fov / rel_z
            screen_x = WIDTH // 2 + rel_x * scale
            screen_y = horizon_y + world_y * scale
            return int(screen_x), int(screen_y), scale
        return None, None, 0
    
    # MASSIVE WORLD ENVIRONMENT - Hyper detailed with TRUE 3D depth
    grass_blades = []
    for _ in range(2000):  # MASSIVE amount of grass!
        grass_blades.append({
            'x': random.randint(-world_size // 2, world_size // 2),
            'y': 0,  # Ground level
            'z': random.randint(-500, 2000),  # 3D depth
            'height': random.randint(20, 60),
            'sway': random.uniform(0, 2 * math.pi),
            'sway_speed': random.uniform(0.5, 2.0),
            'color_variation': random.randint(-20, 20),
        })
    
    # REALISTIC TREES - 3D with proper depth
    trees = []
    for _ in range(30):  # More trees!
        trees.append({
            'x': random.randint(-world_size // 2, world_size // 2),
            'y': 0,
            'z': random.randint(100, 1500),  # 3D depth
            'height': random.randint(150, 350),
            'width': random.randint(50, 100),
            'trunk_width': random.randint(20, 40),
            'sway': random.uniform(0, 2 * math.pi),
            'leaves_density': random.randint(8, 15),
        })
    
    # MOUNTAINS - 3D background with multiple layers
    mountains = []
    for layer in range(3):  # Multiple mountain layers for depth
        for _ in range(6):
            mountains.append({
                'x': random.randint(-world_size, world_size * 2),
                'y': 0,
                'z': 3000 + layer * 2000,  # Far in the background
                'height': random.randint(300, 800) - layer * 100,
                'width': random.randint(400, 1000),
                'layer': layer,
            })
    
    # ATMOSPHERIC ELEMENTS - Way more with 3D depth!
    particles = []
    clouds = []
    for _ in range(25):  # More clouds with depth
        clouds.append({
            'x': random.randint(-world_size, world_size * 2),
            'y': random.randint(-100, 100),
            'z': random.randint(1000, 4000),  # 3D depth
            'speed': random.uniform(0.3, 1.2),
            'size': random.randint(150, 400),
            'opacity': random.randint(180, 255),
            'puffiness': random.randint(3, 7),
        })
    
    # VOLUMETRIC LIGHT RAYS - God rays with 3D depth
    light_rays = []
    for _ in range(40):
        light_rays.append({
            'x': random.randint(-world_size, world_size * 2),
            'z': random.randint(500, 3000),
            'width': random.randint(80, 200),
            'opacity': random.randint(30, 80),
            'speed': random.uniform(0.05, 0.2),
            'angle': random.uniform(-0.3, 0.3),
        })
    
    # ROCKS and OBSTACLES - 3D positioned
    rocks = []
    for _ in range(40):
        rocks.append({
            'x': random.randint(-world_size // 2, world_size // 2),
            'y': 0,
            'z': random.randint(-200, 800),
            'size': random.randint(30, 80),
            'color_variation': random.randint(-30, 30),
        })
    
    # OBJECTIVES & COLLECTIBLES - BIGGER & MORE with 3D!
    collectibles = []
    enemies = []
    bosses = []  # BOSS ENEMIES!
    explosions = []  # Visual effects
    powerups = []
    projectiles = []  # Enemy and player projectiles
    
    # Spawn initial collectibles (MASSIVE coins/gems in 3D space)
    for _ in range(50):  # Way more collectibles
        collectibles.append({
            'x': random.randint(-world_size // 2, world_size // 2),
            'y': random.randint(0, 150),  # Can be floating!
            'z': random.randint(-200, 1000),  # 3D depth
            'collected': False,
            'type': random.choice(['coin', 'gem', 'star', 'diamond', 'crystal']),
            'value': random.choice([100, 250, 500, 1000, 2500]),
            'bounce': random.uniform(0, 2 * math.pi),
            'rotation': random.uniform(0, 2 * math.pi),
            'size': random.randint(25, 50),  # Much bigger
            'glow': random.randint(5, 15),
        })
    
    # Spawn initial enemies - BIGGER & MORE DETAILED with 3D AI!
    enemy_types = [
        {'type': 'goblin', 'health': 3, 'size': 60, 'speed': 2, 'color': (100, 180, 100)},
        {'type': 'orc', 'health': 5, 'size': 90, 'speed': 1.5, 'color': (120, 80, 80)},
        {'type': 'demon', 'health': 7, 'size': 110, 'speed': 2.5, 'color': (200, 50, 50)},
        {'type': 'dragon', 'health': 10, 'size': 140, 'speed': 1.8, 'color': (180, 0, 180)},
        {'type': 'wraith', 'health': 4, 'size': 70, 'speed': 3, 'color': (100, 100, 200)},
    ]
    
    for _ in range(15):  # More enemies
        enemy_type = random.choice(enemy_types)
        enemies.append({
            'x': random.randint(-world_size // 2, world_size // 2),
            'y': 0,
            'z': random.randint(-100, 600),  # 3D depth
            'vx': random.uniform(-2, 2),
            'vz': random.uniform(-0.5, 0.5),
            'type': enemy_type['type'],
            'health': enemy_type['health'],
            'max_health': enemy_type['health'],
            'size': enemy_type['size'],
            'base_size': enemy_type['size'],
            'speed': enemy_type['speed'],
            'color': enemy_type['color'],
            'attack_timer': random.uniform(0, 3),
            'animation_frame': 0,
            'ai_state': 'patrol',  # patrol, chase, attack, flee
            'ai_timer': 0,
        })
    
    objectives_completed = 0
    total_objectives = 15  # More objectives
    
    # SCORE & TIME - Enhanced tracking
    score = 0
    coins_collected = 0
    enemies_defeated = 0
    bosses_defeated = 0
    time_elapsed = 0
    combo_multiplier = 1.0
    combo_timer = 0
    max_combo = 0
    
    # ULTRA-REALISTIC PHYSICS - 3D enhanced
    gravity = 1.2
    friction = 0.88
    air_resistance = 0.94
    ground_friction = 0.75
    
    # SPECIAL EFFECTS
    screen_flash = 0
    screen_flash_color = (255, 255, 255)
    rumble_timer = 0
    slow_motion = 1.0  # Slow motion effect
    
    running = True
    frame_count = 0
    boss_spawned = False
    
    # EPIC INTRO SEQUENCE - MUCH LONGER AND MORE CINEMATIC!
    intro_duration = 150  # Longer intro
    for fade_frame in range(intro_duration):
        # Animated gradient background with depth
        t = fade_frame / intro_duration
        bg_color = (
            int(10 + t * 30 + math.sin(fade_frame * 0.1) * 10),
            int(5 + t * 25 + math.sin(fade_frame * 0.15) * 10),
            int(20 + t * 60 + math.sin(fade_frame * 0.2) * 15)
        )
        screen.fill(bg_color)
        
        # Parallax star field
        if fade_frame > 20:
            for i in range(100):
                star_t = (fade_frame - 20 + i * 7) * 0.02
                star_x = (WIDTH // 2 + math.sin(star_t) * (300 + i * 3))
                star_y = (HEIGHT // 2 + math.cos(star_t * 0.7) * (200 + i * 2))
                star_alpha = int(abs(math.sin(star_t * 2)) * 255)
                if 0 <= star_x < WIDTH and 0 <= star_y < HEIGHT and star_alpha > 50:
                    star_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
                    pygame.draw.circle(star_surf, (255, 255, 255, star_alpha), (2, 2), 2)
                    screen.blit(star_surf, (int(star_x), int(star_y)))
        
        # Pulsing glow effect
        intro_alpha = int(255 * abs(math.sin(fade_frame * 0.08)) * 0.4 + 180)
        
        # MASSIVE title with ULTRA 3D effect and glow
        title_font = pygame.font.Font(None, 240)
        
        # Multiple 3D shadow layers for depth
        for offset in range(15, 0, -3):
            shadow_intensity = offset * 8
            shadow_color = (shadow_intensity, 0, shadow_intensity // 3)
            shadow_title = title_font.render("FINAL MODE", True, shadow_color)
            shadow_x = WIDTH // 2 - shadow_title.get_width() // 2 + offset * 2
            shadow_y = HEIGHT // 2 - 120 + offset * 2
            shadow_surf = pygame.Surface(shadow_title.get_size(), pygame.SRCALPHA)
            shadow_surf.blit(shadow_title, (0, 0))
            shadow_surf.set_alpha(50)
            screen.blit(shadow_surf, (shadow_x, shadow_y))
        
        # Outer glow
        if fade_frame > 30:
            glow_size = int(20 + math.sin(fade_frame * 0.1) * 10)
            for glow_offset in range(glow_size, 0, -5):
                glow_alpha = int((glow_size - glow_offset) * 3)
                glow_title = title_font.render("FINAL MODE", True, (255, 100, 100))
                glow_surf = pygame.Surface(glow_title.get_size(), pygame.SRCALPHA)
                glow_surf.blit(glow_title, (0, 0))
                glow_surf.set_alpha(glow_alpha)
                screen.blit(glow_surf, (WIDTH // 2 - glow_title.get_width() // 2 + glow_offset, 
                                       HEIGHT // 2 - 120 + glow_offset))
        
        # Main title in red with dynamic brightness
        title_brightness = int(200 + abs(math.sin(fade_frame * 0.1)) * 55)
        title = title_font.render("FINAL MODE", True, (title_brightness, 50, 50))
        title_surf = pygame.Surface(title.get_size(), pygame.SRCALPHA)
        title_surf.blit(title, (0, 0))
        title_surf.set_alpha(intro_alpha)
        screen.blit(title_surf, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 120))
        
        # Subtitle with animation
        if fade_frame > 60:
            subtitle_alpha = min(255, (fade_frame - 60) * 5)
            subtitle_font = pygame.font.Font(None, 60)
            subtitle = subtitle_font.render("THE ULTIMATE BATTLE AWAITS", True, (255, 200, 100))
            subtitle_surf = pygame.Surface(subtitle.get_size(), pygame.SRCALPHA)
            subtitle_surf.blit(subtitle, (0, 0))
            subtitle_surf.set_alpha(subtitle_alpha)
            screen.blit(subtitle_surf, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 2 + 80))
        
        # Swirling particles around title
        if fade_frame > 30:
            num_particles = min(40, (fade_frame - 30) // 2)
            for i in range(num_particles):
                particle_angle = (fade_frame * 0.03 + i * (360 / 40)) * math.pi / 180
                particle_dist = 250 + math.sin(fade_frame * 0.08 + i * 0.5) * 80
                px = WIDTH // 2 + math.cos(particle_angle) * particle_dist
                py = HEIGHT // 2 + math.sin(particle_angle) * particle_dist * 0.6
                particle_size = int(6 + math.sin(fade_frame * 0.12 + i) * 4)
                particle_color = [
                    int(255 * abs(math.sin(fade_frame * 0.05 + i * 0.3))),
                    int(200 * abs(math.cos(fade_frame * 0.07 + i * 0.2))),
                    int(100 + 155 * abs(math.sin(fade_frame * 0.06 + i * 0.4)))
                ]
                pygame.draw.circle(screen, particle_color, (int(px), int(py)), particle_size)
                # Particle trail
                if fade_frame > 50:
                    trail_angle = particle_angle - 0.3
                    trail_x = px - math.cos(trail_angle) * 30
                    trail_y = py - math.sin(trail_angle) * 30
                    pygame.draw.line(screen, particle_color, (int(px), int(py)), 
                                   (int(trail_x), int(trail_y)), 2)
        
        # Energy buildup effect
        if fade_frame > 100:
            buildup_intensity = (fade_frame - 100) / 50
            for ring in range(5):
                ring_radius = int(150 + ring * 50 + buildup_intensity * 100)
                ring_alpha = int(100 - ring * 15 - buildup_intensity * 50)
                if ring_alpha > 0:
                    ring_surf = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(ring_surf, (255, 255, 255, ring_alpha), 
                                     (ring_radius, ring_radius), ring_radius, 5)
                    screen.blit(ring_surf, (WIDTH // 2 - ring_radius, HEIGHT // 2 - ring_radius))
        
        pygame.display.flip()
        clock.tick(60)
    
    while running:
        dt = clock.tick(60) / 1000.0 * slow_motion
        frame_count += 1
        time_elapsed += dt
        
        # Update time of day (cycles every 3 minutes for longer day/night)
        time_of_day = (time_of_day + dt / 180) % 1.0
        
        # Dynamic weather system
        if random.random() < 0.001:  # Rare weather changes
            weather = random.choice(['clear', 'rain', 'fog', 'storm'])
        
        # === INPUT HANDLING with ADVANCED CONTROLS ===
        keys = pygame.key.get_pressed()
        attack_pressed = False
        special_attack_pressed = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # JUMP with double jump
                if event.key == pygame.K_SPACE and player['stamina'] > 20:
                    if player['y'] <= 1:  # On ground
                        player['vy'] = -25  # Higher jump
                        player['stamina'] -= 20
                        camera_shake = 8
                    elif player['stamina'] > 40:  # Double jump in air!
                        player['vy'] = -22
                        player['stamina'] -= 40
                        camera_shake = 12
                        # Double jump particles
                        for _ in range(10):
                            particles.append({
                                'x': player['x'],
                                'y': player['y'],
                                'z': player['z'],
                                'vx': random.uniform(-3, 3),
                                'vy': random.uniform(0, 5),
                                'vz': random.uniform(-2, 2),
                                'life': random.uniform(0.5, 1.0),
                                'size': random.randint(2, 5),
                                'color': (200, 200, 255),
                            })
                # REGULAR ATTACK with X or SHIFT
                if (event.key == pygame.K_x or event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT):
                    if player['energy'] > 10 and player['attack_cooldown'] <= 0:
                        attack_pressed = True
                        player['energy'] -= 10
                        player['attack_cooldown'] = 0.25
                        camera_shake = 12
                        screen_flash = 0.15
                        screen_flash_color = (255, 200, 100)
                # SPECIAL MEGA ATTACK with Z or CTRL
                if (event.key == pygame.K_z or event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL):
                    if player['energy'] > 40 and player['special_attack_cooldown'] <= 0:
                        special_attack_pressed = True
                        player['energy'] -= 40
                        player['special_attack_cooldown'] = 2.0
                        camera_shake = 30
                        screen_flash = 0.5
                        screen_flash_color = (255, 100, 255)
                        slow_motion = 0.3  # Slow mo on special attack!
                        player['rage_mode'] = 3.0  # Rage mode!
                        # Create massive explosion
                        for angle in range(0, 360, 30):
                            rad = math.radians(angle)
                            projectiles.append({
                                'x': player['x'],
                                'y': player['y'] + 20,
                                'z': player['z'],
                                'vx': math.cos(rad) * 8,
                                'vz': math.sin(rad) * 8,
                                'vy': 0,
                                'size': 20,
                                'damage': 50,
                                'life': 1.5,
                                'color': (255, 0, 255),
                                'source': 'player',
                            })
        
        # === PLAYER MOVEMENT - IMPROVED and more responsive ===
        move_speed = 3.5 if player['rage_mode'] > 0 else 2.5  # Faster, more responsive
        
        # Direct position control for WASD (like classic games)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player['x'] -= move_speed
            player['stamina'] -= 0.08
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player['x'] += move_speed
            player['stamina'] -= 0.08
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player['z'] += move_speed  # Move into screen (3D)
            player['stamina'] -= 0.08
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player['z'] -= move_speed  # Move out of screen (3D)
            player['stamina'] -= 0.08
        
        # Apply vertical physics only
        player['vy'] += gravity
        player['y'] += player['vy']
        
        # Ground collision
        if player['y'] <= 0:
            player['y'] = 0
            player['vy'] = 0
            player['stamina'] = min(player['max_stamina'], player['stamina'] + 1.0)
        
        # World boundaries
        if player['x'] < -world_size // 2:
            player['x'] = -world_size // 2
            player['vx'] = 0
        if player['x'] > world_size // 2:
            player['x'] = world_size // 2
            player['vx'] = 0
        if player['z'] < -400:
            player['z'] = -400
            player['vz'] = 0
        if player['z'] > 800:
            player['z'] = 800
            player['vz'] = 0
        
        # Update timers
        player['attack_cooldown'] = max(0, player['attack_cooldown'] - dt)
        player['special_attack_cooldown'] = max(0, player['special_attack_cooldown'] - dt)
        player['invincible'] = max(0, player['invincible'] - dt)
        player['rage_mode'] = max(0, player['rage_mode'] - dt)
        
        # Regenerate resources
        player['stamina'] = min(player['max_stamina'], player['stamina'] + 0.25)
        player['energy'] = min(player['max_energy'], player['energy'] + 0.15)
        player['shield'] = min(player['max_shield'], player['shield'] + 0.05)
        
        # Camera follows player smoothly
        camera_x += (player['x'] - camera_x) * 0.1
        camera_z += (player['z'] + 800 - camera_z) * 0.05
        
        # Camera shake with rotation
        if camera_shake > 0:
            camera_shake_x = random.uniform(-camera_shake, camera_shake)
            camera_shake_y = random.uniform(-camera_shake, camera_shake)
            camera_shake *= 0.9
        else:
            camera_shake_x *= 0.8
            camera_shake_y *= 0.8
        
        
        # Restore slow motion gradually
        slow_motion = min(1.0, slow_motion + dt * 0.5)
        
        # === ENVIRONMENTAL UPDATES - 3D World ===
        # Update clouds with parallax
        for cloud in clouds:
            cloud['x'] += cloud['speed'] + wind_strength * 0.2
            if cloud['x'] > world_size * 2:
                cloud['x'] = -world_size
                cloud['y'] = random.randint(-100, 100)
                cloud['z'] = random.randint(1000, 4000)
        
        # Update wind
        wind_strength = math.sin(time_elapsed * 0.5) * 3 + random.uniform(-0.8, 0.8)
        wind_direction = math.sin(time_elapsed * 0.3) * 0.5
        
        # Update grass sway
        for grass in grass_blades:
            grass['sway'] += grass['sway_speed'] * dt
        
        # Update light rays
        for ray in light_rays:
            ray['x'] += ray['speed'] + wind_strength * 0.05
            if ray['x'] > world_size * 2:
                ray['x'] = -world_size
        
        # Update atmospheric particles (dust, pollen, rain, etc.)
        if weather == 'rain' and random.random() < 0.8:
            particles.append({
                'x': camera_x + random.randint(-WIDTH, WIDTH * 2),
                'y': 300,
                'z': random.randint(-200, 1000),
                'vx': wind_strength * 0.5,
                'vy': -15,
                'vz': 0,
                'life': random.uniform(2, 4),
                'size': random.randint(1, 2),
                'color': (150, 150, 200),
            })
        elif random.random() < 0.2:
            particles.append({
                'x': camera_x + random.randint(-WIDTH, WIDTH * 2),
                'y': 200,
                'z': random.randint(-200, 1000),
                'vx': wind_strength * 0.3 + random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'vz': random.uniform(-0.5, 0.5),
                'life': random.uniform(3, 8),
                'size': random.randint(1, 4),
                'color': (200, 200, 150),
            })
        
        # Update particles with 3D physics
        for particle in particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['z'] += particle['vz']
            particle['vy'] += 0.3  # Gravity
            particle['life'] -= dt
            if particle['life'] <= 0 or particle['y'] < -50:
                particles.remove(particle)
        
        # === COLLECTIBLES UPDATE - TRUE 3D Enhanced ===
        combo_timer -= dt
        if combo_timer <= 0:
            combo_multiplier = 1.0
            if combo_multiplier > max_combo:
                max_combo = combo_multiplier
        
        for collectible in collectibles:
            if not collectible['collected']:
                collectible['bounce'] += dt * 6
                collectible['rotation'] += dt * 4
                # Floating animation
                collectible['y'] = abs(math.sin(collectible['bounce'])) * 30 + 50
                
                # TRUE 3D collision check
                dist_3d = math.sqrt((collectible['x'] - player['x'])**2 + 
                                   (collectible['y'] - player['y'])**2 +
                                   (collectible['z'] - player['z'])**2)
                if dist_3d < 70:
                    collectible['collected'] = True
                    points = int(collectible['value'] * combo_multiplier)
                    score += points
                    coins_collected += 1
                    combo_timer = 3.0
                    combo_multiplier = min(10.0, combo_multiplier + 0.8)
                    # Create epic pickup explosion
                    for _ in range(15):
                        particles.append({
                            'x': collectible['x'],
                            'y': collectible['y'],
                            'z': collectible['z'],
                            'vx': random.uniform(-5, 5),
                            'vy': random.uniform(-3, 8),
                            'vz': random.uniform(-5, 5),
                            'life': random.uniform(0.5, 1.5),
                            'size': random.randint(3, 8),
                            'color': (255, 215, 0),
                        })
                    camera_shake = 5
        
        # Spawn collectibles near player
        if len([c for c in collectibles if not c['collected']]) < 20 and random.random() < 0.03:
            collectibles.append({
                'x': player['x'] + random.randint(-500, 500),
                'y': random.randint(20, 150),
                'z': player['z'] + random.randint(-200, 600),
                'collected': False,
                'type': random.choice(['coin', 'gem', 'star', 'diamond', 'crystal']),
                'value': random.choice([100, 250, 500, 1000, 2500]),
                'bounce': random.uniform(0, 2 * math.pi),
                'rotation': random.uniform(0, 2 * math.pi),
                'size': random.randint(25, 50),
                'glow': random.randint(5, 15),
            })
        
        
        # === ENEMIES UPDATE - ADVANCED 3D AI with States ===
        for enemy in enemies[:]:
            enemy['animation_frame'] += dt * 5
            enemy['ai_timer'] += dt
            
            # Calculate distance to player (3D)
            dx = player['x'] - enemy['x']
            dy = player['y'] - enemy['y']
            dz = player['z'] - enemy['z']
            dist_3d = math.sqrt(dx**2 + dy**2 + dz**2)
            
            # AI State Machine
            if dist_3d < 200:
                enemy['ai_state'] = 'chase'
            elif dist_3d > 500:
                enemy['ai_state'] = 'patrol'
            
            if enemy['ai_state'] == 'chase':
                # Chase player intelligently
                if dist_3d > 10:
                    enemy['vx'] = (dx / dist_3d) * enemy['speed'] * 2
                    enemy['vz'] = (dz / dist_3d) * enemy['speed'] * 2
                    
                # Attack if close enough
                if dist_3d < 120:
                    enemy['ai_state'] = 'attack'
                    enemy['attack_timer'] -= dt
                    if enemy['attack_timer'] <= 0:
                        enemy['attack_timer'] = 2.0
                        # Shoot projectile at player!
                        if dist_3d > 0:
                            projectiles.append({
                                'x': enemy['x'],
                                'y': enemy['y'] + 20,
                                'z': enemy['z'],
                                'vx': (dx / dist_3d) * 6,
                                'vy': (dy / dist_3d) * 6,
                                'vz': (dz / dist_3d) * 6,
                                'size': 12,
                                'damage': 10,
                                'life': 2.0,
                                'color': enemy['color'],
                                'source': 'enemy',
                            })
            elif enemy['ai_state'] == 'patrol':
                # Random patrol
                if enemy['ai_timer'] > 2.0:
                    enemy['vx'] = random.uniform(-enemy['speed'], enemy['speed'])
                    enemy['vz'] = random.uniform(-enemy['speed'], enemy['speed'])
                    enemy['ai_timer'] = 0
            
            # Apply gravity to enemies
            if enemy['y'] > 0:
                enemy['y'] -= gravity
            if enemy['y'] < 0:
                enemy['y'] = 0
            
            # Update position
            enemy['x'] += enemy['vx'] * dt * 60
            enemy['z'] += enemy['vz'] * dt * 60
            enemy['vx'] *= 0.95
            enemy['vz'] *= 0.95
            
            # World boundaries
            if enemy['x'] < -world_size // 2:
                enemy['x'] = -world_size // 2
                enemy['vx'] *= -1
            if enemy['x'] > world_size // 2:
                enemy['x'] = world_size // 2
                enemy['vx'] *= -1
            if enemy['z'] < -400:
                enemy['z'] = -400
                enemy['vz'] *= -1
            if enemy['z'] > 800:
                enemy['z'] = 800
                enemy['vz'] *= -1
            
            # Check REGULAR attack collision - TRUE 3D
            if attack_pressed and dist_3d < 150:
                enemy['health'] -= player['attack_power']
                camera_shake = 18
                screen_flash = 0.15
                # Hit particles
                for _ in range(8):
                    particles.append({
                        'x': enemy['x'],
                        'y': enemy['y'],
                        'z': enemy['z'],
                        'vx': random.uniform(-4, 4),
                        'vy': random.uniform(2, 8),
                        'vz': random.uniform(-4, 4),
                        'life': random.uniform(0.3, 0.8),
                        'size': random.randint(3, 7),
                        'color': enemy['color'],
                    })
                
                if enemy['health'] <= 0:
                    # EPIC death explosion!
                    for _ in range(20):
                        particles.append({
                            'x': enemy['x'],
                            'y': enemy['y'] + random.uniform(-20, 40),
                            'z': enemy['z'],
                            'vx': random.uniform(-8, 8),
                            'vy': random.uniform(-2, 12),
                            'vz': random.uniform(-8, 8),
                            'life': random.uniform(0.8, 2.0),
                            'size': random.randint(5, 15),
                            'color': enemy['color'],
                        })
                    enemies.remove(enemy)
                    score += int(1500 * combo_multiplier)
                    enemies_defeated += 1
                    combo_timer = 3.0
                    combo_multiplier = min(10.0, combo_multiplier + 0.5)
                    camera_shake = 25
                    continue
            
            # Check SPECIAL attack collision - MASSIVE range
            if special_attack_pressed and dist_3d < 300:
                enemy['health'] -= player['attack_power'] * 3
                camera_shake = 30
                # Massive hit effect!
                for _ in range(15):
                    particles.append({
                        'x': enemy['x'],
                        'y': enemy['y'],
                        'z': enemy['z'],
                        'vx': random.uniform(-6, 6),
                        'vy': random.uniform(5, 15),
                        'vz': random.uniform(-6, 6),
                        'life': random.uniform(0.5, 1.2),
                        'size': random.randint(5, 12),
                        'color': (255, 0, 255),
                    })
                
                if enemy['health'] <= 0:
                    enemies.remove(enemy)
                    score += int(2000 * combo_multiplier)
                    enemies_defeated += 1
                    combo_timer = 3.0
                    combo_multiplier = min(10.0, combo_multiplier + 0.6)
                    continue
            
            # Check player collision (damage player) - TRUE 3D
            if dist_3d < 80 and player['invincible'] <= 0:
                damage = 20
                if player['shield'] > 0:
                    player['shield'] -= damage
                    if player['shield'] < 0:
                        player['health'] += player['shield']  # Overflow damage
                        player['shield'] = 0
                else:
                    player['health'] -= damage
                player['invincible'] = 1.2
                camera_shake = 25
                screen_flash = 0.4
                screen_flash_color = (255, 0, 0)
                if player['health'] <= 0:
                    running = False  # Game over
        
        # Spawn more enemies dynamically
        max_enemies = 20 if player['rage_mode'] > 0 else 15
        if len(enemies) < max_enemies and random.random() < 0.015:
            enemy_type = random.choice(enemy_types)
            spawn_distance = 600
            angle = random.uniform(0, 2 * math.pi)
            enemies.append({
                'x': player['x'] + math.cos(angle) * spawn_distance,
                'y': 0,
                'z': player['z'] + math.sin(angle) * spawn_distance,
                'vx': 0,
                'vz': 0,
                'type': enemy_type['type'],
                'health': enemy_type['health'],
                'max_health': enemy_type['health'],
                'size': enemy_type['size'],
                'base_size': enemy_type['size'],
                'speed': enemy_type['speed'],
                'color': enemy_type['color'],
                'attack_timer': random.uniform(0, 3),
                'animation_frame': 0,
                'ai_state': 'patrol',
                'ai_timer': 0,
            })
        
        # === BOSS BATTLE SYSTEM ===
        # Spawn boss at milestones
        if enemies_defeated >= 20 and not boss_spawned and len(bosses) == 0:
            boss_spawned = True
            bosses.append({
                'x': player['x'] + 400,
                'y': 0,
                'z': player['z'],
                'vx': 0,
                'vy': 0,
                'vz': 0,
                'size': 200,  # HUGE boss!
                'health': 300,
                'max_health': 300,
                'phase': 1,
                'attack_pattern': 0,
                'attack_timer': 0,
                'animation': 0,
            })
            camera_shake = 40
            slow_motion = 0.2
        
        # Update bosses
        for boss in bosses[:]:
            boss['animation'] += dt * 3
            boss['attack_timer'] -= dt
            
            # Boss AI - different phases
            dx = player['x'] - boss['x']
            dz = player['z'] - boss['z']
            dist = math.sqrt(dx**2 + dz**2)
            
            # Movement
            if dist > 250:
                if dist > 0:
                    boss['vx'] = (dx / dist) * 3
                    boss['vz'] = (dz / dist) * 3
            else:
                boss['vx'] *= 0.9
                boss['vz'] *= 0.9
            
            boss['x'] += boss['vx']
            boss['z'] += boss['vz']
            
            # Attack patterns
            if boss['attack_timer'] <= 0:
                boss['attack_timer'] = 1.5
                boss['attack_pattern'] = (boss['attack_pattern'] + 1) % 3
                
                if boss['attack_pattern'] == 0:
                    # Spiral projectile attack!
                    for angle in range(0, 360, 20):
                        rad = math.radians(angle + boss['animation'] * 50)
                        projectiles.append({
                            'x': boss['x'],
                            'y': boss['size'] // 2,
                            'z': boss['z'],
                            'vx': math.cos(rad) * 5,
                            'vy': 0,
                            'vz': math.sin(rad) * 5,
                            'size': 18,
                            'damage': 25,
                            'life': 3.0,
                            'color': (200, 0, 200),
                            'source': 'boss',
                        })
                elif boss['attack_pattern'] == 1:
                    # Homing missiles!
                    for _ in range(5):
                        if dist > 0:
                            projectiles.append({
                                'x': boss['x'],
                                'y': boss['size'] // 2,
                                'z': boss['z'],
                                'vx': (dx / dist) * 4 + random.uniform(-1, 1),
                                'vy': random.uniform(-2, 2),
                                'vz': (dz / dist) * 4 + random.uniform(-1, 1),
                                'size': 15,
                                'damage': 30,
                                'life': 4.0,
                                'color': (255, 100, 0),
                                'source': 'boss',
                            })
                elif boss['attack_pattern'] == 2:
                    # Ground pound shockwave!
                    camera_shake = 40
                    for angle in range(0, 360, 15):
                        rad = math.radians(angle)
                        particles.append({
                            'x': boss['x'],
                            'y': 0,
                            'z': boss['z'],
                            'vx': math.cos(rad) * 10,
                            'vy': random.uniform(0, 5),
                            'vz': math.sin(rad) * 10,
                            'life': 1.5,
                            'size': 20,
                            'color': (150, 50, 200),
                        })
            
            # Boss takes damage from attacks
            if attack_pressed and dist < 180:
                boss['health'] -= player['attack_power']
                camera_shake = 20
                # Hit effect
                for _ in range(10):
                    particles.append({
                        'x': boss['x'],
                        'y': boss['size'] // 2,
                        'z': boss['z'],
                        'vx': random.uniform(-6, 6),
                        'vy': random.uniform(5, 15),
                        'vz': random.uniform(-6, 6),
                        'life': random.uniform(0.5, 1.0),
                        'size': random.randint(8, 15),
                        'color': (200, 0, 200),
                    })
            
            if special_attack_pressed:
                boss['health'] -= player['attack_power'] * 3
                camera_shake = 35
            
            # Boss death
            if boss['health'] <= 0:
                # MEGA EXPLOSION!
                for _ in range(100):
                    particles.append({
                        'x': boss['x'],
                        'y': boss['size'] // 2,
                        'z': boss['z'],
                        'vx': random.uniform(-15, 15),
                        'vy': random.uniform(0, 20),
                        'vz': random.uniform(-15, 15),
                        'life': random.uniform(1.0, 3.0),
                        'size': random.randint(10, 30),
                        'color': (random.randint(200, 255), random.randint(0, 100), random.randint(200, 255)),
                    })
                bosses.remove(boss)
                score += int(10000 * combo_multiplier)
                bosses_defeated += 1
                objectives_completed = min(total_objectives, objectives_completed + 5)
                camera_shake = 80
                slow_motion = 0.1
                continue
            
            # Boss collision damage
            if dist < 100 and player['invincible'] <= 0:
                player['health'] -= 40
                player['invincible'] = 1.5
                camera_shake = 35
                screen_flash = 0.6
                screen_flash_color = (255, 0, 255)
        
        # === UPDATE PROJECTILES ===
        for proj in projectiles[:]:
            proj['x'] += proj['vx']
            proj['y'] += proj['vy']
            proj['z'] += proj['vz']
            proj['vy'] -= 0.2  # Gravity
            proj['life'] -= dt
            
            if proj['life'] <= 0:
                projectiles.remove(proj)
                continue
            
            # Check collisions
            if proj['source'] == 'player':
                # Hit enemies
                for enemy in enemies[:]:
                    dist = math.sqrt((proj['x'] - enemy['x'])**2 + 
                                   (proj['y'] - enemy['y'])**2 +
                                   (proj['z'] - enemy['z'])**2)
                    if dist < enemy['size']:
                        enemy['health'] -= proj['damage']
                        projectiles.remove(proj)
                        # Hit effect
                        for _ in range(5):
                            particles.append({
                                'x': proj['x'],
                                'y': proj['y'],
                                'z': proj['z'],
                                'vx': random.uniform(-3, 3),
                                'vy': random.uniform(2, 6),
                                'vz': random.uniform(-3, 3),
                                'life': 0.5,
                                'size': 5,
                                'color': proj['color'],
                            })
                        break
            else:
                # Hit player
                dist = math.sqrt((proj['x'] - player['x'])**2 + 
                               (proj['y'] - player['y'])**2 +
                               (proj['z'] - player['z'])**2)
                if dist < 60 and player['invincible'] <= 0:
                    if player['shield'] > 0:
                        player['shield'] -= proj['damage']
                        if player['shield'] < 0:
                            player['health'] += player['shield']
                            player['shield'] = 0
                    else:
                        player['health'] -= proj['damage']
                    player['invincible'] = 0.5
                    projectiles.remove(proj)
                    camera_shake = 15
                    continue
        
        # Update special effects
        camera_shake = max(0, camera_shake - dt * 60)
        screen_flash = max(0, screen_flash - dt * 2.5)
        
        # Check win condition - progressive objectives
        if coins_collected >= 25:
            objectives_completed = min(total_objectives, objectives_completed + 1)
            coins_collected = 0
        if enemies_defeated >= 15:
            objectives_completed = min(total_objectives, objectives_completed + 1)
            enemies_defeated = 0
        if bosses_defeated >= 1:
            objectives_completed = min(total_objectives, objectives_completed + 3)
            bosses_defeated = 0
        
        # === RENDERING - TRUE 3D with DEPTH SORTING! ===
        
        # Sky gradient based on time of day - ULTRA REALISTIC
        if time_of_day < 0.25:  # Night to dawn
            t = time_of_day / 0.25
            sky_top = (int(15 + t * 120), int(15 + t * 150), int(35 + t * 185))
            sky_bottom = (int(25 + t * 190), int(25 + t * 205), int(45 + t * 210))
            ambient_light = 0.3 + t * 0.7
        elif time_of_day < 0.5:  # Dawn to noon
            t = (time_of_day - 0.25) / 0.25
            sky_top = (int(135 + t * 10), int(165 + t * 45), int(220 + t * 20))
            sky_bottom = (int(215 + t * 25), int(230 + t * 20), int(255))
            ambient_light = 1.0
        elif time_of_day < 0.75:  # Noon to dusk
            t = (time_of_day - 0.5) / 0.25
            sky_top = (int(145 - t * 70), int(210 - t * 110), int(240 - t * 100))
            sky_bottom = (int(240 - t * 110), int(250 - t * 125), int(255 - t * 160))
            ambient_light = 1.0 - t * 0.4
        else:  # Dusk to night
            t = (time_of_day - 0.75) / 0.25
            sky_top = (int(75 - t * 60), int(100 - t * 85), int(140 - t * 105))
            sky_bottom = (int(130 - t * 105), int(130 - t * 105), int(95 - t * 50))
            ambient_light = 0.6 - t * 0.3
        
        # Draw sky gradient with dithering for smoothness
        for y in range(HEIGHT):
            if y < horizon_y:
                # Sky portion
                progress = y / horizon_y
                color = (
                    int(sky_top[0] + (sky_bottom[0] - sky_top[0]) * progress),
                    int(sky_top[1] + (sky_bottom[1] - sky_top[1]) * progress),
                    int(sky_top[2] + (sky_bottom[2] - sky_top[2]) * progress),
                )
            else:
                # Ground gradient (below horizon)
                progress = (y - horizon_y) / (HEIGHT - horizon_y)
                # Grass color gradient - darker near horizon, lighter up close
                grass_r = int(40 + progress * 50)
                grass_g = int(90 + progress * 50)
                grass_b = int(25 + progress * 35)
                color = (grass_r, grass_g, grass_b)
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))
        
        # Draw sun/moon
        sun_moon_y = int(horizon_y - abs(time_of_day - 0.5) * HEIGHT * 0.4)
        sun_moon_x = WIDTH // 2 + int((time_of_day - 0.5) * WIDTH * 0.8)
        if 0.2 < time_of_day < 0.8:  # Day - draw sun
            for glow_size in range(80, 20, -10):
                glow_alpha = int(30 - (80 - glow_size) * 0.3)
                if glow_alpha > 0:
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (255, 255, 100, glow_alpha), (glow_size, glow_size), glow_size)
                    screen.blit(glow_surf, (sun_moon_x - glow_size, sun_moon_y - glow_size))
            pygame.draw.circle(screen, (255, 255, 150), (sun_moon_x, sun_moon_y), 25)
            pygame.draw.circle(screen, (255, 255, 200), (sun_moon_x - 5, sun_moon_y - 5), 20)
        else:  # Night - draw moon
            pygame.draw.circle(screen, (220, 220, 240), (sun_moon_x, sun_moon_y), 22)
            pygame.draw.circle(screen, (180, 180, 200), (sun_moon_x + 10, sun_moon_y - 5), 18)
        
        # Draw volumetric light rays (god rays) - TRUE 3D projection
        for ray in light_rays:
            sx, sy, scale = project_3d(ray['x'], 200, ray['z'])
            if sx and scale > 0:
                ray_width = int(ray['width'] * scale)
                if ray_width > 5:
                    ray_surf = pygame.Surface((ray_width, int(HEIGHT * 0.7)), pygame.SRCALPHA)
                    for i in range(ray_width):
                        alpha = int(ray['opacity'] * abs(math.sin(i / ray_width * math.pi)) * scale)
                        if alpha > 0:
                            pygame.draw.line(ray_surf, (255, 255, 200, min(alpha, 255)), (i, 0), (i, int(HEIGHT * 0.7)))
                    screen.blit(ray_surf, (int(sx - ray_width // 2), 0))
        
        # Draw clouds with TRUE 3D perspective and realistic shading
        for cloud in clouds:
            sx, sy, scale = project_3d(cloud['x'], cloud['y'], cloud['z'])
            if sx and scale > 0.1:
                cloud_size = int(cloud['size'] * scale)
                if cloud_size > 10:
                    cloud_surf = pygame.Surface((cloud_size, cloud_size // 2), pygame.SRCALPHA)
                    # Multiple cloud puffs for realism
                    for puff in range(cloud['puffiness']):
                        puff_x = (puff / cloud['puffiness']) * cloud_size
                        puff_size = cloud_size // cloud['puffiness'] + random.randint(-10, 10)
                        # Cloud shadow (darker bottom)
                        shadow_alpha = max(0, min(255, int(cloud['opacity'] * scale * 0.4)))
                        pygame.draw.ellipse(cloud_surf, (120, 120, 140, shadow_alpha),
                                          (int(puff_x), cloud_size // 3, puff_size, puff_size // 2))
                        # Cloud body
                        body_alpha = max(0, min(255, int(cloud['opacity'] * scale)))
                        pygame.draw.ellipse(cloud_surf, (255, 255, 255, body_alpha),
                                          (int(puff_x), 0, puff_size, puff_size // 2))
                        # Cloud highlights (brighter top)
                        highlight_alpha = max(0, min(255, int(cloud['opacity'] * scale * 1.3)))
                        pygame.draw.ellipse(cloud_surf, (255, 255, 255, highlight_alpha),
                                          (int(puff_x + puff_size // 4), 0, puff_size // 2, puff_size // 4))
                    screen.blit(cloud_surf, (int(sx - cloud_size // 2), int(sy)))
        
        # Draw mountains with TRUE 3D layering
        for mountain in mountains:
            sx, sy, scale = project_3d(mountain['x'], mountain['y'], mountain['z'])
            if sx and scale > 0.05:
                m_height = int(mountain['height'] * scale)
                m_width = int(mountain['width'] * scale)
                if m_height > 20 and m_width > 20:
                    # Mountain is triangle/polygon
                    # Color gets cooler/bluer with distance
                    distance_factor = 1.0 - (scale * 0.3)
                    base_r = int(100 * distance_factor + 150 * (1 - distance_factor))
                    base_g = int(120 * distance_factor + 160 * (1 - distance_factor))
                    base_b = int(100 * distance_factor + 180 * (1 - distance_factor))
                    
                    # Draw mountain polygon
                    peak_y = int(sy - m_height)
                    base_y = int(sy)
                    left_x = int(sx - m_width // 2)
                    right_x = int(sx + m_width // 2)
                    
                    # Main mountain shape
                    pygame.draw.polygon(screen, (base_r, base_g, base_b), [
                        (sx, peak_y),
                        (left_x, base_y),
                        (right_x, base_y)
                    ])
                    
                    # Snow cap for tall mountains
                    if mountain['height'] > 400:
                        snow_height = int(m_height * 0.3)
                        pygame.draw.polygon(screen, (240, 240, 250), [
                            (sx, peak_y),
                            (sx - m_width // 6, peak_y + snow_height),
                            (sx + m_width // 6, peak_y + snow_height)
                        ])
        
        # === 3D OBJECT RENDERING with DEPTH SORTING ===
        # Collect all 3D objects with their depth for sorting
        render_objects = []
        
        # Add grass blades
        for grass in grass_blades:
            render_objects.append(('grass', grass, grass['z']))
        
        # Add trees
        for tree in trees:
            render_objects.append(('tree', tree, tree['z']))
        
        # Add rocks
        for rock in rocks:
            render_objects.append(('rock', rock, rock['z']))
        
        # Add collectibles
        for collectible in collectibles:
            if not collectible['collected']:
                render_objects.append(('collectible', collectible, collectible['z']))
        
        # Add enemies
        for enemy in enemies:
            render_objects.append(('enemy', enemy, enemy['z']))
        
        # Add bosses
        for boss in bosses:
            render_objects.append(('boss', boss, boss['z']))
        
        # Add projectiles
        for proj in projectiles:
            render_objects.append(('projectile', proj, proj['z']))
        
        # Add player
        render_objects.append(('player', player, player['z']))
        
        # Add particles
        for particle in particles:
            render_objects.append(('particle', particle, particle['z']))
        
        # SORT by depth (far to near) - TRUE 3D DEPTH SORTING!
        render_objects.sort(key=lambda obj: obj[2], reverse=True)
        
        # RENDER all objects in depth order
        for obj_type, obj, depth in render_objects:
            sx, sy, scale = project_3d(obj['x'], obj['y'], obj['z'])
            if not sx or scale <= 0:
                continue
            
            if obj_type == 'grass':
                # Realistic grass blade
                sway_offset = math.sin(obj['sway'] + wind_strength * 0.5) * scale * 8
                blade_height = int(obj['height'] * scale)
                base_x, base_y = sx, sy
                tip_x, tip_y = int(sx + sway_offset), int(sy - blade_height)
                
                if blade_height > 2:
                    blade_r = max(0, min(255, 40 + obj['color_variation']))
                    blade_g = max(0, min(255, 120 + obj['color_variation']))
                    blade_b = max(0, min(255, 30 + obj['color_variation'] // 2))
                    blade_color = (blade_r, blade_g, blade_b)
                    
                    pygame.draw.line(screen, blade_color, (base_x, base_y), (tip_x, tip_y), max(1, int(2 * scale)))
                    # Highlight
                    if blade_height > 5:
                        pygame.draw.line(screen, (blade_r + 40, blade_g + 40, blade_b + 20), 
                                       (base_x + 1, base_y), (tip_x + 1, tip_y), 1)
            
            elif obj_type == 'tree':
                # Realistic tree with trunk and foliage
                tree_height = int(obj['height'] * scale)
                trunk_width = int(obj['trunk_width'] * scale)
                canopy_width = int(obj['width'] * scale)
                
                if tree_height > 10:
                    # Trunk
                    trunk_top_y = int(sy - tree_height)
                    pygame.draw.rect(screen, (101, 67, 33), 
                                   (int(sx - trunk_width // 2), trunk_top_y, trunk_width, tree_height))
                    # Trunk texture lines
                    for line_y in range(trunk_top_y, int(sy), max(5, int(15 * scale))):
                        pygame.draw.line(screen, (80, 50, 20), 
                                       (int(sx - trunk_width // 2), line_y), 
                                       (int(sx + trunk_width // 2), line_y), 1)
                    
                    # Foliage - multiple leaf clusters
                    sway = math.sin(obj['sway'] + time_elapsed) * 5 * scale
                    for i in range(obj['leaves_density']):
                        leaf_offset_x = random.randint(-canopy_width // 3, canopy_width // 3)
                        leaf_offset_y = random.randint(-canopy_width // 2, 0)
                        leaf_size = int(canopy_width * random.uniform(0.4, 0.7))
                        leaf_x = int(sx + leaf_offset_x + sway)
                        leaf_y = trunk_top_y + leaf_offset_y
                        # Leaf cluster (circle)
                        leaf_color = (random.randint(50, 90), random.randint(140, 180), random.randint(50, 80))
                        pygame.draw.circle(screen, leaf_color, (leaf_x, leaf_y), leaf_size)
                        # Highlight on leaves
                        pygame.draw.circle(screen, (leaf_color[0] + 30, leaf_color[1] + 30, leaf_color[2] + 20),
                                         (leaf_x - leaf_size // 4, leaf_y - leaf_size // 4), leaf_size // 3)
            
            elif obj_type == 'rock':
                # Realistic rock obstacle
                rock_size = int(obj['size'] * scale)
                if rock_size > 5:
                    rock_r = max(0, min(255, 100 + obj['color_variation']))
                    rock_g = max(0, min(255, 100 + obj['color_variation']))
                    rock_b = max(0, min(255, 100 + obj['color_variation']))
                    # Irregular rock shape (polygon)
                    rock_points = [
                        (sx, int(sy - rock_size)),
                        (int(sx - rock_size * 0.7), int(sy - rock_size * 0.3)),
                        (int(sx - rock_size * 0.4), sy),
                        (int(sx + rock_size * 0.5), sy),
                        (int(sx + rock_size * 0.6), int(sy - rock_size * 0.4))
                    ]
                    pygame.draw.polygon(screen, (rock_r, rock_g, rock_b), rock_points)
                    # Rock highlights
                    pygame.draw.line(screen, (rock_r + 40, rock_g + 40, rock_b + 40),
                                   (sx, int(sy - rock_size)), (int(sx - rock_size * 0.7), int(sy - rock_size * 0.3)), 2)
            
            elif obj_type == 'collectible':
                # MASSIVE collectibles with glow and 3D rotation
                coll_size = int(obj['size'] * scale)
                if coll_size > 5:
                    # Glow effect
                    glow_size = int(obj['glow'] * scale)
                    for glow in range(glow_size, 0, -2):
                        glow_alpha = int(30 - glow * 2)
                        if glow_alpha > 0:
                            glow_surf = pygame.Surface((coll_size + glow * 2, coll_size + glow * 2), pygame.SRCALPHA)
                            if obj['type'] == 'coin':
                                pygame.draw.circle(glow_surf, (255, 215, 0, glow_alpha), 
                                                 (coll_size // 2 + glow, coll_size // 2 + glow), coll_size // 2 + glow)
                            elif obj['type'] in ['gem', 'diamond', 'crystal']:
                                pygame.draw.circle(glow_surf, (100, 200, 255, glow_alpha), 
                                                 (coll_size // 2 + glow, coll_size // 2 + glow), coll_size // 2 + glow)
                            else:
                                pygame.draw.circle(glow_surf, (255, 255, 0, glow_alpha), 
                                                 (coll_size // 2 + glow, coll_size // 2 + glow), coll_size // 2 + glow)
                            screen.blit(glow_surf, (int(sx - coll_size // 2 - glow), int(sy - coll_size // 2 - glow)))
                    
                    # Main collectible
                    if obj['type'] == 'coin':
                        # 3D coin with rotation
                        pygame.draw.ellipse(screen, (255, 215, 0), 
                                          (int(sx - coll_size // 2), int(sy - coll_size // 2), coll_size, coll_size))
                        pygame.draw.ellipse(screen, (255, 255, 150), 
                                          (int(sx - coll_size // 3), int(sy - coll_size // 3), coll_size // 2, coll_size // 2))
                        pygame.draw.ellipse(screen, (200, 170, 0), 
                                          (int(sx - coll_size // 2), int(sy - coll_size // 2), coll_size, coll_size), 2)
                    elif obj['type'] in ['gem', 'diamond', 'crystal']:
                        # 3D diamond/gem
                        rotation = obj['rotation']
                        points = []
                        for i in range(6):
                            angle = rotation + i * math.pi / 3
                            px = sx + math.cos(angle) * coll_size // 2
                            py = sy + math.sin(angle) * coll_size // 2
                            points.append((int(px), int(py)))
                        pygame.draw.polygon(screen, (100, 200, 255), points)
                        # Inner highlight
                        inner_points = [(sx, int(sy - coll_size // 3)), (int(sx - coll_size // 4), sy), (int(sx + coll_size // 4), sy)]
                        pygame.draw.polygon(screen, (200, 255, 255), inner_points)
                    else:  # star
                        # 3D star
                        for angle in range(0, 360, 72):
                            angle_rad = math.radians(angle + obj['rotation'] * 50)
                            outer_x = sx + math.cos(angle_rad) * coll_size // 2
                            outer_y = sy + math.sin(angle_rad) * coll_size // 2
                            pygame.draw.line(screen, (255, 255, 0), (sx, sy), (int(outer_x), int(outer_y)), 4)
                        pygame.draw.circle(screen, (255, 255, 150), (sx, sy), coll_size // 4)
            
            elif obj_type == 'enemy':
                # ULTRA REALISTIC enemies with 3D detail
                enemy_size = int(obj['size'] * scale)
                if enemy_size > 10:
                    # Shadow
                    shadow_surf = pygame.Surface((enemy_size, enemy_size // 4), pygame.SRCALPHA)
                    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (0, 0, enemy_size, enemy_size // 4))
                    screen.blit(shadow_surf, (int(sx - enemy_size // 2), int(sy + enemy_size // 2)))
                    
                    # Animated bobbing
                    bob = math.sin(obj['animation_frame']) * 3 * scale
                    enemy_y = int(sy + bob)
                    
                    # SHOW IF ENEMY IS IN RANGE - Target indicator!
                    dist_to_player = math.sqrt((obj['x'] - player['x'])**2 + 
                                               (obj['y'] - player['y'])**2 +
                                               (obj['z'] - player['z'])**2)
                    
                    # Regular attack range indicator
                    if dist_to_player < 150:
                        # Draw targeting reticle - enemy is in attack range!
                        target_surf = pygame.Surface((enemy_size * 2, enemy_size * 2), pygame.SRCALPHA)
                        pygame.draw.circle(target_surf, (255, 200, 100, 120), (enemy_size, enemy_size), enemy_size, 4)
                        pygame.draw.line(target_surf, (255, 200, 100, 180), 
                                       (enemy_size - enemy_size, enemy_size), 
                                       (enemy_size + enemy_size, enemy_size), 3)
                        pygame.draw.line(target_surf, (255, 200, 100, 180), 
                                       (enemy_size, enemy_size - enemy_size), 
                                       (enemy_size, enemy_size + enemy_size), 3)
                        screen.blit(target_surf, (sx - enemy_size, enemy_y - enemy_size))
                    
                    # Special attack range indicator (much bigger range)
                    if 150 < dist_to_player < 300:
                        # Purple indicator for special attack range only
                        target_surf = pygame.Surface((enemy_size * 2, enemy_size * 2), pygame.SRCALPHA)
                        pygame.draw.circle(target_surf, (255, 100, 255, 100), (enemy_size, enemy_size), enemy_size, 3)
                        screen.blit(target_surf, (sx - enemy_size, enemy_y - enemy_size))
                    
                    # Draw different enemy types
                    if obj['type'] == 'goblin':
                        # Goblin - green with big eyes
                        pygame.draw.circle(screen, obj['color'], (sx, enemy_y), enemy_size // 2)
                        # Eyes
                        eye_size = max(3, int(enemy_size * 0.15))
                        pygame.draw.circle(screen, (255, 255, 0), (int(sx - enemy_size // 4), int(enemy_y - enemy_size // 6)), eye_size)
                        pygame.draw.circle(screen, (255, 255, 0), (int(sx + enemy_size // 4), int(enemy_y - enemy_size // 6)), eye_size)
                        pygame.draw.circle(screen, (0, 0, 0), (int(sx - enemy_size // 4), int(enemy_y - enemy_size // 6)), eye_size // 2)
                        pygame.draw.circle(screen, (0, 0, 0), (int(sx + enemy_size // 4), int(enemy_y - enemy_size // 6)), eye_size // 2)
                        # Mouth
                        pygame.draw.arc(screen, (50, 50, 50), (int(sx - enemy_size // 4), int(enemy_y), enemy_size // 2, enemy_size // 4), 0, math.pi, 2)
                    elif obj['type'] == 'orc':
                        # Orc - brown with tusks
                        pygame.draw.circle(screen, obj['color'], (sx, enemy_y), enemy_size // 2)
                        # Tusks
                        tusk_size = int(enemy_size * 0.2)
                        pygame.draw.polygon(screen, (240, 240, 220), [
                            (int(sx - enemy_size // 3), enemy_y),
                            (int(sx - enemy_size // 2), int(enemy_y + tusk_size)),
                            (int(sx - enemy_size // 4), enemy_y)
                        ])
                        pygame.draw.polygon(screen, (240, 240, 220), [
                            (int(sx + enemy_size // 3), enemy_y),
                            (int(sx + enemy_size // 2), int(enemy_y + tusk_size)),
                            (int(sx + enemy_size // 4), enemy_y)
                        ])
                        # Eyes
                        pygame.draw.circle(screen, (200, 0, 0), (int(sx - enemy_size // 5), int(enemy_y - enemy_size // 6)), max(2, int(enemy_size * 0.1)))
                        pygame.draw.circle(screen, (200, 0, 0), (int(sx + enemy_size // 5), int(enemy_y - enemy_size // 6)), max(2, int(enemy_size * 0.1)))
                    elif obj['type'] == 'demon':
                        # Demon - red with horns
                        pygame.draw.circle(screen, obj['color'], (sx, enemy_y), enemy_size // 2)
                        # Horns
                        horn_size = int(enemy_size * 0.3)
                        pygame.draw.polygon(screen, (150, 0, 0), [
                            (int(sx - enemy_size // 3), int(enemy_y - enemy_size // 2)),
                            (int(sx - enemy_size // 2), int(enemy_y - enemy_size // 2 - horn_size)),
                            (int(sx - enemy_size // 4), int(enemy_y - enemy_size // 2))
                        ])
                        pygame.draw.polygon(screen, (150, 0, 0), [
                            (int(sx + enemy_size // 3), int(enemy_y - enemy_size // 2)),
                            (int(sx + enemy_size // 2), int(enemy_y - enemy_size // 2 - horn_size)),
                            (int(sx + enemy_size // 4), int(enemy_y - enemy_size // 2))
                        ])
                        # Glowing eyes
                        pygame.draw.circle(screen, (255, 200, 0), (int(sx - enemy_size // 6), int(enemy_y - enemy_size // 8)), max(3, int(enemy_size * 0.12)))
                        pygame.draw.circle(screen, (255, 200, 0), (int(sx + enemy_size // 6), int(enemy_y - enemy_size // 8)), max(3, int(enemy_size * 0.12)))
                    elif obj['type'] == 'dragon':
                        # Dragon - purple with wings
                        pygame.draw.circle(screen, obj['color'], (sx, enemy_y), enemy_size // 2)
                        # Wings (flapping animation)
                        wing_angle = math.sin(obj['animation_frame'] * 2) * 0.3
                        wing_size = int(enemy_size * 0.6)
                        # Wing color (darker but valid)
                        wing_color = (max(0, obj['color'][0] - 30), max(0, obj['color'][1] - 30), max(0, obj['color'][2] - 30))
                        # Left wing
                        pygame.draw.polygon(screen, wing_color, [
                            (sx, enemy_y),
                            (int(sx - wing_size * math.cos(wing_angle)), int(enemy_y - wing_size * 0.5)),
                            (int(sx - wing_size * 0.5), enemy_y)
                        ])
                        # Right wing
                        pygame.draw.polygon(screen, wing_color, [
                            (sx, enemy_y),
                            (int(sx + wing_size * math.cos(wing_angle)), int(enemy_y - wing_size * 0.5)),
                            (int(sx + wing_size * 0.5), enemy_y)
                        ])
                        # Eyes
                        pygame.draw.circle(screen, (255, 0, 255), (int(sx - enemy_size // 6), int(enemy_y - enemy_size // 8)), max(3, int(enemy_size * 0.1)))
                        pygame.draw.circle(screen, (255, 0, 255), (int(sx + enemy_size // 6), int(enemy_y - enemy_size // 8)), max(3, int(enemy_size * 0.1)))
                    else:  # wraith
                        # Wraith - ghostly semi-transparent
                        wraith_surf = pygame.Surface((enemy_size, enemy_size), pygame.SRCALPHA)
                        pygame.draw.circle(wraith_surf, (*obj['color'], 180), (enemy_size // 2, enemy_size // 2), enemy_size // 2)
                        screen.blit(wraith_surf, (int(sx - enemy_size // 2), int(enemy_y - enemy_size // 2)))
                        # Glowing eyes
                        pygame.draw.circle(screen, (150, 255, 255), (int(sx - enemy_size // 5), int(enemy_y - enemy_size // 6)), max(2, int(enemy_size * 0.08)))
                        pygame.draw.circle(screen, (150, 255, 255), (int(sx + enemy_size // 5), int(enemy_y - enemy_size // 6)), max(2, int(enemy_size * 0.08)))
                    
                    # Health bar above enemy
                    if enemy_size > 20:
                        bar_width = enemy_size
                        bar_height = max(3, int(enemy_size * 0.1))
                        bar_y = int(enemy_y - enemy_size * 0.7)
                        # Background
                        pygame.draw.rect(screen, (60, 60, 60), (int(sx - bar_width // 2), bar_y, bar_width, bar_height))
                        # Health
                        health_ratio = obj['health'] / obj['max_health']
                        health_color = (int(255 * (1 - health_ratio)), int(255 * health_ratio), 0)
                        pygame.draw.rect(screen, health_color, (int(sx - bar_width // 2), bar_y, int(bar_width * health_ratio), bar_height))
            
            elif obj_type == 'boss':
                # EPIC BOSS - MASSIVE and detailed!
                boss_size = int(obj['size'] * scale)
                if boss_size > 20:
                    # Boss body
                    pygame.draw.circle(screen, (80, 0, 100), (sx, sy), boss_size // 2)
                    # Multiple eyes
                    for i in range(6):
                        angle = (i / 6) * 2 * math.pi + obj['animation']
                        eye_x = sx + math.cos(angle) * boss_size * 0.3
                        eye_y = sy + math.sin(angle) * boss_size * 0.3
                        pygame.draw.circle(screen, (255, 50, 50), (int(eye_x), int(eye_y)), max(5, boss_size // 15))
                    # Health bar
                    bar_width = boss_size * 2
                    bar_height = max(8, boss_size // 12)
                    bar_y = int(sy - boss_size * 0.8)
                    pygame.draw.rect(screen, (60, 0, 0), (int(sx - bar_width // 2), bar_y, bar_width, bar_height))
                    health_ratio = obj['health'] / obj['max_health']
                    pygame.draw.rect(screen, (255, 0, 0), (int(sx - bar_width // 2), bar_y, int(bar_width * health_ratio), bar_height))
                    pygame.draw.rect(screen, (255, 255, 255), (int(sx - bar_width // 2), bar_y, bar_width, bar_height), 2)
            
            elif obj_type == 'projectile':
                # Projectiles with glow
                proj_size = int(obj['size'] * scale)
                if proj_size > 2:
                    # Glow
                    for glow in range(2):
                        glow_surf = pygame.Surface((proj_size * 2 + glow * 4, proj_size * 2 + glow * 4), pygame.SRCALPHA)
                        pygame.draw.circle(glow_surf, (*obj['color'], 40), (proj_size + glow * 2, proj_size + glow * 2), proj_size + glow * 2)
                        screen.blit(glow_surf, (int(sx - proj_size - glow * 2), int(sy - proj_size - glow * 2)))
                    # Main projectile
                    pygame.draw.circle(screen, obj['color'], (sx, sy), proj_size)
            
            elif obj_type == 'player':
                # Player character
                player_size = int(obj['size'] * scale)
                if player_size > 15:
                    # Body
                    pygame.draw.rect(screen, (200, 50, 50), (int(sx - player_size * 0.25), int(sy - player_size * 0.15), int(player_size * 0.5), int(player_size * 0.45)))
                    # Head
                    pygame.draw.circle(screen, (230, 190, 160), (sx, int(sy - player_size * 0.3)), int(player_size * 0.25))
                    # Eyes
                    pygame.draw.circle(screen, (255, 255, 255), (int(sx - player_size * 0.1), int(sy - player_size * 0.35)), max(2, int(player_size * 0.08)))
                    pygame.draw.circle(screen, (255, 255, 255), (int(sx + player_size * 0.1), int(sy - player_size * 0.35)), max(2, int(player_size * 0.08)))
                    pygame.draw.circle(screen, (50, 30, 20), (int(sx - player_size * 0.1), int(sy - player_size * 0.33)), max(1, int(player_size * 0.04)))
                    pygame.draw.circle(screen, (50, 30, 20), (int(sx + player_size * 0.1), int(sy - player_size * 0.33)), max(1, int(player_size * 0.04)))
            
            elif obj_type == 'particle':
                # Particles
                part_size = int(obj['size'] * scale)
                if part_size > 0:
                    life_alpha = int((obj['life'] / 2.0) * 255)
                    if life_alpha > 0:
                        part_surf = pygame.Surface((part_size * 2, part_size * 2), pygame.SRCALPHA)
                        pygame.draw.circle(part_surf, (*obj['color'], min(255, life_alpha)), (part_size, part_size), part_size)
                        screen.blit(part_surf, (int(sx - part_size), int(sy - part_size)))
        
        
        # === EPIC HUD SYSTEM - Professional and Beautiful! ===
        # Apply camera shake to screen
        shake_offset_x = int(camera_shake_x)
        shake_offset_y = int(camera_shake_y)
        
        # Screen flash effect
        if screen_flash > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_alpha = int(screen_flash * 255)
            flash_surf.fill((*screen_flash_color, flash_alpha))
            screen.blit(flash_surf, (0, 0))
        
        # Semi-transparent HUD background
        hud_surf = pygame.Surface((WIDTH, 180), pygame.SRCALPHA)
        pygame.draw.rect(hud_surf, (0, 0, 0, 180), (0, 0, WIDTH, 180))
        screen.blit(hud_surf, (0, 0))
        
        # Vital stats with beautiful bars
        hud_font = pygame.font.Font(None, 32)
        bar_width = 250
        bar_height = 24
        bar_x = 30
        
        # Health bar
        health_label = hud_font.render("HEALTH", True, (255, 255, 255))
        screen.blit(health_label, (bar_x, 25))
        # Background
        pygame.draw.rect(screen, (80, 0, 0), (bar_x + 120, 30, bar_width, bar_height))
        # Health fill
        health_ratio = max(0, player['health'] / player['max_health'])
        health_color = (int(255 * (1 - health_ratio * 0.5)), int(255 * health_ratio), 0)
        pygame.draw.rect(screen, health_color, (bar_x + 120, 30, int(bar_width * health_ratio), bar_height))
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x + 120, 30, bar_width, bar_height), 3)
        # Value text
        health_val = hud_font.render(f"{int(player['health'])}/{player['max_health']}", True, (255, 255, 255))
        screen.blit(health_val, (bar_x + 125, 32))
        
        # Shield bar (if player has shield)
        if player['max_shield'] > 0:
            shield_label = hud_font.render("SHIELD", True, (100, 200, 255))
            screen.blit(shield_label, (bar_x, 60))
            pygame.draw.rect(screen, (0, 50, 80), (bar_x + 120, 65, bar_width, bar_height))
            shield_ratio = max(0, player['shield'] / player['max_shield'])
            pygame.draw.rect(screen, (100, 200, 255), (bar_x + 120, 65, int(bar_width * shield_ratio), bar_height))
            pygame.draw.rect(screen, (255, 255, 255), (bar_x + 120, 65, bar_width, bar_height), 3)
            shield_val = hud_font.render(f"{int(player['shield'])}/{player['max_shield']}", True, (255, 255, 255))
            screen.blit(shield_val, (bar_x + 125, 67))
            stamina_y = 95
        else:
            stamina_y = 60
        
        # Stamina bar
        stamina_label = hud_font.render("STAMINA", True, (100, 255, 100))
        screen.blit(stamina_label, (bar_x, stamina_y))
        pygame.draw.rect(screen, (0, 80, 0), (bar_x + 120, stamina_y + 5, bar_width, bar_height))
        stamina_ratio = max(0, player['stamina'] / player['max_stamina'])
        pygame.draw.rect(screen, (100, 255, 100), (bar_x + 120, stamina_y + 5, int(bar_width * stamina_ratio), bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x + 120, stamina_y + 5, bar_width, bar_height), 3)
        
        # Energy bar
        energy_label = hud_font.render("ENERGY", True, (255, 255, 100))
        screen.blit(energy_label, (bar_x, stamina_y + 35))
        pygame.draw.rect(screen, (80, 80, 0), (bar_x + 120, stamina_y + 40, bar_width, bar_height))
        energy_ratio = max(0, player['energy'] / player['max_energy'])
        pygame.draw.rect(screen, (255, 255, 100), (bar_x + 120, stamina_y + 40, int(bar_width * energy_ratio), bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x + 120, stamina_y + 40, bar_width, bar_height), 3)
        
        # ATTACK COOLDOWNS & INDICATORS - Very visible!
        attack_indicator_y = stamina_y + 75
        indicator_font = pygame.font.Font(None, 28)
        
        # Regular Attack indicator
        if player['attack_cooldown'] > 0:
            attack_color = (150, 150, 150)  # Gray when cooling down
            cooldown_text = f"[X] Attack: {player['attack_cooldown']:.1f}s"
        elif player['energy'] >= 10:
            attack_color = (100, 255, 100)  # Green when ready
            cooldown_text = "[X] Attack: READY!"
        else:
            attack_color = (255, 100, 100)  # Red when not enough energy
            cooldown_text = f"[X] Attack: Need {10 - int(player['energy'])} energy"
        
        attack_indicator = indicator_font.render(cooldown_text, True, attack_color)
        screen.blit(attack_indicator, (bar_x, attack_indicator_y))
        
        # Special Attack indicator
        if player['special_attack_cooldown'] > 0:
            special_color = (150, 150, 150)  # Gray when cooling down
            special_text = f"[Z] SPECIAL: {player['special_attack_cooldown']:.1f}s"
        elif player['energy'] >= 40:
            special_color = (255, 100, 255)  # Purple when ready
            special_text = "[Z] SPECIAL: READY! (MASSIVE DAMAGE)"
        else:
            special_color = (255, 100, 100)  # Red when not enough energy
            special_text = f"[Z] SPECIAL: Need {40 - int(player['energy'])} energy"
        
        special_indicator = indicator_font.render(special_text, True, special_color)
        screen.blit(special_indicator, (bar_x, attack_indicator_y + 30))
        
        # Attack range visualization - Show circles around player
        if keys[pygame.K_x] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            # Show regular attack range
            px_screen, py_screen, p_scale = project_3d(player['x'], player['y'], player['z'])
            if px_screen and p_scale > 0:
                range_radius = int(150 * p_scale)
                range_surf = pygame.Surface((range_radius * 2, range_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(range_surf, (255, 200, 100, 80), (range_radius, range_radius), range_radius, 5)
                screen.blit(range_surf, (px_screen - range_radius, py_screen - range_radius))
        
        if keys[pygame.K_z] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            # Show special attack range (much bigger!)
            px_screen, py_screen, p_scale = project_3d(player['x'], player['y'], player['z'])
            if px_screen and p_scale > 0:
                range_radius = int(300 * p_scale)
                range_surf = pygame.Surface((range_radius * 2, range_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(range_surf, (255, 100, 255, 60), (range_radius, range_radius), range_radius, 8)
                screen.blit(range_surf, (px_screen - range_radius, py_screen - range_radius))
                # Pulsing effect
                pulse = int(abs(math.sin(time_elapsed * 10)) * 30)
                pygame.draw.circle(range_surf, (255, 0, 255, 100 - pulse), (range_radius, range_radius), range_radius - pulse, 3)
                screen.blit(range_surf, (px_screen - range_radius, py_screen - range_radius))
        
        # Score and combo in top right
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"SCORE: {score}", True, (255, 215, 0))
        screen.blit(score_text, (WIDTH - score_text.get_width() - 30, 25))
        
        # Combo multiplier
        if combo_multiplier > 1.0:
            combo_font = pygame.font.Font(None, 40)
            combo_text = combo_font.render(f"COMBO x{combo_multiplier:.1f}!", True, (255, 100, 255))
            # Pulsing effect
            combo_scale = 1.0 + math.sin(time_elapsed * 10) * 0.1
            combo_surf = pygame.transform.scale(combo_text, 
                (int(combo_text.get_width() * combo_scale), int(combo_text.get_height() * combo_scale)))
            screen.blit(combo_surf, (WIDTH - combo_surf.get_width() - 30, 80))
        
        # Time elapsed
        time_font = pygame.font.Font(None, 32)
        time_text = time_font.render(f"TIME: {int(time_elapsed)}s", True, (200, 200, 200))
        screen.blit(time_text, (WIDTH - time_text.get_width() - 30, 130))
        
        # Current objectives - bottom center
        obj_bg = pygame.Surface((WIDTH - 100, 100), pygame.SRCALPHA)
        pygame.draw.rect(obj_bg, (0, 0, 0, 200), (0, 0, WIDTH - 100, 100))
        screen.blit(obj_bg, (50, HEIGHT - 120))
        
        obj_font = pygame.font.Font(None, 36)
        mission_text = obj_font.render(f"MISSION: Collect Treasures & Defeat All Enemies!", True, (100, 200, 255))
        screen.blit(mission_text, (WIDTH // 2 - mission_text.get_width() // 2, HEIGHT - 110))
        
        # Progress stats
        stats_font = pygame.font.Font(None, 30)
        stats_text = stats_font.render(
            f"Treasures: {coins_collected}/25  |  Enemies: {enemies_defeated}/15  |  Bosses: {len(bosses)}  |  Progress: {objectives_completed}/{total_objectives}", 
            True, (255, 255, 150))
        screen.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT - 70))
        
        # Rage mode indicator
        if player['rage_mode'] > 0:
            rage_font = pygame.font.Font(None, 60)
            rage_text = rage_font.render("⚡ RAGE MODE ACTIVE! ⚡", True, (255, 0, 255))
            # Pulsing rage text
            rage_scale = 1.0 + math.sin(time_elapsed * 15) * 0.2
            rage_surf = pygame.transform.scale(rage_text, 
                (int(rage_text.get_width() * rage_scale), int(rage_text.get_height() * rage_scale)))
            screen.blit(rage_surf, (WIDTH // 2 - rage_surf.get_width() // 2, HEIGHT // 2 - 100))
        
        # Win condition display
        if objectives_completed >= total_objectives:
            win_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(win_bg, (0, 0, 0, 150), (0, 0, WIDTH, HEIGHT))
            screen.blit(win_bg, (0, 0))
            
            win_font = pygame.font.Font(None, 100)
            win_text = win_font.render("🎉 VICTORY! 🎉", True, (0, 255, 0))
            screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50))
            
            score_display = win_font.render(f"Final Score: {score}", True, (255, 215, 0))
            screen.blit(score_display, (WIDTH // 2 - score_display.get_width() // 2, HEIGHT // 2 + 50))
        
        # Controls - top center - CLEARER!
        controls_font = pygame.font.Font(None, 26)
        controls_bg = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
        pygame.draw.rect(controls_bg, (0, 0, 0, 180), (0, 0, WIDTH, 40))
        screen.blit(controls_bg, (0, 0))
        
        controls_text = controls_font.render(
            "WASD: Move | SPACE: Jump | [X]: Attack (close range) | [Z]: SPECIAL (huge range, 40 energy) | ESC: Exit", 
            True, (255, 255, 100))
        screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, 12))
        
        # Weather indicator
        if weather != 'clear':
            weather_text = controls_font.render(f"Weather: {weather.upper()}", True, (150, 200, 255))
            screen.blit(weather_text, (WIDTH // 2 - weather_text.get_width() // 2, HEIGHT - 35))
        
        pygame.display.flip()
    
    # Exit fade out animation
    for fade in range(0, 255, 15):
        fade_surf = pygame.Surface((WIDTH, HEIGHT))
        fade_surf.set_alpha(fade)
        fade_surf.fill((0, 0, 0))
        screen.blit(fade_surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)


def grass_mode():
    """Grass Mode - a peaceful grassy field"""
    global menu_key_buffer
    screen_width, screen_height = WIDTH, HEIGHT
    
    # Track ttt key press for unlocking Combine Mode
    grass_key_buffer = ""
    
    running = True
    while running:
        screen.fill((34, 139, 34))  # Forest green background
        
        # Draw grass
        grass_font = pygame.font.Font(None, 80)
        for i in range(10):
            for j in range(8):
                grass_text = grass_font.render("🌿", True, (0, 200, 0))
                screen.blit(grass_text, (i * 100 + random.randint(-10, 10), j * 100 + random.randint(-10, 10)))
        
        # Title
        title_font = pygame.font.Font(None, 100)
        title = title_font.render("GRASS MODE", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Instructions
        inst_font = pygame.font.Font(None, 40)
        inst = inst_font.render("Press ESC to exit", True, (200, 200, 200))
        screen.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT - 100))
        
        # Show hint if wolf vomited this
        if secret_hack.get('grass_mode_unlocked') and not secret_hack.get('combine_mode_unlocked'):
            hint = inst_font.render("Something feels strange about this grass...", True, (255, 255, 0))
            screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT // 2))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                
                # Track ttt for Combine Mode unlock
                if key_name == 't':
                    grass_key_buffer += key_name
                    if len(grass_key_buffer) > 3:
                        grass_key_buffer = grass_key_buffer[-3:]
                    
                    # Check for ttt
                    if grass_key_buffer == "ttt" and not secret_hack.get('combine_mode_unlocked'):
                        secret_hack['combine_mode_unlocked'] = True
                        # Show wolf vomit animation for Combine Mode
                        wolf_vomit_animation("Combine Mode")
                        running = False
                        break
                else:
                    grass_key_buffer = ""
                
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        pygame.time.wait(16)

def combine_mode():
    """Combine Mode - ENHANCED! A dog's epic journey to become human in a vast scrolling world"""
    clock = pygame.time.Clock()
    
    # WORLD CAMERA - Much bigger world!
    camera_x = 0
    world_width = 10000  # Huge scrolling world!
    
    # Dog state - More fluid movement
    dog_x = 100  # Screen position
    dog_world_x = 100  # Position in world
    dog_y = HEIGHT - 150
    dog_speed = 8  # Faster base speed
    dog_direction = 1  # 1 = right, -1 = left
    dog_velocity_y = 0
    dog_velocity_x = 0  # Momentum
    is_jumping = False
    is_double_jump_available = False  # DOUBLE JUMP!
    can_dash = True
    dash_cooldown = 0
    
    # Transformation progress (0 to 100)
    transformation = 0
    items_collected = 0
    distance_traveled = 0
    
    # Score multiplier
    score_multiplier = 1.0
    
    # Obstacles - More variety and danger
    obstacles = []
    obstacle_spawn_timer = 0
    obstacle_spawn_interval = 2.0  # More frequent
    
    # ENEMIES - New!
    enemies = []
    enemy_spawn_timer = 0
    enemy_spawn_interval = 5.0
    
    # PLATFORMS - New jumping challenge!
    platforms = []
    platform_spawn_timer = 0
    platform_spawn_interval = 4.0
    
    # POWER-UPS - New!
    powerups = []
    powerup_spawn_timer = 0
    powerup_spawn_interval = 10.0
    active_powerups = {}  # {powerup_type: remaining_time}
    
    # Health/Lives system - Harder
    health = 100
    max_health = 100
    lives = 5  # More lives for harder game
    invincible_timer = 0
    invincible_duration = 1.5  # Shorter invincibility
    
    # Stamina system - Enhanced
    stamina = 100
    max_stamina = 100
    is_sprinting = False
    stamina_regen_rate = 25  # Faster regen
    
    # Weather effects - More dramatic
    weather_particles = []
    weather_type = "clear"
    weather_timer = 0
    weather_intensity = 1.0
    
    # NPCs - More helpful
    npcs = []
    npc_spawn_timer = 0
    npc_spawn_interval = 12.0
    
    # Background elements - Parallax layers
    bg_buildings = []
    bg_clouds = []
    bg_trees = []
    
    # Ambient messages
    ambient_messages = []
    ambient_timer = 0
    
    # Collectibles - EXPANDED with 25+ items!
    items = []
    item_definitions = [
        # Common (70%)
        {"emoji": "👔", "name": "Shirt", "points": 3, "rarity": "common"},
        {"emoji": "👞", "name": "Shoes", "points": 3, "rarity": "common"},
        {"emoji": "🎩", "name": "Hat", "points": 3, "rarity": "common"},
        {"emoji": "👓", "name": "Glasses", "points": 3, "rarity": "common"},
        {"emoji": "📚", "name": "Book", "points": 3, "rarity": "common"},
        {"emoji": "☕", "name": "Coffee", "points": 3, "rarity": "common"},
        {"emoji": "🍔", "name": "Burger", "points": 3, "rarity": "common"},
        {"emoji": "🔑", "name": "Keys", "points": 3, "rarity": "common"},
        {"emoji": "🕶️", "name": "Sunglasses", "points": 3, "rarity": "common"},
        {"emoji": "🧳", "name": "Suitcase", "points": 3, "rarity": "common"},
        # Uncommon (20%)
        {"emoji": "💼", "name": "Briefcase", "points": 5, "rarity": "uncommon"},
        {"emoji": "💻", "name": "Laptop", "points": 5, "rarity": "uncommon"},
        {"emoji": "📱", "name": "Phone", "points": 5, "rarity": "uncommon"},
        {"emoji": "💍", "name": "Ring", "points": 5, "rarity": "uncommon"},
        {"emoji": "⌚", "name": "Watch", "points": 5, "rarity": "uncommon"},
        {"emoji": "🎧", "name": "Headphones", "points": 5, "rarity": "uncommon"},
        {"emoji": "�", "name": "Camera", "points": 5, "rarity": "uncommon"},
        # Rare (8%)
        {"emoji": "🎓", "name": "Diploma", "points": 8, "rarity": "rare"},
        {"emoji": "🎻", "name": "Violin", "points": 8, "rarity": "rare"},
        {"emoji": "🎨", "name": "Art", "points": 8, "rarity": "rare"},
        {"emoji": "🏆", "name": "Trophy", "points": 8, "rarity": "rare"},
        {"emoji": "💎", "name": "Diamond", "points": 10, "rarity": "rare"},
        # Epic (2%)
        {"emoji": "💰", "name": "Money", "points": 15, "rarity": "epic"},
        {"emoji": "👑", "name": "Crown", "points": 20, "rarity": "epic"},
        {"emoji": "🎪", "name": "Talent", "points": 18, "rarity": "epic"},
    ]
    
    spawn_timer = 0
    spawn_interval = 0.8  # Much faster spawning
    
    # Particle effects - More spectacular
    particles = []
    
    # Story progression
    story_phase = 0
    
    running = True
    game_time = 0
    show_celebration = False
    celebration_timer = 0
    
    # Walking animation - Smoother
    walk_frame = 0
    
    # Combo system - Enhanced
    combo_count = 0
    combo_timer = 0
    combo_timeout = 2.5  # More forgiving
    highest_combo = 0
    
    # Difficulty scaling
    difficulty_multiplier = 1.0
    
    # Initialize background elements
    for i in range(15):
        bg_buildings.append({
            'x': i * 300,
            'height': random.randint(200, 400),
            'width': random.randint(150, 250),
            'color': (random.randint(40, 80), random.randint(40, 80), random.randint(80, 120)),
            'windows': [(random.randint(0, 200), random.randint(0, 400)) for _ in range(random.randint(8, 20))]
        })
    
    for i in range(20):
        bg_clouds.append({
            'x': random.randint(0, world_width),
            'y': random.randint(50, 250),
            'speed': random.uniform(0.1, 0.3),
            'size': random.randint(40, 100)
        })
    
    for i in range(30):
        bg_trees.append({
            'x': i * 250 + random.randint(-50, 50),
            'height': random.randint(80, 150)
        })
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        game_time += dt
        spawn_timer += dt
        walk_frame += 0.3
        obstacle_spawn_timer += dt
        enemy_spawn_timer += dt
        platform_spawn_timer += dt
        powerup_spawn_timer += dt
        npc_spawn_timer += dt
        weather_timer += dt
        ambient_timer += dt
        
        # Update distance traveled
        distance_traveled = dog_world_x / 10
        
        # Increase difficulty over time
        difficulty_multiplier = 1.0 + (distance_traveled / 1000)
        
        # Update dash cooldown
        if dash_cooldown > 0:
            dash_cooldown -= dt
            if dash_cooldown <= 0:
                can_dash = True
        
        # Update invincibility
        if invincible_timer > 0:
            invincible_timer -= dt
        
        # Update combo timer
        if combo_timer > 0:
            combo_timer -= dt
            if combo_timer <= 0:
                combo_count = 0
                score_multiplier = 1.0
        else:
            score_multiplier = 1.0 + (combo_count * 0.1)
        
        # Update active powerups
        for powerup_type in list(active_powerups.keys()):
            active_powerups[powerup_type] -= dt
            if active_powerups[powerup_type] <= 0:
                del active_powerups[powerup_type]
        
        # Regenerate stamina
        if not is_sprinting and stamina < max_stamina:
            regen = stamina_regen_rate
            if 'energy_boost' in active_powerups:
                regen *= 2
            stamina = min(max_stamina, stamina + dt * regen)
        
        # Auto-heal with health powerup
        if 'health_regen' in active_powerups and health < max_health:
            health = min(max_health, health + dt * 10)
        
        # Change weather based on progression and randomness
        if weather_timer >= 15:
            weather_timer = 0
            if story_phase < 2:
                weather_type = random.choice(["clear", "rain", "rain", "storm"])
            elif story_phase < 4:
                weather_type = random.choice(["clear", "clear", "rain", "snow"])
            else:
                weather_type = "clear"
            weather_intensity = random.uniform(0.5, 1.5)
        
        # Add ambient messages
        if ambient_timer >= 8 and story_phase < 4:
            ambient_timer = 0
            messages = {
                0: ["A stray searching for purpose...", "The cold city streets...", "Dreams of being human...", "Alone in the world..."],
                1: ["Learning to walk upright!", "Civilization beckons!", "Progress feels good!", "Almost there..."],
                2: ["The city accepts you!", "You're becoming civilized!", "Humans notice you!", "Keep pushing forward!"],
                3: ["So close to your dream!", "Just a bit more!", "You can feel it!", "The transformation nears..."]
            }
            if story_phase in messages:
                ambient_messages.append({
                    'text': random.choice(messages[story_phase]),
                    'life': 4.0,
                    'y': 150,
                    'x': WIDTH // 2
                })
        
        # Spawn obstacles (things that damage you)
        if obstacle_spawn_timer >= obstacle_spawn_interval and transformation < 100 and story_phase >= 1:
            obstacle_spawn_timer = 0
            obstacle_type = random.choice(["car", "trash", "puddle", "fence"])
            obstacles.append({
                'x': WIDTH + 50,
                'y': HEIGHT - 160 if obstacle_type == "fence" else HEIGHT - 120,
                'type': obstacle_type,
                'speed': random.uniform(4, 6),
                'damage': 10 if obstacle_type == "car" else 5
            })
        
        # Spawn NPCs (helpful humans)
        if npc_spawn_timer >= npc_spawn_interval and transformation < 100 and story_phase >= 2:
            npc_spawn_timer = 0
            npc_types = [
                {"emoji": "👨", "message": "Keep trying, buddy!", "boost": 3},
                {"emoji": "👩", "message": "You can do it!", "boost": 3},
                {"emoji": "🧑", "message": "Almost human!", "boost": 5},
                {"emoji": "👴", "message": "I believe in you!", "boost": 4}
            ]
            npc_def = random.choice(npc_types)
            npcs.append({
                'x': WIDTH + 100,
                'y': HEIGHT - 140,
                'type': npc_def,
                'given_boost': False
            })
        
        # Spawn new items with rarity-based spawning
        if spawn_timer >= spawn_interval and transformation < 100:
            spawn_timer = 0
            item_x = WIDTH + random.randint(50, 200)
            item_y = random.randint(HEIGHT - 240, HEIGHT - 120)
            
            # Rarity-based selection
            roll = random.random()
            if roll < 0.05:  # 5% epic
                possible_items = [i for i in item_definitions if i.get('rarity') == 'epic']
            elif roll < 0.15:  # 10% rare
                possible_items = [i for i in item_definitions if i.get('rarity') == 'rare']
            elif roll < 0.35:  # 20% uncommon
                possible_items = [i for i in item_definitions if i.get('rarity') == 'uncommon']
            else:  # 65% common
                possible_items = [i for i in item_definitions if i.get('rarity') == 'common']
            
            if possible_items:
                item_def = random.choice(possible_items)
                items.append({
                    'x': item_x,
                    'y': item_y,
                    'emoji': item_def['emoji'],
                    'name': item_def['name'],
                    'points': item_def['points'],
                    'rarity': item_def.get('rarity', 'common'),
                    'collected': False,
                    'float_offset': random.uniform(0, 6.28)
                })
        
        # Update story phase
        if transformation < 20:
            story_phase = 0
        elif transformation < 40:
            story_phase = 1
        elif transformation < 70:
            story_phase = 2
        elif transformation < 100:
            story_phase = 3
        else:
            story_phase = 4
            if not show_celebration:
                show_celebration = True
                celebration_timer = 0
                # Mark that player became human! This changes the menu pointer THIS SESSION ONLY
                secret_hack['became_human'] = True
                
                # PERMANENT REWARD: Unlock GOD MODE FOREVER!
                if not secret_hack.get('god_mode_unlocked'):
                    secret_hack['god_mode_unlocked'] = True
                    save_secret_hack()
                    print("🌟✨ COMBINE MODE COMPLETED! ✨🌟")
                    print("🔥 GOD MODE UNLOCKED PERMANENTLY! 🔥")
                    print("💪 You now have SUPERPOWERS in Battle Mode:")
                    print("   - Press 'G' to activate God Mode")
                    print("   - Infinite health, super speed, mega damage!")
                else:
                    print("🎉 YOU BECAME HUMAN! Menu pointer is now human (until you restart the game)!")
        
        # Background - changes with transformation
        if story_phase == 0:
            # Dog's alley - dark and gloomy
            screen.fill((40, 40, 60))
        elif story_phase == 1:
            # Warming up
            screen.fill((60, 70, 100))
        elif story_phase == 2:
            # City street
            screen.fill((100, 120, 150))
        elif story_phase == 3:
            # Bright city
            screen.fill((135, 180, 230))
        else:
            # Human world - vibrant and alive
            screen.fill((180, 220, 255))
        
        # Draw ground
        ground_y = HEIGHT - 80
        ground_color = (80, 60, 40) if story_phase < 2 else (100, 100, 100)
        pygame.draw.rect(screen, ground_color, (0, ground_y, WIDTH, 80))
        
        # Draw city background elements
        if story_phase >= 2:
            # Buildings in background
            for i in range(5):
                building_x = i * 250 - (game_time * 20) % 250
                building_height = 150 + (i % 3) * 50
                pygame.draw.rect(screen, (60, 60, 80), 
                               (int(building_x), ground_y - building_height, 200, building_height))
                # Windows
                for row in range(int(building_height // 30)):
                    for col in range(3):
                        window_x = int(building_x) + 30 + col * 60
                        window_y = ground_y - building_height + 20 + row * 30
                        window_color = (255, 255, 150) if random.random() > 0.3 else (50, 50, 70)
                        pygame.draw.rect(screen, window_color, (window_x, window_y, 25, 20))
        
        # Weather effects
        if weather_type == "rain":
            # Spawn rain particles
            if random.random() < 0.3:
                weather_particles.append({
                    'x': random.randint(0, WIDTH),
                    'y': -10,
                    'speed': random.uniform(8, 12),
                    'type': 'rain'
                })
        elif weather_type == "snow":
            # Spawn snow particles
            if random.random() < 0.2:
                weather_particles.append({
                    'x': random.randint(0, WIDTH),
                    'y': -10,
                    'speed': random.uniform(2, 4),
                    'drift': random.uniform(-1, 1),
                    'type': 'snow'
                })
        
        # Update and draw weather particles
        for wp in weather_particles[:]:
            if wp['type'] == 'rain':
                wp['y'] += wp['speed']
                pygame.draw.line(screen, (100, 100, 255), 
                               (int(wp['x']), int(wp['y'])), 
                               (int(wp['x']), int(wp['y'] + 10)), 2)
            else:  # snow
                wp['y'] += wp['speed']
                wp['x'] += wp['drift']
                pygame.draw.circle(screen, (255, 255, 255), 
                                 (int(wp['x']), int(wp['y'])), 3)
            
            if wp['y'] > HEIGHT:
                weather_particles.remove(wp)
        
        # Story text at top
        story_font = pygame.font.Font(None, 40)
        stories = [
            "You are a lonely dog... dreaming of being human",
            "Collecting human items... feeling more civilized!",
            "You're walking upright now... almost there!",
            "So close to achieving your dream!",
            "🎉 YOU BECAME HUMAN! 🎉"
        ]
        
        story_text = story_font.render(stories[story_phase], True, (255, 255, 255))
        # Draw text with shadow
        shadow_surf = story_font.render(stories[story_phase], True, (0, 0, 0))
        screen.blit(shadow_surf, (WIDTH//2 - story_text.get_width()//2 + 2, 22))
        screen.blit(story_text, (WIDTH//2 - story_text.get_width()//2, 20))
        
        # Progress bar
        bar_width = 400
        bar_height = 30
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = 70
        
        # Background bar
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        # Progress bar
        progress_width = int((transformation / 100) * bar_width)
        bar_color = [(200, 50, 50), (200, 150, 50), (150, 200, 50), (100, 200, 100), (255, 215, 0)][story_phase]
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, progress_width, bar_height))
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 3)
        
        # Percentage text
        percent_font = pygame.font.Font(None, 28)
        percent_text = percent_font.render(f"{int(transformation)}% Human", True, (255, 255, 255))
        screen.blit(percent_text, (WIDTH // 2 - percent_text.get_width() // 2, bar_y + 5))
        
        # Handle input
        keys = pygame.key.get_pressed()
        moving = False
        
        # Sprint with SHIFT if stamina available
        is_sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        current_speed = dog_speed
        
        if is_sprinting and stamina > 0:
            current_speed = dog_speed * 1.8
            stamina -= dt * 30  # Drain stamina
            if stamina < 0:
                stamina = 0
                is_sprinting = False
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dog_x -= current_speed
            dog_direction = -1
            moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dog_x += current_speed
            dog_direction = 1
            moving = True
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and not is_jumping:
            # Jumping costs stamina
            if stamina >= 20:
                dog_velocity_y = -12
                is_jumping = True
                stamina -= 20
            else:
                dog_velocity_y = -8  # Weak jump
                is_jumping = True
        
        # Gravity and jumping
        if is_jumping:
            dog_y += dog_velocity_y
            dog_velocity_y += 0.6  # Gravity
            
            # Land on ground
            if dog_y >= HEIGHT - 150:
                dog_y = HEIGHT - 150
                is_jumping = False
                dog_velocity_y = 0
        
        # Keep dog on screen horizontally
        dog_x = max(50, min(WIDTH - 100, dog_x))
        
        # Draw and update items
        for item in items[:]:
            if not item['collected']:
                # Move items left (world scrolling)
                item['x'] -= 3
                
                # Floating animation
                float_y = item['y'] + math.sin(game_time * 2 + item['float_offset']) * 10
                
                # Draw item with glow effect
                item_font = pygame.font.Font(None, 55)
                item_text = item_font.render(item['emoji'], True, (255, 255, 255))
                
                # Glow circle - different colors based on rarity
                rarity_colors = {
                    'common': (200, 200, 200),
                    'uncommon': (100, 255, 100),
                    'rare': (100, 150, 255),
                    'epic': (255, 215, 0)
                }
                glow_color = rarity_colors.get(item.get('rarity', 'common'), (255, 255, 150))
                glow_radius = 25 + math.sin(game_time * 3 + item['float_offset']) * 5
                pygame.draw.circle(screen, glow_color, 
                                 (int(item['x']), int(float_y)), int(glow_radius))
                
                screen.blit(item_text, (int(item['x']) - 20, int(float_y) - 20))
                
                # Item name label
                label_font = pygame.font.Font(None, 22)
                label = label_font.render(item['name'], True, (255, 255, 255))
                screen.blit(label, (int(item['x']) - label.get_width()//2, int(float_y) + 30))
                
                # Collision with dog
                dog_rect = pygame.Rect(dog_x, dog_y, 60, 80)
                item_rect = pygame.Rect(item['x'] - 25, float_y - 25, 50, 50)
                
                if dog_rect.colliderect(item_rect):
                    item['collected'] = True
                    bonus_points = item['points']
                    
                    # Combo system - collect items quickly for multiplier
                    combo_count += 1
                    combo_timer = combo_timeout
                    if combo_count > highest_combo:
                        highest_combo = combo_count
                    
                    # Bonus from combo
                    if combo_count > 1:
                        bonus_points += combo_count
                    
                    transformation = min(100, transformation + bonus_points)
                    items_collected += 1
                    
                    # Create particles with rarity-based colors
                    particle_colors = {
                        'common': [(200, 200, 200), (220, 220, 220), (180, 180, 180)],
                        'uncommon': [(100, 200, 100), (120, 255, 120), (80, 180, 80)],
                        'rare': [(100, 100, 255), (150, 150, 255), (80, 80, 220)],
                        'epic': [(255, 215, 0), (255, 255, 100), (255, 200, 50)]
                    }
                    colors = particle_colors.get(item.get('rarity', 'common'), [(255, 200, 0)])
                    
                    # Create particles
                    for _ in range(30 if item.get('rarity') == 'epic' else 20):
                        particles.append({
                            'x': item['x'],
                            'y': float_y,
                            'vx': random.uniform(-5, 5),
                            'vy': random.uniform(-8, -2),
                            'life': 1.0,
                            'color': random.choice(colors)
                        })
                
                # Remove items that went off screen
                if item['x'] < -100:
                    items.remove(item)
        
        # Update and draw obstacles
        for obstacle in obstacles[:]:
            obstacle['x'] -= obstacle['speed']
            
            # Draw obstacle
            if obstacle['type'] == 'car':
                # Draw a simple car
                pygame.draw.rect(screen, (200, 0, 0), 
                               (int(obstacle['x']), int(obstacle['y']), 70, 40))
                pygame.draw.rect(screen, (100, 100, 200), 
                               (int(obstacle['x'] + 10), int(obstacle['y'] - 15), 50, 20))
                # Wheels
                pygame.draw.circle(screen, (30, 30, 30), 
                                 (int(obstacle['x'] + 15), int(obstacle['y'] + 40)), 8)
                pygame.draw.circle(screen, (30, 30, 30), 
                                 (int(obstacle['x'] + 55), int(obstacle['y'] + 40)), 8)
            elif obstacle['type'] == 'trash':
                # Draw trash can
                pygame.draw.rect(screen, (80, 80, 80), 
                               (int(obstacle['x']), int(obstacle['y']), 35, 50))
                trash_font = pygame.font.Font(None, 40)
                trash_text = trash_font.render("🗑️", True, (255, 255, 255))
                screen.blit(trash_text, (int(obstacle['x']), int(obstacle['y'])))
            elif obstacle['type'] == 'puddle':
                # Draw puddle
                pygame.draw.ellipse(screen, (50, 100, 200), 
                                  (int(obstacle['x']), int(obstacle['y']), 60, 20))
            elif obstacle['type'] == 'fence':
                # Draw fence
                for i in range(4):
                    fence_x = int(obstacle['x'] + i * 15)
                    pygame.draw.rect(screen, (139, 69, 19), 
                                   (fence_x, int(obstacle['y']), 10, 60))
            
            # Collision with dog
            dog_rect = pygame.Rect(dog_x, dog_y, 60, 80)
            obstacle_rect = pygame.Rect(obstacle['x'], obstacle['y'], 
                                       70 if obstacle['type'] == 'car' else 40, 
                                       40 if obstacle['type'] == 'car' else 50)
            
            if dog_rect.colliderect(obstacle_rect) and invincible_timer <= 0:
                health -= obstacle['damage']
                invincible_timer = invincible_duration
                
                # Damage particles
                for _ in range(15):
                    particles.append({
                        'x': dog_x + 30,
                        'y': dog_y + 40,
                        'vx': random.uniform(-4, 4),
                        'vy': random.uniform(-6, -1),
                        'life': 0.8,
                        'color': (255, 0, 0)
                    })
                
                # Lose a life if health runs out
                if health <= 0:
                    lives -= 1
                    health = 100
                    if lives <= 0:
                        # Game over
                        running = False
            
            # Remove obstacles off screen
            if obstacle['x'] < -100:
                obstacles.remove(obstacle)
        
        # Update and draw NPCs
        for npc in npcs[:]:
            npc['x'] -= 2  # NPCs move slower
            
            # Draw NPC
            npc_font = pygame.font.Font(None, 60)
            npc_text = npc_font.render(npc['type']['emoji'], True, (255, 255, 255))
            screen.blit(npc_text, (int(npc['x']), int(npc['y'])))
            
            # Speech bubble with message
            if abs(npc['x'] - dog_x) < 100 and not npc['given_boost']:
                bubble_font = pygame.font.Font(None, 24)
                bubble = bubble_font.render(npc['type']['message'], True, (255, 255, 255))
                bubble_bg = pygame.Rect(npc['x'] - 60, npc['y'] - 50, bubble.get_width() + 10, 30)
                pygame.draw.rect(screen, (50, 50, 50), bubble_bg, border_radius=8)
                pygame.draw.rect(screen, (255, 255, 255), bubble_bg, 2, border_radius=8)
                screen.blit(bubble, (npc['x'] - 55, npc['y'] - 45))
            
            # Give boost if close enough
            dog_rect = pygame.Rect(dog_x, dog_y, 60, 80)
            npc_rect = pygame.Rect(npc['x'], npc['y'], 40, 60)
            
            if dog_rect.colliderect(npc_rect) and not npc['given_boost']:
                npc['given_boost'] = True
                transformation = min(100, transformation + npc['type']['boost'])
                
                # Healing particles
                for _ in range(15):
                    particles.append({
                        'x': dog_x + 30,
                        'y': dog_y + 20,
                        'vx': random.uniform(-3, 3),
                        'vy': random.uniform(-5, -1),
                        'life': 1.0,
                        'color': (100, 255, 100)
                    })
            
            # Remove NPCs off screen
            if npc['x'] < -100:
                npcs.remove(npc)
        
        # Update and draw particles
        for particle in particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.3  # Gravity
            particle['life'] -= 0.02
            
            if particle['life'] <= 0:
                particles.remove(particle)
            else:
                alpha = int(particle['life'] * 255)
                size = int(particle['life'] * 8)
                pygame.draw.circle(screen, particle['color'], 
                                 (int(particle['x']), int(particle['y'])), size)
        
        # Draw the dog/human (transforms based on progress)
        draw_character(screen, dog_x, dog_y, transformation, dog_direction, walk_frame, moving)
        
        # Celebration when complete
        if show_celebration:
            celebration_timer += dt
            
            # Fireworks
            for i in range(5):
                angle = (celebration_timer * 2 + i * 1.256) % 6.28
                firework_x = WIDTH // 2 + math.cos(angle) * 200
                firework_y = HEIGHT // 2 + math.sin(angle) * 150
                pygame.draw.circle(screen, (255, 200 + int(math.sin(celebration_timer * 5) * 55), 0), 
                                 (int(firework_x), int(firework_y)), 15)
            
            # Victory message
            victory_font = pygame.font.Font(None, 80)
            victory_msgs = [
                "CONGRATULATIONS!",
                f"You collected {items_collected} human items!",
                "You are now fully HUMAN!"
            ]
            
            for i, msg in enumerate(victory_msgs):
                color_shift = int(abs(math.sin(celebration_timer * 2 + i)) * 55)  # Max 55, so 200+55=255
                msg_surf = victory_font.render(msg, True, (255, 200 + color_shift, 100))
                y_pos = 200 + i * 80
                screen.blit(msg_surf, (WIDTH // 2 - msg_surf.get_width() // 2, y_pos))
        
        # Instructions
        inst_font = pygame.font.Font(None, 26)
        inst = inst_font.render("Arrow keys/WASD, SHIFT=Sprint, SPACE=Jump | ESC=Exit", True, (255, 255, 255))
        screen.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT - 35))
        
        # Health bar (top left)
        health_bar_width = 200
        health_bar_height = 20
        pygame.draw.rect(screen, (60, 60, 60), (20, 110, health_bar_width, health_bar_height))
        health_width = int((health / 100) * health_bar_width)
        health_color = (0, 255, 0) if health > 50 else (255, 255, 0) if health > 25 else (255, 0, 0)
        pygame.draw.rect(screen, health_color, (20, 110, health_width, health_bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (20, 110, health_bar_width, health_bar_height), 2)
        health_text = name_font.render(f"❤️ Health: {int(health)}", True, (255, 255, 255))
        screen.blit(health_text, (20, 90))
        
        # Lives counter
        lives_text = name_font.render(f"Lives: {'💖' * lives}", True, (255, 255, 255))
        screen.blit(lives_text, (20, 135))
        
        # Stamina bar (top left, below health)
        pygame.draw.rect(screen, (60, 60, 60), (20, 170, health_bar_width, health_bar_height))
        stamina_width = int((stamina / max_stamina) * health_bar_width)
        stamina_color = (100, 200, 255) if stamina > 50 else (255, 200, 100)
        pygame.draw.rect(screen, stamina_color, (20, 170, stamina_width, health_bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (20, 170, health_bar_width, health_bar_height), 2)
        stamina_text = name_font.render(f"⚡ Stamina: {int(stamina)}", True, (255, 255, 255))
        screen.blit(stamina_text, (20, 150))
        
        # Combo counter (top right)
        if combo_count > 1:
            combo_font = pygame.font.Font(None, 50)
            combo_text = combo_font.render(f"COMBO x{combo_count}!", True, (255, 215, 0))
            screen.blit(combo_text, (WIDTH - 250, 20))
            combo_bar_width = 200
            combo_progress = (combo_timer / combo_timeout) * combo_bar_width
            pygame.draw.rect(screen, (60, 60, 60), (WIDTH - 220, 70, combo_bar_width, 10))
            pygame.draw.rect(screen, (255, 215, 0), (WIDTH - 220, 70, int(combo_progress), 10))
        
        # Invincibility indicator
        if invincible_timer > 0:
            inv_text = font.render("INVINCIBLE!", True, (0, 255, 255))
            screen.blit(inv_text, (WIDTH // 2 - inv_text.get_width() // 2, 110))
        
        # Ambient messages
        for msg in ambient_messages[:]:
            msg['life'] -= dt
            msg['y'] += dt * 10  # Float up
            if msg['life'] > 0:
                alpha = int((msg['life'] / 3.0) * 255)
                ambient_font = pygame.font.Font(None, 32)
                ambient_surf = ambient_font.render(msg['text'], True, (200, 200, 255))
                screen.blit(ambient_surf, (WIDTH // 2 - ambient_surf.get_width() // 2, int(msg['y'])))
            else:
                ambient_messages.remove(msg)
        
        # Weather indicator
        if weather_type != "clear":
            weather_font = pygame.font.Font(None, 30)
            weather_emoji = "🌧️" if weather_type == "rain" else "❄️"
            weather_surf = weather_font.render(f"{weather_emoji} {weather_type.title()}", True, (255, 255, 255))
            screen.blit(weather_surf, (WIDTH - 150, HEIGHT - 40))
        
        # Items collected counter
        counter_font = pygame.font.Font(None, 30)
        counter = counter_font.render(f"Items: {items_collected}", True, (255, 255, 255))
        screen.blit(counter, (20, HEIGHT - 40))
        
        # High combo indicator
        if highest_combo > 1:
            hc_font = pygame.font.Font(None, 26)
            hc_text = hc_font.render(f"Best Combo: x{highest_combo}", True, (255, 215, 0))
            screen.blit(hc_text, (WIDTH - 180, HEIGHT - 40))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        clock.tick(60)
    
    # Game Over screen (if lives ran out)
    if lives <= 0:
        screen.fill((0, 0, 0))
        game_over_font = pygame.font.Font(None, 100)
        go_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 100))
        
        stats_font = pygame.font.Font(None, 40)
        stats = [
            f"Progress: {int(transformation)}% Human",
            f"Items Collected: {items_collected}",
            f"Best Combo: x{highest_combo}",
            "",
            "Press ESC to return to menu"
        ]
        
        for i, stat in enumerate(stats):
            stat_surf = stats_font.render(stat, True, (255, 255, 255))
            screen.blit(stat_surf, (WIDTH // 2 - stat_surf.get_width() // 2, HEIGHT // 2 + i * 50))
        
        pygame.display.flip()
        
        # Wait for ESC
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False


def draw_character(screen, x, y, transformation, direction, walk_frame, moving):
    """Draw the dog/human character based on transformation progress"""
    
    # Walking animation offset
    walk_offset = int(math.sin(walk_frame) * 3) if moving else 0
    
    if transformation < 25:
        # Full dog
        dog_size = 60
        
        # Body
        body_color = (139, 69, 19)
        pygame.draw.ellipse(screen, body_color, 
                          (int(x), int(y + 30 + walk_offset), dog_size, dog_size - 30))
        
        # Head
        head_x = int(x + (dog_size - 25) if direction > 0 else x + 5)
        head_y = int(y + 15)
        pygame.draw.circle(screen, body_color, (head_x, head_y), 22)
        
        # Snout
        snout_x = head_x + (12 * direction)
        pygame.draw.circle(screen, (110, 60, 20), (snout_x, head_y + 8), 10)
        pygame.draw.circle(screen, (50, 30, 10), (snout_x + (3 * direction), head_y + 10), 4)
        
        # Ears - floppy
        ear1_x = head_x - 15
        ear2_x = head_x + 15
        pygame.draw.ellipse(screen, (101, 67, 33), 
                          (ear1_x - 8, head_y - 5, 12, 20))
        pygame.draw.ellipse(screen, (101, 67, 33), 
                          (ear2_x - 4, head_y - 5, 12, 20))
        
        # Eyes - cute dog eyes
        eye_offset = 7 * direction
        pygame.draw.circle(screen, (0, 0, 0), (head_x - 8 + eye_offset, head_y - 3), 4)
        pygame.draw.circle(screen, (255, 255, 255), (head_x - 6 + eye_offset, head_y - 5), 2)
        
        # Tail - wagging
        tail_wag = math.sin(walk_frame * 2) * 15
        tail_x = int(x - 5 if direction > 0 else x + dog_size - 5)
        tail_y = int(y + 45)
        pygame.draw.line(screen, body_color, 
                       (tail_x, tail_y), 
                       (tail_x - 15 * direction, int(tail_y - 20 + tail_wag)), 7)
        
        # Legs
        leg_spacing = 15
        for i in range(2):
            leg_x = x + 15 + i * leg_spacing
            leg_offset = walk_offset if i == 0 else -walk_offset
            pygame.draw.line(screen, body_color, 
                           (leg_x, y + 60), 
                           (leg_x, y + 75 + leg_offset), 6)
            pygame.draw.line(screen, body_color, 
                           (leg_x + 25, y + 60), 
                           (leg_x + 25, y + 75 - leg_offset), 6)
    
    elif transformation < 50:
        # Early hybrid - dog starting to stand
        # Body becoming more upright
        pygame.draw.ellipse(screen, (139, 69, 19), 
                          (int(x + 15), int(y + 20 + walk_offset), 35, 50))
        
        # Dog head
        head_x = int(x + 32)
        head_y = int(y + 10)
        pygame.draw.circle(screen, (139, 69, 19), (head_x, head_y), 20)
        
        # Ears getting smaller
        pygame.draw.polygon(screen, (101, 67, 33), [
            (head_x - 12, head_y - 15),
            (head_x - 18, head_y - 25),
            (head_x - 8, head_y - 10)
        ])
        pygame.draw.polygon(screen, (101, 67, 33), [
            (head_x + 12, head_y - 15),
            (head_x + 18, head_y - 25),
            (head_x + 8, head_y - 10)
        ])
        
        # Eyes
        pygame.draw.circle(screen, (0, 0, 0), (head_x - 8, head_y - 3), 4)
        pygame.draw.circle(screen, (0, 0, 0), (head_x + 8, head_y - 3), 4)
        
        # Small snout
        pygame.draw.circle(screen, (110, 60, 20), (head_x, head_y + 10), 8)
        
        # Arms starting to form
        arm_y_offset = walk_offset // 2
        pygame.draw.line(screen, (210, 180, 140), 
                       (x + 15, y + 30), (x + 5, y + 50 + arm_y_offset), 6)
        pygame.draw.line(screen, (210, 180, 140), 
                       (x + 50, y + 30), (x + 60, y + 50 - arm_y_offset), 6)
        
        # Legs
        pygame.draw.line(screen, (139, 69, 19), 
                       (x + 25, y + 70), (x + 25, y + 85 + walk_offset), 7)
        pygame.draw.line(screen, (139, 69, 19), 
                       (x + 40, y + 70), (x + 40, y + 85 - walk_offset), 7)
    
    elif transformation < 75:
        # Mid hybrid - clearly humanoid with dog features
        # Human-like body
        pygame.draw.rect(screen, (210, 180, 140), 
                       (int(x + 18), int(y + 25), 28, 45))
        
        # Head - less dog-like
        head_x = int(x + 32)
        head_y = int(y + 8)
        pygame.draw.circle(screen, (220, 190, 160), (head_x, head_y), 18)
        
        # Small dog ears
        pygame.draw.circle(screen, (101, 67, 33), (head_x - 15, head_y - 8), 6)
        pygame.draw.circle(screen, (101, 67, 33), (head_x + 15, head_y - 8), 6)
        
        # More human eyes
        pygame.draw.circle(screen, (255, 255, 255), (head_x - 7, head_y - 2), 5)
        pygame.draw.circle(screen, (255, 255, 255), (head_x + 7, head_y - 2), 5)
        pygame.draw.circle(screen, (0, 0, 0), (head_x - 7, head_y - 2), 3)
        pygame.draw.circle(screen, (0, 0, 0), (head_x + 7, head_y - 2), 3)
        
        # Small nose
        pygame.draw.circle(screen, (180, 140, 120), (head_x, head_y + 5), 4)
        
        # Arms
        arm_offset = walk_offset
        pygame.draw.rect(screen, (210, 180, 140), 
                       (int(x + 8), int(y + 30 + arm_offset), 8, 30))
        pygame.draw.rect(screen, (210, 180, 140), 
                       (int(x + 48), int(y + 30 - arm_offset), 8, 30))
        
        # Legs
        pygame.draw.rect(screen, (50, 50, 150), 
                       (int(x + 22), int(y + 70 + walk_offset), 8, 25))
        pygame.draw.rect(screen, (50, 50, 150), 
                       (int(x + 34), int(y + 70 - walk_offset), 8, 25))
    
    else:
        # Almost/fully human
        # Body with shirt
        shirt_color = (100, 100, 255) if transformation < 100 else (50, 150, 50)
        pygame.draw.rect(screen, shirt_color, 
                       (int(x + 18), int(y + 25), 28, 40))
        
        # Head - human
        head_x = int(x + 32)
        head_y = int(y + 8)
        pygame.draw.circle(screen, (255, 220, 177), (head_x, head_y), 16)
        
        # Hair
        hair_color = (101, 67, 33)
        pygame.draw.arc(screen, hair_color, 
                      (head_x - 16, head_y - 16, 32, 25), 
                      0, 3.14, 4)
        
        # Human eyes
        pygame.draw.circle(screen, (255, 255, 255), (head_x - 6, head_y - 2), 4)
        pygame.draw.circle(screen, (255, 255, 255), (head_x + 6, head_y - 2), 4)
        pygame.draw.circle(screen, (0, 100, 200), (head_x - 6, head_y - 2), 2)
        pygame.draw.circle(screen, (0, 100, 200), (head_x + 6, head_y - 2), 2)
        
        # Smile
        pygame.draw.arc(screen, (200, 100, 100), 
                      (head_x - 8, head_y + 2, 16, 12), 
                      0, 3.14, 2)
        
        # Arms with skin tone
        arm_offset = walk_offset
        pygame.draw.rect(screen, (255, 220, 177), 
                       (int(x + 10), int(y + 28 + arm_offset), 7, 28))
        pygame.draw.rect(screen, (255, 220, 177), 
                       (int(x + 47), int(y + 28 - arm_offset), 7, 28))
        
        # Pants
        pygame.draw.rect(screen, (50, 50, 50), 
                       (int(x + 22), int(y + 65 + walk_offset), 9, 28))
        pygame.draw.rect(screen, (50, 50, 50), 
                       (int(x + 33), int(y + 65 - walk_offset), 9, 28))
        
        # Shoes
        pygame.draw.ellipse(screen, (80, 40, 20), 
                          (int(x + 20), int(y + 90 + walk_offset), 12, 8))
        pygame.draw.ellipse(screen, (80, 40, 20), 
                          (int(x + 31), int(y + 90 - walk_offset), 12, 8))
        
        # If fully transformed, add sparkle effect
        if transformation >= 100:
            for i in range(6):
                angle = (walk_frame * 0.5 + i * 1.047) % 6.28
                sparkle_x = x + 32 + math.cos(angle) * 45
                sparkle_y = y + 40 + math.sin(angle) * 45
                size = 3 + int(abs(math.sin(walk_frame * 0.3 + i)) * 4)
                pygame.draw.circle(screen, (255, 255, 0), (int(sparkle_x), int(sparkle_y)), size)

def wolf_eat_animation():
    """Animation of wolf eating all the menu buttons"""
    # Wolf enters from the right side of screen
    wolf_x = WIDTH + 200
    wolf_y = HEIGHT // 2 - 60
    target_x = WIDTH // 2 - 100
    
    # Button positions (simulate menu buttons)
    buttons = []
    for i in range(9):  # 9 game mode buttons
        buttons.append({
            'x': WIDTH // 2,
            'y': 200 + i * 40,
            'eaten': False,
            'fly_x': WIDTH // 2,
            'fly_y': 200 + i * 40,
            'name': ['Battle', 'Coins', 'Makka', 'Mom', 'Flag', 'Survival', '3D', 'Relax', 'Dilly'][i]
        })
    
    for frame in range(180):
        screen.fill((30, 30, 30))
        
        # Animate wolf moving in (first 40 frames)
        if frame < 40:
            wolf_x += (target_x - wolf_x) * 0.15
        
        # Draw wolf body (larger, more detailed)
        wolf_size = 120
        # Body
        pygame.draw.ellipse(screen, (100, 100, 100), 
                          (int(wolf_x), int(wolf_y), wolf_size, wolf_size - 20))
        # Head
        head_x = int(wolf_x + wolf_size - 40)
        head_y = int(wolf_y - 20)
        pygame.draw.circle(screen, (120, 120, 120), (head_x, head_y), 50)
        
        # Ears
        pygame.draw.polygon(screen, (100, 100, 100), [
            (head_x - 30, head_y - 40),
            (head_x - 40, head_y - 70),
            (head_x - 20, head_y - 50)
        ])
        pygame.draw.polygon(screen, (100, 100, 100), [
            (head_x + 30, head_y - 40),
            (head_x + 40, head_y - 70),
            (head_x + 20, head_y - 50)
        ])
        
        # Eyes (getting hungrier)
        eye_color = (255, 0, 0) if frame > 40 else (255, 255, 0)
        pygame.draw.circle(screen, eye_color, (head_x - 15, head_y - 10), 8)
        pygame.draw.circle(screen, eye_color, (head_x + 15, head_y - 10), 8)
        pygame.draw.circle(screen, (0, 0, 0), (head_x - 15, head_y - 10), 4)
        pygame.draw.circle(screen, (0, 0, 0), (head_x + 15, head_y - 10), 4)
        
        # Mouth (opens wider as it eats)
        mouth_open = min(40, frame - 40) if frame > 40 else 0
        # Upper jaw
        pygame.draw.arc(screen, (255, 255, 255), 
                       (head_x - 25, head_y + 5, 50, 30 + mouth_open), 
                       0, 3.14, 3)
        # Lower jaw
        pygame.draw.arc(screen, (255, 255, 255), 
                       (head_x - 25, head_y + 15 - mouth_open//2, 50, 30 + mouth_open), 
                       3.14, 6.28, 3)
        
        # Teeth
        if mouth_open > 10:
            for i in range(8):
                tooth_x = head_x - 20 + i * 6
                pygame.draw.line(screen, (255, 255, 255), 
                               (tooth_x, head_y + 15), 
                               (tooth_x, head_y + 20), 2)
        
        # Tail wagging
        tail_wag = math.sin(frame * 0.3) * 20
        tail_x = int(wolf_x - 10)
        tail_y = int(wolf_y + 40 + tail_wag)
        pygame.draw.line(screen, (100, 100, 100), 
                        (int(wolf_x), int(wolf_y + 50)), 
                        (tail_x, tail_y), 8)
        
        # Animate buttons flying into wolf's mouth (frames 40-140)
        if frame >= 40:
            button_index = min(8, (frame - 40) // 11)  # Eat one button every 11 frames
            
            for i, btn in enumerate(buttons):
                if i <= button_index and not btn['eaten']:
                    # Fly toward wolf's mouth
                    btn['fly_x'] += (head_x - btn['fly_x']) * 0.2
                    btn['fly_y'] += (head_y + 10 - btn['fly_y']) * 0.2
                    
                    # Check if eaten
                    if abs(btn['fly_x'] - head_x) < 20 and abs(btn['fly_y'] - (head_y + 10)) < 20:
                        btn['eaten'] = True
                
                # Draw button if not eaten yet
                if not btn['eaten']:
                    btn_font = pygame.font.Font(None, 30)
                    btn_text = btn_font.render(btn['name'], True, (255, 200, 0))
                    screen.blit(btn_text, (int(btn['fly_x']) - btn_text.get_width()//2, 
                                          int(btn['fly_y']) - btn_text.get_height()//2))
        
        # Message appears after eating
        if frame > 140:
            msg_font = pygame.font.Font(None, 70)
            msg = msg_font.render("The wolf ate everything!", True, (255, 0, 0))
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT - 100))
        
        pygame.display.flip()
        pygame.time.wait(16)  # ~60 FPS
    
    # Stop the Gangnam Style music after wolf eats everything
    pygame.mixer.music.stop()
    secret_hack['music_still_playing'] = False
    
    pygame.time.wait(1000)

def wolf_vomit_animation(mode_name):
    """Animation of wolf vomiting up a new game mode button"""
    # Wolf is in center, looking sick
    wolf_x = WIDTH // 2 - 100
    wolf_y = HEIGHT // 2 - 60
    
    for frame in range(120):
        screen.fill((30, 30, 30))
        
        # Draw wolf body (shaking)
        shake_x = random.randint(-3, 3) if frame < 60 else 0
        shake_y = random.randint(-3, 3) if frame < 60 else 0
        
        wolf_size = 120
        # Body
        pygame.draw.ellipse(screen, (100, 100, 100), 
                          (int(wolf_x + shake_x), int(wolf_y + shake_y), wolf_size, wolf_size - 20))
        # Head
        head_x = int(wolf_x + wolf_size - 40 + shake_x)
        head_y = int(wolf_y - 20 + shake_y)
        pygame.draw.circle(screen, (120, 120, 120), (head_x, head_y), 50)
        
        # Ears
        pygame.draw.polygon(screen, (100, 100, 100), [
            (head_x - 30, head_y - 40),
            (head_x - 40, head_y - 70),
            (head_x - 20, head_y - 50)
        ])
        pygame.draw.polygon(screen, (100, 100, 100), [
            (head_x + 30, head_y - 40),
            (head_x + 40, head_y - 70),
            (head_x + 20, head_y - 50)
        ])
        
        # Sick eyes (X_X)
        if frame < 60:
            # Dizzy spirals
            pygame.draw.circle(screen, (255, 255, 0), (head_x - 15, head_y - 10), 8, 2)
            pygame.draw.circle(screen, (255, 255, 0), (head_x + 15, head_y - 10), 8, 2)
        else:
            # X eyes
            pygame.draw.line(screen, (0, 0, 0), (head_x - 20, head_y - 15), (head_x - 10, head_y - 5), 3)
            pygame.draw.line(screen, (0, 0, 0), (head_x - 10, head_y - 15), (head_x - 20, head_y - 5), 3)
            pygame.draw.line(screen, (0, 0, 0), (head_x + 10, head_y - 15), (head_x + 20, head_y - 5), 3)
            pygame.draw.line(screen, (0, 0, 0), (head_x + 20, head_y - 15), (head_x + 10, head_y - 5), 3)
        
        # Mouth (sick, queasy)
        mouth_color = (100, 255, 100) if frame < 60 else (200, 200, 200)
        pygame.draw.arc(screen, mouth_color, 
                       (head_x - 20, head_y + 10, 40, 25), 
                       3.14, 6.28, 3)
        
        # Vomit animation (frames 30-90)
        if 30 < frame < 90:
            vomit_progress = (frame - 30) / 60.0
            # Green vomit stream
            vomit_y = head_y + 30 + vomit_progress * 150
            pygame.draw.line(screen, (100, 255, 100), 
                           (head_x, head_y + 30), 
                           (head_x, int(vomit_y)), 10)
            
            # Particles
            for i in range(10):
                particle_y = head_y + 30 + random.randint(0, int(vomit_progress * 150))
                particle_x = head_x + random.randint(-15, 15)
                pygame.draw.circle(screen, (100, 255, 100), (particle_x, int(particle_y)), 3)
        
        # New mode button appears (frames 60-120)
        if frame > 60:
            button_y = head_y + 30 + min(200, (frame - 60) * 4)
            button_alpha = min(255, (frame - 60) * 4)
            
            # Draw the new mode button
            mode_font = pygame.font.Font(None, 60)
            mode_text = mode_font.render(mode_name, True, (0, 255, 0))
            screen.blit(mode_text, (WIDTH // 2 - mode_text.get_width() // 2, int(button_y)))
            
            # Sparkles around it
            for i in range(8):
                angle = (frame * 0.1 + i * 0.785) % 6.28
                sparkle_x = WIDTH // 2 + math.cos(angle) * 80
                sparkle_y = button_y + 20 + math.sin(angle) * 40
                pygame.draw.circle(screen, (255, 255, 0), (int(sparkle_x), int(sparkle_y)), 3)
        
        # Message
        if frame > 90:
            msg_font = pygame.font.Font(None, 50)
            msg = msg_font.render(f"{mode_name} unlocked!", True, (0, 255, 0))
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT - 80))
        
        pygame.display.flip()
        pygame.time.wait(16)
    
    pygame.time.wait(1500)

# Mode selection lobby with Exit button

def draw_menu_pointer(screen, x, y, transformation, direction, walk_frame, moving):
    """Draw a HYPER-REALISTIC dog/human character as menu pointer"""
    
    # Scale for menu (make dog BIGGER and more visible)
    scale = 0.7  # Increased from 0.5 for better visibility
    walk_offset = int(math.sin(walk_frame) * 4) if moving else 0
    breath_offset = int(math.sin(walk_frame * 0.5) * 3)  # Breathing animation
    
    if transformation < 50:
        # ULTRA REALISTIC DOG - Golden Retriever/Labrador style!
        dog_size = int(90 * scale)
        
        # SHADOW (subtle ground shadow for realism)
        shadow_y = int(y + 95 * scale)
        pygame.draw.ellipse(screen, (20, 20, 20, 100), 
                          (int(x - 5 * scale), shadow_y, int(65 * scale), int(12 * scale)))
        
        # Back leg (behind body) - more muscular
        back_leg_x = int(x + 12 * scale)
        back_leg_top = int(y + 50 * scale)
        back_leg_bottom = int(y + 85 * scale - walk_offset)
        # Upper leg (thigh) - thicker
        pygame.draw.line(screen, (100, 50, 15), 
                       (back_leg_x, back_leg_top), 
                       (back_leg_x, back_leg_top + int(20 * scale)), int(12 * scale))
        # Lower leg - slightly thinner
        pygame.draw.line(screen, (120, 65, 25), 
                       (back_leg_x, back_leg_top + int(20 * scale)), 
                       (back_leg_x, back_leg_bottom), int(9 * scale))
        # Paw with detail
        pygame.draw.circle(screen, (80, 50, 30), 
                         (back_leg_x, back_leg_bottom), int(7 * scale))
        # Toe pads
        for toe in range(3):
            pygame.draw.circle(screen, (60, 40, 25), 
                             (back_leg_x - 3 + toe * 3, back_leg_bottom + 3), int(2 * scale))
        
        # Body - ULTRA realistic shape with multiple layers for depth
        body_y = int(y + 35 * scale + breath_offset)
        body_width = int(60 * scale)
        body_height = int(40 * scale)
        
        # Body deep shadow (3D effect)
        pygame.draw.ellipse(screen, (80, 40, 10), 
                          (int(x + 5 * scale), body_y + int(8 * scale), body_width, body_height))
        # Body mid-shadow
        pygame.draw.ellipse(screen, (110, 60, 20), 
                          (int(x + 5 * scale), body_y + int(5 * scale), body_width, body_height))
        # Main body - rich golden brown
        pygame.draw.ellipse(screen, (165, 115, 55), 
                          (int(x + 5 * scale), body_y, body_width, body_height))
        # Body highlight (sunlight reflection on fur)
        pygame.draw.ellipse(screen, (200, 145, 85), 
                          (int(x + 10 * scale), body_y + int(3 * scale), 
                           int(45 * scale), int(25 * scale)))
        # Top highlight (spine area - lighter fur)
        pygame.draw.ellipse(screen, (220, 170, 110), 
                          (int(x + 15 * scale), body_y + int(5 * scale), 
                           int(35 * scale), int(15 * scale)))
        
        # Chest fur (lighter, fluffy area)
        pygame.draw.ellipse(screen, (200, 160, 100), 
                          (int(x + 35 * scale), body_y + int(20 * scale), 
                           int(25 * scale), int(18 * scale)))
        # Chest highlight
        pygame.draw.ellipse(screen, (230, 190, 130), 
                          (int(x + 38 * scale), body_y + int(22 * scale), 
                           int(18 * scale), int(12 * scale)))
        
        # Fur texture lines (give realistic fur appearance)
        fur_color = (140, 95, 50)
        for fur_line in range(8):
            fx = int(x + 12 * scale + fur_line * 6 * scale)
            fy = body_y + int(10 * scale)
            pygame.draw.line(screen, fur_color, 
                           (fx, fy), (fx + int(2 * scale), fy + int(8 * scale)), 1)
        
        # Tail - ULTRA realistic wagging tail with volume and motion
        tail_base_x = int(x + 5 * scale)
        tail_base_y = int(y + 40 * scale)
        tail_wag = math.sin(walk_frame * 2.5) * 25 * scale
        
        # Tail has multiple segments for realistic curve and volume
        tail_segments = [
            (tail_base_x, tail_base_y),
            (tail_base_x - int(12 * scale), tail_base_y - int(8 * scale) + tail_wag * 0.3),
            (tail_base_x - int(22 * scale), tail_base_y - int(18 * scale) + tail_wag * 0.6),
            (tail_base_x - int(28 * scale), tail_base_y - int(30 * scale) + tail_wag),
            (tail_base_x - int(25 * scale), tail_base_y - int(40 * scale) + tail_wag * 1.1)
        ]
        
        # Draw tail with thickness variation (thicker at base, thinner at tip)
        for i in range(len(tail_segments) - 1):
            thickness = int((10 - i * 2) * scale)
            # Shadow layer
            pygame.draw.line(screen, (90, 50, 15), 
                           (tail_segments[i][0] + 2, tail_segments[i][1] + 2),
                           (tail_segments[i+1][0] + 2, tail_segments[i+1][1] + 2), 
                           max(1, thickness + 2))
            # Dark base layer
            pygame.draw.line(screen, (120, 70, 30), 
                           tail_segments[i], tail_segments[i+1], max(1, thickness))
            # Highlight layer
            pygame.draw.line(screen, (180, 130, 70), 
                           tail_segments[i], tail_segments[i+1], max(1, thickness - 2))
        
        # Tail tip (fluffy and light)
        tip_pos = tail_segments[-1]
        pygame.draw.circle(screen, (140, 95, 50), tip_pos, int(6 * scale))
        pygame.draw.circle(screen, (210, 170, 110), tip_pos, int(4 * scale))
        
        # Head - HYPER realistic with proper skull structure
        head_x = int(x + 58 * scale)
        head_y = int(y + 22 * scale + breath_offset)
        head_radius = int(24 * scale)
        
        # Head shadow (for depth)
        pygame.draw.circle(screen, (90, 50, 15), 
                         (head_x + int(3 * scale), head_y + int(3 * scale)), head_radius)
        # Head base (darker)
        pygame.draw.circle(screen, (140, 90, 45), (head_x, head_y), head_radius)
        # Head mid-tone
        pygame.draw.circle(screen, (165, 115, 55), (head_x, head_y), int(head_radius * 0.9))
        # Head highlight (light hitting the forehead)
        pygame.draw.circle(screen, (200, 145, 85), 
                         (head_x - int(6 * scale), head_y - int(6 * scale)), int(15 * scale))
        # Top of head (even lighter)
        pygame.draw.circle(screen, (220, 170, 110), 
                         (head_x - int(4 * scale), head_y - int(8 * scale)), int(10 * scale))
        
        # Fur detail on head
        for fur_i in range(6):
            angle = fur_i * 0.5
            fur_x = head_x + int(math.cos(angle) * 15 * scale)
            fur_y = head_y - int(10 * scale) + int(math.sin(angle) * 8 * scale)
            pygame.draw.line(screen, (140, 95, 50), 
                           (fur_x, fur_y), 
                           (fur_x + int(math.cos(angle) * 4 * scale), 
                            fur_y + int(math.sin(angle) * 4 * scale)), 2)
        
        # Snout - ULTRA realistic 3D muzzle
        snout_x = head_x + int(22 * scale)
        snout_y = head_y + int(10 * scale)
        
        # Snout base (darkest - underneath)
        pygame.draw.ellipse(screen, (100, 65, 30), 
                          (snout_x - int(16 * scale), snout_y - int(10 * scale), 
                           int(32 * scale), int(20 * scale)))
        # Snout mid (bridge)
        pygame.draw.ellipse(screen, (140, 95, 45), 
                          (snout_x - int(14 * scale), snout_y - int(12 * scale), 
                           int(28 * scale), int(18 * scale)))
        # Snout top (lightest - top of muzzle)
        pygame.draw.ellipse(screen, (180, 135, 75), 
                          (snout_x - int(12 * scale), snout_y - int(14 * scale), 
                           int(24 * scale), int(16 * scale)))
        
        # Snout sides (give volume)
        pygame.draw.ellipse(screen, (160, 115, 60), 
                          (snout_x - int(10 * scale), snout_y - int(8 * scale), 
                           int(12 * scale), int(14 * scale)))
        pygame.draw.ellipse(screen, (160, 115, 60), 
                          (snout_x + int(2 * scale), snout_y - int(8 * scale), 
                           int(12 * scale), int(14 * scale)))
        
        # Nose - SUPER realistic wet dog nose
        nose_x = snout_x + int(10 * scale)
        nose_y = snout_y
        # Nose base (large)
        pygame.draw.circle(screen, (50, 30, 20), (nose_x, nose_y), int(7 * scale))
        # Nose dark center
        pygame.draw.circle(screen, (25, 15, 10), (nose_x, nose_y), int(6 * scale))
        # Nose SHINE (wet glossy look - KEY for realism!)
        pygame.draw.circle(screen, (120, 100, 90), 
                         (nose_x - int(2 * scale), nose_y - int(2 * scale)), int(3 * scale))
        pygame.draw.circle(screen, (200, 180, 170), 
                         (nose_x - int(3 * scale), nose_y - int(3 * scale)), int(1 * scale))
        
        # Nostrils (detailed)
        pygame.draw.circle(screen, (10, 5, 0), 
                         (nose_x - int(3 * scale), nose_y + int(2 * scale)), int(2 * scale))
        pygame.draw.circle(screen, (10, 5, 0), 
                         (nose_x + int(3 * scale), nose_y + int(2 * scale)), int(2 * scale))
        
        # Nose bridge line
        pygame.draw.line(screen, (70, 50, 30), 
                       (nose_x, nose_y - int(5 * scale)), 
                       (nose_x, nose_y + int(2 * scale)), 2)
        
        # Mouth and lips
        pygame.draw.line(screen, (60, 40, 20), 
                       (nose_x, nose_y + int(4 * scale)), 
                       (nose_x - int(4 * scale), nose_y + int(10 * scale)), int(3 * scale))
        pygame.draw.line(screen, (60, 40, 20), 
                       (nose_x, nose_y + int(4 * scale)), 
                       (nose_x + int(2 * scale), nose_y + int(10 * scale)), int(3 * scale))
        # Mouth corner (slight smile)
        pygame.draw.arc(screen, (60, 40, 20), 
                       (nose_x - int(8 * scale), nose_y + int(5 * scale), 
                        int(16 * scale), int(10 * scale)), 0, 3.14, 2)
        
        # Ears - ULTRA realistic floppy ears with incredible detail
        # Left ear (viewer's left, dog's right)
        ear_left_points = [
            (head_x - int(18 * scale), head_y - int(15 * scale)),
            (head_x - int(28 * scale), head_y - int(10 * scale)),
            (head_x - int(26 * scale), head_y + int(12 * scale)),
            (head_x - int(14 * scale), head_y + int(8 * scale))
        ]
        # Right ear (viewer's right, dog's left)
        ear_right_points = [
            (head_x + int(10 * scale), head_y - int(18 * scale)),
            (head_x + int(20 * scale), head_y - int(15 * scale)),
            (head_x + int(22 * scale), head_y + int(8 * scale)),
            (head_x + int(12 * scale), head_y + int(10 * scale))
        ]
        
        # Ear shadows (depth)
        for ear_points in [ear_left_points, ear_right_points]:
            shadow_points = [(p[0] + 3, p[1] + 3) for p in ear_points]
            pygame.draw.polygon(screen, (80, 45, 15), shadow_points)
        
        # Ear base (darkest)
        pygame.draw.polygon(screen, (110, 65, 28), ear_left_points)
        pygame.draw.polygon(screen, (110, 65, 28), ear_right_points)
        
        # Ear mid-tone
        ear_left_inner = [
            ear_left_points[0],
            ((ear_left_points[0][0] + ear_left_points[1][0])//2, 
             (ear_left_points[0][1] + ear_left_points[1][1])//2),
            ((ear_left_points[1][0] + ear_left_points[2][0])//2, 
             (ear_left_points[1][1] + ear_left_points[2][1])//2),
            ((ear_left_points[2][0] + ear_left_points[3][0])//2, 
             (ear_left_points[2][1] + ear_left_points[3][1])//2)
        ]
        pygame.draw.polygon(screen, (140, 90, 45), ear_left_inner)
        
        # Ear inner (pink/flesh colored - very realistic)
        ear_pink_left = [
            ear_left_points[0],
            ear_left_points[1],
            ((ear_left_points[1][0] + ear_left_points[2][0])//2, 
             (ear_left_points[1][1] + ear_left_points[2][1])//2)
        ]
        pygame.draw.polygon(screen, (220, 170, 160), ear_pink_left)
        
        # Ear fur detail (fine lines for texture)
        for i in range(4):
            offset = i * 6 * scale
            pygame.draw.line(screen, (130, 85, 40), 
                           (ear_left_points[1][0] + int(offset), ear_left_points[1][1]),
                           (ear_left_points[2][0] + int(offset * 0.5), ear_left_points[2][1]), 1)
        
        # Eyes - INCREDIBLY realistic with soul!
        eye_left_x = head_x - int(8 * scale)
        eye_right_x = head_x + int(4 * scale)
        eye_y = head_y - int(6 * scale)
        eye_width = int(12 * scale)
        eye_height = int(10 * scale)
        
        # Eye sockets (subtle shadow for depth)
        pygame.draw.ellipse(screen, (120, 75, 40), 
                          (eye_left_x - int(7 * scale), eye_y - int(6 * scale), 
                           int(14 * scale), int(12 * scale)))
        pygame.draw.ellipse(screen, (120, 75, 40), 
                          (eye_right_x - int(7 * scale), eye_y - int(6 * scale), 
                           int(14 * scale), int(12 * scale)))
        
        # Eye whites (slightly off-white for realism)
        pygame.draw.ellipse(screen, (245, 240, 235), 
                          (eye_left_x - int(6 * scale), eye_y - int(5 * scale), 
                           eye_width, eye_height))
        pygame.draw.ellipse(screen, (245, 240, 235), 
                          (eye_right_x - int(6 * scale), eye_y - int(5 * scale), 
                           eye_width, eye_height))
        
        # Iris (beautiful rich brown with texture)
        iris_radius = int(5 * scale)
        # Outer iris (darker)
        pygame.draw.circle(screen, (70, 45, 20), (eye_left_x, eye_y), iris_radius)
        pygame.draw.circle(screen, (70, 45, 20), (eye_right_x, eye_y), iris_radius)
        # Inner iris (lighter, warmer)
        pygame.draw.circle(screen, (95, 65, 30), (eye_left_x, eye_y), int(iris_radius * 0.8))
        pygame.draw.circle(screen, (95, 65, 30), (eye_right_x, eye_y), int(iris_radius * 0.8))
        
        # Iris detail (radiating lines for texture)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            start_x = eye_left_x + int(math.cos(rad) * 2 * scale)
            start_y = eye_y + int(math.sin(rad) * 2 * scale)
            end_x = eye_left_x + int(math.cos(rad) * 4 * scale)
            end_y = eye_y + int(math.sin(rad) * 4 * scale)
            pygame.draw.line(screen, (80, 55, 25), (start_x, start_y), (end_x, end_y), 1)
        
        # Pupils (deep black)
        pupil_radius = int(3 * scale)
        pygame.draw.circle(screen, (0, 0, 0), (eye_left_x, eye_y), pupil_radius)
        pygame.draw.circle(screen, (0, 0, 0), (eye_right_x, eye_y), pupil_radius)
        
        # Eye shine (CRITICAL for lifelike eyes - multiple highlights)
        # Main highlight (top-left)
        pygame.draw.circle(screen, (255, 255, 255), 
                         (eye_left_x - int(2 * scale), eye_y - int(2 * scale)), int(2 * scale))
        pygame.draw.circle(screen, (255, 255, 255), 
                         (eye_right_x - int(2 * scale), eye_y - int(2 * scale)), int(2 * scale))
        # Secondary highlight (smaller)
        pygame.draw.circle(screen, (200, 200, 200), 
                         (eye_left_x + int(1 * scale), eye_y + int(2 * scale)), int(1 * scale))
        pygame.draw.circle(screen, (200, 200, 200), 
                         (eye_right_x + int(1 * scale), eye_y + int(2 * scale)), int(1 * scale))
        
        # Eyelids (add realism)
        pygame.draw.arc(screen, (100, 60, 30), 
                       (eye_left_x - int(7 * scale), eye_y - int(6 * scale), 
                        int(14 * scale), int(12 * scale)), 0, 3.14, 2)
        pygame.draw.arc(screen, (100, 60, 30), 
                       (eye_right_x - int(7 * scale), eye_y - int(6 * scale), 
                        int(14 * scale), int(12 * scale)), 0, 3.14, 2)
        
        # Eyebrows (expression - happy/friendly)
        pygame.draw.arc(screen, (110, 70, 35), 
                       (eye_left_x - int(8 * scale), eye_y - int(10 * scale), 
                        int(16 * scale), int(10 * scale)), 0, 3.14, int(3 * scale))
        pygame.draw.arc(screen, (110, 70, 35), 
                       (eye_right_x - int(8 * scale), eye_y - int(10 * scale), 
                        int(16 * scale), int(10 * scale)), 0, 3.14, int(3 * scale)) 
        
        # Front legs - ULTRA realistic with joints and muscles!
        
        # Front legs - ULTRA realistic with joints and muscles!
        leg_positions = [
            (int(x + 28 * scale), int(y + 62 * scale)),
            (int(x + 43 * scale), int(y + 62 * scale))
        ]
        
        for i, (leg_x, leg_top_y) in enumerate(leg_positions):
            leg_offset = walk_offset if i == 0 else -walk_offset
            leg_mid_y = int(y + 72 * scale)
            leg_bottom_y = int(y + 90 * scale + leg_offset)
            
            # Upper leg (shoulder/thigh - muscular)
            # Shadow
            pygame.draw.line(screen, (90, 50, 15), 
                           (leg_x + 2, leg_top_y + 2), 
                           (leg_x + 2, leg_mid_y + leg_offset//2), int(14 * scale))
            # Muscle (thick)
            pygame.draw.line(screen, (140, 90, 45), 
                           (leg_x, leg_top_y), 
                           (leg_x, leg_mid_y + leg_offset//2), int(12 * scale))
            # Highlight
            pygame.draw.line(screen, (180, 130, 70), 
                           (leg_x - 1, leg_top_y), 
                           (leg_x - 1, leg_mid_y + leg_offset//2), int(6 * scale))
            
            # Lower leg (thinner, more defined)
            # Shadow
            pygame.draw.line(screen, (100, 55, 20), 
                           (leg_x + 2, leg_mid_y + leg_offset//2), 
                           (leg_x + 2, leg_bottom_y), int(10 * scale))
            # Main
            pygame.draw.line(screen, (165, 115, 55), 
                           (leg_x, leg_mid_y + leg_offset//2), 
                           (leg_x, leg_bottom_y), int(8 * scale))
            # Highlight (catches light)
            pygame.draw.line(screen, (200, 145, 85), 
                           (leg_x - 1, leg_mid_y + leg_offset//2), 
                           (leg_x - 1, leg_bottom_y), int(4 * scale))
            
            # Knee/Elbow joint (small circle for anatomical detail)
            pygame.draw.circle(screen, (130, 85, 42), 
                             (leg_x, leg_mid_y + leg_offset//2), int(6 * scale))
            
            # Paw - HIGHLY detailed with toe beans!
            paw_y = leg_bottom_y
            paw_x = leg_x
            
            # Paw base (shadow)
            pygame.draw.ellipse(screen, (80, 50, 25), 
                              (paw_x - int(9 * scale), paw_y - int(4 * scale), 
                               int(18 * scale), int(12 * scale)))
            # Paw main
            pygame.draw.ellipse(screen, (120, 80, 40), 
                              (paw_x - int(8 * scale), paw_y - int(3 * scale), 
                               int(16 * scale), int(10 * scale)))
            
            # Toe beans (paw pads) - CRITICAL detail!
            # Main pad (center, larger)
            pygame.draw.ellipse(screen, (80, 60, 50), 
                              (paw_x - int(4 * scale), paw_y + int(1 * scale), 
                               int(8 * scale), int(6 * scale)))
            
            # Toe pads (4 small ones)
            toe_positions = [
                (paw_x - 5, paw_y - 2),
                (paw_x - 2, paw_y - 3),
                (paw_x + 2, paw_y - 3),
                (paw_x + 5, paw_y - 2)
            ]
            for toe_x, toe_y in toe_positions:
                # Toe shadow
                pygame.draw.circle(screen, (60, 45, 35), 
                                 (int(toe_x + 1), int(toe_y + 1)), int(2 * scale))
                # Toe pad
                pygame.draw.circle(screen, (90, 70, 60), 
                                 (int(toe_x), int(toe_y)), int(2 * scale))
                # Toe highlight
                pygame.draw.circle(screen, (110, 90, 80), 
                                 (int(toe_x - 0.5), int(toe_y - 0.5)), int(1 * scale))
            
            # Claws (small but visible)
            for claw_i in range(4):
                claw_x = paw_x - 5 + claw_i * 3
                pygame.draw.line(screen, (240, 240, 230), 
                               (claw_x, paw_y - 3), 
                               (claw_x, paw_y - 6), 1)
        
        # Collar - PREMIUM leather collar with realistic details
        collar_y = int(y + 38 * scale + breath_offset)
        collar_width = int(30 * scale)
        collar_height = int(6 * scale)
        collar_x = int(x + 38 * scale)
        
        # Collar shadow
        pygame.draw.rect(screen, (120, 30, 30), 
                       (collar_x + 2, collar_y + 2, collar_width, collar_height), 
                       border_radius=int(3 * scale))
        # Collar base (dark leather)
        pygame.draw.rect(screen, (180, 50, 50), 
                       (collar_x, collar_y, collar_width, collar_height), 
                       border_radius=int(3 * scale))
        # Collar highlight (light reflection)
        pygame.draw.rect(screen, (220, 80, 80), 
                       (collar_x, collar_y, collar_width, int(2 * scale)), 
                       border_radius=int(3 * scale))
        
        # Collar stitching (tiny detail for realism)
        for stitch_x in range(0, int(collar_width), int(4 * scale)):
            pygame.draw.circle(screen, (150, 40, 40), 
                             (collar_x + stitch_x, collar_y + int(3 * scale)), 1)
        
        # Buckle (metallic silver)
        buckle_x = collar_x + int(5 * scale)
        buckle_y = collar_y + int(1 * scale)
        # Buckle base
        pygame.draw.rect(screen, (160, 160, 160), 
                       (buckle_x, buckle_y, int(6 * scale), int(4 * scale)))
        # Buckle highlight (shiny metal)
        pygame.draw.rect(screen, (220, 220, 220), 
                       (buckle_x, buckle_y, int(6 * scale), int(1 * scale)))
        # Buckle pin
        pygame.draw.circle(screen, (140, 140, 140), 
                         (buckle_x + int(3 * scale), buckle_y + int(2 * scale)), 
                         int(1 * scale))
        
        # Name tag (gold/brass, heart-shaped!)
        tag_x = collar_x + int(16 * scale)
        tag_y = collar_y + int(8 * scale)
        # Tag shadow
        tag_points_shadow = [
            (tag_x + 1, tag_y + 1),
            (tag_x - 4 + 1, tag_y + 4 + 1),
            (tag_x + 1, tag_y + 9 + 1),
            (tag_x + 6 + 1, tag_y + 4 + 1)
        ]
        pygame.draw.polygon(screen, (140, 120, 40), tag_points_shadow)
        
        # Tag base
        tag_points = [
            (tag_x, tag_y),
            (tag_x - 4, tag_y + 4),
            (tag_x, tag_y + 9),
            (tag_x + 6, tag_y + 4)
        ]
        pygame.draw.polygon(screen, (220, 190, 80), tag_points)
        
        # Tag highlight (shiny gold)
        tag_highlight = [
            (tag_x, tag_y + 1),
            (tag_x - 2, tag_y + 3),
            (tag_x, tag_y + 5)
        ]
        pygame.draw.polygon(screen, (255, 230, 120), tag_highlight)
        
        # Ring connecting tag to collar
        pygame.draw.circle(screen, (180, 180, 180), (tag_x, collar_y + int(5 * scale)), 2)
        pygame.draw.circle(screen, (200, 200, 200), (tag_x, collar_y + int(5 * scale)), 1)
        
    else:
        # ULTRA REALISTIC HUMAN POINTER - or TRALALA BRAINROT MODE!
        is_italian = secret_hack.get('became_italian', False)
        
        if is_italian:
            # � TRALALA/TRALALERO CHARACTER - The iconic brainrot legend!
            # Scale up for that iconic look
            scale = scale * 1.3
            
            # Tralala's distinctive tan skin
            skin_tone = (230, 190, 150)
            hair_color = (25, 15, 10)  # Very dark hair
            
            # Head - ROUND and distinctive Tralala shape
            head_x = int(x + 32 * scale)
            head_y = int(y + 12 * scale)
            head_radius = int(26 * scale)
            
            # Head shadow for depth
            pygame.draw.circle(screen, (195, 160, 130), 
                             (head_x + 3, head_y + 3), head_radius)
            # Face - rounder, fuller
            pygame.draw.circle(screen, skin_tone, (head_x, head_y), head_radius)
            # Face highlight
            pygame.draw.circle(screen, (245, 210, 175), 
                             (head_x - 8, head_y - 8), int(14 * scale))
            
            # ICONIC TRALALA HAIR - Short, dark, simple style
            # Top of head hair (short and neat)
            for hair_row in range(3):
                for hair_col in range(8):
                    hair_x = head_x - int(18 * scale) + hair_col * int(5 * scale)
                    hair_y = head_y - int(24 * scale) + hair_row * int(3 * scale)
                    pygame.draw.circle(screen, hair_color, (hair_x, hair_y), int(4 * scale))
            
            # Side hair (sideburns)
            pygame.draw.rect(screen, hair_color,
                           (head_x - int(25 * scale), head_y - int(15 * scale),
                            int(7 * scale), int(20 * scale)))
            pygame.draw.rect(screen, hair_color,
                           (head_x + int(18 * scale), head_y - int(15 * scale),
                            int(7 * scale), int(20 * scale)))
            
            # Hairline
            pygame.draw.arc(screen, hair_color,
                          (head_x - int(20 * scale), head_y - int(28 * scale),
                           int(40 * scale), int(20 * scale)), 0, 3.14, 5)
            
            # DISTINCTIVE TRALALA EYEBROWS - thick and expressive
            pygame.draw.arc(screen, (20, 15, 10), 
                          (head_x - int(14 * scale), head_y - int(12 * scale), 
                           int(12 * scale), int(8 * scale)), 0, 3.14, 4)
            pygame.draw.arc(screen, (20, 15, 10), 
                          (head_x + int(2 * scale), head_y - int(12 * scale), 
                           int(12 * scale), int(8 * scale)), 0, 3.14, 4)
            
            # ICONIC TRALALA EYES - Big, round, expressive!
            eye_white = (255, 255, 255)
            eye_iris = (60, 40, 20)  # Dark brown/almost black
            eye_pupil = (0, 0, 0)
            
            # Left eye
            pygame.draw.ellipse(screen, eye_white, 
                              (head_x - int(14 * scale), head_y - int(5 * scale), 
                               int(10 * scale), int(12 * scale)))
            pygame.draw.circle(screen, eye_iris, 
                             (head_x - int(9 * scale), head_y), int(4 * scale))
            pygame.draw.circle(screen, eye_pupil, 
                             (head_x - int(9 * scale), head_y), int(2 * scale))
            # Eye shine (makes it pop!)
            pygame.draw.circle(screen, (255, 255, 255), 
                             (head_x - int(8 * scale), head_y - 1), int(2 * scale))
            
            # Right eye
            pygame.draw.ellipse(screen, eye_white, 
                              (head_x + int(4 * scale), head_y - int(5 * scale), 
                               int(10 * scale), int(12 * scale)))
            pygame.draw.circle(screen, eye_iris, 
                             (head_x + int(9 * scale), head_y), int(4 * scale))
            pygame.draw.circle(screen, eye_pupil, 
                             (head_x + int(9 * scale), head_y), int(2 * scale))
            # Eye shine
            pygame.draw.circle(screen, (255, 255, 255), 
                             (head_x + int(10 * scale), head_y - 1), int(2 * scale))
            
            # ICONIC TRALALA SMILE - BIG, wide, characteristic grin!
            # Big curved smile
            pygame.draw.arc(screen, (160, 60, 60), 
                          (head_x - int(16 * scale), head_y + int(4 * scale), 
                           int(32 * scale), int(20 * scale)), 3.4, 6.0, 4)
            # Inner mouth
            pygame.draw.arc(screen, (140, 40, 40), 
                          (head_x - int(14 * scale), head_y + int(6 * scale), 
                           int(28 * scale), int(16 * scale)), 3.5, 5.9, 3)
            # Teeth showing - big white smile
            for tooth in range(7):
                tooth_x = head_x - 10 + tooth * 3
                pygame.draw.rect(screen, (255, 255, 255), 
                               (tooth_x, head_y + 12, 2, 5))
            
            # Nose - simple but distinctive
            nose_y = head_y + int(4 * scale)
            pygame.draw.circle(screen, (210, 170, 135), 
                             (head_x, nose_y), int(5 * scale))
            # Nostrils
            pygame.draw.circle(screen, (180, 140, 110), 
                             (head_x - 3, nose_y + 2), int(2 * scale))
            pygame.draw.circle(screen, (180, 140, 110), 
                             (head_x + 3, nose_y + 2), int(2 * scale))
            
            # CASUAL OUTFIT - Simple shirt (not fancy suit)
            shirt_color = (220, 220, 220)  # Light gray/white shirt
            
            # Body - simple casual shirt
            pygame.draw.rect(screen, (180, 180, 180),  # Shadow
                           (int(x + 17 * scale), int(y + 38 * scale), 
                            int(32 * scale), int(42 * scale)))
            pygame.draw.rect(screen, shirt_color, 
                           (int(x + 15 * scale), int(y + 36 * scale), 
                            int(32 * scale), int(42 * scale)))
            # Shirt collar
            pygame.draw.polygon(screen, (200, 200, 200), [
                (head_x - 8, head_y + 20),
                (head_x - 10, head_y + 28),
                (head_x - 6, head_y + 28)
            ])
            pygame.draw.polygon(screen, (255, 255, 255), [
                (head_x + 8, head_y + 20),
                (head_x + 10, head_y + 28),
                (head_x + 6, head_y + 28)
            ])
            
            # RED TIE - bold Italian style!
            tie_color = (200, 20, 20)
            pygame.draw.polygon(screen, tie_color, [
                (head_x, head_y + 22),
                (head_x - 4, head_y + 28),
                (head_x, head_y + 48),
                (head_x + 4, head_y + 28)
            ])
            # Tie knot
            pygame.draw.polygon(screen, (180, 15, 15), [
                (head_x - 5, head_y + 22),
                (head_x + 5, head_y + 22),
                (head_x + 4, head_y + 28),
                (head_x - 4, head_y + 28)
            ])
            # Tie shine (silk fabric)
            pygame.draw.line(screen, (255, 80, 80), 
                           (head_x - 2, head_y + 30), 
                           (head_x - 1, head_y + 45), 1)
            
            # Arms - ITALIAN HAND GESTURES! 🤌
            arm_color = skin_tone
            
            # Left arm doing classic Italian gesture (pinched fingers)
            left_arm_x = int(x + 10 * scale)
            left_shoulder_y = int(y + 35 * scale)
            left_elbow_y = int(y + 50 * scale + walk_offset)
            left_hand_y = int(y + 45 * scale + walk_offset * 1.5)
            
            # Left arm (shirt sleeve)
            pygame.draw.line(screen, shirt_color, 
                           (int(x + 18 * scale), left_shoulder_y),
                           (left_arm_x, left_elbow_y), int(10 * scale))
            pygame.draw.line(screen, shirt_color, 
                           (left_arm_x, left_elbow_y),
                           (left_arm_x - int(8 * scale), left_hand_y), int(8 * scale))
            # Left hand - pinched fingers gesture 🤌
            pygame.draw.circle(screen, arm_color, 
                             (left_arm_x - int(8 * scale), left_hand_y), int(6 * scale))
            # Fingers pinched together
            for finger in range(4):
                finger_angle = -0.5 + finger * 0.3
                finger_tip_x = left_arm_x - int(8 * scale) + int(math.cos(finger_angle) * 8 * scale)
                finger_tip_y = left_hand_y + int(math.sin(finger_angle) * 8 * scale)
                pygame.draw.line(screen, arm_color, 
                               (left_arm_x - int(8 * scale), left_hand_y),
                               (finger_tip_x, finger_tip_y), 3)
            
            # Right arm - dramatically pointing!
            right_arm_x = int(x + 46 * scale)
            right_elbow_y = int(y + 45 * scale - walk_offset)
            right_hand_x = int(x + 65 * scale - walk_offset)
            right_hand_y = int(y + 42 * scale - walk_offset * 1.2)
            
            # Right arm (shirt sleeve)
            pygame.draw.line(screen, shirt_color, 
                           (int(x + 46 * scale), left_shoulder_y),
                           (right_arm_x, right_elbow_y), int(10 * scale))
            pygame.draw.line(screen, shirt_color, 
                           (right_arm_x, right_elbow_y),
                           (right_hand_x - int(5 * scale), right_hand_y), int(8 * scale))
            # Right hand pointing
            pygame.draw.circle(screen, arm_color, 
                             (right_hand_x, right_hand_y), int(7 * scale))
            # Pointing finger extended
            pygame.draw.line(screen, arm_color, 
                           (right_hand_x, right_hand_y),
                           (right_hand_x + int(12 * scale), right_hand_y - int(3 * scale)), 4)
            # Fingertip
            pygame.draw.circle(screen, arm_color, 
                             (right_hand_x + int(12 * scale), right_hand_y - int(3 * scale)), 3)
            
            # Legs - dress pants (perfectly tailored)
            pants_color = (30, 30, 50)
            pygame.draw.rect(screen, pants_color, 
                           (int(x + 24 * scale), int(y + 70 * scale + walk_offset), 
                            int(10 * scale), int(28 * scale)))
            pygame.draw.rect(screen, pants_color, 
                           (int(x + 36 * scale), int(y + 70 * scale - walk_offset), 
                            int(10 * scale), int(28 * scale)))
            # Pants crease (sharp!)
            pygame.draw.line(screen, (50, 50, 70), 
                           (int(x + 29 * scale), int(y + 72 * scale + walk_offset)),
                           (int(x + 29 * scale), int(y + 96 * scale + walk_offset)), 1)
            pygame.draw.line(screen, (50, 50, 70), 
                           (int(x + 41 * scale), int(y + 72 * scale - walk_offset)),
                           (int(x + 41 * scale), int(y + 96 * scale - walk_offset)), 1)
            
            # LUXURY ITALIAN LEATHER SHOES (polished to perfection!)
            shoe_color = (20, 10, 5)
            shoe_shine = (100, 80, 60)
            
            # Left shoe
            pygame.draw.ellipse(screen, shoe_color, 
                              (int(x + 22 * scale), int(y + 96 * scale + walk_offset), 
                               int(14 * scale), int(8 * scale)))
            pygame.draw.ellipse(screen, shoe_shine, 
                              (int(x + 24 * scale), int(y + 97 * scale + walk_offset), 
                               int(8 * scale), int(3 * scale)))
            
            # Right shoe
            pygame.draw.ellipse(screen, shoe_color, 
                              (int(x + 34 * scale), int(y + 96 * scale - walk_offset), 
                               int(14 * scale), int(8 * scale)))
            pygame.draw.ellipse(screen, shoe_shine, 
                              (int(x + 36 * scale), int(y + 97 * scale - walk_offset), 
                               int(8 * scale), int(3 * scale)))
            
            # GOLD ROLEX WATCH on left wrist!
            watch_x = left_arm_x - int(6 * scale)
            watch_y = left_elbow_y - int(2 * scale)
            # Watch face
            pygame.draw.circle(screen, (255, 215, 0), (watch_x, watch_y), int(4 * scale))
            pygame.draw.circle(screen, (30, 30, 30), (watch_x, watch_y), int(3 * scale))
            # Watch shine
            pygame.draw.circle(screen, (255, 255, 200), 
                             (watch_x - 1, watch_y - 1), int(1 * scale))
            
        else:
            # ULTRA REALISTIC MODERN HUMAN POINTER
            # Realistic proportions and detailed features
            
            # Skin tone - natural and realistic
            skin_tone = (255, 220, 177)
            skin_shadow = (225, 190, 147)
            skin_highlight = (255, 235, 200)
            
            # Head - properly proportioned with 3D shading
            head_x = int(x + 32 * scale)
            head_y = int(y + 10 * scale)
            head_radius = int(20 * scale)
            
            # Head shadow (depth)
            pygame.draw.circle(screen, skin_shadow, 
                             (head_x + 2, head_y + 2), head_radius)
            # Face base
            pygame.draw.circle(screen, skin_tone, (head_x, head_y), head_radius)
            # Face highlight (forehead, cheekbones)
            pygame.draw.circle(screen, skin_highlight, 
                             (head_x - 5, head_y - 5), int(12 * scale))
            # Cheek blush (natural)
            pygame.draw.circle(screen, (255, 200, 180), 
                             (head_x - 8, head_y + 5), int(6 * scale))
            pygame.draw.circle(screen, (255, 200, 180), 
                             (head_x + 8, head_y + 5), int(6 * scale))
            
            # Hair - modern style with texture
            hair_color = (70, 50, 30)
            hair_highlight = (100, 80, 60)
            # Hair bulk
            for hair_layer in range(15):
                hair_x = head_x - int(16 * scale) + hair_layer * int(2 * scale)
                hair_y = head_y - int(18 * scale) + int(abs(hair_layer - 7) * 0.5 * scale)
                hair_length = int(10 * scale) + int(abs(hair_layer - 7) * scale)
                pygame.draw.line(screen, hair_color, 
                               (hair_x, hair_y), 
                               (hair_x, hair_y - hair_length), int(2 * scale))
            # Hair highlights (realistic shine)
            pygame.draw.line(screen, hair_highlight, 
                           (head_x - 8, head_y - int(20 * scale)),
                           (head_x, head_y - int(24 * scale)), 2)
            
            # Eyebrows - natural shape
            pygame.draw.arc(screen, (60, 40, 25), 
                          (head_x - int(11 * scale), head_y - int(8 * scale), 
                           int(8 * scale), int(5 * scale)), 0, 3.14, 2)
            pygame.draw.arc(screen, (60, 40, 25), 
                          (head_x + int(3 * scale), head_y - int(8 * scale), 
                           int(8 * scale), int(5 * scale)), 0, 3.14, 2)
            
            # Eyes - detailed and expressive
            # Eye whites
            pygame.draw.ellipse(screen, (255, 255, 255), 
                              (head_x - int(12 * scale), head_y - int(3 * scale), 
                               int(9 * scale), int(10 * scale)))
            pygame.draw.ellipse(screen, (255, 255, 255), 
                              (head_x + int(3 * scale), head_y - int(3 * scale), 
                               int(9 * scale), int(10 * scale)))
            
            # Irises (blue eyes)
            pygame.draw.circle(screen, (100, 160, 200), 
                             (head_x - int(7 * scale), head_y + 1), int(4 * scale))
            pygame.draw.circle(screen, (100, 160, 200), 
                             (head_x + int(7 * scale), head_y + 1), int(4 * scale))
            
            # Pupils
            pygame.draw.circle(screen, (0, 0, 0), 
                             (head_x - int(7 * scale), head_y + 1), int(2 * scale))
            pygame.draw.circle(screen, (0, 0, 0), 
                             (head_x + int(7 * scale), head_y + 1), int(2 * scale))
            
            # Eye shine (makes them look alive!)
            pygame.draw.circle(screen, (255, 255, 255), 
                             (head_x - int(6 * scale), head_y), int(1 * scale))
            pygame.draw.circle(screen, (255, 255, 255), 
                             (head_x + int(8 * scale), head_y), int(1 * scale))
            
            # Eyelashes (top)
            for lash in range(3):
                pygame.draw.line(screen, (40, 30, 20), 
                               (head_x - 10 + lash * 2, head_y - 3),
                               (head_x - 10 + lash * 2, head_y - 5), 1)
                pygame.draw.line(screen, (40, 30, 20), 
                               (head_x + 5 + lash * 2, head_y - 3),
                               (head_x + 5 + lash * 2, head_y - 5), 1)
            
            # Nose - subtle but realistic
            pygame.draw.line(screen, skin_shadow, 
                           (head_x, head_y + 2), 
                           (head_x, head_y + 8), 2)
            # Nostrils
            pygame.draw.circle(screen, skin_shadow, 
                             (head_x - 2, head_y + 8), 1)
            pygame.draw.circle(screen, skin_shadow, 
                             (head_x + 2, head_y + 8), 1)
            
            # Mouth - friendly smile
            pygame.draw.arc(screen, (200, 100, 100), 
                          (head_x - int(10 * scale), head_y + int(8 * scale), 
                           int(20 * scale), int(12 * scale)), 3.3, 6.1, 2)
            # Teeth (subtle)
            for tooth in range(4):
                pygame.draw.line(screen, (255, 255, 255), 
                               (head_x - 6 + tooth * 3, head_y + 13),
                               (head_x - 6 + tooth * 3, head_y + 15), 2)
            
            # Neck
            pygame.draw.rect(screen, skin_tone, 
                           (int(x + 27 * scale), int(y + 28 * scale), 
                            int(10 * scale), int(8 * scale)))
            pygame.draw.rect(screen, skin_shadow, 
                           (int(x + 27 * scale), int(y + 28 * scale), 
                            int(3 * scale), int(8 * scale)))
            
            # Body - casual modern clothing
            # T-shirt (sky blue)
            shirt_color = (100, 180, 220)
            shirt_shadow = (80, 150, 190)
            
            pygame.draw.rect(screen, shirt_shadow, 
                           (int(x + 20 * scale), int(y + 35 * scale), 
                            int(24 * scale), int(38 * scale)))
            pygame.draw.rect(screen, shirt_color, 
                           (int(x + 18 * scale), int(y + 35 * scale), 
                            int(24 * scale), int(38 * scale)))
            # Shirt wrinkles (realism!)
            pygame.draw.line(screen, shirt_shadow, 
                           (int(x + 22 * scale), int(y + 45 * scale)),
                           (int(x + 28 * scale), int(y + 48 * scale)), 1)
            pygame.draw.line(screen, shirt_shadow, 
                           (int(x + 32 * scale), int(y + 50 * scale)),
                           (int(x + 38 * scale), int(y + 52 * scale)), 1)
            
            # Arms - one casually down, one pointing
            arm_shadow = skin_shadow
            
            # Left arm (relaxed)
            pygame.draw.line(screen, arm_shadow, 
                           (int(x + 20 * scale), int(y + 38 * scale)),
                           (int(x + 12 * scale), int(y + 50 * scale + walk_offset)), int(8 * scale))
            pygame.draw.line(screen, skin_tone, 
                           (int(x + 19 * scale), int(y + 38 * scale)),
                           (int(x + 11 * scale), int(y + 50 * scale + walk_offset)), int(7 * scale))
            pygame.draw.line(screen, arm_shadow, 
                           (int(x + 12 * scale), int(y + 50 * scale + walk_offset)),
                           (int(x + 10 * scale), int(y + 62 * scale + walk_offset)), int(7 * scale))
            pygame.draw.line(screen, skin_tone, 
                           (int(x + 11 * scale), int(y + 50 * scale + walk_offset)),
                           (int(x + 9 * scale), int(y + 62 * scale + walk_offset)), int(6 * scale))
            # Left hand
            pygame.draw.circle(screen, skin_tone, 
                             (int(x + 9 * scale), int(y + 65 * scale + walk_offset)), int(5 * scale))
            # Fingers
            for finger in range(4):
                pygame.draw.line(screen, skin_tone, 
                               (int(x + 9 * scale), int(y + 65 * scale + walk_offset)),
                               (int(x + 7 * scale) + finger, int(y + 70 * scale + walk_offset)), 2)
            
            # Right arm (pointing enthusiastically!)
            pygame.draw.line(screen, arm_shadow, 
                           (int(x + 42 * scale), int(y + 38 * scale)),
                           (int(x + 48 * scale), int(y + 45 * scale - walk_offset)), int(8 * scale))
            pygame.draw.line(screen, skin_tone, 
                           (int(x + 41 * scale), int(y + 38 * scale)),
                           (int(x + 47 * scale), int(y + 45 * scale - walk_offset)), int(7 * scale))
            pygame.draw.line(screen, arm_shadow, 
                           (int(x + 48 * scale), int(y + 45 * scale - walk_offset)),
                           (int(x + 58 * scale), int(y + 48 * scale - walk_offset)), int(7 * scale))
            pygame.draw.line(screen, skin_tone, 
                           (int(x + 47 * scale), int(y + 45 * scale - walk_offset)),
                           (int(x + 57 * scale), int(y + 48 * scale - walk_offset)), int(6 * scale))
            # Right hand (fist with pointing finger!)
            pygame.draw.circle(screen, skin_tone, 
                             (int(x + 58 * scale), int(y + 48 * scale - walk_offset)), int(6 * scale))
            # Extended pointing finger
            pygame.draw.line(screen, skin_tone, 
                           (int(x + 58 * scale), int(y + 48 * scale - walk_offset)),
                           (int(x + 68 * scale), int(y + 46 * scale - walk_offset)), 4)
            # Fingertip
            pygame.draw.circle(screen, skin_tone, 
                             (int(x + 68 * scale), int(y + 46 * scale - walk_offset)), 2)
            # Fingernail
            pygame.draw.circle(screen, (255, 240, 220), 
                             (int(x + 68 * scale), int(y + 46 * scale - walk_offset)), 1)
            
            # Legs - jeans
            jeans_color = (60, 80, 120)
            jeans_shadow = (40, 60, 100)
            jeans_highlight = (80, 100, 140)
            
            # Left leg
            pygame.draw.rect(screen, jeans_shadow, 
                           (int(x + 24 * scale), int(y + 72 * scale + walk_offset), 
                            int(9 * scale), int(26 * scale)))
            pygame.draw.rect(screen, jeans_color, 
                           (int(x + 23 * scale), int(y + 72 * scale + walk_offset), 
                            int(9 * scale), int(26 * scale)))
            # Jean seam
            pygame.draw.line(screen, jeans_highlight, 
                           (int(x + 27 * scale), int(y + 74 * scale + walk_offset)),
                           (int(x + 27 * scale), int(y + 96 * scale + walk_offset)), 1)
            
            # Right leg
            pygame.draw.rect(screen, jeans_shadow, 
                           (int(x + 36 * scale), int(y + 72 * scale - walk_offset), 
                            int(9 * scale), int(26 * scale)))
            pygame.draw.rect(screen, jeans_color, 
                           (int(x + 35 * scale), int(y + 72 * scale - walk_offset), 
                            int(9 * scale), int(26 * scale)))
            # Jean seam
            pygame.draw.line(screen, jeans_highlight, 
                           (int(x + 39 * scale), int(y + 74 * scale - walk_offset)),
                           (int(x + 39 * scale), int(y + 96 * scale - walk_offset)), 1)
            
            # Sneakers - modern athletic shoes
            shoe_color = (240, 240, 240)
            shoe_shadow = (180, 180, 180)
            shoe_accent = (255, 100, 100)
            
            # Left shoe
            pygame.draw.ellipse(screen, shoe_shadow, 
                              (int(x + 22 * scale), int(y + 96 * scale + walk_offset), 
                               int(13 * scale), int(7 * scale)))
            pygame.draw.ellipse(screen, shoe_color, 
                              (int(x + 21 * scale), int(y + 95 * scale + walk_offset), 
                               int(13 * scale), int(7 * scale)))
            # Shoe accent stripe
            pygame.draw.arc(screen, shoe_accent, 
                          (int(x + 23 * scale), int(y + 96 * scale + walk_offset), 
                           int(9 * scale), int(5 * scale)), 0, 3.14, 2)
            
            # Right shoe
            pygame.draw.ellipse(screen, shoe_shadow, 
                              (int(x + 34 * scale), int(y + 96 * scale - walk_offset), 
                               int(13 * scale), int(7 * scale)))
            pygame.draw.ellipse(screen, shoe_color, 
                              (int(x + 33 * scale), int(y + 95 * scale - walk_offset), 
                               int(13 * scale), int(7 * scale)))
            # Shoe accent stripe
            pygame.draw.arc(screen, shoe_accent, 
                          (int(x + 35 * scale), int(y + 96 * scale - walk_offset), 
                           int(9 * scale), int(5 * scale)), 0, 3.14, 2)


def rainbow_explosion():
    """EPIC RAINBOW EXPLOSION when you type gagabubu!"""
    import subprocess
    
    # Announce it!
    try:
        subprocess.run(['say', '-v', 'Superstar', '-r', '250', 'Gaga bubu! Rainbow explosion!'], check=False)
    except:
        pass
    
    explosion_duration = 5  # 5 seconds of rainbow madness
    start_time = time.time()
    
    # Create rainbow particles
    particles = []
    for _ in range(200):
        particles.append({
            'x': WIDTH // 2,
            'y': HEIGHT // 2,
            'vx': random.uniform(-15, 15),
            'vy': random.uniform(-15, 15),
            'color': [random.randint(0, 255) for _ in range(3)],
            'size': random.randint(5, 20),
            'life': random.uniform(1, 3)
        })
    
    # Rainbow rings expanding
    rings = []
    
    while time.time() - start_time < explosion_duration:
        elapsed = time.time() - start_time
        
        # Cycle through rainbow background
        bg_hue = (elapsed * 100) % 360
        bg_color = pygame.Color(0)
        bg_color.hsva = (bg_hue, 100, 50, 100)
        screen.fill(bg_color)
        
        # Add new expanding rings
        if random.random() < 0.3:
            rings.append({
                'x': WIDTH // 2,
                'y': HEIGHT // 2,
                'radius': 10,
                'color': [random.randint(100, 255) for _ in range(3)],
                'speed': random.uniform(5, 15),
                'width': random.randint(3, 8)
            })
        
        # Draw and update rings
        for ring in rings[:]:
            ring['radius'] += ring['speed']
            if ring['radius'] > max(WIDTH, HEIGHT):
                rings.remove(ring)
            else:
                pygame.draw.circle(screen, ring['color'], 
                                 (ring['x'], ring['y']), 
                                 int(ring['radius']), ring['width'])
        
        # Update and draw particles
        for particle in particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.3  # Gravity
            particle['life'] -= 0.016
            
            if particle['life'] <= 0 or particle['y'] > HEIGHT:
                particles.remove(particle)
            else:
                # Particle changes color over time
                hue = (elapsed * 200 + particle['x']) % 360
                p_color = pygame.Color(0)
                p_color.hsva = (hue, 100, 100, 100)
                
                pygame.draw.circle(screen, p_color, 
                                 (int(particle['x']), int(particle['y'])), 
                                 particle['size'])
        
        # Add new particles continuously
        if len(particles) < 300:
            for _ in range(5):
                particles.append({
                    'x': WIDTH // 2,
                    'y': HEIGHT // 2,
                    'vx': random.uniform(-15, 15),
                    'vy': random.uniform(-15, 15),
                    'color': [random.randint(0, 255) for _ in range(3)],
                    'size': random.randint(5, 20),
                    'life': random.uniform(1, 3)
                })
        
        # Rainbow text effects
        text_font = pygame.font.Font(None, 120)
        messages = ["GAGABUBU!", "🌈", "RAINBOW!", "✨", "EXPLOSION!", "💥"]
        msg = messages[int(elapsed * 2) % len(messages)]
        
        # Each letter in different color
        x_offset = 0
        for i, char in enumerate(msg):
            char_hue = (elapsed * 100 + i * 30) % 360
            char_color = pygame.Color(0)
            char_color.hsva = (char_hue, 100, 100, 100)
            
            char_text = text_font.render(char, True, char_color)
            char_y = HEIGHT // 2 - 200 + int(math.sin(elapsed * 5 + i) * 20)
            screen.blit(char_text, (WIDTH // 2 - 300 + x_offset, char_y))
            x_offset += char_text.get_width()
        
        # Rainbow spiral effect
        num_spirals = 8
        for i in range(num_spirals):
            angle = (elapsed * 3 + i * (360 / num_spirals)) % 360
            radius = 150 + math.sin(elapsed * 2) * 50
            
            spiral_x = WIDTH // 2 + int(math.cos(math.radians(angle)) * radius)
            spiral_y = HEIGHT // 2 + int(math.sin(math.radians(angle)) * radius)
            
            spiral_hue = (angle + elapsed * 100) % 360
            spiral_color = pygame.Color(0)
            spiral_color.hsva = (spiral_hue, 100, 100, 100)
            
            pygame.draw.circle(screen, spiral_color, (spiral_x, spiral_y), 15)
        
        # Screen flash effect
        if int(elapsed * 4) % 2 == 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT))
            flash_surf.set_alpha(30)
            flash_hue = (elapsed * 200) % 360
            flash_color = pygame.Color(0)
            flash_color.hsva = (flash_hue, 100, 100, 100)
            flash_surf.fill(flash_color)
            screen.blit(flash_surf, (0, 0))
        
        pygame.display.flip()
        clock.tick(60)
        
        # Check for exit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
    
    # Final fade out
    for fade_alpha in range(255, 0, -10):
        screen.fill((0, 0, 0))
        fade_surf = pygame.Surface((WIDTH, HEIGHT))
        fade_surf.set_alpha(fade_alpha)
        fade_surf.fill((255, 0, 255))
        screen.blit(fade_surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)


def quiz_mode():
    """General Knowledge Quiz Mode - Test your brain!"""
    import subprocess
    
    # Quiz questions - each has question, options (4 choices), and correct answer index
    questions = [
        {
            "q": "What is the capital of France?",
            "options": ["London", "Paris", "Berlin", "Madrid"],
            "correct": 1,
            "fun_fact": "Paris is called the City of Light!"
        },
        {
            "q": "How many planets are in our solar system?",
            "options": ["7", "8", "9", "10"],
            "correct": 1,
            "fun_fact": "Pluto was reclassified as a dwarf planet in 2006!"
        },
        {
            "q": "What is the largest ocean on Earth?",
            "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
            "correct": 3,
            "fun_fact": "The Pacific Ocean covers more area than all land combined!"
        },
        {
            "q": "How many colors are in a rainbow?",
            "options": ["5", "6", "7", "8"],
            "correct": 2,
            "fun_fact": "ROY G BIV: Red, Orange, Yellow, Green, Blue, Indigo, Violet!"
        },
        {
            "q": "What is the fastest land animal?",
            "options": ["Lion", "Cheetah", "Horse", "Gazelle"],
            "correct": 1,
            "fun_fact": "Cheetahs can run up to 70 mph!"
        },
        {
            "q": "How many sides does a hexagon have?",
            "options": ["5", "6", "7", "8"],
            "correct": 1,
            "fun_fact": "Honeycombs are made of hexagons!"
        },
        {
            "q": "What is the largest mammal?",
            "options": ["Elephant", "Blue Whale", "Giraffe", "Polar Bear"],
            "correct": 1,
            "fun_fact": "Blue whales can weigh up to 200 tons!"
        },
        {
            "q": "How many continents are there?",
            "options": ["5", "6", "7", "8"],
            "correct": 2,
            "fun_fact": "Asia is the largest continent!"
        },
        {
            "q": "What is 12 x 12?",
            "options": ["124", "144", "132", "156"],
            "correct": 1,
            "fun_fact": "This is called a gross - a dozen dozens!"
        },
        {
            "q": "What gas do plants breathe in?",
            "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Helium"],
            "correct": 2,
            "fun_fact": "Plants use CO2 for photosynthesis!"
        },
        {
            "q": "How many days are in a leap year?",
            "options": ["364", "365", "366", "367"],
            "correct": 2,
            "fun_fact": "Leap years happen every 4 years!"
        },
        {
            "q": "What is the smallest country in the world?",
            "options": ["Monaco", "Vatican City", "San Marino", "Luxembourg"],
            "correct": 1,
            "fun_fact": "Vatican City is only 0.17 square miles!"
        },
        {
            "q": "How many keys are on a standard piano?",
            "options": ["76", "82", "88", "92"],
            "correct": 2,
            "fun_fact": "52 white keys and 36 black keys!"
        },
        {
            "q": "What is the tallest mountain in the world?",
            "options": ["K2", "Everest", "Kilimanjaro", "Denali"],
            "correct": 1,
            "fun_fact": "Mount Everest is 29,032 feet tall!"
        },
        {
            "q": "How many bones are in the human body?",
            "options": ["186", "206", "226", "246"],
            "correct": 1,
            "fun_fact": "Babies are born with about 300 bones!"
        }    ]
    
    # Shuffle questions
    random.shuffle(questions)
    
    # Take first 10 questions
    quiz_questions = questions[:10]
    
    score = 0
    current_question = 0
    
    # Intro
    try:
        subprocess.run(['say', '-v', 'Alex', '-r', '180', 'Welcome to the quiz! Test your knowledge!'], check=False)
    except:
        pass
    
    while current_question < len(quiz_questions):
        q_data = quiz_questions[current_question]
        selected = 0
        answered = False
        
        while not answered:
            # Rainbow gradient background
            for y in range(0, HEIGHT, 5):
                hue = (y / HEIGHT * 360) % 360
                color = pygame.Color(0)
                color.hsva = (hue, 30, 90, 100)
                pygame.draw.rect(screen, color, (0, y, WIDTH, 5))
            
            # Progress bar
            progress_width = int((current_question / len(quiz_questions)) * WIDTH)
            pygame.draw.rect(screen, (100, 255, 100), (0, 0, progress_width, 20))
            pygame.draw.rect(screen, (50, 50, 50), (progress_width, 0, WIDTH - progress_width, 20))
            
            # Score display
            score_font = pygame.font.Font(None, 48)
            score_text = score_font.render(f"Score: {score}/{current_question}", True, (255, 255, 255))
            screen.blit(score_text, (20, 40))
            
            # Question number
            q_num_text = score_font.render(f"Question {current_question + 1}/{len(quiz_questions)}", True, (255, 255, 255))
            screen.blit(q_num_text, (WIDTH - q_num_text.get_width() - 20, 40))
            
            # Question text
            question_font = pygame.font.Font(None, 56)
            question_text = question_font.render(q_data["q"], True, (255, 255, 255))
            
            # Word wrap if too long
            if question_text.get_width() > WIDTH - 100:
                words = q_data["q"].split()
                lines = []
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    if question_font.render(test_line, True, (255, 255, 255)).get_width() < WIDTH - 100:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word + " "
                lines.append(current_line)
                
                y_offset = 150
                for line in lines:
                    line_surf = question_font.render(line, True, (255, 255, 255))
                    screen.blit(line_surf, (WIDTH//2 - line_surf.get_width()//2, y_offset))
                    y_offset += 60
            else:
                screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, 150))
            
            # Answer options
            option_font = pygame.font.Font(None, 48)
            option_y = 350
            option_spacing = 80
            
            for i, option in enumerate(q_data["options"]):
                # Highlight selected option
                if i == selected:
                    bg_color = (255, 200, 0)
                    text_color = (0, 0, 0)
                else:
                    bg_color = (70, 70, 100)
                    text_color = (255, 255, 255)
                
                # Draw option box
                option_rect = pygame.Rect(WIDTH//2 - 300, option_y + i * option_spacing, 600, 60)
                pygame.draw.rect(screen, bg_color, option_rect, border_radius=10)
                pygame.draw.rect(screen, (255, 255, 255), option_rect, 3, border_radius=10)
                
                # Letter label (A, B, C, D)
                letter = chr(65 + i)  # A=65 in ASCII
                letter_text = option_font.render(f"{letter})", True, text_color)
                screen.blit(letter_text, (option_rect.x + 20, option_rect.y + 10))
                
                # Option text
                option_text = option_font.render(option, True, text_color)
                screen.blit(option_text, (option_rect.x + 80, option_rect.y + 10))
            
            # Controls hint
            hint_font = pygame.font.Font(None, 36)
            hint = hint_font.render("↑↓ to select  •  Enter to answer  •  ESC to quit", True, (200, 200, 200))
            screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 60))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % 4
                        try:
                            subprocess.run(['say', '-v', 'Zarvox', '-r', '400', 'beep'], check=False)
                        except:
                            pass
                    if event.key == pygame.K_DOWN:
                        selected = (selected + 1) % 4
                        try:
                            subprocess.run(['say', '-v', 'Zarvox', '-r', '400', 'boop'], check=False)
                        except:
                            pass
                    if event.key == pygame.K_RETURN:
                        answered = True
                        
                        # Check if correct
                        if selected == q_data["correct"]:
                            score += 1
                            show_answer_feedback(True, q_data["fun_fact"])
                        else:
                            correct_answer = q_data["options"][q_data["correct"]]
                            show_answer_feedback(False, q_data["fun_fact"], correct_answer)
        
        current_question += 1
    
    # Final results
    show_quiz_results(score, len(quiz_questions))


def show_answer_feedback(correct, fun_fact, correct_answer=None):
    """Show if answer was correct or wrong with animation"""
    import subprocess
    
    duration = 3  # seconds
    start_time = time.time()
    
    if correct:
        bg_color = (0, 150, 0)
        message = "CORRECT! ✓"
        voice_msg = "Correct! Well done!"
    else:
        bg_color = (150, 0, 0)
        message = "WRONG! ✗"
        voice_msg = f"Wrong! The correct answer was {correct_answer}."
    
    # Say it
    try:
        subprocess.run(['say', '-v', 'Alex', '-r', '180', voice_msg], check=False)
    except:
        pass
    
    while time.time() - start_time < duration:
        elapsed = time.time() - start_time
        
        # Pulsing background
        pulse = int(50 * math.sin(elapsed * 5))
        current_bg = tuple(min(255, max(0, c + pulse)) for c in bg_color)
        screen.fill(current_bg)
        
        # Big message
        msg_font = pygame.font.Font(None, 120)
        msg_surf = msg_font.render(message, True, (255, 255, 255))
        screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT//2 - 150))
        
        # Correct answer if wrong
        if not correct and correct_answer:
            ans_font = pygame.font.Font(None, 48)
            ans_text = ans_font.render(f"Correct answer: {correct_answer}", True, (255, 255, 200))
            screen.blit(ans_text, (WIDTH//2 - ans_text.get_width()//2, HEIGHT//2 - 20))
        
        # Fun fact
        fact_font = pygame.font.Font(None, 42)
        fact_label = fact_font.render("Fun Fact:", True, (255, 255, 100))
        screen.blit(fact_label, (WIDTH//2 - fact_label.get_width()//2, HEIGHT//2 + 50))
        
        fact_text = fact_font.render(fun_fact, True, (255, 255, 255))
        screen.blit(fact_text, (WIDTH//2 - fact_text.get_width()//2, HEIGHT//2 + 110))
        
        pygame.display.flip()
        clock.tick(60)
        
        # Allow skip
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return


def show_quiz_results(score, total):
    """Show final quiz results with grade"""
    import subprocess
    
    percentage = (score / total) * 100
    
    # Determine grade and message
    if percentage >= 90:
        grade = "A+"
        message = "AMAZING!"
        color = (255, 215, 0)
        voice = "Superstar"
        voice_msg = "Amazing! You got an A plus! You are a genius!"
    elif percentage >= 80:
        grade = "A"
        message = "EXCELLENT!"
        color = (100, 255, 100)
        voice = "Good News"
        voice_msg = "Excellent! You got an A! Great job!"
    elif percentage >= 70:
        grade = "B"
        message = "GOOD JOB!"
        color = (100, 200, 255)
        voice = "Alex"
        voice_msg = "Good job! You got a B! Nice work!"
    elif percentage >= 60:
        grade = "C"
        message = "NOT BAD!"
        color = (255, 200, 100)
        voice = "Alex"
        voice_msg = "Not bad! You got a C! Keep practicing!"
    else:
        grade = "D"
        message = "KEEP TRYING!"
        color = (255, 100, 100)
        voice = "Bad News"
        voice_msg = "Keep trying! Practice makes perfect!"
    
    # Say results
    try:
        subprocess.run(['say', '-v', voice, '-r', '180', voice_msg], check=False)
    except:
        pass
    
    # Animate results
    for frame in range(180):  # 3 seconds at 60fps
        screen.fill((20, 20, 40))
        
        # Confetti if good score
        if percentage >= 70:
            for _ in range(5):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                confetti_color = [random.randint(100, 255) for _ in range(3)]
                pygame.draw.circle(screen, confetti_color, (x, y), random.randint(3, 8))
            
            # Title
            title_font = pygame.font.Font(None, 80)
            title = title_font.render("QUIZ COMPLETE!", True, (255, 255, 255))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
            
            # Score
            score_font = pygame.font.Font(None, 120)
            score_text = score_font.render(f"{score}/{total}", True, color)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 220))
            
            # Percentage
            perc_font = pygame.font.Font(None, 72)
            perc_text = perc_font.render(f"{percentage:.0f}%", True, (255, 255, 255))
            screen.blit(perc_text, (WIDTH//2 - perc_text.get_width()//2, 360))
            
            # Grade (pulsing)
            pulse = 1.0 + 0.2 * math.sin(frame * 0.1)
            grade_size = int(150 * pulse)
            grade_font = pygame.font.Font(None, grade_size)
            grade_text = grade_font.render(grade, True, color)
            screen.blit(grade_text, (WIDTH//2 - grade_text.get_width()//2, 480))
            
            # Message
            msg_font = pygame.font.Font(None, 64)
            msg_text = msg_font.render(message, True, color)
            screen.blit(msg_text, (WIDTH//2 - msg_text.get_width()//2, 650))
                 # Continue hint
        hint_font = pygame.font.Font(None, 36)
        hint = hint_font.render("Press any key to continue", True, (150, 150, 150))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 80))
        
        pygame.display.flip()
        clock.tick(60)
        
        # Check for exit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return


def ai_helper():
    """Interactive AI Helper that can talk and assist you!"""
    import subprocess
    
    # AI Helper personality and voice settings
    ai_voice = "Zarvox"  # Robot voice
    ai_speed = 180  # Words per minute
    
    def ai_speak(text, voice=None, speed=None):
        """Make the AI speak!"""
        v = voice or ai_voice
        s = speed or ai_speed
        try:
            subprocess.run(['say', '-v', v, '-r', str(s), text], check=False)
        except:
            pass
    
    # Welcome message
    ai_speak("Hello! I am your A I Helper! How can I assist you today?")
    
    # Helper menu options
    helper_options = [
        "📚 Learn Game Controls",
        "🎮 Game Mode Explanations", 
        "🔐 Secret Code Hints",
        "🌐 GitHub Pages Help",
        "💡 General Tips",
        "🗣️ Change My Voice",
        "🎵 Tell Me a Joke",
        "❌ Exit Helper"
    ]
    
    selected = 0
    
    while True:
        screen.fill((20, 20, 40))  # Dark blue background
        
        # Draw AI robot character
        robot_x = WIDTH // 2
        robot_y = 200
        
        # Animated robot head
        pulse = math.sin(time.time() * 3) * 5
        head_size = 100 + int(pulse)
        
        # Robot head (main body)
        pygame.draw.rect(screen, (150, 150, 200), 
                        (robot_x - head_size//2, robot_y - head_size//2, head_size, head_size), 
                        border_radius=10)
        
        # Antenna
        antenna_height = 40
        pygame.draw.line(screen, (200, 200, 255), 
                        (robot_x, robot_y - head_size//2), 
                        (robot_x, robot_y - head_size//2 - antenna_height), 3)
        pygame.draw.circle(screen, (255, 100, 100), 
                          (robot_x, robot_y - head_size//2 - antenna_height), 8)
        
        # Blinking eyes
        blink = int(time.time() * 2) % 10 < 1
        eye_height = 5 if blink else 15
        
        # Left eye
        pygame.draw.rect(screen, (100, 255, 100), 
                        (robot_x - 30, robot_y - 10, 20, eye_height))
        # Right eye
        pygame.draw.rect(screen, (100, 255, 100), 
                        (robot_x + 10, robot_y - 10, 20, eye_height))
        
        # Smile
        smile_width = 40
        pygame.draw.arc(screen, (100, 255, 100), 
                       (robot_x - smile_width//2, robot_y + 10, smile_width, 20), 
                       math.pi, 0, 3)
        
        # Title
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("🤖 AI HELPER 🤖", True, (100, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Menu options
        menu_start_y = 350
        for i, option in enumerate(helper_options):
            color = (255, 255, 100) if i == selected else (200, 200, 200)
            option_font = pygame.font.Font(None, 42)
            option_text = option_font.render(option, True, color)
            screen.blit(option_text, (WIDTH//2 - option_text.get_width()//2, menu_start_y + i * 50))
        
        # Pointer
        pointer_y = menu_start_y + selected * 50 + 10
        pointer_font = pygame.font.Font(None, 60)
        pointer = pointer_font.render("➤", True, (255, 255, 100))
        screen.blit(pointer, (WIDTH//2 - 350, pointer_y))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(helper_options)
                    ai_speak("Beep", speed=300)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(helper_options)
                    ai_speak("Boop", speed=300)
                if event.key == pygame.K_ESCAPE:
                    ai_speak("Goodbye! Have fun playing!")
                    return
                if event.key == pygame.K_RETURN:
                    choice = helper_options[selected]
                    
                    # Handle AI Helper actions
                    if "Exit Helper" in choice:
                        ai_speak("Goodbye! Have fun playing!")
                        return
                    
                    elif "Learn Game Controls" in choice:
                        ai_speak("Here are the game controls!")
                        show_controls_help(ai_speak)
                    
                    elif "Game Mode Explanations" in choice:
                        ai_speak("Let me explain the game modes!")
                        show_mode_explanations(ai_speak)
                    
                    elif "Secret Code Hints" in choice:
                        ai_speak("Ooh, secrets! Let me give you some hints!")
                        show_secret_hints(ai_speak)
                    
                    elif "GitHub Pages Help" in choice:
                        ai_speak("I can help you put your game on the internet!")
                        show_github_help(ai_speak)
                    
                    elif "General Tips" in choice:
                        ai_speak("Here are some helpful tips!")
                        show_general_tips(ai_speak)
                    
                    elif "Change My Voice" in choice:
                        ai_voice = change_ai_voice(ai_speak)
                        ai_speak("This is my new voice! Do you like it?", voice=ai_voice)
                    
                    elif "Tell Me a Joke" in choice:
                        tell_joke(ai_speak)


def show_controls_help(speak_func):
    """Display game controls with AI narration"""
    controls_pages = [
        {
            "title": "Battle Mode Controls",
            "text": [
                "Player 1: WASD to move, Space to shoot",
                "Player 2: Arrow keys to move, Enter to shoot",
                "",
                "Collect items and defeat your opponent!"
            ],
            "speech": "Player 1 uses W A S D to move and space to shoot. Player 2 uses arrow keys to move and enter to shoot."
        },
        {
            "title": "Final Mode Controls",
            "text": [
                "WASD: Move in 3D space",
                "Space: Jump",
                "F: Attack (with cooldown)",
                "G: Special attack (uses energy)",
                "",
                "Defeat 20 enemies to win!"
            ],
            "speech": "In Final Mode, use W A S D to move, space to jump, F to attack, and G for special attack. Defeat 20 enemies to win!"
        }
    ]
    
    page = 0
    speak_func(controls_pages[page]["speech"])
    
    while True:
        screen.fill((30, 30, 60))
        
        # Title
        title_font = pygame.font.Font(None, 64)
        title = title_font.render(controls_pages[page]["title"], True, (255, 255, 100))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # Text content
        text_font = pygame.font.Font(None, 48)
        y_offset = 250
        for line in controls_pages[page]["text"]:
            text = text_font.render(line, True, (200, 200, 200))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y_offset))
            y_offset += 60
        
        # Navigation hints
        hint_font = pygame.font.Font(None, 36)
        if page < len(controls_pages) - 1:
            next_hint = hint_font.render("Press → for next page", True, (150, 150, 150))
            screen.blit(next_hint, (WIDTH - next_hint.get_width() - 50, HEIGHT - 100))
        if page > 0:
            prev_hint = hint_font.render("Press ← for previous page", True, (150, 150, 150))
            screen.blit(prev_hint, (50, HEIGHT - 100))
        
        back_hint = hint_font.render("Press ESC to go back", True, (150, 150, 150))
        screen.blit(back_hint, (WIDTH//2 - back_hint.get_width()//2, HEIGHT - 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_RIGHT and page < len(controls_pages) - 1:
                    page += 1
                    speak_func(controls_pages[page]["speech"])
                if event.key == pygame.K_LEFT and page > 0:
                    page -= 1
                    speak_func(controls_pages[page]["speech"])


def show_mode_explanations(speak_func):
    """Show explanations of different game modes"""
    screen.fill((30, 30, 60))
    
    title_font = pygame.font.Font(None, 64)
    title = title_font.render("Game Modes", True, (255, 255, 100))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    
    modes = [
        "Battle Mode: Classic PvP combat!",
        "Coin Collection: Race to collect coins!",
        "Survival Mode: Fight endless waves!",
        "Final Mode: Epic 3D adventure!",
        "",
        "Unlock secret modes by exploring!"
    ]
    
    speak_func("Battle mode is classic player versus player. Coin collection is a race. Survival mode has endless waves. Final mode is an epic 3 D adventure!")
    
    text_font = pygame.font.Font(None, 42)
    y_offset = 200
    for mode in modes:
        text = text_font.render(mode, True, (200, 200, 200))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, y_offset))
        y_offset += 70
    
    hint_font = pygame.font.Font(None, 36)
    hint = hint_font.render("Press any key to return", True, (150, 150, 150))
    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 100))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return


def show_secret_hints(speak_func):
    """Give hints about secret codes"""
    screen.fill((20, 0, 40))
    
    title_font = pygame.font.Font(None, 64)
    title = title_font.render("🔐 Secret Hints 🔐", True, (255, 100, 255))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    
    hints = [
        "🐑 Try exploring different game modes...",
        "🎵 Music can lead to hidden paths...",
        "🐺 Sometimes things disappear, but can return...",
        "👤 Transformation is key to unlocking power...",
        "💥 The ultimate mode requires a special code...",
        "",
        "✨ Keep playing and experimenting! ✨"
    ]
    
    speak_func("Explore different modes. Music can lead to hidden paths. Transformation is key. Keep experimenting!")
    
    text_font = pygame.font.Font(None, 40)
    y_offset = 200
    for hint in hints:
        text = text_font.render(hint, True, (200, 150, 255))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, y_offset))
        y_offset += 65
    
    hint_font = pygame.font.Font(None, 36)
    hint = hint_font.render("Press any key to return", True, (150, 150, 150))
    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 100))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return


def show_github_help(speak_func):
    """Show GitHub Pages deployment help"""
    screen.fill((10, 30, 10))
    
    title_font = pygame.font.Font(None, 56)
    title = title_font.render("🌐 Put Your Game Online! 🌐", True, (100, 255, 100))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    
    steps = [
        "1. Check your game folder for these files:",
        "   • START_HERE.md (read this first!)",
        "   • deploy_to_github.sh (easy script)",
        "   • DEPLOYMENT_CHECKLIST.md (step by step)",
        "",
        "2. Run: ./deploy_to_github.sh",
        "",
        "3. Follow the prompts to create your",
        "   GitHub repository and enable Pages!",
        "",
        "4. Share your game with the world! 🎉"
    ]
    
    speak_func("Check your game folder for START HERE dot M D. Run the deploy to github script. Follow the prompts. Then share your game with the world!")
    
    text_font = pygame.font.Font(None, 32)
    y_offset = 180
    for step in steps:
        text = text_font.render(step, True, (200, 255, 200))
        screen.blit(text, (100, y_offset))
        y_offset += 45
    
    hint_font = pygame.font.Font(None, 36)
    hint = hint_font.render("Press any key to return", True, (150, 150, 150))
    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 100))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return


def show_general_tips(speak_func):
    """Show general gameplay tips"""
    screen.fill((40, 20, 0))
    
    title_font = pygame.font.Font(None, 64)
    title = title_font.render("💡 Pro Tips 💡", True, (255, 200, 100))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    
    tips = [
        "🎯 Practice makes perfect in Battle Mode!",
        "🏃 Movement is key - keep moving!",
        "🔫 Don't waste shots - aim carefully!",
        "🎵 Some game modes unlock through secrets!",
        "👥 Play with friends for maximum fun!",
        "🎮 Try all the different game modes!",
        "🌟 The shop has special unlockables!",
        "💪 Survival mode gets harder - stay alert!"
    ]
    
    speak_func("Practice makes perfect! Keep moving, aim carefully, and try all the game modes!")
    
    text_font = pygame.font.Font(None, 38)
    y_offset = 180
    for tip in tips:
        text = text_font.render(tip, True, (255, 220, 180))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, y_offset))
        y_offset += 60
    
    hint_font = pygame.font.Font(None, 36)
    hint = hint_font.render("Press any key to return", True, (150, 150, 150))
    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 100))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return


def change_ai_voice(speak_func):
    """Let user change the AI voice"""
    voices = ["Zarvox", "Cellos", "Trinoids", "Ralph", "Fred", "Albert", "Bad News", "Bahh", "Bells", "Boing", "Bubbles", "Deranged", "Good News", "Hysterical", "Pipe Organ", "Superstar", "Whisper", "Wobble", "Alex"]
    selected = 0
    
    speak_func("Choose a voice for me!")
    
    while True:
        screen.fill((40, 0, 40))
        
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("Choose AI Voice", True, (255, 100, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Show voices in a grid
        cols = 3
        x_start = 200
        y_start = 200
        cell_width = (WIDTH - 400) // cols
        cell_height = 60
        
        for i, voice in enumerate(voices):
            row = i // cols
            col = i % cols
            x = x_start + col * cell_width
            y = y_start + row * cell_height
            
            color = (255, 255, 100) if i == selected else (200, 200, 200)
            voice_font = pygame.font.Font(None, 36)
            voice_text = voice_font.render(voice, True, color)
            screen.blit(voice_text, (x, y))
        
        # Pointer
        selected_row = selected // cols
        selected_col = selected % cols
        pointer_x = x_start + selected_col * cell_width - 40
        pointer_y = y_start + selected_row * cell_height + 10
        pointer_font = pygame.font.Font(None, 48)
        pointer = pointer_font.render("➤", True, (255, 255, 100))
        screen.blit(pointer, (pointer_x, pointer_y))
        
        hint_font = pygame.font.Font(None, 36)
        hint = hint_font.render("Arrows to select, Enter to choose, T to test, ESC to cancel", True, (150, 150, 150))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 80))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if selected >= cols:
                        selected -= cols
                if event.key == pygame.K_DOWN:
                    if selected < len(voices) - cols:
                        selected += cols
                if event.key == pygame.K_LEFT:
                    selected = max(0, selected - 1)
                if event.key == pygame.K_RIGHT:
                    selected = min(len(voices) - 1, selected + 1)
                if event.key == pygame.K_t:
                    # Test the voice
                    speak_func(f"Hello! This is {voices[selected]}!", voice=voices[selected])
                if event.key == pygame.K_RETURN:
                    speak_func(f"Voice changed to {voices[selected]}!", voice=voices[selected])
                    return voices[selected]
                if event.key == pygame.K_ESCAPE:
                    speak_func("Keeping my current voice!")
                    return "Zarvox"


def tell_joke(speak_func):
    """Tell a random joke!"""
    jokes = [
        ("Why did the programmer quit his job?", "Because he didn't get arrays!"),
        ("What do you call a fake noodle?", "An impasta!"),
        ("Why don't scientists trust atoms?", "Because they make up everything!"),
        ("What did the ocean say to the beach?", "Nothing, it just waved!"),
        ("Why did the scarecrow win an award?", "Because he was outstanding in his field!"),
        ("What do you call a bear with no teeth?", "A gummy bear!"),
        ("Why did the bicycle fall over?", "Because it was two tired!"),
        ("What do you call a dog magician?", "A labracadabrador!"),
    ]
    
    joke = random.choice(jokes)
    setup, punchline = joke
    
    speak_func(setup)
    
    # Show setup
    screen.fill((0, 20, 40))
    setup_font = pygame.font.Font(None, 48)
    setup_text = setup_font.render(setup, True, (255, 255, 100))
    screen.blit(setup_text, (WIDTH//2 - setup_text.get_width()//2, HEIGHT//2 - 100))
    
    hint_font = pygame.font.Font(None, 36)
    hint = hint_font.render("Press any key for punchline...", True, (150, 150, 150))
    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 100))
    
    pygame.display.flip()
    
    # Wait for key
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
    
    # Show punchline
    speak_func(punchline)
    pygame.time.wait(500)
    
    screen.fill((0, 20, 40))
    screen.blit(setup_text, (WIDTH//2 - setup_text.get_width()//2, HEIGHT//2 - 150))
    
    punchline_font = pygame.font.Font(None, 56)
    punchline_text = punchline_font.render(punchline, True, (100, 255, 100))
    screen.blit(punchline_text, (WIDTH//2 - punchline_text.get_width()//2, HEIGHT//2 - 50))
    
    laugh_font = pygame.font.Font(None, 72)
    laugh = laugh_font.render("😂 Ha Ha Ha! 😂", True, (255, 200, 100))
    screen.blit(laugh, (WIDTH//2 - laugh.get_width()//2, HEIGHT//2 + 80))
    
    hint = hint_font.render("Press any key to return", True, (150, 150, 150))
    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 100))
    
    pygame.display.flip()
    
    # Wait to return
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return


def mode_lobby():
    global session_purchases
    selected = 0
    base_options = ["🤖 AI Helper", "🧠 Quiz Mode", "Battle Mode", "Coin Collection Mode", "Makka Pakka Mode", "Escape Mom Mode", "Capture the Flag", "Survival Mode", "3D Adventure", "Relax Mode", "Dilly Dolly Mode", "🛒 Shop", "Survival Leaderboard", "Mom Mode Leaderboard", "Play Music", "Stop Music", "Watch Cute Video", "Watch Grandma", "Exit"]
    music_playing = False
    
    # Pointer animation
    pointer_frame = 0
    pointer_bob = 0
    
    # Don't stop music if hack sequence is active (music should persist)
    if not secret_hack.get('music_still_playing'):
        pygame.mixer.music.stop()  # Ensure no music plays automatically
    
    while True:
        # Check if user has become human in Combine Mode (check every frame!)
        # This ensures it updates immediately when returning from Combine Mode
        pointer_is_human = secret_hack.get('became_human', False)
        
        # Build options list dynamically based on hack progress
        options = base_options.copy()
        
        # WOLF ATE EVERYTHING - Remove ALL options except Exit (unless restored)
        if secret_hack.get('wolf_ate_buttons') and not secret_hack.get('everything_restored'):
            # Start with empty menu - only Exit remains
            options = ["Exit"]
            
            # Add back ONLY Grass Mode if unlocked
            if secret_hack.get('grass_mode_unlocked'):
                options.insert(0, "Grass Mode")
            
            # Add back ONLY Combine Mode if unlocked
            if secret_hack.get('combine_mode_unlocked'):
                options.insert(0, "Combine Mode")
            
            # Add FINAL MODE if unlocked (most powerful!)
            if secret_hack.get('final_mode_unlocked'):
                options.insert(0, "🔥 FINAL MODE 🔥")
        else:
            # Normal menu (or restored) - add Grass and Combine if unlocked
            # Add Grass Mode if unlocked
            if secret_hack.get('grass_mode_unlocked'):
                # Insert Grass Mode before the Shop
                shop_index = options.index("🛒 Shop")
                options.insert(shop_index, "Grass Mode")
            
            # Add Combine Mode if unlocked
            if secret_hack.get('combine_mode_unlocked'):
                # Insert Combine Mode before the Shop
                shop_index = options.index("🛒 Shop")
                options.insert(shop_index, "Combine Mode")
            
            # Add FINAL MODE if unlocked (insert at top!)
            if secret_hack.get('final_mode_unlocked'):
                options.insert(0, "🔥 FINAL MODE 🔥")
        
        # Check which modes are purchased THIS SESSION
        relax_unlocked = session_purchases.get('relax_mode', False)
        makka_pakka_unlocked = session_purchases.get('makka_pakka_mode', False)
        escape_mom_unlocked = session_purchases.get('escape_mom_mode', False)
        capture_flag_unlocked = session_purchases.get('capture_flag_mode', False)
        survival_unlocked = session_purchases.get('survival_mode', False)
        adventure_3d_unlocked = session_purchases.get('adventure_3d_mode', False)
        dilly_dolly_unlocked = session_purchases.get('dilly_dolly_mode', False)
        shop_unlocked = session_purchases.get('shop_unlocked', False)
        
        screen.fill((30, 30, 30))
        # Smaller title font
        small_lobby_font = pygame.font.Font(None, 48)
        title = small_lobby_font.render("Choose Game Mode", True, (255,255,255))
        screen.blit(title, (WIDTH//2-title.get_width()//2, 30))
        
        # Update pointer animation
        pointer_frame += 0.1
        pointer_bob = math.sin(pointer_frame) * 5  # Bobbing up and down
        
        # Show wolf ate everything warning
        if secret_hack.get('wolf_ate_buttons'):
            small_font = pygame.font.Font(None, 28)
            warning = small_font.render("The wolf ate EVERYTHING!", True, (255, 0, 0))
            screen.blit(warning, (WIDTH//2-warning.get_width()//2, 5))
            if not secret_hack.get('grass_mode_unlocked'):
                tiny_font = pygame.font.Font(None, 20)
                hint = tiny_font.render("(The entire menu is gone... only Exit remains)", True, (150, 150, 150))
                screen.blit(hint, (WIDTH//2-hint.get_width()//2, 25))
        
        # Show shop status hint (only if wolf hasn't eaten everything)
        if shop_unlocked and not secret_hack.get('wolf_ate_buttons'):
            small_font = pygame.font.Font(None, 28)
            shop_hint = small_font.render("🔑 Secret shop unlocked!", True, (255, 215, 0))
            screen.blit(shop_hint, (10, 5))
        
        # Show transformation status if became human
        if pointer_is_human:
            tiny_font = pygame.font.Font(None, 20)
            human_status = tiny_font.render("✨ You became HUMAN! ✨", True, (255, 215, 0))
            screen.blit(human_status, (WIDTH - human_status.get_width() - 10, 5))
        
        # Free modes list
        free_modes = ["🤖 AI Helper", "🧠 Quiz Mode", "Battle Mode", "Coin Collection Mode", "🛒 Shop", "Survival Leaderboard", 
                      "Mom Mode Leaderboard", "Play Music", "Stop Music", "Watch Cute Video", 
                      "Watch Grandma", "Exit"]
        
        # Smaller menu option font
        menu_font = pygame.font.Font(None, 32)
        
        for i, opt in enumerate(options):
            # Check if mode is locked (needs purchase from shop)
            is_locked = False
            is_unlocked = False
            
            if opt == "Relax Mode":
                is_locked = not relax_unlocked
                is_unlocked = relax_unlocked
            elif opt == "Makka Pakka Mode":
                is_locked = not makka_pakka_unlocked
                is_unlocked = makka_pakka_unlocked
            elif opt == "Escape Mom Mode":
                is_locked = not escape_mom_unlocked
                is_unlocked = escape_mom_unlocked
            elif opt == "Capture the Flag":
                is_locked = not capture_flag_unlocked
                is_unlocked = capture_flag_unlocked
            elif opt == "Survival Mode":
                is_locked = not survival_unlocked
                is_unlocked = survival_unlocked
            elif opt == "3D Adventure":
                is_locked = not adventure_3d_unlocked
                is_unlocked = adventure_3d_unlocked
            elif opt == "Dilly Dolly Mode":
                is_locked = not dilly_dolly_unlocked
                is_unlocked = dilly_dolly_unlocked
            
            # Display mode with lock/unlock status
            if is_locked:
                color = (100,100,100) if i!=selected else (150,150,150)
                opt_text = menu_font.render(opt + " 🔒", True, color)
            elif is_unlocked:
                color = (255,255,0) if i==selected else (200,200,200)
                opt_text = menu_font.render(opt + " ✅", True, color)
            else:
                # Free mode
                color = (255,255,0) if i==selected else (200,200,200)
                opt_text = menu_font.render(opt, True, color)
            
            # Smaller spacing between options (35 instead of 50)
            screen.blit(opt_text, (WIDTH//2-opt_text.get_width()//2, 70+i*35))
        
        # Draw the dog/human pointer pointing at the selected option!
        pointer_y = 70 + selected * 35 + pointer_bob
        pointer_x = WIDTH//2 - 200  # Left side of the screen
        
        # Determine transformation level for pointer (0-100)
        # If human: 100, if dog: 0
        pointer_transformation = 100 if pointer_is_human else 0
        
        # Draw the pointer character (reusing draw_character from Combine Mode)
        # Scale it down a bit for the menu
        draw_menu_pointer(screen, pointer_x, pointer_y, pointer_transformation, 1, pointer_frame, True)
        
        # Add a pointing arrow/hand
        if pointer_is_human:
            # Human pointing finger
            pointer_emoji_font = pygame.font.Font(None, 60)
            pointing = pointer_emoji_font.render("👉", True, (255, 255, 255))
            screen.blit(pointing, (pointer_x + 50, int(pointer_y - 5)))
        else:
            # Dog paw pointing
            pointer_emoji_font = pygame.font.Font(None, 60)
            pointing = pointer_emoji_font.render("🐾", True, (255, 200, 150))
            screen.blit(pointing, (pointer_x + 50, int(pointer_y)))
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # HACK SEQUENCE: Detect jjj, qqq, 67, 6776, 123654, and gagabubu in main menu
                global menu_key_buffer
                key_name = pygame.key.name(event.key)
                
                # Track j, q, 6, 7, g, a, b, u, and number presses
                if key_name in ['j', 'q', '1', '2', '3', '4', '5', '6', '7', 'g', 'a', 'b', 'u', 'r', 'v', 'i', 'n']:
                    menu_key_buffer += key_name
                    # Keep only last 8 characters (for gagabubu)
                    if len(menu_key_buffer) > 8:
                        menu_key_buffer = menu_key_buffer[-8:]
                    
                    # Check for gagabubu - RAINBOW EXPLOSION!
                    if menu_key_buffer[-8:] == "gagabubu":
                        menu_key_buffer = ""
                        rainbow_explosion()
                        continue
                    
                    # Check for 6776 - FINAL MODE EXPLOSION! (only after becoming Tralala)
                    if menu_key_buffer[-4:] == "6776" and secret_hack.get('became_italian') and not secret_hack.get('final_mode_unlocked'):
                        secret_hack['explosion_triggered'] = True
                        secret_hack['final_mode_unlocked'] = True
                        menu_key_buffer = ""
                        # EPIC EXPLOSION SEQUENCE!
                        explosion_sequence(screen)
                        continue
                        
                    # Check for 'arvin' - SECRET CREDITS SEQUENCE (only if Final Mode unlocked)
                    if menu_key_buffer[-5:] == "arvin" and secret_hack.get('final_mode_unlocked'):
                        menu_key_buffer = ""
                        credits_sequence(screen)
                        # After credits, unlock AND TRIGGER the post-credits scene
                        secret_hack['post_credits_scene_unlocked'] = True
                        
                        # Loop the post-credits scene so we stay there unless user explicitly quits
                        while True:
                            action = post_credits_scene(screen)
                            if action == 'escape':
                                break
                            # If action is 'jumpscare' or anything else, we restart the loop
                        
                        continue
                    
                    # Check for 67 - TRALALA MODE! (only works if human)
                    if menu_key_buffer[-2:] == "67" and secret_hack.get('became_human') and not secret_hack.get('became_italian'):
                        secret_hack['became_italian'] = True
                        menu_key_buffer = ""
                        continue
                    
                    # Check for 123654 - restore everything
                    if menu_key_buffer == "123654" and secret_hack.get('wolf_ate_buttons'):
                        secret_hack['wolf_ate_buttons'] = False
                        secret_hack['everything_restored'] = True
                        # Show restoration message
                        screen.fill((0, 0, 0))
                        restore_font = pygame.font.Font(None, 100)
                        restore_text = restore_font.render("RESTORED!", True, (0, 255, 0))
                        screen.blit(restore_text, (WIDTH//2 - restore_text.get_width()//2, HEIGHT//2 - 50))
                        msg = font.render("Everything has been restored!", True, (255, 255, 255))
                        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 + 50))
                        pygame.display.flip()
                        pygame.time.wait(2000)
                        menu_key_buffer = ""
                        continue
                    
                    # Check for jjj - wolf eats all buttons
                    if menu_key_buffer[-3:] == "jjj" and secret_hack.get('skibidi_triggered') and not secret_hack.get('wolf_ate_buttons'):
                        secret_hack['wolf_ate_buttons'] = True
                        # Show wolf eating animation
                        wolf_eat_animation()
                        continue
                    
                    # Check for qqq - wolf vomits Grass Mode
                    if menu_key_buffer[-3:] == "qqq" and secret_hack.get('wolf_ate_buttons') and not secret_hack.get('grass_mode_unlocked'):
                        secret_hack['grass_mode_unlocked'] = True
                        # Show wolf vomit animation
                        wolf_vomit_animation("Grass Mode")
                        menu_key_buffer = ""
                        continue
                else:
                    # Reset buffer if other key pressed (but allow navigation)
                    if event.key not in [pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN, pygame.K_ESCAPE]:
                        menu_key_buffer = ""
                
                # No shortcuts! Must use the secret hunt in the shop menu
                
                if event.key == pygame.K_UP:
                    selected = (selected-1)%len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected+1)%len(options)
                if event.key == pygame.K_RETURN:
                    if options[selected] == "Exit":
                        pygame.quit()
                        sys.exit()
                    elif options[selected] == "🤖 AI Helper":
                        ai_helper()
                    elif options[selected] == "🧠 Quiz Mode":
                        quiz_mode()
                    elif options[selected] == "🔥 FINAL MODE 🔥":
                        final_mode()
                    elif options[selected] == "Grass Mode":
                        grass_mode()
                    elif options[selected] == "Combine Mode":
                        combine_mode()
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
                    elif options[selected] == "🛒 Shop":
                        shop_menu()
                    elif options[selected] == "Relax Mode":
                        if relax_unlocked:
                            relax_mode()
                        else:
                            show_locked_message()
                    elif options[selected] == "Dilly Dolly Mode":
                        if dilly_dolly_unlocked:
                            dilly_dolly_mode()
                        else:
                            show_locked_message()
                    elif options[selected] == "3D Adventure":
                        if adventure_3d_unlocked:
                            adventure_3d_mode()
                        else:
                            show_locked_message()
                    else:
                        # Don't stop music if hack sequence is active
                        if not secret_hack.get('music_still_playing'):
                            pygame.mixer.music.stop()
                        if options[selected] == "Battle Mode":
                            return 0
                        elif options[selected] == "Coin Collection Mode":
                            return 1
                        elif options[selected] == "Makka Pakka Mode":
                            if makka_pakka_unlocked:
                                return 3
                            else:
                                show_locked_message()
                        elif options[selected] == "Escape Mom Mode":
                            if escape_mom_unlocked:
                                return 4
                            else:
                                show_locked_message()
                        elif options[selected] == "Capture the Flag":
                            if capture_flag_unlocked:
                                return 5
                            else:
                                show_locked_message()
                        elif options[selected] == "Survival Mode":
                            if survival_unlocked:
                                return 2
                            else:
                                show_locked_message()

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
    elif choice == 'satisfaction':
        try:
            ultimate_satisfaction_mode()
        except Exception as e:
            print(f"ERROR in Ultimate Satisfaction mode: {e}")
            import traceback
            traceback.print_exc()

def relax_mode_menu():
    """Menu to select which relax mode to play"""
    clock = pygame.time.Clock()
    selected = 0
    options = ['Letter Rain', 'Counting Sheep', 'Ultimate Satisfaction', 'Back']
    
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
                    elif selected == 2:
                        return 'satisfaction'
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
            
            # Sample points from the letter surface with better distribution
            width = text.get_width()
            height = text.get_height()
            
            # Grid-based sampling for more even distribution
            for x in range(0, width, 2):  # Finer sampling (was 3)
                for y in range(0, height, 2):  # Finer sampling (was 3)
                    try:
                        pixel = text.get_at((x, y))
                        if pixel[3] > 128:  # Alpha > 128 means visible
                            # Add some randomness to avoid perfect grid
                            jitter_x = random.uniform(-1.0, 1.0)
                            jitter_y = random.uniform(-1.0, 1.0)
                            # Position relative to center
                            world_x = center_x - width//2 + x + jitter_x
                            world_y = center_y - height//2 + y + jitter_y
                            points.append((world_x, world_y))
                    except:
                        pass
    except Exception as e:
        print(f"Error creating letter formation: {e}")
    
    # Shuffle points so they don't form in order
    random.shuffle(points)
    
    # If we didn't get enough points, something went wrong
    if len(points) < 20:
        print(f"Warning: Only got {len(points)} points for letter {letter}")
        # Fallback: create a simple pattern
        for i in range(100):
            angle = (i / 100) * 2 * math.pi
            radius = size * 0.3
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
    global secret_hack
    
    # Mark that player entered sheep mode
    secret_hack['sheep_mode_played'] = True
    
    clock = pygame.time.Clock()
    
    # Sheep state
    sheep_list = []
    count = 0
    spawn_timer = 0
    spawn_interval = 2.5  # Seconds between sheep
    animation_time = 0
    
    # Cheat code state
    cheat_input = ""
    infinity_mode = False
    stampede_mode = False  # Sheep stampede mode!
    
    # Wolf state
    wolf_active = False
    wolf_x = -200
    wolf_speed = 400
    eaten_sheep = []  # Track eaten sheep with heads falling off
    falling_heads = []  # Separate list for falling heads
    wolf_dead = False
    wolf_death_time = 0
    wolf_dancing = False  # Gangnam Style mode!
    wolf_dance_time = 0
    wolf_dance_y_offset = 0
    gangnam_music_playing = False  # Track if music is playing
    
    # Hunter state
    hunter_active = False
    hunter_x = WIDTH + 200
    hunter_speed = 300
    hunter_shooting = False
    bullet_x = 0
    bullet_y = 0
    bullet_active = False
    bullet_speed = 800
    
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
        if stampede_mode:
            # STAMPEDE! ULTIMATE MAXIMUM SHEEP OVERLOAD!!!
            spawn_check = 0.001  # HYPER MEGA ULTRA fast spawning (1000 spawn events per second!)
            if spawn_timer >= spawn_check:
                spawn_timer = 0
                # Spawn 100 sheep at a time for MAXIMUM CHAOS!!!
                for _ in range(100):
                    count += 1
                    # Random vertical position for stampede effect (running on top of each other)
                    y_offset = random.randint(-150, 150)  # ENORMOUS vertical spread
                    sheep_list.append({
                        'x': -150 + random.randint(-100, 100),  # MASSIVE horizontal variation
                        'y': fence_y + 80 + y_offset,  # Random height!
                        'jump_phase': 2,  # Skip jumping, just run!
                        'target_y': fence_y + 80 + y_offset,
                        'speed': random.randint(100, 600),  # INSANE speed variation
                        'num': count,
                        'leg_phase': random.uniform(0, math.pi * 2),
                        'body_bob': 0,
                        'rotation': 0,
                        'stampede_y': y_offset  # Remember the offset
                    })
        else:
            spawn_check = spawn_interval if not infinity_mode else 0.1  # Fast spawn in infinity mode
            if spawn_timer >= spawn_check:
                spawn_timer = 0
                count += 1
                sheep_list.append({
                    'x': -80,
                    'y': fence_y + 80,  # Start on ground
                    'jump_phase': 0,  # 0=walking, 1=jumping, 2=landed
                    'target_y': fence_y + 80,
                    'speed': 120 if not infinity_mode else 200,  # Faster in infinity mode
                    'num': count,
                    'leg_phase': random.uniform(0, math.pi * 2),  # For walking animation
                    'body_bob': 0,  # Bobbing up and down while walking
                    'rotation': 0  # For mid-air rotation
                })
        
        # Update and draw sheep
        for sheep in sheep_list[:]:
            # Check if wolf caught this sheep (only if wolf is not dancing!)
            if wolf_active and not wolf_dancing and abs(wolf_x - sheep['x']) < 60 and not any(e['sheep'] == sheep for e in eaten_sheep):
                # Wolf eats the sheep's head!
                eaten_sheep.append({
                    'sheep': sheep,
                    'time': animation_time,
                    'blood_x': sheep['x'],
                    'blood_y': sheep['y'] - 20,
                    'body_x': sheep['x'],
                    'body_y': sheep['y']
                })
                # Create falling head
                falling_heads.append({
                    'x': sheep['x'],
                    'y': sheep['y'] - 20,
                    'vx': random.uniform(-50, 50),
                    'vy': -80,  # Launch upward
                    'rotation': 0,
                    'rot_speed': random.uniform(-360, 360),
                    'time': animation_time
                })
                # Stop the sheep from moving
                sheep['speed'] = 0
            
            # Only move if not eaten
            is_eaten = any(e['sheep'] == sheep for e in eaten_sheep)
            if not is_eaten:
                sheep['x'] += sheep['speed'] * dt
            
            # Walking leg animation (always animate in stampede mode)
            if sheep['jump_phase'] == 0 or sheep['jump_phase'] == 2 or stampede_mode:
                sheep['leg_phase'] += 8 * dt
                sheep['body_bob'] = 2 * math.sin(sheep['leg_phase'] * 2)
            
            # Jumping animation (skip in stampede mode - just run straight!)
            if not stampede_mode:
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
        
        # Update and draw wolf
        if wolf_active and not wolf_dead:
            # Dancing mode!
            if wolf_dancing:
                wolf_dance_time += dt
                # Wolf stays in center and dances
                wolf_x = WIDTH // 2
                
                # Real Gangnam Style dance sequence (repeats every 8 seconds)
                beat = wolf_dance_time * 2  # Tempo
                cycle = (wolf_dance_time % 8) / 8  # 0 to 1 for full cycle
                
                # Determine dance move based on cycle
                if cycle < 0.25:  # Horse riding move (iconic!)
                    wolf_dance_y_offset = 8 * abs(math.sin(beat * 4))  # Small bounce
                    left_arm_angle = -45 + 15 * math.sin(beat * 4)  # Holding reins
                    right_arm_angle = -45 + 15 * math.sin(beat * 4 + math.pi)
                    left_leg_angle = 10 * math.sin(beat * 4)
                    right_leg_angle = 10 * math.sin(beat * 4 + math.pi)
                    move_name = "HORSE RIDE!"
                elif cycle < 0.5:  # Lasso move
                    wolf_dance_y_offset = 5
                    left_arm_angle = -90 - 30 * math.sin(beat * 8)  # Arm up rotating
                    right_arm_angle = 0
                    left_leg_angle = 0
                    right_leg_angle = 0
                    move_name = "LASSO!"
                elif cycle < 0.75:  # Jumping and clapping
                    wolf_dance_y_offset = 20 * abs(math.sin(beat * 4))  # Big jump
                    left_arm_angle = -120 if abs(math.sin(beat * 4)) > 0.7 else -30
                    right_arm_angle = -120 if abs(math.sin(beat * 4)) > 0.7 else -30
                    left_leg_angle = 0
                    right_leg_angle = 0
                    move_name = "JUMP & CLAP!"
                else:  # Sexy walk/strut
                    wolf_dance_y_offset = 3 * abs(math.sin(beat * 2))
                    left_arm_angle = 20 * math.sin(beat * 2)
                    right_arm_angle = 20 * math.sin(beat * 2 + math.pi)
                    left_leg_angle = 15 * math.sin(beat * 2)
                    right_leg_angle = 15 * math.sin(beat * 2 + math.pi)
                    move_name = "STRUT!"
                
                wolf_y = fence_y + 60 - wolf_dance_y_offset
                
                # Body (bouncing)
                pygame.draw.ellipse(screen, (60, 60, 60), (wolf_x - 30, wolf_y, 80, 40))
                
                # Head (bobbing to the beat)
                head_bob = 3 * math.sin(beat * 4)
                pygame.draw.circle(screen, (50, 50, 50), (wolf_x + 30, wolf_y + 10 + head_bob), 25)
                
                # Snout
                pygame.draw.ellipse(screen, (70, 70, 70), (wolf_x + 40, wolf_y + 15 + head_bob, 25, 15))
                
                # Happy eyes (not evil!) with sunglasses
                pygame.draw.rect(screen, (20, 20, 20), (wolf_x + 20, wolf_y + 3 + head_bob, 25, 12))
                pygame.draw.line(screen, (20, 20, 20), (wolf_x + 20, wolf_y + 9 + head_bob), (wolf_x + 15, wolf_y + 9 + head_bob), 3)
                pygame.draw.line(screen, (20, 20, 20), (wolf_x + 45, wolf_y + 9 + head_bob), (wolf_x + 50, wolf_y + 9 + head_bob), 3)
                
                # Smiling mouth
                pygame.draw.arc(screen, (255, 255, 255), (wolf_x + 35, wolf_y + 18 + head_bob, 20, 10), 3.14, 0, 2)
                
                # Ears (bouncing)
                pygame.draw.polygon(screen, (50, 50, 50), [
                    (wolf_x + 15, wolf_y - 5 + head_bob),
                    (wolf_x + 20, wolf_y - 15 + head_bob),
                    (wolf_x + 25, wolf_y - 5 + head_bob)
                ])
                pygame.draw.polygon(screen, (50, 50, 50), [
                    (wolf_x + 30, wolf_y - 5 + head_bob),
                    (wolf_x + 35, wolf_y - 15 + head_bob),
                    (wolf_x + 40, wolf_y - 5 + head_bob)
                ])
                
                # Dancing legs with real moves!
                left_leg_end_x = wolf_x - 10 + left_leg_angle
                right_leg_end_x = wolf_x + 10 + right_leg_angle
                pygame.draw.line(screen, (60, 60, 60), (wolf_x - 10, wolf_y + 35), (left_leg_end_x, wolf_y + 60), 8)
                pygame.draw.line(screen, (60, 60, 60), (wolf_x + 10, wolf_y + 35), (right_leg_end_x, wolf_y + 60), 8)
                # Feet
                pygame.draw.circle(screen, (40, 40, 40), (int(left_leg_end_x), wolf_y + 60), 5)
                pygame.draw.circle(screen, (40, 40, 40), (int(right_leg_end_x), wolf_y + 60), 5)
                
                # Dancing arms with real Gangnam Style moves!
                left_arm_rad = math.radians(left_arm_angle)
                right_arm_rad = math.radians(right_arm_angle)
                left_arm_end_x = wolf_x - 25 + 40 * math.cos(left_arm_rad + math.pi)
                left_arm_end_y = wolf_y + 15 + 40 * math.sin(left_arm_rad + math.pi)
                right_arm_end_x = wolf_x + 25 + 40 * math.cos(right_arm_rad)
                right_arm_end_y = wolf_y + 15 + 40 * math.sin(right_arm_rad)
                pygame.draw.line(screen, (60, 60, 60), (wolf_x - 25, wolf_y + 15), (int(left_arm_end_x), int(left_arm_end_y)), 6)
                pygame.draw.line(screen, (60, 60, 60), (wolf_x + 25, wolf_y + 15), (int(right_arm_end_x), int(right_arm_end_y)), 6)
                # Hands
                pygame.draw.circle(screen, (50, 50, 50), (int(left_arm_end_x), int(left_arm_end_y)), 6)
                pygame.draw.circle(screen, (50, 50, 50), (int(right_arm_end_x), int(right_arm_end_y)), 6)
                
                # Tail wagging super fast!
                tail_wag = 25 * math.sin(beat * 10)
                pygame.draw.line(screen, (60, 60, 60), (wolf_x - 30, wolf_y + 15), 
                               (wolf_x - 50, wolf_y + tail_wag), 5)
                
                # Draw current dance move name
                move_font = pygame.font.SysFont(None, 40)
                move_text = move_font.render(move_name, True, (255, 100, 255))
                screen.blit(move_text, (wolf_x - move_text.get_width()//2, wolf_y - 60))
                
                # Draw "GANGNAM STYLE!" title with pulsing effect
                pulse = int(70 + 20 * abs(math.sin(beat * 2)))
                gangnam_font = pygame.font.SysFont(None, pulse)
                gangnam_text = gangnam_font.render("♫ GANGNAM STYLE! ♫", True, (255, 215, 0))
                screen.blit(gangnam_text, (wolf_x - gangnam_text.get_width()//2, wolf_y - 110))
                
                # Draw beat indicator
                if int(beat * 2) % 2 == 0:  # Flash on beat
                    beat_text = lobby_font.render("🎵", True, (255, 100, 255))
                    screen.blit(beat_text, (wolf_x - 60, wolf_y - 30))
                    screen.blit(beat_text, (wolf_x + 40, wolf_y - 30))
                
            else:
                # Normal wolf behavior
                wolf_x += wolf_speed * dt
                
                # Check if bullet hit wolf
                if bullet_active and abs(bullet_x - wolf_x) < 40 and abs(bullet_y - (fence_y + 60)) < 30:
                    wolf_dead = True
                    wolf_death_time = animation_time
                    bullet_active = False
                    # Blood splatter from wolf
                    for _ in range(30):
                        angle = random.uniform(0, 2 * math.pi)
                        dist = random.uniform(10, 50)
                        bx = int(wolf_x + math.cos(angle) * dist)
                        by = int(fence_y + 60 + math.sin(angle) * dist)
                
                # Draw scary wolf
                wolf_y = fence_y + 60
                # Body
                pygame.draw.ellipse(screen, (60, 60, 60), (wolf_x - 30, wolf_y, 80, 40))
                # Head
                pygame.draw.circle(screen, (50, 50, 50), (wolf_x + 30, wolf_y + 10), 25)
                # Snout
                pygame.draw.ellipse(screen, (70, 70, 70), (wolf_x + 40, wolf_y + 15, 25, 15))
                # Evil red eyes
                pygame.draw.circle(screen, (255, 0, 0), (wolf_x + 25, wolf_y + 5), 5)
                pygame.draw.circle(screen, (255, 0, 0), (wolf_x + 35, wolf_y + 5), 5)
                # Sharp teeth
                for i in range(4):
                    tooth_x = wolf_x + 45 + i * 5
                    pygame.draw.polygon(screen, (255, 255, 255), [
                        (tooth_x, wolf_y + 20),
                        (tooth_x + 2, wolf_y + 20),
                        (tooth_x + 1, wolf_y + 26)
                    ])
                # Ears (pointed)
                pygame.draw.polygon(screen, (50, 50, 50), [
                    (wolf_x + 15, wolf_y - 5),
                    (wolf_x + 20, wolf_y - 15),
                    (wolf_x + 25, wolf_y - 5)
                ])
                pygame.draw.polygon(screen, (50, 50, 50), [
                    (wolf_x + 30, wolf_y - 5),
                    (wolf_x + 35, wolf_y - 15),
                    (wolf_x + 40, wolf_y - 5)
                ])
                # Legs
                pygame.draw.rect(screen, (60, 60, 60), (wolf_x - 10, wolf_y + 35, 8, 25))
                pygame.draw.rect(screen, (60, 60, 60), (wolf_x + 10, wolf_y + 35, 8, 25))
                pygame.draw.rect(screen, (60, 60, 60), (wolf_x + 30, wolf_y + 35, 8, 25))
                # Tail
                tail_wag = 10 * math.sin(animation_time * 10)
                pygame.draw.line(screen, (60, 60, 60), (wolf_x - 30, wolf_y + 15), 
                               (wolf_x - 50, wolf_y + tail_wag), 5)
                
                # Wolf runs off screen
                if wolf_x > WIDTH + 100:
                    wolf_active = False
                    wolf_x = -200
        
        # Draw dead wolf
        if wolf_dead:
            time_since_death = animation_time - wolf_death_time
            if time_since_death < 3.0:  # Show for 3 seconds
                wolf_y = fence_y + 60
                # Draw wolf lying down (dead)
                pygame.draw.ellipse(screen, (60, 60, 60), (wolf_x - 40, wolf_y + 20, 80, 30))
                # Head on ground
                pygame.draw.circle(screen, (50, 50, 50), (wolf_x + 40, wolf_y + 30), 20)
                # X_X dead eyes
                pygame.draw.line(screen, (255, 255, 255), (wolf_x + 33, wolf_y + 25), (wolf_x + 37, wolf_y + 29), 2)
                pygame.draw.line(screen, (255, 255, 255), (wolf_x + 37, wolf_y + 25), (wolf_x + 33, wolf_y + 29), 2)
                pygame.draw.line(screen, (255, 255, 255), (wolf_x + 43, wolf_y + 25), (wolf_x + 47, wolf_y + 29), 2)
                pygame.draw.line(screen, (255, 255, 255), (wolf_x + 47, wolf_y + 25), (wolf_x + 43, wolf_y + 29), 2)
                # Blood pool
                pygame.draw.ellipse(screen, (150, 0, 0), (wolf_x - 50, wolf_y + 45, 120, 20))
            else:
                wolf_dead = False
                wolf_active = False
                wolf_x = -200
        
        # Update and draw hunter
        if hunter_active:
            # Hunter runs from right to left
            hunter_x -= hunter_speed * dt
            hunter_y = fence_y + 50
            
            # Draw hunter (running pose)
            # Body (green jacket)
            pygame.draw.rect(screen, (40, 100, 40), (hunter_x - 15, hunter_y, 30, 50))
            # Head
            pygame.draw.circle(screen, (220, 180, 150), (hunter_x, hunter_y - 10), 15)
            # Hat
            pygame.draw.rect(screen, (100, 70, 40), (hunter_x - 18, hunter_y - 15, 36, 8))
            pygame.draw.ellipse(screen, (80, 50, 20), (hunter_x - 12, hunter_y - 25, 24, 12))
            # Eyes (determined)
            pygame.draw.circle(screen, (0, 0, 0), (hunter_x - 5, hunter_y - 12), 2)
            pygame.draw.circle(screen, (0, 0, 0), (hunter_x + 5, hunter_y - 12), 2)
            # Rifle
            rifle_angle = -20
            rifle_x = hunter_x - 25
            rifle_y = hunter_y + 15
            # Draw rifle pointing left
            pygame.draw.rect(screen, (80, 60, 40), (rifle_x - 40, rifle_y, 45, 6))
            pygame.draw.rect(screen, (40, 40, 40), (rifle_x - 50, rifle_y + 2, 15, 2))  # Barrel
            # Legs (running)
            leg_swing = 15 * math.sin(animation_time * 10)
            pygame.draw.line(screen, (40, 40, 100), (hunter_x - 8, hunter_y + 48), (hunter_x - 8, hunter_y + 70 + leg_swing), 6)
            pygame.draw.line(screen, (40, 40, 100), (hunter_x + 8, hunter_y + 48), (hunter_x + 8, hunter_y + 70 - leg_swing), 6)
            
            # Shoot at wolf when in range
            if wolf_active and not wolf_dead and not bullet_active and hunter_x - wolf_x < 400 and hunter_x - wolf_x > 100:
                bullet_active = True
                bullet_x = hunter_x - 50
                bullet_y = hunter_y + 15
                hunter_shooting = True
            
            # Hunter leaves when done
            if hunter_x < -100 or (wolf_dead and animation_time - wolf_death_time > 1.0):
                hunter_active = False
                hunter_x = WIDTH + 200
        
        # Update and draw bullet
        if bullet_active:
            bullet_x -= bullet_speed * dt
            # Draw bullet
            pygame.draw.circle(screen, (255, 255, 100), (int(bullet_x), int(bullet_y)), 4)
            pygame.draw.circle(screen, (255, 200, 0), (int(bullet_x), int(bullet_y)), 2)
            # Remove bullet if off screen
            if bullet_x < 0:
                bullet_active = False
        
        # Draw blood effects and headless sheep bodies
        for eaten in eaten_sheep[:]:
            time_since_eaten = animation_time - eaten['time']
            
            # Remove after 1 second
            if time_since_eaten > 1.0:
                eaten_sheep.remove(eaten)
                # Also remove the sheep from the main list
                if eaten['sheep'] in sheep_list:
                    sheep_list.remove(eaten['sheep'])
                continue
            
            # Blood splatter
            if time_since_eaten < 0.5:  # Show blood for 0.5 seconds
                alpha = int(255 * (1 - time_since_eaten / 0.5))
                for i in range(15):
                    angle = random.uniform(0, 2 * math.pi)
                    dist = random.uniform(10, 40)
                    bx = int(eaten['blood_x'] + math.cos(angle) * dist)
                    by = int(eaten['blood_y'] + math.sin(angle) * dist)
                    size = random.randint(2, 6)
                    pygame.draw.circle(screen, (180, 0, 0), (bx, by), size)
            
            # Draw headless sheep body (not moving)
            sheep = eaten['sheep']
            body_x = int(eaten['body_x'])
            body_y = int(eaten['body_y'] + sheep['body_bob'])
            
            # Body (wool)
            pygame.draw.ellipse(screen, (245, 245, 240), (body_x - 25, body_y - 15, 50, 35))
            # Neck stump with blood
            pygame.draw.circle(screen, (150, 0, 0), (body_x + 15, body_y - 15), 8)
            pygame.draw.circle(screen, (200, 0, 0), (body_x + 15, body_y - 15), 6)
            
            # Legs
            for i, leg_x in enumerate([body_x - 15, body_x - 5, body_x + 5, body_x + 15]):
                pygame.draw.line(screen, (35, 30, 30), (leg_x, body_y + 15), (leg_x, body_y + 35), 4)
        
        # Update and draw falling heads
        for head in falling_heads[:]:
            time_alive = animation_time - head['time']
            
            # Remove after 1 second
            if time_alive > 1.0:
                falling_heads.remove(head)
                continue
            
            # Physics
            head['x'] += head['vx'] * dt
            head['y'] += head['vy'] * dt
            head['vy'] += 300 * dt  # Gravity
            head['rotation'] += head['rot_speed'] * dt
            
            # Bounce off ground
            if head['y'] > fence_y + 60:
                head['y'] = fence_y + 60
                head['vy'] *= -0.4  # Bounce with energy loss
                head['vx'] *= 0.7
                head['rot_speed'] *= 0.7
            
            # Draw rotating head
            head_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            # Head circle
            pygame.draw.circle(head_surf, (40, 35, 35), (25, 25), 20)
            # Eyes (X_X dead eyes)
            pygame.draw.line(head_surf, (255, 255, 255), (15, 20), (20, 25), 2)
            pygame.draw.line(head_surf, (255, 255, 255), (20, 20), (15, 25), 2)
            pygame.draw.line(head_surf, (255, 255, 255), (30, 20), (35, 25), 2)
            pygame.draw.line(head_surf, (255, 255, 255), (35, 20), (30, 25), 2)
            # Tongue hanging out
            pygame.draw.ellipse(head_surf, (255, 100, 100), (20, 30, 10, 8))
            # Rotate
            rotated = pygame.transform.rotate(head_surf, head['rotation'])
            rect = rotated.get_rect(center=(int(head['x']), int(head['y'])))
            screen.blit(rotated, rect)
        
        # Draw WOLF ATTACK hint (no button, just text)
        if not wolf_active:
            wolf_hint = lobby_font.render("Press ENTER for 🐺 WOLF ATTACK!", True, (255, 100, 100))
            screen.blit(wolf_hint, (20, 20))
        else:
            wolf_status = lobby_font.render("🐺 Wolf Running...", True, (150, 150, 150))
            screen.blit(wolf_status, (20, 20))
        
        # Draw infinity mode indicator
        if infinity_mode:
            infinity_text = lobby_font.render("♾️ INFINITY MODE ACTIVE! ♾️", True, (255, 215, 0))
            screen.blit(infinity_text, (WIDTH//2 - infinity_text.get_width()//2, 20))
        
        # Draw stampede mode indicator
        if stampede_mode:
            stampede_text = lobby_font.render("🐑💨 STAMPEDE MODE! 💨🐑", True, (255, 50, 50))
            screen.blit(stampede_text, (WIDTH//2 - stampede_text.get_width()//2, 60))
            # Add shaking effect text
            shake_x = random.randint(-2, 2)
            shake_y = random.randint(-2, 2)
            warning = pygame.font.SysFont(None, 30).render("CHAOS!", True, (255, 100, 100))
            screen.blit(warning, (WIDTH//2 - warning.get_width()//2 + shake_x, 100 + shake_y))
        
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
                    # Track if music is still playing for the hack
                    # Check if pygame music is actually playing (not just the flag)
                    if pygame.mixer.music.get_busy():
                        print("[DEBUG] Music is playing when exiting sheep mode - setting hack flag!")
                        secret_hack['music_still_playing'] = True
                    else:
                        print("[DEBUG] Music is NOT playing when exiting")
                    return
                # Spacebar to spawn sheep faster
                elif event.key == pygame.K_SPACE:
                    spawn_timer = spawn_interval
                # ENTER to unleash wolf
                elif event.key == pygame.K_RETURN and not wolf_active:
                    wolf_active = True
                    wolf_x = -200
                    wolf_dead = False
                    eaten_sheep.clear()  # Reset eaten sheep list
                    falling_heads.clear()  # Reset falling heads
                    # Trigger hunter to come after the wolf
                    hunter_active = True
                    hunter_x = WIDTH + 200
                    hunter_shooting = False
                    bullet_active = False
                # Cheat code detection
                else:
                    # Add typed character to cheat input
                    if event.unicode and event.unicode.isprintable():
                        cheat_input += event.unicode
                        # Keep only last 9 characters
                        if len(cheat_input) > 9:
                            cheat_input = cheat_input[-9:]
                        # Check for infinity sheep cheat code
                        if cheat_input.endswith("xxxzzzccc"):
                            infinity_mode = not infinity_mode  # Toggle
                            cheat_input = ""  # Reset
                        # Check for stampede cheat code
                        elif cheat_input.endswith("ttt"):
                            stampede_mode = not stampede_mode  # Toggle
                            if not stampede_mode:
                                # Clear all sheep when turning off stampede
                                sheep_list.clear()
                                count = 0
                            cheat_input = ""  # Reset
                        # Check for WHOPPA GANG secret hack code!!!
                        elif cheat_input.endswith("whoppa gang"):
                            secret_hack['whoppa_gang_entered'] = True
                            cheat_input = ""  # Reset
                            # Show confirmation
                            confirm_text = lobby_font.render("WHOPPA GANG ACTIVATED!", True, (255, 100, 255))
                            screen.blit(confirm_text, (WIDTH//2 - confirm_text.get_width()//2, 50))
                            pygame.display.flip()
                            pygame.time.wait(1000)
                        # Check for dancing wolf cheat code (toggle on/off) - THIS STARTS THE MUSIC FOR HACK
                        elif cheat_input.endswith("lllooolll"):
                            # For the hack sequence, mark that whoppa gang was entered
                            secret_hack['whoppa_gang_entered'] = True
                            
                            if wolf_dancing:
                                # Turn OFF dancing mode
                                wolf_active = False
                                wolf_dancing = False
                                wolf_x = -200
                                # Stop Gangnam Style music!
                                try:
                                    pygame.mixer.music.stop()
                                    gangnam_music_playing = False
                                except Exception as e:
                                    print(f"Error stopping music: {e}")
                            else:
                                # Turn ON dancing mode
                                wolf_active = True
                                wolf_dancing = True
                                wolf_dance_time = 0
                                wolf_x = WIDTH // 2
                                wolf_dead = False
                                eaten_sheep.clear()
                                falling_heads.clear()
                                # No hunter for dancing wolf!
                                hunter_active = False
                                # Play Gangnam Style music!
                                try:
                                    pygame.mixer.music.stop()  # Stop any other music
                                    pygame.mixer.music.load(resource_path('gang.mp3'))
                                    pygame.mixer.music.play(-1)  # Loop forever
                                    gangnam_music_playing = True
                                    print("[DEBUG] lllooolll in sheep mode - Gangnam Style music started!")
                                except Exception as e:
                                    print(f"Error playing gang.mp3: {e}")
                            cheat_input = ""  # Reset
        
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

def get_player_name_online(prompt, y_pos, net, is_host):
    """Get player name with network synchronization - both players enter names simultaneously"""
    name = ""
    my_name_entered = False
    opponent_ready = False
    
    # Phase 1: Enter name
    while not my_name_entered:
        screen.fill((30, 30, 30))
        prompt_text = lobby_font.render(prompt, True, (255, 255, 255))
        screen.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, y_pos - 50))
        
        name_text = font.render(name, True, (255, 255, 255))
        screen.blit(name_text, (WIDTH//2 - name_text.get_width()//2, y_pos + 20))
        
        hint_text = name_font.render("Press ENTER when done", True, (150, 150, 150))
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, y_pos + 80))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    my_name_entered = True
                    # Send ready signal to other player
                    net.send({'type': 'name_ready', 'name': name})
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key <= 127 and event.unicode.isprintable():
                    name += event.unicode
        
        pygame.time.wait(50)
    
    # Phase 2: Wait for opponent to be ready
    while not opponent_ready:
        screen.fill((30, 30, 30))
        prompt_text = lobby_font.render(prompt, True, (255, 255, 255))
        screen.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, y_pos - 50))
        
        name_text = font.render(name, True, (255, 255, 255))
        screen.blit(name_text, (WIDTH//2 - name_text.get_width()//2, y_pos + 20))
        
        waiting_text = name_font.render("Waiting for other player...", True, (255, 255, 0))
        screen.blit(waiting_text, (WIDTH//2 - waiting_text.get_width()//2, y_pos + 80))
        
        pygame.display.flip()
        
        # Handle events to prevent freezing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Check for opponent ready signal
        data = net.recv()
        if data and data.get('type') == 'name_ready':
            opponent_ready = True
        
        pygame.time.wait(50)
    
    return name

def online_host_or_join():
    """Select whether to host or join an online game"""
    while True:
        screen.fill((30, 30, 30))
        title = lobby_font.render("Online Mode", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 200))
        
        host_rect = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 80, 200, 70)
        join_rect = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 - 80, 200, 70)
        quick_rect = pygame.Rect(WIDTH//2 - 140, HEIGHT//2 + 10, 280, 70)
        back_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 60)
        
        pygame.draw.rect(screen, (0, 180, 0), host_rect)
        pygame.draw.rect(screen, (0, 120, 255), join_rect)
        pygame.draw.rect(screen, (255, 140, 0), quick_rect)
        pygame.draw.rect(screen, (100, 100, 100), back_rect)
        
        host_text = font.render("Host Game", True, (255, 255, 255))
        join_text = font.render("Join Game", True, (255, 255, 255))
        quick_text = font.render("Quick Match", True, (255, 255, 255))
        back_text = font.render("Back", True, (255, 255, 255))
        
        screen.blit(host_text, (host_rect.centerx - host_text.get_width()//2, host_rect.centery - host_text.get_height()//2))
        screen.blit(join_text, (join_rect.centerx - join_text.get_width()//2, join_rect.centery - join_text.get_height()//2))
        screen.blit(quick_text, (quick_rect.centerx - quick_text.get_width()//2, quick_rect.centery - quick_text.get_height()//2))
        screen.blit(back_text, (back_rect.centerx - back_text.get_width()//2, back_rect.centery - back_text.get_height()//2))
        
        info = name_font.render("Host: Wait for players | Join: Enter IP", True, (200, 200, 200))
        info2 = name_font.render("Quick Match: Auto-connect with anyone!", True, (200, 200, 200))
        screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2 + 100))
        screen.blit(info2, (WIDTH//2 - info2.get_width()//2, HEIGHT//2 + 130))
        
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
                if quick_rect.collidepoint(event.pos):
                    return 'quick'
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
                            # Check if hack sequence conditions are met
                            if (secret_hack.get('sheep_mode_played') and 
                                secret_hack.get('whoppa_gang_entered') and 
                                secret_hack.get('music_still_playing') and
                                secret_hack.get('entered_battle_after_music')):
                                # HACK SEQUENCE: Show "skibidi" and return to menu
                                secret_hack['skibidi_triggered'] = True
                                screen.fill((0, 0, 0))
                                skibidi_font = pygame.font.Font(None, 200)
                                skibidi_text = skibidi_font.render("skibidi", True, (255, 255, 0))
                                screen.blit(skibidi_text, (WIDTH//2 - skibidi_text.get_width()//2, HEIGHT//2 - skibidi_text.get_height()//2))
                                pygame.display.flip()
                                pygame.time.wait(2000)
                                return 'lobby'  # Return to main menu
                            else:
                                # Normal cheat: instant win
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

# Show classroom adventure menu FIRST (type 'jaaaa' to skip)
try:
    if not hasattr(classroom_adventure_menu, 'shown'):
        result = classroom_adventure_menu()
        classroom_adventure_menu.shown = True
        
        # If a server code was entered, start classroom game
        if result == 'server1' or result == 'server2':
            # Clear screen and show connecting message
            screen.fill((135, 206, 250))  # Sky blue
            connect_font = pygame.font.SysFont(None, 80)
            server_name = "Server 1" if result == 'server1' else "Server 2"
            connect_text = connect_font.render(f"Connecting to {server_name}...", True, (255, 215, 0))
            connect_rect = connect_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(connect_text, connect_rect)
            
            # Show instructions
            instruction_font = pygame.font.SysFont(None, 50)
            inst1 = instruction_font.render("Classroom Adventure Mode!", True, (255, 255, 255))
            inst2 = instruction_font.render("Everyone on the same server can play together!", True, (255, 255, 255))
            screen.blit(inst1, (WIDTH//2 - inst1.get_width()//2, HEIGHT//2 + 80))
            screen.blit(inst2, (WIDTH//2 - inst2.get_width()//2, HEIGHT//2 + 140))
            
            pygame.display.flip()
            pygame.time.wait(2000)  # Show message for 2 seconds
            
            # NOW START THE ACTUAL CLASSROOM GAME!
            play_classroom_game(server_name)
            
            # After game ends, allow them to play again
            classroom_adventure_menu.shown = False
            
except:
    pass  # If classroom menu fails, continue

# Play talking intro sequence ONCE when game starts
try:
    # Check if intro has been shown this session
    if not hasattr(talking_intro, 'shown'):
        talking_intro()
        talking_intro.shown = True
except:
    pass  # If intro fails, continue to main menu

# Main program loop
while True:
    mode = mode_lobby()
    if mode == 0:
        # Show Play Local / Play Online selection
        selected = 0
        options = ["Play Local", "Play Online"]
        battle_lobby_key_buffer = ""  # Track key presses for hack sequence
        
        # Track if entering battle mode after music is still playing
        if secret_hack.get('music_still_playing') and not secret_hack.get('entered_battle_after_music'):
            secret_hack['entered_battle_after_music'] = True
        
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
            
            # DEBUG: Show hack progress and key buffer
            if secret_hack.get('music_still_playing'):
                debug_y = 150
                debug_font = pygame.font.Font(None, 24)
                status_text = debug_font.render(f"Typing: {battle_lobby_key_buffer}", True, (0, 255, 0))
                screen.blit(status_text, (10, debug_y))
                
                if secret_hack.get('sheep_mode_played'):
                    s1 = debug_font.render("✓ Sheep mode played", True, (0, 255, 0))
                    screen.blit(s1, (10, debug_y + 25))
                if secret_hack.get('whoppa_gang_entered'):
                    s2 = debug_font.render("✓ Whoppa gang entered", True, (0, 255, 0))
                    screen.blit(s2, (10, debug_y + 50))
                if secret_hack.get('music_still_playing'):
                    s3 = debug_font.render("✓ Music still playing", True, (0, 255, 0))
                    screen.blit(s3, (10, debug_y + 75))
                if secret_hack.get('entered_battle_after_music'):
                    s4 = debug_font.render("✓ Entered battle mode", True, (0, 255, 0))
                    screen.blit(s4, (10, debug_y + 100))
            
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    # HACK SEQUENCE: Detect lllooolll in Battle Mode lobby
                    key_name = pygame.key.name(event.key)
                    
                    if key_name in ['l', 'o']:
                        battle_lobby_key_buffer += key_name
                        # Keep only last 9 characters
                        if len(battle_lobby_key_buffer) > 9:
                            battle_lobby_key_buffer = battle_lobby_key_buffer[-9:]
                        
                        # Check if lllooolll was entered and hack conditions met
                        if battle_lobby_key_buffer == "lllooolll":
                            print(f"[DEBUG] lllooolll detected!")
                            print(f"  sheep_mode_played: {secret_hack.get('sheep_mode_played')}")
                            print(f"  whoppa_gang_entered: {secret_hack.get('whoppa_gang_entered')}")
                            print(f"  music_still_playing: {secret_hack.get('music_still_playing')}")
                            print(f"  entered_battle_after_music: {secret_hack.get('entered_battle_after_music')}")
                            
                            if (secret_hack.get('sheep_mode_played') and 
                                secret_hack.get('whoppa_gang_entered') and 
                                secret_hack.get('music_still_playing') and
                                secret_hack.get('entered_battle_after_music')):
                                # HACK SEQUENCE: Show "skibidi" and return to menu
                                secret_hack['skibidi_triggered'] = True
                                screen.fill((0, 0, 0))
                                skibidi_font = pygame.font.Font(None, 200)
                                skibidi_text = skibidi_font.render("skibidi", True, (255, 255, 0))
                                screen.blit(skibidi_text, (WIDTH//2 - skibidi_text.get_width()//2, HEIGHT//2 - skibidi_text.get_height()//2))
                                pygame.display.flip()
                                pygame.time.wait(2000)
                                break  # Exit to main menu
                            else:
                                # Show which conditions are missing
                                screen.fill((0, 0, 0))
                                error_font = pygame.font.Font(None, 60)
                                error_text = error_font.render("Code detected, but conditions not met!", True, (255, 100, 100))
                                screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2 - 100))
                                
                                small_font = pygame.font.Font(None, 30)
                                y = HEIGHT//2
                                if not secret_hack.get('sheep_mode_played'):
                                    msg = small_font.render("❌ Need to play sheep mode first", True, (255, 0, 0))
                                    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, y))
                                    y += 35
                                if not secret_hack.get('whoppa_gang_entered'):
                                    msg = small_font.render("❌ Need to enter 'whoppa gang' in sheep mode", True, (255, 0, 0))
                                    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, y))
                                    y += 35
                                if not secret_hack.get('music_still_playing'):
                                    msg = small_font.render("❌ Music must still be playing when you exit sheep mode", True, (255, 0, 0))
                                    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, y))
                                    y += 35
                                
                                pygame.display.flip()
                                pygame.time.wait(3000)
                    else:
                        # Reset buffer on other keys (except ESC and mouse)
                        if event.key != pygame.K_ESCAPE:
                            battle_lobby_key_buffer = ""
                    
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
                            # Show waiting screen with IP
                            local_ip = get_local_ip()
                            
                            try:
                                net = NetworkHost()
                                # Wait for connection with cancel option
                                waiting = True
                                while waiting and not net.conn:
                                    # Redraw waiting screen each frame
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
                                    # Show connection successful message
                                    screen.fill((30, 30, 30))
                                    connected_text = lobby_font.render("Player Connected! Starting...", True, (0, 255, 0))
                                    screen.blit(connected_text, (WIDTH//2 - connected_text.get_width()//2, HEIGHT//2))
                                    pygame.display.flip()
                                    pygame.time.wait(1000)
                                    
                                    # Host enters name AFTER connection (synchronized with client)
                                    player_name = get_player_name_online("Enter your name:", HEIGHT//2, net, True)
                                    
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
                                    player_name = get_player_name_online("Enter your name:", HEIGHT//2, net, False)
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
                        elif role == 'quick':
                            # Quick match: auto-scan for hosts or become host
                            quick_match_flow(mode_type=0)
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
                            # Show waiting screen with IP
                            local_ip = get_local_ip()
                            
                            try:
                                net = NetworkHost()
                                # Wait for connection with cancel option
                                waiting = True
                                while waiting and not net.conn:
                                    # Redraw waiting screen each frame
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
                                    # Show connection successful message
                                    screen.fill((30, 30, 30))
                                    connected_text = lobby_font.render("Player Connected! Starting...", True, (0, 255, 0))
                                    screen.blit(connected_text, (WIDTH//2 - connected_text.get_width()//2, HEIGHT//2))
                                    pygame.display.flip()
                                    pygame.time.wait(1000)
                                    
                                    # Host enters name AFTER connection (synchronized with client)
                                    player_name = get_player_name_online("Enter your name:", HEIGHT//2, net, True)
                                    
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
                                    player_name = get_player_name_online("Enter your name:", HEIGHT//2, net, False)
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
                        elif role == 'quick':
                            # Quick match: auto-scan for hosts or become host
                            quick_match_flow(mode_type=1)
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
                            # Show waiting screen with IP
                            local_ip = get_local_ip()
                            
                            try:
                                net = NetworkHost()
                                # Wait for connection with cancel option
                                waiting = True
                                while waiting and not net.conn:
                                    # Redraw waiting screen each frame
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
                                    # Show connection successful message
                                    screen.fill((30, 30, 30))
                                    connected_text = lobby_font.render("Player Connected! Starting...", True, (0, 255, 0))
                                    screen.blit(connected_text, (WIDTH//2 - connected_text.get_width()//2, HEIGHT//2))
                                    pygame.display.flip()
                                    pygame.time.wait(1000)
                                    
                                    # Host enters name AFTER connection (synchronized with client)
                                    player_name = get_player_name_online("Enter your name:", HEIGHT//2, net, True)
                                    
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
                        elif role == 'join':
                            host_ip = get_ip_address()
                            if host_ip:
                                screen.fill((30, 30, 30))
                                conn_text = lobby_font.render("Connecting...", True, (255, 255, 0))
                                screen.blit(conn_text, (WIDTH//2 - conn_text.get_width()//2, HEIGHT//2))
                                pygame.display.flip()
                                
                                try:
                                    net = NetworkClient(host_ip)
                                    player_name = get_player_name_online("Enter your name:", HEIGHT//2, net, False)
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
                        elif role == 'quick':
                            # Quick match: auto-scan for hosts or become host
                            quick_match_flow(mode_type=2)
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
                            # Show waiting screen with IP
                            local_ip = get_local_ip()
                            
                            try:
                                net = NetworkHost()
                                # Wait for connection with cancel option
                                waiting = True
                                while waiting and not net.conn:
                                    # Redraw waiting screen each frame
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
                                    # Show connection successful message
                                    screen.fill((30, 30, 30))
                                    connected_text = lobby_font.render("Player Connected! Starting...", True, (0, 255, 0))
                                    screen.blit(connected_text, (WIDTH//2 - connected_text.get_width()//2, HEIGHT//2))
                                    pygame.display.flip()
                                    pygame.time.wait(1000)
                                    
                                    # Host enters name AFTER connection (synchronized with client)
                                    player_name = get_player_name_online("Enter your name:", HEIGHT//2, net, True)
                                    
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
                                    player_name = get_player_name_online("Enter your name:", HEIGHT//2, net, False)
                                    # Simplified online - just play locally for now
                                    run_makka_pakka_mode("Opponent", player_name)
                                    net.close()
                                except Exception as e:
                                    screen.fill((30, 30, 30))
                                    error_text = font.render(f"Connection error: {str(e)}", True, (255, 0, 0))
                                    screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
                                    pygame.display.flip()
                                    pygame.time.wait(2000)
                        elif role == 'quick':
                            # Quick match: auto-scan for hosts or become host
                            quick_match_flow(mode_type=3)
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
                            # Show waiting screen with IP
                            local_ip = get_local_ip()
                            
                            try:
                                net = NetworkHost()
                                # Wait for connection with cancel option
                                waiting = True
                                while waiting and not net.conn:
                                    # Redraw waiting screen each frame
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
                                    # Show connection successful message
                                    screen.fill((30, 30, 30))
                                    connected_text = lobby_font.render("Player Connected! Starting...", True, (0, 255, 0))
                                    screen.blit(connected_text, (WIDTH//2 - connected_text.get_width()//2, HEIGHT//2))
                                    pygame.display.flip()
                                    pygame.time.wait(1000)
                                    
                                    # Host enters name AFTER connection (synchronized with client)
                                    player_name = get_player_name_online("Enter your name:", HEIGHT//2, net, True)
                                    
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
                                    player_name = get_player_name_online("Enter your name:", HEIGHT//2, net, False)
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











