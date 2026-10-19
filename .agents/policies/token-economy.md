# Token Economy & Mechanical Enforcement Policy

> Loaded on-demand. Numeric constants live in kit runtime scripts and constants.

## 1. Cost Model
`total_cost ≈ Σ_turns (base_context + history) + Σ tool_outputs`
1. **Reduce turns first:** Batch independent reads/checks in the same turn. Turn 1 MUST group `PROJECT_MEMORY.md` + target files.
2. **Keep base context lean:** `AGENTS.md` ≤ 6 KB, `PROJECT_MEMORY.md` ≤ 8 KB, each `SKILL.md` ≤ 6 KB.
3. **Avoid tool spam:** Never poll `manage_task(status)` in a loop (`MAX_TASK_STATUS_POLLS = 1`). Never re-read a file immediately after editing (`POST_EDIT_REREAD_TTL_SECONDS = 30s`).
4. **File Reads:** Read files ≤ 800 lines (`WHOLE_FILE_READ_MAX_LINES`) in a single call. Above 800 lines, locate symbols via `code-review-graph` or `grep_search` and read exact 400-line sections.

## 2. Turn Budgets by Risk
| Risk | Max Tool Turns | Rule |
|------|----------------|------|
| L0 | 3 | Zero-tool for conceptual questions |
| L1 | 8 | Surgical module tests only |
| L2 | 20 | Spec + tests + implementation |
| L3 | Checkpointed | Atomic checkpoints mandatory |

## 4. 7-Step Simplification Ladder & Debt Tracking
1. YAGNI → 2. Internal Reuse → 3. Standard Library → 4. Platform-Native (`.agents/policies/platform-native.md`) → 5. Installed Dependency → 6. Idiomatic One-Liner → 7. Minimal Code.
Annotate deliberate shortcuts with `# debt: <ceiling>, <upgrade trigger>` and audit via `agy-debt --scan`.
