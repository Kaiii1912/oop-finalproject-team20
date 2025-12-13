from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING
import random

from battle_types import Team, Stats, BattleAction, ActionType
from skills import Skill, AreaAttackSkill, SingleTargetAttackSkill, HealingSkill

if TYPE_CHECKING:
    from dungeon_env import DungeonBattleEnv
    from ai_strategies import EnemyAIStrategy
    from agents import BaseAgent

@dataclass
class Character:
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
        return self.base_stats

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, raw_amount: int) -> int:
        if raw_amount <= 0 or not self.is_alive():
            return 0
        dmg = max(1, raw_amount - self.stats.defense)
        self.hp = max(0, self.hp - dmg)
        return dmg

    def heal(self, amount: int) -> int:
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

    # -------- 修正重點：抽象化回合行為 --------
    def take_turn(self, env: "DungeonBattleEnv", agent: Optional["BaseAgent"] = None) -> Optional[BattleAction]:
        """基底類別定義介面，具體邏輯由子類別實作。"""
        raise NotImplementedError("Subclasses must implement take_turn.")

    def available_actions(self, env: "DungeonBattleEnv") -> List[BattleAction]:
        actions = []
        enemies_list = env.enemies if self.team == Team.PLAYERS else env.players
        allies_list = env.players if self.team == Team.PLAYERS else env.enemies

        for idx, target in enumerate(enemies_list):
            if target.is_alive():
                actions.append(BattleAction(self, ActionType.BASIC_ATTACK, [idx], None))

        for skill in self.skills:
            if skill.can_use(self, env):
                valid_targets = skill.get_valid_targets(self, env)
                if not valid_targets: continue
                
                if isinstance(skill, AreaAttackSkill):
                    search_list = enemies_list if self.team == Team.PLAYERS else env.players
                    target_indices = [i for i, original in enumerate(search_list) if any(t is original for t in valid_targets)]
                    if target_indices:
                        actions.append(BattleAction(self, ActionType.USE_SKILL, target_indices, skill))
                else:
                    search_list = allies_list if isinstance(skill, HealingSkill) else enemies_list
                    for t in valid_targets:
                        found_idx = next((i for i, original in enumerate(search_list) if t is original), -1)
                        if found_idx != -1:
                            actions.append(BattleAction(self, ActionType.USE_SKILL, [found_idx], skill))
        return actions

@dataclass
class PlayerCharacter(Character):
    role: str = "Adventurer"
    # 新增：讓隊友可以內建一個簡單的 Agent，避免環境沒傳入時崩潰
    agent: Optional["BaseAgent"] = None

    # 實作玩家回合：使用傳入的 Agent
    def take_turn(self, env: "DungeonBattleEnv", agent: Optional["BaseAgent"] = None) -> Optional[BattleAction]:
        if not self.can_act(): return None

        # 修正：應檢查 active_agent 而非單純檢查傳入的 agent
        active_agent = agent or self.agent

        if active_agent is None:
            raise ValueError(f"Player {self.name} needs an agent to act.")
        
        return active_agent.select_action(env, self)

@dataclass
class EnemyCharacter(Character):
    ai: "EnemyAIStrategy" = field(default=None)

    # 實作敵人回合：呼叫 decide_action
    def take_turn(self, env: "DungeonBattleEnv", agent: Optional["BaseAgent"] = None) -> Optional[BattleAction]:
        if not self.is_alive(): return None
        return self.decide_action(env)

    def decide_action(self, env: "DungeonBattleEnv") -> BattleAction:
        if self.ai:
            return self.ai.choose_action(self, env)
        # 預設行為：若無 AI 策略則發呆，避免 NotImplementedError
        return BattleAction(self, ActionType.PASS)

@dataclass
class FireDragon(EnemyCharacter):
    enraged_threshold: float = 0.3

    def decide_action(self, env: "DungeonBattleEnv") -> BattleAction:
        hp_ratio = self.hp / max(1, self.stats.max_hp)
        area_skills = [s for s in self.skills if isinstance(s, AreaAttackSkill)]
        single_skills = [s for s in self.skills if isinstance(s, SingleTargetAttackSkill)]
        alive_player_indices = [i for i, p in enumerate(env.players) if p.is_alive()]
        
        if not alive_player_indices:
            return BattleAction(self, ActionType.PASS)

        if hp_ratio < self.enraged_threshold:
            for skill in area_skills:
                if skill.can_use(self, env):
                    return BattleAction(self, ActionType.USE_SKILL, alive_player_indices, skill)
        
        if single_skills and random.random() < 0.7:
            skill = random.choice(single_skills)
            if skill.can_use(self, env):
                return BattleAction(self, ActionType.USE_SKILL, [random.choice(alive_player_indices)], skill)

        return BattleAction(self, ActionType.BASIC_ATTACK, [random.choice(alive_player_indices)])