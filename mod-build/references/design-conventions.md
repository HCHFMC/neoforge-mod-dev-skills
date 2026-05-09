# Minecraft Mod Design Conventions

## Vanilla+ Design Philosophy

### Core Principles
- **Not photorealism** — 16×16 pixel art style, not HD
- **Not excessive geometry** — use textures to express details before adding cubes
- **Industrial cleanliness** — renewable energy theme: clean lines, no rust/grime
- **Silhouette distinctiveness** — each machine should be recognizable from 20 blocks away

### Design Constraints
- Block models: ≤20 elements, ≤30 visible faces
- Textures: 16×16 default, 32×32 only when 16×16 can't express required detail
- GUI: 176×166 standard container size

## Balance Guidelines

### Energy Tiers (FE/t)

| Machine Type | Base Output | Capacity | Work Time | Space Requirements |
|-------------|------------|----------|-----------|-------------------|
| Solar Panel | 20 FE/t | 100,000 FE | Daytime only | 1 block sky access |
| Wind Turbine | 32 FE/t (peak) | 200,000 FE | 24/7 (weather-dependent) | 8 blocks clearance |
| Geothermal | 15 FE/t (lava) | 100,000 FE | 24/7 (source-dependent) | 1 block below hot source |

### Cost Scaling
More powerful → more expensive recipe. Wind (32 FE/t) costs redstone blocks + iron bars. Solar (20 FE/t) costs glass + iron. Geothermal (15 FE/t) costs obsidian + lava bucket.

## Color Palette — SolarMod

### Metals (Machine Housing)
```
Highlight: #D8DCE4   Base: #A8B0BC   Shadow: #788290   Deep: #505A68
```

### Accent Colors (Per Device)
```
Solar Panel Blue:    #2563EB → #1D4ED8 → #1E3A8A
Wind Turbine Blue-Gray: #94A3B8 → #7C8FA0 → #5C7080
Geothermal Orange:   #EA580C → #C2410C → #9A3412
Energy (universal):  #06B6D4 → #0891B2 → #0E7490
Upgrade Card Gold:   #EAB308 → #CA8A04 → #A16207
```

### Background / Neutral
```
GUI Background: #C6C6C6 (main), #8B8B8B (player area)
GUI Border:     #373737 (outer), #1A1A1A (inner)
Leather Brown:  #8B6914 → #A0781E → #6B4E12 → #4A3510
Dark Base:      #3D3D3D → #2D2D2D → #1E1E1E
```

### Tone Shift Rule (Vanilla Style)
**Lighter → warmer (yellow shift). Darker → cooler (blue/purple shift).**

Example for gray metal:
```
#D8DCE4 (warm light) → #A8B0BC (neutral) → #788290 (cool shadow) → #505A68 (blue-dark)
```

## Texture Drawing Rules

- **NO pure black** #000000, **NO pure white** #FFFFFF (except glowing centers)
- **Edge highlighting**: top/left edges +1px brightness. Bottom/right edges -1px darkness
- **Material noise**: metal ≤3% single-pixel noise. Stone 5-10%
- **Dithering**: checkerboard pattern to transition colors (no smooth gradients)
- **2px alignment**: all internal details snap to 2px grid

## Naming Conventions

### Block IDs: `snake_case`, all lowercase
```
✅ solar_panel, wind_turbine, geothermal_generator
❌ SolarPanel, wind-turbine
```

### Translation Keys
```
block.modid.name      → Block item name
item.modid.name       → Non-block item name
container.modid.name  → GUI/Menu title
tooltip.modid.name    → Item tooltip text
itemGroup.modid       → Creative tab name
```

## Reference
For complete texture/model specifications, see `modeling_texturing_scheme.md` in the project's docmd/design/ directory.
