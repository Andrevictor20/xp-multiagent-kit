## 0. BRIEF INFERENCE & DESIGN READ (Ler o Contexto Antes de Qualquer Código)

A maior causa de interfaces ruins geradas por IA é o modelo pular direto para código adotando um default seguro (ex: fundo escuro com glow roxo, Inter em tudo, 3 cards simétricos).

### 0.A Sinais a Inspecionar Primeiro
1. **Tipo de Página:** Landing (SaaS B2B, Consumer, Agência, Evento), Portfólio (Dev, Designer, Estúdio), Redesign (Preservação vs Overhaul), Editorial / Blog.
2. **Palavras de Vibe do Usuário:** "Minimalista", "Calmo", "Linear-style", "Awwwards", "Brutalista", "Apple-like", "Playful", "B2B Sério", "Editorial", "Dark Tech".
3. **Sinais de Referência:** URLs citadas, marcas concorrentes, screenshots anexados.
4. **Público-Alvo:** Compradores corporativos B2B vs Consumidor exigente vs Recrutadores de design. O público dita a estética, não a preferência pessoal da IA.
5. **Restrições Silenciosas:** Acessibilidade crítica, setor público, fintechs reguladas, e-commerce de alta confiança. Essas restrições SOBREPÕEM preferências estéticas.

### 0.B Declaração de "Design Read" Obrigatória
Antes de gerar qualquer código de UI, declare em uma única linha:  
**"Reading this as: \<tipo de página> para \<público>, com linguagem \<vibe>, direcionado para \<design system ou família estética>."**

### 0.C Disciplina Anti-Default (O que NUNCA fazer por reflexo)
Não use por default: gradientes roxos/azuis de IA, hero centralizado sobre malha escura, 3 cards de features idênticos, glassmorphism genérico em tudo, micro-animações infinitas em todos os elementos, Inter + slate-900.

---
