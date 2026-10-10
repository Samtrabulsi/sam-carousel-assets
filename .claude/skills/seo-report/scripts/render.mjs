// Render report.html to an A4 PDF with the preinstalled Playwright Chromium.
//   node render.mjs DIR/report.html DIR/report.pdf
import { createRequire } from 'module';
import { execSync } from 'child_process';
import path from 'path';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = require(execSync('npm root -g').toString().trim() + '/playwright'); }
const [, , html, out] = process.argv;
if (!html || !out) { console.error('usage: node render.mjs report.html report.pdf'); process.exit(1); }
const browser = await pw.chromium.launch();
const page = await browser.newPage();
await page.goto('file://' + path.resolve(html), { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true });
await browser.close();
console.log('pdf ->', out);
