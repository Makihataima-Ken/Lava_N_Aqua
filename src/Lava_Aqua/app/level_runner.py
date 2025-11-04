import pygame
import time
from typing import Tuple, Optional
from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.core.constants import TILE_SIZE, GameResult
from src.Lava_Aqua.graphics.renderer import Renderer
from src.Lava_Aqua.input.input_handler import InputHandler
from src.Lava_Aqua.states.state_manager import GameStateManager


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