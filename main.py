import pygame
import sys
from config import *
from player import Player
from map_generator import MapGenerator
from battle import BattleSystem
from data_manager import DataManager
from ui import UIManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "PLAYING"
        
        self.data_manager = DataManager()
        
        self.map_generator = MapGenerator()
        spawn_pos = self.map_generator.generate_map()
        self.player = Player(spawn_pos[0], spawn_pos[1])
        
        if self.data_manager.has_save():
            self.data_manager.load_player(self.player)
        
        self.ui_manager = UIManager(self.player)
        self.battle_system = None
        
        self.font = pygame.font.Font(FONT_PATH, 36)
        self.small_font = pygame.font.Font(FONT_PATH, 24)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.data_manager.save_player(self.player)
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    if self.data_manager.save_player(self.player):
                        self.ui_manager.show_message("存档成功!", 60)
                    else:
                        self.ui_manager.show_message("存档失败!", 60)
                elif event.key == pygame.K_l:
                    if self.data_manager.has_save():
                        self.data_manager.load_player(self.player)
                        self.ui_manager.show_message("读档成功!", 60)
                    else:
                        self.ui_manager.show_message("无存档数据!", 60)
                elif event.key == pygame.K_u:
                    if self.player.level_up():
                        self.ui_manager.show_message("攻击力提升!", 60)
                    else:
                        self.ui_manager.show_message("金币不足!(需要50)", 60)
                elif event.key == pygame.K_n:
                    self.map_generator = MapGenerator()
                    spawn_pos = self.map_generator.generate_map()
                    self.player.reset_position(spawn_pos[0], spawn_pos[1])
                    self.ui_manager.show_message("新地图生成!", 60)
                
                if self.game_state == "PLAYING":
                    self.player.handle_input(event.key)
            elif event.type == pygame.KEYUP:
                self.player.stop_movement(event.key)
            
            if self.game_state == "BATTLE" and self.battle_system:
                self.battle_system.handle_event(event)
    
    def update(self):
        self.ui_manager.update()
        
        if self.game_state == "PLAYING":
            old_x, old_y = self.player.x, self.player.y
            self.player.update()
            
            if self.map_generator.check_collision(self.player.rect):
                self.player.x, self.player.y = old_x, old_y
                self.player.rect.x, self.player.rect.y = old_x, old_y
            
            gold = self.map_generator.check_gold_collision(self.player.rect)
            if gold > 0:
                self.player.collect_gold(gold)
                self.ui_manager.show_message(f"获得 {gold} 金币!", 30)
            
            monster = self.map_generator.check_monster_collision(self.player.rect)
            if monster:
                self.player.x, self.player.y = old_x, old_y
                self.player.rect.x, self.player.rect.y = old_x, old_y
                self.start_battle(monster)
        
        elif self.game_state == "BATTLE" and self.battle_system:
            self.battle_system.update()
            if not self.battle_system.active:
                if not self.player.is_alive():
                    self.ui_manager.show_message("游戏结束!", 120)
                    pygame.time.delay(2000)
                    self.running = False
                else:
                    self.game_state = "PLAYING"
                    if not self.battle_system.monster.is_alive():
                        self.ui_manager.show_message("获得 20 金币!", 30)
    
    def start_battle(self, monster):
        self.game_state = "BATTLE"
        self.battle_system = BattleSystem(self.player, monster, self.map_generator)
        self.battle_system.start_battle()
    
    def render(self):
        self.screen.fill(BLACK)
        self.map_generator.render(self.screen)
        self.player.render(self.screen)
        self.ui_manager.render(self.screen)
        
        if self.game_state == "BATTLE" and self.battle_system:
            self.battle_system.render(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        self.data_manager.close()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
