from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING
import random

from battle_types import Team, Stats, BattleAction, ActionType
# 為了在 available_actions 裡判斷技能種類，需要引入技能類別
from skills import Skill, AreaAttackSkill, SingleTargetAttackSkill, HealingSkill

if TYPE_CHECKING:
    from dungeon_env import DungeonBattleEnv
    from ai_strategies import EnemyAIStrategy
    from agents import BaseAgent


@dataclass
class Character:
    """
    玩家 / 敵人共同基底類別。
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
        return self.base_stats

    # -------- 生命 / 魔力 相關 --------

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

    # -------- 回合流程（Template Method）--------

    def take_turn(self, env: "DungeonBattleEnv", agent: Optional["BaseAgent"] = None) -> Optional[BattleAction]:
        if not self.can_act():
            return None

        if self.team == Team.PLAYERS:
            # 玩家交給外部 Agent
            if agent is None:
                raise ValueError("PlayerCharacter needs an agent to act.")
            action = agent.select_action(env, self)
        else:
            # 敵人交給自身的 decide_action (AI)
            action = self.decide_action(env)

        return action

    # --------行動列表--------

    def available_actions(self, env: "DungeonBattleEnv") -> List[BattleAction]:
        """
        列出當前所有合法行動，供 Random/Heuristic Agent 選擇。
        需將「物件目標」轉換回「Index 列表」。
        """
        actions = []
        
        # 定義敵我列表
        enemies_list = env.enemies if self.team == Team.PLAYERS else env.players
        allies_list = env.players if self.team == Team.PLAYERS else env.enemies

        # 1. 普通攻擊 (BASIC_ATTACK)
        # 對每一個活著的敵人產生一個選項
        for idx, target in enumerate(enemies_list):
            if target.is_alive():
                actions.append(BattleAction(
                    actor=self,
                    action_type=ActionType.BASIC_ATTACK,
                    target_ids=[idx],
                    skill=None
                ))

        # 2. 使用技能 (USE_SKILL)
        for skill in self.skills:
            if skill.can_use(self, env):
                # 取得該技能合法的目標物件
                valid_targets = skill.get_valid_targets(self, env)
                if not valid_targets:
                    continue
                
                # 根據技能類型分裝 Action
                
                # A. 範圍攻擊 (Action 只會有一個，目標是所有符合的人)
                if isinstance(skill, AreaAttackSkill):
                    target_indices = []
                    # 範圍技通常打敵方，去 enemies_list 找對應的 index
                    search_list = enemies_list if self.team == Team.PLAYERS else env.players
                    
                    for t in valid_targets:
                        for i, original in enumerate(search_list):
                            if t is original:
                                target_indices.append(i)
                                break
                    
                    if target_indices:
                        actions.append(BattleAction(
                            actor=self,
                            action_type=ActionType.USE_SKILL,
                            target_ids=target_indices,
                            skill=skill
                        ))

                # B. 單體 / 補血 (對每個合法目標產生一個 Action)
                else:
                    # 決定去哪個列表找 index
                    if isinstance(skill, HealingSkill):
                        search_list = allies_list
                    else:
                        search_list = enemies_list
                    
                    for t in valid_targets:
                        found_idx = -1
                        for i, original in enumerate(search_list):
                            if t is original:
                                found_idx = i
                                break
                        
                        if found_idx != -1:
                            actions.append(BattleAction(
                                actor=self,
                                action_type=ActionType.USE_SKILL,
                                target_ids=[found_idx],
                                skill=skill
                            ))

        return actions

    # -------- 敵人 AI 用 --------

    def decide_action(self, env: "DungeonBattleEnv") -> BattleAction:
        raise NotImplementedError("Enemy types should override decide_action().")


@dataclass
class PlayerCharacter(Character):
    role: str = "Adventurer"


@dataclass
class EnemyCharacter(Character):
    ai: "EnemyAIStrategy" = field(default=None)

    def decide_action(self, env: "DungeonBattleEnv") -> BattleAction:
        # 一般小怪：委託給 Strategy (由成員 C 寫的 Strategy Pattern)
        if self.ai:
            return self.ai.choose_action(self, env)
        return BattleAction(self, ActionType.PASS)


@dataclass
class FireDragon(EnemyCharacter):
    """
    最終 Boss：噴火龍。
    """
    enraged_threshold: float = 0.3

    def decide_action(self, env: "DungeonBattleEnv") -> BattleAction:
        # 計算血量比例
        hp_ratio = self.hp / max(1, self.stats.max_hp)
        
        # 分類技能
        area_skills = [s for s in self.skills if isinstance(s, AreaAttackSkill)]
        single_skills = [s for s in self.skills if isinstance(s, SingleTargetAttackSkill)]
        
        # 找活著的玩家
        alive_player_indices = [i for i, p in enumerate(env.players) if p.is_alive()]
        if not alive_player_indices:
            return BattleAction(self, ActionType.PASS)

        # 1. 狂暴模式：HP < 30% 且有 MP，強制用範圍技
        if hp_ratio < self.enraged_threshold:
            for skill in area_skills:
                if skill.can_use(self, env):
                    print(f"*** {self.name} is ENRAGED! ROAR! ***")
                    return BattleAction(
                        actor=self,
                        action_type=ActionType.USE_SKILL,
                        target_ids=alive_player_indices,
                        skill=skill
                    )
        
        # 2. 正常模式：有 70% 機率使用單體技能 (如果有魔)
        if single_skills and random.random() < 0.7:
            skill = random.choice(single_skills)
            if skill.can_use(self, env):
                target_idx = random.choice(alive_player_indices)
                return BattleAction(
                    actor=self,
                    action_type=ActionType.USE_SKILL,
                    target_ids=[target_idx],
                    skill=skill
                )

        # 3. 沒魔或隨機到普攻
        target_idx = random.choice(alive_player_indices)
        return BattleAction(
            actor=self,
            action_type=ActionType.BASIC_ATTACK,
            target_ids=[target_idx]
        )