import logging
import random
from dataclasses import dataclass
from typing import List

from beans.dynamics.bean_dynamics import BeanDynamics
from beans.environment.environment import EnvironmentState, create_environment_from_name
from beans.environment.food_manager import FoodManager, create_food_manager_from_name
from config.loader import BeansConfig, EnvironmentConfig, WorldConfig

from .bean import Bean, BeanContext, BeanState, Sex
from .energy_system import EnergySystem, create_energy_system_from_name
from .genetics import create_phenotype, create_random_genotype, extract_phenotype_values
from .placement import create_strategy_from_name
from .population import (
    PopulationEstimator,
    create_population_estimator_from_name,
)
from .survival import SurvivalManager, SurvivalResult

logger = logging.getLogger(__name__)

# Holds the state of the world after a simulation step
@dataclass
class WorldState:
    alive_beans: List[Bean]
    dead_beans: List[Bean]
    current_round: int = 0
    environment_state: EnvironmentState = None

class World:
    def __init__(
        self,
        config: WorldConfig,
        beans_config: BeansConfig,
        env_config: EnvironmentConfig,
    ) -> None:
        logger.debug(
            ">>>>> World.__init__: width=%d, height=%d, population_density=%0.2f",
            config.width,
            config.height,
            config.population_density,
        )
        self.world_config = config
        self.beans_config = beans_config
        self.env_config = env_config
        self.width = config.width
        self.height = config.height
        self.sprite_size = beans_config.initial_bean_size
        self.population_density = config.population_density
        self.male_female_ratio = config.male_female_ratio
        self.max_age_rounds = config.max_age_years * config.rounds_per_year
        self.placement_strategy = create_strategy_from_name(self.world_config.placement_strategy)
        self.population_estimator: PopulationEstimator = create_population_estimator_from_name(self.world_config.population_estimator)
        self.energy_system: EnergySystem = create_energy_system_from_name(self.world_config.energy_system, beans_config)
        self.food_manager: FoodManager = create_food_manager_from_name(self.env_config, self.world_config)
        self.environment = create_environment_from_name(self.world_config,
                                                        self.env_config,
                                                        self.beans_config,
                                                        self.food_manager)
        self.environment_state: EnvironmentState = None
        self._rng = random.Random(self.world_config.seed) if self.world_config.seed is not None else random.Random()
        self.beans: List[Bean] = self._initialize()
        self.initial_beans: int = len(self.beans)
        self.round: int = 1
        # Persistent WorldState instance
        self.state = WorldState(alive_beans=self.beans.copy(), dead_beans=[], current_round=self.round)
        self.bean_dynamics = BeanDynamics(beans_config)
        self.survival_manager = SurvivalManager(beans_config, rng=self._rng)
        self.survival_checker = self.survival_manager.checker
        logger.info(">>>> World initialized with %d beans",len(self.beans),)

    def _initialize(self) -> List[Bean]:
        male_count, female_count = self.population_estimator.estimate(
            width=self.width,
            height=self.height,
            sprite_size=self.sprite_size,
            population_density=self.population_density,
            male_female_ratio=self.male_female_ratio,
        )
        bean_count = male_count + female_count
        logger.info(">>>> World._initialize: calculated population. male_count=%d, female_count=%d",
            male_count,
            female_count,
        )
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


    def step(self, dt: float) -> WorldState:
        logger.debug(f">>>>> World.step: dt={dt}, beans_count={len(self.beans)}, dead_beans_count={len(self.dead_beans)}, round={self.round}")
        self.environment_state = self.environment.step()
        survivors: List[Bean] = []
        dead_this_step: List[Bean] = []
        for bean in self.beans:
            _: BeanState = self._update_bean(bean)
            result = self.survival_manager.check_and_record(bean)
            if not result.alive:
                logger.debug(
                    ">>>>> World.step.dead_bean: Bean %s died: reason=%s, sex=%s, max_age=%0.2f",
                    bean.id,
                    result.reason,
                    bean.sex.value,
                    bean._max_age,
                )
                logger.debug(
                    "phenotype=%s, genotype=%s",
                    extract_phenotype_values(bean._phenotype),
                    bean.genotype.to_compact_str(),
                )
                dead_this_step.append(bean)
            else:
                survivors.append(bean)

        self.beans = survivors
        self.round += 1
        # Update persistent WorldState instance
        self.state.alive_beans = survivors.copy()
        self.state.dead_beans = dead_this_step.copy()
        self.state.current_round = self.round
        self.state.environment_state = self.environment_state

        for bean in self.beans:
            logger.debug(
                ">>>>> World.step [state]. Beans State:"
                f" Bean {bean.id} "
                f" alive={bean.alive}"
                f" sex={bean.sex.value}"
                f" age={bean.age:.2f}"
                f" energy={bean.energy:.2f}"
                f" size={bean.size:.2f}"
                f" target_size={bean._phenotype.target_size:.2f}"
                f" speed={bean.speed:.2f}"
                f" genotype={bean.genotype.to_compact_str()}"
            )
        logger.debug(f">>>>> World.step: [state]. FoodManagerState: "
                    f"food_items_count={self.environment_state.food_manager_state.total_food_count} "
                    f"total_food_energy={self.environment_state.food_manager_state.total_food_energy} "
        )
        logger.debug(f">>>>> World.step: [state]. EnvironmentState: "
                     f"food manager present={self.environment_state.food_manager_state is not None} "
        )
        logger.debug(f">>>>> World.step: [state]. WorldState: "
                     f"alive_beans={len(self.state.alive_beans)} "
                     f"dead_beans={len(self.state.dead_beans)} "
                     f"current_round={self.state.current_round}"
        )

        return self.state

    def _update_bean(self, bean: Bean) -> BeanState:
        bean_state = self.energy_system.apply_energy_system(bean)

        speed = self.bean_dynamics.calculate_speed(bean_state, bean.genotype, bean._max_age)
        bean_state.store(speed=speed)

        age = bean.age_bean()
        bean_state.store(age=age)

        return bean.update_from_state(bean_state)

    @property
    def dead_beans(self) -> List[SurvivalResult]:
        """Backwards compatible accessor for recorded dead beans."""
        return self.survival_manager.dead_beans
