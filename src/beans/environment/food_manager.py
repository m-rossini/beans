
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, Set, Tuple

from config.loader import EnvironmentConfig, WorldConfig


class FoodType(Enum):
    COMMON = auto()
    DEAD_BEAN = auto()

class FoodManager(ABC):
    def __init__(self, world_config: WorldConfig, env_config: EnvironmentConfig) -> None:
        self.world_config = world_config
        self.env_config = env_config
    @abstractmethod
    def spawn_food(self, occupied_positions: Set[Tuple[int, int]]) -> None:
        pass

    @abstractmethod
    def step(self) -> None:
        pass

    @abstractmethod
    def add_dead_bean_as_food(self, position: Tuple[int, int], size: float) -> None:
        pass

    @abstractmethod
    def get_food_at(self, position: Tuple[int, int]) -> Dict[FoodType, float]:
        pass

class HybridFoodManager(FoodManager):
    def __init__(self, world_config: WorldConfig, env_config: EnvironmentConfig) -> None:
        super().__init__(world_config, env_config)
        self.grid: Dict[Tuple[int, int], float] = {}
        self.dead_beans: Dict[Tuple[int, int], Dict[str, float]] = {}

    def spawn_food(self, occupied_positions: Set[Tuple[int, int]]) -> None:
        # Implementation will be added in the next phase
        pass

    def step(self) -> None:
        # Decay grid food by 10% of original value per tick
        for pos in list(self.grid.keys()):
            self.grid[pos] *= 0.9
            if self.grid[pos] < 1e-6:
                del self.grid[pos]
        # Decay dead bean food: 50% per round, remove after 3 rounds
        to_remove = []
        for pos, info in self.dead_beans.items():
            info["value"] *= 0.5
            info["rounds"] += 1
            if info["rounds"] >= 3 or info['value'] < 1e-6:
                to_remove.append(pos)
        for pos in to_remove:
            del self.dead_beans[pos]

    def add_dead_bean_as_food(self, position: Tuple[int, int], size: float) -> None:
        self.dead_beans[position] = {'value': size, 'rounds': 0}

    def get_food_at(self, position: Tuple[int, int]) -> Dict[FoodType, float]:
        result: Dict[FoodType, float] = {}
        # Grid food
        if position in self.grid:
            result[FoodType.COMMON] = self.grid[position]
        # Dead bean food
        if position in self.dead_beans:
            result[FoodType.DEAD_BEAN] = self.dead_beans[position]['value']
        return result

def create_food_manager_from_name(env_config: WorldConfig, world_config: WorldConfig) -> FoodManager:
    name = env_config.food_manager.lower()
    if name == "hybrid":
        return HybridFoodManager(world_config, env_config)
    else:
        raise ValueError(f"Unknown food manager type: {name}")