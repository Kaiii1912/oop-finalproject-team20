# pygame_app.py
from __future__ import annotations

import sys
from typing import List, Tuple

import pygame

from dungeon_env import DungeonBattleEnv
from config_dungeon import create_default_players, build_dungeon_floors
from agents import HeuristicDungeonAgent  # 也可以換 RandomDungeonAgent
from battle_types import Team

WIDTH, HEIGHT = 960, 640
FPS = 60
TURN_INTERVAL = 0.8  # 每一回合之間停留秒數

BG_COLORS = [
    (30, 35, 60),   # B1
    (40, 25, 50),   # B2
    (60, 20, 20),   # B3（火龍巢穴）
]

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HP_GREEN = (46, 204, 113)
HP_RED = (231, 76, 60)
PLAYER_COLOR = (250, 224, 120)   # 奇異鳥
ENEMY_COLOR = (52, 152, 219)
BOSS_COLOR = (231, 76, 60)


def draw_hp_bar(surface: pygame.Surface,
                x: int,
                y: int,
                w: int,
                h: int,
                hp: int,
                max_hp: int,
                color_fg: Tuple[int, int, int]) -> None:
    ratio = max(0, hp) / max(1, max_hp)
    pygame.draw.rect(surface, (60, 60, 60), (x, y, w, h))
    pygame.draw.rect(surface, color_fg, (x, y, int(w * ratio), h))


class DungeonPygameApp:
    """
    使用 DungeonBattleEnv + HeuristicDungeonAgent，
    以 pygame 顯示三層地下城戰鬥流程。
    """

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Kiwi Dungeon - OOP RPG with Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.screen_rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()

        # 建立 Env / Players / Floors / Agent
        players = create_default_players()
        floors = build_dungeon_floors()
        self.env = DungeonBattleEnv(floors=floors, players=players)
        self.agent = HeuristicDungeonAgent()

        self.floor_idx: int = 0
        self.obs = self.env.reset(self.floor_idx)
        self.terminated: bool = False
        self.truncated: bool = False
        self.total_reward: float = 0.0

        self.turn_timer: float = 0.5 
        self.running: bool = True
        self.game_state: str = "PLAYING"  # PLAYING / GAME_OVER / VICTORY

        self.font_big = pygame.font.SysFont("arial", 40)
        self.font_mid = pygame.font.SysFont("arial", 26)
        self.font_small = pygame.font.SysFont("arial", 18)

    # ------------- 主迴圈 -------------

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update_logic(dt)
            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit(0)

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.running = False

    # ------------- 遊戲邏輯更新 -------------

    def _update_logic(self, dt: float) -> None:
        if self.game_state != "PLAYING":
            return

        self.turn_timer -= dt
        if self.turn_timer > 0:
            return

        # 如果目前這一層已經結束，決定是進下一層或遊戲結束
        if self.terminated or self.truncated:
            self._handle_floor_end()
            return

        # 還在這一層：由 Agent 幫 Kiwi 決定下一步
        player = self.env.players[0]  # 假設 index 0 是奇異鳥主角
        action = self.agent.select_action(self.env, player)
        self.obs, reward, self.terminated, self.truncated, _ = self.env.step(action)
        self.total_reward += reward

        self.turn_timer = TURN_INTERVAL

    def _handle_floor_end(self) -> None:
        # 判斷誰還活著
        players_alive = any(p.is_alive() for p in self.env.players)
        enemies_alive = any(e.is_alive() for e in self.env.enemies)

        if not players_alive:
            # 玩家隊伍全滅
            self.game_state = "GAME_OVER"
            return

        if not enemies_alive:
            # 通關當前樓層
            if self.floor_idx + 1 < len(self.env.floors):
                # 還有下一層 → 進下一層
                self.floor_idx += 1
                self.obs = self.env.reset(self.floor_idx)
                self.terminated = False
                self.truncated = False
                self.turn_timer = 1.0  # 進新樓層前停一下
            else:
                # 所有樓層都打完 → 勝利
                self.game_state = "VICTORY"
        else:
            # truncated 情況（例如最多回合限制），這裡可以當作 Game Over 或平局
            self.game_state = "GAME_OVER"

    # ------------- 繪製 -------------

    def _draw_background(self) -> None:
        # 不同樓層給不同顏色
        color = BG_COLORS[min(self.floor_idx, len(BG_COLORS) - 1)]
        self.screen.fill(color)

        # 簡單畫地城邊框
        dungeon_rect = pygame.Rect(40, 80, WIDTH - 80, HEIGHT - 160)
        pygame.draw.rect(self.screen, (20, 20, 20), dungeon_rect)
        pygame.draw.rect(self.screen, (80, 80, 80), dungeon_rect, width=2)

        # 樓層標題
        floor = self.env.floors[self.floor_idx]
        title = self.font_mid.render(
            f"Floor {self.floor_idx + 1}: {floor.name}", True, WHITE
        )
        self.screen.blit(title, (50, 30))

    def _get_layout_positions(
        self, num_players: int, num_enemies: int
    ) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        簡單排版：
        - 玩家在下排
        - 敵人在上排
        """
        bottom_y = HEIGHT - 130
        top_y = 150
        left_x = 120
        right_x = WIDTH - 120

        def row_positions(n: int, y: int) -> List[Tuple[int, int]]:
            if n <= 0:
                return []
            if n == 1:
                return [(WIDTH // 2, y)]
            xs = [
                left_x + (right_x - left_x) * i / (n - 1)
                for i in range(n)
            ]
            return [(int(x), y) for x in xs]

        players_pos = row_positions(num_players, bottom_y)
        enemies_pos = row_positions(num_enemies, top_y)
        return players_pos, enemies_pos

    def _draw_characters(self) -> None:
        players = self.env.players
        enemies = self.env.enemies

        player_pos, enemy_pos = self._get_layout_positions(len(players), len(enemies))

        for p, (x, y) in zip(players, player_pos):
            self._draw_single_character(p, x, y, is_boss=False)

        for e, (x, y) in zip(enemies, enemy_pos):
            is_boss = e.__class__.__name__ == "FireDragon"
            self._draw_single_character(e, x, y, is_boss=is_boss)

    def _draw_single_character(self, ch, x: int, y: int, is_boss: bool = False) -> None:
        if ch.team == Team.PLAYERS:
            body_color = PLAYER_COLOR
        else:
            body_color = BOSS_COLOR if is_boss else ENEMY_COLOR

        if not ch.is_alive():
            body_color = (80, 80, 80)

        radius = 26 if not is_boss else 40
        pygame.draw.circle(self.screen, body_color, (x, y), radius)

        # HP Bar
        hp_color = HP_GREEN if ch.team == Team.PLAYERS else HP_RED
        draw_hp_bar(
            self.screen,
            x - 40,
            y + radius + 8,
            80,
            8,
            ch.hp,
            ch.stats.max_hp,
            hp_color,
        )

        # 名稱
        name_text = self.font_small.render(ch.name, True, WHITE)
        name_rect = name_text.get_rect(center=(x, y - radius - 12))
        self.screen.blit(name_text, name_rect)

    def _draw_ui(self) -> None:
        # 玩家 HP 額外顯示
        main_player = self.env.players[0]
        hp_text = self.font_small.render(
            f"Kiwi HP: {main_player.hp}/{main_player.stats.max_hp}", True, WHITE
        )
        self.screen.blit(hp_text, (50, HEIGHT - 60))

        # 說明
        help_text = self.font_small.render(
            "Demo mode: Kiwi is controlled by HeuristicDungeonAgent (automatic).",
            True,
            (220, 220, 220),
        )
        self.screen.blit(help_text, (50, HEIGHT - 30))

    def _draw_end_overlay(self) -> None:
        if self.game_state == "PLAYING":
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if self.game_state == "GAME_OVER":
            msg = "Kiwi has fallen... Game Over"
            color = HP_RED
        else:
            msg = "You defeated the Fire Dragon! Victory!"
            color = HP_GREEN

        text = self.font_big.render(msg, True, color)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
        self.screen.blit(text, rect)

        sub = self.font_small.render("Press ESC to quit", True, WHITE)
        sub_rect = sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25))
        self.screen.blit(sub, sub_rect)

    def _draw(self) -> None:
        self._draw_background()
        self._draw_characters()
        self._draw_ui()
        self._draw_end_overlay()

def main() -> None:
    app = DungeonPygameApp()
    app.run()


if __name__ == "__main__":
    main()
