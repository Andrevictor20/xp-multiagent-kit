# ATDD / BDD / TDD Contract Separation Policy

1. **Contract Separation:** Human defines *WHAT* (Acceptance Criteria, Specification by Example tables, Gherkin scenarios). AI implements *HOW* (Acceptance/Integration/Unit tests, production code, refactoring).
2. **Specification Pyramid (L2/L3 Mandatory):** Product Intent → ATDD Acceptance Criteria & SbE (`SPEC-NNN-ATDD.md`) → **⏸️ Human Stop Gate** → Automated RED Tests → Production Code (GREEN) → Conformance Report (`agy-conformance`).
3. **Anti-Self-Test Rule:** AI must never author both Acceptance Criteria and tests without human Stop Gate confirmation in L2/L3, UNLESS explicit multi-agent execution was requested in the initial prompt (pre-authorized contract). In multi-agent mode, the orchestrator dispatches `navigator` and `test-guardian` immediately in Turn 1 without stalling.
4. **Blocking Conformance:** Any AC without a passing test produces `NON-COMPLIANT` and blocks release.
