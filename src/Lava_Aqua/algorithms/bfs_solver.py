from collections import deque
from typing import List, Optional, Set, Tuple
from copy import deepcopy

from src.Lava_Aqua.algorithms.base_solver import BaseSolver, PathNode
from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.core.constants import Direction

import time


class BFSSolver(BaseSolver):
    """Breadth-First Search solver implementation."""
    
    def __init__(self):
        super().__init__(name="BFS")
    
    def solve(self, game_logic: GameLogic,visualize:bool = False) -> Optional[List[Direction]]:
        
        start_time = time.time()
        
        simulation = deepcopy(game_logic)        
        
        if visualize:
            renderer = self._setup_renderer(simulation=simulation)
        
        init_state = simulation.get_state()
       
        queue = deque([(init_state,PathNode(None))])
        # queue = deque([(init_state,[])])
       
        visited = set()
        visited.add(self._hash_state(init_state))
       
        while queue:
            currrent_state, path = queue.popleft()
            self.stats['nodes_explored'] += 1
           
            simulation.load_state(currrent_state)

            # print(time.time()-start_time, f"BFS exploring node at depth {len(path)}, total explored: {self.stats['nodes_explored']}")
            
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
                
                if visualize:
                    renderer.draw_solver_step(simulation)

                if new_state is None:
                    continue
                
                self.stats['nodes_generated'] += 1
                
                state_hash = self._hash_state(new_state)
                if state_hash in visited:
                    continue
                
                visited.add(state_hash)
                # new_path = path + [move]
                new_path = PathNode(move,path)
                queue.append((new_state, new_path))
           
        return None
