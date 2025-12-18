import time
from typing import Dict, List, Optional, Set, Tuple
from copy import deepcopy
from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.graphics.renderer import Renderer
from src.Lava_Aqua.algorithms.base_solver import BaseSolver, PathNode
from src.Lava_Aqua.core.constants import Direction

import heapq


class DijkstraSolver(BaseSolver):
    """Dijkstra solver implementation."""
    def __init__(self):
        super().__init__(name="Dijkstra")
    
    def solve(self, game_logic: GameLogic,visualize:bool = False) -> Optional[List[Direction]]:
        
        start_time = time.time()
        
        simulation = deepcopy(game_logic)
        
        if visualize:
            renderer = self._setup_renderer(simulation=simulation)
        
        init_state = simulation.get_state()
        
        p_queue = [(0,init_state, PathNode(val=None))]
        # p_queue = [(0,init_state,[])]
        
        heapq.heapify(p_queue)

        best_cost: Dict[str, int] = {}
        best_cost[self._hash_state(init_state)] = 0
        
        while p_queue:
            current_cost,current_state, path = heapq.heappop(p_queue)
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

            if current_cost > best_cost.get(self._hash_state(current_state), float("inf")):
                continue
            
            moves = simulation.allowed_moves()
            
            for move in moves:
                new_state = simulation.simulate_move(move)
                
                if visualize:
                    renderer.draw_solver_step(simulation)
                
                if new_state is None:
                    continue
                
                self.stats['nodes_generated'] += 1
                
                step_cost = new_state.moves - current_state.moves

                new_cost = current_cost + step_cost
                
                state_hash = self._hash_state(new_state)
                
                if new_cost < best_cost.get(state_hash, float("inf")):
                    best_cost[state_hash] = new_cost
                    # new_path = path + [move]
                    new_path = PathNode(val=move,parent=path)
                    heapq.heappush(
                        p_queue,
                        (new_cost, new_state, new_path)
                    )
           
        return None