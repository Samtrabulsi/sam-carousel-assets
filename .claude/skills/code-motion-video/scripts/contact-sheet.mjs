#!/usr/bin/env node
// Contact sheet: N labelled frames on one PNG, so Claude can review a whole
// animation as a storyboard before (HTML) or after (MP4) the full render.
//
//   node contact-sheet.mjs page.html sheet.png [--w 1080] [--h 1920] [--fps 30] [--sec 10] [--n 12] [--cols 4] [--frames 0,84,85]
//   node contact-sheet.mjs out.mp4   sheet.png [--n 12] [--cols 4] [--frames 0,84,85]
// HTML runs on the same virtual clock as record.mjs, so frame N here is frame N in the MP4.
// --frames picks exact frames (e.g. the two either side of a glitch); otherwise N evenly spaced
// frames from 0, never the last one (in a loop, frame total is frame 0 again).
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import os from 'node:os';
import path from 'node:path';
import { clock, loadChromium } from './lib/clock.mjs';

const [, , input, output, ...rest] = process.argv;
if (!input || !output) {
  console.error('usage: contact-sheet.mjs page.html|video.mp4 sheet.png [--w W] [--h H] [--fps N] [--sec S] [--n 12] [--cols 4] [--frames a,b,c] [--thumb 360]');
  process.exit(1);
}
const opt = { w: 1080, h: 1920, fps: 30, sec: 10, n: 12, cols: 4, frames: null, thumb: 360 };
for (let i = 0; i < rest.length; i += 2) {
  const k = rest[i].replace(/^--/, '');
  if (!(k in opt)) { console.error(`unknown flag --${k}`); process.exit(1); }
  opt[k] = k === 'frames' ? rest[i + 1].split(',').map(Number) : Number(rest[i + 1]);
}
const isVideo = /\.(mp4|mov|webm|mkv)$/i.test(input);

if (isVideo) {
  const probe = execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-count_packets',
    '-show_entries', 'stream=width,height,r_frame_rate,nb_read_packets', '-of', 'json', input]);
  const s = JSON.parse(probe).streams[0];
  const [a, b] = s.r_frame_rate.split('/').map(Number);
  Object.assign(opt, { w: s.width, h: s.height, fps: a / b, sec: Number(s.nb_read_packets) / (a / b) });
}
const total = Math.round(opt.fps * opt.sec);
const picks = (opt.frames ?? Array.from({ length: opt.n }, (_, i) => Math.round((i * total) / opt.n)))
  .filter((f) => f >= 0 && f < total);
if (!picks.length) { console.error(`no frames in range 0..${total - 1}`); process.exit(1); }

const chromium = loadChromium();
const browser = await chromium.launch();
const shots = []; // { f, src }

if (isVideo) {
  const dir = mkdtempSync(path.join(os.tmpdir(), 'sheet-'));
  const sel = picks.map((f) => `eq(n\\,${f})`).join('+');
  execFileSync('ffmpeg', ['-v', 'error', '-i', input, '-vf', `select='${sel}'`, '-vsync', '0', path.join(dir, '%03d.png')]);
  const files = readdirSync(dir).sort();
  files.forEach((file, i) => shots.push({ f: picks[i], src: readFileSync(path.join(dir, file)) }));
  rmSync(dir, { recursive: true });
} else {
  const page = await browser.newPage({ viewport: { width: opt.w, height: opt.h } });
  page.on('pageerror', (e) => console.error('page error:', e.message));
  await page.addInitScript(clock);
  await page.goto(pathToFileURL(path.resolve(input)).href, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const step = 1000 / opt.fps;
  const want = new Set(picks);
  // Step every frame (not jump) so timers and rAF chains behave exactly as in record.mjs.
  for (let f = 0; f <= Math.max(...picks); f++) {
    await page.evaluate((ms) => window.__advance(ms), f === 0 ? 0 : step);
    if (want.has(f)) shots.push({ f, src: await page.screenshot({ type: 'png' }) });
  }
  await page.close();
}

const tw = opt.thumb, th = Math.round((tw * opt.h) / opt.w);
const cells = shots.map(({ f, src }) => `<figure><img src="data:image/png;base64,${src.toString('base64')}">
  <figcaption>f${f} · ${(f / opt.fps).toFixed(2)}s</figcaption></figure>`).join('');
const html = `<!doctype html><style>
  body{margin:0;background:#1a1a1a;font:600 15px system-ui,sans-serif;color:#eee}
  main{display:grid;grid-template-columns:repeat(${opt.cols},${tw}px);gap:10px;padding:10px;width:max-content}
  figure{margin:0}img{display:block;width:${tw}px;height:${th}px;object-fit:contain;background:#000}
  figcaption{padding:4px 2px}
</style><main>${cells}</main>`;
const sheet = await browser.newPage({ viewport: { width: 400, height: 400 } });
await sheet.setContent(html, { waitUntil: 'load' });
await sheet.locator('main').screenshot({ path: output });
await browser.close();
console.log(`wrote ${output}: ${shots.length} frames (${picks.join(', ')}) of ${total} at ${opt.fps}fps`);
