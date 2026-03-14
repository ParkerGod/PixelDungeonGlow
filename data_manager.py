import sqlite3
import os
from config import *

class DataManager:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.init_database()
    
    def init_database(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.create_tables()
        except sqlite3.Error as e:
            print(f"数据库初始化错误: {e}")
    
    def create_tables(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hp INTEGER NOT NULL,
                    max_hp INTEGER NOT NULL,
                    atk INTEGER NOT NULL,
                    gold INTEGER NOT NULL,
                    level INTEGER NOT NULL,
                    x REAL NOT NULL,
                    y REAL NOT NULL
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    current_level INTEGER NOT NULL,
                    save_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fps INTEGER NOT NULL,
                    volume INTEGER NOT NULL
                )
            ''')
            
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"创建表错误: {e}")
    
    def save_player(self, player):
        try:
            self.cursor.execute('DELETE FROM player_data')
            self.cursor.execute('''
                INSERT INTO player_data (hp, max_hp, atk, gold, level, x, y)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (player.hp, player.max_hp, player.atk, player.gold, player.level, player.x, player.y))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"存档错误: {e}")
            return False
    
    def load_player(self, player):
        try:
            self.cursor.execute('SELECT * FROM player_data ORDER BY id DESC LIMIT 1')
            data = self.cursor.fetchone()
            if data:
                player.hp = data[1]
                player.max_hp = data[2]
                player.atk = data[3]
                player.gold = data[4]
                player.level = data[5]
                player.x = data[6]
                player.y = data[7]
                player.rect.x = data[6]
                player.rect.y = data[7]
                return True
        except sqlite3.Error as e:
            print(f"读档错误: {e}")
        return False
    
    def save_game_state(self, level):
        try:
            self.cursor.execute('DELETE FROM game_state')
            self.cursor.execute('''
                INSERT INTO game_state (current_level) VALUES (?)
            ''', (level,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"保存游戏状态错误: {e}")
            return False
    
    def load_game_state(self):
        try:
            self.cursor.execute('SELECT * FROM game_state ORDER BY id DESC LIMIT 1')
            data = self.cursor.fetchone()
            if data:
                return data[1]
        except sqlite3.Error as e:
            print(f"读取游戏状态错误: {e}")
        return 1
    
    def has_save(self):
        try:
            self.cursor.execute('SELECT COUNT(*) FROM player_data')
            count = self.cursor.fetchone()[0]
            return count > 0
        except sqlite3.Error as e:
            print(f"检查存档错误: {e}")
            return False
    
    def clear_save(self):
        try:
            self.cursor.execute('DELETE FROM player_data')
            self.cursor.execute('DELETE FROM game_state')
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"清除存档错误: {e}")
            return False
    
    def close(self):
        if self.conn:
            self.conn.close()
