from enum import Enum

class GameResult(Enum):
    """Possible outcomes of a level."""
    WIN = 'win'
    RESTART = 'restart'
    QUIT = 'quit'
    CONTINUE = 'continue'
