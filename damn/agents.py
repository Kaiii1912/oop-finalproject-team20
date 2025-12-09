from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, TYPE_CHECKING
import random

from battle_types import BattleAction
from dungeon_env import DungeonBattleEnv
from characters import PlayerCharacter

if TYPE_CHECKING:
    from skills import HealingSkill


class BaseAgent(ABC):
    """
    控制「玩家」行動的 Agent 介面。
    """

    @abstractmethod
    def select_action(self, env: DungeonBattleEnv, player: PlayerCharacter) -> BattleAction:
        raise NotImplementedError

    def observe(self, transition: Dict[str, Any]) -> None:
        """
        若之後做 Q-learning，可在這裡接收 (s, a, r, s') 等資訊更新。
        """
        pass


class RandomDungeonAgent(BaseAgent):
    """
    從 player.available_actions(env) 中隨機選一個。
    """

    def select_action(self, env: DungeonBattleEnv, player: PlayerCharacter) -> BattleAction:
        legal_actions = player.available_actions(env)
        if not legal_actions:
            raise RuntimeError("No legal actions for player.")
        return random.choice(legal_actions)


class HeuristicDungeonAgent(BaseAgent):
    """
    簡單規則型 Agent：
    1. 若有隊友血量 < 30% 且有補血技能 → 優先補血
    2. 否則：
       - 若是 Boss 層 → 優先打 FireDragon
       - 非 Boss 層 → 打敵人中血量最低者
    """

    def select_action(self, env: DungeonBattleEnv, player: PlayerCharacter) -> BattleAction:
        # TODO[C]:
        # 1. 從 player.available_actions(env) 拿出所有行動
        # 2. 判斷是否有人 HP% < 0.3 且有 HealingSkill 行動可以選
        # 3. 判斷目前樓層是否 Boss 層（env.floors[env.current_floor_idx].is_boss_floor）
        # 4. 根據規則回傳一個 BattleAction
        raise NotImplementedError


class QLearningDungeonAgent(BaseAgent):
    """
    （選做）Q-learning Agent。
    核心版可以先不實作，由之後有時間再補。
    """

    def __init__(self, epsilon: float = 0.1, alpha: float = 0.1, gamma: float = 0.99):
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.q_table: Dict[Any, Dict[int, float]] = {}

    def _encode_state(self, obs: Dict[str, Any]) -> Any:
        # TODO[Bonus]: 設計簡化版 state（例如：樓層、敵人數量、我方剩餘 HP 百分比）
        raise NotImplementedError

    def _select_action_id(self, state: Any, num_actions: int) -> int:
        # TODO[Bonus]: epsilon-greedy 選擇行動 index
        raise NotImplementedError

    def select_action(self, env: DungeonBattleEnv, player: PlayerCharacter) -> BattleAction:
        # TODO[Bonus]: 使用 Q-table 在 legal_actions 中選一個
        raise NotImplementedError

    def observe(self, transition: Dict[str, Any]) -> None:
        # TODO[Bonus]: Q-learning 更新式
        raise NotImplementedError
