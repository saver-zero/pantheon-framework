"""Shared constants for the Pantheon Framework.

This module contains all framework-wide constants to ensure consistency
and eliminate duplication across components.
"""

# Process types
PROCESS_TYPE_CREATE = "create"
PROCESS_TYPE_UPDATE = "update"
PROCESS_TYPE_GET = "get"
PROCESS_TYPE_BUILD = "build"

# ProcessResult field names
RESULT_SUCCESS = "success"
RESULT_OUTPUT = "output"
RESULT_ERROR = "error"
RESULT_FILES_CREATED = "files_created"

# ProcessInput field names
INPUT_PROCESS = "process"
INPUT_ACTOR = "actor"
INPUT_INPUT_PARAMS = "input_params"
INPUT_FRAMEWORK_PARAMS = "framework_params"

# Parameter names for read processes
PARAM_SECTIONS = "pantheon_sections"

# Built-in template variable names (pantheon_ prefixed)
BUILTIN_ACTOR = "pantheon_actor"
BUILTIN_PROCESS = "pantheon_process"  # Updated to follow naming convention
BUILTIN_ACTIVE_PROFILE = "pantheon_active_profile"  # Just the active profile config
BUILTIN_FULL_PROFILE = "pantheon_full_profile"  # Complete profile structure
BUILTIN_TIMESTAMP = "pantheon_timestamp"
BUILTIN_DATESTAMP = "pantheon_datestamp"
BUILTIN_ARTIFACT_ID = "pantheon_artifact_id"
BUILTIN_INSERT_MODE = "pantheon_insert_mode"
BUILTIN_PROJECT_ROOT = "pantheon_project_root"  # Full path to project root
BUILTIN_ARTIFACTS_ROOT = "pantheon_artifacts_root"  # Full path to artifacts output root

# Template YAML Front Matter
TEMPLATE_YAML_FRONT_MATTER = "---\ncreated_at: {{ pantheon_timestamp }}\n---"

# Registry of reserved framework parameters
FRAMEWORK_PARAMETERS: frozenset[str] = frozenset(
    {
        BUILTIN_ACTOR,
        BUILTIN_PROCESS,
        BUILTIN_ACTIVE_PROFILE,
        BUILTIN_FULL_PROFILE,
        BUILTIN_TIMESTAMP,
        BUILTIN_DATESTAMP,
        BUILTIN_ARTIFACT_ID,
        BUILTIN_INSERT_MODE,
        BUILTIN_PROJECT_ROOT,
        BUILTIN_ARTIFACTS_ROOT,
        PARAM_SECTIONS,
    }
)

# Framework parameter synonyms for backward compatibility and user convenience
FRAMEWORK_PARAMETER_SYNONYMS: dict[str, str] = {
    "sections": PARAM_SECTIONS,
    "artifact_id": BUILTIN_ARTIFACT_ID,
    "pantheon_sections": PARAM_SECTIONS,
    "pantheon_actor": BUILTIN_ACTOR,
    "pantheon_active_profile": BUILTIN_ACTIVE_PROFILE,
    "pantheon_full_profile": BUILTIN_FULL_PROFILE,
    "pantheon_timestamp": BUILTIN_TIMESTAMP,
    "pantheon_datestamp": BUILTIN_DATESTAMP,
    "pantheon_artifact_id": BUILTIN_ARTIFACT_ID,
    "pantheon_process": BUILTIN_PROCESS,  # Canonical form
    "pantheon_project_root": BUILTIN_PROJECT_ROOT,
    "pantheon_artifacts_root": BUILTIN_ARTIFACTS_ROOT,
}
