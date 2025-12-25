import pytest

from src.beans.bean import Bean, Sex
from src.beans.environment.food_manager import FoodType, HybridFoodManager
from src.beans.genetics import create_phenotype, create_random_genotype
from src.config.loader import DEFAULT_BEANS_CONFIG, DEFAULT_ENVIRONMENT_CONFIG, DEFAULT_WORLD_CONFIG
from src.rendering.bean_sprite import BeanSprite
from src.rendering.movement import SpriteMovementSystem

# Integration test: movement system detects bean-food collision, world/subsystem applies energy

def make_bean_sprite(size=10.0, sex=Sex.MALE, id=1, x=5.0, y=5.0):
    beans_config = DEFAULT_BEANS_CONFIG
    genotype = create_random_genotype()
    phenotype = create_phenotype(beans_config, genotype)
    bean = Bean(beans_config, id, sex, genotype=genotype, phenotype=phenotype)
    state = bean.to_state()
    state.size = size
    state.target_size = size
    state.energy = 50.0
    bean.update_from_state(state)
    sprite = BeanSprite(bean=bean, position=(x, y), color=(0, 255, 0), direction=0.0)
    return sprite

