"""Markdown formatting utilities for template post-processing.

This module provides utilities to fix common markdown formatting issues
in generated templates, particularly from LLM-generated content that
may not handle markdown line break semantics correctly.
"""

import re


def fix_markdown_formatting(content: str) -> str:
    """Fix markdown formatting with Jinja-aware line break handling.

    This addresses LLM-generated templates that don't properly handle markdown
    line break semantics while preserving compact Jinja control structures.

    - Converts single newlines to double newlines for regular markdown content
    - Preserves compact structure around Jinja control tags ({% for %}, {% if %}, etc.)
    - Keeps list items with template variables compact within loops

    Args:
        content: The markdown template content to fix

    Returns:
        Formatted content with proper markdown spacing that preserves Jinja structure
    """
    if not content or not isinstance(content, str):
        return content

    # First normalize multiple consecutive newlines to single newlines
    normalized = re.sub(r"\n\n+", "\n\n", content)

    lines = normalized.split("\n")
    result_lines = []

    for i, line in enumerate(lines):
        result_lines.append(line)

        # Don't add extra newlines after the last line
        if i == len(lines) - 1:
            continue

        next_line = lines[i + 1]

        # Skip adding extra newlines around Jinja control structures
        if _is_jinja_control_line(line) or _is_jinja_control_line(next_line):
            continue
        if line == "":
            continue  # Current line is truly empty (already a paragraph break)
        if next_line == "":
            continue  # Next line is truly empty (already creates paragraph break)
        # Add blank line for regular content to create proper markdown spacing
        result_lines.append("")

    return "\n".join(result_lines)


def _is_jinja_control_line(line: str) -> bool:
    """Check if line contains Jinja control structures that should stay compact.

    Detects:
    - Jinja control tags: {% for %}, {% endfor %}, {% if %}, {% endif %}, {% else %}
    - List items with template variables: - {{ variable }}

    Args:
        line: Line to check for Jinja control structures

    Returns:
        True if line contains Jinja control structures that need compact formatting
    """
    if not line or not isinstance(line, str):
        return False

    stripped = line.strip()

    # Jinja control structure patterns
    jinja_patterns = [
        r"{%\s*for\s+.*%}",  # {% for ... %}
        r"{%\s*endfor\s*%}",  # {% endfor %}
        r"{%\s*if\s+.*%}",  # {% if ... %}
        r"{%\s*endif\s*%}",  # {% endif %}
        r"{%\s*else\s*%}",  # {% else %}
        r"{%\s*elif\s+.*%}",  # {% elif ... %}
        r"^-\s*{{.*}}",  # - {{ variable }} (list items with variables)
    ]

    return any(re.search(pattern, stripped) for pattern in jinja_patterns)
