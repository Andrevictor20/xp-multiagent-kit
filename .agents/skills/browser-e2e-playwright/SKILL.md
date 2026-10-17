---
name: browser-e2e-playwright
description: Headless E2E browser testing with Playwright, auto-wait locators, and traces.
---

# Browser E2E Playwright

Build deterministic End-to-End browser tests with Playwright to verify critical user journeys, live accessibility, zero console errors, and rendering stability.

## 1. Anti-Flaky E2E Principles
- **Zero Artificial Sleeps:** Ban `time.sleep()` and `page.waitForTimeout()`. Use web-first auto-waiting assertions (`await expect(locator).toBeVisible()`).
- **Resilient Locators:** Prefer user-facing semantic locators (`getByRole`, `getByLabel`, `getByTestId`) over brittle CSS chains or XPath.
- **State Isolation:** Run every test in a fresh `BrowserContext` with clean cookies and `localStorage`.

## 2. Canonical Playwright Pattern

```typescript
import { test, expect } from '@playwright/test';

test.describe('Critical Flow: Checkout', () => {
  test('completes purchase with zero console errors', async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });

    await page.goto('/pricing');
    await page.getByRole('button', { name: /subscribe pro/i }).click();

    await expect(page).toHaveURL(/.*checkout/);
    await page.getByLabel('Cardholder Name').fill('Jane Doe');
    await page.getByRole('button', { name: /confirm payment/i }).click();

    await expect(page.getByText('Subscription Confirmed!')).toBeVisible({ timeout: 5000 });
    expect(consoleErrors).toHaveLength(0);
  });
});
```

## 3. Surgical Failure Diagnostics
1. Inspect failure screenshots in `test-results/`.
2. Analyze network and DOM snapshots in `trace.zip` via `npx playwright show-trace`.
3. Isolate whether the failure stems from layout regression, async timeout, or backend error.
