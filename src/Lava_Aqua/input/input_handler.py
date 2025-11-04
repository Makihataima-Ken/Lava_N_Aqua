import pygame
from typing import Tuple, Optional

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