from __future__ import annotations

from abc import ABC, abstractmethod


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


__all__ = ["Environment"]
