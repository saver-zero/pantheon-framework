---
created_at: 2025-10-03 HH:MM PM PDT
created_by: tech-lead
---
<!-- SECTION:START:PROJECT_CONTEXT -->
## Project Context
last updated: 2025-10-03 HH:MM PM PDT
updated by: tech-lead

### Problem Statement

AI development workflows suffer from prompt drift, output inconsistency, and lack of systematic improvement. Traditional AI agent systems are black boxes where process logic is invisible, making debugging difficult and preventing teams from learning and improving over time.

### Business Outcomes

- Eliminate prompt drift by externalizing process logic into version-controlled Routines
- Achieve consistent artifact formatting through JSON Schema to Jinja2 Template workflow
- Enable systematic process improvement through structured feedback loops
- Provide complete audit trail for AI-assisted development decisions
- Support multi-team isolation with portable Team Packages

### Key Features

- **Retrieval-Augmented Execution**: Externalizes task-specific logic into Routines retrieved at runtime, preventing prompt drift and enabling process evolution
- **Unified Execute Model**: Single command interface for CREATE, UPDATE, GET, and BUILD operations with operation type determined by file conventions
- **Convention Over Configuration**: Standardized directory structures and filenames enable dynamic process discovery without complex configuration
- **Context-Aware Schema Composition**: Profile-driven schema adaptation through Jsonnet context injection enables team customization without file duplication
- **Closed-Loop Artifact System**: Framework operates exclusively on artifacts it created, ensuring traceability and enabling systematic artifact lifecycle management
- **Actor-Based Security**: Declarative permissions with agent validation and sandboxed artifact output provide governance without complexity
<!-- SECTION:END:PROJECT_CONTEXT -->

<!-- SECTION:START:HIGH_LEVEL_OVERVIEW -->
## High Level Overview
last updated: 2025-10-03 HH:MM PM PDT
updated by: tech-lead

### System Function
The Pantheon Framework is an operating system for containerized AI teams that implements Retrieval-Augmented Execution to orchestrate development workflows. It packages AI agents and processes into portable Team Packages, externalizes process logic into version-controlled Routines, and enforces strict JSON-to-template workflows for consistent artifact generation. The framework provides transparent, auditable, and systematically improvable AI development workflows through its Glass Box philosophy.

### Architectural Approach
The framework implements a layered architecture with strict separation of concerns: CLI presentation layer, ProcessHandler application layer, and specialized service components. The Pantheon Workspace acts as a facade encapsulating filesystem knowledge and providing content-retrieval methods, while the Artifact Engine focuses on pure computation. Dependency inversion through FileSystem abstraction enables testability, and Protection Proxy pattern with PantheonPath objects enforces architectural boundaries. The system enforces convention over configuration with standardized directory structures accessed exclusively through Workspace abstraction methods.

### Key Technologies
Python 3.9+ provides the runtime environment with pathlib for path operations. Jsonnet enables context-aware schema composition with profile injection via external variables. Jinja2 handles template rendering with built-in framework variables and custom filters. YAML serves as the configuration format for team profiles and project settings. The framework uses standard library components for core functionality, minimizing external dependencies and ensuring portability.<!-- SECTION:END:HIGH_LEVEL_OVERVIEW -->

<!-- SECTION:START:CORE_PRINCIPLES -->
## Core Principles
last updated: 2025-10-03 HH:MM PM PDT
updated by: tech-lead

### Transparency Over Opacity

**Principle**: Every workflow step must be visible through routines, schemas, and templates

**Rationale**: Traditional AI workflows are black boxes. Making processes visible enables debugging, auditability, and collaborative improvement.

**Examples**:
- Process logic externalized into human-readable routine.md files
- Data contracts defined explicitly in schema.jsonnet files
- All decisions recorded in version-controlled artifacts

### Mechanical Reliability Over Prompt Elegance

**Principle**: Use structured processes with templates rather than crafting perfect prompts

**Rationale**: Prompts drift over time. Structured JSON-to-template workflows produce consistent outputs regardless of prompt variations.

**Examples**:
- Agents generate structured JSON data, framework handles formatting
- Templates enforce output consistency independent of agent behavior
- Schema validation ensures data integrity before template rendering

### Systematic Learning Over Ad-hoc Fixes

**Principle**: Improve processes systematically through version-controlled changes

**Rationale**: Ad-hoc fixes solve immediate problems but lose knowledge. Version-controlled processes enable systematic improvement benefiting all future executions.

**Examples**:
- Team Packages are software artifacts that can be iterated and shared
- Process updates automatically apply to all agents using that process
- Feedback loops identify patterns for process-level improvements

### Separation of Concerns

**Principle**: Each component has a single, well-defined responsibility within its architectural layer

**Rationale**: Layered architecture with clear boundaries ensures components are decoupled, testable, and modifiable in isolation.

**Examples**:
- CLI handles presentation, ProcessHandler contains business logic, Workspace manages filesystem
- Artifact Engine performs pure computation, Workspace orchestrates I/O
- PantheonPath objects prevent computational components from performing I/O

### Convention Over Configuration

**Principle**: Use standardized structures with runtime discovery rather than explicit configuration

**Rationale**: Conventions reduce cognitive load and configuration complexity while enabling dynamic process discovery.

**Examples**:
- Process names map to directories without registration
- Conventional filenames enable automatic process type detection
- Workspace content-retrieval methods hide path complexity from other components

### Dependency Inversion

**Principle**: High-level components depend on abstractions, not volatile implementation details

**Rationale**: Abstracting filesystem operations through dependency injection enables testability without external dependencies.

**Examples**:
- Workspace receives FileSystem instance via constructor injection
- Unit tests inject mock FileSystem for in-memory testing
- Artifact Engine produces PantheonPath proxies, Workspace unwraps for I/O

### Pragmatism and YAGNI

**Principle**: Build the simplest solution that meets current requirements with clear extension points

**Rationale**: Over-engineering creates unnecessary complexity. Building minimal viable architecture with seams enables future extension when needed.

**Examples**:
- Single concrete FileSystem class provides testability seam without abstract interface
- Name-based actor model provides sufficient security without token complexity
- Framework focuses on process orchestration, not code execution


## Anti-Patterns

### Direct File I/O in Business Logic

**What to Avoid**: Components performing file operations directly instead of using Workspace abstraction

**Why It's Problematic**: Breaks testability, couples components to filesystem, prevents sandboxing enforcement

**Instead, Do This**: Use Workspace content-retrieval methods that return content directly. Only Workspace unwraps PantheonPath objects for I/O.

### Path Construction Outside Workspace

**What to Avoid**: Components building file paths manually instead of using Workspace methods

**Why It's Problematic**: Duplicates filesystem knowledge, breaks convention encapsulation, prevents multi-team isolation

**Instead, Do This**: Use Workspace methods like get_process_schema(process_name) that take process names and return content

### Profile Logic in Templates

**What to Avoid**: Templates checking pantheon_profile settings to determine what to render

**Why It's Problematic**: Spreads profile logic between schemas and templates, makes behavior harder to understand and test

**Instead, Do This**: Use Smart Schema pattern where profiles control schema fields, templates render based on data presence

### Hardcoded Artifact Paths

**What to Avoid**: Processes using hardcoded paths to artifacts instead of finder patterns

**Why It's Problematic**: Breaks artifact location abstraction, prevents artifact root customization, couples to specific directory structure

**Instead, Do This**: Define locator.jsonnet and parser.jsonnet files for dynamic artifact finding and ID normalization

### Writing to pantheon-teams Directory

**What to Avoid**: Processes writing directly to source directories instead of staging in artifacts root

**Why It's Problematic**: Bypasses review workflow, breaks closed-loop artifact system, prevents manual approval gate

**Instead, Do This**: All process outputs save to pantheon-artifacts directory for review before manual promotion to source

### Multiple Abstract FileSystem Interfaces

**What to Avoid**: Creating FileSystemProtocol, FileSystemPort, and other abstract interfaces prematurely

**Why It's Problematic**: Adds complexity without current benefit, violates YAGNI principle, creates maintenance burden

**Instead, Do This**: Use single concrete FileSystem class that provides testability seam. Add abstraction when second implementation needed.

<!-- SECTION:END:CORE_PRINCIPLES -->

<!-- SECTION:START:TECHNOLOGY_STACK -->
## Tech Stack
last updated: 2025-10-03 HH:MM PM PDT
updated by: tech-lead

### Python

- **Version**: 3.9+

- **Purpose**: Runtime environment providing pathlib, typing, and standard library components

- **License**: PSF License
- **Why Chosen Over**: Node.js was considered but Python's mature ecosystem and typing support made it the better choice

### Jsonnet

- **Version**: 0.20.0

- **Purpose**: Context-aware schema composition with profile injection via std.extVar() for dynamic adaptation

- **License**: Apache 2.0
- **Why Chosen Over**: JSON Schema was considered but Jsonnet's programmability enables context-aware composition

### Jinja2

- **Version**: 3.1+

- **Purpose**: Template rendering with built-in framework variables, custom filters, and semantic URI resolution

- **License**: BSD-3-Clause
- **Why Chosen Over**: Mustache was considered but Jinja2's logic support and filters provide needed flexibility

### PyYAML

- **Version**: 6.0+

- **Purpose**: Team profile configuration parsing and YAML artifact generation with schema-aware documentation

- **License**: MIT
- **Why Chosen Over**: TOML was considered but YAML's readability and comment support fit team configuration needs better


### Frameworks and Libraries

#### Testing

- **pytest** (v7.0+): Test framework for unit, integration, and end-to-end tests
- **unittest.mock** (vbuilt-in): Mock objects for dependency injection testing with FileSystem abstraction

#### Development Tools

- **pathlib** (vbuilt-in): Path manipulation and validation for PantheonPath Protection Proxy pattern
- **subprocess** (vbuilt-in): CLI subprocess testing for end-to-end workflow validation


### Development Tools

- **git**: Version control for Team Packages and process evolution tracking (Required: Yes)
- **pytest**: Three-tier testing strategy: unit, integration, and end-to-end tests (Required: Yes)
- **Jsonnet compiler**: Schema compilation with profile context injection (Required: Yes)
- **IDE with Python support**: Development environment with type checking and autocomplete (Required: Optional)
<!-- SECTION:END:TECHNOLOGY_STACK -->

<!-- SECTION:START:SYSTEM_COMPONENTS -->

## System Components
last updated: 2025-10-03 HH:MM PM PDT
updated by: tech-lead

### CLI (Command-Line Interface)

**Purpose**: Presentation layer orchestrator and single entry point for all framework interactions

#### Responsibilities
- Parse command-line arguments and validate actor identity
- Enforce declarative permissions through permissions.jsonnet files
- Coordinate ProcessHandler, Workspace, and other components for command execution
- Provide built-in retrieval commands (get process, get schema, get sections, get tempfile)
- Handle interactive project initialization with team and profile selection
- Manage exit codes and error contract (0=success, 1=bad input, 13=permission denied)

#### Dependencies
- **ProcessHandler**: Delegates core business logic orchestration for process execution
- **Pantheon Workspace**: Retrieves permissions, validates actors, and accesses team configuration
- **FileSystem**: Instantiates FileSystem abstraction for dependency injection

#### Data Flows
- **Input**: Command-line arguments including --actor, --id, --sections, --from-file flags
- **Output**: Success messages to stdout, error messages to stderr, exit codes to shell
- **Output**: Audit log events to Workspace for JSONL persistence when audit enabled

---

### ProcessHandler

**Purpose**: Application layer orchestrator implementing core business logic for unified process execution

#### Responsibilities
- Detect process type (BUILD/CREATE/UPDATE/GET) through efficient file existence checks
- Validate input data structure against composed schemas with profile context
- Handle reserved parameter processing (sections parameter conversion)
- Resolve section metadata for UPDATE processes via target.jsonnet evaluation
- Manage process redirection system with circular redirect detection
- Coordinate Workspace, Artifact Engine, and RAE Engine for complete workflows
- Standardize execution results using ProcessResult format

#### Dependencies
- **Pantheon Workspace**: Retrieves process content, team profile, and accesses filesystem operations
- **Artifact Engine**: Performs schema composition, template rendering, and artifact generation
- **RAE Engine**: Retrieves routine.md content for agent instructions

#### Data Flows
- **Input**: Process name, actor name, input parameters from CLI
- **Bidirectional**: Process content requests to Workspace, receives schemas and templates
- **Bidirectional**: Generation requests to Artifact Engine, receives rendered artifacts and paths
- **Output**: ProcessResult objects with success status, output, errors, and artifact paths

---

### Pantheon Workspace

**Purpose**: Service layer facade providing single source of truth for filesystem paths and conventions

#### Responsibilities
- Provide high-level content-retrieval methods (get_process_schema, get_process_routine, etc.)
- Resolve active team context from .pantheon_project configuration
- Encapsulate all filesystem knowledge and convention-over-configuration logic
- Manage sandboxed file I/O within configurable artifacts root directory
- Create and manage temporary files for atomic operations
- Unwrap PantheonPath objects for authorized filesystem operations
- Persist audit log entries to JSONL files with guardrails

#### Dependencies
- **FileSystem**: Performs all physical read/write operations through injected abstraction

#### Data Flows
- **Input**: Process names, section paths, artifact IDs from ProcessHandler and CLI
- **Output**: File content (schemas, routines, templates) to requesting components
- **Bidirectional**: Filesystem operations delegated to FileSystem abstraction
- **Output**: Created artifacts and temporary files to artifacts root directory

---

### Artifact Engine

**Purpose**: Service layer specialist for schema composition, template rendering, and artifact location

#### Responsibilities
- Compose JSON schemas with profile context via Jsonnet compilation
- Render Jinja2 templates with input data and built-in framework variables
- Generate PantheonPath objects for artifact placement without performing I/O
- Find artifacts using normalizer and finder patterns via Workspace methods
- Parse artifact sections using marker definitions from Workspace
- Provide JSONL logging support for CREATE processes
- Supply enhanced YAML generation with schema-aware documentation

#### Dependencies
- **Pantheon Workspace**: Retrieves schema content, templates, normalizer rules, and finder patterns

#### Data Flows
- **Input**: Schema requests, template rendering requests, artifact location requests from ProcessHandler
- **Bidirectional**: Content retrieval requests to Workspace for schemas, templates, and artifact definitions
- **Output**: Composed schemas, rendered content strings, PantheonPath objects to ProcessHandler
- **Output**: Located artifact paths and parsed section content for GET/UPDATE operations

---

### RAE Engine

**Purpose**: Specialized component for Retrieval-Augmented Execution pattern implementation

#### Responsibilities
- Retrieve routine.md content for given process names
- Delegate to Workspace get_process_routine method for all file operations
- Support process-to-process references and imports

#### Dependencies
- **Pantheon Workspace**: Retrieves routine content with path resolution and active team context

#### Data Flows
- **Input**: Process name from ProcessHandler or CLI
- **Bidirectional**: Routine content request to Workspace, receives routine.md content
- **Output**: Routine content (Markdown instructions) to requesting agent

---

### FileSystem

**Purpose**: Low-level abstraction creating testability seam for all physical I/O operations

#### Responsibilities
- Wrap standard library functions for file operations (read_text, write_text, exists)
- Enable dependency injection for testability with mock objects
- Provide consistent interface for filesystem interactions across framework
- Support append operations for JSONL log persistence

#### Dependencies
- None (standalone component)

#### Data Flows
- **Input**: File paths and content from Workspace for I/O operations
- **Output**: File content read from disk to Workspace
- **Bidirectional**: Physical disk operations for reading, writing, and checking file existence

---


<!-- SECTION:END:SYSTEM_COMPONENTS -->

<!-- SECTION:START:SHARED_SERVICES -->

## Shared Services
last updated: 2025-10-03 HH:MM PM PDT
updated by: tech-lead

### Workspace Content-Retrieval Methods

**Purpose**: High-level methods that abstract filesystem complexity by taking process names and returning content directly

#### Usage Pattern

```python

# Retrieve schema content without knowing file paths
schema_content = workspace.get_process_schema('create-ticket')

# Retrieve section schema from nested directories
section_schema = workspace.get_section_schema(
    'update-architecture-guide',
    'sections/core-principles'
)

# Retrieve routine content with active team resolution
routine = workspace.get_process_routine('create-ticket')

```

#### Configuration

- **project_root**: Root directory of Pantheon project containing .pantheon_project (Default: `Discovered by searching upward from current directory`)
- **artifacts_root**: Output directory for all generated artifacts (Default: `pantheon-artifacts/`)
- **active_team**: Team package context resolved from .pantheon_project (Default: `From selected_team in .pantheon_project`)

#### Best Practices

- Always use content-retrieval methods instead of constructing file paths manually
- Let Workspace handle active team resolution and path construction
- Use semantic URIs for cross-process asset sharing within team boundaries
- Rely on convention-over-configuration for standardized directory structures

---

### PantheonPath Protection Proxy

**Purpose**: Secure wrapper around path objects that prevents accidental I/O by omitting I/O methods

#### Usage Pattern

```python

# Artifact Engine generates paths without I/O capability
artifact_path = PantheonPath('tickets', 'T001_feature.md')

# Only Workspace can unwrap for actual I/O
workspace.save_artifact(content, artifact_path)

# Attempting I/O on PantheonPath fails at compile time
# artifact_path.write_text(content)  # AttributeError: no write_text method

```

#### Configuration

- **path_components**: Variable number of path segments to construct relative path (Default: `No default, constructed from arguments`)

#### Best Practices

- Use PantheonPath for all artifact path generation in pure computation components
- Never unwrap PantheonPath outside Workspace - this enforces architectural boundaries
- Treat PantheonPath as immutable Value Object with value-based equality
- Let Protection Proxy pattern provide compile-time guarantee of I/O separation

---

### Schema Composition with Profile Context

**Purpose**: Jsonnet-based schema compilation that injects active profile configuration as external variables

#### Usage Pattern

```jsonnet

// Access profile properties as external variables
local verbosity = std.extVar('verbosity');
local enforce_tdd = std.extVar('enforce_tdd');

// Conditionally build schema based on profile
local tddFields = if enforce_tdd then {
  properties+: { test_file: { type: 'string' } },
  required+: ['test_file']
} else {};

baseSchema + tddFields

```

#### Configuration

- **profile**: Active profile object injected as std.extVar('profile') (Default: `Resolved from team-profile.yaml active_profile`)
- **include_schema_metadata**: Whether to inject $schema metadata in output (Default: `true (false for section-level fragments)`)

#### Best Practices

- Use profile properties to control what fields agents are prompted for (Smart Schema pattern)
- Keep templates data-driven, checking for data presence rather than profile settings
- Access individual properties via std.extVar('property_name') for cleaner code
- Centralize profile logic in schemas rather than spreading across templates

---

### Built-in Template Variables

**Purpose**: Framework-injected variables available in all Jinja2 templates for metadata and context access

#### Usage Pattern

```jinja2

# Architecture Guide

Created by: {{ pantheon_actor }}
Created at: {{ pantheon_timestamp }}
Artifact ID: {{ pantheon_artifact_id }}

{% if pantheon_profile.verbosity == 'detailed' %}
## Detailed Analysis
{{ detailed_content }}
{% endif %}

Project Root: {{ pantheon_project_root }}
Artifacts Root: {{ pantheon_artifacts_root }}

```

#### Configuration

- **pantheon_actor**: Agent name from --actor flag (Default: `Required CLI parameter`)
- **pantheon_timestamp**: Current timestamp in YYYY-MM-DD hh:mm AM/PM TZ format (Default: `Generated at template rendering time`)
- **pantheon_artifact_id**: Unique incrementing ID for artifact (Default: `Auto-generated or from --id flag`)
- **pantheon_profile**: Entire active profile object from team-profile.yaml (Default: `Resolved active profile configuration`)
- **pantheon_schema**: Compiled JSON schema for current process (Default: `Schema with profile context injection`)

#### Best Practices

- Use pantheon_actor and pantheon_timestamp for audit trail metadata
- Use pantheon_profile sparingly in templates, prefer Smart Schema pattern
- Quote template variables in YAML files to prevent YAML parser errors
- Leverage pantheon_schema for enhanced YAML generation with to_yaml filter

---

### Semantic URI Resolution

**Purpose**: Protocol-based asset sharing mechanism enabling cross-process references within team boundaries

#### Usage Pattern

```jsonnet

// Import schema from another process
local corePrinciples = import 'process-schema://update-architecture-guide/sections/core-principles';

// Import artifact sections with data extraction
local sections = import 'artifact-sections://get-ticket?data=sections.plan';

// Import routine content
local routine = import 'process-routine://create-ticket';

```

#### Configuration

- **scheme**: URI scheme determining asset type (process-schema, artifact-sections, etc.) (Default: `One of: process-schema, process-routine, artifact-locator, artifact-parser, artifact-sections, artifact-template`)
- **process_name**: Process name component of URI (Default: `Required in URI path`)
- **sub_path**: Optional sub-path for nested resources (e.g., sections/section-name) (Default: `Empty for root resource`)

#### Best Practices

- Use semantic URIs for DRY principle - single source of truth for shared assets
- Let Workspace preprocessing handle URI resolution during content retrieval
- Keep team boundaries strict - semantic URIs only reference assets within active team
- Use sub-paths for nested resources like section schemas in artifact directories

---


<!-- SECTION:END:SHARED_SERVICES -->

<!-- SECTION:START:IMPLEMENTATION_PATTERNS -->

## Implementation Patterns
last updated: 2025-10-03 HH:MM PM PDT
updated by: tech-lead

### Dependency Injection via Constructor

**Category**: Architectural

**Problem**: Components coupled to concrete filesystem implementation cannot be tested without touching disk, leading to slow, brittle tests

**Solution**: Inject FileSystem abstraction through constructor, enabling mock injection in tests while using real implementation in production

#### Implementation

```python

class PantheonWorkspace:
    def __init__(self, project_root: Path, artifacts_root: str, fs: FileSystem):
        self.project_root = project_root
        self.artifacts_root = artifacts_root
        self.fs = fs  # Injected dependency

    def save_artifact(self, content: str, path: PantheonPath):
        absolute_path = self.project_root / self.artifacts_root / path.unwrap()
        self.fs.write_text(absolute_path, content)  # Uses injected dependency

# Production usage
workspace = PantheonWorkspace(project_root, artifacts_root, FileSystem())

# Test usage
mock_fs = Mock(spec=FileSystem)
workspace = PantheonWorkspace(project_root, artifacts_root, mock_fs)

```

#### When to Use

- Component needs filesystem access but must be testable without disk I/O
- Creating seam for future abstraction without premature interface creation
- Enabling isolated unit testing of business logic with mock dependencies

#### When NOT to Use

- Component has no external dependencies requiring abstraction
- Adding unnecessary indirection for components that don't need testing isolation
- Creating abstract interfaces when single concrete implementation exists (violates YAGNI)

---

### Protection Proxy with Value Object

**Category**: Structural

**Problem**: Components performing pure computation should not have I/O capability, but need to produce path information for components that do I/O

**Solution**: Wrap path object in PantheonPath proxy that omits I/O methods, treating it as immutable Value Object. Only authorized components unwrap for I/O.

#### Implementation

```python

class PantheonPath:
    """Protection Proxy preventing I/O while enabling path composition."""
    def __init__(self, *parts: str):
        self._path = Path(*parts)

    def unwrap(self) -> Path:
        """Only Workspace should call this method."""
        return self._path

    def __eq__(self, other):
        return isinstance(other, PantheonPath) and self._path == other._path

# Artifact Engine generates paths without I/O capability
artifact_path = PantheonPath('tickets', 'T001_feature.md')

# Only Workspace unwraps for actual I/O
workspace.save_artifact(content, artifact_path)

# Attempting I/O fails at compile time
# artifact_path.write_text(content)  # AttributeError

```

#### When to Use

- Enforcing architectural boundary between computation and I/O layers
- Preventing accidental I/O in pure computation components
- Providing compile-time guarantee of I/O separation for linting tools

#### When NOT to Use

- Component legitimately needs I/O capability for its responsibilities
- Creating unnecessary abstraction for internal-only path manipulation
- Wrapping objects that don't need capability restriction

---

### Facade with Content-Retrieval Methods

**Category**: Architectural

**Problem**: Components need file content but should not understand filesystem structure or construct paths, leading to coupling and complexity

**Solution**: Provide high-level methods taking process names as parameters, returning content directly. Encapsulate all filesystem knowledge in single Facade component.

#### Implementation

```python

class PantheonWorkspace:
    def get_process_schema(self, process_name: str) -> str:
        """Retrieve schema content without exposing path construction."""
        schema_path = (
            self.project_root / 
            'pantheon-teams' / 
            self.active_team / 
            'processes' / 
            process_name / 
            'schema.jsonnet'
        )
        return self.fs.read_text(schema_path)

    def get_section_schema(self, process_name: str, section_path: str) -> str:
        """Retrieve section schema from nested directories."""
        schema_path = (
            self.project_root / 
            'pantheon-teams' / 
            self.active_team / 
            'processes' / 
            process_name / 
            'artifact' / 
            f'{section_path}.schema.jsonnet'
        )
        return self.fs.read_text(schema_path)

# Usage: components only know process names, not file structures
schema = workspace.get_process_schema('create-ticket')
section = workspace.get_section_schema('update-guide', 'sections/core-principles')

```

#### When to Use

- Multiple components need same file content with complex path construction
- Hiding filesystem conventions from business logic components
- Enabling active team resolution and multi-team isolation transparently

#### When NOT to Use

- Single component needs file access with simple, unchanging paths
- Creating unnecessary indirection for one-off file operations
- Facade would have only one or two methods with no reuse benefit

---

### Convention Over Configuration

**Category**: Architectural

**Problem**: Configuration files become complex and require updates for every new component, creating maintenance burden and registration overhead

**Solution**: Establish standardized directory structures and filenames. Use runtime discovery with Workspace methods that encapsulate conventions.

#### Implementation

```python

# Convention: processes/<verb-noun>/schema.jsonnet
# Convention: processes/<verb-noun>/routine.md
# Convention: processes/<verb-noun>/artifact/content.md

class PantheonWorkspace:
    def get_process_schema(self, process_name: str) -> str:
        """Convention: schema.jsonnet is always in process root."""
        path = self._build_process_path(process_name) / 'schema.jsonnet'
        return self.fs.read_text(path)

    def get_artifact_content_template(self, process_name: str) -> str:
        """Convention: content.md is always in artifact subdirectory."""
        path = self._build_process_path(process_name) / 'artifact' / 'content.md'
        return self.fs.read_text(path)

    def _build_process_path(self, process_name: str) -> Path:
        """Encapsulates team and process path conventions."""
        return (
            self.project_root / 
            'pantheon-teams' / 
            self.active_team / 
            'processes' / 
            process_name
        )

# No registration needed - process exists when directory exists
# Components use process names, Workspace handles conventions

```

#### When to Use

- Creating extensible system where new components should work without registration
- Reducing cognitive load and configuration complexity for developers
- Establishing predictable patterns that enable dynamic discovery

#### When NOT to Use

- System requires high flexibility with non-standard structures
- Conventions would be frequently violated requiring many special cases
- Configuration provides essential metadata beyond what conventions can encode

---

### Smart Schema, Dumb Template

**Category**: Behavioral

**Problem**: Profile settings spread between schemas and templates creates inconsistent behavior and makes profile logic hard to understand and maintain

**Solution**: Use profile properties to control schema fields (what agents are prompted for). Templates render based on data presence, not profile settings.

#### Implementation

```jsonnet

// schema.jsonnet - Smart: controls what fields are required
local verbosity = std.extVar('verbosity');
local enforce_tdd = std.extVar('enforce_tdd');

local baseSchema = {
  properties: { ticket_id: { type: 'string' } },
  required: ['ticket_id']
};

// Profile controls whether test field appears in schema
local tddFields = if enforce_tdd then {
  properties+: { test_file: { type: 'string' } },
  required+: ['test_file']
} else {};

baseSchema + tddFields

// template.md - Dumb: renders based on data presence
# Ticket {{ ticket_id }}

{% if test_file %}
## Test-First Development
**Test File:** {{ test_file }}
{% endif %}

```

#### When to Use

- Profile settings should control what data agents provide
- Centralizing profile logic for easier maintenance and testing
- Keeping templates simple and data-driven for predictable rendering

#### When NOT to Use

- Profile only controls pure formatting (font size, colors) that schemas cannot control
- Template legitimately needs profile for output format selection (JSON vs YAML)
- Creating unnecessary indirection when direct profile check is clearer

---

### Semantic URI with Workspace Resolution

**Category**: Architectural

**Problem**: Cross-process asset sharing requires hardcoded paths that break encapsulation and prevent team isolation

**Solution**: Use protocol-based URIs (process-schema://, artifact-sections://) that Workspace resolves during content retrieval, maintaining team boundaries.

#### Implementation

```jsonnet

// In create-architecture-guide/schema.jsonnet
// Import section schema from UPDATE process for DRY principle
local corePrinciples = import 'process-schema://update-architecture-guide/sections/core-principles';

local baseSchema = {
  properties: {
    project_context: { type: 'string' }
  },
  required: ['project_context']
};

// Reuse section schema without duplication
{
  properties: baseSchema.properties + corePrinciples.properties,
  required: baseSchema.required + corePrinciples.required
}

// Workspace resolves semantic URI during preprocessing
// process-schema://update-architecture-guide/sections/core-principles
// -> pantheon-teams/{active_team}/processes/update-architecture-guide/artifact/sections/core-principles.schema.jsonnet

```

#### When to Use

- Sharing schemas, templates, or artifact definitions between processes
- Maintaining DRY principle with single source of truth for shared assets
- Keeping team boundaries strict while enabling internal asset reuse

#### When NOT to Use

- Asset is only used in single process with no reuse benefit
- Attempting cross-team asset sharing (breaks team isolation)
- Creating unnecessary indirection for simple, local references

---

### Process Type Detection via File Convention

**Category**: Architectural

**Problem**: Explicit operation type registration creates maintenance burden and couples process definition to central registry

**Solution**: Detect operation type through file combinations: BUILD (build-schema.jsonnet), CREATE (content.md + placement + naming), UPDATE (patch.md + GET files), GET (locator + parser).

#### Implementation

```python

class ProcessHandler:
    def _detect_process_type(self, process_name: str) -> ProcessType:
        """Detect operation type from file conventions."""
        # Efficient 2-call detection with clear precedence
        
        # Check for BUILD first (highest precedence)
        if self.workspace.file_exists(f'processes/{process_name}/build-schema.jsonnet'):
            return ProcessType.BUILD

        # Check for CREATE
        try:
            self.workspace.get_artifact_content_template(process_name)
            return ProcessType.CREATE
        except FileNotFoundError:
            pass

        # Check for UPDATE
        try:
            self.workspace.get_artifact_patch_template(process_name)
            return ProcessType.UPDATE
        except FileNotFoundError:
            pass

        # Default to GET
        return ProcessType.GET

# Usage: single execute command for all operation types
result = process_handler.execute(process_name, actor, input_data)

```

#### When to Use

- Creating self-documenting processes where intent is visible from file structure
- Enabling single unified command interface for all operation types
- Avoiding central registry that requires updates for each new process

#### When NOT to Use

- File combinations would be ambiguous or overlapping
- Operation type cannot be reliably determined from file presence
- System requires metadata beyond what file conventions can encode

---

### Arrange-Act-Assert with Mock Verification

**Category**: Behavioral

**Problem**: Traditional filesystem tests are slow, brittle, and require cleanup. Business logic is hard to test independently of I/O.

**Solution**: Use Arrange-Act-Assert pattern with mock FileSystem verification. Assert on method calls instead of disk side effects.

#### Implementation

```python

def test_save_artifact_resolves_correct_path():
    # ARRANGE - Setup test data and inject mock
    mock_fs = Mock(spec=FileSystem)
    workspace = PantheonWorkspace(
        project_root=Path('/project'),
        artifacts_root='pantheon-artifacts',
        fs=mock_fs
    )
    content = '## Ticket T012'
    relative_path = PantheonPath('tickets', 'T012_init.md')

    # ACT - Call method under test
    workspace.save_artifact(content, relative_path)

    # ASSERT - Verify correct method call with transformed data
    expected_path = Path('/project/pantheon-artifacts/tickets/T012_init.md')
    mock_fs.write_text.assert_called_once_with(expected_path, content)

    # Test runs in microseconds without touching disk

```

#### When to Use

- Testing business logic that coordinates I/O without testing actual I/O
- Verifying path construction and data transformation logic
- Creating fast, reliable unit tests that don't require cleanup

#### When NOT to Use

- Testing actual I/O behavior requires integration test with real filesystem
- Business logic is so simple mock setup is more complex than just testing I/O
- Creating unnecessary mocks for components without external dependencies

---


<!-- SECTION:END:IMPLEMENTATION_PATTERNS -->

<!-- SECTION:START:TESTING_STRATEGY -->

## Testing
last updated: 2025-10-03 HH:MM PM PDT
updated by: tech-lead

### Testing Philosophy

The framework follows true Test Driven Development with a three-tier testing strategy emphasizing fast, focused unit tests with dependency injection and mock verification. Tests are written as if implementation is working and fail naturally, following the Red-Green-Refactor cycle. Before completing work, all tests must be run to check for regression, ensuring continuous quality and systematic validation of business logic independent of external dependencies.

### Test Types

#### Unit Tests

**Purpose**: Test individual components in isolation with mock dependencies for fast, focused validation of business logic

**Coverage Target**: 80%+%

**Key Patterns**:
- Use dependency injection to inject mock FileSystem objects
- Follow Arrange-Act-Assert pattern with mock verification
- Assert on method calls to mocks instead of disk side effects
- Test business logic (path construction, data transformation) not actual I/O
- Write tests as if implementation is working, failing naturally
- Each test runs in microseconds without touching disk or network

**Example**:

```python

def test_workspace_saves_artifact_to_correct_path():
    # ARRANGE - Setup mock and test data
    mock_fs = Mock(spec=FileSystem)
    workspace = PantheonWorkspace(
        project_root=Path('/project'),
        artifacts_root='pantheon-artifacts',
        fs=mock_fs
    )
    content = '## Architecture Guide'
    path = PantheonPath('docs', 'guide.md')

    # ACT - Call method under test
    workspace.save_artifact(content, path)

    # ASSERT - Verify mock was called correctly
    expected_path = Path('/project/pantheon-artifacts/docs/guide.md')
    mock_fs.write_text.assert_called_once_with(expected_path, content)

```

#### Integration Tests

**Purpose**: Test component interactions with real objects to validate coordination and data flow between layers

**Coverage Target**: 60%+%

**Key Patterns**:
- Use real FileSystem instance with temporary directories
- Test multiple components working together (ProcessHandler + Workspace + Artifact Engine)
- Validate actual file creation, content, and directory structure
- Clean up temporary files after each test
- Focus on component boundaries and integration points
- Moderate speed with actual filesystem operations

**Example**:

```python

def test_process_handler_creates_artifact_via_workspace(tmp_path):
    # ARRANGE - Real components with temp directory
    fs = FileSystem()
    workspace = PantheonWorkspace(
        project_root=tmp_path,
        artifacts_root='artifacts',
        fs=fs
    )
    handler = ProcessHandler(workspace, artifact_engine, rae_engine)
    input_data = {'title': 'Test Guide', 'content': 'Guide content'}

    # ACT - Execute process through handler
    result = handler.execute('create-guide', 'tech-lead', input_data)

    # ASSERT - Verify artifact created on disk
    assert result.success
    artifact_path = tmp_path / 'artifacts' / 'docs' / 'guide.md'
    assert artifact_path.exists()
    assert 'Guide content' in artifact_path.read_text()

```

#### End-to-End Tests

**Purpose**: Test complete workflows via CLI subprocess calls to validate entire system behavior from user perspective

**Coverage Target**: Critical paths only%

**Key Patterns**:
- Use subprocess.run() to invoke actual CLI commands
- Test complete user workflows from command to artifact creation
- Validate exit codes, stdout/stderr, and generated artifacts
- Use temporary project directories for test isolation
- Focus on critical paths and user-facing scenarios
- Slowest tests, run less frequently during development

**Example**:

```python

def test_cli_create_architecture_guide_workflow(tmp_path):
    # ARRANGE - Setup test project and input file
    project_dir = tmp_path / 'test-project'
    project_dir.mkdir()
    input_file = project_dir / 'input.json'
    input_file.write_text(json.dumps({
        'problem_statement': 'Test problem',
        'business_outcomes': ['Outcome 1']
    }))

    # ACT - Run actual CLI command via subprocess
    result = subprocess.run(
        ['pantheon', 'execute', 'create-architecture-guide',
         '--from-file', str(input_file), '--actor', 'tech-lead'],
        cwd=project_dir,
        capture_output=True,
        text=True
    )

    # ASSERT - Verify complete workflow
    assert result.returncode == 0
    assert 'architecture-guide.md' in result.stdout
    artifact = project_dir / 'pantheon-artifacts' / 'docs' / 'architecture-guide' / 'architecture-guide.md'
    assert artifact.exists()
    assert 'Test problem' in artifact.read_text()

```


### Testing Best Practices

#### Red-Green-Refactor Cycle

Write failing test first (Red), implement minimal code to pass (Green), then improve code quality (Refactor). Tests should fail naturally when implementation is missing, not through artificial NotImplementedError raises.

**Example**:

```python

# RED - Write failing test first
def test_workspace_resolves_active_team_from_config():
    workspace = PantheonWorkspace(project_root, config={'selected_team': 'dev'})
    assert workspace.active_team == 'dev'  # Fails naturally - property doesn't exist

# GREEN - Implement minimal code to pass
class PantheonWorkspace:
    def __init__(self, project_root, config):
        self._active_team = config['selected_team']
    
    @property
    def active_team(self):
        return self._active_team  # Test passes

# REFACTOR - Improve without breaking tests
class PantheonWorkspace:
    def __init__(self, project_root, config, fs):
        self._config = config
        self.fs = fs
    
    @property
    def active_team(self):
        return self._config.get('selected_team', 'default')  # Better with default

```

#### Test One Thing Per Test

Each test should verify a single behavior or outcome. Multiple assertions are acceptable when verifying the same behavior from different angles, but avoid testing unrelated functionality in one test.

**Example**:

```python

# GOOD - Tests single behavior with multiple related assertions
def test_pantheon_path_equality_based_on_value():
    path1 = PantheonPath('docs', 'guide.md')
    path2 = PantheonPath('docs', 'guide.md')
    path3 = PantheonPath('tickets', 'T001.md')
    
    assert path1 == path2  # Same value equals
    assert path1 != path3  # Different value not equals
    assert path1 is not path2  # Different instances

# BAD - Tests multiple unrelated behaviors
def test_pantheon_path_operations():
    path = PantheonPath('docs', 'guide.md')
    assert path == PantheonPath('docs', 'guide.md')  # Equality
    workspace.save_artifact(content, path)  # Saving
    assert workspace.active_team == 'dev'  # Team resolution (unrelated!)

```

#### Avoid Complex Test Setup

Keep test setup simple and focused. Complex mocking or test data generation suggests the component under test has too many responsibilities or dependencies. Simplify the component or use integration tests instead.

**Example**:

```python

# GOOD - Simple setup with minimal mocking
def test_artifact_engine_renders_template():
    mock_workspace = Mock(spec=PantheonWorkspace)
    mock_workspace.get_artifact_content_template.return_value = '# {{ title }}'
    
    engine = ArtifactEngine(mock_workspace)
    result = engine.render_content('create-guide', {'title': 'Guide'})
    
    assert result == '# Guide'

# BAD - Complex setup indicates problem
def test_process_handler_with_many_dependencies():
    # 20 lines of mock setup...
    mock_ws = Mock()
    mock_ae = Mock()
    mock_rae = Mock()
    mock_fs = Mock()
    # Configure 15 different mock behaviors...
    # Consider integration test or refactoring instead

```

#### Prioritize Pragmatism Over Quantity

Focus on testing core functionality and critical paths. Avoid writing fluff tests that test the same criteria with minute variations. Quality and coverage of essential behavior matters more than raw test count.

**Example**:

```python

# GOOD - Core functionality test
def test_workspace_content_retrieval_with_process_name():
    workspace = PantheonWorkspace(project_root, config, fs)
    content = workspace.get_process_schema('create-ticket')
    assert 'ticket_id' in content  # Verifies core retrieval works

# BAD - Fluff test with minute variation
def test_workspace_content_retrieval_with_different_process_name():
    workspace = PantheonWorkspace(project_root, config, fs)
    content = workspace.get_process_schema('create-guide')
    assert 'guide_title' in content  # Same test, different process name

# Instead: One parameterized test covering multiple cases
@pytest.mark.parametrize('process_name,expected_field', [
    ('create-ticket', 'ticket_id'),
    ('create-guide', 'guide_title')
])
def test_workspace_retrieves_schema_for_processes(process_name, expected_field):
    content = workspace.get_process_schema(process_name)
    assert expected_field in content

```

#### Run All Tests Before Completion

Before wrapping up work, run the complete test suite to check for regression. Fast unit tests enable running the full suite frequently during development to catch breaking changes early.

**Example**:

```bash

# Run full test suite with coverage
pytest tests/ --cov=pantheon --cov-report=term-missing

# Run specific test tier for faster feedback during development
pytest tests/unit/  # Fast unit tests only
pytest tests/integration/  # Integration tests
pytest tests/e2e/  # End-to-end tests

# Before commit: run all tests
pytest tests/ -v

# Check coverage targets
pytest tests/ --cov=pantheon --cov-fail-under=80

```


<!-- SECTION:END:TESTING_STRATEGY -->

<!-- SECTION:START:DOCUMENTATION_STANDARDS -->
# Documentation Standards

## 1. Philosophy and Purpose

This document outlines the standards for creating, organizing, and managing all documentation assets, including text and diagrams.

### The Challenge: Engineering Context for AI Agents

AI agents, particularly in a Retrieval-Augmented Execution (RAE) system, do not "read" or "browse" documentation like humans. They perform targeted retrieval operations to acquire specific knowledge needed for a task. When documentation is unstructured—existing as large, monolithic files or a disorganized collection of documents—it becomes a significant obstacle to building reliable agentic workflows.

### Our Goal: A Retrieval-Friendly Knowledge Base

To solve this, our goal is to create a **retrieval-friendly knowledge base**. By enforcing a structured format, we transform our documentation from a simple collection of human-readable text into a queryable, API-like system for knowledge. This enables precise, reliable retrieval, which is the foundation for effective Context Engineering and, ultimately, for building dependable AI agents.

## 2. Core Principles

- **Topic-Oriented:** Content is organized around specific, orthogonal concepts (e.g., "Database," "API Client").
- **Co-location:** All assets for a single topic—both text and diagrams—must be located in the same directory.
- **Single Source of Truth (SSoT):** Every concept must have one, and only one, canonical document or diagram.
- **Discoverability First:** The structure must be optimized for search and navigation via metadata and a master index.

## 3. Content Philosophy: What to Document

Our guiding principle is: **document the *why*, not the *what*.** The code shows the action; the docs must explain the reasoning.

- **Document Decisions:** Explain architectural choices and trade-offs. For major decisions, create an **Design Decision Doc** using `pantheon get process create-design-decision --actor <your_agent_name>`
- **Document the Non-Obvious:** Focus on complex algorithms, counter-intuitive logic, or critical side-effects.
- **Document Contracts and Boundaries:** Clearly define the public API of a component—its inputs, outputs, and guarantees.
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
<!-- SECTION:END:DOCUMENTATION_STANDARDS -->