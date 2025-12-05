from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import numpy as np
import random
from collections import deque


class BaseAgent(ABC):
    """Base class for RL agents."""
    
    def __init__(self, name: str, state_shape: Tuple[int, ...], num_actions: int):
        """
        Initialize RL agent.
        
        Args:
            name: Agent name
            state_shape: Shape of state observation
            num_actions: Number of possible actions (4 for this game)
        """
        self.name = name
        self.state_shape = state_shape
        self.num_actions = num_actions
    
    @abstractmethod
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Select action given current state.
        
        Args:
            state: Current state observation
            training: If True, may explore; if False, exploit only
            
        Returns:
            Action index (0-3)
        """
        pass
    
    @abstractmethod
    def learn(
        self, 
        state: np.ndarray, 
        action: int, 
        reward: float, 
        next_state: np.ndarray, 
        done: bool
    ) -> None:
        """
        Learn from transition.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode ended
        """
        pass
    
    @abstractmethod
    def save(self, filepath: str) -> None:
        """Save agent to file."""
        pass
    
    @abstractmethod
    def load(self, filepath: str) -> None:
        """Load agent from file."""
        pass