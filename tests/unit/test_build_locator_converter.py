from pantheon.process_handler import ProcessHandler


def test_derive_locator_always_generates_consistent_pattern():
    """Test that locator always generates [artifact_id]_ pattern with literal suffix when present."""
    tpl = "T{{ pantheon_artifact_id }}_{{ title | slugify }}.md"
    locator_jsonnet, used_id, warnings = ProcessHandler._derive_locator_jsonnet(
        tpl, "tickets/"
    )

    assert used_id is True
    assert warnings == []
    # Should always contain the consistent pattern
    assert 'std.extVar("pantheon_artifact_id")' in locator_jsonnet
    assert '"directory": "tickets"' in locator_jsonnet

    # Check the Jsonnet structure - should include literal suffix .md
    expected_pattern = (
        '"^\\\\[" + std.extVar("pantheon_artifact_id") + "\\\\]_.*\\\\.md$"'
    )
    assert expected_pattern in locator_jsonnet


def test_derive_locator_with_no_directory():
    """Test locator generation with empty directory."""
    tpl = "file.v1{{ something }}(draft).md"
    locator_jsonnet, used_id, warnings = ProcessHandler._derive_locator_jsonnet(tpl, "")

    assert used_id is True
    assert warnings == []
    assert '"directory": null' in locator_jsonnet
    # Should generate pattern with literal suffix (draft).md
    expected_pattern = '"^\\\\[" + std.extVar("pantheon_artifact_id") + "\\\\]_.*\\\\(draft\\\\)\\\\.md$"'
    assert expected_pattern in locator_jsonnet


def test_derive_locator_strips_trailing_slash():
    """Test that directory trailing slashes are stripped."""
    tpl = "test{{ pantheon_artifact_id }}.md"
    locator_jsonnet, used_id, warnings = ProcessHandler._derive_locator_jsonnet(
        tpl, "my-dir/"
    )

    assert used_id is True
    assert warnings == []
    assert (
        '"directory": "my-dir"' in locator_jsonnet
    )  # Trailing slash should be stripped
    # Should generate pattern with literal suffix .md
    expected_pattern = (
        '"^\\\\[" + std.extVar("pantheon_artifact_id") + "\\\\]_.*\\\\.md$"'
    )
    assert expected_pattern in locator_jsonnet


def test_derive_locator_with_literal_suffix():
    """Test that literal suffixes are extracted and included in pattern."""
    tpl = "[TB{{ pantheon_artifact_id }}]_{{ target_team }}_team-blueprint.md"
    locator_jsonnet, used_id, warnings = ProcessHandler._derive_locator_jsonnet(
        tpl, "blueprints/"
    )

    assert used_id is True
    assert warnings == []
    assert '"directory": "blueprints"' in locator_jsonnet
    # Should generate pattern with literal suffix
    expected_pattern = '"^\\\\[" + std.extVar("pantheon_artifact_id") + "\\\\]_.*_team-blueprint\\\\.md$"'
    assert expected_pattern in locator_jsonnet


def test_derive_locator_with_complex_literal_suffix():
    """Test pattern matching with complex literal suffix containing special characters."""
    tpl = "file{{ pantheon_artifact_id }}_v1.2.3(draft).md"
    locator_jsonnet, used_id, warnings = ProcessHandler._derive_locator_jsonnet(
        tpl, "docs"
    )

    assert used_id is True
    assert warnings == []
    assert '"directory": "docs"' in locator_jsonnet
    # Should escape special regex characters in literal suffix
    expected_pattern = '"^\\\\[" + std.extVar("pantheon_artifact_id") + "\\\\]_.*_v1\\\\.2\\\\.3\\\\(draft\\\\)\\\\.md$"'
    assert expected_pattern in locator_jsonnet


def test_derive_locator_no_literal_suffix():
    """Test that templates ending with variables work as before."""
    tpl = "{{ prefix }}{{ pantheon_artifact_id }}{{ suffix }}"
    locator_jsonnet, used_id, warnings = ProcessHandler._derive_locator_jsonnet(
        tpl, "output"
    )

    assert used_id is True
    assert warnings == []
    assert '"directory": "output"' in locator_jsonnet
    # Should generate original pattern when no literal suffix
    expected_pattern = '"^\\\\[" + std.extVar("pantheon_artifact_id") + "\\\\]_.*$"'
    assert expected_pattern in locator_jsonnet


def test_derive_locator_with_yaml_suffix():
    """Test that YAML file suffixes are correctly extracted and escaped."""
    tpl = "{{ team_name }}_{{ pantheon_artifact_id }}_team-profile.yaml"
    locator_jsonnet, used_id, warnings = ProcessHandler._derive_locator_jsonnet(
        tpl, "configs"
    )

    assert used_id is True
    assert warnings == []
    assert '"directory": "configs"' in locator_jsonnet
    # Should generate pattern with literal suffix _team-profile.yaml
    expected_pattern = '"^\\\\[" + std.extVar("pantheon_artifact_id") + "\\\\]_.*_team-profile\\\\.yaml$"'
    assert expected_pattern in locator_jsonnet


def test_derive_locator_team_readme_pattern():
    """Test that team-readme pattern is correctly handled without extra ]_ in pattern."""
    tpl = "[TR{{ pantheon_artifact_id }}]_team-readme.md"
    locator_jsonnet, used_id, warnings = ProcessHandler._derive_locator_jsonnet(tpl, "")

    assert used_id is True
    assert warnings == []
    assert '"directory": null' in locator_jsonnet

    # Print the actual output to debug escaping
    print(f"\nActual locator_jsonnet:\n{locator_jsonnet}")

    # Should generate pattern with literal suffix team-readme.md (no extra ]_)
    expected_pattern = (
        '"^\\\\[" + std.extVar("pantheon_artifact_id") + "\\\\]_.*team-readme\\\\.md$"'
    )
    assert expected_pattern in locator_jsonnet
    # Ensure the malformed pattern with extra ]_ is not present
    malformed_pattern = '"^\\\\[" + std.extVar("pantheon_artifact_id") + "\\\\]_.*\\\\]_team-readme\\\\.md$"'
    assert malformed_pattern not in locator_jsonnet


def test_derive_locator_team_readme_escaping_detail():
    """Test escaping for team-readme pattern."""
    # Input
    input_template = "[TR{{ pantheon_artifact_id }}]_team-readme.md"

    # Expected output
    expected_output = (
        '"^\\\\[" + std.extVar("pantheon_artifact_id") + "\\\\]_.*team-readme\\\\.md$"'
    )

    # Actual result
    locator_jsonnet, used_id, warnings = ProcessHandler._derive_locator_jsonnet(
        input_template, ""
    )

    # Test
    assert expected_output in locator_jsonnet, "Expected pattern not found in output"
