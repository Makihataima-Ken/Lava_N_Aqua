from typing import Optional
import time
import pygame

from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.core.constants import Direction, GameResult
from src.Lava_Aqua.algorithms.base_solver import BaseSolver
from .base_controller import BaseController


class SolverController(BaseController):
    """Controller for algorithm-based solver mode."""
    
    def __init__(self, game_logic: GameLogic, solver: BaseSolver,
                 move_delay: float = 0.2, visualize: bool = True):
        """Initialize algorithm solver controller.
        
        Args:
            game_logic: Game logic instance
            solver: Solver algorithm to use
            move_delay: Delay between moves in seconds
            visualize: Whether to render the solving process
        """
        super().__init__(game_logic)
        self.solver = solver
        self.move_delay = move_delay
        self.visualize = visualize
        self.solution_moves: list[Direction] = []
        self.current_move_index = 0
        self.solving_complete = False
        self.solving_in_progress = False
    
    def solve_current_level(self) -> bool:
        """Run the solver algorithm on the current level.
        
        Returns:
            True if solution found, False otherwise
        """
        print(f"Running {self.solver.name}...")
        self.solving_in_progress = True
        
        # Reset solver stats
        self.solver.reset_stats()
        
        # Run solver
        start_time = time.time()
        solution = self.solver.solve(self.game_logic)
        solve_time = time.time() - start_time
        
        self.solving_in_progress = False
        
        if solution:
            self.solution_moves = solution
            self.current_move_index = 0
            self.solving_complete = False
            
            # Update stats
            self.solver.stats['time_taken'] = solve_time
            self.solver.stats['solution_length'] = len(solution)
            
            print(f"Solution found: {len(solution)} moves in {solve_time:.3f}s")
            self.solver.print_stats()
            return True
        else:
            print(f"No solution found (searched for {solve_time:.3f}s)")
            self.solver.print_stats()
            return False
    
    def process_input(self) -> tuple[Optional[Direction], Optional[str]]:
        """Process input for solver mode (handles quit events)."""
        # Check for quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None, 'quit'
                if event.key == pygame.K_SPACE:
                    return None, 'pause'
        
        # Don't execute moves while solving
        if self.solving_in_progress:
            return None, None
        
        # # Return next move from solution
        if self.current_move_index < len(self.solution_moves):
            move = self.solution_moves[self.current_move_index]
            self.current_move_index += 1
            return move, None
        else:
            self.solving_complete = True
            return None, None
    
    def run_level(self) -> GameResult:
        """Run the solver loop for a level."""
        self.on_level_start()
        
        # First, solve the level
        if not self.solve_current_level():
            print("Cannot proceed without solution!")
            pygame.time.wait(2000)
            return GameResult.CONTINUE
        
        # Then execute the solution
        self.running = True
        
        while self.running and not self.solving_complete:
            movement, action = self.process_input()
            
            if action == 'quit':
                return GameResult.QUIT
            elif action == 'pause':
                self.pause_level()
                continue
            
            if movement:
                success = self.execute_move(movement)
                if not success:
                    print(f"Move {self.current_move_index} failed!")
                    self._display_failed_state()
                    return GameResult.QUIT
                
                if self.visualize:
                    time.sleep(self.move_delay)
            
            if self.game_logic.game_over:
                print("Solution led to game over!")
                self._display_failed_state()
                return self.handle_game_over_state()
            
            if self.game_logic.level_complete:
                return self.handle_victory_state()
            
            if self.visualize:
                self.render_frame()
        
        if self.solving_complete and not self.game_logic.level_complete:
            print("Solution executed but level not completed!")
            self._display_failed_state()
            return GameResult.QUIT
        
        return GameResult.QUIT
    
    def _display_failed_state(self) -> None:
        """Display the game state when solution fails."""
        if self.visualize:
            self.render_frame()
            pygame.time.wait(2000)
    
    
    def on_level_start(self) -> None:
        """Called when level starts."""
        print(f"\n{'='*60}")
        print(f"Solving {self.game_logic.get_level_description()}")
        print(f"Algorithm: {self.solver.name}")
        print(f"{'='*60}")
    
    def on_level_complete(self) -> None:
        """Called when level is completed."""
        stats = self.get_stats()
        print(f"\n Solution verified successfully!")
        print(f"  Moves executed: {stats['moves']}")
        print(f"  Execution time: {stats['elapsed_time']:.1f}s")
    
    def on_game_over(self) -> None:
        """Called when game over occurs."""
        print(f" Solution failed at move {self.current_move_index}")