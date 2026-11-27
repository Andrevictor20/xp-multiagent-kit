---
name: vito-prototype-fidelity
description: "Fidelidade visual 1:1 no Vito mobile (Reanimated 4, Android AVD e diff de imagem)."
---

# Vito Prototype Fidelity Loop (Zero-Guesswork)

Nunca edite UI do Vito mobile "no escuro" nem declare tela pronta apenas com testes unitários ou `expo web`.

## Stack Obrigatória
- **Motor de animação:** `react-native-reanimated` v4 (`CSS Animations / Keyframes / Transitions` ou `useSharedValue` + `useAnimatedStyle` na UI thread). Proibido usar `Animated` legado com `useNativeDriver: false` em animações de tela, transições ou mascote.
- **Mascote (`500x500`):** animar partes articuladas (corpo, chapéu, olhos, gravata, FX) na UI thread via `Reanimated 4` (camadas nativas `Animated.View` ou `@shopify/react-native-skia`), mantendo 60–120fps constantes.
- **Gradientes e Blur:** usar `expo-linear-gradient` e `expo-blur` conforme computed styles do protótipo.

## Loop Fechado por Fatia (1 tela/módulo por vez)
1. **Inspecionar protótipo real (`chrome-devtools` MCP):**
   - Abrir `file:///home/andrevmp/Downloads/vito/Vito-telas-atualizadas.html` em `390x844` (Light e Dark via `data-theme`).
   - Consultar `get_computed_styles` e `get_element_box_model` dos elementos-chave em vez de reler os 551 KB de HTML.
   - Capturar screenshot de referência (`take_screenshot`).
2. **Implementar em React Native (`Reanimated 4` + `animatereactnative` skill):**
   - Aplicar cores exatas (Light e Dark), espaçamentos, bordas hairline, tipografia (`Geist` / `Geist Mono`), curvas `cubic-bezier` e durações idênticas.
3. **Validar no Emulador Android (`mobile-mcp`):**
   - Garantir AVD `vito_pixel` rodando (`adb devices`).
   - Navegar até a tela/estado real no app e capturar screenshot real do Android.
4. **Diff objetivo (`image-compare` MCP):**
   - Comparar screenshot do protótipo vs. screenshot real do Android com `compare_images`.
   - Corrigir divergências reais (cores, alinhamento, proporção, estados Dark/Light) até atingir fidelidade visual antes de avançar para a próxima tela.
