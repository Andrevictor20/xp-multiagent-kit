---
name: ui-quality-gate
description: Pre-release UI checklist: WCAG AA contrast, 100dvh viewport, and Anti-Slop gate.
---

# UI Quality Gate

Run this mandatory pre-commit / pre-release verification checklist on every frontend or UI task before delivery.

## 1. Accessibility & Contrast (WCAG AA)
- [ ] **Body & Heading Contrast:** Meets `>= 4.5:1` for normal text and `>= 3:1` for large text.
- [ ] **CTA Button Contrast:** Button label is high-contrast against button fill (ban white-on-white or invisible ghost buttons).
- [ ] **Form Control Contrast:** Input borders, placeholders, helper text, and error states pass contrast checks.
- [ ] **Keyboard Focus:** Every interactive element displays a visible focus ring (`focus-visible:ring-2`).
- [ ] **Semantic HTML:** Uses native `<button>`, `<a>`, `<nav>`, `<main>`, `<section>` (zero clickable `<div onClick>`).

## 2. Responsiveness & Viewport Stability
- [ ] **Dynamic Viewport Height:** Uses `min-h-[100dvh]` for full-height heroes/modals (**never `h-screen` or `100vh`**).
- [ ] **Single-Line Desktop Navbar:** Top navigation fits on one line on desktop (`max-h-[80px]`).
- [ ] **No Wrapped CTA Labels:** Primary CTA button labels stay on a single line without awkward text wrapping.
- [ ] **Mobile Grid Collapse:** Multi-column/asymmetric grids collapse cleanly to `grid-cols-1 w-full px-4` below `768px`.

## 3. Motion & Rendering Performance
- [ ] **Reduced Motion Support:** Respects `prefers-reduced-motion` with instant/static transitions.
- [ ] **Zero Window Scroll Listeners:** Uses `IntersectionObserver`, Motion `useScroll`, or GSAP `ScrollTrigger` (never `window.addEventListener('scroll')`).
- [ ] **GPU-Safe Properties:** Animates only `transform` and `opacity`; restricts `backdrop-blur` to fixed elements.

## 4. Anti-Slop Aesthetic Filter
- [ ] **Zero Em-Dashes (`—` / `–`):** None in headlines, eyebrows, buttons, pills, or body copy.
- [ ] **No Fake Div Mockups:** Uses real or generated visual assets rather than crude `<div>` wireframe placeholders.
- [ ] **Disciplined Hero:** Max 2 headline lines, `<= 20` subheadline words, primary CTA visible above the fold.
- [ ] **Page Theme & Color Lock:** Single consistent theme and primary accent from top to bottom.
