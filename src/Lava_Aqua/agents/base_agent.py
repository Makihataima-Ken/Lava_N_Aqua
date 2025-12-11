from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
from src.Lava_Aqua.core.constants import Direction


from src.Lava_Aqua.core.game import GameLogic, GameState
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
    def solve(self,game_logic:'GameLogic')->Optional[List[Direction]]:
        """
        Run a level by a trained model

        Args:
            game_logic (GameLogic): Game logic instance

        Returns:
            List of moves that solves the game
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
    
    def _hash_state(self, state: GameState) -> str:

        player_hash = str(state.player_pos)
        boxes_hash = str(sorted(state.box_positions))
        keys_hash = str(sorted(state.collected_key_indices))
        lava_hash = str(sorted(state.lava_positions))
        aqua_hash = str(sorted(state.aqua_positions))
        temp_wall_hash = str(sorted(state.temp_wall_data))
        altered_positions_hash = str(sorted(state.altered_tile_positions))
        
        return f"{player_hash}|{boxes_hash}|{keys_hash}|{lava_hash}|{aqua_hash}{temp_wall_hash}{altered_positions_hash}"
    
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