from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from copy import deepcopy

from .level import LevelManager
from .constants import TileType, Direction
from ..entities.player import Player
from ..entities.lava import Lava
from ..entities.box import Box
from ..graphics.grid import Grid
from ..entities.aqua import Aqua
from ..entities.temporary_wall import TemporaryWall
from ..entities.exit_key import ExitKey

@dataclass
class GameState:
    player_pos: Tuple[int, int]
    box_positions: set[Tuple[int, int]]
    lava_positions: set[Tuple[int, int]]
    aqua_positions: set[Tuple[int, int]]
    collected_key_indices: set[int]
    temp_wall_data: set[Tuple[Tuple[int, int], int]]
    altered_tile_positions: set[Tuple[int,int]]
    moves: int


class GameLogic:
    
    def __init__(self) -> None:
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
        
        self.altered_tile_positions: list[Tuple[int,int]] = []
        
        self.load_current_level()    
    
    def load_current_level(self) -> None:
        level_data = self.level_manager.get_current_level()
        
        grid_data = deepcopy(level_data.grid)

        self.grid = Grid(grid_data)
        
        self.player.set_position(level_data.initial_pos)
        
        self.exit_pos = (level_data.exit_pos)
        
        self.exit_keys = [ExitKey(pos) for pos in level_data.exit_keys_poses]
        
        self.lava.reset(level_data.lava_poses)

        self.boxes = [Box(pos) for pos in level_data.box_poses]
        
        self.temp_walls = []

        for wall_data in level_data.temp_walls:
            pos = tuple(wall_data['position'])
            duration = wall_data['duration']
            self.temp_walls.append(TemporaryWall(pos, duration))
        
        self.aqua.reset(level_data.aqua_poses)
        
        self.moves = 0
        self.history = []
        self.game_over = False
        self.level_complete = False
    
    def save_state(self) -> None:
        state = GameState(
            player_pos=self.player.get_position(),
            lava_positions=set(self.lava.get_positions()),
            box_positions=[box.get_position() for box in self.boxes],
            aqua_positions = set(self.aqua.get_positions()),
            collected_key_indices = [i for i, key in enumerate(self.exit_keys) if key.is_collected()],
            temp_wall_data=[(wall.get_position(), wall.get_remaining_duration()) for wall in self.temp_walls],
            altered_tile_positions = self.altered_tile_positions.copy(),
            moves=self.moves
        )
        self.history.append(state)
    
    def undo(self) -> bool:
        if not self.history:
            return False
        
        state = self.history.pop()
        self.player.set_position(state.player_pos)
        self.lava.set_positions(set(state.lava_positions))
        self.aqua.set_positions(set(state.aqua_positions))
            
        for i, pos in enumerate(state.box_positions):
            self.boxes[i].set_position(pos)
            
        for pos, duration in state.temp_wall_data:
            wall = self._get_temp_wall_at(pos)
            if wall:
                wall.set_remaining_duration(duration)
                
        for i, key in enumerate(self.exit_keys):
            if i in state.collected_key_indices:
                key.collect()
            else:
                key.uncollect()
        
        current_altered_set = set(self.altered_tile_positions)
        saved_altered_set = set(state.altered_tile_positions)
        tiles_to_revert = current_altered_set - saved_altered_set

        if self.grid:
            for pos in tiles_to_revert:
                self.grid.set_tile_type(pos[0], pos[1], TileType.EMPTY)

        self.altered_tile_positions = state.altered_tile_positions
        
        self.moves = state.moves
        self.game_over = False
        self.level_complete = False
        
        return True
    
    def reset_level(self) -> None:
        self.load_current_level()
        
    def next_level(self) -> bool:
        if self.level_manager.next_level():
            self.load_current_level()
            return True
        return False
        
    def _get_active_temp_wall_at(self, pos: Tuple[int, int]) -> Optional[TemporaryWall]:
        for wall in self.temp_walls:
            if wall.get_position() == pos and wall.is_blocking():
                return wall
        return None
    
    def _get_temp_wall_at(self, pos: Tuple[int, int]) -> Optional[TemporaryWall]:
        for wall in self.temp_walls:
            if wall.get_position() == pos:
                return wall
        return None
    
    def movable(self, pos: Tuple[int, int]) -> bool:
        x, y = pos
        
        if not self.grid:
            return False
        
        if self._get_active_temp_wall_at(pos):
            return False

        # if self.lava.is_at(pos):
        #     return False
        
        return self.grid.is_walkable(x, y)
    
    def move_player(self, direction: Direction) -> bool:
        
        if self.game_over or self.level_complete:
            return False
        
        
        dx, dy = direction.value
        current_pos = self.player.get_position()
        new_pos = (current_pos[0] + dx, current_pos[1] + dy)
        
        if not self.movable(new_pos):
            return False

        box_to_push = self._get_box_at(new_pos)

        move_successful = False

        if box_to_push:
            move_successful = self._handle_box_push(box_to_push, new_pos, direction)
        else:
            move_successful = self._handle_empty_space_move(new_pos)

        if move_successful:
            self._update_game_state() 
            return True

        return False
        
    def _get_box_at(self, pos: Tuple[int, int]) -> Optional[Box]:
        """Find if a box is at a given (x, y) position."""
        for box in self.boxes:
            if box.get_position() == pos:
                return box
        return None
    
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
                
        self.aqua.update(
            self.grid, 
            [box.get_position() for box in self.boxes],
            [wall.get_position() for wall in self.temp_walls if wall.is_blocking()]
        )
        
        self._handle_lava_aqua_collisions()
        
        self.lava.update(
            self.grid, 
            [box.get_position() for box in self.boxes],
            [wall.get_position() for wall in self.temp_walls if wall.is_blocking()]
        )
        
        self._handle_lava_aqua_collisions()
        
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
                self.altered_tile_positions.append((x,y))

    
    def _check_game_state(self) -> None:
        player_pos = self.player.get_position()
        
        for key in self.exit_keys:
            if key.is_at(player_pos) and not key.is_collected():
                key.collect()
                
        all_keys_collected = True
        if self.exit_keys:
            all_keys_collected = all(key.is_collected() for key in self.exit_keys)

        if player_pos == self.exit_pos and all_keys_collected:
            self.level_complete = True
        
        if self.grid.get_tile_type(player_pos[0],player_pos[1]) == TileType.WALL:
            self.game_over = True
            
        if self.lava.is_at(player_pos):
            self.game_over = True
            
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
    
    def get_level_description(self) -> str:
        """Get current level description."""
        return f"Lava & Aqua - Level {self.get_level_number()}/{self.get_total_levels()}: {self.get_level_name()}"
    
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
    
    
    # Algorithms helper functions ----------------------------------------------

    def get_state(self) -> GameState:
        """Return a serializable snapshot of the current game state."""
        return GameState(
            player_pos=self.player.get_position(),
            box_positions=[box.get_position() for box in self.boxes],
            lava_positions=set(self.lava.get_positions()),
            aqua_positions=set(self.aqua.get_positions()),
            collected_key_indices=[
                i for i, key in enumerate(self.exit_keys) if key.is_collected()
            ],
            temp_wall_data=[
                (wall.get_position(), wall.get_remaining_duration()) for wall in self.temp_walls
            ],
            altered_tile_positions=self.altered_tile_positions.copy(),
            moves=self.moves,
        )

    def load_state(self, state: GameState) -> None:
        """Restore the game to a given snapshot (used for solver transitions)."""
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
        
        current_altered_set = set(self.altered_tile_positions)
        saved_altered_set = set(state.altered_tile_positions)
        tiles_to_revert = current_altered_set - saved_altered_set

        # 2. Revert those specific tiles back to EMPTY (assuming they were EMPTY before)
        if self.grid:
            for pos in tiles_to_revert:
                self.grid.set_tile_type(pos[0], pos[1], TileType.EMPTY)

        # 3. Restore the list of altered tiles to its previous state
        self.altered_tile_positions = state.altered_tile_positions
        
        self.moves = state.moves
        self.game_over = False
        self.level_complete = False
        self._check_game_state() 
    
    # excludes sure game overs    
    def algorithmic_movable(self,direction:Direction) -> bool:
        
        dx, dy = direction.value
        current_pos = self.player.get_position()
        new_pos = (current_pos[0] + dx, current_pos[1] + dy)
        neighbours_pos = [(new_pos[0]+ direction.value[0], new_pos[1] + direction.value[1]) for direction in Direction]
        print(neighbours_pos)
        for cell in neighbours_pos:
            if self.lava.is_at(cell):
                return False
            
        if self.movable(new_pos) and not self.lava.is_at(new_pos):   
            box_to_push = self._get_box_at(new_pos)
            if box_to_push:
                # Check if box can be pushed
                box_new_pos = (new_pos[0] + dx, new_pos[1] + dy)
                if self._can_push_box(box_new_pos):
                    return True
                else:
                    return False
            
            else: return True
                    
        return False
                
        
    # used in solver mode to make actions list
    def allowed_moves(self) -> List[Direction]:
        """Get list of valid move directions from current state."""
        valid_moves = []
        for direction in Direction:
            
            if self.algorithmic_movable(direction):                    
                valid_moves.append(direction)
                
        print(valid_moves)        
        return valid_moves

    def simulate_move(self, direction: Direction) -> Optional[GameState]:
        """
        Simulate moving the player WITHOUT deepcopy.
        
        Returns a new GameState if valid move, otherwise None.
        """
        # Save current state (lightweight)
        original_state = self.get_state()
        
        # Try the move (modifies self temporarily)
        moved = self.move_player(direction)
        
        if moved and not self.game_over:
            # Capture the resulting state
            result_state = self.get_state()
            
            # Restore original state
            self.load_state(original_state)
            
            return result_state
        else:
            # Move failed or game over - restore and return None
            self.load_state(original_state)
            return None
        
    def is_level_completed(self)->bool:
        return self.level_complete