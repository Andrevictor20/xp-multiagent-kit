# Release & Deployment Policy

## 1. Release Quality Gate
1. **Zero Failing Tests:** Release candidate requires all tests passing without skips or suppressions.
2. **Conformance Verification:** 100% of acceptance criteria have passing test cases with verifiable execution evidence.
3. **Security Gate:** Zero unaddressed High or Critical security vulnerabilities and zero secrets committed.
4. **Clean Diff & Atomic Commit:** Code changes must be reviewed, free of temporary debugging stubs, and committed with structured messages.

## 2. Zero-Downtime Deployment
1. **Rollout Strategies:** Deploy via Canary or Blue-Green phases with health checks active at each step.
2. **Automated Rollback:** Revert deployment automatically if error rates, latency spikes, or health telemetry degrade.

## 3. Structured Agent Handoff
1. **Explicit Delegation Contract:** Multi-agent handoffs must pass structured parameters: `task_id`, `risk_level`, `surfaces`, `spec_path`, `tests.status`, and `files_touched`.
2. **Deterministic Reporting:** All multi-agent workflows report total agent count and roles at start and completion.
