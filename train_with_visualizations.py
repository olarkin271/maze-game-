#!/usr/bin/env python3
"""
Training script with comprehensive visualizations
Generates plots and heatmaps of Q-learning performance
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from maze_game import MazeGame
from q_learning_agent import QLearningAgent
import argparse
import os
from collections import defaultdict

def train_with_visualization(num_episodes: int = 2000,
                             maze_size: tuple = (12, 12),
                             num_coins: int = 5,
                             model_path: str = "trained_agent.pkl"):
    """
    Train the Q-learning agent and generate comprehensive visualizations
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
    scores = []
    epsilon_values = []
    q_table_sizes = []

    # Track Q-value evolution for specific states
    q_value_evolution = defaultdict(list)
    sample_states = []

    # Track win rate over windows
    window_size = 100
    win_rates = []
    avg_rewards = []
    avg_steps_list = []

    print(f"Starting training for {num_episodes} episodes...")
    print(f"Maze size: {maze_size}, Coins: {num_coins}")
    print("-" * 80)

    for episode in range(num_episodes):
        state_dict = env.reset()
        state = env.get_state_representation()
        total_reward = 0
        done = False
        steps = 0

        # Track first state of episode for Q-value evolution
        if episode % 100 == 0 and episode < 500:
            sample_states.append(state)

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
        epsilon_values.append(agent.epsilon)
        q_table_sizes.append(len(agent.q_table))

        if state_dict['won']:
            wins.append(1)
        else:
            wins.append(0)

        # Track Q-values for sample states
        for sample_state in sample_states:
            if sample_state in agent.q_table:
                max_q = np.max(agent.q_table[sample_state])
                q_value_evolution[sample_state].append(max_q)

        # Calculate moving averages
        if episode >= window_size:
            win_rate = np.sum(wins[-window_size:]) / window_size * 100
            avg_reward = np.mean(episode_rewards[-window_size:])
            avg_steps = np.mean(episode_steps[-window_size:])
            win_rates.append(win_rate)
            avg_rewards.append(avg_reward)
            avg_steps_list.append(avg_steps)
        else:
            win_rates.append(np.sum(wins) / (episode + 1) * 100)
            avg_rewards.append(np.mean(episode_rewards))
            avg_steps_list.append(np.mean(episode_steps))

        # Print progress
        if (episode + 1) % 100 == 0:
            print(f"Episode {episode + 1}/{num_episodes} | "
                  f"Win Rate: {win_rates[-1]:.1f}% | "
                  f"Avg Reward: {avg_rewards[-1]:.2f} | "
                  f"Avg Steps: {avg_steps_list[-1]:.1f} | "
                  f"Epsilon: {agent.epsilon:.4f} | "
                  f"Q-Table: {q_table_sizes[-1]} states")

    # Save final model
    agent.save(model_path)

    print("\n" + "=" * 80)
    print("Training completed!")
    print("=" * 80)
    print(f"Generating visualizations...")

    # Generate all visualizations
    generate_all_plots(
        episode_rewards, episode_steps, wins, scores, epsilon_values,
        q_table_sizes, win_rates, avg_rewards, avg_steps_list,
        q_value_evolution, agent, env, num_episodes
    )

    print("\n" + "=" * 80)
    print("Final Statistics:")
    print("=" * 80)
    print(f"Total episodes: {num_episodes}")
    print(f"Final epsilon: {agent.epsilon:.4f}")
    print(f"Q-table size: {len(agent.q_table)} states")
    print(f"Final win rate (last 100): {win_rates[-1]:.1f}%")
    print(f"Final avg reward (last 100): {avg_rewards[-1]:.2f}")
    print(f"Final avg steps (last 100): {avg_steps_list[-1]:.1f}")
    print(f"Best win rate: {max(win_rates):.1f}%")


def generate_all_plots(episode_rewards, episode_steps, wins, scores, epsilon_values,
                       q_table_sizes, win_rates, avg_rewards, avg_steps_list,
                       q_value_evolution, agent, env, num_episodes):
    """Generate comprehensive visualizations"""

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.facecolor'] = 'white'

    # Create output directory
    os.makedirs('visualizations', exist_ok=True)

    # 1. Main Training Dashboard (4 subplots)
    print("Generating main training dashboard...")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Q-Learning Training Dashboard', fontsize=16, fontweight='bold')

    # Plot 1: Win Rate
    ax = axes[0, 0]
    ax.plot(win_rates, linewidth=2, color='#2ecc71')
    ax.fill_between(range(len(win_rates)), win_rates, alpha=0.3, color='#2ecc71')
    ax.set_xlabel('Episode', fontsize=12)
    ax.set_ylabel('Win Rate (%)', fontsize=12)
    ax.set_title('Win Rate Over Episodes (100-episode moving average)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 100])

    # Plot 2: Average Reward
    ax = axes[0, 1]
    ax.plot(avg_rewards, linewidth=2, color='#3498db')
    ax.fill_between(range(len(avg_rewards)), avg_rewards, alpha=0.3, color='#3498db')
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Zero reward')
    ax.set_xlabel('Episode', fontsize=12)
    ax.set_ylabel('Average Reward', fontsize=12)
    ax.set_title('Average Reward Over Episodes (100-episode moving average)', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 3: Q-Table Growth & Epsilon
    ax = axes[1, 0]
    ax2 = ax.twinx()

    line1 = ax.plot(q_table_sizes, linewidth=2, color='#9b59b6', label='Q-Table Size')
    ax.set_xlabel('Episode', fontsize=12)
    ax.set_ylabel('Q-Table Size (states)', fontsize=12, color='#9b59b6')
    ax.tick_params(axis='y', labelcolor='#9b59b6')

    line2 = ax2.plot(epsilon_values, linewidth=2, color='#e74c3c', label='Epsilon')
    ax2.set_ylabel('Epsilon (exploration rate)', fontsize=12, color='#e74c3c')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc='upper left')
    ax.set_title('Learning Progress: Q-Table Growth & Exploration', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Plot 4: Average Steps per Episode
    ax = axes[1, 1]
    ax.plot(avg_steps_list, linewidth=2, color='#f39c12')
    ax.fill_between(range(len(avg_steps_list)), avg_steps_list, alpha=0.3, color='#f39c12')
    ax.axhline(y=env.max_steps, color='red', linestyle='--', alpha=0.5, label='Max steps (timeout)')
    ax.set_xlabel('Episode', fontsize=12)
    ax.set_ylabel('Average Steps', fontsize=12)
    ax.set_title('Average Steps per Episode (100-episode moving average)', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('visualizations/training_dashboard.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: visualizations/training_dashboard.png")
    plt.close()

    # 2. Q-Value Evolution Plot
    if q_value_evolution:
        print("Generating Q-value evolution plot...")
        plt.figure(figsize=(14, 8))

        for i, (state, values) in enumerate(list(q_value_evolution.items())[:5]):
            if values:
                plt.plot(range(0, len(values) * 100, 100), values,
                        linewidth=2, marker='o', markersize=4,
                        label=f'Sample State {i+1}', alpha=0.8)

        plt.xlabel('Episode', fontsize=12)
        plt.ylabel('Max Q-Value', fontsize=12)
        plt.title('Q-Value Evolution for Sample States', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('visualizations/q_value_evolution.png', dpi=300, bbox_inches='tight')
        print("  ✓ Saved: visualizations/q_value_evolution.png")
        plt.close()

    # 3. Q-Value Heatmap for Starting Position
    print("Generating Q-value heatmap...")
    generate_q_value_heatmap(agent, env)

    # 4. Performance Distribution
    print("Generating performance distribution...")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Reward distribution
    axes[0].hist(episode_rewards, bins=50, color='#3498db', alpha=0.7, edgecolor='black')
    axes[0].axvline(np.mean(episode_rewards), color='red', linestyle='--',
                   linewidth=2, label=f'Mean: {np.mean(episode_rewards):.1f}')
    axes[0].set_xlabel('Episode Reward', fontsize=12)
    axes[0].set_ylabel('Frequency', fontsize=12)
    axes[0].set_title('Reward Distribution', fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Steps distribution
    axes[1].hist(episode_steps, bins=50, color='#f39c12', alpha=0.7, edgecolor='black')
    axes[1].axvline(np.mean(episode_steps), color='red', linestyle='--',
                   linewidth=2, label=f'Mean: {np.mean(episode_steps):.1f}')
    axes[1].set_xlabel('Steps per Episode', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].set_title('Steps Distribution', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    # Score distribution
    axes[2].hist(scores, bins=50, color='#2ecc71', alpha=0.7, edgecolor='black')
    axes[2].axvline(np.mean(scores), color='red', linestyle='--',
                   linewidth=2, label=f'Mean: {np.mean(scores):.1f}')
    axes[2].set_xlabel('Score', fontsize=12)
    axes[2].set_ylabel('Frequency', fontsize=12)
    axes[2].set_title('Score Distribution', fontsize=14, fontweight='bold')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('visualizations/performance_distributions.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: visualizations/performance_distributions.png")
    plt.close()

    # 5. Learning Phases Analysis
    print("Generating learning phases analysis...")
    phase_size = num_episodes // 4
    phases = ['Early\n(0-25%)', 'Mid-Early\n(25-50%)', 'Mid-Late\n(50-75%)', 'Late\n(75-100%)']

    phase_win_rates = []
    phase_avg_rewards = []
    phase_avg_scores = []

    for i in range(4):
        start_idx = i * phase_size
        end_idx = (i + 1) * phase_size
        phase_win_rates.append(np.mean(wins[start_idx:end_idx]) * 100)
        phase_avg_rewards.append(np.mean(episode_rewards[start_idx:end_idx]))
        phase_avg_scores.append(np.mean(scores[start_idx:end_idx]))

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Win rate by phase
    axes[0].bar(phases, phase_win_rates, color=['#e74c3c', '#e67e22', '#f39c12', '#2ecc71'],
               alpha=0.8, edgecolor='black', linewidth=2)
    axes[0].set_ylabel('Win Rate (%)', fontsize=12)
    axes[0].set_title('Win Rate by Learning Phase', fontsize=14, fontweight='bold')
    axes[0].set_ylim([0, 100])
    axes[0].grid(True, alpha=0.3, axis='y')

    # Average reward by phase
    axes[1].bar(phases, phase_avg_rewards, color=['#e74c3c', '#e67e22', '#f39c12', '#2ecc71'],
               alpha=0.8, edgecolor='black', linewidth=2)
    axes[1].set_ylabel('Average Reward', fontsize=12)
    axes[1].set_title('Average Reward by Learning Phase', fontsize=14, fontweight='bold')
    axes[1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    axes[1].grid(True, alpha=0.3, axis='y')

    # Average score by phase
    axes[2].bar(phases, phase_avg_scores, color=['#e74c3c', '#e67e22', '#f39c12', '#2ecc71'],
               alpha=0.8, edgecolor='black', linewidth=2)
    axes[2].set_ylabel('Average Score', fontsize=12)
    axes[2].set_title('Average Score by Learning Phase', fontsize=14, fontweight='bold')
    axes[2].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('visualizations/learning_phases.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: visualizations/learning_phases.png")
    plt.close()

    print("\n✓ All visualizations generated successfully!")
    print("\nGenerated files:")
    print("  - visualizations/training_dashboard.png (Main overview)")
    print("  - visualizations/q_value_heatmap.png (Q-value heatmap)")
    print("  - visualizations/q_value_evolution.png (Q-value over time)")
    print("  - visualizations/performance_distributions.png (Statistical distributions)")
    print("  - visualizations/learning_phases.png (Phase comparison)")


def generate_q_value_heatmap(agent, env):
    """Generate heatmap of Q-values for the maze"""

    # Create a grid to store max Q-values
    q_grid = np.zeros((env.height, env.width))
    visit_grid = np.zeros((env.height, env.width))

    # Iterate through Q-table and extract position-based Q-values
    for state, q_values in agent.q_table.items():
        try:
            # Parse state (assuming it's a JSON string with player_pos)
            import json
            state_dict = json.loads(state)
            player_pos = state_dict.get('player', (0, 0))

            if isinstance(player_pos, (list, tuple)) and len(player_pos) == 2:
                row, col = player_pos
                if 0 <= row < env.height and 0 <= col < env.width:
                    max_q = np.max(q_values)
                    # Average Q-values for the same position
                    q_grid[row, col] += max_q
                    visit_grid[row, col] += 1
        except:
            continue

    # Average the Q-values
    mask = visit_grid > 0
    q_grid[mask] = q_grid[mask] / visit_grid[mask]

    # Create the heatmap
    fig, ax = plt.subplots(figsize=(12, 10))

    # Mask walls
    maze_copy = env.maze.copy()
    q_grid_masked = np.ma.masked_where(maze_copy == MazeGame.WALL, q_grid)

    # Create heatmap
    im = ax.imshow(q_grid_masked, cmap='RdYlGn', interpolation='nearest', aspect='equal')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Max Q-Value', fontsize=12, fontweight='bold')

    # Mark special positions
    # Start position
    ax.scatter(1, 1, s=300, c='blue', marker='o', edgecolors='white', linewidth=3,
              label='Start', zorder=5)

    # Exit position
    ax.scatter(env.exit_pos[1], env.exit_pos[0], s=300, c='gold', marker='*',
              edgecolors='white', linewidth=3, label='Exit', zorder=5)

    # Add grid
    ax.set_xticks(np.arange(-0.5, env.width, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, env.height, 1), minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)

    # Labels
    ax.set_xlabel('Column', fontsize=12)
    ax.set_ylabel('Row', fontsize=12)
    ax.set_title('Q-Value Heatmap: Learned State Values\n(Darker green = Higher expected reward)',
                fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)

    # Add text annotations for high-value states
    for i in range(env.height):
        for j in range(env.width):
            if visit_grid[i, j] > 0 and maze_copy[i, j] != MazeGame.WALL:
                value = q_grid[i, j]
                if abs(value) > 10:  # Only show significant values
                    ax.text(j, i, f'{value:.0f}', ha='center', va='center',
                           fontsize=8, color='black', fontweight='bold')

    plt.tight_layout()
    plt.savefig('visualizations/q_value_heatmap.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: visualizations/q_value_heatmap.png")
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train Q-learning agent with visualizations')
    parser.add_argument('--episodes', type=int, default=2000,
                        help='Number of episodes to train (default: 2000)')
    parser.add_argument('--maze-height', type=int, default=12,
                        help='Maze height (default: 12)')
    parser.add_argument('--maze-width', type=int, default=12,
                        help='Maze width (default: 12)')
    parser.add_argument('--coins', type=int, default=5,
                        help='Number of coins (default: 5)')
    parser.add_argument('--model-path', type=str, default='trained_agent.pkl',
                        help='Path to save trained model (default: trained_agent.pkl)')

    args = parser.parse_args()

    train_with_visualization(
        num_episodes=args.episodes,
        maze_size=(args.maze_height, args.maze_width),
        num_coins=args.coins,
        model_path=args.model_path
    )
