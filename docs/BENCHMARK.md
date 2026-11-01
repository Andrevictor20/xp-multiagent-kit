# Efficiency Benchmark — XP Multi-Agent Kit v4 vs v3.9

Execution guide for the 4 reference tasks for empirical measurement of token usage and gates.

## 1. Reference Tasks (`tests/evals/tasks.jsonl`)
- `task_l0_typo`: Documentation/typo (L0, chore).
- `task_l1_bugfix`: Regression with RED unit test (L1, fix).
- `task_l2_feature`: Specification + SbE + TDD implementation (L2, feature).
- `task_l3_auth`: Token validation with STRIDE and mitigation (L3, migration).

## 2. Running the Benchmark
Run the tasks on baseline (`v3.9.2-baseline`) and current version (`v4.0.0`):

```bash
# 1. Run evaluation on baseline (generates baseline.jsonl with results)
git checkout v3.9.2-baseline
# Run all 4 tasks and save receipts to /tmp/eval_v39.jsonl

# 2. Run evaluation on v4.0.0 Thin Harness (generates target.jsonl)
git checkout refactor/thin-harness
# Run all 4 tasks with the Thin Harness and save to /tmp/eval_v40.jsonl

# 3. Compare canonical metrics
xp kit eval compare /tmp/eval_v39.jsonl /tmp/eval_v40.jsonl
```

## 3. Evaluated Metrics
- **Primary:** Total tokens / Tasks with gate PASS (cost per accepted task).
- **Secondary:** First-gate PASS rate, repeated failures (`signature` ≥ 2), human interventions, L1+ sessions without verdict, average turns, and total execution time (s).
