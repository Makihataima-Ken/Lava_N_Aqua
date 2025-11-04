import pygame
from typing import Tuple
from ..core.constants import Color, TILE_SIZE

class Box:
    def __init__(self, position: Tuple[int, int]) -> None:
        """Create a box entity.
        
        Args:
            position: Starting position as (x, y) tuple
        """
        # Store as list to allow modification, or use tuple
        self._position = list(position)  # Convert to list for mutability
        
    def get_position(self) -> Tuple[int, int]:
        """Get box's position.
        
        Returns:
            Position as (x, y) tuple
        """
        return tuple(self._position)
    
    def set_position(self, position: Tuple[int, int]) -> None:
        """Set box's position.
        
        Args:
            position: New position as (x, y) tuple
        """
        self._position = list(position)
        
    def draw(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:
        """Draw box on surface.
        
        Args:
            surface: Pygame surface to draw on
            offset_x: X offset for grid
            offset_y: Y offset for grid
        """
        # Get position as (x, y)
        x, y = self._position
        
        # Calculate pixel position
        pixel_x = offset_x + x * TILE_SIZE
        pixel_y = offset_y + y * TILE_SIZE
        
        # Draw box as a rectangle (for simplicity)
        box_rect = pygame.Rect(pixel_x, pixel_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, Color.BOX, box_rect)