"""Unit tests for markdown formatting utilities."""

from pantheon.markdown_formatter import fix_markdown_formatting


class TestMarkdownFormatter:
    """Test the markdown formatting utilities."""

    def test_fix_markdown_formatting_converts_single_to_double_newlines(self):
        """Test that single newlines are converted to double newlines."""
        content = "Line 1\nLine 2\nLine 3"
        expected = "Line 1\n\nLine 2\n\nLine 3"

        result = fix_markdown_formatting(content)

        assert result == expected

    def test_fix_markdown_formatting_preserves_existing_double_newlines(self):
        """Test that existing double newlines are preserved."""
        content = "Line 1\n\nLine 3\nLine 4"
        expected = "Line 1\n\nLine 3\n\nLine 4"

        result = fix_markdown_formatting(content)

        assert result == expected

    def test_fix_markdown_formatting_normalizes_multiple_newlines(self):
        """Test that multiple newlines are normalized to double newlines."""
        content = "Line 1\n\n\n\nLine 3\nLine 4"
        expected = "Line 1\n\nLine 3\n\nLine 4"

        result = fix_markdown_formatting(content)

        assert result == expected

    def test_fix_markdown_formatting_handles_bold_key_value_pattern(self):
        """Test the specific pattern that caused the original issue."""
        content = "#### {{ config.key }}\n**Type:** {{ config.type }}\n**Purpose:** {{ config.purpose }}"
        expected = "#### {{ config.key }}\n\n**Type:** {{ config.type }}\n\n**Purpose:** {{ config.purpose }}"

        result = fix_markdown_formatting(content)

        assert result == expected

    def test_fix_markdown_formatting_handles_empty_content(self):
        """Test that empty content is handled gracefully."""
        assert fix_markdown_formatting("") == ""
        assert fix_markdown_formatting(None) is None

    def test_fix_markdown_formatting_handles_non_string_input(self):
        """Test that non-string input is returned unchanged."""
        assert fix_markdown_formatting(123) == 123
        assert fix_markdown_formatting([]) == []

    def test_fix_markdown_formatting_handles_whitespace_only_content(self):
        """Test that whitespace-only content is handled correctly."""
        content = "   \n   \n   "
        expected = "   \n\n   \n\n   "

        result = fix_markdown_formatting(content)

        assert result == expected

    def test_fix_markdown_formatting_preserves_jinja_for_loops(self):
        """Test that Jinja for loops stay compact without extra spacing."""
        content = "{% for objective in objectives %}\n- {{ objective }}\n{% endfor %}"
        expected = "{% for objective in objectives %}\n- {{ objective }}\n{% endfor %}"

        result = fix_markdown_formatting(content)

        assert result == expected

    def test_fix_markdown_formatting_preserves_jinja_conditionals(self):
        """Test that Jinja if/else blocks stay compact."""
        content = "{% if condition %}\n- {{ item }}\n{% else %}\n- default\n{% endif %}"
        expected = (
            "{% if condition %}\n- {{ item }}\n{% else %}\n- default\n{% endif %}"
        )

        result = fix_markdown_formatting(content)

        assert result == expected

    def test_fix_markdown_formatting_handles_mixed_jinja_and_markdown(self):
        """Test mixed Jinja templates and markdown content formatting."""
        content = "**Type:** {{ config.type }}\n**Purpose:** {{ config.purpose }}\n{% for item in items %}\n- {{ item }}\n{% endfor %}\n**Default:** {{ config.default }}"
        expected = "**Type:** {{ config.type }}\n\n**Purpose:** {{ config.purpose }}\n{% for item in items %}\n- {{ item }}\n{% endfor %}\n**Default:** {{ config.default }}"

        result = fix_markdown_formatting(content)

        assert result == expected

    def test_fix_markdown_formatting_handles_jinja_list_items(self):
        """Test that list items with Jinja variables are preserved."""
        content = "Items:\n- {{ item1 }}\n- {{ item2 }}\n- {{ item3 }}"
        expected = "Items:\n- {{ item1 }}\n- {{ item2 }}\n- {{ item3 }}"

        result = fix_markdown_formatting(content)

        assert result == expected

    def test_fix_markdown_formatting_detects_various_jinja_patterns(self):
        """Test detection of various Jinja control structures."""
        from pantheon.markdown_formatter import _is_jinja_control_line

        # Test various Jinja patterns
        assert _is_jinja_control_line("{% for item in items %}")
        assert _is_jinja_control_line("{% endfor %}")
        assert _is_jinja_control_line("{% if condition %}")
        assert _is_jinja_control_line("{% endif %}")
        assert _is_jinja_control_line("{% else %}")
        assert _is_jinja_control_line("{% elif other_condition %}")
        assert _is_jinja_control_line("- {{ variable }}")

        # Test non-Jinja lines
        assert not _is_jinja_control_line("**Bold:** regular text")
        assert not _is_jinja_control_line("- regular list item")
        assert not _is_jinja_control_line("# Header")
