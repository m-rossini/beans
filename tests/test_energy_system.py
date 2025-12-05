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


class TestApplyFatStorage:
    """Tests for StandardEnergySystem.apply_fat_storage method."""

    def test_apply_fat_storage_increases_size_when_energy_above_baseline(self):
        """When energy > energy_baseline, size should increase."""
        from beans.energy_system import StandardEnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            energy_baseline=50.0,
            fat_gain_rate=0.1,
            energy_to_fat_ratio=1.0
        )
        energy_system = StandardEnergySystem(config)
        
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
        bean._phenotype.energy = 80.0  # Above baseline of 50
        
        initial_size = bean.size
        energy_system.apply_fat_storage(bean)
        
        assert bean.size > initial_size

    def test_apply_fat_storage_decreases_energy_by_conversion_ratio(self):
        """Energy should decrease by fat_gain * energy_to_fat_ratio when storing fat."""
        from beans.energy_system import StandardEnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            energy_baseline=50.0,
            fat_gain_rate=0.1,
            energy_to_fat_ratio=2.0  # 2 energy units per 1 fat unit
        )
        energy_system = StandardEnergySystem(config)
        
        genes = {
            Gene.METABOLISM_SPEED: 0.5,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 1.0,  # Max fat accumulation
            Gene.MAX_GENETIC_AGE: 0.5,
        }
        genotype = Genotype(genes=genes)
        phenotype = create_phenotype(config, genotype)
        phenotype.size = 10.0
        bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
        bean._phenotype.energy = 80.0  # 30 surplus above baseline of 50
        
        initial_energy = bean.energy
        initial_size = bean.size
        energy_system.apply_fat_storage(bean)
        
        # fat_gain = fat_gain_rate * FAT_ACCUMULATION * surplus = 0.1 * 1.0 * 30 = 3.0
        # energy_cost = fat_gain * energy_to_fat_ratio = 3.0 * 2.0 = 6.0
        size_increase = bean.size - initial_size
        energy_decrease = initial_energy - bean.energy
        
        assert energy_decrease == size_increase * config.energy_to_fat_ratio

    def test_higher_fat_accumulation_gene_increases_fat_gain(self):
        """Higher FAT_ACCUMULATION gene should store more fat from same surplus."""
        from beans.energy_system import StandardEnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            energy_baseline=50.0,
            fat_gain_rate=0.1,
            energy_to_fat_ratio=1.0
        )
        energy_system = StandardEnergySystem(config)
        
        low_fat_genes = {
            Gene.METABOLISM_SPEED: 0.5,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.2,
            Gene.MAX_GENETIC_AGE: 0.5,
        }
        high_fat_genes = {
            Gene.METABOLISM_SPEED: 0.5,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.8,
            Gene.MAX_GENETIC_AGE: 0.5,
        }
        
        low_genotype = Genotype(genes=low_fat_genes)
        high_genotype = Genotype(genes=high_fat_genes)
        
        low_phenotype = create_phenotype(config, low_genotype)
        high_phenotype = create_phenotype(config, high_genotype)
        low_phenotype.size = 10.0
        high_phenotype.size = 10.0
        
        low_bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=low_genotype, phenotype=low_phenotype)
        high_bean = Bean(config=config, id=2, sex=Sex.MALE, genotype=high_genotype, phenotype=high_phenotype)
        low_bean._phenotype.energy = 80.0
        high_bean._phenotype.energy = 80.0
        
        energy_system.apply_fat_storage(low_bean)
        energy_system.apply_fat_storage(high_bean)
        
        # Higher FAT_ACCUMULATION should gain more size
        assert high_bean.size > low_bean.size

    def test_apply_fat_storage_does_nothing_when_energy_at_or_below_baseline(self):
        """No fat storage when energy <= energy_baseline."""
        from beans.energy_system import StandardEnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            energy_baseline=50.0,
            fat_gain_rate=0.1,
            energy_to_fat_ratio=1.0
        )
        energy_system = StandardEnergySystem(config)
        
        genotype = create_random_genotype()
        phenotype = create_phenotype(config, genotype)
        phenotype.size = 10.0
        bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
        bean._phenotype.energy = 50.0  # At baseline
        
        initial_size = bean.size
        initial_energy = bean.energy
        energy_system.apply_fat_storage(bean)
        
        assert bean.size == initial_size
        assert bean.energy == initial_energy


class TestApplyFatBurning:
    """Tests for StandardEnergySystem.apply_fat_burning method."""

    def test_apply_fat_burning_decreases_size_when_energy_below_baseline(self):
        """When energy < energy_baseline, size should decrease (fat burned)."""
        from beans.energy_system import StandardEnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            energy_baseline=50.0,
            fat_burn_rate=0.1,
            fat_to_energy_ratio=0.9
        )
        energy_system = StandardEnergySystem(config)
        
        genes = {
            Gene.METABOLISM_SPEED: 0.5,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.5,
            Gene.MAX_GENETIC_AGE: 0.5,
        }
        genotype = Genotype(genes=genes)
        phenotype = create_phenotype(config, genotype)
        phenotype.size = 15.0  # Has fat to burn
        bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
        bean._phenotype.energy = 30.0  # Below baseline of 50
        
        initial_size = bean.size
        energy_system.apply_fat_burning(bean)
        
        assert bean.size < initial_size

    def test_apply_fat_burning_increases_energy_by_conversion_ratio(self):
        """Energy should increase by fat_burned * fat_to_energy_ratio when burning fat."""
        from beans.energy_system import StandardEnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            energy_baseline=50.0,
            fat_burn_rate=0.1,
            fat_to_energy_ratio=0.8
        )
        energy_system = StandardEnergySystem(config)
        
        genes = {
            Gene.METABOLISM_SPEED: 0.5,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 1.0,
            Gene.MAX_GENETIC_AGE: 0.5,
        }
        genotype = Genotype(genes=genes)
        phenotype = create_phenotype(config, genotype)
        phenotype.size = 20.0  # Has fat to burn
        bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
        bean._phenotype.energy = 30.0  # 20 deficit below baseline of 50
        
        initial_energy = bean.energy
        initial_size = bean.size
        energy_system.apply_fat_burning(bean)
        
        # fat_burned = fat_burn_rate * FAT_ACCUMULATION * deficit = 0.1 * 1.0 * 20 = 2.0
        # energy_gain = fat_burned * fat_to_energy_ratio = 2.0 * 0.8 = 1.6
        size_decrease = initial_size - bean.size
        energy_increase = bean.energy - initial_energy
        
        assert energy_increase == pytest.approx(size_decrease * config.fat_to_energy_ratio)

    def test_higher_fat_accumulation_gene_increases_fat_burn(self):
        """Higher FAT_ACCUMULATION gene should burn more fat from same deficit."""
        from beans.energy_system import StandardEnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            energy_baseline=50.0,
            fat_burn_rate=0.1,
            fat_to_energy_ratio=0.9
        )
        energy_system = StandardEnergySystem(config)
        
        low_fat_genes = {
            Gene.METABOLISM_SPEED: 0.5,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.2,
            Gene.MAX_GENETIC_AGE: 0.5,
        }
        high_fat_genes = {
            Gene.METABOLISM_SPEED: 0.5,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.8,
            Gene.MAX_GENETIC_AGE: 0.5,
        }
        
        low_genotype = Genotype(genes=low_fat_genes)
        high_genotype = Genotype(genes=high_fat_genes)
        
        low_phenotype = create_phenotype(config, low_genotype)
        high_phenotype = create_phenotype(config, high_genotype)
        low_phenotype.size = 20.0
        high_phenotype.size = 20.0
        
        low_bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=low_genotype, phenotype=low_phenotype)
        high_bean = Bean(config=config, id=2, sex=Sex.MALE, genotype=high_genotype, phenotype=high_phenotype)
        low_bean._phenotype.energy = 30.0
        high_bean._phenotype.energy = 30.0
        
        energy_system.apply_fat_burning(low_bean)
        energy_system.apply_fat_burning(high_bean)
        
        # Higher FAT_ACCUMULATION should lose more size (burn more fat)
        assert high_bean.size < low_bean.size

    def test_apply_fat_burning_does_nothing_when_energy_at_or_above_baseline(self):
        """No fat burning when energy >= energy_baseline."""
        from beans.energy_system import StandardEnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            energy_baseline=50.0,
            fat_burn_rate=0.1,
            fat_to_energy_ratio=0.9
        )
        energy_system = StandardEnergySystem(config)
        
        genotype = create_random_genotype()
        phenotype = create_phenotype(config, genotype)
        phenotype.size = 15.0
        bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
        bean._phenotype.energy = 50.0  # At baseline
        
        initial_size = bean.size
        initial_energy = bean.energy
        energy_system.apply_fat_burning(bean)
        
        assert bean.size == initial_size
        assert bean.energy == initial_energy