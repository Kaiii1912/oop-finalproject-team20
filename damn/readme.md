# Kiwi Dungeon RPG — 三層地下城與噴火龍 Boss（OOP + Gym-style + pygame）

這個專案是一個 **單機 2D 地下城 RPG 戰鬥系統**：

- 主角是一隻奇異鳥 Kiwi（玩家隊伍第一個角色）。
- 共有 **三層地下城**，最後一層是噴火龍 Boss。
- 有「純文字回合制版」與「pygame 2D 介面版」兩種 Demo 模式。
- 重點是展示 **物件導向設計（OOP）** 與 **自訂環境 + Agent 結構**，不是畫面多華麗或訓練多強。

---

## 🎯 專案目標（對應作業要求）

- 設計一個自訂的 **Dungeon Battle Environment**，介面類似 Gym：
  - `reset(floor_idx)`
  - `step(player_action)`
  - `render()`
- 實作 **Agent 類別** 控制玩家行動：
  - `BaseAgent` 介面
  - `RandomDungeonAgent`、`HeuristicDungeonAgent`、（選做）`QLearningDungeonAgent`
- 強調 OOP 概念：
  - Encapsulation：角色數值、技能效果、環境邏輯、AI 決策各自封裝在 class 裡。
  - Inheritance：
    - `Character` → `PlayerCharacter / EnemyCharacter / FireDragon`
    - `Skill` → `SingleTargetAttackSkill / AreaAttackSkill / HealingSkill`
    - `EnemyAIStrategy` → `RandomAIStrategy / FocusWeakestAIStrategy`
    - `BaseAgent` → `RandomDungeonAgent / HeuristicDungeonAgent / QLearningDungeonAgent`
  - Polymorphism：
    - 同樣呼叫 `skill.apply(user, targets, env)`，實際效果依技能子類不同。
    - 同樣呼叫 `agent.select_action(env, player)`，不同 Agent 會做出不同策略。
    - 敵人呼叫 `enemy.ai.choose_action(enemy, env)`，不同 AI 策略有不同行為。
- 額外加值：
  - 使用 **pygame** 製作一個簡單的 2D 地下城介面作為 Demo 視覺化層。

---

## 📂 檔案結構

```text
dungeon_rpg/
├─ battle_types.py      # 共用型別：Team, Stats, ActionType, BattleAction
├─ skills.py            # 技能系統：Skill 抽象類別 + 攻擊 / 補血技能
├─ characters.py        # 角色系統：Character / PlayerCharacter / EnemyCharacter / FireDragon
├─ ai_strategies.py     # 敵人 AI：EnemyAIStrategy + Random / FocusWeakest
├─ dungeon_env.py       # 地城戰鬥環境：DungeonBattleEnv + TurnManager + EventLog
├─ config_dungeon.py    # 關卡與數值設定：玩家隊伍 + 三層樓敵人 factory
├─ agents.py            # 玩家 Agent：BaseAgent + Random / Heuristic (+ Q-learning 預留)
├─ main.py              # 純文字版本：run_dungeon(env, agent) + main()
└─ pygame_app.py        # pygame 2D 介面：DungeonPygameApp（自動操作 Kiwi 的 Demo）
