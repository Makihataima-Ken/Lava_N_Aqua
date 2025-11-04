"""water entity."""

from typing import List, Tuple, Set
import pygame

from ..graphics.grid import Grid
from ..core.constants import Color, TILE_SIZE


class Water:
    """Water entity that flows and spreads."""
    
    def __init__(self, positions: List[Tuple[int, int]]) -> None:
        """Create a Water entity.
        
        Args:
            positions: List of starting positions as (x, y) tuples
        """
        self._positions: Set[Tuple[int, int]] = set(positions)
    
    def get_positions(self) -> Set[Tuple[int, int]]:
        """Get all Water positions.
        
        Returns:
            Set of positions as (x, y) tuples
        """
        return self._positions.copy()
    
    def set_positions(self, positions: Set[Tuple[int, int]]) -> None:
        """Set Water positions.
        
        Args:
            positions: Set of positions as (x, y) tuples
        """
        self._positions = set(positions)
    
    def add_position(self, position: Tuple[int, int]) -> None:
        """Add a single Water position.
        
        Args:
            position: Position as (x, y) tuple
        """
        self._positions.add(position)
        
    def remove_at(self, pos: Tuple[int, int]) -> None:
        """Remove Water from a specific position."""
        if pos in self._positions:
            self._positions.remove(pos)

    
    def is_at(self, position: Tuple[int, int]) -> bool:
        """Check if Water is at given position.
        
        Args:
            position: Position to check as (x, y) tuple
            
        Returns:
            True if Water is at position
        """
        return position in self._positions
    
    def update(self, grid: Grid,box_positions: List[Tuple[int, int]]=None) -> None:
        """Update Water flow - spread to adjacent tiles.
        
        Water spreads to adjacent empty floor tiles in all 4 directions.
        
        Args:
            grid: The main Grid object, used to check for walkable tiles.
        """
        # Start with current positions
        new_positions = set(self._positions)
        
        # Get grid dimensions once
        grid_width = grid.get_width()
        grid_height = grid.get_height()
        
        # Check all *current* Water positions
        # Note: We iterate over self._positions, but only add to new_positions.
        # This correctly simulates the Water spreading from its current locations.
        for x, y in self._positions:
            # Try spreading in all 4 directions
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                
                # --- This is the new, optimized logic ---
                
                # 1. Check if new position is within bounds
                if 0 <= nx < grid_width and 0 <= ny < grid_height:
                    
                    # 2. Check if the tile is walkable (i.e., not a wall)
                    # We use the grid's own method, which is much cleaner.
                    if grid.is_flowable(nx, ny) and (box_positions is None or (nx, ny) not in box_positions):
                        new_positions.add((nx, ny))
        
        # Update positions
        self._positions = new_positions
    
    def reset(self, positions: List[Tuple[int, int]]) -> None:
        """Reset Water to initial positions.
        
        Args:
            positions: List of starting positions as (x, y) tuples
        """
        self._positions = set(positions)
    
    def clear(self) -> None:
        """Remove all Water from the level."""
        self._positions.clear()
    
    def count(self) -> int:
        """Get number of Water tiles.
        
        Returns:
            Number of tiles with Water
        """
        return len(self._positions)
    
    def draw(self, surface: pygame.Surface, offset_x: int, offset_y: int, 
             animation_time: float = 0.0) -> None:
        """Draw Water on surface with animation.
        
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
            
            # Animate Water color (pulsing effect)
            base_color = Color.WATER
            dark_color = Color.WATER_DARK
            
            r = int(dark_color[0] + (base_color[0] - dark_color[0]) * wave)
            g = int(dark_color[1] + (base_color[1] - dark_color[1]) * wave)
            b = int(dark_color[2] + (base_color[2] - dark_color[2]) * wave)
            
            # Draw Water tile
            pygame.draw.rect(surface, (r, g, b), rect)
            
            # Draw border
            pygame.draw.rect(surface, Color.WATER_DARK, rect, 2)