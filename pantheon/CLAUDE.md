# Pantheon Framework Core Implementation

## Framework Core Architecture

This directory contains the core implementation of the Pantheon Framework following **Retrieval-Augmented Execution (RAE)** architecture with strict **Glass Box** principles.

### Component Overview

#### CLI (`cli.py`)
**Presentation Layer** - Entry point with clean separation of concerns:
- Handle argument parsing and user interaction only
- Enforce actor validation and permission checking
- Required `--actor <name>` flag for all commands
- Built-in flags: `--id`, `--sections`, `--from-file`
- Standard exit codes: 0 (success), 1 (bad input), 13 (permission denied)
- **NO business logic** - delegate everything to ProcessHandler

#### ProcessHandler (`process_handler.py`)
**Application Layer** - Central orchestrator containing core business logic:
- Implement **Unified Execute Model** with operation type detection
- Handle process redirection system with circular redirect prevention
- Manage reserved parameter processing (sections parameter conversion)
- Coordinate between presentation and service layers
- **Operation Detection**: Use 2-call pattern for efficient type detection

#### Workspace (`workspace.py`)
**Service Layer - Facade Pattern** - Single source of truth for filesystem operations:
- **High-level content-retrieval methods**: `get_process_schema()`, `get_process_routine()`, `get_artifact_normalizer()`, etc.
- **Active team resolution**: Automatically handle team context from `.pantheon_project`
- **Sandboxed file I/O**: All operations within configurable artifacts root
- **Convention over Configuration**: Encapsulate all filesystem knowledge
- **Only component allowed to unwrap PantheonPath objects**

#### Artifact Engine (`artifact_engine.py`)
**Service Layer - Pure Computation** - Handles all artifact operations:
- **Generation Methods**: Schema composition, data validation, template rendering (pure computation)
- **Location Methods**: Complex queries using Workspace content-retrieval (I/O orchestration)
- **Built-in template variables**: `pantheon_actor`, `pantheon_timestamp`, `pantheon_datestamp`, `pantheon_artifact_id`, `pantheon_profile`
- **NO direct I/O** - only pure computation and PantheonPath manipulation

#### FileSystem (`filesystem.py`)
**Infrastructure Layer** - Abstraction for all I/O operations:
- Single concrete class wrapping standard I/O operations
- Enable dependency injection and mock-based unit testing
- Create clean seam between business logic and physical filesystem
- **Only used by Workspace** - other components must go through Workspace

#### RAE Engine (`rae_engine.py`)
**Service Component** - Specialized routine retrieval:
- Retrieve `routine.md` content using Workspace methods
- Support process-to-process references and imports
- Handle routine parsing and validation

#### PantheonPath (`path.py`)
**Protection Proxy** - Enforced boundaries for file access:
- Prevent accidental I/O operations in business logic
- Only Workspace can unwrap paths for actual filesystem operations
- Separate computation from I/O operations

#### Logger (`logger.py`)
**Cross-cutting Concern** - Standardized logging:
- Import `Log` from `pantheon.logger` in all files
- Use `Log.info()`, `Log.debug()`, `Log.warning()`, `Log.error()`
- **NEVER use print() statements**

## Implementation Protocols

### Dependency Injection Pattern
```python
# Correct: Inject FileSystem dependency
def __init__(self, filesystem: FileSystem):
    self.filesystem = filesystem

# Incorrect: Direct instantiation
def __init__(self):
    self.filesystem = FileSystem()  # Hard to test
```

### Workspace Abstraction Protocol
```python
# Correct: Use high-level Workspace methods
schema = workspace.get_process_schema(process_name, actor)
routine = workspace.get_process_routine(process_name)

# Incorrect: Direct file operations
with open(f"processes/{process_name}/schema.jsonnet") as f:  # Breaks abstraction
```

### PantheonPath Protection Protocol
```python
# Correct: Only Workspace unwraps paths
class Workspace:
    def read_file(self, path: PantheonPath) -> str:
        return self.filesystem.read_file(path.unwrap())  # Only here

# Incorrect: Business logic unwrapping paths
def process_data(path: PantheonPath):
    content = open(path.unwrap(), 'r').read()  # Breaks encapsulation
```

### Error Handling Protocol
```python
# Correct: Standardized error handling
try:
    result = workspace.get_process_schema(process_name, actor)
except PermissionDenied:
    Log.error(f"Permission denied for actor {actor}")
    sys.exit(13)
except InvalidInput as e:
    Log.error(f"Invalid input: {e}")
    sys.exit(1)
```

## Testing Guidelines

### Component Testing Strategy
- **Unit Tests**: Mock FileSystem, test pure business logic
- **Integration Tests**: Real FileSystem, test component interactions
- **End-to-End Tests**: CLI subprocess calls, test complete workflows

### Mock Injection Pattern
```python
# Test setup
mock_filesystem = Mock(spec=FileSystem)
workspace = Workspace(mock_filesystem)
process_handler = ProcessHandler(workspace)

# Test execution with verification
mock_filesystem.read_file.assert_called_once_with("/expected/path")
```

## Code Organization Principles

### Single Responsibility
- **CLI**: Only argument parsing and user interaction
- **ProcessHandler**: Only business logic orchestration
- **Workspace**: Only high-level file operations and path resolution
- **Artifact Engine**: Only pure computation and artifact manipulation

### Convention over Configuration
- Use `workspace.get_*()` methods instead of constructing paths
- Rely on standardized directory structures and filenames
- Enable runtime discovery through conventional naming

### Glass Box Transparency
- Every operation should be traceable through logs
- Use structured processes over dynamic prompt generation
- Version control all process definitions and schemas

## Important Constraints

### Strict Prohibitions
- **NO direct file I/O** except in FileSystem and Workspace classes
- **NO business logic in CLI** - only presentation concerns
- **NO I/O operations in Artifact Engine** - pure computation only
- **NO unwrapping PantheonPath** except in Workspace class
- **NO print() statements** - always use Log methods

### Required Patterns
- **Always inject FileSystem dependency** for testability
- **Always use Workspace methods** for file operations
- **Always validate actor permissions** before processing
- **Always use standard exit codes** for consistent behavior
- **Always import Log from pantheon.logger** for output

## Framework Integration

### Team Package Integration
- Components must work with standardized team package structure
- Support profile context injection through `std.extVar('profile')`
- Respect artifact sandboxing and cross-team isolation
- Handle semantic URI references for cross-process asset sharing

### CLI Integration
- All commands require `--actor <name>` parameter
- Support `--from-file <json>` for structured input
- Handle `--sections` parameter for artifact retrieval
- Maintain backward compatibility with existing process definitions