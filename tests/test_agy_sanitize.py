#!/usr/bin/env python3
"""
Unit tests for agy-sanitize utility.
Tests command execution, pipe input, truncation thresholds, and exit code preservation.
"""

import os
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SANITIZE_BIN = REPO_ROOT / "scripts" / "agy-sanitize"


class TestAgySanitize(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SANITIZE_BIN.exists(), f"Sanitize script not found at {SANITIZE_BIN}")

    def test_short_input_not_truncated(self):
        """Outputs with fewer lines than threshold should pass through completely."""
        short_text = "Line 1\nLine 2\nLine 3\n"
        proc = subprocess.run(
            [str(SANITIZE_BIN)],
            input=short_text,
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Line 1", proc.stdout)
        self.assertIn("Line 2", proc.stdout)
        self.assertIn("Line 3", proc.stdout)
        self.assertNotIn("omitidas", proc.stdout)

    def test_long_input_is_truncated(self):
        """Outputs with many lines should be truncated to head + notice + tail."""
        lines = [f"Output line {i}" for i in range(1, 201)]
        long_text = "\n".join(lines) + "\n"

        proc = subprocess.run(
            [str(SANITIZE_BIN)],
            input=long_text,
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0)
        # Head lines should be present
        self.assertIn("Output line 1", proc.stdout)
        self.assertIn("Output line 5", proc.stdout)
        # Middle lines should NOT be present
        self.assertNotIn("Output line 100", proc.stdout)
        # Truncation marker should be present
        self.assertIn("omitidas", proc.stdout)
        # Tail lines should be present
        self.assertIn("Output line 200", proc.stdout)

    def test_command_execution_success(self):
        """Executing a command directly via agy-sanitize cmd args."""
        proc = subprocess.run(
            [str(SANITIZE_BIN), "echo", "Hello from sanitized command"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Hello from sanitized command", proc.stdout)

    def test_exit_code_preservation_on_failure(self):
        """agy-sanitize MUST preserve the exit code of failing commands."""
        proc = subprocess.run(
            [str(SANITIZE_BIN), "bash", "-c", "echo 'failed step' >&2; exit 42"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 42)
        combined = proc.stdout + proc.stderr
        self.assertIn("failed step", combined)

    def test_custom_line_threshold(self):
        """Custom AGY_MAX_LINES environment variable should adjust threshold."""
        lines = [f"Item {i}" for i in range(1, 30)]
        text = "\n".join(lines) + "\n"

        # With default (usually 40), 29 lines is NOT truncated
        proc_default = subprocess.run(
            [str(SANITIZE_BIN)],
            input=text,
            text=True,
            capture_output=True,
        )
        self.assertNotIn("omitidas", proc_default.stdout)

        # With custom limit of 15, it SHOULD be truncated
        env = dict(os.environ, AGY_MAX_LINES="15")
        proc_custom = subprocess.run(
            [str(SANITIZE_BIN)],
            input=text,
            text=True,
            capture_output=True,
            env=env,
        )
        self.assertIn("omitidas", proc_custom.stdout)


if __name__ == "__main__":
    unittest.main()
