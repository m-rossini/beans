# Pluggable Energy System - Architecture Diagram

```mermaid
flowchart TB
    subgraph Config["Configuration Layer"]
        WC["WorldConfig"]
        BC["BeansConfig"]
    end

    subgraph Factory["Factory Layer"]
        F["create_energy_system_from_name"]
    end

    subgraph Interface["EnergySystem ABC"]
        ES["EnergySystem"]
        M1["apply_intake"]
        M2["apply_basal_metabolism"]
        M3["apply_movement_cost"]
        M4["apply_fat_storage"]
        M5["apply_fat_burning"]
        M6["handle_negative_energy"]
        M7["clamp_size"]
        M9["can_survive_starvation"]
        M10["can_survive_health"]
    end

    subgraph Dynamics["BeanDynamics (speed calculations)"]
        BD["BeanDynamics"]
        S1["size_speed_penalty"]
    end

    subgraph Implementation["Implementation"]
        SES["StandardEnergySystem"]
    end

    subgraph WorldLayer["World Orchestration"]
        W["World"]
        STEP["step"]
        UB["_update_bean"]
    end

    subgraph BeanLayer["Bean Data Entity"]
        B["Bean"]
        PH["Phenotype"]
        GE["Genotype"]
    end

    WC --> F
    BC --> F
    F --> SES
    SES -.-> ES
    W --> STEP
    STEP --> UB
    UB --> M2
    UB --> M3
    W --> SES
    ES --> PH
    ES --> GE
    BD --> S1
    BD --> PH
    B --> PH
    B --> GE
```

## Key Relationships

| From | To | Relationship |
|------|-----|--------------|
| WorldConfig | Factory | Provides energy system name |
| BeansConfig | Factory | Provides configuration parameters |
| Factory | StandardEnergySystem | Creates instance |
| StandardEnergySystem | EnergySystem | Implements interface |
| World | StandardEnergySystem | Owns and orchestrates |
| EnergySystem | Phenotype | Modifies energy, size |
| EnergySystem | Genotype | Reads gene values |

## Update Loop Sequence

```mermaid
sequenceDiagram
    participant W as World
    participant ES as EnergySystem
    participant B as Bean
    participant P as Phenotype

    loop For each bean
        W->>W: _update_bean
        W->>ES: apply_basal_metabolism
        ES->>P: energy -= burn
        W->>ES: apply_movement_cost
        ES->>P: energy -= cost
        W->>B: update
        B->>P: age += 1
        W->>B: survive
        B-->>W: alive, reason
    end
```
