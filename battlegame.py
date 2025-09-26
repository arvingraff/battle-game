import pygame
import sys
import time
import random
import threading
import json
import os
from network import NetworkHost, NetworkClient

pygame.init()



# Set fullscreen mode
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("2 Player Battle Game")
clock = pygame.time.Clock()

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
    options = ["Battle Mode", "Coin Collection Mode", "Survival Mode", "Play Music", "Stop Music", "Watch Cute Video", "Watch Grandma", "Exit"]
    music_playing = False
    pygame.mixer.music.stop()  # Ensure no music plays automatically
    while True:
        screen.fill((30, 30, 30))
        title = lobby_font.render("Choose Game Mode", True, (255,255,255))
        screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-120))
        for i, opt in enumerate(options):
            color = (255,255,0) if i==selected else (200,200,200)
            opt_text = font.render(opt, True, color)
            screen.blit(opt_text, (WIDTH//2-opt_text.get_width()//2, HEIGHT//2-40+i*60))
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
                            pygame.mixer.music.load('playmusic.mp3')
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
                        return selected if options[selected] not in ["Play Music", "Stop Music", "Watch Cute Video", "Watch Grandma"] else None

def watch_cute_video():
    import cv2
    cap = cv2.VideoCapture('cutevideo.mp4')
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
        pygame.mixer.music.load('lala.mp3')
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Error playing grandma music: {e}")
    cap = cv2.VideoCapture('grandma.mp4')
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
        sound = pygame.mixer.Sound('321go.mp3')
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
    if style == 0:  # Classic Mafia (no smile)
        # Head with subtle jawline
        pygame.draw.ellipse(screen, (224, 172, 105), (x-15, y-35, 30, 38))
        pygame.draw.line(screen, (200,160,90), (x-10, y-10), (x+10, y-10), 2)
        # Fedora with red band
        pygame.draw.rect(screen, (60,60,60), (x-15, y-45, 30, 10))
        pygame.draw.rect(screen, (200,0,0), (x-15, y-42, 30, 4))
        pygame.draw.rect(screen, (30,30,30), (x-10, y-50, 20, 8))
        # Sunglasses
        pygame.draw.rect(screen, (0,0,0), (x-8, y-25, 8, 6))
        pygame.draw.rect(screen, (0,0,0), (x+2, y-25, 8, 6))
        pygame.draw.line(screen, (0,0,0), (x, y-22), (x+2, y-22), 2)
        # Eyes and eyebrows (hidden by sunglasses)
        # Mustache
        pygame.draw.arc(screen, (80,42,20), (x-7, y-8, 14, 6), 3.14, 2*3.14, 2)
        # Suit with pocket square
        pygame.draw.rect(screen, (0,0,0), (x-14, y+3, 28, 38))
        pygame.draw.rect(screen, (255,255,255), (x-6, y+3, 12, 38))
        pygame.draw.rect(screen, (200,0,0), (x-2, y+10, 4, 24))
        pygame.draw.rect(screen, (255,215,0), (x+8, y+10, 6, 6))  # gold pocket square
        # Shoes
        pygame.draw.ellipse(screen, (0,0,0), (x-12, y+38, 12, 8))
        pygame.draw.ellipse(screen, (0,0,0), (x+0, y+38, 12, 8))
    elif style == 1:  # Mafia Boss (improved head)
        # Head: oval, natural jawline
        pygame.draw.ellipse(screen, (224, 172, 105), (x-20, y-40, 40, 48))
        # Jaw shadow for depth
        pygame.draw.arc(screen, (200,160,90), (x-12, y-10, 24, 18), 3.14, 2*3.14, 3)
        # Cheekbones (subtle)
        pygame.draw.arc(screen, (200,160,90), (x-16, y-20, 12, 10), 3.8, 5.5, 2)
        pygame.draw.arc(screen, (200,160,90), (x+4, y-20, 12, 10), 3.8, 5.5, 2)
        # Thicker eyebrows
        pygame.draw.rect(screen, (60,40,20), (x-12, y-28, 10, 3))
        pygame.draw.rect(screen, (60,40,20), (x+2, y-28, 10, 3))
        # Eyes (intense)
        pygame.draw.ellipse(screen, (255,255,255), (x-8, y-22, 10, 8))
        pygame.draw.ellipse(screen, (255,255,255), (x+8, y-22, 10, 8))
        pygame.draw.ellipse(screen, (0,0,0), (x-4, y-19, 4, 5))
        pygame.draw.ellipse(screen, (0,0,0), (x+12, y-19, 4, 5))
        # Stern mouth
        pygame.draw.arc(screen, (0,0,0), (x-6, y-10, 16, 8), 3.8, 5.5, 2)
        # Big hat with feather (more detail)
        pygame.draw.rect(screen, (40,40,40), (x-22, y-55, 44, 14))
        pygame.draw.rect(screen, (80,80,80), (x-10, y-65, 24, 12))
        pygame.draw.polygon(screen, (255,255,0), [(x+10, y-55), (x+18, y-70), (x+14, y-55)])  # feather
        pygame.draw.line(screen, (255,255,255), (x-10, y-60), (x+10, y-60), 2)
        # Monocle
        pygame.draw.circle(screen, (255,215,0), (x+12, y-18), 7, 2)
        pygame.draw.line(screen, (255,215,0), (x+12, y-11), (x+12, y-5), 2)
        # Cigar (detailed)
        pygame.draw.rect(screen, (139,69,19), (x-8, y-8, 18, 7))
        pygame.draw.circle(screen, (255,0,0), (x+10, y-5), 4)
        # Gold chain
        pygame.draw.arc(screen, (255,215,0), (x-10, y+20, 28, 18), 3.14, 2*3.14, 3)
        # Gold ring
        pygame.draw.circle(screen, (255,215,0), (x+18, y+30), 5)
        # Gold watch
        pygame.draw.rect(screen, (255,215,0), (x-24, y+28, 8, 6))
        # Pinstripe suit
        pygame.draw.rect(screen, (30,30,30), (x-18, y+3, 36, 48))
        for i in range(-16, 18, 8):
            pygame.draw.line(screen, (200,200,200), (x+i, y+3), (x+i, y+51), 2)
        pygame.draw.rect(screen, (255,255,255), (x-6, y+3, 12, 48))
        pygame.draw.rect(screen, (200,0,0), (x-2, y+18, 4, 28))
    elif style == 2:  # Mafia Hitman (no smile, no scar)
        # Head
        pygame.draw.ellipse(screen, (224, 172, 105), (x-15, y-35, 30, 38))
        # Slicked-back hair
        pygame.draw.arc(screen, (0,0,0), (x-15, y-40, 30, 18), 3.8, 5.5, 6)
        # Intense, narrowed eyes
        pygame.draw.ellipse(screen, (255,255,255), (x-8, y-25, 7, 6))
        pygame.draw.ellipse(screen, (255,255,255), (x+1, y-25, 7, 6))
        pygame.draw.ellipse(screen, (0,0,0), (x-5, y-23, 3, 3))
        pygame.draw.ellipse(screen, (0,0,0), (x+4, y-23, 3, 3))
        # Stern mouth (no smile)
        pygame.draw.arc(screen, (0,0,0), (x-7, y-2, 14, 6), 3.8, 5.5, 2)
        # Angular sunglasses
        pygame.draw.polygon(screen, (0,0,0), [(x-10, y-25), (x, y-25), (x, y-19), (x-10, y-19)])
        pygame.draw.polygon(screen, (0,0,0), [(x+2, y-25), (x+12, y-25), (x+12, y-19), (x+2, y-19)])
        pygame.draw.line(screen, (0,0,0), (x, y-22), (x+2, y-22), 2)
        # Earring
        pygame.draw.circle(screen, (255,215,0), (x+13, y-10), 2)
        # Black glove
        pygame.draw.rect(screen, (0,0,0), (x+18, y+20, 8, 12))
        # Trench coat
        pygame.draw.rect(screen, (10,10,10), (x-16, y+3, 32, 44))
        pygame.draw.rect(screen, (255,0,0), (x-4, y+3, 8, 44))
        # Red tie
        pygame.draw.polygon(screen, (200,0,0), [(x, y+10), (x-3, y+30), (x+3, y+30)])
        # Arms
        pygame.draw.line(screen, (224, 172, 105), (x-20, y+20), (x+20, y+20), 8)
        # Shoes
        pygame.draw.ellipse(screen, (0,0,0), (x-12, y+45, 14, 8))
        pygame.draw.ellipse(screen, (0,0,0), (x-2, y+45, 14, 8))
    # ...add arms, legs, shoes as needed...

def draw_explorer_character(screen, x, y, style):
    if style == 0:  # Jungle Explorer (improved)
        # Head
        pygame.draw.ellipse(screen, (255, 224, 189), (x-15, y-35, 30, 38))
        # Eyes
        pygame.draw.ellipse(screen, (255,255,255), (x-8, y-25, 7, 10))
        pygame.draw.ellipse(screen, (255,255,255), (x+1, y-25, 7, 10))
        pygame.draw.ellipse(screen, (0,0,0), (x-5, y-21, 3, 5))
        pygame.draw.ellipse(screen, (0,0,0), (x+4, y-21, 3, 5))
        # Explorer hat
        pygame.draw.rect(screen, (139,69,19), (x-15, y-40, 30, 10))
        pygame.draw.rect(screen, (205,133,63), (x-10, y-45, 20, 8))
        pygame.draw.ellipse(screen, (139,69,19), (x-15, y-48, 30, 10))
        # Smile
        pygame.draw.arc(screen, (255,0,0), (x-7, y-10, 14, 10), 3.14, 2*3.14, 3)
        # Backpack
        pygame.draw.rect(screen, (80,50,20), (x-18, y+10, 36, 18))
        # Green shirt
        pygame.draw.rect(screen, (0, 200, 0), (x-10, y+3, 20, 38))
        # Boots
        pygame.draw.ellipse(screen, (80,50,20), (x-12, y+38, 12, 8))
        pygame.draw.ellipse(screen, (80,50,20), (x+0, y+38, 12, 8))
    elif style == 1:  # Desert Adventurer (improved)
        # Head
        pygame.draw.ellipse(screen, (255, 224, 189), (x-15, y-35, 30, 38))
        # Eyes
        pygame.draw.ellipse(screen, (255,255,255), (x-8, y-25, 7, 10))
        pygame.draw.ellipse(screen, (255,255,255), (x+1, y-25, 7, 10))
        pygame.draw.ellipse(screen, (0,0,0), (x-5, y-21, 3, 5))
        pygame.draw.ellipse(screen, (0,0,0), (x+4, y-21, 3, 5))
        # Sun hat
        pygame.draw.rect(screen, (210,180,140), (x-15, y-40, 30, 10))
        pygame.draw.ellipse(screen, (210,180,140), (x-15, y-48, 30, 10))
        # Scarf
        pygame.draw.rect(screen, (255,222,173), (x-10, y-45, 20, 8))
        # Goggles
        pygame.draw.rect(screen, (255,215,0), (x-10, y+25, 20, 8))
        # Smile
        pygame.draw.arc(screen, (255,140,0), (x-7, y-10, 14, 10), 3.14, 2*3.14, 3)
        # Backpack
        pygame.draw.rect(screen, (210,180,140), (x-18, y+10, 36, 18))
        # Shirt
        pygame.draw.rect(screen, (255, 228, 181), (x-10, y+3, 20, 38))
        # Boots
        pygame.draw.ellipse(screen, (210,180,140), (x-12, y+38, 12, 8))
        pygame.draw.ellipse(screen, (210,180,140), (x+0, y+38, 12, 8))
    elif style == 2:  # Arctic Explorer (improved)
        # Head
        pygame.draw.ellipse(screen, (220, 220, 255), (x-15, y-35, 30, 38))
        # Eyes
        pygame.draw.ellipse(screen, (255,255,255), (x-8, y-25, 7, 10))
        pygame.draw.ellipse(screen, (255,255,255), (x+1, y-25, 7, 10))
        pygame.draw.ellipse(screen, (0,0,0), (x-5, y-21, 3, 5))
        pygame.draw.ellipse(screen, (0,0,0), (x+4, y-21, 3, 5))
        # Fur hood
        pygame.draw.rect(screen, (135,206,250), (x-15, y-40, 30, 10))
        pygame.draw.ellipse(screen, (255,255,255), (x-15, y-48, 30, 10))
        # Fur trim
        pygame.draw.rect(screen, (255,255,255), (x-10, y-45, 20, 8))
        # Rosy cheeks
        pygame.draw.circle(screen, (255,182,193), (x, y-20), 4)
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

# Main game loop refactored into a function

def run_game(mode, player1_name, player2_name, char_choices, network=None, is_host=False, online=False):
    # Start original background music
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load('fart.mp3')
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
            
            # Determine Player 1's current weapon based on upgrades
            if p1_bazooka_left > 0:
                p1_weapon = "bazooka"
            elif p1_kannon_left > 0:
                p1_weapon = "kannon"
            else:
                p1_weapon = "default"
            
            # Determine Player 2's current weapon based on upgrades
            if p2_bazooka_left > 0:
                p2_weapon = "bazooka"
            elif p2_kannon_left > 0:
                p2_weapon = "kannon"
            else:
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
            # Draw green rectangle
            pygame.draw.rect(screen, (0,180,0), paper)
            # Draw yellow border
            pygame.draw.rect(screen, (255,220,0), paper, 3)
            # Draw yellow $ symbol in center
            dollar_font = pygame.font.SysFont(None, 32)
            dollar_text = dollar_font.render("$", True, (255,220,0))
            screen.blit(dollar_text, (paper.centerx - dollar_text.get_width()//2, paper.centery - dollar_text.get_height()//2))
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
    # Draws the selected weapon for a player
    if weapon == "bazooka":
        # Bazooka: big green tube, orange tip
        if right:
            pygame.draw.rect(screen, (0,180,0), (x, y-8, 44, 14))
            pygame.draw.ellipse(screen, (255,140,0), (x+44, y-12, 12, 22))
            pygame.draw.rect(screen, (80,40,0), (x+10, y-8, 10, 14))
        else:
            pygame.draw.rect(screen, (0,180,0), (x-56, y-8, 44, 14))
            pygame.draw.ellipse(screen, (255,140,0), (x-68, y-12, 12, 22))
            pygame.draw.rect(screen, (80,40,0), (x-20, y-8, 10, 14))
    elif weapon == "kannon":
        # Kannon: big gray barrel, gold tip
        if right:
            pygame.draw.rect(screen, (120,120,120), (x, y-10, 38, 18))
            pygame.draw.ellipse(screen, (255,215,0), (x+38, y-14, 14, 26))
            pygame.draw.rect(screen, (80,80,80), (x+10, y-10, 10, 18))
        else:
            pygame.draw.rect(screen, (120,120,120), (x-52, y-10, 38, 18))
            pygame.draw.ellipse(screen, (255,215,0), (x-66, y-14, 14, 26))
            pygame.draw.rect(screen, (80,80,80), (x-20, y-10, 10, 18))
    else:
        # Default gun: AK-47 style
        if right:
            pygame.draw.rect(screen, (80,80,80), (x+20, y-4, 22, 4))
            pygame.draw.rect(screen, (139,69,19), (x-18, y-7, 16, 8))
            pygame.draw.rect(screen, (80,80,80), (x, y-7, 38, 8))
            pygame.draw.arc(screen, (60,60,60), (x+10, y+2, 18, 14), 3.14, 2*3.14, 4)
            pygame.draw.rect(screen, (60,60,60), (x+30, y+2, 6, 12))
        else:
            pygame.draw.rect(screen, (80,80,80), (x-42, y-4, 22, 4))
            pygame.draw.rect(screen, (139,69,19), (x+2, y-7, 16, 8))
            pygame.draw.rect(screen, (80,80,80), (x-38, y-7, 38, 8))
            pygame.draw.arc(screen, (60,60,60), (x-28, y+2, 18, 14), 0, 3.14, 4)
            pygame.draw.rect(screen, (60,60,60), (x-36, y+2, 6, 12))

# Main game with upgrades

def run_game_with_upgrades(player1_name, player2_name, char_choices, p1_bazooka, p2_bazooka, p1_kannon, p2_kannon, p1_life, p2_life, mode=0):
    # Battle mode with upgrades: bazooka/kannon = 2 shots each, then normal
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load('fart.mp3')
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
    start_countdown()
    while True:
        now = time.time()
        # (No online/network sync in this function)
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
            
            # Determine Player 1's current weapon based on upgrades
            if p1_bazooka_left > 0:
                p1_weapon = "bazooka"
            elif p1_kannon_left > 0:
                p1_weapon = "kannon"
            else:
                p1_weapon = "default"
            
            # Determine Player 2's current weapon based on upgrades
            if p2_bazooka_left > 0:
                p2_weapon = "bazooka"
            elif p2_kannon_left > 0:
                p2_weapon = "kannon"
            else:
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

# Survival Mode Implementation
def run_survival_mode(num_players, player1_name, player2_name, player3_name, char_choices, p1_upgrades, p2_upgrades):
    """
    Run survival mode for 1, 2, or 3 players with enemies spawning in waves.
    Players must survive as long as possible against increasing difficulty.
    """
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load('fart.mp3')
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Error playing background music: {e}")
    
    # Initialize players based on number of players
    players = []
    player_names = []
    
    if num_players >= 1:
        players.append(pygame.Rect(100, HEIGHT//2, 50, 50))
        player_names.append(player1_name)
    if num_players >= 2:
        players.append(pygame.Rect(WIDTH-150, HEIGHT//2, 50, 50))
        player_names.append(player2_name)
    if num_players >= 3:
        players.append(pygame.Rect(WIDTH//2, 100, 50, 50))
        player_names.append(player3_name)
    
    # Game state variables
    player_healths = [10] * num_players  # Each player starts with 10 health
    player_rights = [True, False, True]  # Direction each player is facing
    speed = 5
    
    # Survival mode specific variables
    score = 0
    level = 1
    enemies = []
    enemy_spawn_timer = 0
    enemy_spawn_rate = 2.0  # Enemies spawn every 2 seconds initially
    enemies_per_wave = 3
    level_timer = time.time() + 30  # Level up every 30 seconds
    
    bullets = []
    player_shots = [0] * num_players
    player_reload_times = [0] * num_players
    RELOAD_LIMIT = 5
    RELOAD_DURATION = 2
    
    start_countdown()
    
    clock = pygame.time.Clock()
    game_over = False
    
    while not game_over:
        now = time.time()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                # Player 1 shooting (Space)
                if event.key == pygame.K_SPACE and num_players >= 1:
                    if player_shots[0] < RELOAD_LIMIT and now > player_reload_times[0]:
                        bx = players[0].right if player_rights[0] else players[0].left - 10
                        bullets.append({'rect': pygame.Rect(bx, players[0].centery-5, 10, 10), 
                                      'dir': 1 if player_rights[0] else -1, 'owner': 0})
                        player_shots[0] += 1
                        if player_shots[0] == RELOAD_LIMIT:
                            player_reload_times[0] = now + RELOAD_DURATION
                
                # Player 2 shooting (Enter)
                if event.key == pygame.K_RETURN and num_players >= 2:
                    if player_shots[1] < RELOAD_LIMIT and now > player_reload_times[1]:
                        bx = players[1].right if player_rights[1] else players[1].left - 10
                        bullets.append({'rect': pygame.Rect(bx, players[1].centery-5, 10, 10), 
                                      'dir': 1 if player_rights[1] else -1, 'owner': 1})
                        player_shots[1] += 1
                        if player_shots[1] == RELOAD_LIMIT:
                            player_reload_times[1] = now + RELOAD_DURATION
                
                # Player 3 shooting (Right Shift)
                if event.key == pygame.K_RSHIFT and num_players >= 3:
                    if player_shots[2] < RELOAD_LIMIT and now > player_reload_times[2]:
                        bx = players[2].right if player_rights[2] else players[2].left - 10
                        bullets.append({'rect': pygame.Rect(bx, players[2].centery-5, 10, 10), 
                                      'dir': 1 if player_rights[2] else -1, 'owner': 2})
                        player_shots[2] += 1
                        if player_shots[2] == RELOAD_LIMIT:
                            player_reload_times[2] = now + RELOAD_DURATION
        
        # Reset shots after reload
        for i in range(num_players):
            if player_shots[i] == RELOAD_LIMIT and now > player_reload_times[i]:
                player_shots[i] = 0
        
        # Player movement
        keys = pygame.key.get_pressed()
        
        # Player 1 controls (WASD)
        if num_players >= 1:
            if keys[pygame.K_a]:
                players[0].x -= speed
                player_rights[0] = False
            if keys[pygame.K_d]:
                players[0].x += speed
                player_rights[0] = True
            if keys[pygame.K_w]:
                players[0].y -= speed
            if keys[pygame.K_s]:
                players[0].y += speed
        
        # Player 2 controls (Arrow keys)
        if num_players >= 2:
            if keys[pygame.K_LEFT]:
                players[1].x -= speed
                player_rights[1] = False
            if keys[pygame.K_RIGHT]:
                players[1].x += speed
                player_rights[1] = True
            if keys[pygame.K_UP]:
                players[1].y -= speed
            if keys[pygame.K_DOWN]:
                players[1].y += speed
        
        # Player 3 controls (IJKL)
        if num_players >= 3:
            if keys[pygame.K_j]:
                players[2].x -= speed
                player_rights[2] = False
            if keys[pygame.K_l]:
                players[2].x += speed
                player_rights[2] = True
            if keys[pygame.K_i]:
                players[2].y -= speed
            if keys[pygame.K_k]:
                players[2].y += speed
        
        # Keep players within bounds
        for player in players:
            if player.left < 0:
                player.left = 0
            if player.right > WIDTH:
                player.right = WIDTH
            if player.top < 0:
                player.top = 0
            if player.bottom > HEIGHT:
                player.bottom = HEIGHT
        
        # Spawn enemies
        if now > enemy_spawn_timer:
            for _ in range(enemies_per_wave):
                # Spawn enemies from random edges
                edge = random.randint(0, 3)  # 0=top, 1=right, 2=bottom, 3=left
                if edge == 0:  # Top
                    enemy = pygame.Rect(random.randint(0, WIDTH-30), -30, 30, 30)
                elif edge == 1:  # Right
                    enemy = pygame.Rect(WIDTH, random.randint(0, HEIGHT-30), 30, 30)
                elif edge == 2:  # Bottom
                    enemy = pygame.Rect(random.randint(0, WIDTH-30), HEIGHT, 30, 30)
                else:  # Left
                    enemy = pygame.Rect(-30, random.randint(0, HEIGHT-30), 30, 30)
                
                enemies.append({'rect': enemy, 'health': 2})
            
            enemy_spawn_timer = now + enemy_spawn_rate
        
        # Move enemies toward nearest player
        for enemy in enemies[:]:
            # Find nearest player
            nearest_dist = float('inf')
            target_player = None
            for i, player in enumerate(players):
                if player_healths[i] > 0:  # Only target alive players
                    dist = ((enemy['rect'].centerx - player.centerx)**2 + (enemy['rect'].centery - player.centery)**2)**0.5
                    if dist < nearest_dist:
                        nearest_dist = dist
                        target_player = player
            
            if target_player:
                # Move enemy toward target
                dx = target_player.centerx - enemy['rect'].centerx
                dy = target_player.centery - enemy['rect'].centery
                dist = (dx**2 + dy**2)**0.5
                if dist > 0:
                    enemy_speed = min(2 + level * 0.2, 4)  # Enemies get faster each level
                    enemy['rect'].x += int((dx / dist) * enemy_speed)
                    enemy['rect'].y += int((dy / dist) * enemy_speed)
        
        # Move bullets
        for bullet in bullets[:]:
            bullet['rect'].x += bullet['dir'] * 8
            if bullet['rect'].x < 0 or bullet['rect'].x > WIDTH:
                bullets.remove(bullet)
        
        # Bullet-enemy collisions
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet['rect'].colliderect(enemy['rect']):
                    enemy['health'] -= 1
                    bullets.remove(bullet)
                    if enemy['health'] <= 0:
                        enemies.remove(enemy)
                        score += 10 * level  # More points for higher levels
                    break
        
        # Enemy-player collisions
        for enemy in enemies[:]:
            for i, player in enumerate(players):
                if player_healths[i] > 0 and enemy['rect'].colliderect(player):
                    player_healths[i] -= 1
                    enemies.remove(enemy)
                    break
        
        # Check if all players are dead
        if all(health <= 0 for health in player_healths):
            game_over = True
        
        # Level progression
        if now > level_timer:
            level += 1
            level_timer = now + 30
            enemy_spawn_rate = max(0.5, enemy_spawn_rate - 0.1)  # Spawn enemies faster
            enemies_per_wave = min(8, enemies_per_wave + 1)  # More enemies per wave
        
        # Draw everything
        screen.fill((20, 20, 20))  # Dark background for survival mode
        
        # Draw border
        pygame.draw.rect(screen, (100, 100, 100), (0, 0, WIDTH, HEIGHT), 5)
        
        # Draw players
        for i, player in enumerate(players):
            if player_healths[i] > 0:
                draw_survivor_character(screen, player.centerx, player.centery, char_choices[i])
                
                # Draw player name and health
                name_color = [(0,0,255), (255,0,0), (0,255,0)][i]
                name_text = font.render(f"{player_names[i]}: {player_healths[i]}HP", True, name_color)
                screen.blit(name_text, (player.centerx - name_text.get_width()//2, player.centery-70))
        
        # Draw enemies
        for enemy in enemies:
            pygame.draw.rect(screen, (139, 0, 0), enemy['rect'])  # Dark red enemies
            pygame.draw.rect(screen, (255, 255, 255), enemy['rect'], 2)  # White border
        
        # Draw bullets
        for bullet in bullets:
            pygame.draw.rect(screen, (255, 255, 0), bullet['rect'])
        
        # Draw UI
        score_text = lobby_font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))
        
        level_text = lobby_font.render(f"Level: {level}", True, (255, 255, 255))
        screen.blit(level_text, (20, 60))
        
        enemies_text = font.render(f"Enemies: {len(enemies)}", True, (255, 255, 255))
        screen.blit(enemies_text, (20, 100))
        
        # Show reload status for each player
        for i in range(num_players):
            if player_healths[i] > 0:
                if player_shots[i] < RELOAD_LIMIT and now > player_reload_times[i]:
                    status = f"P{i+1} Shots: {RELOAD_LIMIT - player_shots[i]}"
                else:
                    status = f"P{i+1} Reloading..."
                status_text = font.render(status, True, [(0,0,255), (255,0,0), (0,255,0)][i])
                screen.blit(status_text, (WIDTH - 200, 20 + i*30))
        
        # Show controls
        controls_text = font.render("P1: WASD+Space | P2: Arrows+Enter | P3: IJKL+RShift", True, (150, 150, 150))
        screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)
    
    # Game Over Screen with High Score Integration
    pygame.mixer.music.stop()
    
    # Add score to high scores and get updated leaderboard
    active_player_names = [name for i, name in enumerate(player_names) if name]
    updated_highscores = add_highscore(active_player_names, score, level)
    current_rank = get_player_rank(active_player_names, score, level)
    
    # Get all-time high score
    all_highscores = load_highscores()
    all_time_high = all_highscores[0] if all_highscores else None
    
    # Interactive game over screen
    waiting_for_input = True
    while waiting_for_input:
        screen.fill((30, 30, 30))
        
        # Title
        game_over_text = lobby_font.render("SURVIVAL MODE - GAME OVER", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 200))
        
        # Final stats
        final_score_text = lobby_font.render(f"Final Score: {score}", True, (255, 255, 255))
        screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2 - 140))
        
        final_level_text = lobby_font.render(f"Reached Level: {level}", True, (255, 255, 255))
        screen.blit(final_level_text, (WIDTH//2 - final_level_text.get_width()//2, HEIGHT//2 - 110))
        
        # Current players' high score info
        if len(active_player_names) == 1:
            player_text = f"{active_player_names[0]}'s"
        else:
            player_text = " & ".join([name for name in active_player_names if name])
        
        rank_text = font.render(f"{player_text} Rank: #{current_rank}", True, (0, 255, 255))
        screen.blit(rank_text, (WIDTH//2 - rank_text.get_width()//2, HEIGHT//2 - 60))
        
        # All-time high score
        if all_time_high:
            all_time_text = font.render(f"All-Time High Score: {all_time_high['names']}", True, (255, 215, 0))
            screen.blit(all_time_text, (WIDTH//2 - all_time_text.get_width()//2, HEIGHT//2 - 30))
            
            all_time_score_text = font.render(f"Score: {all_time_high['score']} (Level {all_time_high['level']})", True, (255, 215, 0))
            screen.blit(all_time_score_text, (WIDTH//2 - all_time_score_text.get_width()//2, HEIGHT//2))
        else:
            no_scores_text = font.render("No previous high scores", True, (150, 150, 150))
            screen.blit(no_scores_text, (WIDTH//2 - no_scores_text.get_width()//2, HEIGHT//2 - 15))
        
        # Back to menu button
        back_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 50)
        pygame.draw.rect(screen, (100, 100, 100), back_button)
        back_text = font.render("Back to Menu", True, (255, 255, 255))
        screen.blit(back_text, (back_button.centerx - back_text.get_width()//2, back_button.centery - back_text.get_height()//2))
        
        # Show leaderboard preview
        leaderboard_title = font.render("Top 5 High Scores:", True, (200, 200, 200))
        screen.blit(leaderboard_title, (WIDTH//2 - leaderboard_title.get_width()//2, HEIGHT//2 + 130))
        
        for i, entry in enumerate(updated_highscores[:5]):
            if i < 5:  # Show top 5
                color = (255, 215, 0) if i == 0 else (192, 192, 192) if i == 1 else (205, 127, 50) if i == 2 else (255, 255, 255)
                entry_text = font.render(f"{i+1}. {entry['names']}: {entry['score']} (Lvl {entry['level']})", True, color)
                screen.blit(entry_text, (WIDTH//2 - entry_text.get_width()//2, HEIGHT//2 + 160 + i*25))
        
        pygame.display.flip()
        
        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    waiting_for_input = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    waiting_for_input = False

# High Score System for Survival Mode
HIGHSCORE_FILE = "survival_highscores.json"

def load_highscores():
    """Load high scores from file, return empty list if file doesn't exist"""
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, 'r') as f:
                return json.load(f)
        return []
    except:
        return []

def save_highscores(highscores):
    """Save high scores to file"""
    try:
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump(highscores, f, indent=2)
    except:
        pass  # Fail silently if can't save

def add_highscore(player_names, score, level):
    """Add a new high score entry and maintain top 10"""
    highscores = load_highscores()
    
    # Create player name string
    if len(player_names) == 1:
        name_str = player_names[0]
    else:
        name_str = " & ".join([name for name in player_names if name])
    
    new_entry = {
        "names": name_str,
        "score": score,
        "level": level,
        "players": len([name for name in player_names if name]),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    highscores.append(new_entry)
    # Sort by score (highest first), then by level
    highscores.sort(key=lambda x: (x["score"], x["level"]), reverse=True)
    
    # Keep only top 10
    highscores = highscores[:10]
    
    save_highscores(highscores)
    return highscores

def get_player_rank(player_names, score, level):
    """Get the rank of the current players in the all-time leaderboard"""
    highscores = load_highscores()
    
    # Count how many scores are better than current score
    better_scores = 0
    for entry in highscores:
        if entry["score"] > score or (entry["score"] == score and entry["level"] > level):
            better_scores += 1
    
    return better_scores + 1  # Rank is 1-based

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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if local_rect.collidepoint(event.pos):
                        player1_name = get_player_name("Player 1, enter your name:", HEIGHT//2 - 120)
                        player2_name = get_player_name("Player 2, enter your name:", HEIGHT//2 + 40)
                        char_choices = character_select(0)  # Mafia mode
                        # Go straight to battle, no shop, no upgrades
                        result = run_game_with_upgrades(player1_name, player2_name, char_choices, 0, 0, 0, 0, 0, 0, mode=0)
                        if result == 'lobby':
                            break  # Return to main menu
                    if back_rect.collidepoint(event.pos):
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
                    if back_rect.collidepoint(event.pos):
                        break
            else:
                continue
            break  # Always return to main menu after game ends
    elif mode == 2:
        # Show Play Local / Play Online selection for Survival Mode
        selected = 0
        options = ["Play Local", "Play Online (Coming Soon)"]
        while True:
            screen.fill((30, 30, 30))
            title = lobby_font.render("Survival Mode", True, (255,255,255))
            screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-120))
            
            for i, option in enumerate(options):
                y_pos = HEIGHT//2-20 + i*60
                rect = pygame.Rect(WIDTH//2-120, y_pos, 240, 50)
                color = (0,100,200) if option == "Play Local" else (100,100,100)
                pygame.draw.rect(screen, color, rect)
                option_text = font.render(option, True, (255,255,255))
                screen.blit(option_text, (rect.centerx-option_text.get_width()//2, rect.centery-option_text.get_height()//2))
            
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
                    if options[0] == "Play Local" and HEIGHT//2-20 <= event.pos[1] <= HEIGHT//2+30 and WIDTH//2-120 <= event.pos[0] <= WIDTH//2+120:
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
                    if back_rect.collidepoint(event.pos):
                        break
            else:
                continue
            break  # Always return to main menu after game ends











