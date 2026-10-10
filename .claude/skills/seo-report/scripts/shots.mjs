// Above-the-fold screenshots (desktop + mobile) for the report.
//   node shots.mjs OUT_DIR domain1 [domain2 ...]   -> OUT_DIR/<domain>-desktop.jpg, <domain>-mobile.jpg
import { createRequire } from 'module';
import { execSync } from 'child_process';
import path from 'path';
import fs from 'fs';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = require(execSync('npm root -g').toString().trim() + '/playwright'); }
const [, , out, ...domains] = process.argv;
fs.mkdirSync(out, { recursive: true });
const UA_D = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36';
const UA_M = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1';
const browser = await pw.chromium.launch();
async function shot(domain, kind) {
  const opts = kind === 'mobile'
    ? { viewport: { width: 390, height: 780 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, userAgent: UA_M }
    : { viewport: { width: 1366, height: 820 }, deviceScaleFactor: 1, userAgent: UA_D };
  const ctx = await browser.newContext({ ...opts, locale: 'ar' });
  const page = await ctx.newPage();
  try {
    await page.goto('https://' + domain + '/', { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2500);                       // let sliders/fonts settle
    const file = path.join(out, `${domain}-${kind}.jpg`);
    await page.screenshot({ path: file, type: 'jpeg', quality: 72 });
    console.log('ok', file);
  } catch (e) { console.log('fail', domain, kind, String(e).slice(0, 120)); }
  await ctx.close();
}
await Promise.all(domains.flatMap(d => [shot(d, 'desktop'), shot(d, 'mobile')]));
await browser.close();
