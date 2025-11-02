"""Level management and loading."""

import json
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

from .constants import TileType, LEVELS_FILE


@dataclass
class LevelData:
    """Level data structure."""
    name: str
    grid: List[List[str]]
    width: int
    height: int
    player_start: Tuple[int, int]
    exit_pos: Tuple[int, int]
    
    def __post_init__(self) -> None:
        """Validate level data after initialization."""
        if not self.grid:
            raise ValueError("Level grid cannot be empty")
        if not self.player_start:
            raise ValueError("Player start position not found")
        if not self.exit_pos:
            raise ValueError("Exit position not found")


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
    
    def _load_levels(self) -> None:
        """Load levels from JSON file."""
        try:
            with open(self.levels_file, 'r', encoding='utf-8') as f:
                self.levels = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise RuntimeError(f"Failed to load levels: {e}")
    
    def get_level_count(self) -> int:
        """Get total number of levels."""
        return len(self.levels)
    
    def load_level(self, level_index: int) -> LevelData:
        """Load a specific level by index.
        
        Args:
            level_index: Index of the level to load
            
        Returns:
            LevelData object
            
        Raises:
            IndexError: If level index is out of range
        """
        if level_index < 0 or level_index >= len(self.levels):
            raise IndexError(f"Level index {level_index} out of range")
        
        level = self.levels[level_index]
        grid = [list(row) for row in level['grid']]
        height = len(grid)
        width = len(grid[0]) if grid else 0
        
        # Find player and exit positions
        player_start: Optional[Tuple[int, int]] = None
        exit_pos: Optional[Tuple[int, int]] = None
        
        for y in range(height):
            for x in range(width):
                if grid[y][x] == TileType.PLAYER.value:
                    player_start = (y, x)
                    grid[y][x] = TileType.EMPTY.value
                elif grid[y][x] == TileType.EXIT.value:
                    exit_pos = (y, x)
        
        if player_start is None:
            raise ValueError(f"Level '{level['name']}' has no player start position")
        if exit_pos is None:
            raise ValueError(f"Level '{level['name']}' has no exit position")
        
        return LevelData(
            name=level['name'],
            grid=grid,
            width=width,
            height=height,
            player_start=player_start,
            exit_pos=exit_pos
        )
    
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