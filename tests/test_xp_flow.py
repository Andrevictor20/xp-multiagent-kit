#!/usr/bin/env python3
"""tests/test_xp_flow.py — Testes unitários do executor de fluxo (AC-7)"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.xp_flow import (
    freeze_test_files,
    get_flow_state_path,
    load_flow_state,
    load_workflow_yaml,
    reopen_node,
    reset_flow,
    run_flow,
    save_flow_state,
)


class TestXpFlow(unittest.TestCase):
    def setUp(self) -> None:
        reset_flow()

    def tearDown(self) -> None:
        reset_flow()

    def test_load_workflow_yaml(self) -> None:
        res = load_workflow_yaml()
        wfs = res.get("workflows", {})
        self.assertIn("feature", wfs)
        self.assertIn("fix", wfs)
        self.assertIn("refactor", wfs)
        self.assertIn("chore", wfs)
        self.assertIn("hotfix", wfs)
        self.assertIn("release", wfs)
        self.assertIn("migration", wfs)
        self.assertIn("incident", wfs)
        self.assertEqual(len(wfs), 8)

    def test_freeze_test_files(self) -> None:
        frozen = freeze_test_files()
        self.assertIsInstance(frozen, dict)
        self.assertGreater(len(frozen), 0)
        # Any test file should have a 64-char hex SHA-256
        for path, sha in frozen.items():
            self.assertEqual(len(sha), 64)
            break

    @patch("scripts.xp_flow.run_node_exit_cmd")
    def test_run_flow_step_and_complete(self, mock_cmd) -> None:
        mock_cmd.return_value = True
        # Executa em modo step o workflow chore
        code = run_flow("chore", step_only=True)
        self.assertEqual(code, 0)
        state = load_flow_state()
        self.assertEqual(state["workflow"], "chore")
        self.assertEqual(state["current_idx"], 1)
        self.assertIn("lint_check", state["completed"])

    @patch("scripts.xp_flow.run_node_exit_cmd")
    def test_reopen_node(self, mock_cmd) -> None:
        mock_cmd.return_value = True
        run_flow("chore", step_only=False)
        state = load_flow_state()
        self.assertEqual(state["current_idx"], 2)

        code = reopen_node("lint_check", reason="Regressão de lint detectada")
        self.assertEqual(code, 0)
        state_after = load_flow_state()
        self.assertEqual(state_after["current_idx"], 0)
        self.assertEqual(len(state_after["reopened"]), 1)
        self.assertEqual(state_after["reopened"][0]["reason"], "Regressão de lint detectada")


if __name__ == "__main__":
    unittest.main()
