#!/usr/bin/env python3
"""tests/test_kit_events.py — Testes unitários para scripts/kit_events.py (AC-4)"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.kit_events import (
    emit,
    classify_failure,
    get_events_path,
)


class TestKitEvents(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.orig_env = os.environ.get("KIT_RUNTIME_DIR")
        os.environ["KIT_RUNTIME_DIR"] = self.test_dir
        os.environ.pop("XP_EVENTS", None)

    def tearDown(self):
        if self.orig_env is not None:
            os.environ["KIT_RUNTIME_DIR"] = self.orig_env
        else:
            os.environ.pop("KIT_RUNTIME_DIR", None)
        os.environ.pop("XP_EVENTS", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_emit_basic_and_truncation(self):
        long_text = "x" * 500
        event = emit("node", name="red", details=long_text)
        self.assertIsNotNone(event)
        self.assertEqual(event["kind"], "node")
        self.assertEqual(len(event["details"]), 200)

        # Check line length in file
        events_file = get_events_path()
        self.assertTrue(events_file.is_file())
        with open(events_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 1)
        self.assertLessEqual(len(lines[0].encode("utf-8")), 300)

    def test_classify_failure(self):
        # Timeout
        cls, sig1 = classify_failure("bash", "Command timed out after 30 seconds")
        self.assertEqual(cls, "timeout")
        self.assertEqual(len(sig1), 10)

        # Invalid args
        cls, sig2 = classify_failure("git", "error: unrecognized argument --invalid")
        self.assertEqual(cls, "invalid_args")

        # Test fail
        cls, sig3 = classify_failure("pytest", "AssertionError: Expected 200, got 500")
        self.assertEqual(cls, "test_fail")

        # Permission
        cls, sig4 = classify_failure("rm", "Permission denied: /etc/hosts")
        self.assertEqual(cls, "permission")

        # Other
        cls, sig5 = classify_failure("python", "KeyError: 'foo'")
        self.assertEqual(cls, "other")

        # Same tool and error line gives same signature
        _, sig1_again = classify_failure("bash", "Command timed out after 30 seconds\nmore info...")
        self.assertEqual(sig1, sig1_again)

    def test_emit_disabled_via_env(self):
        os.environ["XP_EVENTS"] = "0"
        event = emit("gate", status="PASS")
        self.assertIsNone(event)
        self.assertFalse(get_events_path().exists())

    def test_rotation_at_1mb(self):
        events_file = get_events_path()
        # Seed file with ~1MB of dummy data
        events_file.write_bytes(b"x" * (1024 * 1024 + 10))
        emit("node", name="test_rotation")
        # Should have rotated
        rotated = events_file.with_name("events.1.jsonl")
        self.assertTrue(rotated.is_file())


if __name__ == "__main__":
    unittest.main()
