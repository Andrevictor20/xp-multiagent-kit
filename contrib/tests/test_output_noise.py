import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.output_noise import clean_output, is_ascii_art, is_noise_line, noise_stats

# Banner real de fastfetch observado em chamadas de ferramenta deste ambiente
FASTFETCH_BANNER = """             .',;::::;,'.                 ╭───────────╮
         .';:cccccccccccc:;,.             │  user    │ andrevmp
      .;cccccccccccccccccccccc;.          │  hname   │ andrevmp-pc
    .:cccccccccccccccccccccccccc:.        │  distro  │ Fedora Linux 44 x86_64
cccccc;0MMKxdd:;MMMkddc.;cccccccccccc:    │  cpu     │ AMD Ryzen 5 3500U
 ':cccccccccccccccc::;,..
"""

REAL_OUTPUT = """$ wc -l scripts/token_tracker.py
1969 scripts/token_tracker.py
OK (3 tests)
"""


class TestShellNoiseStripping(unittest.TestCase):

    def test_banner_lines_are_detected_as_noise(self):
        for line in FASTFETCH_BANNER.splitlines():
            if line.strip():
                self.assertTrue(is_noise_line(line), f"não detectado: {line!r}")

    def test_ascii_art_without_box_chars_is_detected(self):
        self.assertTrue(is_ascii_art("cccccc;0MMKxdd:;MMMkddc.;cccccccccccc:"))
        self.assertTrue(is_ascii_art(" ':cccccccccccccccc::;,."))

    def test_real_command_output_is_preserved(self):
        for line in REAL_OUTPUT.splitlines():
            self.assertFalse(is_noise_line(line), f"falso positivo: {line!r}")

    def test_clean_output_removes_banner_and_keeps_result(self):
        cleaned = clean_output(FASTFETCH_BANNER + REAL_OUTPUT)
        self.assertIn("1969 scripts/token_tracker.py", cleaned)
        self.assertIn("OK (3 tests)", cleaned)
        self.assertNotIn("andrevmp-pc", cleaned)
        self.assertNotIn("cccccccccc", cleaned)
        self.assertIn("linhas de banner/decoração de shell removidas", cleaned)

    def test_noise_stats_reports_savings(self):
        stats = noise_stats(FASTFETCH_BANNER + REAL_OUTPUT)
        self.assertEqual(stats["noise_lines"], len(FASTFETCH_BANNER.splitlines()))
        self.assertGreater(stats["saved_chars"], 200)

    def test_short_decorative_block_below_threshold_is_kept(self):
        text = "╭─╮\nreal output line\n"
        cleaned = clean_output(text)
        self.assertIn("╭─╮", cleaned)
        self.assertIn("real output line", cleaned)

    def test_code_lines_are_not_stripped(self):
        code = "def strip_shell_noise(lines):\n    kept = []\n    return kept, removed\n"
        self.assertEqual(clean_output(code), code)

    def test_never_worse_keeps_smaller_filtered(self):
        from scripts.output_noise import never_worse
        raw = "a" * 100
        filtered = "a" * 10
        self.assertEqual(never_worse(raw, filtered), filtered)

    def test_never_worse_reverts_if_filtered_is_longer(self):
        from scripts.output_noise import never_worse
        raw = "small"
        filtered = "much_longer_sanitized_string_with_extra_decorations"
        self.assertEqual(never_worse(raw, filtered), raw)


if __name__ == "__main__":
    unittest.main()
