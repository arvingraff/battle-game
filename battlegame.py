import pygame
import sys
import time

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

player1_shots = 0
player2_shots = 0
player1_reload_time = 0
player2_reload_time = 0
RELOAD_LIMIT = 3
RELOAD_DURATION = 3  # seconds

while True:
    now = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
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

    # Move bullets
    for bullet in bullets[:]:
        bullet['rect'].x += bullet['dir'] * 12
        # Remove if off screen
        if bullet['rect'].right < 0 or bullet['rect'].left > WIDTH:
            bullets.remove(bullet)
        # Collision with players
        elif bullet['owner'] == 1 and bullet['rect'].colliderect(player2):
            player2_health -= 1
            bullets.remove(bullet)
        elif bullet['owner'] == 2 and bullet['rect'].colliderect(player1):
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

    # Draw everything
    screen.fill((30, 30, 30))
    # Draw map border
    border_color = (200, 200, 200)
    border_thickness = 8
    pygame.draw.rect(screen, border_color, (0, 0, WIDTH, HEIGHT), border_thickness)


    # Draw Player 1 (Blue, human-like)
    # Head
    pygame.draw.circle(screen, (0, 0, 255), (player1.centerx, player1.centery-20), 15)
    # Body
    pygame.draw.rect(screen, (0, 0, 255), (player1.centerx-8, player1.centery-20, 16, 30))
    # Arms
    pygame.draw.line(screen, (0, 0, 255), (player1.centerx-18, player1.centery-10), (player1.centerx+18, player1.centery-10), 6)
    # Legs
    pygame.draw.line(screen, (0, 0, 255), (player1.centerx-8, player1.centery+10), (player1.centerx-8, player1.centery+30), 6)
    pygame.draw.line(screen, (0, 0, 255), (player1.centerx+8, player1.centery+10), (player1.centerx+8, player1.centery+30), 6)

    # Draw Player 2 (Red, human-like)
    pygame.draw.circle(screen, (255, 0, 0), (player2.centerx, player2.centery-20), 15)
    pygame.draw.rect(screen, (255, 0, 0), (player2.centerx-8, player2.centery-20, 16, 30))
    pygame.draw.line(screen, (255, 0, 0), (player2.centerx-18, player2.centery-10), (player2.centerx+18, player2.centery-10), 6)
    pygame.draw.line(screen, (255, 0, 0), (player2.centerx-8, player2.centery+10), (player2.centerx-8, player2.centery+30), 6)
    pygame.draw.line(screen, (255, 0, 0), (player2.centerx+8, player2.centery+10), (player2.centerx+8, player2.centery+30), 6)

    # Draw pistols
    if p1_right:
        pygame.draw.rect(screen, (200,200,200), (player1.right, player1.centery-5, 15, 10))
    else:
        pygame.draw.rect(screen, (200,200,200), (player1.left-15, player1.centery-5, 15, 10))
    if p2_right:
        pygame.draw.rect(screen, (200,200,200), (player2.right, player2.centery-5, 15, 10))
    else:
        pygame.draw.rect(screen, (200,200,200), (player2.left-15, player2.centery-5, 15, 10))
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

    pygame.display.flip()
    clock.tick(60)











