---
name: mod-build
description: Implement Minecraft NeoForge mod features from design documents to BUILD SUCCESS. Use this skill when the user asks to implement a mod feature, write mod code, build Minecraft mod content, or says "实现XXX". This skill generates Java code, resources (textures/models/JSON), compiles with Gradle, and files discoveries back to the LLM Wiki. ALWAYS use mod-design first to create the design document before implementing with this skill.
compatibility: Requires LLM Wiki KB, Python 3, Gradle+JDK21. Optional: Blockbench MCP for complex models.
---

# Mod Build Skill

## Purpose
Take a design document from mod-design and produce a complete, compilable NeoForge 1.21 mod feature. Follow verified KB patterns for code generation, use Python for textures, MCP for complex models, and file all discoveries back to the knowledge base.

## KB_PATH
```
The LLM Wiki knowledge base. Searched in order:
  1. <project-root>/kb/              ← Preferred: portable, per-project
  2. Ask user once, save to kb/.kb_path
If neither exists, ask the user where the KB is located.
```

## Prerequisites

Before starting, verify:
1. A design document exists at `docmd/design/<feature>.md` (if not, run mod-design first)
2. KB_PATH contains `wiki/index.md`
3. `scripts/gen_textures.py` is accessible (relative to this SKILL.md)

For first-time use, read:
- `references/code-conventions.md` — MC code standards + API verification rules
- `references/resource-pipeline.md` — Texture/model decision tree
- `references/kb-navigation.md` — How to use the LLM Wiki
- `references/design-conventions.md` — MC design standards (for context)

## Workflow

### Stage A: Read and Plan

```
1. Read the design document at docmd/design/<feature>.md
2. Identify all files from the file checklist:
   - New Java files → which KB pattern provides the skeleton?
   - Modified files → which sections to edit?
   - Resource files → what type (texture, model, JSON, lang)?
3. Read KB patterns needed (skeleton 30 lines first, expand <details> if confirmed)

✋ CONFIRM (only for complex features >3 new files):
  "I'll create [N] new files and modify [M] existing files. Proceed?"
```

### Stage B: Code Generation

```
JAVA FILES — Follow code-conventions.md rules:

1. For each NEW file:
   a. Copy the full pattern code from KB <details> block
   b. Replace class names, package names, MODID references
   c. Override ★-marked customization points only
   d. Keep all imports intact from the pattern
   e. Add new file to src/main/java/com/solarmod/<package>/

2. For SolarMod.java MODIFICATIONS:
   - Add imports at top
   - Add DeferredRegister entries (Block, Item, BE type, Menu)
   - Add to creative tab displayItems
   - Add to registerCapabilities()
   - Add to ClientModEvents screen registration
   Use surgical edits — never rewrite the entire file.

3. For Config.java MODIFICATIONS:
   - Add new ModConfigSpec entries BEFORE "static final ModConfigSpec SPEC = BUILDER.build();"
   - Add after the last existing config entry, before SPEC

4. For lang files:
   - Append new translation keys at end (before closing })
   - Follow naming: block.modid.name, item.modid.name, container.modid.name
```

### Stage C: Resource Generation

```
DECISION TREE for each model/texture:

Is this a block model?
├── 1 cube, simple → Write JSON directly (cube_bottom_top or parent reference)
├── 2-4 additional elements → Tier 1: Write JSON with elements[] array
└── 5+ cubes, complex shape → Tier 2: Use Blockbench MCP
    ├── ensure_project(name, format="Java Block/Item")
    ├── add_cube() × N
    ├── render_preview() → ✋ CONFIRM
    └── export(format="java_block_item_json", destPath="models/block/xxx.json")

Is this an item texture?
├── Flat item → item/generated JSON + Python 16×16 texture
└── Block item → parent reference to block model

TEXTURE GENERATION:
  Run: python scripts/gen_textures.py
  For new models: add a gen_<model>() function at bottom, then run.
  The script uses material functions (metal_brushed, grid_panel, etc.)
  with colors from references/design-conventions.md §Color Palette.

JSON DATA FILES:
  Recipes  → Follow KB_PATH/wiki/06-data-json/recipe/<type>.md
  Tags     → Follow KB_PATH/wiki/06-data-json/tags/<type>.md
  Lang     → Follow KB_PATH/wiki/06-data-json/lang.md
  Models   → Follow KB_PATH/wiki/06-data-json/block/<type>.md
```

### Stage D: Build

```
1. Run: .\gradlew.bat build --no-daemon
2. If BUILD SUCCESSFUL:
   → Proceed to Stage E (FILE BACK)
3. If BUILD FAILED:
   a. Read the COMPLETE error (not just first line)
   b. Cross-reference with KB pattern's API Verification Records
   c. Apply targeted fix based on error type:
      - "找不到符号 import" → wrong class path in KB → verify with javap on JAR
      - "方法不会覆盖" → signature mismatch → check KB's latest API record
      - "无法推断类型参数" → constructor format → check KB pattern's full code block
   d. NEVER repeat the same failing approach. Use the 3-strike protocol:
      Attempt 1: fix from error message
      Attempt 2: try alternative API (e.g., different constructor overload)
      Attempt 3: decompile JAR with javap, verify signature, ask user if still stuck

4. Re-run build after each fix
```

### Stage E: FILE BACK (Knowledge Base Improvement)

```
After BUILD SUCCESSFUL, update the KB:

1. NEW REUSABLE SKELETON?
   → Create KB_PATH/wiki/XX-category/pattern.md
   → Use KB_PATH/templates/pattern-template.md
   → Only if the code represents a new generalizable pattern, not a trivial variant

2. API MISMATCH DURING DEVELOPMENT?
   → Add Delta entry to the affected pattern's "Contradiction Records" table:
     | Date | Claimed | Actual | Status |
   → Mark as "resolved" if fixed, "pending" if workaround

3. NEW VARIANT DISCOVERED?
   → Update the variants file
   → E.g., energy-variants.md: geothermal from [placeholder] → verified code

4. SUPPLEMENTARY FILES READ during this session?
   → Add [[wikilinks]] in relevant Java patterns
   → Under "Supplemental References" section

5. Update KB_PATH/wiki/index.md if new patterns created

6. Append to KB_PATH/log.md:
   "DEV: [feature] → BUILD SUCCESS, [N] patterns updated"
```

## Critical Rules

### 1. NEVER Trust Memory
All API signatures must come from: KB API Verification Records, or JAR decompilation (javap). Never generate NeoForge API calls from LLM training data. This caused 6 compilation errors in earlier development.

### 2. Pattern First, Custom Code Last
If a KB pattern provides 90% of what's needed, copy the pattern and override only the ★ customization points. Never write a BlockEntity from scratch if energy-generator pattern covers it.

### 3. Surgical Edits
When modifying SolarMod.java, Config.java, or lang files: use precise edits. Never rewrite entire files.

### 4. BUILD SUCCESS Gates FILE BACK
No KB updates until the build passes. The FILE BACK data must come from verified, compilable code.

### 5. One Feature Per Execution
Don't implement multiple features in one session unless they share all KB patterns.
