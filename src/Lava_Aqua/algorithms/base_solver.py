"""Base solver interface for game algorithms."""

from abc import ABC, abstractmethod
from typing import List, Optional, Generator, Tuple
from src.Lava_Aqua.core.game import GameLogic
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