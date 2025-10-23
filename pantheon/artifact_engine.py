"""
ArtifactEngine - Pure Computational Interface for Artifact Generation

This module defines the ArtifactEngine class interface that handles all computational
aspects of artifact generation including Jsonnet schema composition, Jinja2 template
rendering, and path generation. This is a pure computational component that never
performs I/O operations, instead producing PantheonPath objects and content strings
that the Workspace will save, ensuring complete separation of computation from I/O.

Key Responsibilities:
1. Schema Composition - Evaluate Jsonnet schemas with profile context injection
2. Template Rendering - Render Jinja2 templates with data and built-in variables
3. Path Generation - Generate PantheonPath objects from directory/filename templates

Architecture Constraints:
- Never imports or uses FileSystem - no I/O operations allowed
- Returns PantheonPath objects, never pathlib.Path
- All methods are pure functions without side effects
- Produces outputs that other components use for I/O operations

This interface follows the YAGNI principle - only method signatures and contracts
are defined, leaving actual implementation for future work.
"""

from collections.abc import Callable
from datetime import datetime
from enum import Enum
import json
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pantheon.workspace import PantheonWorkspace

import _jsonnet
import jinja2
import yaml

from pantheon.artifact_id_manager import ArtifactId
from pantheon.constants import BUILTIN_ARTIFACT_ID, BUILTIN_PROCESS
from pantheon.logger import Log
from pantheon.path import PantheonPath


def slugify(text: str) -> str:
    """
    Convert a string to a URL-friendly slug.

    Converts the input text to lowercase, replaces spaces and underscores
    with hyphens, removes non-alphanumeric characters (except hyphens),
    removes consecutive hyphens, and strips leading/trailing hyphens.

    Args:
        text: The string to convert to a slug

    Returns:
        URL-friendly slug string

    Examples:
        >>> slugify("Hello World!")
        'hello-world'
        >>> slugify("My_Title 123")
        'my-title-123'
        >>> slugify("  Special-Characters!!!  ")
        'special-characters'
    """
    import re

    if not isinstance(text, str):
        text = str(text)

    # Convert to lowercase
    slug = text.lower()

    # Replace spaces and underscores with hyphens
    slug = re.sub(r"[\s_]+", "-", slug)

    # Remove non-alphanumeric characters (except hyphens)
    slug = re.sub(r"[^a-z0-9-]", "", slug)

    # Remove consecutive hyphens
    slug = re.sub(r"-+", "-", slug)

    # Strip leading/trailing hyphens
    return slug.strip("-")


def remove_suffix(text: str, suffix: str | list[Any], ignore_case: bool = False) -> str:
    """
    Remove suffix from text if it exists, with support for case-insensitive matching
    and multiple suffix patterns.

    Args:
        text: The string to process
        suffix: The suffix to remove (string) or list of suffixes to try
        ignore_case: If True, perform case-insensitive matching

    Returns:
        String with suffix removed if it was present, otherwise original string

    Examples:
        >>> remove_suffix("pantheon-team", "-team")
        'pantheon'
        >>> remove_suffix("my-project", "-team")
        'my-project'
        >>> remove_suffix("team-name-team", "-team")
        'team-name'
        >>> remove_suffix("My Team", "team", ignore_case=True)
        'My '
        >>> remove_suffix("project-Team", ["-team", " team"], ignore_case=True)
        'project'
        >>> remove_suffix("My-TEAM", [" team", "-team"], ignore_case=True)
        'My'
    """
    if not isinstance(text, str):
        text = str(text)

    # Handle single suffix - convert to list for uniform processing
    if isinstance(suffix, str):
        suffixes = [suffix]
    elif hasattr(suffix, "__iter__") and not isinstance(suffix, str):
        suffixes = [str(s) for s in suffix]  # Convert all items to strings
    else:
        suffixes = [str(suffix)]  # Convert single non-string item to string

    for suf in suffixes:
        # Skip empty suffixes to avoid removing entire string
        if not suf:
            continue

        if ignore_case:
            # Case-insensitive comparison
            if text.lower().endswith(suf.lower()):
                return text[: -len(suf)]
        else:
            # Case-sensitive comparison (original behavior)
            if text.endswith(suf):
                return text[: -len(suf)]

    return text


# Operation type enumeration for artifact processing
class OperationType(Enum):
    """Enumeration of artifact operation types based on file combinations."""

    CREATE = "create"  # Operations that generate new artifacts
    RETRIEVE = "retrieve"  # Operations that find and parse existing artifacts
    UPDATE = "update"  # Operations that modify sections of existing artifacts


# Constants for JSON configuration keys
NORMALIZER_PATTERN_KEY = "pattern"
NORMALIZER_REPLACEMENT_KEY = "replacement"
LOCATOR_PATTERN_KEY = "pattern"
LOCATOR_DIRECTORY_KEY = "directory"
MARKER_SECTION_START_KEY = "section_start"
MARKER_SECTION_END_KEY = "section_end"
MARKER_PLACEHOLDER_KEY = "placeholder"
FINDER_ID_PLACEHOLDER = "__PANTHEON_ARTIFACT_ID__"

# Built-in template variable names now imported from constants module


class SecurityError(Exception):
    """Raised when security violations are detected in path generation."""


if TYPE_CHECKING:
    from pantheon.workspace import PantheonWorkspace


class SemanticUriLoader(jinja2.BaseLoader):
    """Custom Jinja2 loader for resolving semantic URIs in template includes.

    This loader integrates with the Workspace abstraction layer to resolve semantic URIs
    (e.g., artifact-template://, process-schema://, process-routine://) in Jinja2 include
    statements. It delegates URI resolution to Workspace.get_resolved_content() method,
    maintaining architectural boundaries where all filesystem knowledge is encapsulated
    in the Workspace.

    The loader is designed to work in a ChoiceLoader chain, where it handles semantic
    URIs and raises TemplateNotFound for non-semantic paths, allowing fallback loaders
    (like FileSystemLoader) to handle regular file-based includes.

    Args:
        workspace: PantheonWorkspace instance for semantic URI resolution

    Example:
        # Configure Jinja2 environment with semantic URI support
        from jinja2 import Environment, ChoiceLoader, FileSystemLoader

        workspace = PantheonWorkspace(...)
        loader = ChoiceLoader([
            SemanticUriLoader(workspace),  # Try semantic URIs first
            FileSystemLoader('/path/to/templates')  # Fallback to file paths
        ])
        env = Environment(loader=loader)

        # Template can now use semantic URI includes
        # {% include 'artifact-template://update-guide/sections/core-principles' %}

    Note:
        This loader only handles templates that start with recognized semantic URI
        schemes. All other template names are rejected with TemplateNotFound,
        allowing the ChoiceLoader to try subsequent loaders in the chain.
    """

    def __init__(self, workspace: "PantheonWorkspace"):
        """Initialize the semantic URI loader with workspace dependency.

        Args:
            workspace: PantheonWorkspace instance for URI resolution
        """
        self.workspace = workspace

    def get_source(
        self, environment: jinja2.Environment, template: str
    ) -> tuple[str, str, Callable[[], bool]]:
        """Load template source from semantic URI.

        Implements Jinja2 BaseLoader protocol. Detects semantic URI templates
        (artifact-template://, process-schema://, etc.) and delegates resolution
        to Workspace.get_resolved_content(). Non-semantic templates raise
        TemplateNotFound to enable loader chain fallback.

        Args:
            environment: Jinja2 Environment instance (unused but required by protocol)
            template: Template name/path to load

        Returns:
            Tuple of (source, filename, uptodate_func) where:
            - source: Template content string
            - filename: Template identifier (the URI itself)
            - uptodate_func: Callable that always returns False for development

        Raises:
            jinja2.TemplateNotFound: If template is not a semantic URI or URI
                                    resolution fails

        Example:
            loader = SemanticUriLoader(workspace)
            source, filename, uptodate = loader.get_source(
                env,
                'artifact-template://update-guide/sections/core-principles'
            )
        """
        # Check if template is a semantic URI (contains ://)
        if "://" not in template:
            # Not a semantic URI - let fallback loaders handle it
            raise jinja2.TemplateNotFound(template)

        # Delegate resolution to Workspace
        try:
            content = self.workspace.get_resolved_content(template)
        except (FileNotFoundError, ValueError) as e:
            # Convert filesystem/validation errors to Jinja2 TemplateNotFound
            raise jinja2.TemplateNotFound(
                f"Failed to resolve semantic URI '{template}': {e}"
            ) from e

        # Return tuple: (source, filename, uptodate_func)
        # uptodate_func always returns False to force reload during development
        return content, template, lambda: False


class ArtifactEngine:
    """
    Expert interface for artifact generation and location operations.

    The ArtifactEngine is the framework's single expert on all artifact/
    directory conventions and provides two distinct categories of functionality:

    **Generation Methods (Pure Computation):**
    - Schema composition using Jsonnet with profile context injection
    - Template rendering using Jinja2 with structured data
    - Path generation producing PantheonPath objects for safe I/O delegation
    These methods never perform I/O and maintain strict computational purity.

    **Location Methods (I/O Orchestration):**
    - Artifact finding using normalizer.jsonnet and finder.jsonnet rules
    - Section parsing using markers.jsonnet definitions
    These methods orchestrate complex queries by delegating to PantheonWorkspace,
    following the principle of High Cohesion over Universal Purity.

    This dual responsibility design encapsulates expert-level knowledge of
    artifact conventions within the ArtifactEngine rather than forcing the
    ProcessHandler to become a micromanager of low-level steps.

    Note: This is an interface definition following YAGNI principle.
    Implementation details are deferred until concrete requirements emerge.
    """

    def __init__(
        self,
        workspace: "PantheonWorkspace",
        artifact_id: ArtifactId | None = None,
    ) -> None:
        """
        Initialize the ArtifactEngine with workspace dependency.

        Args:
            workspace: PantheonWorkspace instance for location method I/O operations
            artifact_id: Optional ArtifactId instance for {{pantheon_artifact_id}} template variables.
                       If not provided, creates default instance using workspace's artifacts_root.

        The workspace dependency enables location methods to orchestrate complex
        queries while generation methods remain pure computational functions.
        The artifact_id provides automatic sequential ID generation for artifacts.
        """
        self._workspace = workspace

        # Create ArtifactId instance if not provided
        if artifact_id is None:
            self._artifact_id = ArtifactId(workspace)
        else:
            self._artifact_id = artifact_id

    # Core Interface Methods - Called by ProcessHandler

    def compile_schema(
        self,
        schema_content: str,
        full_profile_content: dict[str, Any],
        process_name: str | None = None,
        *,
        include_schema_metadata: bool = True,
    ) -> dict[str, Any]:
        """
        Compile a JSON schema from preprocessed Jsonnet source with profile context injection.

        This method compiles preprocessed Jsonnet schema content with profile-aware context
        injection, returning the compiled schema as a dictionary. The schema content is
        expected to already have all imports resolved by the Workspace preprocessing.

        The method automatically sanitizes the compiled result to ensure proper JSON Schema
        structure (adding type/object wrappers and optional $schema metadata when requested).

        Args:
            schema_content: The preprocessed Jsonnet schema content to compile
            full_profile_content: Full profile structure with active_profile and profiles keys
            process_name: Name of the process (used for filename context)

        Returns:
            The compiled JSON schema as a dictionary

        Note: This is a pure computational function that never performs I/O.
              The schema content should already be preprocessed by the Workspace
              with all imports resolved.
        """
        if not schema_content or not schema_content.strip():
            raise ValueError("Schema content cannot be empty or None")

        # Profile data can be empty - schemas may not use profile variables
        # If empty, provide default empty structure for Jsonnet compilation
        if not full_profile_content:
            full_profile_content = {}

        try:
            # Handle structured format with active_profile
            if (
                "active_profile" in full_profile_content
                and "profiles" in full_profile_content
            ):
                active_profile_name = full_profile_content["active_profile"]
                profiles = full_profile_content["profiles"]
                if not isinstance(profiles, dict):
                    raise ValueError("Profiles section must be an object")
                if active_profile_name not in profiles:
                    raise ValueError(
                        f"Active profile '{active_profile_name}' not found in profiles"
                    )
                active_profile_config = profiles[active_profile_name]
            else:
                # Handle simple format - return empty profile when no profiles section
                active_profile_config = {}

            # Schema content is already preprocessed by Workspace - no import callback needed

            # Compile Jsonnet with profile config as external variables
            # If active_profile_config is a dict, pass each key as a separate ext_var
            # Otherwise, pass the whole config under "profile" key
            if isinstance(active_profile_config, dict):
                ext_vars = active_profile_config.copy()
            else:
                ext_vars = {"profile": active_profile_config}

            # Get schema file path for directory context if process_name is provided
            filename = "snippet"
            if process_name:
                try:
                    filename = self._workspace.get_process_schema_path(process_name)
                    Log.debug(f"Using schema file path as filename: {filename}")
                except Exception as e:
                    # Fall back to generic filename if path resolution fails
                    Log.debug(
                        f"Could not get schema file path for {process_name}, using 'snippet': {e}"
                    )
                    filename = "snippet"
            else:
                Log.debug("No process_name provided, using 'snippet' as filename")

            Log.debug(
                f"Compiling schema with filename='{filename}', content length={len(schema_content)}"
            )

            # First: Compile the Jsonnet content to JSON
            compiled_result = self._compile_jsonnet(
                schema_content,
                ext_vars=ext_vars,
                filename=filename,
            )

            # Ensure result is a dictionary (JSON Schema must be an object)
            if not isinstance(compiled_result, dict):
                raise ValueError("Compiled schema must be a JSON object")

            # Second: Sanitize the compiled JSON to ensure proper JSON Schema structure
            # Convert the compiled result back to JSON string for sanitization
            import json

            compiled_json_str = json.dumps(compiled_result, indent=2)
            sanitized_json_str = self._sanitize_schema_structure(
                compiled_json_str,
                include_schema_metadata=include_schema_metadata,
            )

            # Parse the sanitized result back to dict
            sanitized_result = json.loads(sanitized_json_str)

            # Ensure the sanitized result is a dict (for mypy type checking)
            if not isinstance(sanitized_result, dict):
                raise ValueError("Sanitized schema must be a JSON object")

            Log.debug("Schema compiled and sanitized successfully")

            return sanitized_result

        except Exception as e:
            Log.error(f"Schema compilation failed: {str(e)}")
            raise RuntimeError(f"Schema compilation failed: {str(e)}") from e

    def _sanitize_schema_structure(
        self, raw_schema_content: str, *, include_schema_metadata: bool = True
    ) -> str:
        """Sanitize schema content to ensure proper JSON Schema structure.

        This method takes raw schema content (which may be just properties or incomplete)
        and ensures it has the proper JSON Schema structure with $schema, type: object,
        and properties wrapper if needed.

        Only applies sanitization to content that appears to be pure JSON.
        Jsonnet content with functions like std.extVar() is passed through unchanged.

        Args:
            raw_schema_content: Raw schema content that may be incomplete

        Returns:
            Properly structured JSON Schema jsonnet content

        Raises:
            ValueError: If content is empty, not a JSON object, or contains invalid JSON

        Examples:
            Input: '{"name": {"type": "string"}}'
            Output: '{"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {"name": {"type": "string"}}}'
        """
        if not raw_schema_content or not raw_schema_content.strip():
            raise ValueError("Schema content cannot be empty or None")

        # Quick check - if content contains Jsonnet functions, don't sanitize
        if "std." in raw_schema_content or "function(" in raw_schema_content:
            Log.debug(
                "Schema content contains Jsonnet functions, skipping sanitization"
            )
            return raw_schema_content

        try:
            import json

            # Try to parse the content as JSON to check its structure
            parsed_content = json.loads(raw_schema_content)

            if not isinstance(parsed_content, dict):
                raise ValueError("Schema content must be a JSON object")

            # Check if it already has proper JSON Schema structure
            has_schema = "$schema" in parsed_content
            has_type = parsed_content.get("type") == "object"
            has_properties = "properties" in parsed_content

            # If it's already a complete JSON Schema, return as-is
            if has_schema and has_type and has_properties:
                if include_schema_metadata:
                    return raw_schema_content

                parsed_content.pop("$schema", None)
                return json.dumps(parsed_content, indent=2)

            # If it's missing JSON Schema wrapper but has properties, add wrapper
            if has_properties and not (has_schema and has_type):
                properties_wrapped_schema: dict[str, Any] = {
                    "type": "object",
                }
                if include_schema_metadata:
                    properties_wrapped_schema["$schema"] = (
                        "http://json-schema.org/draft-07/schema#"
                    )

                content_copy = dict(parsed_content)
                if not include_schema_metadata:
                    content_copy.pop("$schema", None)

                properties_wrapped_schema.update(content_copy)
                return json.dumps(properties_wrapped_schema, indent=2)

            # If it doesn't have properties, assume the content IS the properties
            # Need to separate schema fields from property fields
            if not has_properties:
                # Standard JSON Schema fields that should stay at root level
                schema_fields = {
                    "$schema",
                    "type",
                    "title",
                    "description",
                    "required",
                    "additionalProperties",
                    "definitions",
                    "$defs",
                }

                # Separate schema fields from property fields
                root_fields: dict[str, Any] = {}
                property_fields: dict[str, Any] = {}

                for key, value in parsed_content.items():
                    if key in schema_fields:
                        root_fields[key] = value
                    else:
                        property_fields[key] = value

                # Build the complete schema
                wrapped_schema: dict[str, Any] = {
                    "type": "object",
                }
                if include_schema_metadata:
                    wrapped_schema["$schema"] = (
                        "http://json-schema.org/draft-07/schema#"
                    )

                if not include_schema_metadata:
                    root_fields.pop("$schema", None)

                # Add any existing schema fields
                wrapped_schema.update(root_fields)

                # Add properties if we found any
                if property_fields:
                    wrapped_schema["properties"] = property_fields

                return json.dumps(wrapped_schema, indent=2)

            # Fallback - shouldn't reach here but handle gracefully
            return raw_schema_content

        except json.JSONDecodeError as e:
            # Invalid JSON that's not Jsonnet - raise an error
            raise ValueError(f"Invalid JSON in schema content: {e}") from e
        except ValueError:
            # Re-raise ValueError as-is (don't wrap in RuntimeError)
            raise
        except Exception as e:
            Log.error(f"Unexpected error during schema sanitization: {e}")
            raise RuntimeError(f"Schema sanitization failed: {e}") from e

    def validate(self, input_data: dict[str, Any], schema: dict[str, Any]) -> bool:
        """
        Validate input data against a JSON schema.

        This method validates the provided input data against the given JSON
        schema, returning True if validation passes or raising an exception
        if validation fails.

        Args:
            input_data: The data to validate
            schema: The JSON schema to validate against

        Returns:
            True if validation passes

        Raises:
            ValueError: If validation fails with details of the failure

        Note: This is a pure computational function that never performs I/O.
        """
        if not isinstance(input_data, dict):
            raise ValueError("Input data must be a dictionary")

        if not isinstance(schema, dict):
            raise ValueError("Schema must be a dictionary")

        try:
            from jsonschema import Draft202012Validator
            from jsonschema.exceptions import ValidationError

            # Create validator instance
            validator = Draft202012Validator(schema)

            # Check if data is valid - explicitly cast to bool
            result: bool = bool(validator.is_valid(input_data))

            if not result:
                # Collect all validation errors for detailed reporting
                errors = list(validator.iter_errors(input_data))
                error_details = []

                for error in errors:
                    # Build path to the failing field
                    field_path = (
                        ".".join(str(p) for p in error.absolute_path)
                        if error.absolute_path
                        else "root"
                    )

                    # Get the failing value for context
                    failing_value = error.instance

                    # Create detailed error message
                    error_msg = f"Field '{field_path}': {error.message}"
                    if hasattr(error, "schema_path") and error.schema_path:
                        schema_location = ".".join(str(p) for p in error.schema_path)
                        error_msg += f" (schema constraint: {schema_location})"

                    # Add value context for debugging
                    if isinstance(failing_value, str | int | float | bool):
                        error_msg += f" [current value: {failing_value}]"
                    elif isinstance(failing_value, list | dict):
                        error_msg += (
                            f" [current value type: {type(failing_value).__name__}]"
                        )

                    error_details.append(error_msg)

                # Raise detailed validation error
                detailed_message = "Schema validation failed:\n" + "\n".join(
                    f"  - {detail}" for detail in error_details
                )
                raise ValueError(detailed_message)

            return result

        except ValueError:
            # Re-raise ValueError exceptions (including our detailed validation errors)
            raise
        except ValidationError as e:
            raise ValueError(f"Schema validation error: {e.message}") from e
        except Exception as e:
            Log.error(f"Unexpected error during validation: {str(e)}")
            raise RuntimeError(
                f"Validation failed due to unexpected error: {str(e)}"
            ) from e

    def generate_artifact(
        self,
        templates: dict[str, str],
        input_params: dict[str, Any],
        framework_params: dict[str, Any],
    ) -> tuple[str, PantheonPath]:
        """
        Generate artifact content and path from templates and input data.

        This method renders the artifact template with input data and generates
        the output path by rendering directory and filename templates. Returns
        both the rendered content and the target path as a PantheonPath.
        Uses only the new operation-specific naming conventions.

        Args:
            templates: Dictionary containing 'content', 'placement', and 'naming' templates
            input_params: The clean input parameters for template rendering
            framework_params: The built-in framework variables

        Returns:
            Tuple of (rendered_content, target_path)

        Note: This is a pure computational function that never performs I/O.
        Returns PantheonPath to maintain protection proxy pattern.
        """
        if not isinstance(templates, dict):
            raise ValueError("Templates must be a dictionary")

        if not isinstance(input_params, dict):
            raise ValueError("Input parameters must be a dictionary")

        if not isinstance(framework_params, dict):
            raise ValueError("Built-in parameters must be a dictionary")

        # Use only new enum-based template keys
        content_key = "content"
        placement_key = "placement"
        naming_key = "naming"

        # Validate required template keys exist
        if content_key not in templates:
            raise ValueError(
                f"Missing required template key: {content_key} (content.md)"
            )

        if placement_key not in templates:
            raise ValueError(
                f"Missing required template key: {placement_key} (placement.jinja)"
            )

        if naming_key not in templates:
            raise ValueError(
                f"Missing required template key: {naming_key} (naming.jinja)"
            )

        try:
            # Create enhanced context with built-in variables (includes artifact_id for CREATE)
            Log.debug("Creating template context for generate_artifact")
            context = self._create_template_context(
                input_params, framework_params, "CREATE"
            )
            Log.debug(
                f"Template context created successfully with keys: {list(context.keys())}"
            )

            # Render the main content template with include support
            content_template = templates[content_key]
            process_name = framework_params.get(BUILTIN_PROCESS)
            Log.debug("Rendering content.md template")
            if process_name:
                # Use artifact template rendering with semantic URI include support for content.md
                env = self.create_artifact_jinja_environment(self._workspace)
                rendered_content = self.render_artifact_template(
                    content_template, context, env, "content.md"
                )
            else:
                # Fall back to basic rendering if no process context
                rendered_content = self.render_template(
                    content_template, context, "content.md"
                )
            Log.debug("Content template rendered successfully")

            # Generate the target path from placement and naming templates
            placement_template = templates[placement_key]
            naming_template = templates[naming_key]

            # Render placement and naming separately, then combine (basic rendering)
            Log.debug("Rendering placement.jinja template")
            rendered_placement = self.render_template(
                placement_template, context, "placement.jinja"
            ).strip()
            Log.debug("Placement template rendered successfully")

            Log.debug("Rendering naming.jinja template")
            rendered_naming = self.render_template(
                naming_template, context, "naming.jinja"
            ).strip()
            Log.debug("Naming template rendered successfully")

            # Create PantheonPath by combining placement and naming
            if rendered_placement:
                target_path = PantheonPath(rendered_placement, rendered_naming)
            else:
                target_path = PantheonPath(rendered_naming)

            return (rendered_content, target_path)

        except Exception as e:
            Log.error(f"Artifact generation failed: {str(e)}")
            raise RuntimeError(f"Artifact generation failed: {str(e)}") from e

    def generate_jsonl_path(
        self,
        templates: dict[str, str],
        input_params: dict[str, Any],
        framework_params: dict[str, Any],
    ) -> PantheonPath:
        """Generate JSONL file path from templates and input data.

        This method renders JSONL directory and filename templates with input data
        to generate the target path for JSONL log entries. Returns the path as a
        PantheonPath object for security.

        Args:
            templates: Dictionary containing 'jsonl_placement' and 'jsonl_naming' templates
            input_params: The clean input parameters for template rendering
            framework_params: The built-in framework variables

        Returns:
            PantheonPath for the JSONL file

        Raises:
            ValueError: If required templates are missing
            RuntimeError: If template rendering fails

        Note: This is a pure computational function that never performs I/O.
        Returns PantheonPath to maintain protection proxy pattern.
        """
        if not isinstance(templates, dict):
            raise ValueError("Templates must be a dictionary")

        if not isinstance(input_params, dict):
            raise ValueError("Input parameters must be a dictionary")

        if not isinstance(framework_params, dict):
            raise ValueError("Built-in parameters must be a dictionary")

        # Validate required template keys exist
        jsonl_placement_key = "jsonl_placement"
        jsonl_naming_key = "jsonl_naming"

        if jsonl_placement_key not in templates:
            raise ValueError(f"Missing required template key: {jsonl_placement_key}")

        if jsonl_naming_key not in templates:
            raise ValueError(f"Missing required template key: {jsonl_naming_key}")

        try:
            # Create enhanced context with built-in variables for JSONL
            Log.debug("Creating template context for generate_jsonl_path")
            context = self._create_template_context(
                input_params, framework_params, "CREATE"
            )
            Log.debug(
                f"Template context created successfully with keys: {list(context.keys())}"
            )

            # Render placement and naming templates (basic rendering only)
            placement_template = templates[jsonl_placement_key]
            naming_template = templates[jsonl_naming_key]

            Log.debug("Rendering jsonl_placement template")
            rendered_placement = self.render_template(
                placement_template, context, "jsonl_placement.jinja"
            ).strip()
            Log.debug("JSONL placement template rendered successfully")

            Log.debug("Rendering jsonl_naming template")
            rendered_naming = self.render_template(
                naming_template, context, "jsonl_naming.jinja"
            ).strip()
            Log.debug("JSONL naming template rendered successfully")

            # Create PantheonPath by combining placement and naming
            if rendered_placement:
                jsonl_path = PantheonPath(rendered_placement, rendered_naming)
            else:
                jsonl_path = PantheonPath(rendered_naming)

            return jsonl_path

        except Exception as e:
            Log.error(f"JSONL path generation failed: {str(e)}")
            raise RuntimeError(f"JSONL path generation failed: {str(e)}") from e

    def detect_operation_type(self, templates: dict[str, str]) -> OperationType:
        """
        Determine the operation type based on available template keys.

        Analyzes the combination of template keys to determine whether this is a
        CREATE, RETRIEVE, or UPDATE operation based on the new naming conventions.

        Args:
            templates: Dictionary of available template keys and content

        Returns:
            OperationType enum value indicating the detected operation type

        Raises:
            ValueError: If template combination doesn't match any valid operation type
        """
        if not isinstance(templates, dict):
            raise ValueError("Templates must be a dictionary")

        template_keys = set(templates.keys())

        # CREATE operations: content + placement + naming
        create_keys = {"content", "placement", "naming"}
        if create_keys.issubset(template_keys):
            return OperationType.CREATE

        # UPDATE operations: patch + locator + parser + target
        # Note: UPDATE operations work with existing artifacts
        update_keys = {"patch", "locator", "parser", "target"}
        if update_keys.issubset(template_keys):
            return OperationType.UPDATE

        # RETRIEVE operations: locator + parser + sections (no content or patch)
        retrieve_keys = {"locator", "parser", "sections"}
        if retrieve_keys.issubset(template_keys):
            return OperationType.RETRIEVE

        # If no pattern matches, raise error with guidance
        available_keys = ", ".join(sorted(template_keys))
        raise ValueError(
            f"Invalid template combination: {available_keys}. "
            f"Expected CREATE (content+placement+naming), "
            f"RETRIEVE (locator+parser+sections), or UPDATE (patch+locator+parser+target)"
        )

    def find_artifact(
        self, process_name: str, artifact_id: str | None = None
    ) -> PantheonPath | None:
        """
        Locate artifacts using normalized IDs and finder patterns.

        Supports two modes based on parser.jsonnet presence:
        - Multi-artifact mode (with parser.jsonnet): Normalizes ID and searches for specific artifact
        - Singleton mode (no parser.jsonnet): Expects exactly one artifact, artifact_id is optional/ignored

        Args:
            process_name: Name of the process for context
            artifact_id: The artifact identifier to find (optional for singleton mode)

        Returns:
            PantheonPath to found artifact, or None if not found

        Note: This method uses workspace for I/O operations to search for artifacts.
        Returns PantheonPath objects to maintain protection proxy pattern.
        """
        Log.debug(
            f"ArtifactEngine.find_artifact: process='{process_name}', artifact_id='{artifact_id}'"
        )

        # Check if parser.jsonnet exists to determine mode
        has_parser = self._workspace.has_artifact_parser(process_name)

        if has_parser:
            # Multi-artifact mode: Require ID and normalize it
            if not artifact_id:
                Log.warning(
                    f"artifact_id required for multi-artifact process '{process_name}' (has parser.jsonnet)"
                )
                return None

            # Phase 1: Normalize the fuzzy ID
            canonical_id = self._normalize_id(process_name, artifact_id)
            Log.debug(f"Normalized ID '{artifact_id}' -> '{canonical_id}'")

            if not canonical_id:
                Log.warning(
                    f"Failed to normalize artifact ID '{artifact_id}' for process '{process_name}'"
                )
                return None

            # Phase 2: Locate artifact using finder pattern
            result = self._locate_artifact(process_name, canonical_id)
            Log.debug(f"Locate artifact result: {result}")
            return result
        # Singleton mode: artifact_id is optional/ignored
        Log.debug(f"Singleton mode for process '{process_name}' (no parser.jsonnet)")
        result = self._locate_singleton_artifact(process_name)
        Log.debug(f"Locate singleton artifact result: {result}")
        return result

    def get_artifact_sections(
        self, process_name: str, artifact_path: PantheonPath, section_names: list[str]
    ) -> dict[str, str]:
        """
        Extract marked sections from artifact content.

        Uses workspace.get_artifact_markers() to retrieve markers and parse sections
        from the specified artifact. This method supports the evolutionary artifact
        pattern by identifying HTML comment markers and extracting the content
        between start and end markers for each requested section.

        Handles four cases:
        1. No sections.jsonnet file - return entire artifact content as "content"
        2. No sections - document has no section markers, placeholder key only
        3. Single section - flat structure with section_start, section_end, placeholder keys
        4. Multiple sections - nested structure with sections object containing named sections

        Args:
            process_name: Name of the process for context
            artifact_path: PantheonPath to the artifact file to parse
            section_names: List of section names to extract

        Returns:
            Dictionary mapping section names to extracted content

        Note: This method uses workspace for I/O operations to read markers and content.
        """
        try:
            # Get marker definitions from workspace
            try:
                markers_content = self._workspace.get_artifact_section_markers(
                    process_name
                )
            except FileNotFoundError:
                # Case 1: No sections.jsonnet file exists - return entire artifact content
                Log.debug(
                    f"No sections.jsonnet found for process '{process_name}', returning entire artifact content"
                )
                try:
                    file_content = self._workspace.read_artifact_file(artifact_path)
                    return {"content": file_content}
                except Exception as e:
                    Log.warning(f"Failed to read artifact file {artifact_path}: {e}")
                    return {}

            if not markers_content or not markers_content.strip():
                Log.warning(f"No marker definitions found for process '{process_name}'")
                return {}

            # Parse marker JSON to get marker templates
            markers_config = json.loads(markers_content)
            if not isinstance(markers_config, dict):
                Log.warning(
                    f"Invalid markers format for process '{process_name}' - expected object"
                )
                return {}

            # Read artifact file content through workspace delegation
            try:
                file_content = self._workspace.read_artifact_file(artifact_path)
            except Exception as e:
                Log.warning(f"Failed to read artifact file {artifact_path}: {e}")
                return {}

            # Determine which case we're dealing with and extract sections accordingly
            if "sections" in markers_config:
                # Case 4: Multiple sections with nested structure
                return self._extract_multiple_sections(
                    markers_config, file_content, section_names
                )
            if (
                MARKER_SECTION_START_KEY in markers_config
                and MARKER_SECTION_END_KEY in markers_config
            ):
                # Case 3: Single section with flat structure
                return self._extract_single_section(
                    markers_config, file_content, section_names
                )
            if MARKER_PLACEHOLDER_KEY in markers_config:
                # Case 2: No sections, just check if document is empty template
                return self._extract_no_sections(markers_config, file_content)
            Log.warning(
                f"Invalid marker configuration for process '{process_name}' - no recognizable structure"
            )
            return {}

        except json.JSONDecodeError as e:
            Log.warning(
                f"Failed to parse markers JSON for process '{process_name}': {e}"
            )
            return {}
        except Exception as e:
            Log.warning(
                f"Unexpected error during section extraction for process '{process_name}': {e}"
            )
            return {}

    def _extract_multiple_sections(
        self,
        markers_config: dict[str, Any],
        file_content: str,
        section_names: list[str],
    ) -> dict[str, str]:
        """Extract sections using nested sections structure (Case 3)."""
        sections = {}
        placeholder_marker = markers_config.get(MARKER_PLACEHOLDER_KEY, "")
        sections_config = markers_config["sections"]

        # If no specific sections requested, return all available sections
        if not section_names:
            section_names = list(sections_config.keys())
            Log.debug(
                f"No sections specified, extracting all available: {section_names}"
            )
        else:
            Log.debug(f"Extracting requested sections: {section_names}")

        for section_name in section_names:
            if section_name not in sections_config:
                Log.debug(
                    f"Section '{section_name}' not found in sections configuration"
                )
                continue

            section_config = sections_config[section_name]
            start_marker = section_config.get("start", "")
            end_marker = section_config.get("end", "")

            if not start_marker or not end_marker:
                Log.debug(f"Missing start or end marker for section '{section_name}'")
                continue

            # Parse section content
            section_content = self._parse_section_markers(
                file_content, start_marker, end_marker
            )

            if section_content is not None:
                # Check if content contains placeholder marker
                if placeholder_marker and placeholder_marker in section_content:
                    # Skip sections containing placeholder marker
                    continue
                # Include section with actual content
                sections[section_name] = section_content

        return sections

    def _extract_single_section(
        self,
        markers_config: dict[str, Any],
        file_content: str,
        section_names: list[str],
    ) -> dict[str, str]:
        """Extract sections using flat structure (Case 2)."""
        sections = {}
        placeholder_marker = markers_config.get(MARKER_PLACEHOLDER_KEY, "")

        # For single section case, if no sections specified, we can't auto-determine
        # what sections exist, so return empty
        if not section_names:
            Log.debug("Single section structure requires explicit section names")
            return {}

        Log.debug(f"Extracting single section: {section_names}")

        for section_name in section_names:
            # Format markers with section name
            start_marker = markers_config[MARKER_SECTION_START_KEY].format(
                name=section_name
            )
            end_marker = markers_config[MARKER_SECTION_END_KEY].format(
                name=section_name
            )

            # Parse section content
            section_content = self._parse_section_markers(
                file_content, start_marker, end_marker
            )

            if section_content is not None:
                # Check if content contains placeholder marker
                if placeholder_marker and placeholder_marker in section_content:
                    # Skip sections containing placeholder marker
                    continue
                # Include section with actual content
                sections[section_name] = section_content

        return sections

    def _extract_no_sections(
        self, markers_config: dict[str, Any], file_content: str
    ) -> dict[str, str]:
        """Handle case where document has no sections (Case 1)."""
        placeholder_marker = markers_config.get(MARKER_PLACEHOLDER_KEY, "")

        Log.debug(
            "Document has no sections, checking if it contains placeholder marker"
        )

        # If the document contains the placeholder marker, return empty
        if placeholder_marker and placeholder_marker in file_content:
            return {}

        # Otherwise return the entire content as a single unnamed section
        return {"content": file_content}

    # Internal Helper Methods - Not part of public interface

    def _normalize_newlines(self, content: str) -> str:
        """
        Normalize excessive newlines in rendered template content.

        Recursively replaces triple newlines (\\n\\n\\n) with double newlines (\\n\\n)
        until no triple newlines remain. This ensures consistent spacing in rendered
        templates without requiring manual updates to all template files.

        With trim_blocks=False set in Jinja environments, templates may produce
        inconsistent newline spacing. This post-processing step normalizes the output.

        Args:
            content: The rendered template content to normalize

        Returns:
            Content with normalized newlines (max 2 consecutive newlines)

        Examples:
            >>> _normalize_newlines("foo\\n\\n\\nbar")
            'foo\\n\\nbar'
            >>> _normalize_newlines("foo\\n\\n\\n\\nbar")  # 4 newlines -> 2
            'foo\\n\\nbar'
        """
        while "\n\n\n" in content:
            content = content.replace("\n\n\n", "\n\n")
        return content

    def _compile_jsonnet(
        self,
        jsonnet_content: str,
        ext_vars: dict[str, Any] | None = None,
        filename: str = "snippet",
    ) -> Any:
        """
        Compile Jsonnet code to JSON with external variables.

        This internal method provides the foundation for Jsonnet operations,
        supporting external variable injection. It handles the core Jsonnet
        compilation logic used by schema composition methods.

        Args:
            jsonnet_content: The preprocessed Jsonnet content to compile
            ext_vars: Optional external variables for std.extVar() access
            filename: Optional filename for error reporting

        Returns:
            The evaluated result (typically a dict for schemas)

        Raises:
            ValueError: If jsonnet_content is empty or None
            RuntimeError: If Jsonnet compilation fails due to syntax errors

        Note: This is a pure computational function that never performs I/O.
              Content should already be preprocessed with all imports resolved.
        """
        if not jsonnet_content or not jsonnet_content.strip():
            raise ValueError("Jsonnet content cannot be empty or None")

        try:
            # Prepare kwargs for evaluate_snippet
            kwargs: dict[str, Any] = {}

            # Convert ext_vars to string format for jsonnet evaluation
            if ext_vars:
                ext_vars_str = {}
                ext_codes = {}
                for key, value in ext_vars.items():
                    if isinstance(value, str):
                        ext_vars_str[key] = value
                    else:
                        # For non-string values, use ext_codes which allows Jsonnet to evaluate them
                        ext_codes[key] = json.dumps(value)

                if ext_vars_str:
                    kwargs["ext_vars"] = ext_vars_str
                if ext_codes:
                    kwargs["ext_codes"] = ext_codes

            # Evaluate the preprocessed jsonnet content - imports are already inlined
            Log.debug(
                f"Calling _jsonnet.evaluate_snippet with filename='{filename}', kwargs keys: {list(kwargs.keys())}"
            )
            json_str = _jsonnet.evaluate_snippet(filename, jsonnet_content, **kwargs)

            Log.debug(f"Compiled Jsonnet output length: {len(json_str)}")
            Log.debug(f"Compiled Jsonnet output preview: {json_str[:200]}")

            # Parse the JSON result and return as Python object
            return json.loads(json_str)

        except Exception as e:
            # Log the error and re-raise as RuntimeError with clear message
            Log.error(f"Jsonnet compilation failed: {str(e)}")
            raise RuntimeError(f"Jsonnet compilation failed: {str(e)}") from e

    def _create_template_context(
        self,
        input_params: dict[str, Any],
        framework_params: dict[str, Any],
        operation_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Create enhanced template context with built-in variables.

        Internal helper method that combines input parameters with built-in template
        variables for comprehensive template rendering context. Only includes
        {{pantheon_artifact_id}} for CREATE operations to avoid unnecessary ID consumption.

        Args:
            input_params: The clean input parameters for template rendering
            framework_params: The built-in framework variables
            operation_type: The operation type:
                - "CREATE": Generate new artifacts (generates artifact_id)
                - "UPDATE": Modify existing artifacts (no artifact_id)
                - "RETRIEVE": Read existing artifacts (no artifact_id)
                - "ROUTINE": Retrieve routine instructions (no artifact_id)
                - None: No operation type specified (no artifact_id)

        Returns:
            Enhanced context dictionary with built-in variables added

        Note: This is a pure computational function that never performs I/O.
              Only CREATE operations will trigger artifact ID generation.
        """
        # Start with a copy of input parameters to avoid mutation
        context = input_params.copy()

        # Add the clean input data as 'input_data' variable for templates like {{ input_data | to_yaml }}
        context["input_data"] = input_params.copy()

        # Add built-in template variables
        context.update(framework_params)

        # Only add artifact_id for CREATE operations to avoid unnecessary ID consumption
        if operation_type == "CREATE":
            try:
                # Extract process_name from built-in parameters using the correct BUILTIN_PROCESS key
                process_name = framework_params.get(BUILTIN_PROCESS)

                # Only add pantheon_artifact_id if process is available
                if process_name:
                    artifact_id_value = self._artifact_id.get_next_count(process_name)
                    context[BUILTIN_ARTIFACT_ID] = artifact_id_value
                    Log.debug(
                        f"Added artifact ID to template context: {process_name} = {artifact_id_value}"
                    )
                else:
                    # Log missing context but don't fail
                    Log.debug(
                        f"Artifact ID not available - missing process key '{BUILTIN_PROCESS}' in framework_params"
                    )

            except Exception as e:
                # Log error but don't fail template rendering
                # Add None value so conditional checks {% if artifact_id %} work with StrictUndefined
                context[BUILTIN_ARTIFACT_ID] = None
                Log.warning(f"Failed to add artifact ID to template context: {e}")
        else:
            Log.debug(
                f"Skipping artifact ID generation for operation type: {operation_type}"
            )

        return context

    def _check_for_undefined_variables(
        self, rendered_content: str, template_name: str, context: dict[str, Any]
    ) -> None:
        """
        Check rendered content for DebugUndefined variable markers and log warnings.

        DebugUndefined renders undefined variables as {{ variable_name }} strings
        in the output. This method detects these patterns and provides helpful
        error messages while allowing templates to render successfully.

        Args:
            rendered_content: The rendered template content to check
            template_name: Name of the template for error reporting
            context: The template context for suggesting available variables
        """
        import re

        # Pattern to match DebugUndefined output: {{ variable_name }}
        undefined_pattern = r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}"
        undefined_matches = re.findall(undefined_pattern, rendered_content)

        if undefined_matches:
            available_vars = list(context.keys())

            for undefined_var in undefined_matches:
                Log.debug(
                    f"Undefined variable '{undefined_var}' found in template '{template_name}'"
                )
                Log.debug(f"Available context variables: {available_vars}")

                # Try to suggest similar variable names
                suggestions = self._suggest_similar_variables(
                    undefined_var, available_vars
                )
                if suggestions:
                    Log.debug(f"Did you mean one of these? {suggestions}")
                else:
                    Log.debug(
                        f"Consider adding '{undefined_var}' to input data or updating the template"
                    )

    def _suggest_similar_variables(
        self, undefined_var: str, available_vars: list[str]
    ) -> list[str]:
        """
        Suggest similar variable names based on string similarity.

        Args:
            undefined_var: The undefined variable name
            available_vars: List of available variable names

        Returns:
            List of suggested similar variable names
        """
        suggestions = []
        undefined_lower = undefined_var.lower()

        for var in available_vars:
            var_lower = var.lower()

            # Check for exact substring matches or word-based similarity
            if (
                undefined_lower in var_lower
                or var_lower in undefined_lower
                or self._has_common_words(undefined_var, var)
            ):
                suggestions.append(var)
            # Check for similar names (simple edit distance approximation)
            elif len(undefined_var) > 3 and len(var) > 3:
                # Count matching characters in similar positions
                matches = sum(
                    1
                    for i, c in enumerate(undefined_lower)
                    if i < len(var_lower) and c == var_lower[i]
                )
                if matches >= min(len(undefined_var), len(var)) * 0.6:  # 60% similarity
                    suggestions.append(var)

        return suggestions[:3]  # Return top 3 suggestions

    def _has_common_words(self, var1: str, var2: str) -> bool:
        """
        Check if two variable names share common words (split by underscore).

        Args:
            var1: First variable name
            var2: Second variable name

        Returns:
            True if they share at least one common word
        """
        words1 = set(var1.lower().split("_"))
        words2 = set(var2.lower().split("_"))
        return len(words1.intersection(words2)) > 0

    def render_template(
        self,
        template_str: str,
        context: dict[str, Any],
        template_name: str = "basic template",
    ) -> str:
        """
        Basic template rendering without includes.

        Public method for basic Jinja2 template rendering using a simple environment
        without FileSystemLoader. Used for templates that don't need include support.

        Args:
            template_str: Jinja2 template content to render
            context: Complete context dictionary for template variables

        Returns:
            Rendered template content as string

        Raises:
            ValueError: If template content is empty or None
            RuntimeError: If template rendering fails due to syntax or variable errors
        """
        env = self._create_basic_jinja_environment()
        return self._render_with_environment(template_str, context, env, template_name)

    def render_artifact_template(
        self,
        template_str: str,
        context: dict[str, Any],
        env: jinja2.Environment,
        template_name: str = "artifact template",
    ) -> str:
        """
        Artifact template rendering with include support.

        Public method for rendering process artifact templates that may contain
        include statements. Requires a pre-configured Jinja2 environment with
        FileSystemLoader from the workspace.

        Args:
            template_str: Jinja2 template content to render
            context: Complete context dictionary for template variables
            env: Pre-configured Jinja2 Environment with FileSystemLoader

        Returns:
            Rendered template content as string

        Raises:
            ValueError: If template content is empty or None
            RuntimeError: If template rendering fails due to syntax or variable errors
        """
        return self._render_with_environment(template_str, context, env, template_name)

    def _render_with_environment(
        self,
        template_str: str,
        context: dict[str, Any],
        env: jinja2.Environment,
        template_name: str = "unknown template",
    ) -> str:
        """
        Common rendering logic using provided environment.

        Internal helper method that performs the actual template rendering using
        the provided Jinja2 environment. This enables code reuse between basic
        and artifact template rendering methods.

        Args:
            template_str: Jinja2 template content to render
            context: Complete context dictionary for template variables
            env: Configured Jinja2 Environment to use for rendering

        Returns:
            Rendered template content as string

        Raises:
            ValueError: If template content is empty or None
            RuntimeError: If template rendering fails due to syntax or variable errors
        """
        if not template_str:
            raise ValueError("Template content cannot be empty or None")

        if not isinstance(context, dict):
            raise ValueError("Context must be a dictionary")

        # Add custom YAML filter to generate YAML artifacts
        def to_yaml_filter(data: Any) -> str:
            """
            Convert data to YAML format with optional documentation from property_definitions.

            If the data contains a 'property_definitions' key, it will be used to generate
            documentation headers. The 'property_definitions' key itself is excluded from
            the final YAML output.

            Args:
                data: The data to convert to YAML

            Returns:
                YAML string with documentation header when property_definitions are available
            """
            if not isinstance(data, dict):
                # If data is not a dict, just return basic YAML
                return yaml.dump(data, default_flow_style=False, allow_unicode=True)

            # Check if data contains property definitions
            property_definitions = data.get("property_definitions")

            if property_definitions is None:
                # No property definitions, return basic YAML
                return yaml.dump(data, default_flow_style=False, allow_unicode=True)

            # Generate YAML with documentation header, excluding property_definitions
            return self._generate_yaml_with_data_definitions(data, property_definitions)

        env.filters["to_yaml"] = to_yaml_filter

        try:
            # Create template from string using provided environment
            Log.debug(f"template_str preview: {template_str[:100]}")
            Log.debug(
                f"Rendering template '{template_name}' with context keys: {list(context.keys())}"
            )

            # Validate context before expansion
            if not isinstance(context, dict):
                raise ValueError(f"Context must be a dictionary, got {type(context)}")

            # Check for any non-string keys in context that might cause dict expansion issues
            for key in context:
                if not isinstance(key, str):
                    Log.warning(
                        f"Non-string key found in context: {key} (type: {type(key)})"
                    )

            template = env.from_string(template_str)

            # Render with context - explicitly cast to str
            Log.debug(
                f"About to render template '{template_name}' with context expansion"
            )
            rendered_result: str = str(template.render(**context))
            Log.debug(f"Rendered template preview: {rendered_result[:100]}")

            # Normalize excessive newlines in rendered output
            rendered_result = self._normalize_newlines(rendered_result)

            # Check for DebugUndefined markers in the rendered output
            self._check_for_undefined_variables(rendered_result, template_name, context)

            return rendered_result

        except jinja2.TemplateError as e:
            # Enhanced error logging with template context
            error_msg = str(e)

            Log.error(f"Template rendering error in {template_name}: {error_msg}")
            Log.error(f"Available context variables: {list(context.keys())}")

            # Detect undefined variable errors specifically
            if isinstance(e, jinja2.UndefinedError):
                Log.error(
                    "Undefined variable error - check if all required template variables are provided"
                )
                # Try to extract the undefined variable name from the error message
                import re

                undefined_var_match = re.search(r"'([^']+)' is undefined", error_msg)
                if undefined_var_match:
                    undefined_var = undefined_var_match.group(1)
                    Log.error(f"Missing template variable: '{undefined_var}'")
                    Log.error(
                        f"Consider adding '{undefined_var}' to input data or updating the template"
                    )

            raise RuntimeError(
                f"Template rendering failed in {template_name}: {error_msg}"
            ) from e
        except Exception as e:
            Log.error(f"Unexpected error during template rendering: {str(e)}")
            Log.error(f"Available context variables: {list(context.keys())}")
            raise RuntimeError(
                f"Template rendering failed due to unexpected error: {str(e)}"
            ) from e

    def _create_basic_jinja_environment(self) -> jinja2.Environment:
        """
        Create basic Jinja environment without FileSystemLoader.

        Internal helper method that creates a Jinja2 environment with standard
        settings but no file system access. Used for basic template rendering
        that doesn't require include statements.

        Returns:
            Configured Jinja2 Environment without FileSystemLoader
        """
        # Create Jinja2 environment with safe configuration
        env = jinja2.Environment(
            autoescape=False,  # Disable HTML escaping for text/markdown content
            undefined=jinja2.DebugUndefined,  # Log undefined variables but allow conditionals
            trim_blocks=False,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        # Register custom filters
        env.filters["slugify"] = slugify
        env.filters["remove_suffix"] = remove_suffix

        return env

    def create_artifact_jinja_environment(
        self, workspace: "PantheonWorkspace"
    ) -> jinja2.Environment:
        """
        Create Jinja2 environment with semantic URI include support.

        Public method that constructs a Jinja2 Environment with ChoiceLoader combining
        SemanticUriLoader and FileSystemLoader, enabling both semantic URI includes
        (artifact-template://, process-schema://, etc.) and regular file-based includes
        in templates.

        The ChoiceLoader tries loaders in order: SemanticUriLoader first for semantic
        URIs, then FileSystemLoader for regular file paths. This priority ensures
        semantic URIs are resolved correctly before attempting file-based resolution.

        Args:
            workspace: PantheonWorkspace instance for semantic URI resolution and
                      team source root path determination

        Returns:
            Configured Jinja2 Environment with ChoiceLoader supporting both semantic
            URI includes and file-based includes

        Example:
            # In ProcessHandler during CREATE operation
            env = artifact_engine.create_artifact_jinja_environment(workspace)
            rendered = artifact_engine.render_artifact_template(
                template_str=content_template,
                context=validated_data,
                env=env
            )

        Note:
            - DebugUndefined allows graceful handling of optional template variables
            - Custom filters (slugify, remove_suffix) are registered automatically
            - FileSystemLoader uses team source root as base path for relative includes
        """
        # Get team source root for FileSystemLoader base path
        try:
            team_root = workspace._get_active_team_root()
            base_path = str(team_root)
        except ValueError:
            # Fallback to current directory if team root is not set
            base_path = "."

        # Create ChoiceLoader with SemanticUriLoader first, then FileSystemLoader
        loader = jinja2.ChoiceLoader(
            [
                SemanticUriLoader(workspace),
                jinja2.FileSystemLoader(base_path),
            ]
        )

        # Create Jinja2 environment with debug undefined handling
        env = jinja2.Environment(
            loader=loader,
            autoescape=False,  # Disable HTML escaping for text/markdown content
            undefined=jinja2.DebugUndefined,  # Log undefined variables but allow conditionals
            trim_blocks=False,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        # Register custom filters
        env.filters["slugify"] = slugify
        env.filters["remove_suffix"] = remove_suffix

        return env

    def _generate_path(self, pattern: str, context: dict[str, Any]) -> PantheonPath:
        """
        Generate PantheonPath by rendering path pattern with context data.

        Internal helper method for path generation used by generate_artifact.
        The pattern is rendered with the provided context data and converted
        into a path object that enforces the protection proxy pattern.

        Args:
            pattern: Jinja2 template pattern for the complete path
            context: Data context for template rendering

        Returns:
            PantheonPath object (not pathlib.Path) for safe I/O delegation

        Raises:
            ValueError: If pattern is empty or None
            RuntimeError: If template rendering fails
            SecurityError: If rendered path contains directory traversal attempts

        Note: This is a pure computational function that never performs I/O.
        Returns PantheonPath to prevent accidental I/O operations.
        """
        raise NotImplementedError("Interface method - implementation deferred")

    def _get_timezone_abbreviation(self, now: datetime) -> str:
        """
        Get timezone abbreviation for consistent timestamp formatting.

        Args:
            now: datetime object with timezone info

        Returns:
            Timezone abbreviation (e.g., 'PDT', 'EST', 'UTC')
        """
        tz_name = now.strftime("%Z")
        # If it's a long timezone name, create abbreviation from first letters
        if len(tz_name) > 4:
            # Split on spaces and take first letter of each word
            return "".join(word[0].upper() for word in tz_name.split())
        # Already short, use as-is
        return tz_name

    def _generate_timestamp(self) -> str:
        """
        Generate timestamp string for built-in template variable.

        Provides consistent timestamp formatting across all template rendering
        operations. The format follows the framework's standard timestamp
        conventions for artifact metadata.

        Returns:
            Formatted timestamp string for {{ timestamp }} variable
            Format: 'YYYY-MM-DD hh:mm AM/PM TZ' (e.g., '2025-08-29 10:05 PM PDT')

        Note: This is a pure computational function that never performs I/O.
        """
        now = datetime.now().astimezone()
        tz_abbr = self._get_timezone_abbreviation(now)
        return now.strftime("%Y-%m-%d %I:%M %p") + f" {tz_abbr}"

    def _generate_datestamp(self) -> str:
        """
        Generate datestamp string for built-in template variable.

        Provides consistent datestamp formatting across all template rendering
        operations. The format follows the framework's standard date
        conventions for artifact organization.

        Returns:
            Formatted datestamp string for {{ datestamp }} variable
            Format: 'YYYY-MM-DD TZ' (e.g., '2025-08-29 PDT')

        Note: This is a pure computational function that never performs I/O.
        """
        now = datetime.now().astimezone()
        tz_abbr = self._get_timezone_abbreviation(now)
        return now.strftime("%Y-%m-%d") + f" {tz_abbr}"

    # Artifact Retrieval Methods - Uses Workspace for I/O

    def _parse_section_markers(
        self, content: str, start_marker: str, end_marker: str
    ) -> str | None:
        """
        Parse and extract content between section markers.

        Internal helper method that provides the core logic for parsing HTML comment
        markers and extracting the content between start and end markers. It handles
        the marker pattern matching and content extraction used by the
        get_artifact_sections method.

        Args:
            content: The content to parse for markers
            start_marker: The start marker pattern to find
            end_marker: The end marker pattern to find

        Returns:
            Extracted content between markers, or None if not found

        Note: This is a pure computational function that never performs I/O.
        """
        try:
            # Find start marker position
            start_pos = content.find(start_marker)
            if start_pos == -1:
                return None

            # Find end marker position after the start marker
            end_pos = content.find(end_marker, start_pos + len(start_marker))
            if end_pos == -1:
                return None

            # Extract content between markers
            section_start = start_pos + len(start_marker)
            extracted_content = content[section_start:end_pos]

            # Strip leading/trailing whitespace but preserve internal formatting
            return extracted_content.strip()

        except Exception as e:
            Log.warning(f"Error parsing section markers: {e}")
            return None

    def resolve_uri_data(
        self,
        jsonnet_content: str,
        data_path: str,
        ext_vars: dict[str, Any] | None = None,
    ) -> Any:
        """
        Compile Jsonnet and extract data using WYSIWYG path resolution.

        This method compiles the Jsonnet content first, then attempts to extract
        the requested data path using a WYSIWYG approach - users specify paths
        based on what they see in the source file, not the compiled structure.

        If the direct path fails and the compiled result has a 'properties' wrapper,
        it automatically tries to find the path inside the properties section.

        Args:
            jsonnet_content: The preprocessed Jsonnet content to compile
            data_path: Dot-notation path to extract (e.g., "sections.plan")
            ext_vars: Optional external variables for Jsonnet compilation

        Returns:
            The extracted data at the specified path

        Raises:
            KeyError: If the data path cannot be found in the compiled result
            RuntimeError: If Jsonnet compilation fails

        Example:
            # Source file has: {"sections": {"plan": {...}}}
            # User requests: data_path="sections.plan"
            # Works even if compilation wraps it in {"properties": {"sections": {...}}}
        """
        Log.debug(
            f"Resolving URI data from Jsonnet content (length: {len(jsonnet_content)})"
        )
        Log.debug(f"Requested data path: '{data_path}'")

        # 1. Compile the preprocessed Jsonnet content
        compiled_result = self._compile_jsonnet(
            jsonnet_content,
            ext_vars=ext_vars,
        )

        # Convert to JSON string for logging, then back to dict
        compiled_json = json.dumps(compiled_result, indent=2)
        Log.debug(f"Compiled JSON result: {compiled_json}")

        # If no data path specified, return entire compiled result
        if not data_path:
            Log.debug("No data path specified, returning entire compiled result")
            return compiled_result

        # 2. Try to extract the data path using dot notation
        try:
            extracted_data = self._extract_path(compiled_result, data_path)
            Log.debug(
                f"Successfully extracted data using direct path: {json.dumps(extracted_data)}"
            )
            return extracted_data
        except KeyError as e:
            Log.debug(f"Direct path extraction failed: {e}")

        # 3. If direct path fails and result has 'properties', try inside properties
        if (
            isinstance(compiled_result, dict)
            and "properties" in compiled_result
            and not data_path.startswith("properties.")
        ):
            try:
                extracted_data = self._extract_path(
                    compiled_result["properties"], data_path
                )
                Log.debug(
                    f"Successfully extracted data from properties wrapper: {json.dumps(extracted_data)}"
                )
                return extracted_data
            except KeyError as e:
                Log.debug(f"Properties path extraction also failed: {e}")

        # 4. If all attempts fail, raise clear error
        available_paths = self._get_available_paths(compiled_result)
        error_msg = f"Data path '{data_path}' not found in compiled result. Available paths: {available_paths}"
        Log.error(error_msg)
        raise KeyError(error_msg)

    def _extract_path(self, data: Any, path: str) -> Any:
        """
        Extract data using dot notation path with array index support.

        Args:
            data: The data structure to extract from
            path: Dot-notation path (e.g., "sections.plan" or "rules.0.pattern")

        Returns:
            The data at the specified path

        Raises:
            KeyError: If any part of the path is not found
        """
        if not path:
            return data

        parts = path.split(".")
        result = data

        for i, part in enumerate(parts):
            try:
                if part.isdigit():
                    # Array/list access
                    if not isinstance(result, list | tuple):
                        raise KeyError(
                            f"Expected array at path segment '{'.'.join(parts[:i])}', got {type(result).__name__}"
                        )
                    result = result[int(part)]
                else:
                    # Object/dict access
                    if not isinstance(result, dict):
                        raise KeyError(
                            f"Expected object at path segment '{'.'.join(parts[:i])}', got {type(result).__name__}"
                        )
                    result = result[part]
            except (KeyError, IndexError, TypeError) as e:
                current_path = ".".join(parts[: i + 1])
                raise KeyError(f"Path segment '{current_path}' not found: {e}") from e

        return result

    def _get_available_paths(
        self, data: Any, prefix: str = "", max_depth: int = 3
    ) -> list[str]:
        """
        Get a list of available paths in the data structure for error reporting.

        Args:
            data: The data structure to analyze
            prefix: Current path prefix (for recursion)
            max_depth: Maximum depth to traverse to avoid infinite recursion

        Returns:
            List of available dot-notation paths
        """
        if max_depth <= 0:
            return []

        paths = []

        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{prefix}.{key}" if prefix else key
                paths.append(current_path)

                # Recurse into nested structures
                if isinstance(value, dict | list) and max_depth > 1:
                    nested_paths = self._get_available_paths(
                        value, current_path, max_depth - 1
                    )
                    paths.extend(nested_paths)

        elif isinstance(data, list | tuple):
            for i, value in enumerate(data):
                current_path = f"{prefix}.{i}" if prefix else str(i)
                paths.append(current_path)

                # Recurse into nested structures
                if isinstance(value, dict | list) and max_depth > 1:
                    nested_paths = self._get_available_paths(
                        value, current_path, max_depth - 1
                    )
                    paths.extend(nested_paths)

        return paths

    def _generate_yaml_with_comments(self, data: Any, schema: dict[str, Any]) -> str:
        """
        Generate YAML with schema documentation header and minimal inline comments.

        This method creates human-readable YAML by adding:
        - A documentation header explaining all field types and constraints
        - Minimal inline comments for key identification only

        Args:
            data: The data to convert to YAML
            schema: JSON schema containing descriptions and constraints

        Returns:
            YAML string with documentation header and basic structure comments
        """
        try:
            # Extract properties schema for documentation generation
            properties = schema.get("properties", {})
            if not properties:
                # No schema properties available, return basic YAML
                return yaml.dump(data, default_flow_style=False, allow_unicode=True)

            # Generate documentation header for profile properties only
            doc_header = self._generate_schema_documentation_header(properties)

            # Generate basic YAML without repetitive comments
            yaml_lines = yaml.dump(
                data, default_flow_style=False, allow_unicode=True
            ).splitlines()

            # Only add comments if we have a documentation header
            if doc_header:
                # Add minimal structural comments for key sections only
                commented_lines = []
                for line in yaml_lines:
                    commented_line = self._add_minimal_structure_comment(
                        line, properties
                    )
                    commented_lines.append(commented_line)
                result_parts = [doc_header, ""] + commented_lines
                return "\n".join(result_parts)

            # No profile properties to document, return clean YAML without any comments
            return "\n".join(yaml_lines)

        except Exception as e:
            Log.warning(f"Failed to generate YAML with comments: {e}")
            # Fallback to basic YAML if comment generation fails
            return yaml.dump(data, default_flow_style=False, allow_unicode=True)

    def _generate_yaml_with_data_definitions(
        self, data: dict[str, Any], property_definitions: dict[str, Any]
    ) -> str:
        """
        Generate YAML with documentation header from data-driven property definitions.

        This method creates human-readable YAML by:
        - Extracting property definitions from the input data
        - Generating a documentation header explaining all field types and constraints
        - Excluding the 'property_definitions' key from the final YAML output
        - Adding minimal inline comments for key identification

        Args:
            data: The complete input data including property_definitions
            property_definitions: Property definition metadata from the input data

        Returns:
            YAML string with documentation header and clean output excluding property_definitions
        """
        try:
            # Generate documentation header from property definitions
            doc_header = self._generate_data_documentation_header(property_definitions)

            # Create a copy of data excluding property_definitions for YAML output
            yaml_data = {k: v for k, v in data.items() if k != "property_definitions"}

            # Generate basic YAML from the filtered data
            yaml_lines = yaml.dump(
                yaml_data, default_flow_style=False, allow_unicode=True
            ).splitlines()

            # Only add comments if we have a documentation header
            if doc_header:
                # Add minimal structural comments for key sections only
                commented_lines = []
                for line in yaml_lines:
                    commented_line = self._add_minimal_data_comment(
                        line, property_definitions
                    )
                    commented_lines.append(commented_line)
                result_parts = [doc_header, ""] + commented_lines
                return "\n".join(result_parts)

            # No property definitions to document, return clean YAML
            return "\n".join(yaml_lines)

        except Exception as e:
            Log.warning(f"Failed to generate YAML with data definitions: {e}")
            # Fallback to basic YAML if generation fails, excluding property_definitions
            yaml_data = {k: v for k, v in data.items() if k != "property_definitions"}
            return yaml.dump(yaml_data, default_flow_style=False, allow_unicode=True)

    def _generate_data_documentation_header(
        self, property_definitions: dict[str, Any]
    ) -> str:
        """
        Generate a documentation header from data-driven property definitions.

        Creates a comprehensive header explaining all profile properties based on
        the property_definitions provided in the input data.

        Args:
            property_definitions: Dictionary containing property definitions with type, description, enum, etc.

        Returns:
            Formatted documentation header as multi-line comment string
        """
        if not property_definitions or not isinstance(property_definitions, dict):
            return ""

        header_lines = ["# Profile Properties Documentation:", "#"]

        for prop_name, prop_def in property_definitions.items():
            if not isinstance(prop_def, dict):
                continue

            header_lines.append(f"# {prop_name}:")

            # Add description if available
            description = prop_def.get("description", "")
            if description:
                # Clean up "Example:" prefix if present
                if description.startswith("Example: "):
                    description = description[9:]
                header_lines.append(f"#   Description: {description}")

            # Add type information
            prop_type = prop_def.get("type", "unknown")
            if prop_type == "boolean":
                header_lines.append(f"#   Type: {prop_type} (true/false)")
            else:
                header_lines.append(f"#   Type: {prop_type}")

            # Add enum options if available
            enum_values = prop_def.get("enum")
            if enum_values and isinstance(enum_values, list):
                options_str = ", ".join(str(v) for v in enum_values)
                header_lines.append(f"#   Options: {options_str}")

            header_lines.append("#")

        return "\n".join(header_lines)

    def _add_minimal_data_comment(
        self, yaml_line: str, property_definitions: dict[str, Any]
    ) -> str:
        """
        Add minimal comment to a YAML line based on data-driven property definitions.

        Only adds comments for top-level keys that are defined in property_definitions
        to help identify documented properties in the YAML structure.

        Args:
            yaml_line: Single line from YAML output
            property_definitions: Property definitions from input data

        Returns:
            YAML line with optional minimal comment for identification
        """
        # Skip empty lines or lines that are just values (indented without keys)
        stripped = yaml_line.strip()
        if not stripped or ":" not in stripped:
            return yaml_line

        # Only process top-level keys (no leading whitespace before key)
        if yaml_line.startswith((" ", "\t")):
            return yaml_line

        # Extract the property key (everything before the first colon, stripped)
        key_part = stripped.split(":")[0].strip()

        # Handle array indicators and other YAML syntax
        if key_part.startswith(("- ", "#")):
            return yaml_line

        # Only add comment for properties that have definitions
        if key_part in property_definitions:
            # Just add field name as identifier, no repetitive details
            return f"{yaml_line}  # {key_part} (documented above)"

        return yaml_line

    def _add_schema_comment(self, yaml_line: str, properties: dict[str, Any]) -> str:
        """
        Add schema-based comment to a YAML line if it contains a property key.

        Args:
            yaml_line: Single line from YAML output
            properties: Schema properties dictionary

        Returns:
            YAML line with comment appended if applicable
        """
        # Skip empty lines or lines that are just values (indented without keys)
        stripped = yaml_line.strip()
        if not stripped or ":" not in stripped:
            return yaml_line

        # Extract the property key (everything before the first colon, stripped)
        key_part = stripped.split(":")[0].strip()

        # Handle array indicators and other YAML syntax
        if key_part.startswith(("- ", "#")):
            return yaml_line

        # Check if this key exists in the schema properties
        if key_part in properties:
            prop_schema = properties[key_part]
            comment_parts = []

            # Add description if available
            if "description" in prop_schema:
                description = prop_schema["description"]
                # Clean up "Example:" prefix if present
                if description.startswith("Example: "):
                    description = description[9:]
                comment_parts.append(description)

            # Add enum values if available
            if "enum" in prop_schema:
                enum_values = prop_schema["enum"]
                comment_parts.append(
                    f"Options: {', '.join(str(v) for v in enum_values)}"
                )

            # Add type info for boolean fields
            if prop_schema.get("type") == "boolean":
                comment_parts.append("true/false")

            # Add default value if specified
            if "default" in prop_schema:
                default_val = prop_schema["default"]
                comment_parts.append(f"Default: {default_val}")

            # Combine comment parts and add to line
            if comment_parts:
                comment = " | ".join(comment_parts)
                return f"{yaml_line}  # {comment}"

        return yaml_line

    def _generate_schema_documentation_header(self, properties: dict[str, Any]) -> str:
        """
        Generate a YAML comment header documenting profile properties only.

        Args:
            properties: Schema properties dictionary

        Returns:
            Multi-line comment header explaining profile properties, or empty string if none
        """
        # Extract profile properties from nested schema structure
        profile_properties = self._extract_profile_properties(properties)

        if not profile_properties:
            # No profile properties to document, return empty string
            return ""

        lines = ["# Profile Properties Documentation:", "#"]

        for field_name, field_schema in profile_properties.items():
            field_lines = [f"# {field_name}:"]

            # Add description
            if "description" in field_schema:
                description = field_schema["description"]
                # Clean up "Example:" prefix if present
                if description.startswith("Example: "):
                    description = description[9:]
                field_lines.append(f"#   Description: {description}")

            # Add type information
            if "type" in field_schema:
                field_type = field_schema["type"]
                if field_type == "boolean":
                    field_lines.append("#   Type: boolean (true/false)")
                else:
                    field_lines.append(f"#   Type: {field_type}")

            # Add enum options
            if "enum" in field_schema:
                options = ", ".join(str(v) for v in field_schema["enum"])
                field_lines.append(f"#   Options: {options}")

            # Add default value
            if "default" in field_schema:
                field_lines.append(f"#   Default: {field_schema['default']}")

            lines.extend(field_lines)
            lines.append("#")  # Blank comment line between fields

        # Remove the last blank line
        lines.pop()

        return "\n".join(lines)

    def _extract_profile_properties(self, properties: dict[str, Any]) -> dict[str, Any]:
        """
        Extract profile properties from schema structure.

        Args:
            properties: Top-level schema properties

        Returns:
            Dictionary of profile properties, or empty dict if none found
        """
        # Look for profiles -> additionalProperties -> properties (nested profile structure)
        if "profiles" in properties:
            profiles_schema = properties["profiles"]
            if isinstance(profiles_schema, dict):
                additional_props = profiles_schema.get("additionalProperties", {})
                if isinstance(additional_props, dict):
                    # Check if this references a $def
                    if "$ref" in additional_props:
                        # Can't resolve $ref here, return empty
                        return {}
                    # Check if it has properties directly
                    if "properties" in additional_props:
                        nested_properties = additional_props["properties"]
                        if isinstance(nested_properties, dict):
                            return nested_properties

        return {}

    def _add_minimal_structure_comment(
        self, yaml_line: str, properties: dict[str, Any]
    ) -> str:
        """
        Add minimal structural comments only for top-level keys.

        Args:
            yaml_line: Single line from YAML output
            properties: Schema properties dictionary

        Returns:
            YAML line with minimal comment if it's a top-level documented key
        """
        # Skip empty lines or lines that are just values (indented without keys)
        stripped = yaml_line.strip()
        if not stripped or ":" not in stripped:
            return yaml_line

        # Only process top-level keys (no leading whitespace before key)
        if yaml_line.startswith((" ", "\t")):
            return yaml_line

        # Extract the property key (everything before the first colon, stripped)
        key_part = stripped.split(":")[0].strip()

        # Handle array indicators and other YAML syntax
        if key_part.startswith(("- ", "#")):
            return yaml_line

        # Only add comment for documented top-level keys
        if key_part in properties:
            # Just add field name as identifier, no repetitive details
            return f"{yaml_line}  # {key_part} configuration"

        return yaml_line

    def _normalize_id(self, process_name: str, fuzzy_id: str) -> str:
        """
        Normalize a fuzzy artifact ID using process-specific rules.

        Applies regex transformation rules from parser.jsonnet sequentially
        to transform fuzzy IDs into canonical form. Handles common transformations
        like strip whitespace, extract basename, and normalize format.

        Args:
            process_name: Name of the process for context
            fuzzy_id: The raw identifier to normalize

        Returns:
            Canonical ID string, or original fuzzy_id if normalization fails

        Note: This method uses workspace for retrieving parser rules and compiles Jsonnet.
        """
        try:
            # Get parser rules from workspace
            parser_content = self._workspace.get_artifact_parser(process_name)
            if not parser_content or not parser_content.strip():
                Log.debug(
                    f"No parser rules found for process '{process_name}', using fuzzy_id as-is"
                )
                return fuzzy_id

            # Compile Jsonnet to get transformation rules (returns Python object, not JSON string)
            rules = self._compile_jsonnet(parser_content, {})

            if not isinstance(rules, list):
                Log.warning(
                    f"Invalid parser format for process '{process_name}' - expected array, got {type(rules)}"
                )
                return fuzzy_id

            Log.debug(f"Applying {len(rules)} normalization rules to ID '{fuzzy_id}'")

            # Apply rules sequentially
            current_id = fuzzy_id
            for rule in rules:
                if (
                    not isinstance(rule, dict)
                    or NORMALIZER_PATTERN_KEY not in rule
                    or NORMALIZER_REPLACEMENT_KEY not in rule
                ):
                    Log.debug(f"Skipping malformed parser rule (missing keys): {rule}")
                    continue

                try:
                    pattern = rule[NORMALIZER_PATTERN_KEY]
                    replacement = rule[NORMALIZER_REPLACEMENT_KEY]
                    old_id = current_id
                    current_id = re.sub(pattern, replacement, current_id)
                    Log.debug(
                        f"Applied rule '{pattern}' -> '{replacement}': '{old_id}' -> '{current_id}'"
                    )
                except re.error as e:
                    Log.warning(f"Invalid regex pattern '{pattern}': {e}")
                    continue

            Log.debug(f"Final normalized ID: '{fuzzy_id}' -> '{current_id}'")
            return current_id

        except Exception as e:
            Log.warning(
                f"Unexpected error during ID normalization for process '{process_name}': {e}"
            )
            return fuzzy_id

    def _locate_artifact(
        self, process_name: str, canonical_id: str
    ) -> PantheonPath | None:
        """
        Locate artifact using finder pattern and canonical ID.

        Retrieves finder pattern from workspace, injects canonical ID, and
        searches for matching files in the artifacts directory.

        Args:
            process_name: Name of the process for context
            canonical_id: The normalized canonical ID

        Returns:
            PantheonPath to found artifact, or None if not found or ambiguous

        Note: This method uses workspace for pattern retrieval and file search.
        """
        try:
            # Get finder pattern from workspace (already preprocessed)
            try:
                artifact_locator_jsonnet = self._workspace.get_artifact_locator(
                    process_name
                )
                if not artifact_locator_jsonnet or not artifact_locator_jsonnet.strip():
                    Log.warning(
                        f"No artifact locator found for process '{process_name}'"
                    )
                    return None

            except FileNotFoundError:
                Log.warning(f"No artifact locator found for process '{process_name}'")
                return None

            # Compile Jsonnet with artifact ID as external variable
            ext_vars = {"pantheon_artifact_id": canonical_id}
            Log.debug(
                f"artifact_locator_jsonnet: {artifact_locator_jsonnet}, ext_vars: {ext_vars}"
            )

            artifact_locator_json = self._compile_jsonnet(
                artifact_locator_jsonnet, ext_vars
            )

            if (
                not isinstance(artifact_locator_json, dict)
                or LOCATOR_PATTERN_KEY not in artifact_locator_json
            ):
                Log.warning(
                    f"Invalid finder format for process '{process_name}' - expected object with '{LOCATOR_PATTERN_KEY}' keys"
                )
                return None

            # Extract directory field (optional)
            artifact_directory = artifact_locator_json.get(LOCATOR_DIRECTORY_KEY)

            # Get the compiled search pattern (ID already injected by Jsonnet)
            search_pattern = artifact_locator_json[LOCATOR_PATTERN_KEY]

            # Log the search approach for debugging
            if artifact_directory:
                Log.debug(
                    f"Performing directory-scoped search in '{artifact_directory}' for pattern '{search_pattern}'"
                )
            else:
                Log.debug(
                    f"Performing full artifacts_root search for pattern '{search_pattern}'"
                )

            # Use workspace delegation to find matching files with optional directory scope
            matching_files = self._workspace.get_matching_artifact(
                search_pattern, directory=artifact_directory
            )

            if not matching_files:
                Log.debug(
                    f"No artifacts found matching pattern for ID '{canonical_id}'"
                )
                return None
            if len(matching_files) > 1:
                Log.warning(
                    f"Multiple artifacts found for ID '{canonical_id}': {[str(f) for f in matching_files]}"
                )
                return None

            # Single unique match found
            return matching_files[0]

        except json.JSONDecodeError as e:
            Log.warning(
                f"Failed to parse finder JSON for process '{process_name}': {e}"
            )
            return None
        except Exception as e:
            Log.warning(
                f"Unexpected error during artifact location for process '{process_name}': {e}"
            )
            return None

    def _locate_singleton_artifact(self, process_name: str) -> PantheonPath | None:
        """
        Locate singleton artifact (expects exactly one artifact, no ID needed).

        Retrieves finder pattern from workspace and searches for matching files
        in the artifacts directory. Enforces exactly 1 match requirement - errors
        if 0 or multiple artifacts are found.

        Args:
            process_name: Name of the process for context

        Returns:
            PantheonPath to found artifact, or None if not found or multiple found

        Note: This method uses workspace for pattern retrieval and file search.
        """
        try:
            # Get finder pattern from workspace (already preprocessed)
            try:
                artifact_locator_jsonnet = self._workspace.get_artifact_locator(
                    process_name
                )
                if not artifact_locator_jsonnet or not artifact_locator_jsonnet.strip():
                    Log.warning(
                        f"No artifact locator found for process '{process_name}'"
                    )
                    return None
            except FileNotFoundError:
                Log.warning(f"No artifact locator found for process '{process_name}'")
                return None

            # Compile Jsonnet WITHOUT artifact ID (singleton mode)
            artifact_locator_json = self._compile_jsonnet(artifact_locator_jsonnet, {})

            if (
                not isinstance(artifact_locator_json, dict)
                or LOCATOR_PATTERN_KEY not in artifact_locator_json
            ):
                Log.warning(
                    f"Invalid finder format for process '{process_name}' - expected object with '{LOCATOR_PATTERN_KEY}' keys"
                )
                return None

            # Extract directory field (optional)
            artifact_directory = artifact_locator_json.get(LOCATOR_DIRECTORY_KEY)

            # Get the compiled search pattern (exact pattern without ID injection)
            search_pattern = artifact_locator_json[LOCATOR_PATTERN_KEY]

            # Log the search approach for debugging
            if artifact_directory:
                Log.debug(
                    f"Singleton search in '{artifact_directory}' for pattern '{search_pattern}'"
                )
            else:
                Log.debug(
                    f"Singleton search in artifacts_root for pattern '{search_pattern}'"
                )

            # Use workspace delegation to find matching files with optional directory scope
            matching_files = self._workspace.get_matching_artifact(
                search_pattern, directory=artifact_directory
            )

            if not matching_files:
                Log.warning(
                    f"Singleton mode: No artifacts found for process '{process_name}'"
                )
                return None
            if len(matching_files) > 1:
                Log.warning(
                    f"Singleton mode: Multiple artifacts found for process '{process_name}': {[str(f) for f in matching_files]}. Expected exactly 1."
                )
                return None

            # Single unique match found
            Log.debug(
                f"Singleton mode: Found artifact for process '{process_name}': {matching_files[0]}"
            )
            return matching_files[0]

        except json.JSONDecodeError as e:
            Log.warning(
                f"Failed to parse finder JSON for process '{process_name}': {e}"
            )
            return None
        except Exception as e:
            Log.warning(
                f"Unexpected error during singleton artifact location for process '{process_name}': {e}"
            )
            return None
