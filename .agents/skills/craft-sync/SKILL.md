---
name: craft-sync
description: "Sync design tokens and components bidirectionally between code and design tools."
---

# Design system sync

## Overview
Mirror an existing code design system in the design tool (**Import**) and push approved guide edits back to code as a reviewed diff (**Export**). Track last agreed values in **`design-sync.json`** at project root; code remains source of truth until export is approved.

## When to use / NOT to use
- **Use:** Starting design with a code design system not yet in the tool; importing tokens/components to Paper/Figma; exporting guide edits back to code.
- **Skip:** No code design system → `craft-system` (create). Single explicit code token change → edit directly and update `design-sync.json`.

## Before you start
Read `DESIGN.md` and `design-sync.json` if present; pick adapter in `references/adapters/` (`paper.md`, `figma.md`, fallback `html.md`). Schema in [common mistakes](references/common-mistakes.md).

## Import (code → design tool)
1. **Detect** ([signals](references/detect.md)): locate token **source of truth** (never generated output) and naming rule. Two UI packages → ask which is source.
2. **Inventory, then stop** ([inventory format](references/inventory.md)): list tokens by role, components (grouped if >15), docs, gaps, and **conflicts**. Ask which 3–6 components to draw now and how to resolve each conflict. Never draw everything by default.
3. **Build:** register tokens (never overwrite unsettled conflicts), create foundations guide + component index (`drawn` / `in code only`), draw chosen components with state matrices from code values (label undefined states `"proposed"`).
4. **Self-check:** render guide and compare with Storybook/demo if available (else state unrendered).
5. **Record:** write `design-sync.json`; update `DESIGN.md` Brand (`Design system source: <path>`) and Decisions log (if no `DESIGN.md`, create sync-only stub `<!-- sync record only: run craft-setup for the brief -->`).

### One-component import (from `craft`)
Skip inventory stop if import was already agreed: draw that component, mark `drawn`, leave `tokens` untouched. If never agreed/declined, ask once before importing.

## Export (design tool → code)
1. **Read** guide values (adapter) and code values by name.
2. **Classify** with `design-sync.json` ([diff format](references/export-diff.md)): `equal` (in sync), `guide changed` (propose), `code changed` (offer refresh), `both changed` (**ask which wins**). Without `design-sync.json`, ask direction per difference.
3. **Propose edits** to **source** files only (file, line, impact, color contrast); exclude `"proposed"` states and substituted fonts. **Stop.**
4. **Apply** approved edits, sync guide for code-wins items, run project checks (lint/typecheck/tests).
5. **Record:** update `design-sync.json`, append Decisions log, log open conflicts.

## Rules & Done when
Keep identical token names via one rule, read values from code (never screenshots), label missing states `"proposed"`, stop before exporting diffs. Done when inventory/conflicts or approved diffs are settled, checks run, and `design-sync.json` + `DESIGN.md` are updated. See [common mistakes](references/common-mistakes.md).
