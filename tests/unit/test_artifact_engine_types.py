"""
Unit tests for ArtifactEngine type checking validation.

This test module runs mypy programmatically to ensure all method signatures
have complete type hints that pass static type checking. It verifies the
interface maintains strict type safety requirements.
"""

from pathlib import Path
import subprocess
import sys

import pytest


class TestArtifactEngineTypes:
    """Test suite for ArtifactEngine type checking with mypy."""

    def test_mypy_type_checking_passes(self):
        """Test that mypy validates ArtifactEngine with no type errors."""
        # Get the path to the artifact_engine module
        artifact_engine_path = Path("pantheon/artifact_engine.py")

        # Run mypy with strict type checking
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "mypy",
                str(artifact_engine_path),
                "--strict",
                "--follow-imports=silent",
                "--no-error-summary",
            ],
            capture_output=True,
            text=True,
        )

        # Check that mypy passes without errors
        assert result.returncode == 0, (
            f"mypy type checking failed:\n{result.stdout}\n{result.stderr}"
        )

    def test_no_missing_type_annotations(self):
        """Test that all methods have complete type annotations."""
        # Run mypy specifically checking for missing annotations
        artifact_engine_path = Path("pantheon/artifact_engine.py")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "mypy",
                str(artifact_engine_path),
                "--disallow-untyped-defs",
                "--disallow-incomplete-defs",
                "--follow-imports=silent",
                "--no-error-summary",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"Missing type annotations:\n{result.stdout}\n{result.stderr}"
        )

    def test_return_type_consistency(self):
        """Test that return types match documented contracts."""
        from typing import get_type_hints

        from pantheon.artifact_engine import ArtifactEngine
        from pantheon.path import PantheonPath

        # Get type hints for the class
        get_type_hints(ArtifactEngine)

        # Check specific method return types
        compile_schema = ArtifactEngine.compile_schema
        compile_schema_hints = get_type_hints(compile_schema)
        # Check that return type is dict with str keys
        return_type = compile_schema_hints.get("return")
        assert str(return_type).startswith("dict[str,") or str(return_type).startswith(
            "typing.Dict[str,"
        )

        generate_artifact = ArtifactEngine.generate_artifact
        generate_artifact_hints = get_type_hints(generate_artifact)
        assert generate_artifact_hints.get("return") == tuple[str, PantheonPath]

        find_artifact = ArtifactEngine.find_artifact
        find_artifact_hints = get_type_hints(find_artifact)
        # Union types may be represented differently
        return_type = find_artifact_hints.get("return")
        assert (
            return_type == PantheonPath | None
            or str(return_type) == "typing.Union[pantheon.path.PantheonPath, NoneType]"
        )

    def test_parameter_type_consistency(self):
        """Test that parameter types are properly annotated."""
        from typing import get_type_hints

        from pantheon.artifact_engine import ArtifactEngine

        # Check compile_schema parameters
        compile_schema = ArtifactEngine.compile_schema
        compile_schema_hints = get_type_hints(compile_schema)

        # Should have proper parameter types
        assert "schema_content" in compile_schema_hints
        assert "full_profile_content" in compile_schema_hints

        # Check generate_artifact parameters
        generate_artifact = ArtifactEngine.generate_artifact
        generate_artifact_hints = get_type_hints(generate_artifact)

        assert "templates" in generate_artifact_hints
        assert "input_params" in generate_artifact_hints
        assert "framework_params" in generate_artifact_hints

    def test_mypy_with_pantheon_path_imports(self):
        """Test that PantheonPath imports are properly resolved by mypy."""
        # Create a minimal test file that imports and uses PantheonPath
        test_code = """
from unittest.mock import Mock
from pantheon.artifact_engine import ArtifactEngine
from pantheon.path import PantheonPath

def test_function() -> None:
    mock_workspace = Mock()
    engine = ArtifactEngine(mock_workspace)
    framework_params: dict[str, str] = {}
    # This should type-check properly
    content, path = engine.generate_artifact({}, {}, framework_params)
    result: PantheonPath = path
"""

        # Write test file
        test_file = Path("test_mypy_temp.py")
        try:
            test_file.write_text(test_code)

            # Run mypy on the test file
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "mypy",
                    str(test_file),
                    "--strict",
                    "--follow-imports=silent",
                    "--no-error-summary",
                ],
                capture_output=True,
                text=True,
            )

            # Should pass type checking (even though it will raise NotImplementedError at runtime)
            assert result.returncode == 0, (
                f"PantheonPath type checking failed:\n{result.stdout}\n{result.stderr}"
            )

        finally:
            # Clean up test file
            if test_file.exists():
                test_file.unlink()

    @pytest.mark.skipif(
        subprocess.run(
            [sys.executable, "-m", "mypy", "--version"], capture_output=True
        ).returncode
        != 0,
        reason="mypy not available",
    )
    def test_strict_type_checking_config(self):
        """Test that the module passes strict mypy configuration."""
        artifact_engine_path = Path("pantheon/artifact_engine.py")

        # Test with very strict mypy settings
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "mypy",
                str(artifact_engine_path),
                "--strict",
                "--warn-return-any",
                "--warn-unused-configs",
                "--disallow-any-generics",
                "--follow-imports=silent",
                "--no-error-summary",
            ],
            capture_output=True,
            text=True,
        )

        # Allow some warnings but no errors
        assert result.returncode == 0, (
            f"Strict type checking failed:\n{result.stdout}\n{result.stderr}"
        )
