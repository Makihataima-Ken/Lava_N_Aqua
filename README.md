# Lava & Aqua 🌋💧

A grid-based puzzle game featuring dynamic lava and water mechanics, solvable through classical AI search algorithms and reinforcement learning agents.

## 🎮 Overview

**Lava & Aqua** is an educational puzzle game where players navigate through increasingly complex levels while managing spreading lava, flowing water, movable boxes, temporary walls, and collectible keys. The project serves as a comprehensive sandbox for experimenting with:

- **Classical AI Search Algorithms**: BFS, DFS, UCS, Dijkstra, A*, Hill Climbing
- **Reinforcement Learning**: Q-Learning and Deep Q-Network (DQN) agents
- **Game AI Development**: Complete framework for implementing and testing new algorithms

## ✨ Features

### Game Mechanics
- **Dynamic Lava Flow**: Lava spreads across the grid each turn
- **Water (Aqua)**: Flows similarly to lava; collision creates walls
- **Movable Boxes**: Push boxes to block lava or create paths
- **Temporary Walls**: Time-limited barriers that disappear after moves
- **Exit Keys**: Collect keys to unlock the exit
- **Multiple Levels**: 19 pre-designed levels with increasing complexity

### AI Capabilities
- **6 Search Algorithms**: Compare performance across different approaches
- **2 RL Agents**: Train and evaluate Q-Learning and DQN agents
- **Solution Recording**: Save and replay optimal solutions
- **Performance Metrics**: Track nodes explored, solution length, and execution time
- **Visual Debugging**: Watch algorithms solve levels in real-time

## 🚀 Quick Start

### Prerequisites
- Python 3.12.12
- pip or uv package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/lava-and-aqua.git
cd lava-and-aqua
```

2. **Create virtual environment**
```bash
python -m venv .venv
```

3. **Activate environment**

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -e .
```

## 🎯 Usage

### Interactive Menu (Recommended)
Launch the interactive UI to select controllers and levels:
```bash
python -m src.Lava_Aqua.ui_main
```

Features:
- Navigate with arrow keys
- Select controller type (Player, Solver, RL Agent)
- Choose from available levels
- Load pre-trained RL models
- Visual feedback and progress tracking

### Command Line Interface

#### Play Manually
```bash
python -m src.Lava_Aqua.main --mode play
```

**Controls:**
- `WASD` or `Arrow Keys` - Move
- `R` - Reset level
- `U/Z` - Undo move
- `ESC` - Quit

#### Run Search Algorithms

**Breadth-First Search:**
```bash
python -m src.Lava_Aqua.main --mode bfs --visualize
```

**Depth-First Search:**
```bash
python -m src.Lava_Aqua.main --mode dfs
```

**A* Search:**
```bash
python -m src.Lava_Aqua.main --mode aStar --visualize
```

**Available modes:**
- `bfs` - Breadth-First Search
- `dfs` - Depth-First Search  
- `ucs` - Uniform Cost Search
- `dijkstra` - Dijkstra's Algorithm
- `aStar` - A* Search
- `hc` - Hill Climbing

**Options:**
- `--visualize` - Watch the algorithm solve (slower but visual)
- Omit `--visualize` for faster solving

#### Train Reinforcement Learning Agents

**Q-Learning:**
```bash
python -m src.Lava_Aqua.main --mode qlearning
```

**Deep Q-Network:**
```bash
python -m src.Lava_Aqua.main --mode dqn
```

Training will:
1. Run 1000 episodes by default
2. Evaluate every 100 episodes
3. Save the trained model to `assets/trained models/`
4. Generate training curves plot
5. Run a final visualization episode

#### Load and Run Trained Models
```python
from src.Lava_Aqua.agents.dqn_agent import DQNAgent
from src.Lava_Aqua.controllers.rl_controller import RLController
from src.Lava_Aqua.core.game import GameLogic

# Load game
env = GameLogic()
env.load_level(1)  # Select level

# Load agent
agent = DQNAgent(state_shape=(env.get_grid_dimensions()[0], 
                              env.get_grid_dimensions()[1], 6))

# Create controller and run
controller = RLController(game_logic=env, agent=agent)
controller.run_level(
    agent_path="assets/trained models/dqn_agent.pkl",
    visualize=True
)
```

## 📁 Project Structure
```
lava-and-aqua/
├── assets/
│   ├── levels/              # Level definitions (JSON)
│   ├── solutions/           # Recorded algorithm solutions
│   │   ├── BFS/
│   │   ├── DFS/
│   │   ├── A Star/
│   │   └── ...
│   ├── trained models/      # Saved RL agents (.pkl)
│   └── training_plots/      # Training visualization graphs
│
├── src/Lava_Aqua/
│   ├── core/               # Game logic and state management
│   │   ├── game.py         # Main game engine
│   │   ├── level.py        # Level loading and management
│   │   └── constants.py    # Game constants
│   │
│   ├── entities/           # Game entities
│   │   ├── player.py
│   │   ├── lava.py
│   │   ├── aqua.py
│   │   ├── box.py
│   │   ├── temporary_wall.py
│   │   └── exit_key.py
│   │
│   ├── algorithms/         # Search algorithms
│   │   ├── base_solver.py  # Abstract base class
│   │   ├── bfs_solver.py
│   │   ├── dfs_solver.py
│   │   ├── aStar_solver.py
│   │   └── ...
│   │
│   ├── agents/             # RL agents
│   │   ├── base_agent.py
│   │   ├── qlearning_agent.py
│   │   └── dqn_agent.py
│   │
│   ├── controllers/        # Game mode controllers
│   │   ├── player_controller.py
│   │   ├── solver_controller.py
│   │   ├── rl_controller.py
│   │   └── controller_factory.py
│   │
│   ├── graphics/           # Rendering and UI
│   │   ├── renderer.py
│   │   ├── grid.py
│   │   ├── tile.py
│   │   └── menu.py
│   │
│   ├── main.py            # CLI entry point
│   └── ui_main.py         # Interactive menu entry point
│
├── pyproject.toml
└── README.md
```

## 🎓 Educational Use Cases

### For Students
- **Learn Search Algorithms**: Visualize how BFS, DFS, A*, etc. explore state space
- **Compare Performance**: Analyze nodes explored, time complexity, and solution quality
- **Experiment with Heuristics**: Modify A* heuristics and observe behavior
- **RL Fundamentals**: Understand Q-Learning and DQN training dynamics

### For Researchers
- **Algorithm Benchmarking**: Test new search strategies on standardized levels
- **RL Experimentation**: Modify reward functions, network architectures, hyperparameters
- **State Space Analysis**: Study impact of dynamic environments on search complexity

### For Developers
- **Game AI Patterns**: Clean separation of game logic, controllers, and AI
- **Pygame Framework**: Reusable rendering and UI components
- **Modular Design**: Easy to extend with new algorithms or game mechanics

## 🔧 Adding Content

### Creating New Levels

1. Copy an example from `assets/levels/levels.json`
2. Define your grid using these symbols:
   - `#` - Wall
   - `P` - Player start
   - `E` - Exit
   - `L` - Lava
   - `W` - Water (Aqua)
   - `B` - Box
   - `K` - Key
   - `T` - Temporary wall
   - `S` - Semi-permeable wall
   - `D` - Dark wall
   - ` ` - Empty space

3. Example level:
```json
{
    "name": "My Custom Level",
    "grid": [
        "############",
        "#P    L   E#",
        "#  B   B   #",
        "############"
    ],
    "temp_walls": [
        {"position": [5, 1], "duration": 20}
    ]
}
```

### Implementing New Algorithms

1. **Create a new solver** in `src/Lava_Aqua/algorithms/`:
```python
from src.Lava_Aqua.algorithms.base_solver import BaseSolver
from src.Lava_Aqua.core.constants import Direction

class MyCustomSolver(BaseSolver):
    def __init__(self):
        super().__init__(name="My Algorithm")
    
    def solve(self, game_logic, visualize=False):
        # Implement your algorithm
        # Return list of Direction moves or None
        pass
```

2. **Register in main.py**:
```python
def main_solver_custom(visualize=False):
    from src.Lava_Aqua.algorithms.my_solver import MyCustomSolver
    app = GameApplication()
    solver = MyCustomSolver()
    app.run(solver=solver, visualize=visualize)
```

### Creating RL Agents

1. **Subclass BaseAgent** in `src/Lava_Aqua/agents/`:
```python
from src.Lava_Aqua.agents.base_agent import BaseAgent

class MyRLAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="My RL Agent")
    
    def run_episode(self, game_logic, training=False, **kwargs):
        # Implement training/evaluation logic
        pass
    
    def solve(self, game_logic):
        # Return path and success indicator
        pass
```

## 📊 Performance Comparison

Example results on Level 2 ("First Challenge"):

| Algorithm | Nodes Explored | Nodes Generated | Time (s) | Solution Length |
|-----------|---------------|-----------------|----------|-----------------|
| BFS       | 1,523         | 3,536          | 0.96     | 14              |
| DFS       | 1,337         | 2,942          | 0.85     | 28              |
| UCS       | 145           | 499            | 0.08     | 18              |
| A*        | 1,482         | 3,488          | 1.04     | 14              |
| Hill Climbing | 59        | 160            | 0.11     | 14              |

**Observations:**
- BFS and A* find optimal solutions
- Hill Climbing is fastest but may get stuck
- DFS explores fewer nodes but finds longer paths
- UCS balances speed and solution quality

## 🤖 RL Agent Training

### Q-Learning Agent
- **State Space**: Discretized game state hash
- **Action Space**: 4 directional moves
- **Default Hyperparameters**:
  - Learning rate: 0.2
  - Discount factor: 0.95
  - Epsilon decay: 0.998
  - Initial epsilon: 1.0

### DQN Agent
- **Architecture**: 2-layer neural network (128→64 units)
- **Input**: 10×10×6 tensor (grid dimensions × feature layers)
- **Feature Layers**:
  1. Walls
  2. Player position
  3. Box positions
  4. Lava positions
  5. Water positions
  6. Exit position
- **Experience Replay**: 10,000 capacity buffer
- **Target Network**: Updated every 100 steps

## 🐛 Known Issues & Limitations

- **Browser Storage**: `localStorage`/`sessionStorage` not supported in artifacts (use in-memory state)
- **Performance**: Complex levels with many entities may slow down visualization
- **DQN Convergence**: May require 5,000+ episodes for challenging levels
- **State Space**: Exponential growth with level complexity affects search algorithms

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Include test levels demonstrating your feature
4. Document algorithm complexity and performance
5. Submit a pull request with clear description

**Areas for Contribution:**
- New search algorithms (IDA*, RBFS, etc.)
- Advanced RL agents (PPO, A3C)
- Level editor UI
- Performance optimizations
- Additional game mechanics

## 📝 License

This project is provided for educational purposes. Feel free to use, modify, and distribute.

## 🙏 Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Inspired by [Lava and Aqua](https://www.crazygames.com/game/lava-and-aqua)
- Developed as an AI education tool

## 📧 Contact

For questions, suggestions, or collaboration:
- Open an issue on GitHub
- Submit a pull request
- Share your custom levels and algorithms!

---

**Made with ❤️ for AI education and puzzle game enthusiasts**