"""PantheonWorkspace facade for filesystem operations and project conventions.

This module provides the PantheonWorkspace class that serves as the central hub
for all filesystem operations in the Pantheon Framework. It implements the Facade
pattern by providing a simplified interface to complex filesystem operations and
convention-based logic.

The workspace follows the Dependency Injection pattern by accepting a FileSystem
instance in its constructor, enabling complete unit testing with mocks while
maintaining complete separation between computation and I/O operations.

The PantheonWorkspace is the only component authorized to unwrap PantheonPath
objects and perform actual I/O operations through the injected FileSystem
dependency. This maintains architectural boundaries while enabling practical
filesystem operations.

Key Responsibilities:
- Project root discovery through .pantheon_project marker files
- Convention-based path resolution for team packages, processes, and agents
- Sandboxed artifact management in the output directory
- Transparent semantic URI handling for cross-process asset sharing
- Security validation to prevent directory traversal attacks
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
import re
from typing import Any, TypedDict
import uuid

import jinja2
import yaml

from pantheon.artifact_engine import remove_suffix, slugify
from pantheon.filesystem import FileSystem
from pantheon.logger import Log
from pantheon.path import PantheonPath
from pantheon.path_security import (
    PathSecurityError,
    validate_directory_param,
    validate_import_path,
    validate_path_safety,
    validate_section_path,
)

from .process_handler import CreatedFileType

# Configuration keys and directory names as constants
PROJECT_MARKER_FILE = ".pantheon_project"
CONFIG_KEY_ACTIVE_TEAM = "active_team"
CONFIG_KEY_artifacts_root = "artifacts_root"
DEFAULT_artifacts_root = "pantheon-artifacts"
# Audit configuration keys and defaults
CONFIG_KEY_AUDIT_ENABLED = "audit_enabled"
CONFIG_KEY_AUDIT_DIRECTORY = "audit_directory"
CONFIG_KEY_TEMP_FILE_CLEANUP = "temp_file_cleanup"
DEFAULT_AUDIT_DIRECTORY = "pantheon-audit"
DEFAULT_TEMP_FILE_CLEANUP = "always"
TEAMS_DIR = "pantheon-teams"
PROCESSES_SUBDIR = "processes"
AGENTS_SUBDIR = "agents"
CONFIG_DIR = "config"
TEMP_SUBDIR = "temp"
AGENT_FILE_EXTENSION = ".md"
CONFIG_FILE_EXTENSION = ".yaml"

# Process file constants
SCHEMA_FILENAME = "schema.jsonnet"
ROUTINE_FILENAME = "routine.md"
REDIRECT_FILENAME = "redirect.md"
TEAM_PROFILE_FILENAME = "team-profile.yaml"
CONTEXT_TEMPLATE_FILENAME = "context.md"
CONTEXT_SCHEMA_FILENAME = "context-schema.jsonnet"
PERMISSIONS_FILENAME = "permissions.jsonnet"
BUILD_SCHEMA_FILENAME = "build-schema.jsonnet"
DIRECTORY_TEMPLATE_FILENAME = "directory.jinja"
JSONL_NAMING_TEMPLATE_FILENAME = "jsonl_naming.jinja"
JSONL_PLACEMENT_TEMPLATE_FILENAME = "jsonl_placement.jinja"
DEFAULT_GET_ROUTINE = "get-process-routine.md"
DEFAULT_UPDATE_ROUTINE = "update-process-routine.md"
DEFAULT_CREATE_ROUTINE = "create-process-routine.md"

# Artifact directory and file constants
ARTIFACT_SUBDIR = "artifact"


class ArtifactCreate(Enum):
    """Operation-specific filenames for CREATE operations that generate new artifacts."""

    PLACEMENT = "placement.jinja"  # Directory template for artifact placement
    NAMING = "naming.jinja"  # Filename template for artifact naming
    CONTENT = "content.md"  # Template for artifact content


class ArtifactRetrieve(Enum):
    """Operation-specific filenames for RETRIEVE operations that find existing artifacts."""

    LOCATOR = "locator.jsonnet"  # Configuration for finding artifacts
    PARSER = "parser.jsonnet"  # Normalization rules for artifact parsing
    SECTIONS = "sections.jsonnet"  # Section markers for structured documents


class ArtifactUpdate(Enum):
    """Operation-specific filenames for UPDATE operations that modify artifact sections."""

    LOCATOR = (
        "locator.jsonnet"  # Configuration for finding artifacts (shared with RETRIEVE)
    )
    PARSER = "parser.jsonnet"  # Normalization rules for artifact parsing (shared with RETRIEVE)
    TARGET = "target.jsonnet"  # Section bounds definition for targeted updates
    PATCH = "patch.md"  # Content template for section replacement


# URI prefixes
PROCESS_URI_PREFIX = "process://"


class SecurityError(Exception):
    """Raised when a path operation violates security constraints."""


class ProjectConfig(TypedDict, total=False):
    """Type definition for .pantheon_project configuration.

    Attributes:
        active_team: The currently active team identifier
        artifacts_root: The root directory for generated artifacts
        log_level: Optional log level configuration (DEBUG, INFO, WARNING, ERROR)
        audit_enabled: Whether CLI audit logging is enabled
        audit_directory: Directory under artifacts_root reserved for audit logs
        temp_file_cleanup: When to clean up temporary files (always, on_failure, never)
    """

    active_team: str
    artifacts_root: str
    log_level: str
    audit_enabled: bool
    audit_directory: str
    temp_file_cleanup: str


class PantheonWorkspace:
    """Facade for all filesystem operations and project conventions.

    The PantheonWorkspace serves as the central hub for filesystem operations
    in the Pantheon Framework. It encapsulates project discovery logic,
    convention-based path resolution, sandboxed artifact management, and
    security validation.

    This class follows the Facade pattern by providing a simplified interface
    to complex filesystem operations. It uses Dependency Injection to accept
    a FileSystem instance, enabling complete testability through mocking.

    The workspace is the only component authorized to unwrap PantheonPath
    objects and perform actual I/O operations, maintaining architectural
    boundaries while enabling practical filesystem operations.

    Attributes:
        _project_root: The root directory of the Pantheon project
        _artifacts_root: The sandboxed directory for generated artifacts
        _filesystem: The injected FileSystem dependency for I/O operations
        _project_config: Configuration from .pantheon_project file
    """

    def __init__(
        self,
        project_root: str,
        artifacts_root: str,
        filesystem: FileSystem,
    ) -> None:
        """Initialize the workspace with project boundaries and I/O dependency.

        This constructor serves as the architectural boundary between the "outside
        world" of raw filesystem paths and the "inside world" of safe PantheonPath
        abstractions. It takes untrusted string paths from the outside and
        establishes the secure sandbox boundaries.

        Args:
            project_root: Root directory path of the Pantheon project (raw string)
            artifacts_root: Output directory path for generated artifacts (raw string)
            filesystem: FileSystem instance for dependency injection

        The constructor immediately converts the raw string paths into internal
        pathlib.Path representations and establishes the workspace boundaries.
        From this point forward, all operations use safe PantheonPath abstractions.
        """
        # Convert raw outside-world strings to internal path representations
        # These are absolute root paths, not relative PantheonPaths
        self._project_root = Path(project_root).resolve()
        self._artifacts_root = (self._project_root / artifacts_root).resolve()
        self._filesystem = filesystem

        Log.debug(f"Workspace initialized with project_root: {self._project_root}")
        Log.debug(f"Workspace initialized with _artifacts_root: {self._artifacts_root}")

        # Load project configuration to get active_team
        self._project_config = self.load_project_config(filesystem, project_root)
        # Normalize audit config defaults
        if CONFIG_KEY_AUDIT_ENABLED not in self._project_config:
            self._project_config[CONFIG_KEY_AUDIT_ENABLED] = False
        if CONFIG_KEY_AUDIT_DIRECTORY not in self._project_config:
            self._project_config[CONFIG_KEY_AUDIT_DIRECTORY] = DEFAULT_AUDIT_DIRECTORY

    @classmethod
    def discover_project_root(
        cls, filesystem: FileSystem, start_path: str
    ) -> str | None:
        """Discover the project root by searching for .pantheon_project marker.

        This class method operates in the "outside world" of raw filesystem paths.
        It searches from the given start path upward through the directory tree
        until finding a .pantheon_project marker file. This enables project
        discovery before workspace instantiation.

        Args:
            filesystem: FileSystem instance for checking file existence
            start_path: Directory path to start searching from (raw string)

        Returns:
            Raw string path to the discovered project root, or None if not found

        The search traverses up the directory tree from start_path until either
        finding the marker file or reaching the filesystem root. Returns raw
        string paths suitable for passing to the workspace constructor.
        """
        from pathlib import Path

        current_path = Path(start_path).resolve()

        while True:
            marker_path = current_path / PROJECT_MARKER_FILE
            if filesystem.exists(marker_path):
                return str(current_path)

            parent = current_path.parent
            if parent == current_path:  # Reached filesystem root
                break
            current_path = parent

        return None

    @classmethod
    def load_project_config(
        cls, filesystem: FileSystem, project_root: str
    ) -> ProjectConfig:
        """Load project configuration from .pantheon_project file.

        Reads and parses the .pantheon_project YAML file from the project root.
        This is used by CLI to get configuration before workspace instantiation
        and by the workspace constructor to set up active team context.

        Args:
            filesystem: FileSystem instance for reading the config file
            project_root: Root directory path of the Pantheon project

        Returns:
            ProjectConfig dictionary with active_team and artifacts_root

        Raises:
            FileNotFoundError: If .pantheon_project doesn't exist
            ValueError: If configuration is missing required keys
        """
        config_path = Path(project_root) / PROJECT_MARKER_FILE

        if not filesystem.exists(config_path):
            Log.warning(
                f"No {PROJECT_MARKER_FILE} found at {config_path}, using defaults"
            )
            # Return sensible defaults if config doesn't exist
            return ProjectConfig(
                active_team="",
                artifacts_root=DEFAULT_artifacts_root,
                audit_enabled=False,
                audit_directory=DEFAULT_AUDIT_DIRECTORY,
                temp_file_cleanup=DEFAULT_TEMP_FILE_CLEANUP,
            )

        try:
            config_text = filesystem.read_text(config_path)
            config_data = yaml.safe_load(config_text)

            # Ensure required keys exist with defaults
            config = ProjectConfig(
                active_team=config_data.get(CONFIG_KEY_ACTIVE_TEAM, ""),
                artifacts_root=config_data.get(
                    CONFIG_KEY_artifacts_root, DEFAULT_artifacts_root
                ),
                audit_enabled=bool(config_data.get(CONFIG_KEY_AUDIT_ENABLED, False)),
                audit_directory=str(
                    config_data.get(CONFIG_KEY_AUDIT_DIRECTORY, DEFAULT_AUDIT_DIRECTORY)
                ),
                temp_file_cleanup=str(
                    config_data.get(
                        CONFIG_KEY_TEMP_FILE_CLEANUP, DEFAULT_TEMP_FILE_CLEANUP
                    )
                ),
            )

            # Add optional log_level if present and valid
            if "log_level" in config_data:
                log_level = config_data["log_level"].upper()
                if log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
                    config["log_level"] = log_level

            return config
        except Exception as e:
            Log.error(f"Failed to load {PROJECT_MARKER_FILE}: {e}")
            # Return defaults on error
            return ProjectConfig(
                active_team="",
                artifacts_root=DEFAULT_artifacts_root,
                audit_enabled=False,
                audit_directory=DEFAULT_AUDIT_DIRECTORY,
                temp_file_cleanup=DEFAULT_TEMP_FILE_CLEANUP,
            )

    def _get_active_team_root(self) -> Path:
        """Get the absolute path to the active team's directory.

        Computes the sandbox path for the active team based on the
        pantheon-teams/<active_team>/ convention. This is the boundary
        for process:// URI resolution.

        Returns:
            Path object for pantheon-teams/<active_team>/ directory

        Raises:
            ValueError: If active_team is not set in configuration
        """
        active_team = self._project_config["active_team"]
        if not active_team:
            raise ValueError(
                f"No {CONFIG_KEY_ACTIVE_TEAM} configured in {PROJECT_MARKER_FILE}"
            )

        return self._project_root / TEAMS_DIR / active_team

    def save_artifact(
        self,
        content: str,
        path: PantheonPath,
    ) -> PantheonPath:
        """Save content as an artifact to the sandboxed output directory.

        Core method for persisting generated artifacts to the sandboxed output
        directory. Validates paths for security, creates parent directories as
        needed, and writes content through the FileSystem.

        This method enforces sandboxing by ensuring all paths remain within
        the artifacts_root boundary and prevents directory traversal attacks.

        Args:
            content: Text content to save as the artifact
            path: Target path for the artifact within the sandbox

        Returns:
            PantheonPath to the saved artifact location

        Raises:
            SecurityError: If path attempts to escape the sandbox
            PermissionError: If write access is denied
            FileNotFoundError: If parent directory creation fails

        Examples:
            workspace.save_artifact("Hello", PantheonPath("output/test.txt"))
        """
        # Validate path security to prevent traversal attacks
        self._validate_path_security(path)

        # Ensure path is within output root sandbox
        absolute_path = self._artifacts_root / path.get_underlying_path()

        # Prevent writes into audit directory from general artifact operations
        audit_dir = self._artifacts_root / self._project_config.get(
            CONFIG_KEY_AUDIT_DIRECTORY, DEFAULT_AUDIT_DIRECTORY
        )
        try:
            # Resolve to handle any relative elements safely
            abs_resolved = absolute_path.resolve()
            if str(abs_resolved).startswith(str(audit_dir.resolve())):
                raise SecurityError("Writes to audit directory are not permitted")
        except Exception as err:
            # If resolution fails, be conservative and block
            raise SecurityError(
                "Invalid artifact path; potential attempt to access audit directory"
            ) from err

        # Create parent directories as needed
        parent_path = absolute_path.parent
        if not self._filesystem.exists(parent_path):
            self._filesystem.mkdir(parent_path, parents=True, exist_ok=True)

        # Write content through FileSystem dependency
        self._filesystem.write_text(absolute_path, content)

        return PantheonPath(str(absolute_path.relative_to(self._artifacts_root)))

    def append_jsonl_entry(
        self,
        data: dict[str, Any],
        path: PantheonPath,
    ) -> PantheonPath:
        """Append a JSON object as a line to a JSONL file.

        Serializes the provided data dictionary to a JSON string and appends it
        as a new line to the specified JSONL file. Creates the file if it doesn't
        exist. Enforces the same sandboxing security as save_artifact.

        Args:
            data: Dictionary to serialize as JSON and append
            path: Target path for the JSONL file within the sandbox

        Returns:
            PantheonPath to the JSONL file location

        Raises:
            SecurityError: If path attempts to escape the sandbox
            PermissionError: If write access is denied
            FileNotFoundError: If parent directory creation fails
            TypeError: If data cannot be serialized to JSON

        Examples:
            workspace.append_jsonl_entry(
                {"user": "alice", "action": "submit_feedback"},
                PantheonPath("logs/feedback.jsonl")
            )
        """
        import json as _json

        # Validate path security to prevent traversal attacks
        self._validate_path_security(path)

        # Ensure path is within output root sandbox
        absolute_path = self._artifacts_root / path.get_underlying_path()

        # Prevent writes into audit directory from general artifact operations
        audit_dir = self._artifacts_root / self._project_config.get(
            CONFIG_KEY_AUDIT_DIRECTORY, DEFAULT_AUDIT_DIRECTORY
        )
        try:
            # Resolve to handle any relative elements safely
            abs_resolved = absolute_path.resolve()
            if str(abs_resolved).startswith(str(audit_dir.resolve())):
                raise SecurityError("Writes to audit directory are not permitted")
        except Exception as err:
            # If resolution fails, be conservative and block
            raise SecurityError(
                "Invalid JSONL path; potential attempt to access audit directory"
            ) from err

        # Create parent directories as needed
        parent_path = absolute_path.parent
        if not self._filesystem.exists(parent_path):
            self._filesystem.mkdir(parent_path, parents=True, exist_ok=True)

        # Serialize data and append as JSONL entry
        json_line = _json.dumps(data, ensure_ascii=False)
        self._filesystem.append_text(absolute_path, json_line + "\n")

        return PantheonPath(str(absolute_path.relative_to(self._artifacts_root)))

    def create_tempfile(
        self,
        suffix: str | None = None,
        prefix: str | None = None,
    ) -> PantheonPath:
        """Create unique temporary file path within the sandbox.

        Creates unique temporary file paths within the sandboxed output
        directory for intermediate processing. Returns path without creating
        the file, allowing components to write when ready.

        Args:
            suffix: Optional file suffix (e.g., ".txt", ".json")
            prefix: Optional file prefix for identification

        Returns:
            PantheonPath to unique temporary location within artifacts_root

        Examples:
            temp_path = workspace.create_tempfile(suffix=".json")
            log_path = workspace.create_tempfile(prefix="build_", suffix=".log")
        """
        # Generate unique identifier
        unique_id = str(uuid.uuid4())

        # Construct filename with optional prefix/suffix
        filename_parts = []

        from datetime import datetime

        filename_parts.append(datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M"))

        if prefix:
            filename_parts.append(prefix)

        filename_parts.append(unique_id)

        filename = "_".join(filename_parts)
        if suffix:
            filename += suffix

        # Create path within temp subdirectory of output root
        return PantheonPath(TEMP_SUBDIR, filename)

    def cleanup_temp_file(self, file_path: str, execution_success: bool) -> None:
        """Clean up temporary file based on configured policy.

        Checks if the provided file path is within the temp directory and
        cleans it up according to the temp_file_cleanup policy configuration.

        Args:
            file_path: String path to the file that may need cleanup
            execution_success: Whether the process execution was successful

        Policy Values:
            "always": Clean up temp files after every execution (default)
            "on_failure": Only clean up temp files if execution failed
            "never": Never clean up temp files
        """
        try:
            # Convert string to Path for checking
            path_obj = Path(file_path)

            # Check if file is within temp directory
            temp_dir = self._artifacts_root / TEMP_SUBDIR
            temp_dir_resolved = temp_dir.resolve()

            # Resolve the file path to handle relative paths correctly
            try:
                file_path_resolved = path_obj.resolve()
            except (OSError, ValueError):
                # Path doesn't exist or is invalid - nothing to clean up
                Log.debug(
                    f"Temp cleanup: file path '{file_path}' does not exist or is invalid"
                )
                return

            # Check if file is actually within temp directory
            try:
                file_path_resolved.relative_to(temp_dir_resolved)
            except ValueError:
                # File is not within temp directory - don't clean up
                Log.debug(
                    f"Temp cleanup: file '{file_path}' is not in temp directory, skipping cleanup"
                )
                return

            # Get cleanup policy from configuration
            cleanup_policy = self._project_config.get(
                CONFIG_KEY_TEMP_FILE_CLEANUP, DEFAULT_TEMP_FILE_CLEANUP
            )

            # Determine if we should clean up based on policy
            should_cleanup = False
            if cleanup_policy == "always":
                should_cleanup = True
                Log.debug(
                    f"Temp cleanup: policy 'always' - will clean up '{file_path}'"
                )
            elif cleanup_policy == "on_failure":
                should_cleanup = not execution_success
                if should_cleanup:
                    Log.debug(
                        f"Temp cleanup: policy 'on_failure' and execution failed - will clean up '{file_path}'"
                    )
                else:
                    Log.debug(
                        f"Temp cleanup: policy 'on_failure' and execution succeeded - keeping '{file_path}'"
                    )
            elif cleanup_policy == "never":
                should_cleanup = False
                Log.debug(f"Temp cleanup: policy 'never' - keeping '{file_path}'")
            else:
                # Unknown policy, default to safe behavior (always clean up)
                should_cleanup = True
                Log.warning(
                    f"Temp cleanup: unknown policy '{cleanup_policy}', defaulting to 'always' - will clean up '{file_path}'"
                )

            # Perform cleanup if needed
            if should_cleanup:
                self._filesystem.unlink(path_obj, missing_ok=True)
                Log.debug(f"Temp cleanup: successfully removed '{file_path}'")

        except Exception as e:
            # Never let cleanup failure affect the main operation
            Log.warning(f"Temp cleanup: failed to clean up '{file_path}': {e}")

    def _validate_path_security(self, path: PantheonPath) -> None:
        """Validate path security to prevent directory traversal attacks.

        Internal security method that validates all paths remain within
        project boundaries. Prevents malicious path constructions that
        could escape the sandbox through traversal sequences.

        Args:
            path: PantheonPath to validate for security

        Raises:
            SecurityError: If path contains traversal sequences or
                          attempts to escape the sandbox

        This method checks for:
        - Directory traversal sequences (..)
        - Absolute paths that might escape the sandbox
        - URL-encoded and Unicode-encoded traversal attempts
        - Other path manipulation attempts
        """
        # Use centralized path security validation
        try:
            validate_path_safety(
                str(path), allow_absolute=False, context="artifact path"
            )
        except PathSecurityError as e:
            # Convert to SecurityError for backward compatibility
            raise SecurityError(str(e)) from e

    def get_team_package_path(self, team: str | None = None) -> PantheonPath:
        """Resolve team package directory path based on naming conventions.

        Constructs path to team-specific directory where team processes and
        configurations are stored. Follows the standardized team package
        structure under the pantheon-teams directory.

        Args:
            team: Team identifier (directory name). If None, uses active_team.

        Returns:
            PantheonPath to the team package directory

        Examples:
            team_path = workspace.get_team_package_path("backend-team")
            # Returns: pantheon-teams/backend-team/

            active_path = workspace.get_team_package_path()  # Uses active_team
            # Returns: pantheon-teams/<active_team>/
        """
        if team is None:
            team = self._project_config["active_team"]
            if not team:
                raise ValueError(
                    f"No team specified and no {CONFIG_KEY_ACTIVE_TEAM} configured"
                )
        return PantheonPath(TEAMS_DIR, team)

    def _build_process_path(self, process_name: str, *path_parts: str) -> Path:
        """Build absolute path to process file within active team directory.

        Constructs complete filesystem path for process-related files by combining
        the active team root with process directory structure and provided path parts.

        Args:
            process_name: Name of the process (e.g., "create-ticket")
            *path_parts: Additional path components (e.g., "artifact", "finder.jsonnet")

        Returns:
            Path object for the complete absolute path to the process file

        Examples:
            _build_process_path("create-ticket", "schema.jsonnet")
            # Returns: /project/pantheon-teams/active-team/processes/create-ticket/schema.jsonnet

            _build_process_path("update-plan", "artifact", "finder.jsonnet")
            # Returns: /project/pantheon-teams/active-team/processes/update-plan/artifact/finder.jsonnet
        """
        team_root = self._get_active_team_root()
        return team_root / PROCESSES_SUBDIR / process_name / Path(*path_parts)

    def _build_team_path(self, *path_parts: str) -> Path:
        """Build absolute path within active team directory.

        Constructs complete filesystem path for team-level files by combining
        the active team root with provided path components.

        Args:
            *path_parts: Path components within team directory

        Returns:
            Path object for the complete absolute path within team

        Examples:
            _build_team_path("team-profile.yaml")
            # Returns: /project/pantheon-teams/active-team/team-profile.yaml

            _build_team_path("agents", "tech-lead.md")
            # Returns: /project/pantheon-teams/active-team/agents/tech-lead.md
        """
        team_root = self._get_active_team_root()
        return team_root / Path(*path_parts)

    # Content-Retrieval Methods
    def get_process_schema(self, process_name: str) -> str:
        """Returns preprocessed schema content for a process, handling path construction and active team resolution.

        Retrieves the Jsonnet schema file for the specified process from the active team's
        process directory and preprocesses it to resolve all import statements. The schema
        defines the input contract for the process.

        Args:
            process_name: Name of the process (e.g., "create-ticket", "update-plan")

        Returns:
            String content of the schema.jsonnet file with all imports resolved

        Raises:
            FileNotFoundError: If the schema file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
            ValueError: If circular imports are detected
            RuntimeError: If import resolution fails
        """
        path = self._build_process_path(process_name, SCHEMA_FILENAME)
        raw_content = self._filesystem.read_text(path)
        return self._preprocess_content(raw_content, path)

    def get_process_schema_path(self, process_name: str) -> str:
        """Returns the filesystem path for a process schema file.

        Gets the absolute path to the schema.jsonnet file for the specified process
        from the active team's process directory. This is useful for providing
        directory context to Jsonnet compilation.

        Args:
            process_name: Name of the process (e.g., "create-ticket", "update-plan")

        Returns:
            Absolute path string to the schema.jsonnet file

        Raises:
            FileNotFoundError: If the process directory doesn't exist
        """
        path = self._build_process_path(process_name, SCHEMA_FILENAME)
        return str(path)

    def get_section_schema(self, process_name: str, section_path: str) -> str:
        """Returns preprocessed section schema content for a process.

        Retrieves the Jsonnet schema file for a specific section within a process's
        artifact directory and preprocesses it to resolve all import statements. Section
        schemas are used for modular schema composition in UPDATE processes.

        Convention: Section schemas are located at:
        processes/<process-name>/artifact/sections/<section-name>.schema.jsonnet

        Args:
            process_name: Name of the process (e.g., "update-architecture-guide")
            section_path: Path to the section schema relative to artifact/
                         (e.g., "sections/core-principles")

        Returns:
            String content of the section schema file with all imports resolved

        Raises:
            FileNotFoundError: If the section schema file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
            ValueError: If circular imports are detected or invalid section_path
            RuntimeError: If import resolution fails

        Examples:
            get_section_schema("update-guide", "sections/core-principles")
            # Returns content from: processes/update-guide/artifact/sections/core-principles.schema.jsonnet
        """
        # Validate section_path to prevent directory traversal
        validate_section_path(section_path)

        # Build path: processes/<process-name>/artifact/<section-path>.schema.jsonnet
        process_dir = self._build_process_path(process_name)
        section_file = f"{section_path}.schema.jsonnet"
        path = process_dir / "artifact" / section_file

        raw_content = self._filesystem.read_text(path)
        return self._preprocess_content(raw_content, path)

    def get_artifact_section_template(
        self, process_name: str, section_path: str
    ) -> str:
        """Returns section template content for artifact generation.

        Retrieves the Markdown template file for a specific section within a process's
        artifact directory. Section templates are used by CREATE processes to include
        content from UPDATE process section templates using semantic URI includes.

        Convention: Section templates are located at:
        processes/<process-name>/artifact/<section-path>.md

        This method is used by the custom Jinja2 loader (SemanticUriLoader) to resolve
        artifact-template:// semantic URIs in template include statements.

        Args:
            process_name: Name of the process (e.g., "update-architecture-guide")
            section_path: Path to the section template relative to artifact/
                         (e.g., "sections/core-principles")

        Returns:
            String content of the section template file

        Raises:
            FileNotFoundError: If the section template file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
            ValueError: If section_path contains directory traversal

        Examples:
            get_artifact_section_template("update-guide", "sections/core-principles")
            # Returns content from: processes/update-guide/artifact/sections/core-principles.md
        """
        # Validate section_path to prevent directory traversal
        validate_section_path(section_path)

        # Append .md extension if not present
        if not section_path.endswith(".md"):
            section_file = f"{section_path}.md"
        else:
            section_file = section_path

        # Build path: processes/<process-name>/artifact/<section-path>.md
        path = self._build_team_path(
            "processes", process_name, "artifact", section_file
        )

        # Read and return content directly (no preprocessing needed for markdown templates)
        return self._filesystem.read_text(path)

    def get_process_routine(self, process_name: str) -> str:
        """Returns routine content for a process.

        Retrieves the Markdown routine file for the specified process from the active team's
        process directory. The routine contains step-by-step instructions for agents.

        Args:
            process_name: Name of the process (e.g., "create-ticket", "update-plan")

        Returns:
            String content of the routine.md file

        Raises:
            FileNotFoundError: If the routine file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
        """
        path = self._build_process_path(process_name, ROUTINE_FILENAME)
        return self._filesystem.read_text(path)

    def get_process_directory(self, process_name: str) -> Path:
        """Return the absolute path to a process directory for template rendering."""

        return self._build_process_path(process_name)

    def check_process_exists(self, process_name: str) -> None:
        """Check if a process exists by verifying its routine file.

        Validates that the specified process exists by checking for its routine.md file.
        This is a lightweight validation method for early error checking.

        Args:
            process_name: Name of the process to check (e.g., "create-ticket", "update-plan")

        Raises:
            FileNotFoundError: If the process doesn't exist (routine file not found)
            PermissionError: If read access is denied to the process directory
        """
        path = self._build_process_path(process_name, ROUTINE_FILENAME)
        if not self._filesystem.exists(path):
            raise FileNotFoundError(f"Process '{process_name}' not found")

    def has_process_redirect(self, process_name: str) -> bool:
        """Check if a process has a redirect.md file indicating redirection behavior.

        Args:
            process_name: Name of the process to check for redirect

        Returns:
            True if redirect.md exists for the process, False otherwise

        Examples:
            has_redirect = workspace.has_process_redirect("get-plan")
        """
        redirect_path = self._build_process_path(process_name, REDIRECT_FILENAME)
        return self._filesystem.exists(redirect_path)

    def get_process_redirect(self, process_name: str) -> str:
        """Retrieve redirect URI content from redirect.md file.

        Args:
            process_name: Name of the process to get redirect URI for

        Returns:
            Redirect URI string with whitespace stripped

        Raises:
            FileNotFoundError: If redirect.md file does not exist

        Examples:
            uri = workspace.get_process_redirect("get-plan")
            # Returns: "process://get-ticket?sections=plan"
        """
        redirect_path = self._build_process_path(process_name, REDIRECT_FILENAME)
        redirect_content = self._filesystem.read_text(redirect_path)
        return redirect_content.strip()

    def get_artifact_parser(self, process_name: str) -> str:
        """Returns preprocessed normalizer rules for artifact finding.

        Retrieves the Jsonnet normalizer rules for the specified process and preprocesses
        them to resolve all import statements. These rules define regex transformations
        to normalize fuzzy artifact IDs into canonical form.
        Uses the new RETRIEVE operation naming convention (parser.jsonnet).

        Args:
            process_name: Name of the process (e.g., "get-ticket")

        Returns:
            String content of the artifact/parser.jsonnet file with all imports resolved

        Raises:
            FileNotFoundError: If the parser.jsonnet file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
            ValueError: If circular imports are detected
            RuntimeError: If import resolution fails
        """
        path = self._build_process_path(
            process_name, ARTIFACT_SUBDIR, ArtifactRetrieve.PARSER.value
        )
        raw_content = self._filesystem.read_text(path)
        return self._preprocess_content(raw_content, path)

    def get_artifact_locator(self, process_name: str) -> str:
        """Returns preprocessed finder pattern templates.

        Retrieves the Jsonnet finder pattern for the specified process and preprocesses
        it to resolve all import statements. The finder defines regex patterns used to
        locate artifact files by canonical ID.
        Uses the new RETRIEVE operation naming convention (locator.jsonnet).

        Args:
            process_name: Name of the process (e.g., "get-ticket")

        Returns:
            String content of the artifact/locator.jsonnet file with all imports resolved

        Raises:
            FileNotFoundError: If the locator.jsonnet file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
            ValueError: If circular imports are detected
            RuntimeError: If import resolution fails
        """
        path = self._build_process_path(
            process_name, ARTIFACT_SUBDIR, ArtifactRetrieve.LOCATOR.value
        )
        raw_content = self._filesystem.read_text(path)
        return self._preprocess_content(raw_content, path)

    def get_artifact_section_markers(self, process_name: str) -> str:
        """Returns preprocessed section marker definitions.

        Retrieves the Jsonnet marker definitions for the specified process and preprocesses
        them to resolve all import statements. These markers define the HTML comment patterns
        used to delimit sections within artifacts.
        Uses the new RETRIEVE operation naming convention (sections.jsonnet).

        Args:
            process_name: Name of the process (e.g., "get-ticket")

        Returns:
            String content of the artifact/sections.jsonnet file with all imports resolved

        Raises:
            FileNotFoundError: If the sections.jsonnet file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
            ValueError: If circular imports are detected
            RuntimeError: If import resolution fails
        """
        path = self._build_process_path(
            process_name, ARTIFACT_SUBDIR, ArtifactRetrieve.SECTIONS.value
        )
        raw_content = self._filesystem.read_text(path)
        return self._preprocess_content(raw_content, path)

    # --- BUILD operation helpers (process-root files) ---
    def has_build_schema(self, process_name: str) -> bool:
        """Check if a process provides a BUILD schema at its root.

        Looks for a conventional build schema file alongside schema.jsonnet to
        identify BUILD-type processes.

        Args:
            process_name: Name of the process (e.g., "build-team-process")

        Returns:
            True if build-schema.jsonnet exists at the process root; False otherwise
        """
        path = self._build_process_path(process_name, BUILD_SCHEMA_FILENAME)
        return self._filesystem.exists(path)

    def get_process_directory_template(self, process_name: str) -> str:
        """Returns the root-level directory template for BUILD operations.

        Retrieves the directory template from the process root. This template
        determines the top-level directory under the artifacts sandbox where
        the BUILD output bundle will be staged.

        Args:
            process_name: Name of the process (e.g., "build-team-process")

        Returns:
            String content of the directory.jinja file at the process root

        Raises:
            FileNotFoundError: If the directory.jinja file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
        """
        path = self._build_process_path(process_name, DIRECTORY_TEMPLATE_FILENAME)
        return self._filesystem.read_text(path)

    def copy_default_get_routine(
        self,
        target_path: PantheonPath,
        enhanced_parameters: dict[str, Any] | None = None,
    ) -> PantheonPath:
        """Copy bundled GET routine boilerplate to target PantheonPath with Jinja rendering.

        Reads the packaged template from pantheon/_templates/routines and saves it
        into the artifacts sandbox at the provided PantheonPath.

        Args:
            target_path: Destination path (within artifacts sandbox)
            enhanced_parameters: Optional parameters for Jinja template rendering

        Returns:
            PantheonPath where the routine was written
        """
        try:
            template_content = self._filesystem.read_bundled_resource(
                "pantheon", f"_templates/routines/{DEFAULT_GET_ROUTINE}"
            )

            # Render Jinja template if enhanced_parameters provided
            if enhanced_parameters:
                try:
                    from pantheon.artifact_engine import ArtifactEngine

                    # Create a minimal context for template rendering
                    context = enhanced_parameters.copy()
                    # Create temporary ArtifactEngine instance for template rendering
                    temp_engine = ArtifactEngine(workspace=self)
                    rendered_content = temp_engine.render_template(
                        template_content, context
                    )
                    return self.save_artifact(rendered_content, target_path)
                except Exception as render_error:
                    Log.warning(
                        f"Failed to render GET routine template: {render_error}"
                    )
                    # Fall back to raw template content
                    return self.save_artifact(template_content, target_path)
            else:
                # No parameters provided, use raw template
                return self.save_artifact(template_content, target_path)

        except Exception as e:
            Log.warning(f"Failed to copy default GET routine: {e}")
            # Fallback to minimal stub
            return self.save_artifact(
                "# Routine: GET Process\n\nReturn sections from an artifact.\n",
                target_path,
            )

    def copy_default_update_routine(
        self,
        target_path: PantheonPath,
        enhanced_parameters: dict[str, Any] | None = None,
    ) -> PantheonPath:
        """Copy bundled UPDATE routine boilerplate to target PantheonPath with Jinja rendering.

        Args:
            target_path: Destination path (within artifacts sandbox)
            enhanced_parameters: Optional parameters for Jinja template rendering

        Returns:
            PantheonPath where the routine was written
        """
        try:
            template_content = self._filesystem.read_bundled_resource(
                "pantheon", f"_templates/routines/{DEFAULT_UPDATE_ROUTINE}"
            )

            # Render Jinja template if enhanced_parameters provided
            if enhanced_parameters:
                try:
                    from pantheon.artifact_engine import ArtifactEngine

                    # Create a minimal context for template rendering
                    context = enhanced_parameters.copy()
                    # Create temporary ArtifactEngine instance for template rendering
                    temp_engine = ArtifactEngine(workspace=self)
                    rendered_content = temp_engine.render_template(
                        template_content, context
                    )
                    return self.save_artifact(rendered_content, target_path)
                except Exception as render_error:
                    Log.warning(
                        f"Failed to render UPDATE routine template: {render_error}"
                    )
                    # Fall back to raw template content
                    return self.save_artifact(template_content, target_path)
            else:
                # No parameters provided, use raw template
                return self.save_artifact(template_content, target_path)

        except Exception as e:
            Log.warning(f"Failed to copy default UPDATE routine: {e}")
            # Fallback to minimal stub
            return self.save_artifact(
                "# Routine: UPDATE Process\n\nReplace content of a target section.\n",
                target_path,
            )

    def copy_default_create_routine(
        self,
        target_path: PantheonPath,
        enhanced_parameters: dict[str, Any] | None = None,
    ) -> PantheonPath:
        """Copy bundled CREATE routine boilerplate to target PantheonPath with Jinja rendering."""
        try:
            template_content = self._filesystem.read_bundled_resource(
                "pantheon", f"_templates/routines/{DEFAULT_CREATE_ROUTINE}"
            )

            # Render Jinja template if enhanced_parameters provided
            if enhanced_parameters:
                try:
                    from pantheon.artifact_engine import ArtifactEngine

                    # Create a minimal context for template rendering
                    context = enhanced_parameters.copy()
                    # Create temporary ArtifactEngine instance for template rendering
                    temp_engine = ArtifactEngine(workspace=self)
                    rendered_content = temp_engine.render_template(
                        template_content, context
                    )
                    return self.save_artifact(rendered_content, target_path)
                except Exception as render_error:
                    Log.warning(
                        f"Failed to render CREATE routine template: {render_error}"
                    )
                    # Fall back to raw template content
                    return self.save_artifact(template_content, target_path)
            else:
                # No parameters provided, use raw template
                return self.save_artifact(template_content, target_path)

        except Exception as e:
            Log.warning(f"Failed to copy default CREATE routine: {e}")
            return self.save_artifact(
                "# Routine: CREATE Process\n\nRender a new artifact from structured input.\n",
                target_path,
            )

    # --- High-level scaffolding helpers for BUILD operations ---
    def scaffold_create_process(
        self,
        bundle_root: PantheonPath,
        process_name: str,
        content_md: str,
        placement_jinja: str,
        naming_jinja: str,
        schema_jsonnet: str,
        permissions_jsonnet: str | None = None,
        include_default_routine: bool = True,
        enhanced_parameters: dict[str, Any] | None = None,
    ) -> list[PantheonPath]:
        """Create a CREATE process folder with canonical files under bundle_root.

        Returns list of PantheonPath objects that were written.
        """
        written: list[PantheonPath] = []
        proc_root = bundle_root.joinpath(process_name)

        # artifact/content.md
        try:
            written.append(
                self.save_artifact(
                    content_md, proc_root.joinpath("artifact", "content.md")
                )
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to scaffold CREATE content.md for {process_name}: {e}"
            ) from e
        # artifact/placement.jinja and artifact/naming.jinja
        try:
            written.append(
                self.save_artifact(
                    placement_jinja,
                    proc_root.joinpath("artifact", "placement.jinja"),
                )
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to scaffold CREATE placement.jinja for {process_name}: {e}"
            ) from e
        try:
            written.append(
                self.save_artifact(
                    naming_jinja, proc_root.joinpath("artifact", "naming.jinja")
                )
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to scaffold CREATE naming.jinja for {process_name}: {e}"
            ) from e
        # schema.jsonnet
        try:
            written.append(
                self.save_artifact(schema_jsonnet, proc_root.joinpath("schema.jsonnet"))
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to scaffold CREATE schema.jsonnet for {process_name}: {e}"
            ) from e
        # permissions.jsonnet (optional)
        if permissions_jsonnet is not None:
            try:
                written.append(
                    self.save_artifact(
                        permissions_jsonnet,
                        proc_root.joinpath("permissions.jsonnet"),
                    )
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to scaffold CREATE permissions.jsonnet for {process_name}: {e}"
                ) from e
        # routine.md
        if include_default_routine:
            written.append(
                self.copy_default_create_routine(
                    proc_root.joinpath("routine.md"), enhanced_parameters
                )
            )

        return written

    def scaffold_get_process(
        self,
        bundle_root: PantheonPath,
        process_name: str,
        sections_json: str | None,
        locator_jsonnet: str,
        parser_jsonnet: str,
        permissions_jsonnet: str | None = None,
        include_default_routine: bool = True,
        enhanced_parameters: dict[str, Any] | None = None,
    ) -> list[PantheonPath]:
        """Create a GET process folder with canonical files under bundle_root."""
        written: list[PantheonPath] = []
        proc_root = bundle_root.joinpath(process_name)

        # Only create sections.jsonnet if sections_json is provided (multi-section case)
        if sections_json is not None:
            try:
                written.append(
                    self.save_artifact(
                        sections_json,
                        proc_root.joinpath("artifact", "sections.jsonnet"),
                    )
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to scaffold GET sections.jsonnet for {process_name}: {e}"
                ) from e
        try:
            written.append(
                self.save_artifact(
                    locator_jsonnet, proc_root.joinpath("artifact", "locator.jsonnet")
                )
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to scaffold GET locator.jsonnet for {process_name}: {e}"
            ) from e
        try:
            written.append(
                self.save_artifact(
                    parser_jsonnet, proc_root.joinpath("artifact", "parser.jsonnet")
                )
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to scaffold GET parser.jsonnet for {process_name}: {e}"
            ) from e
        if permissions_jsonnet is not None:
            try:
                written.append(
                    self.save_artifact(
                        permissions_jsonnet, proc_root.joinpath("permissions.jsonnet")
                    )
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to scaffold GET permissions.jsonnet for {process_name}: {e}"
                ) from e
        if include_default_routine:
            written.append(
                self.copy_default_get_routine(
                    proc_root.joinpath("routine.md"), enhanced_parameters
                )
            )

        return written

    def scaffold_update_process(
        self,
        bundle_root: PantheonPath,
        process_name: str,
        target_jsonnet: str | None,
        locator_jsonnet: str,
        parser_jsonnet: str,
        patch_md: str,
        schema_jsonnet: str,
        permissions_jsonnet: str | None = None,
        include_default_routine: bool = True,
        enhanced_parameters: dict[str, Any] | None = None,
    ) -> list[PantheonPath]:
        """Create an UPDATE process folder with canonical files under bundle_root."""
        written: list[PantheonPath] = []
        proc_root = bundle_root.joinpath(process_name)

        # Only create target.jsonnet if target_jsonnet is provided (multi-section case)
        if target_jsonnet is not None:
            try:
                written.append(
                    self.save_artifact(
                        target_jsonnet, proc_root.joinpath("artifact", "target.jsonnet")
                    )
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to scaffold UPDATE target.jsonnet for {process_name}: {e}"
                ) from e
        try:
            written.append(
                self.save_artifact(
                    locator_jsonnet, proc_root.joinpath("artifact", "locator.jsonnet")
                )
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to scaffold UPDATE locator.jsonnet for {process_name}: {e}"
            ) from e
        try:
            written.append(
                self.save_artifact(
                    parser_jsonnet, proc_root.joinpath("artifact", "parser.jsonnet")
                )
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to scaffold UPDATE parser.jsonnet for {process_name}: {e}"
            ) from e
        try:
            written.append(
                self.save_artifact(patch_md, proc_root.joinpath("artifact", "patch.md"))
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to scaffold UPDATE patch.md for {process_name}: {e}"
            ) from e
        try:
            written.append(
                self.save_artifact(schema_jsonnet, proc_root.joinpath("schema.jsonnet"))
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to scaffold UPDATE schema.jsonnet for {process_name}: {e}"
            ) from e
        if permissions_jsonnet is not None:
            try:
                written.append(
                    self.save_artifact(
                        permissions_jsonnet, proc_root.joinpath("permissions.jsonnet")
                    )
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to scaffold UPDATE permissions.jsonnet for {process_name}: {e}"
                ) from e
        if include_default_routine:
            written.append(
                self.copy_default_update_routine(
                    proc_root.joinpath("routine.md"), enhanced_parameters
                )
            )

        return written

    def get_artifact_sections(
        self, process_name: str, data_path: str | None = None
    ) -> str:
        """Returns artifact section data with optional data extraction.

        Retrieves section markers from the specified process and optionally extracts
        specific data using dot-notation paths (e.g., "sections.plan").

        Args:
            process_name: Name of the process (e.g., "get-ticket")
            data_path: Optional dot-notation path for data extraction

        Returns:
            JSON string of extracted data or raw sections content

        Raises:
            FileNotFoundError: If the sections.jsonnet file doesn't exist
            ValueError: If data extraction fails
        """
        # Get the raw sections content
        sections_content = self.get_artifact_section_markers(process_name)

        # If data parameter is specified, extract that part
        if data_path:
            from pantheon.artifact_engine import ArtifactEngine

            # Create a temporary artifact engine to use resolve_uri_data
            temp_engine = ArtifactEngine(self)
            extracted_data = temp_engine.resolve_uri_data(sections_content, data_path)

            # Return as JSON string for Jsonnet import
            import json

            return json.dumps(extracted_data)

        # Return the raw content if no data parameter
        return sections_content

    def get_artifact_content_template(self, process_name: str) -> str:
        """Returns artifact template content.

        Retrieves the Jinja2 template for the specified process. This template
        is used to render the final output artifact from structured data.
        Uses the new CREATE operation naming convention (content.md).

        Args:
            process_name: Name of the process (e.g., "create-ticket")

        Returns:
            String content of the artifact/content.md file

        Raises:
            FileNotFoundError: If the content.md file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
        """
        path = self._build_process_path(
            process_name, ARTIFACT_SUBDIR, ArtifactCreate.CONTENT.value
        )
        return self._filesystem.read_text(path)

    def get_artifact_template_environment(
        self, process_name: str
    ) -> jinja2.Environment:
        """Returns configured Jinja2 environment for process artifact templates with include support.

        Creates a Jinja2 environment configured with FileSystemLoader pointing to the
        process's artifact directory, enabling include statements in content.md templates.
        Includes all standard template settings and custom filters used by the framework.

        Args:
            process_name: Name of the process (e.g., "create-ticket")

        Returns:
            Configured Jinja2 Environment with FileSystemLoader for artifact directory

        Raises:
            FileNotFoundError: If the process artifact directory doesn't exist

        Examples:
            env = workspace.get_artifact_template_environment("create-routine")
            template = env.from_string(template_content)
            rendered = template.render(context)
        """
        # Get the absolute path to the process artifact directory
        artifact_dir = self._build_process_path(process_name, ARTIFACT_SUBDIR)

        # Create FileSystemLoader pointing to the artifact directory
        loader = jinja2.FileSystemLoader(str(artifact_dir))

        # Create environment with same settings as ArtifactEngine
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

    def get_artifact_target_section(self, process_name: str) -> str:
        """Returns preprocessed target section bounds definition for UPDATE operations.

        Retrieves the Jsonnet target configuration for the specified process and preprocesses
        it to resolve all import statements. This defines the section bounds for targeted
        updates within artifacts.
        Uses the new UPDATE operation naming convention (target.jsonnet).

        Args:
            process_name: Name of the process (e.g., "update-plan")

        Returns:
            String content of the artifact/target.jsonnet file with all imports resolved

        Raises:
            FileNotFoundError: If the target.jsonnet file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
            ValueError: If circular imports are detected
            RuntimeError: If import resolution fails
        """
        path = self._build_process_path(
            process_name, ARTIFACT_SUBDIR, ArtifactUpdate.TARGET.value
        )
        raw_content = self._filesystem.read_text(path)
        return self._preprocess_content(raw_content, path)

    def get_artifact_patch_template(self, process_name: str) -> str:
        """Returns patch content template for UPDATE operations.

        Retrieves the Jinja2 patch template for the specified process. This template
        is used to render the replacement content for targeted section updates.
        Uses the new UPDATE operation naming convention (patch.md).

        Args:
            process_name: Name of the process (e.g., "update-plan")

        Returns:
            String content of the artifact/patch.md file

        Raises:
            FileNotFoundError: If the patch.md file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
        """
        path = self._build_process_path(
            process_name, ARTIFACT_SUBDIR, ArtifactUpdate.PATCH.value
        )
        return self._filesystem.read_text(path)

    def get_artifact_directory_template(self, process_name: str) -> str:
        """Returns directory template for artifact path generation.

        Retrieves the Jinja2 directory template for the specified process. This template
        determines the output directory path for generated artifacts.
        Uses the new CREATE operation naming convention (placement.jinja).

        Args:
            process_name: Name of the process (e.g., "create-ticket")

        Returns:
            String content of the artifact/placement.jinja file

        Raises:
            FileNotFoundError: If the placement.jinja file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
        """
        path = self._build_process_path(
            process_name, ARTIFACT_SUBDIR, ArtifactCreate.PLACEMENT.value
        )
        return self._filesystem.read_text(path)

    def get_artifact_filename_template(self, process_name: str) -> str:
        """Returns filename template for artifact path generation.

        Retrieves the Jinja2 filename template for the specified process. This template
        determines the filename for generated artifacts.
        Uses the new CREATE operation naming convention (naming.jinja).

        Args:
            process_name: Name of the process (e.g., "create-ticket")

        Returns:
            String content of the artifact/naming.jinja file

        Raises:
            FileNotFoundError: If the naming.jinja file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
        """
        path = self._build_process_path(
            process_name, ARTIFACT_SUBDIR, ArtifactCreate.NAMING.value
        )
        return self._filesystem.read_text(path)

    def has_jsonl_templates(self, process_name: str) -> bool:
        """Check if process has JSONL templates defined.

        Verifies whether both JSONL naming and placement templates exist for
        the specified process. Used to determine if JSONL logging should be
        enabled for CREATE operations.

        Args:
            process_name: Name of the process (e.g., "submit-feedback")

        Returns:
            True if both JSONL templates exist, False otherwise
        """
        try:
            naming_path = self._build_process_path(
                process_name, ARTIFACT_SUBDIR, JSONL_NAMING_TEMPLATE_FILENAME
            )
            placement_path = self._build_process_path(
                process_name, ARTIFACT_SUBDIR, JSONL_PLACEMENT_TEMPLATE_FILENAME
            )
            return self._filesystem.exists(naming_path) and self._filesystem.exists(
                placement_path
            )
        except Exception:
            return False

    def has_artifact_parser(self, process_name: str) -> bool:
        """Check if a process has an artifact parser (parser.jsonnet).

        Used to distinguish between multi-artifact GET processes (with parser.jsonnet)
        and singleton GET processes (without parser.jsonnet). Singleton processes
        expect exactly one artifact and don't require ID normalization.

        Args:
            process_name: Name of the process to check for parser

        Returns:
            True if parser.jsonnet exists for the process, False otherwise

        Examples:
            has_parser = workspace.has_artifact_parser("get-ticket")  # True (multi-artifact)
            has_parser = workspace.has_artifact_parser("get-architecture-guide")  # False (singleton)
        """
        parser_path = self._build_process_path(
            process_name, ARTIFACT_SUBDIR, ArtifactRetrieve.PARSER.value
        )
        return self._filesystem.exists(parser_path)

    def get_artifact_jsonl_filename_template(self, process_name: str) -> str:
        """Returns JSONL filename template for log path generation.

        Retrieves the Jinja2 JSONL filename template for the specified process.
        This template determines the filename for JSONL log entries created
        alongside regular artifacts.

        Args:
            process_name: Name of the process (e.g., "submit-feedback")

        Returns:
            String content of the artifact/jsonl_naming.jinja file

        Raises:
            FileNotFoundError: If the jsonl_naming.jinja file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
        """
        path = self._build_process_path(
            process_name, ARTIFACT_SUBDIR, JSONL_NAMING_TEMPLATE_FILENAME
        )
        return self._filesystem.read_text(path)

    def get_artifact_jsonl_directory_template(self, process_name: str) -> str:
        """Returns JSONL directory template for log path generation.

        Retrieves the Jinja2 JSONL directory template for the specified process.
        This template determines the output directory path for JSONL log entries
        created alongside regular artifacts.

        Args:
            process_name: Name of the process (e.g., "submit-feedback")

        Returns:
            String content of the artifact/jsonl_placement.jinja file

        Raises:
            FileNotFoundError: If the jsonl_placement.jinja file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
        """
        path = self._build_process_path(
            process_name, ARTIFACT_SUBDIR, JSONL_PLACEMENT_TEMPLATE_FILENAME
        )
        return self._filesystem.read_text(path)

    def get_context_schema(self, process_name: str) -> str:
        """Returns context schema content for build-team-process.

        Retrieves the JSON schema file for the context section used in the
        build-team-process. This schema defines the structure for the artifact
        context information (introduction, conceptual_model, core_capabilities, key_principles).

        Args:
            process_name: Name of the process (should be "build-team-process")

        Returns:
            String content of the context-schema.json file

        Raises:
            FileNotFoundError: If the context-schema.json file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
        """
        path = self._build_process_path(process_name, CONTEXT_SCHEMA_FILENAME)
        return self._filesystem.read_text(path)

    def get_context_template(self, process_name: str) -> str:
        """Returns context template content for build-team-process.

        Retrieves the Jinja2 template for the context section used in the
        build-team-process. This template renders the artifact context information
        into a formatted markdown section.

        Args:
            process_name: Name of the process (should be "build-team-process")

        Returns:
            String content of the context.md file

        Raises:
            FileNotFoundError: If the context.md file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
        """
        path = self._build_process_path(process_name, CONTEXT_TEMPLATE_FILENAME)
        return self._filesystem.read_text(path)

    def get_team_profile(self) -> str:
        """Returns the active team's profile configuration.

        Retrieves the YAML team profile configuration from the active team's directory.
        The profile defines behavioral settings like verbosity, testing requirements, etc.

        Returns:
            String content of the team-profile.yaml file

        Raises:
            FileNotFoundError: If the team profile doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
        """
        path = self._build_team_path(TEAM_PROFILE_FILENAME)
        return self._filesystem.read_text(path)

    def get_permissions(self, process_name: str) -> str:
        """Returns preprocessed permissions configuration for a process.

        Retrieves the Jsonnet permissions configuration from the active team's directory
        and preprocesses it to resolve all import statements. This defines which agents
        are allowed to execute which processes.

        Args:
            process_name: Name of the process to get permissions for

        Returns:
            String content of the permissions.jsonnet file with all imports resolved

        Raises:
            FileNotFoundError: If the permissions file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If file encoding is invalid
            ValueError: If circular imports are detected
            RuntimeError: If import resolution fails
        """
        path = self._build_process_path(process_name, PERMISSIONS_FILENAME)
        raw_content = self._filesystem.read_text(path)
        return self._preprocess_content(raw_content, path)

    def get_config(self, config_name: str, scope: str | None = None) -> dict[str, Any]:
        """Returns configuration as dictionary, handling hierarchical config resolution.

        Retrieves and parses YAML configuration files with support for hierarchical
        resolution. If scope is provided, looks for scoped config first.

        Args:
            config_name: Name of the configuration file (without .yaml extension)
            scope: Optional scope for hierarchical config (e.g., team name)

        Returns:
            Dictionary containing the parsed configuration

        Raises:
            FileNotFoundError: If the config file doesn't exist
            PermissionError: If read access is denied
            ValueError: If YAML parsing fails
        """
        # Try scoped config first if scope is provided
        if scope:
            try:
                scoped_path = self._build_team_path(
                    CONFIG_DIR, scope, f"{config_name}{CONFIG_FILE_EXTENSION}"
                )
                content = self._filesystem.read_text(scoped_path)
                result = yaml.safe_load(content)
                return result if isinstance(result, dict) else {}
            except FileNotFoundError:
                # Fall back to global config
                pass

        # Try global config
        global_path = self._build_team_path(
            CONFIG_DIR, f"{config_name}{CONFIG_FILE_EXTENSION}"
        )
        content = self._filesystem.read_text(global_path)
        result = yaml.safe_load(content)
        return result if isinstance(result, dict) else {}

    def get_resolved_content(self, uri: str) -> str:
        """Resolves semantic URIs and returns content directly.

        Handles semantic URI resolution by parsing the scheme and routing to the
        appropriate content-retrieval method. Supports sub-path URIs for accessing
        nested resources like section schemas.

        Args:
            uri: Semantic URI to resolve (e.g., "process-schema://create-ticket",
                 "process-schema://update-guide/sections/core-principles",
                 "artifact-locator://get-ticket",
                 "artifact-sections://get-ticket?data=sections.plan")

        Returns:
            String content from the resolved URI

        Raises:
            ValueError: If URI format is invalid or scheme is unsupported
            FileNotFoundError: If the resolved content doesn't exist

        Examples:
            get_resolved_content("process-schema://create-ticket")
            get_resolved_content("process-schema://update-guide/sections/core-principles")
            get_resolved_content("artifact-locator://get-ticket")
            get_resolved_content("artifact-sections://get-ticket?data=sections.plan")
        """
        # Parse semantic URI with sub-path and parameters
        scheme, process_name, sub_path, parameters = self._parse_semantic_uri(uri)

        # Route to appropriate content-retrieval method based on scheme
        match scheme:
            case "artifact-content-template":
                return self.get_artifact_content_template(process_name)
            case "artifact-directory-template":
                return self.get_artifact_directory_template(process_name)
            case "artifact-filename-template":
                return self.get_artifact_filename_template(process_name)
            case "artifact-locator":
                return self.get_artifact_locator(process_name)
            case "artifact-parser":
                return self.get_artifact_parser(process_name)
            case "artifact-section-markers":
                return self.get_artifact_section_markers(process_name)
            case "artifact-sections":
                return self.get_artifact_sections(process_name, parameters.get("data"))
            case "process-routine":
                return self.get_process_routine(process_name)
            case "process-schema":
                # Route to section schema if sub-path is present
                if sub_path:
                    return self.get_section_schema(process_name, sub_path)
                return self.get_process_schema(process_name)
            case "artifact-template":
                # Route to section template if sub-path is present
                if not sub_path:
                    raise ValueError(
                        f"artifact-template:// URIs require sub-path (e.g., sections/section-name): {uri}"
                    )
                return self.get_artifact_section_template(process_name, sub_path)
            case _:
                raise ValueError(f"Unsupported URI scheme: {scheme}")

    def get_matching_artifact(
        self, pattern: str, directory: str | None = None
    ) -> list[PantheonPath]:
        """Find files in artifacts directory matching the regex pattern.

        Recursively searches the artifacts directory for files matching the provided
        regex pattern. Used by ArtifactEngine for artifact discovery without
        exposing filesystem implementation details.

        Args:
            pattern: Regex pattern string to match against filenames
            directory: Optional subdirectory within artifacts_root to limit search scope.
                      Supports glob patterns (* ? []) for flexible directory matching.
                      If None, searches entire artifacts_root recursively.

        Returns:
            List of PantheonPath objects for matching files (relative to artifacts root)

        Note: This method encapsulates the filesystem search logic that should not
        be implemented in ArtifactEngine, maintaining architectural boundaries.
        """
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            Log.warning(f"Invalid regex pattern '{pattern}': {e}")
            return []

        # Determine search root directory or use glob patterns
        if directory is not None:
            # Validate directory parameter for security
            try:
                validate_directory_param(directory)
            except PathSecurityError as e:
                Log.warning(str(e))
                return []

            # Check if directory contains glob patterns
            if "*" in directory or "?" in directory or "[" in directory:
                # Use glob pattern matching via FileSystem abstraction
                try:
                    matching_dirs = self._filesystem.glob(
                        self._artifacts_root, directory
                    )

                    if not matching_dirs:
                        Log.debug(
                            f"No directories found matching glob pattern '{directory}'"
                        )
                        return []

                    Log.debug(
                        f"Found {len(matching_dirs)} directories matching pattern '{directory}'"
                    )

                    # Search all matching directories
                    search_roots = matching_dirs
                except Exception as e:
                    Log.warning(f"Error processing glob pattern '{directory}': {e}")
                    return []
            else:
                # Handle as literal directory path (existing behavior)
                search_root = self._artifacts_root / directory
                Log.debug(f"Searching in literal directory '{search_root}'")
                # Verify the directory exists and is within artifacts_root
                if not self._filesystem.exists(search_root):
                    Log.debug(
                        f"Directory '{directory}' does not exist within artifacts_root"
                    )
                    return []

                # Ensure the resolved path stays within artifacts_root boundary
                try:
                    search_root.resolve().relative_to(self._artifacts_root.resolve())
                except ValueError:
                    Log.warning(
                        f"Directory '{directory}' resolves outside artifacts_root boundary"
                    )
                    return []

                search_roots = [search_root]
        else:
            # Use entire artifacts_root for backward compatibility
            search_roots = [self._artifacts_root]

        matching_files = []

        def _search_directory(directory_path: Path) -> None:
            try:
                if not self._filesystem.exists(directory_path):
                    return

                for file_path in self._filesystem.iterdir(directory_path):
                    if file_path.is_file():
                        if compiled_pattern.match(file_path.name):
                            # Convert to relative path from artifacts root
                            relative_path = file_path.relative_to(self._artifacts_root)
                            matching_files.append(PantheonPath(str(relative_path)))
                    elif file_path.is_dir():
                        # Recursively search subdirectories
                        _search_directory(file_path)
            except Exception as e:
                Log.debug(f"Error searching directory {directory_path}: {e}")

        # Search all root directories (either single literal or multiple from glob)
        for search_root in search_roots:
            _search_directory(search_root)
        return matching_files

    def read_artifact_file(self, artifact_path: PantheonPath) -> str:
        """Read artifact file content from the artifacts directory.

        Reads the content of an artifact file using the workspace's filesystem
        dependency, maintaining architectural boundaries.

        Args:
            artifact_path: PantheonPath to the artifact file (relative to artifacts root)

        Returns:
            Content of the artifact file as a string

        Raises:
            FileNotFoundError: If the artifact file doesn't exist
            PermissionError: If access to the file is denied
            UnicodeDecodeError: If the file cannot be decoded as text

        Note: This method encapsulates file reading logic that should not
        be implemented in ArtifactEngine, maintaining architectural boundaries.
        """
        try:
            # Convert PantheonPath to absolute path for filesystem reading
            absolute_path = self._artifacts_root / artifact_path._path

            # Prevent reads from audit directory via artifact retrieval APIs
            audit_dir = self._artifacts_root / self._project_config.get(
                CONFIG_KEY_AUDIT_DIRECTORY, DEFAULT_AUDIT_DIRECTORY
            )
            abs_resolved = absolute_path.resolve()
            if str(abs_resolved).startswith(str(audit_dir.resolve())):
                raise SecurityError("Reads from audit directory are not permitted")

            return self._filesystem.read_text(absolute_path)
        except Exception as e:
            # Re-raise with context about the artifact path
            raise type(e)(f"Failed to read artifact file {artifact_path}: {e}") from e

    def save_audit_log(self, event: dict[str, Any]) -> None:
        """Append a single audit event as JSON to the daily JSONL file.

        This method is the only allowed writer to the audit directory. It enforces
        sandboxing and naming conventions and avoids exposing raw filesystem paths
        to callers.

        Behavior:
        - No-op if audit_enabled is False in project config
        - Creates the audit directory if missing under artifacts_root
        - Appends a newline-terminated JSON object to YYYY-MM-DD_cli.jsonl

        Args:
            event: Dictionary containing the audit fields. This method will not mutate it.
        """
        try:
            if not self._project_config.get(CONFIG_KEY_AUDIT_ENABLED, False):
                return

            from datetime import datetime
            import json as _json

            # Determine audit directory under artifacts_root
            audit_dir_name = self._project_config.get(
                CONFIG_KEY_AUDIT_DIRECTORY, DEFAULT_AUDIT_DIRECTORY
            )
            audit_root = self._artifacts_root / audit_dir_name

            # Ensure directory exists
            if not self._filesystem.exists(audit_root):
                self._filesystem.mkdir(audit_root, parents=True, exist_ok=True)

            # Build filename with underscore per spec
            today = datetime.now().astimezone().strftime("%Y-%m-%d")
            audit_file = audit_root / f"{today}_cli.jsonl"

            # Append JSON line
            line = _json.dumps(event, ensure_ascii=False)
            self._filesystem.append_text(audit_file, line + "\n")

        except Exception as e:
            Log.warning(f"Failed to write audit log: {e}")

    def read_artifact_id(self) -> str:
        """
        Read artifact ID file content as plain text.

        Returns:
            Artifact ID file content as string, or empty string if file doesn't exist

        Raises:
            OSError: If file read fails due to permissions or other I/O errors
        """
        try:
            artifact_id_file_path = self._artifacts_root / ".artifact_id.json"

            # Return empty string if file doesn't exist
            if not self._filesystem.exists(artifact_id_file_path):
                return ""

            # Read artifact ID file content
            return self._filesystem.read_text(artifact_id_file_path)

        except Exception as e:
            Log.error(f"Failed to read artifact ID file: {e}")
            raise

    def save_artifact_id(self, content: str) -> None:
        """
        Save artifact ID content as plain text to the artifact ID file.

        Args:
            content: Artifact ID content as string to save

        Raises:
            OSError: If file write fails due to permissions or other I/O errors
        """
        try:
            artifact_id_file_path = self._artifacts_root / ".artifact_id.json"

            # Write artifact ID content as plain text
            self._filesystem.write_text(artifact_id_file_path, content)

            Log.debug(f"Saved artifact ID content to {artifact_id_file_path}")

        except Exception as e:
            Log.error(f"Failed to save artifact ID file: {e}")
            raise

    def summarize_created_files(
        self, file_paths: list[PantheonPath]
    ) -> list[dict[str, str]]:
        """Convert created file paths to structured summary information.

        Takes a list of PantheonPath objects representing files that were created during
        process execution and returns structured metadata about each file including
        project-relative paths, file types, and human-readable descriptions.

        Args:
            file_paths: List of PantheonPath objects for created files

        Returns:
            List of dictionaries with keys: path, type, description.
            Returns empty list if no files provided (e.g., GET operations).

        Examples:
            [
                {
                    "path": "pantheon-team-builds/my-team/processes/create-blueprint/routine.md",
                    "type": "routine",
                    "description": "Process execution instructions"
                },
                {
                    "path": "pantheon-team-builds/my-team/processes/create-blueprint/schema.jsonnet",
                    "type": "schema",
                    "description": "Input validation schema"
                }
            ]
        """
        if not file_paths:
            return []

        result = []
        for path in file_paths:
            # Convert to project-relative path by adding artifacts_root prefix
            # The PantheonPath objects are already relative to artifacts_root,
            # so we need to prepend the artifacts directory name to make them searchable
            artifacts_dir_name = self._artifacts_root.name  # e.g., "pantheon-artifacts"
            project_relative_path = PantheonPath(artifacts_dir_name).joinpath(path)
            project_relative_str = str(
                project_relative_path
            )  # __str__ already normalizes path separators

            # Classify file type and generate description
            file_type, description = self._classify_created_file(path)

            result.append(
                {
                    "path": project_relative_str,
                    "type": file_type.value,
                    "description": description,
                }
            )

        return result

    def _classify_created_file(self, path: PantheonPath) -> tuple[CreatedFileType, str]:
        """Classify a created file and generate description.

        Uses existing filename constants to avoid magic strings and provides
        centralized logic for file type classification.

        Args:
            path: PantheonPath object to classify

        Returns:
            Tuple of (CreatedFileType, description_string)
        """
        filename = path.name
        parent_dir = path.parent.name if path.parent else ""

        if filename == ROUTINE_FILENAME:
            return CreatedFileType.ROUTINE, "Process execution instructions"
        if filename == SCHEMA_FILENAME:
            return CreatedFileType.SCHEMA, "Input validation schema"
        if filename == BUILD_SCHEMA_FILENAME:
            return CreatedFileType.SCHEMA, "Build process specification schema"
        if filename == CONTEXT_SCHEMA_FILENAME:
            return CreatedFileType.SCHEMA, "Context section schema definition"
        if filename == CONTEXT_TEMPLATE_FILENAME:
            return CreatedFileType.TEMPLATE, "Context section template"
        if filename == DIRECTORY_TEMPLATE_FILENAME:
            return CreatedFileType.TEMPLATE, "Directory path template"
        if filename == PERMISSIONS_FILENAME:
            return CreatedFileType.PERMISSIONS, "Access control configuration"
        if filename == ArtifactCreate.CONTENT.value:
            return CreatedFileType.TEMPLATE, "Artifact content template"
        if filename == ArtifactCreate.PLACEMENT.value:
            return CreatedFileType.TEMPLATE, "Artifact directory template"
        if filename == ArtifactCreate.NAMING.value:
            return CreatedFileType.TEMPLATE, "Artifact filename template"
        if filename == ArtifactUpdate.PATCH.value:
            return CreatedFileType.PATCH, "Section update template"
        if filename == ArtifactUpdate.TARGET.value:
            return CreatedFileType.TARGET, "Section targeting configuration"
        if filename == ArtifactRetrieve.LOCATOR.value:
            return CreatedFileType.LOCATOR, "Artifact location pattern"
        if filename == ArtifactRetrieve.PARSER.value:
            return CreatedFileType.PARSER, "Artifact ID normalization rules"
        if filename == ArtifactRetrieve.SECTIONS.value:
            return CreatedFileType.SECTIONS, "Artifact section markers"
        if filename == JSONL_NAMING_TEMPLATE_FILENAME:
            return CreatedFileType.TEMPLATE, "JSONL filename template"
        if filename == JSONL_PLACEMENT_TEMPLATE_FILENAME:
            return CreatedFileType.TEMPLATE, "JSONL directory template"
        if parent_dir == ARTIFACT_SUBDIR:
            return CreatedFileType.TEMPLATE, f"Process template file ({filename})"

        # Check for JSONL log files by extension
        if filename.endswith(".jsonl"):
            return CreatedFileType.JSONL, "JSONL log entries"

        return CreatedFileType.ARTIFACT, "Generated artifact"

    def _parse_semantic_uri(
        self, uri: str
    ) -> tuple[str, str, str | None, dict[str, str]]:
        """Parse semantic URI into scheme, process name, sub-path, and parameters.

            Internal helper method to extract the scheme, process name, optional sub-path,
        and query parameters from a semantic URI following the pattern:
        scheme://process-name[/sub-path]?param1=value1&param2=value2

        Args:
            uri: Semantic URI to parse

        Returns:
            Tuple of (scheme, process_name, sub_path, parameters)
            where sub_path is None if not present

        Raises:
            ValueError: If URI format is invalid

        Examples:
            _parse_semantic_uri("process-schema://create-ticket")
            # Returns: ("process-schema", "create-ticket", None, {})

            _parse_semantic_uri("process-schema://update-guide/sections/core-principles")
            # Returns: ("process-schema", "update-guide", "sections/core-principles", {})

            _parse_semantic_uri("artifact-sections://get-ticket?data=sections.plan")
            # Returns: ("artifact-sections", "get-ticket", None, {"data": "sections.plan"})
        """
        if "://" not in uri:
            raise ValueError(f"Invalid semantic URI format (missing ://): {uri}")

        scheme, rest = uri.split("://", 1)

        if not scheme:
            raise ValueError(f"Invalid semantic URI format (empty scheme): {uri}")
        if not rest:
            raise ValueError(
                f"Invalid semantic URI format (missing process name): {uri}"
            )

        # Parse query parameters first
        if "?" in rest:
            path_part, query_string = rest.split("?", 1)

            # Parse query parameters
            parameters = {}
            if query_string:
                for param_pair in query_string.split("&"):
                    if "=" in param_pair:
                        key, value = param_pair.split("=", 1)
                        parameters[key] = value
                    else:
                        # Parameter without value (e.g., ?flag)
                        parameters[param_pair] = ""
        else:
            path_part = rest
            parameters = {}

        # Parse process name and optional sub-path
        if "/" in path_part:
            process_name, sub_path = path_part.split("/", 1)
        else:
            process_name = path_part
            sub_path = None

        return scheme, process_name, sub_path, parameters

    def _preprocess_content(
        self, content: str, base_path: Path, import_stack: set[str] | None = None
    ) -> str:
        """Preprocess content by resolving all import statements.

        This method finds all import statements in the content and replaces them with
        either absolute paths (for relative file imports) or inlined content (for
        semantic URI imports). It handles nested imports recursively and detects
        circular dependencies.

        Args:
            content: The raw file content to preprocess
            base_path: The absolute path of the file containing this content
            import_stack: Set of file paths currently being processed (for circular detection)

        Returns:
            The preprocessed content with all imports resolved

        Raises:
            ValueError: If circular imports are detected
            FileNotFoundError: If imported files cannot be found
            RuntimeError: If import resolution fails
        """
        if import_stack is None:
            import_stack = set()

        # Add current file to import stack for circular detection
        base_path_str = str(base_path)
        if base_path_str in import_stack:
            import_chain = " -> ".join(list(import_stack) + [base_path_str])
            raise ValueError(
                f"Circular Import Error: An import loop was detected: {import_chain}"
            )

        import_stack = import_stack | {base_path_str}

        import re

        # Regex to match import statements anywhere in the line
        # Matches: import 'path' or import "path" in any context (assignments, standalone, etc.)
        # Captures the quote style and import path, preserving everything before/after
        import_pattern = re.compile(r'\bimport\s+(["\']+)([^"\']+)\1', re.MULTILINE)

        def resolve_import(match):
            import_path = match.group(2)

            try:
                # Determine if this is a semantic URI or relative path
                if "://" in import_path:
                    # Semantic URI - resolve through workspace
                    Log.debug(f"Resolving semantic URI import: {import_path}")

                    # For semantic URIs, we inline the content directly
                    # Return the resolved content as-is without wrapping
                    return self.get_resolved_content(import_path)

                # Relative file path - inline the content just like semantic URIs
                # Block upward traversal (..) and absolute paths
                validate_import_path(import_path)

                # Construct path to the imported file in same directory as base file
                import_file_path = base_path.parent / import_path

                if not import_file_path.exists():
                    raise FileNotFoundError(
                        f"Import Resolution Error: The file '{import_file_path}' could not be found, "
                        f"as imported by '{base_path}'"
                    )

                # Read and recursively preprocess the imported file
                Log.debug(
                    f"Inlining relative import: {import_path} from {import_file_path}"
                )

                # Read the imported file content
                imported_content = self._filesystem.read_text(import_file_path)

                # Recursively preprocess the imported content to resolve its imports
                # Return the processed content directly (inline it)
                return self._preprocess_content(
                    imported_content, import_file_path, import_stack
                )

            except Exception as e:
                Log.error(
                    f"Failed to resolve import '{import_path}' in file '{base_path}': {e}"
                )
                raise RuntimeError(f"Import resolution failed: {e}") from e

        # Replace all import statements with resolved content
        try:
            processed_content = import_pattern.sub(resolve_import, content)
            Log.debug(f"Preprocessing completed for {base_path}")
            return processed_content

        except Exception as e:
            Log.error(f"Content preprocessing failed for {base_path}: {e}")
            raise

    def get_team_data(self) -> str:
        """Get raw team-data.yaml content.

        Reads the team-data.yaml file from the active team root and returns
        the raw file content without any processing.

        Returns:
            Raw YAML content as string

        Raises:
            FileNotFoundError: If team-data.yaml doesn't exist

        Examples:
            raw_content = workspace.get_team_data()
        """
        team_data_path = self._build_team_path("team-data.yaml")

        if not self._filesystem.exists(team_data_path):
            raise FileNotFoundError("team-data.yaml not found in team root")

        return self._filesystem.read_text(team_data_path)

    def set_team_data(self, updates: dict[str, str], deletes: list[str]) -> None:
        """Set or delete keys in team-data.yaml.

        Updates the team-data.yaml file with new values and/or deletes existing keys.
        Uses dot notation for nested keys and performs deep merge to preserve existing data.

        Args:
            updates: Dictionary of dot notation keys to string values
            deletes: List of dot notation keys to delete

        Raises:
            ValueError: If operations are invalid or YAML parsing fails

        Examples:
            # Set some values and delete others
            workspace.set_team_data(
                {"agents.backend": "Backend specialist", "foo": "bar"},
                ["agents.old_agent", "deprecated_key"]
            )
        """
        team_data_path = self._build_team_path("team-data.yaml")

        # Load existing data or start with empty dict
        if self._filesystem.exists(team_data_path):
            content = self._filesystem.read_text(team_data_path)
            try:
                data = yaml.safe_load(content) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in team-data.yaml: {e}") from e
        else:
            data = {}

        # Apply deletes first
        for delete_key in deletes:
            self._delete_nested_key(data, delete_key)

        # Apply updates using deep merge with type coercion
        for dot_key, value in updates.items():
            coerced_value = self._coerce_value_type(value)
            nested_update = self._parse_dot_notation(dot_key, coerced_value)
            data = self._deep_merge(data, nested_update)

        # Write back to file
        yaml_content = yaml.dump(data, default_flow_style=False)
        self._filesystem.write_text(team_data_path, yaml_content)

    def _parse_dot_notation(self, dot_key: str, value: Any) -> dict[str, Any]:
        """Parse dot notation key into nested dictionary structure.

        Converts a dot notation key like 'agents.backend' into a nested dictionary
        {'agents': {'backend': value}}.

        Args:
            dot_key: Key in dot notation (e.g., 'agents.backend')
            value: Value to set (any type after type coercion)

        Returns:
            Nested dictionary structure

        Examples:
            _parse_dot_notation("agents.backend", "Backend dev")
            # Returns: {"agents": {"backend": "Backend dev"}}

            _parse_dot_notation("metrics.count", 15)
            # Returns: {"metrics": {"count": 15}}
        """
        parts = dot_key.split(".")
        result: dict[str, Any] = {}
        current = result

        for part in parts[:-1]:
            current[part] = {}
            current = current[part]

        current[parts[-1]] = value
        return result

    def _deep_merge(
        self, base: dict[str, Any], update: dict[str, Any]
    ) -> dict[str, Any]:
        """Recursively merge update dictionary into base dictionary.

        Performs a deep merge where nested dictionaries are merged recursively,
        and other values are overwritten.

        Args:
            base: Base dictionary to merge into
            update: Update dictionary to merge from

        Returns:
            Merged dictionary (modifies base in-place and returns it)
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base

    def _get_nested_value(self, data: dict[str, Any], dot_key: str) -> Any:
        """Get value from nested dictionary using dot notation.

        Traverses nested dictionary structure using dot notation key.

        Args:
            data: Dictionary to search in
            dot_key: Key in dot notation (e.g., 'agents.backend')

        Returns:
            Value at the specified key path

        Raises:
            KeyError: If key path doesn't exist
        """
        parts = dot_key.split(".")
        current = data

        for part in parts:
            if not isinstance(current, dict) or part not in current:
                raise KeyError(f"Key '{dot_key}' not found")
            current = current[part]

        return current

    def _delete_nested_key(self, data: dict[str, Any], dot_key: str) -> None:
        """Delete key from nested dictionary using dot notation.

        Traverses nested dictionary structure and deletes the final key.
        Does nothing if the key doesn't exist.

        Args:
            data: Dictionary to delete from (modified in-place)
            dot_key: Key in dot notation (e.g., 'agents.backend')
        """
        parts = dot_key.split(".")
        current = data

        # Navigate to parent of target key
        for part in parts[:-1]:
            if not isinstance(current, dict) or part not in current:
                return  # Path doesn't exist, nothing to delete
            current = current[part]

        # Delete the final key
        if isinstance(current, dict):
            current.pop(parts[-1], None)

    def _coerce_value_type(self, value: str) -> Any:
        """Convert string value to appropriate type when unambiguous.

        Applies smart type coercion to convert string values to their most
        likely intended types (boolean, integer, float) while keeping
        ambiguous values as strings.

        Args:
            value: String value from CLI input

        Returns:
            Coerced value (bool, int, float, or str)

        Examples:
            _coerce_value_type("true") → True
            _coerce_value_type("15") → 15
            _coerce_value_type("87.5") → 87.5
            _coerce_value_type("hello") → "hello"
            _coerce_value_type("1.2.3") → "1.2.3" (ambiguous, stays string)
        """
        # Boolean detection (case-insensitive)
        lower_val = value.lower()
        if lower_val == "true":
            return True
        if lower_val == "false":
            return False

        # Integer detection (only digits, optional negative sign)
        if value.lstrip("-").isdigit():
            return int(value)

        # Float detection (digits with exactly one decimal point)
        if "." in value and value.count(".") == 1:
            # Remove negative sign for digit check
            without_minus = value.lstrip("-")
            # Check if it's digits.digits format
            if without_minus.replace(".", "").isdigit():
                return float(value)

        # Everything else stays as string
        return value
