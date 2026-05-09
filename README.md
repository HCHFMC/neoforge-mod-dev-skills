# Mod Dev — OpenCode Skills for Minecraft NeoForge Mod Development

A pair of skills that guide AI agents through the complete NeoForge mod development lifecycle: from design research in the LLM Wiki knowledge base, through code generation and resource creation, to knowledge base feedback.

## What This Does

```
User: "做一个风力发电机"
  ↓
mod-design → researches KB patterns → writes design doc
  ↓ (user approves)
mod-build  → copies verified code skeletons → generates textures
           → compiles → BUILD SUCCESS → files discoveries back to KB
  ↓
The KB gets smarter. The next feature takes half the time.
```

## Skills

| Skill | Purpose | Triggers When |
|-------|---------|---------------|
| `mod-design` | Research KB, select patterns, write design docs | "设计一个XXX", "帮我规划 mod 功能" |
| `mod-build` | Generate code, textures, models; compile; feedback KB | "实现XXX", "按设计文档写代码" |

## Prerequisites

- **LLM Wiki KB**: A NeoForge knowledge base built on the [Karpathy LLM Wiki pattern](https://karpathy-wiki.lol/en). Place it at `<project-root>/kb/` (portable, per-project). The skills auto-detect and fall back to asking the user.
- **JDK 21 + Gradle**: For building the mod.
- **Python 3**: For texture generation (`gen_textures.py` in `mod-build/scripts/`).
- **Blockbench** (optional): Only needed for Tier 2 complex block models (≥5 cubes). The MCP tool `ashfox-blockbench_*` is detected automatically.

## Installation

Copy both skill directories into your OpenCode skills folder:

```
# Linux/macOS
cp -r mod-design ~/.config/opencode/skills/
cp -r mod-build ~/.config/opencode/skills/

# Windows
xcopy mod-design %USERPROFILE%\.config\opencode\skills\mod-design\ /E
xcopy mod-build %USERPROFILE%\.config\opencode\skills\mod-build\ /E
```

Or install as `.skill` files via the OpenCode skill manager.

## Where the Skills Read From

```
LLM Wiki KB (external, read-only)
  D:\LLM WIKI\Minecraft-neoforge-new-Version\
  ├── wiki/index.md           ← Pattern quick-reference (read first on every query)
  ├── wiki/01-foundation/     ← @Mod entry, config, creative tabs
  ├── wiki/02-blocks/         ← Blocks with/without BlockEntity
  ├── wiki/03-energy/         ← Energy generators, consumers, variants
  ├── wiki/04-items/          ← Items, tools, armor, tooltips
  ├── wiki/05-gui/            ← Menu+Screen with/without slots
  ├── wiki/06-data-json/      ← JSON formats (recipes, tags, models, loot)
  ├── raw/mod-sources/        ← 9 reference mods (Create, Mekanism, GregTech...)
  └── raw/framework-tests/    ← NeoForge official test code

Your Mod Project (read-write)
  ├── docmd/design/           ← Design documents written by mod-design
  ├── src/main/java/          ← Java code written by mod-build
  └── src/main/resources/     ← Assets written by mod-build
```

## Workflow Example

### Designing a Feature

```
User: 设计一个地热发电机，放岩浆上方发电
Agent: (mod-design triggers)
  1. Reads wiki/index.md → finds energy-variants, energy-generator patterns
  2. Reads energy-variants.md skeleton → confirms geothermal variant exists as placeholder
  3. Researches LAVA/MAGMA_BLOCK detection APIs
  4. ✋ Shows pattern selection: "This needs energy-generator + energy-variants + gui-display"
  5. User approves
  6. Writes docmd/design/geothermal_generator.md
```

### Implementing a Feature

```
User: 实现地热发电机
Agent: (mod-build triggers)
  1. Reads docmd/design/geothermal_generator.md
  2. Copies energy-generator pattern → replaces class names → overrides canGenerate()
  3. Copies gui-display pattern → creates Menu+Screen
  4. Runs gen_textures.py for geothermal textures
  5. Writes JSON resources (blockstate, recipe, tags, lang)
  6. Runs .\gradlew.bat build --no-daemon → BUILD SUCCESS (0 errors)
  7. Files back: updates energy-variants.md from [placeholder] → verified code
```

## What's Inside

### mod-design/
```
mod-design/
├── SKILL.md                          # 140 lines: 4-stage workflow with ✋ checkpoints
└── references/
    ├── kb-navigation.md              # How to read the LLM Wiki (index→skeleton→full code)
    └── design-conventions.md         # MC design standards, color palette, balance guide
```

### mod-build/
```
mod-build/
├── SKILL.md                          # 230 lines: 5-stage workflow (code→resources→build→fileback)
├── scripts/
│   └── gen_textures.py               # Portable texture generator (3-layer architecture)
└── references/
    ├── kb-navigation.md              # Same as above — shared reference
    ├── design-conventions.md         # Same as above — for context during implementation
    ├── code-conventions.md           # MC code standards + 6 known API traps + verification rules
    └── resource-pipeline.md          # Model/texture decision tree + MCP workflow
```

## Key Design Decisions

### Why two skills, not one?
Design and implementation are different mental modes. Design needs user interaction and pattern discovery. Implementation is systematic code generation. Splitting them lets each skill be concise (~150 lines vs ~400 lines), which means better triggering accuracy and less token waste.

### Why is FILE BACK part of mod-build, not a separate skill?
FILE BACK only ever runs after BUILD SUCCESS, which only happens in mod-build. It's the last stage of implementation, not an independent workflow.

### Why not bundle the LLM Wiki KB?
The KB is 13,000 files / 135MB — a full knowledge base with 9 mod reference sources. Embedding it would make the skill unmanageable. Instead, the skill references it by configurable path, falling back to asking the user.

### Where does the texture generator come from?
`gen_textures.py` is the actual Python script used to generate all textures for SolarMod. It uses a 3-layer architecture: material functions (Level 1) → UV atlas layout (Level 2) → model binding (Level 3). Bundled in `mod-build/scripts/` so it's portable across machines.

## Proven Results

During development, these skills (then as manual workflow) produced:

| Feature | KB queries | Compile errors | Time to BUILD SUCCESS | Pattern reuse |
|---------|-----------|----------------|----------------------|---------------|
| Wind Turbine (before skills) | 10+ / 4 agents | 2 | ~60 min | ~60% |
| Geothermal Generator (after skills) | 2 | 0 | ~10 min | ~90% |

## License

MIT — same as SolarMod.
