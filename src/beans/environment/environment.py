from __future__ import annotations

from abc import ABC, abstractmethod

from beans.environment.food_manager import FoodManager
from config.loader import BeansConfig, EnvironmentConfig, WorldConfig


class Environment(ABC):
    """Abstract Environment interface.

    Minimal interface required by `World`. Implementations should provide
    `step()` which advances environment state, and query methods for energy
    intake and temperature.
    """

    @abstractmethod
    def step(self) -> None: ...

    @abstractmethod
    def get_temperature(self) -> float: ...

    @property
    @abstractmethod
    def food_manager(self) -> FoodManager: ...


class DefaultEnvironment(Environment):
    """Minimal default environment implementation.

    For now it is a lightweight placeholder: `step()` is a no-op, and
    query methods return conservative defaults derived from config.
    """

    def __init__(
        self,
        env_config: EnvironmentConfig,
        beans_config: BeansConfig,
        world_config: WorldConfig,
        food_manager: FoodManager,
    ) -> None:
        self._env_config = env_config
        self._beans_config = beans_config
        self._world_config = world_config
        self._food_manager = food_manager

    def step(self) -> None:
        self._food_manager.step()

        return self._beans_config.energy_gain_per_step

    def get_temperature(self) -> float:
        #TODO implement a climate model system
        pass

    @property
    def food_manager(self) -> FoodManager:
        return self._food_manager


def create_environment_from_name(
    world_config: WorldConfig,
    env_config: EnvironmentConfig,
    beans_config: BeansConfig,
    food_manager: FoodManager,
) -> Environment:
    """Instantiate an Environment implementation by name.

    Currently only "default" is supported. Raises ValueError for unknown names.
    """
    name = env_config.name.lower()
    if name == "default".lower():
        return DefaultEnvironment(env_config, beans_config, world_config, food_manager=food_manager)

    raise ValueError(f"Unknown environment implementation: {name}")
