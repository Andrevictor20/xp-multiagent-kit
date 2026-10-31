---
name: feature
description: "Completeness-First L2 workflow for new features, APIs, and architectural planning with ATDD/BDD Specification Pyramid and 3-Pass EGM Goldfish Reviews."
---
# Feature Workflow (L2 — Completeness Over Speed)

## Flow
Step 0: Fast Context Bootstrap (`.agents/memory/PROJECT_MEMORY.md`) → `navigator` formulates **Heilmeier Catechism + Alternatives Considered + Zero-Decision Implementation Plan + Acceptance Criteria + SbE + Gherkin** (`SPEC-NNN-ATDD.md`) → **🐟 EGM Pass 1 (Stateless Goldfish Spec & Implementation Readiness Review + `xp-goldfish --check-readiness`)** → **⏸️ Stop Gate: Human Spec Approval** (pre-authorized if multi-agent/EGM requested in prompt) → **Dynamic Multi-Agent Dispatch** (`.agents/active-mission.json` + `invoke_subagent` or `agy-orchestrate`) → `test-guardian` writes Acceptance & Unit Tests (RED) → `builder` implements 100% complete code (GREEN) → **🐟 EGM Pass 2 (`refactor-warden` + Goldfish `codebase_details` review + deslop)** → **🐟 EGM Pass 3 (`conformance-tracker` + `xp-goldfish --multipass` verifying 3/3 passes & N/N ACs GREEN)** → **`archivist` persists `.agents/memory/PROJECT_MEMORY.md`** → `release-gatekeeper`.

## Rules
- **Completeness Over Speed:** Never truncate planning or implementation to save time or turns. Deliver 100% of planned items with zero `TODO`/`TBD` placeholders.
- Never write production code before RED test evidence. If multi-agent/EGM execution was requested in the initial prompt, Stop Gate is pre-authorized: dispatch subagents in Turn 1, display initial roster, and provide final Multi-Agent Execution Report.
- Execute 5-Point Pre-Response Self-Audit (Completeness, 3-Pass EGM, Green, Multi-Agent Roster, Memory) and write all user-facing responses in Portuguese.
