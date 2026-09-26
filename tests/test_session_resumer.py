import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestSessionResumer(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.memory_dir = self.workspace / ".agents" / "memory"
        self.memory_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_load_session_state(self):
        from scripts.session_resumer import save_session_state, load_session_state, STATE_FILENAME

        state_file = save_session_state(
            self.workspace,
            goal="Implementando feature X",
            next_steps="Rodar testes e fazer commit",
            active_agent="builder",
        )
        self.assertTrue(state_file.is_file())
        self.assertEqual(state_file.name, STATE_FILENAME)

        loaded = load_session_state(self.workspace)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["goal"], "Implementando feature X")
        self.assertEqual(loaded["next_steps"], "Rodar testes e fazer commit")
        self.assertEqual(loaded["active_agent"], "builder")

    def test_generate_resume_prompt_compact(self):
        from scripts.session_resumer import save_session_state, load_session_state, generate_resume_prompt

        save_session_state(
            self.workspace,
            goal="Refatorando modulo de auth",
            next_steps="Validar token expiration",
        )
        loaded = load_session_state(self.workspace)
        prompt = generate_resume_prompt(loaded)
        self.assertIn("Refatorando modulo de auth", prompt)
        self.assertIn("Validar token expiration", prompt)
        # Ensure under 20 lines to conserve tokens
        self.assertLess(len(prompt.splitlines()), 20)

    def test_clear_session_state(self):
        from scripts.session_resumer import save_session_state, clear_session_state, load_session_state

        save_session_state(self.workspace, goal="Temporario")
        self.assertIsNotNone(load_session_state(self.workspace))

        cleared = clear_session_state(self.workspace)
        self.assertTrue(cleared)
        self.assertIsNone(load_session_state(self.workspace))


if __name__ == "__main__":
    unittest.main()
