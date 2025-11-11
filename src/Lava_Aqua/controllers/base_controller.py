"""Base controller"""

from abc import ABC, abstractmethod
import time
from typing import Optional
import pygame

from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.core.constants import GameResult, Direction
from src.Lava_Aqua.graphics.renderer import Renderer


class BaseController(ABC):
    """Abstract base controller for game execution modes."""
    
    def __init__(self, game_logic: GameLogic):
        """Initialize base controller.
        
        Args:
            game_logic: Game logic instance
        """
        self.game_logic = game_logic
        self.renderer = self._setup_renderer()
        self.start_time = time.time()
        self.running = True
        
    def _setup_renderer(self) -> Renderer:
        """Setup renderer based on grid dimensions.
        
        Returns:
            Renderer instance
        """
        tile_grid = self.game_logic.get_grid()
        
        if not tile_grid:
            raise ValueError("No grid available")
        
        screen_width = tile_grid.get_width()
        screen_height = tile_grid.get_height() 
        caption = self.game_logic.get_level_description()
        
        return Renderer(screen_width, screen_height, caption)
    
    @abstractmethod
    def process_input(self) -> tuple[Optional[Direction], Optional[str]]:
        """Process input for this controller mode.
        
        Returns:
            Tuple of (movement_direction, action_string)
            action can be: 'quit', 'reset', 'undo', or None
        """
        pass
    
    @abstractmethod
    def on_level_start(self) -> None:
        """Called when a level starts. Override for custom behavior."""
        pass
    
    @abstractmethod
    def on_level_complete(self) -> None:
        """Called when a level is completed. Override for custom behavior."""
        pass
    
    @abstractmethod
    def on_game_over(self) -> None:
        """Called when game over occurs. Override for custom behavior."""
        pass
    
    def run_level(self) -> GameResult:
        """Run the main game loop for a level.
        
        Returns:
            GameResult indicating outcome
        """
        self.on_level_start()
        self.running = True
        
        while self.running:
            # Process input (mode-specific)
            movement, action = self.process_input()
            
            # Handle actions
            if action == 'quit':
                return GameResult.QUIT
            elif action == 'reset':
                self.reset_level()
                continue
            elif action == 'undo':
                self.undo_move()
            elif movement:
                self.execute_move(movement)
            
            # Check game state
            if self.game_logic.game_over:
                result = self.handle_game_over_state()
                if result != GameResult.CONTINUE:
                    return result
            
            if self.game_logic.level_complete:
                return self.handle_victory_state()
            
            # Render
            self.render_frame()
        
        return GameResult.QUIT
    
    def execute_move(self, direction: Direction) -> bool:
        """Execute a player move.
        
        Args:
            direction: Direction to move
            
        Returns:
            True if move was successful
        """
        return self.game_logic.move_player(direction)
    
    def reset_level(self) -> None:
        """Reset the current level."""
        self.game_logic.reset_level()
        self.start_time = time.time()
        print(f"Level reset! (Moves: {self.game_logic.moves})")
    
    def undo_move(self) -> bool:
        """Undo the last move.
        
        Returns:
            True if undo was successful
        """
        if self.game_logic.undo():
            print(f"Undo! (Moves: {self.game_logic.moves})")
            return True
        return False
    
    def render_frame(self) -> None:
        """Render the current game state."""
        animation_time = time.time() - self.start_time
        
        self.renderer.clear()
        self.renderer.draw_game_state(self.game_logic, animation_time)
        self.renderer.draw_ui_info(
            self.game_logic.get_level_number(),
            self.game_logic.get_total_levels(),
            self.game_logic.moves,
            self.game_logic.lava.count()
        )
        self.renderer.flip()
    
    def handle_game_over_state(self) -> GameResult:
        """Handle game over state with rendering.
        
        Returns:
            GameResult indicating next action
        """
        print("Dead! Press R to restart or ESC to quit.")
        
        animation_time = time.time() - self.start_time
        self.renderer.clear()
        self.renderer.draw_game_state(self.game_logic, animation_time)
        self.renderer.draw_game_over(self.game_logic.moves)
        self.renderer.flip()
        
        # Trigger custom handler
        self.on_game_over()
        
        # Wait for input (overridable by subclasses)
        return self._wait_for_game_over_input()
    
    def _wait_for_game_over_input(self) -> GameResult:
        """Wait for input during game over state.
        
        Returns:
            GameResult indicating next action
        """
        while self.running:
            movement, action = self.process_input()
            
            if action == 'quit':
                return GameResult.QUIT
            elif action == 'reset':
                return GameResult.RESTART
            elif action == 'undo':
                if self.undo_move():
                    return GameResult.CONTINUE
        
        return GameResult.QUIT
    
    def handle_victory_state(self) -> GameResult:
        """Handle victory state with rendering.
        
        Returns:
            GameResult indicating next action
        """
        print(f"You win! Completed in {self.game_logic.moves} moves!")
        
        animation_time = time.time() - self.start_time
        self.renderer.clear()
        self.renderer.draw_game_state(self.game_logic, animation_time)
        self.renderer.draw_victory(self.game_logic.moves)
        self.renderer.flip()
        
        # Trigger custom handler
        self.on_level_complete()
        
        # Wait before continuing
        pygame.time.wait(2000)
        return GameResult.WIN
    
    
    def cleanup(self) -> None:
        """Cleanup resources. Override for custom cleanup."""
        pass
    
    def get_stats(self) -> dict:
        """Get current game statistics.
        
        Returns:
            Dictionary of game stats
        """
        return {
            'level': self.game_logic.get_level_number(),
            'total_levels': self.game_logic.get_total_levels(),
            'moves': self.game_logic.moves,
            'lava_count': self.game_logic.lava.count(),
            'elapsed_time': time.time() - self.start_time,
            'game_over': self.game_logic.game_over,
            'level_complete': self.game_logic.level_complete
        }