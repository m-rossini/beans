"""Survival system for beans.

Provides an extensible interface and a default implementation used by the
simulation's `World.step()` to decide whether a bean survives a tick.

This is a minimal implementation to satisfy current integration tests
and will be extended in later phases per the plan.
"""

import logging
import random
from dataclasses import dataclass
from typing import List, Optional

from config.loader import BeansConfig

from .bean import Bean


@dataclass
class SurvivalResult:
    alive: bool
    reason: Optional[str] = None
    message: Optional[str] = None
    bean: Optional[Bean] = None


class SurvivalChecker:
    """Interface for survival checkers."""

    def check(self, bean: Bean, world) -> SurvivalResult:
        raise NotImplementedError()

    def handle_event(self, bean: Bean, event) -> None:
        """Hook for external events (no-op default)."""
        return None


class DefaultSurvivalChecker(SurvivalChecker):
    """Default survival rules (minimal).

    - Age death (priority)
    - Starvation: if energy <= 0 and size <= min_size => STARVATION death
    - If energy <= 0 but still has fat, consume a small amount of size
      (represents drawing on fat) and survive the tick.
    """

    def __init__(self, config, rng=None) -> None:
        self.config = config
        self.rng = rng
        self.logger = logging.getLogger(__name__)

    def check(self, bean: Bean) -> SurvivalResult:
        config: BeansConfig = self.config

        if bean.age >= bean._max_age:
            return SurvivalResult(
                alive=False,
                reason="max_age_reached",
                message="Age exceeded genetic max",
            )

        if bean.energy <= 0:
            self.logger.debug(
                f">>>>> Survival.check: bean={bean.id}, energy={bean.energy}, size={bean.size}, min_size={config.min_bean_size}"
            )
            if bean.size <= config.min_bean_size:
                return SurvivalResult(
                    alive=False,
                    reason="energy_depleted",
                    message="No fat left to sustain (energy depleted)",
                )

            base = config.starvation_base_depletion
            mult = config.starvation_depletion_multiplier
            depletion = base * mult
            new_size = max(config.min_bean_size, bean.size - depletion)
            bean._phenotype.size = new_size
            bean._phenotype.energy = 0.0
            return SurvivalResult(
                alive=True,
                reason=None,
                message=f"Drew {depletion} fat due to starvation; new_size={new_size}",
            )

        if config.enable_obesity_death:
            threshold = config.max_bean_size * config.obesity_threshold_factor
            if bean.size >= threshold:
                rng = self.rng or random
                prob = config.obesity_death_probability
                self.logger.debug(
                    f">>>>> Survival.check: obesity check bean={bean.id}, size={bean.size}, threshold={threshold}, prob={prob}"
                )
                if rng.random() < prob:
                    return SurvivalResult(
                        alive=False,
                        reason="obesity",
                        message="Probabilistic obesity death",
                    )

        return SurvivalResult(alive=True)


class SurvivalManager:
    """Manager that encapsulates a SurvivalChecker and records dead beans.

    This keeps death bookkeeping inside the survival subsystem instead of
    scattering it in `World.step()`.
    """

    def __init__(
        self, config: BeansConfig, rng: Optional[random.Random] = None
    ) -> None:
        self.config: BeansConfig = config
        self.rng: Optional[random.Random] = rng
        self.logger = logging.getLogger(__name__)
        self.checker = DefaultSurvivalChecker(config, rng=self.rng)
        self.dead_beans: List[SurvivalResult] = []

    def check_and_record(self, bean: Bean) -> SurvivalResult:
        result = self.checker.check(bean)
        if not result.alive:
            bean.die()

            result.bean = bean
            self.dead_beans.append(result)
            self.logger.debug(
                f">>>>> SurvivalManager: bean {bean.id} died: reason={result.reason}"
            )

        return result
