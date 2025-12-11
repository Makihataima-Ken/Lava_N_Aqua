import pygame
import sys
from typing import Optional

from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.core.constants import GameResult
from src.Lava_Aqua.controllers.base_controller import BaseController
from src.Lava_Aqua.controllers.controller_factory import ControllerFactory, ControllerType
from src.Lava_Aqua.algorithms.base_solver import BaseSolver
from src.Lava_Aqua.agents.base_agent import BaseAgent


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
    
    def run(self, solver: BaseSolver = None, agent: BaseAgent = None,
            move_delay: float = 0.2, visualize: bool = True) -> None:
        """Run the main game loop.
        
        Args:
            solver: Optional solver algorithm for solver mode
            agent: Optional RL agent for RL mode
            move_delay: Delay between moves in seconds
            visualize: Whether to render the game
        """
        if agent:
            self._run_with_rl_agent(agent, move_delay, visualize)
        elif solver:
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
                            (self.game_logic.get_level_number(), self.game_logic.get_level_name())
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
    
    def _run_with_rl_agent(self, agent: BaseAgent, move_delay: float = 0.05,
                          visualize: bool = False) -> None:
        """Run game with reinforcement learning agent.
        
        Args:
            agent: RL agent instance to use
            move_delay: Delay between moves in seconds
            visualize: Whether to render the training/evaluation process
        """
        print(f"\n Starting RL mode with {agent.name}")
        print("=" * 60)
        
        try:
            # Create RL controller
            self.current_controller = ControllerFactory.create_rl(
                game_logic=self.game_logic,
                agent=agent,
                move_delay=move_delay,
                max_steps_per_episode=500
            )
            
            # Training mode
            print("\nStarting training phase...")
            training_stats = self.current_controller.train(
                num_episodes=1000,
                eval_frequency=100
            )
            
            self.current_controller.agent.save('qlearning_agent.pkl')
            print("\n Agent saved to 'qlearning_agent.pkl'")
            
            # Final evaluation
            print("\n" + "=" * 60)
            print("FINAL EVALUATION")
            print("=" * 60)
            eval_stats = self.current_controller.evaluate(
                num_episodes=100,
                visualize=visualize
            )
            
            # self._print_rl_summary(training_stats, eval_stats)
            
            self.current_controller.run_level(visualize=True,agent_path="C:\\Users\\ahmad\\Developement\\Lava_and_Aqua\\assets\\trained models\\qlearning_agent.pkl")
            
        except Exception as e:
            print(f" Error in RL mode: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._cleanup()
    
    def train_rl_agent(self, agent: BaseAgent, num_episodes: int = 1000,
                      eval_frequency: int = 100, visualize: bool = False) -> dict:
        """Train an RL agent on the current level.
        
        Args:
            agent: RL agent to train
            num_episodes: Number of training episodes
            eval_frequency: Evaluate every N episodes
            visualize: Whether to render training
            
        Returns:
            Training statistics dictionary
        """
        self.current_controller = ControllerFactory.create_rl(
            self.game_logic,
            agent=agent,
            move_delay=0.05,
            # max_steps_per_episode=10000
        )
        
        return self.current_controller.train(
            num_episodes=num_episodes,
            eval_frequency=eval_frequency
        )
    
    def evaluate_rl_agent(self, agent: BaseAgent, num_episodes: int = 100,
                         visualize: bool = True) -> dict:
        """Evaluate an RL agent on the current level.
        
        Args:
            agent: RL agent to evaluate
            num_episodes: Number of evaluation episodes
            visualize: Whether to render evaluation
            
        Returns:
            Evaluation statistics dictionary
        """
        self.current_controller = ControllerFactory.create_rl(
            self.game_logic,
            agent=agent,
            move_delay=0.2,
            max_steps_per_episode=500
        )
        
        return self.current_controller.evaluate(
            num_episodes=num_episodes,
            visualize=visualize
        )
    
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
    
    def _print_rl_summary(self, training_stats: dict, eval_stats: dict) -> None:
        """Print summary of RL training and evaluation.
        
        Args:
            training_stats: Training statistics
            eval_stats: Evaluation statistics
        """
        print("\n" + "=" * 60)
        print("RL TRAINING & EVALUATION SUMMARY")
        print("=" * 60)
        print(f"\nTraining:")
        print(f"  Total episodes: {training_stats['total_episodes']}")
        print(f"  Total steps: {training_stats['total_steps']}")
        print(f"  Training time: {training_stats['training_time']:.1f}s")
        
        # print(f"\nFinal Evaluation ({eval_stats['num_episodes']} episodes):")
        print(f"  Success rate: {eval_stats['success_rate']:.1%}")
        print(f"  Success count: {eval_stats['success_count']}/{eval_stats['num_episodes']}")
        print(f"  Avg reward: {eval_stats['avg_reward']:.2f} ± {eval_stats['std_reward']:.2f}")
        print(f"  Avg steps: {eval_stats['avg_steps']:.1f} ± {eval_stats['std_steps']:.1f}")
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