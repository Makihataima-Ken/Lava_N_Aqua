"""Temporary wall entity """

import pygame
import math
from typing import Tuple
from ..core.constants import TILE_SIZE, Color


class TemporaryWall:
    """Wall that disappears after a certain number of moves."""
    
    def __init__(self, position: Tuple[int, int], duration: int):
        """Initialize temporary wall.
        
        Args:
            position: Position as (x, y)
            duration: Number of moves until wall disappears
        """
        self._position = position
        self._initial_duration = duration
        self._remaining_duration = duration
        self._expired = False
    
    def get_position(self) -> Tuple[int, int]:
        """Get wall position.
        
        Returns:
            Position as (x, y)
        """
        return self._position
    
    def get_remaining_duration(self) -> int:
        """Get remaining duration.
        
        Returns:
            Moves remaining until expiration
        """
        return self._remaining_duration
    
    def set_remaining_duration(self, duration: int) -> None:
        """Set remaining duration.
        
        Args:
            duration: New remaining duration
        """
        self._remaining_duration = duration
        if self._remaining_duration <= 0:
            self._expired = True
        elif self._expired:
            print("Reviving temporary wall")
            self._expired = False
            
    
    def is_expired(self) -> bool:
        """Check if wall has expired.
        
        Returns:
            True if wall should be removed
        """
        return self._expired
    
    def is_blocking(self) -> bool:
        """Check if wall is still blocking.
        
        Returns:
            True if wall blocks movement
        """
        return not self._expired
    
    def update(self) -> None:
        """Decrease duration by one move."""
        if self._remaining_duration > 0:
            self._remaining_duration -= 1
            
        if self._remaining_duration <= 0:
            self._expired = True
    
    def draw(self, surface: pygame.Surface, offset_x: int = 0,
             offset_y: int = 0, animation_time: float = 0.0) -> None:
        """Draw temporary wall with duration indicator.
        
        Args:
            surface: Pygame surface
            offset_x: X offset
            offset_y: Y offset
            animation_time: Animation time
        """
        if self._expired:
            return
        
        x, y = self._position
        screen_x = x * TILE_SIZE + offset_x
        screen_y = y * TILE_SIZE + offset_y
        
        wall_color = Color.Temp_WALL
        
        # Create surface with alpha
        temp_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        
        pygame.draw.rect(temp_surface, wall_color,
                         (0, 0, TILE_SIZE, TILE_SIZE))
        # Draw border
        pygame.draw.rect(temp_surface, Color.Temp_WALL_DARK,
                        (0, 0, TILE_SIZE, TILE_SIZE), 2)
        
        surface.blit(temp_surface, (screen_x, screen_y))
        
        # Draw duration number
        if self._remaining_duration > 0:
            font = pygame.font.Font(None, 20)
            text = font.render(str(self._remaining_duration), True, Color.WHITE)
            text_rect = text.get_rect(
                center=(screen_x + TILE_SIZE // 2, screen_y + TILE_SIZE // 2)
            )
            surface.blit(text, text_rect)