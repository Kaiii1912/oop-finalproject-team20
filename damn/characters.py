from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

from battle_types import Team, Stats, BattleAction, ActionType

if TYPE_CHECKING:
    from dungeon_env import DungeonBattleEnv
    from skills import Skill
    from ai_strategies import EnemyAIStrategy
    from agents import BaseAgent


@dataclass
class Character:
    """
    玩家 / 敵人共同基底類別。

    展示：
    - 繼承：PlayerCharacter / EnemyCharacter / FireDragon
    - 封裝：HP/MP 操作、傷害計算、行動選擇
    """
    name: str
    team: Team
    base_stats: Stats
    skills: List["Skill"] = field(default_factory=list)

    hp: int = field(init=False)
    mp: int = field(init=False)

    def __post_init__(self) -> None:
        self.hp = self.base_stats.max_hp
        self.mp = self.base_stats.max_mp

    @property
    def stats(self) -> Stats:
        """
        核心版：直接回傳 base_stats。
        之後要加裝備系統，可以在這裡套裝備加成。
        """
        return self.base_stats

    # -------- 生命 / 魔力 相關 --------

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, raw_amount: int) -> int:
        """
        受到傷害，回傳實際扣血量。
        """
        if raw_amount <= 0 or not self.is_alive():
            return 0
        dmg = max(1, raw_amount - self.stats.defense)
        self.hp = max(0, self.hp - dmg)
        return dmg

    def heal(self, amount: int) -> int:
        """
        補血，回傳實際回復量。
        """
        if amount <= 0 or not self.is_alive():
            return 0
        old = self.hp
        self.hp = min(self.stats.max_hp, self.hp + amount)
        return self.hp - old

    def spend_mp(self, cost: int) -> bool:
        if self.mp < cost:
            return False
        self.mp -= cost
        return True

    def can_act(self) -> bool:
        return self.is_alive()

    # -------- 回合流程（Template Method）--------

    def take_turn(self, env: "DungeonBattleEnv", agent: Optional["BaseAgent"] = None) -> Optional[BattleAction]:
        """
        一個完整回合：
        - 玩家：交給 Agent 決定
        - 敵人：交給自身的 AI 決定
        """
        if not self.can_act():
            return None

        if self.team == Team.PLAYERS:
            if agent is None:
                raise ValueError("PlayerCharacter needs an agent to act.")
            action = agent.select_action(env, self)  # BaseAgent 由 agents.py 定義
        else:
            # 交給子類 (EnemyCharacter / FireDragon) 實作
            action = self.decide_action(env)

        return action

    # -------- 可用行動列表（讓 Agent / AI 使用）--------

    def available_actions(self, env: "DungeonBattleEnv") -> List[BattleAction]:
        """
        TODO[A]:
        由這裡根據當前狀況，產生一組合法的 BattleAction：
        - BASIC_ATTACK：對每個敵人產生一個可選目標
        - USE_SKILL：對每個技能與合法目標組合產生行動
        - DEFEND / PASS：可以各自做成一個動作
        具體如何編 target_ids，可以跟組員協調。
        """
        raise NotImplementedError

    # -------- 敵人 AI 用：預設不實作（交給子類）--------

    def decide_action(self, env: "DungeonBattleEnv") -> BattleAction:
        raise NotImplementedError("Enemy types should override decide_action().")


@dataclass
class PlayerCharacter(Character):
    """
    玩家角色。
    """
    role: str = "Adventurer"


@dataclass
class EnemyCharacter(Character):
    """
    敵人角色，持有一個 AI Strategy。
    """
    ai: "EnemyAIStrategy" = field(default=None)

    def decide_action(self, env: "DungeonBattleEnv") -> BattleAction:
        return self.ai.choose_action(self, env)


@dataclass
class FireDragon(EnemyCharacter):
    """
    最終 Boss：噴火龍。
    核心版：直接在 decide_action 中用血量比例決定招式。
    之後可以再抽成 DragonPhase state pattern。
    """

    enraged_threshold: float = 0.3  # HP 低於 30% 進入狂暴模式

    def decide_action(self, env: "DungeonBattleEnv") -> BattleAction:
        hp_ratio = self.hp / max(1, self.stats.max_hp)
        # TODO[A/C]: 在這裡決定火龍在「正常 / 狂暴」狀態下要用的技能
        # 例如：
        # if hp_ratio < self.enraged_threshold:
        #     -> 使用範圍攻擊技能（噴火）
        # else:
        #     -> 使用單體攻擊或普通攻擊
        raise NotImplementedError
