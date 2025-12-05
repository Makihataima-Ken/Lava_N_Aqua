from typing import Dict, Any, Tuple
import numpy as np
import random
from collections import deque
from src.Lava_Aqua.agents.base_agent import BaseAgent

class QLearningAgent(BaseAgent):
    """
    Tabular Q-Learning agent.
    
    Works by discretizing the state space and maintaining a Q-table.
    Good for small state spaces.
    """
    
    def __init__(
        self, 
        state_shape: Tuple[int, ...], 
        num_actions: int = 4,
        learning_rate: float = 0.1,
        gamma: float = 0.99,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01
    ):
        super().__init__("Q-Learning Agent", state_shape, num_actions)
        
        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Q-table: state_hash -> [Q(s,a) for each action]
        self.q_table: Dict[int, np.ndarray] = {}
    
    def _hash_state(self, state: np.ndarray) -> int:
        """Convert state to hash for Q-table lookup."""
        # Simple hash - you may want something more sophisticated
        return hash(state.tobytes())
    
    def _get_q_values(self, state: np.ndarray) -> np.ndarray:
        """Get Q-values for state."""
        state_hash = self._hash_state(state)
        if state_hash not in self.q_table:
            self.q_table[state_hash] = np.zeros(self.num_actions)
        return self.q_table[state_hash]
    
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """Epsilon-greedy action selection."""
        if training and random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)
        
        q_values = self._get_q_values(state)
        return int(np.argmax(q_values))
    
    def learn(self, state, action, reward, next_state, done) -> None:
        """Q-Learning update."""
        q_values = self._get_q_values(state)
        next_q_values = self._get_q_values(next_state)
        
        # Q-Learning update rule
        if done:
            target = reward
        else:
            target = reward + self.gamma * np.max(next_q_values)
        
        q_values[action] += self.lr * (target - q_values[action])
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def save(self, filepath: str) -> None:
        """Save Q-table."""
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump({
                'q_table': self.q_table,
                'epsilon': self.epsilon
            }, f)
    
    def load(self, filepath: str) -> None:
        """Load Q-table."""
        import pickle
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.q_table = data['q_table']
            self.epsilon = data['epsilon']