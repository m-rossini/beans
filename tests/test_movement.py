import math
import pytest
from beans.bean import Bean, Sex
from beans.genetics import Genotype, Phenotype, create_random_genotype
from config.loader import BeansConfig
from rendering.bean_sprite import BeanSprite
from rendering.movement import SpriteMovementSystem


@pytest.fixture
def beans_config():
    return BeansConfig(
        speed_min=1.0,
        speed_max=100.0,
        initial_energy=50.0,
        male_bean_color="blue",
        female_bean_color="red",
        max_age_rounds=100,
    )


@pytest.fixture
def sample_genotype():
    return create_random_genotype()


@pytest.fixture
def sample_phenotype(beans_config, sample_genotype):
    # create a simple Phenotype for testing
    return Phenotype(age=0.0, speed=10.0, energy=50.0, size=10.0, target_size=10.0)


@pytest.fixture
def bean(beans_config, sample_genotype, sample_phenotype):
    return Bean(config=beans_config, id=0, sex=Sex.MALE, genotype=sample_genotype, phenotype=sample_phenotype)


def test_move_right_by_speed(bean):
    sprite = BeanSprite(bean, (100.0, 100.0), (255, 0, 0))
    sprite.direction = 0.0
    sprite.center_x = 100.0
    sprite.center_y = 100.0
    bean._phenotype.speed = 10.0
    mover = SpriteMovementSystem()
    new_x, new_y, collisions = mover.move_sprite(sprite, 800, 600)
    assert collisions == 0
    assert new_x == 110.0


def test_negative_speed_reverses_motion(bean):
    sprite = BeanSprite(bean, (200.0, 200.0), (255, 0, 0))
    sprite.direction = 0.0
    sprite.center_x = 200.0
    sprite.center_y = 200.0
    bean._phenotype.speed = -10.0
    mover = SpriteMovementSystem()
    new_x, new_y, collisions = mover.move_sprite(sprite, 800, 600)
    assert collisions == 0
    assert new_x == 190.0


def test_horizontal_bounce_reflects_and_energy_loss(bean):
    sprite = BeanSprite(bean, (790.0, 300.0), (255, 0, 0))
    # Set direction right -> 0 deg, speed enough to cross edge
    sprite.direction = 0.0
    sprite.center_x = 790.0
    sprite.center_y = 300.0
    # set radius so it's near boundary; bean.size is 10 -> radius 5
    bean._phenotype.size = 10.0
    bean._phenotype.speed = 20.0
    initial_energy = bean.energy
    mover = SpriteMovementSystem()
    new_x, new_y, collisions = mover.move_sprite(sprite, 800, 600)
    # We expect a horizontal collision
    assert collisions >= 1
    # Direction should be reflected
    assert sprite.direction == 180.0
    # Energy deduction must happen via DTO; ensure energy was reduced accordingly
    assert bean.energy == initial_energy - collisions * bean.beans_config.energy_loss_on_bounce


def test_vertical_bounce_reflects_and_energy_loss(bean):
    sprite = BeanSprite(bean, (400.0, 595.0), (255, 0, 0))
    sprite.direction = 90.0
    sprite.center_x = 400.0
    sprite.center_y = 595.0
    bean._phenotype.size = 10.0
    bean._phenotype.speed = 20.0
    initial_energy = bean.energy
    mover = SpriteMovementSystem()
    new_x, new_y, collisions = mover.move_sprite(sprite, 800, 600)
    assert collisions >= 1
    assert sprite.direction == 270.0
    assert bean.energy == initial_energy - collisions * bean.beans_config.energy_loss_on_bounce


def test_corner_bounce_reflects_and_energy_loss(bean):
    sprite = BeanSprite(bean, (795.0, 595.0), (255, 0, 0))
    sprite.direction = 45.0
    sprite.center_x = 795.0
    sprite.center_y = 595.0
    bean._phenotype.size = 10.0
    bean._phenotype.speed = 20.0
    initial_energy = bean.energy
    mover = SpriteMovementSystem()
    new_x, new_y, collisions = mover.move_sprite(sprite, 800, 600)
    assert collisions >= 2
    assert sprite.direction == 225.0
    assert bean.energy == initial_energy - collisions * bean.beans_config.energy_loss_on_bounce


def test_visual_interpolation(bean):
    sprite = BeanSprite(bean, (100.0, 200.0), (255, 0, 0))
    sprite.direction = 0.0
    sprite.center_x = 100.0
    sprite.center_y = 200.0
    bean._phenotype.size = 10.0
    bean._phenotype.speed = 50.0
    mover = SpriteMovementSystem()

    # small dt -> partial interpolation
    sprite.update_from_bean(0.1, movement_system=mover, bounds=(800, 600))
    # computed lerp factor should be dt*6 = 0.6, expect center_x to move towards 150 but not fully
    assert 100.0 < sprite.center_x < 150.0

    # large dt -> full catch up (reset to initial center first)
    sprite.center_x = 100.0
    sprite.center_y = 200.0
    sprite.update_from_bean(1.0, movement_system=mover, bounds=(800, 600))
    assert pytest.approx(150.0, rel=1e-3) == sprite.center_x
