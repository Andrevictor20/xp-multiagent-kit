#!/usr/bin/env python3
"""
tests/test_mission_scenarios.py
Acceptance tests for SPEC-007 (XP Multi-Agent Kit v4 Honesty & Corrections).
Scenarios S1 through S15 executed in isolated environments or repository audits.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent.parent
XP_GATE = KIT_ROOT / "scripts" / "xp_gate.py"
XP_CONTRACT = KIT_ROOT / "scripts" / "xp_contract.py"


class TestMissionScenarios(unittest.TestCase):
    """Scenarios S1 through S15 as defined in SPEC-007."""

    def make_temp_repo(self) -> tuple[Path, Path]:
        """Creates an isolated temporary git repository and runtime directory."""
        tmp_dir = Path(tempfile.mkdtemp(prefix="xp_test_repo_"))
        repo_dir = tmp_dir / "repo"
        repo_dir.mkdir()
        runtime_dir = tmp_dir / "runtime"
        runtime_dir.mkdir()

        subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "XP Test"], cwd=str(repo_dir), check=True)
        subprocess.run(["git", "config", "user.email", "test@xp.local"], cwd=str(repo_dir), check=True)

        (repo_dir / "README.md").write_text("# Test Repo\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=str(repo_dir), capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=str(repo_dir), capture_output=True, check=True)

        self.addCleanup(lambda: shutil.rmtree(tmp_dir, ignore_errors=True))
        return repo_dir, runtime_dir

    def run_cmd(self, cmd: list[str], cwd: Path, runtime_dir: Path) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env["KIT_RUNTIME_DIR"] = str(runtime_dir)
        env["PYTHONPATH"] = str(KIT_ROOT)
        return subprocess.run(
            cmd,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
        )

    # ------------------------------------------------------------------
    # S1: nenhum contrato -> exit 1, GATE FAIL step=1
    # ------------------------------------------------------------------
    def test_s1_no_contract_gate_fails_step_1(self):
        repo_dir, runtime_dir = self.make_temp_repo()
        res = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res.returncode, 1, f"Expected exit 1, got {res.returncode}. Output: {res.stdout}\n{res.stderr}")
        self.assertIn("step=1", res.stdout)
        self.assertIn("GATE FAIL", res.stdout)

    # ------------------------------------------------------------------
    # S2: L1, 3 ACs, nenhum teste os referencia, verify_cmd=true -> exit 1; sem stubs=0 big=0 fixos
    # ------------------------------------------------------------------
    def test_s2_acs_without_tests_fails_step_9_no_fixed_stubs(self):
        repo_dir, runtime_dir = self.make_temp_repo()
        # Init contract
        self.run_cmd([
            sys.executable, str(XP_CONTRACT), "init",
            "--risk", "L1",
            "--goal", "Implement feature X",
            "--acs", "AC-01", "AC-02", "AC-03",
            "--verify", "true",
        ], repo_dir, runtime_dir)

        res = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res.returncode, 1, f"Expected exit 1. Output: {res.stdout}\n{res.stderr}")
        self.assertIn("step=9", res.stdout)
        self.assertNotIn("stubs=0 big=0", res.stdout)

    # ------------------------------------------------------------------
    # S3: arquivo alterado com # TODO -> exit 1, step=4
    # ------------------------------------------------------------------
    def test_s3_file_with_todo_fails_step_4(self):
        repo_dir, runtime_dir = self.make_temp_repo()
        self.run_cmd([
            sys.executable, str(XP_CONTRACT), "init",
            "--risk", "L1",
            "--goal", "Implement feature with TODO",
            "--verify", "true",
        ], repo_dir, runtime_dir)

        todo_file = repo_dir / "module.py"
        todo_file.write_text("# TODO: finish later\ndef run():\n    return True\n", encoding="utf-8")
        subprocess.run(["git", "add", "module.py"], cwd=str(repo_dir), check=True)

        res = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res.returncode, 1, f"Expected exit 1. Output: {res.stdout}")
        self.assertIn("step=4", res.stdout)

    # ------------------------------------------------------------------
    # S4: verify_cmd falha igual duas vezes -> 1ª exit 1, 2ª exit 3 ESCALATE, DEAD ENDS não vazio
    # ------------------------------------------------------------------
    def test_s4_verify_cmd_fails_twice_escalates(self):
        repo_dir, runtime_dir = self.make_temp_repo()
        self.run_cmd([
            sys.executable, str(XP_CONTRACT), "init",
            "--risk", "L1",
            "--goal", "Task with failing verify",
            "--verify", "false",
        ], repo_dir, runtime_dir)

        # 1st attempt -> exit 1
        res1 = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res1.returncode, 1, f"Expected 1st run exit 1, got {res1.returncode}. Out: {res1.stdout}")

        # 2nd attempt -> exit 3 ESCALATE
        res2 = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res2.returncode, 3, f"Expected 2nd run exit 3 ESCALATE, got {res2.returncode}. Out: {res2.stdout}")
        self.assertIn("ESCALATE", res2.stdout)
        self.assertIn("DEAD ENDS: [", res2.stdout)
        self.assertNotIn("DEAD ENDS: []", res2.stdout)

    # ------------------------------------------------------------------
    # S7: memória inicial -> --sync-memory x25 -> título intacto, <= 3000 B, archive preenchido
    # ------------------------------------------------------------------
    def test_s7_sync_memory_25_times_budget_and_header_intact(self):
        repo_dir, runtime_dir = self.make_temp_repo()
        mem_dir = repo_dir / ".agents" / "memory"
        mem_dir.mkdir(parents=True, exist_ok=True)
        memory_file = mem_dir / "PROJECT_MEMORY.md"
        memory_file.write_text(
            "# Project Memory\n\n## 1. FATOS\n- Fato 1\n\n## 3. PROGRESSO\n- Marco zero\n\n## 4. LIÇÕES\n- Lição 1\n",
            encoding="utf-8",
        )

        for i in range(1, 26):
            res = self.run_cmd([
                sys.executable, str(XP_GATE),
                "--sync-memory", f"Entrega número {i:02d} com texto detalhado para testar rotação de memória",
            ], repo_dir, runtime_dir)
            self.assertEqual(res.returncode, 0, f"sync-memory failed at run {i}: {res.stderr}")

        content = memory_file.read_text(encoding="utf-8")
        self.assertEqual(content.count("## 3. PROGRESSO"), 1, "Header '## 3. PROGRESSO' must appear exactly once")
        self.assertNotIn("## 3.\n", content, "Corrupted header '## 3.' must not exist")
        self.assertLessEqual(len(content.encode("utf-8")), 3000, f"Memory ({len(content.encode('utf-8'))} B) must be <= 3000 B")

        hist_file = mem_dir / "archive" / "HISTORY.md"
        self.assertTrue(hist_file.is_file(), "HISTORY.md must exist after rotation")
        hist_content = hist_file.read_text(encoding="utf-8")
        self.assertIn("Entrega número", hist_content)

    # ------------------------------------------------------------------
    # S8: bugfix L1, verify_cmd passando, sem execução falha registrada -> step=7; com record falho e depois passando -> PASS; refactor: true -> PASS sem RED
    # ------------------------------------------------------------------
    def test_s8_red_green_evidence_required_for_bugfix_l1(self):
        repo_dir, runtime_dir = self.make_temp_repo()
        # 1. Bugfix sem evidência de RED registrada -> FAIL step=7
        self.run_cmd([
            sys.executable, str(XP_CONTRACT), "init",
            "--risk", "L1",
            "--goal", "Fix bug in calculation",
            "--verify", "true",
        ], repo_dir, runtime_dir)

        res = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res.returncode, 1, f"Expected exit 1 step=7, got {res.returncode}. Out: {res.stdout}")
        self.assertIn("step=7", res.stdout)

        # 2. Registra falha (RED) e depois sucesso (GREEN) -> PASS
        rec_fail = self.run_cmd([sys.executable, str(XP_GATE), "record", "--", "false"], repo_dir, runtime_dir)
        self.assertEqual(rec_fail.returncode, 1)

        rec_pass = self.run_cmd([sys.executable, str(XP_GATE), "record", "--", "true"], repo_dir, runtime_dir)
        self.assertEqual(rec_pass.returncode, 0)

        res_pass = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res_pass.returncode, 0, f"Expected PASS after RED->GREEN. Out: {res_pass.stdout}")

        # 3. Com refactor: true -> PASS sem RED
        self.run_cmd([
            sys.executable, str(XP_CONTRACT), "init",
            "--risk", "L1",
            "--goal", "Refactor module",
            "--verify", "true",
            "--refactor",
        ], repo_dir, runtime_dir)
        rec_pass2 = self.run_cmd([sys.executable, str(XP_GATE), "record", "--", "true"], repo_dir, runtime_dir)
        self.assertEqual(rec_pass2.returncode, 0)

        res_refactor = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res_refactor.returncode, 0, f"Expected PASS for refactor without RED. Out: {res_refactor.stdout}")

    # ------------------------------------------------------------------
    # S9: execução passando registrada, depois arquivo do escopo editado -> exit 1 step=6 (evidência velha)
    # ------------------------------------------------------------------
    def test_s9_stale_evidence_fails_step_6(self):
        repo_dir, runtime_dir = self.make_temp_repo()
        app_file = repo_dir / "app.py"
        app_file.write_text("def val(): return 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "app.py"], cwd=str(repo_dir), check=True)
        subprocess.run(["git", "commit", "-m", "add app.py"], cwd=str(repo_dir), check=True)

        self.run_cmd([
            sys.executable, str(XP_CONTRACT), "init",
            "--risk", "L1",
            "--goal", "Refactor app",
            "--verify", "true",
            "--refactor",
            "--scope", "app.py",
        ], repo_dir, runtime_dir)

        # Grava execução passando
        rec = self.run_cmd([sys.executable, str(XP_GATE), "record", "--", "true"], repo_dir, runtime_dir)
        self.assertEqual(rec.returncode, 0)

        # Edita o arquivo do escopo DEPOIS da evidência
        time.sleep(0.05)
        app_file.write_text("def val(): return 2 # edited after record\n", encoding="utf-8")

        res = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res.returncode, 1, f"Expected exit 1 step=6 (stale evidence), got {res.returncode}. Out: {res.stdout}")
        self.assertIn("step=6", res.stdout)

    # ------------------------------------------------------------------
    # S15: Repositório entregue -> testes de orçamento
    # ------------------------------------------------------------------
    def test_s15_repository_delivered_budget_tests(self):
        from scripts.kit_constants import BASE_CONTEXT_MAX_BYTES, MEMORY_INDEX_MAX_BYTES

        agents_md = KIT_ROOT / "AGENTS.md"
        memory_md = KIT_ROOT / ".agents" / "memory" / "PROJECT_MEMORY.md"

        self.assertTrue(agents_md.is_file(), "AGENTS.md must exist")
        self.assertTrue(memory_md.is_file(), "PROJECT_MEMORY.md must exist")

        agents_bytes = len(agents_md.read_text(encoding="utf-8").encode("utf-8"))
        memory_bytes = len(memory_md.read_text(encoding="utf-8").encode("utf-8"))

        self.assertLessEqual(
            memory_bytes,
            MEMORY_INDEX_MAX_BYTES,
            f"PROJECT_MEMORY.md ({memory_bytes} B) must be <= {MEMORY_INDEX_MAX_BYTES} B",
        )
        self.assertLessEqual(
            agents_bytes + memory_bytes,
            BASE_CONTEXT_MAX_BYTES,
            f"AGENTS.md + memory ({agents_bytes + memory_bytes} B) must be <= {BASE_CONTEXT_MAX_BYTES} B",
        )


if __name__ == "__main__":
    unittest.main()
