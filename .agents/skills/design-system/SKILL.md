---
name: design-system
description: Unified design system architecture covering semantic tokens, 6-state modular components, and reusable component catalog governance.
---

# Design System (`design-system`)

Consolida a governança visual: **Design Tokens Semânticos**, **Arquitetura de Componentes** e **Catálogo de Reutilização**.

## 1. Tokens de Design Semânticos
- Nomes baseados em propósito e semântica (`--color-surface-primary`, `--color-text-muted`, `--spacing-md`), nunca em cores físicas literais.
- Suporte a temas claro/escuro via variáveis CSS nativas sem duplicação de layouts.
- **Concentric Shape Lock:** Raios de borda proporcionais e aninhamento visual harmonioso.

## 2. Máquina de Estados de 6 Fases
- Todo componente interativo deve prever explicitamente os 6 estados:
  1. **Idle:** Estado neutro de repouso.
  2. **Hover:** Feedback visual sutil ao passar o cursor.
  3. **Active/Focus:** Anel de foco visível com alto contraste.
  4. **Loading:** Skeleton ou spinner sem salto de layout (CLS zero).
  5. **Disabled:** Visualmente atenuado com `aria-disabled="true"`.
  6. **Error:** Borda de aviso e mensagem acessível com `aria-live`.

## 3. Modularidade & Catálogo de Componentes
- Componentes puros e desacoplados, aceitando composição e slots.
- Catálogo centralizado para prevenir duplicações acidentais de botões, modais e cards.
