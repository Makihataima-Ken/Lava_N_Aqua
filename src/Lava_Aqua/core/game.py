"""Main game logic and state management."""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from copy import deepcopy

from .level import LevelManager
from .constants import TileType, MAX_UNDO_HISTORY
from ..entities.player import Player
from ..entities.lava import Lava


@dataclass
class GameState:
    """Represents a snapshot of the game state."""
    grid: List[List[str]]
    player_pos: Tuple[int, int]
    moves: int
    lava_positions: List[Tuple[int, int]]


class GameLogic:
    """Core game logic."""
    
    def __init__(self) -> None:
        """Initialize game logic."""
        self.level_manager = LevelManager()
        self.player = Player((0, 0))
        self.lava = Lava([])
        self.grid: List[List[str]] = []
        self.exit_pos: Tuple[int, int] = (0, 0)
        self.moves = 0
        self.history: List[GameState] = []
        self.game_over = False
        self.level_complete = False
        
        self.load_current_level()
    
    def _extract_lava_from_grid(self, grid: List[List[str]]) -> List[Tuple[int, int]]:
        """Extract lava positions from grid and replace with empty tiles.
        
        Args:
            grid: Grid to extract from (modified in place)
            
        Returns:
            List of lava positions as (x, y) tuples
        """
        lava_positions = []
        
        for row_idx, row in enumerate(grid):
            for col_idx, tile in enumerate(row):
                if tile == 'L':
                    # Store as (x, y) which is (col, row)
                    lava_positions.append((col_idx, row_idx))
                    # Replace with empty tile
                    grid[row_idx][col_idx] = ' '
        
        return lava_positions
    
    def load_current_level(self) -> None:
        """Load the current level."""
        level_data = self.level_manager.get_current_level()
        
        self.grid = deepcopy(level_data.grid)
        
        # Extract lava positions from grid before setting up player
        lava_positions = self._extract_lava_from_grid(self.grid)
        
        # Convert from (row, col) to (x, y) for player
        row, col = level_data.player_start
        self.player.set_position((col, row))
        
        # Convert exit position from (row, col) to (x, y)
        exit_row, exit_col = level_data.exit_pos
        self.exit_pos = (exit_col, exit_row)
        
        # Initialize lava with extracted positions
        self.lava.reset(lava_positions)
        
        self.moves = 0
        self.history = []
        self.game_over = False
        self.level_complete = False
    
    def save_state(self) -> None:
        """Save current state for undo."""
        state = GameState(
            grid=deepcopy(self.grid),
            player_pos=self.player.get_position(),
            moves=self.moves,
            lava_positions=list(self.lava.get_positions())
        )
        self.history.append(state)
        
        # Limit history size
        if len(self.history) > MAX_UNDO_HISTORY:
            self.history.pop(0)
    
    def undo(self) -> bool:
        """Undo last move.
        
        Returns:
            True if undo was successful
        """
        if not self.history:
            return False
        
        state = self.history.pop()
        self.grid = state.grid
        self.player.set_position(state.player_pos)
        self.lava.set_positions(set(state.lava_positions))
        self.moves = state.moves
        self.game_over = False
        self.level_complete = False
        
        return True
    
    def reset_level(self) -> None:
        """Reset current level."""
        self.load_current_level()
    
    def can_move_to(self, pos: Tuple[int, int]) -> bool:
        """Check if position is walkable.
        
        Args:
            pos: Position to check as (x, y)
            
        Returns:
            True if position is walkable
        """
        x, y = pos
        height = len(self.grid)
        width = len(self.grid[0]) if height > 0 else 0
        
        # Out of bounds
        if y < 0 or y >= height or x < 0 or x >= width:
            return False
        
        tile = self.grid[y][x]
        
        # Can walk on empty spaces, water, and exit
        return tile in [TileType.EMPTY.value, TileType.WATER.value, TileType.EXIT.value]
    
    def move_player(self, direction: Tuple[int, int]) -> bool:
        """Attempt to move player.
        
        Args:
            direction: Direction tuple (dx, dy)
            
        Returns:
            True if move was successful
        """
        if self.game_over or self.level_complete:
            return False
        
        new_pos = self.player.move(direction)
        
        if self.can_move_to(new_pos):
            # Save state before move
            self.save_state()
            
            # Move player
            self.player.set_position(new_pos)
            self.moves += 1
            
            # Flow lava
            self.lava.update(self.grid)
            
            # Check game state
            self._check_game_state()
            
            return True
        
        return False
    
    def _check_game_state(self) -> None:
        """Check if game is over or level is complete."""
        player_pos = self.player.get_position()
        
        # Check if player reached exit
        if player_pos == self.exit_pos:
            self.level_complete = True
        
        # Check if player is on lava
        if self.lava.is_at(player_pos):
            self.game_over = True
    
    def next_level(self) -> bool:
        """Move to next level.
        
        Returns:
            True if moved to next level
        """
        if self.level_manager.next_level():
            self.load_current_level()
            return True
        return False
    
    def get_level_name(self) -> str:
        """Get current level name."""
        return self.level_manager.get_current_level().name
    
    def get_level_number(self) -> int:
        """Get current level number (1-indexed)."""
        return self.level_manager.current_level_index + 1
    
    def get_total_levels(self) -> int:
        """Get total number of levels."""
        return self.level_manager.get_level_count()
    
    def is_last_level(self) -> bool:
        """Check if on last level."""
        return self.level_manager.is_last_level()
    
    def get_grid_dimensions(self) -> Tuple[int, int]:
        """Get grid dimensions.
        
        Returns:
            (height, width)
        """
        height = len(self.grid)
        width = len(self.grid[0]) if height > 0 else 0
        return (height, width)