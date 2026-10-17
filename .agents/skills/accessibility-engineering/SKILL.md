---
name: accessibility-engineering
description: Web accessibility: keyboard navigation, WCAG AA contrast, and semantic ARIA.
---

# Accessibility Engineering

Verify every new UI component or view against strict accessibility standards:
- **Keyboard Navigation:** Full operability via `Tab`, `Shift+Tab`, `Enter`, `Space`, arrow keys, and `Escape`.
- **Focus Management:** Visible focus rings (`focus-visible:ring-2`) and focus trapping inside modals/dialogs.
- **Semantic HTML:** Use native `<button>`, `<form>`, `<label>`, `<nav>`, `<main>`, and sequential headings (`<h1>`-`<h6>`).
- **Contrast (WCAG AA):** Minimum `4.5:1` for normal text, `3:1` for large text and interactive boundaries/focus indicators.
- **Motion Sensitivity:** Respect `prefers-reduced-motion` by collapsing animations into instant transitions.

Broken critical accessibility is a release blocker.
