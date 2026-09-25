---
name: browser-e2e-playwright
description: Automação autônoma de testes de ponta a ponta (E2E) no navegador com Playwright headless, validação visual e captura de traces.
---

# Browser E2E Playwright Skill

Esta skill governa a criação, execução e diagnóstico de testes de integração ponta a ponta (**End-to-End**) no navegador web através do **Playwright** (ou Puppeteer), validando fluxos críticos de usuário, acessibilidade ao vivo, erros de console e performance real de renderização.

---

## 1. Princípios de Testes E2E Confiáveis (Anti-Flaky)
- **Zero Sleeps Artificiais:** Proibido o uso de `time.sleep()`, `page.waitForTimeout()` ou esperas arbitrárias. Use sempre localizadores reativos com auto-wait (`page.locator('text=...').toBeVisible()`).
- **Resiliência a Seletores:** Prefira atributos de acessibilidade ou teste semântico (`getByRole`, `getByTestId('checkout-submit-btn')`) em vez de seletores CSS frágeis ou XPaths complexos.
- **Isolamento de Estado:** Cada teste E2E deve iniciar em um contexto de navegador limpo (`BrowserContext`), sem cookies residuais ou dados em `localStorage`.

---

## 2. Padrão Canônico de Teste com Playwright

```typescript
import { test, expect } from '@playwright/test';

test.describe('Fluxo Crítico: Cadastro e Checkout', () => {
  test('deve completar compra com sucesso e sem erros no console', async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });

    await page.goto('/pricing');
    await page.getByRole('button', { name: /assinar plano pro/i }).click();

    await expect(page).toHaveURL(/.*checkout/);
    await page.getByLabel('Nome no Cartão').fill('João da Silva');
    await page.getByRole('button', { name: /confirmar pagamento/i }).click();

    await expect(page.getByText('Assinatura Confirmada!')).toBeVisible({ timeout: 5000 });
    
    // Verificação estrita contra erros silenciosos de JavaScript
    expect(consoleErrors).toHaveLength(0);
  });
});
```

---

## 3. Diagnóstico Cirúrgico de Falhas
Ao detectar falha em teste E2E:
1. Examine o screenshot de erro gerado automaticamente em `test-results/`.
2. Inspecione o trace de rede (`trace.zip`) via `npx playwright show-trace`.
3. Valide se a falha é de regressão de layout, timeout de requisição assíncrona ou quebra de backend.
