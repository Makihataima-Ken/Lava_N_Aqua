import pygame
import time
from src.Lava_Aqua.core.game import GameLogic

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
        # tile_grid = game_logic.get_grid()
        # if tile_grid:
        game_logic.draw(self.screen, 0, 0, animation_time)
    
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