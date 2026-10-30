import unittest
import tempfile
import os
from pathlib import Path
from scripts.goldfish_review import check_anti_glazing, validate_heilmeier_compliance

class TestGoldfishReview(unittest.TestCase):
    def test_check_anti_glazing_detects_banned_words(self):
        sample_bad = "This is a brilliant solution that integrates seamlessly and is blazingly fast."
        findings = check_anti_glazing(sample_bad)
        self.assertGreaterEqual(len(findings), 3)

    def test_check_anti_glazing_passes_clean_content(self):
        sample_clean = "The cache layer reduces latency by 40ms by preloading user preferences in Redis."
        findings = check_anti_glazing(sample_clean)
        self.assertEqual(len(findings), 0)

    def test_validate_heilmeier_compliance_identifies_missing_sections(self):
        incomplete_spec = """
        # Feature Spec
        ## Objetivo
        Adicionar autenticação biométrica no login mobile.
        """
        result = validate_heilmeier_compliance(incomplete_spec)
        self.assertFalse(result["compliant"])
        self.assertIn("current_state", result["missing"])
        self.assertIn("risks_and_costs", result["missing"])

    def test_validate_heilmeier_compliance_full(self):
        complete_spec = """
        # Feature Spec Completa
        ## Objetivo / Problem Statement
        O que estamos tentando fazer: substituir polling por WebSockets.
        ## Estado Atual / How is it done today
        Como isso é feito hoje: polling HTTP a cada 5 segundos.
        ## Nova Abordagem / What is new
        O que há de novo: multiplexação de canais em conexão TCP persistente.
        ## Impacto / Who cares
        Quem se importa: reduz consumo de bateria mobile e carga no API Gateway.
        ## Riscos e Custos / Trade-offs
        Riscos e custos: manutenção de conexões abertas exige balanceamento com sticky sessions.
        ## Métricas e Testes / Evaluation
        Critérios de sucesso: taxa de entrega sob 200ms e teste de stress com 50k conexões simultâneas.
        """
        result = validate_heilmeier_compliance(complete_spec)
        self.assertTrue(result["compliant"])
        self.assertEqual(result["score"], 100.0)

if __name__ == "__main__":
    unittest.main()
