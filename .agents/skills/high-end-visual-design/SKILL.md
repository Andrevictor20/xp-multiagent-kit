---
name: high-end-visual-design
description: $150k+ Awwwards-tier visual design: Double-Bezel chassis and spring physics.
---

# High-End Visual Design & Motion Choreography ($150k+ Tier)

Craft digital interfaces with tactile hardware depth, generous spatial rhythm, concentric geometry, and fluid spring choreography.

## 1. Precision Component Architecture

### 1.A The "Double-Bezel" (Concentric Machined Chassis)
Never float a card with a flat grey border; build a two-layer chassis:
- **Outer Shell:** `bg-black/5 dark:bg-white/5 ring-1 ring-black/5 dark:border-white/10 p-2 rounded-[2rem]`.
- **Inner Core:** `bg-white dark:bg-zinc-900 shadow-[inset_0_1px_1px_rgba(255,255,255,0.15)] rounded-[calc(2rem-0.5rem)] p-6`.

### 1.B Nested Pill CTA ("Button-in-Button")
- Solid pill button (`rounded-full px-6 py-3`) with trailing arrow (`↗`) housed inside its own circular badge (`w-8 h-8 rounded-full bg-black/10 dark:bg-white/10 flex items-center justify-center`).
- Apply tactile press (`active:scale-[0.98]`) and diagonal icon shift on hover (`group-hover:translate-x-1 group-hover:-translate-y-[1px]`).

## 2. Spatial Rhythm & Macro-Whitespace
- **Generous Section Breathing:** Pad vertical sections with `py-24` to `py-40`.
- **Eyebrow Pills:** `rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em] font-medium` (max 1 per 3 sections).
- **Asymmetric Grids:** Pair asymmetric spans (`col-span-8` + `col-span-4`) that collapse cleanly to `grid-cols-1 w-full px-4` below `768px`.

## 3. Fluid & Spring Motion Choreography
- **Inertial Curves:** Replace `linear`/`ease-in-out` with custom spring/inertial curves:
  ```css
  transition: all 0.7s cubic-bezier(0.32, 0.72, 0, 1);
  ```
- **Scroll Reveal:** Progressive fade-up (`translate-y-12 blur-sm opacity-0` -> `translate-y-0 blur-0 opacity-100` over `700ms`).
- **Floating Island Navbar:** Detached glass pill navbar (`mt-6 mx-auto w-max rounded-full backdrop-blur-xl`).

## 4. Performance Guardrails
- **Strict GPU Acceleration:** Animate only `transform` and `opacity`.
- **Scoped Backdrop Blur:** Apply `backdrop-blur` only to fixed/sticky navbars and modals, never scrolling containers.
- **Fixed Grain Overlay:** Keep noise textures on a fixed `pointer-events-none` layer (`fixed inset-0 z-50 pointer-events-none`).
