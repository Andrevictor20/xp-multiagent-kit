---
name: visual-regression
description: Visual regression testing across viewports, interactive states, and dark mode.
---

# Visual Regression Guardian

Ensure code changes never break visual fidelity, alignment, or theming across the application:
- **Baseline Comparison:** Compare rendered component/page snapshots against approved baselines across mobile (`375px`), tablet (`768px`), and desktop (`1440px`) viewports.
- **Interactive States & Themes:** Verify all 6 component states (`default`, `hover`, `focus`, `active`, `loading`, `error/empty`) and both Light/Dark modes via semantic tokens.
- **Behavioral + Visual QA:** Always pair visual snapshot checks with functional Playwright assertions (`browser-e2e-playwright`).
