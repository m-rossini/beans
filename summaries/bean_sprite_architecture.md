```mermaid
graph TD
    A[World] --> B[Bean Logic]
    A --> C[BeanSprite Rendering]
    B --> D[Age, Energy, Sex]
    C --> E[Position, Color, Size]
    F[BeansConfig] --> G[initial_bean_size]
    F --> H[male_bean_color]
    F --> I[female_bean_color]
    G --> J[Population Density]
    G --> K[Sprite Diameter]
    H --> L[Male Bean Color]
    I --> M[Female Bean Color]
    C --> N[Arcade Sprite]
    N --> O[Circle Texture]
```</content>
<parameter name="filePath">c:\dev\DevProjects\beans\summaries\bean_sprite_architecture.md