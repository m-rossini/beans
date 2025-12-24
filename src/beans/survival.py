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

    def __init__(self, config, rng) -> None:
        self.config = config
        self.rng = rng
        self.logger = logging.getLogger(__name__)

    def check(self, bean: Bean) -> SurvivalResult:
        config: BeansConfig = self.config
        self.logger.debug(f">>>>> Survival.check: "
                          f" Bean {bean.id}"
                          f" age={bean.age}"
                          f" energy={bean.energy}"
                          f" size={bean.size}"
                          f" min_size={config.min_bean_size}"
                          )

        # Priority order: age, starvation, obesity
        result = (
            self._check_age_death(bean) or
            self._check_starvation(bean) or
            self._check_obesity(bean)
        )
        if result is not None:
            return result
        return SurvivalResult(alive=True)

    def _check_age_death(self, bean: Bean) -> Optional[SurvivalResult]:
        if bean.age >= bean._max_age:
            return SurvivalResult(
                alive=False,
                reason="max_age_reached",
                message="Age exceeded genetic max",
            )
        return None

    def _check_starvation(self, bean: Bean) -> Optional[SurvivalResult]:
        config: BeansConfig = self.config
        if bean.energy <= 0:
            self.logger.debug(f">>>>> Survival.check: Bean {bean.id}, energy={bean.energy}, size={bean.size}, min_size={config.min_bean_size}")
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
        return None

    def _check_obesity(self, bean: Bean) -> Optional[SurvivalResult]:
        config: BeansConfig = self.config
        threshold = min(config.max_bean_size, config.initial_bean_size * config.obesity_threshold_factor)
        if bean.size >= threshold:
            min_size = config.min_bean_size
            max_size = config.max_bean_size
            base_prob = config.obesity_death_probability
            # Scale probability linearly with size
            prob = base_prob * (bean.size - min_size) / (max_size - min_size)
            prob = max(0.0, min(prob, base_prob))  # Clamp to [0, base_prob]
            rng_val = self.rng.random()
            self.logger.debug(f">>>>> Survival.check: obesity check Bean {bean.id}, "
                              f"size={bean.size}, "
                              f"threshold={threshold}, "
                              f"base_prob={base_prob}, "
                              f"prob={prob}, "
                              f"rng={rng_val}"
                              f"min_size={min_size}, "
                              f"max_size={max_size} "
                            )
            if rng_val < prob:
                return SurvivalResult(
                    alive=False,
                    reason="obesity",
                    message="Probabilistic obesity death",
                )
        return None


class SurvivalManager:
    """Manager that encapsulates a SurvivalChecker and records dead beans.

    This keeps death bookkeeping inside the survival subsystem instead of
    scattering it in `World.step()`.
    """

    def __init__(self, config: BeansConfig, rng: Optional[random.Random] = None) -> None:
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
            self.logger.debug(f">>>>> SurvivalManager::check_and_record: bean {bean.id} died: reason={result.reason}")

        return result
