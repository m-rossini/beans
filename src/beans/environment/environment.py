from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from beans.environment.food_manager import FoodManager, FoodManagerState
from config.loader import BeansConfig, EnvironmentConfig, WorldConfig


@dataclass
class EnvironmentState:
    food_manager_state: FoodManagerState

class Environment(ABC):
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
        self._environment_state: EnvironmentState = EnvironmentState(food_manager_state=None)

    @abstractmethod
    def step(self) -> EnvironmentState: ...

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
        super().__init__(env_config, beans_config, world_config, food_manager)

    def step(self) -> EnvironmentState:
        self._food_manager_state = self._food_manager.step()
        self._environment_state.food_manager_state = self._food_manager_state
        return self._environment_state

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
