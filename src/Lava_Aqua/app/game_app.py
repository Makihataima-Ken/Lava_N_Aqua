import pygame
import sys
from typing import Optional

from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.core.constants import GameResult
from src.Lava_Aqua.controllers.base_controller import BaseController
from src.Lava_Aqua.controllers.controller_factory import ControllerFactory, ControllerType
from src.Lava_Aqua.algorithms.base_solver import BaseSolver


class GameApplication:
    """Main game application with controller factory support."""
    
    def __init__(self):
        """Initialize the game application."""
        self.game_logic = None
        self.current_controller: Optional[BaseController] = None
        
        self._initialize_game()
    
    def _print_welcome(self) -> None:
        """Print welcome message."""
        print(" Lava & Aqua")
        print("=" * 40)
        print("Controls:")
        print("  WASD or Arrow Keys - Move")
        print("  R - Reset level")
        print("  U/Z - Undo last move")
        print("  ESC - Quit")
        print("=" * 40)
    
    def _initialize_game(self) -> None:
        """Initialize game logic."""
        try:
            self.game_logic = GameLogic()
            total_levels = self.game_logic.get_total_levels()
            print(f"\n Loaded {total_levels} levels")
        except Exception as e:
            print(f"Error loading game: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def run(self,solver: BaseSolver = None, move_delay: float = 0.2, 
                       visualize: bool = True) -> None:
        """Run the main game loop."""
        if solver:
            self._run_with_solver(solver, move_delay, visualize)
        else:
            self._run_player_mode()
            
    def _run_player_mode(self) -> None:
        """Run the main game loop (for user play mode)."""
        
        self._print_welcome()
        
        while not self.game_logic.is_last_level() or not self.game_logic.level_complete:
            
            try:
                print(f"\n Lava & Aqua - Level  {self.game_logic.get_level_description()}")
                
                self.current_controller = ControllerFactory.create_player(self.game_logic)
                result = self.current_controller.run_level()
                
                # Handle result
                if result == GameResult.QUIT:
                    break
                elif result == GameResult.WIN:
                    if self.game_logic.is_last_level():
                        self._print_victory()
                        break
                    else:
                        if not self.game_logic.next_level():
                            print("No more levels!")
                            break
                elif result == GameResult.RESTART:
                    self.game_logic.reset_level()
                    print(f" Restarting level {self.game_logic.get_level_description()}")
                    
            except Exception as e:
                print(f" Error running level: {e}")
                import traceback
                traceback.print_exc()
                break
        
        self._cleanup()
    
    def _run_with_solver(self, solver: BaseSolver, move_delay: float = 0.2, 
                       visualize: bool = True) -> None:
        """Run game with algorithm solver controller.
        
        Args:
            solver: Solver algorithm instance to use
            move_delay: Delay between moves in seconds
            visualize: Whether to render the solving process
        """
        print(f"\n Starting solver mode with {solver.name}")
        print("=" * 60)
        
        total_stats = {
            'levels_solved': 0,
            'total_moves': 0,
            'total_time': 0.0,
            'failed_levels': []
        }
        
        try:
            while not self.game_logic.is_last_level() or not self.game_logic.level_complete:
                
                try:
                    print(f"\n Lava & Aqua - Level {self.game_logic.get_level_description()}")
                    
                    self.current_controller = ControllerFactory.create_solver(
                        self.game_logic,
                        solver,
                        move_delay=move_delay,
                        visualize=visualize
                    )
                    
                    # Run solver on level
                    result = self.current_controller.run_level()
                    
                    # Handle result
                    if result == GameResult.QUIT:
                        break
                    elif result == GameResult.WIN:
                        # Update stats
                        total_stats['levels_solved'] += 1
                        total_stats['total_moves'] += self.game_logic.moves
                        total_stats['total_time'] += solver.stats['time_taken']
                        
                        # Check if last level
                        if self.game_logic.is_last_level():
                            self._print_victory()
                            self._print_solver_summary(total_stats)
                            break
                        else:
                            if not self.game_logic.next_level():
                                print("No more levels!")
                                self._print_solver_summary(total_stats)
                                break
                    elif result == GameResult.CONTINUE:
                        # Solver failed
                        total_stats['failed_levels'].append(
                            (self.game_logic.get_level_number(),self.game_logic.get_level_name())
                        )
                        print(f"\n Solver failed on level {self.game_logic.get_level_description()}")

                        if not self.game_logic.next_level():
                            print("No more levels!")
                            break
                        
                except Exception as e:
                    print(f" Error solving level: {e}")
                    import traceback
                    traceback.print_exc()
                    break
        
        finally:
            self._print_solver_summary(total_stats)
            self._cleanup()
    
    def _print_solver_summary(self, stats: dict) -> None:
        """Print summary of solver performance.
        
        Args:
            stats: Dictionary of solver statistics
        """
        print("\n" + "=" * 60)
        print("SOLVER SUMMARY")
        print("=" * 60)
        print(f"Levels solved: {stats['levels_solved']}")
        print(f"Total moves: {stats['total_moves']}")
        print(f"Total time: {stats['total_time']:.2f}s")
        
        if stats['total_moves'] > 0:
            avg_moves = stats['total_moves'] / stats['levels_solved']
            print(f"Average moves per level: {avg_moves:.1f}")
        
        if stats['failed_levels']:
            print(f"\nFailed levels ({len(stats['failed_levels'])}):")
            for level_num, level_name in stats['failed_levels']:
                print(f"  - Level {level_num}: {level_name}")
        
        print("=" * 60)
    
    def _print_victory(self) -> None:
        """Print victory message."""
        print("\n" + "=" * 40)
        print("CONGRATULATIONS! \nYou beat all levels!")
        print("=" * 40)
    
    def _cleanup(self) -> None:
        """Clean up and exit."""
        print("\nThanks for playing!")
        pygame.quit()
        sys.exit(0)