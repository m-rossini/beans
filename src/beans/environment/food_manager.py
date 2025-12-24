import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Set, Tuple

from config.loader import EnvironmentConfig, WorldConfig

logger = logging.getLogger(__name__)

class FoodType(Enum):
    COMMON = auto()
    DEAD_BEAN = auto()

@dataclass
class FoodManagerState:
    total_food_energy: float = 0
    total_food_count: int = 0

class FoodManager(ABC):
    def __init__(self, world_config: WorldConfig, env_config: EnvironmentConfig) -> None:
        self.world_config = world_config
        self.env_config = env_config
        self.food_manager_state = FoodManagerState()

    @abstractmethod
    def _spawn_food(self, occupied_positions: Set[Tuple[int, int]]) -> None:
        pass

    @abstractmethod
    def step(self) -> FoodManagerState:
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
        # Each grid entry: { 'value': float, 'type': FoodType, 'rounds': int (for DEAD_BEAN) }
        self.grid: Dict[Tuple[int, int], dict] = {}
        self.total_food_energy: float = 0.0
        self._spawn_food(set())

    def consume_food_at_position(self, bean, position):
        """
        Transfers energy from food to bean at the given position, decreases food value accordingly.
        Food is not removed here, only during decay in step().
        Returns the amount of energy gained by the bean (float).
        """
        entry = self.grid.get(position)
        if not entry or entry['value'] <= 0:
            return 0.0
        energy_available = entry['value']
        gained = min(energy_available, self.env_config.food_quality)
        entry['value'] -= gained
        return gained

    def __init__(self, world_config: WorldConfig, env_config: EnvironmentConfig) -> None:
        super().__init__(world_config, env_config)
        # Each grid entry: { 'value': float, 'type': FoodType, 'rounds': int (for DEAD_BEAN) }
        self.grid: Dict[Tuple[int, int], dict] = {}
        self.total_food_energy: float = 0.0
        self._spawn_food(set())

    def _current_total_food_energy(self) -> float:
        """Return the current total food energy in the world (all types)."""
        return sum(entry['value'] for entry in self.grid.values())

    def _determine_food_spawn(self) -> tuple[int, float]:
        density = self.env_config.food_density
        energy_per_food = self.env_config.food_quality
        width = self.world_config.width
        height = self.world_config.height
        area = width * height
        max_total_energy = area * 0.05
        # Target total food energy for this round
        target_total_energy = min(area * density * energy_per_food, max_total_energy)
        # Calculate current total energy in grid (all food, including dead beans)
        current_total_energy = sum(entry['value'] for entry in self.grid.values())
        # Only spawn enough food to reach target
        energy_to_spawn = max(0.0, target_total_energy - current_total_energy)
        food_count = int(energy_to_spawn // energy_per_food)
        total_energy = food_count * energy_per_food
        logger.debug(f"Spawning {food_count} "
                    f"max_total_energy={max_total_energy} "
                    f"target_total_energy={target_total_energy} "
                    f"current_total_energy={current_total_energy} "
                    f"energy_to_spawn={energy_to_spawn} "
                    f"food_count={food_count} "
                    f"food items totaling={total_energy} "
                    f"energy_per_food={energy_per_food} "
                    f"density={density} "
                )
        return food_count, total_energy


    def _spawn_food(self, occupied_positions: Set[Tuple[int, int]]) -> None:
        max_count, max_energy = self._determine_food_spawn()
        current_energy = self._current_total_food_energy()
        allowed_energy = max(0.0, max_energy - current_energy)
        if allowed_energy <= 0:
            logger.debug(f">>>> HybridFoodManager::spawn_food: No food spawned, world at or above max food energy. "
                         f"max_energy={max_energy} "
                         f"current_energy={current_energy}"
                         f"Allowed_energy={allowed_energy} "
                         f"max_count={max_count}")
            return

        energy_per_food = self.env_config.food_quality
        food_count = int(allowed_energy // energy_per_food)
        if food_count <= 0:
            logger.debug(f">>>> HybridFoodManager::spawn_food: No food spawned, not enough room for a single food item. "
                         f"max_count={max_count} "
                         f"allowed_energy={allowed_energy} "
                         f"energy_per_food={energy_per_food} "
                         f"food_count={food_count}")
            return

        self.total_food_energy = food_count * energy_per_food
        distribution = self.env_config.food_spawn_distribution
        if distribution == "random":
            self._spawn_food_random(occupied_positions, food_count)
        elif distribution == "clustered":
            self._spawn_food_clustered(occupied_positions, food_count)
        else:
            raise ValueError(f"Unknown food spawn distribution: {distribution}")

        logger.debug(
            ">>>>> HybridFoodManager::_spawn_food: Food spawned:",
            f"food_pixels={len(self.grid)}",
            f"total_energy={self.total_food_energy}",
            f"occupied_positions={len(occupied_positions)}",
            f"food_count={food_count}"
        )

    def _spawn_food_random(self, occupied_positions: Set[Tuple[int, int]], num_to_spawn: int) -> None:
        width = self.world_config.width
        height = self.world_config.height
        energy_per_food = self.env_config.food_quality
        spawned = 0
        attempts = 0
        while spawned < num_to_spawn and attempts < num_to_spawn * 20:
            x = random.randint(0, width - 2)
            y = random.randint(0, height - 2)
            square = [(x + dx, y + dy) for dx in range(2) for dy in range(2)]
            # Check overlap with occupied or existing food
            if any(pos in occupied_positions or pos in self.grid for pos in square):
                attempts += 1
                continue
            for pos in square:
                self.grid[pos] = {'value': energy_per_food, 'type': FoodType.COMMON}
            spawned += 1
            attempts += 1

    def _spawn_food_clustered(self, occupied_positions: Set[Tuple[int, int]], num_to_spawn: int) -> None:
        width = self.world_config.width
        height = self.world_config.height
        energy_per_food = self.env_config.food_quality
        spawned = 0
        # Pick a random cluster center, but ensure 2x2 fits
        center_x = random.randint(0, width - 2)
        center_y = random.randint(0, height - 2)
        # Try to spawn all food within a 3x3 area around the center, each as a 2x2 square
        possible_origins = [
            (x, y)
            for x in range(max(0, center_x - 1), min(width - 1, center_x + 2))
            for y in range(max(0, center_y - 1), min(height - 1, center_y + 2))
        ]
        random.shuffle(possible_origins)
        for origin in possible_origins:
            if spawned >= num_to_spawn:
                break
            square = [(origin[0] + dx, origin[1] + dy) for dx in range(2) for dy in range(2)]
            if any(pos[0] >= width or pos[1] >= height or pos in occupied_positions or pos in self.grid for pos in square):
                continue
            for pos in square:
                self.grid[pos] = {'value': energy_per_food, 'type': FoodType.COMMON}
            spawned += 1

    def step(self) -> FoodManagerState:
        # Decay food by type
        to_remove = []
        for pos, entry in self.grid.items():
            if entry['type'] == FoodType.COMMON:
                entry['value'] *= 0.9
                if entry['value'] < 1e-6:
                    to_remove.append(pos)
            elif entry['type'] == FoodType.DEAD_BEAN:
                entry['value'] *= 0.5
                entry['rounds'] = entry.get('rounds', 0) + 1
                if entry['rounds'] >= 3 or entry['value'] < 1e-6:
                    to_remove.append(pos)
        for pos in to_remove:
            del self.grid[pos]
        # Spawn food after decay
        self._spawn_food(set())
        self.food_manager_state.total_food_energy = self._current_total_food_energy()
        self.food_manager_state.total_food_count = len(self.grid)
        return self.food_manager_state

    def add_dead_bean_as_food(self, position: Tuple[int, int], size: float) -> None:
        # Dead bean food is always added, ignoring the global food cap
        if position in self.grid and self.grid[position]['type'] == FoodType.DEAD_BEAN:
            self.grid[position]['value'] += size
            self.grid[position]['rounds'] = 0
            logger.debug(
                ">>>>> HybridFoodManager::add_dead_bean_as_food: Increased dead bean food:",
                f"position={position}",
                f"added_value={size}"
            )
        else:
            self.grid[position] = {'value': size, 'type': FoodType.DEAD_BEAN, 'rounds': 0}
            logger.debug(
                ">>>>> HybridFoodManager::add_dead_bean_as_food: Added dead bean food:",
                f"position={position}",
                f"value={size}"
            )

    def get_food_at(self, position: Tuple[int, int]) -> Dict[FoodType, float]:
        # Return a dict of food type to value at this position
        result: Dict[FoodType, float] = {}
        entry = self.grid.get(position)
        if entry:
            result[entry['type']] = entry['value']
        return result

def create_food_manager_from_name(env_config: WorldConfig, world_config: WorldConfig) -> FoodManager:
    name = env_config.food_manager.lower()
    if name == "hybrid":
        return HybridFoodManager(world_config, env_config)
    else:
        raise ValueError(f"Unknown food manager type: {name}")
