---
name: critical
description: "High-assurance L3 workflow for auth, payments, cryptography, and destructive migrations with STRIDE and 3-Pass EGM Goldfish Reviews."
---
# Critical Change Workflow (L3 — Maximum Assurance & Completeness)

## Flow
Step 0: Read `.agents/memory/PROJECT_MEMORY.md` → `navigator` + `sentinel` draft Threat Model (STRIDE) + Exhaustive ATDD Spec (`SPEC-NNN-ATDD.md` with Heilmeier Catechism, Alternatives, and Zero-Decision Plan) → **🐟 EGM Pass 1 (Stateless Goldfish Hostile Design Critique & Implementation Readiness Review)** → **⏸️ Stop Gate: Human Approval + High Effort Confirmation** → `test-guardian` creates security/acceptance/unit tests (RED) → `builder` implements 100% complete code (GREEN) → **🐟 EGM Pass 2 (`sentinel` security review + Goldfish `codebase_details` audit)** → **🐟 EGM Pass 3 (`conformance-tracker` + `xp-goldfish --multipass` full Conformance & Drift Report)** → `archivist` updates `.agents/memory/PROJECT_MEMORY.md` → `release-gatekeeper` (full regression suite) → `shipper` Zero-Downtime plan.

## Rules
- **Completeness Over Speed:** Zero turn limits; atomic checkpoints required. High/Critical vulnerabilities or failed EGM passes block release. Reply to the user in Portuguese.
