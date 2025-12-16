from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import random
import pickle
import time
import pygame
from copy import deepcopy
from collections import deque

from src.Lava_Aqua.agents.base_agent import BaseAgent
from src.Lava_Aqua.core.constants import TRAINED_MODELS_DIR, Direction


class ReplayBuffer:
    """Experience replay buffer for DQN."""
    
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state: np.ndarray, action: int, reward: float, 
             next_state: np.ndarray, done: bool):
        """Add experience to buffer."""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size: int) -> Tuple[np.ndarray, ...]:
        """Sample random batch from buffer."""
        batch = random.sample(self.buffer, batch_size)
        
        states = np.array([exp[0] for exp in batch])
        actions = np.array([exp[1] for exp in batch])
        rewards = np.array([exp[2] for exp in batch])
        next_states = np.array([exp[3] for exp in batch])
        dones = np.array([exp[4] for exp in batch])
        
        return states, actions, rewards, next_states, dones
    
    def __len__(self):
        return len(self.buffer)


class DenseLayer:
    """Fully connected neural network layer."""
    
    def __init__(self, input_size: int, output_size: int):
        # He initialization
        self.weights = np.random.randn(input_size, output_size) * np.sqrt(2.0 / input_size)
        self.biases = np.zeros((1, output_size))
        
        # Cache for backprop
        self.input = None
        self.output = None
        
        # Gradients
        self.dw = None
        self.db = None
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass."""
        self.input = x
        self.output = np.dot(x, self.weights) + self.biases
        return self.output
    
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Backward pass."""
        batch_size = self.input.shape[0]
        
        # Gradients
        self.dw = np.dot(self.input.T, grad_output) / batch_size
        self.db = np.sum(grad_output, axis=0, keepdims=True) / batch_size
        
        # Gradient for previous layer
        grad_input = np.dot(grad_output, self.weights.T)
        return grad_input
    
    def update(self, learning_rate: float):
        """Update weights using gradients."""
        self.weights -= learning_rate * self.dw
        self.biases -= learning_rate * self.db


class ReLU:
    """ReLU activation function."""
    
    def __init__(self):
        self.mask = None
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass."""
        self.mask = x > 0
        return x * self.mask
    
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Backward pass."""
        return grad_output * self.mask


class NeuralNetwork:
    """Simple feedforward neural network."""
    
    def __init__(self, input_size: int, hidden_sizes: List[int], output_size: int):
        self.layers = []
        self.activations = []
        
        # Build network
        prev_size = input_size
        for hidden_size in hidden_sizes:
            self.layers.append(DenseLayer(prev_size, hidden_size))
            self.activations.append(ReLU())
            prev_size = hidden_size
        
        # Output layer (no activation)
        self.layers.append(DenseLayer(prev_size, output_size))
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass through network."""
        out = x
        for i, layer in enumerate(self.layers[:-1]):
            out = layer.forward(out)
            out = self.activations[i].forward(out)
        
        # Output layer
        out = self.layers[-1].forward(out)
        return out
    
    def backward(self, grad_output: np.ndarray):
        """Backward pass through network."""
        grad = grad_output
        
        # Output layer
        grad = self.layers[-1].backward(grad)
        
        # Hidden layers (reverse order)
        for i in range(len(self.layers) - 2, -1, -1):
            grad = self.activations[i].backward(grad)
            grad = self.layers[i].backward(grad)
    
    def update(self, learning_rate: float):
        """Update all layer weights."""
        for layer in self.layers:
            layer.update(learning_rate)
    
    def copy_weights_from(self, other: 'NeuralNetwork'):
        """Copy weights from another network (for target network)."""
        for self_layer, other_layer in zip(self.layers, other.layers):
            self_layer.weights = other_layer.weights.copy()
            self_layer.biases = other_layer.biases.copy()
    
    def get_weights(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Get all weights and biases."""
        return [(layer.weights.copy(), layer.biases.copy()) for layer in self.layers]
    
    def set_weights(self, weights: List[Tuple[np.ndarray, np.ndarray]]):
        """Set all weights and biases."""
        for layer, (w, b) in zip(self.layers, weights):
            layer.weights = w.copy()
            layer.biases = b.copy()


class DQNAgent(BaseAgent):
    """Deep Q-Network agent using only NumPy."""
    
    def __init__(
        self,
        state_shape: Tuple[int, int, int] = (10, 10, 6),
        hidden_sizes: List[int] = [128, 64],
        learning_rate: float = 0.001,
        gamma: float = 0.99,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        batch_size: int = 32,
        buffer_size: int = 10000,
        target_update_freq: int = 100,
        max_steps_per_episode: int = 500
    ):
        super().__init__("DQN Agent")
        
        # Hyperparameters
        self.state_shape = state_shape
        self.input_size = np.prod(state_shape)
        self.num_actions = 4
        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.max_steps = max_steps_per_episode
        
        # Networks
        self.q_network = NeuralNetwork(self.input_size, hidden_sizes, self.num_actions)
        self.target_network = NeuralNetwork(self.input_size, hidden_sizes, self.num_actions)
        self.target_network.copy_weights_from(self.q_network)
        
        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_size)
        
        # Statistics
        self.stats.update({
            'updates': 0,
            'current_epsilon': epsilon,
            'target_updates': 0
        })
    
    def _preprocess_observation(self, observation: np.ndarray) -> np.ndarray:
        """Flatten observation for neural network input."""
        return observation.flatten()
    
    def _select_action(self, state: np.ndarray, training: bool) -> int:
        """Select action using epsilon-greedy policy."""
        if training and random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)
        
        # Forward pass through Q-network
        state_batch = state.reshape(1, -1)
        q_values = self.q_network.forward(state_batch)[0]
        
        return int(np.argmax(q_values))
    
    def _train_step(self):
        """Perform one training step (if enough samples)."""
        if len(self.replay_buffer) < self.batch_size:
            return
        
        # Sample batch
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)
        
        # Compute target Q-values
        next_q_values = self.target_network.forward(next_states)
        max_next_q = np.max(next_q_values, axis=1)
        targets = rewards + self.gamma * max_next_q * (1 - dones)
        
        # Forward pass
        q_values = self.q_network.forward(states)
        
        # Compute loss gradient (MSE)
        q_pred = q_values[np.arange(self.batch_size), actions]
        errors = q_pred - targets
        
        # Backward pass
        grad_output = np.zeros_like(q_values)
        grad_output[np.arange(self.batch_size), actions] = 2 * errors
        
        self.q_network.backward(grad_output)
        self.q_network.update(self.lr)
        
        self.stats['updates'] += 1
        
        # Update target network periodically
        if self.stats['updates'] % self.target_update_freq == 0:
            self.target_network.copy_weights_from(self.q_network)
            self.stats['target_updates'] += 1
    
    def run_episode(
        self,
        game_logic,
        training: bool = False,
        visualize: bool = False,
        move_delay: float = 0.05,
        controller=None
    ) -> Dict[str, Any]:
        """Run a single episode."""
        simulation = deepcopy(game_logic)
        simulation.reset_level()
        
        actions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        
        episode_reward = 0.0
        steps = 0
        terminated = False
        
        # Get initial state
        observation = simulation.get_observation()
        state = self._preprocess_observation(observation)
        
        while steps < self.max_steps:
            # Select action
            action_idx = self._select_action(state, training)
            action = actions[action_idx]
            
            # Execute action
            move_success = simulation.move_player(action)
            reward = simulation.calculate_reward(move_success)
            
            # Get next state
            next_observation = simulation.get_observation()
            next_state = self._preprocess_observation(next_observation)
            
            done = simulation.level_complete or simulation.game_over
            
            # Store experience
            if training:
                self.replay_buffer.push(state, action_idx, reward, next_state, done)
                self._train_step()
            
            episode_reward += reward
            steps += 1
            self.stats['total_steps'] += 1
            
            # Visualization
            if visualize and controller:
                controller.render_frame()
                time.sleep(move_delay)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (
                        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                    ):
                        terminated = True
                        break
            
            state = next_state
            
            if done or terminated:
                break
        
        # Decay epsilon
        if training and self.epsilon > self.epsilon_min:
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
    
    def solve(self, game_logic) -> Tuple[List[Direction], int]:
        """Let model solve the game."""
        simulation = deepcopy(game_logic)
        simulation.reset_level()
        
        actions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        
        steps = 0
        path = []
        success = 0
        
        observation = simulation.get_observation()
        state = self._preprocess_observation(observation)
        
        while steps < self.max_steps:
            # Select best action (greedy)
            action_idx = self._select_action(state, training=False)
            action = actions[action_idx]
            
            path.append(action)
            
            # Execute action
            simulation.move_player(action)
            
            # Get next state
            next_observation = simulation.get_observation()
            state = self._preprocess_observation(next_observation)
            
            steps += 1
            
            if simulation.level_complete:
                success = 1
                break
            if simulation.game_over:
                break
        
        return path, success
    
    def save(self, filepath: str) -> None:
        """Save agent state."""
        save_path = TRAINED_MODELS_DIR / filepath if not filepath.startswith('/') else filepath
        
        save_data = {
            'q_network_weights': self.q_network.get_weights(),
            'target_network_weights': self.target_network.get_weights(),
            'epsilon': self.epsilon,
            'stats': self.stats,
            'hyperparameters': {
                'state_shape': self.state_shape,
                'hidden_sizes': [128, 64],  # Store for reconstruction
                'lr': self.lr,
                'gamma': self.gamma,
                'epsilon_decay': self.epsilon_decay,
                'epsilon_min': self.epsilon_min,
                'batch_size': self.batch_size,
                'target_update_freq': self.target_update_freq
            }
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(save_data, f)
        
        print(f"💾 DQN Agent saved: {self.stats['updates']} updates, "
              f"{len(self.replay_buffer)} experiences")
    
    def load(self, filepath: str) -> None:
        """Load agent state."""
        with open(filepath, 'rb') as f:
            save_data = pickle.load(f)
        
        self.q_network.set_weights(save_data['q_network_weights'])
        self.target_network.set_weights(save_data['target_network_weights'])
        self.epsilon = save_data.get('epsilon', self.epsilon_min)
        self.stats = save_data.get('stats', self.stats)
        
        if 'hyperparameters' in save_data:
            hyper = save_data['hyperparameters']
            self.lr = hyper.get('lr', self.lr)
            self.gamma = hyper.get('gamma', self.gamma)
        
        print(f"📂 DQN Agent loaded: {self.stats['updates']} updates, "
              f"ε={self.epsilon:.4f}")