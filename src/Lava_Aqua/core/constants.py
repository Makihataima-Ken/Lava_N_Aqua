"""Game constants and configuration."""

from enum import Enum
from pathlib import Path

# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
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
    PLAYER = (0, 255, 255)
    PLAYER_DARK = (0, 200, 200)
    EXIT = (50, 205, 50)
    EXIT_DARK = (34, 139, 34)
    WALL = (169, 169, 169)
    WALL_DARK = (105, 105, 105)
    EMPTY = (40, 40, 40)
    
    # UI colors
    UI_BG = (30, 30, 40)
    UI_TEXT = (220, 220, 220)
    UI_HIGHLIGHT = (100, 149, 237)
    UI_SUCCESS = (50, 205, 50)
    UI_DANGER = (255, 69, 0)

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

# Input keys
class InputAction(Enum):
    """Input action enumeration."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    UNDO = "undo"
    RESET = "reset"
    QUIT = "quit"
    NEXT_LEVEL = "next"
    MENU = "menu"