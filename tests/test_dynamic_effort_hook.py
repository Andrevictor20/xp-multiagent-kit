import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.hooks.dynamic_effort_hook import (
    extract_latest_user_prompt,
    handle_pre_invocation,
)


class TestDynamicEffortHook(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        self.transcript_file = self.temp_path / "transcript.jsonl"
        steps = [
            {"step_index": 1, "type": "USER_INPUT", "content": "Olá, tudo bem?"},
            {"step_index": 2, "type": "PLANNER_RESPONSE", "content": "Olá! Como posso ajudar?"},
            {"step_index": 3, "type": "USER_INPUT", "content": "<USER_REQUEST>\nImplementar novo microserviço de pagamentos stripe\n</USER_REQUEST>"},
        ]
        with open(self.transcript_file, "w", encoding="utf-8") as f:
            for s in steps:
                f.write(json.dumps(s) + "\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_latest_user_prompt(self):
        prompt = extract_latest_user_prompt(str(self.transcript_file))
        self.assertIn("Implementar novo microserviço de pagamentos stripe", prompt)
        self.assertNotIn("<USER_REQUEST>", prompt)

    def test_handle_pre_invocation_classifies_and_injects_step(self):
        payload = {
            "invocationNum": 2,
            "transcriptPath": str(self.transcript_file),
            "conversationId": "test-conv-123",
        }
        res = handle_pre_invocation(payload)
        self.assertIn("injectSteps", res)
        self.assertTrue(len(res["injectSteps"]) > 0)
        injected = res["injectSteps"][0]
        self.assertIn("ephemeralMessage", injected)
        msg = injected["ephemeralMessage"]
        self.assertIn("HIGH", msg.upper())
        self.assertIn("L3", msg.upper())

    def test_handle_pre_invocation_trivial_prompt_injects_low(self):
        low_transcript = self.temp_path / "transcript_low.jsonl"
        steps = [
            {"step_index": 1, "type": "USER_INPUT", "content": "qual a diferenca entre cli e ide?"},
        ]
        with open(low_transcript, "w", encoding="utf-8") as f:
            for s in steps:
                f.write(json.dumps(s) + "\n")

        payload = {
            "invocationNum": 1,
            "transcriptPath": str(low_transcript),
        }
        res = handle_pre_invocation(payload)
        self.assertIn("injectSteps", res)
        msg = res["injectSteps"][0]["ephemeralMessage"]
        self.assertIn("LOW", msg.upper())

    def test_handle_pre_invocation_missing_transcript_fallback(self):
        payload = {
            "invocationNum": 1,
            "transcriptPath": "/tmp/non_existent_transcript.jsonl",
        }
        res = handle_pre_invocation(payload)
        self.assertIn("injectSteps", res)

    def test_handle_pre_invocation_multi_turn_with_stop_gate_and_directive(self):
        # Scenario matching user screenshot: Turn 1 is feature/auth, Turn 2 is Stop Gate, Turn 3 is "Mude para o effort high e continue"
        multi_transcript = self.temp_path / "transcript_multi.jsonl"
        steps = [
            {
                "step_index": 1,
                "type": "USER_INPUT",
                "content": "<USER_REQUEST>\nQuero criar plano robusto para visualização mobile e controle de containers com autenticação 2FA\n</USER_REQUEST>"
            },
            {
                "step_index": 2,
                "type": "PLANNER_RESPONSE",
                "content": "### Stop Gate de Governança (Regra de Ouro & Regra [L-019])\nComo esta tarefa possui classificação de risco L3 (Critical), o plano de implementação foi detalhado. Por favor confirme para iniciarmos a implementação na prática com o modelo em High (ou /effort high)."
            },
            {
                "step_index": 3,
                "type": "USER_INPUT",
                "content": "<USER_REQUEST>\nMude para o effort high e continue\n</USER_REQUEST>"
            }
        ]
        with open(multi_transcript, "w", encoding="utf-8") as f:
            for s in steps:
                f.write(json.dumps(s) + "\n")

        payload = {
            "invocationNum": 3,
            "transcriptPath": str(multi_transcript),
            "conversationId": "test-multi-turn",
        }
        res = handle_pre_invocation(payload)
        self.assertIn("injectSteps", res)
        msg = res["injectSteps"][0]["ephemeralMessage"]
        self.assertIn("HIGH", msg.upper())
        self.assertIn("L3", msg.upper())

    def test_handle_pre_invocation_multi_turn_simple_continue(self):
        # Scenario: User simply types "continue" after L3 Stop Gate
        cont_transcript = self.temp_path / "transcript_cont.jsonl"
        steps = [
            {
                "step_index": 1,
                "type": "USER_INPUT",
                "content": "Implementar módulo de pagamentos stripe e faturamento"
            },
            {
                "step_index": 2,
                "type": "PLANNER_RESPONSE",
                "content": "Stop Gate de Governança: Risco L3 (Critical). Confirme para executar."
            },
            {
                "step_index": 3,
                "type": "USER_INPUT",
                "content": "continue"
            }
        ]
        with open(cont_transcript, "w", encoding="utf-8") as f:
            for s in steps:
                f.write(json.dumps(s) + "\n")

        payload = {
            "invocationNum": 3,
            "transcriptPath": str(cont_transcript),
            "conversationId": "test-cont-123",
        }
        res = handle_pre_invocation(payload)
        self.assertIn("injectSteps", res)
        msg = res["injectSteps"][0]["ephemeralMessage"]
        self.assertIn("HIGH", msg.upper())
        self.assertIn("L3", msg.upper())


if __name__ == "__main__":
    unittest.main()
