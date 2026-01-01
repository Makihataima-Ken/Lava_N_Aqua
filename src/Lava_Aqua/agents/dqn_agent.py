from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import random
import pickle
import time
import pygame
from copy import deepcopy
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

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

    def sample(self, batch_size: int, device: torch.device) -> Tuple[torch.Tensor, ...]:
        """Sample random batch from buffer and convert to tensors."""
        batch = random.sample(self.buffer, batch_size)

        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.from_numpy(np.array(states)).float().to(device)
        actions = torch.from_numpy(np.array(actions)).long().to(device)
        rewards = torch.from_numpy(np.array(rewards)).float().to(device)
        next_states = torch.from_numpy(np.array(next_states)).float().to(device)
        dones = torch.from_numpy(np.array(dones).astype(np.uint8)).float().to(device)

        return states, actions, rewards, next_states, dones

    def __len__(self):
        return len(self.buffer)

class NeuralNetwork(nn.Module):
    """Feedforward neural network using PyTorch."""

    def __init__(self, input_size: int, hidden_sizes: List[int], output_size: int):
        super(NeuralNetwork, self).__init__()
        layers = []
        prev_size = input_size
        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            prev_size = hidden_size
        layers.append(nn.Linear(prev_size, output_size))
        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through network."""
        return self.network(x)

class DQNAgent(BaseAgent):
    """Deep Q-Network agent using PyTorch."""

    def __init__(
        self,
        state_shape: Tuple[int, int, int] = (10, 10, 6),
        hidden_sizes: List[int] = [128, 64],
        learning_rate: float = 0.001,
        gamma: float = 0.99,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.999,
        epsilon_min: float = 0.05,
        batch_size: int = 32,
        buffer_size: int = 10000,
        target_update_freq: int = 100,
        max_steps_per_episode: int = 60
    ):
        super().__init__("DQN")

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

        # Device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Networks
        self.q_network = NeuralNetwork(self.input_size, hidden_sizes, self.num_actions).to(self.device)
        self.target_network = NeuralNetwork(self.input_size, hidden_sizes, self.num_actions).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()

        # Optimizer
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=self.lr)

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

        with torch.no_grad():
            state_tensor = torch.from_numpy(state).float().unsqueeze(0).to(self.device)
            q_values = self.q_network(state_tensor)
            return q_values.argmax().item()

    def _train_step(self):
        """Perform one training step (if enough samples)."""
        if len(self.replay_buffer) < self.batch_size:
            return

        # Sample batch
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size, self.device)

        # Compute target Q-values
        with torch.no_grad():
            next_q_values = self.target_network(next_states)
            max_next_q = next_q_values.max(1)[0]
            targets = rewards + self.gamma * max_next_q * (1 - dones)

        # Compute Q-values
        q_values = self.q_network(states)
        q_pred = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)

        # Compute loss
        loss = F.mse_loss(q_pred, targets)

        # Backward pass and optimization
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.stats['updates'] += 1

        # Update target network periodically
        if self.stats['updates'] % self.target_update_freq == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
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
        prev_state = simulation.get_state()

        while steps < self.max_steps:
            # Select action
            action_idx = self._select_action(state, training)
            action = actions[action_idx]

            # Execute action
            move_success = simulation.move_player(action)
            reward = simulation.calculate_reward(move_success, prev_state)

            reward = np.clip(reward, -10.0, 10.0)
            prev_state = simulation.get_state()

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
            'q_network_state_dict': self.q_network.state_dict(),
            'target_network_state_dict': self.target_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'stats': self.stats,
            'hyperparameters': {
                'state_shape': self.state_shape,
                'hidden_sizes': [layer.out_features for layer in self.q_network.network if isinstance(layer, nn.Linear)][:-1],
                'lr': self.lr,
                'gamma': self.gamma,
                'epsilon_decay': self.epsilon_decay,
                'epsilon_min': self.epsilon_min,
                'batch_size': self.batch_size,
                'target_update_freq': self.target_update_freq
            }
        }

        torch.save(save_data, save_path)

        print(f"💾 DQN Agent saved: {self.stats['updates']} updates, "
              f"{len(self.replay_buffer)} experiences")

    def load(self, filepath: str) -> None:
        """Load agent state."""
        save_data = torch.load(filepath, map_location=self.device)

        self.q_network.load_state_dict(save_data['q_network_state_dict'])
        self.target_network.load_state_dict(save_data['target_network_state_dict'])
        self.optimizer.load_state_dict(save_data['optimizer_state_dict'])
        self.epsilon = save_data.get('epsilon', self.epsilon_min)
        self.stats = save_data.get('stats', self.stats)

        if 'hyperparameters' in save_data:
            hyper = save_data['hyperparameters']
            self.lr = hyper.get('lr', self.lr)
            self.gamma = hyper.get('gamma', self.gamma)

        print(f"📂 DQN Agent loaded: {self.stats['updates']} updates, "
              f"ε={self.epsilon:.4f}")

