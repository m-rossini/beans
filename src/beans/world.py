import logging
import random
from typing import List

from beans.dynamics.bean_dynamics import BeanDynamics
from config.loader import BeansConfig, WorldConfig, EnvironmentConfig
from beans.environment import Environment

from .bean import Bean, BeanState, Sex
from .context import BeanContext
from .energy_system import EnergySystem, create_energy_system_from_name
from .genetics import create_phenotype, create_random_genotype
from .placement import create_strategy_from_name
from .population import (
    PopulationEstimator,
    create_population_estimator_from_name,
)
from .survival import SurvivalManager, SurvivalResult

logger = logging.getLogger(__name__)

class World:
    def __init__(self, config: WorldConfig, beans_config: BeansConfig, environment: Environment | None = None) -> None:
        logger.debug(f">>>>> World.__init__: width={config.width}, height={config.height}, population_density={config.population_density}")
        self.world_config = config
        self.beans_config = beans_config
        # Environment is optional; if provided, World will delegate energy and
        # temperature queries and will call `step()` at the start of each tick.
        self.environment = environment
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
        self._rng = random.Random(self.world_config.seed) if self.world_config.seed is not None else None
        self.beans: List[Bean] = self._initialize()
        self.initial_beans: int = len(self.beans)
        self.bean_dynamics = BeanDynamics(beans_config)
        self.survival_manager = SurvivalManager(beans_config, rng=self._rng)
        self.survival_checker = self.survival_manager.checker
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
        # Run environment update at the start of each tick
        if self.environment is not None:
            self.environment.step()
        survivors: List[Bean] = []
        deaths_this_step = 0
        for bean in self.beans:
            _: BeanState = self._update_bean(bean)
            result = self.survival_manager.check_and_record(bean)
            if not result.alive:
                deaths_this_step += 1
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

    @property
    def dead_beans(self) -> List[SurvivalResult]:
        """Backwards compatible accessor for recorded dead beans."""
        return self.survival_manager.dead_beans

    def get_energy_intake(self) -> float:
        """Return the energy intake available from the world.

        Currently returns a hardcoded default value.
        TODO: Implement dynamic energy intake based on world state.
        """
        if self.environment is not None:
            return self.environment.get_energy_intake()

        # Fallback: return configured per-step intake from BeansConfig.
        return self.beans_config.energy_gain_per_step

    def get_temperature(self) -> float:
        """Return the current world temperature.

        Currently returns a hardcoded default value.
        TODO: Implement dynamic temperature based on world state.
        """
        if self.environment is not None:
            return self.environment.get_temperature()

        return 1.0
