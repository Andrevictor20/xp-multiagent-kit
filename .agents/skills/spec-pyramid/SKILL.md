---
name: spec-pyramid
description: Specification Pyramid combining ATDD/BDD, Spec-Driven Development (SDD), Specification by Example (SbE), and pair navigation.
---

# Specification Pyramid (`spec-pyramid`)

Consolidates the disciplines of **ATDD/BDD**, **SDD**, **SbE**, and **Pair Navigation** into a single concise source of truth.

## 1. Contract Separation: WHAT vs HOW
- **Human defines WHAT:** Acceptance Criteria (ACs), Specification by Example (SbE) tables, and business scenarios.
- **AI implements HOW:** Deterministic RED unit tests, minimal GREEN implementation, and regression-free refactoring.
- **Anti-Self-Test Rule:** The agent never drafts the specification and tests without submitting the spec to the Human Stop Gate (`approve_spec`).

## 2. Specification by Example (SbE)
- Ambiguous business logic MUST be expressed through concrete tables with explicit inputs and expected outputs:
  - Happy path scenarios.
  - Boundary cases (zero, null, empty, extreme limits).
  - Error conditions and handled exceptions.

## 3. SDD Structure (Specification-Driven Development)
- Every specification in `.agents/specs/` must contain:
  1. **Goal & Context:** The actual problem solved and who is affected.
  2. **Rejected Alternatives:** At least two discarded alternatives with technical justifications.
  3. **Acceptance Criteria (ACs):** Measurable, testable, and with direct traceability to tests.
  4. **Scope Constraints:** Permitted files for alteration and strictly prohibited changes.

## 4. Pair Navigation & Anti-Over-Engineering
- Implement the simplest solution satisfying the criteria.
- No premature abstractions or speculative features (YAGNI).
- Halt on the second consecutive identical failure (Circuit Breaker).
