
import pygame
import sys

from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.core.constants import GameResult
from src.Lava_Aqua.app.level_runner import LevelRunner

class GameApplication:
    """Main game application."""
    
    def __init__(self):
        """Initialize the game application."""
        self.game_logic = None
        self._print_welcome()
        self._initialize_game()
    
    def _print_welcome(self) -> None:
        """Print welcome message."""
        print("🎮 Lava & Aqua")
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
            print(f"\n📦 Loaded {total_levels} levels")
        except Exception as e:
            print(f"❌ Error loading game: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def run(self) -> None:
        """Run the main game loop."""
        while not self.game_logic.is_last_level() or not self.game_logic.level_complete:
            current_level = self.game_logic.get_level_number()
            level_name = self.game_logic.get_level_name()
            total_levels = self.game_logic.get_total_levels()
            
            try:
                print(f"\n🔥 Level {current_level}/{total_levels}: {level_name}")
                
                level_runner = LevelRunner(self.game_logic)
                result = level_runner.run()
                
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
                    print(f"💀 Restarting level {current_level}: {level_name}")
                    
            except Exception as e:
                print(f"❌ Error running level: {e}")
                import traceback
                traceback.print_exc()
                break
        
        self._cleanup()
    
    def _print_victory(self) -> None:
        """Print victory message."""
        print("\n" + "=" * 40)
        print("🎉 CONGRATULATIONS!")
        print("You beat all levels!")
        print("=" * 40)
    
    def _cleanup(self) -> None:
        """Clean up and exit."""
        print("\nThanks for playing! 👋")
        pygame.quit()
        sys.exit(0)