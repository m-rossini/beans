```mermaid
graph TD
    A[World Update Cycle] --> B[WorldWindow.on_update()]
    B --> C[For each bean in world]
    C --> D[BeanSprite.update_from_bean(bean)]
    D --> E[Calculate scale_factor = bean.size / initial_diameter]
    E --> F[Set sprite.scale = scale_factor]
    F --> G[Arcade renders scaled sprite]

    H[Energy System] --> I[apply_energy_system()]
    I --> J[Bean size changes via fat storage/burning]
    J --> K[Bean.size property updated]

    L[Test Validation] --> M[test_update_from_bean]
    M --> N[Create bean with different sizes]
    N --> O[Call update_from_bean()]
    O --> P[Assert sprite.scale matches expected ratio]

    classDef process fill:#e1f5fe
    classDef data fill:#f3e5f5
    classDef test fill:#e8f5e8

    class A,B,C,D,E,F,G process
    class H,I,J,K data
    class L,M,N,O,P test
```</content>
<parameter name="filePath">c:\dev\DevProjects\beans\summaries\2025-01-13-sprite-size-scaling-diagram.md