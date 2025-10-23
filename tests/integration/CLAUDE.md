# Integration Testing

## Integration Testing Philosophy

Integration tests validate **component interactions** using **real objects** rather than mocks, while maintaining **moderate execution speed**. These tests ensure components work correctly together and demonstrate **dependency injection** patterns in realistic scenarios.

### Integration Testing Scope
- **Component interactions**: Multiple components working together with real dependencies
- **Realistic I/O operations**: Real FileSystem with temporary directories
- **Framework integration**: Service layer coordination (Workspace + Artifact Engine)
- **Dependency injection validation**: Real implementation of abstract boundaries

### Integration vs Other Test Tiers
- **Unit Tests**: Single components with mocks (fast, isolated)
- **Integration Tests**: Multiple components with real objects (moderate speed, realistic)
- **E2E Tests**: Complete CLI workflows via subprocess (slow, comprehensive)

## Integration Test Patterns

### FileSystem Integration Testing

#### Real FileSystem with Temporary Directories
```python
def test_filesystem_integration(tmp_path):
    """Test FileSystem with real I/O operations."""
    # Arrange: Create real filesystem instance
    filesystem = FileSystem()
    test_file = tmp_path / "test_config.yaml"
    test_file.write_text("test: value")
    
    # Act: Use real filesystem operations
    content = filesystem.read_file(str(test_file))
    
    # Assert: Verify real file operations work
    assert content == "test: value"
```

#### Dependency Injection with Real Objects
```python
def test_workspace_filesystem_integration(tmp_path):
    """Test Workspace with real FileSystem dependency."""
    # Arrange: Inject real FileSystem into Workspace
    filesystem = FileSystem()
    workspace = Workspace(filesystem)
    
    # Create realistic directory structure
    setup_realistic_project_structure(tmp_path)
    
    # Act: Test high-level workspace methods with real I/O
    schema = workspace.get_process_schema("test-process", "test-actor")
    
    # Assert: Verify end-to-end functionality
    assert "test schema content" in schema
```

### Multi-Component Integration

#### Workspace + Artifact Engine Integration
```python
def test_workspace_artifact_engine_integration(tmp_path):
    """Test Workspace and Artifact Engine working together."""
    # Arrange: Set up multi-component system
    filesystem = FileSystem()
    workspace = Workspace(filesystem)
    artifact_engine = ArtifactEngine()
    
    # Create realistic test environment
    setup_team_package(tmp_path)
    
    # Act: Test coordinated operations
    template = workspace.get_artifact_content_template("create-ticket")
    rendered = artifact_engine.render_template(template, test_data)
    
    # Assert: Verify coordinated behavior
    assert "rendered content" in rendered
    assert artifact_engine.validate_output(rendered)
```

#### ProcessHandler Integration Testing
```python
def test_process_handler_integration(tmp_path):
    """Test ProcessHandler coordinating service components."""
    # Arrange: Set up realistic component stack
    filesystem = FileSystem()
    workspace = Workspace(filesystem)
    process_handler = ProcessHandler(workspace)
    
    setup_complete_test_environment(tmp_path)
    
    # Act: Test application layer orchestration
    result = process_handler.execute_process(
        "test-process", {"param": "value"}, "test-actor"
    )
    
    # Assert: Verify orchestration works correctly
    assert result.success
    assert result.artifacts_created == ["test-output.md"]
```

## Realistic Test Environment Setup

### Project Structure Simulation
```python
def setup_realistic_project_structure(project_dir: Path) -> None:
    """Create realistic project structure for integration testing."""
    # Project marker
    (project_dir / ".pantheon_project").write_text("test-team")
    
    # Team package structure
    team_dir = project_dir / "pantheon-teams" / "test-team"
    team_dir.mkdir(parents=True)
    
    # Team profile
    (team_dir / "team-profile.yaml").write_text("""
    team_name: test-team
    profiles:
      development:
        verbosity: true
        test_coverage: 80
    """)
    
    # Process structure
    process_dir = team_dir / "processes" / "test-process"
    process_dir.mkdir(parents=True)
    (process_dir / "routine.md").write_text("# Test Process Routine")
    (process_dir / "schema.jsonnet").write_text('{"param": "string"}')
    (process_dir / "permissions.jsonnet").write_text('{"allow": ["test-actor"]}')
    
    # Artifacts directory
    (project_dir / "pantheon-artifacts").mkdir()
```

### Team Package Integration
```python
def setup_team_package(project_dir: Path) -> None:
    """Set up complete team package for integration testing."""
    team_dir = project_dir / "pantheon-teams" / "integration-test-team"
    
    # Copy from fixtures or create programmatically
    create_agent_definitions(team_dir)
    create_process_definitions(team_dir)
    create_artifact_templates(team_dir)
    
    # Validate structure integrity
    validate_team_package_structure(team_dir)
```

## Error Handling Integration

### Permission Integration Testing
```python
def test_permission_integration_flow(tmp_path):
    """Test permission checking across component boundaries."""
    setup_project_with_permissions(tmp_path)
    
    filesystem = FileSystem()
    workspace = Workspace(filesystem)
    process_handler = ProcessHandler(workspace)
    
    # Test permission denial flows through components
    with pytest.raises(PermissionDenied) as exc_info:
        process_handler.execute_process(
            "restricted-process", {}, "unauthorized-actor"
        )
    
    assert "unauthorized-actor" in str(exc_info.value)
    assert exc_info.value.exit_code == 13
```

### Error Propagation Testing
```python
def test_error_propagation_integration(tmp_path):
    """Test error propagation through component stack."""
    setup_project_with_invalid_schema(tmp_path)
    
    filesystem = FileSystem()
    workspace = Workspace(filesystem)
    
    # Test errors bubble up correctly through layers
    with pytest.raises(SchemaValidationError) as exc_info:
        workspace.get_process_schema("invalid-process", "test-actor")
    
    # Verify error contains context from all layers
    assert "schema validation failed" in str(exc_info.value)
    assert "invalid-process" in str(exc_info.value)
```

## Profile Context Integration

### Profile Injection Testing
```python
def test_profile_context_integration(tmp_path):
    """Test profile context flows through all components."""
    setup_project_with_profile_context(tmp_path, "development")
    
    filesystem = FileSystem()
    workspace = Workspace(filesystem)
    artifact_engine = ArtifactEngine()
    
    # Test profile context is available throughout stack
    schema = workspace.get_process_schema("profile-aware-process", "test-actor")
    template = workspace.get_artifact_content_template("profile-aware-process")
    
    # Verify profile context in schema composition
    assert "development" in schema
    
    # Test profile context in template rendering
    rendered = artifact_engine.render_template(template, {}, profile_context="development")
    assert "development profile" in rendered
```

## Framework Boundary Integration

### PantheonPath Protection Integration
```python
def test_pantheon_path_protection_integration(tmp_path):
    """Test PantheonPath protection across component boundaries."""
    filesystem = FileSystem()
    workspace = Workspace(filesystem)
    
    # Create PantheonPath (protected)
    protected_path = PantheonPath(tmp_path / "protected_file.md")
    
    # Test only Workspace can unwrap paths
    content = workspace.read_file_content(protected_path)  # Should work
    
    # Verify other components cannot unwrap paths directly
    with pytest.raises(AttributeError):
        direct_path = protected_path.unwrap()  # Should fail outside Workspace
```

### Sandboxing Integration Testing
```python
def test_artifact_sandboxing_integration(tmp_path):
    """Test artifact sandboxing works across components."""
    setup_sandboxed_project(tmp_path)
    
    filesystem = FileSystem()
    workspace = Workspace(filesystem)
    
    # Test operations stay within sandbox
    result_path = workspace.create_artifact(
        "test-artifact", "content", "test-actor"
    )
    
    # Verify result is within artifacts sandbox
    artifacts_root = tmp_path / "pantheon-artifacts"
    assert result_path.is_relative_to(artifacts_root)
    
    # Verify cannot escape sandbox
    with pytest.raises(SandboxViolation):
        workspace.create_artifact_at_path("../../../etc/passwd", "content")
```

## Performance Integration Testing

### Resource Usage Integration
```python
def test_resource_usage_integration(tmp_path):
    """Test resource usage across integrated components."""
    setup_large_project_structure(tmp_path)
    
    filesystem = FileSystem()
    workspace = Workspace(filesystem)
    
    # Measure resource usage during integration operations
    start_time = time.time()
    
    # Perform resource-intensive integrated operations
    for i in range(100):
        schema = workspace.get_process_schema(f"process-{i}", "test-actor")
        template = workspace.get_artifact_content_template(f"process-{i}")
    
    execution_time = time.time() - start_time
    
    # Verify performance characteristics
    assert execution_time < 5.0  # Should complete within reasonable time
```

### Concurrent Operations Integration
```python
def test_concurrent_operations_integration(tmp_path):
    """Test concurrent operations across components."""
    import threading
    
    setup_project_for_concurrency_testing(tmp_path)
    
    filesystem = FileSystem()
    workspace = Workspace(filesystem)
    results = []
    errors = []
    
    def worker(process_name: str):
        try:
            result = workspace.get_process_schema(process_name, "test-actor")
            results.append(result)
        except Exception as e:
            errors.append(e)
    
    # Run concurrent operations
    threads = [
        threading.Thread(target=worker, args=[f"process-{i}"])
        for i in range(10)
    ]
    
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    # Verify concurrent operations work correctly
    assert len(results) == 10
    assert len(errors) == 0
```

## Running Integration Tests

### Execution Guidelines
```bash
# Run all integration tests
python -m pytest tests/integration/ -v

# Run specific integration test
python -m pytest tests/integration/test_filesystem_integration.py -v

# Run with detailed output and timing
python -m pytest tests/integration/ -s -v --durations=10

# Run integration tests with coverage
python -m pytest tests/integration/ --cov=pantheon --cov-report=html
```

### Test Environment Requirements
- **Temporary directories**: Each test gets isolated tmp_path
- **Real filesystem**: Tests use actual file operations
- **Component dependencies**: Real object instantiation
- **Moderate execution time**: Balance realism with speed (<100ms per test)

### Debugging Integration Issues
- **Component interaction**: Use debug logging to trace component calls
- **State inspection**: Examine intermediate states between components
- **Resource monitoring**: Monitor file handles and memory usage
- **Error context**: Capture full error context from all component layers