import pygame
from config import *

class UIManager:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.Font(FONT_PATH, 36)
        self.small_font = pygame.font.Font(FONT_PATH, 24)
        self.message = ""
        self.message_timer = 0
    
    def show_message(self, msg, duration=120):
        self.message = msg
        self.message_timer = duration
    
    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def render_hp_bar(self, screen, x, y, current_hp, max_hp, width=200, height=20):
        bar_width = int((current_hp / max_hp) * width)
        pygame.draw.rect(screen, RED, (x, y, width, height))
        pygame.draw.rect(screen, GREEN, (x, y, bar_width, height))
        pygame.draw.rect(screen, WHITE, (x, y, width, height), 2)
        
        hp_text = self.small_font.render(f"{current_hp}/{max_hp}", True, WHITE)
        screen.blit(hp_text, (x + width//2 - 20, y))
    
    def render(self, screen):
        self.render_hp_bar(screen, 10, 10, self.player.hp, self.player.max_hp)
        
        gold_text = self.font.render(f"金币: {self.player.gold}", True, YELLOW)
        screen.blit(gold_text, (10, 40))
        
        atk_text = self.small_font.render(f"攻击力: {self.player.atk}", True, GREEN)
        screen.blit(atk_text, (10, 75))
        
        level_text = self.small_font.render(f"等级: {self.player.level}", True, WHITE)
        screen.blit(level_text, (WIDTH - 80, 10))
        
        save_text = self.small_font.render("S:存档 L:读档 U:升级攻击(50金币)", True, WHITE)
        screen.blit(save_text, (WIDTH - 220, HEIGHT - 30))
        
        if self.message and self.message_timer > 0:
            msg_surface = self.font.render(self.message, True, YELLOW)
            msg_rect = msg_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
            bg_rect = pygame.Rect(msg_rect.x - 10, msg_rect.y - 10, msg_rect.width + 20, msg_rect.height + 20)
            pygame.draw.rect(screen, BLACK, bg_rect)
            pygame.draw.rect(screen, WHITE, bg_rect, 2)
            screen.blit(msg_surface, msg_rect)
