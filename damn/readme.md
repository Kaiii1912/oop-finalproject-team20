# Dungeon RPG — 三層地下城與噴火龍 Boss（OOP Showcase）

這個專案是一個 **回合制 RPG 地下城戰鬥系統**。  
玩家操控小隊從 B1 打到 B3，最終挑戰噴火龍 Boss。

專案重點不是畫面有多華麗，而是：

> 用一個 **可實際跑的戰鬥流程**，清楚展示物件導向程式設計（OOP）概念：  
> 封裝（Encapsulation）、繼承（Inheritance）、多型（Polymorphism），  
> 再配合策略模式（Strategy Pattern）、Template Method 等設計想法。

---

## 🎯 專案目標

- 實作一個簡單但完整的 **三層地下城 + 最終 Boss** 戰鬥系統。
- 在程式架構中展示：
  - Encapsulation：數值計算、回合流程、Agent 決策都封裝在各自類別中。
  - Inheritance：角色、技能、AI 策略都透過繼承擴充。
  - Polymorphism：相同介面下，不同子類有不同行為（例如不同 Agent / AI）。
  - Strategy Pattern：敵方 AI (`EnemyAIStrategy`)、玩家 Agent (`BaseAgent`)。
  - Template Method：`Character.take_turn()` 固定流程，細節交給子類與 Agent。

---

## 📂 專案結構

```text
dungeon_rpg/
├─ battle_types.py      # 共用型別：Team, Stats, ActionType, BattleAction
├─ skills.py            # 技能系統：Skill 抽象類別 + 攻擊 / 補血技能
├─ characters.py        # 角色系統：Character / PlayerCharacter / EnemyCharacter / FireDragon
├─ ai_strategies.py     # 敵人 AI：EnemyAIStrategy + Random / FocusWeakest
├─ dungeon_env.py       # 地城戰鬥環境：DungeonBattleEnv + TurnManager + EventLog
├─ config_dungeon.py    # 關卡與數值設定：玩家隊伍 + 三層樓敵人 factory
├─ agents.py            # 玩家 Agent：BaseAgent + Random / Heuristic (+ Q-learning 預留)
└─ main.py              # 入口：run_dungeon() + main()
