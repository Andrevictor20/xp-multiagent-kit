#!/usr/bin/env python3
import os
import tempfile
import unittest
from pathlib import Path

from scripts.apply_ignore_rules import (
    get_template_content,
    apply_ignore_to_directory,
)


class TestApplyIgnoreRules(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_template_content(self):
        content = get_template_content()
        self.assertTrue(len(content) > 100)
        self.assertIn("node_modules", content)
        self.assertIn("__pycache__", content)
        self.assertIn(".git", content)

    def test_apply_ignore_to_directory(self):
        template = "# Ignore Template Test\nnode_modules/\n"
        created = apply_ignore_to_directory(self.project_path, template)

        self.assertIn(".geminiignore", created)
        self.assertIn(".antigravityignore", created)

        gemini_ignore = self.project_path / ".geminiignore"
        antigravity_ignore = self.project_path / ".antigravityignore"

        self.assertTrue(gemini_ignore.is_file())
        self.assertTrue(antigravity_ignore.is_file())
        self.assertEqual(gemini_ignore.read_text(encoding="utf-8"), template)
        self.assertEqual(antigravity_ignore.read_text(encoding="utf-8"), template)

    def test_apply_ignore_handles_permission_error_gracefully(self):
        template = "# Ignore Template Test\n"
        # Test against non-existent or read-only directory
        non_existent = self.project_path / "does_not_exist"
        created = apply_ignore_to_directory(non_existent, template)
        self.assertEqual(created, [])


if __name__ == "__main__":
    unittest.main()
