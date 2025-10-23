"""Tests for ProcessHandler acronym generation functionality."""

import unittest

from pantheon.process_handler import ProcessHandler


class TestProcessHandlerAcronym(unittest.TestCase):
    """Test acronym generation from various artifact name formats."""

    def test_generate_artifact_acronym_hyphen_separated(self):
        """Test acronym generation from hyphen-separated names."""
        result = ProcessHandler._generate_artifact_acronym("team-blueprint")
        self.assertEqual(result, "TB")

    def test_generate_artifact_acronym_underscore_separated(self):
        """Test acronym generation from underscore-separated names."""
        result = ProcessHandler._generate_artifact_acronym("user_spec")
        self.assertEqual(result, "US")

    def test_generate_artifact_acronym_space_separated(self):
        """Test acronym generation from space-separated names."""
        result = ProcessHandler._generate_artifact_acronym("project plan document")
        self.assertEqual(result, "PPD")

    def test_generate_artifact_acronym_single_word(self):
        """Test acronym generation from single word."""
        result = ProcessHandler._generate_artifact_acronym("api")
        self.assertEqual(result, "A")

    def test_generate_artifact_acronym_mixed_separators(self):
        """Test acronym generation from mixed separators."""
        result = ProcessHandler._generate_artifact_acronym("user-plan_spec document")
        self.assertEqual(result, "UPSD")

    def test_generate_artifact_acronym_starts_with_numbers(self):
        """Test acronym generation when words start with numbers still extracts letters."""
        result = ProcessHandler._generate_artifact_acronym("123-invalid")
        self.assertEqual(result, "I")

    def test_generate_artifact_acronym_no_valid_letters(self):
        """Test acronym generation with no valid letters falls back to default."""
        result = ProcessHandler._generate_artifact_acronym("123-456-789")
        self.assertEqual(result, "ART")

    def test_generate_artifact_acronym_empty_input(self):
        """Test acronym generation with empty input falls back to default."""
        result = ProcessHandler._generate_artifact_acronym("")
        self.assertEqual(result, "ART")

    def test_generate_artifact_acronym_whitespace_only(self):
        """Test acronym generation with whitespace-only input falls back to default."""
        result = ProcessHandler._generate_artifact_acronym("   ")
        self.assertEqual(result, "ART")

    def test_generate_artifact_acronym_numbers_and_letters(self):
        """Test acronym generation ignores numbers but includes letters."""
        result = ProcessHandler._generate_artifact_acronym("spec1-doc2-test3")
        self.assertEqual(result, "SDT")


if __name__ == "__main__":
    unittest.main()
