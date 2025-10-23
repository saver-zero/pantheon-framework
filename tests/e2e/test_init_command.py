"""End-to-end tests for pantheon init command."""

from pathlib import Path

import pytest
import yaml


@pytest.mark.e2e
def test_init_creates_project_structure(temp_project: Path, run_pantheon):
    """Test that pantheon init creates the correct project structure."""
    # Run pantheon init with pantheon-team-builder selection
    # Input: team selection (2), then accept defaults for 6 prompts:
    # Claude agent (Y), OpenCode agent (Y), CLAUDE.md (Y), AGENTS.md (Y), GEMINI.md (Y), gitignore (N)
    result = run_pantheon(["init"], input_text="2\n\n\n\n\n\n\n")

    # Verify command succeeded
    assert result.returncode == 0

    # Check that .pantheon_project was created
    project_config_file = temp_project / ".pantheon_project"
    assert project_config_file.exists()

    # Verify project config content
    config = yaml.safe_load(project_config_file.read_text())
    assert config["active_team"] == "pantheon-team-builder"
    assert config["artifacts_root"] == "pantheon-artifacts"

    # Check pantheon-teams directory structure
    teams_dir = temp_project / "pantheon-teams" / "pantheon-team-builder"
    assert teams_dir.exists()
    assert (teams_dir / "team-profile.yaml").exists()
    assert (teams_dir / "agents").is_dir()
    assert (teams_dir / "processes").is_dir()

    # Check artifacts directory
    artifacts_dir = temp_project / "pantheon-artifacts"
    assert artifacts_dir.exists()
    assert (artifacts_dir / ".gitignore").exists()
    assert (artifacts_dir / "temp").is_dir()


@pytest.mark.e2e
def test_init_with_existing_project_switches_team(temp_project: Path, run_pantheon):
    """Test that running init again switches the active team safely."""
    # First initialization
    # Input: team selection (2), then accept defaults for 6 prompts
    result1 = run_pantheon(["init"], input_text="2\n\n\n\n\n\n\n")
    assert result1.returncode == 0

    # Modify a file in the team to test that it's not overwritten
    team_profile = (
        temp_project / "pantheon-teams" / "pantheon-team-builder" / "team-profile.yaml"
    )
    original_content = team_profile.read_text()
    modified_content = original_content + "\n# Custom modification"
    team_profile.write_text(modified_content)

    # Second initialization with same team (should not overwrite)
    # Input: team selection (2), decline Claude (N), decline OpenCode (N), then accept defaults for 4 prompts
    # We decline agent installation to avoid file conflict prompts
    result2 = run_pantheon(["init"], input_text="2\nN\nN\n\n\n\n\n")
    assert result2.returncode == 0

    # Verify modification is preserved
    assert team_profile.read_text() == modified_content

    # Verify config still correct
    project_config = temp_project / ".pantheon_project"
    config = yaml.safe_load(project_config.read_text())
    assert config["active_team"] == "pantheon-team-builder"


@pytest.mark.e2e
def test_init_team_selection_validation(temp_project: Path, run_pantheon):
    """Test that init works when only one team is available."""
    # With only pantheon-team-builder available, init should auto-select it
    # Input: team selection (2), then accept defaults for 6 prompts
    result = run_pantheon(["init"], input_text="2\n\n\n\n\n\n\n")
    assert result.returncode == 0

    # Verify the correct team was selected
    project_config = temp_project / ".pantheon_project"
    config_content = project_config.read_text()
    assert "pantheon-team-builder" in config_content


@pytest.mark.e2e
def test_init_creates_proper_gitignore(temp_project: Path, run_pantheon):
    """Test that init creates proper .gitignore for artifacts directory."""
    # Input: team selection (2), then accept defaults for 6 prompts
    result = run_pantheon(["init"], input_text="2\n\n\n\n\n\n\n")
    assert result.returncode == 0

    gitignore_path = temp_project / "pantheon-artifacts" / ".gitignore"
    assert gitignore_path.exists()

    gitignore_content = gitignore_path.read_text()
    assert "/temp/" in gitignore_content


@pytest.mark.e2e
def test_init_displays_profiles_with_descriptions(temp_project: Path, run_pantheon):
    """Test that init displays available profiles with descriptions after team selection."""
    # Input: team selection (1), profile selection (2), then accept defaults for 6 prompts:
    # Claude agent (Y), OpenCode agent (Y), CLAUDE.md (Y), AGENTS.md (Y), GEMINI.md (Y), gitignore (N)
    result = run_pantheon(["init"], input_text="1\n2\n\n\n\n\n\n\n")

    assert result.returncode == 0

    assert "vibe-coding" in result.stdout
    assert "run-some-tests" in result.stdout
    assert "plan-and-review" in result.stdout

    assert "Optimized for rapid vibe coding" in result.stdout
    assert "Run some tests and read existing docs" in result.stdout
    assert "Recommended profile for reliable long term execution" in result.stdout


@pytest.mark.e2e
def test_init_writes_selected_profile_to_config(temp_project: Path, run_pantheon):
    """Test that init writes selected profile to team-profile.yaml configuration."""
    # Input: team selection (1), profile selection (1), then accept defaults for 6 prompts
    result = run_pantheon(["init"], input_text="1\n1\n\n\n\n\n\n\n")

    assert result.returncode == 0

    # Verify .pantheon_project does NOT contain active_profile
    project_config = temp_project / ".pantheon_project"
    assert project_config.exists()
    config = yaml.safe_load(project_config.read_text())
    assert "active_profile" not in config

    # Verify active_profile is written to team-profile.yaml instead
    team_profile = (
        temp_project / "pantheon-teams" / "pantheon-dev" / "team-profile.yaml"
    )
    assert team_profile.exists()
    profile_data = yaml.safe_load(team_profile.read_text())
    assert "active_profile" in profile_data
    assert profile_data["active_profile"] in [
        "vibe-coding",
        "run-some-tests",
        "plan-and-review",
        "check-everything",
    ]


@pytest.mark.e2e
def test_init_handles_teams_without_profiles_gracefully(
    temp_project: Path, run_pantheon
):
    """Test that init handles teams without profiles section gracefully."""
    # Input: team selection (2), then accept defaults for 6 prompts
    result = run_pantheon(["init"], input_text="2\n\n\n\n\n\n\n")

    assert result.returncode == 0

    project_config = temp_project / ".pantheon_project"
    config_text = project_config.read_text()

    assert (
        "active_profile" not in config_text or config_text.count("active_profile") == 0
    )


@pytest.mark.e2e
def test_init_active_profile_selected_as_default(temp_project: Path, run_pantheon):
    """Test that active_profile is selected as default when user presses enter."""
    # Select pantheon-dev (has active_profile: plan-and-review)
    # Input: team selection (1), accept default profile (\n), then accept defaults for 6 prompts
    result = run_pantheon(["init"], input_text="1\n\n\n\n\n\n\n\n")

    assert result.returncode == 0

    # Verify .pantheon_project contains active_team but NOT active_profile
    project_config = temp_project / ".pantheon_project"
    assert project_config.exists()

    config = yaml.safe_load(project_config.read_text())
    assert config["active_team"] == "pantheon-dev"
    assert "active_profile" not in config

    # Verify the active_profile (plan-and-review) was written to team-profile.yaml
    team_profile = (
        temp_project / "pantheon-teams" / "pantheon-dev" / "team-profile.yaml"
    )
    assert team_profile.exists()
    profile_data = yaml.safe_load(team_profile.read_text())
    assert profile_data["active_profile"] == "plan-and-review", (
        "Expected active_profile 'plan-and-review' to be selected as default"
    )


@pytest.mark.e2e
def test_init_creates_directories_from_team_data_paths(
    temp_project: Path, run_pantheon
):
    """Test that pantheon init creates directories from team-data.yaml path values."""
    # Run pantheon init with pantheon-dev (has team-data.yaml with path definitions)
    # Input: team selection (1), accept default profile, then accept defaults for 6 prompts
    result = run_pantheon(["init"], input_text="1\n\n\n\n\n\n\n\n")

    # Verify command succeeded
    assert result.returncode == 0

    # Verify success message mentions directory creation
    assert "directories from team-data paths" in result.stdout, (
        "Success message should indicate directories were created"
    )

    # Verify artifacts root exists
    artifacts_root = temp_project / "pantheon-artifacts"
    assert artifacts_root.exists()

    # Spot-check: verify at least one subdirectory was created
    # (exact paths may vary if team-data.yaml changes, but some should exist)
    subdirs = [d for d in artifacts_root.iterdir() if d.is_dir() and d.name != "temp"]
    assert len(subdirs) > 0, (
        "At least one directory should be created from team-data.yaml"
    )


@pytest.mark.e2e
def test_init_directory_creation_is_idempotent(temp_project: Path, run_pantheon):
    """Test that directory creation is idempotent - re-running init doesn't fail on existing directories."""
    # Run init first time
    # Input: team selection (1), accept default profile, then accept defaults for 6 prompts
    result1 = run_pantheon(["init"], input_text="1\n\n\n\n\n\n\n\n")
    assert result1.returncode == 0

    # Verify directories were created
    artifacts_root = temp_project / "pantheon-artifacts"
    docs_dir = artifacts_root / "docs"
    assert docs_dir.exists()

    # Run init second time with same team
    # Input: team selection (1), accept default profile, decline Claude (N), decline OpenCode (N), then accept defaults for 4 prompts
    # We decline agent installation to avoid file conflict prompts
    result2 = run_pantheon(["init"], input_text="1\n\nN\nN\n\n\n\n\n")

    # Verify no errors on second run
    assert result2.returncode == 0

    # Verify directories still exist
    assert docs_dir.exists()

    # Verify no error messages about directories already existing
    assert "error" not in result2.stderr.lower() or len(result2.stderr) == 0


@pytest.mark.e2e
def test_init_provides_feedback_about_created_directories(
    temp_project: Path, run_pantheon
):
    """Test that init provides clear feedback about created directories in success message."""
    # Run pantheon init with pantheon-dev
    # Input: team selection (1), accept default profile, then accept defaults for 6 prompts
    result = run_pantheon(["init"], input_text="1\n\n\n\n\n\n\n\n")

    # Verify command succeeded
    assert result.returncode == 0

    # Verify output contains directory creation feedback
    # The success message should mention created directories
    assert (
        "directory" in result.stdout.lower() or "directories" in result.stdout.lower()
    ), "Expected success message to mention directory creation"
