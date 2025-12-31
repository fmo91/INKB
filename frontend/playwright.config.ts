import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: 'tests/e2e',
  use: {
    baseURL: 'http://localhost:19006',
  },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
  ],
  webServer: {
    command:
      'EXPO_NON_INTERACTIVE=1 npm run web -- --host localhost --port 19006',
    url: 'http://localhost:19006',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
