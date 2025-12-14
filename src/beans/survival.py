"""Survival system for beans.

Provides an extensible interface and a default implementation used by the
simulation's `World.step()` to decide whether a bean survives a tick.

This is a minimal implementation to satisfy current integration tests
and will be extended in later phases per the plan.
"""
import logging
from dataclasses import dataclass
from typing import Optional

from .bean import Bean


@dataclass
class SurvivalResult:
    alive: bool
    reason: Optional[str] = None
    message: Optional[str] = None


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
        # Age check (priority)
        if not bean.can_survive_age():
            # Use canonical reason used by existing Bean.survive() (tests expect this string)
            return SurvivalResult(alive=False, reason="max_age_reached", message="Age exceeded genetic max")

        # Starvation behavior
        if bean.energy <= 0:
            self.logger.debug(f">>>>> Survival.check: bean={bean.id}, energy={bean.energy}, size={bean.size}, min_size={self.config.min_bean_size}")
            # If at or below minimum healthy size, die of starvation
            if bean.size <= self.config.min_bean_size:
                # For compatibility with existing tests, report energy_depleted when
                # there is no fat left to sustain the bean.
                return SurvivalResult(alive=False, reason="energy_depleted", message="No fat left to sustain (energy depleted)")

            # Draw on fat: reduce size by a small amount; configurable in Phase 3
            depletion = 1.0  # conservative default; will be replaced by config later
            new_size = max(self.config.min_bean_size, bean.size - depletion)
            # Apply the change to the bean phenotype (mutating bean in-place)
            bean._phenotype.size = new_size
            # Normalize energy to zero (representing debt satisfied by fat)
            bean._phenotype.energy = 0.0
            return SurvivalResult(alive=True, reason=None, message=f"Drew {depletion} fat due to starvation; new_size={new_size}")

        return SurvivalResult(alive=True)
