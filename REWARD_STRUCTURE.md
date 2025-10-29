# Reward Structure - Quick Reference

## Complete Reward Table

### Movement Penalties (Encourage Efficiency)

| Event | Reward | When Applied |
|-------|--------|--------------|
| Any step taken | **-0.05** | Every action |
| Hit wall (no movement) | **-1.0** | When action leads to wall/boundary |
| Stay in same position | **-1.0** | Combined with wall hit |
| Visit cell 3rd time | **-0.1** | Cumulative: 3rd visit = -0.1 |
| Visit cell 4th time | **-0.2** | Cumulative: 4th visit = -0.2 |
| Visit cell 5th time | **-0.3** | Pattern: -0.1 × (visits - 2) |

### Progress Rewards (Guide Behavior)

| Event | Reward | Condition |
|-------|--------|-----------|
| Move toward nearest coin | **+0.5** | When coins remain & distance decreases |
| Move away from nearest coin | **-0.3** | When coins remain & distance increases |
| Move toward exit | **+1.0** | When NO coins remain & distance decreases |
| Move away from exit | **-0.5** | When NO coins remain & distance increases |

### Goal Achievement (Major Rewards)

| Event | Reward | Details |
|-------|--------|---------|
| Collect a coin | **+20** | Each coin collected |
| Reach exit (base) | **+150** | Successfully escape |
| All coins collected bonus | **+50** | Additional if all 5 coins collected |
| Efficiency bonus | **+0.1 per step saved** | Max +50 (if completed in 0 steps, theoretical) |
| **Maximum win reward** | **~250** | 150 + 50 + efficiency |

### Failure Penalties

| Event | Reward | Terminal |
|-------|--------|----------|
| Caught by NPC | **-50** | Yes (episode ends) |
| Timeout (500 steps) | **-10** | Yes (episode ends) |

---

## Reward Examples by Scenario

### Scenario 1: Optimal Path to First Coin

```
Step 1: Move toward coin    = -0.05 + 0.5  = +0.45
Step 2: Move toward coin    = -0.05 + 0.5  = +0.45
Step 3: Move toward coin    = -0.05 + 0.5  = +0.45
Step 4: Collect coin        = -0.05 + 0.5 + 20 = +20.45
Total: +22.80
```

### Scenario 2: Hit Wall and Backtrack

```
Step 1: Hit wall            = -0.05 - 1.0   = -1.05
Step 2: Backtrack (2nd visit) = -0.05      = -0.05
Step 3: Backtrack (3rd visit) = -0.05 - 0.1 = -0.15
Total: -1.25 (bad!)
```

### Scenario 3: Collect All Coins and Win Quickly

```
Coin 1 collection:    +20
Coin 2 collection:    +20
Coin 3 collection:    +20
Coin 4 collection:    +20
Coin 5 collection:    +20
Exit reached:         +150
All coins bonus:      +50
Efficiency (400 saved): +40
Progress rewards:     ~+30
Movement penalties:   ~-5
Total: ~365 points!
```

### Scenario 4: Caught by NPC

```
Move toward coin:     +0.45
Move toward coin:     +0.45
Caught by NPC:        -50
Total: -49.1 (failure)
```

---

## Reward Shaping Strategy

### Phase-Based Rewards

**Phase 1: Coin Collection (coins remaining > 0)**
- Primary: Progress toward nearest coin (+0.5 / -0.3)
- Secondary: Coin collection (+20)
- Avoid: NPC proximity, wall hits, revisits

**Phase 2: Escape (coins remaining = 0)**
- Primary: Progress toward exit (+1.0 / -0.5)
- Secondary: Speed (efficiency bonus)
- Goal: Reach exit (+150 + bonuses)

### Behavioral Incentives

| Desired Behavior | Reward Mechanism |
|------------------|------------------|
| **Explore efficiently** | Small step penalty (-0.05) |
| **Avoid walls** | Large wall penalty (-1.0) |
| **Don't loop** | Escalating revisit penalty |
| **Pursue coins** | Progress rewards (+0.5) |
| **Reach exit** | Large terminal reward (+150+) |
| **Be fast** | Efficiency bonus |
| **Avoid NPC** | Caught penalty (-50) |

---

## Cumulative Reward Breakdown

### Minimum Possible Episode Reward
```
Scenario: Caught immediately at start
- Steps: 1
- Hit wall: -1.0
- Caught: -50
- Total: -51
```

### Maximum Possible Episode Reward
```
Scenario: Perfect run with all coins
- Coins: 5 × 20 = +100
- Exit: +150
- All coins bonus: +50
- Efficiency: ~+40 (80 steps)
- Progress: ~+40
- Movement: ~-4
- Total: ~376
```

### Expected Typical Win
```
Scenario: Win with 3-4 coins
- Coins: 3.5 × 20 = +70
- Exit: +150
- Progress: ~+20
- Movement: ~-6
- Total: ~234
```

### Expected Typical Loss
```
Scenario: Caught after exploring
- Coins: 1 × 20 = +20
- Caught: -50
- Progress: ~+5
- Movement: ~-8
- Total: -33
```

---

## Reward Balance Analysis

### Risk vs. Reward

| Decision | Risk | Reward | Expected Value |
|----------|------|--------|----------------|
| Collect coin (risky path) | -50 (caught) × 0.1 | +20 × 0.9 | +13 ✅ |
| Avoid coin (safe path) | -0.05 (step) | +0.5 (progress) | +0.45 ❌ |
| Rush to exit (no coins) | -50 (caught) × 0.05 | +150 × 0.95 | +140 ✅ |
| Loop/backtrack | -0.1+ (revisit) | 0 | -0.1 ❌ |

**Conclusion:** Taking calculated risks to collect coins and reach exit is rewarded.

---

## Training Progress Expectations

### Early Training (Episodes 1-500)
- **Win Rate:** 0-10%
- **Average Reward:** -20 to +10
- **Behavior:** Random exploration, frequent failures

### Mid Training (Episodes 500-1500)
- **Win Rate:** 10-40%
- **Average Reward:** +10 to +80
- **Behavior:** Learning to collect 1-2 coins, occasional wins

### Late Training (Episodes 1500-3000)
- **Win Rate:** 40-70%
- **Average Reward:** +60 to +150
- **Behavior:** Systematic coin collection, efficient pathing

### Converged (Episodes 3000+)
- **Win Rate:** 60-80%
- **Average Reward:** +100 to +200
- **Behavior:** Near-optimal coin collection and escape

---

## Reward Tuning Notes

### Why These Values?

1. **Step Penalty (-0.05):**
   - Small enough to allow exploration
   - Large enough to encourage efficiency
   - 100 steps = -5 penalty (manageable)

2. **Wall Hit (-1.0):**
   - 20× larger than step penalty
   - Strongly discourages invalid moves
   - Encourages learning valid actions quickly

3. **Coin Reward (+20):**
   - 2× the typical progress rewards needed to reach it
   - Worthwhile to pursue
   - Not so large that agent ignores exit

4. **Exit Reward (+150):**
   - 7.5× a coin reward
   - Primary goal is clear
   - Balanced with coin collection

5. **Progress Rewards (+0.5, +1.0):**
   - Provides continuous feedback
   - Guides agent when far from goals
   - Exit progress 2× coin progress (prioritize after coins)

6. **Caught Penalty (-50):**
   - Smaller than exit reward (agent will still take risks)
   - Large enough to encourage avoidance
   - Balanced to prevent excessive caution

---

*This reward structure creates a balanced learning environment where the agent*
*learns to efficiently collect coins and escape while avoiding the NPC.*
