import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt
import pickle

LEARNING_RATE = 0.1          
DISCOUNT_FACTOR = 0.99       

EPSILON_DECAY_RATE = 0.00014  
MIN_EXPLORATION_RATE = 0.001

def print_success_rate(rewards_per_episode):
    total_episodes = len(rewards_per_episode)
    success_count = np.sum(rewards_per_episode)
    success_rate = (success_count / total_episodes) * 100
    print(f"✅ Success Rate: {success_rate:.2f}% ({int(success_count)} / {total_episodes} episodes)")
    return success_rate

def run(episodes, is_training=True, render=False):
    env = gym.make(
        "FrozenLake-v1",
        map_name="8x8",
        is_slippery=True,
        render_mode='human' if render else None
    )

    if is_training:
        q = np.zeros((env.observation_space.n, env.action_space.n)) 
    else:
        with open('frozen_lake8x8.pkl', 'rb') as f:
            q = pickle.load(f)

    learning_rate_a = LEARNING_RATE
    epsilon = 1.0
    rng = np.random.default_rng()

    rewards_per_episode = np.zeros(episodes)

    for i in range(episodes):
        state = env.reset()[0]
        terminated = False
        truncated = False

        while not terminated and not truncated:
            if is_training and rng.random() < epsilon:
                action = env.action_space.sample() 
            else:
                best_actions = np.where(q[state, :] == np.max(q[state, :]))[0]
                action = rng.choice(best_actions)

            new_state, reward, terminated, truncated, _ = env.step(action)

            if is_training:
                q[state, action] = q[state, action] + learning_rate_a * (
                    reward + DISCOUNT_FACTOR * np.max(q[new_state, :]) - q[state, action]
                )

            state = new_state

        if reward == 1:
            rewards_per_episode[i] = 1

        # Epsilon Decay
        if is_training:
            epsilon = max(epsilon - EPSILON_DECAY_RATE, MIN_EXPLORATION_RATE)

    env.close()

    sum_rewards = np.zeros(episodes)
    for t in range(episodes):
        sum_rewards[t] = np.sum(rewards_per_episode[max(0, t - 100):(t + 1)])

    if is_training:
        plt.plot(sum_rewards)
        plt.xlabel("Episodes")
        plt.ylabel("Successes in last 100 episodes")
        plt.title(f"FrozenLake 8x8 (Fixed LR & Tie-Breaking)")
        plt.savefig('frozen_lake8x8.png')
        plt.close()
        
        with open("frozen_lake8x8.pkl", "wb") as f:
            pickle.dump(q, f)
        print(f"Training Finished. Final Epsilon: {epsilon:.4f}")
        
    else:
        print("Evaluation Finished.")
        print_success_rate(rewards_per_episode)

    return q, rewards_per_episode

if __name__ == '__main__':
    print("Starting Training...")
    run(15000, is_training=True, render=False)
    
    print("\nStarting Evaluation...")
    run(800, is_training=False, render=False)