---
name: token-budget-tracker
description: 3-tier token telemetry, Pre-Flight budget gates, and Surgical Atomic Mode.
---

# Token & Quota Budget Tracker

Audit, enforce, and preserve token budgets across 3 quota layers in Antigravity, OpenCode, Cursor, Codex, and Qoder (`.agents/policies/token-economy.md`).

## 1. The 3 Quota Layers
1. **Session Context Window:** Active conversation working memory (e.g., 1.05M tokens on Gemini, 200k on Claude). Warn at `> 70%` used or `< 100k` remaining.
2. **Rolling 5-Hour Rate Limit:** Cross-session rolling 5h window. Warn at `> 80%` used.
3. **Weekly Account Quota:** 7-day rolling subscription quota. Warn at `> 85%` used.

## 2. Tool & Turn Cost Governance
> **Cost Model:** `cost ≈ Σ_turns(base_context + history) + Σ_outputs`. **Reducing turns saves far more tokens than shrinking individual outputs.**

- **Turn Budgets by Risk:** `L0 <= 3` • `L1 <= 8` • `L2 <= 20` • `L3` checkpointed. Batch independent reads/edits in the same turn.
- **Single-Call File Reads:** Read files `<= 800` lines (`WHOLE_FILE_READ_MAX_LINES`) in 1 call; above 800 lines, locate symbols via `REPO_MAP.md`/grep and read the exact range. Never re-read a file immediately after `replace_file_content`.
- **Anti-Tool-Spam:** Never poll `manage_task(status)` in a loop (wait for reactive wakeup). Wrap noisy commands with `agy-run` / `agy-sanitize`.
- **Session Compaction:** Compact or reset sessions every **15 turns or 40k tokens** via `PROJECT_MEMORY.md`.

## 3. Pre-Flight Budget Gate & Surgical Atomic Mode
1. **Mandatory Pre-Flight Alert:** If any of the 3 quota layers is in Warning/Critical state before a heavy task, alert the user with the remaining margin and offer a clean session handoff via `PROJECT_MEMORY.md`.
2. **Surgical Atomic Mode:** If the user insists on proceeding under tight quota, scope work to a single self-contained atomic unit (e.g., 1 green test + 1 module edit), sync `PROJECT_MEMORY.md`, and pause cleanly before truncation.

## 4. Mandatory Telemetry Footer & CLI Commands
Append the canonical 4-line telemetry footer (`agy-tokens --turn` / `xp-tokens --turn`) at the end of **every** response:

```bash
xp-tokens              # Interactive rich terminal dashboard
xp-tokens --turn       # Compact 4-line turn footer for chat responses
xp-tokens --check      # Pre-Flight budget health check
xp-tokens --watch      # Live real-time monitor (tmux/split pane)
xp-tokens --badge      # Compact Markdown badge
xp-tokens --json       # Structured JSON export
xp-tokens --report     # Detailed .agents/memory/TOKEN_TELEMETRY.md report
```
