---
name: industrial-brutalist-ui
description: Industrial brutalist UI engineering: 90-degree grids, Swiss print, CRT telemetry.
---

# Industrial Brutalism & Tactical Telemetry UI

Engineer dense, mechanical, high-authority interfaces inspired by Swiss industrial print and tactical telemetry.

## 1. Visual Archetypes (Choose ONE Per Project)

### 1.1 Swiss Industrial Print (Light Mode)
- Matte documentation paper canvas (`#F4F4F0` or `#EAE8E3`).
- Solid charcoal ink text and structural rules (`#050505` or `#111111`).
- Single hazard/aviation red accent (`#E61919` or `#FF2A2A`) for active markers and heavy dividers.

### 1.2 Tactical Telemetry & CRT Terminal (Dark Mode)
- Powered-down CRT off-black canvas (`#0A0A0A` or `#121212`, never `#000000`).
- Phosphor white primary text (`#EAEAEA`).
- Single status accent: Aviation Red (`#E61919`) or Terminal Green (`#4AF626`) reserved strictly for live telemetry indicators.

## 2. Typographic Architecture
- **Macro-Typography (Structural Headers):** Heavy Neo-Grotesque (`Neue Haas Grotesk Black`, `Archivo Black`, `Monument Extended`), fluid `clamp(3.5rem, 8vw, 12rem)`, tight negative tracking (`-0.03em` to `-0.06em`), compressed leading (`0.85`-`0.95`), uppercase.
- **Micro-Typography (Data & Telemetry):** Technical Monospace (`JetBrains Mono`, `IBM Plex Mono`, `Space Mono`), `11px-13px`, wide tracking (`0.06em-0.1em`), uppercase for coordinates, timestamps, and unit labels (`tabular-nums`).

## 3. Spatial Engineering & 90-Degree Grids
- **Exposed Hairline Grid:** `display: grid; gap: 1px;` over a contrasting background to form crisp 1px structural cell borders.
- **Strict 90-Degree Geometry:** Zero `border-radius` (`rounded-none` everywhere).
- **Industrial Markers:** Bracketed status tags (`[ SYS.ONLINE ]`), directional chevrons (`>>>`), and crosshair intersection markers (`+`).

## 4. Analog Surface Treatments
- **Subtle Scanlines:**
  ```css
  background-image: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.08) 2px, rgba(0,0,0,0.08) 4px);
  ```
- **Mechanical Grain:** Fixed SVG noise overlay (`pointer-events-none`); zero soft drop shadows or blurred gradients.
