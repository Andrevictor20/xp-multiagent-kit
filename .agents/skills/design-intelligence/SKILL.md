---
name: design-intelligence
version: 1.0.0
description: Offline design catalog search (product archetypes, palettes, fonts, UX rules, charts) generating a persistent design-system MASTER.md.
author: André Victor
license: MIT
tags: [ui-ux, design-system, palettes, typography, ux-rules, charts, cursor, claude-code]
compatibility: [cursor, claude-code, codex, gemini-cli, opencode]
entrypoint: SKILL.md
---

# Design Intelligence

Fills the kit's design gap: the other design skills hold principles; this one holds a **searchable, deterministic catalog** so decisions do not depend on model taste per session. It is a source of **options**; the kit's locks always win.

## 1. Workflow (before writing UI code)
1. Run Token Discovery first. If the project already has tokens, they override the catalog.
2. Generate the brief baseline: `python3 scripts/design_search.py "<brief keywords>"` (add `--persist` to write `design-system/MASTER.md`).
3. Refine per domain: `--domain products|palettes|fonts|ux|charts "<keywords>"`.
4. Calibrate dials with `frontend-taste-engineering`, then implement with `component-architecture` and `design-tokens`.
5. Close with `ui-quality-gate` (and `visual-regression` when available).

## 2. Catalogs (`assets/*.csv`)
- `products.csv`: archetype -> style, palette, fonts, layout pattern, 3 dials, what to avoid.
- `palettes.csv`: curated palettes (single accent, no `#000000`, text/bg contrast >= 7:1, accent saturation < 80%).
- `fonts.csv`: display/body/mono pairings by mood (distinctive over default Inter-only).
- `ux-rules.csv`: ~16 do/don't rules with severity (touch, feedback, forms, motion, contrast, keyboard, empty, destructive, viewport).
- `charts.csv`: question -> chart type, accessibility notes, charts to avoid.
- `design-systems.csv`: 33 web and mobile systems (package, license, style, how to customize tokens, a11y). The generator recommends a **Base system** and forbids the default theme.
- `mobile-ux.csv`: 22 iOS/Android/both rules (44pt/48dp, safe area, thumb zone, Dynamic Type, offline, permissions).
- `mobile-apps.csv`: 14 app archetypes (navigation, key screens, system, palette). Use `--mobile`; see `mobile-app-design`.

## 3. Precedence (anti-conflict)
1. Existing project tokens and `MASTER.md` -> 2. Kit locks (Color/Shape Lock, 6 states, `100dvh`, 48px, WCAG AA, Anti-Slop bans) -> 3. This catalog.
Never apply a catalog entry that violates a kit lock; pick the next hit or extend the CSV.

## 4. Extending the catalog
Add rows to the CSVs only; `tests/test_design_search.py` enforces the invariants (AA contrast, no pure black, one accent under 80% saturation, valid palette/font references, dial range 1-10).
