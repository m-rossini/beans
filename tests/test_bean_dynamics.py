from beans.genetics import Gene, Genotype, age_speed_factor
from config.loader import BeansConfig
from src.beans.bean import BeanState
from src.beans.dynamics.bean_dynamics import BeanDynamics


def test_bean_dynamics_speed_calculation():
    config = BeansConfig(speed_min=0.1, speed_max=1.0, min_speed_factor=0.2)
    bean_state = BeanState(id=1, age=5, speed=1.0, energy=10.0, size=10.0, target_size=10.0, alive=True)
    # Provide dummy genotype and max_age for calculation
    genes = {
        Gene.METABOLISM_SPEED: 1.0,
        Gene.MAX_GENETIC_SPEED: 1.0,
        Gene.FAT_ACCUMULATION: 1.0,
        Gene.MAX_GENETIC_AGE: 1.0,
    }
    genotype = Genotype(genes=genes)
    dummy_max_age = 100
    dynamics = BeanDynamics(config)
    speed = dynamics.calculate_speed(bean_state,genotype, dummy_max_age)
    # Expected: vmax * age_factor * size_penalty, all factors = 1.0 except min_speed_factor
    # For age=5, max_age=100, min_speed_factor=0.2, vmax=1.0, size_penalty=1.0
    expected_age_factor = age_speed_factor(5, dummy_max_age, config.min_speed_factor)
    expected_speed = max(config.min_speed_factor, config.speed_max * expected_age_factor * 1.0)
    assert speed == expected_speed
