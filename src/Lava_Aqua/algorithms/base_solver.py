from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from src.Lava_Aqua.core.game import GameLogic, GameState
from src.Lava_Aqua.core.constants import Direction
from dataclasses import dataclass

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
            'nodes_generated': 0,
            'time_taken': 0.0,
            'solution_length': 0
        }
    
    @abstractmethod
    def solve(self, game_logic: GameLogic,visualize:bool = False) -> Optional[List[Direction]]:
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
            'nodes_generated': 0,
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
        print(f"  Nodes generated: {self.stats['nodes_generated']}")
        print(f"  Time taken: {self.stats['time_taken']:.3f}s")
        print(f"  Solution length: {self.stats['solution_length']}")
        
    def _hash_state(self, state: GameState) -> str:

        player_hash = str(state.player_pos)
        boxes_hash = str(sorted(state.box_positions))
        keys_hash = str(sorted(state.collected_key_indices))
        lava_hash = str(sorted(state.lava_positions))
        aqua_hash = str(sorted(state.aqua_positions))
        temp_wall_hash = str(sorted(state.temp_wall_data))
        altered_positions_hash = str(sorted(state.altered_tile_positions))
        
        return f"{player_hash}|{boxes_hash}|{keys_hash}|{lava_hash}|{aqua_hash}{temp_wall_hash}{altered_positions_hash}"
    
    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions.
        
        Args:
            pos1: First position (x, y)
            pos2: Second position (x, y)
            
        Returns:
            Manhattan distance
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _euclidean_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two positions.
        
        Args:
            pos1: First position (x, y)
            pos2: Second position (x, y)
            
        Returns:
            Euclidean distance
        """
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
    
    # Helper methods for JSON serialization of stats
    
    def _stats_to_json(self) -> dict:
        """Convert stats to JSON serializable format."""
        return {
            'nodes_explored': self.stats['nodes_explored'],
            'nodes_generated': self.stats['nodes_generated'],
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
        
    # heruestics 
    
    def _heuristic(self, state, exit_pos) ->int:
        """
        Heuristic function for A*. 
        Calculates the Manhattan distance from the player's position to the exit.
        """
        player_pos = state.player_pos
        return self._manhattan_distance(player_pos, exit_pos)
    
    def _heuristic_keys(self, state: GameState, exit_pos: tuple, all_key_positions: List[tuple]) -> int:
        """
        Heuristic function (h(n)).

        - If all keys are collected, the heuristic is the Manhattan distance from the player to the exit.
        - If keys remain, it's an admissible estimate composed of two parts:
          1. The distance from the player to the NEAREST uncollected key.
          2. The distance from the uncollected key NEAREST to the exit, to the exit itself.
        
        This guides the search toward keys first and is more effective than a simple player-to-exit heuristic.
        """
        player_pos = state.player_pos

        # Identify the positions of keys that have not been collected yet
        uncollected_key_pos = [
            key_pos for i, key_pos in enumerate(all_key_positions) 
            if i not in state.collected_key_indices
        ]

        if not uncollected_key_pos:
            return self._manhattan_distance(player_pos, exit_pos)

        dist_to_closest_key = min(self._manhattan_distance(player_pos, key_pos) for key_pos in uncollected_key_pos)
        
        dist_from_keys_to_exit = min(self._manhattan_distance(key_pos, exit_pos) for key_pos in uncollected_key_pos)

        return dist_to_closest_key + dist_from_keys_to_exit
        
    def _heuristic_box_lava_priority(self,state,  exit_pos: tuple, all_key_positions: List[tuple]):
        """
        Calculates the heuristic value for a given game state.

        The heuristic prioritizes:
        1. Pushing boxes into lava.
        2. Collecting keys.
        3. Reaching the exit.
        """
        player_pos = state.player_pos
        boxes = state.box_positions
        lava_pits = state.lava_positions
        keys = all_key_positions

        # Manhattan distance helper function
        def manhattan_distance(pos1, pos2):
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

        # --- 1. Pushing Boxes into Lava ---
        if boxes:
            min_box_to_lava_dist = float('inf')

            # Find the minimum distance to push any box to any lava pit
            for box in boxes:
                # Heuristic for player to get to the "pushing" side of the box
                # This is a simplification; a more advanced heuristic would find the optimal pushing spot
                player_to_box_dist = manhattan_distance(player_pos, box)

                # Find the closest lava pit for the current box
                closest_lava_dist = min(manhattan_distance(box, lava) for lava in lava_pits)
                
                total_dist = player_to_box_dist + closest_lava_dist
                if total_dist < min_box_to_lava_dist:
                    min_box_to_lava_dist = total_dist
            
            # Add a large constant to prioritize this over key collection and exiting
            return min_box_to_lava_dist + 1000  # The constant ensures this is the highest priority

        # --- 2. Collecting Keys ---
        if keys:
            # If all boxes are gone, focus on the nearest key
            min_key_dist = min(manhattan_distance(player_pos, key) for key in keys)
            
            # Add a smaller constant to prioritize this over exiting
            return min_key_dist + 500 # This constant should be smaller than the box priority

        # --- 3. Reaching the Exit ---
        # If all boxes are pushed and all keys are collected
        return manhattan_distance(player_pos, exit_pos)
@dataclass
class PathNode:
    val: Direction
    parent: Optional["PathNode"] = None
    
    def to_list(self):
        path_list = []
        buff = self
        while buff and buff.val is not None:
            path_list.append(buff.val)
            buff = buff.parent
        return path_list[::-1]
    
    def __lt__(self,other):
        return self.val.value <other.val.value