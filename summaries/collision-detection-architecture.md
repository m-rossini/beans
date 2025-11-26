---
id: collision_detection_architecture
title: Bean Collision Detection System
---
graph TB
    subgraph "Placement Pipeline"
        User["User/Config"]
        Factory["create_strategy_from_name<br/>(factory pattern)"]
        Strategy["PlacementStrategy<br/>(base class)"]
    end

    subgraph "Generation Phase"
        RandGen["RandomGenerator<br/>infinite: random x,y"]
        GridGen["GridIteration<br/>finite: grid cells"]
        ClustGen["ClusterGenerator<br/>infinite: offset from centers"]
    end

    subgraph "Collision Detection"
        Hash["SpatialHash<br/>O(1) collision checks"]
        Loop["Generation Loop<br/>Generate → Collide? → Append"]
    end

    subgraph "Validation Phase"
        Threshold["90% Threshold Check<br/>min_sprites = count * 0.9<br/>if placed >= min: return<br/>else: raise SystemExit"]
    end

    subgraph "Strategy Implementations"
        Random["RandomPlacementStrategy<br/>packing_eff: 0.45"]
        Grid["GridPlacementStrategy<br/>packing_eff: 0.64"]
        Cluster["ClusteredPlacementStrategy<br/>packing_eff: 0.55"]
    end

    subgraph "Early Warning System"
        CanFit["_can_fit() method<br/>Checks: area_needed vs available<br/>Uses packing_efficiency<br/>Prevents impossible requests"]
    end

    User -->|name: 'random'/'grid'/'cluster'| Factory
    Factory -->|creates| Strategy
    
    Strategy -->|delegates to| Random
    Strategy -->|delegates to| Grid
    Strategy -->|delegates to| Cluster
    
    Random -->|calls _can_fit| CanFit
    Grid -->|calls _can_fit| CanFit
    Cluster -->|calls _can_fit| CanFit
    
    Random -->|uses| RandGen
    Grid -->|uses| GridGen
    Cluster -->|uses| ClustGen
    
    RandGen -->|feeds| Loop
    GridGen -->|feeds| Loop
    ClustGen -->|feeds| Loop
    
    Loop -->|collision check| Hash
    Hash -->|return positions| Loop
    
    Loop -->|final positions| Threshold
    Threshold -->|pass: >= 90%| Result["Return positions<br/>PlacedSprites[]"]
    Threshold -->|fail: < 90%| Error["raise SystemExit(1)"]
    
    Result -->|success| User
    Error -->|failure| User
    
    style Strategy fill:#e1f5ff
    style Hash fill:#f3e5f5
    style Threshold fill:#fff3e0
    style CanFit fill:#e8f5e9
    style Random fill:#fce4ec
    style Grid fill:#fce4ec
    style Cluster fill:#fce4ec
