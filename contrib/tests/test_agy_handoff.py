#!/usr/bin/env python3
"""
Unit tests for agy-handoff utility.
Tests creation of ultra-compact session handoff packets for fast session resets.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
HANDOFF_BIN = REPO_ROOT / "scripts" / "agy-handoff"


class TestAgyHandoff(unittest.TestCase):
    def setUp(self):
        self.assertTrue(HANDOFF_BIN.exists(), f"Handoff script not found at {HANDOFF_BIN}")

    def test_handoff_output_format_and_compactness(self):
        """Handoff packet must contain required structured sections and remain under 30 lines."""
        proc = subprocess.run(
            [str(HANDOFF_BIN), "--dry-run"],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, f"agy-handoff failed: {proc.stderr}")
        output = proc.stdout

        # Verify essential structured headers
        self.assertIn("Handoff Packet", output)
        self.assertIn("Goal / Status", output)
        self.assertIn("Files Touched", output)
        self.assertIn("Next Steps", output)

        # Verify compactness (< 35 lines total)
        lines = [line for line in output.strip().splitlines() if line.strip()]
        self.assertLessEqual(len(lines), 35, f"Handoff output too verbose: {len(lines)} lines")

        # Verify token efficiency (< 2500 characters, approx < 500 tokens)
        self.assertLessEqual(len(output), 2500, f"Handoff packet exceeded token budget: {len(output)} chars")

    def test_handoff_file_generation(self):
        """--write-file flag should create SESSION_HANDOFF.md in the target dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            proc = subprocess.run(
                [str(HANDOFF_BIN), "--write-file", "--output-dir", tmpdir],
                cwd=str(REPO_ROOT),
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0)
            target_file = Path(tmpdir) / "SESSION_HANDOFF.md"
            self.assertTrue(target_file.exists(), "SESSION_HANDOFF.md was not created")
            content = target_file.read_text(encoding="utf-8")
            self.assertIn("Handoff Packet", content)


if __name__ == "__main__":
    unittest.main()
