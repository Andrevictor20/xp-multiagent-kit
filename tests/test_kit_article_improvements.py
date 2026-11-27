#!/usr/bin/env python3
"""tests/test_kit_article_improvements.py — Testes para as melhorias de engenharia de contexto e design."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.context_compactor_ccr import (
    ContextualCompressorWithRetrieval,
    compress_conversation_turns,
)
from scripts.hooks.dynamic_effort_hook import handle_pre_invocation
from scripts.kit_constants import AUTO_COMPACT_TOKEN_THRESHOLD
from scripts.xp_contract import init_contract, load_contract
from scripts.xp_gate import record_visual_evidence, run_gate
from scripts.xp_session import (
    create_handoff_contract,
    render_handoff_markdown,
    write_handoff_file,
)


def _load_tool_size_guard():
    mod_path = ROOT_DIR / "scripts" / "hooks" / "tool-size-guard.py"
    spec = importlib.util.spec_from_file_location("tool_size_guard_test", str(mod_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestKitArticleImprovements(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        self.orig_env = os.environ.get("KIT_RUNTIME_DIR")
        os.environ["KIT_RUNTIME_DIR"] = self.test_dir

    def tearDown(self) -> None:
        if self.orig_env is not None:
            os.environ["KIT_RUNTIME_DIR"] = self.orig_env
        else:
            os.environ.pop("KIT_RUNTIME_DIR", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_ac_01_l1_skip_trivial_ephemeral_preserves_kv_cache(self) -> None:
        """AC-01: L1 simples com skip_trivial_ephemeral=True não injeta ephemeralMessage nem roda JIT."""
        tfile = Path(self.test_dir) / "transcript_l1.jsonl"
        tfile.write_text(
            json.dumps({
                "step_index": 1,
                "type": "USER_INPUT",
                "content": "<USER_REQUEST>\nRefatore a função isolada format_badge\n</USER_REQUEST>",
            }) + "\n",
            encoding="utf-8",
        )
        res_without_skip = handle_pre_invocation(
            {"invocationNum": 1, "transcriptPath": str(tfile), "conversationId": "conv-l1-noskip"},
            skip_trivial_ephemeral=False,
        )
        self.assertIn("L1", res_without_skip["injectSteps"][0]["ephemeralMessage"])
        res = handle_pre_invocation(
            {"invocationNum": 1, "transcriptPath": str(tfile), "conversationId": "conv-l1-kv"},
            skip_trivial_ephemeral=True,
        )
        self.assertEqual(res.get("injectSteps"), [])

    def test_ac_02_tool_size_guard_includes_backup_path_and_xp_compact(self) -> None:
        """AC-02: Clamp informa caminho do arquivo completo e CCR referencia xp compact."""
        tsg = _load_tool_size_guard()
        scratch = Path(self.test_dir) / "scratch"
        big = "\n".join(f"Output line {i}" for i in range(90))
        res = tsg.process_tool_payload({"tool_name": "run_command", "output": big}, scratch_dir=scratch)
        self.assertTrue(res["is_flooding"])
        self.assertIn("last_tool_output.log", res["clamped_content"])

        ccr = ContextualCompressorWithRetrieval(cache_dir=str(Path(self.test_dir) / "ccr"), max_inline_chars=50)
        stub, _ = ccr.compress("run_command", "A" * 300)
        self.assertIn("xp compact --expand", stub)

    def test_ac_03_xp_contract_validate_works_without_spec_arg(self) -> None:
        """AC-03: xp contract validate funciona sem argumento posicional validando run.json ativo."""
        init_contract(risk="L1", goal="Validar fluxo design sem spec file", scope_files=["index.html"])
        proc = subprocess.run(
            [sys.executable, str(ROOT_DIR / "scripts" / "xp"), "contract", "validate"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

    def test_ac_04_visual_gate_requires_and_records_screenshot_for_ui(self) -> None:
        """AC-04: Contratos com visual_required exigem evidência visual registrada via record_visual_evidence."""
        html_file = Path(self.test_dir) / "preview.html"
        html_file.write_text("<html><body><h1>Vito</h1></body></html>", encoding="utf-8")
        init_contract(
            risk="L0",
            goal="Validar tela inicial",
            scope_files=[str(html_file)],
            visual_required=True,
        )
        # Sem screenshot registrado -> gate falha com instrução explícita
        code_fail, line_fail, msg_fail = run_gate(dry_run=False, changed_files=[str(html_file)])
        self.assertEqual(code_fail, 1)
        self.assertIn("record-visual", msg_fail)

        # Registra screenshot válido -> gate passa
        shot = Path(self.test_dir) / "preview.png"
        shot.write_bytes(b"\x89PNG\r\n\x1a\nfake-png-content")
        rc = record_visual_evidence([str(shot)], note="Desktop 1280x720 verificado")
        self.assertEqual(rc, 0)
        contract = load_contract()
        self.assertEqual(len(contract.get("visual_evidence", [])), 1)

        code_ok, line_ok, _ = run_gate(dry_run=False, changed_files=[str(html_file)])
        self.assertEqual(code_ok, 0, line_ok)
        self.assertIn("GATE PASS", line_ok)

    def test_ac_05_handoff_markdown_and_late_compaction_pinning(self) -> None:
        """AC-05: Handoff gera handoff.md com estado vivo e compactação tardia fixa caminhos e decisões."""
        init_contract(
            risk="L2",
            goal="Implementar verificação visual",
            scope_files=["scripts/xp_gate.py"],
            verify_cmd="python3 -m unittest tests/test_xp_gate.py",
            known={"design_decision": "Registrar screenshot em run.json"},
            next_step="Rodar review do gate",
        )
        handoff = create_handoff_contract(
            task_id="design-gate-01",
            risk_level="L2",
            files_touched=["scripts/xp_gate.py"],
        )
        self.assertEqual(handoff["goal"], "Implementar verificação visual")
        self.assertIn("scripts/xp_gate.py", handoff["files_touched"])
        self.assertEqual(handoff["next_step"], "Rodar review do gate")

        md = render_handoff_markdown(handoff)
        self.assertIn("# Session Handoff", md)
        self.assertIn("Implementar verificação visual", md)
        self.assertIn("Registrar screenshot em run.json", md)
        self.assertIn("scripts/xp_gate.py", md)

        out = write_handoff_file(handoff)
        self.assertTrue(out.is_file())
        self.assertEqual(out.name, "handoff.md")

        self.assertGreaterEqual(AUTO_COMPACT_TOKEN_THRESHOLD, 500_000)
        messages = [
            {"role": "user", "content": "Analise os logs"},
            {"role": "tool", "content": "X" * 2000, "tool_name": "run_command"},
            {"role": "user", "content": "Continue"},
            {"role": "assistant", "content": "Prosseguindo."},
        ]
        compacted = compress_conversation_turns(
            messages,
            budget_chars=400,
            active_files=["scripts/xp_gate.py"],
            decisions=["Usar SHA-256 para freshness"],
        )
        self.assertTrue(any("[PINNED_STATE]" in m.get("content", "") for m in compacted))
        pinned = next(m["content"] for m in compacted if "[PINNED_STATE]" in m.get("content", ""))
        self.assertIn("scripts/xp_gate.py", pinned)
        self.assertIn("Usar SHA-256 para freshness", pinned)


if __name__ == "__main__":
    unittest.main()
