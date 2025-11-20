"""Main game application entry point."""

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

def main():
    """Run game with command-line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Lava & Aqua Game')
    parser.add_argument(
        '--mode',
        choices=['play', 'bfs', 'dfs', 'random'],
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
    


if __name__ == "__main__":
    main()