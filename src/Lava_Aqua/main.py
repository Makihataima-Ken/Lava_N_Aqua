from src.Lava_Aqua.app.game_app import GameApplication

from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.controllers.player_controller import PlayerController
from src.Lava_Aqua.algorithms import BFSSolver

def main_user_play():
    """Run game in user play mode."""
    app = GameApplication()
    app.run()


def main_solver_bfs():
    """Run game with BFS solver."""
    app = GameApplication()
    solver = BFSSolver()
    app.run(
        solver=solver,
        move_delay=0.3,
        visualize=True
    )
    
def main_solver_dfs():
    """Run game with DFS solver."""
    from src.Lava_Aqua.algorithms.dfs_solver import DFSSolver
    app = GameApplication()
    solver = DFSSolver()
    app.run(
        solver=solver,
        move_delay=0.1,
        visualize=True
    )
    
def main_solver_ucs():
    """Run game with UCS solver."""
    from src.Lava_Aqua.algorithms.ucs_solver import UCSSolver
    app = GameApplication()
    solver = UCSSolver()
    app.run(
        solver=solver,
        move_delay=0.1,
        visualize=True
    )
    
# def main_solver_aStar():
#     from src.Lava_Aqua.algorithms.aStar_solver import AStarSolver
#     app = GameApplication()
#     solver = AStarSolver()
#     app.run(
#         solver=solver,
#         move_delay=0.1,
#         visualize=True
#     )
def main_agent_train_qlearning():
    """Train Q-Learning agent."""
    from src.Lava_Aqua.agents.qlearning_agent import QLearningAgent
    from src.Lava_Aqua.controllers.rl_controller import RLController
    
    app = GameApplication()
    height, width = app.game_logic.get_grid_dimensions()
    state_shape = (height, width, 6)
    
    agent = QLearningAgent(
        state_shape = state_shape,
        num_actions=4,
        learning_rate=0.1,
        gamma=0.99,
        epsilon=1.0,
        epsilon_decay=0.995,
        epsilon_min=0.01
    )
    
    app.run(
        agent=agent,
        move_delay=0.5,
        visualize=False
    )
def main():
    """Run game with command-line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Lava & Aqua Game')
    parser.add_argument(
        '--mode',
        choices=['play', 'bfs', 'dfs', 'random','aStar','ucs','qlearning'],
        default='play',
        help='Game mode'
    )
    parser.add_argument(
        '--speed',
        type=float,
        default=0.2,
        help='Solver move delay in seconds'
    )
    parser.add_argument(
        '--max-depth',
        type=int,
        default=50,
        help='Max depth for DFS solver'
    )
    parser.add_argument(
        '--no-visualize',
        action='store_true',
        help='Disable visualization (faster solving)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'play':
        main_user_play()
    elif args.mode == 'bfs':
        main_solver_bfs()
    elif args.mode == 'dfs':
        main_solver_dfs()
    elif args.mode == 'ucs':
        main_solver_ucs()
    elif args.mode == 'qlearning':
        main_agent_train_qlearning()
    # elif args.mode == 'aStar':
    #     main_solver_aStar()


if __name__ == "__main__":
    main()