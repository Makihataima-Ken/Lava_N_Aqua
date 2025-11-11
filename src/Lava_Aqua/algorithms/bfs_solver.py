"""BFS solver implementation example."""

from collections import deque
from typing import List, Optional, Set, Tuple
from copy import deepcopy

from src.Lava_Aqua.algorithms.base_solver import BaseSolver
from src.Lava_Aqua.core.game import GameLogic, GameState
from src.Lava_Aqua.core.constants import Direction


class BFSSolver(BaseSolver):
    """Breadth-First Search solver implementation."""
    
    def __init__(self):
        super().__init__(name="BFS Solver")
        self.max_moves = 100  # Prevent infinite loops
    
    def solve(self, game_logic: GameLogic) -> Optional[List[Direction]]:
        """
        Solve using BFS algorithm.
        
        Strategy:
        1. Use get_state() to capture states
        2. Use simulate_move() to test moves
        3. Track visited states to avoid cycles
        4. Return path when level_complete is True
        """
        # Reset stats
        self.reset_stats()
        
        # Get initial state
        initial_state = game_logic.get_state()
        
        # Queue: (state, path_to_reach_state)
        queue = deque([(initial_state, [])])
        
        # Track visited states (using a simple hash of key positions)
        visited: Set[str] = set()
        visited.add(self._hash_state(initial_state))
        
        # All possible moves
        moves = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        
        while queue:
            current_state, path = queue.popleft()
            self.stats['nodes_explored'] += 1
            
            # Update max depth
            if len(path) > self.stats['max_depth']:
                self.stats['max_depth'] = len(path)
            
            # Check if path is too long
            if len(path) >= self.max_moves:
                continue
            
            # Load this state into game logic
            game_logic.load_state(current_state)
            print(game_logic.player.get_position())
            # Check if we've won
            if game_logic.level_complete:
                return path
            
            # Try all possible moves
            for move in moves:
                # Simulate the move (doesn't affect current game_logic state)
                new_state = game_logic.simulate_move(move)
                
                if new_state is None:
                    # Invalid move
                    continue
                
                state_hash = self._hash_state(new_state)
                
                if state_hash in visited:
                    # Already explored this state
                    continue
                
                visited.add(state_hash)
                
                # Add to queue
                new_path = path + [move]
                queue.append((new_state, new_path))
        
        # No solution found
        return None
    
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