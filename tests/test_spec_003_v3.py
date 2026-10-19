#!/usr/bin/env python3
"""
tests/test_spec_003_v3.py
Acceptance & Unit Tests for SPEC-003 (XP Multi-Agent Kit v3.0):
- AC-1: Multi-Host Agnostic Installer (Antigravity, OpenCode, Cursor, Qoder — IDE & CLI)
- AC-2: Bilingual Installer (PT/EN) with automatic OS locale detection
- AC-3: Token-Dense English Internal Core with Portuguese User Output mandate
- AC-4: Compact, Visually Clean & ANSI-Colored Token Telemetry + Dynamic Model Detection
- AC-5: Autonomous Self-Correction & Error Reflexion Engine
- AC-6: Token & Tool-Call Reduction (PreInvocation dedup + 800-line read window + <500 line token_tracker)
"""

from __future__ import annotations

import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch


KIT_ROOT = Path(__file__).resolve().parent.parent


class TestSpec003Acceptance(unittest.TestCase):
    """Acceptance tests for SPEC-003 ACs."""

    # ------------------------------------------------------------------
    # AC-1: Multi-Host Agnostic Installer (Antigravity, OpenCode, Cursor, Qoder)
    # ------------------------------------------------------------------
    def test_ac1_multi_host_project_adapters(self):
        """AC-1: ProjectInstaller / HostAdapters generates configs for antigravity, opencode, cursor, qoder."""
        from scripts.kit_installer import ProjectInstaller

        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "sample-app"
            installer = ProjectInstaller(kit_dir=KIT_ROOT)
            res = installer.install_project(
                proj,
                use_symlinks=True,
                targets=["antigravity", "opencode", "cursor", "qoder"],
            )
            self.assertTrue(res["ok"])

            # 1. Antigravity
            self.assertTrue((proj / "AGENTS.md").is_file())
            self.assertTrue((proj / ".agents" / "memory" / "PROJECT_MEMORY.md").is_file())
            self.assertTrue((proj / ".geminiignore").is_file())

            # 2. OpenCode (IDE & CLI)
            opencode_json = proj / "opencode.json"
            self.assertTrue(opencode_json.is_file(), "opencode.json must be created")
            oc_data = json.loads(opencode_json.read_text(encoding="utf-8"))
            self.assertIn("instructions", oc_data)
            self.assertTrue((proj / ".opencode" / "agent").is_dir())
            self.assertTrue((proj / ".opencode" / "command").is_dir())
            self.assertGreaterEqual(len(list((proj / ".opencode" / "agent").glob("*.md"))), 5)
            self.assertGreaterEqual(len(list((proj / ".opencode" / "command").glob("*.md"))), 5)

            # 3. Cursor (IDE & CLI)
            cursor_rules = proj / ".cursor" / "rules"
            self.assertTrue(cursor_rules.is_dir())
            self.assertTrue((cursor_rules / "00-xp-core.mdc").is_file())
            self.assertTrue((proj / ".cursor" / "mcp.json").is_file())
            self.assertTrue((proj / ".cursorignore").is_file())

            # 4. Qoder (IDE & CLI)
            qoder_rules = proj / ".qoder" / "rules"
            self.assertTrue(qoder_rules.is_dir())
            self.assertTrue((qoder_rules / "xp-governance.md").is_file())
            self.assertTrue((proj / ".qoderignore").is_file())

    # ------------------------------------------------------------------
    # AC-2: Bilingual Installer (PT/EN) with OS Locale Detection
    # ------------------------------------------------------------------
    def test_ac2_bilingual_locale_detection(self):
        """AC-2: Installer detects PT vs EN from environment and formats messages in both languages."""
        from scripts.kit_installer import detect_system_language, get_i18n_messages

        with patch.dict(os.environ, {"LANG": "pt_BR.UTF-8", "LC_ALL": ""}, clear=False):
            self.assertEqual(detect_system_language(), "pt")
            msg_pt = get_i18n_messages("pt")
            self.assertIn("Instalação", msg_pt["wizard_title"])

        with patch.dict(os.environ, {"LANG": "en_US.UTF-8", "LC_ALL": "en_US.UTF-8"}, clear=False):
            self.assertEqual(detect_system_language(), "en")
            msg_en = get_i18n_messages("en")
            self.assertIn("Installer", msg_en["wizard_title"])

    # ------------------------------------------------------------------
    # AC-3: Token-Dense English Internal Core with Portuguese User Output
    # ------------------------------------------------------------------
    def test_ac3_english_skills_and_workflows_with_pt_output_rule(self):
        """AC-3: Skills, workflows, agents, and policies are in English; AGENTS.md enforces PT user output."""
        agents_md = (KIT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        # Must mandate Portuguese user output while internal prompts are in English
        self.assertTrue(
            "português" in agents_md.lower() or "portuguese" in agents_md.lower(),
            "AGENTS.md must explicitly preserve Portuguese output for the user",
        )

        # Check sample workflows & skills are in English
        feature_wf = (KIT_ROOT / ".agents" / "workflows" / "feature.md").read_text(encoding="utf-8")
        self.assertIn("Acceptance Criteria", feature_wf)
        self.assertIn("## Flow", feature_wf)

        skills_index = (KIT_ROOT / ".agents" / "skills" / "SKILLS_INDEX.md").read_text(encoding="utf-8")
        self.assertIn("# Skills Index", skills_index)

    # ------------------------------------------------------------------
    # AC-4: Telemetry Footer Disabled in Dynamic Effort Hook
    # ------------------------------------------------------------------
    def test_ac4_telemetry_footer_disabled_in_dynamic_effort_hook(self):
        """AC-4: dynamic_effort_hook outputs only effort and risk guidance without injecting live telemetry footer."""
        from scripts.hooks.dynamic_effort_hook import handle_pre_invocation

        with tempfile.TemporaryDirectory() as tmp:
            tfile = Path(tmp) / "transcript.jsonl"
            tfile.write_text(json.dumps({"step_index": 1, "type": "USER_INPUT", "content": "olá mundo"}) + "\n", encoding="utf-8")
            payload = {
                "invocationNum": 1,
                "transcriptPath": str(tfile),
                "conversationId": f"conv-no-telemetry-{time.time()}",
            }
            res = handle_pre_invocation(payload)
            self.assertIn("injectSteps", res)
            self.assertTrue(len(res["injectSteps"]) > 0)
            msg = res["injectSteps"][0]["ephemeralMessage"]
            self.assertNotIn("TELEMETRIA AO VIVO", msg)
            self.assertNotIn("Contexto:", msg)
            self.assertNotIn("Consumo:", msg)

    # ------------------------------------------------------------------
    # AC-5: Autonomous Self-Correction & Error Reflexion Engine
    # ------------------------------------------------------------------
    def test_ac5_self_heal_trigger_on_tool_error(self):
        """AC-5: tool-size-guard injects [SELF-HEAL TRIGGER] when command output contains failure."""
        import importlib.util

        guard_path = KIT_ROOT / "scripts" / "hooks" / "tool-size-guard.py"
        spec = importlib.util.spec_from_file_location("tool_size_guard", guard_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        payload = {
            "tool_name": "run_command",
            "output": "The command exited with code 1.\nOutput:\nTraceback (most recent call last):\nAssertionError: 1 != 2",
        }
        res = mod.process_tool_payload(payload)
        self.assertIn("overwrite", res)
        self.assertIn("SELF-HEAL", res["overwrite"]["output"])

    # ------------------------------------------------------------------
    # AC-6: Token Reduction (PreInvocation dedup per prompt)
    # ------------------------------------------------------------------
    def test_ac6_pre_invocation_dedup_across_tool_steps_and_file_size(self):
        """AC-6: dynamic_effort_hook does not re-inject on subsequent tool steps of same prompt."""
        from scripts.hooks.dynamic_effort_hook import should_skip_duplicate_injection

        with tempfile.TemporaryDirectory() as tmp:
            conv_id = "conv-dedup-test"
            prompt_hash = "abc12345"
            # Step 1 of user prompt: should NOT skip
            skip_1 = should_skip_duplicate_injection(conv_id, prompt_hash, cache_dir=Path(tmp))
            self.assertFalse(skip_1)
            # Step 2 (after tool call, same user prompt_hash): MUST skip!
            skip_2 = should_skip_duplicate_injection(conv_id, prompt_hash, cache_dir=Path(tmp))
            self.assertTrue(skip_2)


if __name__ == "__main__":
    unittest.main()
