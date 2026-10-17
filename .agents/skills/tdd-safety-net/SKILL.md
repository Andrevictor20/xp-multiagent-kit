---
name: tdd-safety-net
description: Strict RED-GREEN-REFACTOR cycle, Anti-Test-Bypass, and surgical test execution.
---

# TDD Safety Net & Anti-Test-Bypass

> **Core Principle:** Follow strict Test-Driven Development (`RED -> GREEN -> REFACTOR`). A test has value only if it **fails when production logic is broken** and **verifies real behavior**.

## 1. Fundamental TDD Rules
1. **Never Write Production Code Before RED:** Except for disposable exploratory spikes, always write a failing automated test before implementing production logic.
2. **Behavior Coverage Over Line Count:** Test business contracts, boundaries, and critical paths rather than chasing vanity line coverage.
3. **Adaptive Test Matrix:**
   - *Unit:* Pure functions, algorithms, domain rules.
   - *Integration:* DB queries/transactions, queues, HTTP/gRPC adapters.
   - *Contract:* API/schema compatibility.
   - *Regression:* Reproducing and locking fixed bugs.
   - *Property/Fuzzing:* Mathematical and serialization invariants.

## 2. Anti-Test-Bypass Checklist (Zero Tolerance)
- [ ] **Executes Real Production Code?** Ban mocking the system under test; mock only external third-party I/O.
- [ ] **Asserts Concrete Values?** Ban empty tests, `assert(true)`, or type-only checks without value verification.
- [ ] **Zero Skipped Tests?** Ban `.skip`, `xit`, `@unittest.skip` to hide failing tests.
- [ ] **Zero Deleted/Commented Failing Tests?** Fix the root cause in production code instead of deleting tests.
- [ ] **Real Native Execution Evidence?** Run the test runner and observe output before claiming GREEN.

## 3. Surgical Test Execution (Token Economy)
Save 5,000-20,000 tool tokens per turn:
1. **L0 Fast-Path Exemption:** Pure documentation (`.md`), comments, or declarative config changes are **exempt from running code tests**.
2. **Targeted Module Execution:** Run **only** the test file covering the modified module (`python3 -m unittest tests/test_<module>.py` or `pytest tests/test_<module>.py -k <test>`). Never run the full repository suite for local L1/L2 edits.
3. **Full Suite Reservation:** Run the full test suite only at the final `L3` / `release-gatekeeper` gate or when explicitly requested by the user.
