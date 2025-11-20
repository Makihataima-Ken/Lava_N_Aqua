import time
from typing import List, Optional, Set
from copy import deepcopy
from src.Lava_Aqua.algorithms.base_solver import BaseSolver
from src.Lava_Aqua.core.constants import Direction

class DFSSolver(BaseSolver):
    """Depth-First Search solver implementation."""
    def __init__(self):
        super().__init__(name="DFS Solver")
        self.max_depth = 50  # Reasonable depth limit
        
    def solve(self, game_logic) -> Optional[List[Direction]]:
        
        # Reset stats
        self.reset_stats()
        
        # Work with a copy
        simulation = deepcopy(game_logic)
        
        # Get initial state
        initial_state = simulation.get_state()
        
        # Check if already at goal
        if simulation.is_level_completed():
            return []
        
        stack = [(initial_state, [])]
        visited: Set[str] = set()
        visited.add(self._hash_state(initial_state))
        
        while stack:
            current_state, path = stack.pop()
            self.stats['nodes_explored'] += 1

            # Depth limiting
            if len(path) >= self.max_depth:
                continue
            
            print(time.strftime("%H:%M:%S"), f"DFS exploring node at depth {len(path)}, total explored: {self.stats['nodes_explored']}")
                
            # Update max depth stat
            if len(path) > self.stats.get('max_depth', 0):
                self.stats['max_depth'] = len(path)
                
            # Load the current state
            simulation.load_state(current_state)
            
            # Double-check we're not in a bad state
            if simulation.game_over:
                continue
            
            # Get valid moves from current state
            moves = simulation.allowed_moves()
            
            # Try each move (reversed for DFS left-to-right priority)
            for move in reversed(moves):
                # Save state before simulating
                before_sim = simulation.get_state()
                
                # Simulate the move
                new_state = simulation.simulate_move(move)
                
                # Restore state after simulation
                simulation.load_state(before_sim)
                
                if new_state is None:
                    continue
                
                # Check if this state was already visited
                state_hash = self._hash_state(new_state)
                if state_hash in visited:
                    continue
                
                # Load new state to check if it's a solution
                simulation.load_state(new_state)
                
                # Skip if this led to game over
                if simulation.game_over:
                    simulation.load_state(before_sim)
                    continue
                
                # Check if this move solves the level
                if simulation.is_level_completed():
                    return path + [move]
                
                # Restore and continue
                simulation.load_state(before_sim)
                
                # Add to visited and stack
                visited.add(state_hash)
                new_path = path + [move]
                stack.append((new_state, new_path))
                
        return None