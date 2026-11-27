// Run (from repo root, static server already serving habitly/ on 8765; @playwright/test installed OUTSIDE the repo):
//   NODE_PATH=<folder with node_modules> PLAYWRIGHT_JSON_OUTPUT_NAME=<file> npx playwright test -c qa-artifacts/habitly/tools/e2e --reporter=json
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: '.',
  testMatch: '*.spec.js',
  fullyParallel: true,
  retries: 0,
  reporter: [['list']],
  outputDir: process.env.PW_OUT || 'test-results',
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:8765',
    screenshot: 'only-on-failure',
    trace: 'off',
  },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
});
