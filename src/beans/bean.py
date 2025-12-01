import random
import logging
from dataclasses import dataclass, asdict
from typing import NamedTuple
from enum import Enum

from pydantic import BaseModel, field_validator

from config.loader import BeansConfig

logger = logging.getLogger(__name__)


class GeneInfo(NamedTuple):
    """Gene metadata: name and valid range."""
    name: str
    min: float
    max: float


class Gene(Enum):
    """
    Gene types for beans with validation ranges.
    
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
                raise ValueError(
                    f"Gene {gene.name} value {value} out of range [{gene.min}, {gene.max}]"
                )
        return v


def create_random_genotype() -> Genotype:
    """Create a genotype with random values within each gene's valid range."""
    return Genotype(
        genes={gene: random.uniform(gene.min, gene.max) for gene in Gene}
    )


@dataclass
class Phenotype:
    """Mutable expression of genetic traits that change over time.
    
    Attributes:
        age: Current age in simulation ticks
        speed: Current movement speed (absolute, direction handled by sprite)
        energy: Current energy level
        size: Current size (represents fatness)
    """
    age: float
    speed: float
    energy: float
    size: float

    def to_dict(self) -> dict:
        """Serialize phenotype to dictionary for state persistence."""
        return asdict(self)


def create_phenotype(config: BeansConfig, genotype: Genotype) -> Phenotype:
    """Create initial phenotype from config and genotype.
    
    # TODO: Review initial values for phenotype creation
    """
    max_genetic_speed = config.speed_max * genotype.genes[Gene.MAX_GENETIC_SPEED]
    return Phenotype(
        age=0.0,
        speed=random.uniform(-max_genetic_speed, max_genetic_speed),
        energy=config.initial_energy,
        size=float(config.initial_bean_size),
    )


def can_survive_energy(energy: float) -> bool:
    """Check if energy level is survivable.
    
    # TODO: Implement energy survival bounds check
    """
    return True


def can_survive_size(size: float) -> bool:
    """Check if size is survivable.
    
    # TODO: Implement size survival bounds check
    """
    return True


class Sex(Enum):
    MALE = "male"
    FEMALE = "female"

class Bean:
    """Bean with mutable state, initialized from BeansConfig.

    Variables are expected to be set during construction. `update()` modifies the bean in place.
    Phenotype contains the mutable traits (age, speed, energy, size) that change over time.
    """

    def __init__(
        self,
        config: BeansConfig,
        id: int,
        sex: Sex,
        genotype: Genotype,
        phenotype: Phenotype,
    ) -> None:

        self.beans_config = config
        self.id = id
        self.sex = sex
        self.genotype = genotype
        self._phenotype = phenotype
        logger.debug(f">>>>> Bean {self.id} created: sex={self.sex.value}, speed={self.speed:.2f}, energy={self.energy}, genotype={self.genotype.genes}")

    @property
    def age(self) -> float:
        return self._phenotype.age

    @property
    def speed(self) -> float:
        return self._phenotype.speed

    @property
    def energy(self) -> float:
        return self._phenotype.energy

    @property
    def size(self) -> float:
        return self._phenotype.size

    def update(self, dt: float = 1.0) -> dict[str, float]:
        """Update bean in-place and return outcome metrics."""
        self._phenotype.age += 1.0
        energy = self._energy_tick(dt)
        logger.debug(f">>>>> Bean {self.id} after update: age={self.age}, energy={energy:.2f}, dt={dt}")
        return {"energy": energy}

    def _energy_tick(self, dt: float = 1.0) -> float:
        """Adjust energy based on per-step gains and movement costs."""
        gain = self.beans_config.energy_gain_per_step
        cost = abs(self.speed) * self.beans_config.energy_cost_per_speed
        old_energy = self.energy
        self._phenotype.energy += gain - cost
        logger.debug(f">>>>> Bean {self.id} _energy_tick: gain={gain}, cost={cost:.2f}, old_energy={old_energy:.2f}, new_energy={self.energy:.2f}, speed={self.speed:.2f}, cost_per_speed={self.beans_config.energy_cost_per_speed}, dt={dt}")
        return self.energy

    @property
    def is_male(self) -> bool:
        return self.sex == Sex.MALE

    @property
    def is_female(self) -> bool:
        return self.sex == Sex.FEMALE
