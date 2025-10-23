# Unit Testing

## Unit Testing Philosophy

Unit tests validate **individual components in isolation** using **dependency injection** and **mocks** to eliminate external dependencies. These tests provide **fast feedback** during development and ensure each component's **single responsibility** is correctly implemented.

### Unit Testing Core Principles
- **Component isolation**: Test single components without external dependencies
- **Mock all dependencies**: Use dependency injection with mocks for all I/O and external services
- **Fast execution**: < 10ms per test for rapid development feedback
- **Single responsibility focus**: Validate each component's specific role and boundaries

### Unit vs Other Test Tiers
- **Unit Tests**: Single components with mocks (fast, isolated)
- **Integration Tests**: Component interactions with real objects (moderate speed)
- **E2E Tests**: Complete CLI workflows via subprocess (slow, comprehensive)

## Component-Specific Unit Testing

### CLI Unit Testing (`test_cli.py`)
**Presentation Layer Testing** - Pure argument parsing and user interaction:

```python
def test_cli_requires_actor_parameter(mock_process_handler):
    """Test CLI enforces required --actor parameter."""
    # Arrange: Mock ProcessHandler to isolate presentation logic
    cli = CLI(mock_process_handler)
    
    # Act: Test CLI with missing actor parameter
    result = cli.parse_and_execute(["execute", "test-process"])
    
    # Assert: Verify CLI validation without business logic
    assert result.exit_code == 1
    assert "actor required" in result.error_message
    mock_process_handler.execute.assert_not_called()
```

**Key Testing Areas**:
- Argument parsing with various input combinations
- Actor validation and permission enforcement  
- Exit code handling (0=success, 1=bad input, 13=permission denied)
- Error message formatting and presentation

### ProcessHandler Unit Testing (`test_process_handler*.py`)
**Application Layer Testing** - Business logic orchestration:

```python
def test_unified_execute_model_operation_detection(mock_workspace):
    """Test ProcessHandler detects operation types correctly."""
    # Arrange: Configure mock workspace responses
    mock_workspace.get_artifact_content_template.return_value = "content template"
    mock_workspace.get_artifact_patch_template.side_effect = FileNotFoundError()
    
    process_handler = ProcessHandler(mock_workspace)
    
    # Act: Test operation detection logic
    operation_type = process_handler.detect_operation_type("test-process")
    
    # Assert: Verify correct detection without I/O
    assert operation_type == OperationType.CREATE
    mock_workspace.get_artifact_content_template.assert_called_once()
```

**Key Testing Areas**:
- Unified Execute Model operation detection (CREATE/UPDATE/RETRIEVE)
- Process redirection with circular prevention
- Reserved parameter processing (sections parameter handling)
- Business logic orchestration without I/O dependencies

### Workspace Unit Testing (`test_workspace*.py`)
**Service Layer Facade Testing** - High-level content retrieval:

```python  
def test_get_process_schema_with_actor_validation(mock_filesystem):
    """Test Workspace validates actor permissions."""
    # Arrange: Configure filesystem mock responses
    mock_filesystem.read_file.side_effect = [
        '{"allow": ["test-actor"]}',  # permissions.jsonnet
        '{"param": "string"}'         # schema.jsonnet  
    ]
    
    workspace = PantheonWorkspace(mock_filesystem)
    
    # Act: Test schema retrieval with actor validation
    schema = workspace.get_process_schema("test-process", "test-actor")
    
    # Assert: Verify method coordination without actual I/O
    assert schema == '{"param": "string"}'
    assert mock_filesystem.read_file.call_count == 2
```

**Key Testing Areas**:
- High-level content-retrieval methods
- Active team resolution from `.pantheon_project`
- Convention-based path construction and resolution
- Actor validation and permission checking
- Sandboxed file operations within artifacts root

### Artifact Engine Unit Testing (`test_artifact_engine*.py`)
**Service Layer Pure Computation Testing** - Template and schema operations:

```python
def test_schema_composition_with_profile_injection(mock_workspace):
    """Test Artifact Engine composes schemas with profile context."""
    # Arrange: Mock workspace for I/O operations only
    mock_workspace.get_process_schema_file.return_value = schema_path
    
    artifact_engine = ArtifactEngine()
    profile_context = {"team_name": "test-team", "verbosity": True}
    
    # Act: Test pure computation without I/O
    composed_schema = artifact_engine.compose_schema_with_profile(
        "test-process", profile_context
    )
    
    # Assert: Verify composition logic without filesystem dependencies
    assert composed_schema["verbosity"] == [True]
    assert "team_name" in composed_schema
```

**Key Testing Areas**:
- Schema composition with profile context injection (`std.extVar('profile')`)
- Template rendering with built-in variables
- Data validation and type checking
- PantheonPath manipulation without I/O operations
- Semantic URI resolution and cross-process references

### FileSystem Unit Testing (`test_filesystem.py`)
**Infrastructure Layer Testing** - I/O abstraction validation:

```python
def test_filesystem_read_file_with_error_handling():
    """Test FileSystem handles I/O errors appropriately."""
    filesystem = FileSystem()
    
    # Test error handling for non-existent files
    with pytest.raises(FileNotFoundError):
        filesystem.read_file("/nonexistent/path.txt")
    
    # Test error handling for permission issues
    with pytest.raises(PermissionError):
        filesystem.write_file("/root/restricted.txt", "content")
```

**Key Testing Areas**:
- File read/write operations with proper error handling
- Directory creation and path resolution
- Cross-platform path handling (Windows/Unix)
- Exception propagation and error context

### RAE Engine Unit Testing (`test_rae_engine.py`) 
**Service Component Testing** - Routine retrieval operations:

```python
def test_rae_engine_routine_retrieval(mock_workspace):
    """Test RAE Engine retrieves routines via Workspace."""
    # Arrange: Mock Workspace methods
    mock_workspace.get_process_routine.return_value = "# Test Routine"
    
    rae_engine = RAEEngine(mock_workspace)
    
    # Act: Test routine retrieval
    routine = rae_engine.get_routine("test-process")
    
    # Assert: Verify delegation to Workspace
    assert routine == "# Test Routine"
    mock_workspace.get_process_routine.assert_called_once_with("test-process")
```

**Key Testing Areas**:
- Routine retrieval using Workspace methods
- Process-to-process references and imports
- Routine parsing and validation
- Error handling for missing or invalid routines

### Logger Unit Testing (`test_logger*.py`)
**Cross-cutting Concern Testing** - Logging functionality:

```python
def test_log_info_outputs_correctly(capsys):
    """Test Log.info outputs to correct stream."""
    from pantheon.logger import Log
    
    # Act: Use logger
    Log.info("test message")
    
    # Assert: Verify output formatting
    captured = capsys.readouterr()
    assert "test message" in captured.out
    assert captured.err == ""  # Should not write to stderr
```

**Key Testing Areas**:
- Log level filtering and output routing
- Message formatting and timestamps
- Integration with Python logging system
- Stream handling (stdout vs stderr)

## Mock Strategy and Patterns

### Dependency Injection Testing Pattern
```python
class TestComponentWithDependencies:
    @pytest.fixture
    def mock_dependency(self) -> Mock:
        """Create mock with spec for interface validation."""
        return Mock(spec=DependencyInterface)
    
    @pytest.fixture
    def component_under_test(self, mock_dependency):
        """Create component with injected mock."""
        return ComponentUnderTest(mock_dependency)
    
    def test_component_behavior(self, component_under_test, mock_dependency):
        """Test component behavior with mocked dependency."""
        # Configure mock behavior
        mock_dependency.method.return_value = "expected_result"
        
        # Test component
        result = component_under_test.execute()
        
        # Verify interactions
        mock_dependency.method.assert_called_once_with("expected_input")
        assert result == "expected_result"
```

### Mock Configuration Patterns
```python
# Return values for successful cases
mock_filesystem.read_file.return_value = "file content"

# Side effects for multiple calls
mock_filesystem.read_file.side_effect = [
    "first call result",
    "second call result",
    FileNotFoundError("third call fails")
]

# Conditional responses based on input
def filesystem_read_side_effect(path):
    if "permissions" in path:
        return '{"allow": ["test-actor"]}'
    elif "schema" in path:
        return '{"param": "string"}'
    else:
        raise FileNotFoundError(f"No mock for {path}")

mock_filesystem.read_file.side_effect = filesystem_read_side_effect
```

### Mock Verification Patterns
```python
# Verify exact method calls
mock_filesystem.read_file.assert_called_once_with("/expected/path")

# Verify call count and arguments
assert mock_filesystem.write_file.call_count == 2
mock_filesystem.write_file.assert_any_call("/path1", "content1")
mock_filesystem.write_file.assert_any_call("/path2", "content2")

# Verify method call order
mock_filesystem.read_file.assert_called_before(mock_filesystem.write_file)

# Verify no unexpected calls
mock_filesystem.delete_file.assert_not_called()
```

## Arrange-Act-Assert Pattern

### Standard Test Structure
```python
def test_component_functionality():
    """Test follows standard AAA pattern."""
    # Arrange: Set up test data and mock behavior
    mock_dependency = Mock()
    mock_dependency.process.return_value = "expected_output"
    component = ComponentUnderTest(mock_dependency)
    test_input = {"parameter": "value"}
    
    # Act: Execute the operation being tested  
    result = component.execute_operation(test_input)
    
    # Assert: Verify expected outcomes and interactions
    assert result.status == "success"
    assert result.output == "expected_output"
    mock_dependency.process.assert_called_once_with(test_input)
```

### Error Testing Pattern
```python
def test_component_error_handling():
    """Test component handles errors appropriately."""
    # Arrange: Configure mock to simulate error
    mock_dependency = Mock()
    mock_dependency.process.side_effect = ProcessingError("test error")
    component = ComponentUnderTest(mock_dependency)
    
    # Act & Assert: Verify proper error handling
    with pytest.raises(ComponentError) as exc_info:
        component.execute_operation({"invalid": "input"})
    
    assert "test error" in str(exc_info.value)
    mock_dependency.process.assert_called_once()
```

## Framework-Specific Unit Testing

### PantheonPath Protection Testing
```python
def test_pantheon_path_cannot_unwrap_outside_workspace():
    """Test PantheonPath protection proxy works correctly."""
    path = PantheonPath("/test/path")
    
    # Assert: PantheonPath prevents direct unwrapping
    with pytest.raises(AttributeError):
        actual_path = path.unwrap()  # Should fail outside Workspace
```

### Profile Context Testing
```python
def test_profile_context_injection():
    """Test profile context is correctly injected into templates."""
    profile = {"team_name": "test", "verbosity": True}
    template = "Team: {{ profile.team_name }}, Verbose: {{ profile.verbosity }}"
    
    # Test pure template rendering without I/O
    result = render_template_with_profile(template, {}, profile)
    
    assert result == "Team: test, Verbose: True"
```

### Actor Validation Testing
```python
def test_actor_validation_logic():
    """Test actor validation without filesystem dependencies."""
    permissions = {"allow": ["valid-actor"], "deny": ["banned-actor"]}
    
    # Test validation logic directly
    assert validate_actor_permissions("valid-actor", permissions) == True
    assert validate_actor_permissions("banned-actor", permissions) == False
    assert validate_actor_permissions("unknown-actor", permissions) == False
```

## Running Unit Tests

### Execution Commands
```bash
# Run all unit tests (should be very fast)
python -m pytest tests/unit/ -v

# Run specific component tests
python -m pytest tests/unit/test_workspace.py -v

# Run with coverage reporting
python -m pytest tests/unit/ --cov=pantheon --cov-report=html

# Run tests matching pattern
python -m pytest tests/unit/ -k "test_workspace" -v

# Run tests with timing information  
python -m pytest tests/unit/ --durations=10
```

### Test Performance Guidelines
- **< 10ms per test**: Unit tests should execute very quickly
- **No I/O operations**: All external dependencies mocked
- **Minimal setup**: Arrange phase should be lightweight
- **Focused assertions**: Test single behavior per test method

### Unit Test Quality Indicators
- **High test speed**: Unit test suite completes in seconds
- **Clear test names**: Method names describe exact behavior tested
- **Focused scope**: Each test validates single responsibility
- **Mock isolation**: No real filesystem or network operations
- **Comprehensive coverage**: All public methods and error paths tested