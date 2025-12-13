import random
import pytest

from beans.genetics import create_random_genotype, create_phenotype, create_genotype_from_values, create_phenotype_from_values
from beans.genetics import Genotype, Gene
from config.loader import BeansConfig


def test_create_random_genotype_accepts_rng():
    rng = random.Random(0)
    g1 = create_random_genotype(rng=rng)

    rng = random.Random(0)
    g2 = create_random_genotype(rng=rng)

    # Expect genotypes to be reproducible with same RNG seed
    assert isinstance(g1, Genotype)
    assert isinstance(g2, Genotype)
    assert g1.genes == g2.genes


def test_create_phenotype_accepts_rng():
    rng = random.Random(0)
    # create a deterministic genotype to use
    genes = {g: 0.5 for g in Gene}
    genotype = create_genotype_from_values(genes)

    cfg = BeansConfig(speed_min=0.1, speed_max=1.0, initial_bean_size=10)
    p1 = create_phenotype(cfg, genotype, rng=rng)

    rng = random.Random(0)
    p2 = create_phenotype(cfg, genotype, rng=rng)

    assert p1.age == p2.age
    assert p1.speed == p2.speed
    assert p1.energy == p2.energy
    assert p1.size == p2.size


def test_create_genotype_from_values_validation():
    # gene values must be between 0.0 and 1.0
    genes = {g: -0.1 for g in Gene}
    with pytest.raises(ValueError):
        _ = create_genotype_from_values(genes)


def test_create_phenotype_from_values_preserves_values():
    genes = {g: 0.5 for g in Gene}
    genotype = create_genotype_from_values(genes)
    cfg = BeansConfig(speed_min=0.1, speed_max=1.0, initial_bean_size=10)
    ph = create_phenotype_from_values(cfg, genotype, age=3.0, speed=0.5, energy=20.0, size=7.0, target_size=7.0)
    assert ph.age == 3.0
    assert ph.speed == 0.5
    assert ph.energy == 20.0
    assert ph.size == 7.0
    assert ph.target_size == 7.0
