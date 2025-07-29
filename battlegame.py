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

# Play background music in a loop
try:
  pygame.mixer.music.load('coolwav.mp3')
except pygame.error as e:
    print(f"Error loading music file: {e}")
    sys.exit()      
pygame.mixer.music.play(-1)  # -1 means loop forever

# Player settings
player1 = pygame.Rect(100, HEIGHT//2, 50, 50)
player2 = pygame.Rect(WIDTH-150, HEIGHT//2, 50, 50)
player1_health = 5
player2_health = 5
speed = 6

# Direction: True = right, False = left
p1_right = True
p2_right = False

bullets = []  # Each bullet: {'rect': ..., 'dir': ..., 'owner': ...}

font = pygame.font.SysFont(None, 48)
lobby_font = pygame.font.SysFont(None, 64)

player1_shots = 0
player2_shots = 0
player1_reload_time = 0
player2_reload_time = 0
RELOAD_LIMIT = 3
RELOAD_DURATION = 3  # seconds

# Mode selection lobby
def mode_lobby():
    selected = 0
    options = ["Battle Mode", "Coin Collection Mode"]
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
                    return selected
mode = mode_lobby()

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

player1_name = get_player_name("Player 1, enter your name:", HEIGHT//2 - 120)
player2_name = get_player_name("Player 2, enter your name:", HEIGHT//2 + 40)

# Coin collection mode setup
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

    # Collision: if players touch, reduce health
    if player1.colliderect(player2):
        player1_health -= 1
        player2_health -= 1
        player1.x = 100
        player1.y = HEIGHT//2
        player2.x = WIDTH-150
        player2.y = HEIGHT//2

    # Coin collection logic
    if mode == 1:
        # Check for coin collection
        for coin in coin_rects[:]:
            if player1.colliderect(coin):
                player1_score += 1
                coin_rects.remove(coin)
            elif player2.colliderect(coin):
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


    # Draw Player 1 (Blue, more realistic)
    # Head (oval, skin tone)
    pygame.draw.ellipse(screen, (224, 172, 105), (player1.centerx-15, player1.centery-35, 30, 38))
    # Eyes (white sclera, blue iris, black pupil)
    pygame.draw.ellipse(screen, (255,255,255), (player1.centerx-10, player1.centery-25, 8, 12))
    pygame.draw.ellipse(screen, (255,255,255), (player1.centerx+2, player1.centery-25, 8, 12))
    pygame.draw.ellipse(screen, (30,144,255), (player1.centerx-7, player1.centery-21, 4, 6))
    pygame.draw.ellipse(screen, (30,144,255), (player1.centerx+5, player1.centery-21, 4, 6))
    pygame.draw.ellipse(screen, (0,0,0), (player1.centerx-6, player1.centery-19, 2, 3))
    pygame.draw.ellipse(screen, (0,0,0), (player1.centerx+6, player1.centery-19, 2, 3))
    # Eyebrows
    pygame.draw.line(screen, (80, 42, 20), (player1.centerx-10, player1.centery-28), (player1.centerx-2, player1.centery-30), 2)
    pygame.draw.line(screen, (80, 42, 20), (player1.centerx+10, player1.centery-28), (player1.centerx+2, player1.centery-30), 2)
    # Nose
    pygame.draw.line(screen, (160, 110, 60), (player1.centerx, player1.centery-18), (player1.centerx, player1.centery-13), 2)
    # Mouth
    pygame.draw.arc(screen, (150,75,0), (player1.centerx-7, player1.centery-10, 14, 8), 3.14, 2*3.14, 2)
    # Body (shirt)
    pygame.draw.rect(screen, (0, 0, 200), (player1.centerx-10, player1.centery+3, 20, 38))
    # Arms (skin tone)
    pygame.draw.line(screen, (224, 172, 105), (player1.centerx-20, player1.centery+10), (player1.centerx+20, player1.centery+10), 8)
    # Hands
    pygame.draw.circle(screen, (224, 172, 105), (player1.centerx-20, player1.centery+10), 5)
    pygame.draw.circle(screen, (224, 172, 105), (player1.centerx+20, player1.centery+10), 5)
    # Legs (pants)
    pygame.draw.line(screen, (0,0,128), (player1.centerx-5, player1.centery+41), (player1.centerx-5, player1.centery+70), 8)
    pygame.draw.line(screen, (0,0,128), (player1.centerx+5, player1.centery+41), (player1.centerx+5, player1.centery+70), 8)
    # Shoes
    pygame.draw.ellipse(screen, (0,0,0), (player1.centerx-12, player1.centery+68, 14, 8))
    pygame.draw.ellipse(screen, (0,0,0), (player1.centerx-2, player1.centery+68, 14, 8))

    # Draw Player 2 (Red, more realistic)
    pygame.draw.ellipse(screen, (224, 172, 105), (player2.centerx-15, player2.centery-35, 30, 38))
    # Eyes (white sclera, brown iris, black pupil)
    pygame.draw.ellipse(screen, (255,255,255), (player2.centerx-10, player2.centery-25, 8, 12))
    pygame.draw.ellipse(screen, (255,255,255), (player2.centerx+2, player2.centery-25, 8, 12))
    pygame.draw.ellipse(screen, (139,69,19), (player2.centerx-7, player2.centery-21, 4, 6))
    pygame.draw.ellipse(screen, (139,69,19), (player2.centerx+5, player2.centery-21, 4, 6))
    pygame.draw.ellipse(screen, (0,0,0), (player2.centerx-6, player2.centery-19, 2, 3))
    pygame.draw.ellipse(screen, (0,0,0), (player2.centerx+6, player2.centery-19, 2, 3))
    # Eyebrows
    pygame.draw.line(screen, (80, 42, 20), (player2.centerx-10, player2.centery-28), (player2.centerx-2, player2.centery-30), 2)
    pygame.draw.line(screen, (80, 42, 20), (player2.centerx+10, player2.centery-28), (player2.centerx+2, player2.centery-30), 2)
    # Nose
    pygame.draw.line(screen, (160, 110, 60), (player2.centerx, player2.centery-18), (player2.centerx, player2.centery-13), 2)
    # Mouth
    pygame.draw.arc(screen, (150,75,0), (player2.centerx-7, player2.centery-10, 14, 8), 3.14, 2*3.14, 2)
    # Body (shirt)
    pygame.draw.rect(screen, (200, 0, 0), (player2.centerx-10, player2.centery+3, 20, 38))
    # Arms (skin tone)
    pygame.draw.line(screen, (224, 172, 105), (player2.centerx-20, player2.centery+10), (player2.centerx+20, player2.centery+10), 8)
    # Hands
    pygame.draw.circle(screen, (224, 172, 105), (player2.centerx-20, player2.centery+10), 5)
    pygame.draw.circle(screen, (224, 172, 105), (player2.centerx+20, player2.centery+10), 5)
    # Legs (pants)
    pygame.draw.line(screen, (128,0,0), (player2.centerx-5, player2.centery+41), (player2.centerx-5, player2.centery+70), 8)
    pygame.draw.line(screen, (128,0,0), (player2.centerx+5, player2.centery+41), (player2.centerx+5, player2.centery+70), 8)
    # Shoes
    pygame.draw.ellipse(screen, (0,0,0), (player2.centerx-12, player2.centery+68, 14, 8))
    pygame.draw.ellipse(screen, (0,0,0), (player2.centerx-2, player2.centery+68, 14, 8))

    # Draw Player 1 name above head
    name_text1 = font.render(player1_name, True, (0,0,255))
    screen.blit(name_text1, (player1.centerx - name_text1.get_width()//2, player1.centery-60))

    # Draw Player 2 name above head
    name_text2 = font.render(player2_name, True, (255,0,0))
    screen.blit(name_text2, (player2.centerx - name_text2.get_width()//2, player2.centery-60))

    # Draw guns only in battle mode
    if mode == 0:
        # Draw Player 1 AK-47 (attached to hand, correct direction)
        if p1_right:
            hand_x = player1.centerx+20
            hand_y = player1.centery+10
            pygame.draw.rect(screen, (80,80,80), (hand_x+20, hand_y-4, 22, 4))
            pygame.draw.rect(screen, (139,69,19), (hand_x-18, hand_y-7, 16, 8))
            pygame.draw.rect(screen, (80,80,80), (hand_x, hand_y-7, 38, 8))
            pygame.draw.arc(screen, (60,60,60), (hand_x+10, hand_y+2, 18, 14), 3.14, 2*3.14, 4)
            pygame.draw.rect(screen, (60,60,60), (hand_x+30, hand_y+2, 6, 12))
        else:
            hand_x = player1.centerx-20
            hand_y = player1.centery+10
            pygame.draw.rect(screen, (80,80,80), (hand_x-42, hand_y-4, 22, 4))
            pygame.draw.rect(screen, (139,69,19), (hand_x+2, hand_y-7, 16, 8))
            pygame.draw.rect(screen, (80,80,80), (hand_x-38, hand_y-7, 38, 8))
            pygame.draw.arc(screen, (60,60,60), (hand_x-28, hand_y+2, 18, 14), 0, 3.14, 4)
            pygame.draw.rect(screen, (60,60,60), (hand_x-36, hand_y+2, 6, 12))
        # Draw Player 2 AK-47 (attached to hand, correct direction)
        if p2_right:
            hand_x = player2.centerx+20
            hand_y = player2.centery+10
            pygame.draw.rect(screen, (80,80,80), (hand_x+20, hand_y-4, 22, 4))
            pygame.draw.rect(screen, (139,69,19), (hand_x-18, hand_y-7, 16, 8))
            pygame.draw.rect(screen, (80,80,80), (hand_x, hand_y-7, 38, 8))
            pygame.draw.arc(screen, (60,60,60), (hand_x+10, hand_y+2, 18, 14), 3.14, 2*3.14, 4)
            pygame.draw.rect(screen, (60,60,60), (hand_x+30, hand_y+2, 6, 12))
        else:
            hand_x = player2.centerx-20
            hand_y = player2.centery+10
            pygame.draw.rect(screen, (80,80,80), (hand_x-42, hand_y-4, 22, 4))
            pygame.draw.rect(screen, (139,69,19), (hand_x+2, hand_y-7, 16, 8))
            pygame.draw.rect(screen, (80,80,80), (hand_x-38, hand_y-7, 38, 8))
            pygame.draw.arc(screen, (60,60,60), (hand_x-28, hand_y+2, 18, 14), 0, 3.14, 4)
            pygame.draw.rect(screen, (60,60,60), (hand_x-36, hand_y+2, 6, 12))

    # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, (255,255,0), bullet['rect'])
    health_text = font.render(f"P1 Health: {player1_health}  P2 Health: {player2_health}", True, (255,255,255))
    screen.blit(health_text, (WIDTH//2 - health_text.get_width()//2, 20))

    # Show shots left and reload status for both players
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
    if player1_health <= 0:
        win_text = font.render("Player 2 Wins!", True, (255, 0, 0))
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()
    if player2_health <= 0:
        win_text = font.render("Player 1 Wins!", True, (0, 0, 255))
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

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
            pygame.quit()
            sys.exit()

    pygame.display.flip()
    clock.tick(60)











