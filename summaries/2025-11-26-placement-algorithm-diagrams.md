```mermaid
graph TB
    subgraph "RandomPlacementStrategy"
        A["place(count, width, height, size)"]
        B["Validation Layer"]
        C["Position Generator"]
        D["Collection & Threshold"]
    end

    subgraph "SpatialHash"
        E["Grid Initialization"]
        F["Collision Detection"]
        G["9-Cell Neighborhood Check"]
    end

    subgraph "Base Class Helpers"
        H["_get_min_distance()"]
        I["_get_valid_bounds()"]
        J["_can_fit()"]
    end

    subgraph "Output"
        K["Valid Positions List"]
        L["Empty List on Failed Threshold"]
    end

    A -->|count, bounds| B
    B -->|validate count > 0| J
    J -->|check feasibility| C
    C -->|generate random x,y| I
    I -->|within valid bounds| F
    F -->|check collision| H
    H -->|min_distance| G
    G -->|safe position?| D
    D -->|collect until count or generator exhausted| K
    D -->|validate >= 90% threshold| L
    K -->|success| L
    
    style A fill:#4a90e2
    style F fill:#7ed321
    style K fill:#50e3c2
    style L fill:#f5a623
```

## Placement Algorithm Flow

```mermaid
flowchart TD
    Start["place(count=6, width=400, height=300, size=10)"]
    
    Start --> CheckCount{count > 0?}
    CheckCount -->|No| ReturnEmpty["Return []"]
    CheckCount -->|Yes| CheckFit{_can_fit<br/>returns True?}
    
    CheckFit -->|No| RaiseError["Return []<br/>impossible to fit"]
    CheckFit -->|Yes| CalcBounds["_get_valid_bounds()<br/>min=71, max=319"]
    
    CalcBounds --> InitHash["SpatialHash(30)<br/>cell_size=30"]
    InitHash --> GenLoop["Loop: Generate Random Positions"]
    
    GenLoop --> RandPos["Random x,y in<br/>71..319"]
    RandPos --> HashCheck{has_collision?}
    
    HashCheck -->|Yes| GenLoop
    HashCheck -->|No| AddPos["Add to positions<br/>& SpatialHash"]
    AddPos --> CheckCount2{len >= count?}
    
    CheckCount2 -->|No| GenLoop
    CheckCount2 -->|Yes| CalcRatio["ratio = 6/6 = 100%"]
    
    CalcRatio --> CheckThreshold{ratio >= 90%?}
    CheckThreshold -->|Yes| Return["Return positions"]
    CheckThreshold -->|No| RaiseError2["Return []<br/>90% threshold failed"]
    
    Return --> End["Success"]
    RaiseError --> End
    RaiseError2 --> End
    ReturnEmpty --> End
    
    style Start fill:#4a90e2,color:#fff
    style Return fill:#50e3c2,color:#000
    style RaiseError fill:#f5a623,color:#000
    style RaiseError2 fill:#f5a623,color:#000
    style ReturnEmpty fill:#f5a623,color:#000
```

## SpatialHash Collision Detection

```mermaid
graph TB
    A["Check collision at (x, y)"]
    B["Calculate cell: cell_x = x // 30, cell_y = y // 30"]
    C["Create 9-cell neighborhood:<br/>cells = cells cx±1 × cy±1"]
    D["Loop through 9 cells"]
    E{Check distance<br/>to each bean}
    F["If distance < min_distance<br/>→ COLLISION"]
    G["If all ok → NO COLLISION"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E -->|Too close| F
    E -->|Far enough| G
    
    style A fill:#4a90e2,color:#fff
    style F fill:#f5a623,color:#000
    style G fill:#50e3c2,color:#000
```

## Performance Characteristics

```mermaid
xyChart
    title "Placement Performance vs Population"
    x-axis [6, 150, 1200]
    y-axis "Placement Rate (beans/sec)" 0 --> 250000
    line [28558, 105308, 228397]
```

## Data Structure: SpatialHash Example

```
Configuration: 400×300 world, bean size=10, 6 beans to place

Cell Size: 10 × 3 = 30
Grid: ~14×10 cells (400/30 × 300/30)

Example State After 3 Placements:
┌─────────────────────────────────────────┐
│  Grid cells with bean centers           │
├─────────────────────────────────────────┤
│                                         │
│  [1][2][3][4][5]...[13]                 │
│  [1][2]●(86,91)[4]...                   │ ← (2,3): bean 1
│  [1][2][3]●(115,95)...                  │ ← (3,3): bean 2
│  [1][2][3][4]●(141,105)...              │ ← (4,3): bean 3
│  ...                                    │
│  [1][2][3][4][5]...[13]                 │
│                                         │
└─────────────────────────────────────────┘

SpatialHash Dictionary:
{
  (2, 3): [(86, 91)],           # cell (2,3) contains bean at (86,91)
  (3, 3): [(115, 95)],          # cell (3,3) contains bean at (115,95)
  (4, 3): [(141, 105)],         # cell (4,3) contains bean at (141,105)
}

Collision Check at (150, 100):
→ Target cell: (5, 3)
→ Check 9 cells: (4,2) (5,2) (6,2) (4,3) (5,3) (6,3) (4,4) (5,4) (6,4)
→ Found bean at (141, 105) in cell (4,3)
→ Distance: sqrt((150-141)² + (100-105)²) = sqrt(81+25) = 10.3
→ Required: size + PIXEL_DISTANCE = 10 + 1 = 11
→ 10.3 < 11 → COLLISION → skip this position
```

## Component Dependencies

```mermaid
graph LR
    A["RandomPlacementStrategy"]
    B["SpatialHash"]
    C["PlacementStrategy Base"]
    D["DensityPopulationEstimator"]
    E["World"]
    F["WorldWindow"]
    
    A -->|uses| B
    A -->|extends| C
    A -->|receives count from| D
    E -->|uses| A
    F -->|uses| A
    
    style A fill:#4a90e2,color:#fff
    style B fill:#7ed321,color:#000
    style C fill:#50b3a2,color:#fff
```
