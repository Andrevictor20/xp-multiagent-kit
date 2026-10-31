# Token Economy & Mechanical Discipline Policy (Completeness-First)

> Loaded on-demand. Numeric constants live in `scripts/kit_constants.py`.

## 1. Completeness Over Speed & Cost Model
`total_cost ≈ Σ_turns (base_context + history) + Σ tool_outputs`
1. **Completeness Overrides Speed (`COMPLETENESS_OVER_SPEED = True`):** Never truncate an architectural plan, omit edge cases, leave `TODO`/`TBD` placeholders, or skip Multi-Pass EGM Goldfish reviews just to finish in fewer turns. Delivering 100% of the feature and plan is mandatory regardless of wall-clock time.
2. **Batch independent operations:** Group independent reads/checks in the same turn (Turn 1 MUST group `PROJECT_MEMORY.md` + target files) so turns are spent on deep engineering and EGM reviews rather than sequential file-read overhead.
3. **Keep base context lean:** `AGENTS.md` ≤ 6 KB, `PROJECT_MEMORY.md` ≤ 8 KB, each `SKILL.md` ≤ 6 KB.
4. **Avoid tool spam:** Never poll `manage_task(status)` in a loop (`MAX_TASK_STATUS_POLLS = 1`). Never re-read a file immediately after editing (`POST_EDIT_REREAD_TTL_SECONDS = 30s`).
5. **File Reads & Symbol Mapping:** Read files ≤ 800 lines (`WHOLE_FILE_READ_MAX_LINES`) in a single call. Above 800 lines or when mapping callers/impact, mandatorily locate symbols via `code-review-graph` (MCP or `agy-graph`). Blind text grep is prohibited for AST call-hierarchies.

## 2. Soft Orientation Turn Budgets by Risk
> Turn budgets are soft orientation metrics (`kit_constants.py`), NEVER hard stops that truncate planning or implementation.

| Risk | Soft Turn Orientation | Rule |
|------|-----------------------|------|
| L0 | 5 | Zero-tool for conceptual questions |
| L1 | 25 | Surgical module tests + completeness check |
| L2 | 100 | Exhaustive Spec + 3-Pass EGM Review + TDD implementation |
| L3 | Checkpointed | Atomic checkpoints + STRIDE + 3-Pass EGM Review |

## 3. 7-Step Simplification Ladder & Debt Tracking
1. YAGNI → 2. Internal Reuse → 3. Standard Library → 4. Platform-Native (`.agents/policies/platform-native.md`) → 5. Installed Dependency → 6. Idiomatic One-Liner → 7. Minimal Code.
Annotate deliberate shortcuts with `# debt: <ceiling>, <upgrade trigger>` and audit via `agy-debt --scan`.
