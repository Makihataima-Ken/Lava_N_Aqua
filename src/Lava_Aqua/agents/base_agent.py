from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional, TYPE_CHECKING
from src.Lava_Aqua.graphics.renderer import Renderer
import numpy as np

if TYPE_CHECKING:
    from src.Lava_Aqua.core.game import GameLogic
    from src.Lava_Aqua.controllers.base_controller import BaseController


class BaseAgent(ABC):
    """
    Base class for RL agents.
    
    Similar to BaseSolver, agents have direct access to game logic
    and handle their own training/evaluation loops.
    """
    
    def __init__(self, name: str):
        """
        Initialize RL agent.
        
        Args:
            name: Agent name
        """
        self.name = name
        
        # Statistics tracking
        self.stats = {
            'total_episodes': 0,
            'total_steps': 0,
        }
    
    @abstractmethod
    def train(
        self,
        game_logic: 'GameLogic',
        num_episodes: int,
        eval_frequency: int = 100,
        visualize: bool = False,
        move_delay: float = 0.05,
        controller: Optional['BaseController'] = None
    ) -> Dict[str, Any]:
        """
        Train the agent on the given game logic.
        
        Args:
            game_logic: Game logic instance to train on
            num_episodes: Number of training episodes
            eval_frequency: Evaluate every N episodes
            visualize: Whether to render training
            move_delay: Delay between moves for visualization
            controller: Optional controller for rendering
            
        Returns:
            Training statistics dict with at least:
                - episode_rewards: List[float]
                - episode_lengths: List[int]
        """
        pass
    
    @abstractmethod
    def evaluate(
        self,
        game_logic: 'GameLogic',
        num_episodes: int = 100,
        visualize: bool = False,
        move_delay: float = 0.05,
        controller: Optional['BaseController'] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the agent without training.
        
        Args:
            game_logic: Game logic instance
            num_episodes: Number of evaluation episodes
            visualize: Whether to render evaluation
            move_delay: Delay between moves
            controller: Optional controller for rendering
            
        Returns:
            Evaluation statistics dict with at least:
                - success_rate: float
                - avg_reward: float
                - avg_steps: float
        """
        pass
    
    @abstractmethod
    def run_episode(
        self,
        game_logic: 'GameLogic',
        training: bool = False,
        visualize: bool = False,
        move_delay: float = 0.05,
        controller: Optional['BaseController'] = None
    ) -> Dict[str, Any]:
        """
        Run a single episode.
        
        Args:
            game_logic: Game logic instance
            training: Whether to learn during this episode
            visualize: Whether to render
            move_delay: Delay between moves
            controller: Optional controller for rendering
            
        Returns:
            Episode statistics dict with at least:
                - steps: int
                - total_reward: float
                - level_complete: bool
                - game_over: bool
                - terminated: bool
        """
        pass
    
    @abstractmethod
    def save(self, filepath: str) -> None:
        """
        Save agent to file.
        
        Args:
            filepath: Path to save the agent
        """
        pass
    
    @abstractmethod
    def load(self, filepath: str) -> None:
        """
        Load agent from file.
        
        Args:
            filepath: Path to load the agent from
        """
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent statistics.
        
        Returns:
            Dictionary of agent statistics
        """
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """Reset agent statistics."""
        self.stats = {
            'total_episodes': 0,
            'total_steps': 0,
        }
    
    def print_stats(self) -> None:
        """Print agent statistics."""
        print(f"\n{self.name} Statistics:")
        for key, value in self.stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")
                
    def _setup_renderer(self,simulation:GameLogic) -> Renderer:
            """Setup renderer based on grid dimensions.
            
            Returns:
                Renderer instance
            """
            tile_grid = simulation.get_grid()
            
            if not tile_grid:
                raise ValueError("No grid available")
            
            screen_width = tile_grid.get_width()
            screen_height = tile_grid.get_height() 
            caption = simulation.get_level_description()
            
            return Renderer(screen_width, screen_height, caption)