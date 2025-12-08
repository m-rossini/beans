import pytest
import arcade
import logging
from beans.bean import Bean, Sex
from beans.genetics import Gene, Genotype, Phenotype
from config.loader import BeansConfig
from rendering.bean_sprite import BeanSprite

logger = logging.getLogger(__name__)


class TestBeanSprite:
    @pytest.fixture
    def beans_config(self):
        return BeansConfig(
            speed_min=10.0,
            speed_max=20.0,
            initial_energy=50.0,
            male_bean_color="blue",
            female_bean_color="red",
            max_age_rounds=100,
        )

    @pytest.fixture
    def sample_genotype(self):
        return Genotype(genes={
            Gene.METABOLISM_SPEED: 0.5,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.5,
            Gene.MAX_GENETIC_AGE: 0.5,
        })

    @pytest.fixture
    def sample_phenotype(self):
        """Create a phenotype for testing with controlled values."""
        return Phenotype(age=0.0, speed=15.0, energy=50.0, size=5.0, target_size=5.0)

    @pytest.fixture
    def male_bean(self, beans_config, sample_genotype, sample_phenotype):
        return Bean(config=beans_config, id=1, sex=Sex.MALE, genotype=sample_genotype, phenotype=sample_phenotype)

    @pytest.fixture
    def female_bean(self, beans_config, sample_genotype, sample_phenotype):
        return Bean(config=beans_config, id=2, sex=Sex.FEMALE, genotype=sample_genotype, phenotype=sample_phenotype)

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
        
        # Initial scale should be 1.0 (bean size equals initial size)
        initial_size = male_bean.size
        sprite.update_from_bean()
        assert sprite.scale == (1.0, 1.0)  # scale is a tuple (x, y)
        
        # Change bean size and verify scale updates
        male_bean._phenotype.size = initial_size * 1.5  # Make bean 50% larger
        sprite.update_from_bean()
        assert sprite.scale == (1.5, 1.5)
        
        # Change bean size again
        male_bean._phenotype.size = initial_size * 0.8  # Make bean 20% smaller
        sprite.update_from_bean()
        assert sprite.scale == (0.8, 0.8)

    def test_sprite_direction_default_in_valid_range(self, male_bean):
        position = (100.0, 200.0)
        color = arcade.color.BLUE
        sprite = BeanSprite(male_bean, position, color)
        assert 0.0 <= sprite.direction < 360.0

    def test_sprite_direction_explicit_value(self, female_bean):
        position = (150.0, 250.0)
        color = arcade.color.RED
        sprite = BeanSprite(female_bean, position, color, direction=45.0)
        assert sprite.direction == 45.0

    def test_sprite_direction_normalized(self, male_bean):
        position = (100.0, 200.0)
        color = arcade.color.BLUE
        sprite = BeanSprite(male_bean, position, color, direction=450.0)
        assert sprite.direction == 90.0