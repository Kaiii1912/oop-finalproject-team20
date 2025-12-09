from __future__ import annotations
from typing import List

from battle_types import Stats, Team
from characters import PlayerCharacter, EnemyCharacter, FireDragon
from dungeon_env import DungeonFloorConfig
from ai_strategies import RandomAIStrategy, FocusWeakestAIStrategy
from skills import SingleTargetAttackSkill, AreaAttackSkill, HealingSkill


def create_default_players() -> List[PlayerCharacter]:
    """
    建立玩家隊伍（例如 Knight + Priest）。
    """
    # TODO[B/A]:
    # 1. 定義 Knight / Priest 的 Stats
    # 2. 幫他們配上技能：
    #    - Knight: 單體攻擊技
    #    - Priest: HealingSkill
    # 3. 回傳 [knight, priest] 或至少一個主控角色
    raise NotImplementedError


# ------ 敵人工廠：每個函式回傳一個敵人實例 ------

def make_slime() -> EnemyCharacter:
    # TODO[B/A]: 設計 Slime 的 Stats + 技能 + 使用 RandomAIStrategy
    raise NotImplementedError


def make_goblin() -> EnemyCharacter:
    # TODO[B/A]: Goblin 可以攻擊力高一點，使用 RandomAIStrategy 或 FocusWeakestAIStrategy
    raise NotImplementedError


def make_orc_warrior() -> EnemyCharacter:
    # TODO[B/A]: OrcWarrior 偏坦但攻擊也不低，通常集火玩家
    raise NotImplementedError


def make_dark_mage() -> EnemyCharacter:
    # TODO[B/A]: DarkMage 可以給一個範圍攻擊技能，使用 FocusWeakestAIStrategy
    raise NotImplementedError


def make_fire_dragon() -> FireDragon:
    # TODO[B/A/C]:
    # 1. 設定 Dragon Stats（HP 很高、攻擊高）
    # 2. 給單體攻擊技能 + 範圍噴火技能
    # 3. AI 可以先用 Random / FocusWeakest，或留給 FireDragon.decide_action 自己處理
    raise NotImplementedError


def build_dungeon_floors() -> List[DungeonFloorConfig]:
    """
    建立三層地下城：
    B1: Slime Tunnels
    B2: Dark Ritual Hall
    B3: Inferno Dragon's Lair（火龍 Boss）
    """
    # TODO[B]:
    # floor1 = DungeonFloorConfig("B1: Slime Tunnels", [make_slime, make_goblin])
    # floor2 = DungeonFloorConfig("B2: Dark Ritual Hall", [make_orc_warrior, make_dark_mage])
    # floor3 = DungeonFloorConfig("B3: Inferno Dragon's Lair", [make_fire_dragon], is_boss_floor=True)
    # return [floor1, floor2, floor3]
    raise NotImplementedError
