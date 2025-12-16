# OOP group Project team_20

## group member
member1: B123245011 楊鎧榤

member2: B123245007 許珈瑜

member3: B123040015 陳進發

### **Part 1: Mountain Car**
Train and test the reinforcement learning agent:

```bash
# Train the agent
python mountain_car.py --train --episodes 5000

# Render and visualize performance
python mountain_car.py --render --episodes 10
```

### **Part 2: Frozen Lake**
Train a Q-learning agent on the 8x8 Frozen Lake environment and evaluate its performance:

```bash
python frozen_lake.py
```

The script trains for 15,000 episodes, saves the Q-table, then evaluates on 800 episodes and displays the success rate, which ranging from 58% to 65%.

### **Part 3: Kiwi Dungeon RPG**

### 1. Project Overview

**Kiwi Dungeon RPG** is a small 2D, turn-based dungeon crawler built to demonstrate **Object-Oriented Programming (OOP)** concepts rather than game complexity.

- You control a kiwi bird hero and a teammate.
- Fight through **3 dungeon floors**, ending with a **fire dragon boss**.
- Supports **manual control** and **auto-play** via different agents:
  - Random agent
  - Heuristic agent
  - Q-learning–style agent (simplified, inspired by Part 2 FrozenLake)

Key OOP ideas in this project:

- **Encapsulation**:  
  - Combat logic is encapsulated in `Character`, `Skill`, and `DungeonBattleEnv`.
- **Inheritance & Polymorphism**:  
  - `Character` → `PlayerCharacter`, `EnemyCharacter`, `FireDragon`  
  - `Skill` → different concrete skills (single-target, AoE, healing)  
  - `BaseAgent` → `RandomDungeonAgent`, `HeuristicDungeonAgent`, `QLearningDungeonAgent`
- **Strategy Pattern**:  
  - Different AI behaviors for both player agents and enemy AI strategies.
- **Separation of Concerns**:  
  - Core battle logic (`dungeon_env.py`) is separated from the pygame UI (`pygame_app.py`).

---

### 2. How to Run

### 2.1 Text-based demo (console only)

This runs a full B1 → B3 dungeon clear using one chosen agent, printing logs in the terminal.

```bash
python main.py
````

Inside `main.py` you can switch the agent:

```python
# agent = RandomDungeonAgent()
agent = HeuristicDungeonAgent()
# agent = QLearningDungeonAgent()
```

---

### 2.2 Pygame 2D game (recommended, choose this one~)

This starts the full 2D dungeon view with Kiwi, enemies, HP bars, and skill effects.

```bash
python pygame_app.py
```

**Basic controls:**

* **Mouse**

  * Click buttons at the bottom to choose **actions** and **targets** in manual mode.
* **Keyboard** (English keyboard only!!!)

  * `Q` → cycle agent mode

    * Heuristic / Random / Q-Learning
    * Used in **auto-play** mode.
  * `SPACE`

    * On floor clear → go to the **next floor**
    * During play → toggle **manual / auto** control or return from target selection
    * On game over / victory → **restart** the run
  * `ESC` → quit the game

For the in-class demo, we recommend:

1. Start `pygame_app.py`
2. Show manual control for one or two turns.
3. Switch to auto (Heuristic / Random / Q-learning) and let the agent play while you explain the OOP design.

---

### 3. Dependencies

Tested with:

* **Python** 3.10+
* **pygame** 2.x

Install pygame with:

```bash
pip install pygame
```

No external RL frameworks (e.g., Stable Baselines, gymnasium) are required.
The Q-learning agent is implemented with pure Python and dictionaries.

---

## 4. Contribution List

> Replace `Member A/B/C` with your real names/student IDs.

* **Member 1 – 楊鎧榤**

  * code -> branch c
  * report
  * slides
  * UML diagrams

* **Member 2 – 許珈瑜**

  * code -> branch a
  * report
  * slides

* **Member 3 – 陳進發**

  * code -> branch b
  * report
  * slides
