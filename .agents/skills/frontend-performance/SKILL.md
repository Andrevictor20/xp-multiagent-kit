---
name: frontend-performance
description: Core Web Vitals (LCP, INP, CLS), 60fps GPU animations, and scroll optimization.
---

# Frontend Performance & Core Web Vitals

Enforce 60+ FPS rendering, instant load times, and top Lighthouse scores across web and mobile viewports.

## 1. Hardware Acceleration & GPU-Safe Animations
- **Compositor-Only Properties:** Animate **only** `transform` and `opacity`. NEVER animate `top`, `left`, `width`, or `height` (triggers layout reflow and paint thrashing).
- **Scoped `will-change: transform`:** Apply only to actively animating elements.

## 2. DOM Cost, Blur & Noise Safeguards
- **Restricted `backdrop-blur`:** Apply `backdrop-filter: blur(...)` ONLY to fixed/sticky elements (navbars, modals). NEVER apply blur to scrolling containers (destroys mobile FPS).
- **Fixed Noise/Grain Layer:** Render SVG noise overlays on a single fixed layer (`fixed inset-0 z-50 pointer-events-none`).
- **Systematic Z-Index Scale:** Ban magic numbers (`z-[9999]`); use token scale (`nav: 40`, `modal: 50`, `grain: 60`).

## 3. Scroll & State Management
- **Ban Raw Scroll Listeners:** Never attach `window.addEventListener('scroll', ...)`. Use Motion `useScroll()`, GSAP `ScrollTrigger`, or `IntersectionObserver`.
- **Zero Per-Frame React State:** Never call `setState` on scroll ticks or `mousemove`; bind `useMotionValue` and `useTransform` outside React's render loop.

## 4. Core Web Vitals Targets
- **LCP (Largest Contentful Paint) < 2.5s:** Preload Hero media (`priority` / `fetchpriority="high"`), serve `.webp`/`.avif`, and lazy-load below-the-fold images (`loading="lazy"`).
- **INP (Interaction to Next Paint) < 200ms:** Keep main thread unblocked; yield or offload heavy computation.
- **CLS (Cumulative Layout Shift) < 0.1:** Reserve explicit `width`/`height` or `aspect-ratio` on all media, fonts, and dynamic embeds.
