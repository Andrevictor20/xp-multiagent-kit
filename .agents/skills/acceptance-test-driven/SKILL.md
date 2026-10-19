---
name: acceptance-test-driven
version: 1.0.0
description: ATDD/BDD with human-AI contract separation and Specification Pyramid.
author: André Victor
license: MIT
tags: [atdd, bdd, gherkin, specifications, clean-code, cursor, claude-code]
compatibility: [cursor, claude-code, codex, gemini-cli, opencode]
entrypoint: SKILL.md
---

# Acceptance Test-Driven Development (ATDD)

Enforce strict separation of responsibilities: the human defines **what** must happen (behavioral contract); the AI implements **how** (production code and automated tests).

## 1. Human-AI Contract Boundary

### Human Zone (What)
- Business intent, requirements, and formal Acceptance Criteria (AC).
- Specification by Example (SbE parameterized tables).
- Explicit specification approval (**Stop Gate**).
- Final review of the Conformance Report.

### AI Zone (How)
- Convert Gherkin scenarios into automated Acceptance Tests (RED).
- Decompose into Integration and Unit Tests (TDD RED).
- Implement minimal production code to pass tests (GREEN).
- Refactor, document, and generate the Conformance Report.

## 2. Specification Pyramid (Mandatory Top-Down Order)

```text
Product Intent -> ATDD/BDD (AC + Gherkin + SbE) -> Integration Tests -> TDD Unit Tests -> Code
```

### Activation by Risk Level
- **L0 (Trivial):** Exempt (typos, docs, minor CSS).
- **L1 (Small):** Informal bullet-point Acceptance Criteria.
- **L2 (Feature):** Formal ATDD mandatory (AC + Gherkin + Stop Gate).
- **L3 (Critical):** Formal ATDD + SbE tables + integrated STRIDE Threat Modeling.

## 3. Machine-Verifiable Acceptance Criteria

### Canonical Format
```markdown
## Acceptance Criteria

### AC-1: [Descriptive Title]
- **Given:** [precondition]
- **When:** [action]
- **Then:** [verifiable expected outcome]
- **Metric:** [status code, payload field, emitted event, latency bound]
```

### Forbidden Anti-Patterns
- ❌ Vague ("System must work properly", "Response must be fast", "Must be secure").
- ✅ Verifiable ("POST /users with duplicate email returns 409 and creates no record").

## 4. Operational ATDD Cycle

1. **`navigator`:** Elicit requirements and draft AC + Gherkin scenarios.
2. **Stop Gate:** Present full spec and wait for explicit human confirmation.
3. **`test-guardian`:** Convert AC into failing Acceptance, Integration, and Unit Tests (RED).
4. **`builder`:** Implement only the logic required to pass tests (GREEN).
5. **`refactor-warden`:** Refactor cleanly while keeping all tests GREEN.
6. **`conformance-tracker`:** Run `agy-conformance` and generate the Conformance Report (N/N covered).
7. **`archivist`:** Persist spec, report, and update `PROJECT_MEMORY.md`.

## 5. Mandatory Conformance Report (L2+)

```markdown
## Conformance Report — SPEC-NNN

| # | Acceptance Criteria | Test File | Status |
|---|---|---|---|
| AC-1 | Unique valid email | `tests/test_user.py::test_duplicate_email` | ✅ GREEN |
| AC-2 | Bcrypt password hash | `tests/test_user.py::test_password_hashed` | ✅ GREEN |

**Result: 2/2 criteria covered and passing.**
```

- **Hard Gate:** Any RED or uncovered AC marks the delivery `NON-COMPLIANT` and **BLOCKS** completion.
