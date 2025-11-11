"""Concrete controller implementations for different play modes."""

from typing import Optional
import time
import pygame

from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.core.constants import Direction
from .base_controller import BaseController


class PlayerController(BaseController):
    """Controller for human player mode."""
    
    def process_input(self) -> tuple[Optional[Direction], Optional[str]]:
        """Process keyboard input from user.
        
        Returns:
            Tuple of (movement_direction, action_string)
        """
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, 'quit'
            
            elif event.type == pygame.KEYDOWN:
                # Movement keys
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    return Direction.LEFT, None
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    return Direction.RIGHT, None
                elif event.key in (pygame.K_UP, pygame.K_w):
                    return Direction.UP, None
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    return Direction.DOWN, None
                
                # Action keys
                elif event.key == pygame.K_r:
                    return None, 'reset'
                elif event.key in (pygame.K_u, pygame.K_z):
                    return None, 'undo'
                elif event.key == pygame.K_ESCAPE:
                    return None, 'quit'
        
        return None, None
    
    def on_level_start(self) -> None:
        """Called when level starts."""
        print(f"Starting {self.game_logic.get_level_description()}")
        print("Controls: Arrow Keys to move, R to reset, U to undo, ESC to quit")
    
    def on_level_complete(self) -> None:
        """Called when level is completed."""
        stats = self.get_stats()
        print(f"Level {stats['level']} completed!")
        print(f"Moves: {stats['moves']}, Time: {stats['elapsed_time']:.1f}s")
    
    def on_game_over(self) -> None:
        """Called when game over occurs."""
        print(f"Game Over at move {self.game_logic.moves}")
