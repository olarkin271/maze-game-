import pickle
from maze_game import MazeGame
from q_learning_agent import QLearningAgent

# Load trained agent
agent = QLearningAgent()
agent.load('trained_agent.pkl')
agent.epsilon = 0.0  # No exploration

# Run 10 test games
wins = 0
caught = 0
timeouts = 0

for game_num in range(10):
    game = MazeGame((12, 12), 5)
    game.reset()

    state = game.get_state_representation()
    total_reward = 0
    step_count = 0

    while step_count < 600:  # Safety limit
        action = agent.get_action(state, training=False)
        next_state_dict, reward, done = game.step(action)
        total_reward += reward
        step_count += 1

        if done:
            if game.won:
                wins += 1
                print(f"Game {game_num+1}: WON in {game.steps} steps, Reward={total_reward:.2f}, Coins={5-len(game.coins)}/5")
            elif game.caught:
                caught += 1
                print(f"Game {game_num+1}: CAUGHT in {game.steps} steps, Reward={total_reward:.2f}, Coins={5-len(game.coins)}/5")
            else:
                timeouts += 1
                dist = abs(game.player_pos[0]-game.exit_pos[0]) + abs(game.player_pos[1]-game.exit_pos[1])
                print(f"Game {game_num+1}: TIMEOUT in {game.steps} steps, Reward={total_reward:.2f}, Coins={5-len(game.coins)}/5, Dist={dist}")
            break

        state = game.get_state_representation()

print(f"\n=== Summary ===")
print(f"Wins: {wins}/10 = {wins*10}%")
print(f"Caught: {caught}/10 = {caught*10}%")
print(f"Timeouts: {timeouts}/10 = {timeouts*10}%")
