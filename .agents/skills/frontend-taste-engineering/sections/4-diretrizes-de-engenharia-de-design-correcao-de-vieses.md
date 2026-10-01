## 4. DIRETRIZES DE ENGENHARIA DE DESIGN & CORREÇÃO DE VIESES

### 4.1 Tipografia
* **Headlines / Display:** `text-4xl md:text-6xl tracking-tighter leading-none`.
* **Corpo / Parágrafos:** `text-base text-gray-600 dark:text-gray-400 leading-relaxed max-w-[65ch]`.
* **Sans Font:** Evite `Inter` como padrão cego. Prefira `Geist`, `Outfit`, `Cabinet Grotesk`, `Satoshi`, `Plus Jakarta Sans`.
* **Disciplina de Serifas:** Serifa é RESTRITA a briefings genuinamente editoriais, luxo ou vintage.
  - Banimento específico como defaults: `Fraunces` e `Instrument_Serif` (favoritos de IA).
  - Quando justificada, rotacione fontes como *PP Editorial New, Tiempos Headline, Cormorant Garamond, Newsreader*.
* **Descendentes Itálicos:** Quando usar itálico com letras `y, g, j, p, q`, use `leading-[1.1]` e reserva `pb-1` para não cortar os traços.

### 4.2 Calibração de Cores & Lila Rule
* No máximo 1 cor de acento com saturação < 80%.
* **A Regra Lila:** Banido o reflexo automático de gradientes e botões roxos/azuis com glow. Use bases neutras (Zinc, Slate, Stone) com acentos singulares de alto contraste (Emerald, Electric Blue, Deep Rose, Burnt Orange).
* **Banimento da Paleta Padrão de IA:** Para produtos premium/artesanais, a IA sempre gera bege (#f5f1ea) + latão (#b08947) + espresso (#1a1714). Roteie para:
  - *Cold Luxury:* Cinza prata + cromo + fumaça.
  - *Forest:* Verde profundo + osso + âmbar.
  - *Black and Tan:* Off-black + tan quente com contraste nítido.
  - *Cobalt + Cream:* Azul saturado contra neutro único.
* **Color Consistency Lock:** O acento escolhido deve ser mantido de forma 100% consistente em toda a página.

### 4.3 Disciplina Rígida de Hero
* **O Hero DEVE caber na primeira viewport:** Headline em no máximo 2 linhas; subtexto com no máximo **20 palavras** e 3-4 linhas; CTAs visíveis sem rolagem.
* **Hero Top Padding Cap:** Máximo `pt-24` (≈6rem) no desktop para o conteúdo não flutuar no meio da tela.
* **Hero Stack Discipline:** No máximo 4 elementos no stack do Hero (1. Eyebrow OU Brand Strip; 2. Headline; 3. Subtexto; 4. CTAs). Logo wall de clientes/confiança pertence ABAIXO do Hero, nunca comprimido dentro dele.

### 4.4 Regras de Anti-Repetição de Seções
* **Variação de Layout de Seção:** Em uma página com 8 seções, use pelo menos 4 famílias de layout distintas. Nunca repita o mesmo layout em seções consecutivas.
* **Cap de Zigzag:** No máximo 2 seções consecutivas com divisão imagem+texto alternada. A 3ª consecutiva é proibida.
* **Restrição Mecânica de Eyebrows:** No máximo 1 eyebrow (rótulo pequeno em maiúsculas tracking largo) a cada 3 seções. Em uma página de 9 seções, use no máximo 3 eyebrows no total.
* **Ban de Split-Header:** Proibido o cabeçalho "título gigante na esquerda + parágrafo flutuando no canto superior direito". Se precisar de ambos, empilhe verticalmente (`max-w-[65ch]`).
* **Bento Diversity & Exact Count:** Grids Bento devem ter contagem exata de células (sem espaços vazios) e pelo menos 2 a 3 células com variação visual real (imagem, gradiente tonal, contraste), não apenas texto branco sobre branco.

### 4.5 Banimento Absoluto de Em-Dash (`—`)
* **Zero Em-Dashes:** O caractere `—` (travessão longo) e `–` (meia-risca) é expressamente proibido em headlines, eyebrows, botões, pills, body copy, citações e legendas. É a principal assinatura de texto gerado por IA. Use ponto final, vírgula, dois-pontos ou o hífen simples `-`.

---
