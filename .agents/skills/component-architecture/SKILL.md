---
name: component-architecture
description: Modular UI components, token anchoring, 6-state machine, and mobile ergonomics.
---

# Component Architecture

Engineer tactile, accessible, and design-system-compliant UI components.

## 0. Golden Rule: Token Anchoring First
**NEVER** generate UI code before inspecting existing project tokens (`tokens.ts`, `theme.ts`, `tailwind.config.*`, or CSS variables).
- **Ban Arbitrary Hex Codes:** Never hardcode `#3b82f6` or `#1e293b`; bind semantic tokens (`colors.surface`, `colors.primary`, `colors.border`).
- **8pt Spacing Scale:** Use strict 4px/8px multiples (`gap-1` 4px, `gap-2` 8px, `gap-3` 12px, `gap-4` 16px, `gap-6` 24px, `gap-8` 32px). Ban arbitrary values like `gap-[17px]`.

## 1. Structural Component Patterns
- **1.A Double-Bezel (Concentric Chassis):**
  - *Outer Shell:* `bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/10 p-2 rounded-[2rem]`.
  - *Inner Core:* `bg-white dark:bg-zinc-900 rounded-[calc(2rem-8px)] p-6 shadow-sm`.
  - *Concentric Formula:* `radius_inner = max(0, radius_outer - padding)`.
- **1.B Nested Pill CTA ("Button-in-Button"):**
  - Pill button housing a trailing action icon (`↗`) inside its own circular badge (`w-8 h-8 rounded-full bg-black/10 flex items-center justify-center`), shifting diagonally on hover with `active:scale-[0.98]`.
- **1.C Exact-Count Bento Grid:**
  - Match grid cells strictly to item count ($N$ items -> $N$ cells, zero orphan holes) with visual variation across cells.

## 2. Mobile Ergonomics & Real Viewport
1. **Touch Targets:** Minimum **48x48px** on mobile and **40x40px** on desktop.
2. **Keyboard Safety:** Wrap mobile inputs/docks in `KeyboardAvoidingView` (`behavior={Platform.OS === 'ios' ? 'padding' : undefined}`).
3. **Safe Areas & Viewport:** Respect `useSafeAreaInsets` and use `min-h-[100dvh]` on web (never `100vh`).

## 3. Mandatory 6-State Machine
Every interactive or data-driven component must implement:
1. **Default:** Polished layout with WCAG AA contrast (>= 4.5:1).
2. **Hover & Focus:** Subtle elevation and accessible focus ring (`focus-visible:ring-2`).
3. **Active / Pressed:** Tactile depression (`active:scale-[0.98]`, transition <= 150ms).
4. **Loading:** Geometry-matched skeleton/shimmer (no bare floating spinners).
5. **Empty:** Composed illustration/icon, helpful copy, and primary creation CTA.
6. **Error:** Subtle alert border, human-readable explanation, and *Retry* action.
