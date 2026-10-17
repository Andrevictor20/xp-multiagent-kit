---
name: critical
description: "High-assurance L3 workflow for auth, payments, cryptography, and destructive migrations."
---
# Critical Change Workflow (L3)

## Flow
Step 0: Read `.agents/memory/PROJECT_MEMORY.md` → `navigator` + `sentinel` draft Threat Model (STRIDE) + ATDD Spec (`SPEC-NNN-ATDD.md`) → **⏸️ Stop Gate: Human Approval + High Effort Confirmation** → `test-guardian` creates security/acceptance/unit tests (RED) → `builder` implements (GREEN) → `sentinel` security review → `conformance-tracker` full Conformance Report → `archivist` updates `.agents/memory/PROJECT_MEMORY.md` → `release-gatekeeper` (full regression suite) → `shipper` Zero-Downtime plan.

## Rules
- Atomic checkpoints required. High/Critical vulnerabilities block release. Reply to the user in Portuguese.
