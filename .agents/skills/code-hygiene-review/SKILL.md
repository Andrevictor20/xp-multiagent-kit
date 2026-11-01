---
name: code-hygiene-review
description: Strict code quality guardian enforcing atomic commits, code deslop, YAGNI diff simplification, no-workarounds, and no god files.
---

# Code Hygiene Review (`code-hygiene-review`)

Consolidates disciplines of **Code Hygiene**, **Atomic Commits**, **No-Workarounds**, **Diff Simplification**, and **No-God-Files**.

## 1. Atomic Commits & Git Ops
- Each commit must represent a single, indivisible, and tested unit of work.
- Standardized messages following Conventional Commits: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`.
- The test suite must pass (100% green) on each individual commit.

## 2. No Workarounds & Root Cause
- **Absolute Prohibition of Workarounds:** Never suppress typing (`as any`, `@ts-ignore`, `# type: ignore`) or tests to pass gates.
- **No Arbitrary Sleeps:** Replace `time.sleep()` or temporal pauses with deterministic conditional polling or state awaits.
- Always address the root cause rather than masking symptoms.

## 3. Deslop & Diff Simplification (YAGNI)
- Active removal of dead code, unused variables, boilerplate AI-generated comments, and redundant prose.
- Diff minimalism: modify only files strictly necessary to satisfy task contracts.
- No speculative abstractions for hypothetical requirements.

## 4. No God Files (< 500 Lines)
- No production source file, script, or test suite may exceed 500 lines.
- When approaching the limit, refactor by extracting single-responsibility submodules.
- No logic duplication across modules.
