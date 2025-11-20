# Lava & Aqua

Lava & Aqua is a small puzzle game implemented in Python using Pygame.
The player navigates a level with boxes, lava, and an exit — and the project
includes solver algorithms to automatically find solutions for
levels.

**Table of contents**

- **Project**: overview and goals
- **Features**: gameplay and solver modes
- **Requirements**: dependencies and environment
- **Install**: setup steps for Windows (PowerShell)
- **Run**: how to run the game and solver modes
- **Project structure**: important modules and responsibilities
- **Contributing**: how to help and add levels/solvers

**Project**

Lava & Aqua is a top-down puzzle game where the player must reach an exit
while avoiding hazards (lava) and manipulating boxes. The repository includes
both interactive play and automated solvers so you can run the game manually or have the solver attempt to
solve levels with optional visualization.

**Features**

- Player-controlled mode (keyboard)
- Solver mode (a base solver interface for adding algorithms)
- Level data stored under `assets/levels/` as JSON files
- Simple rendering using Pygame (see `src/Lava_Aqua/graphics`)

**Requirements**

- Python 3.10+ (project was developed with Python 3.12; adjust as needed)
- Pygame (tested with 2.6.x)
- Optional: your chosen runner; the project expects to be run as a module
	(examples below use `python -m` or `uv run -m` as in your environment)

**Run the game**

You can run the project as a module. Two common ways shown below:

Using plain Python (recommended):

```powershell
python -m src.Lava_Aqua.main --mode play
```

If you want the BFS solver mode:

```powershell
python -m src.Lava_Aqua.main --mode bfs
```

If your environment uses a runner called `uv` (as in the provided example),
use the same arguments but with that runner:

```powershell
uv run -m src.Lava_Aqua.main --mode bfs
```

Command-line options (from `src/Lava_Aqua/main.py`):
- `--mode`: one of `play`, `bfs`, `dfs`, `random` (default: `play`)

**Project structure (key files)**

- `src/Lava_Aqua/__main__.py` / `src/Lava_Aqua/main.py`: CLI entrypoints and
	high-level launch code. Use `--mode` to switch between play and solver.
- `src/Lava_Aqua/app/game_app.py`: application wrapper that manages the Pygame
	loop and provides `run()` and `run_with_solver()` APIs.
- `src/Lava_Aqua/core/`: core game logic and constants (levels, tiles, rules).
- `src/Lava_Aqua/entities/`: game entities such as `player`, `lava`, `box`,
	and `temporary_wall` implementations.
- `src/Lava_Aqua/algorithms/`: solver implementations.`BaseSolver` defines the
	solver interface.
- `src/Lava_Aqua/graphics/`: rendering code and tile/grid helpers.
- `assets/levels/`: example level JSON files. Add new levels here to test.

**Usage examples**

- Play locally (interactive):

```powershell
python -m src.Lava_Aqua.main --mode play
```

**Adding a level**

1. Create a JSON file in `assets/levels/` following the format of
	 existing sample levels (see `test.json` and `walls_test.json`).
2. Launch the game; the level loader will include any properly structured
	 level files found in that folder.

**Adding a solver**

1. Implement a new solver class that inherits from `BaseSolver` in
	 `src/Lava_Aqua/algorithms/`.
2. Expose the new solver in `src/Lava_Aqua/algorithms/__init__.py` so it can
	 be imported from `src.Lava_Aqua.algorithms`.
3. Wire it into `src/Lava_Aqua/main.py` if you want a CLI mode for it.

**Development notes**

- The project follows a small MVC-like separation: `core` (model & rules),
	`graphics` (view), and `controllers` / `algorithms` (input & solvers).
- Keep changes small and run the game frequently while developing new
	mechanics or solvers. Use `deepcopy` carefully in solvers for performance
	sensitive work.

**Contributing**

- Fork the repo, create a feature branch, and open a pull request. Provide a
	clear description of changes and test instructions.
- For new solvers, include sample levels where the solver behavior can be
	reproduced.



