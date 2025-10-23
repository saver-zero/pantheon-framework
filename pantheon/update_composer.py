"""Helper utilities for consolidated UPDATE process scaffolding."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
import json

_SCHEMABASE = "http://json-schema.org/draft-07/schema#"


def generate_update_schema_jsonnet(section_names: Sequence[str]) -> str:
    """Generate the Jsonnet source for aggregated update schemas.

    For single section: Returns null to indicate no sections.jsonnet should be created.
    For multiple sections: Each section gets its own schema import under ``artifact/sections/<name>.schema.jsonnet``.
    """
    if not section_names:
        raise ValueError("section_names cannot be empty")

    ordered = list(section_names)

    # Single section case: return null to indicate no sections.jsonnet needed
    if len(ordered) == 1:
        return "null"

    # Multiple sections case: generate nested structure
    lines: list[str] = ["local sections = {"]
    for idx, name in enumerate(ordered):
        suffix = "," if idx < len(ordered) - 1 else ""
        lines.append(
            f'  "{name}": import "artifact/sections/{name}.schema.jsonnet"{suffix}'
        )
    lines.append("};")
    lines.append("")
    section_order_json = json.dumps(ordered)
    lines.extend(
        [
            "{",
            f'  "$schema": "{_SCHEMABASE}",',
            '  type: "object",',
            "  properties: {",
            "    section_updates: {",
            '      type: "object",',
            "      additionalProperties: false,",
            "      properties: sections,",
            "    },",
            "    section_order: {",
            '      type: "array",',
            '      description: "Canonical ordering of sections for default workflows.",',
            '      items: { type: "string" },',
            f"      default: {section_order_json},",
            "    },",
            "  },",
            '  required: ["section_updates"],',
            "}",
        ]
    )
    return "\n".join(lines)


def compose_update_schema_payload(
    section_schemas: Mapping[str, Mapping[str, object]],
    *,
    section_order: Sequence[str] | None = None,
) -> dict[str, object]:
    """Compose the runtime JSON schema payload used for validation."""
    if not section_schemas:
        raise ValueError("section_schemas cannot be empty")

    if section_order is None:
        ordered = sorted(section_schemas.keys())
    else:
        ordered = list(section_order)
        if set(ordered) != set(section_schemas.keys()):
            raise ValueError(
                "section_order must contain the same section names as section_schemas"
            )

    properties = {name: deepcopy(section_schemas[name]) for name in ordered}

    return {
        "$schema": _SCHEMABASE,
        "type": "object",
        "properties": {
            "section_updates": {
                "type": "object",
                "additionalProperties": False,
                "properties": properties,
            },
            "section_order": {
                "type": "array",
                "description": "Canonical ordering of sections for default workflows.",
                "items": {"type": "string"},
                "default": ordered,
            },
        },
        "required": ["section_updates"],
    }
