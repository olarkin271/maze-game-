# Maze Game with Q-Learning AI Agent

A maze game implementation featuring a Q-learning AI agent that learns to navigate through a maze, collect coins, avoid an NPC enemy, and reach the exit to maximize its score.

## Features

- **Dynamic Maze Generation**: Randomly generated mazes with walls and obstacles
- **Q-Learning AI Agent**: Reinforcement learning agent that learns optimal strategies
- **NPC Enemy**: Chasing enemy that tries to catch the player
- **Coin Collection**: Collectible coins that increase the score
- **Exit Goal**: Agent must reach the exit to win
- **Visualization**: PyGame-based visualization to watch the agent play
- **Training Analytics**: Plots showing learning progress over time

## Game Objectives

The AI agent has three competing objectives:
1. **Reach the exit** - Find the way out of the maze (large reward)
2. **Collect coins** - Maximize score by collecting coins (medium reward)
3. **Avoid the NPC** - Don't get caught by the chasing enemy (large penalty)

The agent learns to balance these objectives through trial and error using Q-learning.

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Requirements:
- Python 3.7+
- numpy
- pygame
- matplotlib

## Usage

### 1. Train the Agent

Train the Q-learning agent for a specified number of episodes:

```bash
# Basic training (5000 episodes)
python train.py

# Custom training parameters
python train.py --episodes 10000 --maze-height 12 --maze-width 12 --coins 7

# See all options
python train.py --help
```

Training parameters:
- `--episodes`: Number of training episodes (default: 5000)
- `--maze-height`: Height of the maze (default: 10)
- `--maze-width`: Width of the maze (default: 10)
- `--coins`: Number of coins in the maze (default: 5)
- `--model-path`: Path to save the trained model (default: trained_agent.pkl)
- `--save-interval`: Save model every N episodes (default: 500)

The training script will:
- Train the agent for the specified number of episodes
- Print progress every 100 episodes
- Save the model periodically and at the end
- Generate training plots showing:
  - Episode rewards over time
  - Steps per episode
  - Win rate
  - Score per episode

Training plots are saved as `training_results.png`.

### 2. Watch the Trained Agent Play

Watch the trained agent play the game with visualization:

```bash
# Watch the agent play one game
python play.py --mode agent

# Watch multiple games
python play.py --mode agent --games 5

# Adjust speed (delay between steps in seconds)
python play.py --mode agent --delay 0.1

# See all options
python play.py --help
```

Agent play parameters:
- `--mode`: Play mode (agent or manual)
- `--model-path`: Path to trained model (default: trained_agent.pkl)
- `--maze-height`: Maze height (default: 10)
- `--maze-width`: Maze width (default: 10)
- `--coins`: Number of coins (default: 5)
- `--delay`: Delay between steps in seconds (default: 0.2)
- `--games`: Number of games to play (default: 1)

Controls during visualization:
- **SPACE**: Play another game
- **ESC**: Quit
- **Close window**: Quit

### 3. Play Manually

You can also play the game yourself:

```bash
python play.py --mode manual
```

Manual play controls:
- **Arrow keys**: Move the player
- **R**: Restart the game
- **ESC**: Quit

## Game Elements

### Visual Representation

- **Blue circle**: AI Agent (player)
- **Red circle**: NPC Enemy (chaser)
- **Yellow circles**: Coins
- **Green square**: Exit
- **Black squares**: Walls
- **White squares**: Empty walkable space

### Scoring

- Collecting a coin: **+10 points**
- Reaching the exit: **+100 points**
- Getting caught by NPC: **-50 points**
- Each step taken: **-0.1 points** (encourages efficiency)
- Timeout (max steps): **-10 points**

## How Q-Learning Works

The agent uses Q-learning, a reinforcement learning algorithm that learns the optimal action-value function Q(s, a), which represents the expected reward for taking action 'a' in state 's'.

### Algorithm Details

- **State representation**: Position of player, relative position of NPC, relative position of exit, relative position of nearest coin, number of coins remaining
- **Actions**: Up, Down, Left, Right (4 actions)
- **Learning rate (α)**: 0.1 - How much new information overrides old
- **Discount factor (γ)**: 0.95 - Importance of future rewards
- **Epsilon-greedy exploration**: Starts at 1.0 (100% random), decays to 0.01 (1% random)

### Learning Process

1. **Exploration phase** (early episodes): Agent explores randomly to discover the environment
2. **Exploitation phase** (later episodes): Agent uses learned Q-values to make optimal decisions
3. **Convergence**: As training progresses, the agent's performance stabilizes

### Q-Update Rule

```
Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]
```

Where:
- Q(s,a): Current Q-value for state s and action a
- α: Learning rate
- r: Reward received
- γ: Discount factor
- max(Q(s',a')): Maximum Q-value for next state s'

## Project Structure

```
maze-game/
├── maze_game.py          # Game environment implementation
├── q_learning_agent.py   # Q-learning agent implementation
├── train.py              # Training script
├── play.py               # Visualization and play script
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── trained_agent.pkl    # Saved trained model (after training)
└── training_results.png # Training plots (after training)
```

## Training Tips

1. **Start small**: Train on smaller mazes (8x8) first to see faster results
2. **Increase episodes**: More episodes generally lead to better performance (try 10,000+)
3. **Adjust difficulty**: Increase maze size or number of coins for more challenge
4. **Monitor progress**: Watch the training plots to see if the agent is learning
5. **Expected results**:
   - Early episodes: Random behavior, low win rate
   - Mid training: Agent starts avoiding NPC and finding exit
   - Late training: Agent efficiently collects coins and reaches exit

## Expected Performance

After 5000 episodes of training on a 10x10 maze:
- **Win rate**: 60-80%
- **Average steps**: 50-100 steps
- **Average score**: 30-60 points

Performance improves with more training episodes!

## Troubleshooting

### Model not found error
If you see "Model file 'trained_agent.pkl' not found", you need to train the agent first:
```bash
python train.py
```

### Agent performs poorly
Try training for more episodes:
```bash
python train.py --episodes 10000
```

### Pygame window issues
Make sure pygame is properly installed:
```bash
pip install --upgrade pygame
```

## Future Improvements

Potential enhancements:
- Multiple NPCs with different behaviors
- Power-ups (speed boost, temporary invincibility)
- Different maze generation algorithms
- Deep Q-Learning (DQN) with neural networks
- More complex reward shaping
- Multiplayer mode

## License

This project is open source and available for educational purposes.

## Acknowledgments

This project demonstrates reinforcement learning concepts using Q-learning, a fundamental algorithm in the field of AI and machine learning.
