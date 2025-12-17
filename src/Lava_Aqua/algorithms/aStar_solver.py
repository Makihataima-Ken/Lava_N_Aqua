from copy import deepcopy
import time
import heapq
from typing import List, Optional

from src.Lava_Aqua.core.game import GameLogic, GameState
from src.Lava_Aqua.core.constants import Direction
from src.Lava_Aqua.algorithms.base_solver import BaseSolver, PathNode

class AStarSolver(BaseSolver):
    """
    A* search algorithm implementation for solving the game.
    """

    def __init__(self):
        """
        Initializes the A* solver.
        """
        super().__init__(name="A Star")

    def solve(self, game_logic: GameLogic) -> Optional[List[Direction]]:
        """
        Solves the puzzle using A* search.

        Args:
            game_logic: An instance of the GameLogic.

        Returns:
            A list of directions representing the solution path, or None if no solution is found.
        """
        start_time = time.time()

        simulation = deepcopy(game_logic)
        initial_state = simulation.get_state()
        
        exit_pos = simulation.get_exit_position()
        all_key_positions = simulation.get_key_positions()
        
        renderer = self._setup_renderer(simulation=simulation)
        
        p_queue = [(self._heuristic_keys(initial_state, exit_pos,all_key_positions), 0, initial_state, PathNode(val=None))]
        heapq.heapify(p_queue)

        best_cost = {self._hash_state(initial_state):self._heuristic_keys(initial_state, exit_pos,all_key_positions)}
        
        self.stats['nodes_generated'] = 1

        while p_queue:
            _, current_cost, current_state, path = heapq.heappop(p_queue)
            self.stats['nodes_explored'] += 1

            simulation.load_state(current_state)

            if simulation.is_level_completed():
                self.stats['time_taken'] = time.time() - start_time
                path_list = path.to_list()
                self.stats['solution_length'] = len(path_list)
                return path_list

            if current_cost > best_cost.get(self._hash_state(current_state)):
                continue
            
            moves = simulation.allowed_moves()
            
            for move in moves:
                new_state = simulation.simulate_move(move)
                
                renderer.draw_solver_step(simulation)

                if new_state is None:
                    continue
                
                self.stats['nodes_generated'] += 1

                # g(n): Cost from the start to the new state
                step_cost = new_state.moves - current_state.moves
                
                new_cost = current_cost + step_cost
                
                state_hash = self._hash_state(new_state)

                # If this is a better path to this state, update and push to the queue
                if new_cost < best_cost.get(state_hash, float("inf")):
                    best_cost[state_hash] = new_cost
                    
                    # h(n): Heuristic cost from the new state to the goal
                    heuristic_cost = self._heuristic_keys(new_state, exit_pos,all_key_positions)
                    
                    # f(n) = g(n) + h(n)
                    priority = new_cost + heuristic_cost
                    
                    new_path = PathNode(val=move, parent=path)
                    heapq.heappush(p_queue, (priority, new_cost, new_state, new_path))
        
        # No solution found
        self.stats['time_taken'] = time.time() - start_time
        return None

