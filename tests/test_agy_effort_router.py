import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module to be tested
from scripts.agy_effort_router import (
    classify_task_effort,
    detect_git_context,
    map_model_to_effort,
    update_settings_effort,
    EffortDecision,
    EFFORT_LOW,
    EFFORT_MEDIUM,
    EFFORT_HIGH,
    LEVEL_L0_TRIVIAL,
    LEVEL_L1_SMALL,
    LEVEL_L2_FEATURE,
    LEVEL_L3_CRITICAL,
)


class TestAgyEffortRouter(unittest.TestCase):

    def test_classify_l0_trivial_prompts(self):
        prompts = [
            "Corrija o typo no README.md",
            "Ajuste a cor do botão no arquivo style.css",
            "Adicione comentários explicativos nas funções",
            "O que é o padrão Extreme Programming?",
            "Explique como funciona o hook PostInvocation",
            "Formate o código com prettier e remova espaços",
            "Mostre o git log dos últimos 5 commits",
        ]
        for p in prompts:
            decision = classify_task_effort(prompt=p)
            self.assertEqual(
                decision.effort,
                EFFORT_LOW,
                f"Prompt '{p}' deveria ser LOW, mas foi {decision.effort}"
            )
            self.assertEqual(decision.risk_level, LEVEL_L0_TRIVIAL)
            self.assertGreater(decision.estimated_token_savings, 0)

    def test_classify_l1_small_prompts(self):
        prompts = [
            "Pequeno ajuste na função calculateTotal para validar nulos",
            "Refatore a função isolada format_badge para simplificar o ternário",
            "Adicione um teste unitário para cobrir o caso de string vazia",
            "Corrija um pequeno bug na ordenação de itens da lista",
        ]
        for p in prompts:
            decision = classify_task_effort(prompt=p)
            self.assertEqual(
                decision.effort,
                EFFORT_MEDIUM,
                f"Prompt '{p}' deveria ser MEDIUM, mas foi {decision.effort}"
            )
            self.assertEqual(decision.risk_level, LEVEL_L1_SMALL)

    def test_classify_l2_feature_prompts(self):
        prompts = [
            "Crie um novo endpoint /api/v2/analytics e integre no dashboard",
            "Implemente uma nova funcionalidade de exportação em PDF e Excel",
            "Construa a tela de visualização de métricas com gráficos interativos",
            "Monte a nova esteira de workflows para testes E2E",
        ]
        for p in prompts:
            decision = classify_task_effort(prompt=p)
            self.assertEqual(
                decision.effort,
                EFFORT_HIGH,
                f"Prompt '{p}' deveria ser HIGH (Feature Implementation), mas foi {decision.effort}"
            )
            self.assertEqual(decision.risk_level, LEVEL_L2_FEATURE)

    def test_classify_l3_critical_prompts(self):
        prompts = [
            "Implemente autenticação JWT com refresh token e rotação de chaves",
            "Crie a migração de banco de dados para particionar a tabela de transações sem downtime",
            "Integre o gateway de pagamento Stripe com webhooks e idempotência",
            "Realize threat modeling STRIDE e corrija vulnerabilidade de IDOR",
            "Investigue a causa raiz de race condition e deadlock na fila de concorrência",
            "Prepare o script de deploy canary zero-downtime com rollback automático",
        ]
        for p in prompts:
            decision = classify_task_effort(prompt=p)
            self.assertEqual(
                decision.effort,
                EFFORT_HIGH,
                f"Prompt '{p}' deveria ser HIGH (Critical/Security/DB), mas foi {decision.effort}"
            )
            self.assertEqual(decision.risk_level, LEVEL_L3_CRITICAL)

    def test_budget_throttle_downshifts_when_critical(self):
        # Even a critical prompt (normally HIGH) should be throttled to MEDIUM or LOW if quota > 80%
        critical_prompt = "Corrija vulnerabilidade de segurança e migração de banco"
        
        # When budget is healthy (e.g. 30%)
        decision_healthy = classify_task_effort(
            prompt=critical_prompt,
            token_budget={"rolling_5h_percent": 30.0, "weekly_percent": 25.0}
        )
        self.assertEqual(decision_healthy.effort, EFFORT_HIGH)
        self.assertFalse(decision_healthy.throttled)

        # When budget is critical (>80% on 5h)
        decision_throttled = classify_task_effort(
            prompt=critical_prompt,
            token_budget={"rolling_5h_percent": 85.0, "weekly_percent": 40.0}
        )
        self.assertEqual(decision_throttled.effort, EFFORT_MEDIUM)
        self.assertTrue(decision_throttled.throttled)
        self.assertIn("Cota crítica", decision_throttled.reason)

        # When budget is critical and prompt is L1 (normally MEDIUM) -> downshifts to LOW
        decision_l1_throttled = classify_task_effort(
            prompt="Refatore a função isolada format_badge",
            token_budget={"rolling_5h_percent": 82.0, "weekly_percent": 40.0}
        )
        self.assertEqual(decision_l1_throttled.effort, EFFORT_LOW)
        self.assertTrue(decision_l1_throttled.throttled)

    def test_git_context_heuristics_when_prompt_empty(self):
        # Empty prompt, but branch is 'docs/update-guide'
        decision_docs = classify_task_effort(
            prompt="",
            git_context={"branch": "docs/token-optimization", "changed_files": ["README.md", "guide.md"]}
        )
        self.assertEqual(decision_docs.effort, EFFORT_LOW)
        self.assertEqual(decision_docs.risk_level, LEVEL_L0_TRIVIAL)

        # Empty prompt, but branch is 'feat/payment-integration'
        decision_feat = classify_task_effort(
            prompt="",
            git_context={"branch": "feat/user-onboarding", "changed_files": ["src/routes/user.ts"]}
        )
        self.assertEqual(decision_feat.effort, EFFORT_HIGH)
        self.assertEqual(decision_feat.risk_level, LEVEL_L2_FEATURE)

        # Empty prompt, but branch is 'hotfix/auth-leak'
        decision_hotfix = classify_task_effort(
            prompt="",
            git_context={"branch": "hotfix/auth-leak", "changed_files": ["src/auth/jwt.py"]}
        )
        self.assertEqual(decision_hotfix.effort, EFFORT_HIGH)
        self.assertEqual(decision_hotfix.risk_level, LEVEL_L3_CRITICAL)

    def test_explicit_effort_override(self):
        # User specified --effort low for a critical prompt
        decision = classify_task_effort(
            prompt="Implemente migração e segurança crítica",
            explicit_effort="low"
        )
        self.assertEqual(decision.effort, EFFORT_LOW)
        self.assertTrue(decision.override)

    def test_map_model_to_effort(self):
        self.assertEqual(map_model_to_effort("Gemini 3.8 Flash (High)", EFFORT_LOW), "Gemini 3.8 Flash (Low)")
        self.assertEqual(map_model_to_effort("Gemini 3.8 Flash (High)", EFFORT_MEDIUM), "Gemini 3.8 Flash (Medium)")
        self.assertEqual(map_model_to_effort("Gemini 3.8 Flash (Low)", EFFORT_HIGH), "Gemini 3.8 Flash (High)")
        self.assertEqual(map_model_to_effort("gemini-3.8-flash-high", EFFORT_LOW), "gemini-3.8-flash-low")
        self.assertEqual(map_model_to_effort("gemini-3.7-flash-medium", EFFORT_HIGH), "gemini-3.7-flash-high")
        # For models without effort suffix, append or keep
        self.assertEqual(map_model_to_effort("Claude Sonnet 4.6 (Thinking)", EFFORT_HIGH), "Claude Sonnet 4.6 (Thinking)")

    def test_update_settings_effort(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.json"
            initial_data = {
                "agentMode": "accept-edits",
                "model": "Gemini 3.8 Flash (High)"
            }
            settings_path.write_text(json.dumps(initial_data, indent=2), encoding="utf-8")

            success, old_m, new_m = update_settings_effort(settings_path, EFFORT_LOW)
            self.assertTrue(success)
            self.assertEqual(old_m, "Gemini 3.8 Flash (High)")
            self.assertEqual(new_m, "Gemini 3.8 Flash (Low)")

            # Verify file content
            updated_data = json.loads(settings_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_data["model"], "Gemini 3.8 Flash (Low)")
            self.assertEqual(updated_data["reasoningEffort"], "low")


if __name__ == "__main__":
    unittest.main()
