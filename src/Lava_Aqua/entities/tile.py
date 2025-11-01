"""Tile entity and tile rendering."""

from typing import Tuple, List, Optional
from enum import Enum
import pygame
import math

from ..core.constants import Color, TILE_SIZE


class TileType(Enum):
    """Enumeration of tile types."""
    EMPTY = ' '
    WALL = '#'
    EXIT = 'E'
    FLOOR = '.'
    WATER = 'W'


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
        elif self._tile_type == TileType.WATER:
            self._draw_water(surface, rect, animation_time)
        elif self._tile_type == TileType.FLOOR:
            self._draw_floor(surface, rect)
        else:  # EMPTY
            self._draw_empty(surface, rect)
    
    def _draw_empty(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw empty tile."""
        pygame.draw.rect(surface, (200, 200, 200), rect)
        pygame.draw.rect(surface, (150, 150, 150), rect, 1)
    
    def _draw_floor(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw floor tile."""
        pygame.draw.rect(surface, (180, 180, 180), rect)
        pygame.draw.rect(surface, (140, 140, 140), rect, 1)
    
    def _draw_wall(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw wall tile with 3D effect."""
        # Main wall
        pygame.draw.rect(surface, (100, 100, 100), rect)
        
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
        pygame.draw.rect(surface, (70, 70, 70), rect, 1)
    
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
    
    def _draw_water(self, surface: pygame.Surface, rect: pygame.Rect,
                    animation_time: float) -> None:
        """Draw water tile with ripple effect."""
        # Animate water ripples
        wave1 = math.sin(animation_time * 2) * 0.15 + 0.5
        wave2 = math.sin(animation_time * 2 + 1) * 0.15 + 0.5
        
        base_color = Color.WATER
        dark_color = Color.WATER_DARK
        
        r = int(dark_color[0] + (base_color[0] - dark_color[0]) * wave1)
        g = int(dark_color[1] + (base_color[1] - dark_color[1]) * wave1)
        b = int(dark_color[2] + (base_color[2] - dark_color[2]) * wave1)
        
        # Background
        pygame.draw.rect(surface, (r, g, b), rect)
        
        # Draw ripple
        center_x = rect.centerx
        center_y = rect.centery
        radius = int(TILE_SIZE // 4 * (1 + wave2 * 0.3))
        pygame.draw.circle(surface, (255, 255, 255), 
                          (center_x, center_y), radius, 1)
        
        # Border
        pygame.draw.rect(surface, Color.WATER_DARK, rect, 2)


class TileGrid:
    """Grid of tiles representing the game level."""
    
    def __init__(self, grid_data: List[List[str]]) -> None:
        """Create a tile grid from level data.
        
        Args:
            grid_data: 2D list of characters representing tiles
        """
        self._width: int = len(grid_data[0]) if grid_data else 0
        self._height: int = len(grid_data)
        self._tiles: List[List[Tile]] = []
        
        # Create tiles from grid data
        for y, row in enumerate(grid_data):
            tile_row = []
            for x, char in enumerate(row):
                # Convert character to TileType
                tile_type = self._char_to_tile_type(char)
                tile = Tile((x, y), tile_type)
                tile_row.append(tile)
            self._tiles.append(tile_row)
    
    def get_width(self) -> int:
        """Get grid width."""
        return self._width
    
    def get_height(self) -> int:
        """Get grid height."""
        return self._height
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tile at position or None if out of bounds
        """
        if 0 <= y < self._height and 0 <= x < self._width:
            return self._tiles[y][x]
        return None
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if position is walkable.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if position is walkable
        """
        tile = self.get_tile(x, y)
        return tile.is_walkable() if tile else False
    
    def get_tile_type(self, x: int, y: int) -> Optional[TileType]:
        """Get tile type at position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            TileType or None if out of bounds
        """
        tile = self.get_tile(x, y)
        return tile.get_type() if tile else None
    
    def set_tile_type(self, x: int, y: int, tile_type: TileType) -> bool:
        """Set tile type at position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            tile_type: New tile type
            
        Returns:
            True if successful
        """
        tile = self.get_tile(x, y)
        if tile:
            tile.set_type(tile_type)
            return True
        return False
    
    def draw(self, surface: pygame.Surface, offset_x: int = 0, 
             offset_y: int = 0, animation_time: float = 0.0) -> None:
        """Draw entire grid.
        
        Args:
            surface: Pygame surface to draw on
            offset_x: X offset for grid
            offset_y: Y offset for grid
            animation_time: Time for animation effects
        """
        for row in self._tiles:
            for tile in row:
                tile.draw(surface, offset_x, offset_y, animation_time)
    
    def _char_to_tile_type(self, char: str) -> TileType:
        """Convert character to TileType.
        
        Args:
            char: Character from level file
            
        Returns:
            Corresponding TileType
        """
        char_map = {
            ' ': TileType.EMPTY,
            '#': TileType.WALL,
            'E': TileType.EXIT,
            '.': TileType.FLOOR,
            'W': TileType.WATER,
        }
        return char_map.get(char, TileType.EMPTY)
    
    def find_tiles_of_type(self, tile_type: TileType) -> List[Tuple[int, int]]:
        """Find all positions with given tile type.
        
        Args:
            tile_type: Type to search for
            
        Returns:
            List of (x, y) positions
        """
        positions = []
        for y, row in enumerate(self._tiles):
            for x, tile in enumerate(row):
                if tile.get_type() == tile_type:
                    positions.append((x, y))
        return positions
    
    def get_all_tiles(self) -> List[List[Tile]]:
        """Get all tiles in the grid.
        
        Returns:
            2D list of tiles
        """
        return self._tiles
    
    def to_char_grid(self) -> List[List[str]]:
        """Convert tile grid back to character grid.
        
        Returns:
            2D list of characters
        """
        char_grid = []
        for row in self._tiles:
            char_row = [tile.get_type().value for tile in row]
            char_grid.append(char_row)
        return char_grid