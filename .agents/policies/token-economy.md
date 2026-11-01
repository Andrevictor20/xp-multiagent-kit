# Token Economy & Mechanical Discipline Policy

> Loaded on-demand. Numeric constants live in `scripts/kit_constants.py`.

## 1. Completeness Over Speed
1. **No Rushed Delivery:** Never truncate architectural plans, omit edge cases, leave `TODO`/`TBD` placeholders, or skip test verification to reduce turns. Delivering 100% of the requested capability is mandatory.
2. **Batch Operations:** Group independent file reads and checks in the same turn to preserve execution turns for deep engineering.
3. **Lean Context:** Fixed base context is strictly budgeted (`AGENTS.md` ≤ 3000 bytes, `PROJECT_MEMORY.md` ≤ 3000 bytes, total base ≤ 8000 bytes).
4. **Tool Discipline:** Avoid polling loops on long tasks. Do not re-read files immediately after editing.
5. **AST Symbol Mapping:** For files > 800 lines or complex call hierarchies, locate symbols via `code-review-graph` rather than blind text grep.

## 2. 7-Step Simplification Ladder
1. YAGNI → 2. Internal Reuse → 3. Standard Library → 4. Platform-Native → 5. Installed Dependency → 6. Idiomatic One-Liner → 7. Minimal Code.
Annotate deliberate temporary compromises with `# debt: <ceiling>, <upgrade trigger>` and audit via `xp kit audit` or `agy-debt`.
