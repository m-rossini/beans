from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from beans.world import World
from config.loader import BeansConfig, WorldConfig

if TYPE_CHECKING:
    from rendering.window import WorldWindow

logger = logging.getLogger(__name__)


class SimulationReport(ABC):
    @abstractmethod
    def generate(
        self,
        world_config: WorldConfig,
        beans_config: BeansConfig,
        world: World,
        window: "WorldWindow",
    ) -> None: ...


class ConsoleSimulationReport(SimulationReport):
    def __init__(self) -> None:
        self._logger = logger

    def generate(
        self,
        world_config: WorldConfig,
        beans_config: BeansConfig,
        world: World,
        window: "WorldWindow",
    ) -> None:
        report_lines = [
            "Simulation Report:",
            f"  Rounds completed: {world.round}",
            f"  Beans surviving: {len(world.beans)}",
            f"  Dead beans: {len(world.dead_beans)}",
            f"  Max age (years/months): {world.max_age_years}/{world.max_age_months}",
        ]
        for line in report_lines:
            print(line)
            self._logger.info(f">>>> {line}")
