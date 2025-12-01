import time
from typing import List, Optional, Set
from copy import deepcopy
from src.Lava_Aqua.graphics.renderer import Renderer
from src.Lava_Aqua.algorithms.base_solver import BaseSolver
from src.Lava_Aqua.core.constants import Direction

class DFSSolver(BaseSolver):
    """Depth-First Search solver implementation."""
    def __init__(self):
        super().__init__(name="DFS")
        self.max_depth = 35
        
    def solve(self, game_logic) -> Optional[List[Direction]]:
        
        # start_time = time.time()
        
        self.reset_stats()
        
        simulation = deepcopy(game_logic)
        
        # renderer = self._setup_renderer(simulation=simulation)
        
        initial_state = simulation.get_state()
        
        stack = [(initial_state, [])]
        visited: Set[str] = set()
        visited.add(self._hash_state(initial_state))
        
        while stack:
            current_state, path = stack.pop()
            self.stats['nodes_explored'] += 1

            if len(path) >= self.max_depth:
                continue
            
            # print(time.time()-start_time, f"DFS exploring node at depth {len(path)}, total explored: {self.stats['nodes_explored']}")
                
            simulation.load_state(current_state)

            if simulation.is_level_completed():
                return path

            moves = simulation.allowed_moves()
            
            for move in moves:

                new_state = simulation.simulate_move(move)
                
                # renderer.draw_game(simulation, animation_time=0.1)
                
                if new_state is None:
                    continue
                
                self.stats['nodes_generated'] += 1
                
                state_hash = self._hash_state(new_state)
                if state_hash in visited:
                    continue
                
                visited.add(state_hash)
                new_path = path + [move]
                stack.append((new_state, new_path))
                
        return None