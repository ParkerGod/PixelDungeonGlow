import pygame
from config import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.speed = PLAYER_SPEED
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.atk = PLAYER_ATK
        self.gold = 0
        self.level = 1
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.color = BLUE
        
        self.dx = 0
        self.dy = 0
    
    def handle_input(self, key):
        if key == pygame.K_LEFT:
            self.dx = -self.speed
        elif key == pygame.K_RIGHT:
            self.dx = self.speed
        elif key == pygame.K_UP:
            self.dy = -self.speed
        elif key == pygame.K_DOWN:
            self.dy = self.speed
    
    def stop_movement(self, key):
        if key == pygame.K_LEFT or key == pygame.K_RIGHT:
            self.dx = 0
        elif key == pygame.K_UP or key == pygame.K_DOWN:
            self.dy = 0
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.x = self.x
        self.rect.y = self.y
    
    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
    
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
    
    def attack(self, target):
        target.take_damage(self.atk)
    
    def collect_gold(self, amount):
        self.gold += amount
    
    def level_up(self):
        if self.gold >= 50:
            self.gold -= 50
            self.atk += 5
            self.level += 1
            return True
        return False
    
    def is_alive(self):
        return self.hp > 0
    
    def reset_position(self, x, y):
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
