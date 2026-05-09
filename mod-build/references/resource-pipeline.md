# Resource Pipeline — Texture & Model Decision Tree

## Quick Decision

```
Block model?
├── 1 cube, simple shape → Hand-write JSON (cube_bottom_top or parent)
├── 2-4 extra elements → Tier 1: Hand-write JSON with elements[] array
└── 5+ cubes, complex → Tier 2: Blockbench MCP (ashfox-blockbench_*)

Item texture?
├── Flat item → JSON (item/generated) + Python 16×16 PNG
└── Block item → JSON (parent → block model)

GUI background?
└── Python 256×256 PNG (gen_textures.py → gen_gui())
```

## Python Textures (gen_textures.py)

Located at `scripts/gen_textures.py` (relative to this SKILL.md).

### Three-Level Architecture

```
Level 3: Model Binding     gen_wind_turbine() → wind_turbine.png
Level 2: UV Atlas Layout   atlas_regions(w, h, regions_dict)
Level 1: Material Functions metal_brushed(), grid_panel(), brick_refractory(), leather_stitched(), card_gold()
```

### Material Functions Reference

| Function | Use For | Parameters |
|----------|---------|-----------|
| `metal_brushed(w, h, base, highlight, shadow, noise_pct)` | Machine housing, pillars, frames | base/highlight/shadow: HEX colors |
| `grid_panel(w, h, base, grid, cell, line)` | Solar panel surface | cell: grid spacing in px |
| `brick_refractory(w, h, brick, mortar, brick_w, brick_h)` | Geothermal base, furnace | brick_w/h: brick size in px |
| `leather_stitched(w, h, base, flap, stitch, buckle, flap_y)` | Backpack, bags | flap_y: where flap meets body |
| `card_gold(w, h, base, border, inner_border, icon, highlight)` | Upgrade cards, items | icon: center diamond color |

### Adding a New Model Texture

```python
# Add to end of gen_textures.py:

def gen_my_machine():
    w, h = 16, 16
    regions = {
        (0, 0, w, 6):   {'fn': metal_brushed, 'args': {'base': '#A8B0BC', 'highlight': '#D8DCE4', 'shadow': '#788290'}},
        (0, 6, w, 10):  {'fn': metal_brushed, 'args': {'base': '#3D3D3D', 'highlight': '#505050', 'shadow': '#2D2D2D'}},
    }
    px = atlas_regions(w, h, regions)
    png(w, h, px, f'{BASE}/block/my_machine_texture.png')

# Then call gen_my_machine() at the bottom
```

## MCP Blockbench Models (Tier 2)

Only for models with ≥5 non-trivial cubes. Use the ashfox-blockbench MCP tools.

### Workflow
```
1. ensure_project(name, format="Java Block/Item")
2. get_project_state(detail="full") → capture revision
3. for each cube:
     add_cube(name, from=[x,y,z], to=[x,y,z], ifRevision=rev)
     → receives new revision
4. assign_texture(textureName, cubeIds, ifRevision=newRev)
5. validate(ifRevision=rev) → check for UV errors
6. render_preview(mode="fixed", angle=[30,45,0])
   → ✋ CONFIRM with user
7. export(format="java_block_item_json", destPath="models/block/xxx.json")
8. Move exported JSON to assets/solarmod/models/block/
```

### Texture Strategy
Generate textures with Python FIRST, then use `assign_texture` in MCP. Do NOT use `paint_faces` for complex textures — it's for solid-color face fills only.

## File Paths Reference

| Resource | Path |
|----------|------|
| Block models | `assets/solarmod/models/block/<name>.json` |
| Item models | `assets/solarmod/models/item/<name>.json` |
| Blockstates | `assets/solarmod/blockstates/<name>.json` |
| Block textures | `assets/solarmod/textures/block/<name>.png` |
| Item textures | `assets/solarmod/textures/item/<name>.png` |
| GUI textures | `assets/solarmod/textures/gui/<name>.png` |
| Recipes | `data/solarmod/recipe/<name>.json` |
| Block tags | `data/minecraft/tags/block/mineable/pickaxe.json` |
| Item tags | `data/solarmod/tags/item/<name>.json` |
| Lang (en) | `assets/solarmod/lang/en_us.json` |
| Lang (zh) | `assets/solarmod/lang/zh_cn.json` |
