# ui.py - UI模块
# 渲染血量、金币、关卡信息等界面元素

import pygame
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE,
    COLOR_WHITE, COLOR_BLACK, COLOR_RED, COLOR_GREEN,
    COLOR_YELLOW, COLOR_GRAY, COLOR_BLUE,
    FONT_SIZE_SMALL, FONT_SIZE_NORMAL, FONT_SIZE_LARGE
)


class UIManager:
    """UI管理器类"""
    
    def __init__(self, screen):
        """
        初始化UI管理器
        :param screen: Pygame屏幕对象
        """
        self.screen = screen
        
        # 初始化字体
        self.font_small = pygame.font.SysFont("simhei", FONT_SIZE_SMALL)
        self.font_normal = pygame.font.SysFont("simhei", FONT_SIZE_NORMAL)
        self.font_large = pygame.font.SysFont("simhei", FONT_SIZE_LARGE)
        
        # UI元素位置
        self.ui_y = 10
        self.padding = 10
        
        # 按钮定义
        self.buttons = {}
        self._init_buttons()
        
        # 消息系统
        self.messages = []  # [(text, color, timer), ...]
        
        # 玩家数据引用
        self.player_hp = 100
        self.player_max_hp = 100
        self.player_gold = 0
        self.dungeon_level = 1
    
    def _init_buttons(self):
        """初始化按钮"""
        # 存档按钮
        self.buttons['save'] = {
            'rect': pygame.Rect(WINDOW_WIDTH - 200, 10, 80, 30),
            'text': '存档',
            'color': COLOR_BLUE,
            'hover': False
        }
        
        # 升级按钮
        self.buttons['upgrade'] = {
            'rect': pygame.Rect(WINDOW_WIDTH - 110, 10, 100, 30),
            'text': '升级攻击',
            'color': COLOR_YELLOW,
            'hover': False
        }
    
    def update_player_data(self, hp, max_hp):
        """
        更新玩家血量数据
        :param hp: 当前血量
        :param max_hp: 最大血量
        """
        self.player_hp = hp
        self.player_max_hp = max_hp
    
    def update_gold(self, gold):
        """
        更新金币数据
        :param gold: 金币数量
        """
        self.player_gold = gold
    
    def update_dungeon_level(self, level):
        """
        更新地牢层数
        :param level: 层数
        """
        self.dungeon_level = level
    
    def add_message(self, text, color=COLOR_WHITE, duration=120):
        """
        添加消息提示
        :param text: 消息文本
        :param color: 颜色
        :param duration: 持续时间(帧)
        """
        self.messages.append([text, color, duration])
    
    def draw(self, player_attack=10, player_level=1, exp=0, exp_to_next=100):
        """
        绘制UI
        :param player_attack: 玩家攻击力
        :param player_level: 玩家等级
        :param exp: 当前经验值
        :param exp_to_next: 升级所需经验值
        """
        # 绘制顶部信息栏背景
        info_bar = pygame.Rect(0, 0, WINDOW_WIDTH, 55)
        pygame.draw.rect(self.screen, (30, 30, 30), info_bar)
        pygame.draw.line(self.screen, COLOR_GRAY, (0, 55), (WINDOW_WIDTH, 55), 2)

        # 绘制血量和等级
        self._draw_health_bar(10, 8, 120, 18, self.player_hp, self.player_max_hp)
        hp_text = self.font_small.render(f"HP: {self.player_hp}/{self.player_max_hp}", True, COLOR_WHITE)
        self.screen.blit(hp_text, (35, 10))

        # 绘制经验条
        self._draw_exp_bar(10, 32, 120, 14, exp, exp_to_next)
        exp_text = self.font_small.render(f"Lv.{player_level} EXP", True, COLOR_WHITE)
        self.screen.blit(exp_text, (35, 32))

        # 绘制金币
        gold_text = self.font_normal.render(f"金币: {self.player_gold}", True, COLOR_YELLOW)
        self.screen.blit(gold_text, (150, 12))

        # 绘制攻击力
        attack_text = self.font_normal.render(f"攻击: {player_attack}", True, COLOR_RED)
        self.screen.blit(attack_text, (300, 12))

        # 绘制地牢层数
        level_text = self.font_normal.render(f"地牢: {self.dungeon_level}层", True, COLOR_GREEN)
        self.screen.blit(level_text, (430, 12))

        # 绘制按钮
        self._draw_buttons()

        # 绘制消息
        self._draw_messages()

        # 绘制操作提示
        self._draw_controls_hint()

    def _draw_exp_bar(self, x, y, width, height, current, maximum):
        """
        绘制经验条
        :param x: x坐标
        :param y: y坐标
        :param width: 宽度
        :param height: 高度
        :param current: 当前值
        :param maximum: 最大值
        """
        # 背景
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, COLOR_GRAY, bg_rect)

        # 经验值
        if maximum > 0:
            exp_width = int(width * (current / maximum))
            exp_rect = pygame.Rect(x, y, exp_width, height)
            pygame.draw.rect(self.screen, (100, 200, 255), exp_rect)  # 蓝色经验条

        # 边框
        pygame.draw.rect(self.screen, COLOR_WHITE, bg_rect, 1)
    
    def _draw_health_bar(self, x, y, width, height, current, maximum):
        """
        绘制血条
        :param x: x坐标
        :param y: y坐标
        :param width: 宽度
        :param height: 高度
        :param current: 当前值
        :param maximum: 最大值
        """
        # 背景
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, COLOR_GRAY, bg_rect)
        
        # 血量
        if maximum > 0:
            health_width = int(width * (current / maximum))
            # 根据血量比例选择颜色
            if current / maximum > 0.5:
                color = COLOR_GREEN
            elif current / maximum > 0.25:
                color = COLOR_YELLOW
            else:
                color = COLOR_RED
            
            health_rect = pygame.Rect(x, y, health_width, height)
            pygame.draw.rect(self.screen, color, health_rect)
        
        # 边框
        pygame.draw.rect(self.screen, COLOR_WHITE, bg_rect, 1)
    
    def _draw_buttons(self):
        """绘制按钮"""
        mouse_pos = pygame.mouse.get_pos()
        
        for key, button in self.buttons.items():
            # 检查鼠标悬停
            button['hover'] = button['rect'].collidepoint(mouse_pos)
            
            # 选择颜色
            if button['hover']:
                color = (min(button['color'][0] + 50, 255),
                        min(button['color'][1] + 50, 255),
                        min(button['color'][2] + 50, 255))
            else:
                color = button['color']
            
            # 绘制按钮背景
            pygame.draw.rect(self.screen, color, button['rect'])
            pygame.draw.rect(self.screen, COLOR_WHITE, button['rect'], 2)
            
            # 绘制按钮文字
            text = self.font_small.render(button['text'], True, COLOR_BLACK)
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)
    
    def _draw_messages(self):
        """绘制消息提示"""
        y_offset = WINDOW_HEIGHT - 100
        
        # 更新并绘制消息
        for msg in self.messages[:]:
            text = self.font_normal.render(msg[0], True, msg[1])
            text.set_alpha(min(255, msg[2] * 2))  # 淡出效果
            self.screen.blit(text, (10, y_offset))
            y_offset -= 30
            msg[2] -= 1
        
        # 移除过期消息
        self.messages = [msg for msg in self.messages if msg[2] > 0]
    
    def _draw_controls_hint(self):
        """绘制操作提示"""
        hint_text = "方向键移动 | 空格攻击 | ESC暂停 | S存档 | U升级(50金币)"
        text = self.font_small.render(hint_text, True, COLOR_GRAY)
        self.screen.blit(text, (10, WINDOW_HEIGHT - 30))
    
    def handle_click(self, pos):
        """
        处理鼠标点击
        :param pos: 鼠标位置 (x, y)
        :return: str 点击的按钮名称，如果没有返回None
        """
        for key, button in self.buttons.items():
            if button['rect'].collidepoint(pos):
                return key
        return None
    
    def draw_game_over(self, victory=True, gold_earned=0):
        """
        绘制游戏结束界面
        :param victory: 是否胜利
        :param gold_earned: 获得的金币
        """
        # 半透明背景
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(COLOR_BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        # 标题
        if victory:
            title = self.font_large.render("胜利！", True, COLOR_GREEN)
        else:
            title = self.font_large.render("游戏结束", True, COLOR_RED)
        
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(title, title_rect)
        
        # 统计信息
        if victory:
            stats_text = f"获得金币: {gold_earned}"
            stats = self.font_normal.render(stats_text, True, COLOR_YELLOW)
            stats_rect = stats.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
            self.screen.blit(stats, stats_rect)
        
        # 提示
        hint = self.font_normal.render("按 R 重新开始 | 按 ESC 退出", True, COLOR_WHITE)
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))
        self.screen.blit(hint, hint_rect)
    
    def draw_pause_menu(self):
        """绘制暂停菜单"""
        # 半透明背景
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(COLOR_BLACK)
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        
        # 标题
        title = self.font_large.render("游戏暂停", True, COLOR_WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80))
        self.screen.blit(title, title_rect)
        
        # 选项
        options = [
            ("继续游戏", COLOR_GREEN, "resume"),
            ("保存进度", COLOR_BLUE, "save"),
            ("返回主菜单", COLOR_YELLOW, "menu"),
            ("退出游戏", COLOR_RED, "quit")
        ]
        
        y_offset = WINDOW_HEIGHT // 2 - 20
        for text, color, action in options:
            option_text = self.font_normal.render(text, True, color)
            option_rect = option_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(option_text, option_rect)
            y_offset += 50
    
    def draw_main_menu(self, selected_index=0):
        """
        绘制主菜单
        :param selected_index: 当前选中的菜单项索引
        """
        # 背景
        self.screen.fill(COLOR_BLACK)

        # 标题
        title = self.font_large.render("Pixel Dungeon Glow", True, COLOR_GREEN)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # 副标题
        subtitle = self.font_normal.render("像素地牢冒险", True, COLOR_GRAY)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(subtitle, subtitle_rect)

        # 选项
        options = [
            ("新游戏", COLOR_GREEN, "new_game"),
            ("继续游戏", COLOR_BLUE, "continue"),
            ("退出", COLOR_RED, "quit")
        ]

        y_offset = 290
        for i, (text, color, action) in enumerate(options):
            # 如果是选中项，使用高亮颜色并添加背景
            if i == selected_index:
                # 绘制选中背景
                bg_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, y_offset - 20, 240, 50)
                pygame.draw.rect(self.screen, (50, 50, 50), bg_rect)
                pygame.draw.rect(self.screen, COLOR_WHITE, bg_rect, 2)
                # 使用白色高亮文字
                option_text = self.font_normal.render(text, True, COLOR_WHITE)
            else:
                option_text = self.font_normal.render(text, True, color)

            option_rect = option_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(option_text, option_rect)
            y_offset += 60

        # 操作提示
        hint = self.font_small.render("↑↓方向键选择 | 回车键确认 | 数字键1/2/3快捷选择", True, COLOR_GRAY)
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(hint, hint_rect)
    
    def show_notification(self, text, color=COLOR_WHITE):
        """
        显示通知
        :param text: 通知文本
        :param color: 颜色
        """
        self.add_message(text, color, duration=180)
