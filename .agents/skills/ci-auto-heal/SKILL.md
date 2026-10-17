---
name: ci-auto-heal
description: Autonomous CI/CD failure diagnosis and root-cause self-healing (max 3 iterations).
---

# CI/CD Auto-Heal & Self-Correction

Autonomously monitor local and remote CI pipelines (GitHub Actions), isolate failure logs with minimal token cost, and fix root causes.

## 1. Activation Triggers
- After `git push`, release, or deployment workflow triggers.
- Failures detected by `agy-ci-heal --status` or `gh run list`.
- Invocations from `/release`, `/incident`, or `/bugfix` workflows.

## 2. 5-Step Operational Protocol

### Step 1: Surgical Failure Diagnosis
Extract only the failing log block (95% token reduction; never run unfiltered `gh run view --log`):
```bash
agy-ci-heal --diagnose-run <run-id>
# or: agy-git-ops ci-log <run-id>
# or: gh run view <run-id> --log-failed | agy-compact --ci
```

### Step 2: 4-Phase Root-Cause Investigation
1. **Comprehension:** Identify exact failing file, line, dependency, or env var.
2. **Isolation:** Distinguish transient infra/network timeouts from deterministic failures (tests, types, migrations, lint).
3. **Local Reproduction:** Run the targeted failing check locally (`python3 -m unittest ...`, `npm test`, `pytest`).
4. **Source Fix:** Fix the root cause in production code or config.
   > [!CAUTION]
   > **Zero Bypass Tolerance:** Never silence linters (`eslint-disable`), mask types (`as any`, `@ts-ignore`), or skip tests (`test.skip`) to force green CI.

### Step 3: Strict Local Verification (TDD GREEN)
Confirm the targeted test and linter pass locally before pushing.

### Step 4: Atomic Commit & Re-Trigger
```bash
git commit -m "fix(ci): <concise fix> [run #<run-id>] (auto-heal [iter <N>/3])"
git push origin <branch>
```

### Step 5: 3-Fix Circuit Breaker (`[L-003]`)
- Cap auto-heal loops at **maximum 3 consecutive iterations**.
- If iteration 3 still fails, **STOP immediately**, record diagnostics, and escalate to the user.
