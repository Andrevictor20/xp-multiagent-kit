---
name: codebase-cartography
description: AST dependency graph mapping and blast-radius analysis via code-review-graph.
---

# Codebase Cartography (CodeReviewGraph)

Deterministic AST (Tree-sitter) and dependency graph mapping via MCP (`code-review-graph`) and CLI (`agy-graph`). Replaces blind file scans with surgical ~100-800 token context.

## 1. Essential MCP Tools (Execution Order)
1. **Surgical Initial Context (~100 tokens):**
   - Call `get_minimal_context_tool(task="<task description>")` before reading files.
2. **Blast Radius Mapping:**
   - Call `get_impact_radius_tool(files=[...])` to map transitive callers, dependents, and affected downstream modules.
3. **Callers & Test Coverage Lookup:**
   - Call `query_graph_tool(pattern="callers_of", target="<symbol>")` to locate all invocation sites.
   - Call `query_graph_tool(pattern="tests_for", target="<symbol>")` to find existing tests and identify test gaps.
4. **Change Risk Analysis:**
   - Call `detect_changes_tool(detail_level="minimal")` to compute risk scores, affected execution flows, and untested functions.
5. **Architecture & Module Clusters:**
   - Call `get_architecture_overview_tool()` to inspect Leiden functional communities and inter-module edges without reading full files.

## 2. Companion CLI (`agy-graph` / `code-review-graph`)
- `agy-graph query callers_of <symbol>`: Direct and transitive callers.
- `agy-graph query tests_for <symbol>`: Tests covering the symbol.
- `agy-graph dead-code`: Unreferenced functions and classes.
- `agy-graph detect-changes --brief`: Compact risk and impact summary.
- `agy-graph update --skip-flows`: Fast incremental index update (~2s) after edits.

## 3. Token Economy Discipline
- Prefer structured graph queries over full-file `view_file` scans.
- Default to `detail_level="minimal"`; escalate to `"standard"` only when needed.
- Budget at most 3 graph calls (~800 total tokens) per analysis cycle, then read only the exact line ranges required.
