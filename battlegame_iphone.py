"""
BattleGame for iPhone - Optimized for Pythonista
Run this file in the Pythonista app on your iPhone
"""

import ui
import sound
import random
import math
from scene import *

class Player:
    def __init__(self, x, y, color, name="Player"):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.health = 5
        self.facing_right = True
        self.speed = 200
        self.reload_time = 0
        self.shots_fired = 0
        self.size = 30
    
    def move(self, dx, dy, dt):
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt
        
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False
    
    def draw(self):
        fill(*self.color)
        ellipse(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
        
        # Eyes
        fill(1, 1, 1)
        if self.facing_right:
            ellipse(self.x + 5, self.y + 5, 8, 8)
        else:
            ellipse(self.x - 13, self.y + 5, 8, 8)

class Bullet:
    def __init__(self, x, y, dx, dy, owner):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.owner = owner
        self.speed = 400
        self.size = 6
        self.active = True
    
    def update(self, dt):
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt
        
        if self.x < 0 or self.x > 768 or self.y < 0 or self.y > 1024:
            self.active = False
    
    def draw(self):
        fill(1, 1, 0)
        ellipse(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
    
    def hits(self, player):
        if self.owner == player:
            return False
        dx = self.x - player.x
        dy = self.y - player.y
        dist = math.sqrt(dx*dx + dy*dy)
        return dist < (self.size + player.size) / 2

class BattleGame(Scene):
    def setup(self):
        self.background_color = '#1a1a2e'
        
        # Create players
        self.player1 = Player(200, 512, (1, 0, 0), "Player 1")
        self.player2 = Player(568, 512, (0, 0, 1), "Player 2")
        self.bullets = []
        
        # Touch tracking
        self.touches = {}
        self.p1_joystick = None
        self.p2_joystick = None
        
        # Game state
        self.game_over = False
        self.winner = None
    
    def draw(self):
        background(0.1, 0.1, 0.18)
        
        if self.game_over:
            text(f"{self.winner} Wins!", 'Helvetica-Bold', 48, 
                 x=self.size.w/2, y=self.size.h/2, alignment=5)
            text("Tap to restart", 'Helvetica', 24,
                 x=self.size.w/2, y=self.size.h/2-50, alignment=5)
            return
        
        # Draw players
        self.player1.draw()
        self.player2.draw()
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw()
        
        # Draw health
        text(f"P1: {'♥' * self.player1.health}", 'Helvetica', 24,
             x=80, y=self.size.h-30, alignment=3)
        text(f"P2: {'♥' * self.player2.health}", 'Helvetica', 24,
             x=self.size.w-80, y=self.size.h-30, alignment=3)
        
        # Draw controls hint
        text("Touch & drag bottom corners to move", 'Helvetica', 14,
             x=self.size.w/2, y=30, alignment=5)
        text("Tap top corners to shoot", 'Helvetica', 14,
             x=self.size.w/2, y=10, alignment=5)
    
    def update(self):
        if self.game_over:
            return
        
        dt = self.dt
        
        # Update reload times
        if self.player1.reload_time > 0:
            self.player1.reload_time -= dt
            if self.player1.reload_time <= 0:
                self.player1.shots_fired = 0
        
        if self.player2.reload_time > 0:
            self.player2.reload_time -= dt
            if self.player2.reload_time <= 0:
                self.player2.shots_fired = 0
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update(dt)
            
            if not bullet.active:
                self.bullets.remove(bullet)
                continue
            
            if bullet.hits(self.player1):
                self.player1.health -= 1
                self.bullets.remove(bullet)
                if self.player1.health <= 0:
                    self.game_over = True
                    self.winner = "Player 2"
            elif bullet.hits(self.player2):
                self.player2.health -= 1
                self.bullets.remove(bullet)
                if self.player2.health <= 0:
                    self.game_over = True
                    self.winner = "Player 1"
    
    def touch_began(self, touch):
        if self.game_over:
            self.__init__()
            self.setup()
            return
        
        x, y = touch.location
        
        # Player 1 controls (left side)
        if x < self.size.w / 2:
            if y < 200:  # Bottom left - movement
                self.p1_joystick = touch.touch_id
            elif y > self.size.h - 200:  # Top left - shoot
                self.shoot(self.player1)
        
        # Player 2 controls (right side)
        else:
            if y < 200:  # Bottom right - movement
                self.p2_joystick = touch.touch_id
            elif y > self.size.h - 200:  # Top right - shoot
                self.shoot(self.player2)
        
        self.touches[touch.touch_id] = touch.location
    
    def touch_moved(self, touch):
        if self.game_over:
            return
        
        x, y = touch.location
        
        if touch.touch_id == self.p1_joystick:
            # Move player 1
            if touch.touch_id in self.touches:
                old_x, old_y = self.touches[touch.touch_id]
                dx = x - old_x
                dy = y - old_y
                self.player1.move(dx/50, dy/50, self.dt)
        
        elif touch.touch_id == self.p2_joystick:
            # Move player 2
            if touch.touch_id in self.touches:
                old_x, old_y = self.touches[touch.touch_id]
                dx = x - old_x
                dy = y - old_y
                self.player2.move(dx/50, dy/50, self.dt)
        
        self.touches[touch.touch_id] = touch.location
    
    def touch_ended(self, touch):
        if touch.touch_id == self.p1_joystick:
            self.p1_joystick = None
        elif touch.touch_id == self.p2_joystick:
            self.p2_joystick = None
        
        if touch.touch_id in self.touches:
            del self.touches[touch.touch_id]
    
    def shoot(self, player):
        if player.reload_time > 0:
            return
        
        if player.shots_fired >= 3:
            player.reload_time = 3.0
            player.shots_fired = 0
            return
        
        # Shoot in facing direction
        dx = 1 if player.facing_right else -1
        bullet = Bullet(player.x, player.y, dx, 0, player)
        self.bullets.append(bullet)
        player.shots_fired += 1
        
        try:
            sound.play_effect('arcade:Laser_1')
        except:
            pass

if __name__ == '__main__':
    run(BattleGame(), orientation=PORTRAIT)
