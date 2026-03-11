# Item Flow Diagram - Current Game Stage

This diagram represents the item and production-chain vision for the current stage of Capital Farm.

```mermaid
flowchart TD

%% Plantacoes
A[Trigo] --> B[Farinha]
B --> C[Pao]

M[Milho] --> D[Racao]
D --> E[Galinha]
E --> F[Ovos]

%% Consumo de trabalhadores
C --> G[Trabalhadores]
F --> G

%% Producao agricola
G --> H[Producao Agricola]

%% Combustivel
M --> I[Etanol]
S[Soja] --> J[Oleo]
J --> K[Biodiesel]

I --> L[Maquinas]
K --> L

L --> H

%% Fertilidade
E --> N[Esterco]
N --> O[Fertilizante]

O --> A
O --> M
O --> S
```

## Interpreting The Diagram

- `Trigo` can be processed into `Farinha`, which can be processed into `Pao`.
- `Milho` can be turned into `Racao`, which supports `Galinha`, which produces `Ovos`.
- `Pao` and `Ovos` support `Trabalhadores`.
- `Milho` can also generate `Etanol`.
- `Soja` can generate `Oleo`, which can become `Biodiesel`.
- `Etanol` and `Biodiesel` support `Maquinas`.
- `Galinha` also produces `Esterco`, which becomes `Fertilizante` and feeds crop production again.

## Design Use

This file is intended as a high-level production/economy reference for backend and Unity planning. It is not the source of truth for balancing values or implementation details.
