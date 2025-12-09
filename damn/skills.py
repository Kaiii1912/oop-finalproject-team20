from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Sequence, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from characters import Character
    from dungeon_env import DungeonBattleEnv


class Skill(ABC):
    """
    技能基底類別。

    展示：
    - 繼承：各種攻擊/補血技能繼承自 Skill
    - 多型：呼叫 skill.apply(...) 時，根據子類型做出不同效果。
    """

    def __init__(self, name: str, mp_cost: int):
        self.name = name
        self.mp_cost = mp_cost

    def can_use(self, user: "Character", env: "DungeonBattleEnv") -> bool:
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
        類似 overloading：可以接受單一 target 或 List[target]。
        """
        if isinstance(targets, Sequence) and not isinstance(targets, (str, bytes)):
            target_list = list(targets)
        else:
            target_list = [targets]
        self._apply_impl(user, target_list, env)

    @abstractmethod
    def _apply_impl(self, user: "Character", targets: List["Character"], env: "DungeonBattleEnv") -> None:
        raise NotImplementedError


class SingleTargetAttackSkill(Skill):
    """
    單體攻擊技能（例如：Heavy Slash）
    """

    def __init__(self, name: str, mp_cost: int, power: int):
        super().__init__(name, mp_cost)
        self.power = power

    def get_valid_targets(self, user: "Character", env: "DungeonBattleEnv") -> List["Character"]:
        # TODO[A]: 回傳「敵方陣營中存活角色」列表
        raise NotImplementedError

    def _apply_impl(self, user: "Character", targets: List["Character"], env: "DungeonBattleEnv") -> None:
        # TODO[A]: 對 targets[0] 計算傷害並呼叫 target.take_damage(...)
        #          可考慮使用 user.stats.attack + self.power 等公式
        raise NotImplementedError


class AreaAttackSkill(Skill):
    """
    範圍攻擊技能（例如：Fireball，打敵方全體）
    """

    def __init__(self, name: str, mp_cost: int, power: int):
        super().__init__(name, mp_cost)
        self.power = power

    def get_valid_targets(self, user: "Character", env: "DungeonBattleEnv") -> List["Character"]:
        # TODO[A]: 回傳敵方全體存活角色
        raise NotImplementedError

    def _apply_impl(self, user: "Character", targets: List["Character"], env: "DungeonBattleEnv") -> None:
        # TODO[A]: 對每個 target 呼叫 take_damage(...)
        raise NotImplementedError


class HealingSkill(Skill):
    """
    單體補血技能（例如：Heal）
    """

    def __init__(self, name: str, mp_cost: int, heal_power: int):
        super().__init__(name, mp_cost)
        self.heal_power = heal_power

    def get_valid_targets(self, user: "Character", env: "DungeonBattleEnv") -> List["Character"]:
        # TODO[A]: 回傳己方陣營中「血量未滿」的角色
        raise NotImplementedError

    def _apply_impl(self, user: "Character", targets: List["Character"], env: "DungeonBattleEnv") -> None:
        # TODO[A]: 對每個 target 呼叫 heal(...)
        raise NotImplementedError
