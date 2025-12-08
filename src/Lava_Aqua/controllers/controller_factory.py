from typing import Type, Optional, Dict, Any
from enum import Enum

from src.Lava_Aqua.agents.base_agent import BaseAgent
from src.Lava_Aqua.controllers.rl_controller import RLController
from src.Lava_Aqua.core.game import GameLogic
from src.Lava_Aqua.controllers.base_controller import BaseController
from src.Lava_Aqua.controllers.player_controller import PlayerController
from src.Lava_Aqua.controllers.solver_controller import SolverController
from src.Lava_Aqua.algorithms.base_solver import BaseSolver


class ControllerType(Enum):
    """Available controller types."""
    PLAYER = "player"
    SOLVER = "solver"
    RL = "reinforcement_learning"


class ControllerFactory:
    """Factory for creating game controllers."""
    
    _controllers: Dict[ControllerType, Type[BaseController]] = {
        ControllerType.PLAYER: PlayerController,
        ControllerType.SOLVER: SolverController,
        ControllerType.RL: RLController
    }
    
    @classmethod
    def create(cls, controller_type: ControllerType, 
               game_logic: GameLogic, 
               **kwargs) -> BaseController:
        """Create a controller instance.
        
        Args:
            controller_type: Type of controller to create
            game_logic: Game logic instance
            **kwargs: Additional arguments for specific controller types
                For SOLVER: solver (BaseSolver), move_delay (float), visualize (bool)
        
        Returns:
            Controller instance
            
        Raises:
            ValueError: If controller type is not registered
            TypeError: If required arguments are missing
        """
        if controller_type not in cls._controllers:
            raise ValueError(f"Unknown controller type: {controller_type}")
        
        controller_class = cls._controllers[controller_type]
        
        try:
            return controller_class(game_logic, **kwargs)
        except TypeError as e:
            # Re-raise the TypeError with more context
            raise TypeError(
                f"Failed to create {controller_class.__name__} for "
                f"type {controller_type}. Missing/invalid arguments? "
                f"Original error: {e}"
            ) from e
    
    @classmethod
    def create_player(cls, game_logic: GameLogic) -> PlayerController:
        """Create a player controller (convenience method).
        
        Args:
            game_logic: Game logic instance
            
        Returns:
            PlayerController instance
        """
        return cls.create(ControllerType.PLAYER, game_logic)
    
    @classmethod
    def create_solver(cls, game_logic: GameLogic, solver: BaseSolver,
                     move_delay: float = 0.2, 
                     visualize: bool = True) -> SolverController:
        """Create a solver controller (convenience method).
        
        Args:
            game_logic: Game logic instance
            solver: Solver algorithm instance
            move_delay: Delay between moves in seconds
            visualize: Whether to render the solving process
            
        Returns:
            SolverController instance
        """
        return cls.create(
            ControllerType.SOLVER, 
            game_logic, 
            solver=solver,
            move_delay=move_delay,
            visualize=visualize
        )
        
    @classmethod
    def create_rl(  cls,
                    game_logic: GameLogic,
                    agent: BaseAgent,
                    move_delay: float = 0.05,
                    max_steps_per_episode: int = 500) -> RLController:
        
        """Create a reinforcement learning controller.
            Args:
                game_logic: Game logic instance
                agent: Reinforcement learning agent
                move_delay: Delay between moves in seconds
                max_steps_per_episode: Maximum steps per episode
        """
        
        return cls.create(ControllerType.RL,
                          game_logic=game_logic,
                          agent = agent,
                          move_delay=move_delay, 
                          max_steps_per_episode=max_steps_per_episode)