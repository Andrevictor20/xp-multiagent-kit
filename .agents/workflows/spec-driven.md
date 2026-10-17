---
name: spec-driven
description: "Specification-Driven Development (SDD) workflow with executable contracts."
---
# Spec-Driven Development Workflow

## Flow
Step 0: Read `.agents/memory/PROJECT_MEMORY.md` → `navigator` authors formal `SPEC-NNN-ATDD.md` (ACs + SbE tables + Gherkin) → **⏸️ Human Stop Gate** → `test-guardian` binds each AC to parameterized tests (RED) → `builder` satisfies contract (GREEN) → `agy-conformance` verifies 100% AC coverage → `archivist` updates `.agents/memory/PROJECT_MEMORY.md`.
