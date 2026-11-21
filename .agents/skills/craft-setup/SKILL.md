---
name: craft-setup
description: "Set up product design brief (DESIGN.md), brand guidelines, and foundations (/craft-setup)."
---

# Design setup

## Overview
Agree on product, audience, mood, and anti-patterns in `DESIGN.md` before drawing the first screen. **Ask, don't invent**: read existing files, interview one question at a time, confirm `DESIGN.md`, then establish foundations.

## When to use / NOT to use
- **Use:** Design task with no `DESIGN.md` at project root; setting up brand/style/guidelines; `/craft-setup`.
- **Skip:** `DESIGN.md` already exists → `craft`. Single token/guideline tweak → `craft-system`.

## Before you start
- Use `references/adapters/` (`paper.md`, `figma.md`, fallback `html.md`). `DESIGN.md` is always Markdown at project root.

## Steps
1. **Read first.** Inspect README, docs, existing CSS/tokens, design files, brand folders, old drafts. If code already has a design system, report counts and record `Design system source: <path>` in Brand (if two UI packages, ask which is source). **Never ask what files already answer** — confirm in one line instead.
2. **Interview (one question per message).** Follow [interview](references/interview.md): product, audience/voice, mood, brand, references, constraints. Offer 3–5 options + "something else"; skip answered items; stop once 6–8 answers suffice for the first screen.
3. **References required.** Ask for 2–5 references with **what to take and what to avoid**. Inspect any link/image before asking.
4. **Write `DESIGN.md`** at project root from [template](references/design-md-template.md) with all 8 sections (`Product`, `Audience and voice`, `Mood`, `Brand`, `References`, `Constraints`, `Decisions log`, `Open questions`). Mark unconfirmed inferences under Open questions.
5. **Stop for approval** on `DESIGN.md` and revise until approved.
6. **Foundations.**
   - **Design system in code:** offer import → on yes, **REQUIRED SUB-SKILL: `craft-sync`** (import); on no, log decline in Decisions log.
   - **No system in code:** **REQUIRED SUB-SKILL: `craft-system`** (create mode: tokens, type, spacing, interaction rules) with its approval stop. Extend existing tokens; don't rename without asking.

## If the person says "skip" or "just design it"
Write a minimal `DESIGN.md` marking gaps as Open questions and assumptions as `(assumed)`, summarize key assumptions in one line, and **never skip step 6** (still ask import if code system exists, or run foundations if no tokens exist). Then continue the design task.

## Rules
- One question per message with options; read repo first; never invent brand values silently.
- References must include take/avoid; explicitly ask "never like".
- No screens and no CSS redesign during setup.

## Done when
`DESIGN.md` is approved (or written with `(assumed)` on skip) and foundations are settled via `craft-system` or `craft-sync` (or decline logged). See [common mistakes](references/common-mistakes.md).
