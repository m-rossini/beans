import math
from typing import Dict, List, Tuple

import pytest

from src.beans.bean import Bean, Sex
from src.beans.genetics import create_phenotype, create_random_genotype
from src.config.loader import DEFAULT_BEANS_CONFIG
from src.rendering.bean_sprite import BeanSprite
from src.rendering.movement import SpriteMovementSystem

# Helper functions


def make_bean_and_sprite(
    size: float = 10.0,
    speed: float = 0.0,
    sex: Sex = Sex.MALE,
    beans_config=None,
    id: int = 1,
) -> Tuple[Bean, BeanSprite]:
    if beans_config is None:
        # Use default beans config for tests when no config provided
        beans_config = DEFAULT_BEANS_CONFIG

    genotype = create_random_genotype()
    phenotype = create_phenotype(beans_config, genotype)
    bean = Bean(beans_config, id, sex, genotype=genotype, phenotype=phenotype)
    # Set deterministic properties
    state = bean.to_state()
    state.size = size
    state.target_size = size
    state.energy = 100.0
    state.speed = speed
    bean.update_from_state(state)

    sprite = BeanSprite(bean, position=(0.0, 0.0), color=(255, 0, 0), direction=0.0)
    # Ensure sprite visual attributes match bean
    sprite.center_x = 0.0
    sprite.center_y = 0.0
    sprite.direction = 0.0
    return bean, sprite


def distance(a: BeanSprite, b: BeanSprite) -> float:
    return math.hypot(a.center_x - b.center_x, a.center_y - b.center_y)


@pytest.fixture
def movement_system() -> SpriteMovementSystem:
    return SpriteMovementSystem()


def run_frame_for_sprites(
    movement: SpriteMovementSystem,
    sprites: List[BeanSprite],
    width: int = 500,
    height: int = 500,
    delta_time: float = 1.0,
) -> Tuple[Dict[BeanSprite, Tuple[float, float]], Dict[int, float]]:
    class DummyFoodManager:
        def get_all_food(self):
            return {}
    food_manager = DummyFoodManager()
    # Collect targets from move_sprite
    targets = []
    for s in sprites:
        tx, ty, _ = movement.move_sprite(s, width, height)
        targets.append((s, tx, ty))

    food_items = food_manager.get_all_food()
    # resolve_collisions is part of the plan and should exist on SpriteMovementSystem
    # It returns (adjusted_targets, damage_report)
    adjusted, report, _ = movement.resolve_collisions(targets, width, height, food_items=food_items)

    # Apply visual updates
    for s in sprites:
        tx, ty = adjusted.get(s, (s.center_x, s.center_y))
        s.update_from_bean(delta_time, (tx, ty))

    return adjusted, report


def test_no_damage_below_area_threshold(movement_system):
    # Place two beans so their intersection area is just below 2 px
    b1, s1 = make_bean_and_sprite(size=10.0, speed=0.0, sex=Sex.MALE, id=1)
    b2, s2 = make_bean_and_sprite(size=10.0, speed=0.0, sex=Sex.MALE, id=2)

    # Position them with centers separated so tiny overlap (<2 px area). Use manual centers.
    # For two equal circles radius=5, place them very close so intersection area approx 1.9
    # This is a delicate geometric placement; we'll set distance slightly less than 10 but
    # large enough to make intersection small.
    s1.center_x, s1.center_y = 100.0, 100.0
    s2.center_x, s2.center_y = 109.9, 100.0  # 0.1 px overlap in x

    sprites = [s1, s2]
    adjusted, report = run_frame_for_sprites(movement_system, sprites)

    # Energies unchanged
    assert pytest.approx(100.0, rel=1e-6) == b1.to_state().energy
    assert pytest.approx(100.0, rel=1e-6) == b2.to_state().energy


def test_minimal_clash_causes_damage_and_nudge(movement_system):
    b1, s1 = make_bean_and_sprite(size=10.0, speed=1.0, sex=Sex.MALE, id=10)
    b2, s2 = make_bean_and_sprite(size=10.0, speed=1.0, sex=Sex.FEMALE, id=11)

    # Head-on: place facing each other
    s1.center_x, s1.center_y = 200.0, 200.0
    s1.direction = 0.0  # right
    s2.center_x, s2.center_y = 209.0, 200.0
    s2.direction = 180.0  # left

    sprites = [s1, s2]
    adjusted, report = run_frame_for_sprites(movement_system, sprites)

    # Some damage should be applied
    e1 = b1.to_state().energy
    e2 = b2.to_state().energy
    assert e1 < 100.0
    assert e2 < 100.0

    # Ensure sprites do not overlap after update (distance >= sum radii)
    r_sum = b1.size / 2.0 + b2.size / 2.0
    assert distance(s1, s2) >= (r_sum - 1e-3)


def test_speed_scaling_damage(movement_system):
    # Low speed scenario
    b1a, s1a = make_bean_and_sprite(size=8.0, speed=0.5, sex=Sex.MALE, id=20)
    b2a, s2a = make_bean_and_sprite(size=8.0, speed=0.5, sex=Sex.MALE, id=21)
    s1a.center_x, s1a.center_y = 50.0, 50.0
    s1a.direction = 0.0
    s2a.center_x, s2a.center_y = 57.0, 50.0
    s2a.direction = 180.0

    adj_a, rep_a = run_frame_for_sprites(movement_system, [s1a, s2a])
    total_damage_a = sum(rep_a.values())

    # High speed scenario
    b1b, s1b = make_bean_and_sprite(size=8.0, speed=3.0, sex=Sex.MALE, id=30)
    b2b, s2b = make_bean_and_sprite(size=8.0, speed=3.0, sex=Sex.MALE, id=31)
    s1b.center_x, s1b.center_y = 80.0, 80.0
    s1b.direction = 0.0
    s2b.center_x, s2b.center_y = 87.0, 80.0
    s2b.direction = 180.0

    adj_b, rep_b = run_frame_for_sprites(movement_system, [s1b, s2b])
    total_damage_b = sum(rep_b.values())

    assert total_damage_b > total_damage_a


def test_size_asymmetry_damage_split(movement_system):
    # Small vs large
    b_small, s_small = make_bean_and_sprite(size=6.0, speed=1.0, sex=Sex.MALE, id=40)
    b_large, s_large = make_bean_and_sprite(size=14.0, speed=1.0, sex=Sex.MALE, id=41)
    s_small.center_x, s_small.center_y = 300.0, 300.0
    s_small.direction = 0.0
    s_large.center_x, s_large.center_y = 307.0, 300.0
    s_large.direction = 180.0

    adj, rep = run_frame_for_sprites(movement_system, [s_small, s_large])

    # Damage split: small should take larger fraction
    d_small = rep.get(b_small.id, 0.0)
    d_large = rep.get(b_large.id, 0.0)
    assert d_small > d_large


def test_sex_multiplier_ladies_first_mapping(movement_system):
    # Ensure loader mapping uses ladies-first tuple (1.05, 1.0)
    beans_config = DEFAULT_BEANS_CONFIG
    beans_config.collision_damage_sex_factors = (1.05, 1.0)
    # map is expected to be created by loader; tests assume resolve_collisions uses the mapping

    b_male, s_male = make_bean_and_sprite(size=10.0, speed=1.0, sex=Sex.MALE, beans_config=beans_config, id=50)
    b_female, s_female = make_bean_and_sprite(size=10.0, speed=1.0, sex=Sex.FEMALE, beans_config=beans_config, id=51)

    s_male.center_x, s_male.center_y = 400.0, 400.0
    s_male.direction = 0.0
    s_female.center_x, s_female.center_y = 409.0, 400.0
    s_female.direction = 180.0

    adj, rep = run_frame_for_sprites(movement_system, [s_male, s_female])

    dmg_male = rep.get(b_male.id, 0.0)
    dmg_female = rep.get(b_female.id, 0.0)

    assert dmg_female >= dmg_male


def test_direction_change_avoids_future_overlap(movement_system):
    b1, s1 = make_bean_and_sprite(size=10.0, speed=2.0, sex=Sex.MALE, id=60)
    b2, s2 = make_bean_and_sprite(size=10.0, speed=2.0, sex=Sex.MALE, id=61)

    s1.center_x, s1.center_y = 10.0, 10.0
    s1.direction = 0.0
    s2.center_x, s2.center_y = 19.0, 10.0
    s2.direction = 180.0

    # Run two frames
    adj1, rep1 = run_frame_for_sprites(movement_system, [s1, s2])
    adj2, rep2 = run_frame_for_sprites(movement_system, [s1, s2])

    # After second update they should not overlap
    r_sum = b1.size / 2.0 + b2.size / 2.0
    assert distance(s1, s2) >= (r_sum - 1e-3)
