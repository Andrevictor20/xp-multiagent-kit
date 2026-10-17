---
name: release
description: "Pre-release quality gate, Conformance verification, security scan, and Canary/Blue-Green deploy."
---
# Release Workflow

## Flow
Step 0: Read `.agents/memory/PROJECT_MEMORY.md` → `release-gatekeeper` audits full test suite, Conformance Report (`COMPLIANT`), Anti-Test-Bypass, SAST/secrets scan, and context budget (`agy-skill-index audit`) → atomic commit/tag → `shipper` executes Canary/Blue-Green rollout with auto-rollback triggers → `archivist` updates `.agents/memory/PROJECT_MEMORY.md`.
