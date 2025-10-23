---
doc_id: process-model-update
title: "UPDATE Processes"
description: "UPDATE process behavior, section targeting, and workflows for modifying existing artifacts"
keywords: [update, process-model, section-updates, patch-template, target-definition]
relevance: "Use this document to understand UPDATE process structure and how existing artifacts are modified through section targeting"
---

# UPDATE Processes

UPDATE processes locate existing artifacts and modify specific sections or entire documents.

## File Requirements

### Required Files
- **`artifact/locator.jsonnet`** - Configuration for finding artifacts (shared with GET)
- **`artifact/parser.jsonnet`** - ID normalization rules (shared with GET, optional for singleton)
- **`artifact/patch.md`** - Jinja2 template for replacement content
- **`schema.jsonnet`** - Data contract for update parameters
- **`routine.md`** - Step-by-step instructions
- **`permissions.jsonnet`** - Access control rules

### Optional Files
- **`artifact/target.jsonnet`** - Section bounds definition (presence enables multi-section)
- **`artifact/sections/<section>.md`** - Individual section templates for includes

## Single-Section vs Multi-Section

### Single-Section (No `target.jsonnet`)
- Performs **whole document replacement**
- Flat schema structure (no `section_updates` wrapper)
- Simple `patch.md` template replaces entire content

### Multi-Section (Has `target.jsonnet`)
- Performs **targeted section updates**
- Nested `section_updates` schema structure
- `patch.md` uses iteration and includes for sections
- Preserves other sections not being updated

## INSERT Modes

UPDATE processes support non-destructive section modifications:
- **`--insert-mode=append`**: Adds content at section end
- **`--insert-mode=prepend`**: Adds content at section start
- **Default**: Replaces entire section content

Example: `pantheon execute update-progress --insert-mode=append --from-file entry.json --actor dev`

## Workflow

1. Agent discovers sections: `pantheon get sections update-ticket --actor engineer`
2. Agent creates JSON with section updates
3. Agent executes: `pantheon execute update-ticket --id T001 --from-file updates.json --actor engineer`
4. Framework locates artifact using `locator.jsonnet` and `parser.jsonnet`
5. Framework renders `patch.md` with section data
6. Framework replaces targeted sections using `target.jsonnet` bounds
7. Framework saves modified artifact to same location

---

**Related:** [Process Model Overview](overview.md) | [GET Processes](get-processes.md) | [Single-Section Simplification](single-section-simplification.md)
