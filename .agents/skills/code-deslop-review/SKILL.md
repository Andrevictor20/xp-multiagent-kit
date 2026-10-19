---
name: code-deslop-review
version: 1.0.0
description: Systematic AI code cleanup, dead-code removal, and <500-line No God Files rule.
author: André Victor
license: MIT
tags: [code-review, anti-slop, clean-code, refactoring, cursor, claude-code]
compatibility: [cursor, claude-code, codex, gemini-cli, opencode]
entrypoint: SKILL.md
---

# Code Deslop Review

Systematically strip AI-generated verbosity, obvious comments, redundant defensive checks, lazy typecasts, and deep nesting before delivery.

## 1. The 5 Dimensions of Code Deslop

### 1.A Strip Obvious Comments
- **Slop:** Comments that restate the code (`// set user status to active`).
- **Clean:** Keep only comments explaining non-obvious **WHY** decisions, invariants, or external constraints.

### 1.B Remove Redundant Defensive Checks
- **Slop:** Empty `try/catch` blocks or repetitive `null`/`undefined` checks inside already-validated internal paths.
- **Clean:** Validate once at system boundaries (Zod/schemas) and trust internal types; handle errors only where recovery or context enrichment occurs.

### 1.C Flatten Nesting with Early Returns
- **Slop:** 4-6 levels of nested `if/else` trees.
- **Clean:** Invert conditions into guard clauses / early returns so the happy path stays at the top indentation level.

### 1.D Eliminate Lazy Typecasts
- **Slop:** `as any`, `!`, or `as unknown as T` to silence the compiler.
- **Clean:** Fix the underlying type contract or add a runtime type guard.

### 1.E Purge Dead Code & Speculative Abstractions
- **Slop:** Unused helpers "for future use", unused parameters, leftover debug logs, and unreferenced imports.
- **Clean:** Ship only code required for the current scope.

## 2. The "No God Files" Rule (< 500 Lines)
- **Hard Cap:** No production source file may exceed **500 lines**.
- **Mandatory Separation of Concerns:** Never mix in one file:
  1. Type contracts/interfaces (`types.ts`)
  2. Registries/mappings (`registry.ts`)
  3. Domain/service logic (`service.ts`)
  4. Pure formatting/utility helpers (`utils.ts`)
- Split any file approaching 500 lines into cohesive named modules before completing the task.
