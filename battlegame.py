import pygame
import sys
import os
import time
import random
import threading
import math
from network import NetworkHost, NetworkClient

pygame.init()

# Helper function to get the correct path for bundled files
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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
    options = ["Battle Mode", "Coin Collection Mode", "Makka Pakka Mode", "Escape Mom Mode", "Capture the Flag", "Survival Mode", "Play Music", "Stop Music", "Watch Cute Video", "Watch Grandma", "Exit"]
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
    import cv2
    cap = cv2.VideoCapture(resource_path('cutevideo.mp4'))
    if not cap.isOpened():
        # Show error message in lobby
        screen.fill((30,30,30))
        error_text = lobby_font.render("Error: Could not open cutevideo.mp4", True, (255,0,0))
        screen.blit(error_text, (WIDTH//2-error_text.get_width()//2, HEIGHT//2-error_text.get_height()//2))
        pygame.display.flip()
        pygame.time.wait(2000)
        return
    exit_button_rect = pygame.Rect(WIDTH//2-100, HEIGHT-120, 200, 60)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        try:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (WIDTH, HEIGHT))
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0,1))
            screen.blit(frame_surface, (0,0))
        except Exception as e:
            screen.fill((30,30,30))
            error_text = lobby_font.render(f"Video error: {e}", True, (255,0,0))
            screen.blit(error_text, (WIDTH//2-error_text.get_width()//2, HEIGHT//2-error_text.get_height()//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            cap.release()
            return
        pygame.draw.rect(screen, (255,0,0), exit_button_rect)
        exit_text = lobby_font.render("Exit", True, (255,255,255))
        screen.blit(exit_text, (exit_button_rect.centerx-exit_text.get_width()//2, exit_button_rect.centery-exit_text.get_height()//2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button_rect.collidepoint(event.pos):
                    cap.release()
                    return
    cap.release()

def watch_grandma():
    import cv2
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(resource_path('lala.mp3'))
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Error playing grandma music: {e}")
    cap = cv2.VideoCapture(resource_path('grandma.mp4'))
    if not cap.isOpened():
        screen.fill((30,30,30))
        error_text = lobby_font.render("Error: Could not open grandma.mp4", True, (255,0,0))
        screen.blit(error_text, (WIDTH//2-error_text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        time.sleep(2)
        return
    exit_button_rect = pygame.Rect(WIDTH//2-100, HEIGHT-120, 200, 60)
    running = True
    while running:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (WIDTH, HEIGHT))
            pygame_frame = pygame.surfarray.make_surface(frame.swapaxes(0,1))
            screen.blit(pygame_frame, (0,0))
            pygame.draw.rect(screen, (255,0,0), exit_button_rect)
            exit_text = lobby_font.render("Exit", True, (255,255,255))
            screen.blit(exit_text, (exit_button_rect.centerx-exit_text.get_width()//2, exit_button_rect.centery-exit_text.get_height()//2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_button_rect.collidepoint(event.pos):
                        running = False
                        break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
        # Loop video and music automatically
    cap.release()
    pygame.mixer.music.stop()

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
        # Online networking
        if online:
            if is_host:
                my_bullets = '|'.join([f"{b['rect'].x},{b['rect'].y},{b['dir']},{b['owner']}" for b in bullets if b['owner']==1])
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
                        if len(parts) > 1 and parts[1]:
                            for bstr in parts[1].split('|'):
                                bx, by, bdir, bowner = bstr.split(',')
                                if not any(abs(b['rect'].x-int(bx))<5 and abs(b['rect'].y-int(by))<5 and b['owner']==2 for b in bullets):
                                    bullets.append({'rect': pygame.Rect(int(bx), int(by), 10, 10), 'dir': int(bdir), 'owner': int(bowner)})
                except:
                    pass
            else:
                my_bullets = '|'.join([f"{b['rect'].x},{b['rect'].y},{b['dir']},{b['owner']}" for b in bullets if b['owner']==2])
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
    
    # Interpolation for smoother remote player movement
    target_p1_x, target_p1_y = player1.x, player1.y
    target_p2_x, target_p2_y = player2.x, player2.y
    interp_speed = 0.5  # Interpolation factor (0-1, higher = faster catch-up)
    
    # Send position updates only when moved significantly
    position_threshold = 3  # pixels - only send if moved more than this
    
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
                
                if (sync_counter % 3 == 0 and (moved_significantly or health_changed or direction_changed)) or has_new_bullets:
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
                
                if (sync_counter % 3 == 0 and (moved_significantly or health_changed or direction_changed)) or has_new_bullets:
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
    """Scary horror mode - escape from an angry mother in dark corridors!"""
    try:
        pygame.mixer.music.stop()
        # Use fart.mp3 but play it slower/creepier if possible, or just use suspenseful silence
    except:
        pass
    
    # Player (child)
    player = pygame.Rect(WIDTH//2, HEIGHT//2, 30, 40)
    player_speed = 5
    
    # Mother (chaser)
    mom = pygame.Rect(random.randint(0, WIDTH), random.randint(0, HEIGHT), 40, 60)
    mom_speed = 3  # Slower but persistent
    mom_visible = False  # She's hidden in the dark!
    mom_last_seen = 0
    
    # Corridor walls (random maze)
    walls = []
    # Create a corridor maze
    for i in range(15):
        if random.random() < 0.5:
            # Vertical wall
            w = pygame.Rect(random.randint(50, WIDTH-150), random.randint(50, HEIGHT-150), 20, random.randint(100, 300))
        else:
            # Horizontal wall
            w = pygame.Rect(random.randint(50, WIDTH-150), random.randint(50, HEIGHT-150), random.randint(100, 300), 20)
        walls.append(w)
    
    # Game state
    survived_time = 0
    start_time = time.time()
    caught = False
    heartbeat_sound = 0
    
    # Darkness vignette
    try:
        darkness_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        darkness_surface.set_alpha(180)
    except Exception as e:
        print(f"Error creating darkness surface: {e}")
        darkness_surface = pygame.Surface((WIDTH, HEIGHT))
    
    while not caught:
        now = time.time()
        survived_time = now - start_time
        
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
        
        # Mom AI - hunts the player
        dx = player.x - mom.x
        dy = player.y - mom.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        # Mom moves toward player
        if dist > 0:
            mom.x += (dx / dist) * mom_speed
            mom.y += (dy / dist) * mom_speed
        
        # Mom collision with walls
        mom_old_x, mom_old_y = mom.x, mom.y
        for wall in walls:
            if mom.colliderect(wall):
                # Mom can phase through walls sometimes (spooky!)
                if random.random() < 0.3:
                    pass  # She goes through!
                else:
                    mom.x, mom.y = mom_old_x, mom_old_y
                break
        
        # Check if mom is close (she becomes visible!)
        if dist < 200:
            mom_visible = True
            mom_last_seen = now
        elif now - mom_last_seen > 2:
            mom_visible = False
        
        # Caught!
        if player.colliderect(mom):
            caught = True
        
        # Drawing
        screen.fill((20, 20, 25))  # Dark blue/black
        
        # Draw walls (dim gray corridors)
        for wall in walls:
            pygame.draw.rect(screen, (60, 60, 70), wall)
            pygame.draw.rect(screen, (40, 40, 50), wall, 2)
        
        # Draw player (small scared child)
        # Head
        pygame.draw.circle(screen, (255, 220, 180), (player.centerx, player.y+10), 8)
        # Eyes (scared wide eyes)
        pygame.draw.circle(screen, (255, 255, 255), (player.centerx-4, player.y+8), 3)
        pygame.draw.circle(screen, (255, 255, 255), (player.centerx+4, player.y+8), 3)
        pygame.draw.circle(screen, (0, 0, 0), (player.centerx-4, player.y+8), 2)
        pygame.draw.circle(screen, (0, 0, 0), (player.centerx+4, player.y+8), 2)
        # Scared mouth
        pygame.draw.arc(screen, (0, 0, 0), (player.centerx-4, player.y+12, 8, 6), 0, 3.14, 2)
        # Body (pajamas)
        pygame.draw.rect(screen, (100, 150, 200), (player.x+5, player.y+18, 20, 22))
        
        # Draw mom (scary when visible!)
        if mom_visible:
            # Angry mother figure (scary red tint)
            # Head
            pygame.draw.circle(screen, (255, 200, 200), (mom.centerx, mom.y+15), 12)
            # Angry eyes
            pygame.draw.line(screen, (200, 0, 0), (mom.centerx-8, mom.y+12), (mom.centerx-4, mom.y+14), 3)
            pygame.draw.line(screen, (200, 0, 0), (mom.centerx+4, mom.y+14), (mom.centerx+8, mom.y+12), 3)
            # Angry mouth
            pygame.draw.arc(screen, (150, 0, 0), (mom.centerx-6, mom.y+18, 12, 8), 3.14, 6.28, 3)
            # Body (dress)
            pygame.draw.rect(screen, (100, 50, 50), (mom.x+8, mom.y+27, 24, 33))
            # Arms reaching
            pygame.draw.line(screen, (255, 200, 200), (mom.centerx-10, mom.y+30), (mom.centerx-20, mom.y+25), 6)
            pygame.draw.line(screen, (255, 200, 200), (mom.centerx+10, mom.y+30), (mom.centerx+20, mom.y+25), 6)
            
            # Warning text when she's near!
            if dist < 100:
                warning = lobby_font.render("SHE'S CLOSE!", True, (255, 0, 0))
                screen.blit(warning, (WIDTH//2-warning.get_width()//2, 50))
        
        # Darkness overlay (limited vision)
        darkness_surface.fill((0, 0, 0))
        # Create a circle of light around player
        for radius in range(150, 0, -5):
            alpha = int(200 * (1 - radius/150))
            pygame.draw.circle(darkness_surface, (0, 0, 0, alpha), player.center, radius)
        screen.blit(darkness_surface, (0, 0))
        
        # UI
        time_text = font.render(f"Survived: {int(survived_time)}s", True, (255, 255, 255))
        screen.blit(time_text, (20, 20))
        
        tip_text = name_font.render("Use WASD/Arrows to run! Press ESC to quit", True, (200, 200, 200))
        screen.blit(tip_text, (WIDTH//2-tip_text.get_width()//2, HEIGHT-30))
        
        # Heartbeat effect when mom is close
        if dist < 150:
            heartbeat_sound += 1
            if heartbeat_sound % 30 < 15:
                pygame.draw.circle(screen, (255, 0, 0, 50), (20, HEIGHT-40), 15)
        
        pygame.display.flip()
        clock.tick(60)
    
    # JUMPSCARE! Show TERRIFYING mom eating you from your perspective!
    jumpscare_time = time.time()
    jumpscare_duration = 2.0  # 2 seconds of pure terror
    
    # Play scary scream sound
    try:
        pygame.mixer.music.load(resource_path("scary-scream.mp3"))
        pygame.mixer.music.play()
    except:
        # Fallback to system beeps if sound file not found
        for _ in range(10):
            print("\a")  # System beep
    
    while time.time() - jumpscare_time < jumpscare_duration:
        elapsed = time.time() - jumpscare_time
        progress = elapsed / jumpscare_duration
        
        # Flash between black and red for extra scary effect
        if int((time.time() - jumpscare_time) * 20) % 2 == 0:
            screen.fill((0, 0, 0))
        else:
            screen.fill((int(100 * progress), 0, 0))
        
        # Mom grows MASSIVE (20-30x bigger as she gets closer!)
        scale = 20 + (progress * 10)  # Grows from 20x to 30x size
        face_size = int(400 * scale / 20)
        face_x = WIDTH // 2
        face_y = HEIGHT // 2
        
        # GIANT DECAYING HEAD with veins
        pygame.draw.circle(screen, (200 + int(30 * progress), 160 - int(60 * progress), 160 - int(60 * progress)), (face_x, face_y), face_size//2)
        pygame.draw.circle(screen, (180 + int(40 * progress), 140 - int(80 * progress), 140 - int(80 * progress)), (face_x, face_y), face_size//2 - 10)
        
        # Dark circles under eyes (tired, scary mom)
        pygame.draw.ellipse(screen, (100, 50, 100), (face_x - 150, face_y - 100, 100, 60))
        pygame.draw.ellipse(screen, (100, 50, 100), (face_x + 50, face_y - 100, 100, 60))
        
        # MASSIVE BLOODSHOT EYES staring DOWN at you!
        eye_size = int(100 + progress * 30)
        eye_spacing = int(140 + progress * 20)
        
        # Left eye - bloodshot and terrifying
        pygame.draw.ellipse(screen, (255, 255, 200), (face_x - eye_spacing - eye_size//2, face_y - 100, eye_size, eye_size + 30))
        # Bloodshot iris - RED
        pygame.draw.circle(screen, (180, 0, 0), (face_x - eye_spacing, face_y - 70), int(50 + progress * 10))
        pygame.draw.circle(screen, (120, 0, 0), (face_x - eye_spacing, face_y - 70), int(40 + progress * 8))
        # Black pupil staring at YOU
        pygame.draw.circle(screen, (0, 0, 0), (face_x - eye_spacing, face_y - 70), int(25 + progress * 5))
        # Tiny white glint (makes it look alive)
        pygame.draw.circle(screen, (255, 255, 255), (face_x - eye_spacing + 8, face_y - 75), 5)
        
        # Right eye - bloodshot and terrifying
        pygame.draw.ellipse(screen, (255, 255, 200), (face_x + eye_spacing - eye_size//2, face_y - 100, eye_size, eye_size + 30))
        # Bloodshot iris - RED
        pygame.draw.circle(screen, (180, 0, 0), (face_x + eye_spacing, face_y - 70), int(50 + progress * 10))
        pygame.draw.circle(screen, (120, 0, 0), (face_x + eye_spacing, face_y - 70), int(40 + progress * 8))
        # Black pupil staring at YOU
        pygame.draw.circle(screen, (0, 0, 0), (face_x + eye_spacing, face_y - 70), int(25 + progress * 5))
        # Tiny white glint
        pygame.draw.circle(screen, (255, 255, 255), (face_x + eye_spacing + 8, face_y - 75), 5)
        
        # Red veins spreading from eyes
        for i in range(15):
            vein_angle = random.random() * 6.28
            vein_length = random.randint(30, 80)
            start_x = face_x - eye_spacing
            start_y = face_y - 70
            end_x = int(start_x + math.cos(vein_angle) * vein_length)
            end_y = int(start_y + math.sin(vein_angle) * vein_length)
            pygame.draw.line(screen, (200, 0, 0), (start_x, start_y), (end_x, end_y), 2)
        for i in range(15):
            vein_angle = random.random() * 6.28
            vein_length = random.randint(30, 80)
            start_x = face_x + eye_spacing
            start_y = face_y - 70
            end_x = int(start_x + math.cos(vein_angle) * vein_length)
            end_y = int(start_y + math.sin(vein_angle) * vein_length)
            pygame.draw.line(screen, (200, 0, 0), (start_x, start_y), (end_x, end_y), 2)
        
        # THICK ANGRY EYEBROWS
        pygame.draw.line(screen, (60, 30, 30), (face_x - eye_spacing - 60, face_y - 140), (face_x - eye_spacing + 40, face_y - 100), 18)
        pygame.draw.line(screen, (60, 30, 30), (face_x + eye_spacing - 40, face_y - 100), (face_x + eye_spacing + 60, face_y - 140), 18)
        
        # Wrinkles (angry forehead)
        for i in range(5):
            y_pos = face_y - 160 + i * 15
            pygame.draw.line(screen, (150, 100, 100), (face_x - 80, y_pos), (face_x + 80, y_pos + 5), 3)
        
        # HUGE GAPING MOUTH - gets WIDER as she eats you!
        mouth_width = int(200 + progress * 100)  # Grows wider
        mouth_height = int(180 + progress * 80)  # Opens more
        mouth_y = int(face_y + 30 - progress * 20)  # Comes toward you
        
        # Dark throat
        pygame.draw.ellipse(screen, (10, 0, 0), (face_x - mouth_width//2, mouth_y, mouth_width, mouth_height))
        pygame.draw.ellipse(screen, (5, 0, 0), (face_x - mouth_width//2 + 20, mouth_y + 20, mouth_width - 40, mouth_height - 40))
        
        # Tongue (wet and scary)
        tongue_points = [
            (face_x - 40, mouth_y + mouth_height - 40),
            (face_x, mouth_y + mouth_height - 20),
            (face_x + 40, mouth_y + mouth_height - 40),
            (face_x + 30, mouth_y + mouth_height - 10),
            (face_x - 30, mouth_y + mouth_height - 10)
        ]
        pygame.draw.polygon(screen, (180, 80, 100), tongue_points)
        # Saliva drip effect
        if int(elapsed * 10) % 3 == 0:
            pygame.draw.line(screen, (200, 200, 255, 150), (face_x - 50, mouth_y + 20), (face_x - 50, mouth_y + 80), 3)
            pygame.draw.line(screen, (200, 200, 255, 150), (face_x + 50, mouth_y + 20), (face_x + 50, mouth_y + 80), 3)
        
        # SHARP TEETH (both top and bottom rows)
        teeth_count = 14
        for i in range(teeth_count):
            # Top teeth
            tooth_x = face_x - mouth_width//2 + 20 + i * (mouth_width - 40) // teeth_count
            tooth_width = 15
            tooth_height = int(35 + progress * 20)
            pygame.draw.polygon(screen, (255, 255, 220), [
                (tooth_x, mouth_y),
                (tooth_x + tooth_width, mouth_y),
                (tooth_x + tooth_width//2, mouth_y + tooth_height)
            ])
            # Yellow stains on teeth
            pygame.draw.polygon(screen, (240, 240, 180), [
                (tooth_x + 2, mouth_y),
                (tooth_x + tooth_width - 2, mouth_y),
                (tooth_x + tooth_width//2, mouth_y + tooth_height - 5)
            ])
            
            # Bottom teeth
            tooth_x_bottom = face_x - mouth_width//2 + 30 + i * (mouth_width - 60) // teeth_count
            pygame.draw.polygon(screen, (255, 255, 220), [
                (tooth_x_bottom, mouth_y + mouth_height - tooth_height),
                (tooth_x_bottom + tooth_width, mouth_y + mouth_height - tooth_height),
                (tooth_x_bottom + tooth_width//2, mouth_y + mouth_height)
            ])
        
        # Blood stains around mouth
        for i in range(20):
            stain_x = face_x - mouth_width//2 + random.randint(-20, mouth_width + 20)
            stain_y = mouth_y + random.randint(-15, mouth_height + 15)
            pygame.draw.circle(screen, (120, 0, 0), (stain_x, stain_y), random.randint(3, 8))
        
        # CRACKS and VEINS all over face
        for i in range(30):
            crack_start_x = face_x + random.randint(-face_size//3, face_size//3)
            crack_start_y = face_y + random.randint(-face_size//3, face_size//3)
            crack_end_x = crack_start_x + random.randint(-60, 60)
            crack_end_y = crack_start_y + random.randint(-60, 60)
            pygame.draw.line(screen, (150, 0, 0), (crack_start_x, crack_start_y), (crack_end_x, crack_end_y), 3)
        
        # Hair (messy and scary)
        for i in range(30):
            hair_x = face_x + random.randint(-face_size//2, face_size//2)
            hair_y = face_y - face_size//2 + random.randint(-30, 30)
            hair_length = random.randint(40, 100)
            pygame.draw.line(screen, (20, 10, 10), (hair_x, hair_y), (hair_x + random.randint(-20, 20), hair_y - hair_length), 4)
        
        # Shake effect - screen trembles
        shake_intensity = int(10 + progress * 20)
        shake_x = random.randint(-shake_intensity, shake_intensity)
        shake_y = random.randint(-shake_intensity, shake_intensity)
        
        # Text that changes and shakes
        if progress < 0.5:
            jumpscare_text = lobby_font.render("SHE CAUGHT YOU!", True, (255, int(50 + progress * 200), int(50 + progress * 200)))
        else:
            jumpscare_text = lobby_font.render("YOU'RE BEING EATEN!", True, (255, 0, 0))
        screen.blit(jumpscare_text, (WIDTH//2 - jumpscare_text.get_width()//2 + shake_x, 50 + shake_y))
        
        # Add more scary text at bottom
        if progress > 0.6:
            terror_text = font.render("NO ESCAPE...", True, (200, 0, 0))
            screen.blit(terror_text, (WIDTH//2 - terror_text.get_width()//2 + shake_x//2, HEIGHT - 100 + shake_y//2))
        
        pygame.display.flip()
        clock.tick(60)
        
        # Allow emergency exit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'lobby'
    
    # After jumpscare, show normal game over screen
    while True:
        screen.fill((20, 0, 0))  # Red tint
        
        gameover = lobby_font.render("SHE CAUGHT YOU!", True, (255, 0, 0))
        screen.blit(gameover, (WIDTH//2-gameover.get_width()//2, HEIGHT//2-100))
        
        time_survived = font.render(f"You survived for {int(survived_time)} seconds", True, (255, 255, 255))
        screen.blit(time_survived, (WIDTH//2-time_survived.get_width()//2, HEIGHT//2-30))
        
        back_button = pygame.Rect(WIDTH//2-100, HEIGHT//2+40, 200, 60)
        pygame.draw.rect(screen, (100, 0, 0), back_button)
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
                            # Show waiting screen with IP
                            import socket
                            hostname = socket.gethostname()
                            local_ip = socket.gethostbyname(hostname)
                            
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
                                    player_name = get_player_name("Enter your name:", HEIGHT//2)
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
                            # Show waiting screen with IP
                            import socket
                            hostname = socket.gethostname()
                            local_ip = socket.gethostbyname(hostname)
                            
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
                                    player_name = get_player_name("Enter your name:", HEIGHT//2)
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
                            # Show waiting screen with IP
                            import socket
                            hostname = socket.gethostname()
                            local_ip = socket.gethostbyname(hostname)
                            
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
                            # Show waiting screen with IP
                            import socket
                            hostname = socket.gethostname()
                            local_ip = socket.gethostbyname(hostname)
                            
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
                                    player_name = get_player_name("Enter your name:", HEIGHT//2)
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
                            import socket
                            hostname = socket.gethostname()
                            local_ip = socket.gethostbyname(hostname)
                            
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
                                    player_name = get_player_name("Enter your name:", HEIGHT//2)
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











