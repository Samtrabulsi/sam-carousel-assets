// "Tamara": the Little Miss Tamara host, drawn in code so she is identical in every video.
// Design from youtube/kids-songs/2026-10-09-phases-of-the-moon/tamara-reference.webp:
// long dark wavy hair (side part), big brown eyes, navy turtleneck with pink + white stripes,
// denim A-line skirt with buttons, navy tights, black Mary Janes.
//
// drawTamara(ctx, opts) draws her full body with the feet's bottom-centre at (0,0), ~930 units tall.
// opts: { t, pose, lt (s in pose), beat (beats since start, for dance/clap), mouth ('X' rest | 'A' closed |
//         'B' small | 'C' open | 'D' wide | 'E' round | 'F' pucker), look (-1..1), blinkSeed }
// poses: idle, sing (hands clasped), wave, point (up-right), clap, cheer, dance, open (arms out)
(function () {
  const SKIN = '#EDBE9A', SKIN_D = '#D69F7B', HAIR = '#2A1A14', HAIR_L = '#4A3124', HAIR_D = '#1A100C',
        SWEAT = '#242C4A', SWEAT_D = '#1A2038', PINK = '#EFA7C5', WHITE = '#EEF0F6',
        DENIM = '#3F72AE', DENIM_D = '#2E5A8E', TIGHTS = '#1E1F33', SHOE = '#14141C', IRIS = '#6B3B1C', INK = '#1A1010';
  // arm angles [upper, fore]: radians from straight down, positive = outward/up, negative = across the body
  const POSES = {
    idle:  { L: [0.14, 0.12], R: [0.14, 0.12], brow: 0.1, smile: 1 },
    sing:  { L: [-0.05, -0.95], R: [-0.05, -0.95], brow: 0.25, smile: 1, front: true },
    wave:  { L: [0.14, 0.12], R: [2.5, 0.35], brow: 0.3, smile: 1, waveArm: true },
    point: { L: [0.14, 0.12], R: [2.0, 0.15], brow: 0.3, smile: 1, lookUp: true },
    clap:  { L: [0.1, -1.75], R: [0.1, -1.75], brow: 0.3, smile: 1, front: true, clap: true },
    cheer: { L: [2.65, 0.25], R: [2.65, 0.25], brow: 0.5, smile: 1 },
    dance: { L: [1.2, 0.6], R: [1.2, 0.6], brow: 0.3, smile: 1, dance: true },
    open:  { L: [0.9, 0.5], R: [0.9, 0.5], brow: 0.6, smile: 1 },
  };
  const lerp = (a, b, k) => a + (b - a) * k;
  const ease = v => { v = Math.max(0, Math.min(1, v)); return v * v * (3 - 2 * v); };

  function stripes(c, x0, x1, y0, y1, step, off) {
    let i = 0;
    for (let y = y0 + off; y < y1; y += step, i++) {
      c.strokeStyle = i % 2 ? WHITE : PINK; c.lineWidth = 7;
      c.beginPath(); for (let x = x0; x <= x1; x += 12) c.lineTo(x, y + ((x / 12) % 2 ? 1.5 : -1.5)); c.stroke(); // knit wobble
    }
  }

  function arm(c, s, sx, sy, up, fore, t, wave) {
    if (wave) fore += 0.45 * Math.sin(t * 9);
    const L1 = 125, L2 = 112;
    const ex = sx + s * Math.sin(up) * L1, ey = sy + Math.cos(up) * L1;
    const a2 = up + fore, hx = ex + s * Math.sin(a2) * L2, hy = ey + Math.cos(a2) * L2;
    c.lineCap = 'round'; c.lineJoin = 'round';
    // sleeve (oversized knit): dark outline, body, stripes along the arm
    c.strokeStyle = SWEAT_D; c.lineWidth = 64; c.beginPath(); c.moveTo(sx, sy); c.lineTo(ex, ey); c.lineTo(hx, hy); c.stroke();
    c.strokeStyle = SWEAT; c.lineWidth = 56; c.stroke();
    [[sx, sy, ex, ey], [ex, ey, hx, hy]].forEach(([ax, ay, bx, by], seg) => {
      for (let k = 0.25; k < 0.95; k += 0.33) {
        const px = lerp(ax, bx, k), py = lerp(ay, by, k), ang = Math.atan2(by - ay, bx - ax) + Math.PI / 2;
        c.strokeStyle = (seg + Math.round(k * 3)) % 2 ? WHITE : PINK; c.lineWidth = 6;
        c.beginPath(); c.moveTo(px - Math.cos(ang) * 26, py - Math.sin(ang) * 26); c.lineTo(px + Math.cos(ang) * 26, py + Math.sin(ang) * 26); c.stroke();
      }
    });
    // ribbed cuff + hand peeking out
    const hx2 = lerp(ex, hx, 1.12), hy2 = lerp(ey, hy, 1.12);
    c.fillStyle = SKIN; c.beginPath(); c.arc(hx2, hy2, 25, 0, Math.PI * 2); c.fill();
    c.fillStyle = SKIN_D; c.beginPath(); c.arc(hx2 + s * 9, hy2 - 8, 9, 0, Math.PI * 2); c.fill();
    c.strokeStyle = SWEAT_D; c.lineWidth = 60; c.beginPath(); c.moveTo(lerp(ex, hx, 0.86), lerp(ey, hy, 0.86)); c.lineTo(hx, hy); c.stroke();
  }

  function mouthShape(c, v, my, smile) {
    const IN = '#6A2228', TONGUE = '#EC7C8A';
    const open = (w, h, teeth) => {
      c.fillStyle = IN; c.beginPath(); c.moveTo(-w, my - h * 0.35);
      c.quadraticCurveTo(0, my - h * 0.55, w, my - h * 0.35); c.quadraticCurveTo(w * 0.8, my + h, 0, my + h); c.quadraticCurveTo(-w * 0.8, my + h, -w, my - h * 0.35); c.fill();
      c.fillStyle = TONGUE; c.beginPath(); c.ellipse(0, my + h * 0.68, w * 0.5, h * 0.3, 0, 0, Math.PI * 2); c.fill();
      if (teeth) { c.fillStyle = '#fff'; c.beginPath(); c.moveTo(-w * 0.82, my - h * 0.33); c.quadraticCurveTo(0, my - h * 0.5, w * 0.82, my - h * 0.33); c.lineTo(w * 0.7, my - h * 0.05); c.quadraticCurveTo(0, my - h * 0.12, -w * 0.7, my - h * 0.05); c.fill(); }
    };
    switch (v) {
      case 'A': c.strokeStyle = IN; c.lineWidth = 7; c.lineCap = 'round'; c.beginPath(); c.moveTo(-22, my); c.quadraticCurveTo(0, my + 8, 22, my); c.stroke(); break;
      case 'B': open(30, 16, true); break;
      case 'C': open(30, 28, true); break;
      case 'D': open(32, 40, true); break;
      case 'E': c.fillStyle = IN; c.beginPath(); c.ellipse(0, my + 8, 17, 22, 0, 0, Math.PI * 2); c.fill();
        c.fillStyle = TONGUE; c.beginPath(); c.ellipse(0, my + 20, 10, 7, 0, 0, Math.PI * 2); c.fill(); break;
      case 'F': c.fillStyle = IN; c.beginPath(); c.ellipse(0, my + 4, 10, 12, 0, 0, Math.PI * 2); c.fill();
        c.strokeStyle = '#C9606E'; c.lineWidth = 5; c.stroke(); break;
      default: // rest: the big toothy smile from the reference
        open(38, 22 * Math.max(0.4, smile), true);
    }
  }

  window.drawTamara = function (c, o) {
    const t = o.t || 0, lt = o.lt ?? 9, beat = o.beat || 0, P = POSES[o.pose] || POSES.idle, I = POSES.idle;
    const k = ease(lt / 0.45);
    let L = [lerp(I.L[0], P.L[0], k), lerp(I.L[1], P.L[1], k)], R = [lerp(I.R[0], P.R[0], k), lerp(I.R[1], P.R[1], k)];
    const bph = beat * Math.PI; // half a cycle per beat
    if (P.dance) { L = [L[0] + 0.7 * Math.sin(bph), L[1]]; R = [R[0] - 0.7 * Math.sin(bph), R[1]]; }
    if (P.clap) { const sep = Math.abs(Math.sin(bph)) * 0.32 * k; L = [L[0] + sep, L[1]]; R = [R[0] + sep, R[1]]; }
    const bounce = (P.dance || P.clap ? Math.abs(Math.sin(bph)) * 16 : Math.sin(t * 2.2) * 4);
    const sway = P.dance ? Math.sin(bph) * 0.05 : Math.sin(t * 0.9) * 0.012;
    const brow = lerp(I.brow, P.brow, k), smile = lerp(I.smile, P.smile, k);

    c.save();
    // shadow
    c.fillStyle = 'rgba(0,0,0,0.22)'; c.beginPath(); c.ellipse(0, 0, 110, 16, 0, 0, Math.PI * 2); c.fill();
    c.rotate(sway);
    // legs + shoes (feet stay planted; the body bounces above them)
    const hip = -300 - bounce * 0.4, liftL = P.dance ? Math.max(0, Math.sin(bph)) * 18 : 0, liftR = P.dance ? Math.max(0, -Math.sin(bph)) * 18 : 0;
    [[-36, liftL], [36, liftR]].forEach(([x, lift]) => {
      c.strokeStyle = TIGHTS; c.lineWidth = 40; c.lineCap = 'round'; c.beginPath(); c.moveTo(x * 0.8, hip); c.lineTo(x, -34 - lift); c.stroke();
      c.fillStyle = SHOE; c.beginPath(); c.ellipse(x + (x > 0 ? 8 : -8), -18 - lift, 40, 20, 0, 0, Math.PI * 2); c.fill();
      c.strokeStyle = '#3A3A48'; c.lineWidth = 5; c.beginPath(); c.moveTo(x - 18, -30 - lift); c.lineTo(x + 18, -30 - lift); c.stroke(); // strap
      c.fillStyle = '#9A8A70'; c.beginPath(); c.arc(x + (x > 0 ? 14 : -14), -30 - lift, 4, 0, Math.PI * 2); c.fill();
      c.fillStyle = 'rgba(255,255,255,0.25)'; c.beginPath(); c.ellipse(x + (x > 0 ? 18 : -2), -26 - lift, 12, 5, 0, 0, Math.PI * 2); c.fill();
    });
    c.translate(0, -bounce);

    const sy = -585; // shoulder line
    // back hair (behind the body): long, wavy, to the elbows
    c.fillStyle = HAIR_D; c.beginPath();
    c.moveTo(-150, -820); c.bezierCurveTo(-200, -700, -190, -600, -175, -520);
    for (let i = 0; i <= 6; i++) { const x = -175 + i * 58.3; c.quadraticCurveTo(x - 29, -470 + (i % 2) * 20, x, -505 + (i % 2 ? 0 : 10)); }
    c.bezierCurveTo(190, -600, 200, -700, 150, -820); c.closePath(); c.fill();

    // skirt
    const wy = -430;
    c.fillStyle = DENIM; c.beginPath(); c.moveTo(-95, wy); c.lineTo(95, wy); c.quadraticCurveTo(130, -360, 150, -292);
    c.quadraticCurveTo(0, -270, -150, -292); c.quadraticCurveTo(-130, -360, -95, wy); c.fill();
    c.strokeStyle = DENIM_D; c.lineWidth = 3; c.setLineDash([7, 6]); c.beginPath(); c.moveTo(-142, -300); c.quadraticCurveTo(0, -280, 142, -300); c.stroke();
    c.beginPath(); c.moveTo(-14, wy + 6); c.lineTo(-18, -284); c.stroke(); c.setLineDash([]);
    [-60, 60].forEach(x => { c.strokeStyle = DENIM_D; c.lineWidth = 3; c.beginPath(); c.moveTo(x * 0.9, wy + 10); c.lineTo(x * 1.45, -290); c.stroke(); }); // pleats
    c.fillStyle = '#5A3A22'; [-385, -330].forEach(y => { c.beginPath(); c.arc(4, y, 8, 0, Math.PI * 2); c.fill(); });

    // sweater body (oversized), clipped stripes, ribbed hem
    c.save();
    c.beginPath(); c.moveTo(-112, sy - 5); c.quadraticCurveTo(-140, -500, -122, -410); c.lineTo(122, -410); c.quadraticCurveTo(140, -500, 112, sy - 5);
    c.quadraticCurveTo(0, sy - 30, -112, sy - 5); c.closePath();
    c.fillStyle = SWEAT; c.fill(); c.clip();
    stripes(c, -150, 150, sy - 10, -410, 34, 18);
    c.restore();
    c.fillStyle = SWEAT_D; c.beginPath(); c.roundRect(-124, -428, 248, 30, 12); c.fill();
    c.strokeStyle = SWEAT; c.lineWidth = 3; for (let x = -114; x < 120; x += 12) { c.beginPath(); c.moveTo(x, -424); c.lineTo(x, -402); c.stroke(); }

    if (!P.front) { arm(c, -1, -100, sy + 15, L[0], L[1], t, false); arm(c, 1, 100, sy + 15, R[0], R[1], t, P.waveArm && k > 0.9); }

    // turtleneck
    c.fillStyle = SWEAT_D; c.beginPath(); c.roundRect(-58, sy - 70, 116, 70, 22); c.fill();
    c.strokeStyle = SWEAT; c.lineWidth = 3; for (let x = -48; x <= 48; x += 12) { c.beginPath(); c.moveTo(x, sy - 64); c.lineTo(x, sy - 6); c.stroke(); }

    // head
    const hy = -790, look = (o.look || 0) * 9, up = P.lookUp ? 6 * k : 0;
    c.fillStyle = SKIN; c.beginPath(); c.ellipse(0, hy, 122, 130, 0, 0, Math.PI * 2); c.fill();
    c.beginPath(); c.ellipse(-120, hy + 12, 18, 24, 0, 0, Math.PI * 2); c.ellipse(120, hy + 12, 18, 24, 0, 0, Math.PI * 2); c.fill();
    // eyes: big, brown, two highlights, lashes; blink every ~4 s
    const bp = (t + (o.blinkSeed || 0)) % 4.1, open = bp < 0.13 ? 0.08 : 1, ey = hy + 10 - up;
    [-50, 50].forEach(ex => {
      c.save(); c.translate(ex, ey); c.scale(1, open);
      c.fillStyle = '#fff'; c.beginPath(); c.ellipse(0, 0, 33, 36, 0, 0, Math.PI * 2); c.fill();
      c.fillStyle = IRIS; c.beginPath(); c.arc(look, 4 - up, 24, 0, Math.PI * 2); c.fill();
      c.fillStyle = '#3A1E0E'; c.beginPath(); c.arc(look, 4 - up, 13, 0, Math.PI * 2); c.fill();
      c.fillStyle = '#fff'; c.beginPath(); c.arc(look + 8, -6 - up, 8, 0, Math.PI * 2); c.fill();
      c.beginPath(); c.arc(look - 8, 12 - up, 3.5, 0, Math.PI * 2); c.fill();
      c.restore();
      // upper lash line + outer lashes
      c.strokeStyle = INK; c.lineWidth = 7; c.lineCap = 'round';
      c.beginPath(); c.ellipse(ex, ey, 34, 37 * open, 0, Math.PI * 1.08, Math.PI * 1.92); c.stroke();
      const s = Math.sign(ex); c.lineWidth = 4;
      for (let i = 0; i < 3; i++) { const a = -0.35 - i * 0.28, bx = ex + s * 32 * Math.cos(a), by = ey - 8 + 30 * Math.sin(a) * open;
        c.beginPath(); c.moveTo(bx, by); c.lineTo(bx + s * 12, by - 8); c.stroke(); }
    });
    // brows: thick, arched
    c.strokeStyle = HAIR; c.lineWidth = 11; c.lineCap = 'round';
    [-1, 1].forEach(s => { const by = hy - 52 - brow * 9 - up; c.beginPath(); c.moveTo(s * 22, by + 6); c.quadraticCurveTo(s * 50, by - 12, s * 80, by + 4); c.stroke(); });
    // cheeks, nose
    c.fillStyle = 'rgba(236,120,120,0.32)'; c.beginPath(); c.ellipse(-78, hy + 52, 24, 14, 0, 0, Math.PI * 2); c.ellipse(78, hy + 52, 24, 14, 0, 0, Math.PI * 2); c.fill();
    c.strokeStyle = SKIN_D; c.lineWidth = 5; c.beginPath(); c.moveTo(-8, hy + 48); c.quadraticCurveTo(0, hy + 56, 10, hy + 47); c.stroke();
    mouthShape(c, o.mouth || 'X', hy + 82, smile);

    // front hair: side-parted fringe + locks falling over the shoulders
    c.fillStyle = HAIR;
    c.beginPath(); c.ellipse(0, hy - 62, 130, 92, 0, Math.PI, Math.PI * 2); c.fill(); // crown cap under the fringe
    c.beginPath(); c.moveTo(-132, hy + 10); c.bezierCurveTo(-150, hy - 120, -60, hy - 170, 30, hy - 150);  // crown, part at x≈30
    c.bezierCurveTo(-20, hy - 120, -70, hy - 90, -110, hy - 20); c.quadraticCurveTo(-120, hy, -132, hy + 10); c.fill();
    c.beginPath(); c.moveTo(30, hy - 150); c.bezierCurveTo(120, hy - 160, 160, hy - 80, 132, hy + 10);
    c.quadraticCurveTo(110, hy - 60, 60, hy - 100); c.quadraticCurveTo(40, hy - 110, 30, hy - 150); c.fill();
    [-1, 1].forEach(s => { // long side locks in front of the shoulders
      c.beginPath(); c.moveTo(s * 128, hy - 30); c.bezierCurveTo(s * 150, hy + 60, s * 120, hy + 140, s * 150, hy + 210);
      c.bezierCurveTo(s * 170, hy + 260, s * 140, hy + 300, s * 160, hy + 330); c.quadraticCurveTo(s * 115, hy + 300, s * 112, hy + 230);
      c.bezierCurveTo(s * 100, hy + 160, s * 112, hy + 80, s * 108, hy + 20); c.closePath(); c.fill();
    });
    c.strokeStyle = HAIR_L; c.lineWidth = 6; // shine strands
    c.beginPath(); c.moveTo(-60, hy - 135); c.quadraticCurveTo(-110, hy - 90, -118, hy - 10); c.stroke();
    c.beginPath(); c.moveTo(80, hy - 140); c.quadraticCurveTo(130, hy - 90, 128, hy - 20); c.stroke();

    if (P.front) { arm(c, -1, -100, sy + 15, L[0], L[1], t, false); arm(c, 1, 100, sy + 15, R[0], R[1], t, false); }
    c.restore();
  };

  // Pick a mouth shape while singing: words = [{w,start,end}] for the song; returns 'X' between words.
  window.tamaraMouth = function (words, t) {
    let lo = 0, hi = words.length - 1, w = null;
    while (lo <= hi) { const m = (lo + hi) >> 1; if (words[m].end + 0.05 <= t) lo = m + 1; else if (words[m].start > t) hi = m - 1; else { w = words[m]; break; } }
    if (!w) return 'X';
    const vow = (w.w.toLowerCase().match(/[aeiouy]+/g) || ['a']);
    const p = (t - w.start) / Math.max(0.1, w.end - w.start), v = vow[Math.min(vow.length - 1, Math.floor(p * vow.length))];
    if (p > 0.92) return 'A';
    if (/^(oo|o|u|ou)$/.test(v)) return (Math.floor(t * 8) % 3) ? 'E' : 'F';
    if (/a/.test(v)) return (Math.floor(t * 9) % 4) ? 'D' : 'C';
    return (Math.floor(t * 9) % 3) ? 'C' : 'B';
  };
})();
