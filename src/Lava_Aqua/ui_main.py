import pygame
from src.Lava_Aqua.graphics.menu import Menu, MenuItem
from src.Lava_Aqua.app.game_app import GameApplication
from src.Lava_Aqua.algorithms.bfs_solver import BFSSolver
from src.Lava_Aqua.algorithms.dfs_solver import DFSSolver
from src.Lava_Aqua.algorithms.ucs_solver import UCSSolver
from src.Lava_Aqua.algorithms.dijkstra_solver import DijkstraSolver
from src.Lava_Aqua.algorithms.aStar_solver import AStarSolver
from src.Lava_Aqua.algorithms.hill_climbing import HillClimbingSolver
from src.Lava_Aqua.agents.qlearning_agent import QLearningAgent
from src.Lava_Aqua.agents.dqn_agent import DQNAgent

def launch_game(app: GameApplication, level_index: int, **kwargs):
    """
    Loads a specific level and launches the game with the given configuration.
    """
    print(f"Loading level {level_index + 1} and launching with options: {kwargs}")
    app.game_logic.load_level(level_index)
    app.run(**kwargs)

def show_level_menu(screen: pygame.Surface, app: GameApplication, controller_config: dict):
    """
    Displays the level selection menu.
    
    Args:
        screen: The pygame screen to draw on.
        app: The main game application instance.
        controller_config: A dictionary with the solver or agent selected previously.
    """
    total_levels = app.game_logic.get_total_levels()

    # Create a list of menu items, one for each level.
    # The 'on_select' for each item is a function that calls 'launch_game' with the
    # correct level index and the controller configuration we received.
    level_items = [
        MenuItem(
            text=f"Level {i + 1}",
            on_select=lambda i=i: launch_game(app, level_index=i, **controller_config)
        ) for i in range(total_levels)
    ]

    # If there are no levels, display a message instead of an empty menu
    if not level_items:
        level_items = [MenuItem("No levels found!", on_select=lambda: None)]

    level_menu = Menu(screen, "Select Level", level_items)
    level_menu.run() # This will block until a level is selected

def main():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Lava & Aqua")

    app = GameApplication()

    # --- Controller Actions ---
    # Instead of launching the game directly, each controller's action
    # will now call 'show_level_menu', passing its specific configuration.
    
    controller_configs = {
        "Player": {"visualize": True},
        "BFS": {"solver": BFSSolver(), "visualize": True},
        "DFS": {"solver": DFSSolver(), "visualize": True},
        "UCS": {"solver": UCSSolver(), "visualize": True},
        "Dijkstra": {"solver": DijkstraSolver(), "visualize": True},
        "A*": {"solver": AStarSolver(), "visualize": True},
        "Hill Climbing": {"solver": HillClimbingSolver(), "visualize": True},
        "Q-Learning": {"agent": QLearningAgent(), "visualize": False},
        "DQN": {
            "agent": DQNAgent(state_shape=app.game_logic.get_grid_dimensions() + (6,)),
            "visualize": False
        },
    }

    # Create the controller menu items.
    # The 'on_select' action for each is now a lambda that calls 'show_level_menu'
    # with the correct screen, app instance, and controller configuration.
    controller_items = [
        MenuItem(
            name, 
            on_select=lambda config=config: show_level_menu(screen, app, config)
        ) for name, config in controller_configs.items()
    ]
    
    # --- Run the Controller Menu ---
    # This is the first menu the user will see.
    controller_menu = Menu(screen, "Select Controller", controller_items)
    controller_menu.run()

    # After the controller_menu.run() completes, a level will have been selected,
    # and the game will have been launched. The program can now gracefully exit.
    print("Game session finished. Exiting.")

if __name__ == "__main__":
    main()

