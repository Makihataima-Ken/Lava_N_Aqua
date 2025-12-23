import pygame
import sys
from typing import Optional, Dict, Tuple
import time

from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.core.constants import GameResult
from src.Lava_Aqua.controllers.base_controller import BaseController
from src.Lava_Aqua.controllers.controller_factory import ControllerFactory
from src.Lava_Aqua.algorithms.base_solver import BaseSolver
from src.Lava_Aqua.agents.base_agent import BaseAgent


class GameApplication:
    """Optimized game application with controller factory support."""
    
    # Class constants
    WELCOME_MSG = """🎮 Lava & Aqua
{'=' * 40}
Controls:
  WASD or Arrow Keys - Move
  R - Reset level
  U/Z - Undo last move
  ESC - Quit
{'=' * 40}"""
    
    VICTORY_MSG = f"""
{'=' * 40}
🎉 CONGRATULATIONS!
You beat all levels!
{'=' * 40}"""
    
    def __init__(self):
        """Initialize the game application."""
        self.game_logic = self._initialize_game()
        self.current_controller: Optional[BaseController] = None
    
    def _initialize_game(self) -> GameLogic:
        """Initialize game logic."""
        try:
            game_logic = GameLogic()
            print(f"\n✅ Loaded {game_logic.get_total_levels()} levels")
            return game_logic
        except Exception as e:
            print(f"❌ Error loading game: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def run(self, solver: BaseSolver = None, agent: BaseAgent = None,
            move_delay: float = 0.2, visualize: bool = True, agent_path: str = None) -> None:
        """Run the main game loop.
        
        Args:
            solver: Optional solver algorithm for solver mode
            agent: Optional RL agent for RL mode
            move_delay: Delay between moves in seconds
            visualize: Whether to render the game
            agent_path: Path to load agent from
        """
        if agent:
            self._run_with_rl_agent(agent, move_delay, visualize, agent_path)
        elif solver:
            self._run_with_solver(solver, move_delay, visualize)
        else:
            self._run_player_mode()
    
    def _run_player_mode(self) -> None:
        """Run the main game loop for user play mode."""
        print(self.WELCOME_MSG)
        
        while self._should_continue():
            try:
                print(f"\n🎮 Lava & Aqua - Level {self.game_logic.get_level_description()}")
                
                self.current_controller = ControllerFactory.create_player(self.game_logic)
                result = self.current_controller.run_level()
                
                if not self._handle_level_result(result):
                    break
                    
            except Exception as e:
                self._handle_error("running level", e)
                break
        
        self._cleanup()
    
    def _run_with_solver(self, solver: BaseSolver, move_delay: float = 0.2, 
                        visualize: bool = True) -> None:
        """Run game with algorithm solver controller."""
        print(f"\n🤖 Starting solver mode with {solver.name}")
        print("=" * 60)
        
        total_stats = {'levels_solved': 0, 'total_moves': 0, 'total_time': 0.0, 'failed_levels': []}
        
        try:
            while self._should_continue():
                try:
                    print(f"\n🎮 Lava & Aqua - Level {self.game_logic.get_level_description()}")
                    
                    self.current_controller = ControllerFactory.create_solver(
                        self.game_logic, solver, move_delay=move_delay, visualize=visualize
                    )
                    
                    result = self.current_controller.run_level()
                    
                    if result == GameResult.QUIT:
                        break
                    elif result == GameResult.WIN:
                        self._update_solver_stats(total_stats, solver)
                        if not self._advance_level():
                            self._print_solver_summary(total_stats)
                            break
                    elif result == GameResult.CONTINUE:
                        self._record_failed_level(total_stats)
                        if not self._advance_level(silent=True):
                            break
                        
                except Exception as e:
                    self._handle_error("solving level", e)
                    break
        finally:
            self._print_solver_summary(total_stats)
            self._cleanup()
    
    def _run_with_rl_agent(self, agent: BaseAgent, move_delay: float = 0.05,
                          visualize: bool = False, agent_path: str = None) -> None:
        """Run game with reinforcement learning agent."""
        print(f"\n🤖 Starting RL mode with {agent.name}")
        print("=" * 60)
        
        try:
            if agent_path:
                agent.load(agent_path)
                print(f"📂 Agent loaded from '{agent_path}'")
            
            self.current_controller = ControllerFactory.create_rl(
                game_logic=self.game_logic,
                agent=agent,
                move_delay=move_delay
            )
            
            # Training
            print("\n📚 Starting training phase...")
            training_stats = self.current_controller.train(
                num_episodes=1000,
                eval_frequency=100,
                visualize=visualize
            )
            
            # Save and evaluate
            agent.save(f"{agent.name.lower()}_agent.pkl")
            print(f"\n💾 Agent saved to {agent.name.lower()}_agent.pkl")
            
            self.current_controller.plot_training_curves()
            
            print("\n" + "=" * 60)
            print("📊 FINAL EVALUATION")
            print("=" * 60)
            eval_stats = self.current_controller.evaluate(num_episodes=100, visualize=False)
            
            self._print_rl_summary(training_stats, eval_stats)
            
            # Visualization
            print("\n🎬 Running visualization episode...")
            result = self.current_controller.run_level(visualize=True, agent_path=None)
            print("✅ Agent successfully completed the level!" if result == GameResult.WIN 
                  else "❌ Agent failed to complete the level")
            
        except Exception as e:
            self._handle_error("RL mode", e)
        finally:
            self._cleanup()
    
    def train_rl_agent(self, agent: BaseAgent, num_episodes: int = 1000,
                      eval_frequency: int = 100, visualize: bool = False,
                      save_path: str = 'qlearning_agent.pkl') -> dict:
        """Train an RL agent on the current level."""
        print(f"\n🎓 Training {agent.name} on {self.game_logic.get_level_description()}")
        
        self.current_controller = ControllerFactory.create_rl(
            self.game_logic, agent=agent, move_delay=0.05
        )
        
        training_stats = self.current_controller.train(
            num_episodes=num_episodes,
            eval_frequency=eval_frequency,
            visualize=visualize
        )
        
        if save_path:
            agent.save(save_path)
            print(f"\n💾 Agent saved to '{save_path}'")
        
        return training_stats
    
    # Helper methods
    def _should_continue(self) -> bool:
        """Check if game should continue to next level."""
        return not self.game_logic.is_last_level() or not self.game_logic.level_complete
    
    def _handle_level_result(self, result: GameResult) -> bool:
        """Handle level completion result. Returns True to continue, False to quit."""
        if result == GameResult.QUIT:
            return False
        elif result == GameResult.WIN:
            if self.game_logic.is_last_level():
                print(self.VICTORY_MSG)
                return False
            return self._advance_level()
        elif result == GameResult.RESTART:
            self.game_logic.reset_level()
            print(f"🔄 Restarting level {self.game_logic.get_level_description()}")
        return True
    
    def _advance_level(self, silent: bool = False) -> bool:
        """Advance to next level. Returns True if successful."""
        if not self.game_logic.next_level():
            if not silent:
                print("No more levels!")
            return False
        return True
    
    def _update_solver_stats(self, stats: Dict, solver: BaseSolver) -> None:
        """Update solver statistics after successful level."""
        stats['levels_solved'] += 1
        stats['total_moves'] += self.game_logic.moves
        stats['total_time'] += solver.stats['time_taken']
    
    def _record_failed_level(self, stats: Dict) -> None:
        """Record a failed level in statistics."""
        stats['failed_levels'].append(
            (self.game_logic.get_level_number(), self.game_logic.get_level_name())
        )
        print(f"\n⚠️ Solver failed on level {self.game_logic.get_level_description()}")
    
    def _handle_error(self, context: str, error: Exception) -> None:
        """Handle and log errors."""
        print(f"❌ Error {context}: {error}")
        import traceback
        traceback.print_exc()
    
    def _print_solver_summary(self, stats: Dict) -> None:
        """Print summary of solver performance."""
        print("\n" + "=" * 60)
        print("📊 SOLVER SUMMARY")
        print("=" * 60)
        print(f"✅ Levels solved: {stats['levels_solved']}")
        print(f"🎯 Total moves: {stats['total_moves']}")
        print(f"⏱️ Total time: {stats['total_time']:.2f}s")
        
        if stats['levels_solved'] > 0:
            print(f"📈 Average moves per level: {stats['total_moves'] / stats['levels_solved']:.1f}")
            print(f"📈 Average time per level: {stats['total_time'] / stats['levels_solved']:.2f}s")
        
        if stats['failed_levels']:
            print(f"\n❌ Failed levels ({len(stats['failed_levels'])}):")
            for level_num, level_name in stats['failed_levels']:
                print(f"  - Level {level_num}: {level_name}")
        
        print("=" * 60)
    
    def _print_rl_summary(self, training_stats: Dict, eval_stats: Dict) -> None:
        """Print summary of RL training and evaluation."""
        print("\n" + "=" * 60)
        print("📊 RL TRAINING & EVALUATION SUMMARY")
        print("=" * 60)
        
        print(f"\n📚 Training:")
        if 'episode_rewards' in training_stats:
            print(f"  Episodes: {len(training_stats['episode_rewards'])}")
        if 'total_steps' in training_stats:
            print(f"  Total steps: {training_stats['total_steps']}")
        if 'training_time' in training_stats:
            print(f"  Training time: {training_stats['training_time']:.1f}s")
        
        agent_stats = training_stats.get('agent_stats', {})
        if agent_stats:
            print(f"\n🤖 Agent Statistics:")
            for key, value in agent_stats.items():
                print(f"  {key}: {value:.4f}" if isinstance(value, float) else f"  {key}: {value}")
        
        print(f"\n📊 Final Evaluation ({eval_stats['num_episodes']} episodes):")
        print(f"  ✅ Success rate: {eval_stats['success_rate']:.1%}")
        print(f"  🎯 Success count: {eval_stats['success_count']}/{eval_stats['num_episodes']}")
        print(f"  🏆 Avg reward: {eval_stats['avg_reward']:.2f} ± {eval_stats.get('std_reward', 0):.2f}")
        print(f"  👣 Avg steps: {eval_stats['avg_steps']:.1f} ± {eval_stats.get('std_steps', 0):.1f}")
        print("=" * 60)
    
    def _cleanup(self) -> None:
        """Clean up and exit."""
        print("\n👋 Thanks for playing!")
        pygame.quit()
        sys.exit(0)