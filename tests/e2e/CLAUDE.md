# End-to-End Testing

## E2E Testing Philosophy

End-to-end tests validate **complete user workflows** through the **CLI interface** using subprocess calls. These tests ensure the entire **Pantheon Framework** functions correctly from the user's perspective, including all component integrations and real filesystem operations.

### ✨ **Fixture-Based Architecture (Current)**

Our E2E tests now use a **fixture-based approach** that provides:
- **Complete Test Isolation**: Tests use `tests/fixtures/teams/pantheon-e2e-test/` 
- **Production Independence**: Zero dependency on production templates
- **Robustness**: Tests work regardless of production template changes
- **Clean UX**: Production users only see `pantheon-foundry` (auto-selected)

### E2E Testing Scope
- **Complete CLI workflows**: Full user scenarios from command invocation to output
- **Real filesystem operations**: Actual file I/O with temporary project directories
- **Framework integration**: All components working together in production-like environment
- **User experience validation**: Command-line interface behavior and output formatting

### E2E vs Other Test Tiers
- **Unit Tests**: Component isolation with mocks (fast)
- **Integration Tests**: Component interaction with real objects (moderate)
- **E2E Tests**: Complete workflows via CLI subprocess (comprehensive but slow)

## Test Infrastructure

### E2E-Specific Fixtures (`conftest.py`)

#### `temp_project` Fixture
- Creates isolated temporary directory for each test
- Provides clean environment for filesystem operations
- Automatically cleaned up after test completion

#### `pantheon_cli` Fixture  
- Locates pantheon CLI executable in current environment
- Enables subprocess calls to actual installed framework
- Handles cross-platform executable resolution (`.exe` on Windows)

#### `run_pantheon` Fixture
- Wraps subprocess execution with consistent interface
- Handles command execution in isolated test environment
- Provides standardized result processing and error handling

#### `setup_test_project` Fixture ✨ **NEW**
- Creates isolated project structure using test fixtures
- Copies `pantheon-e2e-test` team from `tests/fixtures/teams/`
- No dependency on production templates or CLI `init` command
- Ensures complete test isolation from production changes

### E2E Test Organization

#### Test Categories
- **Golden Path Tests** (`test_golden_path.py`): Primary user workflows
- **Init Command Tests** (`test_init_command.py`): Project initialization scenarios
- **Retrieval Commands** (`test_retrieval_commands.py`): Information retrieval workflows
- **Artifact Generation** (`test_artifact_generation.py`): CREATE/UPDATE/RETRIEVE operations

## E2E Testing Patterns

### CLI Subprocess Pattern
```python
def test_complete_workflow(run_pantheon, temp_project):
    """Test complete user workflow through CLI."""
    # Arrange: Set up test project structure
    setup_test_project(temp_project)
    
    # Act: Execute CLI command via subprocess
    result = run_pantheon([
        "execute", "test-process",
        "--actor", "test-actor", 
        "--param", "value"
    ])
    
    # Assert: Verify command success and output
    assert result.returncode == 0
    assert "success message" in result.stdout
    
    # Verify filesystem changes
    output_file = temp_project / "expected_output.md"
    assert output_file.exists()
    assert "expected content" in output_file.read_text()
```

### Fixture-Based Project Setup Pattern ✨ **UPDATED**
```python
def test_example(temp_project: Path, run_pantheon, setup_test_project):
    """Modern fixture-based test pattern."""
    # Set up isolated test project using fixtures
    project_info = setup_test_project()
    assert project_info["team_name"] == "pantheon-e2e-test"
    
    # Execute test - no CLI init required!
    result = run_pantheon([
        "execute", "create-ticket",
        "--actor", "ticket-handler",
        "--title", "Test Ticket"
    ])
    
    assert result.returncode == 0
```

### Legacy Project Setup Pattern ❌ **DEPRECATED**
```python
# OLD PATTERN - NO LONGER USED
def setup_test_project(project_dir: Path) -> None:
    # This pattern required production template dependencies
    # and was brittle to template changes
    pass
```

### Multi-Command Workflow Pattern
```python
def test_create_then_retrieve_workflow(run_pantheon, temp_project):
    """Test CREATE followed by RETRIEVE operations."""
    setup_test_project(temp_project)
    
    # Step 1: Create artifact
    create_result = run_pantheon([
        "execute", "create-ticket",
        "--actor", "ticket-handler",
        "--title", "Test Ticket"
    ])
    assert create_result.returncode == 0
    
    # Step 2: Retrieve created artifact
    retrieve_result = run_pantheon([
        "execute", "get-ticket", 
        "--actor", "ticket-handler",
        "--id", "test-ticket"
    ])
    assert retrieve_result.returncode == 0
    assert "Test Ticket" in retrieve_result.stdout
```

## Testing Framework Integration

### Framework Installation Validation
- **CLI availability**: Verify pantheon command is properly installed
- **Python package**: Confirm framework package is importable
- **Template bundling**: Test bundled templates are accessible
- **Command registration**: Validate all CLI commands are available

### Team Package Integration Testing ✨ **UPDATED**
```python
def test_team_package_workflow(run_pantheon, temp_project, setup_test_project):
    """Test complete team package workflow with fixtures."""
    # Set up test project with fixture team
    project_info = setup_test_project()
    
    # Verify team structure from fixtures
    team_dir = temp_project / "pantheon-teams" / "pantheon-e2e-test"
    assert team_dir.exists()
    assert (team_dir / "team-profile.yaml").exists()
    
    # Test process execution with test team
    process_result = run_pantheon([
        "execute", "create-ticket",
        "--actor", "ticket-handler"
    ])
    assert process_result.returncode == 0
```

### Init Command Testing (Production Templates)
```python
def test_init_command_production(run_pantheon, temp_project):
    """Test init command with production templates only."""
    # This tests the actual init command behavior
    init_result = run_pantheon(["init"])  # Auto-selects pantheon-foundry
    assert init_result.returncode == 0
    
    # Verify production team was installed
    team_dir = temp_project / "pantheon-teams" / "pantheon-foundry"
    assert team_dir.exists()
```

### Profile Context Testing
```python
def test_profile_context_integration(run_pantheon, temp_project):
    """Test profile context injection through complete workflow."""
    setup_test_project_with_profile(temp_project, "development")
    
    result = run_pantheon([
        "execute", "test-process",
        "--actor", "test-actor"
    ])
    
    # Verify profile-specific behavior
    assert result.returncode == 0
    output_file = temp_project / "pantheon-artifacts" / "output.md"
    content = output_file.read_text()
    assert "development profile" in content
```

## Error Scenario Testing

### Permission Denied Testing
```python
def test_permission_denied_scenario(run_pantheon, temp_project):
    """Test proper handling of permission denied scenarios."""
    setup_test_project_with_restricted_permissions(temp_project)
    
    result = run_pantheon([
        "execute", "restricted-process",
        "--actor", "unauthorized-actor"
    ])
    
    assert result.returncode == 13  # Permission denied exit code
    assert "Permission denied" in result.stderr
```

### Invalid Input Testing
```python
def test_invalid_input_handling(run_pantheon, temp_project):
    """Test framework handles invalid inputs gracefully."""
    setup_test_project(temp_project)
    
    result = run_pantheon([
        "execute", "nonexistent-process",
        "--actor", "test-actor"
    ])
    
    assert result.returncode == 1  # Bad input exit code
    assert "Process not found" in result.stderr
```

## Performance and Reliability

### Test Execution Guidelines
- **Timeout handling**: Set appropriate timeouts for subprocess calls
- **Resource cleanup**: Ensure temporary directories are cleaned up
- **Parallel execution**: Design tests to run independently
- **Cross-platform compatibility**: Handle platform-specific path issues

### Test Reliability Patterns
```python
def test_with_retry_logic(run_pantheon, temp_project):
    """Test with retry logic for flaky operations."""
    setup_test_project(temp_project)
    
    for attempt in range(3):
        result = run_pantheon(["execute", "potentially-flaky-process"])
        if result.returncode == 0:
            break
        time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
    else:
        pytest.fail("Process failed after 3 attempts")
    
    assert "expected output" in result.stdout
```

## Data-Driven Testing

### Parametrized E2E Tests
```python
@pytest.mark.parametrize("process_name,actor,expected", [
    ("create-ticket", "ticket-handler", "Ticket created"),
    ("update-plan", "tech-lead", "Plan updated"),
    ("get-status", "viewer", "Status retrieved"),
])
def test_process_execution_variants(run_pantheon, temp_project, process_name, actor, expected):
    """Test multiple process execution scenarios."""
    setup_test_project(temp_project)
    
    result = run_pantheon([
        "execute", process_name,
        "--actor", actor
    ])
    
    assert result.returncode == 0
    assert expected in result.stdout
```

### Test Data Management

#### Test Fixtures Architecture
- **Test Teams**: `tests/fixtures/teams/pantheon-e2e-test/` - Isolated test team
- **Production Teams**: `pantheon/_templates/pantheon-teams/pantheon-team-builder/` - Production only
- **Complete Isolation**: Test teams never bundled in production builds
- **Robustness**: Tests immune to production template changes

#### Test Data Types
- **Sample data files**: JSON files with test parameters in fixtures
- **Configuration variants**: Different profile configurations
- **Expected outputs**: Golden master files for comparison
- **Agent definitions**: `ticket-handler` for test scenarios vs `pantheon` for production

## Test Architecture Principles

### ✅ **Current Best Practices**

1. **Use `setup_test_project` fixture** - Never call `pantheon init` in tests
2. **Import fixture in function signature** - Add `setup_test_project` parameter  
3. **Use `ticket-handler` actor** - Test team agent, not production `pantheon` agent
4. **Test complete isolation** - Each test gets fresh `pantheon-e2e-test` team copy
5. **No production dependencies** - Tests work regardless of bundled templates

### ❌ **Deprecated Patterns**

- ~~`run_pantheon(["init"], input_text="pantheon-skeleton\n")`~~ - Brittle, production-dependent
- ~~Hardcoded team names~~ - Broke when templates changed
- ~~`pantheon-skeleton` references~~ - No longer exists in production

### 🔄 **Migration Guide**

When updating E2E tests:

```python
# OLD: Brittle production dependency
def test_example(temp_project: Path, run_pantheon):
    init_result = run_pantheon(["init"], input_text="pantheon-skeleton\n")

# NEW: Robust fixture-based 
def test_example(temp_project: Path, run_pantheon, setup_test_project):
    setup_test_project()  # Uses fixtures automatically
```

## Running E2E Tests

### Execution Commands
```bash
# Run all E2E tests (now 25 tests, all passing!)
python -m pytest tests/e2e/ -v

# Run specific E2E test file
python -m pytest tests/e2e/test_golden_path.py -v

# Run with detailed output
python -m pytest tests/e2e/ -s -v --tb=long

# Run with timeout for long-running tests
python -m pytest tests/e2e/ --timeout=30
```

### Test Environment Setup
- **Framework installation**: Install framework in test environment
- **Temporary isolation**: Each test uses isolated temporary directory
- **Clean state**: No shared state between test executions
- **Real filesystem**: Tests use actual file operations

### CI/CD Integration
- **Test isolation**: Each test run in clean environment
- **Artifact collection**: Collect test outputs for debugging
- **Performance monitoring**: Track E2E test execution times
- **Flaky test detection**: Monitor for inconsistent test results