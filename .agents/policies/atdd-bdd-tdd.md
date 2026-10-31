# ATDD / BDD / TDD & Multi-Pass EGM Contract Policy

1. **Contract Separation:** Human defines *WHAT* (Acceptance Criteria, Specification by Example tables, Gherkin scenarios). AI implements *HOW* (Acceptance/Integration/Unit tests, production code, refactoring).
2. **Specification Pyramid & 3-Pass EGM Protocol (L2/L3 Mandatory):**
   - **Pass 1 (EGM Spec & Zero-Decision Readiness):** `navigator` authors `SPEC-NNN-ATDD.md` answering all 6 Heilmeier Catechism questions, Alternatives Considered, and a Zero-Decision Implementation Plan (`Create`/`Modify`/`Delete` target files + exact signatures, zero `TODO`/`TBD`/`{{...}}` placeholders). Audited by stateless Goldfish subagents (`design_critic` + `implementation_readiness`) and `xp-goldfish --check-readiness`.
   - **⏸️ Human Stop Gate:** Pause for human approval in single-agent L2/L3 (pre-authorized when multi-agent/EGM execution is requested in prompt).
   - **Automated RED Tests → Production Code (GREEN) → Refactor.**
   - **Pass 2 (EGM Codebase Details & Implementation Completeness):** Stateless Goldfish `codebase_details` review + `xp-goldfish --multipass` verifying zero stubs (`NotImplementedError`), zero workarounds (`as any`, `@ts-ignore`), and `< 500` lines per file.
   - **Pass 3 (EGM Spec-vs-Code Drift & Conformance):** Verify 100% of `AC-N` items have passing tests via `xp-goldfish --multipass` and `agy-conformance`.
3. **Blocking Conformance:** Any AC without a passing test or any failed EGM review pass produces `NON-COMPLIANT` and blocks release.
