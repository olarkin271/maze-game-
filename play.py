#!/usr/bin/env python3
"""
Visualization script to watch the trained Q-learning agent play the maze game
"""

import pygame
import sys
import argparse
import time
from maze_game import MazeGame
from q_learning_agent import QLearningAgent

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

class MazeGameVisualizer:
    """Pygame visualization for the maze game"""

    def __init__(self, game: MazeGame, cell_size: int = 50):
        pygame.init()
        self.game = game
        self.cell_size = cell_size

        # Calculate window size
        self.width = game.width * cell_size
        self.height = game.height * cell_size + 80  # Extra space for info panel

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Maze Game - Q-Learning AI Agent")

        # Font for text
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)

        self.clock = pygame.time.Clock()

    def draw(self):
        """Draw the current game state"""
        self.screen.fill(WHITE)

        # Draw maze grid
        for i in range(self.game.height):
            for j in range(self.game.width):
                x = j * self.cell_size
                y = i * self.cell_size

                # Draw cell based on type
                if self.game.maze[i, j] == MazeGame.WALL:
                    pygame.draw.rect(self.screen, BLACK, (x, y, self.cell_size, self.cell_size))
                else:
                    pygame.draw.rect(self.screen, WHITE, (x, y, self.cell_size, self.cell_size))
                    pygame.draw.rect(self.screen, GRAY, (x, y, self.cell_size, self.cell_size), 1)

                # Draw exit
                if [i, j] == self.game.exit_pos:
                    pygame.draw.rect(self.screen, GREEN, (x + 5, y + 5, self.cell_size - 10, self.cell_size - 10))
                    text = self.font.render("EXIT", True, BLACK)
                    self.screen.blit(text, (x + 5, y + 15))

        # Draw coins
        for coin in self.game.coins:
            x = coin[1] * self.cell_size + self.cell_size // 2
            y = coin[0] * self.cell_size + self.cell_size // 2
            pygame.draw.circle(self.screen, YELLOW, (x, y), self.cell_size // 4)
            pygame.draw.circle(self.screen, ORANGE, (x, y), self.cell_size // 4, 2)

        # Draw NPC (enemy)
        npc_x = self.game.npc_pos[1] * self.cell_size + self.cell_size // 2
        npc_y = self.game.npc_pos[0] * self.cell_size + self.cell_size // 2
        pygame.draw.circle(self.screen, RED, (npc_x, npc_y), self.cell_size // 3)
        # Draw eyes
        eye_offset = self.cell_size // 8
        pygame.draw.circle(self.screen, WHITE, (npc_x - eye_offset, npc_y - eye_offset), 3)
        pygame.draw.circle(self.screen, WHITE, (npc_x + eye_offset, npc_y - eye_offset), 3)

        # Draw player (AI agent)
        player_x = self.game.player_pos[1] * self.cell_size + self.cell_size // 2
        player_y = self.game.player_pos[0] * self.cell_size + self.cell_size // 2
        pygame.draw.circle(self.screen, BLUE, (player_x, player_y), self.cell_size // 3)
        # Draw agent marker
        pygame.draw.circle(self.screen, WHITE, (player_x, player_y), self.cell_size // 6)

        # Draw info panel
        info_y = self.game.height * self.cell_size
        pygame.draw.rect(self.screen, GRAY, (0, info_y, self.width, 80))

        # Display stats
        score_text = self.font.render(f"Score: {self.game.score}", True, WHITE)
        steps_text = self.font.render(f"Steps: {self.game.steps}/{self.game.max_steps}", True, WHITE)
        coins_text = self.font.render(f"Coins: {len(self.game.coins)}", True, WHITE)

        self.screen.blit(score_text, (10, info_y + 10))
        self.screen.blit(steps_text, (10, info_y + 40))
        self.screen.blit(coins_text, (self.width - 120, info_y + 10))

        # Display game status
        if self.game.won:
            status_text = self.title_font.render("YOU WON!", True, GREEN)
            text_rect = status_text.get_rect(center=(self.width // 2, info_y + 30))
            self.screen.blit(status_text, text_rect)
        elif self.game.caught:
            status_text = self.title_font.render("CAUGHT!", True, RED)
            text_rect = status_text.get_rect(center=(self.width // 2, info_y + 30))
            self.screen.blit(status_text, text_rect)

        pygame.display.flip()

    def close(self):
        """Close the visualization"""
        pygame.quit()

def play_with_agent(model_path: str = "trained_agent.pkl",
                   maze_size: tuple = (10, 10),
                   num_coins: int = 5,
                   delay: float = 0.2,
                   num_games: int = 1):
    """
    Play the game with trained agent

    Args:
        model_path: Path to trained model
        maze_size: Size of the maze
        num_coins: Number of coins
        delay: Delay between steps (seconds)
        num_games: Number of games to play
    """
    # Initialize environment
    env = MazeGame(maze_size=maze_size, num_coins=num_coins)

    # Load trained agent
    agent = QLearningAgent()
    try:
        agent.load(model_path)
    except FileNotFoundError:
        print(f"Error: Model file '{model_path}' not found!")
        print("Please train the agent first by running: python train.py")
        sys.exit(1)

    # Initialize visualizer
    visualizer = MazeGameVisualizer(env, cell_size=50)

    print("=" * 60)
    print("Watching trained Q-learning agent play!")
    print("=" * 60)
    print("Controls:")
    print("  - Close window or press ESC to quit")
    print("  - Press SPACE to play another game")
    print("=" * 60)

    games_played = 0
    total_wins = 0
    total_score = 0

    running = True
    while running and games_played < num_games:
        # Reset game
        state_dict = env.reset()
        state = env.get_state_representation()
        done = False

        # Draw initial state
        visualizer.draw()
        time.sleep(0.5)

        # Play episode
        while not done and running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break

            if not running:
                break

            # Agent chooses action (no exploration during play)
            action = agent.get_action(state, training=False)

            # Take action
            state_dict, reward, done = env.step(action)
            state = env.get_state_representation()

            # Draw updated state
            visualizer.draw()
            visualizer.clock.tick(int(1 / delay))

            if done:
                time.sleep(1)  # Pause to show final state

        games_played += 1
        if state_dict['won']:
            total_wins += 1
        total_score += state_dict['score']

        print(f"\nGame {games_played} completed:")
        print(f"  Result: {'WON' if state_dict['won'] else 'CAUGHT' if state_dict['caught'] else 'TIMEOUT'}")
        print(f"  Score: {state_dict['score']}")
        print(f"  Steps: {state_dict['steps']}")

        # Wait for space bar or window close
        if games_played < num_games:
            print("\nPress SPACE for next game, or close window to quit...")
            waiting = True
            while waiting and running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            waiting = False
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                            waiting = False

    # Print summary
    if games_played > 0:
        print("\n" + "=" * 60)
        print("Summary:")
        print("=" * 60)
        print(f"Games played: {games_played}")
        print(f"Wins: {total_wins} ({total_wins/games_played*100:.1f}%)")
        print(f"Average score: {total_score/games_played:.1f}")

    visualizer.close()

def play_manual(maze_size: tuple = (10, 10), num_coins: int = 5):
    """
    Play the game manually (human player)

    Args:
        maze_size: Size of the maze
        num_coins: Number of coins
    """
    # Initialize environment
    env = MazeGame(maze_size=maze_size, num_coins=num_coins)

    # Initialize visualizer
    visualizer = MazeGameVisualizer(env, cell_size=50)

    print("=" * 60)
    print("Manual Play Mode")
    print("=" * 60)
    print("Controls:")
    print("  - Arrow keys to move")
    print("  - ESC to quit")
    print("  - R to restart")
    print("=" * 60)

    state_dict = env.reset()
    running = True

    while running:
        # Draw current state
        visualizer.draw()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                action = None
                if event.key == pygame.K_UP:
                    action = MazeGame.UP
                elif event.key == pygame.K_DOWN:
                    action = MazeGame.DOWN
                elif event.key == pygame.K_LEFT:
                    action = MazeGame.LEFT
                elif event.key == pygame.K_RIGHT:
                    action = MazeGame.RIGHT
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    state_dict = env.reset()
                    print("\nGame restarted!")

                if action is not None:
                    state_dict, reward, done = env.step(action)

                    if done:
                        print(f"\nGame Over!")
                        print(f"Result: {'WON' if state_dict['won'] else 'CAUGHT' if state_dict['caught'] else 'TIMEOUT'}")
                        print(f"Score: {state_dict['score']}")
                        print(f"Steps: {state_dict['steps']}")
                        print("Press R to restart or ESC to quit")

        visualizer.clock.tick(60)  # 60 FPS

    visualizer.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Play maze game with AI agent or manually')
    parser.add_argument('--mode', type=str, default='agent', choices=['agent', 'manual'],
                        help='Play mode: agent (watch AI) or manual (play yourself)')
    parser.add_argument('--model-path', type=str, default='trained_agent.pkl',
                        help='Path to trained model (default: trained_agent.pkl)')
    parser.add_argument('--maze-height', type=int, default=10,
                        help='Maze height (default: 10)')
    parser.add_argument('--maze-width', type=int, default=10,
                        help='Maze width (default: 10)')
    parser.add_argument('--coins', type=int, default=5,
                        help='Number of coins (default: 5)')
    parser.add_argument('--delay', type=float, default=0.2,
                        help='Delay between agent steps in seconds (default: 0.2)')
    parser.add_argument('--games', type=int, default=1,
                        help='Number of games to play (default: 1)')

    args = parser.parse_args()

    if args.mode == 'agent':
        play_with_agent(
            model_path=args.model_path,
            maze_size=(args.maze_height, args.maze_width),
            num_coins=args.coins,
            delay=args.delay,
            num_games=args.games
        )
    else:
        play_manual(
            maze_size=(args.maze_height, args.maze_width),
            num_coins=args.coins
        )
