"""Level management and loading."""

import json
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

from .constants import TileType, LEVELS_FILE


@dataclass
class LevelData:
    """Level data structure."""
    
    # static data
    name: str
    grid: List[List[str]]
    width: int
    height: int
    exit_pos: Tuple[int, int]
    
    # initial dynamic data
    initial_pos: Tuple[int, int]
    lava_poses: List[Tuple[int, int]]
    box_poses: List[Tuple[int, int]] 
    aqua_poses: List[Tuple[int, int]]
    
    exit_keys_poses: List[Tuple[int, int]]  
    temp_walls: Optional[List[Dict[str, Any]]] = None 
    
    def __str__(self) -> str:
        return f"LevelData(name={self.name}, size=({self.width}x{self.height}), initial_pos={self.initial_pos}, exit_pos={self.exit_pos})"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LevelData':
        """
        Factory method to parse a raw dictionary (from JSON)
        into a validated LevelData object.
        """
        name = data.get('name', 'Unnamed Level')
        grid = [list(row) for row in data.get('grid', [])]
        
        if not grid:
            raise ValueError(f"Level '{name}' grid cannot be empty")
            
        height = len(grid)
        width = len(grid[0])
        
        initial_pos, exit_pos = None, None
        lava_poses, box_poses, aqua_poses, exit_keys_poses = [], [], [], []
        
        for y in range(height):
            # Ensure grid is not ragged
            if len(grid[y]) != width:
                raise ValueError(f"Level '{name}' has inconsistent row width")
            for x in range(width):
                tile = grid[y][x]
                if tile == TileType.PLAYER.value:
                    if initial_pos:
                        raise ValueError(f"Level '{name}' has multiple start positions")
                    initial_pos = (x,y)
                    grid[y][x] = TileType.EMPTY.value
                    
                elif tile == TileType.EXIT.value:
                    if exit_pos:
                         raise ValueError(f"Level '{name}' has multiple exits")
                    exit_pos = (x,y)
                elif tile == TileType.LAVA.value:
                    lava_poses.append((x,y))
                    grid[y][x] = TileType.EMPTY.value
                elif tile == TileType.BOX.value:
                    box_poses.append((x,y))
                    grid[y][x] = TileType.EMPTY.value
                elif tile == TileType.AQUA.value:
                    aqua_poses.append((x,y))
                    grid[y][x] = TileType.EMPTY.value
                elif tile == TileType.Key.value:
                    exit_keys_poses.append((x,y))
                elif tile == TileType.Temp_Wall.value:
                    # Temporary walls handled elsewhere
                    grid[y][x] = TileType.EMPTY.value 

        if initial_pos is None:
            raise ValueError(f"Level '{name}' has no player start position")
        if exit_pos is None:
            raise ValueError(f"Level '{name}' has no exit position")
        
        temp_walls = data.get("temp_walls", [])
        
        return cls(
            name=name,
            grid=grid,
            width=width,
            height=height,
            initial_pos=initial_pos,
            exit_pos=exit_pos,
            lava_poses = lava_poses,
            box_poses = box_poses,
            aqua_poses = aqua_poses,
            exit_keys_poses = exit_keys_poses,
            temp_walls=temp_walls
        )


class LevelManager:
    """Manages game levels."""
    
    def __init__(self, levels_file: Path = LEVELS_FILE) -> None:
        """Initialize level manager.
        
        Args:
            levels_file: Path to levels JSON file
        """
        self.levels_file = levels_file
        self.levels: List[Dict[str, Any]] = []
        self.current_level_index = 0
        self._ensure_levels_file()
        self._load_levels()
    
    def _ensure_levels_file(self) -> None:
        """Ensure levels file and directory exist."""
        self.levels_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.levels_file.exists():
            self._create_default_levels()
            
    def _create_default_levels(self) -> None:
        """Creates a placeholder default level file."""
        default_level_data = [
            {
                "name": "Lava Flow",
                "grid": [
                    "###################",
                    "###################",
                    "###################",
                    "#            ######",
                    "#P               E#",
                    "#            ######",
                    "#            #    #",
                    "##           #  L #",
                    "###L         #    #",
                    "###################"
                ]
            },
        ]
        try:
            with open(self.levels_file, 'w', encoding='utf-8') as f:
                json.dump(default_level_data, f, indent=2)
        except IOError as e:
            raise RuntimeError(f"Failed to create default levels file: {e}")
    
    def _load_levels(self) -> None:
        """Load levels from JSON and parse them into LevelData objects."""
        try:
            with open(self.levels_file, 'r', encoding='utf-8') as f:
                raw_levels = json.load(f)
                if not isinstance(raw_levels, list):
                    raise ValueError("Levels file root must be a list")
            
            # Parse all levels at once
            self.levels = [LevelData.from_dict(lvl) for lvl in raw_levels]
            
            if not self.levels:
                raise ValueError("No levels found in levels file.")
                
        except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
            raise RuntimeError(f"Failed to load and parse levels: {e}")
    
    def get_level_count(self) -> int:
        """Get total number of levels."""
        return len(self.levels)
    
    def load_level(self, level_index: int) -> LevelData:
        """
        Load a specific level by index.
        This is now a fast lookup.
        """
        # More concise index check
        if level_index not in range(len(self.levels)):
            raise IndexError(f"Level index {level_index} out of range")
        
        # Just return the already-parsed object
        return self.levels[level_index]
    
    def get_current_level(self) -> LevelData:
        """Get current level data."""
        return self.load_level(self.current_level_index)
    
    def next_level(self) -> bool:
        """Move to next level.
        
        Returns:
            True if moved to next level, False if at last level
        """
        if self.current_level_index < len(self.levels) - 1:
            self.current_level_index += 1
            return True
        return False
    
    def previous_level(self) -> bool:
        """Move to previous level.
        
        Returns:
            True if moved to previous level, False if at first level
        """
        if self.current_level_index > 0:
            self.current_level_index -= 1
            return True
        return False
    
    def reset_progress(self) -> None:
        """Reset to first level."""
        self.current_level_index = 0
    
    def is_last_level(self) -> bool:
        """Check if current level is the last level."""
        return self.current_level_index == len(self.levels) - 1