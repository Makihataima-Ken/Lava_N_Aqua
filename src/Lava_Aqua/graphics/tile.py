"""Tile entity and tile rendering."""

from typing import Tuple, List, Optional
import pygame
import math

from ..core.constants import Color, TILE_SIZE, TileType

class Tile:
    """Individual tile entity."""
    
    def __init__(self, position: Tuple[int, int], tile_type: TileType) -> None:
        """Create a tile entity.
        
        Args:
            position: Position as (x, y) tuple
            tile_type: Type of tile
        """
        self._position: Tuple[int, int] = position
        self._tile_type: TileType = tile_type
        self._walkable: bool = self._is_walkable()
    
    def get_position(self) -> Tuple[int, int]:
        """Get tile position.
        
        Returns:
            Position as (x, y) tuple
        """
        return self._position
    
    def get_type(self) -> TileType:
        """Get tile type.
        
        Returns:
            TileType enum value
        """
        return self._tile_type
    
    def set_type(self, tile_type: TileType) -> None:
        """Set tile type.
        
        Args:
            tile_type: New tile type
        """
        self._tile_type = tile_type
        self._walkable = self._is_walkable()
    
    def is_walkable(self) -> bool:
        """Check if tile is walkable.
        
        Returns:
            True if entities can walk on this tile
        """
        return self._walkable
    
    def _is_walkable(self) -> bool:
        """Determine if current tile type is walkable."""
        return self._tile_type in [TileType.EMPTY, TileType.FLOOR, 
                                    TileType.EXIT, TileType.WATER]
    
    def is_flowable(self) -> bool:
        """Check if tile can be flowed into by lava/water."""
        return self._is_flowable()
    
    def _is_flowable(self) -> bool:
        """Determine if current tile type is walkable."""
        return self._tile_type in [TileType.EMPTY, TileType.FLOOR]
    
    def draw(self, surface: pygame.Surface, offset_x: int, offset_y: int,
             animation_time: float = 0.0) -> None:
        """Draw tile on surface.
        
        Args:
            surface: Pygame surface to draw on
            offset_x: X offset for grid
            offset_y: Y offset for grid
            animation_time: Time for animation effects
        """
        x, y = self._position
        pixel_x = offset_x + x * TILE_SIZE
        pixel_y = offset_y + y * TILE_SIZE
        rect = pygame.Rect(pixel_x, pixel_y, TILE_SIZE, TILE_SIZE)
        
        if self._tile_type == TileType.WALL:
            self._draw_wall(surface, rect)
        elif self._tile_type == TileType.EXIT:
            self._draw_exit(surface, rect, animation_time)
        elif self._tile_type == TileType.FLOOR:
            self._draw_floor(surface, rect)
        else:  # EMPTY
            self._draw_empty(surface, rect)
    
    def _draw_empty(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw empty tile."""
        pygame.draw.rect(surface, Color.EMPTY, rect)
        pygame.draw.rect(surface, (150, 150, 150), rect, 1)
    
    def _draw_floor(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw floor tile."""
        pygame.draw.rect(surface, (180, 180, 180), rect)
        pygame.draw.rect(surface, (140, 140, 140), rect, 1)
    
    def _draw_wall(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw wall tile with 3D effect."""
        # Main wall
        pygame.draw.rect(surface, Color.WALL, rect)
        
        # Highlight (top-left)
        pygame.draw.line(surface, (150, 150, 150), 
                        rect.topleft, rect.topright, 2)
        pygame.draw.line(surface, (150, 150, 150), 
                        rect.topleft, rect.bottomleft, 2)
        
        # Shadow (bottom-right)
        pygame.draw.line(surface, (50, 50, 50), 
                        rect.bottomleft, rect.bottomright, 2)
        pygame.draw.line(surface, (50, 50, 50), 
                        rect.topright, rect.bottomright, 2)
        
        # Border
        pygame.draw.rect(surface, Color.WALL_DARK, rect, 1)
    
    def _draw_exit(self, surface: pygame.Surface, rect: pygame.Rect,
                   animation_time: float) -> None:
        """Draw exit tile with glowing effect."""
        # Animate glow
        glow = abs(math.sin(animation_time * 2)) * 0.3 + 0.7
        
        base_color = Color.EXIT
        r = int(base_color[0] * glow)
        g = int(base_color[1] * glow)
        b = int(base_color[2] * glow)
        
        # Background
        pygame.draw.rect(surface, (r, g, b), rect)
        
        # Border
        pygame.draw.rect(surface, Color.EXIT_DARK, rect, 2)