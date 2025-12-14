"""Genetics module for bean genetic traits and phenotype expression.

This module contains:
- GeneInfo: Gene metadata (name, min/max range)
- Gene: Enum of gene types with validation ranges
- Genotype: Immutable genetic blueprint (Pydantic model)
- Phenotype: Mutable trait expression (dataclass)
- Factory functions for creating genotypes and phenotypes
- Helper functions for genetic calculations
"""

import logging
import math
import random
from dataclasses import asdict, dataclass
from enum import Enum
from typing import NamedTuple, Optional

from pydantic import BaseModel, field_validator

from config.loader import BeansConfig

logger = logging.getLogger(__name__)


# =============================================================================
# Helper Functions
# =============================================================================

def size_sigma(target_size: float) -> float:
    """Calculate standard deviation for size (±15% of target)."""
    return target_size * 0.15


def size_z_score(size: float, target: float) -> float:
    """Calculate z-score for size deviation from target."""
    sigma = size_sigma(target)
    return (size - target) / sigma if sigma else 0.0


def apply_age_gene_curve(raw_value: float) -> float:
    """Apply logarithmic curve to MAX_GENETIC_AGE gene value.

    Transforms a uniform random value [0,1] into a logarithmic distribution
    that favors longevity:
    - raw 0.0 → 0.1 (minimum 10% lifespan)
    - raw 0.5 → ~0.73 (logarithmic midpoint favors longevity)
    - raw 1.0 → 1.0 (full lifespan)
    """
    min_fraction = 0.1  # Minimum 10% lifespan even with gene=0
    k = 5.0  # Steepness of logarithmic curve

    log_factor = math.log(1 + k * raw_value) / math.log(1 + k)
    return min_fraction + (1 - min_fraction) * log_factor


def age_speed_factor(age: float, max_age: float, min_speed_factor: float = 0.0) -> float:
    """Calculate speed factor based on age lifecycle curve, with configurable minimum.

    Returns a value between min_speed_factor and 1 representing the speed multiplier
    based on the bean's age relative to its maximum age.
    """
    if age <= 0:
        return min_speed_factor

    x = min(max(age / max_age, 0.0), 1.0)

    # shape parameters
    p = 2.0   # childhood growth rate
    q = 2.0   # maturity steepness
    r = 4.0   # aging decay strength

    growth = (x ** p) * math.exp(-q * x)
    aging = (1 - x ** r)

    raw = max(0.0, growth * aging)
    return max(min_speed_factor, raw)


def age_energy_efficiency(age: float, max_age: float, min_efficiency: float) -> float:
    """Calculate energy efficiency based on age lifecycle curve.

    Returns a value between min_efficiency and 1.0 representing how
    efficiently a bean uses energy at its current age.

    - Newborns start at min_efficiency (inefficient)
    - Peak efficiency (~1.0) at maturity
    - Declines in old age but never below min_efficiency

    Uses similar curve shape to age_speed_factor.
    """
    if max_age <= 0:
        return min_efficiency

    x = min(max(age / max_age, 0.0), 1.0)

    # shape parameters (similar to age_speed_factor)
    p = 2.0   # childhood growth rate
    q = 2.0   # maturity steepness
    r = 4.0   # aging decay strength

    growth = (x ** p) * math.exp(-q * x)
    aging = (1 - x ** r)

    raw_efficiency = max(0.0, growth * aging)

    # Scale to range [min_efficiency, 1.0]
    # Normalize raw_efficiency (which peaks around 0.09) to [0, 1]
    # age_speed_factor peaks around x=0.25 with value ~0.09
    peak_value = 0.09  # approximate peak of the curve
    normalized = min(raw_efficiency / peak_value, 1.0)

    return min_efficiency + (1.0 - min_efficiency) * normalized


# =============================================================================
# Core Classes
# =============================================================================

class GeneInfo(NamedTuple):
    """Gene metadata: name and valid range."""

    name: str
    min: float
    max: float


class Gene(Enum):
    """Gene types for beans with validation ranges.

    Each gene influences a bean's characteristics. Values are between 0.0 and 1.0.

    - METABOLISM_SPEED: How quickly a bean burns energy (higher = faster metabolism)
    - MAX_GENETIC_SPEED: Maximum speed a bean can achieve genetically
    - FAT_ACCUMULATION: How efficiently a bean stores excess energy as fat
    - MAX_GENETIC_AGE: Maximum age a bean can reach genetically
    """

    METABOLISM_SPEED = GeneInfo("metabolism_speed", 0.0, 1.0)
    MAX_GENETIC_SPEED = GeneInfo("max_genetic_speed", 0.0, 1.0)
    FAT_ACCUMULATION = GeneInfo("fat_accumulation", 0.0, 1.0)
    MAX_GENETIC_AGE = GeneInfo("max_genetic_age", 0.0, 1.0)

    @property
    def min(self) -> float:
        return self.value.min

    @property
    def max(self) -> float:
        return self.value.max


class Genotype(BaseModel):
    """Immutable genetic blueprint for a bean."""

    genes: dict[Gene, float]

    model_config = {"frozen": True}

    @field_validator("genes")
    @classmethod
    def validate_genes(cls, v: dict[Gene, float]) -> dict[Gene, float]:
        for gene in Gene:
            if gene not in v:
                raise ValueError(f"Missing gene: {gene.name}")
            value = v[gene]
            if not gene.min <= value <= gene.max:
                raise ValueError(f"Gene {gene.name} value {value} out of range [{gene.min}, {gene.max}]")
        return v

    def to_compact_str(self) -> str:
        """Return compact string for logging: {MET:0.32, SPD:0.75, FAT:0.36, AGE:0.05}."""
        abbrev = {
            Gene.METABOLISM_SPEED: "MET",
            Gene.MAX_GENETIC_SPEED: "SPD",
            Gene.FAT_ACCUMULATION: "FAT",
            Gene.MAX_GENETIC_AGE: "AGE",
        }
        parts = [f"{abbrev[g]}:{v:.2f}" for g, v in self.genes.items()]
        return "{" + ", ".join(parts) + "}"


@dataclass
class Phenotype:
    """Mutable expression of genetic traits that change over time.

    Attributes:
        age: Current age in simulation ticks
        speed: Current movement speed (absolute, direction handled by sprite)
        energy: Current energy level
        size: Current size (represents fatness)
        target_size: Computed fittest size at that age

    """

    age: float
    speed: float
    energy: float
    size: float
    target_size: float

    def to_dict(self) -> dict:
        """Serialize phenotype to dictionary for state persistence."""
        return asdict(self)


# =============================================================================
# Genetic Calculation Functions
# =============================================================================

def genetic_max_age(config: BeansConfig, genotype: Genotype) -> float:
    """Calculate maximum age from config and genotype.

    The gene value is already transformed via apply_age_gene_curve() at
    genotype creation, so this is a simple multiplication.
    """
    return config.max_age_rounds * genotype.genes[Gene.MAX_GENETIC_AGE]


def size_target(age: float, genotype: Genotype, config: BeansConfig) -> float:
    """Calculate target size based on age and genotype.

    Uses a bell curve centered at mid-life to model size changes.
    """
    max_age = genetic_max_age(config, genotype)
    x = min(max(age / max_age, 0), 1)

    Smin = config.min_bean_size
    Smax = config.max_bean_size * genotype.genes[Gene.FAT_ACCUMULATION]

    k = 5.0  # width of life bell curve

    bell = math.exp(-k * (x - 0.5) ** 2)
    return Smin + (Smax - Smin) * bell


def genetic_max_speed(config: BeansConfig, genotype: Genotype) -> float:
    """Calculate maximum speed from config and genotype."""
    return config.speed_max * genotype.genes[Gene.MAX_GENETIC_SPEED]


# =============================================================================
# Factory Functions
# =============================================================================

def create_random_genotype(rng: Optional[random.Random] = None) -> Genotype:
    """Create a genotype with random values within each gene's valid range.

    MAX_GENETIC_AGE uses a logarithmic curve to favor longevity.
    """
    genes = {}
    r = rng if rng is not None else random
    for gene in Gene:
        raw_value = r.uniform(gene.min, gene.max)
        if gene == Gene.MAX_GENETIC_AGE:
            genes[gene] = apply_age_gene_curve(raw_value)
        else:
            genes[gene] = raw_value

    genotype = Genotype(genes=genes)
    logger.debug(f">>>>> genetics::create_random_genotype: created genotype with genes={genes}")
    return genotype


def create_phenotype(config: BeansConfig, genotype: Genotype, rng: Optional[random.Random] = None) -> Phenotype:
    """Create initial phenotype from config and genotype.

    Newborn beans start with age=0 and speed=0 (since age_speed_factor(0) = 0).
    Initial values have ±5% random variation.
    """
    max_age = config.max_age_rounds * genotype.genes[Gene.MAX_GENETIC_AGE]
    max_speed = config.speed_max * genotype.genes[Gene.MAX_GENETIC_SPEED]

    r = rng if rng is not None else random
    initial_speed = max_speed * age_speed_factor(0, max_age,0.0)
    random_low_bound = 0.95
    random_high_bound = 1.05

    phenotype = Phenotype(
        age=0.0,
        speed=r.choice([-1, 1]) * initial_speed * r.uniform(random_low_bound, random_high_bound),
        energy=config.initial_energy * r.uniform(random_low_bound, random_high_bound),
        size=float(config.initial_bean_size) * r.uniform(random_low_bound, random_high_bound),
        target_size=size_target(0.0, genotype, config),
    )
    logger.debug(f">>>>> genetics::create_phenotype: created phenotype age={phenotype.age}, speed_base={initial_speed:.2f}, speed={phenotype.speed:.2f}, energy={phenotype.energy:.2f}, size={phenotype.size:.2f}, target_size={phenotype.target_size:.2f}, max_age={max_age:.2f}, max_speed={max_speed:.2f}")
    return phenotype


def create_genotype_from_values(genes: dict[Gene, float]) -> Genotype:
    """Create a genotype from explicit gene values.

    This helper is useful for deterministic tests where the exact gene
    values must be specified.
    """
    return Genotype(genes=genes)


def create_phenotype_from_values(config: BeansConfig, genotype: Genotype, age: float, speed: float, energy: float, size: float, target_size: float) -> Phenotype:
    """Create a phenotype instance with explicit values."""
    return Phenotype(age=age, speed=speed, energy=energy, size=size, target_size=target_size)


# =============================================================================
# Survival Checks (TODO)
# =============================================================================
#TODO MOve to survival check system
def can_survive_size(size: float) -> bool:
    """Check if size allows survival."""
    raise NotImplementedError("Need to implement and use")
