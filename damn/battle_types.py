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
    actor: "Character"
    action_type: ActionType
    target_ids: Optional[List[int]] = None  # 存的是 env.players 或 env.enemies 的 index
    skill: Optional["Skill"] = None