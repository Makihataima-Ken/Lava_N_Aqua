import pygame
import time
from src.Lava_Aqua.core.game import GameLogic
from ..core.constants import TILE_SIZE

class Renderer:
    """Handles all rendering operations."""
    
    def __init__(self, width:int, height:int, caption:str="Lava & Aqua"):
        """Initialize renderer.
        
        Args:
            screen: Pygame surface to draw on
        """
        self.screen = self._setup_screen(width, height, caption)
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 74)
        self.medium_font = pygame.font.Font(None, 36)
        
    def _setup_screen(self, width:int, height:int, caption:str="Lava & Aqua") -> pygame.Surface:
        """Setup pygame screen based on grid dimensions.
        
        Returns:
            width: Screen width
            height: Screen height
            caption: Window caption
        """
        
        pygame.init()
        screen_width = width * TILE_SIZE
        screen_height = height * TILE_SIZE
        screen = pygame.display.set_mode((screen_width, screen_height))
        
        pygame.display.set_caption(caption)
        
        return screen
    
    def clear(self) -> None:
        """Clear the screen."""
        self.screen.fill((0, 0, 0))

    def draw_game_state(self, game_logic: GameLogic, animation_time: float = 0.0) -> None:
        """Draw the current game state.

        Args:
            game_logic: Game logic instance
            animation_time: Current animation time
        """
        grid = game_logic.grid
        
        if not grid:
            raise ValueError("No grid available to draw")

        grid.draw(self.screen, 0, 0, animation_time)
        game_logic.lava.draw(self.screen, 0, 0, animation_time)
        game_logic.aqua.draw(self.screen, 0, 0, animation_time)
        
        for box in game_logic.boxes:
            box.draw(self.screen, 0, 0)
            
        for wall in game_logic.temp_walls:
            wall.draw(self.screen, 0, 0, animation_time)
            
        for key in game_logic.exit_keys:
            key.draw(self.screen, 0, 0, animation_time)
            
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
        
    def draw_game(self,game_logic: GameLogic, animation_time: float = 0.0):
            
        self.clear()
        self.draw_game_state(game_logic, animation_time)
        self.draw_ui_info(
            game_logic.get_level_number(),
            game_logic.get_total_levels(),
            game_logic.moves,
            game_logic.lava.count()
           )            
        self.flip()
        
    
    def draw_solver_step(
        self,
        game_logic: GameLogic,
        delay: float = 0.15,
        show_ui: bool = True,
        animation_time: float = 0.0
    ) -> None:
        """
        Render a single solver step while keeping the window responsive.

        Args:
            game_logic: Game state after the solver applied a move.
            delay: Time in seconds to wait after rendering (per move).
            show_ui: Whether to draw the standard UI info bar.
            animation_time: Animation time (optional).
        """
        # Process window events so the OS doesn't think the window froze
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit()

        # Draw main scene
        self.clear()
        self.draw_game_state(game_logic, animation_time)

        # Optional UI bar
        if show_ui:
            self.draw_ui_info(
                game_logic.get_level_number(),
                game_logic.get_total_levels(),
                game_logic.moves,
                game_logic.lava.count()
            )

        # Update frame
        self.flip()

        # Control solver animation speed
        if delay > 0:
            time.sleep(delay)


    def draw_training_info(self, episode, epsilon, reward):
        text = self.font.render(
            f"Episode: {episode} | ε: {epsilon:.3f} | Reward: {reward:.1f}",
            True,
            (255, 255, 0)
        )
        self.screen.blit(text, (10, self.screen.get_height() - 30))
