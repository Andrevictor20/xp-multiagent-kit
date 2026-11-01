#!/usr/bin/env python3
"""
tests/test_egm_completeness_engine.py
TDD Acceptance & Unit Tests for SPEC-005:
Motor de Completude Exaustiva & Revisão Multi-Pass EGM (Elephant-Goldfish Model).
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

KIT_ROOT = Path(__file__).resolve().parent.parent


class TestEgmCompletenessEngine(unittest.TestCase):
    """Tests covering AC-1 through AC-6 of SPEC-005."""

    # ------------------------------------------------------------------
    # AC-1: Zero-Decision Implementation Readiness, Alternatives & Placeholders
    # ------------------------------------------------------------------
    def test_ac1_zero_decision_and_placeholder_validation(self):
        from scripts.goldfish_review import (
            check_placeholders,
            validate_implementation_readiness,
        )

        # Notice: "criar uma API" in prose must NOT false-trigger zero_decision_target_files
        incomplete_spec = """
        # SPEC-999: Teste Incompleto
        ## 1. Contexto
        Objetivo: criar uma API nova.
        TODO: definir depois {{placeholder}}
        TBD na próxima sprint.
        """
        placeholders = check_placeholders(incomplete_spec)
        self.assertGreaterEqual(len(placeholders), 3)

        readiness_bad = validate_implementation_readiness(incomplete_spec)
        self.assertFalse(readiness_bad["compliant"])
        self.assertIn("alternatives_considered", readiness_bad["missing"])
        self.assertIn("zero_decision_target_files", readiness_bad["missing"])
        self.assertIn("acceptance_criteria", readiness_bad["missing"])
        self.assertIn("no_placeholders", readiness_bad["missing"])

        spec_005 = (KIT_ROOT / ".agents" / "specs" / "SPEC-005-EGM-COMPLETENESS-ENGINE.md").read_text(encoding="utf-8")
        self.assertEqual(check_placeholders(spec_005), [])
        readiness_ok = validate_implementation_readiness(spec_005)
        self.assertTrue(readiness_ok["compliant"], f"Missing readiness items: {readiness_ok.get('missing')}")
        self.assertEqual(readiness_ok["score"], 100.0)

    # ------------------------------------------------------------------
    # AC-2: Multi-Pass EGM Review Engine (3 Passes: Spec, Code, Drift & CLI)
    # ------------------------------------------------------------------
    def test_ac2_multipass_egm_review_engine(self):
        from scripts.goldfish_review import (
            main as goldfish_main,
            run_multipass_egm_review,
        )

        spec_005_path = KIT_ROOT / ".agents" / "specs" / "SPEC-005-EGM-COMPLETENESS-ENGINE.md"
        code_files = [
            KIT_ROOT / "scripts" / "goldfish_review.py",
            KIT_ROOT / "scripts" / "agy_effort_router.py",
            KIT_ROOT / "scripts" / "kit_constants.py",
            KIT_ROOT / "scripts" / "antigravity_multiagent.py",
        ]
        test_files = [Path(__file__).resolve()]

        report = run_multipass_egm_review(
            spec_path=spec_005_path,
            code_paths=code_files,
            test_paths=test_files,
        )
        self.assertEqual(report["passes_completed"], 3)
        self.assertTrue(report["pass1_spec"]["compliant"], f"Pass 1 failed: {report['pass1_spec']}")
        self.assertTrue(report["pass2_code"]["compliant"], f"Pass 2 failed: {report['pass2_code']}")
        self.assertTrue(report["pass3_drift"]["compliant"], f"Pass 3 failed: {report['pass3_drift']}")
        self.assertTrue(report["overall_compliant"])

        # CLI flags: --check-readiness, --check-code, --multipass
        self.assertEqual(goldfish_main(["--check-readiness", str(spec_005_path)]), 0)
        self.assertEqual(goldfish_main(["--check-code", "--code-files", str(code_files[0])]), 0)
        self.assertEqual(
            goldfish_main([
                "--multipass", str(spec_005_path),
                "--code-files", str(code_files[0]),
                "--test-files", str(test_files[0]),
            ]),
            0,
        )

        # Negative test: inline TODO, NotImplementedError, type suppression, missing file, and missing AC test
        with tempfile.TemporaryDirectory() as tmp:
            bad_code = Path(tmp) / "bad_mod.py"
            bad_code.write_text(
                "def foo():\n"
                "    x = 1  # TODO: fix inline later\n"
                "    # @" + "ts-ignore\n"
                "    raise NotImplementedError()\n",
                encoding="utf-8",
            )
            missing_code = Path(tmp) / "non_existent.py"
            bad_test = Path(tmp) / "test_bad.py"
            bad_test.write_text("def test_ac1_only():\n    assert True\n", encoding="utf-8")

            bad_report = run_multipass_egm_review(
                spec_path=spec_005_path,
                code_paths=[bad_code, missing_code],
                test_paths=[bad_test],
            )
            self.assertFalse(bad_report["pass2_code"]["compliant"])
            self.assertGreaterEqual(len(bad_report["pass2_code"]["findings"]), 4)
            self.assertEqual(len(bad_report["pass2_code"]["missing_files"]), 1)
            self.assertFalse(bad_report["pass3_drift"]["compliant"])
            self.assertFalse(bad_report["overall_compliant"])
            self.assertEqual(goldfish_main(["--check-code", "--code-files", str(bad_code)]), 2)

    # ------------------------------------------------------------------
    # AC-3: Completeness Priority & HIGH Effort on Planning / EGM without Turn Throttling
    # ------------------------------------------------------------------
    def test_ac3_planning_effort_high_and_no_turn_throttle(self):
        from scripts.agy_effort_router import (
            EFFORT_HIGH,
            LEVEL_L2_FEATURE,
            classify_task_effort,
            get_canonical_model_for_task,
        )

        user_prompt = (
            "Melhorar o kit multiagent\n"
            "- O sistema não está completando planejamentos de forma completa\n"
            "- o ideal é fazer o sistema fazer múltiplas revisões de tudo que está sendo implementado e usar mais o EGM para isso\n"
            "- foco em entregar as features e planejamento não importando quanto tempo demore"
        )
        # Even in a long session (turns >= 10) with local preflight alerts, effort must remain HIGH (unthrottled)
        with patch(
            "scripts.agy_effort_router._local_preflight",
            return_value={"alerts": ["CRITICAL: 10 turns elapsed"], "turns": 10},
        ):
            decision = classify_task_effort(
                prompt=user_prompt,
                conversation_context={"session_id": "long-session-01"},
            )
            self.assertEqual(decision.effort, EFFORT_HIGH)
            self.assertIn("L2", decision.risk_level)
            self.assertFalse(decision.throttled)

        # L2 planning must also use HIGH effort (never downgraded to medium)
        _, plan_effort = get_canonical_model_for_task(LEVEL_L2_FEATURE, is_planning=True)
        self.assertEqual(plan_effort, EFFORT_HIGH)

    # ------------------------------------------------------------------
    # AC-4: goldfish-spec-review & spec-driven-development in CORE_SKILLS
    # ------------------------------------------------------------------
    def test_ac4_goldfish_in_core_skills(self):
        from scripts.skill_profiles import CORE_SKILLS, SKILL_DESCRIPTIONS

        self.assertIn("goldfish-spec-review", CORE_SKILLS)
        self.assertIn("spec-driven-development", CORE_SKILLS)
        self.assertIn("goldfish-spec-review", SKILL_DESCRIPTIONS)

    # ------------------------------------------------------------------
    # AC-5: Governance Constants, Context Budget & Multi-Pass EGM in Mission Engine
    # ------------------------------------------------------------------
    def test_ac5_governance_and_mission_egm_passes(self):
        from scripts.antigravity_multiagent import AntigravityMissionEngine
        from scripts.kit_constants import (
            BASE_CONTEXT_MAX_BYTES,
            EGM_MIN_REVIEW_PASSES,
            ZERO_DECISION_PLANNING_REQUIRED,
        )
        from scripts.skill_index import audit_context_budget

        self.assertLessEqual(BASE_CONTEXT_MAX_BYTES, 8000)
        self.assertGreaterEqual(EGM_MIN_REVIEW_PASSES, 2)
        self.assertTrue(ZERO_DECISION_PLANNING_REQUIRED)

        agents_md = (KIT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("EGM", agents_md)
        self.assertLessEqual(len(agents_md.encode("utf-8")), 6000)

        budget_report = audit_context_budget(KIT_ROOT)
        self.assertFalse(
            budget_report["blocking"],
            f"Context budget exceeded: {budget_report['findings']}",
        )

        with tempfile.TemporaryDirectory() as tmp:
            engine = AntigravityMissionEngine(project_dir=Path(tmp))
            manifest = {
                "mission_id": "mission-egm-01",
                "feature_name": "Feature Com Multi-Pass EGM",
                "egm_review_passes": 3,
                "tasks": [
                    {
                        "task_id": "t1-spec-and-code",
                        "subagent": "builder",
                        "model": "gemini-3.8-flash",
                        "effort": "high",
                        "execution_group": 1,
                        "allowed_paths": ["scripts/"],
                        "objective": "Implementar feature completa com 3 revisões EGM",
                        "verification_cmd": "python3 -c 'print(1)'",
                    }
                ],
            }
            res = engine.run_mission(manifest)
            self.assertTrue(res["success"])
            self.assertEqual(res.get("egm_review_passes"), 3)
            report_text = (Path(tmp) / ".agents" / "mission-report.md").read_text(encoding="utf-8")
            self.assertIn("EGM", report_text)

    # ------------------------------------------------------------------
    # AC-6: Global CLI Binaries xp-goldfish & agy-goldfish
    # ------------------------------------------------------------------
    def test_ac6_goldfish_cli_binaries_registered(self):
        from scripts.kit_installer import KitDoctor
        from scripts.windows_support import SHIM_COMMANDS

        self.assertIn("xp-goldfish", SHIM_COMMANDS)
        self.assertIn("agy-goldfish", SHIM_COMMANDS)
        self.assertEqual(SHIM_COMMANDS["xp-goldfish"], "scripts/goldfish_review.py")
        self.assertEqual(SHIM_COMMANDS["agy-goldfish"], "scripts/goldfish_review.py")

        diag = KitDoctor(kit_dir=KIT_ROOT).run_diagnostics()
        self.assertIn("xp-goldfish", diag["installed_bins"])
        self.assertIn("agy-goldfish", diag["installed_bins"])

    # ------------------------------------------------------------------
    # AC-9: EGM 2 Personas & LLM Review Triggers
    # ------------------------------------------------------------------
    def test_ac9_egm_two_personas_and_llm_triggers(self):
        from scripts.goldfish_review import should_trigger_llm_review
        from unittest.mock import patch

        personas_dir = KIT_ROOT / ".agents" / "skills" / "goldfish-spec-review" / "personas"
        persona_files = list(personas_dir.glob("*.md"))
        self.assertEqual(len(persona_files), 2)
        persona_names = {p.name for p in persona_files}
        self.assertEqual(persona_names, {"spec_reviewer.md", "code_reviewer.md"})

        for pf in persona_files:
            self.assertLessEqual(len(pf.read_bytes()), 2048, f"{pf.name} excede 2 KB")

        # L3 always triggers single review
        trig, reason = should_trigger_llm_review("L3")
        self.assertTrue(trig)
        self.assertEqual(reason, "L3_single")

        # L2 triggers on warning or touching > 8 files
        trig, _ = should_trigger_llm_review("L2", {"compliant": True, "touches_more_than_8_files": False})
        self.assertFalse(trig)
        trig, reason = should_trigger_llm_review("L2", {"compliant": False})
        self.assertTrue(trig)
        self.assertEqual(reason, "L2_on_warning")
        trig, reason = should_trigger_llm_review("L2", {"compliant": True, "touches_more_than_8_files": True})
        self.assertTrue(trig)
        self.assertEqual(reason, "L2_touches_more_than_8_files")

        # Environment rollback overrides
        with patch.dict(os.environ, {"XP_EGM_LLM": "always"}):
            self.assertTrue(should_trigger_llm_review("L1")[0])
        with patch.dict(os.environ, {"XP_EGM_LLM": "off"}):
            self.assertFalse(should_trigger_llm_review("L3")[0])


if __name__ == "__main__":
    unittest.main()
