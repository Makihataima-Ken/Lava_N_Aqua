from typing import Tuple
import pygame

from ..core.constants import Color, TILE_SIZE


class Player:
    
    def __init__(self, position: Tuple[int, int]) -> None:
        """Create a player entity.
        
        Args:
            position: Starting position as (x, y) tuple
        """
        
        self._position = list(position)  
        
    def get_position(self) -> Tuple[int, int]:
        """Get player's position.
        
        Returns:
            Position as (x, y) tuple
        """
        return tuple(self._position)
    
    def set_position(self, position: Tuple[int, int]) -> None:
        """Set player's position.
        
        Args:
            position: New position as (x, y) tuple
        """
        self._position = list(position)
    
    def draw(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:
        """Draw player on surface.
        
        Args:
            surface: Pygame surface to draw on
            offset_x: X offset for grid
            offset_y: Y offset for grid
        """
        x, y = self._position
        
        # Calculate pixel position
        pixel_x = offset_x + x * TILE_SIZE
        pixel_y = offset_y + y * TILE_SIZE
        
        # Draw player as a circle with border
        center = (pixel_x + TILE_SIZE // 2, pixel_y + TILE_SIZE // 2)
        radius = TILE_SIZE // 3
        
        # Shadow
        pygame.draw.circle(surface, Color.BLACK, 
                          (center[0] + 2, center[1] + 2), radius)
        # Main body
        pygame.draw.circle(surface, Color.PLAYER, center, radius)

        # Border
        pygame.draw.circle(surface, Color.PLAYER_DARK, center, radius, 2)