---
name: component-architecture
description: Componentes modulares, estados e micro-interações.
---

# Component Architecture (Modern AI Design Standard)

Padrões de engenharia para componentes de UI robustos, táteis e fiéis ao design system:

---

## 0. Regra de Ouro: Token Anchoring First
A IA **NUNCA** gera código visual antes de inspecionar os tokens existentes no projeto (`tokens.ts`, `theme.ts`, `ThemeContext.tsx`, `tailwind.config.*` ou CSS vars).
- **Proibição de Hexadecimais Arbitrários:** Proibido inventar `#3b82f6` ou `#1e293b`. Use sempre `colors.surface`, `colors.primary`, `colors.border`, etc.
- **Escala de Espaçamento 8pt:** Utilize múltiplos estritos de 4px/8px (`gap-1 (4px)`, `gap-2 (8px)`, `gap-3 (12px)`, `gap-4 (16px)`, `gap-6 (24px)`, `gap-8 (32px)`). Proibido valores ímpares aleatórios (`gap-[17px]`).

---

## 1. Padrões Estruturais Avançados

### 1.A The "Double-Bezel" (Doppelrand / Chassi Usinado)
- Envolva componentes e cartões principais em uma estrutura de duas camadas:
  - **Casca Externa:** `bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/10 p-2 rounded-[2rem]`.
  - **Núcleo Interno:** `bg-white dark:bg-zinc-900 rounded-[calc(2rem-8px)] p-6 shadow-sm`.
- **Raios Concêntricos:** $\text{radius}_{\text{interno}} = \max(0, \text{radius}_{\text{externo}} - \text{padding})$.

### 1.B Nested CTA & "Button-in-Button"
- Botões primários em pílula com o ícone de ação (`↗`) aninhado em seu próprio círculo interno (`w-8 h-8 rounded-full bg-black/10 flex items-center justify-center`).
- Micro-interação no hover deslocando a seta na diagonal e aplicando `active:scale-[0.98]` no clique/toque.

### 1.C Bento Grid com Contagem Exata & Diversidade Visual
- Uma grade Bento deve ter exatamente o número de células do conteúdo disponível ($N$ itens $\rightarrow N$ células). Sem buracos ou células vazias no final.
- Pelo menos 2 a 3 células devem ter variação visual real (imagem, gradiente tonal suave, destaque de contraste), não apenas texto branco idêntico em todas.

---

## 2. Ergonomia Móvel & Viewport Real

1. **Alvos de Toque Mínimos:**
   - Mínimo de **48x48px** em mobile e **40x40px** em desktop (adicione padding ou `hitSlop` compensatório se o ícone for menor).
2. **Segurança de Teclado (Mobile):**
   - Inputs e docks de digitação devem usar `KeyboardAvoidingView` com comportamento específico da plataforma (`behavior={Platform.OS === 'ios' ? 'padding' : undefined}`) e folga inferior para docks ancorados.
3. **Safe Areas & Viewport:**
   - Use `useSafeAreaInsets` no topo (notch) e na base (home bar). Em web, use `min-h-[100dvh]`.

---

## 3. Máquina de 6 Estados Obrigatória

Todo componente interativo ou dependente de dados deve prever e implementar:
1. **Default State:** Visual polido, legibilidade e contraste WCAG AA (≥ 4.5:1).
2. **Hover & Focus State:** Realce visual suave e anel de foco acessível (`focus-visible:ring-2`).
3. **Active / Pressed State:** Simulação de clique tátil (`active:scale-[0.98]` com transição suave ≤ 150ms).
4. **Loading State:** Skeleton loader / Shimmer espelhando o formato final exato (sem spinners soltos no vazio).
5. **Empty State:** Visual composto com ilustração/ícone, mensagem acolhedora e CTA de primeira ação.
6. **Error State:** Borda de alerta sutil, mensagem de erro amigável e botão de reintento (*Retry*).

