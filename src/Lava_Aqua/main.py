from .app.game_app import GameApplication

def main_user_play():
    """Run game in user play mode."""
    app = GameApplication()
    app.run()


def main_solver_bfs(visualize=False):
    """Run game with BFS solver."""
    from .algorithms import BFSSolver
    app = GameApplication()
    solver = BFSSolver()
    app.run(
        solver=solver,
        visualize=visualize
    )
    
def main_solver_dfs(visualize=False):
    """Run game with DFS solver."""
    from .algorithms.dfs_solver import DFSSolver
    app = GameApplication()
    solver = DFSSolver()
    app.run(
        solver=solver,
        visualize=visualize
    )
    
def main_solver_ucs(visualize=False):
    """Run game with UCS solver."""
    from .algorithms.ucs_solver import UCSSolver
    app = GameApplication()
    solver = UCSSolver()
    app.run(
        solver=solver,
        visualize=visualize
    )
    
def main_solver_dijkstra(visualize=False):
    """Run game with Dijkstra solver."""
    from .algorithms.dijkstra_solver import DijkstraSolver
    app = GameApplication()
    solver = DijkstraSolver()
    app.run(
        solver=solver,
        visualize=visualize
    )
    
def main_solver_aStar(visualize=False):
    from .algorithms.aStar_solver import AStarSolver
    app = GameApplication()
    solver = AStarSolver()
    app.run(
        solver=solver,
        visualize=visualize
    )
    
def main_solver_hill_climbing(visualize=False):
    from .algorithms.hill_climbing import HillClimbingSolver
    app = GameApplication()
    solver = HillClimbingSolver()
    app.run(
        solver=solver,
        visualize=visualize
    )

def main_agent_train_qlearning():
    """Train Q-Learning agent."""
    from .agents.qlearning_agent import QLearningAgent
    from .controllers.rl_controller import RLController
    
    app = GameApplication()
    height, width = app.game_logic.get_grid_dimensions()
    state_shape = (height, width, 6)
    
    agent = QLearningAgent(
        # state_shape = state_shape,
        # num_actions=4,
        # learning_rate=0.1,
        # gamma=0.99,
        # epsilon=1.0,
        # epsilon_decay=0.995,
        # epsilon_min=0.01
    )
    
    app.run(
        agent=agent,
        move_delay=0.5,
        visualize=False
    )
def main_agent_train_DQN():
    """Train Q-Learning agent."""
    from .agents.dqn_agent import DQNAgent
    
    app = GameApplication()
    height, width = app.game_logic.get_grid_dimensions()
    state_shape = (height, width, 6)
    
    agent = DQNAgent(
        state_shape = state_shape,
        # num_actions=4,
        # learning_rate=0.1,
        # gamma=0.99,
        # epsilon=1.0,
        # epsilon_decay=0.995,
        # epsilon_min=0.01
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
        choices=['play', 'bfs', 'dfs', 'random','aStar','ucs','qlearning','dijkstra','dqn','hc'],
        default='play',
        help='Game mode'
    )
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Enable visualization (default: disabled)'
    )
    
    args = parser.parse_args()
    visualize = args.visualize
    
    if args.mode == 'play':
        main_user_play(visualize)
    elif args.mode == 'bfs':
        main_solver_bfs(visualize)
    elif args.mode == 'dfs':
        main_solver_dfs(visualize)
    elif args.mode == 'ucs':
        main_solver_ucs(visualize)
    elif args.mode == 'dijkstra':
        main_solver_dijkstra(visualize)
    elif args.mode =='hc':
        main_solver_hill_climbing(visualize)
    elif args.mode == 'aStar':
        main_solver_aStar(visualize)
    elif args.mode == 'qlearning':
        main_agent_train_qlearning()
    elif args.mode == 'dqn':
        main_agent_train_DQN()

if __name__ == "__main__":
    main()