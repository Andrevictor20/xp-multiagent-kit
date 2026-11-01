---
name: ui-accessibility-responsive
description: Fluid responsive layout architecture and web accessibility (WCAG AA contrast, semantic ARIA, keyboard navigation).
---

# UI Accessibility & Responsive Layouts (`ui-accessibility-responsive`)

Consolidates disciplines of **Fluid Responsive Layouts** and **Digital Accessibility (WCAG AA)**.

## 1. Fluid Responsive Architecture
- Mobile-first adaptive design supporting viewports from 320px to 4K displays.
- Comfortable touch targets: minimum 48x48px for interactive elements on mobile.
- Fluid typography using `clamp()` without layout breakage at 200% zoom.

## 2. WCAG 2.1 Level AA Accessibility
- **Color Contrast:** Minimum 4.5:1 for normal text and 3.0:1 for large text and essential graphical components.
- **Keyboard Navigation:** Logical focus order (Tab / Shift+Tab), zero keyboard traps, and visible focus indicator (`:focus-visible`).
- **Semantic HTML & ARIA:** Prioritize native HTML elements (`<button>`, `<nav>`, `<main>`, `<dialog>`); use ARIA attributes only to bridge semantic gaps.
