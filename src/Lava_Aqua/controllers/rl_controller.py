from typing import Optional, Dict, Any, Tuple
import time
import pygame
import numpy as np
from copy import deepcopy

from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.core.constants import Direction, GameResult
from .base_controller import BaseController

from src.Lava_Aqua.agents.base_agent import BaseAgent


class RLController(BaseController):
    """
    Controller for Reinforcement Learning agent.
    
    This controller interfaces between the RL agent and the game,
    handling training episodes, evaluation, and rendering.
    """
    
    def __init__(
        self, 
        game_logic: GameLogic,
        agent: BaseAgent,
        move_delay: float = 0.05,
        max_steps_per_episode: int = 500
    ):
        """
        Initialize RL controller.
        
        Args:
            game_logic: Game logic instance
            agent: RL agent to train/evaluate
            move_delay: Delay between moves (for visualization)
            max_steps_per_episode: Maximum steps before episode ends
        """
        super().__init__(game_logic)
        self.agent = agent
        self.move_delay = move_delay
        self.max_steps_per_episode = max_steps_per_episode
        
        # Episode tracking
        self.episode_count = 0
        self.total_steps = 0
        self.episode_rewards = []
        self.episode_lengths = []
        
        # Current episode state
        self.current_episode_reward = 0.0
        self.current_episode_steps = 0
    
    def reset_episode(self) -> np.ndarray:
        """
        Reset environment for new episode.
        
        Returns:
            Initial state observation
        """
        self.game_logic.reset_level()
        self.current_episode_reward = 0.0
        self.current_episode_steps = 0
        
        return self.game_logic.get_observation()
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """
        Execute one step in the environment (OpenAI Gym style).
        
        Args:
            action: Action index (0=UP, 1=DOWN, 2=LEFT, 3=RIGHT)
            
        Returns:
            observation: Next state
            reward: Reward for this step
            done: Whether episode is complete
            info: Additional information
        """
        # Map action to direction
        directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        direction = directions[action]
        
        # Calculate reward
        reward = self.game_logic.calculate_reward(direction=direction)
        
        # Update counters
        self.current_episode_steps += 1
        self.current_episode_reward += reward
        self.total_steps += 1
        
        # Check if episode is done
        done = (
            self.game_logic.level_complete or 
            self.game_logic.game_over or 
            self.current_episode_steps >= self.max_steps_per_episode
        )
        
        # Get next observation
        next_observation = self.game_logic.get_observation()
        
        # Additional info
        info = {
            # 'move_successful': move_successful,
            'level_complete': self.game_logic.level_complete,
            'game_over': self.game_logic.game_over,
            'steps': self.current_episode_steps,
            'total_reward': self.current_episode_reward
        }
        
        return next_observation, reward, done, info
    
    def run_episode(self,training_mode:bool = False, visualize:bool =False ) -> Dict[str, Any]:
        """
        Run a complete episode (training or evaluation).
        
        Returns:
            Episode statistics
        """
        observation = self.reset_episode()
        done = False
        
        while not done:
            # Agent selects action
            action = self.agent.select_action(observation, training=training_mode)
            
            # Execute action
            next_observation, reward, done, info = self.step(action)
            
            # Agent learns from transition (if training)
            if training_mode:
                self.agent.learn(observation, action, reward, next_observation, done)
            
            # Update observation
            observation = next_observation
            
            # Check for quit events
            if visualize:
                
                self.render_frame()
                time.sleep(self.move_delay)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (
                        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                    ):
                        return self._get_episode_stats(terminated=True)
        
        # Episode complete
        self.episode_count += 1
        self.episode_rewards.append(self.current_episode_reward)
        self.episode_lengths.append(self.current_episode_steps)
        
        return self._get_episode_stats()
    
    def train(self, num_episodes: int, eval_frequency: int = 100) -> Dict[str, Any]:
        """
        Train the agent for multiple episodes.
        
        Args:
            num_episodes: Number of training episodes
            eval_frequency: Evaluate agent every N episodes
            
        Returns:
            Training statistics
        """
        print(f"\n{'='*70}")
        print(f"🎓 TRAINING RL AGENT")
        print(f"{'='*70}")
        print(f"Episodes: {num_episodes}")
        print(f"Level: {self.game_logic.get_level_description()}")
        print(f"Agent: {self.agent.name}")
        print()
        
        training_start = time.time()
        
        for episode in range(1, num_episodes + 1):
            stats = self.run_episode()
            
            # Logging
            if episode % 10 == 0:
                avg_reward = np.mean(self.episode_rewards[-10:])
                avg_length = np.mean(self.episode_lengths[-10:])
                
                print(
                    f"Episode {episode}/{num_episodes} | "
                    f"Avg Reward: {avg_reward:.2f} | "
                    f"Avg Length: {avg_length:.1f} | "
                    f"Success: {stats['level_complete']}"
                )
            
            # Evaluation
            if episode % eval_frequency == 0:
                eval_stats = self.evaluate(num_episodes=10, visualize=False)
                print(f"\n📊 Evaluation after {episode} episodes:")
                print(f"  Success Rate: {eval_stats['success_rate']:.1%}")
                print(f"  Avg Reward: {eval_stats['avg_reward']:.2f}")
                print(f"  Avg Steps: {eval_stats['avg_steps']:.1f}\n")
        
        training_time = time.time() - training_start
        
        print(f"\n{'='*70}")
        print(f"✓ Training Complete")
        print(f"  Total time: {training_time:.1f}s")
        print(f"  Total steps: {self.total_steps}")
        print(f"{'='*70}")
        
        return {
            'training_time': training_time,
            'total_episodes': num_episodes,
            'total_steps': self.total_steps,
            'episode_rewards': self.episode_rewards,
            'episode_lengths': self.episode_lengths
        }
    
    def evaluate(
        self, 
        num_episodes: int = 100, 
        visualize: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate the agent without training.
        
        Args:
            num_episodes: Number of evaluation episodes
            visualize: Whether to render evaluation
            
        Returns:
            Evaluation statistics
        """
        
        eval_rewards = []
        eval_lengths = []
        success_count = 0
        
        for _ in range(num_episodes):
            stats = self.run_episode()
            eval_rewards.append(stats['total_reward'])
            eval_lengths.append(stats['steps'])
            if stats['level_complete']:
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
    
    def _get_episode_stats(self, terminated: bool = False) -> Dict[str, Any]:
        """Get statistics for completed episode."""
        return {
            'episode': self.episode_count,
            'steps': self.current_episode_steps,
            'total_reward': self.current_episode_reward,
            'level_complete': self.game_logic.level_complete,
            'game_over': self.game_logic.game_over,
            'terminated': terminated
        }
    
    def run_level(self) -> GameResult:
        """
        Override base method - not used for RL training.
        Use train() or evaluate() instead.
        """
        raise NotImplementedError(
            "Use train() or evaluate() methods for RL training/evaluation"
        )
        
    def on_level_start(self) -> None:
        """Called when a level starts. Override for custom behavior."""
        pass
    
    def on_level_complete(self) -> None:
        """Called when a level is completed. Override for custom behavior."""
        pass
    def on_game_over(self) -> None:
        """Called when game over occurs. Override for custom behavior."""
        pass
    def process_input(self) -> Tuple[Optional[Direction], Optional[str]]:
        """
        Process input events. Not used in RL controller.
        """
        pass