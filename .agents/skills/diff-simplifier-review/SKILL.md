---
name: diff-simplifier-review
version: 1.0.0
description: Minimalist git diff review, YAGNI enforcement, and over-engineering removal.
author: André Victor
license: MIT
tags: [git-diff, code-review, minimalism, yagni, cursor, claude-code]
compatibility: [cursor, claude-code, codex, gemini-cli, opencode]
entrypoint: SKILL.md
---

# Diff Simplifier Review

Perform a surgical self-review and diff simplification pass before handing off to `release-gatekeeper`, ensuring only the minimal required code enters the repository.

## 1. Minimalist & Deslop Principles
1. **Less Is More:** Every added line is future maintenance and bug surface. Delete unnecessary abstractions.
2. **Purge Accidental Artifacts:** Remove debug prints (`console.log`, `print`, `dbg!`), commented-out code, scratch files, and unused imports.
3. **No God Files (< 500 Lines):** Split any touched production file that exceeds 500 lines into cohesive modules.

## 2. 5-Pass Surgical `git diff` Checklist
- [ ] **Pass 1 (Scope):** Does every hunk in `git diff` belong strictly to the requested task?
- [ ] **Pass 2 (YAGNI):** Are there single-implementation interfaces, unused config flags, or single-caller wrappers? Inline them.
- [ ] **Pass 3 (Comments):** Strip comments that restate code; keep only non-obvious *why* rationale.
- [ ] **Pass 4 (Error Handling):** Ensure no swallowed exceptions (`except Exception: pass`, empty `catch {}`).
- [ ] **Pass 5 (Naming):** Use clear, self-explanatory identifiers without cryptic abbreviations.

## 3. 1-Line Finding Grammar
Report simplification findings in 1 line per item:
`L<line>: <tag> <what to cut>. <replacement>.` (or `<file>:L<line>: <tag> ...`)

### Standard Tags
- `delete:` dead code, unused flexibility, or speculative feature. Replacement: none.
- `stdlib:` custom reimplementation of a Standard Library function. Name the native stdlib call.
- `native:` external dependency duplicating HTML5/CSS3/platform capability.
- `yagni:` single-use abstraction or unrequested configuration layer.
- `shrink:` equivalent logic in fewer lines.

### Context Tags (production-bug review)
Read the code around the diff (callers, tests, configs) before tagging. These tags only flag; `sentinel` / `release-gatekeeper` decide.
- `risk:` security hole, unvalidated trust boundary, data-loss or unhandled-error path.
- `perf:` slow path or load concern (N+1, unbounded loop, missing timeout).
- `test:` risky logic or edge case without a covering test.
- `gap:` change incomplete: caller, config or doc left out of sync.

### Final Review Balance
End every review with net reduction: `net: -<N> lines, -<M> deps possible.` or `Lean already. Ship.`

## 4. Repo-Wide Audit
1. Map the repo first (`code-review-graph` or `agy-repo-map`).
2. List findings with the same 1-line grammar, ranked by severity (`risk:` > `test:` > `gap:` > `perf:` > simplification tags).
3. End with the top fixes in priority order.

## 5. Refactor-Warden Execution
```bash
git diff --stat
git diff
git checkout -- <unintended-file>
```
