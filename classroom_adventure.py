#!/usr/bin/env python3
"""
🌈 CLASSROOM ADVENTURE - Peaceful Multiplayer Game 🌈
A fun, cooperative game for 22 kids + 2 adults!
Everyone works together to collect stars, solve puzzles, and explore!
"""

import pygame
import sys
import random
import json
import math
from network import NetworkHost, NetworkClient

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
PLAYER_SIZE = 40

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 250)
GRASS_GREEN = (34, 139, 34)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
PINK = (255, 192, 203)
PURPLE = (147, 112, 219)
ORANGE = (255, 165, 0)

# Player colors for each person
PLAYER_COLORS = [
    (255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 255, 100),
    (255, 100, 255), (100, 255, 255), (255, 150, 100), (150, 100, 255),
    (100, 255, 150), (255, 200, 100), (200, 100, 255), (100, 200, 255),
    (255, 100, 200), (150, 255, 100), (100, 150, 255), (255, 255, 150),
    (255, 150, 255), (150, 255, 255), (200, 200, 100), (200, 100, 200),
    (100, 200, 200), (220, 220, 100), (220, 100, 220), (100, 220, 220)
]

class ClassroomAdventure:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🌈 CLASSROOM ADVENTURE 🌈")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        
        self.mode = "menu"  # menu, name_entry, lobby, playing
        self.role = None  # "host" or "client"
        self.player_name = ""
        self.is_adult = False
        
        # Multiplayer
        self.network = None
        self.players = {}  # {id: {name, x, y, color, emoji, is_adult}}
        self.my_id = None
        
        # Game world
        self.stars = []
        self.flowers = []
        self.clouds = []
        self.butterflies = []
        self.team_score = 0
        self.goal_score = 100
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Fun emojis for each player type
        self.student_emojis = ["😊", "😎", "🤓", "😁", "🥳", "😄", "🤗", "😇"]
        self.adult_emojis = ["👨‍🏫", "👩‍🏫", "🧑‍🏫"]
        
    def draw_text(self, text, x, y, font=None, color=WHITE, center=True):
        """Draw text on screen"""
        if font is None:
            font = self.font
        text_surface = font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
        else:
            text_rect = text_surface.get_rect(topleft=(x, y))
        self.screen.blit(text_surface, text_rect)
    
    def draw_emoji(self, emoji, x, y, size=40):
        """Draw emoji (simplified as colored circle with text)"""
        text_surface = self.big_font.render(emoji, True, WHITE)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)
    
    def main_menu(self):
        """Beautiful main menu"""
        running = True
        while running:
            self.screen.fill(SKY_BLUE)
            
            # Animated clouds
            time = pygame.time.get_ticks() / 1000
            for i in range(5):
                cloud_x = ((i * 300 + time * 30) % (SCREEN_WIDTH + 200)) - 100
                cloud_y = 50 + i * 30
                self.draw_cloud(cloud_x, cloud_y)
            
            # Title with shadow
            self.draw_text("🌈 CLASSROOM ADVENTURE 🌈", SCREEN_WIDTH//2 + 3, 103, self.big_font, (100, 100, 100))
            self.draw_text("🌈 CLASSROOM ADVENTURE 🌈", SCREEN_WIDTH//2, 100, self.big_font, GOLD)
            
            self.draw_text("A Peaceful Game for Everyone!", SCREEN_WIDTH//2, 180, self.font, WHITE)
            
            # Menu options with cute borders
            options = [
                ("1. 🎮 HOST GAME (Teacher/First Student)", 280, PINK),
                ("2. 👋 JOIN GAME (Other Students)", 340, SKY_BLUE),
                ("3. ⚔️  BATTLE MODE (Main Game)", 400, PURPLE),
                ("4. 🚪 EXIT", 460, ORANGE)
            ]
            
            for text, y, color in options:
                # Background box
                box_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, y - 25, 600, 50)
                pygame.draw.rect(self.screen, color, box_rect, border_radius=15)
                pygame.draw.rect(self.screen, WHITE, box_rect, 3, border_radius=15)
                self.draw_text(text, SCREEN_WIDTH//2, y, self.font, BLACK)
            
            self.draw_text("Press 1, 2, 3, or 4", SCREEN_WIDTH//2, 550, self.font, (100, 100, 100))
            
            # Draw grass at bottom
            pygame.draw.rect(self.screen, GRASS_GREEN, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
            
            # Draw flowers
            for i in range(15):
                flower_x = i * 80 + 40
                self.draw_flower(flower_x, SCREEN_HEIGHT - 50)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.setup_host()
                        running = False
                    elif event.key == pygame.K_2:
                        self.setup_client()
                        running = False
                    elif event.key == pygame.K_3:
                        self.launch_battle_game()
                        running = False
                    elif event.key == pygame.K_4:
                        pygame.quit()
                        sys.exit()
            
            self.clock.tick(FPS)
    
    def draw_cloud(self, x, y):
        """Draw a cute cloud"""
        pygame.draw.circle(self.screen, WHITE, (int(x), int(y)), 30)
        pygame.draw.circle(self.screen, WHITE, (int(x + 30), int(y)), 40)
        pygame.draw.circle(self.screen, WHITE, (int(x + 60), int(y)), 30)
    
    def draw_flower(self, x, y):
        """Draw a cute flower"""
        # Stem
        pygame.draw.line(self.screen, GRASS_GREEN, (x, y), (x, y + 30), 3)
        # Petals
        petal_colors = [PINK, YELLOW, PURPLE, ORANGE]
        for i in range(4):
            angle = i * (3.14159 * 2 / 4)
            petal_x = x + int(math.cos(angle) * 15)
            petal_y = y + int(math.sin(angle) * 15)
            pygame.draw.circle(self.screen, petal_colors[i % 4], (petal_x, petal_y), 8)
        # Center
        pygame.draw.circle(self.screen, GOLD, (x, y), 8)
    
    def setup_host(self):
        """Host sets up the game"""
        self.role = "host"
        self.player_name = self.get_player_name()
        
        # Initialize game world
        self.spawn_collectibles()
        
        try:
            self.network = NetworkHost()
            self.my_id = 0
            self.players[0] = {
                'name': self.player_name,
                'x': SCREEN_WIDTH // 2,
                'y': SCREEN_HEIGHT // 2,
                'color': PLAYER_COLORS[0],
                'emoji': self.adult_emojis[0] if self.is_adult else random.choice(self.student_emojis),
                'is_adult': self.is_adult
            }
            self.run_lobby()
        except Exception as e:
            print(f"Failed to host: {e}")
            self.main_menu()
    
    def setup_client(self):
        """Client joins the game"""
        self.role = "client"
        self.player_name = self.get_player_name()
        
        try:
            self.network = NetworkClient()
            join_data = {
                'name': self.player_name,
                'is_adult': self.is_adult
            }
            self.network.send(json.dumps(join_data))
            self.run_lobby()
        except Exception as e:
            print(f"Failed to join: {e}")
            self.main_menu()
    
    def get_player_name(self):
        """Get player's name with cute UI"""
        name = ""
        entering = True
        
        while entering:
            self.screen.fill(SKY_BLUE)
            
            # Title
            self.draw_text("✨ Enter Your Name ✨", SCREEN_WIDTH//2, 150, self.big_font, GOLD)
            
            # Name box
            box_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, 300, 500, 80)
            pygame.draw.rect(self.screen, WHITE, box_rect, border_radius=20)
            pygame.draw.rect(self.screen, PURPLE, box_rect, 5, border_radius=20)
            
            self.draw_text(f"{name}_", SCREEN_WIDTH//2, 340, self.big_font, BLACK)
            
            self.draw_text("Press ENTER when done", SCREEN_WIDTH//2, 450, self.font, (100, 100, 100))
            self.draw_text("Press A if you're an ADULT (Teacher)", SCREEN_WIDTH//2, 500, self.font, PINK)
            
            if self.is_adult:
                self.draw_text("👨‍🏫 ADULT MODE ACTIVATED! 👩‍🏫", SCREEN_WIDTH//2, 550, self.font, GOLD)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name:
                        entering = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event.key == pygame.K_a:
                        self.is_adult = not self.is_adult
                    elif event.unicode.isprintable() and len(name) < 15:
                        name += event.unicode
            
            self.clock.tick(FPS)
        
        return name
    
    def run_lobby(self):
        """Waiting room with animations"""
        waiting = True
        bob_offset = 0
        
        while waiting:
            bob_offset = math.sin(pygame.time.get_ticks() / 500) * 10
            
            self.screen.fill(SKY_BLUE)
            
            # Title
            self.draw_text("🎮 GAME LOBBY 🎮", SCREEN_WIDTH//2, 80, self.big_font, GOLD)
            
            # Player count
            count_text = f"Players Ready: {len(self.players)}/24 {'🌟' * len(self.players)}"
            self.draw_text(count_text, SCREEN_WIDTH//2, 150, self.font, WHITE)
            
            # Show all players in a grid
            cols = 6
            start_x = 100
            start_y = 220
            spacing_x = 180
            spacing_y = 80
            
            for i, (player_id, player) in enumerate(self.players.items()):
                col = i % cols
                row = i // cols
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y + (bob_offset if i % 2 == 0 else -bob_offset)
                
                # Player circle
                pygame.draw.circle(self.screen, player['color'], (x, y), 25)
                pygame.draw.circle(self.screen, WHITE, (x, y), 25, 3)
                
                # Emoji
                self.draw_emoji(player['emoji'], x, y, 30)
                
                # Name
                role = "👨‍🏫" if player.get('is_adult') else ""
                self.draw_text(f"{role}{player['name']}", x, y + 35, self.small_font, WHITE)
            
            # Instructions at bottom
            if self.role == "host":
                pygame.draw.rect(self.screen, GRASS_GREEN, (SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT - 120, 600, 80), border_radius=20)
                self.draw_text("Press SPACE to START ADVENTURE!", SCREEN_WIDTH//2, SCREEN_HEIGHT - 80, self.font, WHITE)
            else:
                self.draw_text("Waiting for host to start...", SCREEN_WIDTH//2, SCREEN_HEIGHT - 80, self.font, (150, 150, 150))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.role == "host":
                        self.mode = "playing"
                        waiting = False
            
            self.clock.tick(FPS)
        
        # Start the game!
        self.play_game()
    
    def spawn_collectibles(self):
        """Create stars, flowers, and butterflies to collect"""
        # Spawn 100 stars across a big world
        for i in range(100):
            self.stars.append({
                'x': random.randint(0, SCREEN_WIDTH * 3),
                'y': random.randint(100, SCREEN_HEIGHT - 200),
                'collected': False
            })
        
        # Spawn butterflies that fly around
        for i in range(20):
            self.butterflies.append({
                'x': random.randint(0, SCREEN_WIDTH * 3),
                'y': random.randint(100, SCREEN_HEIGHT - 200),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'collected': False
            })
    
    def play_game(self):
        """Main peaceful gameplay"""
        running = True
        
        # My player
        if self.my_id in self.players:
            my_player = self.players[self.my_id]
        else:
            my_player = {'x': SCREEN_WIDTH//2, 'y': SCREEN_HEIGHT//2}
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Movement
            keys = pygame.key.get_pressed()
            speed = 5
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                my_player['x'] -= speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                my_player['x'] += speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                my_player['y'] -= speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                my_player['y'] += speed
            
            # Update camera to follow player
            self.camera_x = my_player['x'] - SCREEN_WIDTH // 2
            self.camera_y = my_player['y'] - SCREEN_HEIGHT // 2
            
            # Update butterflies
            for butterfly in self.butterflies:
                if not butterfly['collected']:
                    butterfly['x'] += butterfly['vx']
                    butterfly['y'] += butterfly['vy']
                    
                    # Bounce off edges
                    if butterfly['x'] < 0 or butterfly['x'] > SCREEN_WIDTH * 3:
                        butterfly['vx'] *= -1
                    if butterfly['y'] < 100 or butterfly['y'] > SCREEN_HEIGHT - 200:
                        butterfly['vy'] *= -1
            
            # Check star collection
            for star in self.stars:
                if not star['collected']:
                    dist = math.sqrt((my_player['x'] - star['x'])**2 + (my_player['y'] - star['y'])**2)
                    if dist < 40:
                        star['collected'] = True
                        self.team_score += 1
            
            # Check butterfly collection (worth 5 points!)
            for butterfly in self.butterflies:
                if not butterfly['collected']:
                    dist = math.sqrt((my_player['x'] - butterfly['x'])**2 + (my_player['y'] - butterfly['y'])**2)
                    if dist < 40:
                        butterfly['collected'] = True
                        self.team_score += 5
            
            # Draw everything
            self.draw_game_world(my_player)
            
            # Check win condition
            if self.team_score >= self.goal_score:
                self.show_victory()
                running = False
            
            self.clock.tick(FPS)
        
        self.main_menu()
    
    def draw_game_world(self, my_player):
        """Draw the peaceful game world"""
        # Sky background
        self.screen.fill(SKY_BLUE)
        
        # Grass ground
        ground_y = SCREEN_HEIGHT - 150
        pygame.draw.rect(self.screen, GRASS_GREEN, (0, ground_y, SCREEN_WIDTH, 150))
        
        # Draw stars
        for star in self.stars:
            if not star['collected']:
                screen_x = star['x'] - self.camera_x
                screen_y = star['y'] - self.camera_y
                if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
                    self.draw_star(screen_x, screen_y)
        
        # Draw butterflies
        for butterfly in self.butterflies:
            if not butterfly['collected']:
                screen_x = butterfly['x'] - self.camera_x
                screen_y = butterfly['y'] - self.camera_y
                if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
                    self.draw_butterfly(screen_x, screen_y)
        
        # Draw all players
        for player_id, player in self.players.items():
            screen_x = player['x'] - self.camera_x
            screen_y = player['y'] - self.camera_y
            
            # Player circle
            pygame.draw.circle(self.screen, player['color'], (int(screen_x), int(screen_y)), PLAYER_SIZE//2)
            pygame.draw.circle(self.screen, WHITE, (int(screen_x), int(screen_y)), PLAYER_SIZE//2, 3)
            
            # Emoji
            self.draw_emoji(player['emoji'], int(screen_x), int(screen_y))
            
            # Name
            self.draw_text(player['name'], int(screen_x), int(screen_y) - 35, self.small_font, WHITE)
        
        # UI - Score
        score_text = f"🌟 Team Stars: {self.team_score}/{self.goal_score}"
        pygame.draw.rect(self.screen, (0, 0, 0, 128), (10, 10, 300, 50), border_radius=10)
        self.draw_text(score_text, 160, 35, self.font, GOLD, center=True)
        
        # Instructions
        self.draw_text("Move: WASD or Arrows", SCREEN_WIDTH - 150, 30, self.small_font, WHITE, center=False)
        self.draw_text("ESC: Back to Menu", SCREEN_WIDTH - 150, 55, self.small_font, WHITE, center=False)
        
        pygame.display.flip()
    
    def draw_star(self, x, y):
        """Draw a sparkly star"""
        # Star shape
        points = []
        for i in range(10):
            angle = i * 3.14159 * 2 / 10
            radius = 20 if i % 2 == 0 else 10
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            points.append((px, py))
        pygame.draw.polygon(self.screen, GOLD, points)
        pygame.draw.polygon(self.screen, YELLOW, points, 2)
    
    def draw_butterfly(self, x, y):
        """Draw a cute butterfly"""
        # Wings (two circles)
        wing_bob = math.sin(pygame.time.get_ticks() / 100) * 3
        pygame.draw.circle(self.screen, PINK, (int(x - 10), int(y + wing_bob)), 12)
        pygame.draw.circle(self.screen, PURPLE, (int(x + 10), int(y - wing_bob)), 12)
        # Body
        pygame.draw.circle(self.screen, BLACK, (int(x), int(y)), 5)
    
    def show_victory(self):
        """Celebration screen!"""
        celebration_time = 5  # seconds
        start_time = pygame.time.get_ticks()
        
        while pygame.time.get_ticks() - start_time < celebration_time * 1000:
            self.screen.fill(SKY_BLUE)
            
            # Confetti
            for i in range(50):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                color = random.choice([PINK, YELLOW, PURPLE, ORANGE, GOLD])
                pygame.draw.circle(self.screen, color, (x, y), 5)
            
            # Victory text
            time_offset = math.sin(pygame.time.get_ticks() / 200) * 20
            self.draw_text("🎉 AMAZING TEAMWORK! 🎉", SCREEN_WIDTH//2, 200 + time_offset, self.big_font, GOLD)
            self.draw_text(f"Collected {self.team_score} stars together!", SCREEN_WIDTH//2, 300, self.font, WHITE)
            
            # All player names
            y = 400
            self.draw_text("🌟 CLASS CHAMPIONS 🌟", SCREEN_WIDTH//2, y, self.font, YELLOW)
            y += 50
            for player_id, player in self.players.items():
                self.draw_text(f"{player['emoji']} {player['name']}", SCREEN_WIDTH//2, y, self.small_font, player['color'])
                y += 30
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.clock.tick(FPS)
    
    def launch_battle_game(self):
        """Launch the main battlegame.py"""
        print("\n🎮 Launching BATTLE MODE...")
        print("Loading the epic battle game...\n")
        pygame.quit()
        
        # Import and run the main game
        import battlegame
        # The main game will take over from here

if __name__ == "__main__":
    print("=" * 60)
    print("🌈 CLASSROOM ADVENTURE - Peaceful Multiplayer Game 🌈")
    print("=" * 60)
    print("\nA fun, cooperative game for your entire class!")
    print("Collect stars and butterflies together!")
    print("\nStarting game...\n")
    
    game = ClassroomAdventure()
    game.main_menu()
