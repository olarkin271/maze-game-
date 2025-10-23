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

        # Place NPC at a random position (far from player for easier gameplay)
        self.npc_pos = self._get_random_empty_pos(min_distance_from_player=8)

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

        # Track previous position to penalize staying in place
        self.prev_player_pos = self.player_pos.copy()

        # Track visit counts for each position to encourage exploration
        self.visit_counts = {}
        self._increment_visit_count(self.player_pos)

        return self._get_state()

    def _create_maze(self) -> np.ndarray:
        """Create a maze with walls around the border and some internal walls"""
        maze = np.zeros((self.height, self.width), dtype=int)

        # Border walls
        maze[0, :] = self.WALL
        maze[-1, :] = self.WALL
        maze[:, 0] = self.WALL
        maze[:, -1] = self.WALL

        # Add some internal walls to make it more interesting (reduced density for more escape routes)
        # Vertical walls
        if self.width > 6:
            for i in range(2, self.height - 2, 3):
                for j in range(1, self.width // 2):
                    if random.random() < 0.25:  # Reduced from 0.6 to 0.25 for more open space
                        maze[i, j * 2] = self.WALL

        # Horizontal walls
        if self.height > 6:
            for i in range(1, self.height // 2):
                for j in range(2, self.width - 2, 3):
                    if random.random() < 0.25:  # Reduced from 0.6 to 0.25 for more open space
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

    def _increment_visit_count(self, pos: List[int]) -> int:
        """Increment and return visit count for a position"""
        pos_tuple = tuple(pos)
        if pos_tuple not in self.visit_counts:
            self.visit_counts[pos_tuple] = 0
        self.visit_counts[pos_tuple] += 1
        return self.visit_counts[pos_tuple]

    def step(self, action: int) -> Tuple[dict, float, bool]:
        """
        Take a step in the environment
        Returns: (state, reward, done)
        """
        if self.caught or self.won:
            return self._get_state(), 0, True

        # Calculate distances before moving for progress rewards
        prev_coin_dist = self._get_nearest_coin_distance(self.player_pos)
        prev_exit_dist = self._get_manhattan_distance(self.player_pos, self.exit_pos)

        # Store previous position before moving
        self.prev_player_pos = self.player_pos.copy()

        # Move player
        new_pos = self._get_new_position(self.player_pos, action)
        if self._is_valid_move(new_pos):
            self.player_pos = new_pos

        reward = -0.05  # Reduced step penalty to encourage exploration

        # Penalize staying in the same position (didn't move)
        if self.player_pos == self.prev_player_pos:
            reward -= 1.0  # Strong penalty for hitting walls
        else:
            # Track position visits with lighter penalty
            visit_count = self._increment_visit_count(self.player_pos)
            if visit_count > 2:  # Only penalize after 2nd visit
                reward -= 0.1 * (visit_count - 2)  # Lighter revisit penalty

        # Check if player collected a coin
        collected_coin = False
        if self.player_pos in self.coins:
            self.coins.remove(self.player_pos)
            self.maze[self.player_pos[0], self.player_pos[1]] = self.EMPTY
            self.score += 10
            reward += 20  # Increased reward for collecting coin
            collected_coin = True

        # Check if player reached exit
        if self.player_pos == self.exit_pos:
            self.won = True
            # Bonus for winning with all coins collected
            coin_bonus = 50 if len(self.coins) == 0 else 0
            # Bonus for winning quickly
            efficiency_bonus = max(0, (self.max_steps - self.steps) * 0.1)
            reward += 150 + coin_bonus + efficiency_bonus
            return self._get_state(), reward, True

        # Reward for making progress toward goals
        if not collected_coin and self.player_pos != self.prev_player_pos:
            # If there are coins left, reward getting closer to nearest coin
            if self.coins:
                new_coin_dist = self._get_nearest_coin_distance(self.player_pos)
                if new_coin_dist < prev_coin_dist:
                    reward += 0.5  # Reward for moving toward coin
                elif new_coin_dist > prev_coin_dist:
                    reward -= 0.3  # Penalty for moving away from coin
            # If no coins left, reward getting closer to exit
            else:
                new_exit_dist = self._get_manhattan_distance(self.player_pos, self.exit_pos)
                if new_exit_dist < prev_exit_dist:
                    reward += 1.0  # Strong reward for moving toward exit
                elif new_exit_dist > prev_exit_dist:
                    reward -= 0.5  # Penalty for moving away from exit

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

    def _get_manhattan_distance(self, pos1: List[int], pos2: List[int]) -> int:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _get_nearest_coin_distance(self, pos: List[int]) -> int:
        """Get distance to nearest coin, or large value if no coins"""
        if not self.coins:
            return 999  # Large value if no coins
        return min(self._get_manhattan_distance(pos, coin) for coin in self.coins)

    def _move_npc(self):
        """Move NPC randomly around the board (only moves 30% of the time)"""
        # NPC only moves 30% of the time to make it easier to avoid
        if random.random() > 0.3:
            return

        # Random movement: NPC moves in random valid directions
        valid_actions = []

        for action in self.ACTIONS:
            new_pos = self._get_new_position(self.npc_pos, action)
            if self._is_valid_move(new_pos):
                valid_actions.append(action)

        # Move NPC to a random valid position
        if valid_actions:
            action = random.choice(valid_actions)
            self.npc_pos = self._get_new_position(self.npc_pos, action)

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
