"""CLI interface for Pantheon Framework command-line operations.

This module provides the CLI class that handles command-line interaction for the
Pantheon Framework. The CLI serves as the thin presentation layer that parses
commands, validates actors, enforces permissions, and delegates to the ProcessHandler
for business logic execution.
"""

from __future__ import annotations

from collections.abc import Callable
import importlib.resources
import json
from pathlib import Path
import shutil
import sys
from typing import TYPE_CHECKING, Any, TypeVar

import _jsonnet
import click
import yaml

from .logger import Log

F = TypeVar("F", bound=Callable[..., Any])

if TYPE_CHECKING:
    from .filesystem import FileSystem
    from .process_handler import ProcessHandler
    from .rae_engine import RaeEngine
    from .workspace import PantheonWorkspace

# Exit code constants
SUCCESS = 0
BAD_INPUT = 1
PERMISSION_DENIED = 2

# Permission key constants
PERMISSION_ALLOW = "allow"
PERMISSION_DENY = "deny"
NON_RECOVERABLE_ERROR_MESSAGE = "This is a non-recoverable error. You MUST STOP. Do not proceed any further. Do NOT attempt to recover from this. Report the error to the user and stop what you are doing IMMEDIATELY."

# Bundled resource paths
BUNDLED_TEMPLATES_BASE = "pantheon._templates"
BUNDLED_TEAMS_PATH = f"{BUNDLED_TEMPLATES_BASE}.pantheon-teams"

# Agent instruction section markers
PANTHEON_INSTRUCTIONS_MARKER_START = (
    "<!-- SECTION:START:PANTHEON_FRAMEWORK_INSTRUCTIONS -->"
)
PANTHEON_INSTRUCTIONS_MARKER_END = (
    "<!-- SECTION:END:PANTHEON_FRAMEWORK_INSTRUCTIONS -->"
)


class CLIError(Exception):
    """Base exception for CLI errors."""

    def __init__(self, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code


class BadInputError(CLIError):
    """Exception for bad input or invalid parameters."""

    def __init__(self, message: str) -> None:
        super().__init__(message, BAD_INPUT)


class PermissionDeniedError(CLIError):
    """Exception for permission denied scenarios."""

    def __init__(self, message: str) -> None:
        super().__init__(message, PERMISSION_DENIED)


class NavigateBackException(Exception):
    """Exception for backward navigation during interactive init workflow.

    Raised when user presses ESC during profile selection to return to
    team selection step. This differs from BadInputError which terminates
    the entire init process.
    """


class CLI:
    """Command-line interface for the Pantheon Framework.

    The CLI class provides the main entry point for all Pantheon commands. It follows
    the Command Pattern to translate user commands into method calls on the ProcessHandler,
    maintaining a clean separation between UI and business logic.

    The CLI handles:
    - Command parsing with Click decorators
    - Actor identity validation (non-empty check)
    - Permission enforcement via permissions.jsonnet
    - Error handling with proper exit codes
    - Delegation to ProcessHandler for execution
    """

    def __init__(
        self,
        workspace: PantheonWorkspace,
        process_handler: ProcessHandler,
        rae_engine: RaeEngine,
        filesystem: FileSystem,
    ) -> None:
        """Initialize the CLI with required dependencies.

        Args:
            workspace: PantheonWorkspace for permission validation
            process_handler: ProcessHandler for business logic execution
            rae_engine: RaeEngine for routine retrieval
            filesystem: FileSystem for external file operations (e.g., --from-file)

        """
        self._workspace = workspace
        self._process_handler = process_handler
        self._rae_engine = rae_engine
        self._filesystem = filesystem

    # --- Internal helper: audit logging ---
    def _audit_log(
        self,
        command: str,
        actor: str | None = None,
        id: str | None = None,
        sections: str | None = None,
        result: str = "success",
    ) -> None:
        """Emit an audit event via Workspace if configured.

        Args:
            command: Full subcommand string (e.g., 'execute create-ticket', 'get schema <proc>')
            actor: Actor value if present
            id: ID value if present
            sections: Sections value if present
            result: Outcome string (success | bad_input | permission_denied | error)
        """
        try:
            if not hasattr(self, "_workspace") or self._workspace is None:
                return
            team = self._workspace._project_config.get("active_team", "")
            event = {
                "command": command,
                "actor": actor or "",
                "id": id or "",
                "sections": sections or "",
                "team": team,
                "result": result,
                "timestamp": self._format_timestamp_with_seconds(),
            }

            # Human-readable debug summary (structured event)
            Log.debug("Audit event: %s", event)

            # Call into workspace (no-op if disabled)
            self._workspace.save_audit_log(event)  # type: ignore[union-attr]
        except Exception:
            # Never let audit failure affect CLI behavior
            pass

    def _get_timezone_abbreviation(self) -> str:
        from datetime import datetime

        now = datetime.now().astimezone()
        tz_name = now.strftime("%Z")
        if len(tz_name) > 4:
            return "".join(word[0].upper() for word in tz_name.split())
        return tz_name

    def _format_timestamp_with_seconds(self) -> str:
        from datetime import datetime

        now = datetime.now().astimezone()
        tz_abbr = self._get_timezone_abbreviation()
        return now.strftime("%Y-%m-%d %I:%M:%S %p") + f" {tz_abbr}"

    def _format_option_line(self, text: str, is_default: bool) -> str:
        """Format an option line for display, with bold styling for default option.

        Args:
            text: The text to format
            is_default: Whether this is the default option

        Returns:
            Formatted text with bold styling if default
        """
        if is_default:
            return click.style(text, bold=True)
        return text

    def validate_actor(self, actor: str) -> None:
        """Validate that the actor name is non-empty.

        Args:
            actor: The actor name to validate

        Raises:
            BadInputError: If the actor name is empty or whitespace-only
        """
        if not actor or not actor.strip():
            raise BadInputError("Actor name cannot be empty")

    def _evaluate_permission(self, actor: str, perms: dict[str, Any]) -> bool:
        """Evaluate permission for actor against permission object.

        Args:
            actor: The actor requesting access
            perms: Permission object with allow/deny lists

        Returns:
            True if access should be granted, False otherwise
        """
        # Explicit deny always wins
        deny_list = perms.get(PERMISSION_DENY, [])
        if actor in deny_list:
            return False

        # Check allow list
        allow_list = perms.get(PERMISSION_ALLOW, [])
        if "*" in allow_list:  # Wildcard = everyone
            return True
        return actor in allow_list

    def _get_permitted_sections(
        self, process_name: str, actor: str, sections_data: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        """Filter sections based on actor permissions.

        Args:
            process_name: The process name to check permissions for
            actor: The actor requesting access
            sections_data: List of section metadata dictionaries

        Returns:
            List of sections the actor has permission to access

        Raises:
            BadInputError: If permissions file is malformed or missing
        """
        # Load and parse permissions.jsonnet
        try:
            permissions_content = self._workspace.get_permissions(process_name)
            compiled_json = _jsonnet.evaluate_snippet(
                f"processes/{process_name}/permissions.jsonnet", permissions_content
            )
            permissions = json.loads(compiled_json)
        except FileNotFoundError as e:
            raise BadInputError(
                f"No permissions.jsonnet found for process '{process_name}'. All processes must define permissions. {NON_RECOVERABLE_ERROR_MESSAGE}"
            ) from e
        except json.JSONDecodeError as e:
            raise BadInputError(
                f"Invalid permissions format for process '{process_name}': {e}. {NON_RECOVERABLE_ERROR_MESSAGE}"
            ) from e
        except Exception as e:
            raise BadInputError(
                f"Failed to evaluate permissions for process '{process_name}': {e}. {NON_RECOVERABLE_ERROR_MESSAGE}"
            ) from e

        section_permissions = permissions.get("sections", {})
        process_deny = permissions.get(PERMISSION_DENY, [])
        process_allow = permissions.get(PERMISSION_ALLOW, [])

        permitted_sections = []

        for section_data in sections_data:
            section_name = section_data["name"]
            section_perms = section_permissions.get(section_name, {})
            section_deny = section_perms.get(PERMISSION_DENY, [])
            section_allow = section_perms.get(PERMISSION_ALLOW, [])

            # 1. ANY deny wins (check both process and section level)
            if actor in section_deny or actor in process_deny:
                continue  # Skip this section - actor is explicitly denied

            # 2. Create union of allows and check membership
            combined_allows = set(process_allow + section_allow)

            # 3. Check if actor is in the combined allow list (including wildcard support)
            if "*" in combined_allows or actor in combined_allows:
                permitted_sections.append(section_data)
                continue

            # 4. Default deny - skip this section

        return permitted_sections

    def check_permissions(
        self, actor: str, process_name: str, sections: list[str] | None = None
    ) -> None:
        """Check if actor has permission to execute the process and sections.

        Args:
            actor: The actor requesting access
            process_name: The process name to check permissions for
            sections: Optional list of sections to validate for UPDATE operations

        Raises:
            PermissionDeniedError: If the actor lacks permission
            BadInputError: If process name is invalid or permissions malformed
        """
        if not process_name or not process_name.strip():
            raise BadInputError("Process name cannot be empty")

        # Load and parse permissions.jsonnet (required - no backward compatibility)
        try:
            permissions_content = self._workspace.get_permissions(process_name)
            # Compile the Jsonnet to JSON before parsing
            compiled_json = _jsonnet.evaluate_snippet(
                f"processes/{process_name}/permissions.jsonnet", permissions_content
            )
            permissions = json.loads(compiled_json)
        except FileNotFoundError as e:
            # No backward compatibility - all processes must have permissions.jsonnet
            raise BadInputError(
                f"No permissions.jsonnet found for process '{process_name}'. All processes must define permissions. {NON_RECOVERABLE_ERROR_MESSAGE}"
            ) from e
        except json.JSONDecodeError as e:
            raise BadInputError(
                f"Invalid permissions format for process '{process_name}': {e}. {NON_RECOVERABLE_ERROR_MESSAGE}"
            ) from e
        except Exception as e:
            raise BadInputError(
                f"Failed to evaluate permissions for process '{process_name}': {e}. {NON_RECOVERABLE_ERROR_MESSAGE}"
            ) from e

        # Check section-level permissions first if sections are specified
        if sections:
            section_permissions = permissions.get("sections", {})
            process_deny = permissions.get(PERMISSION_DENY, [])
            process_allow = permissions.get(PERMISSION_ALLOW, [])

            for section in sections:
                section_perms = section_permissions.get(section, {})
                section_deny = section_perms.get(PERMISSION_DENY, [])
                section_allow = section_perms.get(PERMISSION_ALLOW, [])

                # 1. ANY deny wins (check both process and section level)
                if actor in section_deny:
                    raise PermissionDeniedError(
                        f"Actor '{actor}' is explicitly denied access to section '{section}' in process '{process_name}'. {NON_RECOVERABLE_ERROR_MESSAGE}"
                    )
                if actor in process_deny:
                    raise PermissionDeniedError(
                        f"Actor '{actor}' is explicitly denied access to process '{process_name}'. {NON_RECOVERABLE_ERROR_MESSAGE}"
                    )

                # 2. Create union of allows and check membership
                combined_allows = set(process_allow + section_allow)

                # Check if actor is in the combined allow list (including wildcard support)
                if "*" in combined_allows or actor in combined_allows:
                    continue  # This section is allowed

                # 3. Default deny
                raise PermissionDeniedError(
                    f"Actor '{actor}' lacks permission for section '{section}' in process '{process_name}'. {NON_RECOVERABLE_ERROR_MESSAGE}"
                )

            # If we made it through all sections without errors, permission granted
            return

        # Process-level permission check (when no sections specified)
        # Check process-level deny
        process_deny = permissions.get(PERMISSION_DENY, [])
        if actor in process_deny:
            raise PermissionDeniedError(
                f"Actor '{actor}' is explicitly denied access to process '{process_name}'. {NON_RECOVERABLE_ERROR_MESSAGE}"
            )

        # Check process-level allow
        if not self._evaluate_permission(actor, permissions):
            raise PermissionDeniedError(
                f"Actor '{actor}' lacks permission for process '{process_name}'. {NON_RECOVERABLE_ERROR_MESSAGE}"
            )

    def get_process(
        self, process_name: str, actor: str, sections: str | None = None
    ) -> str:
        """Retrieve routine content for a process with optional section filtering."""

        self.validate_actor(actor)
        sections_list = sections.split(",") if sections else None
        self.check_permissions(actor, process_name, sections_list)

        try:
            return self._process_handler.get_routine(process_name, actor, sections)
        except ValueError as e:
            raise BadInputError(str(e)) from e
        except FileNotFoundError as e:
            raise BadInputError(f"Process '{process_name}' not found") from e

    def get_schema(
        self, process_name: str, actor: str, sections: str | None = None
    ) -> str:
        """Retrieve composed JSON schema for a process with optional section filtering."""

        self.validate_actor(actor)
        sections_list = sections.split(",") if sections else None
        self.check_permissions(actor, process_name, sections_list)

        try:
            schema = self._process_handler.compose_schema(process_name, actor, sections)
        except ValueError as e:
            raise BadInputError(str(e)) from e
        except FileNotFoundError as e:
            raise BadInputError(f"Process '{process_name}' not found") from e

        return json.dumps(schema, indent=2)

    def get_sections(self, process_name: str, actor: str) -> str:
        """Retrieve available section metadata for a process that the actor has permission to access."""

        self.validate_actor(actor)

        try:
            sections_data = self._process_handler.get_sections_metadata(process_name)
        except FileNotFoundError as e:
            raise BadInputError(f"Process '{process_name}' not found") from e
        except ValueError as e:
            raise BadInputError(str(e)) from e

        # Filter sections based on actor permissions
        permitted_sections = self._get_permitted_sections(
            process_name, actor, sections_data
        )

        return json.dumps(permitted_sections, indent=2)

    def get_tempfile(self, process_name: str, actor: str) -> str:
        """Get temporary file path for process input.

        Args:
            process_name: Process name for tempfile generation
            actor: Actor requesting the tempfile

        Returns:
            Absolute path to temporary file as string

        Raises:
            BadInputError: If process name or actor name is invalid
        """
        # Validate actor (no permission check needed for tempfile generation)
        self.validate_actor(actor)

        # Use workspace.create_tempfile() for safe tempfile creation within sandbox
        # Returns PantheonPath which should be converted to absolute path for CLI output
        temp_path = self._workspace.create_tempfile(
            suffix=".json", prefix=f"{process_name}"
        )

        # Resolve to absolute path like workspace.save_artifact does
        absolute_path = (
            self._workspace._artifacts_root / temp_path.get_underlying_path()
        )
        return str(absolute_path)

    def get_team_data(self, actor: str, key: str | None = None) -> str:
        """Get team data from team-data.yaml with Jinja2 template rendering.

        Args:
            actor: Actor requesting the data (used for template context)
            key: Optional key to filter (dot notation supported)

        Returns:
            YAML-formatted team data

        Raises:
            BadInputError: If actor name or key is invalid
        """
        self.validate_actor(actor)

        try:
            return self._process_handler.get_team_data(actor, key)
        except FileNotFoundError as e:
            raise BadInputError(
                "team-data.yaml not found. Initialize with 'pantheon set team-data' first."
            ) from e
        except ValueError as e:
            raise BadInputError(str(e)) from e

    def set_team_data(
        self, actor: str, updates: dict[str, str], deletes: list[str]
    ) -> str:
        """Set or delete keys in team-data.yaml.

        Args:
            actor: Actor performing the operation
            updates: Dictionary of dot notation keys to string values
            deletes: List of dot notation keys to delete

        Returns:
            Success message

        Raises:
            BadInputError: If actor name or operations are invalid
        """
        self.validate_actor(actor)

        try:
            self._workspace.set_team_data(updates, deletes)
            operation_count = len(updates) + len(deletes)
            return f"team-data.yaml updated successfully. {operation_count} operations completed."
        except ValueError as e:
            raise BadInputError(str(e)) from e

    def execute_process(
        self,
        process_name: str,
        actor: str,
        id: str | None = None,
        sections: str | None = None,
        insert_mode: str | None = None,
        from_file: str | None = None,
        **kwargs: str,
    ) -> str:
        """Execute a process with given input data.

        Args:
            process_name: Name of the process to execute
            actor: Actor executing the process
            id: Artifact ID for GET and UPDATE processes (maps to pantheon_artifact_id)
            sections: Comma-separated sections list for pantheon_sections
            insert_mode: Insert mode for UPDATE processes (append or prepend)
            from_file: Optional path to JSON input file
            **kwargs: Direct argument input for simple data

        Returns:
            Process execution result message

        Raises:
            BadInputError: If input is invalid or actor name is invalid
            PermissionDeniedError: If actor lacks permission
        """
        from pantheon.process_handler import (
            BUILTIN_ARTIFACT_ID,
            BUILTIN_INSERT_MODE,
            INPUT_ACTOR,
            INPUT_FRAMEWORK_PARAMS,
            INPUT_INPUT_PARAMS,
            INPUT_PROCESS,
            PARAM_SECTIONS,
            ProcessInput,
            coerce_framework_value,
            normalize_framework_key,
        )

        # Early validation - these errors should NOT trigger temp file cleanup
        # since they are easily recoverable by fixing command arguments
        self.validate_actor(actor)

        # Check if process exists before checking permissions
        # This provides a clearer error message for process name typos
        try:
            self._workspace.check_process_exists(process_name)
        except FileNotFoundError as e:
            raise BadInputError(str(e)) from e

        # Convert sections string to list for permission checking
        sections_list = None
        if sections:
            sections_list = [s.strip() for s in sections.split(",") if s.strip()]

        self.check_permissions(actor, process_name, sections_list)

        # Validate input format
        if from_file and kwargs:
            raise BadInputError("Cannot specify both --from-file and direct arguments")

        # For GET operations like get-ticket, allow execution with only reserved parameters like --id
        # GET processes typically don't need JSON input data, only the artifact ID
        needs_input = not process_name.startswith("get-")

        if not from_file and not kwargs and needs_input:
            raise BadInputError("Must specify either --from-file or direct arguments")

        # Prepare parameters - file reading errors are also recoverable
        if from_file:
            try:
                json_content = self._filesystem.read_text(from_file)
                parameters = json.loads(json_content)
                if not isinstance(parameters, dict):
                    raise BadInputError(
                        "Input file must contain a JSON object at the top level"
                    )
            except FileNotFoundError as e:
                raise BadInputError(f"Input file not found: {from_file}") from e
            except json.JSONDecodeError as e:
                raise BadInputError(f"Invalid JSON in input file: {e}") from e
        else:
            parameters = dict(kwargs)

        input_params: dict[str, Any] = {}
        framework_params: dict[str, Any] = {}

        for key, value in parameters.items():
            canonical = normalize_framework_key(key)
            if canonical:
                Log.warning(
                    "Reserved parameter '%s' provided via input; value will be ignored and "
                    "managed by the framework.",
                    key,
                )
                continue
            input_params[key] = value

        if id is not None:
            framework_params[BUILTIN_ARTIFACT_ID] = id

        if sections is not None:
            framework_params[PARAM_SECTIONS] = coerce_framework_value(
                PARAM_SECTIONS, sections
            )

        if insert_mode is not None:
            framework_params[BUILTIN_INSERT_MODE] = insert_mode

        # Construct ProcessInput
        process_input: ProcessInput = {
            INPUT_PROCESS: process_name,
            INPUT_ACTOR: actor,
            INPUT_INPUT_PARAMS: input_params,
            INPUT_FRAMEWORK_PARAMS: framework_params,
        }

        # Only now do we enter the try-finally block for actual process execution
        # This ensures temp file cleanup only happens for actual execution attempts
        execution_success = False
        try:
            from pantheon.process_handler import (
                RESULT_ERROR,
                RESULT_FILES_CREATED,
                RESULT_OUTPUT,
                RESULT_SUCCESS,
            )

            result = self._process_handler.execute(process_input)

            if not result[RESULT_SUCCESS]:
                error_msg = result.get(RESULT_ERROR, "Process execution failed")
                raise BadInputError(error_msg)

            # If we reach here, execution was successful
            execution_success = True

            # Build output message with files created information
            output_lines = []

            # Add the primary output message
            if result.get(RESULT_OUTPUT):
                output_lines.append(result[RESULT_OUTPUT])
            else:
                output_lines.append(f"Process '{process_name}' completed successfully")

            # Add files created information if present
            files_created = result.get(RESULT_FILES_CREATED)
            if files_created:
                output_lines.append("")  # Empty line separator
                output_lines.append("Files created:")
                for file_info in files_created:
                    path = file_info.get("path", "")
                    file_type = file_info.get("type", "")
                    description = file_info.get("description", "")
                    output_lines.append(f"- {path} ({file_type}): {description}")

            return "\n".join(output_lines)

        except Exception as e:
            # ProcessHandler format_error expects error_type and error_message
            formatted_error = self._process_handler.format_error(
                type(e).__name__, str(e)
            )
            raise BadInputError(formatted_error) from e

        finally:
            # Clean up temp file only after attempting actual process execution
            # Early validation errors will not reach this cleanup
            if from_file:
                self._workspace.cleanup_temp_file(from_file, execution_success)

    def _discover_bundled_teams(self) -> list[str]:
        """Discover available bundled team packages from _templates.

        Returns:
            List of available team names

        Raises:
            BadInputError: If no bundled teams are found
        """
        try:
            # Access the bundled teams directory using importlib.resources
            with importlib.resources.as_file(
                importlib.resources.files("pantheon") / "_templates" / "pantheon-teams"
            ) as teams_path:
                if not teams_path.exists():
                    raise BadInputError(
                        "No bundled teams found in framework installation"
                    )

                # Get list of team directories
                team_names = [
                    item.name
                    for item in teams_path.iterdir()
                    if item.is_dir() and not item.name.startswith(".")
                ]

                if not team_names:
                    raise BadInputError("No bundled teams available")

                return sorted(team_names)

        except Exception as e:
            raise BadInputError(f"Failed to discover bundled teams: {e}") from e

    def _load_team_description(self, team_name: str) -> str:
        """Load team description from bundled team-profile.yaml.

        Args:
            team_name: Name of the team to load description for

        Returns:
            Team description string or default message if unavailable
        """
        try:
            # Access the bundled team-profile.yaml using importlib.resources
            with importlib.resources.as_file(
                importlib.resources.files("pantheon")
                / "_templates"
                / "pantheon-teams"
                / team_name
                / "team-profile.yaml"
            ) as profile_path:
                if not profile_path.exists():
                    Log.warning(f"team-profile.yaml not found for team '{team_name}'")
                    return "No description available"

                # Read and parse YAML
                content = profile_path.read_text(encoding="utf-8")
                profile_data = yaml.safe_load(content)

                # Extract team_description field
                if not isinstance(profile_data, dict):
                    Log.warning(
                        f"Invalid team-profile.yaml format for team '{team_name}'"
                    )
                    return "No description available"

                description = profile_data.get("team_description", "").strip()
                return description if description else "No description available"

        except yaml.YAMLError as e:
            Log.warning(
                f"Failed to parse team-profile.yaml for team '{team_name}': {e}"
            )
            return "No description available"
        except Exception as e:
            Log.warning(f"Failed to load description for team '{team_name}': {e}")
            return "No description available"

    def _get_default_team(self) -> str | None:
        """Load default team from bundled framework configuration.

        Returns:
            Default team name if configured, None otherwise
        """
        try:
            # Access bundled defaults.yaml using importlib.resources
            # Use BUNDLED_TEAMS_PATH constant to avoid hardcoding resource structure
            with importlib.resources.as_file(
                importlib.resources.files(BUNDLED_TEAMS_PATH) / "defaults.yaml"
            ) as defaults_path:
                if not defaults_path.exists():
                    Log.debug("No defaults.yaml found - no default team configured")
                    return None

                # Read and parse YAML
                content = defaults_path.read_text(encoding="utf-8")
                defaults_data = yaml.safe_load(content)

                # Extract default_team field
                if not isinstance(defaults_data, dict):
                    Log.warning("Invalid defaults.yaml format - expected dictionary")
                    return None

                default_team = defaults_data.get("default_team")
                if default_team and isinstance(default_team, str):
                    Log.debug(f"Default team configured: {default_team}")
                    return default_team.strip()

                return None

        except yaml.YAMLError as e:
            Log.warning(f"Failed to parse defaults.yaml: {e}")
            return None
        except Exception as e:
            Log.debug(f"Failed to load defaults.yaml: {e}")
            return None

    def _select_team_interactive(self, available_teams: list[str]) -> str:
        """Interactively prompt user to select a team from available options.

        Args:
            available_teams: List of available team names

        Returns:
            Selected team name

        Raises:
            BadInputError: If user cancels selection or invalid choice
        """
        if len(available_teams) == 1:
            # Only one team available, use it directly
            selected_team = available_teams[0]
            description = self._load_team_description(selected_team)
            click.echo(f"Using available team: {selected_team} - {description}")
            return selected_team

        # Get default team from framework configuration
        default_team = self._get_default_team()

        # Reorder teams to place default team first if configured and available
        display_teams = available_teams.copy()
        if default_team and default_team in display_teams:
            display_teams.remove(default_team)
            display_teams.insert(0, default_team)

        # Multiple teams available, prompt for selection
        click.echo("Available starter teams:")
        for i, team in enumerate(display_teams, 1):
            description = self._load_team_description(team)
            # Add default indicator for option 1 when default team is configured
            is_default = i == 1 and default_team and team == default_team
            if is_default:
                option_line = (
                    f"  {i}. {team} (default - press enter to select) - {description}"
                )
            else:
                option_line = f"  {i}. {team} - {description}"
            click.echo(self._format_option_line(option_line, is_default))

        try:
            # Set default='1' in prompt when default team exists
            prompt_kwargs = {
                "type": click.Choice(
                    [str(i) for i in range(1, len(display_teams) + 1)]
                ),
            }
            if default_team and default_team in display_teams:
                prompt_kwargs["default"] = "1"

            choice = click.prompt("Select a team", **prompt_kwargs)
            return display_teams[int(choice) - 1]
        except click.Abort:
            raise BadInputError("Team selection cancelled") from None

    # ARCHITECTURAL EXCEPTION: Direct I/O in CLI during pre-project initialization
    #
    # This method performs direct I/O using importlib.resources, which violates the
    # normal Workspace abstraction pattern. This is an acceptable architectural exception
    # because:
    #
    # 1. Pre-project context: During 'pantheon init', the project doesn't exist yet
    #    (.pantheon_project hasn't been created), so PantheonWorkspace cannot be
    #    instantiated or used for I/O operations.
    #
    # 2. Bundled template access: Profile selection requires reading bundled templates
    #    from _templates/pantheon-teams/<team>/team-profile.yaml, not project-local
    #    files. The Workspace abstraction is designed for project-local file operations.
    #
    # 3. Single-use scope: This exception is limited to the init command workflow.
    #    All post-initialization commands use Workspace properly for I/O operations.
    #
    # For all other commands (after project initialization), use Workspace methods
    # for I/O operations to maintain proper separation of concerns and testability.
    def _select_profile_interactive(self, team_name: str) -> str | None:
        """Interactively prompt user to select a profile from available options.

        Args:
            team_name: Name of the team to get profiles from

        Returns:
            Selected profile name, or None if team has no profiles

        Raises:
            NavigateBackException: If user presses ESC to return to team selection
        """
        # Use importlib.resources to access bundled team-profile.yaml
        try:
            with importlib.resources.as_file(
                importlib.resources.files("pantheon")
                / "_templates"
                / "pantheon-teams"
                / team_name
                / "team-profile.yaml"
            ) as profile_path:
                if not profile_path.exists():
                    return None

                content = profile_path.read_text(encoding="utf-8")
                profile_data = yaml.safe_load(content)

                if not isinstance(profile_data, dict) or "profiles" not in profile_data:
                    return None

                profiles = profile_data.get("profiles", {})
                if not profiles:
                    return None

                profile_names = list(profiles.keys())

                if len(profile_names) == 1:
                    # Only one profile available, auto-select it
                    profile_name = profile_names[0]
                    profile_desc = profiles[profile_name].get(
                        "profile_description", "No description available"
                    )
                    click.echo(f"Using profile: {profile_name} - {profile_desc}")
                    return profile_name

                # Multiple profiles available, prompt for selection
                # Determine default profile from active_profile field
                active_profile = profile_data.get("active_profile")
                default_index = 1  # Default to first profile

                if (
                    active_profile
                    and isinstance(active_profile, str)
                    and active_profile in profile_names
                ):
                    # Use active_profile as default if it exists in profiles
                    default_index = profile_names.index(active_profile) + 1

                click.echo("\nAvailable profiles:")
                for i, profile_name in enumerate(profile_names, 1):
                    profile_config = profiles[profile_name]
                    description = profile_config.get(
                        "profile_description", "No description available"
                    )
                    is_default = i == default_index
                    # Format entire line with bold styling for default option
                    default_indicator = " (default)" if is_default else ""
                    option_line = f"  {i}. {profile_name}{default_indicator}"
                    click.echo(self._format_option_line(option_line, is_default))
                    description_line = f"     {description}"
                    click.echo(self._format_option_line(description_line, is_default))

                try:
                    choice = click.prompt(
                        "Select a profile",
                        type=click.Choice(
                            [str(i) for i in range(1, len(profile_names) + 1)]
                        ),
                        default=str(default_index),
                    )
                    return profile_names[int(choice) - 1]
                except click.Abort:
                    raise NavigateBackException() from None

        except NavigateBackException:
            # Re-raise NavigateBackException to allow navigation loop to catch it
            raise
        except yaml.YAMLError:
            Log.warning(f"Failed to parse team-profile.yaml for team '{team_name}'")
            return None
        except Exception as e:
            Log.warning(f"Failed to load profiles for team '{team_name}': {e}")
            return None

    def _update_team_profile_from_selection(
        self,
        project_root: Path,
        selected_team: str,
        selected_profile: str,
        filesystem: FileSystem,
    ) -> None:
        """Update team-profile.yaml with selected profile during init.

        Reads the bundled team-profile.yaml template, updates the active_profile field
        with the user's selection, and writes it to the project's team directory.

        Args:
            project_root: Root directory of the project being initialized
            selected_team: Name of the team being initialized
            selected_profile: Profile name selected by user
            filesystem: FileSystem instance for file operations

        Note:
            This method handles errors gracefully, logging warnings without failing init.
            Profile update is considered optional enhancement to core functionality.
        """
        try:
            # Read bundled team-profile.yaml template
            with importlib.resources.as_file(
                importlib.resources.files("pantheon")
                / "_templates"
                / "pantheon-teams"
                / selected_team
                / "team-profile.yaml"
            ) as bundled_profile_path:
                if not bundled_profile_path.exists():
                    Log.warning(
                        f"Bundled team-profile.yaml not found for team '{selected_team}'"
                    )
                    return

                # Load the bundled profile
                bundled_content = bundled_profile_path.read_text(encoding="utf-8")
                profile_data = yaml.safe_load(bundled_content)

                # Validate profile_data structure
                if not isinstance(profile_data, dict):
                    Log.warning(
                        f"Invalid team-profile.yaml structure for team '{selected_team}'"
                    )
                    return

                # Update active_profile field
                profile_data["active_profile"] = selected_profile

                # Write updated profile to project team directory
                project_profile_path = (
                    project_root
                    / "pantheon-teams"
                    / selected_team
                    / "team-profile.yaml"
                )
                updated_content = yaml.safe_dump(profile_data, default_flow_style=False)
                filesystem.write_text(project_profile_path, updated_content)

        except FileNotFoundError as e:
            Log.warning(
                f"Failed to find team-profile.yaml for team '{selected_team}': {e}"
            )
        except yaml.YAMLError as e:
            Log.warning(
                f"Failed to parse team-profile.yaml for team '{selected_team}': {e}"
            )
        except KeyError as e:
            Log.warning(
                f"Missing required field in team-profile.yaml for team '{selected_team}': {e}"
            )
        except Exception as e:
            # Final fallback for unexpected errors
            Log.warning(f"Failed to update team-profile.yaml: {e}")

    def init_project(self) -> str:
        """Initialize a Pantheon project with a starter team package.

        Returns:
            Success message describing the initialization result

        Raises:
            BadInputError: If initialization fails or user cancels
        """
        # Get the filesystem - either from minimal setup or from workspace
        filesystem = getattr(self, "_filesystem", None)
        if filesystem is None and self._workspace is not None:
            # We have a workspace, get the filesystem from it
            filesystem = self._workspace._filesystem
        if filesystem is None:
            raise BadInputError("Filesystem not available for project initialization")

        current_dir = Path.cwd()

        # Step 1: Discover bundled teams
        available_teams = self._discover_bundled_teams()

        # Step 2: Interactive team and profile selection with navigation loop
        # Allow user to press ESC during profile selection to return to team selection
        max_iterations = 10  # Prevent infinite loop
        iteration = 0
        selected_team = None
        selected_profile = None

        while iteration < max_iterations:
            iteration += 1

            # Step 2a: Interactive team selection
            selected_team = self._select_team_interactive(available_teams)

            # Step 2b: Interactive profile selection (if profiles are available)
            try:
                selected_profile = self._select_profile_interactive(selected_team)
                # Profile selection succeeded, exit the loop
                break
            except NavigateBackException:
                # User pressed ESC during profile selection, go back to team selection
                click.echo("\nReturning to team selection...")
                continue

        if iteration >= max_iterations:
            raise BadInputError(
                "Maximum navigation attempts exceeded. Please restart initialization."
            )

        # Step 3: Check if project is already initialized
        project_config_path = current_dir / ".pantheon_project"
        is_existing_project = project_config_path.exists()

        # Step 4: Set up project directories
        teams_dir = current_dir / "pantheon-teams"
        selected_team_dir = teams_dir / selected_team
        artifacts_dir = current_dir / "pantheon-artifacts"

        try:
            # Create pantheon-teams directory if it doesn't exist
            if not teams_dir.exists():
                teams_dir.mkdir(parents=True)

            # Step 5: Copy team template if it doesn't exist or if explicitly requested
            if not selected_team_dir.exists():
                click.echo(f"Setting up team '{selected_team}'...")
                self._copy_team_template(selected_team, selected_team_dir)
                action_taken = f"Team '{selected_team}' installed"
            else:
                action_taken = f"Switched to existing team '{selected_team}'"

            # Step 6: Create artifacts directory and .gitignore
            if not artifacts_dir.exists():
                from .workspace import TEMP_SUBDIR

                artifacts_dir.mkdir(parents=True)
                # Create tmp subdirectory
                (artifacts_dir / TEMP_SUBDIR).mkdir(exist_ok=True)
                # Create .gitignore
                gitignore_path = artifacts_dir / ".gitignore"
                filesystem.write_text(gitignore_path, f"/{TEMP_SUBDIR}/\n")

            # Step 6a: Create directories from team-data.yaml path values
            try:
                # Extract paths from team-data.yaml (handles missing file gracefully)
                team_data_paths = self._extract_team_data_paths(
                    current_dir, artifacts_dir, selected_team_dir
                )

                # Create directories with security validation
                created_dirs = self._create_team_data_directories(
                    current_dir, team_data_paths
                )

                if created_dirs:
                    click.echo("Created directories from team-data paths:")
                    for dir_path in created_dirs:
                        # Display relative path for readability
                        try:
                            relative_path = dir_path.relative_to(current_dir)
                            self._display_created_directory(relative_path)
                        except ValueError:
                            # Fallback to absolute path if relative fails
                            self._display_created_directory(dir_path)
            except Exception as e:
                # Log warning but don't fail init - directory creation is optional
                Log.warning(f"Failed to create team-data directories: {e}")

            # Step 6b: Optional Claude agent installation
            self._prompt_claude_agent_installation(
                selected_team, selected_team_dir, current_dir
            )
            # Step 6c: Optional CLAUDE.md protocol append
            claude_md_msg = self._prompt_claude_md_append(current_dir)

            # Step 6d: Optional OpenCode agent installatin and  AGENTS.md instructions append
            self._prompt_opencode_agent_installation(
                selected_team, selected_team_dir, current_dir
            )
            agents_md_msg = self._prompt_agents_md_append(current_dir)

            # Step 6e: Optional GEMINI.md instructions append
            gemini_md_msg = self._prompt_gemini_md_append(current_dir)

            # Step 6f: Optional gitignore management
            gitignore_msg = self._prompt_gitignore_management(current_dir)

            # Step 6g: Update team-profile.yaml with selected profile (if applicable)
            if selected_profile:
                self._update_team_profile_from_selection(
                    current_dir, selected_team, selected_profile, filesystem
                )

            # Construct README path for completion message
            readme_path = selected_team_dir / "README.md"

            # Step 7: Create/update .pantheon_project configuration
            config_content = f"""# Pantheon project configuration
active_team: {selected_team}
artifacts_root: pantheon-artifacts

# Optional: Control when temporary files are cleaned up (default: always)
# Values: "always", "on_failure", "never"
temp_file_cleanup: always

# Optional: Audit logging configuration (disabled by default)
# audit_enabled: false
# Directory is always resolved under artifacts_root
# audit_directory: pantheon-audit
"""
            filesystem.write_text(project_config_path, config_content)

            # Build success message
            if is_existing_project:
                success_msg = f"Project updated successfully. {action_taken}."
            else:
                success_msg = (
                    f"Project initialized successfully with team '{selected_team}'."
                )

            # Add CLAUDE.md append feedback if protocol was appended
            if claude_md_msg:
                success_msg += f" {claude_md_msg}"

            # Add AGENTS.md append feedback if instructions were appended
            if agents_md_msg:
                success_msg += f" {agents_md_msg}"

            # Add GEMINI.md append feedback if instructions were appended
            if gemini_md_msg:
                success_msg += f" {gemini_md_msg}"

            # Add gitignore append feedback if entries were added
            if gitignore_msg:
                success_msg += f" {gitignore_msg}"

            # Display configuration file locations
            self._display_config_file_locations(current_dir, selected_team)

            # Add README path to success message
            success_msg += (
                f"\n\nGet started with the team documentation at: {readme_path}"
            )

            return success_msg

        except Exception as e:
            raise BadInputError(f"Failed to initialize project: {e}") from e

    def _extract_team_data_paths(
        self, project_root: Path, artifacts_root: Path, team_dir: Path
    ) -> list[Path]:
        """Extract and render directory paths from team-data.yaml.

        Reads team-data.yaml directly from team directory, renders Jinja2 templates
        with project context, and extracts all path values for directory creation.

        Args:
            project_root: Absolute path to project root
            artifacts_root: Absolute path to artifacts root directory
            team_dir: Absolute path to the team directory containing team-data.yaml

        Returns:
            List of absolute Path objects for directories to create

        Raises:
            FileNotFoundError: If team-data.yaml doesn't exist
        """
        # Get filesystem for reading team-data.yaml
        filesystem = getattr(self, "_filesystem", None)
        if filesystem is None and self._workspace is not None:
            filesystem = self._workspace._filesystem
        if filesystem is None:
            Log.debug("Filesystem not available - skipping directory creation")
            return []

        # Read team-data.yaml directly from team directory
        team_data_path = team_dir / "team-data.yaml"
        try:
            team_data_raw = filesystem.read_text(team_data_path)
        except FileNotFoundError:
            # Team doesn't have team-data.yaml - return empty list
            Log.debug("No team-data.yaml found - skipping directory creation")
            return []

        # Render Jinja2 templates with project context
        try:
            from jinja2 import Template

            template = Template(team_data_raw)
            rendered_content = template.render(
                pantheon_artifacts_root=str(artifacts_root),
                pantheon_project_root=str(project_root),
            )
        except Exception as e:
            Log.warning(f"Failed to render team-data.yaml templates: {e}")
            return []

        # Parse YAML to extract path values
        try:
            team_data = yaml.safe_load(rendered_content)
        except Exception as e:
            Log.warning(f"Failed to parse team-data.yaml: {e}")
            return []

        if not isinstance(team_data, dict):
            Log.debug(
                "team-data.yaml is not a dictionary - skipping directory creation"
            )
            return []

        # Extract path values
        paths_section = team_data.get("path", {})
        if not isinstance(paths_section, dict):
            Log.debug("No 'path' section found in team-data.yaml")
            return []

        # Collect all path values recursively
        def extract_paths(obj: Any, collected: list[str]) -> None:
            """Recursively extract string path values from nested dicts."""
            if isinstance(obj, dict):
                for value in obj.values():
                    extract_paths(value, collected)
            elif isinstance(obj, str) and obj:  # Filter out empty strings
                collected.append(obj)

        path_strings: list[str] = []
        extract_paths(paths_section, path_strings)

        # Convert to Path objects
        path_objects: list[Path] = []
        for path_str in path_strings:
            try:
                # Resolve to absolute path
                path_obj = Path(path_str)
                if not path_obj.is_absolute():
                    path_obj = project_root / path_obj
                path_objects.append(path_obj.resolve())
            except Exception as e:
                Log.warning(f"Invalid path '{path_str}': {e}")
                continue

        return path_objects

    def _display_created_directory(self, relative_path: Path) -> None:
        """Display feedback for a created directory.

        Args:
            relative_path: Path relative to project root for display
        """
        click.echo(f"  Created directory: {relative_path}")

    def _get_config_file_paths(
        self, project_root: Path, selected_team: str
    ) -> dict[str, Path]:
        """Get paths to configuration files for display.

        Args:
            project_root: Absolute path to project root
            selected_team: Name of the selected team

        Returns:
            Dictionary mapping file descriptions to absolute paths
        """
        return {
            ".pantheon_project": project_root / ".pantheon_project",
            "team-data.yaml": project_root
            / "pantheon-teams"
            / selected_team
            / "team-data.yaml",
            "team-profile.yaml": project_root
            / "pantheon-teams"
            / selected_team
            / "team-profile.yaml",
        }

    def _display_config_file_locations(
        self, project_root: Path, selected_team: str
    ) -> None:
        """Display configuration file locations in user-friendly format.

        Args:
            project_root: Absolute path to project root
            selected_team: Name of the selected team
        """
        paths = self._get_config_file_paths(project_root, selected_team)

        click.echo("\nConfiguration files:")
        click.echo(f"  - .pantheon_project: {paths['.pantheon_project']}")
        click.echo(f"  - team-data.yaml: {paths['team-data.yaml']}")
        click.echo(f"  - team-profile.yaml: {paths['team-profile.yaml']}")

    def _create_team_data_directories(
        self, project_root: Path, directories: list[Path]
    ) -> list[Path]:
        """Create directories from team-data.yaml with security validation.

        Validates that each path is within project boundaries before creation.
        Uses FileSystem abstraction for idempotent directory creation.

        Args:
            project_root: Absolute path to project root
            directories: List of directory paths to create

        Returns:
            List of successfully created directory paths

        Raises:
            BadInputError: If FileSystem is not available
        """
        filesystem = getattr(self, "_filesystem", None)
        if filesystem is None and self._workspace is not None:
            filesystem = self._workspace._filesystem
        if filesystem is None:
            raise BadInputError("Filesystem not available for directory creation")

        created_dirs: list[Path] = []

        for dir_path in directories:
            try:
                # Security validation: ensure path is within project boundaries
                resolved_path = dir_path.resolve()
                resolved_project = project_root.resolve()

                # Check if path is within project root using is_relative_to
                # This prevents path traversal attacks like ../../etc/passwd
                try:
                    resolved_path.relative_to(resolved_project)
                except ValueError:
                    Log.warning(
                        f"Skipping directory outside project boundaries: {dir_path}"
                    )
                    continue

                # Create directory using FileSystem abstraction for testability
                filesystem.mkdir(resolved_path, parents=True, exist_ok=True)
                created_dirs.append(resolved_path)
                Log.debug(f"Created directory: {resolved_path}")

            except Exception as e:
                # Log error but continue with other directories
                Log.warning(f"Failed to create directory {dir_path}: {e}")
                continue

        return created_dirs

    def _copy_team_template(self, team_name: str, destination: Path) -> None:
        """Copy a bundled team template to the project directory.

        Args:
            team_name: Name of the team to copy
            destination: Target directory path

        Raises:
            BadInputError: If team template cannot be copied
        """
        try:
            # Access the bundled team directory
            with importlib.resources.as_file(
                importlib.resources.files("pantheon")
                / "_templates"
                / "pantheon-teams"
                / team_name
            ) as team_source:
                if not team_source.exists():
                    raise BadInputError(f"Team template '{team_name}' not found")

                # Copy the entire team directory
                shutil.copytree(team_source, destination)

        except Exception as e:
            raise BadInputError(
                f"Failed to copy team template '{team_name}': {e}"
            ) from e

    def _discover_team_agents(self, team_dir: Path) -> list[Path]:
        """Discover all agent definition files in the team's agents directory.

        Args:
            team_dir: Path to the team directory

        Returns:
            List of paths to agent .md files, empty list if agents directory doesn't exist
        """

        from .logger import Log
        from .workspace import AGENT_FILE_EXTENSION, AGENTS_SUBDIR

        agents_dir = team_dir / AGENTS_SUBDIR

        # Return empty list if agents directory doesn't exist
        if not self._filesystem.exists(agents_dir):
            Log.debug(
                f"Agents directory not found at {agents_dir}, returning empty list"
            )
            return []

        # Discover all .md files in the agents directory
        agent_files = self._filesystem.glob(agents_dir, f"*{AGENT_FILE_EXTENSION}")

        Log.debug(f"Discovered {len(agent_files)} agent files in {agents_dir}")
        return agent_files

    def _prompt_conflict_strategy(
        self, dest_path: Path, prompt_for_strategy: bool
    ) -> str:
        """Prompt user for conflict resolution (presentation layer).

        Args:
            dest_path: Path to the destination file that conflicts
            prompt_for_strategy: If True, prompt for batch strategy; if False, prompt for single file

        Returns:
            User's choice: 'o' (overwrite), 's' (skip), or 'a' (ask each time)
        """
        import click

        if prompt_for_strategy:
            # First conflict - prompt for batch strategy
            prompt_text = (
                f"File {dest_path.name} already exists. Choose conflict resolution:\n"
                "  (o) overwrite all\n"
                "  (s) skip all\n"
                "  (a) ask for each file"
            )
            choice = click.prompt(
                prompt_text,
                type=click.Choice(["o", "s", "a"], case_sensitive=False),
                show_choices=False,
            )
            return choice.lower()
        # Ask for single file (when strategy is 'a')
        result = click.confirm(
            f"File {dest_path.name} already exists. Overwrite?", default=False
        )
        return "o" if result else "s"

    def _resolve_file_conflict(self, dest_path: Path, conflict_strategy: dict) -> bool:
        """Resolve file conflict when destination file already exists (business logic).

        Args:
            dest_path: Path to the destination file that conflicts
            conflict_strategy: Dict to track user's resolution choice across files

        Returns:
            True to proceed with copying (overwrite), False to skip file
        """
        # Check if we already have a stored strategy
        if "choice" in conflict_strategy:
            choice = conflict_strategy["choice"]
            if choice == "o":  # Overwrite all
                return True
            if choice == "s":  # Skip all
                return False
            if choice == "a":  # Ask each time
                # Delegate to presentation layer for per-file decision
                per_file_choice = self._prompt_conflict_strategy(dest_path, False)
                return per_file_choice == "o"

        # First conflict - delegate to presentation layer for strategy selection
        choice = self._prompt_conflict_strategy(dest_path, True)

        # Store the choice for subsequent conflicts
        conflict_strategy["choice"] = choice

        # Apply the chosen strategy
        if choice == "o":
            return True
        if choice == "s":
            return False
        # choice == "a" - need to ask for this specific file too
        per_file_choice = self._prompt_conflict_strategy(dest_path, False)
        return per_file_choice == "o"

    def _copy_agents_to_platform(
        self,
        agent_files: list[Path],
        team_name: str,
        team_dir: Path,
        project_root: Path,
        platform_config: dict,
    ) -> dict[str, int | list[str]]:
        """Copy agent files to a platform's agents directory with platform-specific configuration.

        Args:
            agent_files: List of agent file paths to copy
            team_name: Name of the team (for target directory)
            team_dir: Path to the team directory
            project_root: Path to the project root
            platform_config: Dictionary with platform-specific configuration:
                - target_base_dir: Base directory path (e.g., '.claude/agents' or '.opencode/agent')
                - platform_display_name: Display name for the platform (e.g., 'Claude' or 'OpenCode')
                - validation_base: Base path for security validation

        Returns:
            Dictionary with counts and files: {'installed': int, 'skipped': int, 'failed': int, 'installed_files': list[str]}
        """

        from .logger import Log

        # Extract platform configuration
        target_base_dir = platform_config["target_base_dir"]
        platform_display_name = platform_config["platform_display_name"]
        validation_base = platform_config["validation_base"]

        # Determine platform agents directory location
        platform_agents_dir = project_root / target_base_dir / team_name

        # Validate path stays within expected boundaries (defense against path traversal)
        try:
            platform_agents_dir.resolve().relative_to(validation_base.resolve())
        except ValueError:
            Log.error(
                f"Invalid team name resulted in path outside {target_base_dir}: {team_name}"
            )
            return {"installed": 0, "skipped": 0, "failed": 0, "installed_files": []}

        # Create target directory structure
        self._filesystem.mkdir(platform_agents_dir, parents=True, exist_ok=True)
        Log.debug(
            f"Created {platform_display_name} agents directory: {platform_agents_dir}"
        )

        # Initialize tracking
        results = {"installed": 0, "skipped": 0, "failed": 0, "installed_files": []}
        conflict_strategy: dict = {}

        # Copy each agent file
        for agent_file in agent_files:
            dest_path = platform_agents_dir / agent_file.name

            try:
                # Check for conflict
                if self._filesystem.exists(dest_path):
                    Log.debug(f"Conflict detected for {agent_file.name}")
                    # Resolve conflict - returns True to overwrite, False to skip
                    should_copy = self._resolve_file_conflict(
                        dest_path, conflict_strategy
                    )
                    if not should_copy:
                        Log.debug(
                            f"Skipping {agent_file.name} due to conflict resolution"
                        )
                        results["skipped"] += 1
                        continue

                # Copy the file using FileSystem abstraction
                content = self._filesystem.read_text(agent_file)
                self._filesystem.write_text(dest_path, content)
                Log.debug(f"Installed agent file: {agent_file.name}")
                results["installed"] += 1
                results["installed_files"].append(agent_file.name)

            except Exception as e:
                Log.warning(f"Failed to copy {agent_file.name}: {e}")
                results["failed"] += 1

        Log.debug(
            f"Agent installation complete: {results['installed']} installed, "
            f"{results['skipped']} skipped, {results['failed']} failed"
        )
        return results

    def _copy_agents_to_claude(
        self,
        agent_files: list[Path],
        team_name: str,
        team_dir: Path,
        project_root: Path,
    ) -> dict[str, int | list[str]]:
        """Copy agent files to Claude's .claude/agents/<team-name>/ directory.

        Args:
            agent_files: List of agent file paths to copy
            team_name: Name of the team (for target directory)
            team_dir: Path to the team directory
            project_root: Path to the project root

        Returns:
            Dictionary with counts and files: {'installed': int, 'skipped': int, 'failed': int, 'installed_files': list[str]}
        """

        # Create Claude-specific platform configuration
        platform_config = {
            "target_base_dir": ".claude/agents",
            "platform_display_name": "Claude",
            "validation_base": project_root / ".claude" / "agents",
        }

        # Delegate to platform-agnostic implementation
        return self._copy_agents_to_platform(
            agent_files, team_name, team_dir, project_root, platform_config
        )

    def _prompt_claude_agent_installation(
        self, selected_team: str, selected_team_dir: Path, project_root: Path
    ) -> None:
        """Prompt user to auto-install team agents for Claude.

        Args:
            selected_team: Name of the selected team
            selected_team_dir: Path to the team directory
            project_root: Path to the project root

        Displays installation feedback directly. No return value.
        """
        import click

        from .logger import Log

        # Prompt user with default 'Yes' for common use case
        install_agents = click.confirm(
            "\nDo you want to auto-install team agents for Claude?",
            default=True,
        )

        if not install_agents:
            return

        try:
            # Discover agent files in the team's agents directory
            agent_files = self._discover_team_agents(selected_team_dir)

            if not agent_files:
                Log.info(f"No agent files found in {selected_team}")
                return

            # Copy agents to Claude directory
            results = self._copy_agents_to_claude(
                agent_files, selected_team, selected_team_dir, project_root
            )

            # Display results
            self._display_agent_installation_result(results, selected_team)

        except Exception as e:
            Log.warning(f"Agent installation failed: {e}")
            click.echo(f"Agent installation encountered errors: {e}")

    def _prompt_opencode_agent_installation(
        self, selected_team: str, selected_team_dir: Path, project_root: Path
    ) -> None:
        """Prompt user to auto-install team agents for OpenCode.

        Args:
            selected_team: Name of the selected team
            selected_team_dir: Path to the team directory
            project_root: Path to the project root

        Displays installation feedback directly. No return value.
        """
        import click

        from .logger import Log

        # Prompt user with default 'Yes' for common use case
        install_agents = click.confirm(
            "\nDo you want to auto-install team agents for OpenCode?",
            default=True,
        )

        if not install_agents:
            return

        try:
            # Discover agent files in the team's agents directory
            agent_files = self._discover_team_agents(selected_team_dir)

            if not agent_files:
                Log.info(f"No agent files found in {selected_team}")
                return

            # Create OpenCode-specific platform configuration
            platform_config = {
                "target_base_dir": ".opencode/agent",
                "platform_display_name": "OpenCode",
                "validation_base": project_root / ".opencode" / "agent",
            }

            # Copy agents to OpenCode directory
            results = self._copy_agents_to_platform(
                agent_files,
                selected_team,
                selected_team_dir,
                project_root,
                platform_config,
            )

            # Display results
            self._display_platform_agent_installation_result(
                results, selected_team, platform_config
            )

        except Exception as e:
            Log.warning(f"Agent installation failed: {e}")
            click.echo(f"Agent installation encountered errors: {e}")

    def _display_platform_agent_installation_result(
        self, results: dict, selected_team: str, platform_config: dict
    ) -> None:
        """Display agent installation results with platform-specific feedback.

        Args:
            results: Dictionary with installation results (installed, skipped, failed, installed_files)
            selected_team: Name of the selected team
            platform_config: Dictionary with platform-specific configuration:
                - target_base_dir: Base directory path for display
                - platform_display_name: Display name for the platform

        Displays detailed installation feedback including installed agent files,
        skipped count, and failed count. No return value - purely display method.
        """
        import click

        installed = results["installed"]
        skipped = results["skipped"]
        failed = results["failed"]
        installed_files = results["installed_files"]

        if installed == 0 and skipped == 0 and failed == 0:
            return

        # Extract platform configuration
        target_base_dir = platform_config["target_base_dir"]

        # Display all installation feedback immediately
        if installed > 0:
            file_list = ", ".join(installed_files)
            click.echo(
                f"Installed agents to {target_base_dir}/{selected_team}/: {file_list}"
            )
        if skipped > 0:
            click.echo(f"Skipped {skipped} agent{'s' if skipped != 1 else ''}")
        if failed > 0:
            click.echo(f"{failed} failed")

    def _display_agent_installation_result(
        self, results: dict, selected_team: str
    ) -> None:
        """Display agent installation results with complete feedback.

        Args:
            results: Dictionary with installation results (installed, skipped, failed, installed_files)
            selected_team: Name of the selected team

        Displays detailed installation feedback including installed agent files,
        skipped count, and failed count. No return value - purely display method.
        """

        # Create Claude-specific platform configuration
        platform_config = {
            "target_base_dir": ".claude/agents",
            "platform_display_name": "Claude",
        }

        # Delegate to platform-agnostic implementation
        self._display_platform_agent_installation_result(
            results, selected_team, platform_config
        )

    @staticmethod
    def _get_protocol_content() -> str:
        """Retrieve Pantheon subagent invocation protocol from bundled template.

        Returns:
            Protocol content from claude_instructions.md template

        Raises:
            FileNotFoundError: If the template file is missing
        """
        from .logger import Log

        Log.debug("Retrieving protocol content from bundled template")

        # Access bundled template using importlib.resources
        template_path = (
            importlib.resources.files("pantheon")
            / "_templates"
            / "agent_instructions"
            / "claude_instructions.md"
        )

        # Read template content
        protocol_content = template_path.read_text()

        if not protocol_content:
            raise FileNotFoundError(
                "Protocol template is empty or missing: claude_instructions.md"
            )

        Log.debug(f"Retrieved {len(protocol_content)} characters of protocol content")
        return protocol_content

    @staticmethod
    def _get_agents_instructions() -> str:
        """Retrieve Pantheon operating protocol instructions from bundled template.

        Returns:
            Instruction content from agents_instructions.md template

        Raises:
            FileNotFoundError: If the template file is missing
        """
        from .logger import Log

        Log.debug("Retrieving Agents.md instructions from bundled template")

        # Access bundled template using importlib.resources
        template_path = (
            importlib.resources.files("pantheon")
            / "_templates"
            / "agent_instructions"
            / "agents_instructions.md"
        )

        # Read template content
        instructions_content = template_path.read_text()

        if not instructions_content:
            raise FileNotFoundError(
                "Instruction template is empty or missing: agents_instructions.md"
            )

        Log.debug(
            f"Retrieved {len(instructions_content)} characters of instruction content"
        )
        return instructions_content

    @staticmethod
    def _get_gemini_instructions() -> str:
        """Retrieve Gemini operating protocol instructions from bundled template.

        Returns:
            Instruction content from gemini_instructions.md template

        Raises:
            FileNotFoundError: If the template file is missing
        """
        from .logger import Log

        Log.debug("Retrieving Gemini instructions from bundled template")

        # Access bundled template using importlib.resources
        template_path = (
            importlib.resources.files("pantheon")
            / "_templates"
            / "agent_instructions"
            / "gemini_instructions.md"
        )

        # Read template content
        instructions_content = template_path.read_text()

        if not instructions_content:
            raise FileNotFoundError(
                "Instruction template is empty or missing: gemini_instructions.md"
            )

        Log.debug(
            f"Retrieved {len(instructions_content)} characters of instruction content"
        )
        return instructions_content

    def _detect_existing_instructions(self, project_root: Path) -> bool:
        """Check if AGENTS.md already contains the Pantheon operating protocol.

        Args:
            project_root: Path to the project root directory

        Returns:
            True if instruction marker found in AGENTS.md, False otherwise
        """
        from .logger import Log

        agents_md_path = project_root / "AGENTS.md"

        # Return False if file doesn't exist
        if not self._filesystem.exists(agents_md_path):
            Log.debug("AGENTS.md does not exist - instructions not present")
            return False

        # Read file content and search for instruction marker
        content = self._filesystem.read_text(agents_md_path)
        instructions_exist = PANTHEON_INSTRUCTIONS_MARKER_START in content

        Log.debug(
            f"Instruction marker {'found' if instructions_exist else 'not found'} in AGENTS.md"
        )
        return instructions_exist

    def _detect_existing_gemini_instructions(self, project_root: Path) -> bool:
        """Check if GEMINI.md already contains the Pantheon operating protocol.

        Args:
            project_root: Path to the project root directory

        Returns:
            True if instruction marker found in GEMINI.md, False otherwise
        """
        from .logger import Log

        gemini_md_path = project_root / "GEMINI.md"

        # Return False if file doesn't exist
        if not self._filesystem.exists(gemini_md_path):
            Log.debug("GEMINI.md does not exist - instructions not present")
            return False

        # Read file content and search for instruction marker
        content = self._filesystem.read_text(gemini_md_path)
        instructions_exist = PANTHEON_INSTRUCTIONS_MARKER_START in content

        Log.debug(
            f"Instruction marker {'found' if instructions_exist else 'not found'} in GEMINI.md"
        )
        return instructions_exist

    def _append_instructions_to_agents_md(self, project_root: Path) -> str:
        """Append Pantheon instructions to AGENTS.md or create new file with instructions.

        Args:
            project_root: Path to the project root directory

        Returns:
            Descriptive message about the operation performed
        """
        from .logger import Log

        # Retrieve instruction content from bundled template
        instructions_content = self._get_agents_instructions()

        # Wrap content with section markers
        wrapped_content = f"{PANTHEON_INSTRUCTIONS_MARKER_START}\n{instructions_content}\n{PANTHEON_INSTRUCTIONS_MARKER_END}"

        # Determine AGENTS.md path
        agents_md_path = project_root / "AGENTS.md"

        # Check if file exists
        if not self._filesystem.exists(agents_md_path):
            # Create new file with wrapped instruction content
            self._filesystem.write_text(agents_md_path, wrapped_content)
            Log.debug(
                f"Created AGENTS.md with Pantheon instructions at {agents_md_path}"
            )
            return "Created AGENTS.md with Pantheon instructions"
        # Append wrapped instructions to existing file with section separator
        existing_content = self._filesystem.read_text(agents_md_path)
        separator = "\n\n---\n\n"
        updated_content = existing_content + separator + wrapped_content
        self._filesystem.write_text(agents_md_path, updated_content)
        Log.debug(
            f"Appended Pantheon instructions to existing AGENTS.md at {agents_md_path}"
        )
        return "Appended Pantheon instructions to existing AGENTS.md"

    def _append_instructions_to_gemini_md(self, project_root: Path) -> str:
        """Append Pantheon instructions to GEMINI.md or create new file with instructions.

        Args:
            project_root: Path to the project root directory

        Returns:
            Descriptive message about the operation performed
        """
        from .logger import Log

        # Retrieve instruction content from bundled template
        instructions_content = self._get_gemini_instructions()

        # Wrap content with section markers
        wrapped_content = f"{PANTHEON_INSTRUCTIONS_MARKER_START}\n{instructions_content}\n{PANTHEON_INSTRUCTIONS_MARKER_END}"

        # Determine GEMINI.md path
        gemini_md_path = project_root / "GEMINI.md"

        # Check if file exists
        if not self._filesystem.exists(gemini_md_path):
            # Create new file with wrapped instruction content
            self._filesystem.write_text(gemini_md_path, wrapped_content)
            Log.debug(
                f"Created GEMINI.md with Pantheon instructions at {gemini_md_path}"
            )
            return "Created GEMINI.md with Pantheon instructions"
        # Append wrapped instructions to existing file with section separator
        existing_content = self._filesystem.read_text(gemini_md_path)
        separator = "\n\n---\n\n"
        updated_content = existing_content + separator + wrapped_content
        self._filesystem.write_text(gemini_md_path, updated_content)
        Log.debug(
            f"Appended Pantheon instructions to existing GEMINI.md at {gemini_md_path}"
        )
        return "Appended Pantheon instructions to existing GEMINI.md"

    def _prompt_agents_md_append(self, project_root: Path) -> str:
        """Prompt user to append Pantheon instructions to AGENTS.md with conservative default.

        Args:
            project_root: Path to the project root directory

        Returns:
            Success message describing append results, empty string if declined or skipped
        """
        import click

        from .logger import Log

        try:
            # Check if instructions already exist
            if self._detect_existing_instructions(project_root):
                Log.info(
                    "Pantheon instructions already exist in AGENTS.md (skipping append)"
                )
                return (
                    "Pantheon instructions already exist in AGENTS.md (skipping append)"
                )

            # Get instructions content before prompting
            instructions_content = self._get_agents_instructions()

            # Display preview of content to append
            self._preview_content(instructions_content)

            # Set default to True for common use case
            default_choice = True

            # Prompt user with reference to preview
            prompt_text = "(Recommended for Codex and OpenCode*) Add Pantheon specific instructions to AGENTS.md? Preview above."
            append_instructions = click.confirm(prompt_text, default=default_choice)

            if not append_instructions:
                return ""

            # Perform append operation
            result_msg = self._append_instructions_to_agents_md(project_root)
            Log.info(result_msg)
            return result_msg

        except Exception as e:
            error_msg = f"AGENTS.md append failed: {e}"
            Log.warning(error_msg)
            return error_msg

    def _prompt_gemini_md_append(self, project_root: Path) -> str:
        """Prompt user to append Pantheon instructions to GEMINI.md with conservative default.

        Args:
            project_root: Path to the project root directory

        Returns:
            Success message describing append results, empty string if declined or skipped
        """
        import click

        from .logger import Log

        try:
            # Check if instructions already exist
            if self._detect_existing_gemini_instructions(project_root):
                Log.info(
                    "Pantheon instructions already exist in GEMINI.md (skipping append)"
                )
                return (
                    "Pantheon instructions already exist in GEMINI.md (skipping append)"
                )

            # Get instructions content before prompting
            instructions_content = self._get_gemini_instructions()

            # Display preview of content to append
            self._preview_content(instructions_content)

            # Set default to True for common use case
            default_choice = True

            # Prompt user with reference to preview
            prompt_text = "(Recommended for Gemini*) Add Pantheon specific instructions to GEMINI.md? Preview above."
            append_instructions = click.confirm(prompt_text, default=default_choice)

            if not append_instructions:
                return ""

            # Perform append operation
            result_msg = self._append_instructions_to_gemini_md(project_root)
            Log.info(result_msg)
            return result_msg

        except Exception as e:
            error_msg = f"GEMINI.md append failed: {e}"
            Log.warning(error_msg)
            return error_msg

    def _detect_existing_protocol(self, project_root: Path) -> bool:
        """Check if CLAUDE.md already contains the Pantheon subagent invocation protocol.

        Args:
            project_root: Path to the project root directory

        Returns:
            True if protocol marker found in CLAUDE.md, False otherwise
        """
        from .logger import Log

        claude_md_path = project_root / "CLAUDE.md"

        # Return False if file doesn't exist
        if not self._filesystem.exists(claude_md_path):
            Log.debug("CLAUDE.md does not exist - protocol not present")
            return False

        # Read file content and search for protocol marker
        content = self._filesystem.read_text(claude_md_path)
        protocol_exists = PANTHEON_INSTRUCTIONS_MARKER_START in content

        Log.debug(
            f"Protocol marker {'found' if protocol_exists else 'not found'} in CLAUDE.md"
        )
        return protocol_exists

    def _detect_gitignore_entries(self, project_root: Path) -> bool:
        """Check if .gitignore already contains Pantheon Framework artifacts marker.

        Args:
            project_root: Path to the project root directory

        Returns:
            True if Pantheon marker found in .gitignore, False otherwise
        """
        from .logger import Log

        gitignore_path = project_root / ".gitignore"

        # Return False if file doesn't exist
        if not self._filesystem.exists(gitignore_path):
            Log.debug(".gitignore does not exist - Pantheon entries not present")
            return False

        # Read file content and search for Pantheon marker
        try:
            content = self._filesystem.read_text(gitignore_path)
            marker = "# Pantheon Framework artifacts"
            entries_exist = marker in content

            Log.debug(
                f"Pantheon marker {'found' if entries_exist else 'not found'} in .gitignore"
            )
            return entries_exist
        except Exception as e:
            Log.warning(f"Error reading .gitignore: {e}")
            return False

    def _append_gitignore_entries(self, project_root: Path) -> None:
        """Append Pantheon entries to .gitignore or create new file with entries.

        Args:
            project_root: Path to the project root directory

        Creates .gitignore if it doesn't exist, or appends Pantheon entries
        if the file exists and doesn't already contain the marker.
        """
        from .logger import Log

        gitignore_path = project_root / ".gitignore"

        # Define Pantheon gitignore entries
        marker = "# Pantheon Framework artifacts"
        entries = f"""{marker}
pantheon-artifacts/
.pantheon_project
pantheon-teams/
"""

        # Check if file exists
        if not self._filesystem.exists(gitignore_path):
            # Create new file with entries
            self._filesystem.write_text(gitignore_path, entries)
            Log.debug(f"Created .gitignore with Pantheon entries at {gitignore_path}")
        else:
            # Append entries to existing file
            existing_content = self._filesystem.read_text(gitignore_path)

            # Add separator if file doesn't end with newline
            separator = (
                "\n" if existing_content and not existing_content.endswith("\n") else ""
            )
            if separator == "":
                separator = "\n\n"  # Add extra newline for section separation

            updated_content = existing_content + separator + entries
            self._filesystem.write_text(gitignore_path, updated_content)
            Log.debug(
                f"Appended Pantheon entries to existing .gitignore at {gitignore_path}"
            )

    def _prompt_gitignore_management(self, project_root: Path) -> str:
        """Prompt user to add Pantheon files to .gitignore with default True.

        Args:
            project_root: Path to the project root directory

        Returns:
            Success message describing gitignore operation, empty string if declined or skipped
        """
        import click

        from .logger import Log

        try:
            # Check if entries already exist
            if self._detect_gitignore_entries(project_root):
                Log.info(
                    "Pantheon entries already exist in .gitignore (skipping append)"
                )
                return ""

            # Prompt user with default False
            add_to_gitignore = click.confirm(
                "\nAdd Pantheon files to .gitignore?",
                default=False,
            )

            if not add_to_gitignore:
                return ""

            # Perform append operation
            self._append_gitignore_entries(project_root)
            result_msg = "Added Pantheon files to .gitignore"
            Log.info(result_msg)
            return result_msg

        except Exception as e:
            # Log warning but don't fail init
            error_msg = f"Gitignore management failed: {e}"
            Log.warning(error_msg)
            return ""

    # Content preview configuration constants
    # 10 lines provides enough context without overwhelming terminal output
    PREVIEW_LINES_TO_SHOW = 10
    # 15-line threshold based on typical protocol/instructions file length
    PREVIEW_TRUNCATION_THRESHOLD = 15

    @staticmethod
    def _preview_content(content: str) -> None:
        """Display a preview of content to be appended with truncation for long content.

        Args:
            content: Content to preview

        Displays first PREVIEW_LINES_TO_SHOW lines if content exceeds
        PREVIEW_TRUNCATION_THRESHOLD lines, otherwise shows full content.
        """
        import click

        lines = content.split("\n")
        total_lines = len(lines)

        click.echo("\n--- Preview of content to append ---")

        # Truncate to first N lines if content exceeds threshold
        if total_lines > CLI.PREVIEW_TRUNCATION_THRESHOLD:
            preview_lines = lines[: CLI.PREVIEW_LINES_TO_SHOW]
            click.echo("\n".join(preview_lines))
            remaining_lines = total_lines - CLI.PREVIEW_LINES_TO_SHOW
            click.echo(f"\n... ({remaining_lines} more lines)")
        else:
            click.echo(content)

        click.echo("--- End preview ---\n")

    def _append_protocol_to_claude_md(self, project_root: Path) -> str:
        """Append Pantheon protocol to CLAUDE.md or create new file with protocol.

        Args:
            project_root: Path to the project root directory

        Returns:
            Descriptive message about the operation performed
        """
        from .logger import Log

        # Retrieve protocol content from bundled template
        protocol_content = self._get_protocol_content()

        # Wrap content with section markers
        wrapped_content = f"{PANTHEON_INSTRUCTIONS_MARKER_START}\n{protocol_content}\n{PANTHEON_INSTRUCTIONS_MARKER_END}"

        # Determine CLAUDE.md path
        claude_md_path = project_root / "CLAUDE.md"

        # Check if file exists
        if not self._filesystem.exists(claude_md_path):
            # Create new file with wrapped protocol content
            self._filesystem.write_text(claude_md_path, wrapped_content)
            Log.debug(f"Created CLAUDE.md with protocol at {claude_md_path}")
            return "Created CLAUDE.md with protocol"
        # Append wrapped protocol to existing file with section separator
        existing_content = self._filesystem.read_text(claude_md_path)
        separator = "\n\n---\n\n"
        updated_content = existing_content + separator + wrapped_content
        self._filesystem.write_text(claude_md_path, updated_content)
        Log.debug(f"Appended protocol to existing CLAUDE.md at {claude_md_path}")
        return "Appended protocol to existing CLAUDE.md"

    def _prompt_claude_md_append(self, project_root: Path) -> str:
        """Prompt user to append Pantheon protocol to CLAUDE.md with smart defaults.

        Args:
            project_root: Path to the project root directory

        Returns:
            Success message describing append results, empty string if declined or skipped
        """
        import click

        from .logger import Log

        try:
            # Check if protocol already exists
            if self._detect_existing_protocol(project_root):
                Log.info(
                    "Pantheon protocol already exists in CLAUDE.md (skipping append)"
                )
                return "Pantheon protocol already exists in CLAUDE.md (skipping append)"

            # Get protocol content before prompting
            protocol_content = self._get_protocol_content()

            # Display preview of content to append
            self._preview_content(protocol_content)

            # Set default to True for common use case
            default_choice = True

            # Prompt user with reference to preview
            prompt_text = "(Recommended for Claude*) Add Pantheon specific instructions to CLAUDE.md? Preview above."
            append_protocol = click.confirm(prompt_text, default=default_choice)

            if not append_protocol:
                return ""

            # Perform append operation
            result_msg = self._append_protocol_to_claude_md(project_root)
            Log.info(result_msg)
            return result_msg

        except Exception as e:
            error_msg = f"CLAUDE.md append failed: {e}"
            Log.warning(error_msg)
            return error_msg


def handle_cli_error(func: F) -> F:
    """Decorator to handle CLI errors and exit codes."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except CLIError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(e.exit_code)
        except Exception as e:
            click.echo(f"Unexpected error: {e}", err=True)
            sys.exit(1)

    return wrapper  # type: ignore[return-value]


def resolve_log_level(
    cli_log_level: str | None, cli_debug: bool, project_config: dict[str, Any]
) -> str:
    """Resolve the final log level using three-tier hierarchy.

    Args:
        cli_log_level: Log level from --log-level flag
        cli_debug: Debug flag from --debug flag
        project_config: Project configuration dictionary

    Returns:
        Resolved log level (DEBUG, INFO, WARNING, ERROR)
    """
    # CLI flags take precedence
    if cli_log_level:
        return cli_log_level.upper()
    if cli_debug:
        return "DEBUG"

    # Check project configuration
    project_log_level = project_config.get("log_level")
    if project_log_level:
        return project_log_level.upper()

    # Default to INFO
    return "INFO"


@click.group()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    help=(
        "Set log level (overrides project configuration). "
        "Use DEBUG for detailed troubleshooting, INFO for normal operations, "
        "WARNING for important notices, ERROR for failures only."
    ),
)
@click.option(
    "--debug",
    is_flag=True,
    help=(
        "Enable debug logging (shorthand for --log-level DEBUG). "
        "Shows detailed component initialization and process execution flow. "
        "Takes precedence over project configuration but is overridden by --log-level."
    ),
)
@click.pass_context
def main(ctx: click.Context, log_level: str | None = None, debug: bool = False) -> None:
    """Pantheon Framework CLI - Operating System for Containerized AI Teams.

    Logging Configuration:

    The CLI supports three-tier logging configuration with the following precedence:
    1. CLI flags (--log-level, --debug) override everything
    2. Project settings (log_level in .pantheon_project) override defaults
    3. Default level (INFO) when no configuration is provided

    Examples:

    \b
    # Use project default (from .pantheon_project)
    pantheon execute create-ticket --actor tech-lead

    \b
    # Override with debug logging for troubleshooting
    pantheon --debug execute create-ticket --actor tech-lead

    \b
    # Set specific log level (overrides --debug if both provided)
    pantheon --log-level WARNING get process --actor engineer
    """
    if ctx.obj is None:
        # Set up dependency injection
        from .artifact_engine import ArtifactEngine
        from .filesystem import FileSystem
        from .logger import configure_logger
        from .process_handler import ProcessHandler
        from .rae_engine import RaeEngine
        from .workspace import (
            CONFIG_KEY_artifacts_root,
            DEFAULT_artifacts_root,
            PantheonWorkspace,
        )

        try:
            # Discover project root and create filesystem
            filesystem = FileSystem()
            project_root = PantheonWorkspace.discover_project_root(filesystem, ".")

            # Check if we're running the init command - allow it to work without an existing project
            is_init_command = len(sys.argv) > 1 and sys.argv[1] == "init"

            if project_root is None and not is_init_command:
                click.echo("Error: Not in a Pantheon project directory", err=True)
                sys.exit(BAD_INPUT)

            # Load project configuration (if we have a project)
            if project_root is not None:
                project_config = PantheonWorkspace.load_project_config(
                    filesystem, project_root
                )
                artifacts_root = project_config.get(
                    CONFIG_KEY_artifacts_root, DEFAULT_artifacts_root
                )
            else:
                # For init command, use defaults
                project_config = {}
                artifacts_root = DEFAULT_artifacts_root

            # Configure logging early using three-tier hierarchy
            resolved_log_level = resolve_log_level(log_level, debug, project_config)
            configure_logger(resolved_log_level)

            from .logger import Log

            Log.debug(f"Configured logging at level: {resolved_log_level}")
            Log.debug(f"Project root discovered at: {project_root}")
            Log.debug(f"Artifacts root set to: {artifacts_root}")

            # Create workspace (if we have a project root)
            if project_root is not None:
                Log.debug("Creating PantheonWorkspace")
                workspace = PantheonWorkspace(project_root, artifacts_root, filesystem)
            else:
                # For init command, we'll create a minimal setup
                workspace = None

            # Create engines (if we have a workspace)
            if workspace is not None:
                Log.debug("Creating ArtifactEngine")
                artifact_engine = ArtifactEngine(workspace)
                Log.debug("Creating RaeEngine")
                rae_engine = RaeEngine(workspace, artifact_engine)
                Log.debug("Creating ProcessHandler")
                process_handler = ProcessHandler(workspace, artifact_engine, rae_engine)

                # Create and store CLI instance
                Log.debug("Creating CLI instance")
                cli_instance = CLI(workspace, process_handler, rae_engine, filesystem)
                ctx.obj = cli_instance
            else:
                # For init command, create a minimal CLI instance
                Log.debug("Creating minimal CLI instance for init")
                cli_instance = CLI(None, None, None, filesystem)  # type: ignore
                cli_instance._filesystem = filesystem  # Store filesystem for init
                ctx.obj = cli_instance

            Log.debug("Pantheon CLI initialized successfully")

        except Exception as e:
            click.echo(f"Error initializing Pantheon CLI: {e}", err=True)
            sys.exit(BAD_INPUT)


@main.group()
@click.pass_context
def get(ctx: click.Context) -> None:
    """Information retrieval commands."""


@get.command()
@click.argument("process_name")
@click.option("--actor", required=True, help="Agent name performing the action")
@click.option("--sections", help="Comma-separated list of sections to retrieve")
@click.pass_context
def process(
    ctx: click.Context, process_name: str, actor: str, sections: str | None = None
) -> None:
    """Get routine content for a process."""
    cli_instance: CLI = ctx.obj
    result = "success"
    try:
        routine_content = cli_instance.get_process(process_name, actor, sections)
        click.echo(routine_content)
    except PermissionDeniedError as e:
        result = "permission_denied"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(
            f"get process {process_name}",
            actor=actor,
            sections=sections,
            result=result,
        )
        sys.exit(PERMISSION_DENIED)
    except BadInputError as e:
        result = "bad_input"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(
            f"get process {process_name}",
            actor=actor,
            sections=sections,
            result=result,
        )
        sys.exit(BAD_INPUT)
    except Exception as e:
        result = "error"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(
            f"get process {process_name}",
            actor=actor,
            sections=sections,
            result=result,
        )
        sys.exit(1)
    else:
        cli_instance._audit_log(
            f"get process {process_name}",
            actor=actor,
            sections=sections,
            result=result,
        )


@get.command()
@click.argument("process_name")
@click.option("--actor", required=True, help="Agent name performing the action")
@click.option("--sections", help="Comma-separated list of sections to retrieve")
@click.pass_context
def schema(
    ctx: click.Context, process_name: str, actor: str, sections: str | None = None
) -> None:
    """Get JSON schema for a process."""
    cli_instance: CLI = ctx.obj
    result = "success"
    try:
        schema_content = cli_instance.get_schema(process_name, actor, sections)
        click.echo(schema_content)
    except PermissionDeniedError as e:
        result = "permission_denied"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(
            f"get schema {process_name}",
            actor=actor,
            sections=sections,
            result=result,
        )
        sys.exit(PERMISSION_DENIED)
    except BadInputError as e:
        result = "bad_input"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(
            f"get schema {process_name}",
            actor=actor,
            sections=sections,
            result=result,
        )
        sys.exit(BAD_INPUT)
    except Exception as e:
        result = "error"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(
            f"get schema {process_name}",
            actor=actor,
            sections=sections,
            result=result,
        )
        sys.exit(1)
    else:
        cli_instance._audit_log(
            f"get schema {process_name}",
            actor=actor,
            sections=sections,
            result=result,
        )


@get.command()
@click.argument("process_name")
@click.option("--actor", required=True, help="Agent name performing the action")
@click.pass_context
def sections(ctx: click.Context, process_name: str, actor: str) -> None:
    """Get available sections for a process."""

    cli_instance: CLI = ctx.obj
    result = "success"
    try:
        sections_payload = cli_instance.get_sections(process_name, actor)
        click.echo(sections_payload)
    except PermissionDeniedError as e:
        result = "permission_denied"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(
            f"get sections {process_name}",
            actor=actor,
            result=result,
        )
        sys.exit(PERMISSION_DENIED)
    except BadInputError as e:
        result = "bad_input"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(
            f"get sections {process_name}",
            actor=actor,
            result=result,
        )
        sys.exit(BAD_INPUT)
    except Exception as e:
        result = "error"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(
            f"get sections {process_name}",
            actor=actor,
            result=result,
        )
        sys.exit(1)
    else:
        cli_instance._audit_log(
            f"get sections {process_name}",
            actor=actor,
            result=result,
        )


@get.command()
@click.option("--process", required=True, help="Process name for tempfile")
@click.option("--actor", required=True, help="Agent name performing the action")
@click.pass_context
def tempfile(ctx: click.Context, process: str, actor: str) -> None:
    """Get temporary file path for process input."""
    cli_instance: CLI = ctx.obj
    result = "success"
    try:
        temp_path = cli_instance.get_tempfile(process, actor)
        click.echo(temp_path)
    except BadInputError as e:
        result = "bad_input"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(f"get tempfile {process}", actor=actor, result=result)
        sys.exit(BAD_INPUT)
    except Exception as e:
        result = "error"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(f"get tempfile {process}", actor=actor, result=result)
        sys.exit(1)
    else:
        cli_instance._audit_log(f"get tempfile {process}", actor=actor, result=result)


@get.command("team-data")
@click.option("--actor", required=True, help="Agent name performing the action")
@click.option("--key", help="Specific key to retrieve (dot notation supported)")
@click.pass_context
def team_data_get(ctx: click.Context, actor: str, key: str | None = None) -> None:
    """Get team data from team-data.yaml."""
    cli_instance: CLI = ctx.obj
    result = "success"
    try:
        team_data_content = cli_instance.get_team_data(actor, key)
        click.echo(team_data_content)
    except BadInputError as e:
        result = "bad_input"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log("get team-data", actor=actor, result=result)
        sys.exit(BAD_INPUT)
    except Exception as e:
        result = "error"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log("get team-data", actor=actor, result=result)
        sys.exit(1)
    else:
        cli_instance._audit_log("get team-data", actor=actor, result=result)


@main.command()
@click.argument("process_name")
@click.option("--actor", required=True, help="Agent name performing the action")
@click.option("--id", help="Artifact ID for GET and UPDATE processes")
@click.option("--sections", help="Comma-separated list of sections to retrieve")
@click.option(
    "--insert-mode",
    type=click.Choice(["append", "prepend"], case_sensitive=False),
    help="Insert mode for UPDATE processes: append to end or prepend to start of sections",
)
@click.option("--from-file", help="Path to JSON input file")
@click.option(
    "--param",
    multiple=True,
    help="Parameter in key=value format (can be used multiple times)",
)
@click.pass_context
def execute(
    ctx: click.Context,
    process_name: str,
    actor: str,
    id: str | None = None,
    sections: str | None = None,
    insert_mode: str | None = None,
    from_file: str | None = None,
    param: tuple[str, ...] = (),
) -> None:
    """Execute a process with input data."""
    cli_instance: CLI = ctx.obj
    result = "success"
    try:
        # Parse --param key=value pairs into kwargs
        params = {}
        for p in param:
            if "=" not in p:
                click.echo(
                    f"Error: Parameter '{p}' must be in key=value format", err=True
                )
                sys.exit(1)
            key, value = p.split("=", 1)
            params[key] = value

        exec_output = cli_instance.execute_process(
            process_name, actor, id, sections, insert_mode, from_file, **params
        )
        click.echo(exec_output)
    except PermissionDeniedError as e:
        result = "permission_denied"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(
            f"execute {process_name}",
            actor=actor,
            id=id,
            sections=sections,
            result=result,
        )
        sys.exit(PERMISSION_DENIED)
    except BadInputError as e:
        result = "bad_input"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(
            f"execute {process_name}",
            actor=actor,
            id=id,
            sections=sections,
            result=result,
        )
        sys.exit(BAD_INPUT)
    except Exception as e:
        result = "error"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(
            f"execute {process_name}",
            actor=actor,
            id=id,
            sections=sections,
            result=result,
        )
        sys.exit(1)
    else:
        cli_instance._audit_log(
            f"execute {process_name}",
            actor=actor,
            id=id,
            sections=sections,
            result=result,
        )


@main.command("set")
@click.argument("target")
@click.option("--actor", required=True, help="Agent name performing the action")
@click.option(
    "--set", "-s", multiple=True, help="Set key=value (dot notation, can be repeated)"
)
@click.option(
    "--del",
    "-d",
    "delete_keys",
    multiple=True,
    help="Delete key (dot notation, can be repeated)",
)
@click.pass_context
def set_command(
    ctx: click.Context,
    target: str,
    actor: str,
    set: tuple[str, ...] = (),
    delete_keys: tuple[str, ...] = (),
) -> None:
    """Set or delete keys in framework data files."""
    if target != "team-data":
        click.echo(
            f"Error: Unknown target '{target}'. Currently only 'team-data' is supported.",
            err=True,
        )
        sys.exit(BAD_INPUT)

    cli_instance: CLI = ctx.obj
    result = "success"
    try:
        # Parse --set values
        updates = {}
        for item in set:
            if "=" not in item:
                click.echo(
                    f"Error: Set parameter '{item}' must be in key=value format",
                    err=True,
                )
                sys.exit(BAD_INPUT)
            key, value = item.split("=", 1)
            updates[key] = value

        # Validate that at least one operation is specified
        if not updates and not delete_keys:
            click.echo(
                "Error: Must specify at least one --set or --del operation", err=True
            )
            sys.exit(BAD_INPUT)

        set_result = cli_instance.set_team_data(actor, updates, list(delete_keys))
        click.echo(set_result)
    except BadInputError as e:
        result = "bad_input"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(f"set {target}", actor=actor, result=result)
        sys.exit(BAD_INPUT)
    except Exception as e:
        result = "error"
        click.echo(f"Error: {e}", err=True)
        cli_instance._audit_log(f"set {target}", actor=actor, result=result)
        sys.exit(1)
    else:
        cli_instance._audit_log(f"set {target}", actor=actor, result=result)


@main.command()
@click.pass_context
def init(ctx: click.Context) -> None:
    """Initialize a Pantheon project with a starter team package."""
    try:
        cli_instance: CLI = ctx.obj
        result = cli_instance.init_project()
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
