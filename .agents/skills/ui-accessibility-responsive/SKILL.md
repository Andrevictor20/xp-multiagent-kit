---
name: ui-accessibility-responsive
description: Fluid responsive layout architecture and web accessibility (WCAG AA contrast, semantic ARIA, keyboard navigation).
---

# UI Accessibility & Responsive Layouts (`ui-accessibility-responsive`)

Consolida as disciplinas de **Layouts Responsivos Fluidos** e **Acessibilidade Digital (WCAG AA)**.

## 1. Arquitetura Responsiva Fluida
- Design mobile-first adaptativo para viewports de 320px até 4K.
- Áreas de toque confortáveis: mínimo de 48x48px para alvos interativos em mobile.
- Tipografia fluida utilizando `clamp()` sem quebra em zoom de 200%.

## 2. Acessibilidade WCAG 2.1 Nível AA
- **Contraste de Cores:** Mínimo de 4.5:1 para texto normal e 3.0:1 para texto grande e componentes gráficos essenciais.
- **Navegação por Teclado:** Ordem lógica de foco (Tab / Shift+Tab), sem armadilhas de teclado e com indicador de foco visível (`:focus-visible`).
- **Semântica HTML e ARIA:** Uso prioritário de elementos nativos (`<button>`, `<nav>`, `<main>`, `<dialog>`); uso de atributos ARIA apenas para suprir limitações semânticas.
