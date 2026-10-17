---
name: test-harness-bootstrap
description: Moment-Zero test harness setup: runner, directory layout, CI step, smoke test.
---

# Test Harness Bootstrap

TDD requires a working test harness before the first feature is written. Run this skill **once at project initialization** (`genesis`) or when onboarding a legacy repo that lacks automated tests.

## 1. Definition of "Harness Ready"
1. **Installed & Configured Runner:** Stack-appropriate framework (`pytest`/`unittest`, `vitest`/`jest`, `go test`, `cargo test`, `rspec`).
2. **Mirrored Test Directory Layout:** `tests/` or `spec/` mirroring `src/` or `app/`.
3. **Single Command Execution:** Documented 1-liner (`npm test`, `pytest`, `python3 -m unittest`) in README and living docs.
4. **Automated CI Pipeline Step:** Configured to run on every commit/PR (`ci-security-gate`).
5. **Passing Smoke Test:** At least one real test executing and passing end-to-end (proving the runner works, not an empty placeholder).
6. **Parallel Execution Enabled:** Configured for fast parallel runs so the suite stays fast as the codebase grows.

## 2. What NOT to Do During Bootstrap
- Do not write feature-specific test suites here (that belongs to `test-guardian` per task).
- Never leave the CI test step commented out or manual "for later".

## Exit Checklist
- [ ] Test framework installed and configured?
- [ ] Test directory structure created?
- [ ] Single test command documented?
- [ ] Automated CI test job active on every commit?
- [ ] At least 1 real smoke test passing?
- [ ] Committed as an atomic commit (`chore(test): bootstrap test harness`)?
