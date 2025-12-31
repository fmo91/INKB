import { test, expect } from '@playwright/test';

test('shows the reading copilot header', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('INKB Reading Copilot')).toBeVisible();
});
