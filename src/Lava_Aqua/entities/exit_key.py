import pygame
from typing import Tuple
from ..core.constants import Color, TILE_SIZE
import math

class ExitKey:
    """Class representing an exit key entity."""
    
    def __init__(self, position: Tuple[int, int]):
        """Initialize exit key.
        
        Args:
            position: Position as (x, y)
        """
        self._position = position
        self._collected = False
    
    def get_position(self) -> Tuple[int, int]:
        """Get exit key position.
        
        Returns:
            Position as (x, y)
        """
        return self._position
    
    def set_position(self, position: Tuple[int, int]) -> None:
        """Set exit key position.
        
        Args:
            position: New position as (x, y)
        """
        self._position = position
        
    def is_at(self, position: Tuple[int, int]) -> bool:
        """Check if exit key is at given position.
        
        Args:
            position: Position to check as (x, y)
        """
        return self._position == position
    
    def is_collected(self) -> bool:
        """Check if exit key has been collected.
        
        Returns:
            True if collected
        """
        return self._collected
    
    def collect(self) -> None:
        """Mark exit key as collected."""
        self._collected = True
        
    def uncollect(self) -> None:
        """Mark exit key as not collected (for undo)."""
        self._collected = False
    
    def draw(self, surface: pygame.Surface, offset_x: int, offset_y: int, animation_time: float = 0.0) -> None:
        """Draw exit key on given surface.
        
        Args:
            surface: Pygame surface to draw on
            offset_x: X offset for grid
            offset_y: Y offset for grid
        """
        if self._collected:
            return
        
        # Get position as (x, y)
        x, y = self._position
        
        # Calculate pixel position
        pixel_x = offset_x + x * TILE_SIZE
        pixel_y = offset_y + y * TILE_SIZE
        
        center = (pixel_x + TILE_SIZE // 2, pixel_y + TILE_SIZE // 2)
        radius = TILE_SIZE // 5 
        
        # Animate glow
        glow = abs(math.sin(animation_time * 2)) * 0.3 + 0.7
        
        base_color = Color.EXIT
        r = int(base_color[0] * glow)
        g = int(base_color[1] * glow)
        b = int(base_color[2] * glow)
        
        pygame.draw.circle(surface, (r,g,b),center,radius)