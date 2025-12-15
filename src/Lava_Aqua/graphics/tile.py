"""Tile entity and tile rendering."""

from typing import Tuple
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
        return self._tile_type in [TileType.EMPTY, TileType.EXIT, TileType.Dark_Wall]
    
    def is_flowable(self) -> bool:
        """Check if tile can be flowed into by lava/aqua."""
        return self._is_flowable()
    
    def _is_flowable(self) -> bool:
        """Determine if current tile type is walkable."""
        return self._tile_type in [TileType.EMPTY, TileType.Semi_Wall]
    
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
        elif self._tile_type == TileType.Semi_Wall:
            self._draw_semi_wall(surface, rect)
        elif self._tile_type == TileType.Dark_Wall:
            self._draw_dark_wall(surface, rect)
        else:  # EMPTY
            self._draw_empty(surface, rect)
    
    def _draw_empty(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw empty tile."""
        pygame.draw.rect(surface, Color.EMPTY, rect)
        pygame.draw.rect(surface, Color.EMPTY_DARK, rect, 1)
    
    def _draw_wall(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw wall tile with 3D effect."""
        # Main wall
        pygame.draw.rect(surface, Color.WALL, rect)
        # Border
        pygame.draw.rect(surface, Color.WALL_DARK, rect, 1)
        
    def _draw_semi_wall(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw semi-wall tile."""
        # Main semi-wall
        pygame.draw.rect(surface, Color.EMPTY, rect)
        # Border
        pygame.draw.rect(surface, Color.EMPTY_DARK, rect, 1)

        # --- Add small rects to corners ---

        # 1. Define the size and color of the corner rects
        corner_size = 14  # You can adjust this 4x4 pixel size
        corner_color = Color.WALL  # Match the border, or use Color.RED etc.

        # 2. Create a single rect to reuse for all corners
        corner_rect = pygame.Rect(0, 0, corner_size, corner_size)

        # 3. Move and draw the rect for each corner
        
        # Top-left
        corner_rect.topleft = rect.topleft
        pygame.draw.rect(surface, corner_color, corner_rect)

        # Top-right
        corner_rect.topright = rect.topright
        pygame.draw.rect(surface, corner_color, corner_rect)

        # Bottom-left
        corner_rect.bottomleft = rect.bottomleft
        pygame.draw.rect(surface, corner_color, corner_rect)

        # Bottom-right
        corner_rect.bottomright = rect.bottomright
        pygame.draw.rect(surface, corner_color, corner_rect)
    
    def _draw_dark_wall(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw dark-wall tile."""
        # Main dark-wall
        pygame.draw.rect(surface, Color.BLACK, rect)
        # Border
        pygame.draw.rect(surface, Color.WHITE, rect, 1)
    
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