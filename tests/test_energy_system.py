import pytest
import logging
from config.loader import BeansConfig
from beans.bean import Bean, Sex
from beans.genetics import create_random_genotype, create_phenotype, Genotype, Gene

logger = logging.getLogger(__name__)


class TestApplyIntake:
    """Tests for StandardEnergySystem.apply_intake method."""

    def test_apply_intake_increases_bean_energy(self):
        """apply_intake should increase bean's energy by the given amount."""
        from beans.energy_system import StandardEnergySystem
        
        config = BeansConfig(speed_min=-5, speed_max=5, initial_energy=50.0)
        energy_system = StandardEnergySystem(config)
        
        genotype = create_random_genotype()
        phenotype = create_phenotype(config, genotype)
        bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
        
        initial_energy = bean.energy
        energy_system.apply_intake(bean, 10.0)
        
        assert bean.energy == initial_energy + 10.0


class TestApplyBasalMetabolism:
    """Tests for StandardEnergySystem.apply_basal_metabolism method."""

    def test_apply_basal_metabolism_uses_correct_formula(self):
        """apply_basal_metabolism should use: burn = base * (1 + 0.5 * metabolism) * size."""
        from beans.energy_system import StandardEnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            initial_bean_size=10,
            metabolism_base_burn=0.10
        )
        energy_system = StandardEnergySystem(config)
        
        # Create genotype with known metabolism value
        genes = {
            Gene.METABOLISM_SPEED: 0.5,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.5,
            Gene.MAX_GENETIC_AGE: 0.5,
        }
        genotype = Genotype(genes=genes)
        phenotype = create_phenotype(config, genotype)
        phenotype.size = 10.0
        bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
        bean._phenotype.energy = 100.0
        
        initial_energy = bean.energy
        energy_system.apply_basal_metabolism(bean)
        
        # burn = 0.10 * (1 + 0.5 * 0.5) * 10 = 0.10 * 1.25 * 10 = 1.25
        expected_burn = config.metabolism_base_burn * (1 + 0.5 * 0.5) * 10.0
        assert bean.energy == initial_energy - expected_burn

    def test_higher_metabolism_gene_increases_burn_rate(self):
        """Higher METABOLISM_SPEED gene value should increase basal burn rate."""
        from beans.energy_system import StandardEnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            initial_bean_size=10,
            metabolism_base_burn=0.10
        )
        energy_system = StandardEnergySystem(config)
        
        # Create two genotypes with different metabolism speeds
        low_metabolism_genes = {
            Gene.METABOLISM_SPEED: 0.0,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.5,
            Gene.MAX_GENETIC_AGE: 0.5,
        }
        high_metabolism_genes = {
            Gene.METABOLISM_SPEED: 1.0,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.5,
            Gene.MAX_GENETIC_AGE: 0.5,
        }
        
        low_genotype = Genotype(genes=low_metabolism_genes)
        high_genotype = Genotype(genes=high_metabolism_genes)
        
        # Create phenotypes with same size to isolate metabolism effect
        low_phenotype = create_phenotype(config, low_genotype)
        high_phenotype = create_phenotype(config, high_genotype)
        low_phenotype.size = 10.0
        high_phenotype.size = 10.0
        
        low_bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=low_genotype, phenotype=low_phenotype)
        high_bean = Bean(config=config, id=2, sex=Sex.MALE, genotype=high_genotype, phenotype=high_phenotype)
        
        # Set same initial energy
        low_bean._phenotype.energy = 100.0
        high_bean._phenotype.energy = 100.0
        
        energy_system.apply_basal_metabolism(low_bean)
        energy_system.apply_basal_metabolism(high_bean)
        
        # Higher metabolism should burn more energy
        assert high_bean.energy < low_bean.energy


class TestApplyMovementCost:
    """Tests for StandardEnergySystem.apply_movement_cost method."""

    def test_apply_movement_cost_deducts_based_on_speed(self):
        """apply_movement_cost should deduct abs(speed) * energy_cost_per_speed."""
        from beans.energy_system import StandardEnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            energy_cost_per_speed=0.5
        )
        energy_system = StandardEnergySystem(config)
        
        genotype = create_random_genotype()
        phenotype = create_phenotype(config, genotype)
        phenotype.speed = 3.0  # Set known speed
        bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
        bean._phenotype.energy = 100.0
        
        initial_energy = bean.energy
        energy_system.apply_movement_cost(bean)
        
        # cost = abs(3.0) * 0.5 = 1.5
        expected_cost = abs(3.0) * config.energy_cost_per_speed
        assert bean.energy == initial_energy - expected_cost

    def test_apply_movement_cost_uses_absolute_speed(self):
        """apply_movement_cost should use absolute value of speed (negative speed costs same as positive)."""
        from beans.energy_system import StandardEnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            energy_cost_per_speed=0.5
        )
        energy_system = StandardEnergySystem(config)
        
        genotype = create_random_genotype()
        
        # Create two beans with opposite speeds
        pos_phenotype = create_phenotype(config, genotype)
        neg_phenotype = create_phenotype(config, genotype)
        pos_phenotype.speed = 4.0
        neg_phenotype.speed = -4.0
        
        pos_bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=pos_phenotype)
        neg_bean = Bean(config=config, id=2, sex=Sex.MALE, genotype=genotype, phenotype=neg_phenotype)
        pos_bean._phenotype.energy = 100.0
        neg_bean._phenotype.energy = 100.0
        
        energy_system.apply_movement_cost(pos_bean)
        energy_system.apply_movement_cost(neg_bean)
        
        # Both should have same energy after (same absolute speed)
        assert pos_bean.energy == neg_bean.energy