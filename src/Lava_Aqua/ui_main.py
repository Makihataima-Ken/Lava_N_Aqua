from src.Lava_Aqua.algorithms.hill_climbing import HillClimbingSolver
from src.Lava_Aqua.graphics.menu import Menu
from src.Lava_Aqua.app.game_app import GameApplication
from src.Lava_Aqua.algorithms import BFSSolver
from src.Lava_Aqua.algorithms.dfs_solver import DFSSolver
from src.Lava_Aqua.algorithms.ucs_solver import UCSSolver
from src.Lava_Aqua.algorithms.dijkstra_solver import DijkstraSolver
from src.Lava_Aqua.algorithms.aStar_solver import AStarSolver
from src.Lava_Aqua.agents.qlearning_agent import QLearningAgent
from src.Lava_Aqua.agents.dqn_agent import DQNAgent
from src.Lava_Aqua.core.constants import CONTROLLER_OPTIONS
import pygame


def level_menu(screen, total_levels: int) -> int:
    levels = [f"Level {i+1}" for i in range(total_levels)]
    menu = Menu(screen, "Select Level", levels)
    return menu.run()

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Lava & Aqua")


    # Controller menu
    controller_menu = Menu(
        screen,
        "Select Controller",
        CONTROLLER_OPTIONS
    )
    controller_choice = controller_menu.run()

    app = GameApplication()
    total_levels = app.game_logic.get_total_levels()

    # Level menu
    level_index = level_menu(screen, total_levels)
    app.game_logic.load_level(level_index)

    # Launch selected mode
    if controller_choice == 0:
        app.run()

    elif controller_choice == 1:
        app.run(solver=BFSSolver(), visualize=True)

    elif controller_choice == 2:
        app.run(solver=DFSSolver(), visualize=True)

    elif controller_choice == 3:
        app.run(solver=UCSSolver(), visualize=True)
        
    elif controller_choice == 4:
        app.run(solver=DijkstraSolver(), visualize=True)
        
    elif controller_choice == 5:
        app.run(solver=AStarSolver(), visualize=True)
        
    elif controller_choice == 6:
         app.run(solver=HillClimbingSolver(), visualize=True)

    # elif controller_choice == 7:
    #     agent = QLearningAgent()
    #     app.run(agent=agent, visualize=False)
        
    # elif controller_choice == 8:
    #     height, width = app.game_logic.get_grid_dimensions()
    #     state_shape = (height, width, 6)
    #     agent = DQNAgent(state_shape=state_shape)
    #     app.run(agent=agent, visualize=False)

if __name__ == "__main__":
    main()