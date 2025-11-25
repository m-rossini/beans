```mermaid
flowchart TD
    Config[WorldConfig] -->|provides| World[World]
    World -->|uses| PlacementStrategy
    World -->|uses| PopulationEstimator
    PopulationEstimator -->|Density| DensityPopulationEstimator
    PopulationEstimator -->|Soft log| SoftLogPopulationEstimator
    PlacementStrategy -->|Random| RandomPlacementStrategy
    PlacementStrategy -->|Grid| GridPlacementStrategy
    PlacementStrategy -->|Clustered| ClusteredPlacementStrategy
    World -->|instantiates beans| BeanPool(Beans)
```