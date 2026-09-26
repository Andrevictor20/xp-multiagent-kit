import os
import unittest
from scripts.context_compactor import (
    strip_ansi_codes,
    compress_whitespace,
    compress_logs,
    compress_diff,
    compress_json,
    compress_conversation_turns,
    calculate_compression_stats,
    ContextualCompressorWithRetrieval,
    compact_payload,
    compress_ci_output,
    compress_git_output,
    compress_html,
)


class TestContextCompactor(unittest.TestCase):
    def test_strip_ansi_codes(self):
        colored_text = "\x1b[32mSUCCESS:\x1b[0m All tests passed! \x1b[1;31m[ERROR]\x1b[0m"
        clean = strip_ansi_codes(colored_text)
        self.assertEqual(clean, "SUCCESS: All tests passed! [ERROR]")

    def test_compress_whitespace(self):
        text = "line 1   \n\n\n\n\nline 2    \n\nline 3"
        compressed = compress_whitespace(text)
        self.assertEqual(compressed, "line 1\n\nline 2\n\nline 3")

    def test_compress_logs_dedup_repeats(self):
        log = (
            "INFO: connecting to db\n"
            "DEBUG: retry 1\n"
            "DEBUG: retry 1\n"
            "DEBUG: retry 1\n"
            "DEBUG: retry 1\n"
            "ERROR: timeout reached"
        )
        compressed = compress_logs(log)
        self.assertIn("INFO: connecting to db", compressed)
        self.assertIn("DEBUG: retry 1 (repeated 4x)", compressed)
        self.assertIn("ERROR: timeout reached", compressed)

    def test_compress_diff_collapses_context(self):
        diff = (
            "diff --git a/file.py b/file.py\n"
            "--- a/file.py\n"
            "+++ b/file.py\n"
            "@@ -1,15 +1,15 @@\n"
            " context line 1\n"
            " context line 2\n"
            " context line 3\n"
            " context line 4\n"
            " context line 5\n"
            " context line 6\n"
            " context line 7\n"
            "-old code\n"
            "+new code\n"
            " context line 8\n"
            " context line 9\n"
            " context line 10\n"
        )
        compressed = compress_diff(diff, max_context_lines=2)
        self.assertIn("-old code", compressed)
        self.assertIn("+new code", compressed)
        self.assertIn("[... unchanged lines collapsed ...]", compressed)

    def test_ccr_cache_and_retrieve(self):
        cache_dir = "/tmp/test_ccr_cache"
        ccr = ContextualCompressorWithRetrieval(cache_dir=cache_dir, max_inline_chars=100)
        
        long_content = "X" * 500
        compressed, doc_id = ccr.compress("tool_output", long_content)
        
        self.assertIn("[CCR_COMPACT", compressed)
        self.assertIn(doc_id, compressed)
        
        # Test retrieve
        retrieved = ccr.retrieve(doc_id)
        self.assertEqual(retrieved, long_content)
        
        # Clean test cache
        ccr.clean_cache()

    def test_compact_payload_pipeline(self):
        payload = {
            "output": "\x1b[32mPASS\x1b[0m\n\n\n\nLine 1\nLine 1\nLine 1\nLine 2"
        }
        res = compact_payload(payload.get("output", ""))
        self.assertIn("PASS", res)
        self.assertNotIn("\x1b[32m", res)
        self.assertIn("Line 1 (repeated 3x)", res)

    def test_compress_json(self):
        complex_json = '{\n  "status": "ok",\n  "count": 42,\n  "empty": null,\n  "items": [\n    1,\n    2\n  ]\n}'
        compressed = compress_json(complex_json)
        self.assertEqual(compressed, '{"status":"ok","count":42,"items":[1,2]}')

    def test_compress_conversation_turns(self):
        messages = [
            {"role": "user", "content": "Rode o comando de teste"},
            {"role": "assistant", "content": "Executando...", "tool_calls": [{"name": "run_command"}]},
            {"role": "tool", "content": "X" * 3000, "tool_name": "run_command"},
            {"role": "user", "content": "Qual foi o resultado final?"},
            {"role": "assistant", "content": "Tudo passou com sucesso."},
        ]
        compacted = compress_conversation_turns(messages, budget_chars=500)
        # Verifica que o tool result longo antigo foi compactado
        tool_msg = [m for m in compacted if m.get("role") == "tool"][0]
        self.assertIn("[CCR_COMPACT", tool_msg["content"])
        # As mensagens recentes continuam intactas
        self.assertEqual(compacted[-1]["content"], "Tudo passou com sucesso.")

    def test_calculate_compression_stats(self):
        original = "A" * 1000
        compressed = "A" * 200
        stats = calculate_compression_stats(original, compressed)
        self.assertEqual(stats["original_chars"], 1000)
        self.assertEqual(stats["compressed_chars"], 200)
        self.assertEqual(stats["saved_chars"], 800)
        self.assertEqual(stats["reduction_percent"], 80.0)

    def test_compress_ci_output_filters_noise_and_keeps_failure(self):
        verbose_ci_log = (
            "2026-09-26T15:00:00.000Z ##[group]Operating System\n"
            "Ubuntu 22.04.4 LTS\n"
            "##[endgroup]\n"
            "2026-09-26T15:00:01.000Z Set up job\n"
            "2026-09-26T15:00:02.000Z Run actions/checkout@v4\n"
            "2026-09-26T15:00:05.000Z Complete job and prepare environment\n"
            "2026-09-26T15:00:10.000Z ##[error]Process completed with exit code 1.\n"
            "FAIL src/runner.test.ts > batch execution failed with timeout\n"
            "Error: Connection timed out after 5000ms\n"
            "    at Timeout._onTimeout (src/runner.ts:42:15)\n"
            "2026-09-26T15:00:12.000Z Post Run actions/checkout@v4\n"
        )
        compressed = compress_ci_output(verbose_ci_log, max_error_lines=10)
        self.assertIn("FAIL src/runner.test.ts", compressed)
        self.assertIn("Error: Connection timed out", compressed)
        self.assertNotIn("Ubuntu 22.04.4 LTS", compressed)
        self.assertNotIn("Post Run actions/checkout@v4", compressed)

    def test_compress_git_output_collapses_untracked_files(self):
        verbose_status = (
            "On branch main\n"
            "Your branch is up to date with 'origin/main'.\n\n"
            "Untracked files:\n"
            "  (use \"git add <file>...\" to include in what will be committed)\n"
            + "\n".join(f"\tfile_{i}.tmp" for i in range(30)) + "\n"
        )
        compressed = compress_git_output(verbose_status, max_items=5)
        self.assertIn("On branch main", compressed)
        self.assertIn("file_0.tmp", compressed)
        self.assertIn("untracked files omitted", compressed)

    def test_compress_html_strips_scripts_styles_and_preserves_text(self):
        raw_html = (
            "<!DOCTYPE html><html><head><title>Test Page</title>"
            "<style>body { font-size: 14px; color: red; }</style>"
            "<script>function track() { console.log('user event'); }</script>"
            "</head><body>"
            "<!-- navigation header -->"
            "<header><nav><a href='/home'>Home</a> | <a href='/docs'>Docs</a></nav></header>"
            "<h1>Documentação da API</h1>"
            "<p>Esta é a introdução com detalhes essenciais.</p>"
            "<svg><circle r='10'/></svg>"
            "<ul><li>Item 1: Endpoint Auth</li><li>Item 2: Webhooks</li></ul>"
            "<script type='text/javascript'>window.__INITIAL_STATE__ = { huge: 'payload' };</script>"
            "<footer>Copyright 2026</footer>"
            "</body></html>"
        )
        compressed = compress_html(raw_html)
        self.assertIn("Documentação da API", compressed)
        self.assertIn("introdução com detalhes essenciais", compressed)
        self.assertIn("Endpoint Auth", compressed)
        self.assertNotIn("<style>", compressed)
        self.assertNotIn("font-size: 14px", compressed)
        self.assertNotIn("function track()", compressed)
        self.assertNotIn("__INITIAL_STATE__", compressed)
        self.assertNotIn("<svg>", compressed)
        self.assertNotIn("<!-- navigation header -->", compressed)


if __name__ == "__main__":
    unittest.main()
