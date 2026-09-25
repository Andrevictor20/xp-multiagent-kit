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
    LiveServerQuota,
    LiveQuotaBucket,
    clean_refresh_text,
    render_plain_dashboard,
    detect_effort,
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

    def test_format_message_footer_tool_warning(self):
        turn = TurnStats(user_input_tokens=100, tool_tokens=2500, model_output_tokens=300, total_tokens=2900)
        rolling = RollingWindowStats(tokens_5h=30000, limit_5h=500000, tokens_7d=1200000, limit_7d=10000000)
        stats = parse_transcript_data(
            conversation_id="conv-warn",
            model_name="gemini-3.8-flash",
            steps=[{"type": "USER_INPUT", "content": "Hello"}],
            system_prompt_bytes=5000,
            rolling=rolling,
        )
        footer = format_message_footer(stats, turn)
        self.assertIn("⚠️ [Alto Uso de Ferramentas", footer)

    def test_clean_refresh_text(self):
        desc1 = "You have used some of your weekly limit, it will fully refresh in 6 days, 23 hours."
        self.assertEqual(clean_refresh_text(desc1), "renova em 6 d, 23 h")
        desc2 = "You have used some of your 5-hour limit, it will fully refresh in 4 hours, 49 minutes."
        self.assertEqual(clean_refresh_text(desc2), "renova em 4 h, 49 m")
        self.assertEqual(clean_refresh_text(""), "")
        self.assertEqual(clean_refresh_text(None), "")

    def test_format_message_footer_live_quota(self):
        turn = TurnStats(user_input_tokens=100, tool_tokens=200, model_output_tokens=300, total_tokens=600)
        live = LiveServerQuota(
            is_live=True,
            gemini_5h=LiveQuotaBucket(window="5h", remaining_fraction=0.884, description="refresh in 4 hours, 49 minutes"),
            gemini_weekly=LiveQuotaBucket(window="weekly", remaining_fraction=0.975, description="refresh in 6 days, 23 hours"),
        )
        stats = parse_transcript_data(
            conversation_id="c-live",
            model_name="gemini-3.8-flash",
            steps=[{"type": "USER_INPUT", "content": "hi"}],
            system_prompt_bytes=5000,
            live_quota=live,
        )
        footer = format_message_footer(stats, turn)
        self.assertIn("88.4% restante", footer)
        self.assertIn("97.5% restante", footer)
        self.assertIn("renova em 4 h, 49 m", footer)
        self.assertIn("renova em 6 d, 23 h", footer)

    def test_check_budget_status_live_critical_when_weekly_low(self):
        # Simulates user's screenshot where weekly remaining is only 2%
        live = LiveServerQuota(
            is_live=True,
            gemini_5h=LiveQuotaBucket(window="5h", remaining_fraction=0.51, description="refresh in 3 hours, 43 minutes"),
            gemini_weekly=LiveQuotaBucket(window="weekly", remaining_fraction=0.02, description="refresh in 2 days, 21 hours"),
        )
        stats = parse_transcript_data(
            conversation_id="c-crit",
            model_name="gemini-3.8-flash",
            steps=[{"type": "USER_INPUT", "content": "hi"}],
            system_prompt_bytes=5000,
            live_quota=live,
        )
        status, is_low, msg = check_budget_status(stats)
        self.assertEqual(status, "CRITICAL")
        self.assertTrue(is_low)
        self.assertIn("Cota Semanal (Google): apenas 2.0% restante", msg)

    def test_format_message_footer_shows_model_and_limits(self):
        turn = TurnStats(user_input_tokens=100, tool_tokens=200, model_output_tokens=300, total_tokens=600)
        rolling = RollingWindowStats(tokens_5h=30000, limit_5h=500000, tokens_7d=1200000, limit_7d=10000000)
        stats = parse_transcript_data(
            conversation_id="conv-limits",
            model_name="gemini-3.8-flash",
            steps=[{"type": "USER_INPUT", "content": "hi"}],
            system_prompt_bytes=5000,
            rolling=rolling,
        )
        footer = format_message_footer(stats, turn)
        self.assertIn("🎯 **Modelo & Limites:**", footer)
        self.assertIn("`Gemini 3.8 Flash`", footer)
        self.assertIn("Janela: `1.05M`", footer)
        self.assertIn("Saída Máx: `65.5k`", footer)

    def test_format_json_stats_includes_model_limits(self):
        sample_steps = [{"type": "USER_INPUT", "content": "Test input"}]
        stats = parse_transcript_data(
            conversation_id="c-json-limits",
            model_name="claude-sonnet-4-6",
            steps=sample_steps,
            system_prompt_bytes=4000,
        )
        json_str = format_json_stats(stats)
        data = json.loads(json_str)
        self.assertEqual(data["model_display_name"], "Claude Sonnet 4.6")
        self.assertIn("model_limits", data)
        self.assertEqual(data["model_limits"]["context_window"], 200_000)
        self.assertEqual(data["model_limits"]["max_output"], 8_192)

    def test_render_plain_dashboard_displays_model_and_limits(self):
        from io import StringIO
        import sys
        stats = parse_transcript_data(
            conversation_id="c-plain",
            model_name="gemini-3.8-pro",
            steps=[{"type": "USER_INPUT", "content": "hi"}],
            system_prompt_bytes=5000,
        )
        captured = StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured
            render_plain_dashboard(stats)
        finally:
            sys.stdout = old_stdout
        out = captured.getvalue()
        self.assertIn("Modelo Utilizado: Gemini 3.8 Pro (gemini-3.8-pro)", out)
        self.assertIn("Limites Modelo:", out)
        self.assertIn("2,097,152", out)
        self.assertIn("65,536", out)

    def test_detect_effort_from_steps(self):
        steps_high = [
            {"type": "USER_INPUT", "content": "Olá\n<USER_SETTINGS_CHANGE>\nThe user changed setting Model Selection from None to Gemini 3.8 Flash (High).\n</USER_SETTINGS_CHANGE>"}
        ]
        self.assertEqual(detect_effort("c-eff-high", steps=steps_high), "High")

        steps_low = [
            {"type": "USER_INPUT", "content": "<USER_SETTINGS_CHANGE>\nThe user changed setting Model Selection from Gemini 3.8 Flash (High) to Claude Sonnet 4.6 (Low).\n</USER_SETTINGS_CHANGE>"}
        ]
        self.assertEqual(detect_effort("c-eff-low", steps=steps_low), "Low")

    def test_format_message_footer_with_effort(self):
        turn = TurnStats(user_input_tokens=100, tool_tokens=200, model_output_tokens=300, total_tokens=600)
        stats = parse_transcript_data(
            conversation_id="conv-effort",
            model_name="gemini-3.8-flash",
            steps=[{"type": "USER_INPUT", "content": "hi"}],
            system_prompt_bytes=5000,
            effort="High",
        )
        footer = format_message_footer(stats, turn)
        self.assertIn("Effort: `High`", footer)

    def test_render_plain_dashboard_with_effort(self):
        from io import StringIO
        import sys
        stats = parse_transcript_data(
            conversation_id="c-plain-eff",
            model_name="gemini-3.8-flash",
            steps=[{"type": "USER_INPUT", "content": "hi"}],
            system_prompt_bytes=5000,
            effort="High",
        )
        captured = StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured
            render_plain_dashboard(stats)
        finally:
            sys.stdout = old_stdout
        out = captured.getvalue()
        self.assertIn("Effort: High", out)

    def test_format_json_stats_with_effort(self):
        stats = parse_transcript_data(
            conversation_id="c-json-eff",
            model_name="gemini-3.8-flash",
            steps=[{"type": "USER_INPUT", "content": "hi"}],
            system_prompt_bytes=5000,
            effort="High",
        )
        json_str = format_json_stats(stats)
        data = json.loads(json_str)
        self.assertEqual(data["effort"], "High")


class TestProviderDefaults(unittest.TestCase):
    """Testes para get_provider_defaults e PROVIDER_RATE_LIMITS."""

    def setUp(self):
        from scripts.token_tracker import get_provider_defaults
        self.gpd = get_provider_defaults

    def test_claude_defaults(self):
        d = self.gpd("claude-sonnet-4-6")
        self.assertEqual(d["limit_5h"], 100_000)
        self.assertEqual(d["limit_7d"], 2_000_000)

    def test_claude_older(self):
        d = self.gpd("claude-3-5-sonnet")
        self.assertEqual(d["limit_5h"], 100_000)

    def test_openai_gpt4o(self):
        d = self.gpd("gpt-4o")
        self.assertEqual(d["limit_5h"], 80_000)
        self.assertEqual(d["limit_7d"], 1_500_000)

    def test_openai_o1(self):
        d = self.gpd("o1")
        self.assertEqual(d["limit_5h"], 80_000)

    def test_openai_o3_mini(self):
        d = self.gpd("o3-mini")
        self.assertEqual(d["limit_5h"], 80_000)

    def test_deepseek(self):
        d = self.gpd("deepseek-v3")
        self.assertEqual(d["limit_5h"], 60_000)
        self.assertEqual(d["limit_7d"], 1_000_000)

    def test_gemini_flash(self):
        d = self.gpd("gemini-3.8-flash")
        self.assertEqual(d["limit_5h"], 800_000)
        self.assertEqual(d["limit_7d"], 10_000_000)

    def test_unknown_model_fallback(self):
        d = self.gpd("some-unknown-model-xyz")
        self.assertEqual(d["limit_5h"], 80_000)
        self.assertEqual(d["limit_7d"], 1_000_000)

    def test_anthropic_in_name(self):
        d = self.gpd("anthropic-custom-model")
        self.assertEqual(d["limit_5h"], 100_000)


if __name__ == "__main__":
    unittest.main()
