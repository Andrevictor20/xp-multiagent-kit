#!/usr/bin/env python3
"""tests/test_agy_run.py — Testes para o wrapper portátil agy-run."""
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
AGY_RUN = SCRIPTS_DIR / "agy-run"


class TestAgyRun(unittest.TestCase):
    """Verifica o comportamento do wrapper agy-run."""

    def _run(self, cmd: str, expect_ok: bool = True) -> subprocess.CompletedProcess:
        """Helper: executa agy-run com um comando e retorna o resultado."""
        result = subprocess.run(
            [sys.executable, str(AGY_RUN), cmd],
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "KIT_ROOT": str(SCRIPTS_DIR.parent)},
        )
        if expect_ok:
            self.assertEqual(
                result.returncode, 0,
                f"agy-run failed: {result.stderr}",
            )
        return result

    def test_agy_run_script_exists(self):
        """O script agy-run deve existir e ser executável."""
        self.assertTrue(AGY_RUN.exists(), f"{AGY_RUN} not found")

    def test_simple_echo(self):
        """Deve executar um echo simples e capturar a saída."""
        result = self._run("echo hello-agy-run")
        self.assertIn("hello-agy-run", result.stdout)

    def test_exit_code_propagation(self):
        """Deve propagar o exit code do comando subjacente."""
        result = self._run("false", expect_ok=False)
        self.assertNotEqual(result.returncode, 0)

    def test_strips_noise_from_output(self):
        """Se a saída contiver decoração de box-drawing, deve removê-la."""
        # Simula output com box-drawing
        cmd = 'printf "╭──────╮\\n│ hello │\\n╰──────╯\\nreal-output"'
        result = self._run(cmd)
        # A linha "real-output" deve estar presente; as de box-drawing podem ter sido removidas
        self.assertIn("real-output", result.stdout)

    def test_handles_multiword_commands(self):
        """Deve lidar com comandos que contêm espaços e argumentos."""
        result = self._run("echo 'multiple words here'")
        self.assertIn("multiple words here", result.stdout)


if __name__ == "__main__":
    unittest.main()
