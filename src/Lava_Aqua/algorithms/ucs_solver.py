import time
from typing import List, Optional, Set, Tuple
from copy import deepcopy
from src.Lava_Aqua.graphics.renderer import Renderer
from src.Lava_Aqua.algorithms.base_solver import BaseSolver, PathNode
from src.Lava_Aqua.core.constants import Direction

import heapq


class UCSSolver(BaseSolver):
    """Uniform-Cost Search solver implementation."""
    def __init__(self):
        super().__init__(name="UCS")
    
    def solve(self, game_logic) -> Optional[List[Direction]]:
        
        start_time = time.time()
        
        simulation = deepcopy(game_logic)
        
        renderer = self._setup_renderer(simulation=simulation)
        
        init_state = simulation.get_state()
        
        p_queue = [(init_state, PathNode(val=None))]
        # p_queue = [(init_state,[])]
        
        heapq.heapify(p_queue)
        
        visited: Set[str] = set()
        visited.add(self._hash_state(init_state))
        
        while p_queue:
            current_state, path = heapq.heappop(p_queue)
            self.stats['nodes_explored'] += 1
            
            simulation.load_state(current_state)
            
            # if simulation.is_level_completed():
            #     self.stats['time_taken'] = time.time() - start_time
            #     self.stats['solution_length'] = len(path)
            #     return path
            
            if simulation.is_level_completed():
                path_list = path.to_list()
                self.stats['time_taken'] = time.time() - start_time
                self.stats['solution_length'] = len(path_list)
                return path_list
            
            moves = simulation.allowed_moves()
            
            for move in moves:
                new_state = simulation.simulate_move(move)

                # renderer.draw_game(simulation, animation_time=0.1)
                renderer.draw_solver_step(simulation)
                
                if new_state is None:
                    continue
                
                self.stats['nodes_generated'] += 1
                
                state_hash = self._hash_state(new_state)
                
                if state_hash in visited:
                    continue
                
                visited.add(state_hash)
                new_path = PathNode(val=move,parent=path)
                # new_path = path + [move]
                heapq.heappush(p_queue,(new_state, new_path))
           
        return None
            
            
            
        
        
        
        