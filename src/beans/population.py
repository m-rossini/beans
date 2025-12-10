from __future__ import annotations

import logging
import math
from abc import ABC, abstractmethod
from typing import Tuple

logger = logging.getLogger(__name__)


class PopulationEstimator(ABC):
    @abstractmethod
    def estimate(
        self,
        width: int,
        height: int,
        sprite_size: int,
        population_density: float,
        male_female_ratio: float,
    ) -> Tuple[int, int]:
        raise NotImplementedError()


class DensityPopulationEstimator(PopulationEstimator):
    """Default estimator that bases counts on area density and sex ratio."""

    def estimate(
        self,
        width: int,
        height: int,
        sprite_size: int,
        population_density: float,
        male_female_ratio: float,
    ) -> Tuple[int, int]:
        area = width * height
        per_bean_area = max(1, sprite_size ** 2)
        total = int(area * population_density / per_bean_area)
        male_fraction = male_female_ratio / (1 + male_female_ratio)
        male = int(total * male_fraction)
        female = total - male
        logger.info(f">>>> DensityPopulationEstimator: total={total}, male={male}, female={female} for width={width}, height={height}, sprite_size={sprite_size}, population_density={population_density}, male_female_ratio={male_female_ratio}")
        return male, female


class SoftLogPopulationEstimator(PopulationEstimator):
    """Logs the density-based total and caps at that maximum."""

    def estimate(
        self,
        width: int,
        height: int,
        sprite_size: int,
        population_density: float,
        male_female_ratio: float,
    ) -> Tuple[int, int]:
        area = width * height
        per_bean_area = max(1, sprite_size ** 2)
        raw_total = area * population_density / per_bean_area
        capped_total = int(raw_total)
        if capped_total <= 0:
            logger.info(">>>> SoftLogPopulationEstimator: capped_total <= 0, returning 0, 0")
            return 0, 0

        log_value = math.log1p(raw_total)
        log_max = math.log1p(capped_total)
        scale = log_value / log_max if log_max > 0 else 0.0
        soft_total = min(capped_total, max(1, math.ceil(scale * capped_total)))

        male_fraction = male_female_ratio / (1 + male_female_ratio)
        male = int(soft_total * male_fraction)
        female = soft_total - male
        logger.info(f">>>> SoftLogPopulationEstimator: raw_total={raw_total:.2f}, soft_total={soft_total}, male={male}, female={female} for width={width}, height={height}, sprite_size={sprite_size}, population_density={population_density}, male_female_ratio={male_female_ratio}")

        return male, female


def create_population_estimator_from_name(name: str) -> PopulationEstimator:
    logger.info(f">>>> create_population_estimator_from_name: name={name}")
    match name.lower() if name else "":
        case "density" | "default":
            logger.debug(">>>>> Creating DensityPopulationEstimator")
            return DensityPopulationEstimator()
        case "soft_log" | "softlog" | "soft-log":
            logger.debug(">>>>> Creating SoftLogPopulationEstimator")
            return SoftLogPopulationEstimator()
        case _:
            logger.debug(f">>>>> Unknown estimator '{name}', defaulting to DensityPopulationEstimator")
            return DensityPopulationEstimator()

