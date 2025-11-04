import pygame
from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.input.input_handler import InputHandler
from src.Lava_Aqua.states.game_result import GameResult
from src.Lava_Aqua.graphics.renderer import Renderer

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