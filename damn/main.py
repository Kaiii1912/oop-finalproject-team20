from __future__ import annotations

from dungeon_env import DungeonBattleEnv
from config_dungeon import create_default_players, build_dungeon_floors
from agents import RandomDungeonAgent, HeuristicDungeonAgent, QLearningDungeonAgent


def run_dungeon(env: DungeonBattleEnv, agent) -> float:
    total_reward = 0.0
    
    # 訓練參數 (如果是 QLearningAgent)
    is_rl_agent = hasattr(agent, "q_table")

    for floor_idx in range(len(env.floors)):
        obs = env.reset(floor_idx)
        terminated = False
        truncated = False

        while not (terminated or truncated):
            player = env.players[0]
            
            # 1. 選擇行動
            action = agent.select_action(env, player)
            
            # 2. 執行行動
            next_obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            
            # 3. [RL Only] 讓 Agent 學習
            # 我們需要把新的環境狀態傳給 observe
            if is_rl_agent:
                transition = {
                    "reward": reward,
                    "terminated": terminated,
                    "env": env,      # 傳入 env 以計算 next_state
                    "player": player # 傳入 player 以計算 next_state
                }
                agent.observe(transition)

            obs = next_obs
            env.render()
        
        if not any(p.is_alive() for p in env.players):
            break

    return total_reward


def main() -> None:
    players = create_default_players()
    floors = build_dungeon_floors()
    env = DungeonBattleEnv(floors=floors, players=players)

    # Demo 時可以自由切換不同 Agent，看多型效果，有三種模式，然後Qlearn是模仿part2的簡易版
    # agent = RandomDungeonAgent()
    agent = HeuristicDungeonAgent()
    # agent = QLearningDungeonAgent()  # Bonus 時再用
    
    total_reward = run_dungeon(env, agent)
    print("\nTotal reward:", total_reward)


if __name__ == "__main__":
    main()
