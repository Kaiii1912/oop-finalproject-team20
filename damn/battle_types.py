from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from characters import Character
    from skills import Skill


class Team(Enum):
    PLAYERS = "players"
    ENEMIES = "enemies"


@dataclass
class Stats:
    """
    角色基本數值。
    TODO[A]: 如需可在此擴充 critical / evade 等欄位。
    """
    max_hp: int
    max_mp: int
    attack: int
    defense: int
    speed: int


class ActionType(Enum):
    BASIC_ATTACK = auto()
    USE_SKILL = auto()
    DEFEND = auto()
    PASS = auto()


@dataclass
class BattleAction:
    """
    一個「行動」物件：誰(actor) 做了什麼(action_type) 對誰(target_ids)，
    如果是技能則附帶 skill。
    """
    actor: "Character"
    action_type: ActionType
    target_ids: Optional[List[int]] = None  # 例如 env.players 或 env.enemies 的 index
    skill: Optional["Skill"] = None
