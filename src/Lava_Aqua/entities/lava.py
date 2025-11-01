"""Lava entity."""

from typing import List, Tuple, Set
import pygame

from ..core.constants import Color, TILE_SIZE


class Lava:
    """Lava entity that flows and spreads."""
    
    def __init__(self, positions: List[Tuple[int, int]]) -> None:
        """Create a lava entity.
        
        Args:
            positions: List of starting positions as (x, y) tuples
        """
        self._positions: Set[Tuple[int, int]] = set(positions)
    
    def get_positions(self) -> Set[Tuple[int, int]]:
        """Get all lava positions.
        
        Returns:
            Set of positions as (x, y) tuples
        """
        return self._positions.copy()
    
    def set_positions(self, positions: Set[Tuple[int, int]]) -> None:
        """Set lava positions.
        
        Args:
            positions: Set of positions as (x, y) tuples
        """
        self._positions = set(positions)
    
    def add_position(self, position: Tuple[int, int]) -> None:
        """Add a single lava position.
        
        Args:
            position: Position as (x, y) tuple
        """
        self._positions.add(position)
    
    def is_at(self, position: Tuple[int, int]) -> bool:
        """Check if lava is at given position.
        
        Args:
            position: Position to check as (x, y) tuple
            
        Returns:
            True if lava is at position
        """
        return position in self._positions
    
    def update(self, grid: List[List[str]]) -> None:
        """Update lava flow - spread to adjacent tiles.
        
        Lava spreads to adjacent empty floor tiles in all 4 directions.
        
        Args:
            grid: 2D grid of the level
        """
        # Start with current positions
        new_positions = set(self._positions)
        
        # Check all current lava positions
        for x, y in self._positions:
            # Try spreading in all 4 directions
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                
                # Check if new position is within bounds
                if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
                    # Check if tile is empty (can flow into it)
                    if grid[ny][nx] in (' ', '.'):
                        new_positions.add((nx, ny))
        
        # Update positions
        self._positions = new_positions
    
    def reset(self, positions: List[Tuple[int, int]]) -> None:
        """Reset lava to initial positions.
        
        Args:
            positions: List of starting positions as (x, y) tuples
        """
        self._positions = set(positions)
    
    def clear(self) -> None:
        """Remove all lava from the level."""
        self._positions.clear()
    
    def count(self) -> int:
        """Get number of lava tiles.
        
        Returns:
            Number of tiles with lava
        """
        return len(self._positions)
    
    def draw(self, surface: pygame.Surface, offset_x: int, offset_y: int, 
             animation_time: float = 0.0) -> None:
        """Draw lava on surface with animation.
        
        Args:
            surface: Pygame surface to draw on
            offset_x: X offset for grid
            offset_y: Y offset for grid
            animation_time: Time for animation effects (optional)
        """
        import math
        
        # Calculate animation wave for pulsing effect
        wave = abs(math.sin(animation_time * 2)) * 0.3 + 0.7
        
        for x, y in self._positions:
            # Calculate pixel position
            pixel_x = offset_x + x * TILE_SIZE
            pixel_y = offset_y + y * TILE_SIZE
            
            rect = pygame.Rect(pixel_x, pixel_y, TILE_SIZE, TILE_SIZE)
            
            # Animate lava color (pulsing effect)
            base_color = Color.LAVA
            dark_color = Color.LAVA_DARK
            
            r = int(dark_color[0] + (base_color[0] - dark_color[0]) * wave)
            g = int(dark_color[1] + (base_color[1] - dark_color[1]) * wave)
            b = int(dark_color[2] + (base_color[2] - dark_color[2]) * wave)
            
            # Draw lava tile
            pygame.draw.rect(surface, (r, g, b), rect)
            
            # Draw border
            pygame.draw.rect(surface, Color.LAVA_DARK, rect, 2)