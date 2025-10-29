# Markov Decision Process (MDP) Specification
## Maze Game with Q-Learning AI Agent

---

## Overview

This document provides a complete MDP formulation for the maze escape game with coin collection and NPC avoidance.

**MDP Tuple:** `M = (S, A, P, R, γ)`

---

## 1. State Space (S)

### State Representation

Each state `s ∈ S` is represented by:

```
s = (player_pos, npc_relative, exit_relative, coin_relative, coins_remaining)
```

Where:
- **`player_pos`**: `(row, col)` - Absolute position of the player in the maze
- **`npc_relative`**: `(Δrow, Δcol)` - NPC position relative to player
- **`exit_relative`**: `(Δrow, Δcol)` - Exit position relative to player
- **`coin_relative`**: `(Δrow, Δcol)` - Nearest coin position relative to player
- **`coins_remaining`**: Integer count of uncollected coins

### State Space Characteristics

| Property | Value |
|----------|-------|
| **State Space Type** | Discrete, Large |
| **Maze Dimensions** | 12×12 (default) = 144 positions |
| **Possible Player Positions** | ~100-120 (excluding walls) |
| **NPC Relative Positions** | Varies based on distance |
| **State Space Size** | Very Large (10³ - 10⁶ states) |
| **Fully Observable** | Yes |
| **Deterministic (Player)** | Yes |
| **Stochastic (NPC)** | Yes (30% movement probability) |

### Special States

| State Type | Description | Terminal |
|------------|-------------|----------|
| **Initial State** | Player at (1,1), NPC 8+ units away | No |
| **Win State** | `player_pos == exit_pos` | Yes |
| **Caught State** | `player_pos == npc_pos` | Yes |
| **Timeout State** | `steps >= 500` | Yes |

---

## 2. Action Space (A)

### Available Actions

```
A = {UP, DOWN, LEFT, RIGHT}
```

| Action | Code | Effect |
|--------|------|--------|
| **UP** | 0 | `row -= 1` |
| **DOWN** | 1 | `row += 1` |
| **LEFT** | 2 | `col -= 1` |
| **RIGHT** | 3 | `col += 1` |

### Action Constraints

- **Total Actions**: 4 (always available)
- **Invalid Actions**: Moving into walls results in no position change
- **Action Space Size**: |A| = 4

---

## 3. Transition Function P(s'|s,a)

The transition function defines: **P(s' | s, a) = Probability of reaching state s' from state s by taking action a**

### Player Movement (Deterministic)

```
If valid_move(s, a):
    player_pos' = player_pos + action_delta
Else:
    player_pos' = player_pos  (stay in place)
```

### NPC Movement (Stochastic)

The NPC introduces stochasticity:

```
P(npc moves | s, a) = 0.3
P(npc stays | s, a) = 0.7

If NPC moves:
    npc chooses random valid direction uniformly
```

### Coin Collection (Deterministic)

```
If player_pos' == coin_pos:
    coins_remaining' = coins_remaining - 1
    Remove coin from maze
```

### Transition Probability Structure

For a given state-action pair (s, a):

```
P(s'|s,a) = P(player_move) × P(npc_move) × P(coin_collection)
          = 1.0 × [0.3 or 0.7] × 1.0
```

Since player and coin mechanics are deterministic, uncertainty comes only from NPC.

---

## 4. Reward Function R(s, a, s')

### Complete Reward Table

| Reward Component | Condition | Value | Purpose |
|------------------|-----------|-------|---------|
| **Base Step Penalty** | Every step | **-0.05** | Encourage efficiency |
| **Wall Hit Penalty** | Tried to move into wall | **-1.0** | Discourage invalid moves |
| **Stay-in-Place Penalty** | `pos == prev_pos` | **-1.0** | Force exploration |
| **Revisit Penalty** | Visiting cell 3+ times | **-0.1 × (visits - 2)** | Discourage loops |
| **Progress Toward Coin** | Moving closer to nearest coin | **+0.5** | Guide to coins |
| **Away From Coin** | Moving farther from coin | **-0.3** | Discourage wrong direction |
| **Progress Toward Exit** | Moving closer to exit (no coins left) | **+1.0** | Guide to exit |
| **Away From Exit** | Moving farther from exit (no coins left) | **-0.5** | Discourage wrong direction |
| **Coin Collection** | Player collects coin | **+20** | Reward subgoal |
| **Reach Exit (Win)** | Player reaches exit | **+150** | Major goal reward |
| **All Coins Bonus** | Win with all coins collected | **+50** | Perfection bonus |
| **Efficiency Bonus** | Win quickly | **+(500 - steps) × 0.1** | Reward speed |
| **Caught by NPC** | Player caught | **-50** | Failure penalty |
| **Timeout** | Exceeded 500 steps | **-10** | Discourage slowness |

### Reward Function Formula

```python
R(s, a, s') = base_reward + movement_reward + goal_reward + penalty

Where:
    base_reward = -0.05

    movement_reward = {
        -1.0,  if pos == prev_pos (wall hit)
        +0.5,  if moving toward coin
        -0.3,  if moving away from coin
        +1.0,  if moving toward exit (no coins)
        -0.5,  if moving away from exit (no coins)
        -0.1×(v-2), if visited v > 2 times
    }

    goal_reward = {
        +20,   if coin collected
        +150 + bonuses,  if reached exit
        -50,   if caught by NPC
        -10,   if timeout
    }
```

### Reward Range

- **Minimum per step**: ~-2.0 (wall hit + penalties)
- **Maximum per step**: ~+21.0 (coin collection + progress)
- **Maximum episode**: ~250+ (win with all coins quickly)
- **Minimum episode**: ~-60 (caught immediately with penalties)

---

## 5. Discount Factor (γ)

```
γ = 0.95
```

### Implications

- **Look-ahead**: Agent considers ~20 steps ahead effectively (1/0.05 = 20)
- **Preference**: Slightly prefers immediate rewards over delayed ones
- **Balance**: Good balance between short-term and long-term planning

---

## 6. Terminal States and Episode Termination

### Terminal Conditions

| Condition | State | Reward | Success |
|-----------|-------|--------|---------|
| **Win** | `player_pos == exit_pos` | +150 to +250 | ✅ Yes |
| **Caught** | `player_pos == npc_pos` | -50 | ❌ No |
| **Timeout** | `steps >= 500` | -10 | ❌ No |

### Episode Flow

```
1. Initialize: s₀ ~ p(s₀)
2. For t = 0, 1, 2, ..., T:
   a. Select action: aₜ ~ π(·|sₜ)
   b. Execute action: player moves
   c. Environment response: NPC moves (30% chance)
   d. Observe: reward rₜ and next state sₜ₊₁
   e. Update: Q-learning update
   f. Check terminal condition
   g. If terminal: break
3. Return: total reward and success status
```

---

## 7. Q-Learning Algorithm Parameters

### Hyperparameters

| Parameter | Symbol | Value | Description |
|-----------|--------|-------|-------------|
| **Learning Rate** | α | 0.1 | How much to update Q-values |
| **Discount Factor** | γ | 0.95 | Future reward importance |
| **Initial Epsilon** | ε₀ | 1.0 | Start with full exploration |
| **Min Epsilon** | ε_min | 0.01 | End with 1% exploration |
| **Epsilon Decay** | ε_decay | 0.995 | Decay rate per episode |
| **Max Steps** | T_max | 500 | Episode timeout |

### Q-Learning Update Rule

```
Q(s, a) ← Q(s, a) + α[r + γ max(Q(s', a')) - Q(s, a)]
                              a'
```

Where:
- **s**: Current state
- **a**: Action taken
- **r**: Reward received
- **s'**: Next state
- **α**: Learning rate (0.1)
- **γ**: Discount factor (0.95)

### Exploration Strategy

**ε-greedy policy:**

```
π(a|s) = {
    random action,           with probability ε
    argmax Q(s, a'),        with probability 1-ε
           a'
}
```

**Epsilon schedule:**
```
εₜ = max(ε_min, ε₀ × ε_decay^t)
```

After 1000 episodes: ε ≈ 0.007 (highly exploitative)

---

## 8. Optimal Policy Characteristics

### Expected Optimal Behavior

The optimal policy π* should learn to:

1. **Phase 1 - Coin Collection:**
   - Navigate to nearest uncollected coin
   - Avoid NPC while collecting
   - Minimize backtracking

2. **Phase 2 - Exit:**
   - Once all coins collected, head straight to exit
   - Take shortest valid path
   - Avoid NPC encounters

3. **General Strategy:**
   - Prefer open spaces over narrow corridors
   - Avoid revisiting cells
   - Balance coin collection vs. NPC avoidance
   - Optimize for speed (efficiency bonus)

### Performance Metrics

| Metric | Target (After Training) |
|--------|-------------------------|
| **Win Rate** | 50-80% |
| **Average Steps (Win)** | 50-100 steps |
| **Average Score** | 60-120 points |
| **Coins Collected** | 3-5 (out of 5) |
| **Q-Table Size** | 10³-10⁴ states |

---

## 9. MDP Properties

### Verification

| Property | Status | Explanation |
|----------|--------|-------------|
| **Markov Property** | ✅ Yes | Next state depends only on current state and action |
| **Stationary** | ✅ Yes | Transition and reward functions don't change over time |
| **Episodic** | ✅ Yes | Clear start and end to each game |
| **Finite Actions** | ✅ Yes | Only 4 actions available |
| **Bounded Rewards** | ✅ Yes | Rewards are bounded |
| **Accessible** | ✅ Yes | Exit reachable from start (with high probability) |

### Challenges

| Challenge | Type | Impact |
|-----------|------|--------|
| **Large State Space** | Computational | Requires many episodes to explore |
| **Sparse Rewards** | Learning | Hard to learn without progress rewards |
| **Stochastic NPC** | Uncertainty | Same action may lead to different outcomes |
| **Credit Assignment** | Learning | Which actions led to success? |

---

## 10. Implementation Notes

### State Representation for Q-Table

Instead of storing absolute positions, we use relative representations:

```python
state_key = (
    player_absolute_pos,      # (row, col)
    npc_relative_pos,          # (Δrow, Δcol)
    exit_relative_pos,         # (Δrow, Δcol)
    nearest_coin_relative_pos, # (Δrow, Δcol)
    num_coins_remaining        # integer
)
```

This reduces state space while maintaining Markov property.

### Q-Table Structure

```python
Q: State → [Q(s,UP), Q(s,DOWN), Q(s,LEFT), Q(s,RIGHT)]
```

Implemented as:
- **Python**: `defaultdict` with tuple keys
- **JavaScript**: `Map` with JSON string keys

---

## 11. Summary Table

| MDP Component | Specification |
|---------------|---------------|
| **States (S)** | Player position + relative positions (NPC, exit, coins) + coin count |
| **Actions (A)** | {UP, DOWN, LEFT, RIGHT} |
| **Transitions (P)** | Deterministic player + 30% stochastic NPC |
| **Rewards (R)** | Progress-based (-2.0 to +250 per episode) |
| **Discount (γ)** | 0.95 |
| **Horizon** | Episodic (max 500 steps) |
| **Terminal States** | Win, Caught, Timeout |
| **Algorithm** | Q-Learning with ε-greedy |
| **Convergence** | Expected after 2000-5000 episodes |

---

## References

- Sutton & Barto (2018). *Reinforcement Learning: An Introduction*
- Watkins (1989). *Learning from Delayed Rewards* (Q-Learning)
- Bellman (1957). *Dynamic Programming* (Bellman Equation)

---

*Generated for maze-game Q-learning implementation*
*Last Updated: 2025-10-29*
