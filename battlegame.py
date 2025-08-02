import pygame
import sys
import time
import random
import threading
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
    else:
        options = [0, 1, 2]  # Explorer styles
        names = ["Jungle Explorer", "Desert Adventurer", "Arctic Explorer"]
        draw_func = draw_explorer_character
    selected1 = 0
    selected2 = 0
    p1_done = False
    p2_done = False
    preview_y = HEIGHT//2+20
    preview_xs = [WIDTH//2-180, WIDTH//2, WIDTH//2+180]
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

# Main game loop refactored into a function

def run_game(mode, player1_name, player2_name, char_choices):
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

    start_countdown()
    countdown_done = True

    while True:
        now = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if mode == 0:
                if event.type == pygame.KEYDOWN:
                    # Player 1 shoot (space only)
                    if event.key == pygame.K_SPACE:
                        if player1_shots < RELOAD_LIMIT and now > player1_reload_time:
                            bx = player1.right if p1_right else player1.left - 10
                            bullets.append({'rect': pygame.Rect(bx, player1.centery-5, 10, 10), 'dir': 1 if p1_right else -1, 'owner': 1})
                            player1_shots += 1
                            if player1_shots == RELOAD_LIMIT:
                                player1_reload_time = now + RELOAD_DURATION
                        else:
                            pass  # Optionally show reload message
                    # Player 2 shoot (right shift)
                    if event.key == pygame.K_RSHIFT:
                        if player2_shots < RELOAD_LIMIT and now > player2_reload_time:
                            bx = player2.right if p2_right else player2.left - 10
                            bullets.append({'rect': pygame.Rect(bx, player2.centery-5, 10, 10), 'dir': 1 if p2_right else -1, 'owner': 2})
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
                player2_health -= 1
                bullets.remove(bullet)
            elif bullet['owner'] == 2 and bullet['rect'].colliderect(player1_hitbox):
                player1_health -= 1
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
        pygame.draw.rect(screen, (0,0,0), (player2.centerx-12, player2.centery-28, 24, 8))
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
            # Draw Player 1 gun
            if char_choices[0] == 2:  # Mafia Hitman with enhanced shotgun
                if p1_right:
                    hand_x = player1.centerx+20
                    hand_y = gun_offset_y1
                    # Barrel (long, metallic)
                    pygame.draw.rect(screen, (160,160,160), (hand_x, hand_y-5, 44, 7))
                    # Muzzle
                    pygame.draw.ellipse(screen, (200,200,200), (hand_x+44, hand_y-7, 8, 11))
                    # Pump
                    pygame.draw.rect(screen, (100,100,100), (hand_x+18, hand_y-7, 12, 11))
                    # Stock (wood)
                    pygame.draw.polygon(screen, (139,69,19), [(hand_x-16, hand_y-8), (hand_x, hand_y-8), (hand_x, hand_y+6), (hand_x-10, hand_y+14)])
                    # Trigger guard
                    pygame.draw.arc(screen, (60,60,60), (hand_x+8, hand_y+2, 8, 6), 3.14, 2*3.14, 2)
                else:
                    hand_x = player1.centerx-20
                    hand_y = gun_offset_y1
                    pygame.draw.rect(screen, (160,160,160), (hand_x-52, hand_y-5, 44, 7))
                    pygame.draw.ellipse(screen, (200,200,200), (hand_x-60, hand_y-7, 8, 11))
                    pygame.draw.rect(screen, (100,100,100), (hand_x-40, hand_y-7, 12, 11))
                    pygame.draw.polygon(screen, (139,69,19), [(hand_x, hand_y-8), (hand_x-16, hand_y-8), (hand_x-16, hand_y+6), (hand_x-6, hand_y+14)])
                    pygame.draw.arc(screen, (60,60,60), (hand_x-16, hand_y+2, 8, 6), 0, 3.14, 2)
            else:
                # AK-47 for other mafia
                if p1_right:
                    hand_x = player1.centerx+20
                    hand_y = gun_offset_y1
                    pygame.draw.rect(screen, (80,80,80), (hand_x+20, hand_y-4, 22, 4))
                    pygame.draw.rect(screen, (139,69,19), (hand_x-18, hand_y-7, 16, 8))
                    pygame.draw.rect(screen, (80,80,80), (hand_x, hand_y-7, 38, 8))
                    pygame.draw.arc(screen, (60,60,60), (hand_x+10, hand_y+2, 18, 14), 3.14, 2*3.14, 4)
                    pygame.draw.rect(screen, (60,60,60), (hand_x+30, hand_y+2, 6, 12))
                else:
                    hand_x = player1.centerx-20
                    hand_y = gun_offset_y1
                    pygame.draw.rect(screen, (80,80,80), (hand_x-42, hand_y-4, 22, 4))
                    pygame.draw.rect(screen, (139,69,19), (hand_x+2, hand_y-7, 16, 8))
                    pygame.draw.rect(screen, (80,80,80), (hand_x-38, hand_y-7, 38, 8))
                    pygame.draw.arc(screen, (60,60,60), (hand_x-28, hand_y+2, 18, 14), 0, 3.14, 4)
                    pygame.draw.rect(screen, (60,60,60), (hand_x-36, hand_y+2, 6, 12))
            # Draw Player 2 gun
            if char_choices[1] == 2:  # Mafia Hitman with enhanced shotgun
                if p2_right:
                    hand_x = player2.centerx+20
                    hand_y = gun_offset_y2
                    pygame.draw.rect(screen, (160,160,160), (hand_x, hand_y-5, 44, 7))
                    pygame.draw.ellipse(screen, (200,200,200), (hand_x+44, hand_y-7, 8, 11))
                    pygame.draw.rect(screen, (100,100,100), (hand_x+18, hand_y-7, 12, 11))
                    pygame.draw.polygon(screen, (139,69,19), [(hand_x-16, hand_y-8), (hand_x, hand_y-8), (hand_x, hand_y+6), (hand_x-10, hand_y+14)])
                    pygame.draw.arc(screen, (60,60,60), (hand_x+8, hand_y+2, 8, 6), 3.14, 2*3.14, 2)
                else:
                    hand_x = player2.centerx-20
                    hand_y = gun_offset_y2
                    pygame.draw.rect(screen, (160,160,160), (hand_x-52, hand_y-5, 44, 7))
                    pygame.draw.ellipse(screen, (200,200,200), (hand_x-60, hand_y-7, 8, 11))
                    pygame.draw.rect(screen, (100,100,100), (hand_x-40, hand_y-7, 12, 11))
                    pygame.draw.polygon(screen, (139,69,19), [(hand_x, hand_y-8), (hand_x-16, hand_y-8), (hand_x-16, hand_y+6), (hand_x-6, hand_y+14)])
                    pygame.draw.arc(screen, (60,60,60), (hand_x-16, hand_y+2, 8, 6), 0, 3.14, 2)
            else:
                # AK-47 for other mafia
                if p2_right:
                    hand_x = player2.centerx+20
                    hand_y = gun_offset_y2
                    pygame.draw.rect(screen, (80,80,80), (hand_x+20, hand_y-4, 22, 4))
                    pygame.draw.rect(screen, (139,69,19), (hand_x-18, hand_y-7, 16, 8))
                    pygame.draw.rect(screen, (80,80,80), (hand_x, hand_y-7, 38, 8))
                    pygame.draw.arc(screen, (60,60,60), (hand_x+10, hand_y+2, 18, 14), 3.14, 2*3.14, 4)
                    pygame.draw.rect(screen, (60,60,60), (hand_x+30, hand_y+2, 6, 12))
                else:
                    hand_x = player2.centerx-20
                    hand_y = gun_offset_y2
                    pygame.draw.rect(screen, (80,80,80), (hand_x-42, hand_y-4, 22, 4))
                    pygame.draw.rect(screen, (139,69,19), (hand_x+2, hand_y-7, 16, 8))
                    pygame.draw.rect(screen, (80,80,80), (hand_x-38, hand_y-7, 38, 8))
                    pygame.draw.arc(screen, (60,60,60), (hand_x-28, hand_y+2, 18, 14), 0, 3.14, 4)
                    pygame.draw.rect(screen, (60,60,60), (hand_x-36, hand_y+2, 6, 12))

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
            return
        if player1_health <= 0:
            win_text = font.render("Player 2 Wins!", True, (255, 0, 0))
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.mixer.music.stop()
            return
        if player2_health <= 0:
            win_text = font.render("Player 1 Wins!", True, (0, 0, 255))
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.mixer.music.stop()
            return

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
                return

        pygame.display.flip()
        clock.tick(60)

# Re-add Coin Collection mode

def run_coin_collection(player1_name, player2_name, char_choices):
    player1_score = 0
    player2_score = 0
    coin_rects = []
    coin_timer = time.time() + 30
    player1 = pygame.Rect(100, HEIGHT//2, 50, 50)
    player2 = pygame.Rect(WIDTH-150, HEIGHT//2, 50, 50)
    speed = 6
    for _ in range(10):
        x = random.randint(60, WIDTH-60)
        y = random.randint(100, HEIGHT-60)
        coin_rects.append(pygame.Rect(x, y, 24, 24))
    start_countdown()
    while time.time() < coin_timer:
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
        for coin in coin_rects[:]:
            if p1_body.colliderect(coin):
                player1_score += 1
                coin_rects.remove(coin)
            elif p2_body.colliderect(coin):
                player2_score += 1
                coin_rects.remove(coin)
        while len(coin_rects) < 10:
            x = random.randint(60, WIDTH-60)
            y = random.randint(100, HEIGHT-60)
            coin_rects.append(pygame.Rect(x, y, 24, 24))
        screen.fill((30,30,30))
        for coin in coin_rects:
            pygame.draw.circle(screen, (255,215,0), coin.center, 12)
        draw_explorer_character(screen, player1.centerx, player1.centery, char_choices[0])
        draw_explorer_character(screen, player2.centerx, player2.centery, char_choices[1])
        score_text = font.render(f"{player1_name}: {player1_score}   {player2_name}: {player2_score}", True, (255,255,255))
        screen.blit(score_text, (WIDTH//2-score_text.get_width()//2, 20))
        timer_text = font.render(f"Time left: {int(coin_timer-time.time())}", True, (255,255,255))
        screen.blit(timer_text, (WIDTH//2-timer_text.get_width()//2, 60))
        pygame.display.flip()
        clock.tick(60)
    winner = player1_name if player1_score > player2_score else player2_name if player2_score > player1_score else "Tie!"
    win_text = font.render(f"Winner: {winner}", True, (0,255,0))
    screen.blit(win_text, (WIDTH//2-win_text.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.mixer.music.stop()
    return

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
    run_game_with_upgrades(player1_name, player2_name, mafia_choices, p1_bazooka, p2_bazooka, p1_kannon, p2_kannon, p1_life, p2_life)
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

def run_game_with_upgrades(player1_name, player2_name, char_choices, p1_bazooka, p2_bazooka, p1_kannon, p2_kannon, p1_life, p2_life):
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
    # Track bazooka/kannon shots left
    p1_bazooka_left = 2 * p1_bazooka
    p2_bazooka_left = 2 * p2_bazooka
    p1_kannon_left = 2 * p1_kannon
    p2_kannon_left = 2 * p2_kannon
    # Weapon selection state
    p1_weapon = "default"
    p2_weapon = "default"
    start_countdown()
    while True:
        now = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Weapon switching
                if event.key == pygame.K_q:
                    p1_weapon = "default"
                if event.key == pygame.K_e:
                    p1_weapon = "bazooka"
                if event.key == pygame.K_r:
                    p1_weapon = "kannon"
                if event.key == pygame.K_o:
                    p2_weapon = "default"
                if event.key == pygame.K_p:
                    p2_weapon = "bazooka"
                if event.key == pygame.K_l:
                    p2_weapon = "kannon"
                # Player 1 shoot (space)
                if event.key == pygame.K_SPACE:
                    if player1_shots < RELOAD_LIMIT and now > player1_reload_time:
                        bx = player1.right if p1_right else player1.left - 10
                        # Use selected weapon's upgrade shots if available
                        if p1_weapon == "bazooka" and p1_bazooka_left > 0:
                            damage = 2
                            p1_bazooka_left -= 1
                        elif p1_weapon == "kannon" and p1_kannon_left > 0:
                            damage = 3
                            p1_kannon_left -= 1
                        else:
                            damage = 1
                        bullets.append({'rect': pygame.Rect(bx, player1.centery-5, 10, 10), 'dir': 1 if p1_right else -1, 'owner': 1, 'damage': damage, 'weapon': p1_weapon})
                        player1_shots += 1
                        if player1_shots == RELOAD_LIMIT:
                            player1_reload_time = now + RELOAD_DURATION
                # Player 2 shoot (right shift)
                if event.key == pygame.K_RSHIFT:
                    if player2_shots < RELOAD_LIMIT and now > player2_reload_time:
                        bx = player2.right if p2_right else player2.left - 10
                        if p2_weapon == "bazooka" and p2_bazooka_left > 0:
                            damage = 2
                            p2_bazooka_left -= 1
                        elif p2_weapon == "kannon" and p2_kannon_left > 0:
                            damage = 3
                            p2_kannon_left -= 1
                        else:
                            damage = 1
                        bullets.append({'rect': pygame.Rect(bx, player2.centery-5, 10, 10), 'dir': 1 if p2_right else -1, 'owner': 2, 'damage': damage, 'weapon': p2_weapon})
                        player2_shots += 1
                        if player2_shots == RELOAD_LIMIT:
                            player2_reload_time = now + RELOAD_DURATION
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
        # Hitboxes
        player1_hitbox = pygame.Rect(player1.centerx-20, player1.centery-35, 40, 110)
        player2_hitbox = pygame.Rect(player2.centerx-20, player2.centery-35, 40, 110)
              
              
              
        # Move bullets
        for bullet in bullets[:]:
            bullet['rect'].x += bullet['dir'] * 12
            if bullet['rect'].right < 0 or bullet['rect'].left > WIDTH:
                bullets.remove(bullet)
            elif bullet['owner'] == 1 and bullet['rect'].colliderect(player2_hitbox):
                player2_health -= bullet['damage']
                bullets.remove(bullet)
            elif bullet['owner'] == 2 and bullet['rect'].colliderect(player1_hitbox):
                player1_health -= bullet['damage']
                bullets.remove(bullet)
        # Collision: if players touch, reduce health
        if player1.colliderect(player2):
            player1_health -= 1
            player2_health -= 1
            player1.x = 100
            player1.y = HEIGHT//2
            player2.x = WIDTH-150
            player2.y = HEIGHT//2
        # Border collision
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
        # Draw everything (reuse battle mode visuals)
        screen.fill((30, 30, 30))
        border_color = (200, 200, 200)
        border_thickness = 8
        pygame.draw.rect(screen, border_color, (0, 0, WIDTH, HEIGHT), border_thickness)
        draw_mafia_character(screen, player1.centerx, player1.centery, char_choices[0])
        draw_mafia_character(screen, player2.centerx, player2.centery, char_choices[1])
        name_text1 = font.render(player1_name, True, (0,0,255))
        screen.blit(name_text1, (player1.centerx - name_text1.get_width()//2, player1.centery-60))
        name_text2 = font.render(player2_name, True, (255,0,0))
        screen.blit(name_text2, (player2.centerx - name_text2.get_width()//2, player2.centery-60))
        # Draw Player 1 weapon
        gun_offset_y1 = player1.centery+10
        hand_x1 = player1.centerx+20 if p1_right else player1.centerx-20
        draw_weapon(screen, hand_x1, gun_offset_y1, p1_right, p1_weapon)
        # Draw Player 2 weapon
        gun_offset_y2 = player2.centery+10
        hand_x2 = player2.centerx+20 if p2_right else player2.centerx-20
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
        # Show bazooka/kannon shots left
        upgrade_text1 = font.render(f"Bazooka:{p1_bazooka_left} Kannon:{p1_kannon_left}", True, (0,255,0))
        upgrade_text2 = font.render(f"Bazooka:{p2_bazooka_left} Kannon:{p2_kannon_left}", True, (255,255,0))
        screen.blit(upgrade_text1, (40, 60))
        screen.blit(upgrade_text2, (WIDTH-40-upgrade_text2.get_width(), 60))
        p1_status_text = font.render(p1_status, True, (0,0,255))
        p2_status_text = font.render(p2_status, True, (255,0,0))
        screen.blit(p1_status_text, (40, 20))
        screen.blit(p2_status_text, (WIDTH-40-p2_status_text.get_width(), 20))
        # Show weapon switch instructions
        instructions1 = font.render("P1: Q=Default, E=Bazooka, R=Kannon", True, (0,255,0))
        instructions2 = font.render("P2: O=Default, P=Bazooka, L=Kannon", True, (255,255,0))
        screen.blit(instructions1, (40, HEIGHT-80))
        screen.blit(instructions2, (WIDTH-40-instructions2.get_width(), HEIGHT-80))
        # Win logic
        if player1_health <= 0 and player2_health <= 0:
            win_text = font.render("Tie!", True, (0,255,0))
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.mixer.music.stop()
            return
        if player1_health <= 0:
            win_text = font.render("Player 2 Wins!", True, (255, 0, 0))
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.mixer.music.stop()
            return
        if player2_health <= 0:
            win_text = font.render("Player 1 Wins!", True, (0, 0, 255))
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.mixer.music.stop()
            return
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
    pygame.draw.line(screen, color, (rect.right-14, leg_y), (rect.right-14, leg_y+18), 8)
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

def run_survival_mode(player1_name, player2_name, char_choices):
    # 2-player survival mode with realistic monsters, easier levels
    level = 1
    score = 0
    player1 = pygame.Rect(WIDTH//3, HEIGHT-120, 50, 50)
    player2 = pygame.Rect(2*WIDTH//3, HEIGHT-120, 50, 50)
    speed = 8
    monsters = []
    monster_speed = 1
    monster_size = 40
    bullets = []
    font_big = pygame.font.SysFont(None, 72)
    barrier = {'rect': pygame.Rect(60, HEIGHT-200, WIDTH-120, 24), 'hp': 50}
    running = True
    start_countdown()
    while running:
        # Spawn fewer monsters per level, slower scaling
        if not monsters:
            for _ in range(2 + level//2):  # 2 + level//2 monsters per wave (slower increase)
                x = random.randint(60, WIDTH-60)
                y = random.randint(-300, -40)
                color = (random.randint(80,200), random.randint(80,200), random.randint(80,200))
                monsters.append({'rect': pygame.Rect(x, y, monster_size, monster_size), 'hp': 2 + level//4, 'color': color})
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Player 1 shoot (space)
                if event.key == pygame.K_SPACE:
                    bullets.append({'rect': pygame.Rect(player1.centerx-5, player1.top-10, 10, 20), 'dir': -1, 'owner': 1})
                # Player 2 shoot (right shift)
                if event.key == pygame.K_RSHIFT:
                    bullets.append({'rect': pygame.Rect(player2.centerx-5, player2.top-10, 10, 20), 'dir': -1, 'owner': 2})
        keys = pygame.key.get_pressed()
        # Player 1 controls (WASD)
        if keys[pygame.K_a]: player1.x -= speed
        if keys[pygame.K_d]: player1.x += speed
        player1.clamp_ip(pygame.Rect(0,0,WIDTH,HEIGHT))
        # Player 2 controls (Arrow keys)
        if keys[pygame.K_LEFT]: player2.x -= speed
        if keys[pygame.K_RIGHT]: player2.x += speed
        player2.clamp_ip(pygame.Rect(0,0,WIDTH,HEIGHT))
        # Move monsters
        for m in monsters:
            m['rect'].y += monster_speed + level//6  # even slower speed increase
        # Move bullets
        for bullet in bullets[:]:
            bullet['rect'].y += bullet['dir'] * 16
            if bullet['rect'].bottom < 0:
                bullets.remove(bullet)
        # Bullet-monster collision
        for bullet in bullets[:]:
            hit = False
            for m in monsters:
                parts = draw_monster(screen, m['rect'], m['color'], m['hp'])
                corners = [bullet['rect'].topleft, bullet['rect'].topright, bullet['rect'].bottomleft, bullet['rect'].bottomright]
                # Check collision with each body part
                if any(point_in_polygon(x, y, parts['body']) for (x, y) in corners) or \
                   any(parts['left_arm'].collidepoint(x, y) for (x, y) in corners) or \
                   any(parts['right_arm'].collidepoint(x, y) for (x, y) in corners) or \
                   any(parts['left_leg'].collidepoint(x, y) for (x, y) in corners) or \
                   any(parts['right_leg'].collidepoint(x, y) for (x, y) in corners) or \
                   any(parts['head'].collidepoint(x, y) for (x, y) in corners):
                    m['hp'] -= 1
                    if m['hp'] <= 0:
                        monsters.remove(m)
                        score += 1
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
        screen.fill((20,20,30))
        draw_mafia_character(screen, player1.centerx, player1.centery, char_choices[0])
        draw_mafia_character(screen, player2.centerx, player2.centery, char_choices[1])
        pygame.draw.rect(screen, (100,100,255), barrier['rect'])
        barrier_hp = font.render(f"Barrier HP: {barrier['hp']}", True, (255,255,255))
        screen.blit(barrier_hp, (barrier['rect'].centerx-barrier_hp.get_width()//2, barrier['rect'].top-30))
        for m in monsters:
            draw_monster(screen, m['rect'], m['color'], m['hp'])
        for bullet in bullets:
            pygame.draw.rect(screen, (255,255,0), bullet['rect'])
        score_text = font.render(f"Score: {score}", True, (255,255,255))
        screen.blit(score_text, (40, 20))
        level_text = font.render(f"Level: {level}", True, (0,255,0))
        screen.blit(level_text, (WIDTH-200, 20))
        if not monsters:
            # Level up
            level += 1
            monster_speed += 0.5  # slower speed increase per level
            monster_size = max(30, monster_size-1)  # slower size reduction
            pygame.time.wait(1000)
        if not running:
            gameover_text = font_big.render("Game Over!", True, (255,0,0))
            screen.blit(gameover_text, (WIDTH//2-gameover_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2500)
            pygame.mixer.music.stop()
            return
        pygame.display.flip()
        clock.tick(60)

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
            for i, opt in enumerate(options):
                color = (255,255,0) if i==selected else (200,200,200)
                opt_text = font.render(opt, True, color)
                screen.blit(opt_text, (WIDTH//2-opt_text.get_width()//2, HEIGHT//2-40+i*80))
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
                        if selected == 0:
                            player1_name = get_player_name("Player 1, enter your name:", HEIGHT//2 - 120)
                            player2_name = get_player_name("Player 2, enter your name:", HEIGHT//2 + 40)
                            char_choices = character_select(mode)
                            run_game(0, player1_name, player2_name, char_choices)  # Local Battle Mode
                            break
                        elif selected == 1:
                            # Online lobby: Host or Join
                            online_selected = 0
                            online_options = ["Host Game", "Join Game"]
                            while True:
                                screen.fill((30,30,30))
                                title = lobby_font.render("Online Battle Mode", True, (255,255,255))
                                screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-120))
                                for i, opt in enumerate(online_options):
                                    color = (255,255,0) if i==online_selected else (200,200,200)
                                    opt_text = font.render(opt, True, color)
                                    screen.blit(opt_text, (WIDTH//2-opt_text.get_width()//2, HEIGHT//2-40+i*80))
                                pygame.display.flip()
                                for event in pygame.event.get():
                                    if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()
                                    if event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_UP:
                                            online_selected = (online_selected-1)%len(online_options)
                                        if event.key == pygame.K_DOWN:
                                            online_selected = (online_selected+1)%len(online_options)
                                        if event.key == pygame.K_RETURN:
                                            if online_selected == 0:
                                                # Host Game: show IP, wait for connection
                                                import socket
                                                hostname = socket.gethostname()
                                                ip_addr = socket.gethostbyname(hostname)
                                                waiting = True
                                                exit_button_rect = pygame.Rect(WIDTH//2-100, HEIGHT-120, 200, 60)
                                                host = NetworkHost()
                                                connected = False
                                                while waiting:
                                                    screen.fill((30,30,30))
                                                    info = font.render(f"Your IP: {ip_addr}", True, (0,255,0))
                                                    wait_text = font.render("Waiting for player to join...", True, (255,255,0))
                                                    screen.blit(info, (WIDTH//2-info.get_width()//2, HEIGHT//2-100))
                                                    screen.blit(wait_text, (WIDTH//2-wait_text.get_width()//2, HEIGHT//2-40))
                                                    pygame.draw.rect(screen, (255,0,0), exit_button_rect)
                                                    exit_text = lobby_font.render("Exit", True, (255,255,255))
                                                    screen.blit(exit_text, (exit_button_rect.centerx-exit_text.get_width()//2, exit_button_rect.centery-exit_text.get_height()//2))
                                                    pygame.display.flip()
                                                    for event in pygame.event.get():
                                                        if event.type == pygame.QUIT:
                                                            host.close()
                                                            pygame.quit()
                                                            sys.exit()
                                                        if event.type == pygame.MOUSEBUTTONDOWN:
                                                            if exit_button_rect.collidepoint(event.pos):
                                                                host.close()
                                                                waiting = False
                                                                break
                                                        if event.type == pygame.KEYDOWN:
                                                            if event.key == pygame.K_ESCAPE:
                                                                host.close()
                                                                waiting = False
                                                                break
                                                    if host.conn:
                                                        connected = True
                                                        waiting = False
                                                if connected:
                                                    # Simple handshake
                                                    host.send("hello from host")
                                                    msg = host.recv()
                                                    if msg == "hello from client":
                                                        info = font.render("Connected! Starting game...", True, (0,255,0))
                                                        screen.blit(info, (WIDTH//2-info.get_width()//2, HEIGHT-120))
                                                        pygame.display.flip()
                                                        pygame.time.wait(1500)
                                                        host.close()
                                                break
                                            elif online_selected == 1:
                                                # Join Game: enter IP
                                                ip = ""
                                                entering = True
                                                while entering:
                                                    screen.fill((30,30,30))
                                                    prompt = font.render("Enter Host IP:", True, (255,255,255))
                                                    ip_text = font.render(ip, True, (0,255,0))
                                                    screen.blit(prompt, (WIDTH//2-prompt.get_width()//2, HEIGHT//2-60))
                                                    screen.blit(ip_text, (WIDTH//2-ip_text.get_width()//2, HEIGHT//2))
                                                    info = font.render("Enter: Connect, Esc: Cancel", True, (200,200,200))
                                                    screen.blit(info, (WIDTH//2-info.get_width()//2, HEIGHT-120))
                                                    pygame.display.flip()
                                                    for event in pygame.event.get():
                                                        if event.type == pygame.QUIT:
                                                            pygame.quit()
                                                            sys.exit()
                                                        if event.type == pygame.KEYDOWN:
                                                            if event.key == pygame.K_ESCAPE:
                                                                entering = False
                                                                break
                                                            elif event.key == pygame.K_RETURN:
                                                                # Try to connect
                                                                try:
                                                                    client = NetworkClient(ip)
                                                                    client.send("hello from client")
                                                                    msg = client.recv()
                                                                    if msg == "hello from host":
                                                                        info = font.render("Connected! Starting game...", True, (0,255,0))
                                                                        screen.blit(info, (WIDTH//2-info.get_width()//2, HEIGHT-120))
                                                                        pygame.display.flip()
                                                                        pygame.time.wait(1500)
                                                                        client.close()
                                                                except Exception as e:
                                                                    err = font.render(f"Failed: {e}", True, (255,0,0))
                                                                    screen.blit(err, (WIDTH//2-err.get_width()//2, HEIGHT-60))
                                                                    pygame.display.flip()
                                                                    pygame.time.wait(2000)
                                                                entering = False
                                                                break
                                                            elif event.key == pygame.K_BACKSPACE:
                                                                ip = ip[:-1]
                                                            else:
                                                                if len(event.unicode) == 1 and (event.unicode.isdigit() or event.unicode == "."):
                                                                    ip += event.unicode
                                                break
                                break
    elif mode == 1:
        player1_name = get_player_name("Player 1, enter your name:", HEIGHT//2 - 120)
        player2_name = get_player_name("Player 2, enter your name:", HEIGHT//2 + 40)
        char_choices = character_select(mode)
        run_coin_collection_and_shop(player1_name, player2_name, char_choices)  # Coin Collection + Shop + Battle Mode
    elif mode == 2:
        player1_name = get_player_name("Player 1, enter your name for Survival Mode:", HEIGHT//2-60)
        player2_name = get_player_name("Player 2, enter your name for Survival Mode:", HEIGHT//2+60)
        char_choices = character_select(0)
        run_survival_mode(player1_name, player2_name, char_choices)











