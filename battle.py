import pygame
import random
import config

class BattleSystem:
    def __init__(self):
        self.in_battle = False
        self.player = None
        self.monster = None
        self.battle_log = []
        self.max_log_lines = 5
        self.battle_cooldown = 0
        self.cooldown_time = 20
        self.turn_count = 0
        self.last_action = ""
        self.combat_ended = False
        
    def start_battle(self, player, monster):
        self.in_battle = True
        self.player = player
        self.monster = monster
        self.battle_log = []
        self.battle_cooldown = 0
        self.turn_count = 0
        self.combat_ended = False
        self.add_log(f"Battle started! Monster Lv.{monster.level}")
        
    def player_attack(self):
        if not self.in_battle or self.battle_cooldown > 0 or self.combat_ended:
            return False
            
        base_damage = self.player.attack
        variance = random.randint(-2, 3)
        
        if random.random() < 0.1:
            damage = base_damage * 2 + variance
            self.add_log(f"CRITICAL HIT! {damage} damage!")
        else:
            damage = max(1, base_damage + variance)
            self.add_log(f"You dealt {damage} damage!")
        
        self.monster.take_damage(damage)
        self.battle_cooldown = self.cooldown_time
        self.turn_count += 1
        
        if not self.monster.alive:
            self.add_log("Monster defeated!")
            self.combat_ended = True
            self.end_battle()
            return True
            
        return False
        
    def monster_attack(self):
        if not self.in_battle or not self.monster.alive or self.combat_ended:
            return False
            
        base_damage = self.monster.attack
        variance = random.randint(-1, 2)
        
        if random.random() < 0.05:
            damage = base_damage * 2
            self.add_log(f"Monster CRITICAL! {damage} damage!")
        else:
            damage = max(1, base_damage + variance)
            self.add_log(f"Monster dealt {damage} damage!")
        
        self.player.take_damage(damage)
        
        if not self.player.is_alive():
            self.add_log("You died!")
            self.combat_ended = True
            self.end_battle()
            return True
            
        return False
        
    def end_battle(self):
        self.in_battle = False
        
    def update(self):
        if self.battle_cooldown > 0:
            self.battle_cooldown -= 1
            
    def add_log(self, message):
        self.battle_log.append(message)
        if len(self.battle_log) > self.max_log_lines:
            self.battle_log.pop(0)
            
    def can_attack(self):
        return self.in_battle and self.battle_cooldown <= 0 and not self.combat_ended
        
    def get_battle_result(self):
        if self.monster and not self.monster.alive:
            return "win"
        if self.player and not self.player.is_alive():
            return "lose"
        return None
        
    def get_cooldown_percent(self):
        if self.cooldown_time <= 0:
            return 1.0
        return 1.0 - (self.battle_cooldown / self.cooldown_time)
