import pygame
from config import *

class BattleSystem:
    def __init__(self, player, monster, map_gen):
        self.player = player
        self.monster = monster
        self.map_gen = map_gen
        self.active = False
        self.font = pygame.font.Font(FONT_PATH, 48)
        self.small_font = pygame.font.Font(FONT_PATH, 24)
        self.message = ""
        self.message_timer = 0
    
    def start_battle(self):
        self.active = True
        self.message = "遇到怪物! 按空格键攻击!"
    
    def handle_event(self, event):
        if not self.active:
            return
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.player_attack()
        elif event.type == pygame.USEREVENT + 1:
            self.monster_attack()
    
    def player_attack(self):
        if not self.monster.is_alive():
            return
        damage = self.player.atk
        self.monster.take_damage(damage)
        self.message = f"你造成了 {damage} 点伤害!"
        self.message_timer = 90
        
        if not self.monster.is_alive():
            self.end_battle(victory=True)
        else:
            pygame.time.set_timer(pygame.USEREVENT + 1, 500, True)
    
    def monster_attack(self):
        if not self.monster.is_alive() or not self.active:
            return
        damage = self.monster.atk
        self.player.take_damage(damage)
        self.message = f"怪物造成了 {damage} 点伤害!"
        self.message_timer = 90
        
        if not self.player.is_alive():
            self.end_battle(victory=False)
    
    def end_battle(self, victory):
        self.active = False
        if victory:
            self.message = "你击败了怪物!"
            self.map_gen.remove_monster(self.monster)
            self.player.collect_gold(20)
        else:
            self.message = "游戏结束!"
    
    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def render(self, screen):
        if not self.active and self.message_timer <= 0:
            return
        
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        battle_text = self.font.render("战斗中!", True, RED)
        screen.blit(battle_text, (WIDTH//2 - 100, HEIGHT//4))
        
        player_hp_text = self.small_font.render(f"你的HP: {self.player.hp}/{self.player.max_hp}", True, WHITE)
        monster_hp_text = self.small_font.render(f"怪物HP: {self.monster.hp}", True, RED)
        screen.blit(player_hp_text, (WIDTH//2 - 100, HEIGHT//2 - 50))
        screen.blit(monster_hp_text, (WIDTH//2 - 100, HEIGHT//2))
        
        if self.message:
            msg_text = self.small_font.render(self.message, True, YELLOW)
            screen.blit(msg_text, (WIDTH//2 - 150, HEIGHT//2 + 100))
        
        if not self.player.is_alive():
            game_over_text = self.font.render("游戏结束!", True, RED)
            screen.blit(game_over_text, (WIDTH//2 - 100, HEIGHT//2 + 150))
