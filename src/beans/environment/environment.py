from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from config.loader import BeansConfig, EnvironmentConfig


class Environment(ABC):
    """Abstract Environment interface.

    Minimal interface required by `World`. Implementations should provide
    `step()` which advances environment state, and query methods for energy
    intake and temperature.
    """

    @abstractmethod
    def step(self) -> None:
        ...

    @abstractmethod
    def get_energy_intake(self) -> float:
        ...

    @abstractmethod
    def get_temperature(self) -> float:
        ...



class DefaultEnvironment(Environment):
    """Minimal default environment implementation.

    For now it is a lightweight placeholder: `step()` is a no-op, and
    query methods return conservative defaults derived from config.
    """

    def __init__(self, env_config: EnvironmentConfig, beans_config: Optional[BeansConfig] = None) -> None:
        self._env_config = env_config
        self._beans_config = beans_config

    def step(self) -> None:
        # no-op for fundamental skeleton
        return None

    def get_energy_intake(self) -> float:
        # Default to beans config setting if available, otherwise 1.0
        if self._beans_config is not None:
            return self._beans_config.energy_gain_per_step
        return 1.0

    def get_temperature(self) -> float:
        # Provide a reasonable default in range [temp_min, temp_max]
        try:
            # Use midpoint of configured range
            return (self._env_config.temp_min + self._env_config.temp_max) / 2.0
        except Exception:
            return 1.0

def create_environment_from_name(name: str, env_config: EnvironmentConfig, beans_config: BeansConfig) -> Environment:
    """Instantiate an Environment implementation by name.

    Currently only "default" is supported. Raises ValueError for unknown names.
    """
    name = name or "default"
    if name == "default":
        return DefaultEnvironment(env_config, beans_config)

    raise ValueError(f"Unknown environment implementation: {name}")