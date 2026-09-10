// Captures the seventeen console screens from the live deployment for docs/readme/screens/.
// Run from a folder with playwright installed:  npm i playwright && npx playwright install chromium && node capture.mjs
// The demo incident INC-0419 is used wherever a screen needs an incident id.
import { chromium } from 'playwright';
const B = 'https://citinel-web.onrender.com';
const OUT = '/Users/danish/CITINEL/docs/readme/screens/';
const PAGES = [
  ['overview',   'Overview.dc.html'],
  ['queue',      'Queue.dc.html'],
  ['replay',     'Replay.dc.html?id=INC-0419'],
  ['confidence', 'Confidence.dc.html?id=INC-0419'],
  ['evidence',   'Evidence.dc.html?id=INC-0419'],
  ['approvals',  'Approvals.dc.html?id=INC-0419'],
  ['compliance', 'Compliance.dc.html?id=INC-0419'],
  ['report',     'Report.dc.html?id=INC-0419&kind=certin'],
  ['audit',      'Audit.dc.html?id=INC-0419'],
  ['corpus',     'Corpus.dc.html'],
  ['eval',       'Eval.dc.html'],
  ['policy',     'Policy.dc.html'],
  ['handover',   'Handover.dc.html'],
  ['executive',  'Executive.dc.html'],
  ['connectors', 'Settings.dc.html'],
  ['demo',       'Demo.dc.html'],
  ['shell',      'Shell.dc.html'],
];
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1, colorScheme: 'dark' });
const page = await ctx.newPage();
for (const [name, path] of PAGES) {
  const t0 = Date.now();
  try {
    await page.goto(B + '/' + path, { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForSelector('[data-citinel-page], [data-screen-label]', { timeout: 20000 }).catch(() => {});
    await page.evaluate(() => document.fonts && document.fonts.ready);
    await page.waitForTimeout(3500);   // the DC runtime paints after its own fetches settle
    await page.screenshot({ path: OUT + name + '.png', fullPage: false });
    console.log('ok ', name.padEnd(11), ((Date.now() - t0) / 1000).toFixed(1) + 's');
  } catch (e) { console.log('!! ', name.padEnd(11), String(e).slice(0, 120)); }
}
await browser.close();
