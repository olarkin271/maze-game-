from maze_game import MazeGame

game = MazeGame((12, 12), 5)
game.reset()

print(f"Player start: {game.player_pos}")
print(f"Exit position: {game.exit_pos}")
print(f"Player pos type: {type(game.player_pos)}")
print(f"Exit pos type: {type(game.exit_pos)}")

# Manually move player to exit
game.player_pos = game.exit_pos.copy()

print(f"\nAfter moving to exit:")
print(f"Player: {game.player_pos}")
print(f"Exit: {game.exit_pos}")
print(f"Are they equal? {game.player_pos == game.exit_pos}")

# Take a step (any action)
state, reward, done = game.step(0)

print(f"\nAfter step:")
print(f"Won: {game.won}")
print(f"Caught: {game.caught}")
print(f"Done: {done}")
print(f"Reward: {reward:.2f}")
