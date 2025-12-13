import random
import pytest

from beans.genetics import create_random_genotype, create_phenotype
from beans.genetics import Genotype
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
    # create a basic genotype to use
    genes = {g: 1.0 for g in Genotype.__fields__["genes"].type_}
    # This is a placeholder until deterministic create_phenotype implementation is added
    # We'll just call the function to confirm it accepts rng parameter
    cfg = BeansConfig(speed_min=0.1, speed_max=1.0, initial_bean_size=10)
    # No strict assertions are made here; this test will be refined later
    ph = create_phenotype(cfg, None, rng=rng)
    assert ph is not None
