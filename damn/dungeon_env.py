from typing import List, Tuple, Optional
from battle_types import Team, ActionType, BattleAction
from characters import Character, PlayerCharacter, EnemyCharacter

class EventLog:
    """封裝戰鬥訊息的紀錄與輸出 [cite: 89-90]"""
    def __init__(self):
        self.logs: List[str] = []

    def add(self, message: str):
        self.logs.append(message)
        print(message)  # 同步印出到終端機以便文字版 Demo [cite: 115]

    def clear(self):
        self.logs.clear()

class TurnManager:
    """負責管理戰鬥回合順序 [cite: 85]"""
    @staticmethod
    def get_turn_order(players: List[Character], enemies: List[Character]) -> List[Character]:
        """根據角色 stats.speed 由大到小排序 [cite: 86, 155]"""
        all_actors = [c for c in players + enemies if c.is_alive()]
        return sorted(all_actors, key=lambda c: c.stats.speed, reverse=True)

class DungeonFloorConfig:
    """每層地城的配置 [cite: 87]"""
    def __init__(self, name: str, enemy_factory_func, is_boss_floor: bool = False):
        self.name = name
        self.enemy_factory_func = enemy_factory_func
        self.is_boss_floor = is_boss_floor

class DungeonBattleEnv:
    """
    地下城戰鬥環境，負責主要的遊戲規則與狀態管理 [cite: 78, 174]。
    使用 Composition 模式持有玩家與敵人隊伍 。
    """
    def __init__(self, players: List[PlayerCharacter], floor_configs: List[DungeonFloorConfig]):
        self.players = players
        self.floor_configs = floor_configs
        self.current_floor_idx = 0
        self.enemies: List[EnemyCharacter] = []
        self.event_log = EventLog()
        self.terminated = False
        self.turn_order: List[Character] = []

    def reset(self, floor_idx: int = 0):
        """重置地城至特定樓層 [cite: 79]"""
        self.current_floor_idx = floor_idx
        config = self.floor_configs[floor_idx]
        self.enemies = config.enemy_factory_func()
        self.event_log.clear()
        self.event_log.add(f"--- Entering Floor {floor_idx + 1}: {config.name} ---")
        self.terminated = False
        return self._get_obs()

    def _get_obs(self):
        """回傳當前環境狀態（簡化版） [cite: 84]"""
        return {"players": self.players, "enemies": self.enemies}

    def step(self, player_action: BattleAction) -> Tuple[dict, float, bool, bool, dict]:
        """執行一個完整的回合流程 [cite: 79, 156]"""
        if self.terminated:
            return self._get_obs(), 0, True, False, {}

        self.turn_order = TurnManager.get_turn_order(self.players, self.enemies)
        
        for actor in self.turn_order:
            if not actor.is_alive():
                continue

            # 執行行動
            if actor.team == Team.PLAYERS:
                # 這裡假設 step 是由 Kiwi 觸發，如果是隊友則可擴充 Agent 邏輯 [cite: 158]
                action = player_action if actor.name == "Kiwi" else actor.take_turn(self, None) 
            else:
                action = actor.take_turn(self) # 敵人 AI 決定行動 [cite: 159]

            if action:
                self._apply_action(action)

            # 每次行動後檢查勝負
            if self._check_battle_over():
                break

        reward = 1.0 if not any(not e.is_alive() for e in self.enemies) else 0.0
        return self._get_obs(), reward, self.terminated, False, {"log": self.event_log.logs}

    def _apply_action(self, action: BattleAction):
        """根據 ActionType 處理普攻、技能、防禦等邏輯 [cite: 162-163]"""
        actor = action.actor
        targets = []
        
        # 解析目標 Index 到物件
        if action.target_ids is not None:
            target_pool = self.enemies if actor.team == Team.PLAYERS else self.players
            targets = [target_pool[i] for i in action.target_ids if i < len(target_pool)]

        if action.action_type == ActionType.BASIC_ATTACK and targets:
            dmg = targets[0].take_damage(actor.stats.attack)
            self.event_log.add(f"{actor.name} attacked {targets[0].name} for {dmg} damage.")
        
        elif action.action_type == ActionType.USE_SKILL and action.skill:
            # 利用成員 A 寫的多型 apply [cite: 208]
            action.skill.apply(actor, targets, self)
            # 技能內部的 print 會顯示效果
        
        elif action.action_type == ActionType.DEFEND:
            self.event_log.add(f"{actor.name} is defending.")

    def _check_battle_over(self) -> bool:
        """判斷勝利或失敗條件 [cite: 83, 161]"""
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