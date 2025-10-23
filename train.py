#!/usr/bin/env python3
"""
Training script for Q-learning agent in the maze game
"""

import numpy as np
import matplotlib.pyplot as plt
from maze_game import MazeGame
from q_learning_agent import QLearningAgent
import argparse
import os

def train(num_episodes: int = 5000,
          maze_size: tuple = (10, 10),
          num_coins: int = 5,
          save_interval: int = 500,
          model_path: str = "trained_agent.pkl"):
    """
    Train the Q-learning agent

    Args:
        num_episodes: Number of episodes to train
        maze_size: Size of the maze (height, width)
        num_coins: Number of coins in the maze
        save_interval: Save model every N episodes
        model_path: Path to save the trained model
    """
    # Initialize environment and agent
    env = MazeGame(maze_size=maze_size, num_coins=num_coins)
    agent = QLearningAgent(
        n_actions=4,
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=1.0,
        epsilon_min=0.01,
        epsilon_decay=0.995
    )

    # Training statistics
    episode_rewards = []
    episode_steps = []
    wins = []
    losses = []
    scores = []
    moving_avg_window = 100

    print(f"Starting training for {num_episodes} episodes...")
    print(f"Maze size: {maze_size}, Coins: {num_coins}")
    print("-" * 60)

    for episode in range(num_episodes):
        state_dict = env.reset()
        state = env.get_state_representation()
        total_reward = 0
        done = False
        steps = 0

        while not done:
            # Choose action
            action = agent.get_action(state, training=True)

            # Take action
            next_state_dict, reward, done = env.step(action)
            next_state = env.get_state_representation()

            # Update Q-table
            agent.update(state, action, reward, next_state, done)

            total_reward += reward
            state = next_state
            steps += 1

        # Decay epsilon
        agent.decay_epsilon()

        # Record statistics
        episode_rewards.append(total_reward)
        episode_steps.append(steps)
        scores.append(state_dict['score'])

        if state_dict['won']:
            wins.append(1)
            losses.append(0)
        else:
            wins.append(0)
            losses.append(1)

        # Print progress
        if (episode + 1) % 100 == 0:
            avg_reward = np.mean(episode_rewards[-100:])
            avg_steps = np.mean(episode_steps[-100:])
            avg_score = np.mean(scores[-100:])
            win_rate = np.sum(wins[-100:]) / 100
            print(f"Episode {episode + 1}/{num_episodes} | "
                  f"Avg Reward: {avg_reward:.2f} | "
                  f"Avg Steps: {avg_steps:.1f} | "
                  f"Avg Score: {avg_score:.1f} | "
                  f"Win Rate: {win_rate:.2%} | "
                  f"Epsilon: {agent.epsilon:.4f}")

        # Save model periodically
        if (episode + 1) % save_interval == 0:
            agent.save(model_path)

    # Save final model
    agent.save(model_path)

    # Plot training results
    plot_training_results(episode_rewards, episode_steps, wins, scores, moving_avg_window)

    # Print final statistics
    print("\n" + "=" * 60)
    print("Training completed!")
    print("=" * 60)
    print(f"Total episodes: {num_episodes}")
    print(f"Final epsilon: {agent.epsilon:.4f}")
    print(f"Q-table size: {len(agent.q_table)} states")
    print(f"Average reward (last 100): {np.mean(episode_rewards[-100:]):.2f}")
    print(f"Average steps (last 100): {np.mean(episode_steps[-100:]):.1f}")
    print(f"Average score (last 100): {np.mean(scores[-100:]):.1f}")
    print(f"Win rate (last 100): {np.sum(wins[-100:]):.0f}%")

def plot_training_results(rewards, steps, wins, scores, window=100):
    """Plot training statistics"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    # Moving average
    def moving_average(data, window):
        return np.convolve(data, np.ones(window)/window, mode='valid')

    # Plot 1: Episode Rewards
    axes[0, 0].plot(rewards, alpha=0.3, label='Raw')
    if len(rewards) >= window:
        axes[0, 0].plot(moving_average(rewards, window), label=f'{window}-episode MA')
    axes[0, 0].set_xlabel('Episode')
    axes[0, 0].set_ylabel('Total Reward')
    axes[0, 0].set_title('Episode Rewards')
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    # Plot 2: Episode Steps
    axes[0, 1].plot(steps, alpha=0.3, label='Raw')
    if len(steps) >= window:
        axes[0, 1].plot(moving_average(steps, window), label=f'{window}-episode MA')
    axes[0, 1].set_xlabel('Episode')
    axes[0, 1].set_ylabel('Steps')
    axes[0, 1].set_title('Steps per Episode')
    axes[0, 1].legend()
    axes[0, 1].grid(True)

    # Plot 3: Win Rate
    win_rate = [np.mean(wins[max(0, i-window):i+1]) * 100 for i in range(len(wins))]
    axes[1, 0].plot(win_rate)
    axes[1, 0].set_xlabel('Episode')
    axes[1, 0].set_ylabel('Win Rate (%)')
    axes[1, 0].set_title(f'Win Rate (moving average, window={window})')
    axes[1, 0].grid(True)

    # Plot 4: Scores
    axes[1, 1].plot(scores, alpha=0.3, label='Raw')
    if len(scores) >= window:
        axes[1, 1].plot(moving_average(scores, window), label=f'{window}-episode MA')
    axes[1, 1].set_xlabel('Episode')
    axes[1, 1].set_ylabel('Score')
    axes[1, 1].set_title('Score per Episode')
    axes[1, 1].legend()
    axes[1, 1].grid(True)

    plt.tight_layout()
    plt.savefig('training_results.png', dpi=150)
    print("\nTraining plots saved to 'training_results.png'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train Q-learning agent for maze game')
    parser.add_argument('--episodes', type=int, default=5000,
                        help='Number of episodes to train (default: 5000)')
    parser.add_argument('--maze-height', type=int, default=10,
                        help='Maze height (default: 10)')
    parser.add_argument('--maze-width', type=int, default=10,
                        help='Maze width (default: 10)')
    parser.add_argument('--coins', type=int, default=5,
                        help='Number of coins (default: 5)')
    parser.add_argument('--model-path', type=str, default='trained_agent.pkl',
                        help='Path to save trained model (default: trained_agent.pkl)')
    parser.add_argument('--save-interval', type=int, default=500,
                        help='Save model every N episodes (default: 500)')

    args = parser.parse_args()

    train(
        num_episodes=args.episodes,
        maze_size=(args.maze_height, args.maze_width),
        num_coins=args.coins,
        save_interval=args.save_interval,
        model_path=args.model_path
    )
