---
name: craft-system
description: Use when starting a design system, style guide or token set, adding or changing a component or token, standardizing screens that drifted apart, or auditing a guide for loose colours, one-off pieces, missing states or screens that don't match it.
---

# Design system

## Overview

A design system is the place where a decision is made once and then reused everywhere. Every colour is a token, every interactive piece shows all its states, and every change reaches every screen that uses the piece. **Build it in layers, foundations first, and stop for approval at each layer. An audit reports and never fixes on its own.**

## When to use

- "Start a style guide / design system / tokens for …"
- Adding a component, variant or token, or changing an existing one.
- "Make these screens consistent", "standardize", "audit the guide", or loose hex values and one-off pieces in the screens.

## When NOT to use

- A question about one value ("what's our primary colour?"): answer it.
- A small edit the person described exactly (one value, one label, one size), even on a shared piece: change it once where it's defined and say which screens it affects. No states matrix, no stop.

## Before you start

0. Read `DESIGN.md` at the project root if it exists: it is the project's design brief.
1. Find what exists: tokens, the guide, the components, the screens and the code. **An existing guide wins on look.** Follow its rules even where they differ from the defaults below, and mention the difference once.
2. Pick your tool's adapter in `references/adapters/` (`paper.md`, `figma.md`, `html.md`). If no adapter matches your tool, do the same verbs in your tool and say which you mapped by hand. With no design tool at all, build in HTML (`html.md`). If an image is all you have, say that values read from it are estimates.
3. Decide the mode: **create**, **add or change**, or **audit**.

## Steps · create

1. **Foundations draft:**
   - colour roles ([token roles](references/token-roles.md));
   - type scale;
   - spacing;
   - radius;
   - shadows (two at most);
   - layout widths;
   - motion durations;
   - a short "how we write" section.

   Name tokens by role (`text-muted`, `border-hover`, `danger-bg`), never only by value (`gray-500`).
2. **Interaction rules, once:** for bordered pieces, borderless pieces and the primary action, write how hover, pressed, focus (keyboard only), disabled, loading and selected look. Components follow these rules instead of each inventing its own.
3. **Stop and show the person the foundations and the interaction rules.** Don't build components yet.
4. **Components one at a time, in the order the first screens need them.** Each gets a guide section with the [component anatomy](references/component-anatomy.md): a legend with the rule and why, examples, and a **states matrix** of variants × states. Add each one to the **component index**.

## Steps · add or change a piece

1. Check whether an existing component plus a variant covers it. Prefer reuse to a one-off.
2. Draw it with the anatomy, including the full states matrix. A new colour, size or icon becomes a token or an icon-set entry now, not later.
3. **List every screen and code location that uses the piece.**
4. **Stop and show the person the change and that list.**
5. On approval, propagate:
   - update every screen on the list;
   - update the code, if any. When `DESIGN.md` says the design system's source is code, do it with **REQUIRED SUB-SKILL:** `craft-sync` (export), so the code change is a reviewed diff. If that diff holds only the change just approved and no conflicts, the approval carries over: say so and apply, without a second stop;
   - update the component index;
   - report what changed where.

## Steps · audit

1. Run the [audit checklist](references/audit-checklist.md) over the guide, the screens and the code if any.
2. Write the report: findings ranked by severity, each with where it is, why it matters and the proposed fix.
3. **Stop and show the person the report. Change no file until they say which fixes to make.** Saving copies of the originals doesn't make editing them acceptable.

## Rules

**Firm (any project):**

| Rule | Why |
|---|---|
| Every colour is a token; no loose hex values in screens or code | Loose values drift into near-duplicates that nobody can change at once |
| One icon set | Mixed sets look like mixed products |
| Design and code change together, design first | Otherwise the guide stops being the truth within a week. When the system's source is code, "design first" means: draw the change in the tool, then land it in code through an approved export |
| Every interactive piece has a states matrix | States drawn ad hoc on screens never agree |
| A change to a shared piece is listed with the screens it affects before it propagates | Otherwise one "small" change silently redesigns twenty screens |

**Defaults (an existing guide overrides them):** See [defaults & common mistakes](references/common-mistakes.md) (bordered hover darkens border only, hover quieter than selected, no weight shift on select, keyboard-only focus ring, zero layout shift on loading, max two shadow strengths, at most one primary action per screen).

## Done when

- **Create:** foundations and interaction rules approved; each component has its anatomy, states matrix and an index row.
- **Change:** every listed screen and code location updated, and the index updated.
- **Audit:** a ranked report delivered and no file changed.

## Common mistakes

See [common mistakes](references/common-mistakes.md) before building components on unapproved foundations, editing during audits, or using literal color tokens.
