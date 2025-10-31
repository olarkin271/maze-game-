# Visualization Guide

## How to Generate Training Visualizations

### Quick Start

```bash
# Install dependencies (including seaborn for visualizations)
pip install -r requirements.txt

# Train agent and generate all visualizations
python train_with_visualizations.py --episodes 2000
```

This will:
1. Train the agent for 2000 episodes
2. Track all performance metrics
3. Generate 5 comprehensive visualization files
4. Save them in the `visualizations/` folder

---

## Generated Visualizations

### 1. **training_dashboard.png** - Main Overview

![Training Dashboard Preview](visualizations/training_dashboard.png)

**Contains 4 plots:**

#### Top Left: Win Rate Over Episodes
- **What it shows:** Percentage of episodes won (100-episode moving average)
- **What to look for:**
  - Should climb from 0% to 50-80%
  - Steep climb = fast learning
  - Plateau = convergence

#### Top Right: Average Reward Over Episodes
- **What it shows:** Average reward per episode (100-episode moving average)
- **What to look for:**
  - Should increase from negative to positive
  - Higher values = better performance
  - Crossing zero line = profitable behavior

#### Bottom Left: Q-Table Growth & Exploration
- **What it shows:**
  - Purple line: Q-table size (number of states learned)
  - Red line: Epsilon (exploration rate)
- **What to look for:**
  - Q-table should grow logarithmically
  - Epsilon should decay smoothly to ~0.01
  - ~5,000-8,000 states is typical

#### Bottom Right: Average Steps per Episode
- **What it shows:** How many steps to complete episode (100-episode moving average)
- **What to look for:**
  - Should decrease over time (getting more efficient)
  - Winning episodes typically 50-100 steps
  - Timeout is 500 steps (red line)

---

### 2. **q_value_heatmap.png** - Learned State Values

![Q-Value Heatmap Preview](visualizations/q_value_heatmap.png)

**What it shows:**
- Heatmap of the maze showing learned Q-values
- Green = High value (good states to be in)
- Red = Low value (bad states)
- White = Walls (not accessible)
- Blue circle = Starting position
- Gold star = Exit

**What to look for:**
- Exit should be bright green (highest value)
- Path from start to exit should be progressively greener
- Areas near coins should be green
- Dead ends should be darker

**Interpretation:**
```
High Q-values (bright green): Agent learned these lead to success
Low Q-values (red/yellow): Agent learned these are dangerous/inefficient
Gradient toward exit: Shows learned optimal path
```

---

### 3. **q_value_evolution.png** - Q-Values Over Time

![Q-Value Evolution Preview](visualizations/q_value_evolution.png)

**What it shows:**
- How Q-values for specific states change during training
- Each line = a different sample state
- X-axis = Episode number
- Y-axis = Maximum Q-value for that state

**What to look for:**
- Should start near 0
- Should increase over time
- Should plateau (convergence)
- Different states converge at different rates

**Interpretation:**
```
Rapid increase (0-500 episodes): Initial learning
Gradual increase (500-1500): Refinement
Plateau (1500+): Converged, optimal values learned
```

---

### 4. **performance_distributions.png** - Statistical Analysis

![Performance Distributions Preview](visualizations/performance_distributions.png)

**Contains 3 histograms:**

#### Left: Reward Distribution
- Shows frequency of different episode rewards
- **Good sign:** Peak shifts right over time (higher rewards)
- **Bad sign:** Stuck at negative rewards

#### Middle: Steps Distribution
- Shows how many steps episodes typically take
- **Good sign:** Concentrated around 50-100 steps for wins
- **Bad sign:** All episodes hitting 500 (timeout)

#### Right: Score Distribution
- Shows frequency of different scores
- **Good sign:** Peak at 70-150 (collecting 3-5 coins + exit)
- **Bad sign:** Peak at 0 (not collecting anything)

---

### 5. **learning_phases.png** - Phase Comparison

![Learning Phases Preview](visualizations/learning_phases.png)

**What it shows:**
- Compares performance across 4 training phases:
  - Early (0-25% of episodes)
  - Mid-Early (25-50%)
  - Mid-Late (50-75%)
  - Late (75-100%)

**Contains 3 bar charts:**

#### Win Rate by Phase
- Should show clear improvement from early to late
- **Typical:** 0% → 10% → 40% → 70%

#### Average Reward by Phase
- Should increase from negative to strongly positive
- **Typical:** -20 → 0 → +50 → +120

#### Average Score by Phase
- Should increase as agent learns to collect coins
- **Typical:** 0 → 10 → 40 → 80

---

## Command Line Options

### Basic Usage

```bash
# Default: 2000 episodes on 12×12 maze with 5 coins
python train_with_visualizations.py

# Custom number of episodes
python train_with_visualizations.py --episodes 5000

# Smaller maze (faster training)
python train_with_visualizations.py --maze-height 10 --maze-width 10

# More coins (harder)
python train_with_visualizations.py --coins 8

# Custom model save path
python train_with_visualizations.py --model-path my_agent.pkl

# All options combined
python train_with_visualizations.py --episodes 3000 --maze-height 15 --maze-width 15 --coins 7
```

### All Options

| Option | Default | Description |
|--------|---------|-------------|
| `--episodes` | 2000 | Number of training episodes |
| `--maze-height` | 12 | Maze height |
| `--maze-width` | 12 | Maze width |
| `--coins` | 5 | Number of coins to collect |
| `--model-path` | trained_agent.pkl | Where to save trained model |

---

## Output Files

After training, you'll find:

```
visualizations/
├── training_dashboard.png          (Main 4-plot dashboard)
├── q_value_heatmap.png            (Maze heatmap of learned values)
├── q_value_evolution.png          (Q-values over time)
├── performance_distributions.png  (Statistical distributions)
└── learning_phases.png            (Phase-by-phase comparison)

trained_agent.pkl                   (Trained model file)
```

All images are high resolution (300 DPI) suitable for:
- Reports and presentations
- Academic papers
- Documentation
- Sharing on social media

---

## Interpreting Your Results

### Good Training Run

**Signs of successful learning:**
- ✅ Win rate reaches 50-80%
- ✅ Average reward climbs above +80
- ✅ Q-table grows to 5,000+ states
- ✅ Epsilon decays to ~0.01
- ✅ Heatmap shows clear path to exit
- ✅ Q-values converge and stabilize

### Poor Training Run

**Signs of learning problems:**
- ❌ Win rate stuck at 0-10%
- ❌ Average reward stays negative
- ❌ Q-table very small (<1,000 states)
- ❌ Agent gets caught every time
- ❌ No clear pattern in heatmap

**Solutions if training is poor:**
- Train for more episodes (try 5,000)
- Check reward structure is correct
- Verify NPC is moving randomly (not chasing)
- Try smaller maze (10×10) first
- Reduce number of coins (3 instead of 5)

---

## Example Training Output

```
Starting training for 2000 episodes...
Maze size: (12, 12), Coins: 5
--------------------------------------------------------------------------------
Episode 100/2000 | Win Rate: 2.0% | Avg Reward: -15.32 | Avg Steps: 234.5 | Epsilon: 0.6050 | Q-Table: 487 states
Episode 200/2000 | Win Rate: 8.0% | Avg Reward: -2.45 | Avg Steps: 198.3 | Epsilon: 0.3660 | Q-Table: 1243 states
Episode 500/2000 | Win Rate: 24.0% | Avg Reward: 22.67 | Avg Steps: 145.2 | Epsilon: 0.0821 | Q-Table: 2891 states
Episode 1000/2000 | Win Rate: 52.0% | Avg Reward: 85.34 | Avg Steps: 98.7 | Epsilon: 0.0067 | Q-Table: 4532 states
Episode 2000/2000 | Win Rate: 68.0% | Avg Reward: 124.56 | Avg Steps: 87.3 | Epsilon: 0.0100 | Q-Table: 6234 states

================================================================================
Training completed!
================================================================================
Generating visualizations...
  ✓ Saved: visualizations/training_dashboard.png
  ✓ Saved: visualizations/q_value_heatmap.png
  ✓ Saved: visualizations/q_value_evolution.png
  ✓ Saved: visualizations/performance_distributions.png
  ✓ Saved: visualizations/learning_phases.png

✓ All visualizations generated successfully!

Final Statistics:
================================================================================
Total episodes: 2000
Final epsilon: 0.0100
Q-table size: 6234 states
Final win rate (last 100): 68.0%
Final avg reward (last 100): 124.56
Final avg steps (last 100): 87.3
Best win rate: 72.0%
```

---

## Tips for Great Visualizations

1. **Train long enough:** 2000+ episodes recommended
2. **High resolution:** All images are 300 DPI (publication quality)
3. **Compare runs:** Train multiple times with different parameters
4. **Share your results:** Visualizations folder is git-ignored by default
5. **Academic use:** All plots include clear labels and legends

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'seaborn'"

```bash
pip install seaborn
# Or reinstall all requirements
pip install -r requirements.txt
```

### "FileNotFoundError: visualizations/"

The script creates this automatically. If you get this error:
```bash
mkdir visualizations
```

### Plots look strange or empty

- **Q-value heatmap is all zeros:** Agent hasn't learned anything yet, train longer
- **Win rate is flat at 0%:** Check if NPC is too difficult
- **Q-values don't converge:** Try reducing learning rate or training longer

---

## Customizing Visualizations

The visualization script (`train_with_visualizations.py`) can be modified:

1. **Change colors:** Edit the color codes in the plotting functions
2. **Add more plots:** Add new subplots in `generate_all_plots()`
3. **Different metrics:** Track additional statistics during training
4. **Export formats:** Change `.png` to `.pdf`, `.svg`, etc.

---

## Next Steps

After generating visualizations:

1. **Analyze your results** using the interpretation guide above
2. **Watch the trained agent** play:
   ```bash
   python play.py --mode agent
   ```
3. **Experiment** with different parameters
4. **Share** your visualizations and results!

---

*Happy training! 🎮📊*
