import random
import pygame
import config

class Room:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def intersects(self, other):
        return (self.x <= other.x + other.width + 1 and
                self.x + self.width + 1 >= other.x and
                self.y <= other.y + other.height + 1 and
                self.y + self.height + 1 >= other.y)

class Monster:
    def __init__(self, x, y, level=1):
        self.x = x
        self.y = y
        self.width = config.TILE_SIZE - 6
        self.height = config.TILE_SIZE - 6
        self.hp = config.MONSTER_HP + (level - 1) * 10
        self.max_hp = self.hp
        self.attack = config.MONSTER_ATTACK + (level - 1) * 2
        self.rect = pygame.Rect(x + 3, y + 3, self.width, self.height)
        self.alive = True
        self.level = level
        
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            
    def draw(self, screen, offset_y=0):
        if self.alive:
            draw_rect = pygame.Rect(self.rect.x, self.rect.y + offset_y, self.width, self.height)
            pygame.draw.rect(screen, config.MONSTER_COLOR, draw_rect)
            pygame.draw.rect(screen, config.WHITE, draw_rect, 1)
            hp_bar_width = int((self.hp / self.max_hp) * self.width)
            pygame.draw.rect(screen, config.RED, 
                           (draw_rect.x, draw_rect.y - 5, hp_bar_width, 3))
            pygame.draw.circle(screen, config.WHITE, 
                             (draw_rect.centerx, draw_rect.centery), 4)

class Coin:
    def __init__(self, x, y, value=10):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.value = value
        self.rect = pygame.Rect(x + 8, y + 8, self.width, self.height)
        self.collected = False
        self.animation_offset = random.randint(0, 360)
        
    def draw(self, screen, frame_count=0, offset_y=0):
        if not self.collected:
            bob_offset = int(3 * abs((frame_count + self.animation_offset) % 60 - 30) / 30)
            center_y = self.y + config.TILE_SIZE // 2 - bob_offset + offset_y
            pygame.draw.circle(screen, config.COIN_COLOR, 
                             (self.x + config.TILE_SIZE // 2, center_y), 8)
            pygame.draw.circle(screen, config.WHITE, 
                             (self.x + config.TILE_SIZE // 2, center_y), 8, 1)

class DungeonMap:
    def __init__(self, level=1):
        self.tiles = [[1 for _ in range(config.GRID_WIDTH)] 
                      for _ in range(config.GRID_HEIGHT)]
        self.walls = []
        self.rooms = []
        self.monsters = []
        self.coins = []
        self.level = level
        self.generate()
        
    def generate(self):
        self.tiles = [[1 for _ in range(config.GRID_WIDTH)] 
                      for _ in range(config.GRID_HEIGHT)]
        self.rooms = []
        self.monsters = []
        self.coins = []
        
        num_rooms = min(config.MAP_MAX_ROOMS + self.level, 12)
        
        attempts = 0
        max_attempts = 100
        
        while len(self.rooms) < num_rooms and attempts < max_attempts:
            width = random.randint(config.MAP_ROOM_MIN_SIZE, config.MAP_ROOM_MAX_SIZE)
            height = random.randint(config.MAP_ROOM_MIN_SIZE, config.MAP_ROOM_MAX_SIZE)
            x = random.randint(1, max(1, config.GRID_WIDTH - width - 2))
            y = random.randint(1, max(1, config.GRID_HEIGHT - height - 2))
            
            new_room = Room(x, y, width, height)
            
            failed = False
            for other_room in self.rooms:
                if new_room.intersects(other_room):
                    failed = True
                    break
                    
            if not failed:
                self.create_room(new_room)
                
                if self.rooms:
                    prev_center = self.rooms[-1].center()
                    new_center = new_room.center()
                    self.create_corridor(prev_center, new_center)
                    
                self.rooms.append(new_room)
                
            attempts += 1
                
        self.update_walls()
        self.spawn_monsters()
        self.spawn_coins()
        
    def create_room(self, room):
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if 0 <= x < config.GRID_WIDTH and 0 <= y < config.GRID_HEIGHT:
                    self.tiles[y][x] = 0
                    
    def create_corridor(self, start, end):
        x1, y1 = start
        x2, y2 = end
        
        if random.random() < 0.5:
            self.create_h_corridor(x1, x2, y1)
            self.create_v_corridor(y1, y2, x2)
        else:
            self.create_v_corridor(y1, y2, x1)
            self.create_h_corridor(x1, x2, y2)
            
    def create_h_corridor(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < config.GRID_WIDTH and 0 <= y < config.GRID_HEIGHT:
                self.tiles[y][x] = 0
                
    def create_v_corridor(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < config.GRID_WIDTH and 0 <= y < config.GRID_HEIGHT:
                self.tiles[y][x] = 0
                
    def update_walls(self):
        self.walls = []
        for y in range(config.GRID_HEIGHT):
            for x in range(config.GRID_WIDTH):
                if self.tiles[y][x] == 1:
                    wall_rect = pygame.Rect(x * config.TILE_SIZE, 
                                           y * config.TILE_SIZE + config.GAME_OFFSET_Y,
                                           config.TILE_SIZE, config.TILE_SIZE)
                    self.walls.append(wall_rect)
                    
    def spawn_monsters(self):
        monster_chance = min(0.5 + self.level * 0.05, 0.85)
        
        for room in self.rooms[1:]:
            if random.random() < monster_chance:
                cx, cy = room.center()
                px = cx * config.TILE_SIZE
                py = cy * config.TILE_SIZE + config.GAME_OFFSET_Y
                monster = Monster(px, py, self.level)
                self.monsters.append(monster)
                
                if random.random() < 0.25 and len(self.monsters) < 10:
                    offset_x = random.choice([-1, 1]) * config.TILE_SIZE
                    offset_y = random.choice([-1, 1]) * config.TILE_SIZE
                    new_x = px + offset_x
                    new_y = py + offset_y
                    
                    grid_x = int(new_x // config.TILE_SIZE)
                    grid_y = int((new_y - config.GAME_OFFSET_Y) // config.TILE_SIZE)
                    
                    if self.is_floor_tile(grid_x, grid_y):
                        extra_monster = Monster(new_x, new_y, self.level)
                        self.monsters.append(extra_monster)
                
    def spawn_coins(self):
        for room in self.rooms:
            num_coins = random.randint(2, 4 + self.level)
            for _ in range(num_coins):
                x = random.randint(room.x + 1, room.x + room.width - 2)
                y = random.randint(room.y + 1, room.y + room.height - 2)
                value = random.randint(5, 15) + self.level * 2
                coin = Coin(x * config.TILE_SIZE, y * config.TILE_SIZE + config.GAME_OFFSET_Y, value)
                self.coins.append(coin)
                
    def draw(self, screen, frame_count=0):
        for y in range(config.GRID_HEIGHT):
            for x in range(config.GRID_WIDTH):
                rect = pygame.Rect(x * config.TILE_SIZE, 
                                  y * config.TILE_SIZE + config.GAME_OFFSET_Y,
                                  config.TILE_SIZE, config.TILE_SIZE)
                if self.tiles[y][x] == 1:
                    pygame.draw.rect(screen, config.WALL_COLOR, rect)
                    pygame.draw.rect(screen, (60, 60, 60), rect, 1)
                else:
                    pygame.draw.rect(screen, config.FLOOR_COLOR, rect)
                    
        for monster in self.monsters:
            monster.draw(screen)
            
        for coin in self.coins:
            coin.draw(screen, frame_count)
            
    def get_player_spawn(self):
        if self.rooms:
            cx, cy = self.rooms[0].center()
            return (cx * config.TILE_SIZE, cy * config.TILE_SIZE + config.GAME_OFFSET_Y)
        return (config.TILE_SIZE, config.TILE_SIZE + config.GAME_OFFSET_Y)
    
    def check_coin_collision(self, player_rect):
        for coin in self.coins:
            if not coin.collected and player_rect.colliderect(coin.rect):
                coin.collected = True
                return coin.value
        return 0
    
    def check_monster_collision(self, player_rect):
        for monster in self.monsters:
            if monster.alive and player_rect.colliderect(monster.rect):
                return monster
        return None
    
    def get_alive_monster_count(self):
        return sum(1 for m in self.monsters if m.alive)
    
    def is_floor_tile(self, grid_x, grid_y):
        if 0 <= grid_x < config.GRID_WIDTH and 0 <= grid_y < config.GRID_HEIGHT:
            return self.tiles[grid_y][grid_x] == 0
        return False
    
    def get_game_bounds(self):
        return {
            'min_x': 0,
            'max_x': config.GRID_WIDTH * config.TILE_SIZE,
            'min_y': config.GAME_OFFSET_Y,
            'max_y': config.GAME_OFFSET_Y + config.GRID_HEIGHT * config.TILE_SIZE
        }
