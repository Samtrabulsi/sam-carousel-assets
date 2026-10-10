// Shared virtual clock + Playwright loader for record.mjs and contact-sheet.mjs.
import { execSync } from 'node:child_process';
import { createRequire } from 'node:module';
import path from 'node:path';

// Use a local playwright if installed, else the global one.
export function loadChromium() {
  const require = createRequire(import.meta.url);
  try { return require('playwright').chromium; } catch {
    const root = execSync('npm root -g').toString().trim();
    return require(path.join(root, 'playwright')).chromium;
  }
}

// Installed before any page script runs (page.addInitScript). Exposes
// window.__advance(ms), which moves rAF, performance.now, Date.now, timers and
// CSS/Web Animations forward together.
export const clock = () => {
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
