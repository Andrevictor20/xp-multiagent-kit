---
name: spec-driven
description: "Specification-Driven Development (SDD) workflow with executable contracts and 3-Pass EGM Goldfish Verification."
---
# Spec-Driven Development Workflow (EGM Enhanced)

## Flow
Step 0: Read `.agents/memory/PROJECT_MEMORY.md` → `navigator` authors formal `SPEC-NNN-ATDD.md` (Heilmeier Catechism + Alternatives + Zero-Decision Target Files + ACs + SbE tables + Gherkin) → **🐟 EGM Pass 1 (Stateless Goldfish Review: `design_critic` + `implementation_readiness` + `xp-goldfish --check-readiness`)** → **⏸️ Human Stop Gate** → `test-guardian` binds each AC to parameterized tests (RED) → `builder` satisfies 100% of contract without stubs (GREEN) → **🐟 EGM Pass 2 & 3 (`xp-goldfish --multipass` + `agy-conformance` verifying 100% AC coverage & zero spec drift)** → `archivist` updates `.agents/memory/PROJECT_MEMORY.md`.
