#!/usr/bin/env python3
"""
Quick demo script to test the game without training
Shows a few episodes with random agent for testing
"""

from maze_game import MazeGame
import random
import time

def demo_game(num_episodes: int = 3):
    """Run a quick demo with random actions"""
    print("="*60)
    print("MAZE GAME QUICK DEMO")
    print("="*60)
    print("This demo runs a few episodes with random actions")
    print("to demonstrate the game mechanics.")
    print("="*60)

    env = MazeGame(maze_size=(8, 8), num_coins=3)

    for episode in range(num_episodes):
        print(f"\n\nEpisode {episode + 1}/{num_episodes}")
        print("-"*60)

        state = env.reset()
        env.render_text()
        time.sleep(1)

        done = False
        total_reward = 0

        while not done:
            # Random action
            action = random.choice(env.ACTIONS)
            action_names = {0: "UP", 1: "DOWN", 2: "LEFT", 3: "RIGHT"}

            state, reward, done = env.step(action)
            total_reward += reward

            print(f"\nAction: {action_names[action]} | Reward: {reward:.1f}")
            env.render_text()
            time.sleep(0.5)

            if done:
                print("\n" + "="*60)
                if state['won']:
                    print("RESULT: WON!")
                elif state['caught']:
                    print("RESULT: CAUGHT BY NPC!")
                else:
                    print("RESULT: TIMEOUT!")
                print(f"Total Reward: {total_reward:.1f}")
                print(f"Final Score: {state['score']}")
                print(f"Steps: {state['steps']}")
                print("="*60)

    print("\n\nDemo completed!")
    print("\nTo train the Q-learning agent:")
    print("  python train.py")
    print("\nTo watch the trained agent play:")
    print("  python play.py --mode agent")
    print("\nTo play manually:")
    print("  python play.py --mode manual")

if __name__ == "__main__":
    demo_game()
