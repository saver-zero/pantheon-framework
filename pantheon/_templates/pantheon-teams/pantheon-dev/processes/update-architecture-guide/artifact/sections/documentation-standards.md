# Documentation Standards
last updated: {{ pantheon_timestamp }}
updated by: {{ pantheon_actor }}

## 1. Philosophy and Purpose

This document outlines the standards for creating, organizing, and managing all documentation assets, including text and diagrams.

### The Challenge: Engineering Context for AI Agents

AI agents, particularly in a Retrieval-Augmented Execution (RAE) system, do not "read" or "browse" documentation like humans. They perform targeted retrieval operations to acquire specific knowledge needed for a task. When documentation is unstructured-existing as large, monolithic files or a disorganized collection of documents-it becomes a significant obstacle to building reliable agentic workflows.

### Our Goal: A Retrieval-Friendly Knowledge Base

To solve this, our goal is to create a **retrieval-friendly knowledge base**. By enforcing a structured format, we transform our documentation from a simple collection of human-readable text into a queryable, API-like system for knowledge. This enables precise, reliable retrieval, which is the foundation for effective Context Engineering and, ultimately, for building dependable AI agents.

## 2. Core Principles

- **Topic-Oriented:** Content is organized around specific, orthogonal concepts (e.g., "Database," "API Client").
- **Co-location:** All assets for a single topic-both text and diagrams-must be located in the same directory.
- **Single Source of Truth (SSoT):** Every concept must have one, and only one, canonical document or diagram.
- **Discoverability First:** The structure must be optimized for search and navigation via metadata and a master index.

## 3. Content Philosophy: What to Document

Our guiding principle is: **document the *why*, not the *what*.** The code shows the action; the docs must explain the reasoning.

- **Document Decisions:** Explain architectural choices and trade-offs. For major decisions, create an **Design Decision Doc** using `pantheon get process create-design-decision --actor <your_agent_name>`
- **Document the Non-Obvious:** Focus on complex algorithms, counter-intuitive logic, or critical side-effects.
- **Document Contracts and Boundaries:** Clearly define the public API of a component-its inputs, outputs, and guarantees.
- **Avoid Paraphrasing Code:** Never write documentation that simply translates a line of code into English.

### Example: High-Signal vs. Low-Signal Documentation

**Anti-Pattern (Low-Signal):**
```python
# This function gets the user by their ID.
def get_user(user_id):
  return db.get(user_id)
```

**Good Pattern (High-Signal):**
```python
# Retrieves a user object, intentionally omitting the 'permissions' field
# to prevent a circular dependency with the auth service.
# Permissions must be fetched separately via `auth_service.get_permissions(user_id)`.
def get_user(user_id):
  return db.get(user_id, exclude_fields=['permissions'])
```

## 4. Unified Directory Structure

All documentation assets must be co-located within topic-specific directories under the  main <docs> folder. Use `pantheon get team-data --key path.docs --actor <your_agent_name>` to get the main <docs> folder.

```
<docs>/
├── README.md
├── _includes/
│   └── plantuml-style.puml
└── database/
    ├── overview.md
    ├── schema-diagram.puml
    └── connection-sequence.puml
```

### 4.1. Defining Orthogonal Topics

To prevent fragmentation, topics must be as orthogonal (non-overlapping) as possible.

- **Litmus Test:** Before creating a new topic directory, ask: "Can this concept be fully explained without extensively detailing another topic?"
- **Handling Overlap:** For naturally related concepts (e.g., "authentication" and "authorization"), place the more specific concept as an article within the broader topic directory. If "authorization" becomes sufficiently complex, it can be nested: `<docs>/authentication/authorization/`.
- **Evolution:** The documentation `owner` is responsible for refactoring topics (splitting or merging) as the system evolves to maintain orthogonality.
- **Nesting:** One level of subdirectory nesting is permitted for grouping within a complex topic. Deeper nesting is discouraged.

## 5. The Master Index (`<docs>/README.md`)

The `<docs>/README.md` file is the single entry point for the entire knowledge base. It must index all assets.

- **Format:** Each list item must be `* **[Asset Title](./relative/path/to/file):** One-sentence relevance description.`
- **Automation:** This file should be automatically generated from asset metadata to ensure it is never out of sync.

**Example:**
```markdown
# Documentation Index

## Database Module

*   **[Database Overview](./database/overview.md):** The canonical explanation of the database module's role and schema.
*   **[Connection Sequence](./database/connection-sequence.puml):** A sequence diagram showing how a service connects to the database.
```

## 6. Asset-Specific Standards

Every file must contain structured metadata to make it discoverable.

### 6.1. Metadata Schema

| Field           | Type         | Required | Description                                                 |
|-----------------|--------------|----------|-------------------------------------------------------------|
| `doc_id`        | `string`     | Yes      | Globally unique, immutable ID (e.g., `database-overview`).  |
| `title`         | `string`     | Yes      | The formal, human-readable title.                           |
| `description`   | `string`     | Yes      | A concise, one-sentence summary of the asset's purpose.     |
| `keywords`      | `string[]`   | Yes      | A list of relevant search tags.                             |
| `relevance`     | `string`     | Yes      | Natural language explanation of when this asset is useful.  |

### 6.2. Text Articles (`.md` files)

Markdown articles must begin with a YAML frontmatter block containing the metadata.

```markdown
---
doc_id: database-overview
title: "Database Overview"
description: "The canonical explanation of the database module's role and schema."
keywords: [database, schema, storage, postgres]
relevance: "Use this document to understand the database module's schema, tables, and core responsibilities."
---

# Database Overview
...
```

### 6.3. Diagrams (`.puml` files)

PlantUML files must begin with `@startuml`, follwed by a structured metadata block using block comments.

```plantuml
@startuml
/'
@id: database-connection-sequence
@title: Database Connection Sequence
@description: A sequence diagram showing how a service connects to the database.
@keywords: [diagram, sequence, database, connection, pooling]
@relevance: "Use this diagram to visualize the handshake and connection pooling sequence for the primary database."
'/
' Import shared styles for consistency
!include ../_includes/plantuml-style.puml

title Database Connection Sequence
...
@enduml
```

#### 6.3.1. Choosing the Right Diagram

Use the following matrix to select the appropriate diagram type. Multiple diagrams for a single topic are encouraged if multiple perspectives are needed.

| If you want to show...                          | Then use a...                |
|-------------------------------------------------|------------------------------|
| How components fit together at a high level     | **System/Container Diagram** |
| The step-by-step flow of a request or process   | **Sequence Diagram**         |
| The internal parts of a single service/module   | **Component Diagram**        |

#### 6.3.2 Syntax
Diagram must follow jebbs Compatibility Rules

**For Sequence Diagrams:**
- Use block `note over X[,Y] ... end note`, or inline notes with `\n` for newlines
- Attach notes to participants (e.g., `note right of CLI : ...`)
- Do not use `note as <name>` or floating notes

**For Component Diagrams:**
- Interfaces do NOT support brace syntax - declare them without opening/closing braces
- Use `note right of InterfaceName`, `note left of InterfaceName`, etc. for interface documentation
- Only components support the brace syntax for defining internal structure

**For Class Diagrams:**
- Use `note right of ClassName`, `note left of ClassName`, `note top of ClassName`, or `note bottom of ClassName`
- Do NOT use `note on link` syntax (not supported by PlantUML renderers)
- Explain relationship cardinality in the legend or class notes instead

## 7. Cross-Referencing

- **Method:** Always use relative paths (e.g., `../database/overview.md`) for links between documents. This ensures portability.

## 8. Search and Retrieval Patterns

To make content retrieval-friendly, write metadata with search in mind.

- **Keywords:** Use a mix of general and specific terms. Include the asset type, the primary component, and the core concepts (e.g., `[diagram, sequence, database, connection]`).
- **Relevance:** Write this as a direct answer to the question, "When should I use this?" Example: "Use this diagram to visualize the handshake and connection pooling sequence for the primary database."
- **Example Queries:** An agent can combine metadata for precise retrieval:
  - `search(keywords: "sequence" AND "database")` -> Finds all sequence diagrams for the database.
  - `search(status: "deprecated" AND owner: "data-team")` -> Finds all outdated docs owned by the data team.