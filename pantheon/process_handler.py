"""ProcessHandler implementation for orchestrating process execution.

The ProcessHandler serves as the central orchestrator that implements the core
business logic for executing processes. It determines the operation type by
checking file combinations (CREATE: content.md+placement.jinja+naming.jinja,
UPDATE: patch.md+locator/parser/target, RETRIEVE: locator/parser/sections),
coordinates the workflow by
requesting schemas and templates from the Workspace, passing them to the
ArtifactEngine for computation, and then using the Workspace to save results.
"""

from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
import json
from typing import TYPE_CHECKING, Any, Literal
import urllib.parse

from typing_extensions import TypedDict
import yaml

from pantheon.constants import (
    BUILTIN_ACTOR,
    BUILTIN_ARTIFACT_ID,
    BUILTIN_DATESTAMP,
    BUILTIN_FULL_PROFILE,
    BUILTIN_INSERT_MODE,
    BUILTIN_PROCESS,
    BUILTIN_TIMESTAMP,
    FRAMEWORK_PARAMETER_SYNONYMS,
    FRAMEWORK_PARAMETERS,
    INPUT_ACTOR,
    INPUT_FRAMEWORK_PARAMS,
    INPUT_INPUT_PARAMS,
    INPUT_PROCESS,
    PARAM_SECTIONS,
    PROCESS_TYPE_BUILD,
    PROCESS_TYPE_CREATE,
    PROCESS_TYPE_GET,
    PROCESS_TYPE_UPDATE,
    RESULT_ERROR,
    RESULT_FILES_CREATED,
    RESULT_OUTPUT,
    RESULT_SUCCESS,
    TEMPLATE_YAML_FRONT_MATTER,
)
from pantheon.logger import Log
from pantheon.markdown_formatter import fix_markdown_formatting
from pantheon.path import PantheonPath
from pantheon.update_composer import generate_update_schema_jsonnet

if TYPE_CHECKING:
    from .artifact_engine import ArtifactEngine
    from .rae_engine import RaeEngine
    from .workspace import PantheonWorkspace


class CreatedFileType(Enum):
    """Enumeration of file types that can be created by processes."""

    ROUTINE = "routine"
    SCHEMA = "schema"
    TEMPLATE = "template"
    ARTIFACT = "artifact"
    PERMISSIONS = "permissions"
    LOCATOR = "locator"
    PARSER = "parser"
    SECTIONS = "sections"
    TARGET = "target"
    PATCH = "patch"
    JSONL = "jsonl"


# Type definitions as per interface contracts
class ProcessInput(TypedDict):
    process: str
    actor: str
    input_params: dict[str, Any]
    framework_params: dict[str, Any]


class ProcessResult(TypedDict):
    success: bool
    output: str | None
    error: str | None
    files_created: list[dict[str, str]] | None


ProcessType = Literal["create", "update", "get", "build"]


def normalize_framework_key(key: str) -> str | None:
    """Return the canonical framework parameter key if the name is reserved."""

    canonical = FRAMEWORK_PARAMETER_SYNONYMS.get(key)
    if canonical:
        return canonical
    if key in FRAMEWORK_PARAMETERS:
        return key
    return None


def is_framework_parameter(key: str) -> bool:
    """Check if the provided key corresponds to a framework-reserved parameter."""

    return normalize_framework_key(key) is not None


def coerce_framework_value(key: str, value: Any) -> Any:
    """Normalize framework parameter values into canonical forms."""

    if key == PARAM_SECTIONS:
        if isinstance(value, str):
            return [section.strip() for section in value.split(",") if section.strip()]
        if isinstance(value, list):
            return value
    return value


def _sanitize_input_parameters(
    input_params: dict[str, Any], framework_params: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Remove reserved framework keys from input parameters.

    Any reserved keys encountered are moved into the provided framework
    parameters dictionary using their canonical names.
    """

    cleaned: dict[str, Any] = {}
    for key, value in input_params.items():
        canonical = normalize_framework_key(key)
        if canonical:
            framework_params[canonical] = coerce_framework_value(canonical, value)
            continue
        cleaned[key] = value
    return cleaned, framework_params


# BUILD spec keys and defaults
BUILD_KEY_TARGET_TEAM = "target_team"
BUILD_KEY_ARTIFACT = "artifact"
BUILD_KEY_CONTEXT = "context"
BUILD_KEY_SECTIONS = "artifact_sections"
BUILD_KEY_INITIAL_SECTION = "initial_section"
BUILD_KEY_SECTION_TEMPLATE = "section_template"
BUILD_KEY_ARTIFACT_LOCATION = "artifact_location"
BUILD_KEY_PERMISSIONS = "permissions"
BUILD_KEY_BUILD_MODE = "build_mode"
BUILD_KEY_INCLUDE_CONTEXT = "include_context"

# JSON Schema keys
SCHEMA_KEY_PROPERTIES = "properties"

DEFAULT_BUILD_OUTPUT_DIR_NAME = "pantheon-team-builds"

SECTION_START_CONTEXT = "<!-- SECTION:START:CONTEXT -->"
SECTION_END_CONTEXT = "<!-- SECTION:END:CONTEXT -->"
CONTEXT_SECTION_DESCRIPTION = "Context captured during the initial planning flow."
PLACEHOLDER_MARKER = "<!-- SECTION:PLACEHOLDER -->"

# Success message template and operation types
SUCCESS_MESSAGE_TEMPLATE = "{process_name} completed successfully. All verifications complete. Operation: {operation_type}."
OPERATION_CREATE = "CREATE"
OPERATION_UPDATE = "UPDATE"
OPERATION_BUILD = "BUILD"
OPERATION_GET = "GET"

# Error type prefixes (reused in format_error)
ERROR_PREFIX_FILE_NOT_FOUND = "File not found"
ERROR_PREFIX_PERMISSION_DENIED = "Permission denied"
ERROR_PREFIX_INVALID_INPUT = "Invalid input"


@dataclass(frozen=True)
class _BuildContext:
    """Immutable context for BUILD process execution.

    Single source of truth for all BUILD execution state,
    making testing and debugging straightforward.
    """

    process_name: str
    target_team: str
    artifact: str
    sections: list[str]
    initial_section: str
    section_defs: dict[str, dict[str, Any]]  # per-section template, schema, metadata
    placement: str
    naming: str
    permissions: dict[str, Any]
    bundle_root: PantheonPath
    create_proc: str
    get_proc: str

    def __post_init__(self) -> None:
        """Validate context invariants."""
        if self.initial_section not in self.sections:
            raise ValueError(
                f"Initial section '{self.initial_section}' not in sections list: {self.sections}"
            )

    def _marker_name(self, name: str) -> str:
        """Convert section name to marker format."""
        return name.upper().replace(" ", "_").replace("-", "_")

    def _process_name(self, name: str) -> str:
        """Convert section name to process name."""
        return name.lower().replace(" & ", "_").replace(" ", "_").replace("-", "_")


class ProcessHandler:
    """Central orchestrator for process execution in the Pantheon Framework.

    The ProcessHandler coordinates specialist components (Workspace, ArtifactEngine)
    to execute both Read and Write processes. It contains the core business logic
    for process execution, implementing the Unified Execute Model that determines
    process behavior through convention.

    This class serves as the Application Layer orchestrator between the Presentation
    layer (CLI) and Service layer components (Workspace, ArtifactEngine).
    """

    def __init__(
        self,
        workspace: PantheonWorkspace,
        artifact_engine: ArtifactEngine,
        rae_engine: RaeEngine,
    ) -> None:
        """Initialize ProcessHandler with specialist components.

        Args:
            workspace: Filesystem facade for I/O operations and path management
            artifact_engine: Pure computation engine for artifact generation
            rae_engine: Retrieval-Augmented Execution engine for routine management
        """
        self._workspace = workspace
        self._artifact_engine = artifact_engine
        self._rae_engine = rae_engine

    def get_sections_metadata(self, process_name: str) -> list[dict[str, str]]:
        """Return section metadata using the process's section configuration.

        Supports both UPDATE processes (target.jsonnet) and RETRIEVE/GET processes
        (sections.jsonnet). Both file types define section metadata with the same structure.

        Args:
            process_name: Name of the process to get section metadata for

        Returns:
            List of dictionaries with 'name' and 'description' keys for each section

        Raises:
            ValueError: If neither target.jsonnet nor sections.jsonnet exists,
                       or if the configuration format is invalid
        """

        # Try target.jsonnet first (UPDATE processes)
        sections_content = None
        source_file = None

        try:
            sections_content = self._workspace.get_artifact_target_section(process_name)
            source_file = "target.jsonnet"
        except FileNotFoundError:
            # Fall back to sections.jsonnet (RETRIEVE/GET processes)
            try:
                sections_content = self._workspace.get_artifact_section_markers(
                    process_name
                )
                source_file = "sections.jsonnet"
            except FileNotFoundError as exc:
                raise ValueError(
                    f"Process '{process_name}' does not define section metadata. "
                    f"Expected either target.jsonnet (UPDATE) or sections.jsonnet (RETRIEVE/GET)"
                ) from exc

        try:
            sections_config = json.loads(sections_content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Failed to parse {source_file} for '{process_name}': {exc}"
            ) from exc

        if not isinstance(sections_config, dict):
            raise ValueError(
                f"Section configuration in {source_file} for '{process_name}' must be a JSON object"
            )

        sections_obj = sections_config.get("sections")
        if not isinstance(sections_obj, dict) or not sections_obj:
            raise ValueError(
                f"Section configuration in {source_file} for '{process_name}' does not define any sections"
            )

        results: list[dict[str, str]] = []
        for name, details in sections_obj.items():
            description = ""
            if isinstance(details, dict):
                desc_value = details.get("description")
                if isinstance(desc_value, str):
                    description = desc_value
            results.append({"name": name, "description": description})

        return results

    def get_team_data(self, actor: str, key: str | None = None) -> str:
        """Get team data from team-data.yaml with Jinja2 template rendering.

        Orchestrates the process of retrieving team data: reads raw content,
        renders it as a Jinja2 template with framework parameters, parses YAML,
        and optionally filters by key.

        Args:
            actor: Actor requesting the data (used for template context)
            key: Optional key to filter (dot notation supported)

        Returns:
            YAML-formatted team data (filtered if key specified)

        Raises:
            FileNotFoundError: If team-data.yaml doesn't exist
            ValueError: If template rendering or YAML parsing fails
        """
        # Step 1: Get raw content from Workspace (pure I/O)
        raw_content = self._workspace.get_team_data()

        # Step 2: Build framework parameters for template context (reuse existing logic)
        context = self._build_framework_context(actor)

        # Step 3: Render template using Artifact Engine (pure computation)
        try:
            rendered_content = self._artifact_engine.render_template(
                raw_content, context, "team-data.yaml"
            )
        except Exception as e:
            raise ValueError(
                f"Template rendering failed for team-data.yaml: {e}"
            ) from e

        # Step 4: Parse rendered YAML
        try:
            data = yaml.safe_load(rendered_content) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in team-data.yaml: {e}") from e

        # Step 5: Filter by key if specified
        if key:
            try:
                filtered_data = self._workspace._get_nested_value(data, key)
                # For scalar values, convert to string representation
                if isinstance(filtered_data, str | int | float | bool):
                    return str(filtered_data)
                # For complex objects, return as YAML
                return yaml.dump(filtered_data, default_flow_style=False).strip()
            except KeyError:
                # Return empty string for non-existent keys
                return ""

        return yaml.dump(data, default_flow_style=False).strip()

    def _build_framework_context(self, actor: str) -> dict[str, Any]:
        """Build framework parameter context for template rendering.

        Extracted from _build_enhanced_parameters to avoid duplication.
        This method builds the minimal framework context needed for template rendering.

        Args:
            actor: Actor name for template context

        Returns:
            Dictionary with framework parameters for template rendering
        """
        import yaml

        from pantheon.constants import (
            BUILTIN_ACTIVE_PROFILE,
            BUILTIN_ARTIFACTS_ROOT,
            BUILTIN_FULL_PROFILE,
            BUILTIN_PROJECT_ROOT,
        )

        context = {
            BUILTIN_ACTOR: actor,
            BUILTIN_TIMESTAMP: self._artifact_engine._generate_timestamp(),
            BUILTIN_DATESTAMP: self._artifact_engine._generate_datestamp(),
            BUILTIN_PROJECT_ROOT: str(self._workspace._project_root),
            BUILTIN_ARTIFACTS_ROOT: str(self._workspace._artifacts_root),
        }

        # Add profile context if available (same logic as _build_enhanced_parameters)
        try:
            profile_content = self._workspace.get_team_profile()
            profile_data = yaml.safe_load(profile_content)

            # Store full profile structure
            context[BUILTIN_FULL_PROFILE] = profile_data or {}

            # Extract and store active profile configuration
            if (
                profile_data
                and "active_profile" in profile_data
                and "profiles" in profile_data
            ):
                active_profile_name = profile_data["active_profile"]
                profiles = profile_data["profiles"]
                if isinstance(profiles, dict) and active_profile_name in profiles:
                    context[BUILTIN_ACTIVE_PROFILE] = profiles[active_profile_name]
                else:
                    context[BUILTIN_ACTIVE_PROFILE] = {}
            else:
                context[BUILTIN_ACTIVE_PROFILE] = {}
        except Exception:
            # Profile not available or error reading - continue without it
            context[BUILTIN_ACTIVE_PROFILE] = {}
            context[BUILTIN_FULL_PROFILE] = {}

        return context

    def execute(
        self,
        input_data: ProcessInput,
        _redirect_chain: set[str] | None = None,
    ) -> ProcessResult:
        """Execute a process by orchestrating all specialist components.

        This is the primary orchestration method that handles both Read and Write
        processes. It determines the process type by convention, validates input
        data, and coordinates the complete execution workflow. Also handles
        process redirection when redirect.md files are present.

        Args:
            input_data: Input data dictionary containing process, actor, and parameters
            _redirect_chain: Internal parameter for redirect chain tracking (not part of public API)

        Returns:
            ProcessResult containing success status, output, error, and artifact_created

        Raises:
            ValueError: If input data validation fails
        """
        process_name = input_data[INPUT_PROCESS]
        Log.debug(
            f"Executing process '{process_name}' for actor '{input_data.get(INPUT_ACTOR, 'unknown')}'"
        )

        try:
            # Validate input structure
            if not self.validate_input(process_name, input_data):
                Log.warning(f"Input validation failed for process '{process_name}'")
                return {
                    RESULT_SUCCESS: False,
                    RESULT_OUTPUT: None,
                    RESULT_ERROR: "Invalid input structure",
                    RESULT_FILES_CREATED: None,
                }

            # Unpack input and framework parameters
            actor = input_data[INPUT_ACTOR]
            raw_input_params = input_data[INPUT_INPUT_PARAMS]
            raw_framework_params = input_data[INPUT_FRAMEWORK_PARAMS]

            input_params, framework_params = self._build_enhanced_parameters(
                process_name, actor, raw_input_params, raw_framework_params
            )

            # Check for redirect before determining process type
            process_name = input_data[INPUT_PROCESS]
            if self._workspace.has_process_redirect(process_name):
                Log.debug(f"Process '{process_name}' has redirect configuration")
                processed_input_data = {
                    INPUT_PROCESS: process_name,
                    INPUT_ACTOR: actor,
                    INPUT_INPUT_PARAMS: input_params,
                    INPUT_FRAMEWORK_PARAMS: framework_params,
                }
                return self._handle_redirect_internal(
                    process_name, processed_input_data, _redirect_chain or set()
                )
            # Determine process type and load initial templates efficiently
            process_type, templates = self.determine_process_type(process_name)
            Log.debug(f"Process '{process_name}' determined as type: {process_type}")

            # Validate that insert-mode is only used with UPDATE processes
            insert_mode = framework_params.get(BUILTIN_INSERT_MODE)
            if insert_mode and process_type != PROCESS_TYPE_UPDATE:
                return {
                    RESULT_SUCCESS: False,
                    RESULT_OUTPUT: None,
                    RESULT_ERROR: "--insert-mode is only supported for UPDATE processes",
                    RESULT_FILES_CREATED: None,
                }

            if process_type == PROCESS_TYPE_CREATE:
                result = self.execute_create_process(
                    input_params, framework_params, templates
                )
            elif process_type == PROCESS_TYPE_UPDATE:
                result = self.execute_update_process(
                    input_params, framework_params, templates
                )
            elif process_type == PROCESS_TYPE_BUILD:
                result = self.execute_build_process(input_params, framework_params)
            else:  # PROCESS_TYPE_GET
                result = self.execute_get_process(input_params, framework_params)

            if result[RESULT_SUCCESS]:
                ## use debug log here as each create/update/build process already reports its own success message, and we want to keep GET clean with data only output
                Log.debug(f"Process '{process_name}' completed successfully")
            else:
                Log.error(
                    f"Process '{process_name}' failed: {result.get(RESULT_ERROR, 'Unknown error')}"
                )

            return result

        except Exception as e:
            Log.error(f"Exception during process '{process_name}' execution: {e}")
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: self.format_error(type(e).__name__, str(e)),
                RESULT_FILES_CREATED: None,
            }

    def _build_enhanced_parameters(
        self,
        process_name: str,
        actor: str,
        input_params: dict[str, Any],
        framework_params: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Prepare clean input parameters and framework parameters."""

        # Start with canonical framework parameters
        prepared_framework: dict[str, Any] = {}
        for key, value in framework_params.items():
            canonical = normalize_framework_key(key)
            if canonical:
                prepared_framework[canonical] = coerce_framework_value(canonical, value)
            else:
                prepared_framework[key] = value

        # Add process name (not included in _build_framework_context)
        prepared_framework[BUILTIN_PROCESS] = process_name

        # Remove any reserved keys accidentally left in input parameters
        sanitized_input, prepared_framework = _sanitize_input_parameters(
            dict(input_params), prepared_framework
        )

        # Build base framework context (actor, timestamp, datestamp, profile)
        # This reuses the logic from _build_framework_context
        base_context = self._build_framework_context(actor)

        # Merge base context into prepared framework
        # Note: prepared_framework may already have some values from user input,
        # but base_context provides the canonical framework values
        prepared_framework.update(base_context)

        return sanitized_input, prepared_framework

    def _handle_redirect_internal(
        self,
        process_name: str,
        input_data: ProcessInput,
        redirect_chain: set[str],
    ) -> ProcessResult:
        """Internal method to handle process redirection with circular redirect detection.

        Args:
            process_name: Name of the current process with redirect
            input_data: Original input data with user parameters
            redirect_chain: Set of processes in current redirect chain

        Returns:
            ProcessResult from executing the target process
        """
        # Check for circular redirect
        if process_name in redirect_chain:
            error_msg = f"Circular redirect detected: {' -> '.join(sorted(redirect_chain))} -> {process_name}"
            Log.error(error_msg)
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: error_msg,
                RESULT_FILES_CREATED: None,
            }

        # Add current process to redirect chain
        new_redirect_chain = redirect_chain.copy()
        new_redirect_chain.add(process_name)

        try:
            # Get redirect URI
            redirect_uri = self._workspace.get_process_redirect(process_name)
            Log.debug(f"Process '{process_name}' redirecting to: {redirect_uri}")

            # Parse redirect URI to extract target process and parameters
            target_process, redirect_params = parse_process_uri(redirect_uri)
            Log.debug(
                f"Parsed redirect - target: '{target_process}', params: {redirect_params}"
            )

            # Merge user and framework parameters with redirect overrides
            combined_params: dict[str, Any] = {
                **input_data[INPUT_INPUT_PARAMS],
                **input_data[INPUT_FRAMEWORK_PARAMS],
            }
            merged_params = merge_parameters(combined_params, redirect_params)
            Log.debug(f"Merged parameters: {merged_params}")

            input_params, framework_params = self._build_enhanced_parameters(
                target_process,
                input_data[INPUT_ACTOR],
                merged_params,
                dict(input_data[INPUT_FRAMEWORK_PARAMS]),
            )

            target_input_data: ProcessInput = {
                INPUT_PROCESS: target_process,
                INPUT_ACTOR: input_data[INPUT_ACTOR],
                INPUT_INPUT_PARAMS: input_params,
                INPUT_FRAMEWORK_PARAMS: framework_params,
            }

            # Recursively execute target process with redirect chain tracking
            return self.execute(target_input_data, new_redirect_chain)

        except ValueError as e:
            # Handle invalid redirect URI
            error_msg = f"Invalid redirect URI in process '{process_name}': {e}"
            Log.error(error_msg)
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: error_msg,
                RESULT_FILES_CREATED: None,
            }
        except FileNotFoundError as e:
            # Handle missing redirect file (shouldn't happen if has_process_redirect returned True)
            error_msg = f"Redirect file not found for process '{process_name}': {e}"
            Log.error(error_msg)
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: error_msg,
                RESULT_FILES_CREATED: None,
            }
        except Exception as e:
            # Handle any other redirect-related errors
            error_msg = f"Redirect handling failed for process '{process_name}': {e}"
            Log.error(error_msg)
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: error_msg,
                RESULT_FILES_CREATED: None,
            }

    def handle_redirect(
        self,
        process_name: str,
        input_data: ProcessInput,
        redirect_chain: set[str] | None = None,
    ) -> ProcessResult:
        """Handle process redirection with circular redirect detection.

        This method delegates to the internal redirect handler with proper
        initialization of the redirect chain.

        Args:
            process_name: Name of the current process with redirect
            input_data: Original input data with user parameters
            redirect_chain: Set of processes in current redirect chain

        Returns:
            ProcessResult from executing the target process
        """
        return self._handle_redirect_internal(
            process_name, input_data, redirect_chain or set()
        )

    def determine_process_type(
        self, process_name: str
    ) -> tuple[ProcessType, dict[str, str]]:
        """Determine process operation type and load initial templates efficiently.

        Uses the new operation-specific file naming conventions to determine whether
        a process is UPDATE, BUILD, CREATE or GET based on (in precedence order):
        - UPDATE: patch.md (plus RETRIEVE files + target.jsonnet)
        - BUILD: build-schema.jsonnet present at process root
        - CREATE: content.md + placement.jinja + naming.jinja
        - RETRIEVE/GET: locator.jsonnet + parser.jsonnet + sections.jsonnet

        Args:
            process_name: Name of the process to check

        Returns:
            Tuple of (ProcessType, templates_dict) where templates_dict contains
            the initially loaded template content to avoid double loading

        Raises:
            FileNotFoundError: If the specified process doesn't exist
        """
        # Verify process exists first - routine file is required for all processes
        self._workspace.get_process_routine(process_name)

        templates = {}

        # Check for CREATE operation first (original behavior)
        try:
            content = self._workspace.get_artifact_content_template(process_name)
            templates["content"] = content
            return PROCESS_TYPE_CREATE, templates
        except FileNotFoundError:
            pass

        # Check for UPDATE operation next
        try:
            patch = self._workspace.get_artifact_patch_template(process_name)
            templates["patch"] = patch
            return PROCESS_TYPE_UPDATE, templates
        except FileNotFoundError:
            pass

        # Check for BUILD operation (explicit True)
        try:
            if self._workspace.has_build_schema(process_name) is True:
                return PROCESS_TYPE_BUILD, templates
        except Exception:
            pass

        # Neither content.md nor patch.md nor build-schema exists, default GET
        return PROCESS_TYPE_GET, templates  # RETRIEVE maps to READ

    def get_routine(
        self,
        process_name: str,
        actor: str,
        sections: str | Sequence[str] | None = None,
    ) -> str:
        """Retrieve routine content with optional section filtering."""

        requested_sections = self._normalize_sections_option(sections)

        process_type, _ = self.determine_process_type(process_name)
        if requested_sections and process_type != PROCESS_TYPE_UPDATE:
            raise ValueError("--sections is only supported for UPDATE processes")

        input_params: dict[str, Any] = {}
        framework_params: dict[str, Any] = {}
        if requested_sections:
            framework_params[PARAM_SECTIONS] = requested_sections

        sanitized_input, prepared_framework = self._build_enhanced_parameters(
            process_name, actor, input_params, framework_params
        )

        return self._rae_engine.get_routine(
            process_name,
            sanitized_input,
            prepared_framework,
            process_type=process_type,
        )

    def compose_schema(
        self,
        process_name: str,
        actor: str,
        sections: str | Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Compose process schema with optional section filtering."""

        _ = actor  # Actor reserved for future schema personalization hooks.

        requested_sections = self._normalize_sections_option(sections)

        process_type, _ = self.determine_process_type(process_name)

        if requested_sections and process_type != PROCESS_TYPE_UPDATE:
            raise ValueError("--sections is only supported for UPDATE processes")

        compiled_schema = self._compile_process_schema(process_name)

        if process_type != PROCESS_TYPE_UPDATE or not requested_sections:
            return compiled_schema

        _, section_properties, section_order = self._get_update_schema_metadata(
            process_name, compiled_schema
        )

        missing = [
            name for name in requested_sections if name not in section_properties
        ]
        if missing:
            raise ValueError(
                f"Unknown section(s) for process '{process_name}': {', '.join(missing)}"
            )

        filtered_schema = deepcopy(compiled_schema)
        # Use section_updates instead of sections (sections is reserved by CLI)
        filtered_props = (
            filtered_schema.setdefault("properties", {})
            .setdefault("section_updates", {})
            .setdefault("properties", {})
        )
        filtered_props.clear()
        for name in requested_sections:
            filtered_props[name] = section_properties[name]

        default_order = (
            filtered_schema.get("properties", {})
            .get("section_order", {})
            .get("default", [])
        )
        if isinstance(default_order, list) and default_order:
            canonical_set = set(requested_sections)
            filtered_order = [name for name in section_order if name in canonical_set]
        else:
            filtered_order = list(requested_sections)

        section_order_node = filtered_schema.setdefault("properties", {}).setdefault(
            "section_order", {}
        )
        section_order_node["default"] = filtered_order

        return filtered_schema

    def _normalize_sections_option(
        self, sections: str | Sequence[str] | None
    ) -> list[str]:
        """Normalize sections input into a deduplicated list."""

        if sections is None:
            return []

        parsed: Any = sections
        if isinstance(sections, str):
            parsed = sections

        parsed = coerce_framework_value(PARAM_SECTIONS, parsed)

        if isinstance(parsed, str):
            parsed = [parsed]

        if not isinstance(parsed, list):
            raise ValueError("Sections parameter must be a comma-separated list")

        normalized: list[str] = []
        for entry in parsed:
            if not isinstance(entry, str):
                raise ValueError("Sections parameter must contain string values")
            cleaned = entry.strip()
            if cleaned and cleaned not in normalized:
                normalized.append(cleaned)
        return normalized

    def _compile_process_schema(self, process_name: str) -> dict[str, Any]:
        """Compile Jsonnet schema for the given process into JSON Schema."""

        try:
            schema_content = self._workspace.get_process_schema(process_name)
        except Exception as exc:
            raise ValueError(
                f"Schema not found for process '{process_name}': {exc}"
            ) from exc

        profile_data = self._load_profile_content()

        try:
            return self._artifact_engine.compile_schema(
                schema_content, profile_data, process_name
            )
        except Exception as exc:
            raise ValueError(
                f"Failed to compile schema for process '{process_name}': {exc}"
            ) from exc

    def _load_profile_content(self) -> dict[str, Any]:
        """Load and parse the active team profile content."""

        try:
            profile_content = self._workspace.get_team_profile()
        except Exception as exc:
            raise ValueError(f"Failed to load team profile: {exc}") from exc

        if not profile_content:
            return {}

        try:
            parsed_profile = yaml.safe_load(profile_content) or {}
        except yaml.YAMLError as exc:
            raise ValueError(f"Failed to parse profile YAML content: {exc}") from exc

        if not isinstance(parsed_profile, dict):
            raise ValueError("Profile content must be a YAML object")

        return parsed_profile

    def _get_update_schema_metadata(
        self,
        process_name: str,
        compiled_schema: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
        """Return compiled schema, section map, and canonical section order."""

        if compiled_schema is None:
            compiled_schema = self._compile_process_schema(process_name)

        properties = compiled_schema.get("properties", {})
        if not isinstance(properties, dict):
            raise ValueError(
                f"Schema for process '{process_name}' is missing properties"
            )

        # Look for section_updates instead of sections (sections is reserved by CLI)
        sections_node = properties.get("section_updates", {})
        if not isinstance(sections_node, dict):
            raise ValueError(
                f"Schema for process '{process_name}' is missing section_updates metadata"
            )

        section_properties = sections_node.get("properties", {})
        if not isinstance(section_properties, dict):
            raise ValueError(
                f"Schema for process '{process_name}' does not define section_updates properties"
            )

        section_order_default = properties.get("section_order", {})
        if isinstance(section_order_default, dict):
            default_value = section_order_default.get("default", [])
            section_order = (
                list(default_value) if isinstance(default_value, list) else []
            )
        else:
            section_order = []

        if not section_order:
            section_order = list(section_properties.keys())

        return compiled_schema, section_properties, section_order

    def validate_input(self, process_name: str, input_data: ProcessInput) -> bool:
        """Validate input data against ProcessInput structure requirements.

        Args:
            process_name: Name of the process to validate
            input_data: Input data to validate

        Returns:
            True if validation passes

        Raises:
            ValueError: If input data doesn't match required structure
        """
        if not isinstance(process_name, str) or not process_name:
            raise ValueError("Process name must be a non-empty string")

        if not isinstance(input_data, dict):
            raise ValueError("Process input must be a dictionary")

        required_keys = {
            INPUT_PROCESS,
            INPUT_ACTOR,
            INPUT_INPUT_PARAMS,
            INPUT_FRAMEWORK_PARAMS,
        }
        if not all(key in input_data for key in required_keys):
            missing_keys = required_keys - set(input_data.keys())
            raise ValueError(f"Missing required keys: {missing_keys}")

        if (
            not isinstance(input_data[INPUT_PROCESS], str)
            or not input_data[INPUT_PROCESS]
        ):
            raise ValueError("Process name must be a non-empty string")

        if not isinstance(input_data[INPUT_ACTOR], str) or not input_data[INPUT_ACTOR]:
            raise ValueError("Actor name must be a non-empty string")

        if not isinstance(input_data[INPUT_INPUT_PARAMS], dict):
            raise ValueError("input_params must be a dictionary")

        if not isinstance(input_data[INPUT_FRAMEWORK_PARAMS], dict):
            raise ValueError("framework_params must be a dictionary")

        return True

    def execute_get_process(
        self, input_params: dict[str, Any], framework_params: dict[str, Any]
    ) -> ProcessResult:
        """Execute a GET process that retrieves existing artifacts.

        Supports two modes:
        - Multi-artifact mode (with parser.jsonnet): Requires artifact_id to locate specific artifact
        - Singleton mode (no parser.jsonnet): Optional artifact_id, expects exactly one artifact

        Args:
            input_params: Clean input parameters for validation and YAML generation
            framework_params: Built-in framework variables

        Returns:
            ProcessResult containing the retrieved JSON data

        Raises:
            FileNotFoundError: If required artifacts don't exist
        """
        # Extract process_name, artifact_id and sections from parameters
        # Apply reserved sections parsing here to avoid clobbering build-spec keys elsewhere
        process_name = framework_params[BUILTIN_PROCESS]
        artifact_id = framework_params.get(
            BUILTIN_ARTIFACT_ID
        )  # None if not provided (singleton mode)
        section_names = framework_params.get(PARAM_SECTIONS, [])

        Log.debug(
            f"GET process '{process_name}': artifact_id='{artifact_id}', sections={section_names}"
        )
        Log.debug(f"Input parameters: {input_params}")
        Log.debug(f"Framework parameters: {framework_params}")

        # Use ArtifactEngine to find and retrieve artifact sections
        # ArtifactEngine.find_artifact() handles both multi-artifact and singleton modes
        Log.debug(f"Searching for artifact with ID: '{artifact_id}'")
        artifact_path = self._artifact_engine.find_artifact(process_name, artifact_id)

        if artifact_path is None:
            # Provide mode-appropriate error message
            if artifact_id:
                error_msg = f"Artifact not found: {artifact_id}"
            else:
                error_msg = f"Artifact not found for singleton process '{process_name}'"

            Log.debug(
                f"Artifact not found for ID '{artifact_id}' in process '{process_name}'"
            )
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: error_msg,
                RESULT_FILES_CREATED: None,
            }

        Log.debug(f"Found artifact at path: {artifact_path}")

        sections_data = self._artifact_engine.get_artifact_sections(
            process_name, artifact_path, section_names
        )

        Log.debug(f"Extracted sections data: {sections_data}")

        # Convert to formatted JSON for output
        import json

        json_output = json.dumps(sections_data, indent=2)

        # do not output any info message to keep output clean for GET operations

        return {
            RESULT_SUCCESS: True,
            RESULT_OUTPUT: json_output,
            RESULT_ERROR: None,
            RESULT_FILES_CREATED: None,  # GET operations don't create files
        }

    def _validate_input_and_compile_schema(
        self,
        process_name: str,
        input_params: dict[str, Any],
        framework_params: dict[str, Any],
    ) -> tuple[bool, dict[str, Any] | None, str | None]:
        """Shared helper for schema validation used by CREATE and UPDATE operations.

        Args:
            process_name: Name of the process to execute
            input_params: Input parameters to validate
            framework_params: Framework parameters containing profile data

        Returns:
            Tuple of (success, compiled_schema_or_None, error_message_or_None)
        """
        # Get schema for validation
        schema_content = self._workspace.get_process_schema(process_name)

        # Get full profile structure from framework parameters
        full_profile = framework_params.get(BUILTIN_FULL_PROFILE, {})

        # Compile schema with profile context
        compiled_schema = self._artifact_engine.compile_schema(
            schema_content, full_profile, process_name
        )

        # Validate input data against schema with detailed error handling
        try:
            self._artifact_engine.validate(input_params, compiled_schema)
        except ValueError as e:
            # Catch detailed validation errors from the enhanced validate method
            detailed_error = str(e)
            Log.error(
                f"Schema validation failed for process '{process_name}': {detailed_error}"
            )
            return False, None, detailed_error
        except Exception as e:
            # Catch any other validation-related errors
            error_msg = f"Validation failed due to unexpected error: {str(e)}"
            Log.error(
                f"Unexpected validation error for process '{process_name}': {error_msg}"
            )
            return False, None, error_msg

        return True, compiled_schema, None

    def execute_build_process(
        self, input_params: dict[str, Any], framework_params: dict[str, Any]
    ) -> ProcessResult:
        """Execute a BUILD process that scaffolds a process family bundle.

        Validates the input build-spec, then generates a staged bundle of
        CREATE/GET/UPDATE processes under the artifacts sandbox.

        Args:
            input_params: Clean input parameters for validation and YAML generation
            framework_params: Built-in framework variables
        """
        process_name = framework_params[BUILTIN_PROCESS]

        # Phase 1: Initialize and validate build context
        success, ctx, compiled_schema, error_message, build_mode = (
            self._build_init_context(process_name, input_params, framework_params)
        )
        if not success:
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: error_message,
                RESULT_FILES_CREATED: None,
            }

        # Phase 2: Scaffold CREATE process
        try:
            create_paths = self._build_scaffold_create(
                ctx, input_params, framework_params, build_mode
            )
        except Exception as e:
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: f"Failed to scaffold CREATE process: {e}",
                RESULT_FILES_CREATED: None,
            }

        # Phase 3: Scaffold GET process
        try:
            get_paths = self._build_scaffold_get(ctx, input_params, framework_params)
        except Exception as e:
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: f"Failed to scaffold GET process: {e}",
                RESULT_FILES_CREATED: None,
            }

        # Phase 4: Scaffold UPDATE processes
        try:
            update_paths, update_processes = self._build_scaffold_updates(
                ctx, input_params, framework_params, compiled_schema
            )
        except Exception as e:
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: f"Failed to scaffold UPDATE processes: {e}",
                RESULT_FILES_CREATED: None,
            }

        # Phase 5: Collect all created files and generate standardized output
        all_created_paths = create_paths + get_paths + update_paths
        files_info = self._workspace.summarize_created_files(all_created_paths)

        # Generate standardized success message
        output = SUCCESS_MESSAGE_TEMPLATE.format(
            process_name=process_name, operation_type=OPERATION_BUILD
        )

        return {
            RESULT_SUCCESS: True,
            RESULT_OUTPUT: output,
            RESULT_ERROR: None,
            RESULT_FILES_CREATED: files_info,
        }

    def _build_init_context(
        self,
        process_name: str,
        input_params: dict[str, Any],
        framework_params: dict[str, Any],
    ) -> tuple[
        bool, _BuildContext | None, dict[str, Any] | None, str | None, str | None
    ]:
        """Initialize and validate BUILD context.

        Args:
            process_name: Name of the BUILD process
            input_params: Clean input parameters for validation and YAML generation
            framework_params: Built-in framework variables

        Returns:
            Tuple of (success, build_context_or_none, compiled_schema_or_none, error_message_or_none, build_mode_or_none)
        """
        # For BUILD processes, use input_params directly since "artifact_sections"
        # is now a regular business parameter (not reserved by framework)
        user_parameters = input_params.copy()

        # Validate schema
        (
            success,
            compiled_schema,
            error_message,
        ) = self._validate_input_and_compile_schema(
            process_name, user_parameters, framework_params
        )
        if not success:
            return False, None, None, error_message, None

        # Extract and validate required build-spec fields
        try:
            target_team: str = user_parameters[BUILD_KEY_TARGET_TEAM]
            artifact: str = user_parameters[BUILD_KEY_ARTIFACT]
            build_mode: str = user_parameters[BUILD_KEY_BUILD_MODE]
            sections: list[str] = list(user_parameters.get(BUILD_KEY_SECTIONS, []))
            initial_section: str = user_parameters[BUILD_KEY_INITIAL_SECTION]
            section_templates_list: list[dict[str, Any]] = list(
                user_parameters.get(BUILD_KEY_SECTION_TEMPLATE, [])
            )
            artifact_location: dict[str, Any] = user_parameters[
                BUILD_KEY_ARTIFACT_LOCATION
            ]
            permissions: dict[str, Any] = user_parameters.get(BUILD_KEY_PERMISSIONS, {})
            include_context: bool = user_parameters[BUILD_KEY_INCLUDE_CONTEXT]
        except Exception as e:
            return False, None, None, f"Invalid build-spec structure: {e}", None

        # Validate build_mode has valid value
        valid_build_modes = ["complete", "modular"]
        if build_mode not in valid_build_modes:
            return (
                False,
                None,
                None,
                f"Invalid build_mode value: '{build_mode}'. Valid values are: {', '.join(valid_build_modes)}",
                None,
            )

        # Build section_defs from user-provided section templates
        # Compile each schema to ensure proper JSON Schema structure
        section_defs: dict[str, dict[str, Any]] = {}
        for entry in section_templates_list:
            name = entry.get("section")
            if not name:
                continue

            description_raw = entry.get("section_description")
            if description_raw is None:
                return (
                    False,
                    None,
                    None,
                    f"Section definition for '{name}' is missing required 'section_description' field",
                    None,
                )
            description = str(description_raw).strip()
            if not description:
                return (
                    False,
                    None,
                    None,
                    f"Section definition for '{name}' must provide a non-empty 'section_description'",
                    None,
                )

            # Get raw schema and compile it to ensure proper structure
            raw_schema = entry.get("schema", {})
            try:
                import json

                # Convert schema dict to JSON string for compilation
                schema_json_str = json.dumps(raw_schema, indent=2)
                # Get full profile structure from framework parameters for schema compilation
                full_profile = framework_params.get(BUILTIN_FULL_PROFILE, {})
                # Compile using ArtifactEngine to get sanitized, validated schema
                compiled_section_schema = self._artifact_engine.compile_schema(
                    schema_json_str,
                    full_profile,
                    process_name,
                    include_schema_metadata=False,
                )

                section_defs[name] = {
                    "template": entry.get("template", ""),
                    "schema": compiled_section_schema,
                    "description": description,
                }
                Log.debug(f"Compiled schema for section '{name}'")
            except Exception as e:
                return (
                    False,
                    None,
                    None,
                    f"Failed to compile schema for section '{name}': {e}",
                    None,
                )

        # Conditionally inject context section based on include_context flag
        if include_context:
            try:
                context_schema_content = self._workspace.get_context_schema(
                    process_name
                )
                context_template_content = self._workspace.get_context_template(
                    process_name
                )

                # Get full profile structure from framework parameters for schema compilation
                full_profile = framework_params.get(BUILTIN_FULL_PROFILE, {})
                # Compile the context schema using ArtifactEngine to ensure proper structure
                compiled_context_schema = self._artifact_engine.compile_schema(
                    context_schema_content,
                    full_profile,
                    process_name,
                    include_schema_metadata=False,
                )

                # Inject "context" as the second section after initial section
                sections.insert(1, BUILD_KEY_CONTEXT)

                # Inject context section definition with compiled schema
                section_defs[BUILD_KEY_CONTEXT] = {
                    "template": context_template_content,
                    "schema": compiled_context_schema,
                    "description": CONTEXT_SECTION_DESCRIPTION,
                }
                Log.debug("Compiled and injected context section schema")

            except Exception as e:
                return False, None, None, f"Failed to inject context section: {e}", None
        else:
            Log.debug("Skipping context section injection (include_context=false)")

        # Resolve output bundle root from directory.jinja at process root
        try:
            dir_tpl = self._workspace.get_process_directory_template(process_name)
            template_ctx = self._artifact_engine._create_template_context(
                input_params, framework_params, None
            )
            bundle_dir = self._artifact_engine.render_template(
                dir_tpl, template_ctx
            ).strip()
            if not bundle_dir:
                bundle_dir = DEFAULT_BUILD_OUTPUT_DIR_NAME
        except Exception as e:
            return False, None, None, f"Failed to render directory template: {e}", None

        # Extract placement and naming
        placement = (
            artifact.strip().lower()
        )  # use artifact name as default placement directory
        naming = str(artifact_location.get("filename_template", "")).strip()

        # Create immutable context
        try:
            bundle_root = PantheonPath(bundle_dir, target_team, "processes")
            Log.debug(
                f"BUILD bundle_root: {bundle_root}, bundle_dir: {bundle_dir}, target_team: {target_team}"
            )
            ctx = _BuildContext(
                process_name=process_name,
                target_team=target_team,
                artifact=artifact,
                sections=sections,
                initial_section=initial_section,
                section_defs=section_defs,
                placement=placement,
                naming=naming,
                permissions=permissions,
                bundle_root=bundle_root,
                create_proc=f"create-{artifact}",
                get_proc=f"get-{artifact}",
            )
            Log.debug(
                f"BUILD bundle root resolved under artifacts sandbox: {ctx.bundle_root}"
            )
            return True, ctx, compiled_schema, None, build_mode
        except ValueError as e:
            return False, None, None, str(e), None

    def _generate_modular_create_schema(
        self, ctx: _BuildContext, build_mode: str
    ) -> str:
        """Generate modular CREATE schema with object-based array and std.foldl composition.

        Args:
            ctx: Build context containing sections data
            build_mode: Build mode value ('complete' or 'modular') that controls enabled defaults

        Returns:
            Jsonnet schema string with sections array and std.foldl-based composition
        """
        update_process = f"update-{ctx.artifact}"
        lines = []

        # Generate sections array with name/schema/enabled objects
        lines.append("local sections = [")
        for i, section in enumerate(ctx.sections):
            uri = f"process-schema://{update_process}/sections/{section}"
            # Set enabled based on build_mode: all true for 'complete', only initial true for 'modular'
            if build_mode == "complete":
                enabled = "true"
            else:
                # For modular mode, only initial section is true
                enabled = "true" if i == 0 else "false"
            lines.append("  {")
            lines.append(f'    name: "{section}",')
            lines.append(f'    schema: import "{uri}",')
            lines.append(f"    enabled: {enabled}")
            suffix = "," if i < len(ctx.sections) - 1 else ""
            lines.append(f"  }}{suffix}")
        lines.append("];")
        lines.append("")

        # Generate properties composition using std.foldl
        lines.append("local properties = std.foldl(")
        lines.append("  function(acc, sec)")
        lines.append("    if sec.enabled then acc + sec.schema.properties else acc,")
        lines.append("  sections,")
        lines.append("  {}")
        lines.append(");")
        lines.append("")

        # Generate required array composition using std.foldl with objectHas guard
        lines.append("local required = std.foldl(")
        lines.append("  function(acc, sec)")
        lines.append("    if sec.enabled && std.objectHas(sec.schema, 'required')")
        lines.append("    then acc + sec.schema.required")
        lines.append("    else acc,")
        lines.append("  sections,")
        lines.append("  []")
        lines.append(");")
        lines.append("")

        # Generate final schema object
        lines.append("{")
        lines.append('  "$schema": "http://json-schema.org/draft-07/schema#",')
        lines.append('  "type": "object",')
        lines.append('  "properties": properties,')
        lines.append('  "required": required')
        lines.append("}")

        return "\n".join(lines)

    def _generate_modular_create_template(
        self, ctx: _BuildContext, build_mode: str
    ) -> str:
        """Generate modular CREATE template with section toggles and artifact-template:// includes.

        Args:
            ctx: Build context containing sections data
            build_mode: Build mode value ('complete' or 'modular') that controls toggle defaults

        Returns:
            Markdown template string with YAML frontmatter, toggle variables, and conditional sections
        """
        update_process = f"update-{ctx.artifact}"
        lines = []

        # Add YAML frontmatter
        lines.append("---")
        lines.append("created_at: {{ pantheon_timestamp }}")
        lines.append("created_by: {{ pantheon_actor }}")
        lines.append("---")

        # Generate section blocks with toggle variables and conditional includes
        for i, section in enumerate(ctx.sections):
            # Toggle variable using template naming convention
            template_var = self._section_name_to_template_variable(section)
            # Set default based on build_mode: all true for 'complete', only initial true for 'modular'
            if build_mode == "complete":
                toggle_value = "true"
            else:
                # For modular mode, only initial section is true
                toggle_value = "true" if i == 0 else "false"
            lines.append(f"{{% set {template_var} = {toggle_value} %}}")

            # HTML comment section markers using CONSTANT_CASE
            section_marker = self._section_name_to_constant_case(section)
            lines.append(f"<!-- SECTION:START:{section_marker} -->")

            # Conditional block with artifact-template:// include
            lines.append(f"{{% if {template_var} %}}")
            uri = f"artifact-template://{update_process}/sections/{section}"
            lines.append(f"{{% include '{uri}' %}}")
            lines.append("{% else %}")
            lines.append("<!-- SECTION:PLACEHOLDER -->")
            lines.append("{% endif %}")
            lines.append(f"<!-- SECTION:END:{section_marker} -->")

            # Add blank line between sections (except after last section)
            if i < len(ctx.sections) - 1:
                lines.append("")

        return "\n".join(lines)

    def _build_scaffold_create(
        self,
        ctx: _BuildContext,
        input_params: dict[str, Any],
        framework_params: dict[str, Any],
        build_mode: str,
    ) -> list[PantheonPath]:
        """Scaffold CREATE process files with enforced artifact ID format.

        Args:
            ctx: Build context with all required state
            input_params: Clean input parameters for validation and YAML generation
            build_mode: Build mode value ('complete' or 'modular') that controls toggle defaults
            framework_params: Built-in framework variables

        Returns:
            List of created file paths
        """
        # Generate artifact acronym
        acronym = self._generate_artifact_acronym(ctx.artifact)

        # Always prepend structured ID format for consistency
        id_prefix = f"[{acronym}{{{{ pantheon_artifact_id }}}}]_"
        naming_template = id_prefix + ctx.naming
        Log.debug(f"Enhanced naming template with artifact ID: {naming_template}")

        # Build content.md based on build_mode and section count
        content_parts: list[str] = []
        content_parts.append(TEMPLATE_YAML_FRONT_MATTER)

        # Determine schema generation approach
        # Use modular generation (semantic URI imports) for multi-section builds
        use_modular_generation = len(ctx.sections) > 1

        # Single section case: No section markers - just plain content
        if len(ctx.sections) == 1:
            section_name = ctx.sections[0]
            section_def = ctx.section_defs.get(section_name, {})
            raw_template = section_def.get("template", "")

            # Add content without section markers for single section
            if raw_template:
                body = fix_markdown_formatting(raw_template)
                content_parts.append(body)

            content_md = "\n".join(content_parts).strip() + "\n"

            # Create root schema from section schema, ensuring $schema field is present
            section_schema = section_def.get("schema", {})
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": section_schema.get("properties", {}),
            }
            # Add required field if it exists in the section schema
            if "required" in section_schema:
                schema["required"] = section_schema["required"]

        else:
            # Multiple sections case: Choose generation approach based on use_modular_generation flag
            if use_modular_generation:
                # Use modular generation with semantic URI imports and toggle variables
                content_md = self._generate_modular_create_template(ctx, build_mode)
            else:
                # Use traditional inline content with markers and toggle pattern
                # Generate toggle variable declarations based on build_mode
                toggle_vars = []
                for sec in ctx.sections:
                    sec_var_name = sec.lower().replace(" ", "_").replace("-", "_")
                    # Set default based on build_mode: all true for 'complete', only initial true for 'modular'
                    if build_mode == "complete":
                        default_value = "true"
                    else:
                        # For modular mode, only initial section and context (if present) are true
                        if sec == ctx.initial_section or (
                            sec == BUILD_KEY_CONTEXT and sec in ctx.section_defs
                        ):
                            default_value = "true"
                        else:
                            default_value = "false"
                    toggle_vars.append(
                        f"{{% set _include_{sec_var_name} = {default_value} %}}"
                    )

                # Add toggle variable declarations at the top
                content_parts.append("\n".join(toggle_vars))
                content_parts.append("")

                # Generate sections with conditional includes
                for sec in ctx.sections:
                    marker = ctx._marker_name(sec)
                    sec_var_name = sec.lower().replace(" ", "_").replace("-", "_")
                    start = f"<!-- SECTION:START:{marker} -->"
                    end = f"<!-- SECTION:END:{marker} -->"

                    # Get section definition
                    section_def = ctx.section_defs.get(sec, {})
                    raw_template = section_def.get("template", "")

                    # Generate conditional block with actual content or placeholder
                    body_lines = [f"{{% if _include_{sec_var_name} %}}"]
                    if raw_template:
                        body_lines.append(fix_markdown_formatting(raw_template))
                    body_lines.append("{% else %}")
                    body_lines.append(PLACEHOLDER_MARKER)
                    body_lines.append("{% endif %}")
                    body = "\n".join(body_lines)

                    content_parts.append("\n".join([start, body, end, ""]))
                content_md = "\n".join(content_parts).strip() + "\n"

            # Build sections array with enabled flags based on build_mode for toggle pattern
            # Enabled flag defaults are determined by build_mode parameter value
            sections_with_toggles = []
            for sec in ctx.sections:
                section_def = ctx.section_defs.get(sec, {})
                schema = section_def.get("schema", {})

                # Set enabled flag based on build_mode
                if build_mode == "complete":
                    enabled = True
                else:
                    # For modular mode, only initial section and context (if present) are enabled
                    enabled = sec == ctx.initial_section or (
                        sec == BUILD_KEY_CONTEXT and sec in ctx.section_defs
                    )

                sections_with_toggles.append(
                    {"name": sec, "schema": schema, "enabled": enabled}
                )

            # Generate schemas_to_merge list based on enabled flags
            # This simulates the std.foldl conditional merging pattern
            schemas_to_merge = [
                item["schema"] for item in sections_with_toggles if item["enabled"]
            ]

            # Extract properties and metadata from each schema (handling both old and sanitized formats)
            merged_properties = {}
            merged_required = []
            merged_meta = {}

            def is_property_definition(value):
                """Check if a value looks like a JSON Schema property definition."""
                return isinstance(value, dict) and (
                    "type" in value or "properties" in value or "$ref" in value
                )

            def is_schema_metadata_field(key):
                """Check if a key is a schema-level metadata field."""
                return key in {
                    "$schema",
                    "type",
                    "title",
                    "description",
                    "required",
                    "additionalProperties",
                    "definitions",
                    "$defs",
                }

            # Process each schema in order (later schemas take precedence for conflicts)
            for schema_item in schemas_to_merge:
                if not schema_item:
                    continue

                schema_properties = {}

                if "properties" in schema_item:
                    # Schema is in full JSON Schema format (sanitized)
                    schema_properties = schema_item.get("properties", {})
                    if "required" in schema_item:
                        # Add required fields, avoiding duplicates
                        for req in schema_item["required"]:
                            if req not in merged_required:
                                merged_required.append(req)
                    # Copy other schema metadata (later schemas take precedence)
                    for key, value in schema_item.items():
                        if key not in ["properties", "required"]:
                            merged_meta[key] = value
                else:
                    # Schema might be properties-only (old format) or mixed format
                    # Separate based on whether the value looks like a property definition
                    for key, value in schema_item.items():
                        if key == "required":
                            req_list = value if isinstance(value, list) else []
                            for req in req_list:
                                if req not in merged_required:
                                    merged_required.append(req)
                        elif is_schema_metadata_field(
                            key
                        ) and not is_property_definition(value):
                            # Schema-level metadata field (later schemas take precedence)
                            merged_meta[key] = value
                        elif is_property_definition(value):
                            # Property definition
                            schema_properties[key] = value
                        else:
                            # Fallback: treat as schema metadata (later schemas take precedence)
                            merged_meta[key] = value

                # Merge properties (later schemas take precedence for conflicts)
                merged_properties.update(schema_properties)

            # Build the final merged schema in proper JSON Schema format
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
            }

            # Add other metadata
            schema.update(merged_meta)

            # Add properties if we have any
            if merged_properties:
                schema["properties"] = merged_properties

            # Add required array if we have any (even if no properties - this handles required-only schemas)
            if merged_required:
                schema["required"] = merged_required

        # Generate schema in appropriate format
        if use_modular_generation:
            # Use Jsonnet with semantic URI imports for modular builds
            schema_jsonnet = self._generate_modular_create_schema(ctx, build_mode)
        else:
            # Use JSON for single-section builds
            schema_jsonnet = json.dumps(schema, indent=2)

        perms_create = self._serialize_permissions(ctx.permissions, "create", ctx)

        # For backward compatibility with workspace methods, merge parameters
        enhanced_parameters = input_params.copy()
        enhanced_parameters.update(framework_params)

        return self._workspace.scaffold_create_process(
            ctx.bundle_root,
            ctx.create_proc,
            content_md,
            ctx.placement,
            naming_template,  # <- Use enhanced template
            schema_jsonnet,
            perms_create,
            include_default_routine=True,
            enhanced_parameters=enhanced_parameters,
        )

    def _build_scaffold_get(
        self,
        ctx: _BuildContext,
        input_params: dict[str, Any],
        framework_params: dict[str, Any],
    ) -> list[PantheonPath]:
        """Scaffold GET process files with enhanced parser for artifact ID extraction.

        Args:
            ctx: Build context with all required state
            input_params: Clean input parameters for validation and YAML generation
            framework_params: Built-in framework variables

        Returns:
            List of created file paths
        """
        # Import the constants for proper key usage
        from .artifact_engine import NORMALIZER_PATTERN_KEY, NORMALIZER_REPLACEMENT_KEY

        # Generate acronym for parser
        acronym = self._generate_artifact_acronym(ctx.artifact)

        # Always prepend the ID prefix to match what CREATE will generate
        id_prefix = f"[{acronym}{{{{ pantheon_artifact_id }}}}]_"
        final_naming_template = id_prefix + ctx.naming
        Log.debug(f"GET process will expect enhanced naming: {final_naming_template}")

        # Generate parser rules to normalize various ID formats to just the acronym+digits
        # Handles: TP1, [TP1], [TP1]_filename, [TP1]_filename.ext → TP1
        parser_rules = [
            {
                NORMALIZER_PATTERN_KEY: f"^.*?({acronym}\\d+).*$",
                NORMALIZER_REPLACEMENT_KEY: "\\1",  # Extract just the ID without brackets
            }
        ]
        parser_json = json.dumps(parser_rules, indent=2)

        # Generate the locator using the correct final template
        locator_jsonnet, _, warnings = self._derive_locator_jsonnet(
            final_naming_template, ctx.placement
        )

        # Should always use ID after our enhancement (no warnings expected)
        for w in warnings:
            Log.warning(w)

        # Optional permissions
        perms_get = self._serialize_permissions(ctx.permissions, "get", ctx)

        # For backward compatibility with workspace methods, merge parameters
        enhanced_parameters = input_params.copy()
        enhanced_parameters.update(framework_params)

        # Single section case: No sections.jsonnet file - treat as single document
        if len(ctx.sections) == 1:
            return self._workspace.scaffold_get_process(
                ctx.bundle_root,
                ctx.get_proc,
                None,  # No sections.jsonnet for single section
                locator_jsonnet,
                parser_json,
                perms_get,
                include_default_routine=True,
                enhanced_parameters=enhanced_parameters,
            )

        # Multiple sections case: Create sections.jsonnet with all section markers
        markers_obj: dict[str, Any] = {
            "sections": {},
            "placeholder": PLACEHOLDER_MARKER,
        }

        # Add all sections (context section only included if include_context was true)
        for sec in ctx.sections:
            m = ctx._marker_name(sec)
            section_meta = ctx.section_defs.get(sec, {}) or {}
            description_value = section_meta.get("description")
            markers_obj["sections"][sec] = {
                "description": description_value.strip()
                if isinstance(description_value, str)
                else "",
                "start": f"<!-- SECTION:START:{m} -->",
                "end": f"<!-- SECTION:END:{m} -->",
            }
        sections_json = json.dumps(markers_obj, indent=2)

        return self._workspace.scaffold_get_process(
            ctx.bundle_root,
            ctx.get_proc,
            sections_json,
            locator_jsonnet,
            parser_json,
            perms_get,
            include_default_routine=True,
            enhanced_parameters=enhanced_parameters,
        )

    def _build_scaffold_updates(
        self,
        ctx: _BuildContext,
        input_params: dict[str, Any],
        framework_params: dict[str, Any],
        compiled_schema: dict[str, Any],
    ) -> tuple[list[PantheonPath], list[str]]:
        """Scaffold UPDATE process files.

        Args:
            ctx: Build context with all required state
            input_params: Clean input parameters for validation and YAML generation
            framework_params: Built-in framework variables
            compiled_schema: Compiled build schema

        Returns:
            Tuple of (created_file_paths, process_names)
        """
        section_names = ctx.sections
        update_process_name = f"update-{ctx.artifact}"

        # Single section case: treat as no sections (whole document replacement)
        if len(section_names) == 1:
            section_name = section_names[0]
            section_def = ctx.section_defs.get(section_name, {})

            # Create simple patch template without loops
            patch_template = fix_markdown_formatting(
                section_def.get("template") or PLACEHOLDER_MARKER
            )

            # Create root schema from section schema, ensuring $schema field is present
            section_schema = section_def.get("schema", {})
            schema_dict = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": section_schema.get("properties", {}),
            }
            # Add required field if it exists in the section schema
            if "required" in section_schema:
                schema_dict["required"] = section_schema["required"]

            schema_jsonnet = json.dumps(schema_dict, indent=2)

            # No target.jsonnet for single section - pass None
            target_json = None
            locator_json = f'import "artifact-locator://{ctx.get_proc}"'
            parser_json = f'import "artifact-parser://{ctx.get_proc}"'
            perms_update = self._serialize_permissions(ctx.permissions, "update", ctx)

            # Flat parameters structure for single section
            enhanced_parameters = input_params.copy()
            enhanced_parameters.update(framework_params)

            created_paths: list[PantheonPath] = []

            created_paths.extend(
                self._workspace.scaffold_update_process(
                    ctx.bundle_root,
                    update_process_name,
                    target_json,  # None for single section
                    locator_json,
                    parser_json,
                    patch_template,
                    schema_jsonnet,
                    perms_update,
                    include_default_routine=True,
                    enhanced_parameters=enhanced_parameters,
                )
            )

            # For single section: Don't create any section files - use flat schema directly
            return created_paths, [update_process_name]

        # Multiple sections case: use existing nested structure
        schema_jsonnet = generate_update_schema_jsonnet(section_names)

        patch_template = (
            "{% set requested_sections = pantheon_sections if pantheon_sections else section_order %}\n\n"
            "{% for section_name in requested_sections %}\n"
            '  {% set snippet = "sections/" ~ section_name ~ ".md" %}\n'
            "  {% include snippet ignore missing %}\n"
            "{% endfor %}\n"
        )

        target_json = f'import "artifact-sections://{ctx.get_proc}"'
        locator_json = f'import "artifact-locator://{ctx.get_proc}"'
        parser_json = f'import "artifact-parser://{ctx.get_proc}"'
        perms_update = self._serialize_permissions(ctx.permissions, "update", ctx)

        enhanced_parameters = input_params.copy()
        enhanced_parameters.update(framework_params)
        enhanced_parameters["section_order"] = section_names

        created_paths: list[PantheonPath] = []

        created_paths.extend(
            self._workspace.scaffold_update_process(
                ctx.bundle_root,
                update_process_name,
                target_json,
                locator_json,
                parser_json,
                patch_template,
                schema_jsonnet,
                perms_update,
                include_default_routine=True,
                enhanced_parameters=enhanced_parameters,
            )
        )

        proc_root = ctx.bundle_root.joinpath(update_process_name)
        for section in section_names:
            section_def = ctx.section_defs.get(section, {})
            snippet_content = fix_markdown_formatting(
                section_def.get("template") or PLACEHOLDER_MARKER
            )
            created_paths.append(
                self._workspace.save_artifact(
                    snippet_content,
                    proc_root.joinpath("artifact", "sections", f"{section}.md"),
                )
            )

            schema_content = json.dumps(section_def.get("schema", {}), indent=2)
            created_paths.append(
                self._workspace.save_artifact(
                    schema_content,
                    proc_root.joinpath(
                        "artifact", "sections", f"{section}.schema.jsonnet"
                    ),
                )
            )

        return created_paths, [update_process_name]

    def _serialize_permissions(
        self, perms_dict: dict[str, Any], perm_type: str, build_ctx: Any = None
    ) -> str | None:
        """Serialize permissions for a specific operation type.

        Args:
            perms_dict: Dictionary containing permission configurations
            perm_type: Type of permission ("create", "get", "update")
            build_ctx: Optional build context containing section information

        Returns:
            JSON serialized permissions or None if not present
        """
        if isinstance(perms_dict, dict) and perms_dict.get(perm_type) is not None:
            return json.dumps(perms_dict.get(perm_type), indent=2)

        # Only return defaults for standard BUILD operations (create, get, update)
        # Other operation types (like "delete" in tests) should return None
        if perm_type not in ["create", "get", "update"]:
            return None

        # If perms_dict is not a valid dict, return None (maintains backward compatibility)
        if not isinstance(perms_dict, dict):
            return None

        # Generate safe default permissions for BUILD operations
        default_perms = {"allow": ["*"], "deny": []}

        # For UPDATE operations, include section-level permissions if this is a multi-section process
        if (
            perm_type == "update"
            and build_ctx
            and hasattr(build_ctx, "sections")
            and len(build_ctx.sections) > 1
        ):
            default_perms["sections"] = {}
            for section_name in build_ctx.sections:
                default_perms["sections"][section_name] = {
                    "allow": ["*"],
                    "deny": [],
                }

        return json.dumps(default_perms, indent=2)

    def _merge_permissions_for_complete_mode(
        self, perms_dict: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Merge create and update permissions for complete mode.

        In complete mode, since no update processes are generated, agents that
        were intended to have update rights should be granted create rights.

        Args:
            perms_dict: Dictionary containing permission configurations

        Returns:
            Merged permissions dictionary or None if no permissions
        """
        if not isinstance(perms_dict, dict):
            return None

        create_perms = perms_dict.get("create", {})
        update_perms = perms_dict.get("update", {})

        if not create_perms and not update_perms:
            return None

        # Start with create permissions
        merged = {"allow": [], "deny": []}

        # Add create permissions
        if isinstance(create_perms, dict):
            merged["allow"].extend(create_perms.get("allow", []))
            merged["deny"].extend(create_perms.get("deny", []))

        # Add update permissions (avoiding duplicates)
        if isinstance(update_perms, dict):
            for allow_actor in update_perms.get("allow", []):
                if allow_actor not in merged["allow"]:
                    merged["allow"].append(allow_actor)
            for deny_actor in update_perms.get("deny", []):
                if deny_actor not in merged["deny"]:
                    merged["deny"].append(deny_actor)

        return merged

    @staticmethod
    def _section_name_to_template_variable(section_name: str) -> str:
        """Convert hyphenated section name to underscore-prefixed template variable.

        Args:
            section_name: Hyphenated section name (e.g., "high-level-overview")

        Returns:
            Underscore-prefixed template variable (e.g., "_include_high_level_overview")
        """
        # Replace hyphens with underscores
        underscored = section_name.replace("-", "_")

        # Prepend with 'include' semantic prefix
        return f"_include_{underscored}"

    @staticmethod
    def _section_name_to_constant_case(section_name: str) -> str:
        """Convert hyphenated section name to CONSTANT_CASE for HTML markers.

        Args:
            section_name: Hyphenated section name (e.g., "high-level-overview")

        Returns:
            CONSTANT_CASE identifier (e.g., "HIGH_LEVEL_OVERVIEW")
        """
        # Replace hyphens with underscores and convert to uppercase
        return section_name.replace("-", "_").upper()

    @staticmethod
    def _generate_artifact_acronym(artifact_name: str) -> str:
        """Generate acronym from artifact name for ID prefixing.

        Args:
            artifact_name: Full artifact name (e.g., "team-blueprint", "user spec")

        Returns:
            Uppercase acronym (e.g., "TB", "US")
        """
        # Split on hyphens, underscores, and spaces
        import re

        words = re.split(r"[-_\s]+", artifact_name.strip())

        # Take first letter of each word, filter empty strings
        letters = [word[0].upper() for word in words if word and word[0].isalpha()]

        # Default to "ART" if no valid letters found
        return "".join(letters) if letters else "ART"

    @staticmethod
    def _derive_locator_jsonnet(
        filename_tpl: str, placement: str
    ) -> tuple[str, bool, list[str]]:
        """Generate locator.jsonnet for consistent [{{ pantheon_artifact_id }}]_ pattern.

        Since _build_scaffold_create always prepends [ACRONYM{{ pantheon_artifact_id }}]_,
        the locator pattern always expects [{{ pantheon_artifact_id }}]_ without the acronym
        (users provide the acronym as part of the ID).

        Now also extracts literal suffixes from the filename template for more precise matching.

        Args:
            filename_tpl: Jinja template for filename
            placement: Directory placement
        """
        import re

        warnings: list[str] = []

        # Extract literal suffix after the last Jinja variable
        literal_suffix = ""
        if filename_tpl and filename_tpl.strip():
            # Check if this is a bracket pattern like [PREFIX{{ pantheon_artifact_id }}]_suffix
            bracket_pattern = r"\[.*?\{\{[^}]*pantheon_artifact_id[^}]*\}\}.*?\]_(.*)"
            bracket_match = re.search(bracket_pattern, filename_tpl)

            if bracket_match:
                # For bracket patterns, extract everything after ]_ and then apply normal logic
                remaining_template = bracket_match.group(1)

                # Apply the same Jinja variable splitting logic to the remaining template
                jinja_pattern = r"\{\{[^}]+\}\}"
                parts = re.split(jinja_pattern, remaining_template)

                # The last part contains the literal suffix (if any)
                if len(parts) > 1 and parts[-1]:
                    literal_suffix = parts[-1]
                elif len(parts) == 1 and parts[0]:
                    # No Jinja variables in remaining template, entire remainder is literal suffix
                    literal_suffix = parts[0]
            else:
                # For non-bracket patterns, use the original logic
                # Find all Jinja variables in the template
                jinja_pattern = r"\{\{[^}]+\}\}"

                # Split template by Jinja variables to find literal parts
                parts = re.split(jinja_pattern, filename_tpl)

                # The last part contains the literal suffix (if any)
                if len(parts) > 1 and parts[-1]:
                    literal_suffix = parts[-1]

        # Always generate the consistent pattern that matches [artifact_id]_ followed by anything
        directory_field = (
            f'"{placement.rstrip("/")}"' if placement and placement.strip() else "null"
        )

        # Build pattern with optional literal suffix matching
        if literal_suffix:
            # Custom escape for JSON context: escape regex special chars but double-escape for JSON
            # Don't escape hyphens (they're only special in character classes)
            escaped_suffix = re.escape(literal_suffix)
            # Remove unnecessary hyphen escaping and double-escape for JSON
            escaped_suffix = escaped_suffix.replace("\\-", "-").replace("\\", "\\\\")
            # Pattern that matches [artifact_id]_ followed by anything, ending with the literal suffix
            full_pattern_expr = (
                '"^\\\\[" + std.extVar("pantheon_artifact_id") + "\\\\]_.*'
                + escaped_suffix
                + '$"'
            )
        else:
            # Simple pattern that matches [artifact_id]_ followed by anything (original behavior)
            full_pattern_expr = (
                '"^\\\\[" + std.extVar("pantheon_artifact_id") + "\\\\]_.*$"'
            )

        locator_jsonnet = (
            '{\n  "directory": ' + directory_field + ",\n"
            '  "pattern": ' + full_pattern_expr + "\n"
            "}"
        )

        return locator_jsonnet, True, warnings

    def execute_create_process(
        self,
        input_params: dict[str, Any],
        framework_params: dict[str, Any],
        templates: dict[str, str],
    ) -> ProcessResult:
        """Execute a CREATE process that generates new artifacts.

        Args:
            input_params: Clean input parameters for validation and YAML generation
            framework_params: Built-in framework variables
            templates: Initial templates loaded during process type detection (contains "content")

        Returns:
            ProcessResult with path to the generated artifact
        """
        process_name = framework_params[BUILTIN_PROCESS]

        # Use shared validation and schema compilation with clean input parameters
        (
            success,
            compiled_schema,
            error_message,
        ) = self._validate_input_and_compile_schema(
            process_name, input_params, framework_params
        )
        if not success:
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: error_message,
                RESULT_FILES_CREATED: None,
            }

        # Load placement and naming templates for CREATE operation
        try:
            templates["placement"] = self._workspace.get_artifact_directory_template(
                process_name
            )
            templates["naming"] = self._workspace.get_artifact_filename_template(
                process_name
            )
        except FileNotFoundError as e:
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: f"Missing required CREATE templates: {e}",
                RESULT_FILES_CREATED: None,
            }

        # Generate new artifact content and path
        content, relative_path = self._artifact_engine.generate_artifact(
            templates, input_params, framework_params
        )

        # Save artifact through workspace
        saved_path = self._workspace.save_artifact(content, relative_path)

        # Check if JSONL logging is enabled for this process
        created_paths = [saved_path]
        if self._workspace.has_jsonl_templates(process_name):
            try:
                # Load JSONL templates
                jsonl_templates = {
                    "jsonl_placement": self._workspace.get_artifact_jsonl_directory_template(
                        process_name
                    ),
                    "jsonl_naming": self._workspace.get_artifact_jsonl_filename_template(
                        process_name
                    ),
                }

                # Generate JSONL file path
                jsonl_path = self._artifact_engine.generate_jsonl_path(
                    jsonl_templates, input_params, framework_params
                )

                # Create JSONL entry with minimal framework metadata
                jsonl_entry = {
                    **input_params,  # User-provided data
                    "timestamp": framework_params[
                        "pantheon_timestamp"
                    ],  # Only timestamp for analytics
                }

                # Append to JSONL file
                jsonl_saved_path = self._workspace.append_jsonl_entry(
                    jsonl_entry, jsonl_path
                )
                created_paths.append(jsonl_saved_path)

                Log.debug(f"JSONL entry appended to {jsonl_path}")

            except Exception as e:
                # Log JSONL generation failure but don't fail the main operation
                Log.warning(
                    f"Failed to generate JSONL entry for process '{process_name}': {e}"
                )

        # Collect created files and generate standardized output
        files_info = self._workspace.summarize_created_files(created_paths)

        # Generate standardized success message
        output = SUCCESS_MESSAGE_TEMPLATE.format(
            process_name=process_name, operation_type=OPERATION_CREATE
        )

        return {
            RESULT_SUCCESS: True,
            RESULT_OUTPUT: output,
            RESULT_ERROR: None,
            RESULT_FILES_CREATED: files_info,
        }

    def execute_update_process(
        self,
        input_params: dict[str, Any],
        framework_params: dict[str, Any],
        templates: dict[str, str],
    ) -> ProcessResult:
        """Execute an UPDATE process that modifies existing artifact sections.

        Args:
            input_params: Clean input parameters for validation and YAML generation
            framework_params: Built-in framework variables
            templates: Initial templates loaded during process type detection (contains "patch")

        Returns:
            ProcessResult with path to the modified artifact
        """
        process_name = framework_params[BUILTIN_PROCESS]

        # Use shared validation and schema compilation with clean input parameters
        (
            success,
            compiled_schema,
            error_message,
        ) = self._validate_input_and_compile_schema(
            process_name, input_params, framework_params
        )
        if not success:
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: error_message,
                RESULT_FILES_CREATED: None,
            }

        # Check if this UPDATE process has target.jsonnet (multi-section) or not (single-section)
        try:
            self._workspace.get_artifact_target_section(process_name)
            has_target = True
        except FileNotFoundError:
            has_target = False

        if not has_target:
            # Single section case: treat as whole document replacement
            return self._execute_whole_document_update(
                process_name, input_params, framework_params, templates
            )

        # Multiple sections case: use existing section-based logic
        return self._execute_sectioned_update(
            process_name, input_params, framework_params, templates, compiled_schema
        )

    def _execute_whole_document_update(
        self,
        process_name: str,
        input_params: dict[str, Any],
        framework_params: dict[str, Any],
        templates: dict[str, str],
    ) -> ProcessResult:
        """Execute update for single-section case (whole document replacement)."""
        # Find the target artifact
        # ArtifactEngine.find_artifact() handles both multi-artifact and singleton modes
        artifact_id = framework_params.get(BUILTIN_ARTIFACT_ID)
        Log.debug(f"Searching for artifact with ID: '{artifact_id}'")
        artifact_path = self._artifact_engine.find_artifact(process_name, artifact_id)

        if artifact_path is None:
            # Provide mode-appropriate error message
            if artifact_id:
                error_msg = f"Artifact not found: {artifact_id}"
            else:
                error_msg = f"Artifact not found for singleton process '{process_name}'"

            Log.debug(
                f"Artifact not found for ID '{artifact_id}' in process '{process_name}'"
            )
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: error_msg,
                RESULT_FILES_CREATED: None,
            }

        # Render patch.md with input parameters directly (no section nesting)
        try:
            context = self._artifact_engine._create_template_context(
                input_params, framework_params, "UPDATE"
            )

            jinja_env = self._workspace.get_artifact_template_environment(process_name)
            new_content = self._artifact_engine.render_artifact_template(
                templates["patch"],
                context,
                jinja_env,
                f"patch template for {process_name}",
            )

            # Replace entire artifact content
            saved_path = self._workspace.save_artifact(new_content, artifact_path)

            # Generate standardized output
            created_paths = [saved_path]
            files_info = self._workspace.summarize_created_files(created_paths)

            output = SUCCESS_MESSAGE_TEMPLATE.format(
                process_name=process_name, operation_type=OPERATION_UPDATE
            )

            return {
                RESULT_SUCCESS: True,
                RESULT_OUTPUT: output,
                RESULT_ERROR: None,
                RESULT_FILES_CREATED: files_info,
            }
        except Exception as e:
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: f"Failed to update artifact: {e}",
                RESULT_FILES_CREATED: None,
            }

    def _execute_sectioned_update(
        self,
        process_name: str,
        input_params: dict[str, Any],
        framework_params: dict[str, Any],
        templates: dict[str, str],
        compiled_schema: dict[str, Any],
    ) -> ProcessResult:
        """Execute update for multi-section case (section-based replacement)."""
        # Load target template for UPDATE operation
        try:
            templates["target"] = self._workspace.get_artifact_target_section(
                process_name
            )
        except FileNotFoundError as e:
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: f"Missing required UPDATE templates: {e}",
                RESULT_FILES_CREATED: None,
            }

        # Step 1: Find the target artifact
        # ArtifactEngine.find_artifact() handles both multi-artifact and singleton modes
        artifact_id = framework_params.get(BUILTIN_ARTIFACT_ID)
        Log.debug(f"Searching for artifact with ID: '{artifact_id}'")
        artifact_path = self._artifact_engine.find_artifact(process_name, artifact_id)

        if artifact_path is None:
            # Provide mode-appropriate error message
            if artifact_id:
                error_msg = f"Artifact not found: {artifact_id}"
            else:
                error_msg = f"Artifact not found for singleton process '{process_name}'"

            Log.debug(
                f"Artifact not found for ID '{artifact_id}' in process '{process_name}'"
            )
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: error_msg,
                RESULT_FILES_CREATED: None,
            }

        # Step 2: Determine marker configuration for requested sections
        try:
            target_config = json.loads(templates["target"])
        except json.JSONDecodeError as e:
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: f"Failed to parse target configuration: {e}",
                RESULT_FILES_CREATED: None,
            }

        placeholder_marker_default = ""
        target_sections = {}
        if isinstance(target_config, dict):
            placeholder_value = target_config.get("placeholder")
            if isinstance(placeholder_value, str):
                placeholder_marker_default = placeholder_value

            if "sections" in target_config and isinstance(
                target_config["sections"], dict
            ):
                target_sections = target_config["sections"]
            elif "start" in target_config and "end" in target_config:
                target_sections = {framework_params.get("section", ""): target_config}
            else:
                return {
                    RESULT_SUCCESS: False,
                    RESULT_OUTPUT: None,
                    RESULT_ERROR: "Invalid target configuration structure",
                    RESULT_FILES_CREATED: None,
                }
        else:
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: "Invalid target configuration - expected JSON object",
                RESULT_FILES_CREATED: None,
            }

        # Step 3: Render patch.md with parameters
        # Step 4: Read current artifact content
        try:
            current_content = self._workspace.read_artifact_file(artifact_path)
        except Exception as e:
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: f"Failed to read artifact file: {e}",
                RESULT_FILES_CREATED: None,
            }

        # Determine which sections to apply
        section_order = (
            compiled_schema.get("properties", {})
            .get("section_order", {})
            .get("default", [])
            if isinstance(compiled_schema, dict)
            else []
        )
        if section_order:
            framework_params.setdefault("section_order", section_order)
        requested_sections = framework_params.get(PARAM_SECTIONS)
        if not requested_sections:
            sections_to_update = section_order or list(target_sections.keys())
        else:
            sections_to_update = requested_sections

        if isinstance(sections_to_update, str):
            sections_to_update = [sections_to_update]

        updated_content = current_content
        for section_name in sections_to_update:
            if target_sections:
                markers = target_sections.get(section_name)
                if not markers:
                    return {
                        RESULT_SUCCESS: False,
                        RESULT_OUTPUT: None,
                        RESULT_ERROR: f"Markers for section '{section_name}' not found",
                        RESULT_FILES_CREATED: None,
                    }
                start_marker = markers.get("start")
                end_marker = markers.get("end")

                placeholder_marker = ""
                if isinstance(markers, dict):
                    section_placeholder = markers.get("placeholder")
                    if isinstance(section_placeholder, str):
                        placeholder_marker = section_placeholder
            else:
                start_marker = target_config.get("start")
                end_marker = target_config.get("end")
                placeholder_marker = placeholder_marker_default

            if not start_marker or not end_marker:
                return {
                    RESULT_SUCCESS: False,
                    RESULT_OUTPUT: None,
                    RESULT_ERROR: "Target configuration missing start/end markers",
                    RESULT_FILES_CREATED: None,
                }

            try:
                context = self._artifact_engine._create_template_context(
                    input_params, framework_params, "UPDATE"
                )
                context[PARAM_SECTIONS] = [section_name]
                context["section_order"] = section_order or sections_to_update
                context["section"] = section_name

                # Extract and flatten section-specific data for direct template access
                section_updates = input_params.get("section_updates", {})
                if section_name in section_updates:
                    # Merge section-specific variables into context
                    section_data = section_updates[section_name]
                    if isinstance(section_data, dict):
                        context.update(section_data)
                        Log.debug(
                            f"Flattened {len(section_data)} variables for section '{section_name}'"
                        )

                jinja_env = self._workspace.get_artifact_template_environment(
                    process_name
                )
                patch_content = self._artifact_engine.render_artifact_template(
                    templates["patch"],
                    context,
                    jinja_env,
                    f"patch template for {process_name}",
                )
                # Check for insert mode (append/prepend) or default to replace
                insert_mode = framework_params.get(BUILTIN_INSERT_MODE)
                effective_placeholder = (
                    placeholder_marker
                    if placeholder_marker
                    else placeholder_marker_default
                )
                updated_content = self._apply_insert_mode_update(
                    updated_content,
                    start_marker,
                    end_marker,
                    patch_content,
                    insert_mode=insert_mode,
                    placeholder_marker=effective_placeholder,
                )
                if updated_content is None:
                    return {
                        RESULT_SUCCESS: False,
                        RESULT_OUTPUT: None,
                        RESULT_ERROR: f"Target section '{section_name}' not found in artifact",
                        RESULT_FILES_CREATED: None,
                    }
            except Exception as e:
                return {
                    RESULT_SUCCESS: False,
                    RESULT_OUTPUT: None,
                    RESULT_ERROR: f"Failed to update section '{section_name}': {e}",
                    RESULT_FILES_CREATED: None,
                }

        # Step 6: Save the updated artifact back to the same location
        try:
            saved_path = self._workspace.save_artifact(updated_content, artifact_path)

            # Collect created files and generate standardized output
            created_paths = [saved_path]
            files_info = self._workspace.summarize_created_files(created_paths)

            # Generate standardized success message
            output = SUCCESS_MESSAGE_TEMPLATE.format(
                process_name=process_name, operation_type=OPERATION_UPDATE
            )

            return {
                RESULT_SUCCESS: True,
                RESULT_OUTPUT: output,
                RESULT_ERROR: None,
                RESULT_FILES_CREATED: files_info,
            }
        except Exception as e:
            return {
                RESULT_SUCCESS: False,
                RESULT_OUTPUT: None,
                RESULT_ERROR: f"Failed to save updated artifact: {e}",
                RESULT_FILES_CREATED: None,
            }

    def _apply_insert_mode_update(
        self,
        content: str,
        start_marker: str,
        end_marker: str,
        new_content: str,
        *,
        insert_mode: str | None,
        placeholder_marker: str | None = None,
    ) -> str | None:
        """Apply insert-mode update with placeholder-aware replacement fallback.

        When a placeholder marker is present within the targeted section, the entire
        section is replaced regardless of insert mode to ensure scaffold content is
        removed on first write. If markers are missing the behavior mirrors the
        existing helpers by returning None so callers can surface errors consistently.
        """
        if insert_mode not in {"append", "prepend"}:
            return self._replace_section_content(
                content, start_marker, end_marker, new_content
            )

        start_index = content.find(start_marker)
        if start_index == -1:
            Log.warning(f"Start marker not found: {start_marker}")
            return None

        end_index = content.find(end_marker, start_index + len(start_marker))
        if end_index == -1:
            Log.warning(f"End marker not found: {end_marker}")
            return None

        start_line_end = content.find("\n", start_index)
        if start_line_end == -1:
            start_line_end = len(content)
        else:
            start_line_end += 1

        section_body = content[start_line_end:end_index]
        if placeholder_marker and placeholder_marker in section_body:
            return self._replace_section_content(
                content, start_marker, end_marker, new_content
            )

        if insert_mode == "append":
            return self._append_section_content(
                content, start_marker, end_marker, new_content
            )

        return self._prepend_section_content(
            content, start_marker, end_marker, new_content
        )

    def _replace_section_content(
        self, content: str, start_marker: str, end_marker: str, new_content: str
    ) -> str | None:
        """Replace content between section markers with new content.

        Args:
            content: The full file content
            start_marker: The start marker pattern to find
            end_marker: The end marker pattern to find
            new_content: The new content to insert between markers

        Returns:
            Updated content with section replaced, or None if markers not found
        """
        start_index = content.find(start_marker)
        if start_index == -1:
            Log.warning(f"Start marker not found: {start_marker}")
            return None

        end_index = content.find(end_marker, start_index + len(start_marker))
        if end_index == -1:
            Log.warning(f"End marker not found: {end_marker}")
            return None

        # Find end of start marker line
        start_line_end = content.find("\n", start_index)
        if start_line_end == -1:
            start_line_end = len(content)
        else:
            start_line_end += 1  # Include the newline

        # Build new content
        before = content[:start_line_end]
        after = content[end_index:]

        return f"{before}{new_content}\n{after}"

    def _append_section_content(
        self, content: str, start_marker: str, end_marker: str, new_content: str
    ) -> str | None:
        """Append content before the end marker, preserving existing section content.

        Args:
            content: The full file content
            start_marker: The start marker pattern to find
            end_marker: The end marker pattern to find
            new_content: The new content to append before the end marker

        Returns:
            Updated content with new content appended, or None if markers not found
        """
        start_index = content.find(start_marker)
        if start_index == -1:
            Log.warning(f"Start marker not found: {start_marker}")
            return None

        end_index = content.find(end_marker, start_index + len(start_marker))
        if end_index == -1:
            Log.warning(f"End marker not found: {end_marker}")
            return None

        # Build new content by inserting before the end marker
        before = content[:end_index]
        after = content[end_index:]

        # Ensure proper formatting - add newline if needed
        separator = "\n" if not before.endswith("\n") else ""

        return f"{before}{separator}{new_content}\n{after}"

    def _prepend_section_content(
        self, content: str, start_marker: str, end_marker: str, new_content: str
    ) -> str | None:
        """Prepend content after the start marker, preserving existing section content.

        Args:
            content: The full file content
            start_marker: The start marker pattern to find
            end_marker: The end marker pattern to find
            new_content: The new content to prepend after the start marker

        Returns:
            Updated content with new content prepended, or None if markers not found
        """
        start_index = content.find(start_marker)
        if start_index == -1:
            Log.warning(f"Start marker not found: {start_marker}")
            return None

        end_index = content.find(end_marker, start_index + len(start_marker))
        if end_index == -1:
            Log.warning(f"End marker not found: {end_marker}")
            return None

        # Find end of start marker line
        start_line_end = content.find("\n", start_index)
        if start_line_end == -1:
            start_line_end = len(content)
        else:
            start_line_end += 1  # Include the newline

        # Build new content by inserting after the start marker
        before = content[:start_line_end]
        after = content[start_line_end:]

        return f"{before}{new_content}\n{after}"

    def format_error(self, error_type: str, context: Any) -> str:
        """Format exception for user-friendly display.

        Args:
            error_type: Type of error that occurred
            context: Context information about the error

        Returns:
            Formatted error message string suitable for user display
        """
        Log.error(f"Formatting error - Type: {error_type}, Context: {context}")

        if error_type == "FileNotFoundError":
            return f"{ERROR_PREFIX_FILE_NOT_FOUND}: {context}"
        if error_type == "PermissionError":
            return f"{ERROR_PREFIX_PERMISSION_DENIED}: {context}"
        if error_type == "ValueError":
            return f"{ERROR_PREFIX_INVALID_INPUT}: {context}"
        return f"{error_type}: {context}"


def parse_process_uri(uri: str) -> tuple[str, dict[str, str]]:
    """Parse process URI and extract target process name and query parameters.

    Parses a process URI in the format 'process://target-process?param1=value1&param2=value2'
    and returns the target process name and a dictionary of parameters.

    Args:
        uri: Process URI string to parse

    Returns:
        Tuple of (process_name, parameters_dict)

    Raises:
        ValueError: If URI scheme is not 'process'

    Examples:
        >>> parse_process_uri("process://get-ticket?sections=plan")
        ("get-ticket", {"sections": "plan"})

        >>> parse_process_uri("process://create-ticket")
        ("create-ticket", {})
    """
    parsed = urllib.parse.urlparse(uri)

    # Validate scheme
    if parsed.scheme != "process":
        raise ValueError(f"Invalid URI scheme '{parsed.scheme}', expected 'process'")

    # Extract process name from netloc (authority) part
    process_name = parsed.netloc

    # Parse query parameters
    parameters = {}
    if parsed.query:
        parameters = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))

    return process_name, parameters


def merge_parameters(
    user_params: dict[str, str], redirect_params: dict[str, str]
) -> dict[str, str]:
    """Merge user parameters with redirect parameters using security precedence rules.

    Combines user-provided parameters with redirect-specified parameters.
    Redirect parameters take precedence over user parameters to prevent
    parameter injection attacks.

    Args:
        user_params: Parameters provided by the user
        redirect_params: Parameters specified in the redirect URI

    Returns:
        Merged parameter dictionary with redirect precedence

    Examples:
        >>> merge_parameters({"format": "md"}, {"sections": "plan"})
        {"format": "md", "sections": "plan"}

        >>> merge_parameters({"sections": "all"}, {"sections": "plan"})
        {"sections": "plan"}  # redirect overrides user
    """
    # Start with user parameters as base
    merged = user_params.copy()

    # Override with redirect parameters (security precedence)
    merged.update(redirect_params)

    return merged


def parse_sections_parameter(parameters: dict[str, Any]) -> dict[str, Any]:
    """Parse sections parameter from string to array if needed and rename to pantheon_sections.

    The sections parameter is a reserved parameter that should always be treated as an array
    and renamed to pantheon_sections to avoid conflicts with user-defined fields.
    This function handles conversion from comma-separated strings to arrays for both
    CLI usage (--param sections=plan,description) and redirect URIs (sections=plan,description).

    Args:
        parameters: Dictionary of parameters that may contain a sections parameter

    Returns:
        Dictionary with sections parameter converted to array and renamed to pantheon_sections if present

    Examples:
        >>> parse_sections_parameter({"sections": "plan"})
        {"pantheon_sections": ["plan"]}

        >>> parse_sections_parameter({"sections": "plan,description"})
        {"pantheon_sections": ["plan", "description"]}

        >>> parse_sections_parameter({"ticket": "T001"})
        {"ticket": "T001"}
    """
    result = parameters.copy()

    if "sections" not in parameters:
        return result

    sections_value = parameters["sections"]

    # Convert string to array if needed
    if isinstance(sections_value, str):
        # Split by comma and strip whitespace from each section
        sections_array = [
            section.strip() for section in sections_value.split(",") if section.strip()
        ]
    elif isinstance(sections_value, list):
        sections_array = sections_value
    else:
        # For any other type, leave as is
        sections_array = sections_value

    # Remove original sections and add pantheon_sections
    del result["sections"]
    result["pantheon_sections"] = sections_array
    return result
