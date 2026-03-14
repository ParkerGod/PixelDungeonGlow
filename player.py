import pygame
import config

class Player:
    def __init__(self, x, y):
        self.grid_x = int(x // config.TILE_SIZE)
        self.grid_y = int((y - config.GAME_OFFSET_Y) // config.TILE_SIZE)
        self.x = self.grid_x * config.TILE_SIZE
        self.y = self.grid_y * config.TILE_SIZE + config.GAME_OFFSET_Y
        self.width = config.TILE_SIZE - 4
        self.height = config.TILE_SIZE - 4
        self.hp = config.PLAYER_INITIAL_HP
        self.max_hp = config.PLAYER_INITIAL_HP
        self.attack = config.PLAYER_INITIAL_ATTACK
        self.gold = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self._hp_changed = True
        self._gold_changed = True
        self.move_cooldown = 0
        self.move_delay = 10
        
    def load_from_save(self, save_data):
        if save_data:
            self.hp = save_data.get('hp', self.hp)
            self.max_hp = save_data.get('max_hp', self.max_hp)
            self.attack = save_data.get('attack', self.attack)
            self.gold = save_data.get('gold', self.gold)
            self._hp_changed = True
            self._gold_changed = True
        
    def try_move(self, dx, dy, dungeon):
        if self.move_cooldown > 0:
            return False
            
        new_grid_x = self.grid_x + dx
        new_grid_y = self.grid_y + dy
        
        if new_grid_x < 0 or new_grid_x >= config.GRID_WIDTH:
            return False
        if new_grid_y < 0 or new_grid_y >= config.GRID_HEIGHT:
            return False
            
        if not dungeon.is_floor_tile(new_grid_x, new_grid_y):
            return False
            
        self.grid_x = new_grid_x
        self.grid_y = new_grid_y
        self.x = self.grid_x * config.TILE_SIZE
        self.y = self.grid_y * config.TILE_SIZE + config.GAME_OFFSET_Y
        self.rect.x = self.x
        self.rect.y = self.y
        self.move_cooldown = self.move_delay
        return True
    
    def update(self):
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
    
    def draw(self, screen):
        pygame.draw.rect(screen, config.PLAYER_COLOR, self.rect)
        pygame.draw.rect(screen, config.WHITE, self.rect, 2)
        eye_size = 4
        pygame.draw.circle(screen, config.WHITE, 
                          (int(self.rect.centerx - 5), int(self.rect.centery - 2)), eye_size)
        pygame.draw.circle(screen, config.WHITE, 
                          (int(self.rect.centerx + 5), int(self.rect.centery - 2)), eye_size)
        
    def take_damage(self, damage):
        old_hp = self.hp
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        if self.hp != old_hp:
            self._hp_changed = True
            
    def heal(self, amount):
        old_hp = self.hp
        self.hp = min(self.hp + amount, self.max_hp)
        if self.hp != old_hp:
            self._hp_changed = True
        
    def add_gold(self, amount):
        if amount > 0:
            self.gold += amount
            self._gold_changed = True
        
    def upgrade_attack(self, cost=30):
        if self.gold >= cost:
            self.gold -= cost
            self.attack += 5
            self._gold_changed = True
            return True
        return False
    
    def is_alive(self):
        return self.hp > 0
    
    def get_grid_pos(self):
        return (self.grid_x, self.grid_y)
    
    def hp_changed(self):
        changed = self._hp_changed
        self._hp_changed = False
        return changed
    
    def gold_changed(self):
        changed = self._gold_changed
        self._gold_changed = False
        return changed
    
    def get_save_data(self):
        return {
            'hp': self.hp,
            'max_hp': self.max_hp,
            'attack': self.attack,
            'gold': self.gold
        }
    
    def set_position(self, x, y):
        self.grid_x = int(x // config.TILE_SIZE)
        self.grid_y = int((y - config.GAME_OFFSET_Y) // config.TILE_SIZE)
        self.x = self.grid_x * config.TILE_SIZE
        self.y = self.grid_y * config.TILE_SIZE + config.GAME_OFFSET_Y
        self.rect.x = self.x
        self.rect.y = self.y
