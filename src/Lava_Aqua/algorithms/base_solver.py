from abc import ABC, abstractmethod
from typing import List, Optional
from src.Lava_Aqua.core.game import GameLogic, GameState
from src.Lava_Aqua.core.constants import Direction

from src.Lava_Aqua.graphics.renderer import Renderer


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
        print(f"  Time taken: {self.stats['time_taken']:.3f}s")
        print(f"  Solution length: {self.stats['solution_length']}")
        
    def _hash_state(self, state: GameState) -> str:

        player_hash = str(state.player_pos)
        boxes_hash = str(sorted(state.box_positions))
        keys_hash = str(sorted(state.collected_key_indices))
        lava_hash = str(sorted(state.lava_positions))
        aqua_hash = str(sorted(state.aqua_positions))
        temp_wall_hash = str(sorted(state.temp_wall_data))
        
        return f"{player_hash}|{boxes_hash}|{keys_hash}|{lava_hash}|{aqua_hash}{temp_wall_hash}"
    
    
    # Helper methods for JSON serialization of stats
    
    def _stats_to_json(self) -> dict:
        """Convert stats to JSON serializable format."""
        return {
            'nodes_explored': self.stats['nodes_explored'],
            'time_taken': self.stats['time_taken'],
            'solution_length': self.stats['solution_length']
        }
        
    def save_to_json(self, file_path: str) -> None:
        """Save solver stats to JSON file.
        
        Args:
            file_path: Path to save the JSON file
        """
        import json
        with open(file_path, 'w') as f:
            json.dump(self._stats_to_json(), f, indent=4)
    
    # render algorithm's moves for debugging
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