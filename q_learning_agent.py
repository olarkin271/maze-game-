import numpy as np
import random
import pickle
from typing import Dict, Tuple
from collections import defaultdict

class QLearningAgent:
    """
    Q-Learning agent that learns to navigate the maze,
    avoid the NPC, and collect coins to maximize score
    """

    def __init__(self,
                 n_actions: int = 4,
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.95,
                 epsilon: float = 1.0,
                 epsilon_min: float = 0.01,
                 epsilon_decay: float = 0.995):
        """
        Initialize Q-Learning agent

        Args:
            n_actions: Number of possible actions
            learning_rate: Learning rate (alpha)
            discount_factor: Discount factor (gamma)
            epsilon: Initial exploration rate
            epsilon_min: Minimum exploration rate
            epsilon_decay: Epsilon decay rate per episode
        """
        self.n_actions = n_actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        # Q-table: maps (state, action) -> Q-value
        # Using defaultdict for automatic initialization
        self.q_table: Dict[Tuple, np.ndarray] = defaultdict(lambda: np.zeros(n_actions))

        # Statistics
        self.total_episodes = 0
        self.total_steps = 0

    def get_action(self, state: Tuple, training: bool = True) -> int:
        """
        Choose an action using epsilon-greedy policy

        Args:
            state: Current state representation
            training: If True, use epsilon-greedy; if False, use greedy

        Returns:
            Selected action
        """
        # Epsilon-greedy action selection
        if training and random.random() < self.epsilon:
            # Explore: random action
            return random.randint(0, self.n_actions - 1)
        else:
            # Exploit: best known action
            q_values = self.q_table[state]
            # If multiple actions have the same max Q-value, choose randomly among them
            max_q = np.max(q_values)
            best_actions = np.where(q_values == max_q)[0]
            return np.random.choice(best_actions)

    def update(self, state: Tuple, action: int, reward: float,
               next_state: Tuple, done: bool):
        """
        Update Q-value using the Q-learning update rule

        Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]
        """
        current_q = self.q_table[state][action]

        if done:
            # If episode is done, there's no next state
            target_q = reward
        else:
            # Get max Q-value for next state
            next_max_q = np.max(self.q_table[next_state])
            target_q = reward + self.discount_factor * next_max_q

        # Update Q-value
        self.q_table[state][action] = current_q + self.learning_rate * (target_q - current_q)

    def decay_epsilon(self):
        """Decay epsilon after each episode"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self.total_episodes += 1

    def save(self, filepath: str):
        """Save Q-table and parameters to file"""
        data = {
            'q_table': dict(self.q_table),  # Convert defaultdict to regular dict
            'epsilon': self.epsilon,
            'total_episodes': self.total_episodes,
            'total_steps': self.total_steps,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'epsilon_min': self.epsilon_min,
            'epsilon_decay': self.epsilon_decay,
            'n_actions': self.n_actions
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        print(f"Agent saved to {filepath}")

    def load(self, filepath: str):
        """Load Q-table and parameters from file"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        # Restore Q-table
        self.q_table = defaultdict(lambda: np.zeros(self.n_actions))
        for state, q_values in data['q_table'].items():
            self.q_table[state] = q_values

        # Restore parameters
        self.epsilon = data['epsilon']
        self.total_episodes = data['total_episodes']
        self.total_steps = data['total_steps']
        self.learning_rate = data['learning_rate']
        self.discount_factor = data['discount_factor']
        self.epsilon_min = data['epsilon_min']
        self.epsilon_decay = data['epsilon_decay']
        self.n_actions = data['n_actions']

        print(f"Agent loaded from {filepath}")
        print(f"Episodes trained: {self.total_episodes}")
        print(f"Current epsilon: {self.epsilon:.4f}")

    def get_stats(self) -> Dict:
        """Get statistics about the agent"""
        return {
            'total_episodes': self.total_episodes,
            'total_steps': self.total_steps,
            'epsilon': self.epsilon,
            'q_table_size': len(self.q_table)
        }
