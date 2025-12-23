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
from src.Lava_Aqua.core.constants import TRAINED_MODELS_DIR


def launch_game(app: GameApplication, level_index: int, **kwargs):
    """
    Loads a specific level and launches the game with the given configuration.
    """
    print(f"Loading level {level_index + 1} and launching with options: {kwargs}")
    app.game_logic.load_level(level_index)
    app.run(**kwargs)


def get_available_agent_models(agent_type: str) -> list:
    """
    Scans the trained models directory for available agent files.
    
    Args:
        agent_type: Type of agent ('qlearning' or 'dqn')
    
    Returns:
        List of tuples (display_name, filepath)
    """
    models = []
    
    # Ensure the directory exists
    if not TRAINED_MODELS_DIR.exists():
        return models
    
    # Search for .pkl files
    for file_path in TRAINED_MODELS_DIR.glob("*.pkl"):
        filename = file_path.name
        # Filter by agent type if specified
        if agent_type == 'qlearning' and 'qlearning' in filename.lower():
            models.append((filename, str(file_path)))
        elif agent_type == 'dqn' and 'dqn' in filename.lower():
            models.append((filename, str(file_path)))
        elif agent_type is None:  # Show all models
            models.append((filename, str(file_path)))
    
    return sorted(models, key=lambda x: x[0])


def show_agent_selection_menu(
    screen: pygame.Surface,
    app: GameApplication,
    agent_type: str,
    base_config: dict
) -> None:
    """
    Displays a menu to select a pre-trained agent model or train a new one.
    
    Args:
        screen: The pygame screen to draw on
        app: The main game application instance
        agent_type: Type of agent ('qlearning' or 'dqn')
        base_config: Base configuration for the agent
    """
    available_models = get_available_agent_models(agent_type)
    
    menu_items = []
    
    # Add option to train a new agent (no pre-trained model)
    def select_no_model():
        config = base_config.copy()
        config['agent_path'] = None
        show_level_menu(screen, app, config)
    
    menu_items.append(
        MenuItem(
            text="Train New Agent",
            on_select=select_no_model,
            description="Start training from scratch"
        )
    )
    
    # Add available pre-trained models
    if available_models:
        for display_name, file_path in available_models:
            def select_model(path=file_path):
                config = base_config.copy()
                config['agent_path'] = path
                show_level_menu(screen, app, config)
            
            menu_items.append(
                MenuItem(
                    text=display_name,
                    on_select=select_model,
                    description=f"Load: {file_path}"
                )
            )
    else:
        menu_items.append(
            MenuItem(
                text="No pre-trained models found",
                on_select=lambda: None,
                description=f"No .pkl files in {TRAINED_MODELS_DIR}"
            )
        )
    
    # Add back button
    menu_items.append(
        MenuItem(
            text="Back",
            on_select=lambda: show_controller_menu(screen, app)
        )
    )
    
    agent_menu = Menu(
        screen,
        f"Select {agent_type.upper()} Agent Model",
        menu_items
    )
    agent_menu.run()


def show_level_menu(
    screen: pygame.Surface,
    app: GameApplication,
    controller_config: dict
) -> None:
    """
    Displays the level selection menu.
    
    Args:
        screen: The pygame screen to draw on
        app: The main game application instance
        controller_config: A dictionary with the solver or agent selected previously
    """
    total_levels = app.game_logic.get_total_levels()

    level_items = [
        MenuItem(
            text=f"Level {i + 1}",
            on_select=lambda i=i: launch_game(app, level_index=i, **controller_config)
        ) for i in range(total_levels)
    ]

    if not level_items:
        level_items = [MenuItem("No levels found!", on_select=lambda: None)]
    
    # Add back button
    level_items.append(
        MenuItem(
            text="Back",
            on_select=lambda: show_controller_menu(screen, app)
        )
    )

    level_menu = Menu(screen, "Select Level", level_items)
    level_menu.run()


def show_controller_menu(screen: pygame.Surface, app: GameApplication) -> None:
    """
    Displays the main controller selection menu.
    
    Args:
        screen: The pygame screen to draw on
        app: The main game application instance
    """
    # Direct controller configs (no agent selection needed)
    direct_configs = {
        "Player": {"visualize": True},
        "BFS": {"solver": BFSSolver(), "visualize": True},
        "DFS": {"solver": DFSSolver(), "visualize": True},
        "UCS": {"solver": UCSSolver(), "visualize": True},
        "Dijkstra": {"solver": DijkstraSolver(), "visualize": True},
        "A*": {"solver": AStarSolver(), "visualize": True},
        "Hill Climbing": {"solver": HillClimbingSolver(), "visualize": True},
    }
    
    controller_items = []
    
    # Add direct controllers
    for name, config in direct_configs.items():
        controller_items.append(
            MenuItem(
                name,
                on_select=lambda config=config: show_level_menu(screen, app, config)
            )
        )
    
    # Add RL agents that require model selection
    def select_qlearning():
        base_config = {
            "agent": QLearningAgent(),
            "visualize": False
        }
        show_agent_selection_menu(screen, app, "qlearning", base_config)
    
    def select_dqn():
        base_config = {
            "agent": DQNAgent(
                state_shape=app.game_logic.get_grid_dimensions() + (6,)
            ),
            "visualize": False
        }
        show_agent_selection_menu(screen, app, "dqn", base_config)
    
    controller_items.extend([
        MenuItem("Q-Learning", on_select=select_qlearning),
        MenuItem("DQN", on_select=select_dqn),
    ])
    
    # Add exit option
    controller_items.append(
        MenuItem(
            text="Exit",
            on_select=lambda: exit_game()
        )
    )
    
    controller_menu = Menu(screen, "Select Controller", controller_items)
    controller_menu.run()


def exit_game():
    """Gracefully exit the game."""
    print("Exiting game...")
    pygame.quit()
    raise SystemExit


def main():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Lava & Aqua")

    app = GameApplication()
    
    # Display models directory info
    print(f"📁 Trained models directory: {TRAINED_MODELS_DIR}")
    if TRAINED_MODELS_DIR.exists():
        model_count = len(list(TRAINED_MODELS_DIR.glob("*.pkl")))
        print(f"   Found {model_count} .pkl model file(s)")
    else:
        print(f"   Directory does not exist. It will be created when saving models.")
    
    # Start with the controller menu
    show_controller_menu(screen, app)
    
    print("Game session finished. Exiting.")


if __name__ == "__main__":
    main()