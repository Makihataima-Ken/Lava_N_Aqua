from typing import Dict, Any, List, Optional, Tuple
import random
import pickle
from copy import deepcopy

from src.Lava_Aqua.agents.base_agent import BaseAgent
from src.Lava_Aqua.core.constants import TRAINED_MODELS_DIR, Direction


class GeneticAgent(BaseAgent):
    """Genetic Algorithm agent that evolves action sequences."""

    def __init__(
        self,
        population_size: int = 80,
        chromosome_length: int = 80,
        elite_count: int = 6,
        mutation_rate: float = 0.08,
        crossover_rate: float = 0.85,
        max_steps_per_episode: int = 80,
    ):
        super().__init__("Genetic")

        self.population_size = population_size
        self.chromosome_length = chromosome_length
        self.elite_count = max(1, min(elite_count, population_size))
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.max_steps = max_steps_per_episode

        self.actions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        self.num_actions = len(self.actions)

        self.population: List[List[int]] = []
        self.best_genome: Optional[List[int]] = None
        self.best_fitness: float = float("-inf")

        # Keep epsilon for compatibility with RLController logging.
        self.epsilon = 0.0

        self.stats.update({
            'generations': 0,
            'best_fitness': self.best_fitness,
            'population_size': self.population_size,
        })

    def _random_genome(self) -> List[int]:
        return [random.randint(0, self.num_actions - 1) for _ in range(self.chromosome_length)]

    def _initialize_population(self) -> None:
        self.population = [self._random_genome() for _ in range(self.population_size)]

    def _evaluate_genome(self, game_logic, genome: List[int]) -> Dict[str, Any]:
        simulation = deepcopy(game_logic)
        simulation.reset_level()

        episode_reward = 0.0
        steps = 0
        prev_state = simulation.get_state()

        for action_idx in genome[:self.max_steps]:
            action = self.actions[action_idx]
            move_success = simulation.move_player(action)
            reward = simulation.calculate_reward(move_success, prev_state)
            prev_state = simulation.get_state()

            episode_reward += reward
            steps += 1

            if simulation.level_complete or simulation.game_over:
                break

        return {
            'fitness': episode_reward,
            'steps': steps,
            'level_complete': simulation.level_complete,
            'game_over': simulation.game_over,
        }

    def _select_parent(self, scored_population: List[Tuple[float, List[int]]]) -> List[int]:
        # Tournament selection
        tournament_size = min(5, len(scored_population))
        candidates = random.sample(scored_population, tournament_size)
        candidates.sort(key=lambda item: item[0], reverse=True)
        return candidates[0][1]

    def _crossover(self, parent1: List[int], parent2: List[int]) -> List[int]:
        if random.random() > self.crossover_rate or self.chromosome_length < 2:
            return parent1[:]

        split = random.randint(1, self.chromosome_length - 1)
        return parent1[:split] + parent2[split:]

    def _mutate(self, genome: List[int]) -> None:
        for i in range(len(genome)):
            if random.random() < self.mutation_rate:
                genome[i] = random.randint(0, self.num_actions - 1)

    def _build_next_population(self, scored_population: List[Tuple[float, List[int]]]) -> None:
        scored_population.sort(key=lambda item: item[0], reverse=True)

        next_population = [genome[:] for _, genome in scored_population[:self.elite_count]]

        while len(next_population) < self.population_size:
            parent1 = self._select_parent(scored_population)
            parent2 = self._select_parent(scored_population)

            child = self._crossover(parent1, parent2)
            self._mutate(child)
            next_population.append(child)

        self.population = next_population

    def run_episode(
        self,
        game_logic,
        training: bool = False,
        visualize: bool = False,
        move_delay: float = 0.05,
        controller=None
    ) -> Dict[str, Any]:
        """Run one GA generation (training) or evaluate best genome (inference)."""
        if not self.population:
            self._initialize_population()

        if training:
            scored_population: List[Tuple[float, List[int]]] = []
            generation_best_result: Optional[Dict[str, Any]] = None

            for genome in self.population:
                result = self._evaluate_genome(game_logic, genome)
                fitness = result['fitness']
                scored_population.append((fitness, genome))

                if generation_best_result is None or fitness > generation_best_result['total_reward']:
                    generation_best_result = {
                        'steps': result['steps'],
                        'total_reward': fitness,
                        'level_complete': result['level_complete'],
                        'game_over': result['game_over'],
                    }

                self.stats['total_steps'] += result['steps']

            best_fitness, best_genome = max(scored_population, key=lambda item: item[0])
            if best_fitness > self.best_fitness:
                self.best_fitness = best_fitness
                self.best_genome = best_genome[:]

            self._build_next_population(scored_population)

            self.stats['total_episodes'] += 1
            self.stats['generations'] += 1
            self.stats['best_fitness'] = self.best_fitness

            return {
                'steps': generation_best_result['steps'] if generation_best_result else 0,
                'total_reward': generation_best_result['total_reward'] if generation_best_result else float('-inf'),
                'level_complete': generation_best_result['level_complete'] if generation_best_result else False,
                'game_over': generation_best_result['game_over'] if generation_best_result else False,
                'terminated': False,
            }

        genome_to_run = self.best_genome if self.best_genome else self.population[0]
        result = self._evaluate_genome(game_logic, genome_to_run)
        self.stats['total_episodes'] += 1
        self.stats['total_steps'] += result['steps']

        return {
            'steps': result['steps'],
            'total_reward': result['fitness'],
            'level_complete': result['level_complete'],
            'game_over': result['game_over'],
            'terminated': False,
        }

    def solve(self, game_logic) -> Tuple[List[Direction], int]:
        """Run the best available genome and return path with success flag."""
        if not self.best_genome:
            if not self.population:
                self._initialize_population()

            scored_population = [
                (self._evaluate_genome(game_logic, genome)['fitness'], genome)
                for genome in self.population
            ]
            best_fitness, best_genome = max(scored_population, key=lambda item: item[0])
            self.best_fitness = max(self.best_fitness, best_fitness)
            self.best_genome = best_genome[:]
            self.stats['best_fitness'] = self.best_fitness

        simulation = deepcopy(game_logic)
        simulation.reset_level()

        path: List[Direction] = []
        success = 0

        for action_idx in self.best_genome[:self.max_steps]:
            action = self.actions[action_idx]
            path.append(action)
            simulation.move_player(action)

            if simulation.level_complete:
                success = 1
                break
            if simulation.game_over:
                break

        return path, success

    def save(self, filepath: str) -> None:
        """Save GA agent state."""
        save_path = TRAINED_MODELS_DIR / filepath if not filepath.startswith('/') else filepath

        save_data = {
            'population': self.population,
            'best_genome': self.best_genome,
            'best_fitness': self.best_fitness,
            'stats': self.stats,
            'hyperparameters': {
                'population_size': self.population_size,
                'chromosome_length': self.chromosome_length,
                'elite_count': self.elite_count,
                'mutation_rate': self.mutation_rate,
                'crossover_rate': self.crossover_rate,
                'max_steps': self.max_steps,
            },
        }

        with open(save_path, 'wb') as f:
            pickle.dump(save_data, f)

        print(f"💾 Genetic Agent saved: best fitness={self.best_fitness:.2f}")

    def load(self, filepath: str) -> None:
        """Load GA agent state."""
        with open(filepath, 'rb') as f:
            save_data = pickle.load(f)

        self.population = save_data.get('population', self.population)
        self.best_genome = save_data.get('best_genome', self.best_genome)
        self.best_fitness = save_data.get('best_fitness', self.best_fitness)
        self.stats = save_data.get('stats', self.stats)

        if 'hyperparameters' in save_data:
            hyper = save_data['hyperparameters']
            self.population_size = hyper.get('population_size', self.population_size)
            self.chromosome_length = hyper.get('chromosome_length', self.chromosome_length)
            self.elite_count = hyper.get('elite_count', self.elite_count)
            self.mutation_rate = hyper.get('mutation_rate', self.mutation_rate)
            self.crossover_rate = hyper.get('crossover_rate', self.crossover_rate)
            self.max_steps = hyper.get('max_steps', self.max_steps)

        self.stats['best_fitness'] = self.best_fitness

        print(f"📂 Genetic Agent loaded: best fitness={self.best_fitness:.2f}")
