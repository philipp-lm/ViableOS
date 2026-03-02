/**
 * Screenshot capture for README — pure UI-driven, no localStorage hacks.
 * Run: npx playwright test tests/e2e/screenshots.spec.ts --workers=1
 */
import { test } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SCREENSHOT_DIR = path.resolve(__dirname, '../../../docs/screenshots');

test.describe.serial('README screenshots', () => {
  test.setTimeout(45_000);

  test('01 - chat page', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('text=VSM Expert Chat', { timeout: 10_000 });
    await page.waitForTimeout(500);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'chat.png'),
      fullPage: false,
    });
  });

  test('02 - wizard templates', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(300);
    await page.locator('text=Wizard').first().click();
    await page.waitForSelector('text=Choose a Template', { timeout: 10_000 });
    await page.waitForTimeout(300);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'wizard-templates.png'),
      fullPage: false,
    });
  });

  test('03 - full wizard flow + dashboard', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(300);

    // Go to Wizard
    await page.locator('text=Wizard').first().click();
    await page.waitForSelector('text=Choose a Template', { timeout: 10_000 });

    // Select SaaS Startup
    await page.locator('text=SaaS Startup').first().click();
    await page.waitForTimeout(500);

    // Now on Identity step — fill purpose
    await page.waitForSelector('text=Your Organization', { timeout: 5_000 });
    const purposeField = page.locator('textarea').first();
    await purposeField.fill('Build and scale a SaaS product with AI-powered operations');
    await page.waitForTimeout(300);

    // Screenshot: Identity
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'wizard-identity.png'),
      fullPage: false,
    });

    // Click Next → Units step
    await page.locator('button:has-text("Next")').first().click();
    await page.waitForTimeout(500);

    // Screenshot: Units
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'wizard-units.png'),
      fullPage: false,
    });

    // Click Next → Budget step
    await page.locator('button:has-text("Next")').first().click();
    await page.waitForTimeout(500);

    // Screenshot: Budget
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'wizard-budget.png'),
      fullPage: true,
    });

    // Click Next → HITL step
    await page.locator('button:has-text("Next")').first().click();
    await page.waitForTimeout(500);

    // Click Next → Review step
    await page.locator('button:has-text("Next")').first().click();
    await page.waitForTimeout(500);

    // Wait for viability check
    try {
      await page.waitForSelector('text=Viability Score', { timeout: 10_000 });
      await page.waitForTimeout(500);
    } catch {
      await page.waitForTimeout(2000);
    }

    // Screenshot: Review
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'wizard-review.png'),
      fullPage: true,
    });

    // Go to Dashboard
    await page.locator('button:has-text("Dashboard")').first().click();
    await page.waitForTimeout(1500);

    // Screenshot: Dashboard
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'dashboard.png'),
      fullPage: true,
    });
  });
});
