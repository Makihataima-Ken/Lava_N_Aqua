"""Main game application entry point."""

from src.Lava_Aqua.app.game_app import GameApplication

def main():
    """Entry point for the game."""
    app = GameApplication()
    app.run()


if __name__ == '__main__':
    main()