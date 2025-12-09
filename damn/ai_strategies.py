from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import random

from battle_types import BattleAction, ActionType

if TYPE_CHECKING:
    from characters import EnemyCharacter
    from dungeon_env import DungeonBattleEnv


class EnemyAIStrategy(ABC):
    """
    敵人 AI 策略介面（Strategy Pattern）
    """

    @abstractmethod
    def choose_action(self, enemy: "EnemyCharacter", env: "DungeonBattleEnv") -> BattleAction:
        raise NotImplementedError


class RandomAIStrategy(EnemyAIStrategy):
    """
    亂打型怪物：從 available_actions 裡隨機選。
    """

    def choose_action(self, enemy: "EnemyCharacter", env: "DungeonBattleEnv") -> BattleAction:
        # TODO[C]: 呼叫 enemy.available_actions(env) 後 random.choice(...)
        raise NotImplementedError


class FocusWeakestAIStrategy(EnemyAIStrategy):
    """
    集火血量最低玩家。
    """

    def choose_action(self, enemy: "EnemyCharacter", env: "DungeonBattleEnv") -> BattleAction:
        # TODO[C]:
        # 1. 找出 env.players 中 hp > 0 且 hp 最低者的 index
        # 2. 建立一個 BASIC_ATTACK 的 BattleAction 指向該 target
        raise NotImplementedError
