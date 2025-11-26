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
    
    def solve(self, game_logic: GameLogic) -> Optional[List[Direction]]:
        
        start_time = time.time()
        
        simulation = deepcopy(game_logic)
        
        initial_state = simulation.get_state()
        
        queue = deque([(initial_state, [])])
        
        visited: Set[str] = set()
        visited.add(self._hash_state(initial_state))
        
        while queue:
            current_state, path = queue.popleft()
            self.stats['nodes_explored'] += 1
            
            print(time.time()-start_time,f"BFS exploring node at depth {len(path)}, total explored: {self.stats['nodes_explored']}")
            
            simulation.load_state(current_state)
            
            if simulation.is_level_completed():
                return path
            
            moves = simulation.allowed_moves()
            
            for move in moves:
                
                new_state = simulation.simulate_move(move)
                
                if new_state is None:
                    continue
                
                state_hash = self._hash_state(new_state)
                
                if state_hash in visited:
                    continue
                
                visited.add(state_hash)
                
                new_path = path + [move]
                queue.append((new_state, new_path))
        
        return None