#!/usr/bin/env node
// Render an HTML animation to MP4, frame by frame, with a virtual clock so the
// output is smooth at any CPU speed. Drives requestAnimationFrame,
// performance.now, Date.now, setTimeout/setInterval, and CSS/Web Animations.
//
//   node record.mjs page.html out.mp4 [--w 1080] [--h 1920] [--fps 30] [--sec 15] [--audio track.mp3]
import { spawn, execSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

// Use a local playwright if installed, else the global one.
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); } catch {
  const root = execSync('npm root -g').toString().trim();
  ({ chromium } = require(path.join(root, 'playwright')));
}

const [, , input, output, ...rest] = process.argv;
if (!input || !output) {
  console.error('usage: record.mjs page.html out.mp4 [--w W] [--h H] [--fps N] [--sec S] [--audio file]');
  process.exit(1);
}
const opt = { w: 1080, h: 1920, fps: 30, sec: 15, audio: null };
for (let i = 0; i < rest.length; i += 2) {
  const k = rest[i].replace(/^--/, '');
  if (!(k in opt)) { console.error(`unknown flag --${k}`); process.exit(1); }
  opt[k] = k === 'audio' ? rest[i + 1] : Number(rest[i + 1]);
}
const frames = Math.round(opt.fps * opt.sec);
const step = 1000 / opt.fps;

// Installed before any page script runs.
const clock = () => {
  let now = 0;
  const start = Date.now();
  let rafQ = [];
  let timers = [];
  let tid = 1;
  window.requestAnimationFrame = (cb) => { rafQ.push(cb); return rafQ.length; };
  window.cancelAnimationFrame = () => {};
  performance.now = () => now;
  Date.now = () => start + now;
  window.setTimeout = (cb, ms = 0, ...a) => { const id = tid++; timers.push({ id, at: now + ms, cb, a }); return id; };
  window.setInterval = (cb, ms = 0, ...a) => { const id = tid++; timers.push({ id, at: now + ms, cb, a, every: Math.max(ms, 1) }); return id; };
  window.clearTimeout = window.clearInterval = (id) => { timers = timers.filter((t) => t.id !== id); };
  window.__advance = (ms) => {
    now += ms;
    for (;;) {
      const due = timers.filter((t) => t.at <= now).sort((x, y) => x.at - y.at)[0];
      if (!due) break;
      if (due.every) due.at += due.every; else timers = timers.filter((t) => t !== due);
      try { due.cb(...due.a); } catch (e) { console.error(e); }
    }
    const q = rafQ; rafQ = [];
    for (const cb of q) { try { cb(now); } catch (e) { console.error(e); } }
    for (const an of document.getAnimations()) { an.pause(); an.currentTime = now; }
  };
};

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
  await page.evaluate((ms) => window.__advance(ms), f === 0 ? 0 : step);
  const buf = await page.screenshot({ type: 'png' });
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  if (f % opt.fps === 0) process.stdout.write(`\r${Math.round((f / frames) * 100)}%`);
}
ff.stdin.end();
await done;
await browser.close();
console.log(`\rwrote ${output} (${opt.w}x${opt.h}, ${opt.fps}fps, ${opt.sec}s)`);
