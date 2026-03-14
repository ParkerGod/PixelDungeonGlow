# main.py - 游戏主入口
# 负责初始化、主循环、模块调度

import pygame
import sys
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE,
    STATE_PLAYING, STATE_BATTLE, STATE_PAUSED, STATE_GAME_OVER,
    TILE_SIZE
)
from player import Player
from map_generator import DungeonMap
from battle import BattleSystem
from ui import UIManager
from data_manager import DataManager


class Game:
    """游戏主类"""
    
    def __init__(self):
        """初始化游戏"""
        pygame.init()
        
        # 创建窗口
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        
        # 创建时钟
        self.clock = pygame.time.Clock()
        
        # 初始化字体
        self.font = pygame.font.SysFont("simhei", 24)
        
        # 初始化数据管理器
        self.data_manager = DataManager()
        
        # 初始化游戏状态
        self.game_state = "menu"  # menu, playing, battle, paused, game_over
        self.running = True

        # 菜单选择索引
        self.menu_selected = 0  # 0: 新游戏, 1: 继续游戏, 2: 退出
        self.menu_options = ["new_game", "continue", "quit"]

        # 游戏对象
        self.player = None
        self.dungeon_map = None
        self.ui_manager = None
        self.battle_system = None

        # 初始化游戏
        self._init_game()
    
    def _init_game(self):
        """初始化游戏对象"""
        # 创建玩家
        self.player = Player(data_manager=self.data_manager)
        
        # 创建地牢地图
        self.dungeon_map = DungeonMap(dungeon_level=1)
        
        # 设置玩家起始位置
        start_pos = self.dungeon_map.get_player_start()
        self.player.grid_x = start_pos[0]
        self.player.grid_y = start_pos[1]
        self.player.pixel_x = start_pos[0] * TILE_SIZE
        self.player.pixel_y = start_pos[1] * TILE_SIZE
        self.player.target_x = self.player.pixel_x
        self.player.target_y = self.player.pixel_y
        
        # 创建UI管理器
        self.ui_manager = UIManager(self.screen)
        
        # 设置玩家属性监听器
        self.player.add_hp_listener(self._on_hp_changed)
        self.player.add_gold_listener(self._on_gold_changed)
        
        # 初始化UI数据
        self.ui_manager.update_player_data(self.player.hp, self.player.max_hp)
        self.ui_manager.update_gold(self.player.gold)
        self.ui_manager.update_dungeon_level(self.player.dungeon_level)
    
    def _on_hp_changed(self, hp, max_hp):
        """血量变化回调"""
        self.ui_manager.update_player_data(hp, max_hp)
    
    def _on_gold_changed(self, gold):
        """金币变化回调"""
        self.ui_manager.update_gold(gold)
    
    def load_game(self):
        """加载游戏存档"""
        player_data = self.data_manager.load_player_data(self.player.player_id)
        if player_data:
            self.player.load_from_save(player_data)
            
            # 重新生成地图
            self.dungeon_map = DungeonMap(dungeon_level=self.player.dungeon_level)
            
            self.ui_manager.show_notification("游戏进度已加载！", (0, 255, 0))
            return True
        else:
            self.ui_manager.show_notification("没有找到存档！", (255, 0, 0))
            return False
    
    def save_game(self):
        """保存游戏"""
        # 更新玩家位置
        self.player.save_to_database()
        
        # 保存游戏进度
        progress_data = {
            'current_state': self.game_state,
            'unlocked_levels': [self.player.dungeon_level],
            'play_time': 0,
            'monsters_killed': 0,
            'coins_collected': self.player.gold
        }
        self.data_manager.save_game_progress(self.player.player_id, progress_data)
        
        self.ui_manager.show_notification("游戏已保存！", (0, 255, 255))
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == STATE_PLAYING:
                        self.game_state = STATE_PAUSED
                    elif self.game_state == STATE_PAUSED:
                        self.game_state = STATE_PLAYING
                    elif self.game_state == "menu":
                        self.running = False
                
                # 存档快捷键
                if event.key == pygame.K_s:
                    if self.game_state == STATE_PLAYING:
                        self.save_game()
                
                # 升级快捷键
                if event.key == pygame.K_u:
                    if self.game_state == STATE_PLAYING:
                        if self.player.upgrade_attack():
                            self.ui_manager.show_notification("攻击力升级成功！", (255, 255, 0))
                        else:
                            self.ui_manager.show_notification("金币不足！需要50金币", (255, 0, 0))
                
                # 重新开始
                if event.key == pygame.K_r:
                    if self.game_state == STATE_GAME_OVER:
                        self.restart_game()
                
                # 菜单选择
                if self.game_state == "menu":
                    if event.key == pygame.K_UP:
                        self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        self._execute_menu_selection()
                    # 数字键快捷选择
                    elif event.key == pygame.K_1 or event.key == pygame.K_KP1:
                        self.start_new_game()
                    elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                        if self.data_manager.player_exists(self.player.player_id):
                            self.load_game()
                            self.game_state = STATE_PLAYING
                        else:
                            print("没有存档！")
                    elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                        self.running = False
            
            # 鼠标点击
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    # 菜单状态处理
                    if self.game_state == "menu":
                        self._handle_menu_click(event.pos)
                    else:
                        # 游戏状态处理
                        button = self.ui_manager.handle_click(event.pos)
                        if button == 'save':
                            if self.game_state == STATE_PLAYING:
                                self.save_game()
                        elif button == 'upgrade':
                            if self.game_state == STATE_PLAYING:
                                if self.player.upgrade_attack():
                                    self.ui_manager.show_notification("攻击力升级成功！", (255, 255, 0))
                                else:
                                    self.ui_manager.show_notification("金币不足！需要50金币", (255, 0, 0))
            
            # 战斗状态输入处理
            if self.game_state == STATE_BATTLE and self.battle_system:
                result = self.battle_system.handle_input(event)
                if result == 'flee':
                    self.end_battle(fled=True)
                elif result == 'attack':
                    pass  # 攻击逻辑在battle_system中处理
            
            # 游戏结束状态
            if self.game_state == STATE_GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
    
    def handle_input(self):
        """处理游戏输入"""
        if self.game_state != STATE_PLAYING:
            return
        
        keys = pygame.key.get_pressed()
        
        # 移动控制
        if not self.player.is_moving and not self.player.in_battle:
            moved = False
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                moved = self.player.move(0, -1, self.dungeon_map)
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                moved = self.player.move(0, 1, self.dungeon_map)
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                moved = self.player.move(-1, 0, self.dungeon_map)
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                moved = self.player.move(1, 0, self.dungeon_map)
            
            if moved:
                self._on_player_moved()
    
    def _on_player_moved(self):
        """玩家移动后的处理"""
        # 检查金币收集
        coin_amount = self.dungeon_map.collect_coin(self.player.grid_x, self.player.grid_y)
        if coin_amount > 0:
            self.player.add_gold(coin_amount)
            self.ui_manager.show_notification(f"获得 {coin_amount} 金币！", (255, 215, 0))

        # 检查药水收集
        potion = self.dungeon_map.collect_potion(self.player.grid_x, self.player.grid_y)
        if potion:
            self._apply_potion_effect(potion)

        # 检查遭遇怪物
        monster = self.dungeon_map.get_monster_at(self.player.grid_x, self.player.grid_y)
        if monster:
            self.start_battle(monster)

    def _apply_potion_effect(self, potion):
        """应用药水效果"""
        from map_generator import Potion

        if potion.potion_type == Potion.TYPE_HEAL:
            self.player.heal(potion.value)
            self.ui_manager.show_notification(f"使用{potion.get_name()}！", (0, 255, 100))
        elif potion.potion_type == Potion.TYPE_POWER:
            self.player.attack += potion.value
            self.ui_manager.show_notification(f"使用{potion.get_name()}！", (255, 100, 255))
    
    def start_battle(self, monster):
        """开始战斗"""
        self.player.in_battle = True
        self.battle_system = BattleSystem(self.screen, self.player, monster)
        self.game_state = STATE_BATTLE
    
    def end_battle(self, fled=False):
        """结束战斗"""
        if self.battle_system:
            if self.battle_system.is_victory():
                # 获得奖励
                rewards = self.battle_system.get_rewards()
                self.player.add_gold(rewards['gold'])

                # 获得经验值
                leveled_up = self.player.add_exp(rewards['exp'])

                # 增加击杀数
                self.player.monsters_killed += 1

                # 显示奖励信息
                self.ui_manager.show_notification(
                    f"战斗胜利！获得 {rewards['gold']} 金币和 {rewards['exp']} 经验！", (0, 255, 0)
                )

                # 如果升级了，显示升级信息
                if leveled_up:
                    self.ui_manager.show_notification(
                        f"升级了！等级: {self.player.level} 攻击力+3 最大生命+20", (255, 215, 0)
                    )

                # 移除死亡的怪物
                self.dungeon_map.remove_dead_monsters()

            elif self.battle_system.is_defeat():
                self.game_state = STATE_GAME_OVER
                self.player.in_battle = False
                self.battle_system = None
                return

            elif fled:
                self.ui_manager.show_notification("成功逃跑！", (255, 255, 0))

        self.player.in_battle = False
        self.battle_system = None
        self.game_state = STATE_PLAYING
    
    def start_new_game(self):
        """开始新游戏"""
        # 重置玩家
        self.player.reset()
        
        # 重新生成地图
        self.dungeon_map = DungeonMap(dungeon_level=1)
        
        # 设置玩家起始位置
        start_pos = self.dungeon_map.get_player_start()
        self.player.grid_x = start_pos[0]
        self.player.grid_y = start_pos[1]
        self.player.pixel_x = start_pos[0] * TILE_SIZE
        self.player.pixel_y = start_pos[1] * TILE_SIZE
        self.player.target_x = self.player.pixel_x
        self.player.target_y = self.player.pixel_y
        
        # 更新UI
        self.ui_manager.update_dungeon_level(1)
        
        self.game_state = STATE_PLAYING
    
    def restart_game(self):
        """重新开始游戏"""
        self.start_new_game()

    def _handle_menu_click(self, pos):
        """
        处理菜单点击
        :param pos: 鼠标位置
        """
        x, y = pos
        # 检查点击的菜单项 (根据UI绘制位置调整)
        # 新游戏按钮区域 (大致在 y=270-310)
        if 270 <= y <= 310:
            self.start_new_game()
        # 继续游戏按钮区域 (大致在 y=330-370)
        elif 330 <= y <= 370:
            if self.data_manager.player_exists(self.player.player_id):
                self.load_game()
                self.game_state = STATE_PLAYING
            else:
                print("没有存档！")
        # 退出按钮区域 (大致在 y=390-430)
        elif 390 <= y <= 430:
            self.running = False

    def _execute_menu_selection(self):
        """执行当前选中的菜单项"""
        option = self.menu_options[self.menu_selected]
        if option == "new_game":
            self.start_new_game()
        elif option == "continue":
            if self.data_manager.player_exists(self.player.player_id):
                self.load_game()
                self.game_state = STATE_PLAYING
            else:
                print("没有存档！")
        elif option == "quit":
            self.running = False
    
    def update(self):
        """更新游戏状态"""
        if self.game_state == STATE_PLAYING:
            # 更新玩家
            self.player.update()
            
            # 检查是否所有怪物都被击败
            if len(self.dungeon_map.monsters) == 0:
                # 进入下一层
                self.player.dungeon_level += 1
                self.dungeon_map.regenerate(self.player.dungeon_level)
                
                # 设置新位置
                start_pos = self.dungeon_map.get_player_start()
                self.player.grid_x = start_pos[0]
                self.player.grid_y = start_pos[1]
                self.player.pixel_x = start_pos[0] * TILE_SIZE
                self.player.pixel_y = start_pos[1] * TILE_SIZE
                self.player.target_x = self.player.pixel_x
                self.player.target_y = self.player.pixel_y
                
                self.ui_manager.update_dungeon_level(self.player.dungeon_level)
                self.ui_manager.show_notification(
                    f"进入地牢第 {self.player.dungeon_level} 层！", (0, 255, 255)
                )
        
        elif self.game_state == STATE_BATTLE and self.battle_system:
            self.battle_system.update()
            
            # 检查战斗是否结束
            if self.battle_system.is_finished():
                self.end_battle()
    
    def draw(self):
        """绘制游戏画面"""
        # 清空屏幕
        self.screen.fill((20, 20, 20))
        
        if self.game_state == "menu":
            self.ui_manager.draw_main_menu(self.menu_selected)
        
        elif self.game_state == STATE_PLAYING:
            # 绘制地图
            self.dungeon_map.draw(self.screen)
            
            # 绘制玩家
            self.player.draw(self.screen)
            
            # 绘制UI
            self.ui_manager.draw(
                self.player.attack,
                self.player.level,
                self.player.exp,
                self.player.exp_to_next_level
            )

        elif self.game_state == STATE_BATTLE and self.battle_system:
            # 绘制游戏世界 (作为背景)
            self.dungeon_map.draw(self.screen)
            self.player.draw(self.screen)
            self.ui_manager.draw(
                self.player.attack,
                self.player.level,
                self.player.exp,
                self.player.exp_to_next_level
            )
            
            # 绘制战斗界面
            self.battle_system.draw(self.font)
        
        elif self.game_state == STATE_PAUSED:
            # 绘制游戏世界
            self.dungeon_map.draw(self.screen)
            self.player.draw(self.screen)
            self.ui_manager.draw(
                self.player.attack,
                self.player.level,
                self.player.exp,
                self.player.exp_to_next_level
            )
            
            # 绘制暂停菜单
            self.ui_manager.draw_pause_menu()
        
        elif self.game_state == STATE_GAME_OVER:
            # 绘制游戏世界
            self.dungeon_map.draw(self.screen)
            self.player.draw(self.screen)
            
            # 绘制游戏结束界面
            victory = self.player.hp > 0
            self.ui_manager.draw_game_over(victory=victory)
        
        # 更新显示
        pygame.display.flip()
    
    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        # 清理
        self.data_manager.close()
        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
