from dataclasses import dataclass
from typing import List, Tuple
from .bean import Bean, Sex
from .placement import PlacementStrategy, create_strategy_from_name
from .population import (
    PopulationEstimator,
    create_population_estimator_from_name,
)
from config.loader import WorldConfig, BeansConfig


@dataclass
class DeadBeanRecord:
    bean: Bean
    reason: str


class World:
    def __init__(self, config: WorldConfig, beans_config: BeansConfig) -> None:
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

    def _initialize(self) -> List[Bean]:
        male_count, female_count = self.population_estimator.estimate(
            width=self.width,
            height=self.height,
            sprite_size=self.sprite_size,
            population_density=self.population_density,
            male_female_ratio=self.male_female_ratio,
        )
        bean_count = male_count + female_count
        return [
            Bean(config=self.beans_config, id=i, sex=Sex.MALE if i < male_count else Sex.FEMALE)
            for i in range(bean_count)
        ]

    def step(self, dt: float) -> None:
        survivors: List[Bean] = []
        for bean in self.beans:
            result = bean.update(dt)
            energy_after_update = result["energy"]
            if energy_after_update <= 0:
                self._mark_dead(bean, reason="energy_depleted")
            else:
                survivors.append(bean)
        self.beans = survivors

    def _mark_dead(self, bean: Bean, reason: str) -> None:
        self.dead_beans.append(DeadBeanRecord(bean=bean, reason=reason))
