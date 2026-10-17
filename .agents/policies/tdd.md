# Strict TDD & Anti-Test-Bypass Policy

1. **RED → GREEN → REFACTOR:** No production code without a failing test first (except L0 trivial changes).
2. **Anti-Test-Bypass (Zero Tolerance):**
   - Zero blind mocks (mock only external I/O boundaries; never mock the unit under test).
   - Zero empty assertions (`assertTrue(True)` is forbidden; assert concrete values/states).
   - Zero skipped/commented/deleted tests to force a green build — fix the root cause.
3. **Surgical Execution:** Run only `tests/test_<module>.py` during iterative development; full suite runs at the release gate.
