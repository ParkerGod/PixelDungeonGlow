import pygame
import sys
import config
from player import Player
from map_generator import DungeonMap
from battle import BattleSystem
from ui import UIManager
from data_manager import DataManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Pixel Dungeon Adventure")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.data_manager = DataManager()
        self.ui = UIManager(self.screen)
        self.battle_system = BattleSystem()
        
        self.dungeon = DungeonMap()
        spawn_x, spawn_y = self.dungeon.get_player_spawn()
        self.player = Player(spawn_x, spawn_y)
        
        self.game_state = "playing"
        self.current_level = 1
        self.total_kills = 0
        self.frame_count = 0
        self.save_cooldown = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_and_quit()
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event)
                    
    def handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            self.save_and_quit()
        elif event.key == pygame.K_r and self.game_state == "game_over":
            self.restart_game()
        elif event.key == pygame.K_l and self.game_state == "game_over":
            self.load_game()
        elif event.key == pygame.K_SPACE:
            if self.battle_system.in_battle:
                self.handle_battle_attack()
        elif event.key == pygame.K_F5 and self.save_cooldown <= 0:
            self.save_game()
        elif event.key == pygame.K_F9:
            self.load_game()
                    
    def handle_mouse_click(self, event):
        if self.game_state == "playing":
            action = self.ui.check_button_click(event.pos)
            if action == "save" and self.save_cooldown <= 0:
                self.save_game()
            elif action == "load":
                self.load_game()
            elif action == "upgrade":
                if self.player.upgrade_attack(30):
                    self.ui.show_message("Attack upgraded! +5 ATK")
                else:
                    self.ui.show_message("Not enough gold! (Need 30)")
                    
    def handle_battle_attack(self):
        if self.battle_system.can_attack():
            self.battle_system.player_attack()
            if self.battle_system.monster.alive:
                self.battle_system.monster_attack()
            result = self.battle_system.get_battle_result()
            if result == "win":
                self.total_kills += 1
                gold_reward = 20 + self.current_level * 5
                self.player.add_gold(gold_reward)
                self.ui.show_message(f"Victory! +{gold_reward} Gold")
            elif result == "lose":
                self.game_state = "game_over"
                
    def check_monster_collision_and_battle(self):
        monster = self.dungeon.check_monster_collision(self.player.rect)
        if monster and monster.alive:
            self.battle_system.start_battle(self.player, monster)
            return True
        return False
            
    def handle_input(self):
        if self.game_state != "playing" or self.battle_system.in_battle:
            return
            
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            
        if dx != 0 or dy != 0:
            if self.player.try_move(dx, dy, self.dungeon):
                self.check_monster_collision_and_battle()
            
    def update(self):
        self.frame_count += 1
        
        if self.save_cooldown > 0:
            self.save_cooldown -= 1
        
        if self.game_state != "playing":
            return
            
        self.player.update()
        self.battle_system.update()
        
        if not self.battle_system.in_battle:
            gold_collected = self.dungeon.check_coin_collision(self.player.rect)
            if gold_collected > 0:
                self.player.add_gold(gold_collected)
                
            if self.dungeon.get_alive_monster_count() == 0 and len(self.dungeon.rooms) > 0:
                self.next_level()
            
    def next_level(self):
        self.current_level += 1
        self.dungeon = DungeonMap(self.current_level)
        spawn_x, spawn_y = self.dungeon.get_player_spawn()
        self.player.set_position(spawn_x, spawn_y)
        self.battle_system = BattleSystem()
        self.ui.show_message(f"Level {self.current_level}!")
        
    def save_game(self):
        if self.save_cooldown > 0:
            self.ui.show_message("Please wait before saving again")
            return
            
        if self.data_manager.save_player(self.player, self.current_level, self.total_kills):
            self.ui.show_message("Game Saved!")
            self.save_cooldown = config.SAVE_COOLDOWN
        else:
            self.ui.show_message("Save Failed!")
        
    def load_game(self):
        save_data = self.data_manager.load_player()
        if save_data:
            self.current_level = save_data.get('current_level', 1)
            self.total_kills = save_data.get('total_kills', 0)
            self.player.load_from_save(save_data)
            
            self.dungeon = DungeonMap(self.current_level)
            spawn_x, spawn_y = self.dungeon.get_player_spawn()
            self.player.set_position(spawn_x, spawn_y)
            
            self.battle_system = BattleSystem()
            self.game_state = "playing"
            self.ui.show_message(f"Game Loaded! Level {self.current_level}")
        else:
            self.ui.show_message("No save found!")
        
    def restart_game(self):
        self.data_manager.reset_save()
        self.current_level = 1
        self.total_kills = 0
        self.dungeon = DungeonMap()
        spawn_x, spawn_y = self.dungeon.get_player_spawn()
        self.player = Player(spawn_x, spawn_y)
        self.battle_system = BattleSystem()
        self.game_state = "playing"
        self.ui.show_message("New Game Started!")
        
    def save_and_quit(self):
        self.data_manager.save_player(self.player, self.current_level, self.total_kills)
        self.running = False
        
    def draw(self):
        self.screen.fill(config.BLACK)
        
        self.dungeon.draw(self.screen, self.frame_count)
        self.player.draw(self.screen)
        
        self.ui.draw_ui(self.player, self.current_level, self.total_kills)
        
        if self.battle_system.in_battle:
            self.ui.draw_battle_ui(self.battle_system)
        
        if self.game_state == "game_over":
            self.ui.draw_game_over(self.total_kills, self.current_level)
            
        pygame.display.flip()
        
    def run(self):
        while self.running:
            self.handle_events()
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(config.FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
