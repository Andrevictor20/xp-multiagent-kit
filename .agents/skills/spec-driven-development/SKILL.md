---
name: spec-driven-development
description: Formal Specification-Driven Development (SDD) as single source of truth.
---

# Spec-Driven Development (SDD)

Treat the versioned, human-approved specification (`SPEC-NNN-ATDD.md`) as the single source of truth and production code as its verifiable derivative.

> **Specification Pyramid Integration:** Works alongside `acceptance-test-driven`, `specification-by-example`, `conformance-tracker`, and `.agents/policies/atdd-bdd-tdd.md`.

## 1. Core SDD Principles
1. **Spec as Source of Truth:** Generate zero production code before the structured Markdown specification is approved.
2. **Machine-Testable Gherkin ACs:** Express every requirement as verifiable `Given / When / Then` scenarios.
3. **Specification by Example (SbE):** Attach parameterized example tables for multi-condition business rules.
4. **Bidirectional Sync:** Tests mirror spec scenarios 1:1. When the spec changes, update tests first (**RED**), then update production code (**GREEN**).
5. **Living Specs:** Store specs in `.agents/specs/` or `docs/specs/` and keep them synchronized.

## 2. Canonical `SPEC-NNN-ATDD.md` Structure
1. **Business Context & Problem Statement**
2. **Acceptance Criteria (ATDD):** `Given / When / Then / Metric`
3. **Specification by Example (SbE):** Parameterized tables covering happy paths, boundaries, and errors
4. **Gherkin BDD Scenarios:** `Scenario` and `Scenario Outline`
5. **Domain Contract & Interfaces:** Schemas, endpoints, events
6. **Invariants & Properties:** Rules that must never be violated
7. **Conformance Tracking:** Populated via `agy-conformance` post-implementation

## 3. Agent Operational Cycle
1. **`navigator`:** Drafts `SPEC-NNN-ATDD.md` (AC + SbE + Gherkin).
2. **Stop Gate:** Pauses for explicit human approval.
3. **`test-guardian`:** Converts AC and SbE rows into failing Acceptance, Integration, and Unit Tests (**RED**).
4. **`builder`:** Implements minimal production code to pass all spec scenarios (**GREEN**).
5. **`conformance-tracker`:** Runs `agy-conformance` to verify N/N compliance.
6. **`archivist`:** Archives spec and updates `PROJECT_MEMORY.md`.
