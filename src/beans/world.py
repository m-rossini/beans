import logging
import random
from dataclasses import dataclass
from typing import List

from beans.dynamics.bean_dynamics import BeanDynamics
from config.loader import BeansConfig, WorldConfig

from .bean import Bean, BeanState, Sex
from .context import BeanContext
from .energy_system import EnergySystem, create_energy_system_from_name
from .genetics import create_phenotype, create_random_genotype
from .survival import DefaultSurvivalChecker
from .placement import create_strategy_from_name
from .population import (
    PopulationEstimator,
    create_population_estimator_from_name,
)

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
        self.max_age_years = config.max_age_years
        self.rounds_per_year = config.rounds_per_year
        self.max_age_rounds = self.max_age_years * self.rounds_per_year
        self.placement_strategy = create_strategy_from_name(self.world_config.placement_strategy)
        self.population_estimator: PopulationEstimator = create_population_estimator_from_name(self.world_config.population_estimator)
        self.energy_system: EnergySystem = create_energy_system_from_name(self.world_config.energy_system, beans_config)
        # Create a private RNG seeded from world config if seed provided
        self._rng = random.Random(self.world_config.seed) if self.world_config.seed is not None else None
        self.beans: List[Bean] = self._initialize()
        self.initial_beans: int = len(self.beans)
        # Single BeanDynamics instance per world; per-bean genotype and max_age
        # are supplied at calculation time to avoid constructing one per bean.
        self.bean_dynamics = BeanDynamics(beans_config)
        # Survival checker (configured at world init)
        self.survival_checker = DefaultSurvivalChecker(beans_config, rng=self._rng)
        self.dead_beans: List[DeadBeanRecord] = []
        self.round: int = 1
        logger.info(f">>>> World initialized with {len(self.beans)} beans")

    def _initialize(self) -> List[Bean]:
        male_count, female_count = self.population_estimator.estimate(
            width=self.width,
            height=self.height,
            sprite_size=self.sprite_size,
            population_density=self.population_density,
            male_female_ratio=self.male_female_ratio,
        )
        bean_count = male_count + female_count
        logger.info(f">>>> World._initialize: calculated population. male_count={male_count}, female_count={female_count}")
        # Build the bean creation context (contains counts and RNG)
        ctx = BeanContext(bean_count=bean_count, male_count=male_count, rng=self._rng)
        beans = self._create_beans(self.beans_config, ctx)

        return beans

    def _create_beans(self, beans_config: BeansConfig, bean_context: BeanContext) -> List[Bean]:
        beans = []
        for i in range(bean_context.bean_count):
            genotype = create_random_genotype(rng=bean_context.rng)
            phenotype = create_phenotype(beans_config, genotype, rng=bean_context.rng)
            bean = Bean(
                config=beans_config,
                id=i,
                sex=Sex.MALE if i < bean_context.male_count else Sex.FEMALE,
                genotype=genotype,
                phenotype=phenotype,
            )
            beans.append(bean)
        return beans

    def step(self, dt: float) -> None:
        logger.debug(f">>>>> World.step: dt={dt}, beans_count={len(self.beans)}, dead_beans_count={len(self.dead_beans)}, round={self.round}")
        survivors: List[Bean] = []
        deaths_this_step = 0
        for bean in self.beans:
            _: BeanState = self._update_bean(bean)

            # Log phenotype before survival check for easier debugging
            logger.info(f">>>>> World.step.pre_survival: Bean {bean.id} phenotype={bean._phenotype.to_dict()}")
            # Use the survival checker (integration point) to decide if the bean lives
            result = self.survival_checker.check(bean, self)
            if not result.alive:
                #TODO move _mark_dead to SurvivalChecker
                #TODO Keep th elis tof dead beans in the SurvivalChecker
                self._mark_dead(bean, reason=result.reason)
                deaths_this_step += 1
                # Use result.reason in the debug message
                logger.debug(f">>>>> World.step.dead_bean: Bean {bean.id} died: reason={result.reason}, sex={bean.sex.value},max_age={bean._max_age:.2f}, phenotype: {bean._phenotype.to_dict()}, genotype: {bean.genotype.to_compact_str()}" )
            else:
                survivors.append(bean)

        self.beans = survivors
        if deaths_this_step > 0:
            logger.debug(f">>>>> World.step.dead_beans: {deaths_this_step} beans died, {len(survivors)} survived")

        self.round += 1

    def _update_bean(self, bean: Bean) -> BeanState:
        bean_state = self.energy_system.apply_energy_system(bean, self.get_energy_intake())

        speed = self.bean_dynamics.calculate_speed(bean_state, bean.genotype, bean._max_age)
        bean_state.store(speed=speed)

        age = bean.age_bean()
        bean_state.store(age=age)

        return bean.update_from_state(bean_state)

    def _mark_dead(self, bean: Bean, reason: str) -> None:
        logger.debug(f">>>>> Bean {bean.id} marked dead: reason={reason}, age={bean.age}, energy={bean.energy:.2f}")
        self.dead_beans.append(DeadBeanRecord(bean=bean, reason=reason))

    def get_energy_intake(self) -> float:
        """Return the energy intake available from the world.

        Currently returns a hardcoded default value.
        TODO: Implement dynamic energy intake based on world state.
        """
        # Return configured per-step intake from BeansConfig. Fail fast if
        # the config object lacks the attribute to surface misconfiguration.
        return self.beans_config.energy_gain_per_step

    def get_temperature(self) -> float:
        """Return the current world temperature.

        Currently returns a hardcoded default value.
        TODO: Implement dynamic temperature based on world state.
        """
        return 1.0
