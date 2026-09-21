#!/usr/bin/env python3
"""
Unit tests for CI/CD Auto-Healer (scripts/ci_healer.py).
Tests GitHub Actions run parsing, log error extraction, iteration limiting (Rule L-003),
and atomic commit generation.
"""

import json
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).parent.parent
HEALER_SCRIPT = REPO_ROOT / "scripts" / "ci_healer.py"

# Add scripts directory to sys.path for direct module import if needed
sys.path.insert(0, str(REPO_ROOT / "scripts"))


class TestCiHealer(unittest.TestCase):
    def setUp(self):
        self.assertTrue(HEALER_SCRIPT.exists(), f"ci_healer.py not found at {HEALER_SCRIPT}")
        try:
            import ci_healer
            self.ci_healer = ci_healer
        except ImportError:
            self.ci_healer = None

    def test_module_importable(self):
        """ci_healer module should be importable."""
        self.assertIsNotNone(self.ci_healer, "Failed to import ci_healer module")

    def test_parse_gh_run_json(self):
        """Should correctly parse GitHub Actions run status JSON from gh CLI."""
        raw_json = json.dumps([
            {
                "databaseId": 32161220784,
                "workflowName": "Trusted Release Validation",
                "headBranch": "test-pr-fail",
                "status": "completed",
                "conclusion": "failure",
                "url": "https://github.com/Andrevictor20/xp-multiagent-kit/actions/runs/32161220784"
            }
        ])
        parsed = self.ci_healer.parse_run_status(raw_json)
        self.assertEqual(parsed["run_id"], 32161220784)
        self.assertEqual(parsed["status"], "completed")
        self.assertEqual(parsed["conclusion"], "failure")
        self.assertEqual(parsed["workflow_name"], "Trusted Release Validation")
        self.assertTrue(parsed["is_failure"])

    def test_extract_error_snippet_from_log(self):
        """Should accurately extract ##[error] and stack trace blocks from raw logs."""
        raw_log = """
validate	Push Prisma Schema	2026-08-18T16:37:17.7068781Z ##[group]Run npx prisma db push
validate	Push Prisma Schema	2026-08-18T16:37:18.8958987Z Prisma schema loaded from prisma/schema.prisma.
validate	Push Prisma Schema	2026-08-18T16:37:18.9660248Z Error: P1000: Authentication failed against database server, the provided database credentials for `admin` are not valid.
validate	Push Prisma Schema	2026-08-18T16:37:18.9663142Z Please make sure to provide valid database credentials.
validate	Push Prisma Schema	2026-08-18T16:37:18.9861201Z ##[error]Process completed with exit code 1.
validate	Post Run Actions	2026-08-18T16:37:19.0000000Z Post job cleanup
        """
        snippet = self.ci_healer.extract_error_snippet(raw_log)
        self.assertIn("Authentication failed against database server", snippet)
        self.assertIn("Process completed with exit code 1", snippet)
        # Verify noise like Post job cleanup is not central
        self.assertLessEqual(len(snippet.splitlines()), 30)

    def test_max_iterations_enforcement(self):
        """Heal loop must halt when iteration reaches MAX_ITERATIONS (Rule L-003: max 3)."""
        self.assertEqual(self.ci_healer.MAX_ITERATIONS, 3)
        self.assertTrue(self.ci_healer.can_attempt_next(iteration=1))
        self.assertTrue(self.ci_healer.can_attempt_next(iteration=2))
        self.assertFalse(self.ci_healer.can_attempt_next(iteration=3))
        self.assertTrue(self.ci_healer.is_limit_exceeded(iteration=4))

    def test_generate_atomic_commit_message(self):
        """Should format semantic commit messages for auto-remediations."""
        msg = self.ci_healer.generate_commit_message(
            run_id=32161220784,
            reason="Authentication failed against database",
            iteration=1
        )
        self.assertIn("fix(ci):", msg)
        self.assertIn("32161220784", msg)
        self.assertIn("auto-heal [iter 1/3]", msg)


if __name__ == "__main__":
    unittest.main()
