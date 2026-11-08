# Testing, Quality & Conformance Policy

## 1. Specification & Contract Separation
1. **Contract Separation:** Human defines *WHAT* (Acceptance Criteria, Specification by Example tables, Gherkin scenarios). AI implements *HOW* (Acceptance/Integration/Unit tests, production code, refactoring).
2. **Specification Pyramid:**
   - **Contract Phase:** Author specification answering Heilmeier Catechism dimensions, Alternatives Considered, and a Zero-Decision Implementation Plan (`Create`/`Modify`/`Delete` target files + signatures, zero `TODO`/`TBD` placeholders).
   - **Automated RED Tests → Production Code (GREEN) → Refactor.**
3. **Traceability & Conformance:** Verify 100% of `AC-N` items have corresponding passing tests. Untested AC or failing test yields `NON-COMPLIANT` and blocks release.

## 2. Strict TDD & Anti-Test-Bypass
1. **RED → GREEN → REFACTOR:** No production code without a failing test first (except L0 trivial changes).
2. **Anti-Test-Bypass (Zero Tolerance):**
   - Zero blind mocks: mock only external I/O boundaries (network, clock, disk); never mock the unit under test.
   - Zero empty assertions: assert concrete values, side effects, and states (`assertTrue(True)` is strictly forbidden).
   - Zero test bypasses: never skip (`.skip`), comment out, or delete failing tests to force a green build — isolate and fix the root cause.
3. **Surgical Execution:** Run targeted test modules (`tests/test_<module>.py`) during iterative development; full suite runs at release gates.

## 3. Empirical Evidence & Anti-Regression
1. **No Verbal Claims:** Never claim "tests pass" or that a bug is fixed without executing native test commands and observing `exit_code: 0`.
2. **Regression Shield:** For any fixed bug, create or update an automated regression test reproducer before closing the task to prevent regressions.
3. **Autonomous Self-Healing:** If any command or test fails, diagnose traceback/logs, isolate the root cause, fix code, and re-verify before concluding turn. Record failed attempts in Dead-Ends memory.
4. **Structured Evidence:** Record deterministic execution artifacts in `.agents/runtime/` with concrete logs and outputs.
