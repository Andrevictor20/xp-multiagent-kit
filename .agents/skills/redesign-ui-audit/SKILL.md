---
name: redesign-ui-audit
description: Surgical UI audit and modernization without breaking existing layouts.
---

# Redesign UI Audit: Surgical Interface Modernization

Upgrade existing web and mobile interfaces to a high-craft visual standard without breaking functional layouts (`Scan -> Diagnose -> Fix`).

## 1. Execution Cycle
1. **Scan:** Inspect existing framework, styling system (Tailwind, CSS Modules, Vanilla CSS), and tokens.
2. **Diagnose:** Audit against the checklist below to flag AI clichés and visual weaknesses.
3. **Fix:** Apply incremental, surgical upgrades within the current stack rather than rewriting from scratch.

## 2. Redesign Audit Checklist

### Typography
- [ ] Replace generic browser/Inter defaults with distinctive fonts (`Geist`, `Cabinet Grotesk`, `Satoshi`, `Outfit`).
- [ ] Apply tight tracking on display headings (`tracking-tight`) and wider tracking on uppercase metadata.
- [ ] Constrain body measure to `~65ch` with `line-height: 1.6`.
- [ ] Enforce `tabular-nums` / monospace on all numeric counters and tables.

### Colors & Surfaces
- [ ] Replace pure `#000000` backgrounds with tinted charcoal/off-black (`#0A0A0A`, `#121212`).
- [ ] Cap accent saturation below `80%` and remove generic purple/blue AI glows in favor of a single locked accent.
- [ ] Tint shadows to match surface hue; eliminate jarring dark sections dropped mid-scroll on light pages.

### Layout & Alignment
- [ ] Upgrade monotonous 3-equal-card rows into asymmetric bento grids or 2-column splits.
- [ ] Replace `100vh` / `h-screen` with `min-h-[100dvh]` for iOS Safari stability.
- [ ] Constrain page containers (`max-w-7xl mx-auto`) and align card CTAs at the bottom (`mt-auto`).

### Interactivity & States
- [ ] Add tactile press feedback (`active:scale-[0.98]`) and visible keyboard focus rings (`focus-visible:ring-2`).
- [ ] Replace generic spinners with layout-matching skeleton loaders and smooth `200-300ms` transitions.

## 3. Priority Fix Order (Highest Impact, Lowest Risk)
1. Typography swap -> 2. Color palette cleanup -> 3. Hover/active/focus states -> 4. Spacing & grid rhythm -> 5. Bento/asymmetric layout upgrades -> 6. Empty/loading/error state polish.
