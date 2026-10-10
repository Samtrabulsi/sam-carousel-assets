#!/usr/bin/env node
// Render an HTML animation to MP4, frame by frame, with a virtual clock so the
// output is smooth at any CPU speed. Drives requestAnimationFrame,
// performance.now, Date.now, setTimeout/setInterval, and CSS/Web Animations.
//
//   node record.mjs page.html out.mp4 [--w 1080] [--h 1920] [--fps 30] [--sec 15] [--audio track.mp3] [--from 0]
// --from S starts the clock at S seconds, so long videos can be rendered as parallel chunks and concatenated.
import { spawn } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import { clock, loadChromium } from './lib/clock.mjs';

const chromium = loadChromium();

const [, , input, output, ...rest] = process.argv;
if (!input || !output) {
  console.error('usage: record.mjs page.html out.mp4 [--w W] [--h H] [--fps N] [--sec S] [--audio file]');
  process.exit(1);
}
const opt = { w: 1080, h: 1920, fps: 30, sec: 15, audio: null, from: 0 };
for (let i = 0; i < rest.length; i += 2) {
  const k = rest[i].replace(/^--/, '');
  if (!(k in opt)) { console.error(`unknown flag --${k}`); process.exit(1); }
  opt[k] = k === 'audio' ? rest[i + 1] : Number(rest[i + 1]);
}
const frames = Math.round(opt.fps * opt.sec);
const step = 1000 / opt.fps;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: opt.w, height: opt.h } });
page.on('pageerror', (e) => console.error('page error:', e.message));
await page.addInitScript(clock);
await page.goto(pathToFileURL(path.resolve(input)).href, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);

const args = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(opt.fps), '-i', '-'];
if (opt.audio) args.push('-i', opt.audio, '-shortest', '-c:a', 'aac');
args.push('-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', output);
const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
const done = new Promise((res, rej) => ff.on('close', (c) => (c ? rej(new Error(`ffmpeg exit ${c}`)) : res())));

for (let f = 0; f < frames; f++) {
  await page.evaluate((ms) => window.__advance(ms), f === 0 ? opt.from * 1000 : step);
  const buf = await page.screenshot({ type: 'png' });
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  if (f % opt.fps === 0) process.stdout.write(`\r${Math.round((f / frames) * 100)}%`);
}
ff.stdin.end();
await done;
await browser.close();
console.log(`\rwrote ${output} (${opt.w}x${opt.h}, ${opt.fps}fps, ${opt.sec}s)`);
