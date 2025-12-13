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
        possible_actions = enemy.available_actions(env)
        if not possible_actions:
            return BattleAction(actor=enemy, action_type=ActionType.PASS)
        return random.choice(possible_actions)


class FocusWeakestAIStrategy(EnemyAIStrategy):
    """
    集火血量最低玩家。
    """

    def choose_action(self, enemy: "EnemyCharacter", env: "DungeonBattleEnv") -> BattleAction:
        alive_players = [p for p in env.players if p.is_alive()]
        
        if not alive_players:
            return BattleAction(actor=enemy, action_type=ActionType.PASS)

        # 找出 HP 絕對值最低的目標
        target = min(alive_players, key=lambda p: p.hp)
        target_idx = env.players.index(target)

        return BattleAction(
            actor=enemy, 
            action_type=ActionType.BASIC_ATTACK, 
            target_ids=[target_idx]
        )
