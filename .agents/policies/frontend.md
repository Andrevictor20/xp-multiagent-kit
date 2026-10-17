# Frontend Anti-Slop & Interactive Ergonomics Policy

1. **Token Anchoring First:** Discover and reuse project CSS variables/tokens before writing styles.
2. **6-State Machine:** Every interactive view/component must handle: Default, Hover/Focus, Active/Pressed, Loading (skeleton), Empty, and Error.
3. **Mobile & Viewport Ergonomics:** Use `100dvh` (never `100vh`), minimum `48x48px` touch targets, and GPU-safe animations (`transform`, `opacity`).
4. **Accessibility:** WCAG AA contrast (4.5:1 text), full keyboard navigation (`:focus-visible`), semantic HTML/ARIA.
