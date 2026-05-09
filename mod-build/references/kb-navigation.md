# LLM Wiki Knowledge Base — Navigation Guide

## Architecture

```
<KB_PATH>/
├── wiki/            ← LLM-maintained pattern library (READ this)
│   ├── index.md     ← START HERE: task → pattern quick-reference
│   ├── 01-foundation/ through 14-datagen/  ← pattern files
│   └── 06-data-json/  ← JSON format references
├── raw/             ← Immutable source data (READ for research)
│   ├── mod-sources/<mod>/SUMMARY.md  ← mod package overviews
│   ├── framework-tests/              ← NeoForge official test code
│   └── design-notes/                 ← Architecture analyses
├── CLAUDE.md        ← Schema: rules that govern this KB
└── log.md           ← Operation history
```

## How to Read a Pattern File

Every pattern has this structure:

```
1. Frontmatter (YAML):
   category, neo, mc, verified, uses
   → Check "verified" date — is this still current?

2. "Skeleton" section (30 lines):
   → Quick confirmation: is this the right pattern?
   → Shows the core logic loop with ★ customization points

3. <details> Full Code:
   → Expand this to get complete, compilable code
   → Contains ALL imports — copy everything

4. Variants section:
   → Table of common modifications with links to details

5. API Verification Records (bottom):
   → Check before using! Any known issues?
   → Each entry: Class.Method | Verified Signature | Date

6. Contradiction Records (bottom):
   → Delta entries for API drift
   → Check if the API changed since the pattern was written
```

## Query Workflow

```
1. Read index.md → find matching pattern name
2. Read pattern's skeleton (30 lines) → confirm match
3. Check API Verification Records → any known issues?
4. Expand <details> for full code if implementing
5. Read JSON references (06-data-json/) if writing data files
```

## When a Pattern Doesn't Exist

```
1. Read raw/mod-sources/<mod>/SUMMARY.md for package overview
2. Navigate to specific source files for implementation details
3. Read raw/framework-tests/ for NeoForge official test examples
4. Extract design patterns, copy file paths as references
```

## Wikilink Format

```
[[filename]] → Obsidian internal link to another wiki page
[[06-data-json/index]] → Use dir/filename when names conflict
```

## Common Pitfalls

- **Skipping API Verification Records**: Always check before implementing. Patterns older than 90 days may have API drift.
- **Trusting the skeleton alone**: The skeleton is for confirmation, not implementation. Expand <details> for actual code.
- **Missing imports**: The <details> block has all imports. Copy the complete block, don't reconstruct.
