from abc import ABC, abstractmethod
from typing import List, Optional
from src.Lava_Aqua.core.game import GameLogic, GameState
from src.Lava_Aqua.core.constants import Direction


class BaseSolver(ABC):
    """Abstract base class for game solving algorithms."""
    
    def __init__(self, name: str = "Base Solver"):
        """Initialize solver.
        
        Args:
            name: Name of the solver algorithm
        """
        self.name = name
        self.stats = {
            'nodes_explored': 0,
            'max_depth': 0,
            'time_taken': 0.0,
            'solution_length': 0
        }
    
    @abstractmethod
    def solve(self, game_logic: GameLogic) -> Optional[List[Direction]]:
        """Solve the current level.
        
        Args:
            game_logic: Current game logic instance
            
        Returns:
            List of Direction moves to solve the level, or None if no solution
        """
        pass
    
    def reset_stats(self) -> None:
        """Reset solver statistics."""
        self.stats = {
            'nodes_explored': 0,
            'max_depth': 0,
            'time_taken': 0.0,
            'solution_length': 0
        }
    
    def get_stats(self) -> dict:
        """Get solver statistics.
        
        Returns:
            Dictionary of solver stats
        """
        return self.stats.copy()
    
    def print_stats(self) -> None:
        """Print solver statistics."""
        print(f"\n{self.name} Statistics:")
        print(f"  Nodes explored: {self.stats['nodes_explored']}")
        print(f"  Max depth: {self.stats['max_depth']}")
        print(f"  Time taken: {self.stats['time_taken']:.3f}s")
        print(f"  Solution length: {self.stats['solution_length']}")
        
    def _hash_state(self, state: GameState) -> str:
        """
        Create a simple hash of the game state.
        
        This is used to detect if we've visited a state before.
        You may want to include more or fewer elements depending on your needs.
        """
        # Hash based on player position, box positions, and collected keys
        player_hash = str(state.player_pos)
        boxes_hash = str(sorted(state.box_positions))
        keys_hash = str(sorted(state.collected_key_indices))
        lava_hash = str(sorted(state.lava_positions))
        aqua_hash = str(sorted(state.aqua_positions))
        
        return f"{player_hash}|{boxes_hash}|{keys_hash}|{lava_hash}|{aqua_hash}"