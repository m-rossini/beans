import random
import logging
from typing import NamedTuple, Optional
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

class Sex(Enum):
    MALE = "male"
    FEMALE = "female"

class Bean:
    """Bean with mutable state, initialized from optional BeansConfig.

    Variables are expected to be set during construction. `update()` modifies the bean in place.
    """

    def __init__(
        self,
        config: BeansConfig,
        id: int,
        sex: Sex,
        genotype: Genotype,
        speed: Optional[float] = None,
    ) -> None:

        self.beans_config = config
        self.id = id
        self.sex = sex
        self.genotype = genotype
        self.age = 0.0
        self.speed = random.uniform(config.speed_min, config.speed_max) if speed is None else speed
        self.energy = config.initial_energy
        self.size = config.initial_bean_size
        logger.debug(f">>>>> Bean {self.id} created: sex={self.sex.value}, speed={self.speed:.2f}, energy={self.energy}, genotype={self.genotype.genes}")

    def update(self, dt: float = 1.0) -> dict[str, float]:
        """Update bean in-place and return outcome metrics."""
        self.age += 1.0
        energy = self._energy_tick(dt)
        logger.debug(f">>>>> Bean {self.id} after update: age={self.age}, energy={energy:.2f}, dt={dt}")
        return {"energy": energy}

    def _energy_tick(self, dt: float = 1.0) -> float:
        """Adjust energy based on per-step gains and movement costs."""
        gain = self.beans_config.energy_gain_per_step
        cost = abs(self.speed) * self.beans_config.energy_cost_per_speed
        old_energy = self.energy
        self.energy += gain - cost
        logger.debug(f">>>>> Bean {self.id} _energy_tick: gain={gain}, cost={cost:.2f}, old_energy={old_energy:.2f}, new_energy={self.energy:.2f}, speed={self.speed:.2f}, cost_per_speed={self.beans_config.energy_cost_per_speed}, dt={dt}")
        return self.energy

    @property
    def is_male(self) -> bool:
        return self.sex == Sex.MALE

    @property
    def is_female(self) -> bool:
        return self.sex == Sex.FEMALE
