// Song-specific visuals for "Phases of the Moon" (loaded by kids-engine.html).
// The moon is drawn to scale for each phase: p = 0 new, 0.25 first quarter, 0.5 full, 0.75 third quarter.
(function () {
  const NAMES = ['New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous', 'Full Moon', 'Waning Gibbous', 'Third Quarter', 'Waning Crescent'];
  const L = SONG.lines, find = (re, n = 0) => L.filter(l => re.test(l.text))[n];
  const MX = 1300, MY = 420, MR = 185;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v)), ease = v => { v = clamp(v, 0, 1); return v * v * (3 - 2 * v); };

  // ---- phase keyframes [time, phase] from the lyric timings ----
  const K = [];
  const v2 = ['New moon', 'Waxing crescent', 'First quarter', 'Waxing gibbous'], v3 = ['Full moon', 'Waning gibbous', 'Third quarter', 'Waning crescent'];
  v2.forEach((s, i) => { const l = find(new RegExp('^' + s)); if (l) K.push([l.start, i * 0.125]); });
  const grow = find(/^Waxing means/); if (grow) K.push([grow.start, 0.375]);
  v3.forEach((s, i) => { const l = find(new RegExp('^' + s)); if (l) K.push([l.start, 0.5 + i * 0.125]); });
  const outro = L.find(l => /Outro/i.test(l.section));
  const darkW = find(/^Waning crescent/); if (darkW) { const w = darkW.words.find(w => /dark/i.test(w.w)); if (w) K.push([w.start, 1.0]); }
  if (outro) K.push([outro.start, 1.5]); // full moon to say goodnight (1.5 = full after one cycle)
  K.sort((a, b) => a[0] - b[0]);
  const bridge = [find(/^New moon, crescent/), find(/^Gibbous, quarter/)];
  const bridgeWords = [];
  if (bridge[0]) bridge[0].words.forEach((w, i) => bridgeWords.push([w.start, [0, 0.125, 0.25, 0.375, 0.5][i] ?? 0.5]));
  if (bridge[1]) bridge[1].words.forEach((w, i) => bridgeWords.push([w.start, [0.625, 0.75, 0.875, 1.0][i] ?? 1]));
  const chorusLines = L.filter(l => /Chorus/i.test(l.section));
  const chorusSpans = []; // a chorus = 4 lines; the moon spins through all 8 phases during it
  for (let i = 0; i < chorusLines.length; i += 4) chorusSpans.push([chorusLines[i].start - 0.3, chorusLines[Math.min(i + 3, chorusLines.length - 1)].end + 0.3]);
  const balloon = L.filter(l => /balloon/.test(l.text));
  const sunLine = find(/^The sun shines/), orbitA = find(/^As the moon goes/), orbitB = find(/^We see new shapes/);
  const sayLine = find(/^Can you say/), days = find(/^Twenty-nine/), again = find(/^Then it starts/);

  function phaseAt(t, beatAt) {
    for (const [a, b] of chorusSpans) if (t >= a && t <= b) return { p: (Math.floor(beatAt(t) / 2) % 8) / 8, spin: true };
    if (again && t >= again.start - 0.2 && t <= again.end + 0.3) return { p: ((t - again.start) * 0.5 + 0.5) % 1, spin: true };
    if (bridgeWords.length && t >= bridgeWords[0][0] - 0.1 && t <= (bridge[1] ? bridge[1].end + 0.4 : 0)) {
      let p = bridgeWords[0][1]; for (const [s, v] of bridgeWords) if (t >= s - 0.05) p = v; return { p, word: true };
    }
    if (!K.length || t < K[0][0] - 0.5) return { p: 0.5 }; // intro + verse 1: full moon
    let p = K[0][1];
    for (let i = 0; i < K.length; i++) if (t >= K[i][0]) { const prev = i ? K[i - 1][1] : 0.5, k = ease((t - K[i][0]) / 0.7); p = prev + (K[i][1] - prev) * k; }
    return { p: p % 1 === 0 && p > 0 ? 0.9999 : p };
  }

  function moon(c, cx, cy, r, p, glow = 1) {
    p = ((p % 1) + 1) % 1; const illum = (1 - Math.cos(2 * Math.PI * p)) / 2;
    const g = c.createRadialGradient(cx, cy, r * 0.8, cx, cy, r * 2.1);
    g.addColorStop(0, `rgba(255,240,170,${0.35 * illum * glow})`); g.addColorStop(1, 'rgba(255,240,170,0)');
    c.fillStyle = g; c.beginPath(); c.arc(cx, cy, r * 2.1, 0, Math.PI * 2); c.fill();
    c.fillStyle = '#353E80'; c.beginPath(); c.arc(cx, cy, r, 0, Math.PI * 2); c.fill(); // the dark part is still there
    c.strokeStyle = 'rgba(255,255,255,0.25)'; c.lineWidth = 3; c.stroke();
    // lit region between two boundaries for each row
    const waxing = p <= 0.5, e = Math.cos(2 * Math.PI * p), N = 64, pts = [];
    for (let i = 0; i <= N; i++) { const y = -r + 2 * r * i / N, w = Math.sqrt(Math.max(0, r * r - y * y)); pts.push([y, w]); }
    c.save(); c.beginPath();
    if (waxing) { pts.forEach(([y, w]) => c.lineTo(cx + w, cy + y)); for (let i = N; i >= 0; i--) c.lineTo(cx + e * pts[i][1], cy + pts[i][0]); }
    else { pts.forEach(([y, w]) => c.lineTo(cx - w, cy + y)); for (let i = N; i >= 0; i--) c.lineTo(cx - e * pts[i][1], cy + pts[i][0]); }
    c.closePath(); c.clip();
    const lg = c.createRadialGradient(cx - r * 0.3, cy - r * 0.3, r * 0.1, cx, cy, r);
    lg.addColorStop(0, '#FFFBE0'); lg.addColorStop(1, '#F6DC7A'); c.fillStyle = lg; c.fillRect(cx - r, cy - r, 2 * r, 2 * r);
    c.fillStyle = 'rgba(214,180,90,0.45)';
    [[-0.35, -0.3, 0.16], [0.3, -0.1, 0.12], [0.05, 0.38, 0.2], [-0.45, 0.25, 0.09], [0.48, 0.42, 0.08], [0.15, -0.55, 0.07]]
      .forEach(([x, y, s]) => { c.beginPath(); c.arc(cx + x * r, cy + y * r, s * r, 0, Math.PI * 2); c.fill(); });
    c.restore();
  }

  function label(c, FONT, text, x, y, size, fill) {
    c.save(); c.font = FONT(`700 ${size}px`); c.textAlign = 'center'; c.textBaseline = 'middle'; c.lineJoin = 'round';
    c.lineWidth = size * 0.16; c.strokeStyle = '#1A1640'; c.strokeText(text, x, y); c.fillStyle = fill; c.fillText(text, x, y); c.restore();
  }
  function fadeIn(t, a, b, d = 0.4) { return ease((t - a) / d) * (1 - ease((t - b) / d)); }

  function sun(c, x, y, r, t) {
    c.save(); c.translate(x, y); c.rotate(t * 0.4);
    c.fillStyle = '#FFB020'; for (let i = 0; i < 12; i++) { c.rotate(Math.PI / 6); c.beginPath(); c.moveTo(r * 1.1, -10); c.lineTo(r * 1.55, 0); c.lineTo(r * 1.1, 10); c.fill(); }
    c.restore(); const g = c.createRadialGradient(x - r * 0.3, y - r * 0.3, 5, x, y, r); g.addColorStop(0, '#FFF2A0'); g.addColorStop(1, '#FFB020');
    c.fillStyle = g; c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fill();
  }

  function orbit(c, t, a, FONT) { // Earth with the Moon going round it, lit from the left by the Sun
    c.save(); c.globalAlpha = a;
    c.fillStyle = 'rgba(16,14,48,0.55)'; c.beginPath(); c.roundRect(MX - 420, MY - 250, 840, 470, 40); c.fill();
    sun(c, MX - 340, MY - 150, 46, t);
    c.strokeStyle = 'rgba(255,255,255,0.35)'; c.setLineDash([10, 10]); c.lineWidth = 3; c.beginPath(); c.ellipse(MX + 40, MY + 10, 280, 120, 0, 0, Math.PI * 2); c.stroke(); c.setLineDash([]);
    const ang = t * 1.4, mx = MX + 40 + Math.cos(ang) * 280, my = MY + 10 + Math.sin(ang) * 120;
    const earthFront = Math.sin(ang) < 0, drawEarth = () => {
      c.fillStyle = '#3A8EDB'; c.beginPath(); c.arc(MX + 40, MY + 10, 70, 0, Math.PI * 2); c.fill();
      c.fillStyle = '#4FBF6A'; [[-20, -18, 26], [24, 10, 22], [-6, 30, 14]].forEach(([x, y, s]) => { c.beginPath(); c.arc(MX + 40 + x, MY + 10 + y, s, 0, Math.PI * 2); c.fill(); });
      c.fillStyle = 'rgba(0,0,30,0.35)'; c.beginPath(); c.arc(MX + 40, MY + 10, 70, -Math.PI / 2, Math.PI / 2); c.fill(); // night side faces away from the Sun
    };
    const drawMoon = () => { c.fillStyle = '#F6E7A8'; c.beginPath(); c.arc(mx, my, 30, 0, Math.PI * 2); c.fill();
      c.fillStyle = 'rgba(0,0,30,0.45)'; c.beginPath(); c.arc(mx, my, 30, -Math.PI / 2, Math.PI / 2); c.fill(); };
    if (earthFront) { drawMoon(); drawEarth(); } else { drawEarth(); drawMoon(); }
    label(c, FONT, 'Earth', MX + 40, MY + 120, 34, '#9FE2FF'); label(c, FONT, 'Moon', mx, my - 52, 30, '#FFE58A'); label(c, FONT, 'Sun', MX - 340, MY - 60, 30, '#FFD43B');
    c.restore();
  }

  function strip(c, t, p, a, FONT, highlightWord) {
    if (a <= 0) return;
    c.save(); c.globalAlpha = a;
    const x0 = 740, step = 125, y = 70, cur = Math.round(p * 8) % 8;
    c.fillStyle = 'rgba(16,14,48,0.55)'; c.beginPath(); c.roundRect(x0 - 70, y - 52, step * 7 + 140, 104, 52); c.fill();
    for (let i = 0; i < 8; i++) { const on = i === cur, s = on ? 1.25 + 0.08 * Math.sin(t * 8) : 1;
      moon(c, x0 + i * step, y, 32 * s, i / 8 + 0.0001, on ? 1 : 0.2);
      if (on) { c.strokeStyle = '#FFD43B'; c.lineWidth = 5; c.beginPath(); c.arc(x0 + i * step, y, 32 * s + 9, 0, Math.PI * 2); c.stroke(); } }
    c.restore();
  }

  window.__moon = moon; // used by thumbnail.html
  window.VIS = {
    draw(c, t, E) {
      const { beatAt, FONT } = E, ph = phaseAt(t, beatAt);
      const titleOff = ease((t - (L[0].start - 0.6)) / 0.8);
      const orbA = orbitA ? fadeIn(t, orbitA.start - 0.4, orbitB.end + 0.2, 0.5) : 0;
      const dA = days ? fadeIn(t, days.start - 0.2, days.end + 0.4, 0.4) : 0;
      // main moon
      let scale = 1; for (const b of balloon) if (t >= b.start && t <= b.end + 0.3) scale = 1 + 0.16 * Math.sin((t - b.start) * Math.PI * 2 / Math.max(0.5, b.end - b.start) * 2);
      const mA = titleOff * (1 - orbA) * (1 - dA);
      if (mA > 0) { c.save(); c.globalAlpha = mA; moon(c, MX, MY + Math.sin(t * 1.2) * 8, MR * scale, ph.p); c.restore(); }
      // sun shining on the moon (verse 1, line 2)
      if (sunLine) { const a = fadeIn(t, sunLine.start - 0.3, sunLine.end + 0.4);
        if (a > 0) { c.save(); c.globalAlpha = a; sun(c, 860, 200, 62, t);
          for (let i = 0; i < 3; i++) { const k = ((t * 0.9 + i / 3) % 1); c.strokeStyle = `rgba(255,214,90,${1 - k})`; c.lineWidth = 8; c.lineCap = 'round';
            const x = 940 + k * 160, y = 230 + k * 90; c.beginPath(); c.moveTo(x, y); c.lineTo(x + 50, y + 28); c.stroke(); }
          label(c, FONT, 'Moonlight is sunlight!', MX, MY + 270, 52, '#FFD43B'); c.restore(); } }
      if (orbA > 0) orbit(c, t, orbA, FONT);
      // phase name under the moon (from verse 2 on), "waxing / waning" rules
      if (t > SONG.duration - 7.5) return; // end card
      const first = K.length ? K[0][0] - 0.3 : 1e9;
      const busy = [grow, find(/^Waning means/), sayLine].some(l => l && t >= l.start - 0.3 && t <= l.end + 0.6); // another caption owns the slot
      if (t > first && mA > 0.5 && !ph.spin && !busy) {
        const idx = Math.round(ph.p * 8) % 8, col = idx === 0 ? '#C9D2FF' : idx < 4 ? '#7CF29A' : idx === 4 ? '#FFD43B' : '#FFA36B';
        label(c, FONT, NAMES[idx], MX, MY + 275, 64, col);
      }
      if (ph.spin && mA > 0.5) label(c, FONT, 'Phases of the Moon!', MX, MY + 275, 60, '#FF8FB8');
      const rule = (l, txt, col, dir) => { if (!l) return; const a = fadeIn(t, l.start - 0.2, l.end + 0.5); if (a <= 0) return;
        c.save(); c.globalAlpha = a; label(c, FONT, txt, MX, MY + 275, 66, col);
        const ay = MY + 30 + (dir < 0 ? 1 : -1) * ((t * 60) % 40); c.fillStyle = col; c.beginPath();
        c.moveTo(MX + 260, ay + dir * 40); c.lineTo(MX + 300, ay - dir * 10); c.lineTo(MX + 340, ay + dir * 40); c.fill(); c.fillRect(MX + 285, ay + dir * 40, 30, dir * 50); c.restore(); };
      rule(grow, 'Waxing = Growing!', '#7CF29A', 1);
      rule(find(/^Waning means/), 'Waning = Shrinking!', '#FFA36B', -1);
      // strip of all 8 phases: from verse 2 on
      strip(c, t, ph.p, t > first ? ease((t - first) / 0.6) * (1 - orbA) : 0, FONT);
      if (sayLine) { const a = fadeIn(t, sayLine.start - 0.2, sayLine.end + 0.3); if (a > 0) { c.save(); c.globalAlpha = a; label(c, FONT, 'Say it with me!', MX, MY + 275, 70, '#FF8FB8'); c.restore(); } }
      // 29 and a half days calendar
      if (dA > 0) { c.save(); c.globalAlpha = dA;
        c.fillStyle = '#FFFFFF'; c.beginPath(); c.roundRect(MX - 200, MY - 190, 400, 380, 36); c.fill();
        c.fillStyle = '#FF6B8B'; c.beginPath(); c.roundRect(MX - 200, MY - 190, 400, 100, [36, 36, 0, 0]); c.fill();
        label(c, FONT, 'DAYS', MX, MY - 140, 50, '#FFFFFF');
        const n = Math.min(29.5, 1 + 28.5 * ease((t - days.start) / Math.max(1, days.end - days.start - 0.6)));
        const whole = Math.floor(n), half = n >= 29.5;
        c.save(); c.font = FONT('700 170px'); c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = '#2B2768'; c.fillText(String(whole) + (half ? '½' : ''), MX, MY + 50); c.restore();
        label(c, FONT, 'One full cycle!', MX, MY + 275, 58, '#FFD43B'); c.restore(); }
    },
    photoPose(t, l) { // gestures for the photo puppet (other lines: sing2 with lip sync, choruses: dance flipbook)
      if (!l) return null;
      const at = (pose, d) => (t < l.start - 0.25 + d ? { pose, since: l.start - 0.25 } : { pose: 'sing2', since: l.start - 0.25 + d });
      if (/^Look up/.test(l.text)) return at('point', 2.2);
      if (/^The moon can't/.test(l.text)) return at('shrug', 2.4);
      if (/^The sun shines/.test(l.text)) return at('point', 2.0);
      if (/^(New moon|Waxing crescent|First quarter|Waxing gibbous|Full moon|Waning gibbous|Third quarter|Waning crescent),/.test(l.text) && !/Bridge/.test(l.section)) return at('pointR', 1.8);
      if (/^Waxing means/.test(l.text)) return { pose: 'cheer', since: l.start - 0.25 };
      if (/^Waning means/.test(l.text)) return at('think', 2.5);
      if (/^Can you say/.test(l.text)) return { pose: 'cheer', since: l.start - 0.25 };
      if (/^New moon, crescent|^Gibbous, quarter/.test(l.text)) return { pose: 'count', since: l.start - 0.25 };
      if (/^Twenty-nine/.test(l.text)) return at('think', 2.6);
      if (/^Then it starts/.test(l.text)) return at('thumbs', 2.4);
      if (/Outro/i.test(l.section)) return { pose: 'hello', since: l.start - 0.25 };
      return null;
    },
    pose(t, l) {
      if (!l) return null;
      if (/^(New moon|Waxing crescent|First quarter|Waxing gibbous|Full moon|Waning gibbous|Third quarter|Waning crescent),/.test(l.text) && !/Bridge/.test(l.section)) return { pose: 'point', since: l.start - 0.25 };
      if (/^Can you say|^New moon, crescent|^Gibbous, quarter/.test(l.text)) return { pose: /^Can/.test(l.text) ? 'cheer' : 'clap', since: l.start - 0.25 };
      if (/^Twenty-nine/.test(l.text)) return { pose: 'point', since: l.start - 0.25 };
      return null;
    },
  };
})();
