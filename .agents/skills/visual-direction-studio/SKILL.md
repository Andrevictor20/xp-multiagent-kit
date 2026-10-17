---
name: visual-direction-studio
description: Deliberate $150k+ visual direction, Hero discipline, and Anti-Slop layout rules.
---

# Visual Direction Studio (Anti-Slop Art Direction)

Direct every frontend interface with the rigor of an elite design studio ($150k+ tier), eliminating generic AI templates and visual repetition.

## 1. Step 0: Design Read & The Three Dials
Calibrate before writing code:
- **`DESIGN_VARIANCE` (1-10):** Asymmetric experimentation (`7-9` creative/marketing, `4-6` editorial/SaaS, `3` high-accessibility utility).
- **`MOTION_INTENSITY` (1-10):** Choreography depth (`6-8` landing pages, `3-4` productivity workspaces).
- **`VISUAL_DENSITY` (1-10):** Information density (`3-4` airy marketing, `7-8` data cockpits/dashboards).

## 2. Strict Hero Discipline
- **Fits Initial Viewport (`min-h-[100dvh]`):** Headline max 2 lines on desktop; subheadline max **20 words**; CTAs visible above the fold.
- **Top Padding Cap:** Max `pt-24` (`~6rem`) on desktop so content never sinks.
- **4-Element Hero Stack Cap:** (1) Eyebrow OR Brand Strip (pick at most 1), (2) H1 Headline, (3) <=20-word Subheadline, (4) CTA group (1 primary + max 1 secondary).
- **Logo Wall Below Hero:** Place client/trust logos in a dedicated strip directly **below** the Hero, never crammed inside it.

## 3. Section Anti-Repetition Rules
- **Layout Diversity:** Use at least **4 distinct layout families** across an 8-section page (asymmetric split, bento grid, editorial pull-quote, interactive showcase).
- **Zigzag Cap:** Maximum 2 consecutive alternating image+text split sections (3rd consecutive is forbidden).
- **Eyebrow Cap:** Max 1 uppercase eyebrow pill per 3 sections (<= 3 total on a 9-section page).
- **Ban Split-Header:** Stack section headings and lead paragraphs vertically (`max-w-[65ch]`) instead of floating paragraphs in the top-right corner.

## 4. Typography, Color Lock & Punctuation Ban
- **Absolute Em-Dash Ban (`—` / `–`):** Never use em-dashes or en-dashes in UI copy; use periods, commas, colons, or standard hyphens `-`.
- **Distinctive Fonts:** Prefer `Geist`, `Cabinet Grotesk`, `Satoshi`, `Outfit`, `Plus Jakarta Sans` over default `Inter`.
- **The Lila Ban & Color Lock:** Ban default purple/indigo AI glow gradients and cliché beige/brass palettes; lock a single calibrated accent across the entire page on neutral Zinc/Slate/Stone surfaces.

## 5. Two-Pass Execution & Style Presets
1. **Pass 1 (Design Plan):** Lock Dials, hex palette roles, font pair, layout sequence, and signature visual element.
2. **Pass 2 (Anti-Slop Critique):** Audit against all rules above before coding.
- **Style Presets:** Activate `minimalist-ui` (Linear/Notion 1px borders), `industrial-brutalist-ui` (90° grids & monospace), or `high-end-visual-design` (Double-Bezel & spring physics) on demand.
