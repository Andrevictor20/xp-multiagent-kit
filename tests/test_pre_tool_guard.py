#!/usr/bin/env python3
"""tests/test_pre_tool_guard.py — Testes unitários para AC-2 (política e pre_tool_guard)"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.hooks.pre_tool_guard import (
    calculate_effective_tier,
    is_action_permitted,
    record_approval,
    has_approval,
    evaluate_policy_for_files_and_commands,
)


class TestPreToolGuard(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.orig_env = os.environ.get("KIT_RUNTIME_DIR")
        os.environ["KIT_RUNTIME_DIR"] = self.test_dir

    def tearDown(self):
        if self.orig_env is not None:
            os.environ["KIT_RUNTIME_DIR"] = self.orig_env
        else:
            os.environ.pop("KIT_RUNTIME_DIR", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_calculate_effective_tier_auto(self):
        tier = calculate_effective_tier(
            declared_risk="L0",
            changed_files=["README.md", "docs/guide.md"],
            commands=["git status", "pytest tests/"],
        )
        self.assertEqual(tier, "auto")

    def test_calculate_effective_tier_escalate_to_review(self):
        tier = calculate_effective_tier(
            declared_risk="L1",
            changed_files=["src/auth/jwt.py"],
            commands=["python3 test.py"],
        )
        self.assertEqual(tier, "review")

    def test_calculate_effective_tier_escalate_to_human(self):
        tier = calculate_effective_tier(
            declared_risk="L1",
            changed_files=["db/migrations/001_init.sql"],
            commands=["python3 migrate.py"],
        )
        self.assertEqual(tier, "human")

    def test_calculate_effective_tier_command_human(self):
        tier = calculate_effective_tier(
            declared_risk="L0",
            changed_files=["README.md"],
            commands=["DROP TABLE users;"],
        )
        self.assertEqual(tier, "human")

    def test_guard_blocks_tampering_policy_and_approvals(self):
        # Trying to edit policy.yaml must be blocked
        ok, reason = is_action_permitted(
            tool_name="edit_file",
            tool_args={"Path": "/repo/.agents/policy.yaml"},
        )
        self.assertFalse(ok)
        self.assertIn("policy.yaml", reason)

        # Trying to edit approvals.json must be blocked
        ok, reason = is_action_permitted(
            tool_name="write_file",
            tool_args={"Path": "/repo/.agents/runtime/approvals.json"},
        )
        self.assertFalse(ok)
        self.assertIn("approvals.json", reason)

    def test_human_tier_requires_approval(self):
        action_id = "migration_20261101"
        self.assertFalse(has_approval(action_id))

        # Check action without approval
        ok, reason = is_action_permitted(
            tool_name="run_command",
            tool_args={"CommandLine": "terraform apply"},
            action_id=action_id,
        )
        self.assertFalse(ok)
        self.assertIn("approval", reason.lower())

        # Now approve
        record_approval(action_id)
        self.assertTrue(has_approval(action_id))

        ok, reason = is_action_permitted(
            tool_name="run_command",
            tool_args={"CommandLine": "terraform apply"},
            action_id=action_id,
        )
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
