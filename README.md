# XP Multi-Agent Kit v4.0.0 — Thin Harness

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Version: 4.0.0](https://img.shields.io/badge/version-4.0.0-brightgreen.svg)](#)
[![TDD: Strict RED-GREEN](https://img.shields.io/badge/TDD-strict-success.svg)](#4-engineering-guarantees)

Deterministic governance Thin Harness for AI agent pair-programming (**Antigravity**, **OpenCode**, **Cursor**, **Codex**, **Qoder**, and **Claude**). Replaces redundant prose with verifiable code mechanisms and restricts the fixed base context to ≤ 8 KB.

---

## 1. 4-Layer Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. HARNESS: PreTool Guard + policy.yaml + kit_events.jsonl (security)  │
├────────────────────────────────────────────────────────────────────────┤
│ 2. LOOP: xp contract (run.json) + xp gate (10 steps) + EGM (2 personas)│
├────────────────────────────────────────────────────────────────────────┤
│ 3. GRAPH: workflow.yaml (8 flows) + xp flow (RED SHA-256 test freeze)  │
├────────────────────────────────────────────────────────────────────────┤
│ 4. CORE: 6 core agents + 24 skills + packs (.agents/packs/)            │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Harness (Outer Layer):** Deterministic interception via hooks (`pre_tool_guard`), permission tiers in `policy.yaml` (`auto|review|human`), and structured telemetry in `.agents/runtime/events.jsonl`.
2. **Loop (Focused Execution):** Structured contract in `run.json` (`xp contract`), 10-step delivery gate (`xp gate`), and EGM audit with 2 personas (`spec_reviewer`, `code_reviewer`).
3. **Graph (Transitions):** State machine driven by `workflow.yaml`, verified progression, and RED test freezing (`xp flow`).
4. **Core (Specialists):** 6 core agents (`orchestrator`, `builder`, `reviewer`, `sentinel`, `designer`, `shipper`) and 24 skills in the main catalog, with optional bundles in `.agents/packs/`.

---

## 2. Installation and Setup

```bash
# Global installation via shell
./scripts/install-global.sh

# Or via Python agnostic installer
python3 scripts/kit_installer.py
```

---

## 3. Canonical Commands (`xp`)

The unified CLI interface `xp` consolidates all kit entry points:

| Command | Description |
|---|---|
| `xp contract <init|show|validate>` | Initializes and validates task contract in `.agents/runtime/run.json` |
| `xp gate <check|--sync-memory>` | Runs the 10-step compliance gate and generates receipt |
| `xp flow <start|next|advance|reopen>` | Drives workflow graph and manages RED test freezing |
| `xp evolve <report|propose|apply>` | Evidence-based self-improvement on failures and ablation audit |
| `xp kit <doctor|pack|eval|install>` | Integrity linter (`kit doctor lint`), packs, eval, and installation |
| `xp memory <sync|search|archive>` | Synchronizes and searches 4-tier continuous memory |
| `xp context <query>` | Low-consumption Just-in-Time (JIT) contextual retrieval |
| `xp approve <action_id>` | Records explicit human authorization for high-risk actions |
| `xp run <cmd>` | Protected and monitored execution via harness |

---

## 4. Engineering Guarantees

- **Base Context ≤ 8,000 B:** `AGENTS.md` (≤ 3,000 B) + `PROJECT_MEMORY.md` (≤ 3,000 B) loaded upfront; remaining loaded on demand.
- **Strict TDD & Mechanical Anti-Test-Bypass:** RED unit tests frozen via SHA-256 hash; unauthorized modification blocked at gate.
- **Continuous Audit:** `xp kit doctor lint` validates integrity, token budgets, and compliance with `components.yaml`.

---

## 5. Git Discipline & Repository Hygiene

- **Atomic Commits:** Structured Conventional Commits messages (`feat`, `fix`, `refactor`, `test`, `chore`).
- **Zero Plans in Git:** Transient work plans and prompts are excluded from version control via `.gitignore`.
- **Blocking Gates:** Every push strictly requires prior approval from `xp gate check` and 100% passing unit tests.
