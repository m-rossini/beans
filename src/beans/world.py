from dataclasses import dataclass
from typing import List, Tuple
import logging
from .bean import Bean, Sex
from .placement import PlacementStrategy, create_strategy_from_name
from .population import (
    PopulationEstimator,
    create_population_estimator_from_name,
)
from config.loader import WorldConfig, BeansConfig

logger = logging.getLogger(__name__)


@dataclass
class DeadBeanRecord:
    bean: Bean
    reason: str


class World:
    def __init__(self, config: WorldConfig, beans_config: BeansConfig) -> None:
        logger.debug(f">>>>> World.__init__: width={config.width}, height={config.height}, population_density={config.population_density}")
        self.world_config = config
        self.beans_config = beans_config
        self.width = config.width
        self.height = config.height
        self.sprite_size = beans_config.initial_bean_size
        self.population_density = config.population_density
        self.male_female_ratio = config.male_female_ratio
        self.placement_strategy = create_strategy_from_name(self.world_config.placement_strategy)
        self.population_estimator: PopulationEstimator = create_population_estimator_from_name(self.world_config.population_estimator)
        self.beans: List[Bean] = self._initialize()
        self.dead_beans: List[DeadBeanRecord] = []
        logger.info(f"World initialized with {len(self.beans)} beans")

    def _initialize(self) -> List[Bean]:
        male_count, female_count = self.population_estimator.estimate(
            width=self.width,
            height=self.height,
            sprite_size=self.sprite_size,
            population_density=self.population_density,
            male_female_ratio=self.male_female_ratio,
        )
        bean_count = male_count + female_count
        logger.info(f">>>>> World._initialize: calculated population. male_count={male_count}, female_count={female_count}")
        return [
            Bean(config=self.beans_config, id=i, sex=Sex.MALE if i < male_count else Sex.FEMALE)
            for i in range(bean_count)
        ]

    def step(self, dt: float) -> None:
        logger.debug(f">>>>> World.step: dt={dt}, beans_count={len(self.beans)}")
        survivors: List[Bean] = []
        deaths_this_step = 0
        for bean in self.beans:
            result = bean.update(dt)
            energy_after_update = result["energy"]
            if energy_after_update <= 0:
                self._mark_dead(bean, reason="energy_depleted")
                deaths_this_step += 1
            else:
                survivors.append(bean)
        self.beans = survivors
        if deaths_this_step > 0:
            logger.debug(f"World.step: {deaths_this_step} beans died, {len(survivors)} survived")

    def _mark_dead(self, bean: Bean, reason: str) -> None:
        logger.debug(f">>>>> Bean {bean.id} marked dead: reason={reason}, age={bean.age}, energy={bean.energy:.2f}")
        self.dead_beans.append(DeadBeanRecord(bean=bean, reason=reason))
