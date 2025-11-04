from typing import Tuple, List, Optional
import pygame
from .tile import Tile
from ..core.constants import TileType

class Grid:
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