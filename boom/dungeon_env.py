from typing import List, Tuple, Optional
from battle_types import Team, ActionType, BattleAction
from skills import HealingSkill
from characters import Character, PlayerCharacter, EnemyCharacter

class EventLog:
    """封裝戰鬥訊息的紀錄與輸出"""
    def __init__(self):
        self.logs: List[str] = []

    def add(self, message: str):
        self.logs.append(message)
        print(message)  # 同步印出到終端機以便文字版 Demo

    def clear(self):
        self.logs.clear()

class TurnManager:
    """負責管理戰鬥回合順序"""
    @staticmethod
    def get_turn_order(players: List[Character], enemies: List[Character]) -> List[Character]:
        """根據角色 stats.speed 由大到小排序"""
        all_actors = [c for c in players + enemies if c.is_alive()]
        return sorted(all_actors, key=lambda c: c.stats.speed, reverse=True)

class DungeonFloorConfig:
    """每層地城的配置"""
    def __init__(self, name: str, enemy_factory_func, is_boss_floor: bool = False):
        self.name = name
        self.enemy_factory_func = enemy_factory_func
        self.is_boss_floor = is_boss_floor

class DungeonBattleEnv:
    """
    地下城戰鬥環境，負責主要的遊戲規則與狀態管理。
    使用 Composition 模式持有玩家與敵人隊伍 。
    """
    # 修正重點：將 floor_configs 改為 floors，以符合 main.py 的呼叫
    def __init__(self, players: List[PlayerCharacter], floors: List[DungeonFloorConfig]):
        self.players = players
        self.floors = floors # 同步修正屬性名稱
        self.current_floor_idx = 0
        self.enemies: List[EnemyCharacter] = []
        self.event_log = EventLog()
        self.terminated = False
        self.turn_order: List[Character] = []
        
        # 追蹤玩家累計受傷量（用於扣分）
        self.damage_taken_total = 0

    def reset(self, floor_idx: int = 0):
        """重置地城至特定樓層"""
        self.current_floor_idx = floor_idx
        # 這裡也要改用 self.floors
        config = self.floors[floor_idx]
        self.enemies = config.enemy_factory_func()
        self.event_log.clear()
        self.event_log.add(f"--- Entering Floor {floor_idx + 1}: {config.name} ---")
        self.terminated = False
        return self._get_obs()

    def _get_obs(self):
        """回傳當前環境狀態（簡化版）"""
        return {"players": self.players, "enemies": self.enemies}
    
    def render(self):
        """實作 main.py 中呼叫的 render 方法"""
        # 這裡可以根據需求實作 UI 或維持簡易輸出
        pass

    def step(self, player_action: BattleAction) -> Tuple[dict, float, bool, bool, dict]:
        """執行一個完整的回合流程"""
        # 1. 執行玩家(Kiwi)的行動 - 修正變數名稱從 action 改為 player_action
        self._apply_action(player_action)
        
        # 2. 檢查玩家行動後是否結束戰鬥
        if self._check_battle_over():
            obs = self._get_obs()
            reward = 100.0 if any(p.is_alive() for p in self.players) else -50.0
            return obs, reward, True, False, {"msg": "Battle ended early"}

        # 3. 取得所有角色的行動順序
        self.turn_order = TurnManager.get_turn_order(self.players, self.enemies)
        
        for actor in self.turn_order:
            # 跳過剛才已經動過的玩家，並確保角色還活著
            if actor == player_action.actor: continue 
            if not actor.is_alive(): continue
            
            action_other = actor.take_turn(self)
            if action_other:
                self._apply_action(action_other)
                
                # 每個人動完都檢查一次，避免鞭屍或 AI 卡死
                if self._check_battle_over():
                    break 

        terminated = self.terminated
        
        # === 改進分數計算（用於比較算法優劣）===
        dead_enemies = sum(1 for e in self.enemies if not e.is_alive())
        
        # 基礎分數：殺敵獎勵
        reward = dead_enemies * 10.0
        
        # 清關獎勵
        if terminated and any(p.is_alive() for p in self.players):
            reward += 50.0
            # Boss 獎勵
            if any("Dragon" in e.name for e in self.enemies):
                reward += 150.0
            
            # 生存獎勵：每個存活玩家 +20
            alive_players = sum(1 for p in self.players if p.is_alive())
            reward += alive_players * 20.0
        
        # === 受傷扣分：每受到 1 點傷害扣 0.05 分 ===
        reward -= self.damage_taken_total * 0.05
        
        # 失敗懲罰
        if terminated and not any(p.is_alive() for p in self.players):
            reward = -100.0
        
        return self._get_obs(), reward, terminated, False, {"log": self.event_log.logs, "damage_taken": self.damage_taken_total}

    def _apply_action(self, action: BattleAction):
        actor = action.actor
        targets = []
        
        if action.target_ids is not None:
            is_support = False
            if action.action_type == ActionType.USE_SKILL and action.skill:
                is_support = isinstance(action.skill, HealingSkill)
            
            # 修正：直接使用 Team.PLAYERS 列舉進行比較，不要用字串 "players"
            if is_support:
                target_pool = self.players if actor.team == Team.PLAYERS else self.enemies
            else:
                target_pool = self.enemies if actor.team == Team.PLAYERS else self.players
                
            targets = [target_pool[i] for i in action.target_ids if i < len(target_pool)]

        if action.action_type == ActionType.BASIC_ATTACK and targets:
            dmg = targets[0].take_damage(actor.stats.attack)
            self.event_log.add(f"{actor.name} attacked {targets[0].name} for {dmg} damage.")
            # 追蹤玩家受到的傷害
            if targets[0].team == Team.PLAYERS:
                self.damage_taken_total += dmg
        
        elif action.action_type == ActionType.USE_SKILL and action.skill:
            # 利用成員 A 寫的多型 apply
            action.skill.apply(actor, targets, self)
        
        elif action.action_type == ActionType.DEFEND:
            self.event_log.add(f"{actor.name} is defending.")

    def _check_battle_over(self) -> bool:
        """判斷勝利或失敗條件"""
        players_alive = any(p.is_alive() for p in self.players)
        enemies_alive = any(e.is_alive() for e in self.enemies)

        if not players_alive:
            self.event_log.add("Game Over... The party has been wiped out.")
            self.terminated = True
            return True
        if not enemies_alive:
            self.event_log.add("Victory! All enemies defeated.")
            self.terminated = True
            return True
        return False