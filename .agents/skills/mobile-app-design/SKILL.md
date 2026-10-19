---
name: mobile-app-design
version: 1.0.0
description: Native and cross-platform mobile app UI/UX: platform units, safe areas, thumb zone, navigation, accessibility, and mobile design systems.
author: André Victor
license: MIT
tags: [mobile, ios, android, react-native, flutter, swiftui, compose, ux, cursor, claude-code]
compatibility: [cursor, claude-code, codex, gemini-cli, opencode]
entrypoint: SKILL.md
---

# Mobile App Design

Web rules do not transfer 1:1 to mobile. Apply this skill for iOS, Android, React Native, Flutter, and hybrid apps. Kit locks still apply (single accent, semantic tokens, WCAG AA, 6 states).

## 1. Workflow
1. Token Discovery: reuse existing theme/tokens first.
2. `python3 scripts/design_search.py --mobile "<app brief>" [--persist]` for archetype, navigation, base system, palette, and rules.
3. Browse systems: `--domain systems "react native"`; rules: `--domain mobile "keyboard"`.
4. Implement with the chosen system; customize tokens, never ship its default theme.
5. Verify on real devices or simulators at the largest text size, dark mode, and with a screen reader.

## 2. Platform Units & Targets
- iOS points (pt): targets >= **44x44pt**. Android dp/sp: targets >= **48x48dp**, 8dp spacing.
- Never use `100vh`/web units; use safe-area insets on all edges (notch, Dynamic Island, home indicator, gesture bar).

## 3. Navigation & Ergonomics
- 3-5 primary destinations in a bottom tab bar (iOS) / Navigation Bar (Android); rail on tablets.
- Primary actions in the lower thumb zone; top corners for secondary actions only.
- Support swipe-back (iOS) and predictive back (Android); every custom gesture needs a visible alternative.
- Prefer bottom sheets for contextual actions; avoid stacked full-screen modals.

## 4. Mobile States & Resilience
- Cover the 6 states plus **Offline** and **Permission denied**.
- Cache last good data; offline banner with retry; never lose typed input.
- Ask permissions in context after explaining value; allow value before sign-up.

## 5. Accessibility & Performance
- Dynamic Type / font scale up to 200%; VoiceOver/TalkBack labels, roles, traits.
- Honor Reduce Motion; transitions <= 300ms; animate transform/opacity.
- Virtualize long lists, size images to display, target 60fps; no heavy work on the UI thread.

## 6. Precedence
Existing project theme -> kit locks -> platform guidelines (HIG / Material 3) -> `design-intelligence` catalog. When HIG and Material conflict, follow the platform the user is on; for cross-platform, adapt per OS only where behavior differs (navigation, back, haptics, type).
