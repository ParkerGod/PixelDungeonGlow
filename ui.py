import pygame
import config

class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        self.save_button = pygame.Rect(700, 10, 80, 30)
        self.load_button = pygame.Rect(700, 45, 80, 30)
        self.upgrade_button = pygame.Rect(300, 550, 100, 35)
        
        self.show_save_message = False
        self.save_message_timer = 0
        self.save_message = ""
        
        self.last_hp = -1
        self.last_max_hp = -1
        self.last_gold = -1
        self.hp_bar_surface = None
        self.hp_bar_update_needed = True
        
    def draw_ui(self, player, current_level, total_kills):
        if player.hp != self.last_hp or player.max_hp != self.last_max_hp:
            self.hp_bar_update_needed = True
            self.last_hp = player.hp
            self.last_max_hp = player.max_hp
            
        if player.gold != self.last_gold:
            self.last_gold = player.gold
            
        ui_rect = pygame.Rect(0, 0, config.SCREEN_WIDTH, 40)
        pygame.draw.rect(self.screen, config.UI_BG_COLOR, ui_rect)
        
        hp_text = self.font.render("HP:", True, config.WHITE)
        self.screen.blit(hp_text, (10, 10))
        
        hp_bar_width = 120
        hp_bar_height = 20
        hp_bar_x = 50
        hp_bar_y = 10
        
        hp_ratio = max(0, min(1, player.hp / player.max_hp)) if player.max_hp > 0 else 0
        
        pygame.draw.rect(self.screen, config.DARK_GRAY, 
                        (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        hp_fill = int(hp_ratio * hp_bar_width)
        
        if hp_ratio > 0.5:
            hp_color = config.GREEN
        elif hp_ratio > 0.25:
            hp_color = config.YELLOW
        else:
            hp_color = config.RED
            
        pygame.draw.rect(self.screen, hp_color, 
                        (hp_bar_x, hp_bar_y, hp_fill, hp_bar_height))
        pygame.draw.rect(self.screen, config.WHITE, 
                        (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)
        
        hp_value_text = self.small_font.render(f"{player.hp}/{player.max_hp}", True, config.WHITE)
        hp_value_x = hp_bar_x + (hp_bar_width - hp_value_text.get_width()) // 2
        self.screen.blit(hp_value_text, (hp_value_x, hp_bar_y + 2))
        
        gold_text = self.font.render(f"Gold: {player.gold}", True, config.COIN_COLOR)
        self.screen.blit(gold_text, (190, 10))
        
        attack_text = self.font.render(f"ATK: {player.attack}", True, config.GREEN)
        self.screen.blit(attack_text, (320, 10))
        
        level_text = self.font.render(f"Lv: {current_level}", True, config.PURPLE)
        self.screen.blit(level_text, (430, 10))
        
        kills_text = self.font.render(f"Kills: {total_kills}", True, config.RED)
        self.screen.blit(kills_text, (520, 10))
        
        pygame.draw.rect(self.screen, config.GREEN, self.save_button)
        pygame.draw.rect(self.screen, config.WHITE, self.save_button, 2)
        save_text = self.small_font.render("Save", True, config.WHITE)
        self.screen.blit(save_text, (self.save_button.x + 20, self.save_button.y + 7))
        
        pygame.draw.rect(self.screen, config.BLUE, self.load_button)
        pygame.draw.rect(self.screen, config.WHITE, self.load_button, 2)
        load_text = self.small_font.render("Load", True, config.WHITE)
        self.screen.blit(load_text, (self.load_button.x + 18, self.load_button.y + 7))
        
        self.draw_bottom_bar(player)
        
        if self.show_save_message:
            self.draw_message()
            
    def draw_bottom_bar(self, player):
        bottom_rect = pygame.Rect(0, config.SCREEN_HEIGHT - 50, config.SCREEN_WIDTH, 50)
        pygame.draw.rect(self.screen, config.UI_BG_COLOR, bottom_rect)
        
        upgrade_cost = 30
        can_upgrade = player.gold >= upgrade_cost
        
        if can_upgrade:
            pygame.draw.rect(self.screen, config.GREEN, self.upgrade_button)
        else:
            pygame.draw.rect(self.screen, config.DARK_GRAY, self.upgrade_button)
        pygame.draw.rect(self.screen, config.WHITE, self.upgrade_button, 2)
        
        upgrade_text = self.small_font.render(f"Upgrade({upgrade_cost}G)", True, config.WHITE)
        text_x = self.upgrade_button.x + (self.upgrade_button.width - upgrade_text.get_width()) // 2
        self.screen.blit(upgrade_text, (text_x, self.upgrade_button.y + 10))
        
        controls_text = self.small_font.render("WASD/Arrows: Move | Space: Attack | ESC: Quit", True, config.WHITE)
        self.screen.blit(controls_text, (420, config.SCREEN_HEIGHT - 35))
        
    def draw_message(self):
        if self.save_message_timer > 0:
            msg_surface = self.font.render(self.save_message, True, config.YELLOW)
            msg_rect = msg_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 80))
            
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, config.UI_BG_COLOR, bg_rect)
            pygame.draw.rect(self.screen, config.YELLOW, bg_rect, 2)
            
            self.screen.blit(msg_surface, msg_rect)
            self.save_message_timer -= 1
        else:
            self.show_save_message = False
            
    def show_message(self, message, duration=90):
        self.save_message = message
        self.show_save_message = True
        self.save_message_timer = duration
        
    def draw_battle_ui(self, battle_system):
        if not battle_system.in_battle:
            return
            
        battle_panel = pygame.Rect(200, 200, 400, 200)
        pygame.draw.rect(self.screen, config.UI_BG_COLOR, battle_panel)
        pygame.draw.rect(self.screen, config.WHITE, battle_panel, 3)
        
        title = self.font.render("BATTLE!", True, config.RED)
        self.screen.blit(title, (battle_panel.centerx - title.get_width() // 2, battle_panel.y + 10))
        
        player_hp_ratio = battle_system.player.hp / battle_system.player.max_hp if battle_system.player.max_hp > 0 else 0
        player_hp_text = self.small_font.render(
            f"Your HP: {battle_system.player.hp}/{battle_system.player.max_hp}", True, config.GREEN)
        self.screen.blit(player_hp_text, (battle_panel.x + 20, battle_panel.y + 50))
        
        player_hp_bar = pygame.Rect(battle_panel.x + 20, battle_panel.y + 70, 360, 10)
        pygame.draw.rect(self.screen, config.DARK_GRAY, player_hp_bar)
        pygame.draw.rect(self.screen, config.GREEN, 
                        (player_hp_bar.x, player_hp_bar.y, int(player_hp_ratio * 360), 10))
        
        monster_hp_ratio = battle_system.monster.hp / battle_system.monster.max_hp if battle_system.monster.max_hp > 0 else 0
        monster_hp_text = self.small_font.render(
            f"Monster HP: {battle_system.monster.hp}/{battle_system.monster.max_hp}", True, config.RED)
        self.screen.blit(monster_hp_text, (battle_panel.x + 20, battle_panel.y + 85))
        
        monster_hp_bar = pygame.Rect(battle_panel.x + 20, battle_panel.y + 105, 360, 10)
        pygame.draw.rect(self.screen, config.DARK_GRAY, monster_hp_bar)
        pygame.draw.rect(self.screen, config.RED, 
                        (monster_hp_bar.x, monster_hp_bar.y, int(monster_hp_ratio * 360), 10))
        
        y_offset = battle_panel.y + 120
        for log_msg in battle_system.battle_log[-3:]:
            log_text = self.small_font.render(log_msg, True, config.WHITE)
            self.screen.blit(log_text, (battle_panel.x + 20, y_offset))
            y_offset += 18
            
        if battle_system.can_attack():
            attack_hint = self.small_font.render("Press SPACE to attack!", True, config.YELLOW)
            self.screen.blit(attack_hint, (battle_panel.centerx - attack_hint.get_width() // 2, 
                                          battle_panel.bottom - 30))
        else:
            cooldown_hint = self.small_font.render("Wait...", True, config.LIGHT_GRAY)
            self.screen.blit(cooldown_hint, (battle_panel.centerx - cooldown_hint.get_width() // 2,
                                            battle_panel.bottom - 30))
            
    def draw_game_over(self, total_kills, current_level):
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.fill(config.BLACK)
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.large_font.render("GAME OVER", True, config.RED)
        text_rect = game_over_text.get_rect(center=(config.SCREEN_WIDTH // 2, 
                                                     config.SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(game_over_text, text_rect)
        
        stats_text = self.font.render(f"Level: {current_level} | Kills: {total_kills}", True, config.WHITE)
        stats_rect = stats_text.get_rect(center=(config.SCREEN_WIDTH // 2, 
                                                  config.SCREEN_HEIGHT // 2))
        self.screen.blit(stats_text, stats_rect)
        
        restart_text = self.font.render("Press R to Restart", True, config.GREEN)
        restart_rect = restart_text.get_rect(center=(config.SCREEN_WIDTH // 2, 
                                                      config.SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
        
        load_text = self.small_font.render("Press L to Load Save", True, config.BLUE)
        load_rect = load_text.get_rect(center=(config.SCREEN_WIDTH // 2, 
                                                config.SCREEN_HEIGHT // 2 + 90))
        self.screen.blit(load_text, load_rect)
        
    def check_button_click(self, pos):
        if self.save_button.collidepoint(pos):
            return "save"
        if self.load_button.collidepoint(pos):
            return "load"
        if self.upgrade_button.collidepoint(pos):
            return "upgrade"
        return None
