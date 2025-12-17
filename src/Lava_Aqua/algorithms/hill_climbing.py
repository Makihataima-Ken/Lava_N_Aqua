import time
from typing import Dict, List, Optional, Set, Tuple
from copy import deepcopy
from src.Lava_Aqua.graphics.renderer import Renderer
from src.Lava_Aqua.algorithms.base_solver import BaseSolver, PathNode
from src.Lava_Aqua.core.constants import Direction

import heapq


class HillClimbingSolver(BaseSolver):
    """Hill Climbing Search solver implementation."""
    def __init__(self):
        super().__init__(name="Hill Climbing")
            
    def solve(self, game_logic) -> Optional[List[Direction]]:
        
        start_time = time.time()
        
        simulation = deepcopy(game_logic)
        
        exit_pos = simulation.get_exit_position()
        
        renderer = self._setup_renderer(simulation=simulation)
        
        init_state = simulation.get_state()
        
        p_queue = [(self._heuristic(init_state, exit_pos),init_state, PathNode(val=None))]
        
        heapq.heapify(p_queue)
        
        best_cost = {self._hash_state(init_state): self._heuristic(init_state, exit_pos)}
        
        while p_queue:
            current_h,current_state, path = heapq.heappop(p_queue)
            self.stats['nodes_explored'] += 1
            
            simulation.load_state(current_state)
            
            if simulation.is_level_completed():
                path_list = path.to_list()
                self.stats['time_taken'] = time.time() - start_time
                self.stats['solution_length'] = len(path_list)
                return path_list
            
            if current_h > best_cost.get(self._hash_state(current_state),float("inf")):
                continue
            
            moves = simulation.allowed_moves()
            
            for move in moves:
                new_state = simulation.simulate_move(move)

                renderer.draw_solver_step(simulation)
                
                if new_state is None:
                    continue
                
                self.stats['nodes_generated'] += 1
                
                state_hash = self._hash_state(new_state)
                
                new_h = self._heuristic(new_state,exit_pos)
    
                best_cost[state_hash] = new_h
                    
                new_path = PathNode(val=move, parent=path)
                heapq.heappush(p_queue, (new_h, new_state, new_path))
           
        return None
