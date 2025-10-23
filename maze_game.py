import numpy as np
import random
from typing import Tuple, List, Optional

class MazeGame:
    """
    Maze game environment with:
    - Player/AI agent that needs to reach the exit
    - NPC that chases the player
    - Coins to collect for score
    """

    # Action constants
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    ACTIONS = [UP, DOWN, LEFT, RIGHT]

    # Cell types
    EMPTY = 0
    WALL = 1
    COIN = 2
    EXIT = 3

    def __init__(self, maze_size: Tuple[int, int] = (10, 10), num_coins: int = 5):
        self.height, self.width = maze_size
        self.num_coins = num_coins
        self.reset()

    def reset(self) -> dict:
        """Reset the game to initial state"""
        # Create maze with walls
        self.maze = self._create_maze()

        # Place player at top-left area
        self.player_pos = [1, 1]

        # Place exit at bottom-right area
        self.exit_pos = [self.height - 2, self.width - 2]
        self.maze[self.exit_pos[0], self.exit_pos[1]] = self.EXIT

        # Place NPC at a random position (not too close to player)
        self.npc_pos = self._get_random_empty_pos(min_distance_from_player=4)

        # Place coins
        self.coins = []
        for _ in range(self.num_coins):
            coin_pos = self._get_random_empty_pos()
            self.coins.append(coin_pos)
            self.maze[coin_pos[0], coin_pos[1]] = self.COIN

        self.score = 0
        self.steps = 0
        self.max_steps = 500
        self.caught = False
        self.won = False

        return self._get_state()

    def _create_maze(self) -> np.ndarray:
        """Create a maze with walls around the border and some internal walls"""
        maze = np.zeros((self.height, self.width), dtype=int)

        # Border walls
        maze[0, :] = self.WALL
        maze[-1, :] = self.WALL
        maze[:, 0] = self.WALL
        maze[:, -1] = self.WALL

        # Add some internal walls to make it more interesting
        # Vertical walls
        if self.width > 6:
            for i in range(2, self.height - 2, 3):
                for j in range(1, self.width // 2):
                    if random.random() < 0.6:
                        maze[i, j * 2] = self.WALL

        # Horizontal walls
        if self.height > 6:
            for i in range(1, self.height // 2):
                for j in range(2, self.width - 2, 3):
                    if random.random() < 0.6:
                        maze[i * 2, j] = self.WALL

        return maze

    def _get_random_empty_pos(self, min_distance_from_player: int = 0) -> List[int]:
        """Get a random empty position in the maze"""
        while True:
            row = random.randint(1, self.height - 2)
            col = random.randint(1, self.width - 2)

            if self.maze[row, col] == self.EMPTY:
                if min_distance_from_player > 0:
                    distance = abs(row - self.player_pos[0]) + abs(col - self.player_pos[1])
                    if distance >= min_distance_from_player:
                        return [row, col]
                else:
                    return [row, col]

    def _get_state(self) -> dict:
        """Get current state representation"""
        return {
            'player_pos': tuple(self.player_pos),
            'npc_pos': tuple(self.npc_pos),
            'coins': [tuple(c) for c in self.coins],
            'score': self.score,
            'steps': self.steps,
            'caught': self.caught,
            'won': self.won,
            'maze': self.maze.copy()
        }

    def step(self, action: int) -> Tuple[dict, float, bool]:
        """
        Take a step in the environment
        Returns: (state, reward, done)
        """
        if self.caught or self.won:
            return self._get_state(), 0, True

        # Move player
        new_pos = self._get_new_position(self.player_pos, action)
        if self._is_valid_move(new_pos):
            self.player_pos = new_pos

        reward = -0.1  # Small negative reward for each step (encourages efficiency)

        # Check if player collected a coin
        if self.player_pos in self.coins:
            self.coins.remove(self.player_pos)
            self.maze[self.player_pos[0], self.player_pos[1]] = self.EMPTY
            self.score += 10
            reward += 10  # Reward for collecting coin

        # Check if player reached exit
        if self.player_pos == self.exit_pos:
            self.won = True
            reward += 100  # Big reward for winning
            return self._get_state(), reward, True

        # Move NPC (chases player)
        self._move_npc()

        # Check if NPC caught player
        if self.player_pos == self.npc_pos:
            self.caught = True
            reward -= 50  # Big penalty for getting caught
            return self._get_state(), reward, True

        self.steps += 1

        # Check if max steps reached
        if self.steps >= self.max_steps:
            reward -= 10  # Penalty for taking too long
            return self._get_state(), reward, True

        return self._get_state(), reward, False

    def _get_new_position(self, pos: List[int], action: int) -> List[int]:
        """Get new position based on action"""
        new_pos = pos.copy()
        if action == self.UP:
            new_pos[0] -= 1
        elif action == self.DOWN:
            new_pos[0] += 1
        elif action == self.LEFT:
            new_pos[1] -= 1
        elif action == self.RIGHT:
            new_pos[1] += 1
        return new_pos

    def _is_valid_move(self, pos: List[int]) -> bool:
        """Check if position is valid (not a wall and within bounds)"""
        row, col = pos
        if row < 0 or row >= self.height or col < 0 or col >= self.width:
            return False
        if self.maze[row, col] == self.WALL:
            return False
        return True

    def _move_npc(self):
        """Move NPC towards player using simple pathfinding"""
        # Simple chase AI: move towards player
        best_action = None
        best_distance = float('inf')

        for action in self.ACTIONS:
            new_pos = self._get_new_position(self.npc_pos, action)
            if self._is_valid_move(new_pos):
                # Calculate Manhattan distance to player
                distance = abs(new_pos[0] - self.player_pos[0]) + abs(new_pos[1] - self.player_pos[1])
                if distance < best_distance:
                    best_distance = distance
                    best_action = action

        # Move NPC with 80% probability (makes it slightly less perfect)
        if best_action is not None and random.random() < 0.8:
            self.npc_pos = self._get_new_position(self.npc_pos, best_action)

    def get_state_representation(self) -> np.ndarray:
        """
        Get a compact state representation for Q-learning
        Returns a tuple that can be used as a dictionary key
        """
        # Discretize relative positions
        player_pos = tuple(self.player_pos)
        npc_relative = (
            self.npc_pos[0] - self.player_pos[0],
            self.npc_pos[1] - self.player_pos[1]
        )
        exit_relative = (
            self.exit_pos[0] - self.player_pos[0],
            self.exit_pos[1] - self.player_pos[1]
        )

        # Get nearest coin relative position
        if self.coins:
            nearest_coin = min(self.coins,
                             key=lambda c: abs(c[0] - self.player_pos[0]) + abs(c[1] - self.player_pos[1]))
            coin_relative = (
                nearest_coin[0] - self.player_pos[0],
                nearest_coin[1] - self.player_pos[1]
            )
        else:
            coin_relative = (0, 0)

        return (player_pos, npc_relative, exit_relative, coin_relative, len(self.coins))

    def render_text(self):
        """Print text representation of the game"""
        print("\n" + "="*50)
        print(f"Score: {self.score} | Steps: {self.steps}")
        print("="*50)

        for i in range(self.height):
            for j in range(self.width):
                if [i, j] == self.player_pos:
                    print("P", end=" ")
                elif [i, j] == self.npc_pos:
                    print("N", end=" ")
                elif [i, j] == self.exit_pos:
                    print("E", end=" ")
                elif [i, j] in self.coins:
                    print("C", end=" ")
                elif self.maze[i, j] == self.WALL:
                    print("#", end=" ")
                else:
                    print(".", end=" ")
            print()

        if self.won:
            print("\n🎉 YOU WON! 🎉")
        elif self.caught:
            print("\n💀 CAUGHT BY NPC! 💀")
        print()
