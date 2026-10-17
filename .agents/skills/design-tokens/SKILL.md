---
name: design-tokens
description: Semantic visual tokens with Color Consistency Lock and Concentric Shape Lock.
---

# Design Tokens

Bind UI styles exclusively to semantic tokens (`color.background`, `color.surface`, `color.accent`, `radius.outer`, `radius.inner`) rather than scattered raw literals.

## 1. Color Consistency Lock
- **Single Primary Accent:** Define at most 1 primary accent color with calibrated saturation (`< 80%`).
- **Full-Page Lock:** Lock the chosen accent across the entire page (never shift from purple in Hero to blue in Features to green in Footer).
- **Anti-Cliche Curated Palettes:**
  - *Cold Luxury:* `#F5F6F8` bg, `#0B0D10` text, `#1F242D` surface, `#4B68FF` or `#10B981` accent.
  - *Forest:* `#F8F9F5` bg, `#0E1711` text, `#1B2E22` deep surface, `#D97706` amber accent.
  - *Black and Tan:* `#0A0A0A` dark bg, `#EDEDED` text, `#161616` surface, `#C8A265` warm tan accent.
- **No Pure Black:** Use tinted off-black (`#0A0A0A`, `#111111`, `#0F172A`) instead of `#000000`.

## 2. Shape Consistency Lock & Concentric Radii
- **Unified Radius Scale:** Commit to one geometry family per product (sharp `4px-8px` or tactile `16px-24px`).
- **Concentric Math (Double-Bezel):** Compute nested inner radius strictly as:
  `radius_inner = max(0, radius_outer - padding)`
  Example: `rounded-[2rem]` outer container with `p-2` (`8px`) requires `rounded-[calc(2rem-8px)]` inner core.

## 3. Core Token Categories
- **Semantic Colors:** `background`, `surface`, `surface-elevated`, `text-primary`, `text-muted`, `accent`, `border-subtle`.
- **Typography:** `font-sans`, `font-display`, `font-mono`, `leading-tight`, `leading-relaxed`, `tracking-tighter`.
- **Spacing & Layout:** `gap-section` (`py-24` to `py-32`), `container-max` (`1400px`).
- **Motion Curves:** `ease-out-expo` (`cubic-bezier(0.16, 1, 0.3, 1)`), `duration-normal` (`300ms`).
