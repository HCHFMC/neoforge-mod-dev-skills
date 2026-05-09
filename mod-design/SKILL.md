---
name: mod-design
description: Design Minecraft NeoForge mod features from requirements. Use this skill when the user asks to design a mod feature, plan a block/item/machine, create design documents for Minecraft development, or says "设计一个XXX". This skill researches the LLM Wiki knowledge base, selects appropriate patterns, and produces a design document in docmd/design/. ALWAYS use this skill before mod-build when creating new mod content.
compatibility: Requires LLM Wiki KB at configurable path (default D:\LLM WIKI\Minecraft-neoforge-new-Version\)
---

# Mod Design Skill

## Purpose
Transform a user's mod feature request into a complete design document, informed by the LLM Wiki knowledge base's verified patterns. Output a docmd/design/<feature>.md ready for implementation by mod-build.

## KB_PATH
```
Default: D:\LLM WIKI\Minecraft-neoforge-new-Version\
If not found: ask user for path, save response.
```

## Before Anything: Learn the KB

This skill requires navigating the LLM Wiki. Read `references/kb-navigation.md` now if you haven't already in this session. It explains: how index.md works, how pattern files are structured (skeleton → full code → API records), and where to find JSON formats, mod source references, and design notes.

## Pre-Flight Check

Before starting, verify:
1. KB_PATH exists and contains `wiki/index.md`
2. User's working directory has `docmd/design/` (create if missing)
3. Read `references/design-conventions.md` for MC design standards

## Workflow

### Stage A: Requirement Clarification

```
1. Ask clarifying questions:
   - What does this feature do? (one sentence)
   - Is it a Block, Item, Machine, Entity, or something else?
   - Does it interact with existing systems (energy, inventory, GUI)?
   - Any special behaviors or constraints?

2. Determine feature scope:
   - "这个功能比太阳能板简单/复杂/差不多？"

✋ CONFIRM: Summarize your understanding in one paragraph. Get user agreement before proceeding.
```

### Stage B: Knowledge Base Research

```
1. Read KB_PATH/wiki/index.md → locate matching patterns

2. For each candidate pattern:
   a. Read the "Skeleton" section (30 lines) → confirm it matches
   b. Check "API Verification Records" at the bottom → any known issues?
   c. Check "Contradiction Records" → any API drift warnings?

3. If no exact pattern exists:
   a. Read KB_PATH/raw/mod-sources/<mod>/SUMMARY.md for similar implementations
   b. Search KB_PATH/raw/framework-tests/ for official NeoForge test examples
   c. Identify the closest pattern and what needs adaptation

4. Note which JSON formats will be needed:
   → Read KB_PATH/wiki/06-data-json/index.md

✋ CONFIRM: Show pattern selection with brief justification.
  "This feature uses: [pattern-A] for base, [pattern-B] for GUI.
   These are all Tier 1-2 verified patterns. Any concerns?"
```

### Stage C: Research Mod References (if needed)

```
If the feature involves an unfamiliar mechanic:
  1. Read KB_PATH/raw/mod-sources/<relevant-mod>/SUMMARY.md
  2. Navigate to specific source files for implementation details
  3. Extract design patterns, not code

This step is optional — skip if the KB patterns already cover the feature.
```

### Stage D: Write Design Document

```
Write to docmd/design/<feature>.md using this structure:

# [Feature Name] — Design Document

## 1. Overview
One paragraph. What it does. How it fits with existing content.

## 2. Core Mechanism
How it works. Key algorithm/formula if applicable.
Include: conditions, inputs, outputs, state transitions.

## 3. Design Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
(Compare with existing machines/blocks for balance)

## 4. Configuration
New Config.java entries with names, defaults, ranges, comments.

## 5. File Checklist
### New Files
| File | Pattern Source | Est. Lines |
|------|---------------|------------|

### Modified Files
| File | Changes |
|------|---------|

## 6. Pattern Cross-Reference
| What I Need | KB Pattern |
|------------|-----------|
(One row per file/concern, with wiki path)

## 7. Recipe (if applicable)
Shaped/shapeless recipe JSON.

✋ CONFIRM: User reviews the design document before any implementation.
  "Design complete. Review and let me know if anything needs adjustment."
```

## Key Rules

1. **Learn before design**: Always read KB patterns before proposing a design. Never design from memory.

2. **Prefer existing patterns**: If a KB pattern covers 80% of the feature, design the remaining 20% as customization points — don't invent a new pattern.

3. **Design for consistency**: New features should feel like they belong with existing ones. Match energy rates, GUI styles, and naming conventions from already-implemented features.

4. **Confirm before document**: Don't write the design document until the user has approved the pattern selection (Stage B checkpoint).

5. **Reference, don't copy**: When citing mod source examples, reference file paths in `raw/mod-sources/` rather than copying large code blocks into the design doc.
