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

    # S1: nenhum contrato -> exit 1, GATE FAIL step=1
    def test_s1_no_contract_gate_fails_step_1(self):
        repo_dir, runtime_dir = self.make_temp_repo()
        res = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res.returncode, 1, f"Expected exit 1, got {res.returncode}. Output: {res.stdout}\n{res.stderr}")
        self.assertIn("step=1", res.stdout)
        self.assertIn("GATE FAIL", res.stdout)

    # S2: L1, 3 ACs, nenhum teste os referencia, verify_cmd=true -> exit 1; sem stubs=0 big=0 fixos
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

        # Registra RED e GREEN para cumprir step 7 (ordem 1..10) antes de step 9
        self.run_cmd([sys.executable, str(XP_GATE), "record", "--", "false"], repo_dir, runtime_dir)
        self.run_cmd([sys.executable, str(XP_GATE), "record", "--", "true"], repo_dir, runtime_dir)

        res = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res.returncode, 1, f"Expected exit 1. Output: {res.stdout}\n{res.stderr}")
        self.assertIn("step=9", res.stdout)
        self.assertNotIn("stubs=0 big=0", res.stdout)

    # S3: arquivo alterado com marcador pendente -> exit 1, step=4
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

    # S4: verify_cmd falha igual duas vezes -> 1ª exit 1, 2ª exit 3 ESCALATE, DEAD ENDS não vazio
    def test_s4_verify_cmd_fails_twice_escalates(self):
        repo_dir, runtime_dir = self.make_temp_repo()
        self.run_cmd([
            sys.executable, str(XP_CONTRACT), "init",
            "--risk", "L1",
            "--goal", "Task with failing verify",
            "--verify", "false",
        ], repo_dir, runtime_dir)

        # Registra RED e GREEN para cumprir step 7 antes de step 8 (verify_cmd)
        self.run_cmd([sys.executable, str(XP_GATE), "record", "--", "false"], repo_dir, runtime_dir)
        self.run_cmd([sys.executable, str(XP_GATE), "record", "--", "true"], repo_dir, runtime_dir)

        # 1st attempt -> exit 1
        res1 = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res1.returncode, 1, f"Expected 1st run exit 1, got {res1.returncode}. Out: {res1.stdout}")

        # 2nd attempt -> exit 3 ESCALATE
        res2 = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res2.returncode, 3, f"Expected 2nd run exit 3 ESCALATE, got {res2.returncode}. Out: {res2.stdout}")
        self.assertIn("ESCALATE", res2.stdout)
        self.assertIn("DEAD ENDS: [", res2.stdout)
        self.assertNotIn("DEAD ENDS: []", res2.stdout)

    # S5: L1, diff em src/auth/ -> gate sem revisão dá exit 2 BLOCK tier=review; com revisão dá PASS
    def test_s5_diff_in_auth_requires_review_record(self):
        repo_dir, runtime_dir = self.make_temp_repo()
        auth_file = repo_dir / "src" / "auth" / "login.py"
        auth_file.parent.mkdir(parents=True, exist_ok=True)
        auth_file.write_text("def auth(): return True\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/auth/login.py"], cwd=str(repo_dir), check=True)

        self.run_cmd([
            sys.executable, str(XP_CONTRACT), "init",
            "--risk", "L1",
            "--goal", "Update auth logic",
            "--verify", "true",
            "--refactor",
            "--scope", "src/auth/login.py",
        ], repo_dir, runtime_dir)

        # 1. Sem registro de revisão -> exit 2 BLOCK tier=review
        res1 = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res1.returncode, 2, f"Expected exit 2 BLOCK tier=review, got {res1.returncode}. Out: {res1.stdout}")
        self.assertIn("BLOCK tier=review", res1.stdout)

        # 2. Com registro de revisão de outro revisor -> PASS
        rec_rev = self.run_cmd([
            sys.executable, str(XP_GATE), "review", "record",
            "--reviewer", "sentinel",
            "--verdict", "approve",
        ], repo_dir, runtime_dir)
        self.assertEqual(rec_rev.returncode, 0)

        res2 = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res2.returncode, 0, f"Expected PASS after review. Out: {res2.stdout}")

    # S6: diff em db/migrations/ -> gate sem aprovação dá exit 2; aprovar com 1ª palavra não libera; ID exato libera
    def test_s6_diff_in_migrations_requires_exact_deterministic_action_id(self):
        repo_dir, runtime_dir = self.make_temp_repo()
        mig_file = repo_dir / "db" / "migrations" / "001_create.sql"
        mig_file.parent.mkdir(parents=True, exist_ok=True)
        mig_file.write_text("CREATE TABLE users (id INT);\n", encoding="utf-8")
        subprocess.run(["git", "add", "db/migrations/001_create.sql"], cwd=str(repo_dir), check=True)

        self.run_cmd([
            sys.executable, str(XP_CONTRACT), "init",
            "--risk", "L1",
            "--goal", "Create initial migration table",
            "--verify", "true",
            "--refactor",
            "--scope", "db/migrations/001_create.sql",
        ], repo_dir, runtime_dir)

        res1 = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res1.returncode, 2, f"Expected exit 2 BLOCK tier=human, got {res1.returncode}. Out: {res1.stdout}")
        self.assertIn("BLOCK tier=human", res1.stdout)

        # Extrai action id: action=([a-f0-9]{8})
        import re
        m = re.search(r"action=([a-f0-9]{8})", res1.stdout)
        self.assertIsNotNone(m, f"Could not find deterministic action ID in output: {res1.stdout}")
        exact_id = m.group(1)

        # Aprovar com a 1ª palavra do objetivo ("Create") NÃO deve liberar
        self.run_cmd([sys.executable, str(KIT_ROOT / "scripts" / "xp"), "approve", "Create"], repo_dir, runtime_dir)
        res2 = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res2.returncode, 2, "Approval by 1st word must NOT release the gate")

        # Aprovar com o ID exato deve liberar
        self.run_cmd([sys.executable, str(KIT_ROOT / "scripts" / "xp"), "approve", exact_id], repo_dir, runtime_dir)
        res3 = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res3.returncode, 0, f"Approval by exact action ID must release the gate: {res3.stdout}")

    # S11: payload PreToolUse simulado -> guard bloqueia policy/approvals, xp approve, rm -rf; leitura permitida; hooks.json contém guard
    def test_s11_pre_tool_guard_security_checks_and_hooks_registration(self):
        from scripts.hooks.pre_tool_guard import is_action_permitted

        # 1. Escrever approvals.json -> negado
        allowed, reason = is_action_permitted("write_to_file", {"Path": ".agents/runtime/approvals.json"})
        self.assertFalse(allowed)

        # 2. Escrever policy.yaml -> negado
        allowed, reason = is_action_permitted("write_file", {"Path": ".agents/policy.yaml"})
        self.assertFalse(allowed)

        # 3. Agente chamando xp approve -> negado
        allowed, reason = is_action_permitted("run_command", {"CommandLine": "xp approve a1b2c3d4"})
        self.assertFalse(allowed)

        # 4. rm -rf sem aprovação -> negado
        allowed, reason = is_action_permitted("run_command", {"CommandLine": "rm -rf /tmp/test"})
        self.assertFalse(allowed)

        # 5. Leitura comum -> permitido
        allowed, reason = is_action_permitted("read_file", {"Path": "src/app.py"})
        self.assertTrue(allowed)

        # 6. hooks.json contém o guard registrado sob PreToolUse
        hooks_json = json.loads((KIT_ROOT / ".agents" / "hooks.json").read_text(encoding="utf-8"))
        has_guard = False
        for hook_entry in hooks_json.values():
            for ptu in hook_entry.get("PreToolUse", []):
                for h in ptu.get("hooks", []):
                    if "pre_tool_guard" in h.get("command", ""):
                        has_guard = True
        self.assertTrue(has_guard, "hooks.json must contain pre_tool_guard under PreToolUse")

    # S7: memória inicial -> --sync-memory x25 -> título intacto, <= 3000 B, archive preenchido
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

    # S8: bugfix L1, verify_cmd passando, sem execução falha registrada -> step=7; com record falho e depois passando -> PASS; refactor: true -> PASS sem RED
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

    # S9: execução passando registrada, depois arquivo do escopo editado -> exit 1 step=6 (evidência velha)
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

    # S10: testes *.test.ts congelados na saída de red -> alterar um congelado dá exit 1 step=3; novo teste permitido
    def test_s10_frozen_tests_blocking_mutation_and_allowing_new_tests(self):
        from scripts.xp_flow import freeze_test_files

        repo_dir, runtime_dir = self.make_temp_repo()
        test_file = repo_dir / "src" / "calc.test.ts"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test('add', () => {});\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/calc.test.ts"], cwd=str(repo_dir), check=True)

        self.run_cmd([
            sys.executable, str(XP_CONTRACT), "init",
            "--risk", "L1",
            "--goal", "TypeScript feature",
            "--verify", "true",
            "--refactor",
        ], repo_dir, runtime_dir)

        # Congela testes no projeto-alvo
        env = dict(os.environ)
        env["KIT_RUNTIME_DIR"] = str(runtime_dir)
        env["KIT_PROJECT_ROOT"] = str(repo_dir)
        env["PYTHONPATH"] = str(KIT_ROOT)
        res_freeze = subprocess.run([sys.executable, "-c", "from scripts.xp_flow import freeze_test_files; freeze_test_files()"], cwd=str(repo_dir), env=env, capture_output=True, text=True)
        self.assertEqual(res_freeze.returncode, 0, f"freeze failed: {res_freeze.stderr}")

        # 1. Modificar teste congelado -> FAIL step=3
        test_file.write_text("test('add modified', () => {});\n", encoding="utf-8")
        res1 = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res1.returncode, 1, f"Expected step=3 fail on mutated test. Out: {res1.stdout}")
        self.assertIn("step=3", res1.stdout)

        # 2. Restaurar teste original e adicionar NOVO teste -> PASS
        test_file.write_text("test('add', () => {});\n", encoding="utf-8")
        new_test_file = repo_dir / "src" / "other.test.ts"
        new_test_file.write_text("test('sub', () => {});\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/other.test.ts"], cwd=str(repo_dir), check=True)

        res2 = self.run_cmd([sys.executable, str(XP_GATE), "check"], repo_dir, runtime_dir)
        self.assertEqual(res2.returncode, 0, f"Adding a new test must be allowed and PASS. Out: {res2.stdout}")

    # S12: workflow.yaml entregue -> validate dá exit 0; agente inexistente dá exit ≠ 0; next imprime ≤ 800 B
    def test_s12_workflow_yaml_validation_and_next_budget(self):
        XP_FLOW = KIT_ROOT / "scripts" / "xp_flow.py"

        # 1. Validar workflow.yaml entregue do kit -> exit 0
        res_val = subprocess.run([sys.executable, str(XP_FLOW), "validate"], cwd=str(KIT_ROOT), capture_output=True, text=True)
        self.assertEqual(res_val.returncode, 0, f"workflow.yaml validation failed: {res_val.stdout}\n{res_val.stderr}")

        # 2. Fixture com nó apontando para agente inexistente -> exit != 0
        with tempfile.NamedTemporaryFile("w", suffix=".yaml") as f:
            f.write(
                "workflows:\n"
                "  dummy:\n"
                "    nodes:\n"
                "      - {name: 'step1', run: 'ghost-agent', exit_cmd: 'true'}\n"
                "      - {name: 'gate', run: 'reviewer', exit_cmd: 'python3 scripts/xp_gate.py check'}\n"
            )
            f.flush()
            res_bad = subprocess.run([sys.executable, str(XP_FLOW), "validate", "--file", f.name], cwd=str(KIT_ROOT), capture_output=True, text=True)
            self.assertNotEqual(res_bad.returncode, 0, "Validation must fail for nonexistent agent")

        # 3. xp flow next imprime <= 800 B
        repo_dir, runtime_dir = self.make_temp_repo()
        self.run_cmd([sys.executable, str(XP_CONTRACT), "init", "--risk", "L1", "--goal", "Goal for next test", "--verify", "true"], repo_dir, runtime_dir)
        self.run_cmd([sys.executable, str(XP_FLOW), "start", "feature"], repo_dir, runtime_dir)
        res_next = self.run_cmd([sys.executable, str(XP_FLOW), "next"], repo_dir, runtime_dir)
        self.assertEqual(res_next.returncode, 0, f"xp flow next failed: {res_next.stderr}")
        self.assertLessEqual(len(res_next.stdout.encode("utf-8")), 800, f"xp flow next output ({len(res_next.stdout.encode('utf-8'))} B) must be <= 800 B")

    # S13: eventos de fixture: 1 assinatura repetida x3 e 1 componente sem uso -> report lista 1 promoção e 1 remoção; apply em AGENTS.md sem --approve é recusado
    def test_s13_evolve_report_promotion_removal_and_approval_gate(self):
        repo_dir, runtime_dir = self.make_temp_repo()
        # Copia estrutura mínima para o repo temporário
        ag_dir = repo_dir / ".agents"
        ag_dir.mkdir(parents=True, exist_ok=True)
        (repo_dir / "AGENTS.md").write_text("# Master\n## CONTRATO\n## CONTEXTO\n## FERRAMENTAS\n## ESTADO\n## POLÍTICA\n## VERIFICAÇÃO\n## RECUPERAÇÃO\n## OBSERVABILIDADE\n", encoding="utf-8")

        # components.yaml com um componente ativo e um inativo
        comp_file = ag_dir / "components.yaml"
        comp_file.write_text(
            "components:\n"
            "  - id: 'active_comp'\n"
            "    kind: 'script'\n"
            "    prevents: 'some failure'\n"
            "  - id: 'unused_comp'\n"
            "    kind: 'script'\n"
            "    prevents: 'prevent unused'\n",
            encoding="utf-8",
        )

        # 10+ eventos em events.jsonl
        events_file = runtime_dir / "events.jsonl"
        events_lines = []
        # 3 falhas repetidas com a mesma assinatura
        for _ in range(3):
            events_lines.append(json.dumps({"ts": 1000, "event": "failure", "signature": "sig_err_rep"}))
        # 7 eventos de ativação do active_comp
        for _ in range(7):
            events_lines.append(json.dumps({"ts": 1000, "event": "active_comp"}))
        events_file.write_text("\n".join(events_lines) + "\n", encoding="utf-8")

        XP_EVOLVE = KIT_ROOT / "scripts" / "xp_evolve.py"
        res_rep = self.run_cmd([sys.executable, str(XP_EVOLVE), "report"], repo_dir, runtime_dir)
        self.assertEqual(res_rep.returncode, 0, f"evolve report failed: {res_rep.stderr}")
        self.assertIn("sig_err_rep", res_rep.stdout)
        self.assertIn("unused_comp", res_rep.stdout)

        # Propose gera proposta que toca AGENTS.md
        res_prop = self.run_cmd([sys.executable, str(XP_EVOLVE), "propose"], repo_dir, runtime_dir)
        self.assertEqual(res_prop.returncode, 0)

        # Simula proposta que toca AGENTS.md
        pr_file = ag_dir / "proposals" / "PR-001.md"
        pr_file.parent.mkdir(parents=True, exist_ok=True)
        pr_file.write_text("# PR-001\nAltera AGENTS.md para promover regra\n", encoding="utf-8")

        # Apply sem --approve deve ser recusado com exit 2
        res_app = self.run_cmd([sys.executable, str(XP_EVOLVE), "apply", "PR-001"], repo_dir, runtime_dir)
        self.assertEqual(res_app.returncode, 2, f"Expected exit 2 when applying to AGENTS.md without approval. Got: {res_app.returncode}")

    # S14: skill existente sem entrada em components.yaml -> kit_lint exit != 0
    def test_s14_skill_without_components_entry_fails_kit_lint(self):
        KIT_LINT = KIT_ROOT / "scripts" / "kit_lint.py"
        repo_dir, runtime_dir = self.make_temp_repo()
        ag_dir = repo_dir / ".agents"
        skills_dir = ag_dir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        (skills_dir / "orphan-skill").mkdir(parents=True, exist_ok=True)

        comp_file = ag_dir / "components.yaml"
        comp_file.write_text("components:\n  - id: 'other_skill'\n    prevents: 'test'\n", encoding="utf-8")

        env = dict(os.environ)
        env["KIT_RUNTIME_DIR"] = str(runtime_dir)
        res = subprocess.run([sys.executable, str(KIT_LINT), "--dir", str(repo_dir)], env=env, capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0, f"kit_lint must fail when a skill is missing from components.yaml. Output: {res.stdout}")

    # S15: Repositório entregue -> testes de orçamento
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
