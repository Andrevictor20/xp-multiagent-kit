# Empirical Evidence & Autonomous Self-Healing Policy

1. **No Verbal Claims:** Never claim "tests pass" without executing the native test command and observing `exit_code: 0`.
2. **Autonomous Self-Healing (`[SELF-HEAL TRIGGER]`):** If any command or test fails during a turn, diagnose the traceback, fix the root cause, and re-run verification before concluding the turn.
3. **Structured Evidence:** Use `agy-evidence run "<cmd>"` to store full logs in `.agents/runtime/evidence/` and render compact tables in `walkthrough.md`.
