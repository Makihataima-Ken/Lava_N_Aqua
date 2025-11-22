from collections import deque
from typing import List, Optional, Set, Tuple
from copy import deepcopy

from src.Lava_Aqua.algorithms.base_solver import BaseSolver
from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.core.constants import Direction

import time


class BFSSolver(BaseSolver):
    """Breadth-First Search solver implementation."""
    
    def __init__(self):
        super().__init__(name="BFS Solver")
        self.max_moves = 35  # Prevent infinite loops
    
    def solve(self, game_logic: GameLogic) -> Optional[List[Direction]]:
        """
        Solve using BFS algorithm.
        
        Strategy:
        1. Use get_state() to capture states
        2. Use simulate_move() to test moves
        3. Track visited states to avoid cycles
        4. Return path when level_complete is True
        """
        
        start_time = time.time()
        
        # Reset stats
        self.reset_stats()
        
        simulation = deepcopy(game_logic)
        
        # Get initial state
        initial_state = simulation.get_state()
        
        # Queue: (state, path_to_reach_state)
        queue = deque([(initial_state, [])])
        
        # Track visited states (using a simple hash of key positions)
        visited: Set[str] = set()
        visited.add(self._hash_state(initial_state))
        
        while queue:
            current_state, path = queue.popleft()
            self.stats['nodes_explored'] += 1
            
            # Update max depth
            if len(path) > self.stats['max_depth']:
                self.stats['max_depth'] = len(path)
            
            # Check if path is too long
            if len(path) >= self.max_moves:
                continue
            
            print(time.time()-start_time,f"BFS exploring node at depth {len(path)}, total explored: {self.stats['nodes_explored']}")
            
            # Load this state into game logic
            simulation.load_state(current_state)
            # print(simulation.player.get_position())
            
            # All possible moves (pruned as possible)
            moves = simulation.allowed_moves()
            
            # Check if we've won
            if simulation.is_level_completed():
                return path
            
            # Try all possible moves
            for move in moves:
                # Simulate the move (doesn't affect current simulation state)
                new_state = simulation.simulate_move(move)
                
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