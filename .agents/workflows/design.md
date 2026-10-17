---
name: design
description: "Dedicated UI/UX workflow: Token Discovery, 6-State Blueprint, Spring Physics, and Polish Gate."
---
# Design & UI Workflow (`/design`)

## Flow
1. **Phase 1 — Token Discovery:** Inspect existing design tokens/CSS variables before writing styles. Lock palette and border radius (Color & Shape Lock).
2. **Phase 2 — 6-State Blueprint:** Specify Default, Hover/Focus, Active/Pressed, Loading (skeleton), Empty, and Error states.
3. **Phase 3 — Implementation & Ergonomics:** Build modular components (< 500 lines), 8pt spatial grid, `100dvh` mobile viewport, touch targets ≥ 48px, GPU-safe animations (`transform`/`opacity`).
4. **Phase 4 — Polish Gate & Memory Sync:** Verify WCAG AA contrast, keyboard navigation, and OpenDesign lint (`od lint` if active), then update `.agents/memory/PROJECT_MEMORY.md`.

## Rules
- Anti-Slop aesthetic discipline mandatory. All user-facing communication in Portuguese.
