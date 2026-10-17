---
name: minimalist-ui
description: Utilitarian minimalist UI (Linear/Notion aesthetic), 1px borders, whitespace.
---

# Minimalist UI: Utilitarian Minimalism & Editorial Precision

Design high-craft workspace and editorial interfaces (Linear/Notion aesthetic) that reject bloated SaaS clichés.

## 1. Strict Negative Constraints (What NEVER to Use)
- **No Default Fonts:** Avoid unstyled `Inter`, `Roboto`, `Arial`, or `Open Sans`.
- **No Heavy Shadows:** Ban `shadow-md`, `shadow-lg`, `shadow-xl`; use crisp `1px` borders or ultra-diffuse shadows (`opacity < 0.04`).
- **No Neon Gradients or Pill Cards:** Never use `rounded-full` on cards/containers; keep card radii crisp (`4px-12px`).
- **No Emojis as UI Icons:** Use crisp vector glyphs (Phosphor, Lucide, Radix).
- **No Fake Placeholder Data:** Replace `"John Doe"` / `"Acme Corp"` / `"99.9%"` with realistic domain values (`47.2%`, realistic names).

## 2. Typographic Architecture
- **Primary Sans (UI & Body):** `Geist Sans`, `SF Pro Display`, `Switzer`, `Plus Jakarta Sans`.
- **Editorial Serif (Hero Headlines & Pull Quotes):** `Newsreader`, `Lyon Text`, `PP Editorial New` with tight tracking (`-0.02em` to `-0.04em`) and compact line-height (`1.1`).
- **Monospace (Code, Shortcuts, Metrics):** `Geist Mono`, `JetBrains Mono`, `IBM Plex Mono` (`tabular-nums`).
- **Text Hierarchy:** Primary body in off-black (`#111111` or `#2F3437`, `leading-relaxed`); muted metadata in warm grey (`#787774`).

## 3. Warm Monochromatic Palette & Spot Pastels
- **Canvas:** Pure White `#FFFFFF` or Warm Bone `#F7F6F3` / `#FBFBFA`.
- **Elevated Surface:** `#FFFFFF` or `#F9F9F8` with `1px solid #EAEAEA` (`rgba(0,0,0,0.06)`).
- **Washed Spot Pastels (Badges/Tags Only):**
  - Pale Red `#FDEBEC` (text `#9F2F2D`) • Pale Blue `#E1F3FE` (text `#1F6C9F`)
  - Pale Green `#EDF3EC` (text `#346538`) • Pale Yellow `#FBF3DB` (text `#956400`)

## 4. Component Specifications & Subtle Motion
- **Bento Grids:** Asymmetric CSS Grid with `1px solid #EAEAEA` hairlines, `8px-12px` radius, `24px-40px` padding.
- **Primary CTA:** Solid `#111111` background, `#FFFFFF` text, `4px-6px` radius, `box-shadow: none`, `active:scale-[0.98]`.
- **Keystroke `<kbd>` Badges:** `border: 1px solid #EAEAEA`, `border-radius: 4px`, `background: #F7F6F3`, monospace.
- **GPU-Safe Scroll Entry:** `translateY(12px)` + `opacity: 0` -> `translateY(0)` over `600ms` (`cubic-bezier(0.16, 1, 0.3, 1)`) via `IntersectionObserver` with `80ms` stagger.
