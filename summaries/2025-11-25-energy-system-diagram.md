```mermaid
flowchart TD
    BeansConfig --> Bean
    Bean -->|energy_tick| EnergyCalc[Energy calculation]
    Bean --> World
    World --> Beans[Active beans]
    EnergyCalc --> DeadBeanList[Dead bean list (reason)]
    Beans -->|zero energy| DeadBeanList
    World --> DeadBeanList
```