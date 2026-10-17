---
name: design-system-architecture
description: Design System governance from semantic tokens and primitives to page templates.
---

# Design System Architecture

Enforce strict layered separation across the UI architecture:
1. **Design Tokens:** Semantic colors, typography scales, spacing, radii, shadows, motion curves.
2. **Primitives:** Unstyled layout/accessibility building blocks (`Box`, `Stack`, `Text`, `Portal`).
3. **Components:** Reusable interactive controls (`Button`, `Input`, `Dialog`, `Card`).
4. **Patterns:** Composed domain-agnostic flows (`DataTable`, `SearchFilterBar`, `FormSection`).
5. **Templates & Pages:** Route-level layouts binding domain data into patterns.

Treat the Design System as executable, reusable UI infrastructure rather than a static style guide.
