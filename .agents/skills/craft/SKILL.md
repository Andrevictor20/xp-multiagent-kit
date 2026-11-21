---
name: craft
description: Use when asked to design, create, mock up or redesign one or more pages, screens, flows or UI elements, or when the person runs /craft (/craft:craft in the Claude Code plugin).
---

# Craft

## Overview

The front door for making anything visual. It turns "design the pricing page" into a finished, reviewed design. It works from the project's brief, covers every state, offers options only when the direction is open, uses only the design system's pieces, and checks its own work before showing it. **It calls the other design skills at fixed points; it doesn't replace them.**

## When to use

- "Design / create / mock up / redesign the <page, screen, flow, element>", `/craft` (`/craft:craft` in the Claude Code plugin).
- Several pages at once ("design the onboarding: welcome, sign-up, verify").

## When NOT to use

- A small edit the person described exactly (one value, one label, one size): make it.
- Only a review ("what's wrong with this?"): `craft-critique`. Only options: `craft-explore`.

## Before you start

- If no adapter in `references/adapters/` (`paper.md`, `figma.md`, `html.md`) matches your tool, do the same verbs in your tool and say which you mapped by hand. With no design tool at all, build in HTML (`html.md`). If an image is all you have, say that values read from it are estimates.

## Stops are real

A **stop** means: end your turn with the question and wait. You can always do that, even in a one-shot or headless session, where your final message *is* the question. **Never decide a stop for the person because the session "can't wait" or "to save a round trip".** Deciding it yourself turns a five-second answer into hours of redoing.

## Steps

1. **Context.**
   - Read `DESIGN.md` at the project root. **If it's missing, or has no Product section** (a sync-only record) → **REQUIRED SUB-SKILL: `craft-setup`**, then come back here.
   - Read the design system (tokens, components, guide) and the screens related to this one.
   - **When the brief and the code disagree** (the brief says teal, the tokens say blue): follow the **code**, say so in one line, add the conflict to `DESIGN.md` › Open questions, and offer to update whichever is wrong. Never override tokens inside a page's own CSS.
   - **When the design tool's guide and the code differ** and a `design-sync.json` exists, don't call the guide stale. Classify with it: **code changed** → offer to refresh the guide before drawing; **guide changed** → it's the person's change waiting for an export, so draw with it and mention the pending export.
2. **Scope in words.** List each page or element to make, each with its job and its one next action.
   - Ambiguous words get one interpretation stated plainly ("pricing page = the bakery's price list, not subscription plans").
   - **Stop and confirm the list** when there's more than one item or the request is vague. One clear item: go on.
3. **For each item, in order:**
   1. **REQUIRED SUB-SKILL: `craft-states`.** Its written state list and its stop come first.
   2. **Open direction?** Only when the person asked for ideas, or when two structurally different layouts are plausible and neither the brief nor the system chooses between them → **REQUIRED SUB-SKILL: `craft-explore`** before drawing the states. For several pages, ask at the scope stop which page (if any) gets options; never run an option round per page by default. The states are then drawn in the picked direction. A screen that follows an existing pattern goes straight to drawing.
   3. **Draw** the main state, then the other states, **using only the system's pieces and tokens**. Something new (a component, a colour, a size the scale doesn't have) → **REQUIRED SUB-SKILL: `craft-system`** (add mode) before using it. A component that **exists in code but isn't drawn in the tool** ("in code only" in the index) → **REQUIRED SUB-SKILL: `craft-sync`** (import of one component), drawing just that component first. If the person declined the import (see `DESIGN.md`), ask once before importing; if they still say no, build from the code's values on the board itself and note it. Never draw a look-alike, and never hard-code a new value in a page.
   4. **REQUIRED SUB-SKILL: `craft-critique` in self-check mode** on every board: render it, fix what it finds within this task's scope, and render again.
4. **Close.**
   - Show the result with the summary below.
   - Append the decisions to `DESIGN.md` › Decisions log (date, decision, why).
   - Move any question that got answered out of Open questions.

## Closing summary

Report `Made`, `Decisions` (also in `DESIGN.md` › Decisions log), `System changes` + affected screens, `Self-check fixed`, and `Open questions` using the template in [common mistakes & summary](references/common-mistakes.md).

## Rules

| Rule | Why |
|---|---|
| `DESIGN.md` first, every time | Without the brief every screen invents its own style |
| Scope confirmed before work when it's more than one item | Three pages built on a wrong reading is three pages wasted |
| States list before drawing (via `craft-states`) | The happy path is one state of many |
| Options only when the direction is open | Options on a solved pattern waste the person's attention |
| Only system pieces and tokens; new ones go through `craft-system` | Hard-coded values in pages are where drift starts |
| Code beats a stale brief; note it, don't override | The tokens are what ships; the brief is updated by decision, not silently |
| Self-check before showing | The person should review design, not catch mistakes |
| Decisions go into `DESIGN.md` | Next session's design starts from them, not from memory |

## Done when

Every item in the confirmed scope has its states drawn and self-checked, any system change has gone through `craft-system`, the closing summary has been given, and `DESIGN.md`'s Decisions log has been updated.

## Common mistakes

See [common mistakes](references/common-mistakes.md) before skipping any stop, overriding tokens locally, or showing unreviewed screens.
