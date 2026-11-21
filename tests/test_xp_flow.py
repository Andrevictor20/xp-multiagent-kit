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
        self.assertIn("design", wfs)
        self.assertEqual(len(wfs), 9)

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

    def test_output_key_whiteboard_passes_state_between_nodes(self) -> None:
        """ADK State Whiteboard: nó anterior grava output_key e nó seguinte interpola {key}."""
        wf_yaml = (
            'version: "4.0.0"\n'
            "workflows:\n"
            "  wb_flow:\n"
            '    description: "Whiteboard test"\n'
            "    nodes:\n"
            '      - {name: "produce", run: "code", exit_cmd: "echo token_xyz_42", output_key: "artifact_id", on_fail: "abort"}\n'
            '      - {name: "gate", run: "reviewer", exit_cmd: "test \'{artifact_id}\' = \'token_xyz_42\'", on_fail: "abort"}\n'
        )
        with tempfile.TemporaryDirectory() as tmp:
            wf_file = Path(tmp) / "workflow.yaml"
            wf_file.write_text(wf_yaml, encoding="utf-8")
            code = run_flow("wb_flow", custom_workflow_path=str(wf_file))
            self.assertEqual(code, 0)
            st = load_flow_state()
            self.assertEqual(st.get("state", {}).get("artifact_id"), "token_xyz_42")

    def test_loop_agent_retry_and_circuit_breaker(self) -> None:
        """ADK LoopAgent: on_fail='retry' tenta até max_retries e escala com exit 3 se persistir."""
        wf_yaml = (
            'version: "4.0.0"\n'
            "workflows:\n"
            "  retry_flow:\n"
            '    description: "Retry test"\n'
            "    nodes:\n"
            '      - {name: "flaky", run: "builder", exit_cmd: "echo check", on_fail: "retry", max_retries: 2}\n'
            '      - {name: "gate", run: "reviewer", exit_cmd: "echo ok", on_fail: "abort"}\n'
        )
        with tempfile.TemporaryDirectory() as tmp:
            wf_file = Path(tmp) / "workflow.yaml"
            wf_file.write_text(wf_yaml, encoding="utf-8")

            # Falha 1x, passa na 2ª tentativa
            with patch("scripts.xp_flow.run_node_exit_cmd", side_effect=[False, True, True]):
                code = run_flow("retry_flow", custom_workflow_path=str(wf_file))
                self.assertEqual(code, 0)

            reset_flow()
            # Falha sempre -> circuit breaker após max_retries (exit 3)
            with patch("scripts.xp_flow.run_node_exit_cmd", return_value=False):
                code_fail = run_flow("retry_flow", custom_workflow_path=str(wf_file))
                self.assertEqual(code_fail, 3)

    def test_loop_agent_reopen_target_node_on_fail(self) -> None:
        """ADK Writer-Critic Loop: review falhando reabre nó impl_green automaticamente."""
        wf_yaml = (
            'version: "4.0.0"\n'
            "workflows:\n"
            "  critic_loop:\n"
            '    description: "Writer-Critic loop"\n'
            "    nodes:\n"
            '      - {name: "draft", run: "builder", exit_cmd: "echo draft", on_fail: "abort"}\n'
            '      - {name: "critic", run: "reviewer", exit_cmd: "echo review", on_fail: "reopen:draft", max_retries: 2}\n'
            '      - {name: "gate", run: "reviewer", exit_cmd: "echo ok", on_fail: "abort"}\n'
        )
        with tempfile.TemporaryDirectory() as tmp:
            wf_file = Path(tmp) / "workflow.yaml"
            wf_file.write_text(wf_yaml, encoding="utf-8")
            # draft(pass) -> critic(fail -> reopen:draft) -> draft(pass) -> critic(pass) -> gate(pass)
            with patch("scripts.xp_flow.run_node_exit_cmd", side_effect=[True, False, True, True, True]):
                code = run_flow("critic_loop", custom_workflow_path=str(wf_file))
                self.assertEqual(code, 0)
                st = load_flow_state()
                self.assertEqual(len(st["reopened"]), 1)
                self.assertEqual(st["reopened"][0]["node"], "draft")

    def test_parallel_node_executes_all_branches_and_collects_outputs(self) -> None:
        """ADK ParallelAgent: executa ramos concorrentes via ThreadPoolExecutor e grava output_key."""
        wf_yaml = (
            'version: "4.0.0"\n'
            "workflows:\n"
            "  par_flow:\n"
            '    description: "Parallel fan-out"\n'
            "    nodes:\n"
            '      - {name: "checks", run: "code", parallel: [{name: "branch_a", exit_cmd: "echo alpha", output_key: "out_a"}, {name: "branch_b", exit_cmd: "echo beta", output_key: "out_b"}], on_fail: "abort"}\n'
            '      - {name: "gate", run: "reviewer", exit_cmd: "test \'{out_a}-{out_b}\' = \'alpha-beta\'", on_fail: "abort"}\n'
        )
        with tempfile.TemporaryDirectory() as tmp:
            wf_file = Path(tmp) / "workflow.yaml"
            wf_file.write_text(wf_yaml, encoding="utf-8")
            code = run_flow("par_flow", custom_workflow_path=str(wf_file))
            self.assertEqual(code, 0)
            st = load_flow_state()
            self.assertEqual(st["state"]["out_a"], "alpha")
            self.assertEqual(st["state"]["out_b"], "beta")


if __name__ == "__main__":
    unittest.main()
