# battle.py - 战斗模块
# 处理玩家与怪物的简易战斗逻辑

import random
import pygame
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BLACK, COLOR_WHITE,
    COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_GRAY,
    MONSTER_GOLD_REWARD
)


class BattleSystem:
    """战斗系统类"""
    
    def __init__(self, screen, player, monster):
        """
        初始化战斗系统
        :param screen: Pygame屏幕对象
        :param player: 玩家对象
        :param monster: 怪物对象
        """
        self.screen = screen
        self.player = player
        self.monster = monster
        
        # 战斗状态
        self.active = True
        self.player_turn = True
        self.battle_log = []
        self.add_log("战斗开始！")
        
        # 战斗UI位置
        self.battle_box_x = 50
        self.battle_box_y = 100
        self.battle_box_width = WINDOW_WIDTH - 100
        self.battle_box_height = WINDOW_HEIGHT - 200
        
        # 攻击冷却
        self.attack_cooldown = 0
        self.attack_delay = 30  # 帧数
        
        # 战斗结果
        self.victory = False
        self.defeat = False
        
        # 动画效果
        self.player_shake = 0
        self.monster_shake = 0
        self.damage_texts = []  # [(x, y, text, color, timer), ...]
    
    def add_log(self, message):
        """添加战斗日志"""
        self.battle_log.append(message)
        if len(self.battle_log) > 5:
            self.battle_log.pop(0)
    
    def player_attack(self):
        """玩家攻击"""
        if not self.player_turn or self.attack_cooldown > 0:
            return False
        
        # 计算伤害 (有随机波动)
        base_damage = self.player.get_attack_damage()
        damage = random.randint(int(base_damage * 0.8), int(base_damage * 1.2))
        
        # 应用伤害
        monster_alive = self.monster.take_damage(damage)
        
        # 添加伤害文字动画
        self.add_damage_text(
            self.battle_box_x + self.battle_box_width - 150,
            self.battle_box_y + 150,
            f"-{damage}",
            COLOR_RED
        )
        
        # 震动效果
        self.monster_shake = 10
        
        self.add_log(f"你造成了 {damage} 点伤害！")
        
        if not monster_alive:
            self.add_log("怪物被击败了！")
            self.victory = True
            self.active = False
        else:
            self.player_turn = False
            self.attack_cooldown = self.attack_delay
        
        return True
    
    def monster_attack(self):
        """怪物攻击"""
        if self.player_turn or self.attack_cooldown > 0:
            return False
        
        # 计算伤害
        damage = random.randint(
            int(self.monster.attack * 0.8),
            int(self.monster.attack * 1.2)
        )
        
        # 应用伤害
        player_alive = self.player.take_damage(damage)
        
        # 添加伤害文字动画
        self.add_damage_text(
            self.battle_box_x + 150,
            self.battle_box_y + 150,
            f"-{damage}",
            COLOR_RED
        )
        
        # 震动效果
        self.player_shake = 10
        
        self.add_log(f"怪物造成了 {damage} 点伤害！")
        
        if not player_alive:
            self.add_log("你被击败了...")
            self.defeat = True
            self.active = False
        else:
            self.player_turn = True
            self.attack_cooldown = self.attack_delay
        
        return True
    
    def add_damage_text(self, x, y, text, color):
        """添加伤害文字动画"""
        self.damage_texts.append([x, y, text, color, 30])
    
    def update(self):
        """更新战斗状态 (每帧调用)"""
        if not self.active:
            return
        
        # 更新攻击冷却
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
            # 怪物自动攻击
            if self.attack_cooldown == 0 and not self.player_turn:
                self.monster_attack()
        
        # 更新震动效果
        if self.player_shake > 0:
            self.player_shake -= 1
        if self.monster_shake > 0:
            self.monster_shake -= 1
        
        # 更新伤害文字
        for dt in self.damage_texts:
            dt[1] -= 1  # 向上飘动
            dt[4] -= 1  # 减少计时器
        self.damage_texts = [dt for dt in self.damage_texts if dt[4] > 0]
    
    def handle_input(self, event):
        """
        处理输入事件
        :param event: Pygame事件
        :return: str 操作结果 ('attack', 'flee', None)
        """
        if not self.active or not self.player_turn:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.player_attack():
                    return 'attack'
            elif event.key == pygame.K_ESCAPE:
                # 逃跑 (50%成功率)
                if random.random() < 0.5:
                    self.add_log("成功逃跑！")
                    self.active = False
                    return 'flee'
                else:
                    self.add_log("逃跑失败！")
                    self.player_turn = False
                    self.attack_cooldown = self.attack_delay
                    return 'flee_failed'
        
        return None
    
    def draw(self, font):
        """
        绘制战斗界面
        :param font: Pygame字体对象
        """
        # 绘制半透明背景
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(COLOR_BLACK)
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        
        # 绘制战斗框
        battle_rect = pygame.Rect(
            self.battle_box_x,
            self.battle_box_y,
            self.battle_box_width,
            self.battle_box_height
        )
        pygame.draw.rect(self.screen, (50, 50, 50), battle_rect)
        pygame.draw.rect(self.screen, COLOR_WHITE, battle_rect, 3)
        
        # 绘制标题
        title_text = font.render("战斗中！", True, COLOR_YELLOW)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, self.battle_box_y + 30))
        self.screen.blit(title_text, title_rect)
        
        # 计算震动偏移
        player_offset_x = random.randint(-self.player_shake, self.player_shake)
        player_offset_y = random.randint(-self.player_shake, self.player_shake)
        monster_offset_x = random.randint(-self.monster_shake, self.monster_shake)
        monster_offset_y = random.randint(-self.monster_shake, self.monster_shake)
        
        # 绘制玩家
        player_x = self.battle_box_x + 100 + player_offset_x
        player_y = self.battle_box_y + 150 + player_offset_y
        player_rect = pygame.Rect(player_x, player_y, 80, 80)
        pygame.draw.rect(self.screen, COLOR_GREEN, player_rect)
        # 玩家眼睛
        pygame.draw.rect(self.screen, COLOR_BLACK, (player_x + 20, player_y + 25, 10, 10))
        pygame.draw.rect(self.screen, COLOR_BLACK, (player_x + 50, player_y + 25, 10, 10))
        
        # 绘制玩家血条
        self._draw_health_bar(
            player_x, player_y - 30, 80, 10,
            self.player.hp, self.player.max_hp, COLOR_GREEN
        )
        
        # 绘制玩家信息
        player_info = font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, COLOR_WHITE)
        self.screen.blit(player_info, (player_x, player_y + 90))
        
        # 绘制怪物
        monster_x = self.battle_box_x + self.battle_box_width - 180 + monster_offset_x
        monster_y = self.battle_box_y + 150 + monster_offset_y
        monster_rect = pygame.Rect(monster_x, monster_y, 80, 80)
        pygame.draw.rect(self.screen, COLOR_RED, monster_rect)
        # 怪物眼睛
        pygame.draw.rect(self.screen, COLOR_YELLOW, (monster_x + 20, monster_y + 25, 10, 10))
        pygame.draw.rect(self.screen, COLOR_YELLOW, (monster_x + 50, monster_y + 25, 10, 10))
        # 怪物嘴巴
        pygame.draw.rect(self.screen, COLOR_BLACK, (monster_x + 25, monster_y + 50, 30, 10))
        
        # 绘制怪物血条
        self._draw_health_bar(
            monster_x, monster_y - 30, 80, 10,
            self.monster.hp, self.monster.max_hp, COLOR_RED
        )
        
        # 绘制怪物信息
        monster_info = font.render(f"HP: {self.monster.hp}/{self.monster.max_hp}", True, COLOR_WHITE)
        self.screen.blit(monster_info, (monster_x, monster_y + 90))
        
        # 绘制VS
        vs_text = font.render("VS", True, COLOR_YELLOW)
        vs_rect = vs_text.get_rect(center=(WINDOW_WIDTH // 2, self.battle_box_y + 190))
        self.screen.blit(vs_text, vs_rect)
        
        # 绘制战斗日志
        log_y = self.battle_box_y + 280
        for log in self.battle_log:
            log_text = font.render(log, True, COLOR_WHITE)
            self.screen.blit(log_text, (self.battle_box_x + 20, log_y))
            log_y += 25
        
        # 绘制操作提示
        if self.active and self.player_turn:
            hint_text = font.render("按空格键攻击 | 按ESC逃跑", True, COLOR_YELLOW)
        elif self.active:
            hint_text = font.render("怪物回合...", True, COLOR_GRAY)
        elif self.victory:
            hint_text = font.render("胜利！按任意键继续", True, COLOR_GREEN)
        else:
            hint_text = font.render("失败！按任意键继续", True, COLOR_RED)
        
        hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH // 2, self.battle_box_y + self.battle_box_height - 40))
        self.screen.blit(hint_text, hint_rect)
        
        # 绘制伤害文字
        for dt in self.damage_texts:
            damage_text = font.render(dt[2], True, dt[3])
            self.screen.blit(damage_text, (dt[0], dt[1]))
    
    def _draw_health_bar(self, x, y, width, height, current, maximum, color):
        """绘制血条"""
        # 背景
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, COLOR_GRAY, bg_rect)
        
        # 血量
        if maximum > 0:
            health_width = int(width * (current / maximum))
            health_rect = pygame.Rect(x, y, health_width, height)
            pygame.draw.rect(self.screen, color, health_rect)
        
        # 边框
        pygame.draw.rect(self.screen, COLOR_WHITE, bg_rect, 1)
    
    def get_rewards(self):
        """
        获取战斗奖励
        :return: dict 奖励信息
        """
        if self.victory:
            return {
                'gold': self.monster.gold_reward,
                'exp': self.monster.exp_reward
            }
        return {'gold': 0, 'exp': 0}
    
    def is_finished(self):
        """战斗是否结束"""
        return not self.active
    
    def is_victory(self):
        """是否胜利"""
        return self.victory
    
    def is_defeat(self):
        """是否失败"""
        return self.defeat
