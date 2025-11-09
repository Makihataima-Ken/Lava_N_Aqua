"""Main game logic and state management."""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from copy import deepcopy

from .level import LevelManager
from .constants import TileType, MAX_UNDO_HISTORY, Direction
from ..entities.player import Player
from ..entities.lava import Lava
from ..entities.box import Box
from ..graphics.grid import Grid
from ..entities.aqua import Aqua
from ..entities.temporary_wall import TemporaryWall
from ..entities.exit_key import ExitKey

import pygame


@dataclass
class GameState:
    """Represents a snapshot of the game state."""
    player_pos: Tuple[int, int]
    box_positions: List[Tuple[int, int]]
    lava_positions: List[Tuple[int, int]]
    aqua_positions: List[Tuple[int, int]]
    collected_key_indices: List[int]
    temp_wall_data: List[Tuple[Tuple[int, int], int]]  # (position, remaining_duration)
    moves: int


class GameLogic:
    """Core game logic."""
    
    def __init__(self) -> None:
        """Initialize game logic."""
        self.level_manager = LevelManager()
        self.player = Player((0, 0))
        self.lava = Lava([])
        self.aqua = Aqua([]) # WIP
        self.boxes: List[Box] = [] # WIP
        self.grid: Optional[Grid] = None
        self.exit_pos: Tuple[int, int] = (0, 0)
        self.moves = 0
        self.history: List[GameState] = []
        self.game_over = False
        self.level_complete = False

        self.exit_keys: List[ExitKey] = []
        
        self.temp_walls: List[TemporaryWall] = []
        
        self.load_current_level()    
    
    def _get_box_at(self, pos: Tuple[int, int]) -> Optional[Box]:
        """Find if a box is at a given (x, y) position."""
        for box in self.boxes:
            if box.get_position() == pos:
                return box
        return None
    
    def load_current_level(self) -> None:
        """Load the current level."""
        level_data = self.level_manager.get_current_level()
        
        # Create a copy of the grid data
        grid_data = deepcopy(level_data.grid)
        
        # Create Grid object from processed grid data
        self.grid = Grid(grid_data)
        
        self.player.set_position(level_data.initial_pos)
        
        self.exit_pos = (level_data.exit_pos)
        
        self.exit_keys = [ExitKey(pos) for pos in level_data.exit_keys_poses]
        
        # Initialize lava with extracted positions
        self.lava.reset(level_data.lava_poses)
        
        # Initialize boxes
        self.boxes = [Box(pos) for pos in level_data.box_poses]
        
        self.temp_walls = []
        # if hasattr(level, 'temp_walls') and level.temp_walls:
        for wall_data in level_data.temp_walls:
            pos = tuple(wall_data['position'])  # [x, y] -> (x, y)
            duration = wall_data['duration']
            self.temp_walls.append(TemporaryWall(pos, duration))
        
        self.aqua.reset(level_data.aqua_poses)
        
        
        self.moves = 0
        self.history = []
        self.game_over = False
        self.level_complete = False
    
    def save_state(self) -> None:
        """Save current state for undo."""
        state = GameState(
            # grid_data=self.grid.to_char_grid(),
            player_pos=self.player.get_position(),
            lava_positions=list(self.lava.get_positions()),
            box_positions=[box.get_position() for box in self.boxes],
            aqua_positions = list(self.aqua.get_positions()),
            collected_key_indices = [i for i, key in enumerate(self.exit_keys) if key.is_collected()],
            temp_wall_data=[(wall.get_position(), wall.get_remaining_duration()) for wall in self.temp_walls],
            moves=self.moves
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
        self.player.set_position(state.player_pos)
        self.lava.set_positions(set(state.lava_positions))
        self.aqua.set_positions(set(state.aqua_positions))
            
        for i, pos in enumerate(state.box_positions):
            self.boxes[i].set_position(pos)
            
        # Restore temp walls
        for pos, duration in state.temp_wall_data:
            wall = self._get_temp_wall_at(pos)
            if wall:
                wall.set_remaining_duration(duration)
                
        for i, key in enumerate(self.exit_keys):
            if i in state.collected_key_indices:
                key.collect()
            else:
                key.uncollect()
        
        self.moves = state.moves
        self.game_over = False
        self.level_complete = False
        
        return True
    
    def reset_level(self) -> None:
        """Reset current level."""
        self.load_current_level()
        
    def _get_active_temp_wall_at(self, pos: Tuple[int, int]) -> Optional[TemporaryWall]:
        """Get active temporary wall at position."""
        for wall in self.temp_walls:
            if wall.get_position() == pos and wall.is_blocking():
                return wall
        return None
    
    def _get_temp_wall_at(self, pos: Tuple[int, int]) -> Optional[TemporaryWall]:
        """Get active temporary wall at position."""
        for wall in self.temp_walls:
            if wall.get_position() == pos:
                return wall
        return None
    
    def can_move_to(self, pos: Tuple[int, int]) -> bool:
        """Check if position is walkable.
        
        Args:
            pos: Position to check as (x, y)
            
        Returns:
            True if position is walkable
        """
        x, y = pos
        
        # Check if position is within bounds using Grid
        if not self.grid:
            return False
        
        # Out of bounds check
        if y < 0 or y >= self.grid.get_height() or x < 0 or x >= self.grid.get_width():
            return False
        
        if self._get_active_temp_wall_at(pos):
            return False
    
        # Use Grid's walkability check
        return self.grid.is_walkable(x, y)
    
    def move_player(self, direction: Direction) -> bool:
        """Attempt to move player and push boxes."""
        
        if self.game_over or self.level_complete:
            return False
        
        # 1. Determine new positions
        dx, dy = direction.value
        current_pos = self.player.get_position()
        new_pos = (current_pos[0] + dx, current_pos[1] + dy)
        # 2. Check if move is valid
        if not self.can_move_to(new_pos):
            return False  # Can't move into a wall

        # Check for a box at the new position
        box_to_push = self._get_box_at(new_pos)

        # 3. Handle the two valid move types  
        move_successful = False

        if box_to_push:
            move_successful = self._handle_box_push(box_to_push, new_pos, direction)
        else:
            move_successful = self._handle_empty_space_move(new_pos)

        # 4. Update game state if any move happened
        if move_successful:
            self._update_game_state() 
            # return True
        
        return False # Move was blocked
    
    def _handle_box_push(self, box_to_push, box_pos: Tuple[int, int], direction: Direction) -> bool:
        """Handle pushing a box. Returns True if successful."""
        # Calculate where the box would move
        dx, dy = direction.value
        box_new_pos = (box_pos[0] + dx, box_pos[1] + dy)
        
        # Check if the box can be pushed
        if not self._can_push_box(box_new_pos):
            return False
        
        # Execute the push
        self._execute_box_push(box_to_push, box_pos, box_new_pos)
        return True
    
    def _can_push_box(self, box_new_pos: Tuple[int, int]) -> bool:
        # Check for another box
        if self._get_box_at(box_new_pos) is not None:
            return False
        
        # Check for wall
        if not self.grid.is_walkable(box_new_pos[0], box_new_pos[1]):
            return False
        
        # Check for active temporary wall (NEW)
        if self._get_active_temp_wall_at(box_new_pos):
            return False
        
        return True

    def _execute_box_push(self, box_to_push, player_new_pos: Tuple[int, int], box_new_pos: Tuple[int, int]):
        """Execute the box push and player movement."""
        self.save_state()  # Save state before moving
        
        # Move the box
        box_to_push.set_position(box_new_pos)
        
        # Handle box landing on lava
        if self.lava.is_at(box_new_pos):
            self.lava.remove_at(box_new_pos)
        
        # Handle box landing on aqua
        if self.aqua.is_at(box_new_pos):
            self.aqua.remove_at(box_new_pos)
        
        # Move the player
        self.player.set_position(player_new_pos)
        self.moves += 1

    def _handle_empty_space_move(self, new_pos: Tuple[int, int]) -> bool:
        """Handle moving into empty space. Returns True if successful."""
        self.save_state()  # Save state before moving
        self.player.set_position(new_pos)
        self.moves += 1
        return True

    def _update_game_state(self) -> None:
        """Update game state after a move."""
                
        # Update lava (with temp wall blocking)
        self.lava.update(
            self.grid, 
            [box.get_position() for box in self.boxes],
            [wall.get_position() for wall in self.temp_walls if wall.is_blocking()]
        )
        
        # Update aqua (with temp wall blocking)
        self.aqua.update(
            self.grid, 
            [box.get_position() for box in self.boxes],
            [wall.get_position() for wall in self.temp_walls if wall.is_blocking()]
        )
        self._handle_lava_aqua_collisions()
        
        # Update temporary walls (decrease duration)
        for wall in self.temp_walls:
            wall.update()
            
        self._check_game_state()
    
    def _handle_lava_aqua_collisions(self) -> None:
        """Turn tiles where lava and aqua collide into walls."""
        lava_positions = set(self.lava.get_positions())
        aqua_positions = set(self.aqua.get_positions())
        collisions = lava_positions & aqua_positions  # intersection

        for (x, y) in collisions:
            # 1. Remove lava and aqua
            self.lava.remove_at((x, y))
            self.aqua.remove_at((x, y))

            # 2. Turn this tile into a wall in the grid
            if self.grid:
                self.grid.set_tile_type(x, y, TileType.WALL)

    
    def _check_game_state(self) -> None:
        """Check if game is over or level is complete."""
        player_pos = self.player.get_position()
        
        # Check for key collection
        for key in self.exit_keys:
            # If player is at key position AND it's not already collected
            if key.is_at(player_pos) and not key.is_collected():
                key.collect()
                
        # Check if all keys are collected
        all_keys_collected = True
        if self.exit_keys: # Only check if the list isn't empty
            all_keys_collected = all(key.is_collected() for key in self.exit_keys)

        # Check if player reached exit
        if player_pos == self.exit_pos and all_keys_collected:
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
    
    
    
    
    # Helper methods
    
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
        if not self.grid:
            return (0, 0)
        return (self.grid.get_height(), self.grid.get_width())
    
    def get_grid(self) -> Optional[Grid]:
        """Get the Grid object for rendering.
        
        Returns:
            Grid object or None
        """
        return self.grid
    
    def draw(self, surface: pygame.Surface, offset_x: int = 0, 
             offset_y: int = 0, animation_time: float = 0.0) -> None:
        """Draw the entire game state.
        Args:
            surface: Pygame surface to draw on
            offset_x: X offset for grid
            offset_y: Y offset for grid
            animation_time: Time for animations
        """
        if not self.grid:
            print("Error: No grid available")
            return 'quit'
        
        # Draw tiles first (background)
        self.grid.draw(surface, offset_x, offset_y, animation_time)
        
        # Draw lava on top of tiles
        self.lava.draw(surface, offset_x, offset_y, animation_time)
        
        # Draw Aqua on top of tiles
        self.aqua.draw(surface, offset_x, offset_y, animation_time)
        
        # 3. Draw boxes on top of lava
        for box in self.boxes:
            box.draw(surface, offset_x, offset_y)
        
        for wall in self.temp_walls:
            wall.draw(surface, offset_x, offset_y, animation_time)    
            
        # --- NEW ---
        # 4. Draw Exit Keys
        for key in self.exit_keys:
            key.draw(surface, offset_x, offset_y, animation_time)
        # ---
            
        # Draw player on top
        self.player.draw(surface, offset_x, offset_y)