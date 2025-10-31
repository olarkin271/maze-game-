from maze_game import MazeGame
import random

# Seed for reproducibility
random.seed(42)

# Run 20 random episodes and track how they end
wins = 0
caught = 0
timeouts = 0
rewards = []

for episode in range(20):
    game = MazeGame((12, 12), 5)
    game.reset()

    episode_reward = 0

    while True:
        # Random action
        action = random.randint(0, 3)
        next_state_dict, reward, done = game.step(action)
        episode_reward += reward

        if done:
            rewards.append(episode_reward)
            if game.won:
                wins += 1
                print(f"Episode {episode+1}: WON in {game.steps} steps, reward={episode_reward:.2f}, coins={5-len(game.coins)}/5")
            elif game.caught:
                caught += 1
                print(f"Episode {episode+1}: CAUGHT in {game.steps} steps, reward={episode_reward:.2f}, coins={5-len(game.coins)}/5")
            elif game.steps >= game.max_steps:
                timeouts += 1
                print(f"Episode {episode+1}: TIMEOUT in {game.steps} steps, reward={episode_reward:.2f}, coins={5-len(game.coins)}/5, distance={abs(game.player_pos[0]-game.exit_pos[0])+abs(game.player_pos[1]-game.exit_pos[1])}")
            else:
                print(f"Episode {episode+1}: Unknown end condition - won={game.won}, caught={game.caught}, steps={game.steps}")
            break

print(f"\n=== Summary ===")
print(f"Wins: {wins}/20 = {wins*5}%")
print(f"Caught: {caught}/20 = {caught*5}%")
print(f"Timeouts: {timeouts}/20 = {timeouts*5}%")
print(f"Avg reward: {sum(rewards)/len(rewards):.2f}")
