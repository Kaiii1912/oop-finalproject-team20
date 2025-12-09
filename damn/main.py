from __future__ import annotations

from dungeon_env import DungeonBattleEnv
from config_dungeon import create_default_players, build_dungeon_floors
from agents import RandomDungeonAgent, HeuristicDungeonAgent  # 或 QLearningDungeonAgent


def run_dungeon(env: DungeonBattleEnv, agent) -> float:
    """
    從 B1 打到 B3 的完整挑戰流程。
    """
    total_reward = 0.0

    for floor_idx in range(len(env.floors)):
        obs = env.reset(floor_idx)
        terminated = False
        truncated = False

        while not (terminated or truncated):
            player = env.players[0]  # 先假設主控第一個玩家
            action = agent.select_action(env, player)
            next_obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            obs = next_obs
            env.render()

    return total_reward


def main() -> None:
    players = create_default_players()
    floors = build_dungeon_floors()
    env = DungeonBattleEnv(floors=floors, players=players)

    # Demo 時可以自由切換不同 Agent，看多型效果
    # agent = RandomDungeonAgent()
    agent = HeuristicDungeonAgent()
    # agent = QLearningDungeonAgent()  # Bonus 時再用

    total_reward = run_dungeon(env, agent)
    print("\nTotal reward:", total_reward)


if __name__ == "__main__":
    main()
