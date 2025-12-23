import time
import pygame
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Dict, Any, Tuple, List
from copy import deepcopy

from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.core.constants import Direction, GameResult
from .base_controller import BaseController
from src.Lava_Aqua.agents.base_agent import BaseAgent


class RLController(BaseController):
    """
    Controller for Reinforcement Learning agent.
    
    Simplified to match the solver pattern - the agent has full control
    over the game logic and learning process.
    """
    
    def __init__(
        self, 
        game_logic: GameLogic,
        agent: BaseAgent,
        move_delay: float = 0.05,
    ):
        """
        Initialize RL controller.
        
        Args:
            game_logic: Game logic instance
            agent: RL agent to train/evaluate
            move_delay: Delay between moves (for visualization)
        """
        super().__init__(game_logic)
        self.agent = agent
        self.move_delay = move_delay
        
        # Training statistics (controller level)
        self.episode_rewards: List[float] = []
        self.episode_lengths: List[int] = []
    
    def train(
        self, 
        num_episodes: int, 
        eval_frequency: int = 100,
        visualize: bool = False
    ) -> Dict[str, Any]:
        """
        Train the agent for multiple episodes.
        
        Args:
            num_episodes: Number of training episodes
            eval_frequency: Evaluate agent every N episodes
            visualize: Whether to visualize training
            
        Returns:
            Training statistics
        """
        self.on_train_start(num_episodes)
        
        training_start = time.time()
        
        for episode in range(1, num_episodes + 1):
            result = self.agent.run_episode(
                game_logic=self.game_logic,
                training=True,
                visualize=visualize,
                move_delay=self.move_delay,
                controller=self
            )
            
            self.episode_rewards.append(result['total_reward'])
            self.episode_lengths.append(result['steps'])
            
            # Logging
            if episode % 10 == 0:
                avg_reward = np.mean(self.episode_rewards[-10:])
                avg_length = np.mean(self.episode_lengths[-10:])
                print(
                    f"Episode {episode}/{num_episodes} | "
                    f"Reward: {avg_reward:.2f} | "
                    f"Steps: {avg_length:.1f} | "
                    f"ε: {self.agent.epsilon:.4f} | "
                    # f"States: {self.agent.stats['unique_states']}"
                )
            
            # Evaluation
            if episode % eval_frequency == 0:
                eval_stats = self.evaluate(
                    num_episodes=10,
                    visualize=False,
                )
                print(f"  Eval - Success: {eval_stats['success_rate']:.1%}, "
                      f"Reward: {eval_stats['avg_reward']:.2f}")
        
        
        training_time = time.time() - training_start
        
        self.on_train_complete(training_time)
        
        return {
            'training_time': training_time,
            'episode_rewards':self.episode_rewards,
            'episode_lengths':self.episode_lengths
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
        print(f"\n{'='*60}")
        print(f"📊 Evaluating {self.agent.name}")
        print(f"{'='*60}")
        
        eval_rewards = []
        eval_lengths = []
        success_count = 0
        
        for _ in range(num_episodes):
            result = self.agent.run_episode(
                game_logic=self.game_logic,
                training=False,
                visualize=visualize,
                move_delay=self.move_delay,
                controller=self
            )
            
            eval_rewards.append(result['total_reward'])
            eval_lengths.append(result['steps'])
            if result['level_complete']:
                success_count += 1
        
        eval_stats = {
            'num_episodes': num_episodes,
            'success_rate': success_count / num_episodes,
            'success_count': success_count,
            'avg_reward': np.mean(eval_rewards),
            'std_reward': np.std(eval_rewards),
            'avg_steps': np.mean(eval_lengths),
            'std_steps': np.std(eval_lengths)
        }
        
        # Print results
        print(f"\n📊 Evaluation Results:")
        print(f"  Success Rate: {eval_stats['success_rate']:.1%}")
        print(f"  Avg Reward: {eval_stats['avg_reward']:.2f} ± {eval_stats.get('std_reward', 0):.2f}")
        print(f"  Avg Steps: {eval_stats['avg_steps']:.1f} ± {eval_stats.get('std_steps', 0):.1f}")
        print(f"{'='*60}\n")
        
        return eval_stats
    
    def run_level(self, visualize: bool = True, agent_path: Optional[str] = None) -> GameResult:
        """
        Run a single episode using the trained agent.
        Similar to SolverController.run_level().

        Args:
            visualize: Whether to render the game during the run
            agent_path: Path to load trained agent from
        
        Returns:
            GameResult: The outcome of the episode
        """
        self.on_level_start()
        
        # Load agent if path provided
        if agent_path:
            self.agent.load(agent_path)
            print(f"Agent loaded from: {agent_path}")
        
        # Agent runs the level
        moves,state = self.agent.solve(self.game_logic)
        
        for move in moves:
            self.game_logic.move_player(move)
            
            if visualize:
                self.render_frame()
                time.sleep(0.2)
                
        self.on_level_complete(len(moves),state)
        
        if state:
            return GameResult.WIN
        else:
            return GameResult.LOSS
        
    
    def on_level_start(self) -> None:
        """Called when a level starts."""
        print(f"\n{'='*70}")
        print(f"Running RL Agent")
        print(f"Level: {self.game_logic.get_level_description()}")
        print(f"Agent: {self.agent.name}")
        print(f"{'='*70}")
    
    def on_train_start(self, num_episodes: int) -> None:
        """Called when training starts."""
        print(f"\n{'='*70}")
        print(f"TRAINING RL AGENT")
        print(f"Episodes: {num_episodes}")
        print(f"Level: {self.game_logic.get_level_description()}")
        print(f"Agent: {self.agent.name}")
        print(f"{'='*70}")
    
    def on_level_complete(self, steps:int, state:bool) -> None:
        """Called when a level is completed."""
        print(f"\n{'='*70}")
        if state:
            print("Level Complete :)")
        else:
            print("level failed :(")
        print(f"  Total steps: {steps}")
        print(f"{'='*70}")
    
    def on_train_complete(self, training_time: float) -> None:
        """Called when training completes."""
        print(f"\n{'='*70}")
        print(f"✅ Training Complete")
        print(f"  Total time: {training_time:.1f}s")
        
        if self.episode_rewards:
            print(f"  Total episodes: {len(self.episode_rewards)}")
            print(f"  Final avg reward: {np.mean(self.episode_rewards[-100:]):.2f}")
        
        agent_stats = self.agent.get_stats()
        if agent_stats:
            print(f"\n  Agent Statistics:")
            for key, value in agent_stats.items():
                if isinstance(value, float):
                    print(f"    {key}: {value:.4f}")
                else:
                    print(f"    {key}: {value}")
        
        print(f"{'='*70}")
    
    def on_game_over(self, result: Dict[str, Any]) -> None:
        """Called when game over occurs."""
        print(f"\n Game Over")
        print(f"  Steps survived: {result.get('steps', 0)}")
        print(f"  Total reward: {result.get('total_reward', 0):.2f}")
    
    def process_input(self) -> Tuple[Optional[Direction], Optional[str]]:
        """
        Process input events. Not used in RL controller during normal operation.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None, 'quit'
                if event.key == pygame.K_SPACE:
                    return None, 'pause'
    
    def plot_training_curves(self, save_path: str = 'training_curves.png'):
        """
        Plot training progress.
        
        Args:
            save_path: Path to save the plot
        """
        if not self.episode_rewards:
            print("No training data to plot")
            return
        
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))
        
        # Plot rewards
        rewards = self.episode_rewards
        window = min(50, len(rewards) // 10)
        
        if len(rewards) >= window:
            smoothed_rewards = np.convolve(
                rewards, 
                np.ones(window)/window, 
                mode='valid'
            )
            axes[0].plot(smoothed_rewards, label=f'Smoothed (window={window})', linewidth=2)
        
        axes[0].plot(rewards, alpha=0.3, label='Raw', linewidth=0.5)
        axes[0].set_xlabel('Episode')
        axes[0].set_ylabel('Total Reward')
        axes[0].set_title(f'Training Rewards - {self.agent.name}')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot episode lengths
        lengths = self.episode_lengths
        if len(lengths) >= window:
            smoothed_lengths = np.convolve(
                lengths, 
                np.ones(window)/window, 
                mode='valid'
            )
            axes[1].plot(smoothed_lengths, label=f'Smoothed (window={window})', linewidth=2)
        
        axes[1].plot(lengths, alpha=0.3, label='Raw', linewidth=0.5)
        axes[1].set_xlabel('Episode')
        axes[1].set_ylabel('Steps')
        axes[1].set_title('Episode Length')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        print(f"\n📈 Training curves saved to '{save_path}'")
        plt.show()