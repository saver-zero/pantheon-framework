"""RAE Engine interface for routine retrieval operations.

This module provides the RaeEngine class that handles routine.md content
retrieval for processes. The RAE Engine has a single responsibility of
retrieving routine content using the Workspace for file operations, maintaining
separation of concerns within the framework architecture.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import jinja2

from pantheon.constants import BUILTIN_FULL_PROFILE, PARAM_SECTIONS, PROCESS_TYPE_UPDATE
from pantheon.logger import Log

if TYPE_CHECKING:
    from .artifact_engine import ArtifactEngine
    from .workspace import PantheonWorkspace


class RaeEngine:
    """Routine retrieval specialist for the Pantheon Framework.

    The RaeEngine class provides a single method to retrieve routine.md content
    for a given process. It uses the Workspace for all file operations and
    follows the dependency injection pattern established by other framework
    components.

    This class serves as a simple service layer component with a single
    responsibility - routine content retrieval. It delegates all file system
    operations to the Workspace to maintain architectural boundaries.
    """

    def __init__(
        self, workspace: PantheonWorkspace, artifact_engine: ArtifactEngine
    ) -> None:
        """Initialize the RAE Engine with workspace and artifact engine dependencies."""

        self._workspace = workspace
        self._artifact_engine = artifact_engine

    def get_routine(
        self,
        process_name: str,
        input_params: dict[str, Any] | None = None,
        framework_params: dict[str, Any] | None = None,
        *,
        process_type: str | None = None,
    ) -> str:
        """Render routine.md content for the specified process using Jinja."""

        Log.debug(f"Rendering routine for process '{process_name}'")

        raw_template = self._workspace.get_process_routine(process_name)
        process_dir = self._workspace.get_process_directory(process_name)

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(process_dir)),
            autoescape=False,
            undefined=jinja2.DebugUndefined,
            trim_blocks=False,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        clean_input: dict[str, Any] = dict(input_params or {})
        framework_context: dict[str, Any] = dict(framework_params or {})

        framework_context.setdefault("pantheon_process", process_name)

        if process_type == PROCESS_TYPE_UPDATE:
            self._enrich_update_context(process_name, framework_context)

        # When retrieving routine content, we're NOT executing the process,
        # so use "ROUTINE" operation type to avoid triggering artifact ID generation.
        # Artifact IDs should only be generated during actual CREATE execution.
        operation_type = "ROUTINE"

        template_context = self._artifact_engine._create_template_context(
            clean_input, framework_context, operation_type
        )

        rendered = self._artifact_engine.render_artifact_template(
            raw_template,
            template_context,
            env,
            template_name=f"{process_name}/routine.md",
        )

        Log.debug(
            "Rendered routine for process '%s' (%d characters)",
            process_name,
            len(rendered),
        )
        return rendered

    def _enrich_update_context(
        self, process_name: str, framework_context: dict[str, Any]
    ) -> None:
        """Add update-specific metadata required for routine rendering."""

        # Get full profile structure from framework context for schema compilation
        full_profile = framework_context.get(BUILTIN_FULL_PROFILE, {})

        try:
            schema_content = self._workspace.get_process_schema(process_name)
            compiled_schema = self._artifact_engine.compile_schema(
                schema_content, full_profile, process_name
            )
        except Exception as exc:
            Log.warning(
                "Unable to load update schema metadata for '%s': %s",
                process_name,
                exc,
            )
            return

        properties = compiled_schema.get("properties", {})
        sections_node = (
            properties.get("sections", {}) if isinstance(properties, dict) else {}
        )
        section_props = (
            sections_node.get("properties", {})
            if isinstance(sections_node, dict)
            else {}
        )

        section_order_default = (
            properties.get("section_order", {}) if isinstance(properties, dict) else {}
        )
        default_value = (
            section_order_default.get("default")
            if isinstance(section_order_default, dict)
            else None
        )
        section_order = (
            list(default_value)
            if isinstance(default_value, list)
            else list(section_props.keys())
        )

        if section_order and "section_order" not in framework_context:
            framework_context["section_order"] = section_order

        if section_order and "initial_section" not in framework_context:
            framework_context["initial_section"] = section_order[0]

        if process_name.startswith("update-") and "artifact" not in framework_context:
            framework_context["artifact"] = process_name.split("update-", 1)[1]

        if PARAM_SECTIONS in framework_context and isinstance(
            framework_context[PARAM_SECTIONS], list
        ):
            framework_context[PARAM_SECTIONS] = list(framework_context[PARAM_SECTIONS])
