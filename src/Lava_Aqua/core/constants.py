"""Game constants and configuration."""

from enum import Enum
from pathlib import Path

# # Window settings
# WINDOW_WIDTH = 800
# WINDOW_HEIGHT = 600
FPS = 60
TITLE = "Lava & Aqua"

# Grid settings
TILE_SIZE = 40
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 100

# Colors (RGB)
class Color:
    """Color constants."""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)
    
    # Tile colors
    LAVA = (255, 69, 0)
    LAVA_DARK = (200, 40, 0)
    WATER = (30, 144, 255)
    WATER_DARK = (0, 100, 200)
    PLAYER = (255, 255, 0)
    PLAYER_DARK = (200, 200, 0)
    EXIT = (50, 205, 50)
    EXIT_DARK = (34, 139, 34)
    WALL = (169, 169, 169)
    WALL_DARK = (105, 105, 105)
    EMPTY = (40, 40, 40)

# Tile types
class TileType(Enum):
    """Tile type enumeration."""
    EMPTY = " "
    WALL = "#"
    LAVA = "L"
    WATER = "W"
    PLAYER = "P"
    EXIT = "E"
    FLOOR = "."

# Animation settings
ANIMATION_SPEED = 0.1
LAVA_ANIMATION_FRAMES = 4
WATER_ANIMATION_FRAMES = 3

# File paths
BASE_DIR = Path(__file__).parent.parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LEVELS_DIR = ASSETS_DIR / "levels"
LEVELS_FILE = LEVELS_DIR / "levels.json"
IMAGES_DIR = ASSETS_DIR / "images"
FONTS_DIR = ASSETS_DIR / "fonts"

# Game settings
MAX_UNDO_HISTORY = 50
MOVE_ANIMATION_DURATION = 0.15  # seconds

class GameResult(Enum):
    """Possible outcomes of a level."""
    WIN = 'win'
    RESTART = 'restart'
    QUIT = 'quit'
    CONTINUE = 'continue'