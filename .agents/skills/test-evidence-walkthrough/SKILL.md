---
name: test-evidence-walkthrough
description: Native test execution evidence recording and verification by risk level.
---

# Test Evidence Walkthrough

Verbal claims like *"tests passed"* are rejected. Every code change must provide verifiable execution evidence proportional to its risk level (`agy-evidence run` / `agy-evidence render`).

## Evidence Levels by Risk
- **L0 (Trivial — docs, typos, minor CSS):** Exempt from code test execution.
- **L1 (Small — isolated fix/refactor):** Targeted test command + exit code + concise summary line.
- **L2 (Feature — new module/API):** Targeted test execution + Conformance Report table (`walkthrough.md` receives the summary table; full raw log stays in `.agents/runtime/evidence/`).
- **L3 (Critical — auth, payments, migrations, release):** Full test suite + SAST/SCA gate + CI artifact log.
- **L4 (Production Release):** Post-deploy staging/production health check and RED telemetry verification.

Never advance from RED to GREEN or mark a task complete without the required evidence level.
