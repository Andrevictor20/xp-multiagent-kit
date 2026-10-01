## 6. PRE-FLIGHT CHECKLIST (Filtro Obrigatório de Entrega)

Antes de considerar qualquer entrega de frontend concluída, valide rigorosamente:
- [ ] **Design Read declarado** em uma linha antes do código?
- [ ] **Dials explicitados** e coerentes com o briefing?
- [ ] **ZERO em-dashes (`—` ou `–`)** em toda a interface?
- [ ] **Page Theme Lock:** um único tema consistente para a página toda?
- [ ] **Color & Shape Consistency Lock:** acento e escala de bordas unificados?
- [ ] **Button Contrast Check:** texto do CTA passa em WCAG AA (mínimo 4.5:1)?
- [ ] **CTA Button Wrap:** nenhum botão de CTA quebra em 2+ linhas no desktop?
- [ ] **Hero Viewport Fit:** headline ≤ 2 linhas, subtexto ≤ 20 palavras, CTA visível sem scroll?
- [ ] **Hero Top Padding Cap:** `pt-24` no máximo no desktop?
- [ ] **Eyebrow Count:** número total de eyebrows ≤ `ceil(total_secoes / 3)`?
- [ ] **Split-Header banido:** sem parágrafo flutuando no canto superior direito do header?
- [ ] **Zigzag Alternation Cap:** no máximo 2 seções consecutivas de imagem+texto?
- [ ] **Bento Diversity:** células com variação visual real e contagem exata de itens?
- [ ] **Imagens Reais / Geradas:** sem divs simulando falsos screenshots de produto?
- [ ] **Sem `window.addEventListener('scroll')`:** uso exclusivo de Motion/ScrollTrigger/IntersectionObserver?
- [ ] **Prefers-reduced-motion** respeitado em todas as animações?
- [ ] **Viewport Stability:** uso de `min-h-[100dvh]`, nunca `h-screen`?
