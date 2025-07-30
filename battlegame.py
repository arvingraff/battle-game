import pygame
import sys
import time
import random

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
    options = ["Battle Mode", "Coin Collection Mode", "Play Music", "Stop Music", "Watch Cute Video", "Exit"]
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
                    else:
                        pygame.mixer.music.stop()
                        return selected if options[selected] not in ["Play Music", "Stop Music", "Watch Cute Video"] else None

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
        screen.fill((30,30,30))
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
        pygame.mixer.music.load('coolwav.mp3')
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
    # Start battle mode with upgrades
    run_game_with_upgrades(player1_name, player2_name, char_choices, p1_bazooka, p2_bazooka, p1_kannon, p2_kannon, p1_life, p2_life)
    return

def run_game_with_upgrades(player1_name, player2_name, char_choices, p1_bazooka, p2_bazooka, p1_kannon, p2_kannon, p1_life, p2_life):
    # Battle mode with upgrades: bazooka/kannon = 2 shots each, then normal
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load('coolwav.mp3')
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
    start_countdown()
    while True:
        now = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Player 1 shoot (space)
                if event.key == pygame.K_SPACE:
                    if player1_shots < RELOAD_LIMIT and now > player1_reload_time:
                        bx = player1.right if p1_right else player1.left - 10
                        # Determine damage for next shot
                        if p1_bazooka_left > 0:
                            damage = 2
                            p1_bazooka_left -= 1
                        elif p1_kannon_left > 0:
                            damage = 3
                            p1_kannon_left -= 1
                        else:
                            damage = 1
                        bullets.append({'rect': pygame.Rect(bx, player1.centery-5, 10, 10), 'dir': 1 if p1_right else -1, 'owner': 1, 'damage': damage})
                        player1_shots += 1
                        if player1_shots == RELOAD_LIMIT:
                            player1_reload_time = now + RELOAD_DURATION
                # Player 2 shoot (right shift)
                if event.key == pygame.K_RSHIFT:
                    if player2_shots < RELOAD_LIMIT and now > player2_reload_time:
                        bx = player2.right if p2_right else player2.left - 10
                        if p2_bazooka_left > 0:
                            damage = 2
                            p2_bazooka_left -= 1
                        elif p2_kannon_left > 0:
                            damage = 3
                            p2_kannon_left -= 1
                        else:
                            damage = 1
                        bullets.append({'rect': pygame.Rect(bx, player2.centery-5, 10, 10), 'dir': 1 if p2_right else -1, 'owner': 2, 'damage': damage})
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
        # Draw guns (reuse from battle mode)
        # ...existing gun drawing code can be reused here...
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

# Main program loop
while True:
    mode = mode_lobby()
    player1_name = get_player_name("Player 1, enter your name:", HEIGHT//2 - 120)
    player2_name = get_player_name("Player 2, enter your name:", HEIGHT//2 + 40)
    char_choices = character_select(mode)
    if mode == 0:
        run_game(0, player1_name, player2_name, char_choices)  # Battle Mode
    elif mode == 1:
        run_coin_collection_and_shop(player1_name, player2_name, char_choices)  # Coin Collection + Shop + Battle Mode











