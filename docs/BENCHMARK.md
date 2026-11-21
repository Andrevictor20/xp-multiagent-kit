# Hybrid A/B Benchmark — XP Multi-Agent Kit v4

Reproducible evaluation comparing repositories **without the kit (`baseline`)** vs **with the kit (`kit`)** across two complementary tracks.

## 1. Track A — Real LLM-in-the-Loop (`benchmark/llm_runner.py`)
Runs identical prompts on paired Git sandboxes (isolating global `~/.gemini/` hooks/skills in `baseline`) using `agy`, `claude`, `codex`, or `gemini`, followed by hidden `unittest` verification and independent oracles:

```bash
# Dry-run pipeline validation (zero LLM cost)
python3 benchmark/llm_runner.py --dry-run

# Full 6-task L0-L3 paired benchmark
python3 benchmark/llm_runner.py --runner agy --model gemini-3.8-flash-low --runs 1
python3 benchmark/llm_aggregate.py
python3 scripts/xp kit eval compare benchmark/results/llm_baseline.jsonl benchmark/results/llm_kit.jsonl
```

### Measured Results (`agy` / `gemini-3.8-flash-low`, `T01`–`T06`)
- **Resolution:** `6/6` (`100.0%`) in both arms; `5/5` `L1+` tasks passed `xp gate check` with RED→GREEN evidence (`0` unverified sessions vs `5` in baseline).
- **Total Tokens (`input + output`):** `177,059` (`baseline`) → `170,642` (`kit`) (**−3.6%**; median **−21.9%**).
- **Real Multi-File Feature A/B (`Coupon` + `pricing.py`, `gemini-3.8-flash-medium`):** `80,259` (`baseline`, `214.8s`) → `63,521` (`kit`, `119.2s`) (**−20.9% tokens**, **−66.2% thinking tokens**, **−44.5% time**).

See [benchmark/results/LLM_RESULTS.md](../benchmark/results/LLM_RESULTS.md).

## 2. Track B — Deterministic Harness & Token Optimizers (`benchmark/runner.py`)
Runs 16 paired defect/benign scenarios plus mechanical overhead and token optimizer measurements:

```bash
python3 benchmark/runner.py
python3 benchmark/overhead.py
python3 benchmark/aggregate.py
python3 scripts/xp kit eval compare benchmark/results/baseline.jsonl benchmark/results/kit.jsonl
```

- **Defect Recall:** `10/10` (`100.0%`) vs `1/10` (`10.0%`) baseline; `0/6` false positives.
- **Token Optimizers:** `context_compactor` **−61.9%**, `repo_map` **−83.3%**, JIT `xp context` **−89.4%**, fixed base context `5,005 B` (`≤ 8,000 B` cap).

See [benchmark/results/RESULTS.md](../benchmark/results/RESULTS.md).
