# map_generator.py - 地牢地图模块
# 生成随机房间/道路，管理地图数据

import random
import pygame
from config import (
    MAP_WIDTH, MAP_HEIGHT, TILE_SIZE,
    COLOR_FLOOR, COLOR_WALL, COLOR_DOOR, COLOR_COIN,
    ROOM_MIN_SIZE, ROOM_MAX_SIZE, MAX_ROOMS,
    MONSTER_DEFAULT_HP, MONSTER_DEFAULT_ATTACK
)


class Room:
    """房间类"""
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center_x = x + width // 2
        self.center_y = y + height // 2
    
    def intersects(self, other):
        """检查是否与另一个房间相交"""
        return (self.x <= other.x + other.width and
                self.x + self.width >= other.x and
                self.y <= other.y + other.height and
                self.y + self.height >= other.y)


class Monster:
    """怪物类"""
    
    # 怪物类型定义
    TYPE_NORMAL = "normal"
    TYPE_STRONG = "strong"
    TYPE_FAST = "fast"
    TYPE_BOSS = "boss"
    
    def __init__(self, x, y, dungeon_level=1, monster_type=None):
        self.x = x
        self.y = y
        self.dungeon_level = dungeon_level
        
        # 随机选择怪物类型
        if monster_type is None:
            self.monster_type = self._random_type(dungeon_level)
        else:
            self.monster_type = monster_type
        
        # 根据类型设置属性
        self._init_stats()
        
        self.alive = True
    
    def _random_type(self, dungeon_level):
        """根据地牢层数随机选择怪物类型"""
        rand = random.random()
        
        if dungeon_level % 5 == 0 and rand < 0.3:  # 每5层有概率出现BOSS
            return self.TYPE_BOSS
        elif rand < 0.6:
            return self.TYPE_NORMAL
        elif rand < 0.8:
            return self.TYPE_STRONG
        else:
            return self.TYPE_FAST
    
    def _init_stats(self):
        """初始化怪物属性"""
        level_bonus = self.dungeon_level - 1
        
        if self.monster_type == self.TYPE_NORMAL:
            self.hp = MONSTER_DEFAULT_HP + level_bonus * 10
            self.attack = MONSTER_DEFAULT_ATTACK + level_bonus * 2
            self.gold_reward = 10 + level_bonus * 5
            self.exp_reward = 20
            self.color = (255, 0, 0)  # 红色
        elif self.monster_type == self.TYPE_STRONG:
            self.hp = int(MONSTER_DEFAULT_HP * 1.5) + level_bonus * 15
            self.attack = int(MONSTER_DEFAULT_ATTACK * 1.3) + level_bonus * 3
            self.gold_reward = 20 + level_bonus * 8
            self.exp_reward = 35
            self.color = (180, 0, 0)  # 深红色
        elif self.monster_type == self.TYPE_FAST:
            self.hp = int(MONSTER_DEFAULT_HP * 0.7) + level_bonus * 5
            self.attack = int(MONSTER_DEFAULT_ATTACK * 0.8) + level_bonus * 2
            self.gold_reward = 15 + level_bonus * 6
            self.exp_reward = 25
            self.color = (255, 100, 0)  # 橙色
        elif self.monster_type == self.TYPE_BOSS:
            self.hp = MONSTER_DEFAULT_HP * 3 + level_bonus * 30
            self.attack = MONSTER_DEFAULT_ATTACK * 2 + level_bonus * 5
            self.gold_reward = 100 + level_bonus * 20
            self.exp_reward = 100
            self.color = (150, 0, 50)  # 紫黑色
        
        self.max_hp = self.hp
    
    def take_damage(self, damage):
        """受到伤害"""
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return self.alive
    
    def get_damage(self):
        """获取攻击伤害"""
        return self.attack
    
    def get_type_name(self):
        """获取怪物类型名称"""
        type_names = {
            self.TYPE_NORMAL: "普通怪物",
            self.TYPE_STRONG: "强壮怪物",
            self.TYPE_FAST: "快速怪物",
            self.TYPE_BOSS: "BOSS"
        }
        return type_names.get(self.monster_type, "未知")


class Coin:
    """金币类"""
    
    def __init__(self, x, y, amount=10):
        self.x = x
        self.y = y
        self.amount = amount
        self.collected = False


class Potion:
    """药水类"""
    
    TYPE_HEAL = "heal"
    TYPE_POWER = "power"
    
    def __init__(self, x, y, potion_type=None):
        self.x = x
        self.y = y
        
        # 随机选择药水类型
        if potion_type is None:
            self.potion_type = random.choice([self.TYPE_HEAL, self.TYPE_POWER])
        else:
            self.potion_type = potion_type
        
        # 设置属性
        if self.potion_type == self.TYPE_HEAL:
            self.value = random.randint(20, 50)  # 恢复生命值
            self.color = (0, 255, 100)  # 绿色
        else:  # TYPE_POWER
            self.value = random.randint(5, 15)  # 临时增加攻击力
            self.color = (255, 100, 255)  # 紫色
        
        self.collected = False
    
    def get_name(self):
        """获取药水名称"""
        if self.potion_type == self.TYPE_HEAL:
            return f"生命药水 (+{self.value} HP)"
        else:
            return f"力量药水 (+{self.value} 攻击)"


class DungeonMap:
    """地牢地图类"""
    
    # 地图元素类型
    TILE_WALL = 0
    TILE_FLOOR = 1
    TILE_DOOR = 2
    
    def __init__(self, width=MAP_WIDTH, height=MAP_HEIGHT, dungeon_level=1):
        self.width = width
        self.height = height
        self.dungeon_level = dungeon_level
        
        # 初始化地图 (全是墙壁)
        self.tiles = [[self.TILE_WALL for _ in range(height)] for _ in range(width)]
        
        # 房间列表
        self.rooms = []
        
        # 怪物列表
        self.monsters = []
        
        # 金币列表
        self.coins = []
        
        # 药水列表
        self.potions = []
        
        # 玩家起始位置
        self.player_start = (1, 1)
        
        # 生成地图
        self.generate()
    
    def generate(self):
        """生成地牢地图"""
        # 生成随机房间
        self._generate_rooms()
        
        # 连接房间
        self._connect_rooms()
        
        # 放置怪物
        self._place_monsters()
        
        # 放置金币
        self._place_coins()
        
        # 放置药水
        self._place_potions()
    
    def _generate_rooms(self):
        """生成随机房间"""
        attempts = 0
        max_attempts = 100
        
        while len(self.rooms) < MAX_ROOMS and attempts < max_attempts:
            attempts += 1
            
            # 随机房间尺寸
            room_width = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            room_height = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            
            # 随机位置
            x = random.randint(1, self.width - room_width - 1)
            y = random.randint(1, self.height - room_height - 1)
            
            new_room = Room(x, y, room_width, room_height)
            
            # 检查是否与其他房间相交
            intersects = False
            for room in self.rooms:
                if new_room.intersects(room):
                    intersects = True
                    break
            
            if not intersects:
                self.rooms.append(new_room)
                self._create_room(new_room)
        
        # 设置玩家起始位置为第一个房间的中心
        if self.rooms:
            first_room = self.rooms[0]
            self.player_start = (first_room.center_x, first_room.center_y)
    
    def _create_room(self, room):
        """在地图上创建房间"""
        for x in range(room.x, room.x + room.width):
            for y in range(room.y, room.y + room.height):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.tiles[x][y] = self.TILE_FLOOR
    
    def _connect_rooms(self):
        """连接所有房间 (使用走廊)"""
        if len(self.rooms) < 2:
            return
        
        for i in range(len(self.rooms) - 1):
            room1 = self.rooms[i]
            room2 = self.rooms[i + 1]
            
            # 随机决定先水平后垂直，或先垂直后水平
            if random.choice([True, False]):
                self._create_h_tunnel(room1.center_x, room2.center_x, room1.center_y)
                self._create_v_tunnel(room1.center_y, room2.center_y, room2.center_x)
            else:
                self._create_v_tunnel(room1.center_y, room2.center_y, room1.center_x)
                self._create_h_tunnel(room1.center_x, room2.center_x, room2.center_y)
    
    def _create_h_tunnel(self, x1, x2, y):
        """创建水平走廊"""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[x][y] = self.TILE_FLOOR
    
    def _create_v_tunnel(self, y1, y2, x):
        """创建垂直走廊"""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[x][y] = self.TILE_FLOOR
    
    def _place_monsters(self):
        """在房间中放置怪物"""
        # 从第二个房间开始放置怪物
        for i in range(1, len(self.rooms)):
            room = self.rooms[i]
            
            # 每个房间随机放置1-2个怪物
            num_monsters = random.randint(1, 2)
            
            for _ in range(num_monsters):
                # 随机选择房间内的位置
                attempts = 0
                while attempts < 10:
                    x = random.randint(room.x + 1, room.x + room.width - 2)
                    y = random.randint(room.y + 1, room.y + room.height - 2)
                    
                    # 检查该位置是否已有怪物
                    if not self.get_monster_at(x, y):
                        monster = Monster(x, y, self.dungeon_level)
                        self.monsters.append(monster)
                        break
                    
                    attempts += 1
    
    def _place_coins(self):
        """在地图中放置金币"""
        # 随机放置金币
        num_coins = random.randint(5, 10)

        for _ in range(num_coins):
            attempts = 0
            while attempts < 20:
                x = random.randint(1, self.width - 2)
                y = random.randint(1, self.height - 2)

                # 检查是否是地板且没有怪物和金币
                if (self.tiles[x][y] == self.TILE_FLOOR and
                    not self.get_monster_at(x, y) and
                    not self.get_coin_at(x, y) and
                    not self.get_potion_at(x, y)):

                    amount = random.randint(5, 20)
                    coin = Coin(x, y, amount)
                    self.coins.append(coin)
                    break

                attempts += 1

    def _place_potions(self):
        """在地图中放置药水"""
        # 随机放置药水
        num_potions = random.randint(2, 5)

        for _ in range(num_potions):
            attempts = 0
            while attempts < 20:
                x = random.randint(1, self.width - 2)
                y = random.randint(1, self.height - 2)

                # 检查是否是地板且没有怪物、金币和药水
                if (self.tiles[x][y] == self.TILE_FLOOR and
                    not self.get_monster_at(x, y) and
                    not self.get_coin_at(x, y) and
                    not self.get_potion_at(x, y)):

                    potion = Potion(x, y)
                    self.potions.append(potion)
                    break

                attempts += 1
    
    def is_walkable(self, x, y):
        """
        检查位置是否可行走
        :param x: 网格x坐标
        :param y: 网格y坐标
        :return: bool 是否可行走
        """
        # 检查边界
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        
        # 检查是否是墙壁
        if self.tiles[x][y] == self.TILE_WALL:
            return False
        
        return True
    
    def get_monster_at(self, x, y):
        """
        获取指定位置的怪物
        :param x: 网格x坐标
        :param y: 网格y坐标
        :return: Monster对象或None
        """
        for monster in self.monsters:
            if monster.x == x and monster.y == y and monster.alive:
                return monster
        return None
    
    def get_coin_at(self, x, y):
        """
        获取指定位置的金币
        :param x: 网格x坐标
        :param y: 网格y坐标
        :return: Coin对象或None
        """
        for coin in self.coins:
            if coin.x == x and coin.y == y and not coin.collected:
                return coin
        return None
    
    def collect_coin(self, x, y):
        """
        收集金币
        :param x: 网格x坐标
        :param y: 网格y坐标
        :return: int 收集到的金币数量，如果没有返回0
        """
        coin = self.get_coin_at(x, y)
        if coin:
            coin.collected = True
            return coin.amount
        return 0

    def get_potion_at(self, x, y):
        """
        获取指定位置的药水
        :param x: 网格x坐标
        :param y: 网格y坐标
        :return: Potion对象或None
        """
        for potion in self.potions:
            if potion.x == x and potion.y == y and not potion.collected:
                return potion
        return None

    def collect_potion(self, x, y):
        """
        收集药水
        :param x: 网格x坐标
        :param y: 网格y坐标
        :return: Potion对象或None
        """
        potion = self.get_potion_at(x, y)
        if potion:
            potion.collected = True
            return potion
        return None
    
    def remove_dead_monsters(self):
        """移除死亡的怪物"""
        self.monsters = [m for m in self.monsters if m.alive]
    
    def get_player_start(self):
        """获取玩家起始位置"""
        return self.player_start
    
    def draw(self, screen):
        """
        绘制地图
        :param screen: Pygame屏幕对象
        """
        # 绘制地图瓦片
        for x in range(self.width):
            for y in range(self.height):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                if self.tiles[x][y] == self.TILE_WALL:
                    pygame.draw.rect(screen, COLOR_WALL, rect)
                    # 绘制墙壁边框
                    pygame.draw.rect(screen, (30, 30, 30), rect, 1)
                elif self.tiles[x][y] == self.TILE_FLOOR:
                    pygame.draw.rect(screen, COLOR_FLOOR, rect)
                    # 绘制地板纹理
                    pygame.draw.rect(screen, (70, 70, 70), rect, 1)
                elif self.tiles[x][y] == self.TILE_DOOR:
                    pygame.draw.rect(screen, COLOR_DOOR, rect)
        
        # 绘制金币
        for coin in self.coins:
            if not coin.collected:
                center_x = coin.x * TILE_SIZE + TILE_SIZE // 2
                center_y = coin.y * TILE_SIZE + TILE_SIZE // 2
                radius = TILE_SIZE // 4
                pygame.draw.circle(screen, COLOR_COIN, (center_x, center_y), radius)
                # 金币光泽效果
                pygame.draw.circle(screen, (255, 255, 200), (center_x - 2, center_y - 2), radius // 3)

        # 绘制药水
        for potion in self.potions:
            if not potion.collected:
                self._draw_potion(screen, potion)

        # 绘制怪物
        for monster in self.monsters:
            if monster.alive:
                self._draw_monster(screen, monster)
    
    def _draw_monster(self, screen, monster):
        """绘制怪物"""
        x = monster.x * TILE_SIZE
        y = monster.y * TILE_SIZE

        # 怪物主体
        rect = pygame.Rect(x + 4, y + 4, TILE_SIZE - 8, TILE_SIZE - 8)
        pygame.draw.rect(screen, monster.color, rect)

        # 怪物眼睛 (愤怒的样子)
        eye_size = 3
        pygame.draw.rect(screen, (255, 255, 0), (x + 8, y + 8, eye_size, eye_size))
        pygame.draw.rect(screen, (255, 255, 0), (x + 21, y + 8, eye_size, eye_size))

        # 怪物嘴巴
        pygame.draw.rect(screen, (0, 0, 0), (x + 10, y + 18, 12, 4))

        # BOSS特殊标记
        if monster.monster_type == Monster.TYPE_BOSS:
            pygame.draw.rect(screen, (255, 215, 0), rect, 2)  # 金色边框

    def _draw_potion(self, screen, potion):
        """绘制药水"""
        x = potion.x * TILE_SIZE
        y = potion.y * TILE_SIZE

        # 药水瓶身
        center_x = x + TILE_SIZE // 2
        center_y = y + TILE_SIZE // 2

        # 瓶身
        bottle_rect = pygame.Rect(x + 8, y + 8, TILE_SIZE - 16, TILE_SIZE - 16)
        pygame.draw.rect(screen, potion.color, bottle_rect)

        # 瓶口
        neck_rect = pygame.Rect(x + 12, y + 4, TILE_SIZE - 24, 6)
        pygame.draw.rect(screen, (200, 200, 200), neck_rect)

        # 高光
        pygame.draw.rect(screen, (255, 255, 255), (x + 10, y + 10, 4, 4))
    
    def get_tile_type(self, x, y):
        """
        获取指定位置的瓦片类型
        :param x: 网格x坐标
        :param y: 网格y坐标
        :return: int 瓦片类型
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[x][y]
        return self.TILE_WALL
    
    def regenerate(self, dungeon_level=None):
        """重新生成地图"""
        if dungeon_level:
            self.dungeon_level = dungeon_level

        # 重置地图
        self.tiles = [[self.TILE_WALL for _ in range(self.height)] for _ in range(self.width)]
        self.rooms = []
        self.monsters = []
        self.coins = []
        self.potions = []

        # 重新生成
        self.generate()
