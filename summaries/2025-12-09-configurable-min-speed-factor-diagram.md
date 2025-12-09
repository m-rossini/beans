```mermaid
graph TD
    Config[BeansConfig (JSON)] --> Loader[Config Loader]
    Loader -->|min_speed_factor| Genetics[age_speed_factor]
    Genetics --> Bean[Bean/Phenotype]
    Bean --> Movement[Movement System]
    Movement --> Sprite[BeanSprite]
    Sprite --> Render[Arcade Render]
    
    subgraph Validation
        Loader
    end
    subgraph Test
        Genetics
        Sprite
    end
```
