## 2. BRIEF → MAPA DE DESIGN SYSTEMS

Não invente CSS do zero para padrões que possuem pacotes oficiais maduros:

### 2.A Quando usar Design Systems Oficiais
- **Enterprise / B2B SaaS / Dashboards Microsoft:** `@fluentui/react-components` (Fluent UI 9).
- **Google / Material Product:** `@material/web` + Material 3 Tokens.
- **IBM / Data Analytics Enterprise:** `@carbon/react` + `@carbon/styles`.
- **Shopify Apps:** `@shopify/polaris` / Polaris Web Components.
- **Atlassian / Ferramentas de Produtividade:** `@atlaskit/*` + `@atlaskit/tokens`.
- **DevTools / GitHub Style:** `@primer/css` ou `@primer/react-brand`.
- **Serviços Públicos:** `govuk-frontend` ou `uswds`.
- **React Moderno com Componentes Próprios:** `shadcn/ui` (`npx shadcn@latest add ...`) — customize tokens, nunca entregue no estado default puro.
- **Fundação Acessível & Temas:** `@radix-ui/themes`.

### 2.B Quando a Direção é uma Estética Nativa
- **Glassmorphism / Vidro Fosco:** `backdrop-filter`, bordas duplas em camadas e realce interno. Fornecer fallback sólido para `prefers-reduced-transparency`.
- **Bento Grid:** CSS Grid com células assimétricas mistas.
- **Brutalismo Industrial:** CSS nativo, tipografia monospace/neo-grotesque, bordas duras de 90°.
- **Editorial / Revista:** Tipografia com personalidade, grid assimétrico, espaços em branco generosos.
- **Dark Tech:** Tipografia mono + acento neon único, motivos de terminal.

---
