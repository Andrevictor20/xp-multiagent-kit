#!/usr/bin/env python3
"""
tests/test_antigravity_multiagent.py
TDD Suite for Antigravity-Native Dynamic Multi-Agent Engine (Boss-Worker Pattern).
Covers: Manifest Validation, Visual Dashboard, Execution Grouping, Subagent Payload Formatting,
Task Gatekeeping, Auto-Healing Escalation, and Mission Report Generation.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.antigravity_multiagent import (
    AntigravityMissionEngine,
    MissionManifestError,
    prepare_subagent_payload,
    render_mission_dashboard,
    validate_mission_manifest,
)


class TestAntigravityMultiAgentValidation(unittest.TestCase):
    """AC-1: Manifest validation and schema verification."""

    def test_valid_manifest_passes_validation(self):
        manifest_data = {
            "mission_id": "feat-auth-01",
            "feature_name": "Autenticação JWT com Refresh Token",
            "orchestrator": {
                "model": "gemini-4-argon",
                "effort": "high",
                "max_retries_per_task": 2,
            },
            "global_verification_cmd": "python3 -m unittest discover tests",
            "tasks": [
                {
                    "task_id": "auth-dto",
                    "subagent": "builder",
                    "model": "gemini-3.8-flash",
                    "effort": "low",
                    "execution_group": 1,
                    "allowed_paths": ["src/auth/dto/"],
                    "objective": "Criar DTOs e tipagens de Login e Refresh",
                    "verification_cmd": "python3 -c 'import sys; sys.exit(0)'",
                },
                {
                    "task_id": "auth-service-tdd",
                    "subagent": "builder",
                    "model": "gemini-3.8-flash",
                    "effort": "medium",
                    "execution_group": 2,
                    "allowed_paths": ["src/auth/service/"],
                    "objective": "Implementar AuthService com TDD",
                    "verification_cmd": "python3 -c 'import sys; sys.exit(0)'",
                },
            ],
        }
        validated = validate_mission_manifest(manifest_data)
        self.assertEqual(validated["mission_id"], "feat-auth-01")
        self.assertEqual(len(validated["tasks"]), 2)

    def test_missing_mandatory_fields_raises_error(self):
        invalid_cases = [
            {},
            {"mission_id": "test"},  # Missing feature_name and tasks
            {"mission_id": "test", "feature_name": "Test", "tasks": []},  # Empty tasks
            {
                "mission_id": "test",
                "feature_name": "Test",
                "tasks": [{"task_id": "t1"}],  # Incomplete task
            },
        ]
        for bad_manifest in invalid_cases:
            with self.subTest(manifest=bad_manifest):
                with self.assertRaises(MissionManifestError):
                    validate_mission_manifest(bad_manifest)


class TestAntigravitySubagentPayload(unittest.TestCase):
    """Native Antigravity invoke_subagent payload formatting and contract injection."""

    def test_prepare_subagent_payload_with_memory_and_scope(self):
        task = {
            "task_id": "auth-dto",
            "subagent": "builder",
            "model": "gemini-3.8-flash",
            "effort": "low",
            "execution_group": 1,
            "allowed_paths": ["src/auth/dto/"],
            "objective": "Criar DTOs de autenticacao",
            "verification_cmd": "pytest tests/test_dto.py",
        }
        shared_memory = "CONTRATO: UserPayload deve ter id, email e role."
        payload = prepare_subagent_payload(task, shared_memory=shared_memory)

        self.assertEqual(payload["TypeName"], "builder")
        self.assertIn("FLASH LOW", payload["Role"])
        self.assertEqual(payload["Model"], "flash")
        self.assertEqual(payload["Workspace"], "branch")
        self.assertIn("CONTRATO: UserPayload", payload["Prompt"])
        self.assertIn("src/auth/dto/", payload["Prompt"])
        self.assertIn("pytest tests/test_dto.py", payload["Prompt"])


class TestAntigravityVisualDashboard(unittest.TestCase):
    """Visual feedback verification for multi-agent status tracking."""

    def test_render_mission_dashboard_contains_visual_indicators(self):
        tasks = [
            {
                "task_id": "task-01",
                "subagent": "builder",
                "model": "gemini-3.8-flash",
                "effort": "low",
                "execution_group": 1,
                "allowed_paths": ["src/dto/"],
                "status": "PASS",
                "retries": 0,
            },
            {
                "task_id": "task-02",
                "subagent": "test-guardian",
                "model": "gemini-3.8-flash",
                "effort": "medium",
                "execution_group": 2,
                "allowed_paths": ["tests/"],
                "status": "RUNNING",
                "retries": 1,
            },
        ]
        output = render_mission_dashboard("feat-parallel-01", "Motor Paralelo", tasks)
        self.assertIn("QUADRO DE EXECUÇÃO MULTIAGENTE", output)
        self.assertIn("feat-parallel-01", output)
        self.assertIn("task-01", output)
        self.assertIn("✅ PASS", output)
        self.assertIn("⚡ EM EXECUÇÃO", output)
        self.assertIn("Flash [LOW]", output)
        self.assertIn("Flash [MEDIUM]", output)


class TestAntigravityMissionEngineExecution(unittest.TestCase):
    """AC-2, AC-3, AC-4, AC-5: Execution grouping, gatekeeping, auto-healing, and reporting."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)
        self.agents_dir = self.work_dir / ".agents"
        self.agents_dir.mkdir(parents=True, exist_ok=True)

        self.manifest_file = self.agents_dir / "active-mission.json"
        self.memory_file = self.agents_dir / "MEMORY.md"
        self.memory_file.write_text("# Shared Memory\nTokens e contratos compartilhados.", encoding="utf-8")

        self.manifest_data = {
            "mission_id": "feat-parallel-tdd",
            "feature_name": "Execucao Paralela Multiagente",
            "orchestrator": {
                "model": "gemini-4-argon",
                "effort": "high",
                "max_retries_per_task": 2,
            },
            "global_verification_cmd": "python3 -c 'import sys; sys.exit(0)'",
            "tasks": [
                {
                    "task_id": "g1-task",
                    "subagent": "builder",
                    "model": "gemini-3.8-flash",
                    "effort": "low",
                    "execution_group": 1,
                    "allowed_paths": ["src/g1/"],
                    "objective": "Criar contratos do grupo 1",
                    "verification_cmd": "python3 -c 'import sys; sys.exit(0)'",
                },
                {
                    "task_id": "g2-task-a",
                    "subagent": "builder",
                    "model": "gemini-3.8-flash",
                    "effort": "medium",
                    "execution_group": 2,
                    "allowed_paths": ["src/g2a/"],
                    "objective": "Worker paralelo A",
                    "verification_cmd": "python3 -c 'import sys; sys.exit(0)'",
                },
                {
                    "task_id": "g2-task-b",
                    "subagent": "test-guardian",
                    "model": "gemini-3.8-flash",
                    "effort": "medium",
                    "execution_group": 2,
                    "allowed_paths": ["src/g2b/"],
                    "objective": "Worker paralelo B",
                    "verification_cmd": "python3 -c 'import sys; sys.exit(0)'",
                },
            ],
        }
        self.manifest_file.write_text(json.dumps(self.manifest_data, indent=2), encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_grouping_orders_tasks_chronologically(self):
        engine = AntigravityMissionEngine(project_dir=self.work_dir)
        groups = engine.get_execution_groups(self.manifest_data)
        self.assertEqual(list(groups.keys()), [1, 2])
        self.assertEqual(len(groups[1]), 1)
        self.assertEqual(len(groups[2]), 2)

    def test_successful_mission_run_generates_report(self):
        engine = AntigravityMissionEngine(project_dir=self.work_dir)
        report = engine.run_mission(manifest=self.manifest_data, execute_subagents=False)

        self.assertTrue(report["success"])
        self.assertEqual(report["passed_tasks"], 3)
        self.assertEqual(report["failed_tasks"], 0)

        report_file = self.agents_dir / "mission-report.md"
        self.assertTrue(report_file.is_file())
        content = report_file.read_text(encoding="utf-8")
        self.assertIn("Relatório de Missão Multiagente", content)
        self.assertIn("g1-task", content)
        self.assertIn("g2-task-a", content)
        self.assertIn("g2-task-b", content)

    def test_task_verification_failure_triggers_auto_healing(self):
        self.manifest_data["tasks"][0]["verification_cmd"] = "python3 -c 'import sys; sys.exit(1)'"
        engine = AntigravityMissionEngine(project_dir=self.work_dir)

        # Simular retry: primeira tentativa falha, segunda passa
        attempt_counter = {"count": 0}

        def mock_run_cmd(cmd, **kwargs):
            if "sys.exit(1)" in cmd:
                attempt_counter["count"] += 1
                if attempt_counter["count"] >= 2:
                    return {"exit_code": 0, "stdout": "Self-healed!", "stderr": ""}
                return {"exit_code": 1, "stdout": "", "stderr": "ErrorTrace: NameError"}
            return {"exit_code": 0, "stdout": "OK", "stderr": ""}

        with patch.object(engine, "_execute_command", side_effect=mock_run_cmd):
            report = engine.run_mission(manifest=self.manifest_data, execute_subagents=False)

        self.assertTrue(report["success"])
        self.assertEqual(attempt_counter["count"], 2)
        task_res = next(t for t in report["tasks"] if t["task_id"] == "g1-task")
        self.assertEqual(task_res["retries"], 1)
        self.assertEqual(task_res["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
