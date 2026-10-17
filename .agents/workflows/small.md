---
name: small
description: "Streamlined L1 workflow for isolated refactors and small adjustments."
---
# Small Change Workflow (L1)

## Flow
Step 0: Read `.agents/memory/PROJECT_MEMORY.md` → `navigator` drafts informal ACs (bullets) → `builder` writes failing test (RED) + minimal implementation (GREEN) + cleanup (REFACTOR) → 1-line conformance summary → `archivist` updates `.agents/memory/PROJECT_MEMORY.md` → `release-gatekeeper`.

## Rules
- Budget: ≤ 8 turns. Run only the affected module's test file.
- Execute Pre-Response Self-Audit (Goal, Green, Memory) and reply in Portuguese.
