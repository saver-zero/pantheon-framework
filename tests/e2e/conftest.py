"""Fixtures for end-to-end tests."""

from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

import pytest


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create an isolated temporary directory for project testing."""
    return tmp_path


@pytest.fixture
def pantheon_cli() -> Path:
    """Get path to the pantheon CLI entry point."""
    # Use the installed pantheon command in the current environment
    executable_name = "pantheon.exe" if sys.platform == "win32" else "pantheon"
    return Path(sys.executable).parent / executable_name


@pytest.fixture
def run_pantheon(pantheon_cli: Path, temp_project: Path):
    """Fixture to run pantheon commands in an isolated test environment."""

    def _run_command(
        args: list[str],
        input_text: str | None = None,
        check: bool = True,
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess:
        """Run a pantheon command and return the result."""
        working_dir = cwd or temp_project
        cmd = [str(pantheon_cli)] + args

        return subprocess.run(
            cmd,
            cwd=working_dir,
            input=input_text,
            text=True,
            capture_output=True,
            check=check,
        )

    return _run_command


@pytest.fixture
def setup_test_project(temp_project: Path):
    """Set up a test project with the test team from fixtures."""

    def _setup_project(team_name: str = "pantheon-e2e-test") -> dict[str, Any]:
        """Set up a project with the test team from fixtures."""
        # Get the test fixture team path
        test_root = Path(__file__).parent.parent  # tests/
        fixture_team_path = test_root / "fixtures" / "teams" / team_name

        if not fixture_team_path.exists():
            raise FileNotFoundError(f"Test team fixture not found: {fixture_team_path}")

        # Create project structure manually (since we can't use init with only pantheon-foundry)
        teams_dir = temp_project / "pantheon-teams"
        teams_dir.mkdir(parents=True, exist_ok=True)

        # Copy the test team from fixtures
        target_team_dir = teams_dir / team_name
        shutil.copytree(fixture_team_path, target_team_dir)

        # Create artifacts directory
        artifacts_dir = temp_project / "pantheon-artifacts"
        artifacts_dir.mkdir(exist_ok=True)
        (artifacts_dir / "tmp").mkdir(exist_ok=True)

        # Create .gitignore for artifacts
        (artifacts_dir / ".gitignore").write_text("/tmp/\n")

        # Create .pantheon_project config
        project_config_content = f"""# Pantheon project configuration
active_team: {team_name}
artifacts_root: pantheon-artifacts
"""
        (temp_project / ".pantheon_project").write_text(project_config_content)

        return {
            "project_path": temp_project,
            "team_name": team_name,
            "config": project_config_content,
        }

    return _setup_project


@pytest.fixture
def project_with_team(setup_test_project):
    """Create a test project with pantheon-e2e-test team initialized."""
    return setup_test_project


@pytest.fixture
def sample_ticket_data() -> dict[str, Any]:
    """Sample ticket data for testing create-ticket process."""
    return {
        "title": "User Authentication System",
        "description": "Implement user authentication feature to enable secure user login for the application with JWT-based authentication using bcrypt hashing for secure password storage",
        "plan": "Set up JWT authentication middleware, create user registration endpoint with email validation, implement secure password hashing using bcrypt, add token generation and validation logic, and create login/logout endpoints with proper error handling",
    }


@pytest.fixture
def sample_plan_data() -> dict[str, Any]:
    """Sample plan data for testing update-plan process."""
    return {
        "technical_summary": "Implementation plan for user authentication system",
        "implementation_approach": "Use FastAPI with JWT tokens and bcrypt for password hashing",
        "key_components": [
            "User model with password hashing",
            "JWT token utilities",
            "Authentication endpoints",
            "Password validation middleware",
        ],
        "testing_strategy": "Unit tests for auth utilities, integration tests for endpoints",
    }


@pytest.fixture
def sample_build_spec_data() -> dict[str, Any]:
    """Sample build-spec data for testing build-team-process."""
    return {
        "target_team": "pantheon-test-dev-team",
        "artifact": "task",
        "build_mode": "modular",
        "include_context": True,
        "artifact_sections": ["description", "implementation"],
        "initial_section": "description",
        "section_template": [
            {
                "section": "description",
                "section_description": "Details for the description section.",
                "template": "# {{ title }}\n\n**ID**: T{{ pantheon_artifact_id }}\n\n## Requirements\n{{ requirements }}\n\n",
                "schema": {
                    "title": {
                        "type": "string",
                        "purpose": "To provide a concise, human-readable identifier for the task",
                        "description_for_schema": "A short, descriptive title for the task",
                    },
                    "requirements": {
                        "type": "string",
                        "purpose": "To capture the detailed requirements and specifications for the task",
                        "description_for_schema": "Detailed requirements and specifications for the task",
                    },
                },
            },
            {
                "section": "implementation",
                "section_description": "Details for the implementation section.",
                "template": "## Implementation\n\n{{ implementation_details }}\n\n## Testing Notes\n{{ testing_approach }}\n",
                "schema": {
                    "implementation_details": {
                        "type": "string",
                        "purpose": "To outline the technical implementation approach for the task",
                        "description_for_schema": "Detailed technical implementation approach and steps",
                    },
                    "testing_approach": {
                        "type": "string",
                        "purpose": "To document testing strategy and validation approach",
                        "description_for_schema": "Testing strategy and validation approach for the implementation",
                    },
                },
            },
        ],
        "artifact_location": {
            "directory": "tasks/",
            "filename_template": "T{{ pantheon_artifact_id }}_{{ title | slugify }}.md",
        },
        "permissions": {
            "create": {"allow": ["ticket-handler", "tech-lead"], "deny": []},
            "get": {"allow": ["ticket-handler", "tech-lead", "developer"], "deny": []},
            "update": {"allow": ["tech-lead"], "deny": []},
        },
    }


@pytest.fixture
def sample_build_spec_data_complete() -> dict[str, Any]:
    """Sample build-spec data for testing complete mode build-team-process."""
    return {
        "target_team": "pantheon-test-dev-team",
        "artifact": "agent",
        "build_mode": "complete",
        "include_context": False,
        "artifact_sections": ["persona", "capabilities"],
        "initial_section": "persona",
        "section_template": [
            {
                "section": "persona",
                "section_description": "Details for the persona section.",
                "template": "# {{ agent_name }}\n\n## Role\n{{ role_description }}\n\n## Personality\n{{ personality }}\n\n",
                "schema": {
                    "agent_name": {
                        "type": "string",
                        "purpose": "To provide a clear identifier for the agent",
                        "description_for_schema": "The name of the agent",
                    },
                    "role_description": {
                        "type": "string",
                        "purpose": "To define the agent's primary role and responsibilities",
                        "description_for_schema": "A description of the agent's role",
                    },
                    "personality": {
                        "type": "string",
                        "purpose": "To capture the agent's personality traits",
                        "description_for_schema": "Personality traits and communication style",
                    },
                },
            },
            {
                "section": "capabilities",
                "section_description": "Details for the capabilities section.",
                "template": "## Capabilities\n\n{% for capability in capabilities %}\n- {{ capability }}\n{% endfor %}\n\n## Tools\n{% for tool in tools %}\n- {{ tool }}\n{% endfor %}\n",
                "schema": {
                    "capabilities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "purpose": "To list the agent's core capabilities",
                        "description_for_schema": "List of the agent's main capabilities",
                    },
                    "tools": {
                        "type": "array",
                        "items": {"type": "string"},
                        "purpose": "To specify tools the agent can use",
                        "description_for_schema": "List of tools available to the agent",
                    },
                },
            },
        ],
        "artifact_location": {
            "directory": "agents/",
            "filename_template": "{{ agent_name | lower | replace(' ', '-') }}.md",
        },
        "permissions": {
            "create": {"allow": ["agent-designer"], "deny": []},
            "get": {"allow": ["agent-designer", "tech-lead"], "deny": []},
            "update": {"allow": ["agent-designer"], "deny": []},
        },
    }


@pytest.fixture
def base_ticket_data() -> dict[str, str]:
    """Realistic base ticket data that naturally meets schema constraints."""
    return {
        "title": "Database Schema Design",
        "description": "Design and implement the core database schema with proper indexing and relationships for optimal query performance across all entity types",
        "plan": "Create entity-relationship diagrams, define table structures with appropriate foreign keys, implement database migration scripts using Alembic, add indexes for frequently queried columns, and establish connection pooling for scalability",
        "assignee": "tech-lead",
    }


@pytest.fixture
def sequence_ticket_factory(base_ticket_data):
    """Factory to create ticket data with optional sequence grouping fields."""

    def _create_ticket(
        sequence_number: int | None = None,
        sequence_description: str | None = None,
        **overrides,
    ) -> dict[str, Any]:
        """Create ticket data with optional sequence fields and custom overrides."""
        ticket_data = base_ticket_data.copy()
        ticket_data.update(overrides)

        if sequence_number is not None and sequence_description is not None:
            ticket_data["sequence_number"] = sequence_number
            ticket_data["sequence_description"] = sequence_description

        return ticket_data

    return _create_ticket


@pytest.mark.e2e
def pytest_configure(config):
    """Configure pytest for E2E tests."""
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
