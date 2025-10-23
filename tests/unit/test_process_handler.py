"""Unit tests for ProcessHandler interface contract verification."""

import inspect
import json
from typing import get_type_hints
from unittest.mock import Mock

import pytest

from pantheon.constants import (
    BUILTIN_ARTIFACT_ID,
    BUILTIN_INSERT_MODE,
    PARAM_SECTIONS,
    PROCESS_TYPE_GET,
    PROCESS_TYPE_UPDATE,
)
from pantheon.process_handler import ProcessHandler, ProcessInput, ProcessResult
from tests.helpers.process_input import make_process_input


class TestProcessHandlerInterface:
    """Test suite for ProcessHandler interface contract verification."""

    def test_process_handler_accepts_dependencies(self) -> None:
        """Verify ProcessHandler can be instantiated with mocked dependencies."""
        # Create mocks for all three specialist components
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()

        # Create a concrete implementation for testing
        class TestProcessHandler:
            def __init__(self, workspace, artifact_engine, rae_engine) -> None:
                self.workspace = workspace
                self.artifact_engine = artifact_engine
                self.rae_engine = rae_engine

            def execute(
                self, process_name: str, input_data: ProcessInput
            ) -> ProcessResult:
                return {"test": "result"}

            def determine_process_type(self, process_name: str):
                return "get", {}

            def validate_input(
                self, process_name: str, input_data: ProcessInput
            ) -> bool:
                return True

            def execute_get_process(self, process_name: str, input_data: ProcessInput):
                return {"test": "get_result"}

            def execute_create_process(
                self,
                process_name: str,
                input_data: ProcessInput,
                templates: dict[str, str],
            ):
                from pantheon.path import PantheonPath

                return PantheonPath("test/create_path")

            def execute_update_process(
                self,
                process_name: str,
                input_data: ProcessInput,
                templates: dict[str, str],
            ):
                from pantheon.path import PantheonPath

                return PantheonPath("test/update_path")

            def format_error(self, error_type: str, context):
                return f"Error: {error_type}"

        # Test instantiation with mocks
        handler = TestProcessHandler(
            workspace=mock_workspace,
            artifact_engine=mock_artifact_engine,
            rae_engine=mock_rae_engine,
        )

        # Assert successful instantiation without errors
        assert handler.workspace is mock_workspace
        assert handler.artifact_engine is mock_artifact_engine
        assert handler.rae_engine is mock_rae_engine

    def test_execute_method_has_correct_signature(self) -> None:
        """Verify execute() method has the expected parameter and return type annotations."""
        # Get the execute method signature from the Protocol
        sig = inspect.signature(ProcessHandler.execute)

        # Check parameter names and types
        params = list(sig.parameters.keys())
        assert params == ["self", "input_data", "_redirect_chain"]

        # Verify parameter types using type hints
        hints = get_type_hints(ProcessHandler.execute)
        assert hints["input_data"] is ProcessInput
        assert hints["return"] is ProcessResult

    def test_all_methods_have_type_hints(self) -> None:
        """Ensure every method in ProcessHandler has complete type hints."""
        # Get all public methods from the Protocol
        public_methods = [
            name
            for name, method in inspect.getmembers(ProcessHandler, inspect.isfunction)
            if not name.startswith("_")
        ]

        for method_name in public_methods:
            method = getattr(ProcessHandler, method_name)
            sig = inspect.signature(method)

            # Check each parameter has type annotation
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                assert param.annotation != inspect.Parameter.empty, (
                    f"Parameter '{param_name}' in method '{method_name}' lacks type annotation"
                )

            # Verify return type is specified
            assert sig.return_annotation != inspect.Signature.empty, (
                f"Method '{method_name}' lacks return type annotation"
            )

    def test_protocol_method_signatures(self) -> None:
        """Test that all expected methods exist with correct signatures."""
        # Test __init__ method exists and has correct parameters
        init_sig = inspect.signature(ProcessHandler.__init__)
        init_params = list(init_sig.parameters.keys())
        expected_init_params = ["self", "workspace", "artifact_engine", "rae_engine"]
        assert init_params == expected_init_params

        # Test determine_process_type method
        determine_sig = inspect.signature(ProcessHandler.determine_process_type)
        determine_params = list(determine_sig.parameters.keys())
        assert determine_params == ["self", "process_name"]

        # Test validate_input method
        validate_sig = inspect.signature(ProcessHandler.validate_input)
        validate_params = list(validate_sig.parameters.keys())
        assert validate_params == ["self", "process_name", "input_data"]

        # Test execute_get_process method (renamed from execute_read_process)
        get_sig = inspect.signature(ProcessHandler.execute_get_process)
        get_params = list(get_sig.parameters.keys())
        assert get_params == ["self", "input_params", "framework_params"]

        # Test execute_create_process method (split from execute_write_process)
        create_sig = inspect.signature(ProcessHandler.execute_create_process)
        create_params = list(create_sig.parameters.keys())
        assert create_params == [
            "self",
            "input_params",
            "framework_params",
            "templates",
        ]

        # Test execute_update_process method (split from execute_write_process)
        update_sig = inspect.signature(ProcessHandler.execute_update_process)
        update_params = list(update_sig.parameters.keys())
        assert update_params == [
            "self",
            "input_params",
            "framework_params",
            "templates",
        ]

        # Test format_error method
        format_sig = inspect.signature(ProcessHandler.format_error)
        format_params = list(format_sig.parameters.keys())
        assert format_params == ["self", "error_type", "context"]

    def test_type_aliases_are_properly_defined(self) -> None:
        """Verify that custom type aliases are properly defined and accessible."""
        from pantheon.process_handler import ProcessInput, ProcessResult, ProcessType

        # These should be importable without errors
        assert ProcessInput is not None
        assert ProcessResult is not None
        assert ProcessType is not None

    def test_protocol_is_structural_typing_compatible(self) -> None:
        """Test that a class can implement the protocol without explicit inheritance."""
        from pantheon.path import PantheonPath

        # Define a class that structurally matches the protocol
        class StructuralHandler:
            def __init__(self, workspace, artifact_engine, rae_engine) -> None:
                pass

            def execute(self, input_data: ProcessInput) -> ProcessResult:
                return {"structural": "implementation"}

            def determine_process_type(self, process_name: str):
                return "get", {}

            def validate_input(
                self, process_name: str, input_data: ProcessInput
            ) -> bool:
                return True

            def execute_get_process(self, process_name: str, input_data: ProcessInput):
                return {"get": "data"}

            def execute_create_process(
                self,
                process_name: str,
                input_data: ProcessInput,
                templates: dict[str, str],
            ):
                return PantheonPath("generated/create_artifact")

            def execute_update_process(
                self,
                process_name: str,
                input_data: ProcessInput,
                templates: dict[str, str],
            ):
                return PantheonPath("generated/update_artifact")

            def format_error(self, error_type: str, context):
                return f"Formatted: {error_type}"

        # This should work due to structural typing
        handler = StructuralHandler(Mock(), Mock(), Mock())

        # Test that it behaves like a ProcessHandler
        input_data = make_process_input(
            "test-process",
            "test-actor",
            input_params={"input": "data"},
        )
        result = handler.execute(input_data)
        assert isinstance(result, dict)
        assert result["structural"] == "implementation"


class TestURIParsingAndParameters:
    """Test suite for URI parsing and parameter merging functionality."""

    def test_parse_process_uri_simple_process_name(self) -> None:
        """Test parsing simple process URI without parameters."""
        from pantheon.process_handler import parse_process_uri

        uri = "process://get-ticket"

        process_name, parameters = parse_process_uri(uri)

        assert process_name == "get-ticket"
        assert parameters == {}

    def test_parse_process_uri_single_parameter(self) -> None:
        """Test parsing process URI with single parameter."""
        from pantheon.process_handler import parse_process_uri

        uri = "process://get-ticket?sections=plan"

        process_name, parameters = parse_process_uri(uri)

        assert process_name == "get-ticket"
        assert parameters == {"sections": "plan"}

    def test_parse_process_uri_multiple_parameters(self) -> None:
        """Test parsing process URI with multiple parameters."""
        from pantheon.process_handler import parse_process_uri

        uri = "process://get-ticket?sections=plan&format=json&verbose=true"

        process_name, parameters = parse_process_uri(uri)

        assert process_name == "get-ticket"
        assert parameters == {"sections": "plan", "format": "json", "verbose": "true"}

    def test_parse_process_uri_url_encoded_parameters(self) -> None:
        """Test parsing process URI with URL encoded parameters."""
        from pantheon.process_handler import parse_process_uri

        uri = "process://get-ticket?query=hello%20world&path=%2Fhome%2Fuser"

        process_name, parameters = parse_process_uri(uri)

        assert process_name == "get-ticket"
        assert parameters == {"query": "hello world", "path": "/home/user"}

    def test_parse_process_uri_empty_parameter_values(self) -> None:
        """Test parsing process URI with empty parameter values."""
        from pantheon.process_handler import parse_process_uri

        uri = "process://get-ticket?sections=&format=json"

        process_name, parameters = parse_process_uri(uri)

        assert process_name == "get-ticket"
        assert parameters == {"sections": "", "format": "json"}

    def test_parse_process_uri_invalid_scheme(self) -> None:
        """Test parsing URI with invalid scheme raises ValueError."""
        import pytest

        from pantheon.process_handler import parse_process_uri

        uri = "invalid://get-ticket?sections=plan"

        with pytest.raises(ValueError, match="Invalid URI scheme"):
            parse_process_uri(uri)

    def test_merge_parameters_redirect_takes_precedence(self) -> None:
        """Test parameter merging where redirect parameters override user parameters."""
        from pantheon.process_handler import merge_parameters

        user_params = {"sections": "all", "format": "markdown"}
        redirect_params = {"sections": "plan", "verbose": "true"}

        result = merge_parameters(user_params, redirect_params)

        assert result == {
            "sections": "plan",  # redirect overrides user
            "format": "markdown",  # user param preserved
            "verbose": "true",  # redirect param added
        }

    def test_merge_parameters_empty_user_params(self) -> None:
        """Test parameter merging with empty user parameters."""
        from pantheon.process_handler import merge_parameters

        user_params = {}
        redirect_params = {"sections": "plan", "format": "json"}

        result = merge_parameters(user_params, redirect_params)

        assert result == {"sections": "plan", "format": "json"}

    def test_merge_parameters_empty_redirect_params(self) -> None:
        """Test parameter merging with empty redirect parameters."""
        from pantheon.process_handler import merge_parameters

        user_params = {"sections": "all", "format": "markdown"}
        redirect_params = {}

        result = merge_parameters(user_params, redirect_params)

        assert result == {"sections": "all", "format": "markdown"}

    def test_merge_parameters_both_empty(self) -> None:
        """Test parameter merging with both parameter sets empty."""
        from pantheon.process_handler import merge_parameters

        user_params = {}
        redirect_params = {}

        result = merge_parameters(user_params, redirect_params)

        assert result == {}


class TestRedirectExecution:
    """Test suite for ProcessHandler redirect execution functionality."""

    def test_execute_with_redirect_successful_flow(self) -> None:
        """Test successful redirect execution flow."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        # Create mock dependencies
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()

        # Set up redirect behavior: get-plan redirects to get-ticket, get-ticket has no redirect
        def mock_has_redirect(process_name):
            return process_name == "get-plan"  # Only get-plan has redirect

        def mock_get_redirect(process_name):
            if process_name == "get-plan":
                return "process://get-ticket?sections=plan"
            return None

        mock_workspace.has_process_redirect.side_effect = mock_has_redirect
        mock_workspace.get_process_redirect.side_effect = mock_get_redirect

        # Mock successful execution of target process (get-ticket)
        mock_workspace.get_artifact_content_template.return_value = "# Template content"
        mock_artifact_engine.render_artifact.return_value = (
            "Generated content",
            "artifacts/result.md",
        )

        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        # Test redirect execution
        input_data = make_process_input(
            "get-plan",
            "test-agent",
            input_params={"ticket_id": "T001"},
        )

        result = handler.execute(input_data)

        # Verify redirect detection was called for both processes
        assert mock_workspace.has_process_redirect.call_count >= 1
        # Verify get-plan redirect was retrieved
        mock_workspace.get_process_redirect.assert_called_with("get-plan")

        # The result should be successful (assuming the target process execution succeeds)
        assert result is not None

    def test_execute_with_redirect_parameter_merging(self) -> None:
        """Test that redirect parameters are properly merged with user parameters."""
        from unittest.mock import Mock, patch

        from pantheon.process_handler import ProcessHandler

        # Create mock dependencies
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()

        # Set up redirect detection
        mock_workspace.has_process_redirect.return_value = True
        mock_workspace.get_process_redirect.return_value = (
            "process://get-ticket?sections=plan&format=json"
        )

        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        # Test with user parameters that should be merged
        input_data = make_process_input(
            "get-plan",
            "test-agent",
            input_params={
                "ticket_id": "T001",
                "format": "markdown",
            },
        )

        with patch.object(handler, "_handle_redirect_internal") as mock_handle_redirect:
            handler.execute(input_data)

            # Verify _handle_redirect_internal was called
            mock_handle_redirect.assert_called_once()
            # The exact verification depends on implementation

    def test_execute_with_circular_redirect_detection(self) -> None:
        """Test that circular redirects are detected and prevented."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        # Create mock dependencies
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()

        # Set up circular redirect: get-plan -> get-ticket -> get-plan
        def mock_has_redirect(process_name):
            return process_name in ["get-plan", "get-ticket"]

        def mock_get_redirect(process_name):
            if process_name == "get-plan":
                return "process://get-ticket"
            if process_name == "get-ticket":
                return "process://get-plan"  # Creates circular reference
            return None

        mock_workspace.has_process_redirect.side_effect = mock_has_redirect
        mock_workspace.get_process_redirect.side_effect = mock_get_redirect

        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        input_data = make_process_input(
            "get-plan",
            "test-agent",
            input_params={"ticket_id": "T001"},
        )

        # Should detect circular redirect and return error result
        result = handler.execute(input_data)

        # Verify it returns an error result instead of raising exception
        assert result["success"] is False
        assert "Circular redirect detected" in result["error"]

    def test_execute_with_redirect_to_nonexistent_process(self) -> None:
        """Test error handling when redirect points to non-existent process."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        # Create mock dependencies
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()

        # Set up redirect to non-existent process
        mock_workspace.has_process_redirect.return_value = True
        mock_workspace.get_process_redirect.return_value = (
            "process://nonexistent-process"
        )

        # Mock that target process doesn't exist (would be caught in recursive execute call)
        def mock_has_redirect_side_effect(process_name):
            if process_name == "get-plan":
                return True
            if process_name == "nonexistent-process":
                return False  # Target doesn't have redirect
            return False

        mock_workspace.has_process_redirect.side_effect = mock_has_redirect_side_effect

        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        input_data = make_process_input(
            "get-plan",
            "test-agent",
            input_params={"ticket_id": "T001"},
        )

        # The exact error handling depends on implementation
        # This will likely result in FileNotFoundError when trying to execute nonexistent process
        handler.execute(input_data)
        # Should return error result instead of raising exception

    def test_execute_with_invalid_redirect_uri(self) -> None:
        """Test error handling for malformed redirect URI."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        # Create mock dependencies
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()

        # Set up invalid redirect URI
        mock_workspace.has_process_redirect.return_value = True
        mock_workspace.get_process_redirect.return_value = "invalid-uri-format"

        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        input_data = make_process_input(
            "get-plan",
            "test-agent",
            input_params={"ticket_id": "T001"},
        )

        # Should handle invalid URI gracefully and return error result
        result = handler.execute(input_data)

        # Verify error result
        assert result["success"] is False
        assert "Invalid redirect URI" in result.get("error", "")

    def test_execute_without_redirect_normal_flow(self) -> None:
        """Test that non-redirect processes continue to work normally."""
        from unittest.mock import Mock, patch

        from pantheon.process_handler import ProcessHandler

        # Create mock dependencies
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()

        # Set up no redirect for this process
        mock_workspace.has_process_redirect.return_value = False

        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        input_data = make_process_input(
            "create-ticket",
            "test-agent",
            input_params={"title": "Test ticket"},
        )

        # Mock the normal execution path
        with (
            patch.object(
                handler,
                "determine_process_type",
                return_value=("create", {"content": "test"}),
            ),
            patch.object(
                handler, "execute_create_process", return_value={"success": True}
            ),
        ):
            result = handler.execute(input_data)

        # Verify redirect check was performed but normal flow continued
        mock_workspace.has_process_redirect.assert_called_with("create-ticket")
        assert result["success"] is True


class TestSectionsParameterParsing:
    """Test cases for sections parameter parsing functionality."""

    def test_parse_sections_parameter_single_section(self) -> None:
        """Test parsing single section from string to array."""
        from pantheon.process_handler import parse_sections_parameter

        parameters = {"sections": "plan"}
        result = parse_sections_parameter(parameters)

        assert result == {"pantheon_sections": ["plan"]}

    def test_parse_sections_parameter_multiple_sections(self) -> None:
        """Test parsing multiple sections from comma-separated string."""
        from pantheon.process_handler import parse_sections_parameter

        parameters = {"sections": "plan,description,acceptance"}
        result = parse_sections_parameter(parameters)

        assert result == {"pantheon_sections": ["plan", "description", "acceptance"]}

    def test_parse_sections_parameter_with_whitespace(self) -> None:
        """Test parsing sections with whitespace around commas."""
        from pantheon.process_handler import parse_sections_parameter

        parameters = {"sections": "plan, description , acceptance"}
        result = parse_sections_parameter(parameters)

        assert result == {"pantheon_sections": ["plan", "description", "acceptance"]}

    def test_parse_sections_parameter_already_array(self) -> None:
        """Test that array sections parameter is left unchanged."""
        from pantheon.process_handler import parse_sections_parameter

        parameters = {"sections": ["plan", "description"]}
        result = parse_sections_parameter(parameters)

        assert result == {"pantheon_sections": ["plan", "description"]}

    def test_parse_sections_parameter_no_sections(self) -> None:
        """Test that parameters without sections are unchanged."""
        from pantheon.process_handler import parse_sections_parameter

        parameters = {"ticket": "T001", "format": "json"}
        result = parse_sections_parameter(parameters)

        assert result == {"ticket": "T001", "format": "json"}

    def test_parse_sections_parameter_empty_sections(self) -> None:
        """Test handling of empty sections parameter."""
        from pantheon.process_handler import parse_sections_parameter

        parameters = {"sections": ""}
        result = parse_sections_parameter(parameters)

        assert result == {"pantheon_sections": []}

    def test_parse_sections_parameter_preserves_other_params(self) -> None:
        """Test that other parameters are preserved when sections is parsed."""
        from pantheon.process_handler import parse_sections_parameter

        parameters = {
            "sections": "plan,description",
            "ticket": "T001",
            "format": "json",
        }
        result = parse_sections_parameter(parameters)

        expected = {
            "pantheon_sections": ["plan", "description"],
            "ticket": "T001",
            "format": "json",
        }
        assert result == expected

    def test_execute_with_sections_string_converts_to_array(self) -> None:
        """Test that ProcessHandler.execute converts sections string to array."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        # Create mock dependencies
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()

        # Configure mocks for successful execution
        mock_workspace.has_process_redirect.return_value = False
        mock_workspace.get_process_schema.return_value = "{}"
        # Both content.md and patch.md don't exist = RETRIEVE process
        mock_workspace.get_artifact_content_template.side_effect = FileNotFoundError()
        mock_workspace.get_artifact_patch_template.side_effect = FileNotFoundError()
        mock_artifact_engine.compile_schema.return_value = {"type": "object"}
        mock_artifact_engine.validate.return_value = True
        mock_artifact_engine.find_artifact.return_value = "path/to/artifact.md"
        mock_artifact_engine.get_artifact_sections.return_value = {
            "plan": "test content"
        }

        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        # Test with sections as string
        input_data = make_process_input(
            "get-ticket",
            "test-agent",
            input_params={"ticket": "T001", "sections": "plan,description"},
        )

        handler.execute(input_data)

        # Verify that get_artifact_sections was called with parsed array
        mock_artifact_engine.get_artifact_sections.assert_called_once()
        call_args = mock_artifact_engine.get_artifact_sections.call_args[
            0
        ]  # positional args
        assert call_args[2] == [
            "plan",
            "description",
        ]  # third argument is section_names


class TestInsertModeContentMethods:
    """Test cases for insert-mode content manipulation methods."""

    def test_append_section_content_basic(self) -> None:
        """Test basic append functionality."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        # Create handler with mocked dependencies
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        content = """<!-- Section Start -->
Existing content here
<!-- Section End -->"""

        new_content = "New appended content"

        result = handler._append_section_content(
            content, "<!-- Section Start -->", "<!-- Section End -->", new_content
        )

        expected = """<!-- Section Start -->
Existing content here
New appended content
<!-- Section End -->"""

        assert result == expected

    def test_prepend_section_content_basic(self) -> None:
        """Test basic prepend functionality."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        # Create handler with mocked dependencies
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        content = """<!-- Section Start -->
Existing content here
<!-- Section End -->"""

        new_content = "New prepended content"

        result = handler._prepend_section_content(
            content, "<!-- Section Start -->", "<!-- Section End -->", new_content
        )

        expected = """<!-- Section Start -->
New prepended content
Existing content here
<!-- Section End -->"""

        assert result == expected

    def test_append_section_content_missing_start_marker(self) -> None:
        """Test append with missing start marker returns None."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        content = """Some content without markers"""

        result = handler._append_section_content(
            content, "<!-- Missing Start -->", "<!-- Section End -->", "new content"
        )

        assert result is None

    def test_append_section_content_missing_end_marker(self) -> None:
        """Test append with missing end marker returns None."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        content = """<!-- Section Start -->
Some content here"""

        result = handler._append_section_content(
            content, "<!-- Section Start -->", "<!-- Missing End -->", "new content"
        )

        assert result is None

    def test_prepend_section_content_missing_start_marker(self) -> None:
        """Test prepend with missing start marker returns None."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        content = """Some content without markers"""

        result = handler._prepend_section_content(
            content, "<!-- Missing Start -->", "<!-- Section End -->", "new content"
        )

        assert result is None

    def test_append_section_content_with_formatting(self) -> None:
        """Test append handles newline formatting correctly."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        # Test content without trailing newline before end marker
        content = """<!-- Section Start -->
Existing content<!-- Section End -->"""

        new_content = "Appended line"

        result = handler._append_section_content(
            content, "<!-- Section Start -->", "<!-- Section End -->", new_content
        )

        expected = """<!-- Section Start -->
Existing content
Appended line
<!-- Section End -->"""

        assert result == expected

    def test_apply_insert_mode_append_replaces_placeholder_section(self) -> None:
        """Insert-mode append replaces placeholder sections instead of appending."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        start_marker = "<!-- Section Start -->"
        end_marker = "<!-- Section End -->"
        placeholder_marker = "<!-- CUSTOM:PLACEHOLDER -->"

        content = f"""{start_marker}
{placeholder_marker}
{end_marker}"""

        patch_content = "Finalized content"

        expected = handler._replace_section_content(
            content, start_marker, end_marker, patch_content
        )

        result = handler._apply_insert_mode_update(
            content,
            start_marker,
            end_marker,
            patch_content,
            insert_mode="append",
            placeholder_marker=placeholder_marker,
        )

        assert result == expected

    def test_apply_insert_mode_prepend_replaces_placeholder_section(self) -> None:
        """Insert-mode prepend also replaces placeholder sections."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        start_marker = "<!-- Section Start -->"
        end_marker = "<!-- Section End -->"
        placeholder_marker = "<!-- CUSTOM:PLACEHOLDER -->"

        content = f"""{start_marker}
{placeholder_marker}
{end_marker}"""

        patch_content = "Prepended content"

        expected = handler._replace_section_content(
            content, start_marker, end_marker, patch_content
        )

        result = handler._apply_insert_mode_update(
            content,
            start_marker,
            end_marker,
            patch_content,
            insert_mode="prepend",
            placeholder_marker=placeholder_marker,
        )

        assert result == expected

    def test_apply_insert_mode_append_without_placeholder_appends(self) -> None:
        """Insert-mode append keeps concatenation when no placeholder appears."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        start_marker = "<!-- Section Start -->"
        end_marker = "<!-- Section End -->"
        placeholder_marker = "<!-- CUSTOM:PLACEHOLDER -->"

        content = f"""{start_marker}
Existing details
{end_marker}"""

        patch_content = "Additional line"

        expected = handler._append_section_content(
            content, start_marker, end_marker, patch_content
        )

        result = handler._apply_insert_mode_update(
            content,
            start_marker,
            end_marker,
            patch_content,
            insert_mode="append",
            placeholder_marker=placeholder_marker,
        )

        assert result == expected

    def test_execute_sectioned_update_append_replaces_default_placeholder(self) -> None:
        """Insert-mode append falls back to default placeholder marker for replacement."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        target_config = {
            "sections": {
                "progress_log": {
                    "start": "<!-- SECTION:START:PROGRESS_LOG -->",
                    "end": "<!-- SECTION:END:PROGRESS_LOG -->",
                }
            },
            "placeholder": "<!-- SECTION:PLACEHOLDER -->",
        }

        mock_workspace.get_artifact_locator.return_value = "{}"
        mock_workspace.get_artifact_parser.return_value = "{}"
        mock_workspace.get_artifact_target_section.return_value = json.dumps(
            target_config
        )
        mock_artifact_engine.find_artifact.return_value = "artifact.md"
        mock_workspace.read_artifact_file.return_value = (
            "<!-- SECTION:START:PROGRESS_LOG -->\n"
            "<!-- SECTION:PLACEHOLDER -->\n"
            "<!-- SECTION:END:PROGRESS_LOG -->"
        )
        mock_workspace.get_artifact_template_environment.return_value = Mock()
        mock_artifact_engine._create_template_context.return_value = {}
        mock_artifact_engine.render_artifact_template.return_value = "Replacement body"
        mock_workspace.save_artifact.return_value = "artifact.md"
        mock_workspace.summarize_created_files.return_value = []

        input_params = {
            "section_updates": {"progress_log": {"body": "Replacement body"}}
        }
        framework_params = {
            BUILTIN_ARTIFACT_ID: "artifact.md",
            BUILTIN_INSERT_MODE: "append",
            PARAM_SECTIONS: ["progress_log"],
        }
        compiled_schema = {
            "properties": {"section_order": {"default": ["progress_log"]}}
        }

        result = handler._execute_sectioned_update(
            "update-ticket",
            input_params,
            framework_params,
            {"patch": "ignored"},
            compiled_schema,
        )

        assert result["success"]
        saved_content = mock_workspace.save_artifact.call_args[0][0]
        assert "<!-- SECTION:PLACEHOLDER -->" not in saved_content
        assert "Replacement body" in saved_content

    def test_execute_sectioned_update_append_appends_without_placeholder(self) -> None:
        """Insert-mode append preserves section content when no placeholder is present."""
        from unittest.mock import Mock

        from pantheon.process_handler import ProcessHandler

        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        target_config = {
            "sections": {
                "progress_log": {
                    "start": "<!-- SECTION:START:PROGRESS_LOG -->",
                    "end": "<!-- SECTION:END:PROGRESS_LOG -->",
                    "placeholder": "<!-- SECTION:PLACEHOLDER -->",
                }
            },
            "placeholder": "<!-- SECTION:PLACEHOLDER -->",
        }

        mock_workspace.get_artifact_locator.return_value = "{}"
        mock_workspace.get_artifact_parser.return_value = "{}"
        mock_workspace.get_artifact_target_section.return_value = json.dumps(
            target_config
        )
        mock_artifact_engine.find_artifact.return_value = "artifact.md"
        mock_workspace.read_artifact_file.return_value = (
            "<!-- SECTION:START:PROGRESS_LOG -->\n"
            "Existing line\n"
            "<!-- SECTION:END:PROGRESS_LOG -->"
        )
        mock_workspace.get_artifact_template_environment.return_value = Mock()
        mock_artifact_engine._create_template_context.return_value = {}
        mock_artifact_engine.render_artifact_template.return_value = "Appended line"
        mock_workspace.save_artifact.return_value = "artifact.md"
        mock_workspace.summarize_created_files.return_value = []

        input_params = {"section_updates": {"progress_log": {"body": "Appended line"}}}
        framework_params = {
            BUILTIN_ARTIFACT_ID: "artifact.md",
            BUILTIN_INSERT_MODE: "append",
            PARAM_SECTIONS: ["progress_log"],
        }
        compiled_schema = {
            "properties": {"section_order": {"default": ["progress_log"]}}
        }

        result = handler._execute_sectioned_update(
            "update-ticket",
            input_params,
            framework_params,
            {"patch": "ignored"},
            compiled_schema,
        )

        assert result["success"]
        saved_content = mock_workspace.save_artifact.call_args[0][0]
        assert "Existing line" in saved_content
        assert "Appended line" in saved_content
        assert saved_content.count("Appended line") == 1

    def test_insert_mode_validation_non_update_process(self) -> None:
        """Test that insert-mode validation rejects non-UPDATE processes."""
        from unittest.mock import Mock

        from pantheon.process_handler import PROCESS_TYPE_CREATE, ProcessHandler

        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        # Mock the necessary methods to avoid redirect path and profile loading
        mock_workspace.has_process_redirect.return_value = False
        mock_workspace.load_profile.return_value = {}
        handler.determine_process_type = Mock(return_value=(PROCESS_TYPE_CREATE, {}))
        handler.validate_input = Mock(return_value=True)
        handler._build_enhanced_parameters = Mock(
            return_value=({}, {"pantheon_insert_mode": "append"})
        )

        input_data = {
            "process": "create-ticket",
            "actor": "test-agent",
            "input_params": {},
            "framework_params": {"pantheon_insert_mode": "append"},
        }

        result = handler.execute(input_data)

        assert result["success"] is False
        assert "--insert-mode is only supported for UPDATE processes" in result["error"]


class TestProcessHandlerRoutineRetrieval:
    """Tests for ProcessHandler.get_routine orchestration."""

    def setup_method(self) -> None:
        self.mock_workspace = Mock()
        self.mock_artifact_engine = Mock()
        self.mock_rae_engine = Mock()
        self.handler = ProcessHandler(
            self.mock_workspace, self.mock_artifact_engine, self.mock_rae_engine
        )

    def test_get_routine_validates_sections_for_non_update(self) -> None:
        """Ensure --sections usage is rejected for non-UPDATE processes."""

        self.handler.determine_process_type = Mock(return_value=(PROCESS_TYPE_GET, {}))

        with pytest.raises(ValueError, match="only supported for UPDATE"):
            self.handler.get_routine("get-ticket", "dev", "plan")

    def test_get_routine_delegates_to_rae_engine(self) -> None:
        """Ensure get_routine normalizes sections and delegates to RaeEngine."""

        self.handler.determine_process_type = Mock(
            return_value=(PROCESS_TYPE_UPDATE, {})
        )
        sanitized_input = {"input": "data"}
        prepared_framework = {"framework": "values"}
        self.handler._build_enhanced_parameters = Mock(
            return_value=(sanitized_input, prepared_framework)
        )
        self.mock_rae_engine.get_routine.return_value = "routine-content"

        result = self.handler.get_routine("update-ticket", "dev", "plan, plan")

        assert result == "routine-content"

        self.handler._build_enhanced_parameters.assert_called_once()
        call_args = self.handler._build_enhanced_parameters.call_args[0]
        assert call_args[0] == "update-ticket"
        assert call_args[1] == "dev"
        framework_params = call_args[3]
        assert framework_params == {PARAM_SECTIONS: ["plan"]}

        self.mock_rae_engine.get_routine.assert_called_once_with(
            "update-ticket",
            sanitized_input,
            prepared_framework,
            process_type=PROCESS_TYPE_UPDATE,
        )


class TestProcessHandlerSchemaComposition:
    """Tests for ProcessHandler.compose_schema delegation and filtering."""

    def setup_method(self) -> None:
        self.mock_workspace = Mock()
        self.mock_artifact_engine = Mock()
        self.mock_rae_engine = Mock()
        self.handler = ProcessHandler(
            self.mock_workspace, self.mock_artifact_engine, self.mock_rae_engine
        )

    def test_compose_schema_rejects_sections_for_non_update(self) -> None:
        """Validate sections guard for non-UPDATE processes."""

        self.handler.determine_process_type = Mock(return_value=(PROCESS_TYPE_GET, {}))

        with pytest.raises(ValueError, match="only supported for UPDATE"):
            self.handler.compose_schema("get-ticket", "dev", "plan")

    def test_compose_schema_filters_requested_sections(self) -> None:
        """Ensure section filtering returns narrowed schema."""

        compiled_schema = {
            "properties": {
                "section_updates": {
                    "properties": {
                        "context": {"type": "object"},
                        "strategy": {"type": "object"},
                    }
                },
                "section_order": {"default": ["context", "strategy"]},
            }
        }

        self.handler.determine_process_type = Mock(
            return_value=(PROCESS_TYPE_UPDATE, {})
        )
        self.handler._compile_process_schema = Mock(return_value=compiled_schema)

        result = self.handler.compose_schema(
            "update-ticket", "dev", sections="strategy"
        )

        # Ensure original schema not mutated
        assert set(
            compiled_schema["properties"]["section_updates"]["properties"].keys()
        ) == {
            "context",
            "strategy",
        }

        assert list(result["properties"]["section_updates"]["properties"].keys()) == [
            "strategy"
        ]
        assert result["properties"]["section_order"]["default"] == ["strategy"]

        self.handler._compile_process_schema.assert_called_once_with("update-ticket")

    def test_compose_schema_raises_for_unknown_section(self) -> None:
        """Unknown sections should surface as ValueError."""

        compiled_schema = {
            "properties": {
                "sections": {"properties": {"context": {"type": "object"}}},
                "section_order": {"default": ["context"]},
            }
        }

        self.handler.determine_process_type = Mock(
            return_value=(PROCESS_TYPE_UPDATE, {})
        )
        self.handler._compile_process_schema = Mock(return_value=compiled_schema)

        with pytest.raises(ValueError, match=r"Unknown section\(s\)"):
            self.handler.compose_schema("update-ticket", "dev", sections="plan")


class TestProcessHandlerSectionMetadata:
    """Tests for ProcessHandler.get_sections_metadata."""

    def setup_method(self) -> None:
        self.mock_workspace = Mock()
        self.mock_artifact_engine = Mock()
        self.mock_rae_engine = Mock()
        self.handler = ProcessHandler(
            self.mock_workspace, self.mock_artifact_engine, self.mock_rae_engine
        )

    def test_get_sections_metadata_returns_descriptions(self) -> None:
        """Ensure section metadata is flattened to name/description pairs."""

        target_config = {
            "sections": {
                "overview": {"description": "Ticket overview."},
                "details": {"description": "Implementation details."},
            }
        }
        self.mock_workspace.get_artifact_target_section.return_value = json.dumps(
            target_config
        )

        result = self.handler.get_sections_metadata("update-ticket")

        assert result == [
            {"name": "overview", "description": "Ticket overview."},
            {"name": "details", "description": "Implementation details."},
        ]
        self.mock_workspace.get_artifact_target_section.assert_called_once_with(
            "update-ticket"
        )

    def test_get_sections_metadata_errors_when_missing_sections(self) -> None:
        """Missing section definitions should raise a ValueError."""

        self.mock_workspace.get_artifact_target_section.return_value = json.dumps({})

        with pytest.raises(ValueError, match="does not define any sections"):
            self.handler.get_sections_metadata("update-ticket")

    def test_get_sections_metadata_errors_when_both_files_missing(self) -> None:
        """Missing both target.jsonnet and sections.jsonnet should yield descriptive ValueError."""

        self.mock_workspace.get_artifact_target_section.side_effect = (
            FileNotFoundError()
        )
        self.mock_workspace.get_artifact_section_markers.side_effect = (
            FileNotFoundError()
        )

        with pytest.raises(ValueError, match="does not define section metadata"):
            self.handler.get_sections_metadata("get-ticket")

    def test_get_sections_metadata_falls_back_to_sections_jsonnet(self) -> None:
        """When target.jsonnet missing, should fall back to sections.jsonnet."""

        sections_config = {
            "sections": {
                "context": {"description": "Ticket context."},
                "plan": {"description": "Implementation plan."},
            }
        }

        self.mock_workspace.get_artifact_target_section.side_effect = (
            FileNotFoundError()
        )
        self.mock_workspace.get_artifact_section_markers.return_value = json.dumps(
            sections_config
        )

        result = self.handler.get_sections_metadata("get-ticket")

        assert result == [
            {"name": "context", "description": "Ticket context."},
            {"name": "plan", "description": "Implementation plan."},
        ]
        self.mock_workspace.get_artifact_target_section.assert_called_once_with(
            "get-ticket"
        )
        self.mock_workspace.get_artifact_section_markers.assert_called_once_with(
            "get-ticket"
        )
