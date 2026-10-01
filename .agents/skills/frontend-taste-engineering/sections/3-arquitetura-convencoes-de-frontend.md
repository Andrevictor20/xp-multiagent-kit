## 3. ARQUITETURA & CONVENÇÕES DE FRONTEND

### 3.A Stack Padrão
* **Framework:** React / Next.js com Server Components (RSC).
  * **Interactivity Isolation:** Componentes com Motion, física ou listeners de scroll DEVEM ser folhas isoladas com `'use client'`.
* **Estilização:** Tailwind CSS (v4 preferido; v3 se projeto legado).
* **Animação:** `motion/react` (Motion / Framer Motion) para interações de UI; GSAP + ScrollTrigger para narrativas de scroll completas.
* **Ícones Permitidos:** `@phosphor-icons/react`, `hugeicons-react`, `@radix-ui/react-icons`, `@tabler/icons-react`. (Evitar `lucide-react` genérico por reflexo; padronizar `strokeWidth` globalmente em `1.5` ou `2.0`).
* **Emojis:** Proibidos por default em código e textos de UI. Use ícones SVG de bibliotecas reais.

### 3.B Layout & Viewport Stability
* **Altura de Viewport Segura:** NUNCA use `h-screen` para heros. SEMPRE use `min-h-[100dvh]` para evitar saltos de layout no mobile (barra de endereço do iOS Safari).
* **Grid sobre Cálculos Flex:** Use CSS Grid (`grid grid-cols-1 md:grid-cols-3 gap-6`) em vez de cálculos manuais de percentual flex (`w-[calc(33%-1rem)]`).
* **Largura Máxima:** Delimite containers com `max-w-7xl mx-auto` ou `max-w-[1400px]`.

---
