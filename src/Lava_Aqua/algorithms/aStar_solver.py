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

    def _heuristic(self, state, exit_pos):
        """
        Heuristic function for A*. 
        Calculates the Manhattan distance from the player's position to the exit.
        """
        player_pos = state.player_pos
        return self._manhattan_distance(player_pos, exit_pos)
    
    # def _heuristic(self, state: GameState, exit_pos: tuple, all_key_positions: List[tuple]) -> int:
    #     """
    #     Heuristic function (h(n)) for A*.

    #     - If all keys are collected, the heuristic is the Manhattan distance from the player to the exit.
    #     - If keys remain, it's an admissible estimate composed of two parts:
    #       1. The distance from the player to the NEAREST uncollected key.
    #       2. The distance from the uncollected key NEAREST to the exit, to the exit itself.
        
    #     This guides the search toward keys first and is more effective than a simple player-to-exit heuristic.
    #     """
    #     player_pos = state.player_pos

    #     # Identify the positions of keys that have not been collected yet
    #     uncollected_key_pos = [
    #         key_pos for i, key_pos in enumerate(all_key_positions) 
    #         if i not in state.collected_key_indices
    #     ]

    #     # CASE 1: All keys are collected (or level has no keys).
    #     # The goal is simply to get to the exit.
    #     if not uncollected_key_pos:
    #         return self._manhattan_distance(player_pos, exit_pos)

    #     # CASE 2: There are still keys to collect.
    #     # The path must go from the player to the keys, and from the keys to the exit.

    #     # Part 1: Minimum distance from the player to any of the remaining keys.
    #     # The player must travel at least this far to get the first key.
    #     dist_to_closest_key = min(self._manhattan_distance(player_pos, key_pos) for key_pos in uncollected_key_pos)
        
    #     # Part 2: Minimum distance from any remaining key to the exit.
    #     # After collecting all keys, the player must travel from the last key to the exit.
    #     # This is a lower bound on that final leg of the journey.
    #     dist_from_keys_to_exit = min(self._manhattan_distance(key_pos, exit_pos) for key_pos in uncollected_key_pos)

    #     # The final heuristic is the sum of these two admissible parts.
    #     # It underestimates the total cost because it doesn't include the travel between keys.
    #     return dist_to_closest_key + dist_from_keys_to_exit

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
        
        p_queue = [(self._heuristic(initial_state, exit_pos), 0, initial_state, PathNode(val=None))]
        heapq.heapify(p_queue)

        best_cost = {self._hash_state(initial_state): 0}
        
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
                if step_cost <= 0: step_cost = 1 # Fallback
                new_cost = current_cost + step_cost
                
                state_hash = self._hash_state(new_state)

                # If this is a better path to this state, update and push to the queue
                if new_cost < best_cost.get(state_hash, float("inf")):
                    best_cost[state_hash] = new_cost
                    
                    # h(n): Heuristic cost from the new state to the goal
                    heuristic_cost = self._heuristic(new_state, exit_pos)
                    
                    # f(n) = g(n) + h(n)
                    priority = new_cost + heuristic_cost
                    
                    new_path = PathNode(val=move, parent=path)
                    heapq.heappush(p_queue, (priority, new_cost, new_state, new_path))
        
        # No solution found
        self.stats['time_taken'] = time.time() - start_time
        return None

