import pygame
from typing import Tuple, Optional

from ..core.constants import Direction, Action

class InputHandler:
    """Handles all keyboard input."""
    
    @staticmethod
    def process_events() -> Tuple[Optional[Direction], Optional[Action]]:
        """Process pygame events.
        
        Returns:
            Tuple of (movement_direction, action)
            - movement_direction: (dx, dy) or None
            - action: 'reset', 'undo', 'quit', or None
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, Action.QUIT
            
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
                    return None, Action.RESET
                elif event.key in (pygame.K_u, pygame.K_z):
                    return None, Action.UNDO
                elif event.key == pygame.K_ESCAPE:
                    return None, Action.QUIT
        
        return None, None