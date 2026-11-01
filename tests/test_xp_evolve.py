#!/usr/bin/env python3
"""tests/test_xp_evolve.py — Testes unitários para o motor de auto-melhoria (AC-10)"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.xp_evolve import load_components, run_apply, run_propose, run_report


class TestXpEvolve(unittest.TestCase):
    def setUp(self) -> None:
        self.proposals_dir = Path(__file__).resolve().parent.parent / ".agents" / "proposals"
        self.proposals_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        for pr_file in self.proposals_dir.glob("PR-*.md"):
            try:
                pr_file.unlink()
            except Exception:
                pass
        p_file = Path(__file__).resolve().parent.parent / ".agents" / "promotions.json"
        if p_file.is_file():
            try:
                p_file.unlink()
            except Exception:
                pass

    def test_load_components(self) -> None:
        comps = load_components().get("components", [])
        self.assertGreaterEqual(len(comps), 5)
        ids = [c["id"] for c in comps]
        self.assertIn("xp_contract", ids)
        self.assertIn("xp_gate", ids)

    def test_run_report(self) -> None:
        rep = run_report()
        self.assertIn("removals", rep)
        self.assertIn("promotions", rep)
        self.assertIn("bloat", rep)
        self.assertFalse(rep["bloat"], "O contexto base fixo não deve apresentar inchaço (> 8.000 B)")

    def test_run_propose_and_apply(self) -> None:
        pr_id = run_propose()
        self.assertTrue(pr_id.startswith("PR-"))
        pr_path = self.proposals_dir / f"{pr_id}.md"
        self.assertTrue(pr_path.is_file())

        content = pr_path.read_text(encoding="utf-8")
        self.assertIn("8 Perguntas de Diagnóstico", content)

        # Aplica a proposta
        with patch("subprocess.run") as mock_sub:
            mock_sub.return_value.returncode = 0
            code = run_apply(pr_id, force_approve=True)
            self.assertEqual(code, 0)

    def test_post_promotion_recurrence_escalates_step(self) -> None:
        from scripts.xp_evolve import save_promotions
        p_file = Path(__file__).resolve().parent.parent / ".agents" / "promotions.json"
        save_promotions({"sig_rec_err": {"promoted_at": 1000, "degrau": "teste"}})

        # Cria evento falso de reincidência
        rdir = Path(__file__).resolve().parent.parent / ".agents" / "runtime"
        rdir.mkdir(parents=True, exist_ok=True)
        ev_file = rdir / "events.test.jsonl"
        ev_lines = [
            json.dumps({"ts": 2000, "kind": "failure", "signature": "sig_rec_err"})
            for _ in range(3)
        ]
        ev_file.write_text("\n".join(ev_lines) + "\n", encoding="utf-8")
        try:
            rep = run_report()
            ineff = [i for i in rep["ineffective"] if i["sig"] == "sig_rec_err"]
            self.assertTrue(len(ineff) > 0, "Deveria detectar ineficácia pós-promoção")
            self.assertEqual(ineff[0]["prev"], "teste")
            self.assertEqual(ineff[0]["next"], "hook")
        finally:
            if ev_file.is_file():
                ev_file.unlink()


if __name__ == "__main__":
    unittest.main()
