import sqlite3
import os
import json
import time

DB_NAME = "game_save.db"

class DataManager:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)
        self._ensure_database()
        
    def _ensure_database(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self.init_database()
        
    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('PRAGMA journal_mode=WAL')
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None
        
    def init_database(self):
        conn = self.get_connection()
        if conn is None:
            return False
            
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_save (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    player_name TEXT DEFAULT 'Hero',
                    hp INTEGER DEFAULT 100,
                    max_hp INTEGER DEFAULT 100,
                    attack INTEGER DEFAULT 10,
                    gold INTEGER DEFAULT 0,
                    current_level INTEGER DEFAULT 1,
                    total_kills INTEGER DEFAULT 0,
                    save_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE,
                    setting_value TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_kills INTEGER,
                    max_level INTEGER,
                    play_time INTEGER,
                    save_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('SELECT COUNT(*) FROM player_save')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO player_save (id, player_name, hp, max_hp, attack, gold, current_level, total_kills)
                    VALUES (1, 'Hero', 100, 100, 10, 0, 1, 0)
                ''')
                
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
        
    def save_player(self, player, current_level, total_kills):
        conn = self.get_connection()
        if conn is None:
            return False
            
        try:
            cursor = conn.cursor()
            
            hp = max(0, min(player.hp, player.max_hp))
            max_hp = max(1, player.max_hp)
            attack = max(1, player.attack)
            gold = max(0, player.gold)
            current_level = max(1, current_level)
            total_kills = max(0, total_kills)
            
            cursor.execute('''
                INSERT OR REPLACE INTO player_save 
                (id, player_name, hp, max_hp, attack, gold, current_level, total_kills, save_time)
                VALUES (1, 'Hero', ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (hp, max_hp, attack, gold, current_level, total_kills))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Save error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
        
    def load_player(self):
        conn = self.get_connection()
        if conn is None:
            return None
            
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT hp, max_hp, attack, gold, current_level, total_kills
                FROM player_save WHERE id = 1
            ''')
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'hp': result[0],
                    'max_hp': result[1],
                    'attack': result[2],
                    'gold': result[3],
                    'current_level': result[4],
                    'total_kills': result[5]
                }
            return None
            
        except sqlite3.Error as e:
            print(f"Load error: {e}")
            return None
        finally:
            conn.close()
        
    def reset_save(self):
        conn = self.get_connection()
        if conn is None:
            return False
            
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO player_save 
                (id, player_name, hp, max_hp, attack, gold, current_level, total_kills, save_time)
                VALUES (1, 'Hero', 100, 100, 10, 0, 1, 0, CURRENT_TIMESTAMP)
            ''')
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Reset error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
        
    def get_high_score(self):
        conn = self.get_connection()
        if conn is None:
            return 0
            
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT MAX(total_kills) FROM player_save')
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except sqlite3.Error:
            return 0
        finally:
            conn.close()
            
    def save_game_history(self, total_kills, max_level, play_time):
        conn = self.get_connection()
        if conn is None:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO game_history (total_kills, max_level, play_time)
                VALUES (?, ?, ?)
            ''', (total_kills, max_level, play_time))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"History save error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
