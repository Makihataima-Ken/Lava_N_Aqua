from typing import Dict, Any, Tuple
import numpy as np
import random
from collections import deque
from src.Lava_Aqua.agents.base_agent import BaseAgent
from src.Lava_Aqua.core.constants import ASSETS_DIR

class QLearningAgent(BaseAgent):
    """
    Improved Q-Learning agent with state discretization.
    
    Uses a simplified state representation to make the state space manageable.
    """
    
    def __init__(
        self, 
        state_shape: Tuple[int, ...], 
        num_actions: int = 4,
        learning_rate: float = 0.2,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.998,
        epsilon_min: float = 0.05
    ):
        super().__init__("Improved Q-Learning Agent", state_shape, num_actions)
        
        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Q-table: state_hash -> [Q(s,a) for each action]
        self.q_table: Dict[int, np.ndarray] = {}
        
        # Track statistics
        self.updates = 0
        self.unique_states = 0
    
    def _discretize_state(self, state: np.ndarray) -> Tuple:
        """
        Convert continuous state to discrete representation.
        
        Instead of hashing the entire grid, extract key features:
        - Player position
        - Relative positions of nearby lava/boxes/aqua
        - Distance to exit
        """
        height, width, channels = state.shape
        
        # Extract player position
        player_layer = state[:, :, 1]
        player_pos = np.argwhere(player_layer == 1.0)
        if len(player_pos) == 0:
            player_pos = (0, 0)
        else:
            player_pos = tuple(player_pos[0])
        
        # Extract exit position
        exit_layer = state[:, :, 5]
        exit_pos = np.argwhere(exit_layer == 1.0)
        if len(exit_pos) == 0:
            exit_pos = (0, 0)
        else:
            exit_pos = tuple(exit_pos[0])
        
        # Relative exit position (discretized into 8 directions + distance buckets)
        dx = exit_pos[0] - player_pos[0]
        dy = exit_pos[1] - player_pos[1]
        distance_bucket = min(abs(dx) + abs(dy), 20) // 5  # 0-4 buckets
        
        direction = 0
        if dx > 0:
            direction += 1
        elif dx < 0:
            direction += 2
        if dy > 0:
            direction += 4
        elif dy < 0:
            direction += 8
        
        # Check immediate surroundings (4 directions)
        surroundings = []
        for drow, dcol in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = player_pos[0] + drow, player_pos[1] + dcol
            
            if 0 <= new_row < height and 0 <= new_col < width:
                cell_state = 0
                # Wall
                if state[new_row, new_col, 0] == 1.0:
                    cell_state = 1
                # Box
                elif state[new_row, new_col, 2] == 1.0:
                    cell_state = 2
                # Lava
                elif state[new_row, new_col, 3] == 1.0:
                    cell_state = 3
                # Aqua
                elif state[new_row, new_col, 4] == 1.0:
                    cell_state = 4
                surroundings.append(cell_state)
            else:
                surroundings.append(1)  # Out of bounds = wall
        
        # Count dangerous tiles in wider area (within 2 cells)
        lava_count = 0
        box_count = 0
        for i in range(max(0, player_pos[0] - 2), min(height, player_pos[0] + 3)):
            for j in range(max(0, player_pos[1] - 2), min(width, player_pos[1] + 3)):
                if state[i, j, 3] == 1.0:  # Lava
                    lava_count += 1
                if state[i, j, 2] == 1.0:  # Box
                    box_count += 1
        
        lava_bucket = min(lava_count, 5)
        box_bucket = min(box_count, 3)
        
        return (player_pos, direction, distance_bucket, 
                tuple(surroundings), lava_bucket, box_bucket)
    
    def _get_q_values(self, state: np.ndarray) -> np.ndarray:
        """Get Q-values for state."""
        state_key = self._discretize_state(state)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.num_actions)
            self.unique_states += 1
        
        return self.q_table[state_key]
    
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """Epsilon-greedy action selection."""
        if training and random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)
        
        q_values = self._get_q_values(state)
        
        # Add small random noise to break ties
        if np.all(q_values == q_values[0]):
            return random.randint(0, self.num_actions - 1)
        
        return int(np.argmax(q_values))
    
    def learn(self, state, action, reward, next_state, done) -> None:
        """Q-Learning update with improved learning."""
        q_values = self._get_q_values(state)
        next_q_values = self._get_q_values(next_state)
        
        # Q-Learning update rule
        if done:
            target = reward
        else:
            target = reward + self.gamma * np.max(next_q_values)
        
        # TD error
        td_error = target - q_values[action]
        
        # Update Q-value
        q_values[action] += self.lr * td_error
        
        self.updates += 1
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def save(self, filepath: str) -> None:
        """Save Q-table."""
        import pickle
        save_path = ASSETS_DIR / filepath
        with open(save_path, 'wb') as f:
            pickle.dump({
                'q_table': self.q_table,
                'epsilon': self.epsilon,
                'updates': self.updates,
                'unique_states': self.unique_states
            }, f)
        print(f"Saved {self.unique_states} unique states")
    
    def load(self, filepath: str) -> None:
        """Load Q-table."""
        import pickle
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.q_table = data['q_table']
            self.epsilon = data.get('epsilon', self.epsilon_min)
            self.updates = data.get('updates', 0)
            self.unique_states = data.get('unique_states', len(self.q_table))
        print(f"Loaded {self.unique_states} unique states")