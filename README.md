# Lava & Aqua

Lava & Aqua is a compact, educational puzzle game and solver sandbox written
in Python. Play interactively, or run automated solvers (BFS, DFS, UCS) and an
RL-based Q-learning agent to experiment with search and reinforcement learning
techniques on small grid-based levels.

**Current status**

- Playable interactive mode using Pygame.
- Multiple solver implementations included: BFS, DFS, UCS.
- Basic Q-learning agent and RL controller under `src/Lava_Aqua/agents`.
- Levels and recorded solutions in `assets/levels` and `assets/solutions`.

**Goals**

- Provide a compact codebase for learning search algorithms and simple RL.
- Make it easy to add new levels, solvers, and agents for experimentation.

**Quick start (Windows)**

1. Create and activate a virtual environment, then install the package in
   editable mode:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

2. Run the interactive game:

```powershell
python -m src.Lava_Aqua.main --mode play
```

3. Run a solver (example: BFS):

```powershell
python -m src.Lava_Aqua.main --mode bfs
```

4. Train / run Q-learning (example):

```powershell
python -m src.Lava_Aqua.main --mode qlearning
```

Tip: some environments include a runner named `uv`; you can use
`uv run -m src.Lava_Aqua.main --mode <mode>` if preferred.

**Command-line options**

- `--mode` : Choose one of `play`, `bfs`, `dfs`, `ucs`, `qlearning` (see
  `src/Lava_Aqua/main.py` for the exact set of supported modes).
- `--level`: (optional) specify a level filename from `assets/levels/`.

Check `src/Lava_Aqua/main.py` for the full set of runtime options and flags.

**Project layout (overview)**

- `src/Lava_Aqua/core/` — game rules, level parsing, constants, and state.
- `src/Lava_Aqua/entities/` — entity implementations: `player`, `lava`, `box`,
  `temporary_wall`, `exit_key`, etc.
- `src/Lava_Aqua/graphics/` — rendering helpers, grid and tile code.
- `src/Lava_Aqua/controllers/` — `player_controller`, `solver_controller`,
  `rl_controller` and factory wiring.
- `src/Lava_Aqua/algorithms/` — `BaseSolver` and search algorithm
  implementations (BFS, DFS, UCS).
- `src/Lava_Aqua/agents/` — RL agents and helpers (Q-learning agent).
- `assets/levels/` — level JSON files used by the game and solvers.
- `assets/solutions/` — recorded solver traces and example solutions.

**Adding levels**

1. Copy an example from `assets/levels/` and modify the JSON to define a new
   layout and entities.
2. (Optional) add a matching solution file under `assets/solutions/` for
   regression testing.

Follow existing files in `assets/levels/` as templates.

**Adding a solver or agent**

1. Implement a solver by subclassing `BaseSolver` in
   `src/Lava_Aqua/algorithms/base_solver.py`.
2. Add tests or a sample level that demonstrates the solver behavior.
3. Wire the solver into the CLI in `src/Lava_Aqua/main.py` if you want a
   dedicated `--mode` for it.

For RL agents, follow the patterns in `src/Lava_Aqua/agents/qlearning_agent.py`
and the RL controller in `src/Lava_Aqua/controllers/rl_controller.py`.

**Development & testing**

- Keep the edit-run-debug cycle short: run small levels when changing rules.
- Use recorded solutions in `assets/solutions/` to validate solver changes.
- Avoid heavy state copying in performance-sensitive solver code; profile if
  needed.

**Dependencies**

- Python 3.10+ (project developed against 3.12).
- Pygame for rendering (tested with 2.6.x).


**Contributing**

- Fork, create a branch, and open a pull request with tests or sample levels.
- For new solvers, include minimal levels that reproduce the solver's use
  cases and link them in the PR description.




