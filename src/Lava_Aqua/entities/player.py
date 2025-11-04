"""Player entity."""

from typing import Tuple
import pygame

from ..core.constants import Color, TILE_SIZE


class Player:
    """Player character."""
    
    def __init__(self, position: Tuple[int, int]) -> None:
        """Create a player entity.
        
        Args:
            position: Starting position as (x, y) tuple
        """
        # Store as list to allow modification, or use tuple
        self._position = list(position)  # Convert to list for mutability
        
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
    
    def move(self, direction: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate new position after move.
        
        Args:
            direction: Direction tuple (dx, dy)
            
        Returns:
            New position (x, y)
        """
        dx, dy = direction
        # Fixed: Use += instead of =+
        # Fixed: Correct order - _position[0] is x, _position[1] is y
        new_x = self._position[0] + dx
        new_y = self._position[1] + dy
        return (new_x, new_y)
    
    def draw(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:
        """Draw player on surface.
        
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
        
        # Draw player as a circle with border
        center = (pixel_x + TILE_SIZE // 2, pixel_y + TILE_SIZE // 2)
        radius = TILE_SIZE // 3
        
        # Shadow
        pygame.draw.circle(surface, Color.BLACK, 
                          (center[0] + 2, center[1] + 2), radius)
        # Main body
        pygame.draw.circle(surface, Color.PLAYER, center, radius)
        # # Highlight
        # pygame.draw.circle(surface, Color.WHITE, 
        #                   (center[0] - 3, center[1] - 3), radius // 3)
        # Border
        pygame.draw.circle(surface, Color.PLAYER_DARK, center, radius, 2)