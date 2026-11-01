# Frontend & Design System Policy

## 1. Design System & Token Governance
1. **8pt Spatial Grid:** Layout spacing and sizing conform strictly to standard increments (`4px`, `8px`, `16px`, `24px`, `32px`, `48px`).
2. **Color Lock:** Use semantic CSS tokens for surface, text, and accent styling. Raw hardcoded hex values in component styling are prohibited.
3. **Shape Lock:** Maintain uniform border-radius hierarchy across nested elements (concentric curvature).

## 2. Interactive Ergonomics & Anti-Slop
1. **6-State Machine:** Every interactive component must handle: Default, Hover/Focus, Active/Pressed, Loading (skeleton), Empty, and Error states.
2. **Viewport & Mobile Ergonomics:** Use dynamic viewport units `100dvh` (never static `100vh`), touch targets minimum `48x48px`, and GPU-safe transitions (`transform`, `opacity`).
3. **Accessibility (WCAG AA):** Ensure minimum 4.5:1 text contrast, complete keyboard accessibility (`:focus-visible`), and semantic HTML/ARIA attributes.
