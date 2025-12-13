import random
from typing import Optional

from pydantic import BaseModel


class BeanContext(BaseModel):
    """Runtime context for spawning beans.

    Holds creation counts and an optional RNG used to create deterministic
    genotypes/phenotypes for testing or reproducible runs.
    """

    bean_count: int
    male_count: int
    rng: Optional[random.Random] = None

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def validate_counts(cls, bean_count: int, male_count: int) -> None:
        if bean_count < 0:
            raise ValueError("bean_count must be >= 0")
        if male_count < 0:
            raise ValueError("male_count must be >= 0")
        if male_count > bean_count:
            raise ValueError("male_count cannot be greater than bean_count")

    def __init__(self, **data):
        bean_count = data.get("bean_count")
        male_count = data.get("male_count")
        self.validate_counts(bean_count, male_count)
        super().__init__(**data)
