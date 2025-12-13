from __future__ import annotations
from battle_types import ActionType
from abc import ABC, abstractmethod
from typing import Dict, Any, TYPE_CHECKING
import random

from battle_types import BattleAction
from dungeon_env import DungeonBattleEnv
from characters import PlayerCharacter

if TYPE_CHECKING:
    from skills import HealingSkill


class BaseAgent(ABC):
    """
    控制「玩家」行動的 Agent 介面。
    """

    @abstractmethod
    def select_action(self, env: DungeonBattleEnv, player: PlayerCharacter) -> BattleAction:
        raise NotImplementedError

    def observe(self, transition: Dict[str, Any]) -> None:
        pass


class RandomDungeonAgent(BaseAgent):
    """
    從 player.available_actions(env) 中隨機選一個。
    """

    def select_action(self, env: DungeonBattleEnv, player: PlayerCharacter) -> BattleAction:
        legal_actions = player.available_actions(env)
        if not legal_actions:
            raise RuntimeError("No legal actions for player.")
        return random.choice(legal_actions)


class HeuristicDungeonAgent(BaseAgent):
    """
    簡單規則型 Agent：
    1. 若有隊友血量 < 30% 且有補血技能 → 優先補血
    2. 否則：
       - 若是 Boss 層 → 優先打 FireDragon
       - 非 Boss 層 → 打敵人中血量最低者
    """

    def select_action(self, env: DungeonBattleEnv, player: PlayerCharacter) -> BattleAction:
        legal_actions = player.available_actions(env)
        if not legal_actions:
             return legal_actions[0] if legal_actions else None

        # 1. 檢查補血
        # <OOP Concept>: Polymorphism via Duck Typing / Type Checking
        # 我們檢查 skill 是否為 HealingSkill 的實例來決定策略
        from skills import HealingSkill 
        low_hp_allies = [p for p in env.players if p.is_alive() and (p.hp / p.stats.max_hp < 0.3)]
        if low_hp_allies:
            heal_acts = []
            for act in legal_actions:
                if act.skill and isinstance(act.skill, HealingSkill):
                    if act.target_ids and env.players[act.target_ids[0]] in low_hp_allies:
                        heal_acts.append(act)
            if heal_acts:
                return heal_acts[0] 

        # 2. Boss 優先
        floor = env.floors[env.current_floor_idx]
        if floor.is_boss_floor:
            # 簡化假設：Boss 在敵人列表 index 0
            boss_acts = [a for a in legal_actions if a.target_ids and a.target_ids[0] == 0 and a.action_type in (ActionType.BASIC_ATTACK, ActionType.USE_SKILL)]
            skill_hits = [a for a in boss_acts if a.action_type == ActionType.USE_SKILL]
            if skill_hits: return skill_hits[0]
            if boss_acts: return boss_acts[0]

        # 3. 打最弱 (Kill fast)
        alive_enemy_objs = [e for e in env.enemies if e.is_alive()]
        
        if alive_enemy_objs:
            # Find the actual object with the lowest HP
            weakest_enemy = min(alive_enemy_objs, key=lambda e: e.hp)
            # Find its index in the original environment list to create the action
            w_idx = env.enemies.index(weakest_enemy)
            
            target_acts = [a for a in legal_actions if a.target_ids and a.target_ids[0] == w_idx]
            if target_acts:
                # Prioritize using a skill if available against the weakest target
                skill_hits = [a for a in target_acts if a.action_type == ActionType.USE_SKILL]
                if skill_hits: return skill_hits[0]
                return target_acts[0]

        if not alive_enemies:
            return BattleAction(actor=actor, action_type=ActionType.PASS)
            
        # 正常選一個血最少的敵人攻擊
        target_idx = env.enemies.index(min(alive_enemy_objs, key=lambda e: e.hp))

        return random.choice(legal_actions)


class QLearningDungeonAgent(BaseAgent):
    """
    Q-learning Agent。
    
    # <OOP Concept>: Encapsulation
    # 將 Q-Table、參數 (epsilon, alpha) 以及學習邏輯全部封裝在這個類別內。
    # 外界不需要知道它內部是如何學習的，只需要呼叫 select_action 和 observe。
    """

    def __init__(self, epsilon: float = 0.1, alpha: float = 0.1, gamma: float = 0.9):
        self.epsilon = epsilon  # 探索率
        self.alpha = alpha      # 學習率
        self.gamma = gamma      # 折扣因子
        
        # Q-Table 結構：Dict[State, Dict[ActionKey, Q_Value]]
        # State 是一個 tuple，ActionKey 是一個字串
        self.q_table: Dict[Tuple, Dict[str, float]] = {}
        
        # 紀錄上一步的狀態與行動，用於 observe 更新
        self.last_state: Optional[Tuple] = None
        self.last_action_key: Optional[str] = None

    def _encode_state(self, env: DungeonBattleEnv, player: PlayerCharacter) -> Tuple:
        """
        將複雜的遊戲環境轉換為簡化的 State Tuple。
        這是一個特徵工程 (Feature Engineering) 的過程。
        """
        # 1. 目前樓層 (0, 1, 2)
        floor_idx = env.current_floor_idx
        
        # 2. 玩家 HP 狀態 (切成 4 個等級: 0=死, 1=危險, 2=普通, 3=健康)
        hp_ratio = player.hp / player.stats.max_hp
        if hp_ratio == 0: hp_bucket = 0
        elif hp_ratio < 0.3: hp_bucket = 1
        elif hp_ratio < 0.7: hp_bucket = 2
        else: hp_bucket = 3
        
        # 3. MP 足夠放技能嗎？ (簡單二分法：夠放任意技能 vs 乾了)
        # 假設最便宜技能 5mp
        mp_status = 1 if player.mp >= 5 else 0
        
        # 4. 敵人存活數量
        alive_enemies = len([e for e in env.enemies if e.is_alive()])
        
        # 5. 是否為 Boss 關且 Boss 活著
        is_boss_alive = 0
        if env.floors[floor_idx].is_boss_floor:
            # 假設 Boss 是最後一個加入 factory 的或是有特定名字，這裡簡單判斷是否有 "Dragon"
            if any("Dragon" in e.name and e.is_alive() for e in env.enemies):
                is_boss_alive = 1

        return (floor_idx, hp_bucket, mp_status, alive_enemies, is_boss_alive)

    def _get_action_key(self, action: BattleAction) -> str:
        """
        將 BattleAction 物件轉換為可作為 Dictionary Key 的字串。
        我們忽略具體的 target_id，將行動抽象化，以減少 Q-Table 大小。
        """
        if action.action_type == ActionType.BASIC_ATTACK:
            return "ATTACK"
        elif action.action_type == ActionType.DEFEND:
            return "DEFEND"
        elif action.action_type == ActionType.USE_SKILL:
            # 區分不同技能，因為不同技能耗魔與效果不同
            skill_name = action.skill.name if action.skill else "UNKNOWN"
            return f"SKILL_{skill_name}"
        else:
            return "PASS"

    def select_action(self, env: DungeonBattleEnv, player: PlayerCharacter) -> BattleAction:
        # 1. 取得目前狀態
        state = self._encode_state(env, player)
        self.last_state = state # 記住這個狀態
        
        legal_actions = player.available_actions(env)
        if not legal_actions:
             # 例外處理
             return BattleAction(actor=player, action_type=ActionType.PASS)

        # 2. Epsilon-Greedy 策略
        # 探索 (Explore)：隨機選
        if random.random() < self.epsilon:
            chosen_action = random.choice(legal_actions)
            self.last_action_key = self._get_action_key(chosen_action)
            return chosen_action

        # 利用 (Exploit)：選 Q 值最高的
        # 確保 Q-table 裡有這個 state
        if state not in self.q_table:
            self.q_table[state] = {}

        best_q = -float('inf')
        best_actions = []

        for action in legal_actions:
            act_key = self._get_action_key(action)
            
            # 如果這個動作在這個狀態下還沒遇過，給予預設值 (例如 0.0)
            q_val = self.q_table[state].get(act_key, 0.0)
            
            if q_val > best_q:
                best_q = q_val
                best_actions = [action]
            elif q_val == best_q:
                best_actions.append(action)
        
        # 如果有多個 Q 值一樣好的動作，隨機選一個
        chosen_action = random.choice(best_actions)
        self.last_action_key = self._get_action_key(chosen_action)
        
        return chosen_action

    def observe(self, transition: Dict[str, Any]) -> None:
        """
        接收環境回饋並更新 Q-Table。
        transition 應包含: {'reward': float, 'next_state_env': env, 'next_player': player, 'terminated': bool}
        注意：為了計算 next_state，我們需要 env 和 player 物件。
        """
        reward = transition.get("reward", 0.0)
        terminated = transition.get("terminated", False)
        
        # 檢查是否有上一步的紀錄 (如果是第一回合則沒有)
        if self.last_state is None or self.last_action_key is None:
            return

        # 取得 Next State 的 Q 值
        if terminated:
            max_next_q = 0.0
        else:
            # 我們需要由 transition 傳進來的環境物件來計算下一個 state
            # 假設 transition 裡有 env 和 player
            env = transition.get("env")
            player = transition.get("player")
            
            if env and player:
                next_state = self._encode_state(env, player)
                if next_state not in self.q_table:
                    self.q_table[next_state] = {}
                
                # 找出 next_state 中所有可能動作的最大 Q 值
                # 這裡做一個簡化：直接找 table 裡紀錄過的 max，而不重新呼叫 available_actions (效能考量)
                # 若 table 裡沒紀錄，max 就是 0
                if self.q_table[next_state]:
                    max_next_q = max(self.q_table[next_state].values())
                else:
                    max_next_q = 0.0
            else:
                max_next_q = 0.0

        # Bellman Equation 更新
        # Q(s, a) = Q(s, a) + alpha * [reward + gamma * max(Q(s', a')) - Q(s, a)]
        
        current_q_map = self.q_table[self.last_state]
        old_q = current_q_map.get(self.last_action_key, 0.0)
        
        new_q = old_q + self.alpha * (reward + self.gamma * max_next_q - old_q)
        
        # 寫回 Table
        current_q_map[self.last_action_key] = new_q