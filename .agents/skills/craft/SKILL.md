---
name: craft
description: "Design, create, mock up, or redesign pages, screens, flows, or UI elements (/craft)."
---

# Craft

## Overview
Front door for visual UI work: turns a request into a finished, self-checked design using `DESIGN.md`, full state coverage, system tokens/components only, and `craft-critique` before showing. Calls the other `craft-*` skills at fixed points.

## When to use / NOT to use
- **Use:** Design, create, mock up, or redesign page(s), screen(s), flow(s), or UI element(s); `/craft`.
- **Skip:** Exact single edit (one value/label/size) → apply directly. Review only → `craft-critique`. Options only → `craft-explore`.

## Before you start & Stops
- Pick adapter in `references/adapters/` (`paper.md`, `figma.md`, fallback `html.md`). If working from an image only, mark values as estimates.
- **Stops are real:** End your turn with the question and wait. Never decide a stop for the user to save a turn.

## Steps
1. **Context.**
   - Read `DESIGN.md` at project root. If missing or sync-only (no Product section) → **REQUIRED SUB-SKILL: `craft-setup`**, then return.
   - Read design system (tokens, components, guide) and related screens.
   - Brief vs code conflict → follow **code**, note in `DESIGN.md` › Open questions, offer to update; never override tokens in page CSS.
   - Guide vs code diff with `design-sync.json` → code changed: offer refresh; guide changed: draw with guide and note pending export.
2. **Scope in words.** List each page/element, its job, and its next action; state plain interpretation of ambiguities. **Stop and confirm** when >1 item or vague.
3. **For each item, in order:**
   1. **REQUIRED SUB-SKILL: `craft-states`** (written state list + stop first).
   2. **Open direction?** Only when asked for ideas or two structurally distinct layouts are plausible → **REQUIRED SUB-SKILL: `craft-explore`** before drawing states. Never run exploration per page by default.
   3. **Draw** main state then remaining states using **only system pieces and tokens**. New token/component → **REQUIRED SUB-SKILL: `craft-system`** (add mode) first. Component in code only → **REQUIRED SUB-SKILL: `craft-sync`** (one-component import); if declined, build from code values and note it. Never hard-code raw values.
   4. **REQUIRED SUB-SKILL: `craft-critique` (self-check)** on every board: render, fix in-scope issues, re-render.
4. **Close.** Present closing summary (`Made`, `Decisions`, `System changes`, `Self-check fixed`, `Open questions` per [common mistakes & summary](references/common-mistakes.md)), append decisions to `DESIGN.md` › Decisions log, clear answered Open questions.

## Rules
- `DESIGN.md` first every time; confirm scope when >1 item.
- States list before drawing (`craft-states`); options only when direction is open (`craft-explore`).
- System tokens/components only (`craft-system`); code beats stale brief.
- Self-check before showing (`craft-critique`); persist decisions in `DESIGN.md`.

## Done when
Every confirmed item has states drawn and self-checked, system changes went through `craft-system`, closing summary was delivered, and `DESIGN.md` Decisions log is updated. See [common mistakes](references/common-mistakes.md).
