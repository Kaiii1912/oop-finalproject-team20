from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Sequence, Union, TYPE_CHECKING

# 引入 Team 以便判斷敵我
from battle_types import Team

if TYPE_CHECKING:
    from characters import Character
    from dungeon_env import DungeonBattleEnv


class Skill(ABC):
    """
    技能基底類別。
    """

    def __init__(self, name: str, mp_cost: int):
        self.name = name
        self.mp_cost = mp_cost

    def can_use(self, user: "Character", env: "DungeonBattleEnv") -> bool: #確認魔力是否足夠
        return user.is_alive() and user.mp >= self.mp_cost

    @abstractmethod
    def get_valid_targets(self, user: "Character", env: "DungeonBattleEnv") -> List["Character"]:
        """
        回傳此技能可選的合法目標清單。
        """
        raise NotImplementedError

    def apply(
        self,
        user: "Character",
        targets: Union["Character", Sequence["Character"]],
        env: "DungeonBattleEnv",
    ) -> None:
        """
        Template Method: 處理耗魔與目標轉換，具體效果交給 _apply_impl。
        """
        if isinstance(targets, Sequence) and not isinstance(targets, (str, bytes)):
            target_list = list(targets)
        else:
            target_list = [targets]
        
        # 扣除 MP
        user.spend_mp(self.mp_cost)
        
        # 執行實作
        self._apply_impl(user, target_list, env)

    @abstractmethod
    def _apply_impl(self, user: "Character", targets: List["Character"], env: "DungeonBattleEnv") -> None:
        raise NotImplementedError


class SingleTargetAttackSkill(Skill):
    """
    單體攻擊技能
    """

    def __init__(self, name: str, mp_cost: int, power: int):
        super().__init__(name, mp_cost)
        self.power = power

    def get_valid_targets(self, user: "Character", env: "DungeonBattleEnv") -> List["Character"]:
        # 攻擊敵方陣營中存活的角色
        targets_pool = env.enemies if user.team == Team.PLAYERS else env.players
        return [c for c in targets_pool if c.is_alive()]

    def _apply_impl(self, user: "Character", targets: List["Character"], env: "DungeonBattleEnv") -> None:
        if not targets:
            return
        target = targets[0]
        
        # 傷害公式：(User攻擊 + 技能威力) - Target防禦 (防禦扣減在 take_damage 內處理)
        raw_damage = user.stats.attack + self.power
        actual_dmg = target.take_damage(raw_damage)
        
        print(f"[{self.name}] {user.name} hits {target.name} for {actual_dmg} dmg.")


class AreaAttackSkill(Skill):
    """
    範圍攻擊技能
    """

    def __init__(self, name: str, mp_cost: int, power: int):
        super().__init__(name, mp_cost)
        self.power = power

    def get_valid_targets(self, user: "Character", env: "DungeonBattleEnv") -> List["Character"]:
        # 攻擊敵方全體存活角色
        targets_pool = env.enemies if user.team == Team.PLAYERS else env.players
        return [c for c in targets_pool if c.is_alive()]

    def _apply_impl(self, user: "Character", targets: List["Character"], env: "DungeonBattleEnv") -> None:
        print(f"[{self.name}] {user.name} casts broad attack!")
        for target in targets:
            raw_damage = user.stats.attack + self.power
            actual_dmg = target.take_damage(raw_damage)
            print(f"  -> {target.name} took {actual_dmg} damage.")


class HealingSkill(Skill):
    """
    單體補血技能
    """

    def __init__(self, name: str, mp_cost: int, heal_power: int):
        super().__init__(name, mp_cost)
        self.heal_power = heal_power

    def get_valid_targets(self, user: "Character", env: "DungeonBattleEnv") -> List["Character"]:
        # 補血針對己方陣營，且只補活著且血沒滿的人
        targets_pool = env.players if user.team == Team.PLAYERS else env.enemies
        return [c for c in targets_pool if c.is_alive() and c.hp < c.stats.max_hp]

    def _apply_impl(self, user: "Character", targets: List["Character"], env: "DungeonBattleEnv") -> None:
        if not targets:
            return
        target = targets[0]
        actual_healed = target.heal(self.heal_power)
        print(f"[{self.name}] {user.name} heals {target.name} for {actual_healed} HP.")