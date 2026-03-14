# data_manager.py - 数据管理模块
# 封装SQLite操作，实现存档/读档功能

import sqlite3
import json
from config import DB_NAME, PLAYER_DEFAULT_HP, PLAYER_DEFAULT_ATTACK, PLAYER_DEFAULT_SPEED, PLAYER_DEFAULT_GOLD


class DataManager:
    """数据管理器 - 处理游戏存档/读档"""
    
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._init_database()
    
    def _init_database(self):
        """初始化数据库连接和表结构"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self._create_tables()
        except sqlite3.Error as e:
            print(f"数据库初始化错误: {e}")
    
    def _create_tables(self):
        """创建游戏数据表"""
        # 玩家属性表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT UNIQUE NOT NULL,
                hp INTEGER DEFAULT 100,
                max_hp INTEGER DEFAULT 100,
                attack INTEGER DEFAULT 10,
                speed INTEGER DEFAULT 4,
                gold INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                dungeon_level INTEGER DEFAULT 1,
                pos_x INTEGER DEFAULT 1,
                pos_y INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 游戏进度表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT UNIQUE NOT NULL,
                current_state TEXT DEFAULT 'playing',
                unlocked_levels TEXT DEFAULT '1',
                play_time INTEGER DEFAULT 0,
                monsters_killed INTEGER DEFAULT 0,
                coins_collected INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 地图数据表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS map_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                dungeon_level INTEGER DEFAULT 1,
                map_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(player_id, dungeon_level)
            )
        ''')
        
        self.conn.commit()
    
    def save_player_data(self, player_id, player_data):
        """
        保存玩家数据
        :param player_id: 玩家ID
        :param player_data: 包含玩家属性的字典
        :return: bool 是否保存成功
        """
        try:
            # 检查表是否存在，如果不存在则创建
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id TEXT UNIQUE NOT NULL,
                    hp INTEGER DEFAULT 100,
                    max_hp INTEGER DEFAULT 100,
                    attack INTEGER DEFAULT 10,
                    speed INTEGER DEFAULT 4,
                    gold INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    dungeon_level INTEGER DEFAULT 1,
                    exp INTEGER DEFAULT 0,
                    exp_to_next_level INTEGER DEFAULT 100,
                    monsters_killed INTEGER DEFAULT 0,
                    pos_x INTEGER DEFAULT 1,
                    pos_y INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()

            self.cursor.execute('''
                INSERT OR REPLACE INTO player_data
                (player_id, hp, max_hp, attack, speed, gold, level, dungeon_level,
                 exp, exp_to_next_level, monsters_killed, pos_x, pos_y, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                player_id,
                player_data.get('hp', PLAYER_DEFAULT_HP),
                player_data.get('max_hp', PLAYER_DEFAULT_HP),
                player_data.get('attack', PLAYER_DEFAULT_ATTACK),
                player_data.get('speed', PLAYER_DEFAULT_SPEED),
                player_data.get('gold', PLAYER_DEFAULT_GOLD),
                player_data.get('level', 1),
                player_data.get('dungeon_level', 1),
                player_data.get('exp', 0),
                player_data.get('exp_to_next_level', 100),
                player_data.get('monsters_killed', 0),
                player_data.get('pos_x', 1),
                player_data.get('pos_y', 1)
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"保存玩家数据错误: {e}")
            return False
    
    def load_player_data(self, player_id):
        """
        加载玩家数据
        :param player_id: 玩家ID
        :return: dict 玩家数据字典，如果不存在返回None
        """
        try:
            # 确保表存在
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id TEXT UNIQUE NOT NULL,
                    hp INTEGER DEFAULT 100,
                    max_hp INTEGER DEFAULT 100,
                    attack INTEGER DEFAULT 10,
                    speed INTEGER DEFAULT 4,
                    gold INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    dungeon_level INTEGER DEFAULT 1,
                    exp INTEGER DEFAULT 0,
                    exp_to_next_level INTEGER DEFAULT 100,
                    monsters_killed INTEGER DEFAULT 0,
                    pos_x INTEGER DEFAULT 1,
                    pos_y INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()

            self.cursor.execute('''
                SELECT hp, max_hp, attack, speed, gold, level, dungeon_level,
                       exp, exp_to_next_level, monsters_killed, pos_x, pos_y
                FROM player_data WHERE player_id = ?
            ''', (player_id,))

            row = self.cursor.fetchone()
            if row:
                return {
                    'hp': row[0],
                    'max_hp': row[1],
                    'attack': row[2],
                    'speed': row[3],
                    'gold': row[4],
                    'level': row[5],
                    'dungeon_level': row[6],
                    'exp': row[7],
                    'exp_to_next_level': row[8],
                    'monsters_killed': row[9],
                    'pos_x': row[10],
                    'pos_y': row[11]
                }
            return None
        except sqlite3.Error as e:
            print(f"加载玩家数据错误: {e}")
            return None
    
    def save_game_progress(self, player_id, progress_data):
        """
        保存游戏进度
        :param player_id: 玩家ID
        :param progress_data: 包含进度信息的字典
        :return: bool 是否保存成功
        """
        try:
            unlocked_levels = json.dumps(progress_data.get('unlocked_levels', [1]))
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO game_progress 
                (player_id, current_state, unlocked_levels, play_time, monsters_killed, coins_collected, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                player_id,
                progress_data.get('current_state', 'playing'),
                unlocked_levels,
                progress_data.get('play_time', 0),
                progress_data.get('monsters_killed', 0),
                progress_data.get('coins_collected', 0)
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"保存游戏进度错误: {e}")
            return False
    
    def load_game_progress(self, player_id):
        """
        加载游戏进度
        :param player_id: 玩家ID
        :return: dict 进度数据字典，如果不存在返回None
        """
        try:
            self.cursor.execute('''
                SELECT current_state, unlocked_levels, play_time, monsters_killed, coins_collected
                FROM game_progress WHERE player_id = ?
            ''', (player_id,))
            
            row = self.cursor.fetchone()
            if row:
                return {
                    'current_state': row[0],
                    'unlocked_levels': json.loads(row[1]),
                    'play_time': row[2],
                    'monsters_killed': row[3],
                    'coins_collected': row[4]
                }
            return None
        except sqlite3.Error as e:
            print(f"加载游戏进度错误: {e}")
            return None
    
    def save_map_data(self, player_id, dungeon_level, map_data):
        """
        保存地图数据
        :param player_id: 玩家ID
        :param dungeon_level: 地牢层数
        :param map_data: 地图数据字典
        :return: bool 是否保存成功
        """
        try:
            map_json = json.dumps(map_data)
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO map_data 
                (player_id, dungeon_level, map_data, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (player_id, dungeon_level, map_json))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"保存地图数据错误: {e}")
            return False
    
    def load_map_data(self, player_id, dungeon_level):
        """
        加载地图数据
        :param player_id: 玩家ID
        :param dungeon_level: 地牢层数
        :return: dict 地图数据字典，如果不存在返回None
        """
        try:
            self.cursor.execute('''
                SELECT map_data FROM map_data 
                WHERE player_id = ? AND dungeon_level = ?
            ''', (player_id, dungeon_level))
            
            row = self.cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None
        except sqlite3.Error as e:
            print(f"加载地图数据错误: {e}")
            return None
    
    def create_new_player(self, player_id):
        """
        创建新玩家数据
        :param player_id: 玩家ID
        :return: bool 是否创建成功
        """
        default_player_data = {
            'hp': PLAYER_DEFAULT_HP,
            'max_hp': PLAYER_DEFAULT_HP,
            'attack': PLAYER_DEFAULT_ATTACK,
            'speed': PLAYER_DEFAULT_SPEED,
            'gold': PLAYER_DEFAULT_GOLD,
            'level': 1,
            'dungeon_level': 1,
            'pos_x': 1,
            'pos_y': 1
        }
        
        default_progress = {
            'current_state': 'playing',
            'unlocked_levels': [1],
            'play_time': 0,
            'monsters_killed': 0,
            'coins_collected': 0
        }
        
        success1 = self.save_player_data(player_id, default_player_data)
        success2 = self.save_game_progress(player_id, default_progress)
        
        return success1 and success2
    
    def player_exists(self, player_id):
        """
        检查玩家是否存在
        :param player_id: 玩家ID
        :return: bool 玩家是否存在
        """
        try:
            # 确保表存在
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id TEXT UNIQUE NOT NULL,
                    hp INTEGER DEFAULT 100,
                    max_hp INTEGER DEFAULT 100,
                    attack INTEGER DEFAULT 10,
                    speed INTEGER DEFAULT 4,
                    gold INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    dungeon_level INTEGER DEFAULT 1,
                    exp INTEGER DEFAULT 0,
                    exp_to_next_level INTEGER DEFAULT 100,
                    monsters_killed INTEGER DEFAULT 0,
                    pos_x INTEGER DEFAULT 1,
                    pos_y INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()

            self.cursor.execute('''
                SELECT COUNT(*) FROM player_data WHERE player_id = ?
            ''', (player_id,))

            count = self.cursor.fetchone()[0]
            return count > 0
        except sqlite3.Error as e:
            print(f"检查玩家存在错误: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
