from typing import Dict, Any, List, Optional
import numpy as np
import random
import pickle
import time
import pygame
from copy import deepcopy

from src.Lava_Aqua.agents.base_agent import BaseAgent
from src.Lava_Aqua.core.constants import TRAINED_MODELS_DIR, Direction


class QLearningAgent(BaseAgent):
    """ Q-Learning agent Implementation """
    
    def __init__(
        self,
        learning_rate: float = 0.2,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.998,
        epsilon_min: float = 0.05,
        max_steps_per_episode: int = 500
    ):
        super().__init__("Q-Learning Agent")
        
        # Q-Learning hyperparameters
        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.initial_epsilon = epsilon
        self.max_steps = max_steps_per_episode
        
        # Q-table: state_hash -> [Q(s,a) for each action]
        self.q_table: Dict[str, np.ndarray] = {}
        self.num_actions = 4  # UP, DOWN, LEFT, RIGHT
        
        # Statistics
        self.stats.update({
            'unique_states': 0,
            'q_updates': 0,
            'current_epsilon': epsilon
        })
    
    def _get_q_values(self, state_hash: str) -> np.ndarray:
        """Get Q-values for a state, initializing if new."""
        if state_hash not in self.q_table:
            self.q_table[state_hash] = np.zeros(self.num_actions)
            self.stats['unique_states'] += 1
        return self.q_table[state_hash]
    
    def _select_action(self, state_hash: str, training: bool) -> int:
        """Select action using epsilon-greedy policy."""
        q_values = self._get_q_values(state_hash)
        
        # Exploration vs exploitation
        if training and random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)
        
        # Break ties randomly
        if np.all(q_values == q_values[0]):
            return random.randint(0, self.num_actions - 1)
        
        return int(np.argmax(q_values))
    
    def _update_q_value(
        self, 
        state_hash: str, 
        action: int, 
        reward: float, 
        next_state_hash: str, 
        done: bool
    ) -> None:
        """Update Q-value using Q-learning rule."""
        q_values = self._get_q_values(state_hash)
        next_q_values = self._get_q_values(next_state_hash)
        
        # Q-learning update
        if done:
            target = reward
        else:
            target = reward + self.gamma * np.max(next_q_values)
        
        q_values[action] += self.lr * (target - q_values[action])
        self.stats['q_updates'] += 1
    
    def run_episode(
        self,
        game_logic,
        training: bool = False,
        visualize: bool = False,
        move_delay: float = 0.05,
        controller=None
    ) -> Dict[str, Any]:
        """
        Run a single episode.
        """
        # Use a copy for simulation
        simulation = deepcopy(game_logic)
        simulation.reset_level()
        
        # Action mapping
        actions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        
        episode_reward = 0.0
        steps = 0
        terminated = False
        
        while steps < self.max_steps:
            # Get current state
            state_hash = self._hash_state(simulation.get_state())
            
            # Select action
            action_idx = self._select_action(state_hash, training)
            action = actions[action_idx]
            
            # Execute action
            move_success = simulation.move_player(action)
            reward = simulation.calculate_reward(move_success)
            
            episode_reward += reward
            steps += 1
            self.stats['total_steps'] += 1
            
            # Get next state
            next_state_hash = self._hash_state(simulation.get_state())
            
            # Learn (if training)
            done = simulation.level_complete or simulation.game_over
            if training:
                self._update_q_value(state_hash, action_idx, reward, next_state_hash, done)
            
            # Visualization
            if visualize and controller:
                controller.render_frame()
                time.sleep(move_delay)
                
                # Check for quit
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (
                        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                    ):
                        terminated = True
                        break
            
            
            if done or terminated:
                break
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            self.stats['current_epsilon'] = self.epsilon
            
        self.stats['total_episodes'] += 1
        
        return {
            'steps': steps,
            'total_reward': episode_reward,
            'level_complete': simulation.level_complete,
            'game_over': simulation.game_over,
            'terminated': terminated
        }
        
    def solve(
        self,
        game_logic,
    ) -> Optional[List[Direction]]:
        """
            let model solve the game
        """
        # Use a copy for simulation
        simulation = deepcopy(game_logic)
        simulation.reset_level()
        
        # Action mapping
        actions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        
        steps = 0
        
        path =[]
        
        success = 0
        
        while steps < self.max_steps:
            # Get current state
            state_hash = self._hash_state(simulation.get_state())
            
            # Select action
            action_idx = self._select_action(state_hash,training=False)
            action = actions[action_idx]
            
            path.append(action)
            
            # Execute action
            simulation.move_player(action)

            steps += 1 
            
            if simulation.level_complete:
                success = 1 
                break
            if simulation.game_over:
                break
            
        return path,success
    
    def save(self, filepath: str) -> None:
        """Save Q-table and agent state."""
        save_path = TRAINED_MODELS_DIR/ filepath if not filepath.startswith('/') else filepath
        
        save_data = {
            'q_table': self.q_table,
            'epsilon': self.epsilon,
            'stats': self.stats,
            'hyperparameters': {
                'lr': self.lr,
                'gamma': self.gamma,
                'epsilon_decay': self.epsilon_decay,
                'epsilon_min': self.epsilon_min,
            }
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(save_data, f)
        
        print(f"💾 Agent saved: {self.stats['unique_states']} states, "
              f"{self.stats['q_updates']} updates")
    
    def load(self, filepath: str) -> None:
        """Load Q-table and agent state."""
        with open(filepath, 'rb') as f:
            save_data = pickle.load(f)
        
        self.q_table = save_data['q_table']
        self.epsilon = save_data.get('epsilon', self.epsilon_min)
        self.stats = save_data.get('stats', self.stats)
        
        if 'hyperparameters' in save_data:
            hyper = save_data['hyperparameters']
            self.lr = hyper.get('lr', self.lr)
            self.gamma = hyper.get('gamma', self.gamma)
        
        print(f"📂 Agent loaded: {self.stats['unique_states']} states, "
              f"ε={self.epsilon:.4f}")