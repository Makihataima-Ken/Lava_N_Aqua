from typing import Dict, Any, List
import numpy as np
import random
import pickle
import time
import pygame
from copy import deepcopy

from src.Lava_Aqua.agents.base_agent import BaseAgent
from src.Lava_Aqua.core.constants import ASSETS_DIR, Direction


class QLearningAgent(BaseAgent):
    """
    Q-Learning agent - simplified to match solver pattern.
    
    The agent has full control over the game logic and manages
    its own training loop, just like DFS/BFS solvers.
    """
    
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
    
    def _state_to_hash(self, game_logic) -> str:
        """
        Convert game state to a hash string.
        Similar to BaseSolver._hash_state()
        """
        state = game_logic.get_state()
        
        # Simple hash of key components
        player_hash = str(state.player_pos)
        boxes_hash = str(sorted(state.box_positions))
        lava_hash = str(sorted(state.lava_positions))
        aqua_hash = str(sorted(state.aqua_positions))
        keys_hash = str(sorted(state.collected_key_indices))
        
        return f"{player_hash}|{boxes_hash}|{lava_hash}|{aqua_hash}|{keys_hash}"
    
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
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            self.stats['current_epsilon'] = self.epsilon
    
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
        Simple and clean like DFS solve().
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
            state_hash = self._state_to_hash(simulation)
            
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
            next_state_hash = self._state_to_hash(simulation)
            
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
        
        self.stats['total_episodes'] += 1
        
        return {
            'steps': steps,
            'total_reward': episode_reward,
            'level_complete': simulation.level_complete,
            'game_over': simulation.game_over,
            'terminated': terminated
        }
    
    def train(
        self,
        game_logic,
        num_episodes: int,
        eval_frequency: int = 100,
        visualize: bool = False,
        move_delay: float = 0.05,
        controller=None
    ) -> Dict[str, Any]:
        """
        Train the agent.
        Simple training loop like your DFS solver.
        """
        episode_rewards: List[float] = []
        episode_lengths: List[int] = []
        
        for episode in range(1, num_episodes + 1):
            result = self.run_episode(
                game_logic=game_logic,
                training=True,
                visualize=visualize,
                move_delay=move_delay,
                controller=controller
            )
            
            episode_rewards.append(result['total_reward'])
            episode_lengths.append(result['steps'])
            
            # Logging
            if episode % 10 == 0:
                avg_reward = np.mean(episode_rewards[-10:])
                avg_length = np.mean(episode_lengths[-10:])
                print(
                    f"Episode {episode}/{num_episodes} | "
                    f"Reward: {avg_reward:.2f} | "
                    f"Steps: {avg_length:.1f} | "
                    f"ε: {self.epsilon:.4f} | "
                    f"States: {self.stats['unique_states']}"
                )
            
            # Evaluation
            if episode % eval_frequency == 0:
                eval_stats = self.evaluate(
                    game_logic=game_logic,
                    num_episodes=10,
                    visualize=False,
                    controller=controller
                )
                print(f"  Eval - Success: {eval_stats['success_rate']:.1%}, "
                      f"Reward: {eval_stats['avg_reward']:.2f}")
        
        return {
            'episode_rewards': episode_rewards,
            'episode_lengths': episode_lengths
        }
    
    def evaluate(
        self,
        game_logic,
        num_episodes: int = 100,
        visualize: bool = False,
        move_delay: float = 0.05,
        controller=None
    ) -> Dict[str, Any]:
        """Evaluate the agent without training."""
        eval_rewards = []
        eval_lengths = []
        success_count = 0
        
        for _ in range(num_episodes):
            result = self.run_episode(
                game_logic=game_logic,
                training=False,
                visualize=visualize,
                move_delay=move_delay,
                controller=controller
            )
            
            eval_rewards.append(result['total_reward'])
            eval_lengths.append(result['steps'])
            if result['level_complete']:
                success_count += 1
        
        return {
            'num_episodes': num_episodes,
            'success_rate': success_count / num_episodes,
            'success_count': success_count,
            'avg_reward': np.mean(eval_rewards),
            'std_reward': np.std(eval_rewards),
            'avg_steps': np.mean(eval_lengths),
            'std_steps': np.std(eval_lengths)
        }
    
    def save(self, filepath: str) -> None:
        """Save Q-table and agent state."""
        save_path = ASSETS_DIR / filepath if not filepath.startswith('/') else filepath
        
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