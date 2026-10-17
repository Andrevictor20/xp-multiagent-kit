---
name: feature
description: "Adaptive L2 workflow for new features and API endpoints with ATDD/BDD Specification Pyramid."
---
# Feature Workflow (L2)

## Flow
Step 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) → `navigator` formulates **Acceptance Criteria + Specification by Example + Gherkin** (`SPEC-NNN-ATDD.md`) → **⏸️ Stop Gate: Human Spec Approval** → `test-guardian` writes Acceptance & Unit Tests (RED) → `builder` implements minimal code (GREEN) → `refactor-warden` deslop → `conformance-tracker` generates **Conformance Report** (N/N ACs GREEN) → **`archivist` persists `.agents/memory/PROJECT_MEMORY.md`** → `release-gatekeeper`.

## Rules
- Budget: ≤ 20 turns. Never write production code before human Stop Gate approval and RED test evidence.
- Execute Pre-Response Self-Audit (Goal, Green, Memory) and write all user-facing responses in Portuguese.
