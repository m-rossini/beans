import pytest
import arcade
import logging
from beans.bean import Bean, Sex
from config.loader import BeansConfig
from rendering.bean_sprite import BeanSprite

logger = logging.getLogger(__name__)


class TestBeanSprite:
    @pytest.fixture
    def beans_config(self):
        return BeansConfig(
            max_bean_age=100,
            speed_min=10.0,
            speed_max=20.0,
            initial_energy=50.0,
            male_bean_color="blue",
            female_bean_color="red",
        )

    @pytest.fixture
    def male_bean(self, beans_config):
        return Bean(config=beans_config, id=1, sex=Sex.MALE)

    @pytest.fixture
    def female_bean(self, beans_config):
        return Bean(config=beans_config, id=2, sex=Sex.FEMALE)

    def test_sprite_creation_male(self, male_bean):
        position = (100.0, 200.0)
        color = arcade.color.BLUE
        sprite = BeanSprite(male_bean, position, color)
        assert sprite.center_x == position[0]
        assert sprite.center_y == position[1]
        assert sprite.bean == male_bean
        assert sprite.color == color
        assert sprite.diameter == male_bean.beans_config.initial_bean_size
        # Texture should be circle with diameter
        # Hard to test texture directly, but sprite exists

    def test_sprite_creation_female(self, female_bean):
        position = (150.0, 250.0)
        color = arcade.color.RED
        sprite = BeanSprite(female_bean, position, color)
        assert sprite.center_x == position[0]
        assert sprite.center_y == position[1]
        assert sprite.bean == female_bean
        assert sprite.color == color
        assert sprite.diameter == female_bean.beans_config.initial_bean_size

    def test_update_from_bean(self, male_bean):
        position = (0.0, 0.0)
        color = arcade.color.BLUE
        sprite = BeanSprite(male_bean, position, color)
        # Currently does nothing, but test it doesn't crash
        sprite.update_from_bean()
        assert sprite.bean == male_bean