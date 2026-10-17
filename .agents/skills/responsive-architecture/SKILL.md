---
name: responsive-architecture
description: Fluid responsive layout architecture, mobile hierarchy, and 48px touch targets.
---

# Responsive Architecture

Treat responsiveness as structural content hierarchy across viewports, not an afterthought of media queries:
- **Mobile-First Content Priority:** Design information hierarchy for small viewports (`320px-430px`) first, then expand into multi-column desktop grids (`>= 768px`).
- **Fluid Layouts & Tokens:** Use CSS Grid/Flexbox, `clamp()` fluid typography, token-based breakpoints, and `min-h-[100dvh]` (never `100vh`).
- **Touch Ergonomics:** Enforce minimum `44x44px` (`48x48px` preferred) touch targets and prevent horizontal overflow (`overflow-x-hidden`).
