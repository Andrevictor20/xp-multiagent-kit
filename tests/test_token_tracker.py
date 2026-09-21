import unittest
import json
import tempfile
import time
from pathlib import Path
from scripts.token_tracker import (
    estimate_tokens,
    get_model_limits,
    parse_token_limit,
    parse_transcript_data,
    calculate_rolling_windows,
    format_badge,
    format_json_stats,
    format_markdown_report,
    check_budget_status,
    audit_token_bottlenecks,
    calculate_turn_stats,
    detect_model_name_from_steps,
    format_message_footer,
    get_model_display_name,
    TokenStats,
    RollingWindowStats,
    TurnStats,
)

class TestTokenTracker(unittest.TestCase):
    def test_estimate_tokens_empty(self):
        self.assertEqual(estimate_tokens(""), 0)
        self.assertEqual(estimate_tokens(None), 0)

    def test_estimate_tokens_calibration(self):
        text = "function calculateTotal(items) { return items.reduce((a, b) => a + b.price, 0); }"
        tokens = estimate_tokens(text)
        self.assertGreater(tokens, 15)
        self.assertLess(tokens, 35)

    def test_parse_token_limit(self):
        self.assertEqual(parse_token_limit("500k"), 500_000)
        self.assertEqual(parse_token_limit("10M"), 10_000_000)
        self.assertEqual(parse_token_limit("1.5M"), 1_500_000)
        self.assertEqual(parse_token_limit("250000"), 250_000)
        self.assertEqual(parse_token_limit(None, default=500_000), 500_000)

    def test_get_model_limits_known_models(self):
        limits_flash = get_model_limits("gemini-3.8-flash")
        self.assertEqual(limits_flash["context_window"], 1_048_576)
        self.assertEqual(limits_flash["max_output"], 65_536)

        limits_pro = get_model_limits("gemini-1.5-pro")
        self.assertEqual(limits_pro["context_window"], 2_097_152)
        self.assertEqual(limits_pro["max_output"], 65_536)

        limits_claude = get_model_limits("claude-sonnet-4-6")
        self.assertEqual(limits_claude["context_window"], 200_000)
        self.assertEqual(limits_claude["max_output"], 8_192)

    def test_get_model_limits_unknown_fallback(self):
        limits = get_model_limits("custom-unknown-model")
        self.assertEqual(limits["context_window"], 1_000_000)
        self.assertEqual(limits["max_output"], 8_192)

    def test_parse_transcript_data(self):
        sample_steps = [
            {"type": "USER_INPUT", "content": "Olá, preciso de um script de teste."},
            {"type": "PLANNER_RESPONSE", "content": "Vou criar o script para você.", "thinking": "Pensando na solução ideal..."},
            {"type": "RUN_COMMAND", "content": "Created At: ... Output: test output line 1\ntest output line 2"},
            {"type": "VIEW_FILE", "content": "1: def hello():\n2:     pass\n"}
        ]
        rolling = RollingWindowStats(
            tokens_5h=45000,
            conversations_5h=2,
            limit_5h=500000,
            tokens_7d=6500000,
            conversations_7d=8,
            limit_7d=10000000
        )
        stats = parse_transcript_data(
            conversation_id="test-conv-123",
            model_name="gemini-3.8-flash",
            steps=sample_steps,
            system_prompt_bytes=80000,
            rolling=rolling
        )
        self.assertIsInstance(stats, TokenStats)
        self.assertEqual(stats.conversation_id, "test-conv-123")
        self.assertEqual(stats.model_name, "gemini-3.8-flash")
        self.assertGreater(stats.system_prompt_tokens, 15000)
        self.assertGreater(stats.user_input_tokens, 5)
        self.assertGreater(stats.tool_tokens, 10)
        self.assertGreater(stats.model_output_tokens, 10)
        self.assertGreater(stats.total_tokens, stats.system_prompt_tokens)
        self.assertGreater(stats.remaining_tokens, 900000)
        self.assertIn("RUN_COMMAND", stats.top_tools)
        self.assertIn("VIEW_FILE", stats.top_tools)
        self.assertEqual(stats.rolling.tokens_5h, 45000)
        self.assertEqual(stats.rolling.limit_5h, 500000)
        self.assertEqual(stats.rolling.tokens_7d, 6500000)
        self.assertEqual(stats.rolling.limit_7d, 10000000)
        self.assertAlmostEqual(stats.rolling.percent_5h, 9.0, places=1)
        self.assertAlmostEqual(stats.rolling.percent_7d, 65.0, places=1)

    def test_calculate_rolling_windows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            t1 = base / "brain" / "conv1" / ".system_generated" / "logs" / "transcript.jsonl"
            t1.parent.mkdir(parents=True)
            t1.write_text('{"type":"USER_INPUT","content":"hello"}\n', encoding="utf-8")

            rolling = calculate_rolling_windows(search_dirs=[base], limit_5h=300000, limit_7d=5000000)
            self.assertGreaterEqual(rolling.tokens_5h, 1)
            self.assertGreaterEqual(rolling.tokens_7d, 1)
            self.assertEqual(rolling.conversations_5h, 1)
            self.assertEqual(rolling.limit_5h, 300000)
            self.assertEqual(rolling.limit_7d, 5000000)

    def test_format_badge_shows_used_and_total_for_all_limits(self):
        sample_steps = [{"type": "USER_INPUT", "content": "Hello world"}]
        rolling = RollingWindowStats(
            tokens_5h=30000,
            conversations_5h=1,
            limit_5h=500000,
            tokens_7d=1200000,
            conversations_7d=5,
            limit_7d=10000000
        )
        stats = parse_transcript_data(
            conversation_id="c1",
            model_name="gemini-3.8-flash",
            steps=sample_steps,
            system_prompt_bytes=4000,
            rolling=rolling
        )
        badge = format_badge(stats)
        self.assertIn("📊 **Token Telemetry (gemini-3.8-flash):**", badge)
        # Verify used/total for 5h and weekly
        self.assertIn("5h:", badge)
        self.assertIn("/500.0k", badge)
        self.assertIn("Semana:", badge)
        self.assertIn("/10.00M", badge)

    def test_format_json_stats(self):
        sample_steps = [{"type": "USER_INPUT", "content": "Test input"}]
        rolling = RollingWindowStats(
            tokens_5h=20000,
            conversations_5h=1,
            limit_5h=500000,
            tokens_7d=500000,
            conversations_7d=3,
            limit_7d=10000000
        )
        stats = parse_transcript_data(
            conversation_id="c2",
            model_name="gemini-3.8-flash",
            steps=sample_steps,
            system_prompt_bytes=4000,
            rolling=rolling
        )
        json_str = format_json_stats(stats)
        data = json.loads(json_str)
        self.assertEqual(data["conversation_id"], "c2")
        self.assertIn("rolling_limits", data)
        self.assertEqual(data["rolling_limits"]["tokens_5h"], 20000)
        self.assertEqual(data["rolling_limits"]["limit_5h"], 500000)
        self.assertEqual(data["rolling_limits"]["tokens_7d"], 500000)
        self.assertEqual(data["rolling_limits"]["limit_7d"], 10000000)

    def test_format_markdown_report(self):
        sample_steps = [
            {"type": "USER_INPUT", "content": "Test input"},
            {"type": "RUN_COMMAND", "content": "sample output"}
        ]
        rolling = RollingWindowStats(
            tokens_5h=45000,
            conversations_5h=2,
            limit_5h=500000,
            tokens_7d=6500000,
            conversations_7d=8,
            limit_7d=10000000
        )
        stats = parse_transcript_data(
            conversation_id="c3",
            model_name="gemini-3.8-flash",
            steps=sample_steps,
            system_prompt_bytes=4000,
            rolling=rolling
        )
        report = format_markdown_report(stats)
        self.assertIn("Janela Móvel de 5 Horas", report)
        self.assertIn("Janela Semanal", report)
        self.assertIn("Teto / Limite Total", report)

    def test_check_budget_status_healthy(self):
        rolling = RollingWindowStats(tokens_5h=20000, limit_5h=500000, tokens_7d=2000000, limit_7d=10000000)
        stats = parse_transcript_data(
            conversation_id="h1",
            model_name="gemini-3.8-flash",
            steps=[{"type": "USER_INPUT", "content": "hi"}],
            system_prompt_bytes=5000,
            rolling=rolling
        )
        status, is_low, msg = check_budget_status(stats)
        self.assertEqual(status, "HEALTHY")
        self.assertFalse(is_low)

    def test_check_budget_status_critical(self):
        rolling = RollingWindowStats(tokens_5h=450000, limit_5h=500000, tokens_7d=9000000, limit_7d=10000000)
        stats = parse_transcript_data(
            conversation_id="c1",
            model_name="gemini-3.8-flash",
            steps=[{"type": "USER_INPUT", "content": "hi"}],
            system_prompt_bytes=5000,
            rolling=rolling
        )
        status, is_low, msg = check_budget_status(stats)
        self.assertEqual(status, "CRITICAL")
        self.assertTrue(is_low)
        self.assertIn("ALERTA DE LIMITE", msg)

    def test_audit_token_bottlenecks_detection(self):
        sample_steps = [
            {"type": "RUN_COMMAND", "content": "x" * 20000},
            {"type": "USER_INPUT", "content": "short"}
        ]
        stats = parse_transcript_data(
            conversation_id="audit1",
            model_name="gemini-3.8-flash",
            steps=sample_steps,
            system_prompt_bytes=2000
        )
        audit = audit_token_bottlenecks(stats)
        self.assertIn("bottlenecks", audit)
        self.assertGreaterEqual(len(audit["bottlenecks"]), 1)
        self.assertIn("RUN_COMMAND", audit["bottlenecks"][0]["tool"])
        self.assertIn("recommendation", audit["bottlenecks"][0])

    def test_get_model_limits_expanded_models(self):
        # Modelos Google
        self.assertEqual(get_model_limits("gemini-3.8-flash")["context_window"], 1_048_576)
        self.assertEqual(get_model_limits("gemini-3.7-pro")["context_window"], 2_097_152)
        self.assertEqual(get_model_limits("gemini-2.5-flash")["context_window"], 1_048_576)
        self.assertEqual(get_model_limits("gemini-2.0-flash")["context_window"], 1_048_576)

        # Modelos Anthropic
        self.assertEqual(get_model_limits("claude-sonnet-4-6")["context_window"], 200_000)
        self.assertEqual(get_model_limits("claude-3-7-sonnet")["context_window"], 200_000)
        self.assertEqual(get_model_limits("claude-opus-4-6")["context_window"], 200_000)

        # Modelos OpenAI
        self.assertEqual(get_model_limits("gpt-4o")["context_window"], 128_000)
        self.assertEqual(get_model_limits("o1")["context_window"], 200_000)
        self.assertEqual(get_model_limits("o3-mini")["context_window"], 200_000)

        # Modelos DeepSeek
        self.assertEqual(get_model_limits("deepseek-chat")["context_window"], 128_000)
        self.assertEqual(get_model_limits("deepseek-reasoner")["context_window"], 128_000)

    def test_get_model_display_name(self):
        self.assertEqual(get_model_display_name("gemini-3.8-flash"), "Gemini 3.8 Flash")
        self.assertEqual(get_model_display_name("claude-sonnet-4-6"), "Claude Sonnet 4.6")
        self.assertEqual(get_model_display_name("gpt-4o"), "GPT-4o")
        self.assertEqual(get_model_display_name("o3-mini"), "o3-mini")
        self.assertEqual(get_model_display_name("custom-model"), "custom-model")

    def test_detect_model_name_from_steps(self):
        steps = [
            {
                "type": "USER_INPUT",
                "content": "Olá\n<USER_SETTINGS_CHANGE>\nThe user changed setting `Model Selection` from None to Claude Sonnet 4.6 (Thinking).\n</USER_SETTINGS_CHANGE>",
            },
            {"type": "PLANNER_RESPONSE", "content": "Olá, como posso ajudar?"},
            {
                "type": "USER_INPUT",
                "content": "Mudei de ideia\n<USER_SETTINGS_CHANGE>\nThe user changed setting `Model Selection` from Claude Sonnet 4.6 (Thinking) to Gemini 3.8 Flash (High).\n</USER_SETTINGS_CHANGE>",
            },
        ]
        model = detect_model_name_from_steps(steps)
        self.assertEqual(model, "gemini-3.8-flash")

    def test_calculate_turn_stats(self):
        steps = [
            {"type": "USER_INPUT", "content": "Turno 1: Mensagem inicial com 50 caracteres para teste"},
            {"type": "PLANNER_RESPONSE", "content": "Resposta 1 do assistente", "thinking": "Pensando na resposta 1"},
            {"type": "RUN_COMMAND", "content": "Resultado do comando 1"},
            {"type": "USER_INPUT", "content": "Turno 2: Pergunta específica sobre consumo de tokens"},
            {"type": "RUN_COMMAND", "content": "Execução da ferramenta do turno 2 com 100 caracteres de saída para testar tokens"},
            {"type": "PLANNER_RESPONSE", "content": "Resposta final do turno 2", "thinking": "Refletindo profundamente"},
        ]
        turn = calculate_turn_stats(steps)
        self.assertIsInstance(turn, TurnStats)
        self.assertGreater(turn.user_input_tokens, 5)
        self.assertGreater(turn.tool_tokens, 10)
        self.assertGreater(turn.model_output_tokens, 5)
        self.assertEqual(
            turn.total_tokens,
            turn.user_input_tokens + turn.tool_tokens + turn.model_output_tokens,
        )

    def test_format_message_footer(self):
        turn = TurnStats(
            user_input_tokens=320,
            tool_tokens=450,
            model_output_tokens=630,
            total_tokens=1400,
        )
        sample_steps = [{"type": "USER_INPUT", "content": "Hello"}]
        rolling = RollingWindowStats(
            tokens_5h=30000,
            limit_5h=500000,
            tokens_7d=1200000,
            limit_7d=10000000,
        )
        stats = parse_transcript_data(
            conversation_id="conv-footer",
            model_name="gemini-3.8-flash",
            steps=sample_steps,
            system_prompt_bytes=5000,
            rolling=rolling,
        )
        footer = format_message_footer(stats, turn)
        self.assertIn("🪙 **Consumo Desta Mensagem:**", footer)
        self.assertIn("Entrada:", footer)
        self.assertIn("Ferramentas:", footer)
        self.assertIn("Resposta:", footer)
        self.assertIn("📊 **Telemetria Acumulada (Gemini 3.8 Flash):**", footer)
        self.assertIn("Contexto:", footer)
        self.assertIn("5h:", footer)
        self.assertIn("Semana:", footer)


if __name__ == "__main__":
    unittest.main()
