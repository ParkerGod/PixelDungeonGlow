import pygame
import random
from config import *

class MapGenerator:
    def __init__(self):
        self.grid_width = GRID_WIDTH
        self.grid_height = GRID_HEIGHT
        self.tile_size = TILE_SIZE
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.walls = []
        self.monsters = []
        self.gold_items = []
    
    def generate_map(self):
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if x == 0 or y == 0 or x == self.grid_width - 1 or y == self.grid_height - 1:
                    self.grid[y][x] = 1
                else:
                    self.grid[y][x] = 0
        
        num_rooms = random.randint(5, 8)
        rooms = []
        
        for _ in range(num_rooms):
            room_w = random.randint(3, 7)
            room_h = random.randint(3, 7)
            room_x = random.randint(1, self.grid_width - room_w - 1)
            room_y = random.randint(1, self.grid_height - room_h - 1)
            
            valid = True
            for y in range(room_y, room_y + room_h):
                for x in range(room_x, room_x + room_w):
                    if self.grid[y][x] != 0:
                        valid = False
                        break
                if not valid:
                    break
            
            if valid:
                for y in range(room_y, room_y + room_h):
                    for x in range(room_x, room_x + room_w):
                        self.grid[y][x] = 2
                
                center_x = (room_x + room_w // 2) * TILE_SIZE
                center_y = (room_y + room_h // 2) * TILE_SIZE
                rooms.append((center_x, center_y, room_x, room_y, room_w, room_h))
        
        if len(rooms) > 0:
            main_x, main_y = rooms[0][0] // TILE_SIZE, rooms[0][1] // TILE_SIZE
            for i in range(1, len(rooms)):
                x1, y1 = rooms[i-1][0] // TILE_SIZE, rooms[i-1][1] // TILE_SIZE
                x2, y2 = rooms[i][0] // TILE_SIZE, rooms[i][1] // TILE_SIZE
                self.create_corridor(x1, y1, x2, y2)
        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] == 0:
                    self.grid[y][x] = 1
        
        self.spawn_monsters()
        self.spawn_gold()
        
        return (rooms[0][0], rooms[0][1]) if rooms else (TILE_SIZE * 2, TILE_SIZE * 2)
    
    def create_corridor(self, x1, y1, x2, y2):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if self.grid[y1][x] == 0:
                self.grid[y1][x] = 2
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if self.grid[y][x2] == 0:
                self.grid[y][x2] = 2
    
    def spawn_monsters(self):
        self.monsters = []
        floor_tiles = []
        for y in range(1, self.grid_height - 1):
            for x in range(1, self.grid_width - 1):
                if self.grid[y][x] == 2:
                    floor_tiles.append((x, y))
        
        spawn_count = min(len(floor_tiles) // 8, 8)
        random.shuffle(floor_tiles)
        
        for i in range(spawn_count):
            if i >= len(floor_tiles):
                break
            x, y = floor_tiles[i]
            if not (abs(x * TILE_SIZE - TILE_SIZE * 3) < TILE_SIZE * 3 and 
                    abs(y * TILE_SIZE - TILE_SIZE * 3) < TILE_SIZE * 3):
                monster = Monster(x * TILE_SIZE, y * TILE_SIZE)
                self.monsters.append(monster)
    
    def spawn_gold(self):
        self.gold_items = []
        floor_tiles = []
        for y in range(1, self.grid_height - 1):
            for x in range(1, self.grid_width - 1):
                if self.grid[y][x] == 2:
                    floor_tiles.append((x, y))
        
        spawn_count = min(len(floor_tiles) // 6, 12)
        random.shuffle(floor_tiles)
        
        for i in range(spawn_count):
            if i >= len(floor_tiles):
                break
            x, y = floor_tiles[i]
            self.gold_items.append(pygame.Rect(x * TILE_SIZE + TILE_SIZE//4, 
                                              y * TILE_SIZE + TILE_SIZE//4, 
                                              TILE_SIZE // 2, TILE_SIZE // 2))
    
    def render(self, screen):
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] == 1:
                    pygame.draw.rect(screen, GRAY, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                else:
                    pygame.draw.rect(screen, BLACK, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        
        for gold in self.gold_items:
            pygame.draw.rect(screen, YELLOW, gold)
        
        for monster in self.monsters:
            monster.render(screen)
    
    def check_collision(self, rect):
        if rect.left < 0 or rect.right > WIDTH or rect.top < 0 or rect.bottom > HEIGHT:
            return True
        
        check_points = [
            (rect.left, rect.top),
            (rect.right - 1, rect.top),
            (rect.left, rect.bottom - 1),
            (rect.right - 1, rect.bottom - 1),
            (rect.centerx, rect.centery)
        ]
        
        for (cx, cy) in check_points:
            gx = int(cx // TILE_SIZE)
            gy = int(cy // TILE_SIZE)
            if 0 <= gx < self.grid_width and 0 <= gy < self.grid_height:
                if self.grid[gy][gx] == 1:
                    return True
        
        return False
    
    def check_monster_collision(self, rect):
        for monster in self.monsters:
            if rect.colliderect(monster.rect):
                return monster
        return None
    
    def check_gold_collision(self, rect):
        for gold in self.gold_items[:]:
            if rect.colliderect(gold):
                self.gold_items.remove(gold)
                return random.randint(5, 15)
        return 0
    
    def remove_monster(self, monster):
        if monster in self.monsters:
            self.monsters.remove(monster)


class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.hp = 50
        self.atk = 5
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = RED
    
    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
    
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
    
    def is_alive(self):
        return self.hp > 0
