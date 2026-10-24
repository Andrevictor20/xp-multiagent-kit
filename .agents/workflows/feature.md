---
name: feature
description: "Adaptive L2 workflow for new features and API endpoints with ATDD/BDD Specification Pyramid."
---
# Feature Workflow (L2)

## Flow
Step 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) → `navigator` formulates **Acceptance Criteria + Specification by Example + Gherkin** (`SPEC-NNN-ATDD.md`) → **⏸️ Stop Gate: Human Spec Approval** → **Dynamic Multi-Agent Dispatch** (Optional parallel Boss-Worker execution via `.agents/active-mission.json` + `invoke_subagent` or `agy-orchestrate`) → `test-guardian` writes Acceptance & Unit Tests (RED) → `builder` implements minimal code (GREEN) → `refactor-warden` deslop → `conformance-tracker` generates **Conformance Report** (N/N ACs GREEN) → **`archivist` persists `.agents/memory/PROJECT_MEMORY.md`** → `release-gatekeeper`.

## Rules
- Budget: ≤ 20 turns. Never write production code before human Stop Gate approval and RED test evidence. If multi-agent execution was requested in the initial prompt, Stop Gate is pre-authorized: dispatch subagents in Turn 1, display initial roster, and provide final Multi-Agent Execution Report.
- Execute 4-Point Pre-Response Self-Audit (Goal, Green, Multi-Agent Roster, Memory) and write all user-facing responses in Portuguese.
