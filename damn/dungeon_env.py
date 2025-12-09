from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, TYPE_CHECKING

from battle_types import BattleAction, ActionType, Team
from characters import PlayerCharacter, EnemyCharacter

if TYPE_CHECKING:
    from characters import Character


class EventLog:
    """
    戰鬥訊息紀錄。
    """

    def __init__(self) -> None:
        self.entries: List[str] = []

    def add(self, msg: str) -> None:
        self.entries.append(msg)

    def flush(self) -> List[str]:
        out = self.entries[:]
        self.entries.clear()
        return out


@dataclass
class DungeonFloorConfig:
    """
    地下城單一樓層配置：
    - 名稱
    - 一組 factory，用來產生敵人實例
    - 是否為 Boss 樓層
    """
    name: str
    enemy_factories: List[callable]  # List[Callable[[], EnemyCharacter]]
    is_boss_floor: bool = False


class TurnManager:
    """
    根據 speed 決定本回合出手順序。
    """

    def __init__(self, env: "DungeonBattleEnv") -> None:
        self.env = env

    def get_turn_order(self) -> List["Character"]:
        from characters import Character  # 避免循環 import
        chars: List[Character] = [
            c for c in (self.env.players + self.env.enemies) if c.is_alive()
        ]
        # TODO[B]: 依 stats.speed 由大到小排序，回傳結果
        raise NotImplementedError


class DungeonBattleEnv:
    """
    三層地下城戰鬥環境。

    介面類似 Gym：
    - reset(floor_idx)
    - step(player_action)
    - render()
    """

    def __init__(self, floors: List[DungeonFloorConfig], players: List[PlayerCharacter]):
        self.floors = floors
        self.players = players
        self.enemies: List[EnemyCharacter] = []

        self.current_floor_idx: int = 0
        self.turn_count: int = 0

        self.event_log = EventLog()
        self.turn_manager = TurnManager(self)

    def reset(self, floor_idx: int = 0) -> Dict[str, Any]:
        """
        初始化某一樓層。
        """
        self.current_floor_idx = floor_idx
        self.turn_count = 0
        self.event_log = EventLog()
        self.turn_manager = TurnManager(self)

        # 重置玩家
        for p in self.players:
            p.hp = p.base_stats.max_hp
            p.mp = p.base_stats.max_mp

        floor = self.floors[floor_idx]
        self.enemies = [factory() for factory in floor.enemy_factories]

        return self._build_observation()

    def step(self, player_action: BattleAction) -> tuple[Dict[str, Any], float, bool, bool, Dict[str, Any]]:
        """
        執行一個完整回合：
        - 依 speed 取得行動順序
        - 主控玩家用傳入的 player_action
        - 敵人用自己的 AI 決定行動
        - 回傳 obs, reward, terminated, truncated, info
        """
        from agents import BaseAgent  # type hint 用，不會實際 import

        self.turn_count += 1
        reward = 0.0
        terminated = False
        truncated = False
        info: Dict[str, Any] = {}

        # TODO[B/C]:
        # 1. 取得 turn_order = self.turn_manager.get_turn_order()
        # 2. 對每個 actor：
        #    - 若是 players[0]：使用傳入的 player_action 呼叫 _apply_action(...)
        #    - 若是其他敵人：呼叫 actor.take_turn(self) 取得 action，再 _apply_action(...)
        # 3. 判斷是否所有 enemies 死亡 → 勝利，reward += 1, terminated = True
        #    判斷是否所有 players 死亡 → 失敗，reward -= 1, terminated = True
        # 4. 每回合可以小小扣分 reward -= 0.01 以避免拖太久

        obs = self._build_observation()
        return obs, reward, terminated, truncated, info

    def render(self) -> None:
        floor = self.floors[self.current_floor_idx]
        print(f"\n=== Floor {self.current_floor_idx + 1}: {floor.name} | Turn {self.turn_count} ===")

        print("[Party]")
        for p in self.players:
            status = "DEAD" if not p.is_alive() else f"HP {p.hp}/{p.stats.max_hp} MP {p.mp}/{p.stats.max_mp}"
            print(f"  - {p.name:10s} ({p.role:7s}) [{status}]")

        print("[Enemies]")
        for e in self.enemies:
            status = "DEAD" if not e.is_alive() else f"HP {e.hp}/{e.stats.max_hp} MP {e.mp}/{e.stats.max_mp}"
            print(f"  - {e.name:15s} [{status}]")

        for line in self.event_log.flush():
            print("  *", line)

    def _build_observation(self) -> Dict[str, Any]:
        """
        簡單用 dict 表示目前遊戲狀態，之後要接 RL 可以再設計 state encoding。
        """
        return {
            "floor_idx": self.current_floor_idx,
            "turn": self.turn_count,
            "players": [
                {
                    "name": p.name,
                    "hp": p.hp,
                    "max_hp": p.stats.max_hp,
                    "mp": p.mp,
                    "max_mp": p.stats.max_mp,
                    "alive": p.is_alive(),
                }
                for p in self.players
            ],
            "enemies": [
                {
                    "name": e.name,
                    "hp": e.hp,
                    "max_hp": e.stats.max_hp,
                    "mp": e.mp,
                    "max_mp": e.stats.max_mp,
                    "alive": e.is_alive(),
                }
                for e in self.enemies
            ],
        }

    def _apply_action(self, action: BattleAction) -> None:
        """
        實際執行一個 BattleAction。
        """
        actor = action.actor
        if not actor.is_alive():
            return

        # TODO[B/A]:
        # 根據 action_type：
        # - BASIC_ATTACK:
        #     依 target_ids 找到目標（在 players 或 enemies），計算傷害，呼叫 target.take_damage(...)
        #     並用 self.event_log.add(...) 記錄
        # - USE_SKILL:
        #     檢查 mp，呼叫 action.skill.apply(actor, targets, self)
        # - DEFEND / PASS:
        #     可以先只紀錄文字，不一定要有實際效果
        raise NotImplementedError
