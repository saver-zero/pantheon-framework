"""Utilities for constructing and asserting ProcessInput payloads in tests."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pantheon.constants import (
    BUILTIN_ACTOR,
    BUILTIN_FULL_PROFILE,
    BUILTIN_PROCESS,
    INPUT_ACTOR,
    INPUT_FRAMEWORK_PARAMS,
    INPUT_INPUT_PARAMS,
    INPUT_PROCESS,
)
from pantheon.process_handler import ProcessInput


def make_process_input(
    process: str,
    actor: str,
    *,
    input_params: Mapping[str, Any] | None = None,
    framework_params: Mapping[str, Any] | None = None,
) -> ProcessInput:
    """Construct a ProcessInput dictionary with separated parameter maps."""

    return ProcessInput(
        {
            INPUT_PROCESS: process,
            INPUT_ACTOR: actor,
            INPUT_INPUT_PARAMS: dict(input_params or {}),
            INPUT_FRAMEWORK_PARAMS: dict(framework_params or {}),
        }
    )


def make_framework_params(
    process: str,
    actor: str,
    **overrides: Any,
) -> dict[str, Any]:
    """Construct a framework parameter mapping with required base fields."""

    params: dict[str, Any] = {
        BUILTIN_PROCESS: process,
        BUILTIN_ACTOR: actor,
        BUILTIN_FULL_PROFILE: {},  # Empty profile by default for tests
    }
    params.update(overrides)
    return params


def assert_input_params(
    process_input: ProcessInput,
    expected: Mapping[str, Any],
) -> None:
    """Assert that ProcessInput contains the expected user input parameters."""

    actual = process_input[INPUT_INPUT_PARAMS]
    assert actual == dict(expected)


def assert_framework_params(
    process_input: ProcessInput,
    expected: Mapping[str, Any],
) -> None:
    """Assert that ProcessInput contains the expected framework parameters."""

    actual = process_input[INPUT_FRAMEWORK_PARAMS]
    assert actual == dict(expected)
