"""Main game application with improved encapsulation."""

import pygame
import sys
import time
from typing import Tuple, Optional
from enum import Enum

from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.core.constants import TILE_SIZE


class GameResult(Enum):
    """Possible outcomes of a level."""
    WIN = 'win'
    RESTART = 'restart'
    QUIT = 'quit'
    CONTINUE = 'continue'


class InputHandler:
    """Handles all keyboard input."""
    
    @staticmethod
    def process_events() -> Tuple[Optional[Tuple[int, int]], Optional[str]]:
        """Process pygame events.
        
        Returns:
            Tuple of (movement_direction, action)
            - movement_direction: (dx, dy) or None
            - action: 'reset', 'undo', 'quit', or None
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, 'quit'
            
            elif event.type == pygame.KEYDOWN:
                # Movement keys
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    return (-1, 0), None
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    return (1, 0), None
                elif event.key in (pygame.K_UP, pygame.K_w):
                    return (0, -1), None
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    return (0, 1), None
                
                # Action keys
                elif event.key == pygame.K_r:
                    return None, 'reset'
                elif event.key in (pygame.K_u, pygame.K_z):
                    return None, 'undo'
                elif event.key == pygame.K_ESCAPE:
                    return None, 'quit'
        
        return None, None


class Renderer:
    """Handles all rendering operations."""
    
    def __init__(self, screen: pygame.Surface):
        """Initialize renderer.
        
        Args:
            screen: Pygame surface to draw on
        """
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 74)
        self.medium_font = pygame.font.Font(None, 36)
    
    def clear(self) -> None:
        """Clear the screen."""
        self.screen.fill((0, 0, 0))
    
    def draw_game_state(self, game_logic: GameLogic, animation_time: float) -> None:
        """Draw the current game state.
        
        Args:
            game_logic: Game logic instance
            animation_time: Current animation time
        """
        tile_grid = game_logic.get_grid()
        if tile_grid:
            tile_grid.draw(self.screen, 0, 0, animation_time)
        
        game_logic.lava.draw(self.screen, 0, 0, animation_time)
        game_logic.player.draw(self.screen, 0, 0)
    
    def draw_ui_info(self, level_num: int, total_levels: int, moves: int, lava_count: int) -> None:
        """Draw UI information bar.
        
        Args:
            level_num: Current level number
            total_levels: Total number of levels
            moves: Number of moves made
            lava_count: Number of lava tiles
        """
        info_text = (f'Level {level_num}/{total_levels} | '
                    f'Moves: {moves} | '
                    f'Lava: {lava_count} | '
                    f'R: Reset | U: Undo | WASD/Arrows: Move')
        text = self.font.render(info_text, True, (255, 255, 255))
        
        # Draw text background for readability
        text_bg = pygame.Surface((text.get_width() + 10, text.get_height() + 4))
        text_bg.set_alpha(180)
        text_bg.fill((0, 0, 0))
        self.screen.blit(text_bg, (5, 5))
        self.screen.blit(text, (10, 7))
    
    def draw_game_over(self, moves: int) -> None:
        """Draw game over screen.
        
        Args:
            moves: Number of moves made
        """
        # Main text
        text = self.large_font.render('GAME OVER', True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(text, text_rect)
        
        # Instruction text
        instruction = self.medium_font.render('Press R to restart | U to undo', True, (255, 255, 255))
        instr_rect = instruction.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 50))
        self.screen.blit(instruction, instr_rect)
    
    def draw_victory(self, moves: int) -> None:
        """Draw victory screen.
        
        Args:
            moves: Number of moves made
        """
        # Main text
        text = self.large_font.render('YOU WIN!', True, (0, 255, 0))
        text_rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(text, text_rect)
        
        # Moves text
        moves_text = self.medium_font.render(f'Moves: {moves}', True, (255, 255, 255))
        moves_rect = moves_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 50))
        self.screen.blit(moves_text, moves_rect)
    
    def flip(self) -> None:
        """Update the display."""
        pygame.display.flip()


class GameStateManager:
    """Manages game state transitions and screen handling."""
    
    def __init__(self, game_logic: GameLogic, renderer: Renderer):
        """Initialize game state manager.
        
        Args:
            game_logic: Game logic instance
            renderer: Renderer instance
        """
        self.game_logic = game_logic
        self.renderer = renderer
        self.input_handler = InputHandler()
    
    def handle_game_over(self, animation_time: float) -> GameResult:
        """Handle game over state.
        
        Args:
            animation_time: Current animation time
            
        Returns:
            GameResult indicating next action
        """
        print("Dead! Press R to restart or ESC to quit.")
        
        # Draw final state
        self.renderer.clear()
        self.renderer.draw_game_state(self.game_logic, animation_time)
        self.renderer.draw_game_over(self.game_logic.moves)
        self.renderer.flip()
        
        # Wait for input
        while True:
            movement, action = self.input_handler.process_events()
            
            if action == 'quit':
                return GameResult.QUIT
            elif action == 'reset':
                return GameResult.RESTART
            elif action == 'undo':
                if self.game_logic.undo():
                    return GameResult.CONTINUE
    
    def handle_victory(self, animation_time: float) -> GameResult:
        """Handle victory state.
        
        Args:
            animation_time: Current animation time
            
        Returns:
            GameResult indicating next action
        """
        print(f"You win! Completed in {self.game_logic.moves} moves!")
        
        # Draw final state
        self.renderer.clear()
        self.renderer.draw_game_state(self.game_logic, animation_time)
        self.renderer.draw_victory(self.game_logic.moves)
        self.renderer.flip()
        
        # Wait before continuing
        pygame.time.wait(2000)
        return GameResult.WIN


class LevelRunner:
    """Runs a single level of the game."""
    
    def __init__(self, game_logic: GameLogic):
        """Initialize level runner.
        
        Args:
            game_logic: Game logic instance
        """
        self.game_logic = game_logic
        self.screen = self._setup_screen()
        self.renderer = Renderer(self.screen)
        self.state_manager = GameStateManager(game_logic, self.renderer)
        self.input_handler = InputHandler()
        self.clock = pygame.time.Clock()
        self.start_time = time.time()
    
    def _setup_screen(self) -> pygame.Surface:
        """Setup pygame screen based on grid dimensions.
        
        Returns:
            Pygame surface
        """
        tile_grid = self.game_logic.get_grid()
        
        if not tile_grid:
            raise ValueError("No grid available")
        
        pygame.init()
        screen_width = tile_grid.get_width() * TILE_SIZE
        screen_height = tile_grid.get_height() * TILE_SIZE
        screen = pygame.display.set_mode((screen_width, screen_height))
        
        level_name = self.game_logic.get_level_name()
        level_num = self.game_logic.get_level_number()
        total_levels = self.game_logic.get_total_levels()
        
        pygame.display.set_caption(f"Lava & Aqua - Level {level_num}/{total_levels}: {level_name}")
        
        return screen
    
    def run(self) -> GameResult:
        """Run the level loop.
        
        Returns:
            GameResult indicating outcome
        """
        while True:
            animation_time = time.time() - self.start_time
            
            # Handle input
            movement, action = self.input_handler.process_events()
            
            if action == 'quit':
                return GameResult.QUIT
            elif action == 'reset':
                self.game_logic.reset_level()
                print(f"Level reset! (Moves: {self.game_logic.moves})")
                continue
            elif action == 'undo':
                if self.game_logic.undo():
                    print(f"Undo! (Moves: {self.game_logic.moves})")
            elif movement:
                self.game_logic.move_player(movement)
            
            # Check game state
            if self.game_logic.game_over:
                result = self.state_manager.handle_game_over(animation_time)
                if result != GameResult.CONTINUE:
                    return result
            
            if self.game_logic.level_complete:
                return self.state_manager.handle_victory(animation_time)
            
            # Draw everything
            self.renderer.clear()
            self.renderer.draw_game_state(self.game_logic, animation_time)
            self.renderer.draw_ui_info(
                self.game_logic.get_level_number(),
                self.game_logic.get_total_levels(),
                self.game_logic.moves,
                self.game_logic.lava.count()
            )
            self.renderer.flip()
            
            self.clock.tick(60)


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


def main():
    """Entry point for the game."""
    app = GameApplication()
    app.run()


if __name__ == '__main__':
    main()