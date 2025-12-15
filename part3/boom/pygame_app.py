# pygame_app.py
"""
Kiwi Dungeon RPG - 經典地下城風格 + 手動操作模式
格子地板、石牆、下樓動畫
"""
from __future__ import annotations

import sys
import math
import random
from typing import List, Tuple, Optional, Dict

import pygame

from dungeon_env import DungeonBattleEnv
from config_dungeon import create_default_players, build_dungeon_floors
from agents import HeuristicDungeonAgent, RandomDungeonAgent, QLearningDungeonAgent
from battle_types import Team, ActionType, BattleAction
from sprites import SpriteRenderer, get_sprite_drawer
from effects import (
    EffectManager, ParticleSystem, 
    SlashEffect, WhirlwindEffect, HealEffect, 
    FireBreathEffect, DarkBoltEffect
)
from skills import HealingSkill, AreaAttackSkill

# === 視窗設定 ===
WIDTH, HEIGHT = 1024, 700
FPS = 60
TURN_INTERVAL = 1.0
TILE_SIZE = 48  # 格子大小

# === 顏色定義 ===
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HP_GREEN = (46, 204, 113)
HP_RED = (231, 76, 60)
MP_BLUE = (52, 152, 219)
GOLD = (255, 215, 0)
MENU_BG = (40, 35, 30)
MENU_HOVER = (70, 60, 50)
MENU_BORDER = (100, 85, 70)

# === 樓層主題 (遺跡森林風格) ===
FLOOR_THEMES = {
    0: {  # B1: 森林遺跡
        'grass_light': (120, 160, 90),
        'grass_dark': (85, 130, 65),
        'stone_light': (130, 125, 115),
        'stone_dark': (90, 85, 80),
        'wall_top': (100, 95, 90),
        'wall_face': (70, 65, 60),
        'tree_trunk': (80, 55, 40),
        'tree_leaves': (45, 80, 45),
        'tree_leaves_light': (70, 110, 60),
        'accent': (100, 180, 120),
    },
    1: {  # B2: 黑暗神殿
        'grass_light': (70, 65, 85),
        'grass_dark': (50, 45, 70),
        'stone_light': (90, 80, 100),
        'stone_dark': (60, 55, 75),
        'wall_top': (80, 70, 95),
        'wall_face': (50, 45, 65),
        'tree_trunk': (60, 45, 55),
        'tree_leaves': (40, 35, 60),
        'tree_leaves_light': (60, 50, 85),
        'accent': (160, 120, 200),
    },
    2: {  # B3: 火焰巢穴
        'grass_light': (100, 70, 60),
        'grass_dark': (75, 50, 45),
        'stone_light': (120, 80, 70),
        'stone_dark': (80, 55, 50),
        'wall_top': (110, 70, 60),
        'wall_face': (70, 45, 40),
        'tree_trunk': (70, 40, 35),
        'tree_leaves': (90, 50, 40),
        'tree_leaves_light': (120, 70, 50),
        'accent': (255, 150, 80),
    }
}


class DungeonTileRenderer:
    """遺跡森林風格地下城渲染器"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tree_positions: List[dict] = []
        self.props: List[dict] = []
        
    def generate_debris(self, floor_idx: int):
        """生成樹木和裝飾物"""
        self.tree_positions.clear()
        self.props.clear()
        
        # 左側樹木
        for i in range(4):
            self.tree_positions.append({
                'x': 30 + random.randint(-10, 10),
                'y': 120 + i * 100 + random.randint(-20, 20),
                'size': random.uniform(0.8, 1.2),
                'type': 'tree'
            })
        
        # 右側樹木
        for i in range(4):
            self.tree_positions.append({
                'x': self.width - 30 + random.randint(-10, 10),
                'y': 120 + i * 100 + random.randint(-20, 20),
                'size': random.uniform(0.8, 1.2),
                'type': 'tree'
            })
        
        # 場景裝飾物（寶箱、水晶等）
        decorations = ['chest', 'crystal', 'pillar', 'barrel']
        for _ in range(3):
            self.props.append({
                'x': random.randint(100, self.width - 100),
                'y': random.randint(120, 380),
                'type': random.choice(decorations)
            })
    
    def draw_tile_floor(self, surface: pygame.Surface, floor_idx: int):
        """繪製草地格子地板"""
        theme = FLOOR_THEMES.get(floor_idx, FLOOR_THEMES[0])
        
        # 深色背景（森林邊緣）
        surface.fill((25, 35, 25))
        
        # 戰場區域
        arena_x, arena_y = 80, 80
        arena_w, arena_h = self.width - 160, self.height - 220
        tile_size = 48
        
        # 繪製格子草地
        for row in range(arena_h // tile_size + 1):
            for col in range(arena_w // tile_size + 1):
                tile_x = arena_x + col * tile_size
                tile_y = arena_y + row * tile_size
                
                if tile_x >= arena_x + arena_w or tile_y >= arena_y + arena_h:
                    continue
                
                # 棋盤格
                if (row + col) % 2 == 0:
                    base_color = theme['grass_light']
                else:
                    base_color = theme['grass_dark']
                
                # 繪製格子
                tile_rect = pygame.Rect(tile_x, tile_y, tile_size, tile_size)
                pygame.draw.rect(surface, base_color, tile_rect)
                
                # 細微的格線
                grid_color = tuple(max(0, c - 20) for c in base_color)
                pygame.draw.rect(surface, grid_color, tile_rect, 1)
                
                # 草地細節
                if random.random() < 0.3:
                    detail_color = tuple(min(255, c + 15) for c in base_color)
                    dx = tile_x + random.randint(5, tile_size - 5)
                    dy = tile_y + random.randint(5, tile_size - 5)
                    pygame.draw.circle(surface, detail_color, (dx, dy), 2)
    
    def draw_walls(self, surface: pygame.Surface, floor_idx: int):
        """繪製石牆邊框"""
        theme = FLOOR_THEMES.get(floor_idx, FLOOR_THEMES[0])
        
        arena_x, arena_y = 80, 80
        arena_w, arena_h = self.width - 160, self.height - 220
        wall_h = 25
        brick_w = 32
        
        # === 上方石牆 ===
        for i in range(0, arena_w + brick_w, brick_w):
            bx = arena_x + i
            if bx > arena_x + arena_w:
                continue
            
            # 石塊頂部
            pygame.draw.rect(surface, theme['wall_top'], 
                           (bx, arena_y - wall_h, brick_w - 2, wall_h // 2))
            # 石塊正面
            pygame.draw.rect(surface, theme['wall_face'], 
                           (bx, arena_y - wall_h // 2, brick_w - 2, wall_h // 2))
            # 陰影
            pygame.draw.line(surface, (30, 25, 20), 
                           (bx, arena_y), (bx + brick_w - 2, arena_y), 2)
        
        # === 左側石牆 ===
        for j in range(0, arena_h, 20):
            by = arena_y + j
            pygame.draw.rect(surface, theme['wall_face'], 
                           (arena_x - 25, by, 25, 18))
            pygame.draw.rect(surface, theme['stone_dark'], 
                           (arena_x - 25, by, 25, 18), 1)
        
        # === 右側石牆 ===
        for j in range(0, arena_h, 20):
            by = arena_y + j
            pygame.draw.rect(surface, theme['wall_face'], 
                           (arena_x + arena_w, by, 25, 18))
            pygame.draw.rect(surface, theme['stone_dark'], 
                           (arena_x + arena_w, by, 25, 18), 1)
        
        # === 下方石牆 ===
        for i in range(0, arena_w + brick_w, brick_w):
            bx = arena_x + i
            if bx > arena_x + arena_w:
                continue
            pygame.draw.rect(surface, theme['wall_face'], 
                           (bx, arena_y + arena_h, brick_w - 2, 20))
    
    def draw_debris(self, surface: pygame.Surface, floor_idx: int):
        """繪製樹木和裝飾物"""
        theme = FLOOR_THEMES.get(floor_idx, FLOOR_THEMES[0])
        
        # 繪製樹木
        for tree in self.tree_positions:
            self._draw_tree(surface, tree['x'], tree['y'], tree['size'], theme)
        
        # 繪製裝飾物
        for prop in self.props:
            self._draw_prop(surface, prop['x'], prop['y'], prop['type'], theme)
    
    def _draw_tree(self, surface: pygame.Surface, x: int, y: int, 
                   size: float, theme: dict):
        """繪製像素風格樹木"""
        trunk_w = int(20 * size)
        trunk_h = int(50 * size)
        
        # 樹幹
        pygame.draw.rect(surface, theme['tree_trunk'],
                        (x - trunk_w // 2, y, trunk_w, trunk_h))
        
        # 樹葉（多層橢圓）
        leaves_y = y - int(30 * size)
        leaves_w = int(60 * size)
        leaves_h = int(80 * size)
        
        # 深色底層
        pygame.draw.ellipse(surface, theme['tree_leaves'],
                           (x - leaves_w // 2 - 5, leaves_y, leaves_w + 10, leaves_h))
        # 主體
        pygame.draw.ellipse(surface, theme['tree_leaves'],
                           (x - leaves_w // 2, leaves_y + 5, leaves_w, leaves_h - 10))
        # 高光
        pygame.draw.ellipse(surface, theme['tree_leaves_light'],
                           (x - leaves_w // 3, leaves_y + 15, leaves_w // 2, leaves_h // 2))
    
    def _draw_prop(self, surface: pygame.Surface, x: int, y: int, 
                   prop_type: str, theme: dict):
        """繪製場景裝飾物"""
        if prop_type == 'chest':
            # 寶箱
            pygame.draw.rect(surface, (120, 80, 40), (x - 15, y - 10, 30, 20))
            pygame.draw.rect(surface, (180, 140, 60), (x - 15, y - 15, 30, 8))
            pygame.draw.rect(surface, (200, 180, 80), (x - 3, y - 8, 6, 6))
        
        elif prop_type == 'crystal':
            # 水晶
            crystal_color = (100, 180, 255)
            points = [(x, y - 25), (x - 10, y), (x, y + 5), (x + 10, y)]
            pygame.draw.polygon(surface, crystal_color, points)
            pygame.draw.polygon(surface, (150, 220, 255), 
                               [(x, y - 20), (x - 5, y - 5), (x, y)])
        
        elif prop_type == 'pillar':
            # 石柱
            pygame.draw.rect(surface, theme['stone_light'], (x - 12, y - 40, 24, 50))
            pygame.draw.rect(surface, theme['stone_dark'], (x - 15, y - 45, 30, 8))
            pygame.draw.rect(surface, theme['stone_dark'], (x - 15, y + 5, 30, 8))
        
        elif prop_type == 'barrel':
            # 木桶
            pygame.draw.ellipse(surface, (100, 70, 45), (x - 12, y - 5, 24, 10))
            pygame.draw.rect(surface, (90, 60, 40), (x - 10, y - 20, 20, 20))
            pygame.draw.ellipse(surface, (80, 55, 35), (x - 12, y - 22, 24, 8))


class FloorTransition:
    """樓層轉換動畫"""
    
    def __init__(self):
        self.active = False
        self.progress = 0.0
        self.duration = 1.5
        self.phase = "descend"  # descend, black, ascend
        self.from_floor = 0
        self.to_floor = 1
        
        # 樓梯動畫參數
        self.stair_offset = 0
        
    def start(self, from_floor: int, to_floor: int):
        self.active = True
        self.progress = 0.0
        self.from_floor = from_floor
        self.to_floor = to_floor
        self.phase = "descend"
    
    def update(self, dt: float) -> bool:
        """更新動畫，返回是否完成"""
        if not self.active:
            return True
        
        self.progress += dt / self.duration
        
        if self.progress < 0.4:
            self.phase = "descend"
            self.stair_offset = int((self.progress / 0.4) * HEIGHT)
        elif self.progress < 0.6:
            self.phase = "black"
        elif self.progress < 1.0:
            self.phase = "ascend"
            self.stair_offset = int(((1.0 - self.progress) / 0.4) * HEIGHT)
        else:
            self.active = False
            return True
        
        return False
    
    def draw(self, surface: pygame.Surface, floor_idx: int):
        """繪製過場動畫"""
        if not self.active:
            return
        
        theme = FLOOR_THEMES.get(floor_idx, FLOOR_THEMES[0])
        
        if self.phase == "black":
            # 全黑畫面 + 文字
            surface.fill((10, 8, 5))
            
            font = pygame.font.SysFont("arial", 36, bold=True)
            text = f"Descending to B{self.to_floor + 1}F..."
            text_surf = font.render(text, True, theme['accent'])
            text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            surface.blit(text_surf, text_rect)
            
            # 樓梯圖示
            stair_y = HEIGHT // 2 + 50
            for i in range(5):
                step_w = 80 - i * 10
                step_x = WIDTH // 2 - step_w // 2
                step_y = stair_y + i * 15
                pygame.draw.rect(surface, theme['accent'], (step_x, step_y, step_w, 10))
        
        else:
            # 下降/上升效果 - 黑幕遮罩
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill(BLACK)
            
            if self.phase == "descend":
                # 從上往下遮蓋
                cover_h = self.stair_offset
                overlay_alpha = min(255, int(cover_h / HEIGHT * 255))
            else:
                # 從下往上揭開
                cover_h = self.stair_offset
                overlay_alpha = min(255, int(cover_h / HEIGHT * 255))
            
            overlay.set_alpha(overlay_alpha)
            surface.blit(overlay, (0, 0))


class Button:
    """可點擊按鈕"""
    def __init__(self, x: int, y: int, w: int, h: int, text: str, 
                 action_data=None, enabled: bool = True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action_data = action_data
        self.enabled = enabled
        self.hovered = False
    
    def contains(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos) and self.enabled
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        if not self.enabled:
            bg_color = (50, 45, 40)
            text_color = (100, 90, 80)
            border_color = (70, 60, 50)
        elif self.hovered:
            bg_color = MENU_HOVER
            text_color = GOLD
            border_color = GOLD
        else:
            bg_color = MENU_BG
            text_color = WHITE
            border_color = MENU_BORDER
        
        # 按鈕底部陰影
        shadow_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, 
                                  self.rect.width, self.rect.height)
        pygame.draw.rect(surface, (20, 18, 15), shadow_rect, border_radius=5)
        
        # 按鈕本體
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=5)
        
        # 文字
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


def draw_fancy_hp_bar(surface: pygame.Surface, x: int, y: int, w: int, h: int,
                      current: int, maximum: int, color: Tuple) -> None:
    """繪製精緻的血條"""
    ratio = max(0, current) / max(1, maximum)
    
    # 外框
    pygame.draw.rect(surface, (20, 18, 15), (x - 2, y - 2, w + 4, h + 4), border_radius=2)
    pygame.draw.rect(surface, (50, 45, 40), (x, y, w, h), border_radius=2)
    
    if ratio > 0:
        fill_w = int(w * ratio)
        pygame.draw.rect(surface, color, (x, y, fill_w, h), border_radius=2)
        
        # 高光
        highlight_color = tuple(min(255, c + 50) for c in color)
        pygame.draw.line(surface, highlight_color, (x + 2, y + 1), (x + fill_w - 2, y + 1))


class DungeonPygameApp:
    """經典地下城風格 RPG - 手動操作"""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("🥝 Kiwi Dungeon - Classic Dungeon Style")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # 建立遊戲環境
        players = create_default_players()
        floors = build_dungeon_floors()
        self.env = DungeonBattleEnv(floors=floors, players=players)
        
        # Agent 模式系統
        self.agent_types = [
            ("Heuristic", HeuristicDungeonAgent),
            ("Random", RandomDungeonAgent),
            ("Q-Learning", QLearningDungeonAgent)
        ]
        self.agent_mode_idx = 0
        self.agent = self.agent_types[0][1]()

        # 狀態
        self.floor_idx: int = 0
        self.obs = self.env.reset(self.floor_idx)
        self.terminated: bool = False
        self.truncated: bool = False
        self.total_reward: float = 0.0

        self.running: bool = True
        self.game_state: str = "PLAYING"

        # 手動操作模式
        self.manual_mode: bool = True
        self.player_turn: bool = True
        self.current_phase: str = "SELECT_ACTION"
        self.selected_action_type: Optional[str] = None
        self.selected_skill = None
        self.action_buttons: List[Button] = []
        self.target_buttons: List[Button] = []
        
        # 動畫
        self.animation_time: float = 0.0
        self.enemy_turn_timer: float = 0.0

        # 視覺系統
        self.tile_renderer = DungeonTileRenderer(WIDTH, HEIGHT)
        self.tile_renderer.generate_debris(self.floor_idx)
        self.floor_transition = FloorTransition()
        self.effect_manager = EffectManager()
        self.particle_system = ParticleSystem(WIDTH, HEIGHT)

        # 角色位置
        self.character_positions: Dict[str, Tuple[int, int]] = {}
        
        # 動作動畫
        self.action_animation_active = False
        self.action_animation_timer = 0.0
        self.pending_action = None
        
        # 戰鬥訊息
        self.battle_messages: List[Tuple[str, float]] = []

        # 字體
        self.font_title = pygame.font.SysFont("arial", 36, bold=True)
        self.font_big = pygame.font.SysFont("arial", 28)
        self.font_mid = pygame.font.SysFont("arial", 20)
        self.font_small = pygame.font.SysFont("arial", 16)
        self.font_tiny = pygame.font.SysFont("arial", 14)
        
        self._build_action_buttons()
        
        # 啟動訊息
        print("=" * 50)
        print("🥝 Kiwi Dungeon RPG - Controls:")
        print("  SPACE = Toggle Manual/Auto mode")
        print("  Q = Cycle Agent mode (Heuristic/Random/Q-Learning)")
        print("  1/2/3 = Select action")
        print("  ESC = Quit")
        print(f"  Current mode: {'MANUAL' if self.manual_mode else 'AUTO'}")
        print("=" * 50)

    def _build_action_buttons(self):
        self.action_buttons.clear()
        player = self.env.players[0]
        
        button_y = HEIGHT - 80
        button_w = 130
        button_h = 40
        spacing = 15
        start_x = 50
        
        self.action_buttons.append(
            Button(start_x, button_y, button_w, button_h, "⚔ Attack", 
                   action_data={"type": "attack"})
        )
        
        for i, skill in enumerate(player.skills):
            can_use = player.mp >= skill.mp_cost
            skill_text = f"✨ {skill.name[:10]}"
            
            self.action_buttons.append(
                Button(start_x + (button_w + spacing) * (i + 1), button_y, 
                      button_w, button_h, skill_text,
                      action_data={"type": "skill", "skill": skill, "index": i},
                      enabled=can_use)
            )

    def _build_target_buttons(self, is_heal: bool = False):
        self.target_buttons.clear()
        targets = self.env.players if is_heal else self.env.enemies
        
        for char in targets:
            if not char.is_alive():
                continue
            pos = self.character_positions.get(char.name)
            if pos:
                btn_w, btn_h = 90, 28
                btn_x = pos[0] - btn_w // 2
                btn_y = pos[1] - 70
                
                target_list = self.env.players if is_heal else self.env.enemies
                idx = target_list.index(char)
                
                self.target_buttons.append(
                    Button(btn_x, btn_y, btn_w, btn_h, f"▶ {char.name[:8]}",
                           action_data={"target": char, "index": idx})
                )

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.animation_time += dt
            
            self._handle_events()
            self._update_logic(dt)
            self._update_effects(dt)
            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit(0)

    def _handle_events(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        
        for btn in self.action_buttons + self.target_buttons:
            btn.hovered = btn.contains(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # ESC 永遠可以退出遊戲
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                # Q 鍵切換 Agent（任何時候都可以）
                elif event.key == pygame.K_q:
                    self._cycle_agent_mode()
                
                # SPACE 鍵處理
                elif event.key == pygame.K_SPACE:
                    print(f"[DEBUG] SPACE pressed! game_state={self.game_state}")
                    
                    if self.game_state == "FLOOR_COMPLETE":
                        # 關卡完成時，按 SPACE 進入傳送門
                        print("[DEBUG] Entering portal to next floor")
                        self._proceed_to_next_floor()
                    elif self.game_state == "MODE_SELECT":
                        # 模式選擇中，按 SPACE 切換 MANUAL/AUTO
                        self.manual_mode = not self.manual_mode
                        print(f"[DEBUG] Mode toggled to: {'MANUAL' if self.manual_mode else 'AUTO'}")
                    elif self.game_state in ("GAME_OVER", "VICTORY"):
                        # 遊戲結束時重新開始
                        print("[DEBUG] Restarting game")
                        self._restart_game()
                    elif self.game_state == "PLAYING":
                        # 遊戲中切換自動/手動模式
                        if self.current_phase == "SELECT_TARGET":
                            self.current_phase = "SELECT_ACTION"
                            self.target_buttons.clear()
                        else:
                            self.manual_mode = not self.manual_mode
                            print(f"[DEBUG] Toggled manual_mode to: {self.manual_mode}")
                            self._build_action_buttons()
                
                # 數字鍵選擇動作（僅遊戲中手動模式）
                elif self.game_state == "PLAYING" and self.manual_mode:
                    if event.key == pygame.K_1:
                        self._handle_action_select(0)
                    elif event.key == pygame.K_2:
                        self._handle_action_select(1)
                    elif event.key == pygame.K_3:
                        self._handle_action_select(2)
                
                # ENTER 鍵開始遊戲（MODE_SELECT 狀態）
                elif event.key == pygame.K_RETURN and self.game_state == "MODE_SELECT":
                    print(f"[DEBUG] Starting game with mode: {'MANUAL' if self.manual_mode else 'AUTO'}")
                    self.game_state = "PLAYING"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_click(mouse_pos)

    def _handle_click(self, pos: Tuple[int, int]):
        if self.game_state != "PLAYING" or self.floor_transition.active:
            return
        
        if self.current_phase == "SELECT_ACTION" and self.manual_mode and self.player_turn:
            for btn in self.action_buttons:
                if btn.contains(pos):
                    self._process_action_button(btn.action_data)
                    return
        
        elif self.current_phase == "SELECT_TARGET":
            for btn in self.target_buttons:
                if btn.contains(pos):
                    self._process_target_select(btn.action_data)
                    return
            
            # 直接點擊角色
            for char in (self.env.enemies + self.env.players):
                if not char.is_alive():
                    continue
                char_pos = self.character_positions.get(char.name)
                if char_pos:
                    dist = math.sqrt((pos[0] - char_pos[0])**2 + (pos[1] - char_pos[1])**2)
                    if dist < 50:
                        is_heal = self.selected_skill and isinstance(self.selected_skill, HealingSkill)
                        if is_heal and char.team == Team.PLAYERS:
                            idx = self.env.players.index(char)
                            self._process_target_select({"target": char, "index": idx})
                            return
                        elif not is_heal and char.team == Team.ENEMIES:
                            idx = self.env.enemies.index(char)
                            self._process_target_select({"target": char, "index": idx})
                            return

    def _handle_action_select(self, index: int):
        if self.current_phase != "SELECT_ACTION" or not self.manual_mode or not self.player_turn:
            return
        if index < len(self.action_buttons) - 1:
            btn = self.action_buttons[index]
            if btn.enabled:
                self._process_action_button(btn.action_data)
    
    def _cycle_agent_mode(self):
        """切換 Agent 模式 (Q 鍵)"""
        self.agent_mode_idx = (self.agent_mode_idx + 1) % len(self.agent_types)
        agent_name, agent_class = self.agent_types[self.agent_mode_idx]
        self.agent = agent_class()
        
        msg = f"🤖 Agent switched to: {agent_name}"
        self.battle_messages.append((msg, 3.0))
        print(f"[Agent Mode] Switched to {agent_name}")

    def _process_action_button(self, action_data: dict):
        if action_data["type"] == "toggle_auto":
            self.manual_mode = not self.manual_mode
            self._build_action_buttons()
            return
        
        if action_data["type"] == "attack":
            self.selected_action_type = "attack"
            self.selected_skill = None
            self.current_phase = "SELECT_TARGET"
            self._build_target_buttons(is_heal=False)
        
        elif action_data["type"] == "skill":
            skill = action_data["skill"]
            self.selected_action_type = "skill"
            self.selected_skill = skill
            
            if isinstance(skill, AreaAttackSkill):
                self._execute_area_skill(skill)
            else:
                is_heal = isinstance(skill, HealingSkill)
                self.current_phase = "SELECT_TARGET"
                self._build_target_buttons(is_heal=is_heal)

    def _execute_area_skill(self, skill):
        player = self.env.players[0]
        alive_enemy_indices = [i for i, e in enumerate(self.env.enemies) if e.is_alive()]
        
        action = BattleAction(
            actor=player,
            action_type=ActionType.USE_SKILL,
            target_ids=alive_enemy_indices,
            skill=skill
        )
        
        self.current_phase = "ANIMATING"
        self._trigger_action_animation(action)
        self.pending_action = action

    def _process_target_select(self, target_data: dict):
        player = self.env.players[0]
        target_idx = target_data["index"]
        
        if self.selected_action_type == "attack":
            action = BattleAction(
                actor=player,
                action_type=ActionType.BASIC_ATTACK,
                target_ids=[target_idx]
            )
        else:
            action = BattleAction(
                actor=player,
                action_type=ActionType.USE_SKILL,
                target_ids=[target_idx],
                skill=self.selected_skill
            )
        
        self.current_phase = "ANIMATING"
        self.target_buttons.clear()
        self._trigger_action_animation(action)
        self.pending_action = action

    def _restart_game(self):
        print("=== RESTARTING GAME ===")
        players = create_default_players()
        floors = build_dungeon_floors()
        self.env = DungeonBattleEnv(floors=floors, players=players)
        self.floor_idx = 0
        self.obs = self.env.reset(self.floor_idx)
        self.terminated = False
        self.truncated = False
        self.total_reward = 0.0
        
        # 進入模式選擇狀態
        self.game_state = "MODE_SELECT"
        self.manual_mode = True  # 預設手動模式
        
        self.player_turn = True
        self.current_phase = "SELECT_ACTION"
        self.battle_messages.clear()
        self.tile_renderer.generate_debris(self.floor_idx)
        self.floor_transition.active = False
        self.action_animation_active = False
        self._build_action_buttons()
        print("=== SELECT MODE TO START ===")  # Debug 訊息  # Debug 訊息

    def _update_logic(self, dt: float) -> None:
        # 樓層轉換動畫
        if self.floor_transition.active:
            self.floor_transition.update(dt)
            return
        
        if self.game_state != "PLAYING":
            return
        
        if self.action_animation_active:
            self.action_animation_timer -= dt
            if self.action_animation_timer <= 0:
                self.action_animation_active = False
                if self.pending_action:
                    self._execute_action(self.pending_action)
                    self.pending_action = None
            return
        
        if self.terminated or self.truncated:
            self._handle_floor_end()
            return
        
        # 自動模式
        if not self.manual_mode and self.player_turn and self.current_phase == "SELECT_ACTION":
            player = self.env.players[0]
            action = self.agent.select_action(self.env, player)
            self.current_phase = "ANIMATING"
            self._trigger_action_animation(action)
            self.pending_action = action
            return
        
        # 敵人回合
        if self.current_phase == "ENEMY_TURN":
            self.enemy_turn_timer -= dt
            if self.enemy_turn_timer <= 0:
                self._process_enemy_turn()

    def _process_enemy_turn(self):
        for enemy in self.env.enemies:
            if enemy.is_alive() and not hasattr(enemy, '_acted_this_round'):
                enemy._acted_this_round = True
                action = enemy.take_turn(self.env)
                if action and action.action_type != ActionType.PASS:
                    self.current_phase = "ANIMATING"
                    self._trigger_action_animation(action)
                    self.pending_action = action
                    return
        
        for enemy in self.env.enemies:
            if hasattr(enemy, '_acted_this_round'):
                delattr(enemy, '_acted_this_round')
        
        self.player_turn = True
        self.current_phase = "SELECT_ACTION"
        self._build_action_buttons()

    def _trigger_action_animation(self, action):
        self.action_animation_active = True
        self.action_animation_timer = 0.5
        
        actor = action.actor
        actor_pos = self.character_positions.get(actor.name, (WIDTH//2, HEIGHT//2))
        
        if action.action_type == ActionType.BASIC_ATTACK and action.target_ids:
            target_pool = self.env.enemies if actor.team == Team.PLAYERS else self.env.players
            if action.target_ids[0] < len(target_pool):
                target = target_pool[action.target_ids[0]]
                target_pos = self.character_positions.get(target.name, (WIDTH//2, 200))
                self.effect_manager.add_slash(actor_pos[0], actor_pos[1], 
                                             target_pos[0], target_pos[1])
                self.effect_manager.shake(5, 0.2)
        
        elif action.action_type == ActionType.USE_SKILL and action.skill:
            skill_name = action.skill.name.lower()
            
            if 'whirlwind' in skill_name:
                self.effect_manager.add_whirlwind(WIDTH // 2, 200)
                self.effect_manager.shake(8, 0.3)
            elif 'slash' in skill_name or 'bite' in skill_name:
                target_pool = self.env.enemies if actor.team == Team.PLAYERS else self.env.players
                if action.target_ids and action.target_ids[0] < len(target_pool):
                    target = target_pool[action.target_ids[0]]
                    target_pos = self.character_positions.get(target.name, (WIDTH//2, 200))
                    self.effect_manager.add_slash(actor_pos[0], actor_pos[1],
                                                 target_pos[0], target_pos[1])
                    self.effect_manager.shake(6, 0.25)
            elif 'heal' in skill_name or 'light' in skill_name:
                if action.target_ids:
                    target = self.env.players[action.target_ids[0]]
                    target_pos = self.character_positions.get(target.name, (WIDTH//2, HEIGHT-180))
                    self.effect_manager.add_heal(target_pos[0], target_pos[1])
            elif 'inferno' in skill_name or 'breath' in skill_name or 'fire' in skill_name:
                targets = [(self.character_positions.get(p.name, (WIDTH//2, HEIGHT-180))) 
                          for p in self.env.players if p.is_alive()]
                self.effect_manager.add_fire_breath(actor_pos[0], actor_pos[1], targets)
            elif 'dark' in skill_name or 'bolt' in skill_name:
                if action.target_ids and action.target_ids[0] < len(self.env.players):
                    target = self.env.players[action.target_ids[0]]
                    target_pos = self.character_positions.get(target.name, (WIDTH//2, HEIGHT-180))
                    self.effect_manager.add_dark_bolt(actor_pos[0], actor_pos[1],
                                                     target_pos[0], target_pos[1])

    def _execute_action(self, action):
        hp_before = {p.name: p.hp for p in self.env.players + self.env.enemies}
        
        self.obs, reward, self.terminated, self.truncated, _ = self.env.step(action)
        self.total_reward += reward
        
        for char in self.env.players + self.env.enemies:
            pos = self.character_positions.get(char.name)
            if pos and char.name in hp_before:
                hp_diff = hp_before[char.name] - char.hp
                if hp_diff > 0:
                    self.effect_manager.add_damage(pos[0], pos[1] - 30, hp_diff)
                    self.effect_manager.add_hit_flash(pos[0], pos[1])
                elif hp_diff < 0:
                    self.effect_manager.add_damage(pos[0], pos[1] - 30, -hp_diff, is_heal=True)
        
        actor_name = action.actor.name
        if action.action_type == ActionType.BASIC_ATTACK:
            msg = f"{actor_name} attacks!"
        elif action.action_type == ActionType.USE_SKILL and action.skill:
            msg = f"{actor_name} uses {action.skill.name}!"
        else:
            msg = f"{actor_name} acts"
        
        self.battle_messages.append((msg, 3.0))
        if len(self.battle_messages) > 4:
            self.battle_messages.pop(0)
        
        self._build_action_buttons()
        
        if action.actor.team == Team.PLAYERS:
            self.player_turn = False
            self.current_phase = "ENEMY_TURN"
            self.enemy_turn_timer = 0.6
        else:
            any_enemy_left = any(e.is_alive() and not hasattr(e, '_acted_this_round') 
                                for e in self.env.enemies)
            if any_enemy_left:
                self.current_phase = "ENEMY_TURN"
                self.enemy_turn_timer = 0.6
            else:
                for enemy in self.env.enemies:
                    if hasattr(enemy, '_acted_this_round'):
                        delattr(enemy, '_acted_this_round')
                self.player_turn = True
                self.current_phase = "SELECT_ACTION"

    def _handle_floor_end(self) -> None:
        players_alive = any(p.is_alive() for p in self.env.players)
        enemies_alive = any(e.is_alive() for e in self.env.enemies)

        if not players_alive:
            self.game_state = "GAME_OVER"
            return

        if not enemies_alive:
            if self.floor_idx + 1 < len(self.env.floors):
                # === 進入等待傳送狀態 ===
                self.game_state = "FLOOR_COMPLETE"
                self.floor_complete_timer = 0.0
                
                # 回復 HP/MP
                for player in self.env.players:
                    if player.is_alive():
                        heal_amount = player.stats.max_hp // 2
                        player.hp = min(player.stats.max_hp, player.hp + heal_amount)
                        mp_restore = int(player.stats.max_mp * 0.8)
                        player.mp = min(player.stats.max_mp, player.mp + mp_restore)
                
                self.battle_messages.append(("✨ Floor cleared! HP/MP restored!", 5.0))
                self.battle_messages.append(("⏳ Press SPACE to enter portal...", 5.0))
            else:
                self.game_state = "VICTORY"
        else:
            self.game_state = "GAME_OVER"
    
    def _proceed_to_next_floor(self):
        """進入下一層"""
        self.floor_transition.start(self.floor_idx, self.floor_idx + 1)
        self.floor_idx += 1
        self.obs = self.env.reset(self.floor_idx)
        self.terminated = False
        self.truncated = False
        self.player_turn = True
        self.current_phase = "SELECT_ACTION"
        self.game_state = "PLAYING"
        self.tile_renderer.generate_debris(self.floor_idx)
        self._build_action_buttons()
        self.battle_messages.append((f"Descending to B{self.floor_idx + 1}F!", 3.0))

    def _update_effects(self, dt: float):
        self.effect_manager.update(dt)
        self.particle_system.update(dt)
        self.battle_messages = [(msg, t - dt) for msg, t in self.battle_messages if t > dt]

    def _draw(self) -> None:
        shake_offset = self.effect_manager.screen_shake.update(0)
        buffer = pygame.Surface((WIDTH, HEIGHT))
        
        # 地下城背景
        self.tile_renderer.draw_tile_floor(buffer, self.floor_idx)
        self.tile_renderer.draw_walls(buffer, self.floor_idx)
        self.tile_renderer.draw_debris(buffer, self.floor_idx)
        
        # 樓層標題
        self._draw_floor_title(buffer)
        
        # 角色
        self._draw_characters(buffer)
        
        # 特效
        self.effect_manager.draw(buffer)
        
        # UI
        self._draw_action_menu(buffer)
        self._draw_target_indicators(buffer)
        self._draw_status_panel(buffer)
        self._draw_battle_log(buffer)
        
        # 樓層轉換動畫
        if self.floor_transition.active:
            self.floor_transition.draw(buffer, self.floor_idx)
        
        # 結束畫面
        self._draw_end_overlay(buffer)
        
        self.screen.blit(buffer, shake_offset)

    def _draw_floor_title(self, surface: pygame.Surface):
        theme = FLOOR_THEMES.get(self.floor_idx, FLOOR_THEMES[0])
        floor = self.env.floors[self.floor_idx]
        
        # 標題背景
        title_bg = pygame.Surface((350, 50), pygame.SRCALPHA)
        title_bg.fill((0, 0, 0, 180))
        surface.blit(title_bg, (WIDTH // 2 - 175, 10))
        
        # 樓層文字
        floor_text = f"B{self.floor_idx + 1}F - {floor.name}"
        title_surf = self.font_mid.render(floor_text, True, theme['accent'])
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 35))
        surface.blit(title_surf, title_rect)
        
        # Boss 警告
        if floor.is_boss_floor:
            boss_alive = any(e.is_alive() and 'Dragon' in e.name for e in self.env.enemies)
            if boss_alive:
                pulse = int(abs(math.sin(self.animation_time * 3)) * 100) + 155
                warning = self.font_small.render("⚠ BOSS ⚠", True, (255, pulse, 50))
                surface.blit(warning, (WIDTH // 2 - 35, 55))

    def _get_character_positions(self):
        players = self.env.players
        enemies = self.env.enemies
        
        player_y = HEIGHT - 240
        player_positions = []
        for i, p in enumerate(players):
            x = 250 + i * 200 if len(players) > 1 else WIDTH // 2
            player_positions.append((x, player_y))
            self.character_positions[p.name] = (x, player_y)
        
        enemy_y = 200
        enemy_positions = []
        for i, e in enumerate(enemies):
            x = WIDTH // 2 if len(enemies) == 1 else 200 + i * (WIDTH - 400) // max(1, len(enemies) - 1)
            enemy_positions.append((x, enemy_y))
            self.character_positions[e.name] = (x, enemy_y)
        
        return player_positions, enemy_positions

    def _draw_characters(self, surface: pygame.Surface) -> None:
        player_positions, enemy_positions = self._get_character_positions()
        
        for enemy, (x, y) in zip(self.env.enemies, enemy_positions):
            self._draw_character_with_sprite(surface, enemy, x, y)
        
        for player, (x, y) in zip(self.env.players, player_positions):
            self._draw_character_with_sprite(surface, player, x, y)

    def _draw_character_with_sprite(self, surface: pygame.Surface, char, x: int, y: int):
        alive = char.is_alive()
        is_boss = char.__class__.__name__ == "FireDragon"
        enraged = is_boss and alive and (char.hp / char.stats.max_hp < 0.3)
        
        # 陰影
        shadow_alpha = 100 if alive else 50
        shadow = pygame.Surface((60, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, shadow_alpha), (0, 0, 60, 20))
        surface.blit(shadow, (x - 30, y + 35))
        
        # 精靈
        if char.name == "Kiwi":
            SpriteRenderer.draw_kiwi(surface, x, y, 50, alive, self.animation_time)
            sprite_h = 50
        elif char.name == "Healer Bird":
            SpriteRenderer.draw_healer(surface, x, y, 45, alive, self.animation_time)
            sprite_h = 45
        elif "Slime" in char.name:
            SpriteRenderer.draw_slime(surface, x, y, 35, alive, self.animation_time)
            sprite_h = 35
        elif char.name == "Goblin":
            SpriteRenderer.draw_goblin(surface, x, y, 40, alive, self.animation_time)
            sprite_h = 40
        elif "Orc" in char.name:
            SpriteRenderer.draw_orc(surface, x, y, 55, alive, self.animation_time)
            sprite_h = 55
        elif "Mage" in char.name:
            SpriteRenderer.draw_dark_mage(surface, x, y, 45, alive, self.animation_time)
            sprite_h = 45
        elif "Dragon" in char.name:
            SpriteRenderer.draw_fire_dragon(surface, x, y, 90, alive, self.animation_time, enraged)
            sprite_h = 90
        else:
            SpriteRenderer.draw_slime(surface, x, y, 35, alive, self.animation_time)
            sprite_h = 35
        
        # 血條
        bar_w = 70 if not is_boss else 100
        bar_y = y + sprite_h // 2 + 20
        hp_color = HP_GREEN if char.team == Team.PLAYERS else HP_RED
        draw_fancy_hp_bar(surface, x - bar_w // 2, bar_y, bar_w, 8, char.hp, char.stats.max_hp, hp_color)
        
        # 名稱
        name_color = GOLD if char.team == Team.PLAYERS else WHITE
        if not alive:
            name_color = (80, 70, 60)
        name_surf = self.font_tiny.render(char.name, True, name_color)
        surface.blit(name_surf, name_surf.get_rect(center=(x, y - sprite_h // 2 - 15)))

    def _draw_action_menu(self, surface: pygame.Surface):
        # 底部選單背景
        menu_rect = pygame.Rect(0, HEIGHT - 120, WIDTH, 120)
        pygame.draw.rect(surface, (25, 22, 18), menu_rect)
        pygame.draw.line(surface, (80, 70, 55), (0, HEIGHT - 120), (WIDTH, HEIGHT - 120), 3)
        
        # === 第一行：狀態提示（最上方）===
        if self.manual_mode:
            if self.current_phase == "SELECT_ACTION" and self.player_turn:
                status = ">> Choose action (1/2/3 or click):"
                color = GOLD
            elif self.current_phase == "SELECT_TARGET":
                status = ">> Select target:"
                color = (100, 200, 255)
            elif self.current_phase == "ENEMY_TURN":
                status = "Enemy turn..."
                color = HP_RED
            else:
                status = "Executing..."
                color = WHITE
        else:
            status = "Auto mode running..."
            color = (100, 180, 255)
        
        status_surf = self.font_small.render(status, True, color)
        surface.blit(status_surf, (20, HEIGHT - 115))
        
        # === 第一行右側：模式顯示（更清晰）===
        agent_name = self.agent_types[self.agent_mode_idx][0]
        mode_text = "MANUAL" if self.manual_mode else "AUTO"
        mode_color = GOLD if self.manual_mode else (100, 180, 255)
        
        # 分開顯示，更清晰
        # 模式
        mode_surf = self.font_small.render(mode_text, True, mode_color)
        surface.blit(mode_surf, (WIDTH - 420, HEIGHT - 115))
        
        # AI 類型
        ai_surf = self.font_tiny.render(f"AI: {agent_name}", True, (150, 145, 140))
        surface.blit(ai_surf, (WIDTH - 340, HEIGHT - 115))
        
        # 按鍵提示（更明顯）
        key_hint = "[Q] Switch AI    [SPACE] Toggle Mode"
        hint_surf = self.font_tiny.render(key_hint, True, (180, 175, 170))
        surface.blit(hint_surf, (WIDTH - 240, HEIGHT - 115))
        
        # === 第二行：動作按鈕（中間）===
        if self.current_phase == "SELECT_ACTION" and self.player_turn and self.manual_mode:
            for btn in self.action_buttons:
                btn.draw(surface, self.font_small)

    def _draw_target_indicators(self, surface: pygame.Surface):
        if self.current_phase != "SELECT_TARGET":
            return
        
        is_heal = self.selected_skill and isinstance(self.selected_skill, HealingSkill)
        targets = self.env.players if is_heal else self.env.enemies
        
        for char in targets:
            if not char.is_alive():
                continue
            pos = self.character_positions.get(char.name)
            if pos:
                pulse = int(abs(math.sin(self.animation_time * 5)) * 50) + 100
                color = (100, 255, 100) if is_heal else (255, 100, 100)
                
                # 目標指示圈
                pygame.draw.circle(surface, color, pos, 55, 3)
                pygame.draw.circle(surface, (*color, pulse), pos, 50, 2)

    def _draw_status_panel(self, surface: pygame.Surface):
        # 左下角玩家狀態
        panel_x, panel_y = 40, HEIGHT - 115
        
        for i, player in enumerate(self.env.players):
            px = WIDTH - 280 + i * 130
            py = HEIGHT - 55
            
            # MP 條
            draw_fancy_hp_bar(surface, px, py, 100, 6, player.mp, player.stats.max_mp, MP_BLUE)
            mp_text = f"MP {player.mp}/{player.stats.max_mp}"
            mp_surf = self.font_tiny.render(mp_text, True, MP_BLUE)
            surface.blit(mp_surf, (px, py - 15))
        
        # 分數
        score_surf = self.font_mid.render(f"Score: {int(self.total_reward)}", True, GOLD)
        surface.blit(score_surf, (WIDTH - 130, 80))

    def _draw_battle_log(self, surface: pygame.Surface):
        if not self.battle_messages:
            return
        
        log_x, log_y = WIDTH - 260, 120
        
        log_bg = pygame.Surface((230, 80), pygame.SRCALPHA)
        log_bg.fill((0, 0, 0, 120))
        surface.blit(log_bg, (log_x - 5, log_y - 5))
        
        for i, (msg, remaining) in enumerate(self.battle_messages[-3:]):
            alpha = min(255, int(remaining * 120))
            color = (255, 255, 255) if remaining > 1 else (180, 170, 160)
            msg_surf = self.font_tiny.render(msg[:30], True, color)
            msg_surf.set_alpha(alpha)
            surface.blit(msg_surf, (log_x, log_y + i * 22))

    def _draw_end_overlay(self, surface: pygame.Surface):
        if self.game_state == "PLAYING":
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        if self.game_state == "MODE_SELECT":
            # === 模式選擇畫面 ===
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
            # 標題
            title = self.font_title.render("SELECT MODE", True, GOLD)
            surface.blit(title, title.get_rect(center=(WIDTH // 2, 100)))
            
            # 當前設定
            agent_name = self.agent_types[self.agent_mode_idx][0]
            mode_text = "MANUAL" if self.manual_mode else "AUTO"
            mode_color = GOLD if self.manual_mode else (100, 180, 255)
            
            # 模式顯示
            mode_label = self.font_mid.render("Mode:", True, WHITE)
            surface.blit(mode_label, (WIDTH // 2 - 150, HEIGHT // 2 - 60))
            mode_value = self.font_big.render(mode_text, True, mode_color)
            surface.blit(mode_value, (WIDTH // 2 + 20, HEIGHT // 2 - 65))
            
            # AI 顯示
            ai_label = self.font_mid.render("AI:", True, WHITE)
            surface.blit(ai_label, (WIDTH // 2 - 150, HEIGHT // 2 - 20))
            ai_value = self.font_big.render(agent_name, True, (150, 200, 255))
            surface.blit(ai_value, (WIDTH // 2 + 20, HEIGHT // 2 - 25))
            
            # 按鍵提示
            hint1 = self.font_small.render("[SPACE]  Toggle Manual / Auto", True, (180, 175, 170))
            surface.blit(hint1, hint1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))
            
            hint2 = self.font_small.render("[Q]  Switch AI Type", True, (180, 175, 170))
            surface.blit(hint2, hint2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))
            
            # 開始提示
            start_hint = self.font_mid.render(">>> Press ENTER to START <<<", True, (255, 255, 150))
            surface.blit(start_hint, start_hint.get_rect(center=(WIDTH // 2, HEIGHT - 100)))
        
        elif self.game_state == "FLOOR_COMPLETE":
            # === 關卡完成 - 傳送門畫面 ===
            overlay.fill((0, 0, 0, 160))
            surface.blit(overlay, (0, 0))
            
            # 傳送門發光效果
            portal_y = HEIGHT // 2 - 20
            portal_pulse = math.sin(self.animation_time * 4) * 10
            portal_size = int(60 + portal_pulse)
            
            pygame.draw.ellipse(surface, (100, 200, 255), 
                              (WIDTH // 2 - portal_size, portal_y - portal_size // 2, 
                               portal_size * 2, portal_size), 4)
            pygame.draw.ellipse(surface, (150, 230, 255), 
                              (WIDTH // 2 - portal_size + 15, portal_y - portal_size // 2 + 10, 
                               portal_size * 2 - 30, portal_size - 20), 2)
            pygame.draw.ellipse(surface, (200, 255, 255), 
                              (WIDTH // 2 - 20, portal_y - 10, 40, 20))
            
            title = self.font_title.render("FLOOR CLEARED!", True, GOLD)
            surface.blit(title, title.get_rect(center=(WIDTH // 2, 100)))
            
            next_floor = self.floor_idx + 2
            portal_text = self.font_mid.render(f"Portal to B{next_floor}F opened!", True, (100, 200, 255))
            surface.blit(portal_text, portal_text.get_rect(center=(WIDTH // 2, portal_y + 60)))
            
            agent_name = self.agent_types[self.agent_mode_idx][0]
            mode_text = "MANUAL" if self.manual_mode else "AUTO"
            mode_info = self.font_small.render(f"Current: {mode_text} | AI: {agent_name}", True, (180, 175, 170))
            surface.blit(mode_info, mode_info.get_rect(center=(WIDTH // 2, HEIGHT - 150)))
            
            hint1 = self.font_small.render("[Q] Switch AI    [SPACE] Toggle Mode", True, (150, 145, 140))
            surface.blit(hint1, hint1.get_rect(center=(WIDTH // 2, HEIGHT - 120)))
            
            enter_hint = self.font_mid.render(">>> Press SPACE to enter portal <<<", True, (255, 255, 150))
            surface.blit(enter_hint, enter_hint.get_rect(center=(WIDTH // 2, HEIGHT - 80)))
        
        else:
            # === 遊戲結束畫面 ===
            overlay.fill((0, 0, 0, 210))
            surface.blit(overlay, (0, 0))

            if self.game_state == "GAME_OVER":
                msg, sub_msg, color = "GAME OVER", "Kiwi has fallen in the dungeon...", HP_RED
            else:
                msg, sub_msg, color = "VICTORY!", "The Fire Dragon is slain!", GOLD
            
            text = self.font_title.render(msg, True, color)
            surface.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
            
            sub = self.font_mid.render(sub_msg, True, WHITE)
            surface.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
            
            score = self.font_mid.render(f"Final Score: {int(self.total_reward)}", True, GOLD)
            surface.blit(score, score.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))
            
            hint = self.font_small.render("SPACE to restart | ESC to quit", True, (150, 140, 130))
            surface.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100)))


def main() -> None:
    app = DungeonPygameApp()
    app.run()


if __name__ == "__main__":
    main()
