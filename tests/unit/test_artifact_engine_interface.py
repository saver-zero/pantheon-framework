"""
Unit tests for ArtifactEngine interface completeness and contracts.

This test module verifies that the ArtifactEngine interface is properly defined
with correct method signatures and maintains architectural boundaries. It ensures
the interface contract is complete without testing implementation details.
"""

import ast
import inspect
from typing import Any
from unittest.mock import Mock

import pytest

from pantheon.artifact_engine import ArtifactEngine
from pantheon.path import PantheonPath


class TestArtifactEngineInterface:
    """Test suite for ArtifactEngine interface definition and contracts."""

    def test_artifact_engine_class_exists(self):
        """Test that ArtifactEngine class exists and can be imported."""
        assert ArtifactEngine is not None
        assert inspect.isclass(ArtifactEngine)

    def test_artifact_engine_instantiation(self):
        """Test that ArtifactEngine can be instantiated."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)
        assert isinstance(engine, ArtifactEngine)

    def test_core_interface_methods_exist(self):
        """Test that all required core interface methods are present."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Check method existence
        assert hasattr(engine, "compile_schema")
        assert hasattr(engine, "validate")
        assert hasattr(engine, "generate_artifact")
        assert hasattr(engine, "find_artifact")
        assert hasattr(engine, "get_artifact_sections")

        # Check methods are callable
        assert callable(engine.compile_schema)
        assert callable(engine.validate)
        assert callable(engine.generate_artifact)
        assert callable(engine.find_artifact)
        assert callable(engine.get_artifact_sections)

    def test_private_helper_methods_exist(self):
        """Test that private helper methods are present but not part of public interface."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Check private method existence
        assert hasattr(engine, "_compile_jsonnet")
        assert hasattr(engine, "_render_with_environment")
        assert hasattr(engine, "_create_basic_jinja_environment")
        assert hasattr(engine, "_generate_path")
        assert hasattr(engine, "_generate_timestamp")
        assert hasattr(engine, "_generate_datestamp")
        assert hasattr(engine, "_parse_section_markers")

        # Check methods are callable
        assert callable(engine._compile_jsonnet)
        assert callable(engine._render_with_environment)
        assert callable(engine._create_basic_jinja_environment)
        assert callable(engine._generate_path)
        assert callable(engine._generate_timestamp)
        assert callable(engine._generate_datestamp)
        assert callable(engine._parse_section_markers)

    def test_workspace_dependency_injection(self):
        """Test that ArtifactEngine requires workspace dependency injection."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)
        assert engine._workspace is mock_workspace

    def test_compile_schema_signature(self):
        """Test that compile_schema has the correct method signature."""
        method = ArtifactEngine.compile_schema
        sig = inspect.signature(method)

        # Check parameter names and types
        params = sig.parameters
        assert "self" in params
        assert "schema_content" in params
        assert "full_profile_content" in params  # Fixed parameter name

        # Check return annotation
        assert sig.return_annotation == dict[str, Any]

    def test_validate_signature(self):
        """Test that validate has the correct method signature."""
        method = ArtifactEngine.validate
        sig = inspect.signature(method)

        # Check parameter names
        params = sig.parameters
        assert "self" in params
        assert "input_data" in params  # Updated parameter name
        assert "schema" in params

        # Check return annotation
        assert sig.return_annotation is bool

    def test_generate_artifact_signature(self):
        """Test that generate_artifact has the correct method signature."""
        method = ArtifactEngine.generate_artifact
        sig = inspect.signature(method)

        # Check parameter names
        params = sig.parameters
        assert "self" in params
        assert "templates" in params
        assert "input_params" in params  # Updated parameter name
        assert "framework_params" in params  # Added new parameter

        # Check return annotation
        assert sig.return_annotation == tuple[str, PantheonPath]

    def test_get_artifact_sections_signature(self):
        """Test that get_artifact_sections has the correct method signature."""
        method = ArtifactEngine.get_artifact_sections
        sig = inspect.signature(method)

        # Check parameter names
        params = sig.parameters
        assert "self" in params
        assert "process_name" in params
        assert "artifact_path" in params
        assert "section_names" in params

        # Check return annotation
        assert sig.return_annotation == dict[str, str]

    def test_find_artifact_signature(self):
        """Test that find_artifact has the correct method signature."""
        method = ArtifactEngine.find_artifact
        sig = inspect.signature(method)

        # Check parameter names
        params = sig.parameters
        assert "self" in params
        assert "process_name" in params
        assert "artifact_id" in params
        # search_directory parameter removed in new interface
        assert "search_directory" not in params

        # Check return annotation is Optional[PantheonPath]
        assert sig.return_annotation == PantheonPath | None

    def test_no_filesystem_dependency(self):
        """Test that ArtifactEngine has no FileSystem dependency."""
        # Parse the artifact_engine.py source file
        import pantheon.artifact_engine

        module_file = pantheon.artifact_engine.__file__

        with open(module_file, encoding="utf-8") as f:
            source_code = f.read()

        # Parse AST to check imports
        tree = ast.parse(source_code)

        # Check for any FileSystem imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "filesystem" not in alias.name.lower()
                    assert "FileSystem" not in alias.name
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "filesystem" not in node.module.lower()
                for alias in node.names:
                    assert "FileSystem" not in alias.name

    def test_pantheon_path_return_types(self):
        """Test that path-returning methods use PantheonPath instead of pathlib.Path."""
        # Check generate_artifact returns tuple with PantheonPath
        generate_artifact_method = ArtifactEngine.generate_artifact
        generate_artifact_sig = inspect.signature(generate_artifact_method)
        assert generate_artifact_sig.return_annotation == tuple[str, PantheonPath]

        # Check find_artifact returns Optional[PantheonPath]
        find_artifact_method = ArtifactEngine.find_artifact
        find_artifact_sig = inspect.signature(find_artifact_method)
        assert find_artifact_sig.return_annotation == PantheonPath | None

    def test_generation_methods_are_implemented(self):
        """Test that Generation Methods are now implemented.

        All methods (find_artifact, get_artifact_sections, compile_schema,
        validate, generate_artifact) should be working implementations.
        """
        mock_workspace = Mock()

        # Mock the Jinja2 environment for any method calls that might need it
        mock_env = Mock()
        filters_dict = {}  # Use a real dict that supports item assignment
        mock_env.filters = filters_dict
        mock_workspace.get_artifact_template_environment.return_value = mock_env

        engine = ArtifactEngine(mock_workspace)

        # Test that methods exist and are callable (basic smoke test)
        assert callable(engine.compile_schema)
        assert callable(engine.validate)
        assert callable(engine.generate_artifact)

        # Test that they don't raise NotImplementedError with valid inputs
        # (The actual functionality is tested in other test files)
        try:
            # This should raise ValueError for empty content, not NotImplementedError
            engine.compile_schema("", "")
        except ValueError:
            pass  # Expected - empty content is invalid
        except NotImplementedError:
            pytest.fail("compile_schema should not raise NotImplementedError")
