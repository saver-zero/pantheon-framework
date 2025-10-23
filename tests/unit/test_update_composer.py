from __future__ import annotations

import pytest

from pantheon.update_composer import (
    compose_update_schema_payload,
    generate_update_schema_jsonnet,
)


def test_generate_update_schema_jsonnet_emits_expected_structure() -> None:
    result = generate_update_schema_jsonnet(["context", "plan"])
    assert "artifact/sections/context.schema.jsonnet" in result
    assert "artifact/sections/plan.schema.jsonnet" in result
    assert 'default: ["context", "plan"]' in result


def test_generate_update_schema_jsonnet_requires_sections() -> None:
    with pytest.raises(ValueError):
        generate_update_schema_jsonnet([])


def test_compose_update_schema_payload_uses_sorted_order_when_not_provided() -> None:
    section_schemas = {
        "strategy": {"type": "object"},
        "context": {"type": "string"},
    }
    payload = compose_update_schema_payload(section_schemas)
    assert payload["properties"]["section_order"]["default"] == ["context", "strategy"]
    assert payload["properties"]["section_updates"]["properties"]["context"] == {
        "type": "string"
    }


def test_compose_update_schema_payload_respects_custom_order() -> None:
    section_schemas = {
        "strategy": {"type": "object"},
        "context": {"type": "string"},
    }
    payload = compose_update_schema_payload(
        section_schemas, section_order=["strategy", "context"]
    )
    assert payload["properties"]["section_order"]["default"] == ["strategy", "context"]


def test_compose_update_schema_payload_validates_mismatch() -> None:
    section_schemas = {"context": {"type": "string"}}
    with pytest.raises(ValueError):
        compose_update_schema_payload(section_schemas, section_order=["strategy"])


def test_generate_update_schema_jsonnet_with_hyphenated_section_names() -> None:
    """Test UPDATE schema generation quotes hyphenated section names in object keys."""
    result = generate_update_schema_jsonnet(["high-level-overview", "core-principles"])
    # Verify quoted keys for hyphenated section names
    assert (
        '"high-level-overview": import "artifact/sections/high-level-overview.schema.jsonnet"'
        in result
    )
    assert (
        '"core-principles": import "artifact/sections/core-principles.schema.jsonnet"'
        in result
    )
    # Verify import paths are correct
    assert "artifact/sections/high-level-overview.schema.jsonnet" in result
    assert "artifact/sections/core-principles.schema.jsonnet" in result
    # Verify section order default
    assert 'default: ["high-level-overview", "core-principles"]' in result
