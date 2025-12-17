from enum import Enum
from pathlib import Path

# Grid tile size
TILE_SIZE = 40

# Colors (RGB)
class Color:
    """Color constants."""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)
    
    BLUE = (50, 150, 255)
    RED = (220, 50, 50)
    
    # Tile colors
    LAVA = (255, 69, 0)
    LAVA_DARK = (200, 40, 0)
    
    AQUA = (30, 144, 255)
    AQUA_DARK = (0, 100, 200)
    
    PLAYER = (255, 255, 0)
    PLAYER_DARK = (200, 200, 0)
    
    EXIT = (128, 0, 128)
    EXIT_DARK = (80, 0, 80)
    
    WALL = (169, 169, 169)
    WALL_DARK = (105, 105, 105)
    
    EMPTY = (40, 40, 40)
    EMPTY_DARK = (20, 20, 20)
    
    BOX = (160, 82, 45)
    BOX_DARK = (110, 52, 25)
    
    Temp_WALL = (50, 205, 50)
    Temp_WALL_DARK = (34, 139, 34)

# Tile types
class TileType(Enum):
    """Tile type enumeration."""
    EMPTY = " "
    WALL = "#"
    LAVA = "L"
    AQUA = "W"
    PLAYER = "P"
    EXIT = "E"
    BOX = "B"
    Key = "K"
    Temp_Wall = "T"
    Semi_Wall = "S"
    Dark_Wall = "D"

# File paths
BASE_DIR = Path(__file__).parent.parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LEVELS_DIR = ASSETS_DIR / "levels"
SOLUTIONS_DIR = ASSETS_DIR / "solutions"
TRAINED_MODELS_DIR = ASSETS_DIR /"trained models"
LEVELS_FILE = LEVELS_DIR / "levels.json"
# LEVELS_FILE = LEVELS_DIR / "assignment.json"
# LEVELS_FILE = LEVELS_DIR / "temp_wall_test.json"
# LEVELS_FILE = LEVELS_DIR / "test.json"
# LEVELS_FILE = LEVELS_DIR / "walls_test.json"

# Game settings
MAX_UNDO_HISTORY = 50
MOVE_ANIMATION_DURATION = 0.15  # seconds

class GameResult(Enum):
    """Possible outcomes of a level."""
    WIN = 'win'
    RESTART = 'restart'
    QUIT = 'quit'
    CONTINUE = 'continue'
    LOSS = 'loss'
    
class Direction(Enum):
    """Movement directions."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    
class Action(Enum):
    """Player actions."""
    RESET = 'reset'
    UNDO = 'undo'
    QUIT = 'quit'
    
    
CONTROLLER_OPTIONS = [
    "Player",
    "BFS",
    "DFS",
    "UCS",
    "Dijkstra",
    "A*",
    "Hill Climbing"
    # "Q-Learning",
    # "DQN"
]