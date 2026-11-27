# XP Multi-Agent Kit v4.0.0 — Thin Harness

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Version: 4.0.0](https://img.shields.io/badge/version-4.0.0-brightgreen.svg)](#)
[![TDD: Strict RED-GREEN](https://img.shields.io/badge/TDD-strict-success.svg)](#4-engineering-guarantees)

Deterministic governance Thin Harness for AI agent pair-programming (**Antigravity**, **OpenCode**, **Cursor**, **Codex**, **Qoder**, and **Claude**). Zero external Python dependencies (100% stdlib), replacing redundant prose with verifiable code mechanisms and restricting the fixed base context to ≤ 8 KB.

---

## 1. 4-Layer Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. HARNESS: PreTool Guard + policy.yaml + kit_events.jsonl (security)  │
├────────────────────────────────────────────────────────────────────────┤
│ 2. LOOP: xp contract (run.json) + xp gate (10 steps) + EGM (2 personas)│
├────────────────────────────────────────────────────────────────────────┤
│ 3. GRAPH: workflow.yaml (9 flows) + xp flow (whiteboard/loops/parallel)│
├────────────────────────────────────────────────────────────────────────┤
│ 4. CORE: 6 core agents + 24 skills + packs (.agents/packs/)            │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Harness (Outer Layer):** Deterministic interception via hooks (`pre_tool_guard`, `smart_tool_optimizer`, `tool-size-guard`), permission tiers in `policy.yaml` (`auto|review|human`), and structured telemetry in `.agents/runtime/events.jsonl`.
2. **Loop (Focused Execution):** Structured contract in `run.json` (`xp contract`), 10-step delivery gate (`xp gate`), and EGM audit with 2 personas (`spec_reviewer`, `code_reviewer`).
3. **Graph (Workflow Engine v2):** State machine driven by `workflow.yaml` (`xp flow`) supporting:
   - **State Whiteboard (`output_key` + `{key}`):** Passes structured outputs deterministically between nodes (`xp flow state`).
   - **Deterministic Loops (`on_fail: retry` / `reopen:<node>`):** Automatic writer-critic refinement cycles with circuit breaker (`max_retries`).
   - **Concurrent Execution (`parallel:`):** Runs independent verification branches concurrently via stdlib `ThreadPoolExecutor`.
   - **RED Test Freezing:** SHA-256 tamper protection on RED unit tests.
4. **Core (Specialists):** 6 core agents (`orchestrator`, `builder`, `reviewer`, `sentinel`, `designer`, `shipper`) and 24 on-demand skills with concise frontmatter descriptions (≤ 110 chars enforced by linter), plus optional bundles in `.agents/packs/`.

---

## 2. Multi-Repository Scoped Memory (`user:` + `repo:` + `session:`)

Powered by zero-dependency **SQLite FTS5** (BM25 ranking, < 15 ms p95), memory is cleanly separated into three scopes with **zero increase in fixed per-turn context**:

```text
~/.xp-kit/memory/         ← user: scope (global cross-repo JIT; never committed to projects)
  ├── USER_MEMORY.md        (developer preferences, cross-project lessons, universal never rules)
  ├── GLOBAL_DEAD_ENDS.md   (universal tooling/stack pitfalls shared across all repositories)
  └── .user_index.db        (local SQLite FTS5 index)

<repo>/.agents/memory/    ← repo: scope (strictly isolated per repository, Git-tracked)
  ├── PROJECT_MEMORY.md     (≤ 3 KB fixed bootstrap: facts, decisions, progress, never, dead-ends)
  ├── archive/HISTORY.md    (sliding-window episodic archive)
  └── .memory_index.db      (local SQLite FTS5 index, gitignored)

<repo>/.agents/runtime/   ← session: scope (ephemeral task state, gitignored)
  ├── run.json              (active task contract + tried[] dead-ends)
  └── flow_state.json       (workflow pointer + whiteboard state)
```

- **Full 5-Tier Indexing:** FTS5 indexes facts, architectural decisions, episodic history, `never` rules, and `Dead-Ends` across both `repo:` and `user:` scopes (`repo:` takes precedence; zero cross-project data leakage).
- **Deterministic Consolidation:** `xp memory consolidate` automatically promotes session `tried[]` dead-ends and `never[]` rules from `run.json` into durable memory with SHA-256 deduplication.

---

## 3. Installation and Setup

```bash
# Global installation + sync across all local projects using the kit
python3 scripts/kit_installer.py --global --yes

# Or via shell script (Antigravity global sync + ~/.local/bin/xp)
./scripts/install-global.sh

# Inject kit into a specific project
python3 scripts/kit_installer.py init /path/to/project --yes
```

---

## 4. Canonical Commands (`xp`)

The unified CLI entrypoint `xp` consolidates all kit tools:

| Command | Description |
|---|---|
| `xp contract <init\|get\|validate>` | Initializes and validates the task contract in `.agents/runtime/run.json` |
| `xp gate <check\|record\|--sync-memory>` | Runs the 10-step compliance gate, records native test evidence, and generates receipt |
| `xp flow <start\|next\|advance\|run\|reopen\|state>` | Drives the 9-flow workflow graph (`output_key` whiteboard, `retry`/`reopen` loops, `parallel` nodes, RED freeze) |
| `xp memory <sync\|search\|archive\|promote\|consolidate>` | Manages scoped multi-repo memory (`user:` global + `repo:` local + `session:` consolidation) |
| `xp context <query> [--scope all\|repo\|user] [--files ...]` | Low-consumption Just-in-Time (JIT) contextual retrieval bounded to ≤ 350 tokens |
| `xp policy <list\|show\|generate>` | Lists, inspects, and regenerates the compact JIT policy index (`.agents/policies/INDEX.md`) |
| `xp kit <doctor\|eval\|pack\|components\|install>` | Governance linter (`kit doctor`), benchmark comparator, packs, and multi-host installer |
| `xp session <compact\|resume\|handoff>` | Compacts and resumes long sessions to prevent history token explosion |
| `xp conformance` | Generates AC-to-test traceability conformance reports |
| `xp evolve <report\|propose\|apply>` | Evidence-based self-improvement on recurring failures and ablation audits |
| `xp <debt\|worktree\|effort\|compact\|repo-map\|skills-profile>` | Technical debt ledger, Git worktrees, effort routing, payload compaction, repo map, and skill profiles |
| `xp approve <action_id>` | Records explicit human authorization for `human`-tier actions |
| `xp run <cmd>` | Protected and monitored command execution via harness |

---

## 5. Engineering Guarantees

- **Lean Base Context (≤ 8,000 B):** `AGENTS.md` (≤ 3,000 B) + `PROJECT_MEMORY.md` (≤ 3,000 B) loaded upfront; policies, skills, and `user:` memory load on demand via JIT.
- **Frontmatter Token Cap (≤ 110 chars):** `xp kit doctor` mechanically enforces concise descriptions on all skills and agents and validates that every agent's declared skills exist on disk.
- **Zero Cosmetic Fixes & Empirical Proof:** Prohibits marking bugs or tasks resolved without running native verification commands (`exit_code: 0`) and adding regression tests.
- **Strict TDD & Mechanical Anti-Test-Bypass:** RED tests are frozen via SHA-256; Step 4 of `xp gate` mechanically blocks God files (> 500 lines), `TODO`/`TBD`/`FIXME`, `NotImplementedError`, type/linter suppressions (`as any`, `@ts-ignore`, `# type: ignore`, `# noqa`), skipped tests (`@unittest.skip`, `.skipTest`, `pytest.mark.skip`), and hardcoded secrets (`sk_live_*`, `AKIA…`, `ghp_…`, `api_key='…'`).
- **Policy JIT Index:** `scripts/policy_index.py` indexes all 7 governance policies in `.agents/policies/INDEX.md` with triggers and 1-line summaries; full bodies load on demand via `xp policy show <id>` or `xp context <query>` (also fixed in OpenCode `opencode.json`).

---

## 6. Git Discipline & Repository Hygiene

- **Atomic Commits:** Structured Conventional Commits (`feat`, `fix`, `refactor`, `test`, `chore`, `docs`).
- **Zero Plans in Git:** Transient plans, prompts, and `.agents/runtime/` logs are excluded via `.gitignore`.
- **Blocking Gates:** Every release requires `python3 -m unittest discover tests`, `python3 scripts/kit_lint.py`, and `python3 scripts/goldfish_review.py --check-code` passing with zero errors.

---

## 7. Empirical Benchmark (With Kit vs Without Kit)

The [benchmark/](benchmark/README.md) suite measures both **deterministic governance** and **real LLM-in-the-loop token consumption** across paired Git sandboxes:

- **Deterministic Harness (`16` paired scenarios):** `10/10` defects blocked (`100%` recall vs `10%` baseline, `0%` false positives), `context_compactor` (`−61.9%`), `repo_map` (`−83.3%`), and JIT context retrieval (`−89.4%`).
- **Real LLM-in-the-Loop (`T01`–`T06`, `agy` / `gemini-3.8-flash-low`):** `6/6` tasks resolved (`100%`), **−3.6% total tokens** (`170,642` vs `177,059`), **−21.9% median tokens/task**, **−2.3% duration**, and `0` unverified `L1+` sessions (`5/5` RED→GREEN + `GATE PASS`).
- **Real Multi-File Feature A/B (`Coupon` + `CouponRegistry` + `pricing.py`, `gemini-3.8-flash-medium`):** **−20.9% total tokens** (`63,521` vs `80,259`), **−66.2% thinking tokens**, and **−44.5% execution time** (`119.2s` vs `214.8s`).

See [docs/BENCHMARK.md](docs/BENCHMARK.md), [benchmark/results/RESULTS.md](benchmark/results/RESULTS.md), and [benchmark/results/LLM_RESULTS.md](benchmark/results/LLM_RESULTS.md).
