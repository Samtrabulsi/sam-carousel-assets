// "Gia": the Grow Success Online presenter, a vector character drawn in code so she looks
// identical in every video. drawGia(ctx, opts) draws her waist-up with the bottom-centre at (0,0)
// in a ~560-unit-tall box; scale/translate the context to place her.
//
// opts: { t, pose, mirror (true when drawn with ctx.scale(-1,1)), badge ('G'), viseme (Rhubarb A–H/X, preferred), mouth (0..1 fallback), look (-1..1), blinkSeed, lt (time in pose, s) }
// poses: idle, wave, point, worried, think, surprised, happy, cheer
(function () {
  const SKIN = '#C98E6B', SKIN_D = '#B07656', HAIR = '#2A1A16', HAIR_L = '#3D2722',
        SHIRT = '#12A4AE', SHIRT_D = '#0E8C95', COLLAR = '#F4F7FB', AMBER = '#FFB547', INK = '#1B1414';
  // arm angles: [upper, fore] measured from straight down, positive = outward/up
  const POSES = {
    idle:      { L: [0.18, 0.15], R: [0.18, 0.15], brow: 0,    smile: 0.6 },
    wave:      { L: [0.18, 0.15], R: [2.55, 0.35], brow: 0.15, smile: 1,   waveArm: true },
    point:     { L: [0.2, 0.2],   R: [1.45, 0.12], brow: 0.1,  smile: 0.8 },
    worried:   { L: [0.45, 2.55], R: [0.45, 2.55], brow: -0.9, smile: -0.8 },
    think:     { L: [0.2, 1.9],   R: [0.35, 2.75], brow: -0.25, smile: 0.1, lookUp: true },
    surprised: { L: [2.15, 0.35], R: [2.15, 0.35], brow: 0.9,  smile: 0.3, oh: true },
    happy:     { L: [0.65, 0.55], R: [0.65, 0.55], brow: 0.3,  smile: 1 },
    cheer:     { L: [2.7, 0.2],   R: [2.7, 0.2],   brow: 0.5,  smile: 1 },
  };
  const lerp = (a, b, k) => a + (b - a) * k;
  const ease = v => { v = Math.max(0, Math.min(1, v)); return v * v * (3 - 2 * v); };

  function arm(c, side, sx, sy, up, fore, t, wave) {
    const s = side; // -1 left, +1 right
    if (wave) fore += 0.45 * Math.sin(t * 9);
    const ex = sx + s * Math.sin(up) * 120, ey = sy + Math.cos(up) * 120;
    const a2 = up + fore, hx = ex + s * Math.sin(a2) * 108, hy = ey + Math.cos(a2) * 108;
    c.lineCap = 'round'; c.lineJoin = 'round';
    c.strokeStyle = SHIRT_D; c.lineWidth = 50; c.beginPath(); c.moveTo(sx, sy); c.lineTo(ex, ey); c.stroke();
    c.strokeStyle = SKIN; c.lineWidth = 40; c.beginPath(); c.moveTo(ex, ey); c.lineTo(hx, hy); c.stroke();
    // sleeve cuff
    c.strokeStyle = SHIRT; c.lineWidth = 54; c.beginPath(); c.moveTo(sx, sy); c.lineTo(lerp(sx, ex, 0.7), lerp(sy, ey, 0.7)); c.stroke();
    c.fillStyle = SKIN; c.beginPath(); c.arc(hx, hy, 27, 0, Math.PI * 2); c.fill();
    c.fillStyle = SKIN_D; c.beginPath(); c.arc(hx + s * 10, hy - 6, 9, 0, Math.PI * 2); c.fill(); // thumb
  }

  // Rhubarb Lip Sync mouth shapes (https://github.com/DanielSWolf/rhubarb-lip-sync#mouth-shapes)
  // A: closed (M B P)  B: slightly open, teeth (K S T EE)  C: open (EH AE)  D: wide open (AA)
  // E: rounded (AO ER)  F: puckered (UW OW W)  G: teeth on lip (F V)  H: tongue up (L)  X: rest
  function drawViseme(c, v, my) {
    const LIP = '#5A1E22', IN = '#5A1E22', TONGUE = '#E86E7A';
    const open = (w, h, teethTop, teethBot, tongue) => {
      c.fillStyle = IN; c.beginPath(); c.ellipse(0, my, w, h, 0, 0, Math.PI * 2); c.fill();
      if (tongue) { c.fillStyle = TONGUE; c.beginPath(); c.ellipse(0, my + h * 0.45, w * 0.6, h * 0.42, 0, 0, Math.PI); c.fill(); }
      c.fillStyle = '#fff';
      if (teethTop) c.fillRect(-w * 0.62, my - h + 1, w * 1.24, Math.min(8, h * 0.4));
      if (teethBot) c.fillRect(-w * 0.55, my + h - Math.min(7, h * 0.35) - 1, w * 1.1, Math.min(7, h * 0.35));
    };
    c.lineCap = 'round';
    switch (v) {
      case 'A': c.strokeStyle = LIP; c.lineWidth = 8; c.beginPath(); c.moveTo(-20, my); c.lineTo(20, my); c.stroke(); break;
      case 'B': open(24, 8, true, true, false); break;
      case 'C': open(25, 16, true, false, true); break;
      case 'D': open(27, 26, true, false, true); break;
      case 'E': open(19, 18, false, false, true); break;
      case 'F': c.fillStyle = IN; c.beginPath(); c.ellipse(0, my, 10, 11, 0, 0, Math.PI * 2); c.fill();
        c.strokeStyle = '#B5525C'; c.lineWidth = 5; c.stroke(); break;
      case 'G': open(22, 9, true, false, false); c.fillStyle = '#C46A6A'; c.fillRect(-18, my + 2, 36, 6); break;
      case 'H': open(24, 17, true, false, false); c.fillStyle = TONGUE; c.beginPath(); c.ellipse(0, my - 6, 11, 7, 0, 0, Math.PI * 2); c.fill(); break;
    }
  }
  // cues: Rhubarb JSON mouthCues; returns the shape at time t (seconds)
  window.giaViseme = function (cues, t) {
    let lo = 0, hi = cues.length - 1;
    while (lo <= hi) { const m = (lo + hi) >> 1; if (cues[m].end <= t) lo = m + 1; else if (cues[m].start > t) hi = m - 1; else return cues[m].value; }
    return 'X';
  };

  window.drawGia = function (c, o) {
    const t = o.t || 0, lt = o.lt ?? 9, P = POSES[o.pose] || POSES.idle, I = POSES.idle;
    const k = ease(lt / 0.5); // blend from idle into the pose
    const mix = (a, b) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k)];
    const L = mix(I.L, P.L), R = mix(I.R, P.R);
    const brow = lerp(I.brow, P.brow, k), smile = lerp(I.smile, P.smile, k);
    const bob = Math.sin(t * 2.1) * 4, sway = Math.sin(t * 0.9) * 0.015;
    const mouth = Math.max(0, Math.min(1, o.mouth || 0));
    c.save(); c.rotate(sway); c.translate(0, bob);

    // back hair (behind body)
    c.fillStyle = HAIR; c.beginPath(); c.ellipse(0, -420, 118, 135, 0, 0, Math.PI * 2); c.fill();
    // torso
    c.fillStyle = SHIRT; c.beginPath();
    c.moveTo(-150, 0); c.bezierCurveTo(-160, -150, -150, -300, -95, -330); c.lineTo(95, -330);
    c.bezierCurveTo(150, -300, 160, -150, 150, 0); c.closePath(); c.fill();
    // collar + badge
    c.fillStyle = COLLAR; c.beginPath(); c.moveTo(-55, -332); c.lineTo(0, -270); c.lineTo(55, -332); c.lineTo(28, -332); c.lineTo(0, -300); c.lineTo(-28, -332); c.closePath(); c.fill();
    c.fillStyle = AMBER; c.beginPath(); c.arc(-75, -220, 24, 0, Math.PI * 2); c.fill();
    c.fillStyle = '#fff'; c.font = '800 28px Inter, Arial, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.save(); c.translate(-75, -218); if (o.mirror) c.scale(-1, 1); c.fillText(o.badge || 'G', 0, 0); c.restore();  // keep the badge letter readable when mirrored
    // neck
    c.fillStyle = SKIN_D; c.fillRect(-28, -372, 56, 50);

    // arms behind/in front: draw raised arms after head so hands show over face for worried/think
    const front = o.pose === 'worried' || o.pose === 'think';
    if (!front) { arm(c, -1, -128, -300, L[0], L[1], t, false); arm(c, 1, 128, -300, R[0], R[1], t, P.waveArm && k > 0.9); }

    // head
    const hy = -455, look = (o.look || 0) * 10;
    c.fillStyle = SKIN; c.beginPath(); c.ellipse(0, hy, 92, 102, 0, 0, Math.PI * 2); c.fill();
    c.beginPath(); c.arc(-90, hy + 8, 18, 0, Math.PI * 2); c.arc(90, hy + 8, 18, 0, Math.PI * 2); c.fill(); // ears
    c.fillStyle = AMBER; c.beginPath(); c.arc(-92, hy + 30, 7, 0, Math.PI * 2); c.arc(92, hy + 30, 7, 0, Math.PI * 2); c.fill(); // earrings
    // front hair: fringe + curly bun
    c.fillStyle = HAIR; c.beginPath(); c.ellipse(0, hy - 62, 98, 55, 0, Math.PI, Math.PI * 2); c.fill();
    c.beginPath(); c.ellipse(-55, hy - 40, 50, 38, -0.5, 0, Math.PI * 2); c.ellipse(45, hy - 50, 58, 30, 0.35, 0, Math.PI * 2); c.fill();
    for (let i = 0; i < 7; i++) { const a = Math.PI + i * Math.PI / 6; c.beginPath(); c.arc(Math.cos(a) * 100, hy - 30 + Math.sin(a) * 85, 24, 0, Math.PI * 2); c.fill(); }
    c.beginPath(); c.arc(0, hy - 150, 46, 0, Math.PI * 2); c.fill();
    c.fillStyle = HAIR_L; c.beginPath(); c.arc(-14, hy - 160, 14, 0, Math.PI * 2); c.fill();

    // eyes with blink
    const bp = ((t + (o.blinkSeed || 0)) % 3.7), blink = bp < 0.12 ? 0.1 : 1, eyY = hy + 5 - (P.lookUp ? 6 * k : 0);
    [-34, 34].forEach(ex => {
      c.fillStyle = '#fff'; c.beginPath(); c.ellipse(ex, eyY, 17, 20 * blink * (P.oh ? 1.15 : 1), 0, 0, Math.PI * 2); c.fill();
      if (blink > 0.5) { c.fillStyle = INK; c.beginPath(); c.arc(ex + look, eyY + 2 - (P.lookUp ? 7 * k : 0), 10, 0, Math.PI * 2); c.fill();
        c.fillStyle = '#fff'; c.beginPath(); c.arc(ex + look + 4, eyY - 3, 3.5, 0, Math.PI * 2); c.fill(); }
    });
    // brows: positive = raised, negative = worried (inner ends up)
    c.strokeStyle = HAIR; c.lineWidth = 8; c.lineCap = 'round';
    [-1, 1].forEach(s => { const bx = s * 34, by = hy - 28 - brow * 8;
      c.beginPath(); c.moveTo(bx - s * 18, by + (brow < 0 ? brow * 7 : 0)); c.lineTo(bx + s * 18, by - (brow < 0 ? brow * 5 : 0)); c.stroke(); });
    // cheeks
    c.fillStyle = 'rgba(232,110,110,0.35)'; c.beginPath(); c.ellipse(-55, hy + 38, 16, 10, 0, 0, Math.PI * 2); c.ellipse(55, hy + 38, 16, 10, 0, 0, Math.PI * 2); c.fill();
    // nose
    c.strokeStyle = SKIN_D; c.lineWidth = 5; c.beginPath(); c.moveTo(2, hy + 14); c.quadraticCurveTo(-8, hy + 36, 4, hy + 38); c.stroke();
    // mouth: open shape follows the voice; otherwise a smile/frown curve
    const my = hy + 62;
    if (o.viseme && o.viseme !== 'X') {
      drawViseme(c, o.viseme, my);
    } else if (mouth > 0.08 || P.oh) {
      const h = P.oh && mouth < 0.3 ? 16 * k : 6 + mouth * 26, w = 26 - mouth * 6;
      c.fillStyle = '#5A1E22'; c.beginPath(); c.ellipse(0, my, w, h, 0, 0, Math.PI * 2); c.fill();
      c.fillStyle = '#E86E7A'; c.beginPath(); c.ellipse(0, my + h * 0.45, w * 0.6, h * 0.4, 0, 0, Math.PI); c.fill();
      c.fillStyle = '#fff'; c.fillRect(-w * 0.6, my - h + 2, w * 1.2, Math.min(7, h * 0.35));
    } else {
      c.strokeStyle = '#5A1E22'; c.lineWidth = 7; c.beginPath(); c.moveTo(-24, my - smile * 2); c.quadraticCurveTo(0, my + smile * 16, 24, my - smile * 2); c.stroke();
    }

    if (front) { arm(c, -1, -128, -300, L[0], L[1], t, false); arm(c, 1, 128, -300, R[0], R[1], t, false); }
    c.restore();
  };
})();
