# player.py - 角色模块
# 管理玩家属性、移动、状态

import pygame
from config import (
    TILE_SIZE, COLOR_PLAYER,
    PLAYER_DEFAULT_HP, PLAYER_DEFAULT_ATTACK, PLAYER_DEFAULT_SPEED, PLAYER_DEFAULT_GOLD
)


class Player:
    """玩家类 - 管理玩家属性、移动和状态"""
    
    def __init__(self, x=1, y=1, data_manager=None):
        # 位置属性 (网格坐标)
        self.grid_x = x
        self.grid_y = y
        
        # 像素位置 (用于平滑移动)
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE
        
        # 战斗属性
        self.hp = PLAYER_DEFAULT_HP
        self.max_hp = PLAYER_DEFAULT_HP
        self.attack = PLAYER_DEFAULT_ATTACK
        self.speed = PLAYER_DEFAULT_SPEED
        self.gold = PLAYER_DEFAULT_GOLD
        self.level = 1
        self.dungeon_level = 1
        
        # 经验值系统
        self.exp = 0
        self.exp_to_next_level = 100
        
        # 击杀统计
        self.monsters_killed = 0
        
        # 数据管理器引用
        self.data_manager = data_manager
        self.player_id = "player_1"
        
        # 移动状态
        self.is_moving = False
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y
        self.move_speed = 4  # 像素移动速度
        
        # 战斗状态
        self.in_battle = False
        self.is_alive = True
        
        # 属性监听器 (用于UI更新)
        self._hp_listeners = []
        self._gold_listeners = []
    
    def add_hp_listener(self, callback):
        """添加血量变化监听器"""
        if callback not in self._hp_listeners:
            self._hp_listeners.append(callback)
    
    def add_gold_listener(self, callback):
        """添加金币变化监听器"""
        if callback not in self._gold_listeners:
            self._gold_listeners.append(callback)
    
    def _notify_hp_change(self):
        """通知血量变化"""
        for callback in self._hp_listeners:
            callback(self.hp, self.max_hp)
    
    def _notify_gold_change(self):
        """通知金币变化"""
        for callback in self._gold_listeners:
            callback(self.gold)
    
    def load_from_save(self, player_data):
        """从存档加载玩家数据"""
        if player_data:
            self.hp = player_data.get('hp', PLAYER_DEFAULT_HP)
            self.max_hp = player_data.get('max_hp', PLAYER_DEFAULT_HP)
            self.attack = player_data.get('attack', PLAYER_DEFAULT_ATTACK)
            self.speed = player_data.get('speed', PLAYER_DEFAULT_SPEED)
            self.gold = player_data.get('gold', PLAYER_DEFAULT_GOLD)
            self.level = player_data.get('level', 1)
            self.dungeon_level = player_data.get('dungeon_level', 1)
            self.exp = player_data.get('exp', 0)
            self.exp_to_next_level = player_data.get('exp_to_next_level', 100)
            self.monsters_killed = player_data.get('monsters_killed', 0)
            
            # 设置位置
            self.grid_x = player_data.get('pos_x', 1)
            self.grid_y = player_data.get('pos_y', 1)
            self.pixel_x = self.grid_x * TILE_SIZE
            self.pixel_y = self.grid_y * TILE_SIZE
            self.target_x = self.pixel_x
            self.target_y = self.pixel_y
            
            # 通知UI更新
            self._notify_hp_change()
            self._notify_gold_change()
    
    def get_save_data(self):
        """获取用于存档的数据字典"""
        return {
            'hp': self.hp,
            'max_hp': self.max_hp,
            'attack': self.attack,
            'speed': self.speed,
            'gold': self.gold,
            'level': self.level,
            'dungeon_level': self.dungeon_level,
            'pos_x': self.grid_x,
            'pos_y': self.grid_y,
            'exp': self.exp,
            'exp_to_next_level': self.exp_to_next_level,
            'monsters_killed': self.monsters_killed
        }
    
    def save_to_database(self):
        """保存玩家数据到数据库"""
        if self.data_manager:
            return self.data_manager.save_player_data(self.player_id, self.get_save_data())
        return False
    
    def move(self, dx, dy, dungeon_map):
        """
        移动玩家
        :param dx: x方向移动量 (-1, 0, 1)
        :param dy: y方向移动量 (-1, 0, 1)
        :param dungeon_map: 地牢地图对象
        :return: bool 是否成功移动
        """
        if self.is_moving or self.in_battle or not self.is_alive:
            return False
        
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy
        
        # 检查边界和碰撞
        if dungeon_map.is_walkable(new_x, new_y):
            self.grid_x = new_x
            self.grid_y = new_y
            self.target_x = new_x * TILE_SIZE
            self.target_y = new_y * TILE_SIZE
            self.is_moving = True
            return True
        
        return False
    
    def update(self):
        """更新玩家状态 (每帧调用)"""
        # 处理平滑移动
        if self.is_moving:
            dx = self.target_x - self.pixel_x
            dy = self.target_y - self.pixel_y
            
            if abs(dx) <= self.move_speed and abs(dy) <= self.move_speed:
                self.pixel_x = self.target_x
                self.pixel_y = self.target_y
                self.is_moving = False
            else:
                if dx > 0:
                    self.pixel_x += self.move_speed
                elif dx < 0:
                    self.pixel_x -= self.move_speed
                
                if dy > 0:
                    self.pixel_y += self.move_speed
                elif dy < 0:
                    self.pixel_y -= self.move_speed
    
    def take_damage(self, damage):
        """
        受到伤害
        :param damage: 伤害值
        :return: bool 是否仍然存活
        """
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        
        self._notify_hp_change()
        
        if self.hp <= 0:
            self.is_alive = False
            return False
        return True
    
    def heal(self, amount):
        """
        恢复生命值
        :param amount: 恢复量
        """
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        self._notify_hp_change()
    
    def add_gold(self, amount):
        """
        增加金币
        :param amount: 金币数量
        """
        self.gold += amount
        self._notify_gold_change()
    
    def spend_gold(self, amount):
        """
        花费金币
        :param amount: 花费数量
        :return: bool 是否成功花费
        """
        if self.gold >= amount:
            self.gold -= amount
            self._notify_gold_change()
            return True
        return False
    
    def upgrade_attack(self, cost=50):
        """
        升级攻击力
        :param cost: 升级花费
        :return: bool 是否升级成功
        """
        if self.spend_gold(cost):
            self.attack += 5
            return True
        return False
    
    def get_attack_damage(self):
        """获取攻击伤害值"""
        return self.attack
    
    def draw(self, screen):
        """
        绘制玩家
        :param screen: Pygame屏幕对象
        """
        # 绘制玩家主体 (像素风格方块)
        rect = pygame.Rect(self.pixel_x + 4, self.pixel_y + 4, TILE_SIZE - 8, TILE_SIZE - 8)
        pygame.draw.rect(screen, COLOR_PLAYER, rect)
        
        # 绘制像素风格细节
        # 眼睛
        eye_size = 4
        left_eye = pygame.Rect(self.pixel_x + 8, self.pixel_y + 10, eye_size, eye_size)
        right_eye = pygame.Rect(self.pixel_x + 20, self.pixel_y + 10, eye_size, eye_size)
        pygame.draw.rect(screen, (0, 0, 0), left_eye)
        pygame.draw.rect(screen, (0, 0, 0), right_eye)
    
    def get_rect(self):
        """获取玩家碰撞矩形"""
        return pygame.Rect(self.pixel_x, self.pixel_y, TILE_SIZE, TILE_SIZE)
    
    def get_position(self):
        """获取当前网格位置"""
        return (self.grid_x, self.grid_y)
    
    def reset(self):
        """重置玩家状态"""
        self.hp = PLAYER_DEFAULT_HP
        self.max_hp = PLAYER_DEFAULT_HP
        self.attack = PLAYER_DEFAULT_ATTACK
        self.gold = PLAYER_DEFAULT_GOLD
        self.level = 1
        self.dungeon_level = 1
        self.exp = 0
        self.exp_to_next_level = 100
        self.monsters_killed = 0
        self.grid_x = 1
        self.grid_y = 1
        self.pixel_x = TILE_SIZE
        self.pixel_y = TILE_SIZE
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y
        self.is_moving = False
        self.in_battle = False
        self.is_alive = True
        self._notify_hp_change()
        self._notify_gold_change()
    
    def add_exp(self, amount):
        """
        增加经验值
        :param amount: 经验值数量
        :return: bool 是否升级
        """
        self.exp += amount
        
        # 检查升级
        if self.exp >= self.exp_to_next_level:
            return self.level_up()
        return False
    
    def level_up(self):
        """
        玩家升级
        :return: bool 是否升级成功
        """
        self.level += 1
        self.exp -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        
        # 提升属性
        self.max_hp += 20
        self.hp = self.max_hp
        self.attack += 3
        
        self._notify_hp_change()
        return True
    
    def get_exp_percentage(self):
        """获取经验值百分比"""
        if self.exp_to_next_level > 0:
            return min(100, int((self.exp / self.exp_to_next_level) * 100))
        return 0
