---
name: design-system
description: Unified design system architecture covering semantic tokens, 6-state modular components, and reusable component catalog governance.
---

# Design System (`design-system`)

Consolidates visual governance: **Semantic Design Tokens**, **Component Architecture**, and **Reusable Component Catalog**.

## 1. Semantic Design Tokens
- Names based on purpose and semantics (`--color-surface-primary`, `--color-text-muted`, `--spacing-md`), never physical color literals.
- Light/dark theme support via native CSS custom properties without duplicating layouts.
- **Concentric Shape Lock:** Proportional border radii and harmonious visual nesting.

## 2. 6-Phase State Machine
- Every interactive component must explicitly handle all 6 states:
  1. **Idle:** Neutral default resting state.
  2. **Hover:** Subtle visual feedback upon cursor hovering.
  3. **Active/Focus:** Visible focus ring with high contrast.
  4. **Loading:** Skeleton or spinner without layout shift (zero CLS).
  5. **Disabled:** Visually muted with `aria-disabled="true"`.
  6. **Error:** Warning border and accessible announcement with `aria-live`.

## 3. Modularity & Component Catalog
- Pure, decoupled components accepting composition and slots.
- Centralized component catalog preventing accidental duplicate creation of buttons, modals, and cards.
